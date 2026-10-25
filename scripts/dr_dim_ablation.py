"""Per-DR-dimension ablation (LOCAL, NOT OFFICIAL; evaluation only). One DREnv DR dimension at a time (slope always off) at breadth .35/.7/1.0
(= curriculum stages 0/1/2; high bands only at 1.0, full width), plus 'none' and 'all'. Deterministic policy, address starts (rsi 1,0,0), seeds < 900000.
Plant (v4 robustness style, per episode): lead-foot slip > 2.5 cm or turn > 10 deg vs ADDRESS, or lead foot airborne (lead sole GRF <= 1 N) > 1 control step,
window address -> impact (no-contact episodes: whole episode). NOTE: the harness window is top -> impact; this window is wider (conservative).
Obs check: per episode max |normalised obs| and fraction of (step, dim) with |z| > 5 (VecNormalize clip 10).
Usage: PYTHONPATH=. python scripts/dr_dim_ablation.py <ckpt_base> <dims comma|ALL> <breadths comma> <n> <seed0> <out.jsonl>"""
import sys, json, os, numpy as np
import train.dr_goal as DG
from train.dr_goal import DREnv
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
CK, DIMS, BRS, N, S0, OUT = sys.argv[1], sys.argv[2], [float(x) for x in sys.argv[3].split(",")], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
ALLD = ("joint", "vel", "mu", "ball", "head", "loft", "seg", "tau", "lat")
DIMS = ["none", *ALLD, "all"] if DIMS == "ALL" else DIMS.split(",")
DR0 = {k: v for k, v in DG.DR.items()}
A = json.load(open(os.path.join(os.path.dirname(CK), "args.json"))); keys = {tuple(k.split("|")): v for k, v in json.load(open(A["keys"])).items()}
W = ('xf_hard','grf_lo','grf_w','xf_cap_lo','xf_cap_w','track_floor','ord2_w','launch_w','desc_w','dloft_w','spin_lo_w','smash_w','spin_w','spin_hi','spin_scale','fine_grf','launch_hi','dl_lo','dl_hi','aoa_lo','spd_w','ctrl_dt','early_w','aim_w','foot_w','plant_term','strike_w','grfd_w','post_t','tc_w','smash2_w','ctr2_w','pel_w','pel_t_w','pel_dps','pel_t_lo','pel_t_hi','sep_w','ctr_w','env_v4','tee_mode')
class AblEnv(DREnv):
    on = set()
    def _apply_model_dr(self):
        L = super()._apply_model_dr(); e = self.env; m = e.m; base, bm, bi, bp, gq, gr, tau = self._model_base(); cb = m.body("club").id
        m.opt.gravity[:] = gr; L.pop("slope", None)
        if "seg" not in self.on:
            keep = m.body_mass[cb], m.body_inertia[cb].copy(), m.body_ipos[cb].copy(); m.body_mass[:] = bm; m.body_inertia[:] = bi; m.body_ipos[:] = bp; m.body_mass[cb], m.body_inertia[cb], m.body_ipos[cb] = keep
        if "head" not in self.on: m.body_mass[cb] = bm[cb]; m.body_inertia[cb] = bi[cb]; m.body_ipos[cb] = bp[cb]
        if "loft" not in self.on: m.geom_quat[e.head_geom] = gq[e.head_geom]
        if "tau" not in self.on: e.tau[:] = tau
        if "mu" not in self.on: m.geom_friction[e.floor, 0] = self._mu0
        if "lat" not in self.on: self._lat = 0
        return L
    jmask = None
    def _mag(self, spec, n, sc, hi_on):
        v = super()._mag(spec, n, sc, hi_on)
        return v * self.jmask if (self.jmask is not None and spec is DG.DR["joint"]) else v
def mk(on, stage, dim=""):
    def f():
        DG.DR.update(DR0)
        if "joint" not in on: DG.DR["joint"] = ((0.0, 0.0), (0.0, 0.0), 0.0)
        if "vel" not in on: DG.DR["vel"] = ((0.0, 0.0), (0.0, 0.0), 0.0)
        if "ball" not in on: DG.DR["ball_sd"] = 0.0
        e = AblEnv(dt=0.002, seed=11, keys=keys, res_scale=A["res_scale"], t_down=A["t_down"]); e.configure(res_mult=json.loads(A['res_mult']), **{k: A.get(k) for k in W})
        e.rsi = (1.0, 0.0, 0.0); e.env.arm_dist = 0.6; e.target_len = 1.15; e.target_tether = 0.0; e.env.friction_rand = False; e.track_w = 0.0
        e.reset(seed=1); e._mu0 = float(e.env.m.geom_friction[e.env.floor, 0]); e.dr = True; e.dr_stage = stage; e.on = set(on)
        if dim in ("joint_legs", "joint_upper"): lg = np.array([n.split("_")[1] in ("hip", "knee", "ankle") for n in e.env.names], float); e.jmask = lg if dim == "joint_legs" else 1.0 - lg
        if dim == "v4noise": e.dr = False; e.init_qn = 0.03; e.init_qvn = 0.06   # JEnv's own v4-gate-style start noise (uniform +-0.03 rad / +-0.06 rad/s), no DR
        return e
    return f
model = PPO.load(CK, device="cpu")
fo = open(OUT, "a")
for br in BRS:
    stage = {0.35: 0, 0.7: 1, 1.0: 2}[br]
    for dim in DIMS:
        on = set(ALLD) if dim == "all" else set() if dim in ("none", "v4noise") else {"joint"} if dim.startswith("joint_") else {dim}
        e = mk(on, stage, dim)(); vn = VecNormalize.load(CK + "_vecnorm.pkl", DummyVecEnv([lambda: e])); vn.training = False
        rows = []
        for i in range(N):
            o, _ = e.reset(seed=S0 + i); E = e.env; d = E.d; sid = E.m.site(f"{E.lead}_sole_site").id; li = 0 if E.lead == "left" else 1
            P0 = d.site_xpos[sid][:2].copy(); R = d.site_xmat[sid].reshape(3, 3); y0 = np.arctan2(R[1, 0], R[0, 0])
            slip = 0.0; turn = 0.0; air = 0; airmax = 0; zmax = 0.0; zbig = 0; ztot = 0; done = False; info = {}; imp = False
            while not done:
                z = vn.normalize_obs(o[None]); zmax = max(zmax, float(np.abs(z).max())); zbig += int((np.abs(z) > 5).sum()); ztot += z.size
                o, r, te, tr, info = e.step(model.predict(z, deterministic=True)[0][0]); done = te or tr
                if not imp:
                    P = d.site_xpos[sid][:2]; R = d.site_xmat[sid].reshape(3, 3); slip = max(slip, float(np.hypot(*(P - P0))))
                    dy = (np.degrees(np.arctan2(R[1, 0], R[0, 0]) - y0) + 180) % 360 - 180; turn = max(turn, abs(float(dy)))
                    g = E.foot_forces()[li]; air = air + 1 if g <= 1.0 else 0; airmax = max(airmax, air)
                    imp = bool(E.contact)
            rows.append(dict(contact=bool(info.get("contact")), fell=bool(info.get("fell")), slip_cm=100 * slip, turn_deg=turn, air_steps=airmax,
                             plant_ok=bool(slip <= 0.025 and turn <= 10.0 and airmax <= 1), slip_fail=slip > 0.025, turn_fail=turn > 10.0, air_fail=airmax > 1,
                             zmax=zmax, zfrac5=zbig / max(ztot, 1), dr={k: v for k, v in ((e.dr_log if e.dr else None) or {}).items() if k in ("mu", "tau_scale", "latency_steps", "head_dm_g", "loft_d_deg", "ball_dxy_mm")}))
        S = dict(ckpt=os.path.basename(os.path.dirname(CK)), dim=dim, breadth=br, stage=stage, n=N, seed0=S0,
                 contact=np.mean([r["contact"] for r in rows]), fell=np.mean([r["fell"] for r in rows]), plant=np.mean([r["plant_ok"] for r in rows]),
                 slip_fail=np.mean([r["slip_fail"] for r in rows]), turn_fail=np.mean([r["turn_fail"] for r in rows]), air_fail=np.mean([r["air_fail"] for r in rows]),
                 slip_cm_med=float(np.median([r["slip_cm"] for r in rows])), turn_deg_med=float(np.median([r["turn_deg"] for r in rows])),
                 zmax_med=float(np.median([r["zmax"] for r in rows])), zfrac5_mean=float(np.mean([r["zfrac5"] for r in rows])), label="LOCAL, NOT OFFICIAL", rows=rows)
        S = {k: (round(float(v), 4) if isinstance(v, (float, np.floating)) else v) for k, v in S.items()}
        fo.write(json.dumps(S) + "\n"); fo.flush()
        print(f"{S['ckpt']} br {br} {dim:6s} contact {S['contact']:.2f} fell {S['fell']:.2f} plant {S['plant']:.2f} (slip {S['slip_fail']:.2f} turn {S['turn_fail']:.2f} air {S['air_fail']:.2f}) slip_med {S['slip_cm_med']:.1f}cm turn_med {S['turn_deg_med']:.1f} zmax {S['zmax_med']:.1f} z>5 {S['zfrac5_mean']:.4f}", flush=True)
