"""STEP2 (a)(b)(d): heavy domain randomisation, DR curriculum stages and the goal-command obs block, as a JEnv SUBCLASS (DREnv).
train/v5_train_j.JEnv is NOT modified, so every existing run/default and the Evaluator worker (which builds JEnv from args.json) are bit-identical.
All DR is OFF unless dr=True; goal obs is OFF unless goal_obs=True (then obs grows by GOAL_DIM at the END: indices [n0, n0+GOAL_DIM)).
DR ranges are DISJOINT from the Evaluator's v5-heldout-1 set (hgs scott-e 1a98372 docs/HARNESS_V5_SPEC.md): checked by assert_disjoint_heldout() at import.
Sources: Data Agent goalcond_refs 5_driver_dr (PROVISIONAL until 7b9faa3 is on main), club-shot-shape-dr-refs @6d610e5; Langdown 2013 (n=20) address SD 11 mm.
Labels: M = measured (cited source), E = estimate, P = provisional engineering choice (no source)."""
import math, numpy as np, mujoco
from train.v5_train_j import JEnv

HELDOUT = dict(seeds=(910000, 910023), joint=(0.0325, 0.045), vel=(0.065, 0.09), mu=((0.55, 0.62), (1.08, 1.15)), ball=(0.013, 0.018))
SEED_MAX = 900000   # training seeds must be < 900000
DR = dict(   # per-component |magnitude| bands (low band w.p. 1-p_hi, high band w.p. p_hi)
    joint=((0.0, 0.03), (0.05, 0.06), 0.2),          # rad per joint, random sign (P; v4 gate perturbation 0.03 = low band top)
    vel=((0.0, 0.06), (0.10, 0.12), 0.2),            # rad/s per dof (P)
    mu=((0.63, 1.07), ((0.45, 0.54), (1.16, 1.25)), 0.2),   # floor sliding mu (P; sourced turf range 0.7-1.05 is E)
    ball_sd=0.011, ball_max=0.012,                   # m per axis, N(0, 11 mm) truncated at 12 mm (Langdown 2013 address SD 11.0 mm, n=20: M)
    slope_max=0.07, slope_p=0.5,                     # gravity tilt grade 0-7% w.p. 0.5 (fairway cross-slope max ~7%: E, club-shot-shape-dr-refs)
    head_g=(190.0, 210.0),                           # club-head mass g (200 g nominal, 190-210: Data Agent 5_driver_dr, PROVISIONAL). SWING DYNAMICS ONLY: golfphys m_head fixed
    loft_deg=1.5,                                    # +-1.5 deg face loft (9-12 deg range, +-2 adjustable: 5_driver_dr, PROVISIONAL)
    seg_cv=dict(trunk=0.04, thigh=0.08, calf=0.08, foot=0.07),   # de Leva masses, Clauser CVs (M, refs @6d610e5); G1 has no separate head body -> head CV unused
    tau=(0.90, 1.00),                                # actuator torque-limit scale, NEVER above stock (P)
    lat_p=0.25)                                      # P(1 control-step = 20 ms action latency) per episode (P)
SEG = dict(trunk=("pelvis", "torso_link", "waist_yaw_link", "waist_roll_link"), thigh=("hip_pitch_link", "hip_roll_link", "hip_yaw_link"), calf=("knee_link",), foot=("ankle_pitch_link", "ankle_roll_link"))
# curriculum stage -> DR breadth (fraction of each band's width used, high bands only from stage 2) ; stages: 0 address, 1 contact, 2 speed, 3 shaping
STAGES = ("address", "contact", "speed", "shaping"); BREADTH = (0.35, 0.7, 1.0, 1.0); HIGH_ON = (False, False, True, True)

def assert_disjoint_heldout():
    j, v = DR["joint"], DR["vel"]
    assert j[0][1] < HELDOUT["joint"][0] and j[1][0] > HELDOUT["joint"][1], "joint DR overlaps held-out"
    assert v[0][1] < HELDOUT["vel"][0] and v[1][0] > HELDOUT["vel"][1], "vel DR overlaps held-out"
    for lo, hi in [DR["mu"][0], *DR["mu"][1]]:
        for hlo, hhi in HELDOUT["mu"]: assert hi < hlo or lo > hhi, f"mu DR {lo}-{hi} overlaps held-out {hlo}-{hhi}"
    assert DR["ball_max"] < HELDOUT["ball"][0], "ball DR overlaps held-out"
    assert SEED_MAX <= HELDOUT["seeds"][0]
assert_disjoint_heldout()

# (d) goal command block. Encoding (all float32), appended after the JEnv obs:
GOAL_KEYS = ("club_driver", "club_7iron", "club_pw", "target_carry", "target_dir", "shape", "bend", "handedness")
GOAL_DIM = len(GOAL_KEYS)
def encode_goal(g):
    c = g.get("club", "driver")
    return np.array([c == "driver", c == "7iron", c == "pw", float(g["target_carry"]) / 200.0, float(g["target_dir"]) / 10.0,
                     {"draw": 1.0, "straight": 0.0, "fade": -1.0}[g.get("shape", "straight")], float(g.get("bend", 0.0)) / 10.0, 1.0 if g.get("handedness", "LH") == "RH" else -1.0], np.float32)
def spin_axis_target_deg(face_to_path_deg, spin_loft_deg, handed="LH"):
    """D-plane: tan(axis) = tan(face-to-path)/tan(spin loft); mirrored (sign flip) for left-handed. Driver start direction ~ 0.85 x face angle."""
    a = math.degrees(math.atan(math.tan(math.radians(face_to_path_deg)) / max(math.tan(math.radians(spin_loft_deg)), 1e-6)))
    return -a if handed == "LH" else a

class DREnv(JEnv):
    dr = False; dr_stage = 0; goal_obs = False; goal_w = 0.0; impact_log = False
    def __init__(self, dt=0.002, seed=0, keys=None, res_scale=1.0, t_down=0.27):
        if seed >= SEED_MAX: raise SystemExit(f"DR SEED GUARD: training env seed {seed} >= {SEED_MAX} (held-out seeds 910000-910023)")
        super().__init__(dt=dt, seed=seed, keys=keys, res_scale=res_scale, t_down=t_down); self.goal = None; self._next_goal = None; self.dr_log = None; self._abuf = None; self._lat = 0
        if self.goal_obs: self._grow_obs()
    def _grow_obs(self):
        from gymnasium import spaces
        n = self.observation_space.shape[0] + GOAL_DIM; self.observation_space = spaces.Box(-np.inf, np.inf, (n,), np.float32)
    def configure(self, **kw):
        had = self.goal_obs; super().configure(**kw)
        if self.goal_obs and not had: self._grow_obs()
    def set_goal(self, goal):
        """Hook: goal dict {club, target_carry (m), target_dir (deg, +left world), shape (draw|straight|fade), bend (deg spin axis), handedness}. Applied at the next reset; logged as ep['goal']."""
        assert goal.get("club", "driver") == "driver", "driver only for now (no 7-iron/PW model yet)"
        self._next_goal = dict(goal)
    def _xobs(self, o):
        x = super()._xobs(o)
        return np.concatenate([x, encode_goal(self.goal or dict(club="driver", target_carry=0.0, target_dir=0.0))]).astype(np.float32) if self.goal_obs else x
    # --- DR helpers
    def _band(self, spec, sc, hi_on):
        lo_b, hi_b, p = spec
        if hi_on and self.rng2.random() < p:
            b = hi_b if isinstance(hi_b[0], float) else hi_b[self.rng2.integers(len(hi_b))]
            return float(self.rng2.uniform(*b))
        return float(lo_b[0] + self.rng2.random() * (lo_b[1] - lo_b[0]) * sc) if spec is not DR["mu"] else float(self.rng2.uniform(1.0 - (1.0 - lo_b[0]) * sc, 1.0 + (lo_b[1] - 1.0) * sc))
    def _mag(self, spec, n, sc, hi_on):   # per-component magnitudes with random sign
        lo_b, hi_b, p = spec; hi = self.rng2.random(n) < (p if hi_on else 0.0)
        m = np.where(hi, self.rng2.uniform(hi_b[0], hi_b[1], n), self.rng2.uniform(lo_b[0], lo_b[0] + (lo_b[1] - lo_b[0]) * sc, n))
        return m * self.rng2.choice((-1.0, 1.0), n)
    def _model_base(self):
        m = self.env.m
        if getattr(self, "_mb", None) is None or self._mb[0] is not m:
            self._mb = (m, m.body_mass.copy(), m.body_inertia.copy(), m.body_ipos.copy(), m.geom_quat.copy(), m.opt.gravity.copy(), self.env.tau.copy())
        return self._mb
    def _apply_model_dr(self):
        e = self.env; m = e.m; _, bm, bi, bp, gq, gr, tau = self._model_base(); sc = BREADTH[self.dr_stage]; hi_on = HIGH_ON[self.dr_stage]; L = {}
        m.body_mass[:] = bm; m.body_inertia[:] = bi; m.body_ipos[:] = bp; m.geom_quat[:] = gq; m.opt.gravity[:] = gr; e.tau[:] = tau
        for seg, names in SEG.items():
            for b in range(m.nbody):
                nm = m.body(b).name
                if any(nm == s or nm.endswith(s) and nm.startswith(("left_", "right_")) for s in names):
                    f = float(np.clip(1.0 + self.rng2.normal(0, DR["seg_cv"][seg] * sc), 1 - 2 * DR["seg_cv"][seg], 1 + 2 * DR["seg_cv"][seg])); m.body_mass[b] = bm[b] * f; m.body_inertia[b] = bi[b] * f; L[nm] = round(f, 4)
        cb = m.body("club").id; dm = (self.rng2.uniform(*DR["head_g"]) - 200.0) * sc / 1000.0; hp = m.geom_pos[e.head_geom]; M = bm[cb]
        m.body_mass[cb] = M + dm; m.body_ipos[cb] = (M * bp[cb] + dm * hp) / (M + dm); m.body_inertia[cb] = bi[cb] * (M + dm) / M; L["head_dm_g"] = round(dm * 1000, 2)
        dl = math.radians(self.rng2.uniform(-1, 1) * DR["loft_deg"] * sc); q = np.zeros(4); mujoco.mju_axisAngle2Quat(q, np.array([0.0, 1.0, 0.0]), dl); qo = np.zeros(4); mujoco.mju_mulQuat(qo, gq[e.head_geom], q); m.geom_quat[e.head_geom] = qo; L["loft_d_deg"] = round(math.degrees(dl), 3)
        if self.rng2.random() < DR["slope_p"]:
            g = self.rng2.uniform(0, DR["slope_max"] * sc); az = self.rng2.uniform(0, 2 * math.pi); t = math.atan(g); G = float(np.linalg.norm(gr))
            m.opt.gravity[:] = (G * math.sin(t) * math.cos(az), G * math.sin(t) * math.sin(az), -G * math.cos(t)); L["slope"] = (round(g, 4), round(math.degrees(az), 1))
        e.tau[:] = tau * self.rng2.uniform(1.0 - (DR["tau"][1] - DR["tau"][0]) * sc, DR["tau"][1]); L["tau_scale"] = round(float(e.tau[0] / tau[0]), 4)
        mu = self._band(DR["mu"], sc, hi_on); m.geom_friction[e.floor, 0] = mu; L["mu"] = round(mu, 4)
        self._lat = int(self.rng2.random() < DR["lat_p"] * sc); L["latency_steps"] = self._lat
        return L
    def reset(self, **kw):
        if kw.get("seed") is not None and HELDOUT["seeds"][0] <= int(kw["seed"]) <= HELDOUT["seeds"][1]: raise SystemExit("DR SEED GUARD: held-out seed passed to a training env")
        if self._next_goal is not None: self.goal = self._next_goal
        if getattr(self.ref, "_plumb_base", None) is not None: self.ref = self.ref._plumb_base   # --plumb_addr: drop last episode's offset reference
        if not self.dr:
            out = super().reset(**kw); self._abuf = None
            if getattr(self, "plumb_addr", False): from train.plumb_addr import apply_plumb; apply_plumb(self); out = (self._xobs(self.env._obs()), {})
            return out
        L = self._apply_model_dr(); fr0, qn0, qvn0, bt0 = self.fr_rand, self.init_qn, self.init_qvn, self.ball_tol
        self.fr_rand = False; self.init_qn = 0.0; self.init_qvn = 0.0; self.ball_tol = 0.0   # DR replaces the JEnv draws (restored after)
        try: o, info = super().reset(**kw)
        finally: self.fr_rand, self.init_qn, self.init_qvn, self.ball_tol = fr0, qn0, qvn0, bt0
        e = self.env; sc = BREADTH[self.dr_stage]; hi_on = HIGH_ON[self.dr_stage]
        if getattr(self, "plumb_addr", False): from train.plumb_addr import apply_plumb; apply_plumb(self); L["plumb"] = self.plumb_log   # --plumb_addr (default off)
        b = np.clip(self.rng2.normal(0, DR["ball_sd"] * sc, 2), -DR["ball_max"], DR["ball_max"]); e.tee[:2] += b; e.d.qpos[e.ball_q:e.ball_q + 2] = e.tee[:2]; L["ball_dxy_mm"] = [round(float(x) * 1000, 2) for x in b]
        if self.mode == 0:
            e.d.qpos[e.qa] += self._mag(DR["joint"], len(e.qa), sc, hi_on); e.d.qvel[e.da] += self._mag(DR["vel"], len(e.da), sc, hi_on)
        mujoco.mj_forward(e.m, e.d); self._abuf = None; self.dr_log = dict(L, stage=STAGES[self.dr_stage])
        return self._xobs(e._obs()), {}
    def step(self, a):
        if self.dr and self._lat:
            a_new = np.asarray(a, np.float32).copy(); a = self._abuf if self._abuf is not None else np.zeros_like(a_new); self._abuf = a_new
        o, r, te, tr, info = super().step(a)
        if (te or tr) and "ep" in info:
            if self.goal is not None:
                info["ep"]["goal"] = dict(self.goal); g = self.goal
                if self.goal_w > 0 and info["ep"].get("contact"):
                    ec = abs(float(info["ep"].get("carry", 0.0)) - float(g["target_carry"])) / max(float(g["target_carry"]), 1.0); ed = abs(float(info["ep"].get("az", 0.0)) - float(g["target_dir"])) / 10.0
                    r += self.goal_w * (2.0 - min(ec, 1.0) - min(ed, 1.0))
            if self.dr: info["ep"]["dr"] = self.dr_log
        if self.impact_log and info.get("contact") and "face_yaw_deg" in info:   # --impact_log (default off): WORLD-frame impact geometry, + = LEFT (+y, target +x). Info/ep only; reward untouched
            hs = 1.0 if self.env.handed.upper().startswith("R") else -1.0          # env face_yaw_deg/club_path_deg are golfer-frame (world x hs); undo it
            fw = float(info["face_yaw_deg"]) * hs; pw = float(info["club_path_deg"]) * hs; sl = float(info["dynamic_loft_deg"]) - float(info["aoa_deg"])
            imp = dict(impact_face_world_deg=fw, impact_path_world_deg=pw, impact_face_to_path_world_deg=fw - pw, impact_spin_loft_deg=sl,
                       impact_dloft_deg=float(info["dynamic_loft_deg"]), impact_aoa_deg=float(info["aoa_deg"]), impact_spin_axis_deg=float(info.get("spin_axis_deg", 0.0)), impact_sidespin_rpm=float(info.get("sidespin_rpm", 0.0)))
            info.update(imp)
            if "ep" in info: info["ep"].update(imp)
        return o, r, te, tr, info
