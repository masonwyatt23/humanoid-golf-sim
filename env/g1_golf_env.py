"""Unitree G1 (29-DoF, MuJoCo Menagerie, BSD-3) + driver club golf env with actuator-tier knobs.

Honest scope: pelvis is a vertical-axis yaw hinge (stand-in for planted-foot hip yaw of both legs, torque = 2x hip-yaw);
all leg joints are held rigid by PD; the robot cannot fall. Club: 0.27 kg (shaft+grip 0.07, head 0.20), 1.15 m, left hand
soft-tied to the shaft 12 cm below the right hand. Ball on an invisible tee (held until first club contact).

Tiers (torque N*m, speed rad/s). 'stock' = Menagerie/Unitree numbers as used in scripts/g1_club_speed_feasibility.py.
'elite' = HYPOTHETICAL robot (NOT an existing product): hips/waist 250 N*m & 45 rad/s (pelvis proxy = 2 hips = 500),
shoulders/elbow 75 N*m & 55 rad/s, wrists 30 N*m (speed 55 rad/s assumed).
Torque-speed curve: torque scales linearly to 0 at the rated speed (in the direction of motion).
"""
import numpy as np
import mujoco
from pathlib import Path
from gymnasium import spaces
import gymnasium as gym

import os
MENAG = os.environ.get("MENAGERIE_DIR") or str(Path(__file__).resolve().parents[2] / "menagerie")   # default: MuJoCo Menagerie checked out next to this repo
CLUB_LEN, GRIP_SEP, SHAFT_M, HEAD_M = 1.15, 0.12, 0.07, 0.20
DT = 0.0005
CTRL_DT = 0.02
SUBSTEPS = int(round(CTRL_DT / DT))

ARM = ["shoulder_pitch", "shoulder_roll", "shoulder_yaw", "elbow", "wrist_roll", "wrist_pitch", "wrist_yaw"]


def tier_limits(tier):
    if tier == "stock":
        hip, waist, sh, wr_r, wr_py = (176, 32), (88, 32), (25, 37), (25, 37), (5, 22)
        wp = (50, 32)
    elif tier == "elite":  # HYPOTHETICAL
        hip, waist, sh, wr_r, wr_py = (500, 45), (250, 45), (75, 55), (30, 55), (30, 55)
        wp = (250, 45)
    else:
        raise ValueError(tier)
    L = {"pelvis_yaw": hip, "waist_yaw_joint": waist, "waist_roll_joint": wp, "waist_pitch_joint": wp}
    for side in ("left", "right"):
        for j in ("shoulder_pitch", "shoulder_roll", "shoulder_yaw", "elbow"):
            L[f"{side}_{j}_joint"] = sh
        L[f"{side}_wrist_roll_joint"] = wr_r
        L[f"{side}_wrist_pitch_joint"] = wr_py
        L[f"{side}_wrist_yaw_joint"] = wr_py
    return L


def build_model():
    spec = mujoco.MjSpec.from_file(f"{MENAG}/unitree_g1/scene.xml")
    for k in list(spec.keys):
        spec.delete(k)
    spec.option.timestep = DT
    pel = spec.body("pelvis")
    for j in list(pel.joints):
        spec.delete(j)
    pel.add_joint(name="pelvis_yaw", type=mujoco.mjtJoint.mjJNT_HINGE, axis=[0, 0, 1], range=[-1.6, 1.6], limited=True,
                  damping=1.0, armature=0.5)
    for g in spec.geoms:
        if g.name != "floor":
            g.contype = 0; g.conaffinity = 0
    rw = spec.body("right_wrist_yaw_link")
    club = rw.add_body(name="club", pos=[0.10, 0, 0])
    club.add_geom(name="shaft", type=mujoco.mjtGeom.mjGEOM_CAPSULE, fromto=[0, 0, 0.20 - CLUB_LEN, 0, 0, 0.20], size=[0.008, 0, 0],
                  mass=SHAFT_M, contype=0, conaffinity=0, rgba=[.2, .2, .2, 1])
    club.add_geom(name="head", type=mujoco.mjtGeom.mjGEOM_BOX, pos=[0.03, 0, 0.20 - CLUB_LEN], size=[0.04, 0.05, 0.03], mass=HEAD_M,
                  contype=2, conaffinity=2, solref=[0.002, 1], solimp=[0.95, 0.99, 0.001, 0.5, 2], friction=[0.5, 0.01, 0.001], rgba=[.7, .7, .75, 1])
    club.add_site(name="grip_left", pos=[0, 0, -GRIP_SEP])
    club.add_site(name="clubhead", pos=[0.03, 0, 0.20 - CLUB_LEN])
    lw = spec.body("left_wrist_yaw_link")
    lw.add_site(name="lhand", pos=[0.10, 0, 0])
    eq = spec.add_equality(name="left_grip", type=mujoco.mjtEq.mjEQ_CONNECT, objtype=mujoco.mjtObj.mjOBJ_SITE, name1="lhand", name2="grip_left")
    eq.solref = [0.01, 1]
    ball = spec.worldbody.add_body(name="ball", pos=[0.5, 0.0, 0.07])
    ball.add_freejoint()
    ball.add_geom(name="ball_geom", type=mujoco.mjtGeom.mjGEOM_SPHERE, size=[0.021, 0, 0], mass=0.046, contype=3, conaffinity=3,
                  solref=[0.002, 1], solimp=[0.95, 0.99, 0.001, 0.5, 2], friction=[0.5, 0.01, 0.001])
    spec.add_actuator(name="pelvis_yaw", target="pelvis_yaw", trntype=mujoco.mjtTrn.mjTRN_JOINT, gear=[1, 0, 0, 0, 0, 0])
    model = spec.compile()
    # all actuators become direct torque motors (ctrl = N*m); PD + limits are computed in python
    model.actuator_gainprm[:, 0] = 1.0
    model.actuator_biasprm[:, :] = 0.0
    model.actuator_forcerange[:] = 0.0
    model.actuator_forcelimited[:] = 0
    model.actuator_ctrllimited[:] = 0
    model.actuator_gear[:, 0] = 1.0
    # joint-level actuatorfrcrange from Menagerie would clip; disable (we apply tier limits ourselves)
    model.jnt_actfrclimited[:] = 0
    return model


POSES = None


def load_poses():
    global POSES
    if POSES is None:
        import json
        POSES = json.load(open(Path(__file__).parent / "g1_poses.json"))
    return POSES


class G1Swing:
    """Scripted swing + torque-limited PD simulation core (no gym). Used for feasibility and by G1GolfEnv."""

    def __init__(self, tier="stock", impact_key="impact_0.3_0.4", kp=400.0, kd=15.0, t_back=0.8, t_hold=0.05, t_down=0.25,
                 follow=0.6, ease=1.5, ball_pos=(0.5, 0.0, 0.07), flight=False, cmd_gain=1.0):
        self.m = build_model(); self.d = mujoco.MjData(self.m)
        self.tier = tier; self.lim = tier_limits(tier)
        P = load_poses()
        self.names = [self.m.actuator(i).name for i in range(self.m.nu)]
        self.qa = {}; self.da = {}
        for n in self.names:
            j = self.m.joint(n).id; self.qa[n] = int(self.m.jnt_qposadr[j]); self.da[n] = int(self.m.jnt_dofadr[j])
        self.rng = {n: self.m.jnt_range[self.m.joint(n).id].copy() for n in self.names}
        base = {n: float(self.m.qpos0[self.qa[n]]) for n in self.names}
        self.addr = dict(base, **{k: v for k, v in P["address"].items()})
        self.imp = dict(base, **{k: v for k, v in P[impact_key].items() if not k.startswith("_")})
        self.top = dict(base, **{k: v for k, v in P["top"].items()})
        self.kp, self.kd = kp, kd
        self.t_back, self.t_hold, self.t_down, self.follow, self.ease = t_back, t_hold, t_down, follow, ease
        self.ball_pos = np.array(ball_pos, float)
        self.head = mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_SITE, "clubhead")
        self.ball_bid = self.m.body("ball").id
        self.ball_q = int(self.m.jnt_qposadr[self.m.body_jntadr[self.ball_bid]])
        self.ball_v = int(self.m.jnt_dofadr[self.m.body_jntadr[self.ball_bid]])
        self.head_geom = self.m.geom("head").id; self.ball_geom = self.m.geom("ball_geom").id
        self.T = t_hold + t_back + 0.08 + t_down + 0.25
        self.flight = flight
        self.speed_scale = 1.0

    def target(self, t):
        a, tp, im = self.addr, self.top, self.imp
        t1 = self.t_hold; t2 = t1 + self.t_back; t3 = t2 + 0.08; t4 = t3 + self.t_down
        out = {}
        for n in self.names:
            if t < t1: v = a[n]
            elif t < t2:
                u = (t - t1) / self.t_back; s = u * u * (3 - 2 * u); v = a[n] + (tp[n] - a[n]) * s
            elif t < t3: v = tp[n]
            elif t < t4:
                u = (t - t3) / self.t_down; v = tp[n] + (im[n] - tp[n]) * u ** self.ease
            else:
                u = (t - t4) / self.t_down; slope = self.ease  # derivative of u^ease at 1
                v = im[n] + (im[n] - tp[n]) * slope * min(u, self.follow / max(slope, 1e-6) * 1.0 + u * 0)* 1.0
            out[n] = float(np.clip(v, self.rng[n][0], self.rng[n][1]))
        return out

    def reset(self):
        d, m = self.d, self.m
        mujoco.mj_resetData(m, d)
        d.qpos[:] = m.qpos0
        for n in self.names: d.qpos[self.qa[n]] = self.addr[n]
        d.qpos[self.ball_q:self.ball_q + 3] = self.ball_pos
        d.qpos[self.ball_q + 3:self.ball_q + 7] = [1, 0, 0, 0]
        mujoco.mj_forward(m, d)
        self.t = 0.0; self.contact = False; self.impact_speed = 0.0; self.prev_speed = 0.0; self.peak_speed = 0.0
        self.peak_joint_speed = {n: 0.0 for n in self.names}

    def _head_speed(self):
        v = np.zeros(6); mujoco.mj_objectVelocity(self.m, self.d, mujoco.mjtObj.mjOBJ_SITE, self.head, v, 0)
        return float(np.linalg.norm(v[3:]))

    def torque(self, tgt):
        d = self.d; ctrl = np.zeros(self.m.nu)
        for i, n in enumerate(self.names):
            q, qd = d.qpos[self.qa[n]], d.qvel[self.da[n]]
            tau = self.kp * (tgt[n] - q) - self.kd * qd
            lim = self.lim.get(n)
            if lim is None:  # legs: held rigid, no tier limit
                tau = np.clip(self.kp * 3 * (tgt[n] - q) - self.kd * 3 * qd, -200, 200)
            else:
                tl, vl = lim; s = np.sign(tau)
                if s * qd > 0: tau = tau * max(0.0, 1 - abs(qd) / vl)   # linear torque-speed derate toward rated speed
                tau = float(np.clip(tau, -tl, tl))
            ctrl[i] = tau
        return ctrl

    def run(self, T=None, hold_ball=True):
        T = self.T if T is None else T
        self.reset(); d, m = self.d, self.m
        tee = self.ball_pos.copy()
        ts = m.opt.timestep
        k = 0
        while k * ts < T:
            tt = k * ts
            if k % 40 == 0: tgt = self.target(tt)   # script updated at 50 Hz
            d.ctrl[:] = self.torque(tgt)
            if hold_ball and not self.contact:
                d.qpos[self.ball_q:self.ball_q + 3] = tee; d.qvel[self.ball_v:self.ball_v + 6] = 0
            mujoco.mj_step(m, d); k += 1
            hs = self._head_speed(); self.peak_speed = max(self.peak_speed, hs)
            if not self.contact:
                for i in range(d.ncon):
                    if {d.contact[i].geom1, d.contact[i].geom2} == {self.head_geom, self.ball_geom}:
                        self.contact = True; self.impact_speed = max(self.prev_speed, hs); self.t_contact = tt
                self.prev_speed = hs
            for n in self.names: self.peak_joint_speed[n] = max(self.peak_joint_speed[n], abs(d.qvel[self.da[n]]))
            if not np.all(np.isfinite(d.qvel)): break
        return dict(contact=self.contact, impact=self.impact_speed, peak=self.peak_speed,
                    ball_v=d.qvel[self.ball_v:self.ball_v + 3].copy(), ball_pos=d.qpos[self.ball_q:self.ball_q + 3].copy())
