"""Harness v4.1 re-grounding (NON-GATING info row; Orchestrator decision 2026-10-25). v4 stays the official gate, unchanged.

Why: the v4 robustness perturbation is meant to be posture noise only (eval/robust_grf.py header). v4 applies it as qpos offsets on the actuated
joints + mj_forward with no re-grounding (results/overnight/_j_worker_gp_v3.py, `if PERT:` block), so leg-joint noise with a fixed floating base moves
the feet: the lead sole shifts ~1 cm sideways at takeaway (Trainer finding: lead-foot lateral shift r -.64 with strike dy). A real golfer would
re-address the ball. v4.1 = the same perturbation (same seeds, same joint/velocity noise draws, ball offset, friction), then the feet are put back.

Method (reground()): after the noise + mj_forward, damped-least-squares IK over the floating base (6 dof) and the 12 leg joint dofs only, driving
both sole sites ({left,right}_sole_site) back to their UNPERTURBED address world position and orientation (6-D error per foot, 12 equations,
18 unknowns -> minimum-norm change from the perturbed posture, so leg noise is only partly removed and waist/arm/wrist noise is kept exactly).
Leg joints are clipped to their ranges. The club free body is moved by the same rigid transform as the floating base, so the hand-club relation
is exactly what v4 produced (hands depend only on base + waist/arm joints). The ball/tee is untouched. Base qvel is set to 0 (it is 0 after reset
anyway; actuated joint velocity noise is kept). Converges in a few iterations; residuals are recorded per episode (perturb.reground)."""
import numpy as np
import mujoco

TOL_POS_M = 1e-3   # target: soles within ~1 mm of the unperturbed address
LEG_JOINTS = tuple(f"{s}_{j}_joint" for s in ("left", "right") for j in ("hip_pitch", "hip_roll", "hip_yaw", "knee", "ankle_pitch", "ankle_roll"))
SOLES = ("left_sole_site", "right_sole_site")

def sole_poses(m, d):
    return [(d.site_xpos[m.site(s).id].copy(), d.site_xmat[m.site(s).id].reshape(3, 3).copy()) for s in SOLES]

def _rot_err(Rt, R):   # axis-angle vector rotating R onto Rt (world frame)
    qt, q, qi, qe, v = np.zeros(4), np.zeros(4), np.zeros(4), np.zeros(4), np.zeros(3)
    mujoco.mju_mat2Quat(qt, Rt.ravel()); mujoco.mju_mat2Quat(q, R.ravel()); mujoco.mju_negQuat(qi, q); mujoco.mju_mulQuat(qe, qt, qi)
    mujoco.mju_quat2Vel(v, qe, 1.0); return v

def residual(m, d, target):
    """(max sole position error m, max sole orientation error deg, per-sole xyz displacement) vs target sole poses."""
    P = sole_poses(m, d); dp = [P[i][0] - target[i][0] for i in range(2)]
    return float(max(np.linalg.norm(x) for x in dp)), float(max(np.degrees(np.linalg.norm(_rot_err(target[i][1], P[i][1]))) for i in range(2))), [x.tolist() for x in dp]

def reground(m, d, target, iters=50, damp=1e-4):
    """IK as in the module docstring. target = sole_poses() at the unperturbed address. Returns a stats dict (before/after residuals)."""
    fb = m.joint("floating_base_joint"); bq, bv = int(fb.qposadr[0]), int(fb.dofadr[0])
    cj = m.joint("club_free"); cq = int(cj.qposadr[0])
    legs = [m.joint(n) for n in LEG_JOINTS]; cols = [bv + k for k in range(6)] + [int(j.dofadr[0]) for j in legs]
    root0 = d.qpos[bq:bq + 7].copy(); club0 = d.qpos[cq:cq + 7].copy()
    mujoco.mj_forward(m, d); b_pos, b_rot, b_dp = residual(m, d, target)
    sids = [m.site(s).id for s in SOLES]; jp, jr = np.zeros((3, m.nv)), np.zeros((3, m.nv)); it = 0
    for it in range(1, iters + 1):
        err, J = [], []
        for i, s in enumerate(sids):
            err += [target[i][0] - d.site_xpos[s], _rot_err(target[i][1], d.site_xmat[s].reshape(3, 3))]
            mujoco.mj_jacSite(m, d, jp, jr, s); J += [jp[:, cols].copy(), jr[:, cols].copy()]
        e = np.concatenate(err); J = np.vstack(J)
        if np.abs(e).max() < 1e-6: break
        dx = J.T @ np.linalg.solve(J @ J.T + damp * np.eye(len(e)), e); v = np.zeros(m.nv); v[cols] = dx
        mujoco.mj_integratePos(m, d.qpos, v, 1.0)
        for j in legs: a = int(j.qposadr[0]); d.qpos[a] = np.clip(d.qpos[a], *m.jnt_range[j.id])
        mujoco.mj_forward(m, d)
    # club: same rigid transform as the base (T_new * T_old^-1)
    r1 = d.qpos[bq:bq + 7]; qi, qd, qc = np.zeros(4), np.zeros(4), np.zeros(4); mujoco.mju_negQuat(qi, root0[3:]); mujoco.mju_mulQuat(qd, r1[3:], qi)
    pc = np.zeros(3); mujoco.mju_rotVecQuat(pc, club0[:3] - root0[:3], qd); mujoco.mju_mulQuat(qc, qd, club0[3:])
    d.qpos[cq:cq + 3] = r1[:3] + pc; d.qpos[cq + 3:cq + 7] = qc / np.linalg.norm(qc)
    d.qvel[bv:bv + 6] = 0.0; mujoco.mj_forward(m, d); a_pos, a_rot, a_dp = residual(m, d, target)
    return dict(method="DLS IK over floating base + 12 leg dofs to unperturbed sole poses; club moved with the base; base qvel 0", iters=it,
                before=dict(pos_max_m=b_pos, rot_max_deg=b_rot, dxyz_m=b_dp), after=dict(pos_max_m=a_pos, rot_max_deg=a_rot, dxyz_m=a_dp),
                base_shift_m=(d.qpos[bq:bq + 3] - root0[:3]).tolist())
