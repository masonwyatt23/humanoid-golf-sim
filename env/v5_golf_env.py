"""v5 from-scratch golf env (Stage 0): full-body G1-based LEFT-handed golfer, club welded in both hands, stock torque limits (force_scale 1),
foot contact + GRF, ball flight through the vendored golfphys module. NEW file; v3/v4 envs untouched. No scripted teacher in the action path
(the Stage-0 scripted sanity swing in scripts/ only tests the pipeline and is never used for training).

Action: 29 values in [-1,1] -> PD target = address pose + action * ACT_SCALE (rad, clipped to joint range); torque capped by the stock limit and
derated linearly to 0 at rated speed (update every 5 ms). Control dt 20 ms; physics dt 0.0005 default.
Ball is held on the tee until the first club-head/ball contact; at that substep golfphys computes launch + flight (carry has NO ROLL).
"""
import math
import numpy as np
import mujoco
import gymnasium as gym
from gymnasium import spaces
from .v5_body import (build_model, load_address, set_address, STOCK, joint_kind, lead_trail, CTRL_DT)
from .v5_shot import shot_from_contact, verify_toe_sign

ACT_SCALE = 1.0
NEAR = 0.12
FAR = 0.30       # swept-contact / velocity-capture radius (m): head moves up to ~10 cm per substep at 110 mph, dt 0.002
SEG_EVERY = 10   # log segment speeds every 10 substeps (5 ms at dt 0.0005)


R_BALL_E = 0.021335


def swept_hit(p0, R0, p1, R1, ball, half, r):
    """Swept test of the (static) ball sphere against the head box moving between two substep poses. The ball centre is expressed in the head frame at both ends
    and the straight local path is tested against the box inflated by r (slab method). Returns a world contact point (box surface point nearest the ball) or None."""
    a = R0.T @ (ball - p0); b = R1.T @ (ball - p1); dvec = b - a; h = np.asarray(half, float) + r
    t0, t1 = 0.0, 1.0
    for k in range(3):
        if abs(dvec[k]) < 1e-12:
            if abs(a[k]) > h[k]: return None
        else:
            u0, u1 = (-h[k] - a[k]) / dvec[k], (h[k] - a[k]) / dvec[k]
            if u0 > u1: u0, u1 = u1, u0
            t0, t1 = max(t0, u0), min(t1, u1)
            if t0 > t1: return None
    loc = a + dvec * t0; cl = np.clip(loc, -np.asarray(half), np.asarray(half))
    Rm = R0 if t0 < 0.5 else R1; pm = p0 if t0 < 0.5 else p1
    return pm + Rm @ cl


class V5GolfEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, handed="LH", club_len=0.87, dt=0.0005, force_scale=1.0, ball_tol_m=0.0, max_s=2.0, post_contact_s=0.10, seed=0,
                 fall_height=0.45, log_segments=True, tether=False, tether_strength=0.0, contact_tol=0.0, friction_rand=False, detail_info=False, arm_dist=0.0):
        self.face_h = None   # K31: optional real driver face height (m, e.g. 0.053; Data Agent DRIVER_FACE_OFFCENTRE_REFS). If set, a head-ball contact whose offset from face centre along the face 'up' axis exceeds face_h/2 is an OFF-FACE MISS (ball disabled, episode ends, info foul=True, off_face=True). Default None = unchanged (head box half-height 0.032 m)
        self.strike_gate_nx = None   # Stage G: if set, a head-ball contact only counts when face normal x >= this, head v_x > 0 and v.n > 0; otherwise it is a FOUL (ball disabled, episode terminates, info foul=True); default off
        self.foul = False
        self.arm_back = 0.0   # >0 (with arm_dist>0): arming also requires the head to be >= arm_back m BEHIND the tee along -x (target is +x); default off
        self.arm_dist = arm_dist   # >0: ball contact is disabled until the club head has been >= arm_dist m from the tee (forces a real backswing; default 0 = off)
        self.detail_info = detail_info   # opt-in per-shot landing/impact logging (ENV_LANDING_LOGGING_SPEC); default off = info dict unchanged
        self.handed, self.club_len, self.force_scale = handed, club_len, force_scale
        self._dt_arg = dt
        self.tether_strength = tether_strength   # SOFT pelvis tether strength in [0,1] (curriculum aid, annealed to 0 = free). 0 at evaluation.
        self.contact_tol = contact_tol           # lenient-contact inflation of the ball radius (m) for the swept test (curriculum, annealed to 0)
        self.friction_rand = friction_rand
        self._init_model(club_len)
        self._finish_init(handed, force_scale, ball_tol_m, max_s, post_contact_s, seed, fall_height, log_segments, tether)

    def _init_model(self, club_len):
        handed, force_scale = self.handed, self.force_scale
        self.club_len = club_len
        self.addr = load_address(handed, club_len)
        self.m, _ = build_model(handed, club_len, dt=self._dt_arg, force_scale=force_scale, addr=self.addr)
        self._bind()

    def set_club_len(self, club_len):
        """Rebuild the model with a different club length (address JSON must exist: 0.87/0.95/1.05/1.15). Takes effect at the next reset."""
        if abs(club_len - self.club_len) > 1e-9:
            self._init_model(club_len); self.reset()

    def _finish_init(self, handed, force_scale, ball_tol_m, max_s, post_contact_s, seed, fall_height, log_segments, tether):
        m = self.m
        self.ball_tol = ball_tol_m; self.max_s = max_s; self.post_s = post_contact_s; self.fall_h = fall_height
        self.log_segments = log_segments; self.tether = tether
        self.rng = np.random.default_rng(seed)
        n_obs = 29 * 3 + 6 + 3 + 3 + 3 + 3 + 3 + 3 + 1
        self.observation_space = spaces.Box(-np.inf, np.inf, (n_obs,), np.float32)
        self.action_space = spaces.Box(-1.0, 1.0, (m.nu,), np.float32)
        self.toe_sign, _, self.toe_dot = verify_toe_sign(m, self._fk_addr(), handed)
        self.act_scale = np.full(m.nu, ACT_SCALE)
        self.reset()

    def _bind(self):
        handed, force_scale = self.handed, self.force_scale
        self.d = mujoco.MjData(self.m)
        m = self.m
        self.dt = m.opt.timestep; self.sub = int(round(CTRL_DT / self.dt)); self.seg_every = max(1, int(round(0.005 / self.dt)))
        self.names = [m.actuator(i).name for i in range(m.nu)]
        self.jid = np.array([m.joint(n).id for n in self.names]); self.qa = m.jnt_qposadr[self.jid]; self.da = m.jnt_dofadr[self.jid]
        self.q_addr = np.array([self.addr["joints"][n] for n in self.names])
        self.jlo, self.jhi = m.jnt_range[self.jid, 0], m.jnt_range[self.jid, 1]
        tv = np.array([STOCK[joint_kind(n)] for n in self.names], float)
        self.tau = tv[:, 0] * force_scale; self.vmax = tv[:, 1]
        self.lead, self.trail = lead_trail(handed)
        self.ball_q = int(m.jnt_qposadr[m.joint("ball_free").id]); self.ball_v = int(m.jnt_dofadr[m.joint("ball_free").id])
        self.head_site = m.site("clubhead").id; self.head_geom = m.geom("head").id; self.ball_geom = m.geom("ball_geom").id
        self.club_body = m.body("club").id; self.pel = m.body("pelvis").id; self.torso = m.body("torso_link").id
        self.sole_geoms = {s: m.geom(f"{s}_sole").id for s in ("left", "right")}
        self.floor = m.geom("floor").id
        self.lead_sh = [m.joint(f"{self.lead}_shoulder_{k}_joint").dofadr[0] for k in ("pitch", "roll", "yaw")]

    def _fk_addr(self):
        d = mujoco.MjData(self.m); set_address(self.m, d, self.addr); return d

    # ---------------- helpers
    def _vel_site(self, sid):
        v = np.zeros(6); mujoco.mj_objectVelocity(self.m, self.d, mujoco.mjtObj.mjOBJ_SITE, sid, v, 0); return v

    def foot_forces(self):
        """Vertical normal force on each sole from contacts with the floor (N). Returns (left, right)."""
        d, m = self.d, self.m
        f = {"left": 0.0, "right": 0.0}; fv = np.zeros(6)
        for i in range(d.ncon):
            c = d.contact[i]; g1, g2 = c.geom1, c.geom2
            for s, gid in self.sole_geoms.items():
                if (g1 == gid and g2 == self.floor) or (g2 == gid and g1 == self.floor):
                    mujoco.mj_contactForce(m, d, i, fv); f[s] += fv[0]
        return f["left"], f["right"]

    def _heading(self, body):
        x = self.d.xmat[body].reshape(3, 3)[:, 0]; return math.atan2(x[1], x[0])

    def _soft_tether(self):
        """Soft pelvis tether (curriculum aid, strength in [0,1], annealed to 0): spring-damper on pelvis position and orientation toward the address pose.
        Max gains at strength 1: 4000 N/m, 250 N*s/m, 400 N*m/rad, 25 N*m*s/rad (external support force, NOT joint torque)."""
        d = self.d; k = self.tether_strength
        f = k * (4000 * (self.pel_q0[0:3] - d.qpos[0:3]) - 250 * d.qvel[0:3])
        q, q0 = d.qpos[3:7], self.pel_q0[3:7]
        qc = np.zeros(4); mujoco.mju_negQuat(qc, q); dq = np.zeros(4); mujoco.mju_mulQuat(dq, q0, qc)   # world-frame error rotation q0*q^-1
        if dq[0] < 0: dq = -dq
        ang = 2 * dq[1:4]
        tq = k * (400 * ang - 25 * d.qvel[3:6])
        d.xfrc_applied[self.pel, :3] = f; d.xfrc_applied[self.pel, 3:] = tq

    def _derate(self):
        qd = self.d.qvel[self.da]
        hi = self.tau * np.clip(1 - np.maximum(qd, 0) / self.vmax, 0, 1)
        lo = -self.tau * np.clip(1 - np.maximum(-qd, 0) / self.vmax, 0, 1)
        self.m.actuator_forcerange[:, 0] = lo; self.m.actuator_forcerange[:, 1] = hi

    def reset(self, seed=None, options=None):
        if seed is not None: self.rng = np.random.default_rng(seed)
        d, m = self.d, self.m
        set_address(m, d, self.addr)
        if self.friction_rand:
            self.m.geom_friction[self.floor, 0] = self.rng.uniform(0.5, 1.2)       # foot/floor sliding friction randomisation
        off = (self.rng.uniform(-1, 1, 2) * self.ball_tol) if self.ball_tol > 0 else np.zeros(2)
        self.tee = np.array(self.addr["ball_pos"], float); self.tee[:2] += off
        d.qpos[self.ball_q:self.ball_q + 3] = self.tee
        self.armed = self.arm_dist <= 0
        m.geom_contype[self.ball_geom] = 2 if self.armed else 0; m.geom_conaffinity[self.ball_geom] = 2 if self.armed else 0
        d.ctrl[:] = self.q_addr
        mujoco.mj_forward(m, d)
        self.pel_q0 = d.qpos[0:7].copy()
        self.contact = False; self.t_contact = None; self.shot = None; self.steps = 0; self.after = 0.0
        self.prev_v = np.zeros(3); self.last_act = np.zeros(m.nu)
        self.log = dict(t=[], pelvis=[], thorax=[], lead_arm=[], club=[], xfactor_deg=[], lead_share=[]); self.peak_club_speed = 0.0
        self.max_weld_drift = 0.0; self.pre_contact_head_speed = 0.0
        self.sub_count = 0; self.min_dist = 9.0
        self.ball_hit_info = None; self.foul = False; self.off_face = False
        return self._obs(), {}

    def _obs(self):
        d = self.d; Rp = d.xmat[self.pel].reshape(3, 3)
        q = d.qpos[self.qa]; qd = d.qvel[self.da]
        head = d.site_xpos[self.head_site]; hv = self._vel_site(self.head_site)[3:]
        rel = lambda v: Rp.T @ v
        shaft = d.xmat[self.club_body].reshape(3, 3)[:, 2]
        fl, fr = self.foot_forces(); tot = max(fl + fr, 1e-6)
        o = np.concatenate([q - self.q_addr, qd * 0.1, self.last_act, Rp[:, :2].T.ravel(), rel(d.qvel[3:6]) * 0.1, rel(head - d.xpos[self.pel]), rel(hv) * 0.05,
                            rel(shaft), rel(d.qpos[self.ball_q:self.ball_q + 3] - head), [fl / tot, fr / tot, 0.0][:3], [self.steps * self.sub * self.dt]])
        return o.astype(np.float32)[: self.observation_space.shape[0]] if len(o) >= self.observation_space.shape[0] else np.pad(o, (0, self.observation_space.shape[0] - len(o))).astype(np.float32)

    def _log_seg(self):
        d = self.d; m = self.m
        ang = lambda b: d.cvel[b][:3] if False else None
        pw = np.zeros(6); mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_BODY, self.pel, pw, 0)
        tw = np.zeros(6); mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_BODY, self.torso, tw, 0)
        cw = np.zeros(6); mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_BODY, self.club_body, cw, 0)
        L = self.log
        L["t"].append(d.time)
        L["pelvis"].append(abs(math.degrees(pw[2]))); L["thorax"].append(abs(math.degrees(tw[2])))
        L["lead_arm"].append(math.degrees(float(np.linalg.norm(d.qvel[self.lead_sh]))))
        L["club"].append(math.degrees(float(np.linalg.norm(cw[:3]))))
        xf = math.degrees((self._heading(self.torso) - self._heading(self.pel) + math.pi) % (2 * math.pi) - math.pi)
        L["xfactor_deg"].append(xf)
        fl, fr = self.foot_forces(); tot = max(fl + fr, 1e-6)
        L["lead_share"].append((fl if self.lead == "left" else fr) / tot)

    def _check_contact(self):
        d = self.d
        for i in range(d.ncon):
            c = d.contact[i]
            if (c.geom1 == self.head_geom and c.geom2 == self.ball_geom) or (c.geom2 == self.head_geom and c.geom1 == self.ball_geom):
                return c.pos.copy()
        return None

    def _do_contact(self, cpos):
        d, m = self.d, self.m
        R = d.geom_xmat[self.head_geom].reshape(3, 3)
        n = R[:, 0].copy(); toe = R[:, 1].copy()
        up = np.cross(n, toe); up = up if up[2] >= 0 else -up
        face_ctr = d.site_xpos[self.head_site]
        r = cpos - face_ctr
        dy, dz = float(np.dot(r, toe)), float(np.dot(r, up))
        res = shot_from_contact(self.prev_v, n, dy, dz, handed=self.handed, toe_sign=self.toe_sign, ball_z=float(self.tee[2]))
        self.shot = res; self.contact = True; self.t_contact = d.time
        self.ball_hit_info = dict(dy=dy, dz=dz, club_speed=float(np.linalg.norm(self.prev_v)), face_normal=n.tolist())
        m.geom_contype[self.ball_geom] = 0; m.geom_conaffinity[self.ball_geom] = 0
        d.qvel[self.ball_v:self.ball_v + 3] = res["v_ball"]
        Rb = d.xmat[m.body("ball").id].reshape(3, 3)
        d.qvel[self.ball_v + 3:self.ball_v + 6] = Rb.T @ res["omega_ball"]

    def step(self, action):
        d, m = self.d, self.m
        a = np.clip(np.asarray(action, float), -1, 1)
        self.last_act = a
        tgt = np.clip(self.q_addr + a * self.act_scale, self.jlo, self.jhi)
        d.ctrl[:] = tgt
        for k in range(self.sub):
            if self.sub_count % 10 == 0: self._derate()   # every 5 ms of sim time (independent of control rate)
            if self.tether_strength > 0: self._soft_tether()
            if not self.contact:
                d.qpos[self.ball_q:self.ball_q + 3] = self.tee; d.qvel[self.ball_v:self.ball_v + 6] = 0
                hp = d.site_xpos[self.head_site]; dist = np.linalg.norm(hp - self.tee); self.min_dist = min(self.min_dist, dist)
                if not self.armed and dist >= self.arm_dist and (self.tee[0] - hp[0]) >= self.arm_back:
                    self.armed = True; m.geom_contype[self.ball_geom] = 2; m.geom_conaffinity[self.ball_geom] = 2
                if dist < FAR and self.armed:
                    self.prev_v = self._vel_site(self.head_site)[3:].copy()
                    pre_pos = d.geom_xpos[self.head_geom].copy(); pre_R = d.geom_xmat[self.head_geom].reshape(3, 3).copy(); swept = True
                else: swept = False
            else: swept = False
            mujoco.mj_step(m, d); self.sub_count += 1
            if self.tether:
                d.qpos[0:7] = self.pel_q0; d.qvel[0:6] = 0
            if not self.contact and swept:
                cp = self._check_contact()
                if cp is None: cp = swept_hit(pre_pos, pre_R, d.geom_xpos[self.head_geom], d.geom_xmat[self.head_geom].reshape(3, 3), self.tee,
                                              self.m.geom_size[self.head_geom], R_BALL_E)
                if cp is not None:
                    if self.strike_gate_nx is not None:
                        n_ = d.geom_xmat[self.head_geom].reshape(3, 3)[:, 0]; v_ = self.prev_v
                        if not (n_[0] >= self.strike_gate_nx and v_[0] > 0 and float(np.dot(v_, n_)) > 0):
                            self.foul = True; m.geom_contype[self.ball_geom] = 0; m.geom_conaffinity[self.ball_geom] = 0; self.foul_info = dict(n=n_.tolist(), v=v_.tolist()); break
                    if self.face_h is not None:
                        R_ = d.geom_xmat[self.head_geom].reshape(3, 3); n2 = R_[:, 0]; up_ = np.cross(n2, R_[:, 1]); up_ = up_ if up_[2] >= 0 else -up_
                        dz_ = float(np.dot(cp - d.site_xpos[self.head_site], up_))
                        if abs(dz_) > 0.5 * self.face_h:
                            self.foul = True; self.off_face = True; m.geom_contype[self.ball_geom] = 0; m.geom_conaffinity[self.ball_geom] = 0; self.foul_info = dict(off_face_dz=dz_); break
                    self._do_contact(cp)
            if self.log_segments and self.sub_count % self.seg_every == 0: self._log_seg()
        self.steps += 1
        if self.contact: self.after = d.time - self.t_contact
        fell = d.qpos[2] < self.fall_h or not np.all(np.isfinite(d.qpos))
        # weld drift: distance between hand sites and grip sites
        for s, gs in ((self.lead, "grip_lead"), (self.trail, "grip_trail")):
            dd = np.linalg.norm(d.site_xpos[m.site(f"{s}_hand").id] - d.site_xpos[m.site(gs).id]); self.max_weld_drift = max(self.max_weld_drift, dd)
        term = fell or self.foul or (self.contact and self.after >= self.post_s)
        trunc = d.time >= self.max_s
        info = dict(contact=self.contact, fell=bool(fell), weld_drift_max_m=self.max_weld_drift, foul=bool(self.foul))
        if self.contact:
            sh = self.shot["shot"]
            info.update(carry_m_noroll=sh.carry_m, total_m_model=sh.total_m, lateral_carry_m=sh.lateral_carry_m, launch_deg=self.shot["launch_deg"],
                        spin_rpm=sh.spin_rpm, smash=self.shot["smash"], ball_speed_mph=self.shot["ball_speed"] / 0.44704,
                        club_speed_mph=self.ball_hit_info["club_speed"] / 0.44704, azimuth_deg=float(self.shot.get("azimuth_deg", 0.0) or 0.0), **{k: self.ball_hit_info[k] for k in ("dy", "dz")})
        if self.contact and self.detail_info:
            hs = 1.0 if self.handed.upper().startswith("R") else -1.0       # golfer frame: y-derived angles x hand_sign (+ = left of target)
            n = np.asarray(self.ball_hit_info["face_normal"]); v = self.prev_v
            info.update(landing_time_s=sh.hang_s, landing_y_m=sh.lateral_carry_m, landing_spin_rpm=sh.landing_spin_rpm, landing_speed_mps=sh.land_speed_ms,
                        descent_deg=sh.descent_deg, apex_m=sh.apex_m, spin_axis_deg=sh.spin_axis_deg, backspin_rpm=sh.backspin_rpm, sidespin_rpm=sh.sidespin_rpm,
                        face_yaw_deg=math.degrees(math.atan2(n[1], n[0])) * hs, dynamic_loft_deg=math.degrees(math.asin(float(np.clip(n[2], -1, 1)))),
                        club_path_deg=math.degrees(math.atan2(v[1], v[0])) * hs, aoa_deg=math.degrees(math.atan2(v[2], math.hypot(v[0], v[1]))),
                        carry_frame="golfphys relative to ball start (NOT absolute x), no roll")
        return self._obs(), 0.0, bool(term), bool(trunc and not term), info
