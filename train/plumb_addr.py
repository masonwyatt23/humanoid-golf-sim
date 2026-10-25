"""--plumb_addr (DREnv, default off): plumb address on a gravity-tilt slope. LOCAL, NOT OFFICIAL.
DREnv models a slope by tilting gravity over the flat world floor; the v4 address pose is solved perpendicular to the floor, so on a slope the
golfer starts leaning by atan(grade) (slope_diag: V10l 0/5 contacts at 8-10%). With the flag, at reset of an ADDRESS start (mode 0):
  1. the whole upper system (free base + club free body) is rotated rigidly by R (world +z -> -g_hat) about the ball centre, so the body's
     vertical axis is gravity-aligned and the club/ball relation at address is unchanged (ball/tee stay on the tilted ground = world floor);
  1b. if the rotated club head penetrates the floor, base+club are lifted vertically until it clears (+0.2 mm; logged club_lift_mm);
  2. each leg's 6 joints (hip p/r/y, knee, ankle p/r) are solved by damped least squares so both sole sites keep their original world pose
     (soles flat on the floor, same seating/penetration as flat);
  3. the joint offsets delta = q_new - q_old (legs only) are added to the reference q(t) for the whole episode (PlumbRef), so PD targets are
     consistent with the plumb base. Mid-swing RSI starts (mode 1/2) are NOT corrected (their pre-roll already ran under the tilt)."""
import numpy as np, mujoco

class PlumbRef:
    def __init__(self, base, delta): self._plumb_base = base; self._delta = np.asarray(delta, float)
    def q(self, t): return self._plumb_base.q(t) + self._delta
    def __getattr__(self, k): return getattr(self._plumb_base, k)

def _rot_z_to(u):
    z = np.array([0.0, 0.0, 1.0]); ax = np.cross(z, u); s = np.linalg.norm(ax); c = float(np.dot(z, u)); q = np.zeros(4)
    if s < 1e-9: q[0] = 1.0; return q, 0.0
    mujoco.mju_axisAngle2Quat(q, ax / s, float(np.arctan2(s, c))); return q, float(np.arctan2(s, c))

def apply_plumb(den, iters=300, tol=1e-7):
    e = den.env; m, d = e.m, e.d; g = np.asarray(m.opt.gravity, float); u = -g / np.linalg.norm(g)
    qR, ang = _rot_z_to(u)
    if ang < 1e-6 or getattr(den, "mode", 0) != 0: den.plumb_log = dict(applied=False, ang_deg=float(np.degrees(ang))); return
    mujoco.mj_kinematics(m, d)
    soles = [m.site(f"{s}_sole_site").id for s in ("left", "right")]
    tgt = [(d.site_xpos[s].copy(), d.site_xmat[s].copy()) for s in soles]
    R = np.zeros(9); mujoco.mju_quat2Mat(R, qR); R = R.reshape(3, 3); c = np.asarray(e.tee, float).copy()
    q_old = d.qpos.copy()
    for jn in ("floating_base_joint", "club_free"):
        a = m.jnt_qposadr[m.joint(jn).id]; p = d.qpos[a:a + 3].copy(); d.qpos[a:a + 3] = c + R @ (p - c)
        qn = np.zeros(4); mujoco.mju_mulQuat(qn, qR, d.qpos[a + 3:a + 7].copy()); d.qpos[a + 3:a + 7] = qn / np.linalg.norm(qn)
    mujoco.mj_forward(m, d); fl = getattr(e, "floor", None); pen = 0.0   # club head may dip into the floor after the rotation -> lift base+club vertically until it clears (+0.2 mm)
    for i in range(d.ncon):
        cc = d.contact[i]
        if fl in (cc.geom1, cc.geom2) and m.body(m.geom_bodyid[cc.geom2 if cc.geom1 == fl else cc.geom1]).name == "club": pen = min(pen, float(cc.dist))
    lift = (-pen + 2e-4) if pen < 0 else 0.0
    for jn in ("floating_base_joint", "club_free"): d.qpos[m.jnt_qposadr[m.joint(jn).id] + 2] += lift
    res = []
    for side, s, (pt, Rt) in zip(("left", "right"), soles, tgt):
        js = [m.joint(f"{side}_{n}_joint").id for n in ("hip_pitch", "hip_roll", "hip_yaw", "knee", "ankle_pitch", "ankle_roll")]
        qa = np.array([m.jnt_qposadr[j] for j in js]); da = np.array([m.jnt_dofadr[j] for j in js]); lo = m.jnt_range[js, 0]; hi = m.jnt_range[js, 1]
        jp = np.zeros((3, m.nv)); jr = np.zeros((3, m.nv)); qt = np.zeros(4); mujoco.mju_mat2Quat(qt, Rt)
        for _ in range(iters):
            mujoco.mj_kinematics(m, d); mujoco.mj_comPos(m, d)
            ep = pt - d.site_xpos[s]; qc = np.zeros(4); mujoco.mju_mat2Quat(qc, d.site_xmat[s]); er = np.zeros(3); mujoco.mju_subQuat(er, qt, qc)
            er = d.site_xmat[s].reshape(3, 3) @ er   # subQuat gives the error in the current site frame -> world
            err = np.concatenate([ep, er])
            if float(err @ err) < tol ** 2: break
            mujoco.mj_jacSite(m, d, jp, jr, s); J = np.vstack([jp[:, da], jr[:, da]])
            dq = J.T @ np.linalg.solve(J @ J.T + 1e-4 * np.eye(6), err); n_ = np.abs(dq).max(); dq = dq * min(1.0, 0.05 / max(n_, 1e-12)); d.qpos[qa] = np.clip(d.qpos[qa] + dq, lo, hi)
        mujoco.mj_kinematics(m, d); res.append(float(np.linalg.norm(pt - d.site_xpos[s])))
    d.qvel[:] = 0.0; mujoco.mj_forward(m, d)
    delta = d.qpos[e.qa] - q_old[e.qa]
    den.ref = PlumbRef(den.ref, delta); e.q_addr = den.ref.q(d.time); d.ctrl[:] = e.q_addr
    den.plumb_log = dict(applied=True, ang_deg=round(float(np.degrees(ang)), 3), club_lift_mm=round(lift * 1e3, 2), sole_pos_res_mm=[round(r * 1e3, 4) for r in res], max_leg_delta_deg=round(float(np.degrees(np.abs(delta).max())), 3))
