"""v5 body builder: Unitree G1 (Menagerie, BSD-3) full body, physically mirrored LEFT-handed golfer, club rigidly welded into both hands,
foot-ground contact with friction, foot force sensors, STOCK torque limits (force_scale 1). Stage 0 of docs/FROM_SCRATCH_SWING_PLAN.md.

Labels: [read] = read from Menagerie g1.xml (actuatorfrcrange, joint ranges); [plan] = value from the plan table; [guess] = my assumption.
New file: does not touch v3/v4 (env/humanoid_golf_env.py, env/models/*) or env/g1_golf_env.py.

Frames: world +x = target line, +y = LEFT of the line, +z up. G1 faces +x in its own frame.
 LH golfer: yaw +90 deg so the golfer FACES +y, its physical RIGHT side points to the target (+x): lead arm = physical right, trail = physical left.
 RH golfer (for the mirror test only): yaw -90 deg, faces -y, physical LEFT side points to the target: lead arm = physical left.
Club frame (LH): origin = lead grip top, local -z toward the head along the shaft, local +x = face direction, local +y = toe side.
"""
import os, json, math
import numpy as np
import mujoco
from scipy.optimize import least_squares

MENAG = os.environ.get("MENAGERIE_DIR", "/workspace/menagerie")
DT = 0.0005
CTRL_DT = 0.02

# Stock tier: torque from Menagerie g1.xml actuatorfrcrange [read]; rated no-load speed from the plan table section 3 (Unitree motor classes,
# [plan]/[published, not re-fetched]); ankle speed and waist roll/pitch speed are [guess]. Torque falls linearly to 0 at rated speed (as g1_golf_env).
#            torque N*m [read]   speed rad/s
STOCK = {
    "hip_pitch": (88, 32), "hip_roll": (139, 20), "hip_yaw": (88, 32), "knee": (139, 20), "ankle_pitch": (50, 37), "ankle_roll": (50, 37),
    "waist_yaw": (88, 32), "waist_roll": (50, 20), "waist_pitch": (50, 20),
    "shoulder_pitch": (25, 37), "shoulder_roll": (25, 37), "shoulder_yaw": (25, 37), "elbow": (25, 37),
    "wrist_roll": (25, 37), "wrist_pitch": (5, 22), "wrist_yaw": (5, 22),
}
LOFT_DEG, LIE_DEG = 10.5, 56.0        # driver loft [guess typical]; lie [guess typical 56-60]
SHAFT_BELOW_GRIP = 0.11               # trail hand below lead hand [plan: 0.10-0.12]
HEAD_M, SHAFT_M = 0.20, 0.10          # head 200 g (matches golfphys m_head), shaft+grip 100 g [plan: 0.30 kg total]
R_BALL, TEE_ABOVE_FACE = 0.021335, 0.010   # ball centre 10 mm above face centre (teed driver, hit slightly high) [guess]


def joint_kind(name):
    n = name.replace("left_", "").replace("right_", "").replace("_joint", "")
    return n


def rz(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])
def ry(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def rx(a):
    c, s = math.cos(a), math.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def mat2quat(R):
    q = np.zeros(4); mujoco.mju_mat2Quat(q, np.asarray(R, float).ravel()); return q


def club_geometry(handed="LH", club_len=0.90, lie_deg=None):
    """Address-pose club in the world. Returns dict with the club frame orientation R (club->world), head geometry in the club frame, etc.
    Club local axes: z along the shaft pointing from head to grip, x = face direction, y = toe direction (LH) / heel... mirrored for RH.
    Frame origin = lead-hand grip point (shaft top). Head hosel (shaft bottom) at local z = -club_len."""
    lie, loft = math.radians(LIE_DEG if lie_deg is None else lie_deg), math.radians(LOFT_DEG)
    # world address orientation of the club frame
    face_dir = np.array([1.0, 0, 0])                                   # target line
    away = -1.0 if handed == "LH" else 1.0                             # golfer stands on -y (LH faces +y) / +y (RH faces -y)
    zc = np.array([0.0, away * math.cos(lie), math.sin(lie)])          # shaft head->grip leans toward the golfer
    xc = face_dir - np.dot(face_dir, zc) * zc; xc /= np.linalg.norm(xc)
    yc = np.cross(zc, xc)
    R = np.stack([xc, yc, zc], axis=1)                                 # columns = local axes in world
    toe_world = np.array([0.0, -away, 0.0])                            # toe points away from the golfer
    toe_sign = float(np.sign(np.dot(yc, toe_world)))                   # +1 if local +y is the toe direction
    # head box frame (world): ex = face normal (lofted), ey = toe (horizontal), ez = ex x ey ... build in world then express in club frame
    n_w = np.array([math.cos(loft), 0.0, math.sin(loft)])
    ey_w = toe_world
    ez_w = np.cross(n_w, ey_w)
    Rb_w = np.stack([n_w, ey_w, ez_w], axis=1)
    half = np.array([0.045, 0.055, 0.032])                              # depth, toe-heel width, height [guess; ~driver head]
    # head centre relative to hosel, in head-world-aligned axes: toe offset 0.05, behind the face by half depth, below hosel
    c_off_w = toe_world * 0.050 - n_w * 0.0 + np.array([0, 0, -0.03])
    return dict(R=R, toe_sign=toe_sign, n_w=n_w, Rb_w=Rb_w, half=half, c_off_w=c_off_w, toe_world=toe_world, away=away, club_len=club_len, lie_deg=(LIE_DEG if lie_deg is None else lie_deg))


def build_spec(handed="LH", club_len=0.90, dt=DT, force_scale=1.0, kp_scale=1.0, grip_quat=None, head="box", lie_deg=None, sw_comp=False):
    spec = mujoco.MjSpec.from_file(f"{MENAG}/unitree_g1/scene.xml")
    for k in list(spec.keys):
        spec.delete(k)
    spec.option.timestep = dt
    spec.option.integrator = mujoco.mjtIntegrator.mjINT_IMPLICITFAST
    spec.option.noslip_iterations = 0
    # --- collisions: only feet (type 4 -> floor), club head (type 2 -> floor+ball), ball (2 -> head); everything else visual-only
    for g in list(spec.geoms):
        if g.name == "floor":
            g.contype = 1; g.conaffinity = 1; g.condim = 6; g.friction = [1.0, 0.005, 0.0001]
            continue
        if g.type == mujoco.mjtGeom.mjGEOM_SPHERE and abs(g.size[0] - 0.005) < 1e-9:
            spec.delete(g); continue            # Menagerie foot-point spheres, replaced by box soles below
        g.contype = 0; g.conaffinity = 0
    for side in ("left", "right"):
        b = spec.body(f"{side}_ankle_roll_link")
        b.add_geom(name=f"{side}_sole", type=mujoco.mjtGeom.mjGEOM_BOX, pos=[0.035, 0, -0.030], size=[0.10, 0.04, 0.005],
                   contype=4, conaffinity=1, condim=6, friction=[1.0, 0.005, 0.0001], priority=1,
                   solref=[0.004, 1], solimp=[0.95, 0.99, 0.001, 0.5, 2], rgba=[0.1, 0.1, 0.1, 1], group=1)
        b.add_site(name=f"{side}_sole_site", pos=[0.035, 0, -0.035], size=[0.11, 0.05, 0.01], type=mujoco.mjtGeom.mjGEOM_BOX, group=4)
        spec.add_sensor(name=f"{side}_foot_touch", type=mujoco.mjtSensor.mjSENS_TOUCH, objtype=mujoco.mjtObj.mjOBJ_SITE, objname=f"{side}_sole_site")
        spec.add_sensor(name=f"{side}_ankle_force", type=mujoco.mjtSensor.mjSENS_FORCE, objtype=mujoco.mjtObj.mjOBJ_SITE, objname=f"{side}_foot")
        spec.add_sensor(name=f"{side}_ankle_torque", type=mujoco.mjtSensor.mjSENS_TORQUE, objtype=mujoco.mjtObj.mjOBJ_SITE, objname=f"{side}_foot")
    # --- hand sites (grip centre ~7.5 cm along the wrist-yaw link x axis, i.e. inside the rubber hand mesh) [guess]
    for side in ("left", "right"):
        spec.body(f"{side}_wrist_yaw_link").add_site(name=f"{side}_hand", pos=[0.075, 0, 0], size=[0.012, 0, 0], group=4)
    # --- sensors for kinematic sequence / state
    pel = spec.body("pelvis")
    spec.add_sensor(name="pelvis_angvel", type=mujoco.mjtSensor.mjSENS_FRAMEANGVEL, objtype=mujoco.mjtObj.mjOBJ_BODY, objname="pelvis")
    spec.add_sensor(name="torso_angvel", type=mujoco.mjtSensor.mjSENS_FRAMEANGVEL, objtype=mujoco.mjtObj.mjOBJ_BODY, objname="torso_link")
    # --- club (free body) + ball
    g = club_geometry(handed, club_len) if lie_deg is None else club_geometry(handed, club_len, lie_deg)
    club = spec.worldbody.add_body(name="club", pos=[0, 0, 1.0])
    club.add_freejoint(name="club_free")
    Ls = club_len
    m_cw = sw_compensation(handed, club_len, lie_deg)["m_butt"] if sw_comp else 0.0   # v4: butt counterweight taken out of the shaft+grip mass (total unchanged)
    club.add_geom(name="shaft", type=mujoco.mjtGeom.mjGEOM_CAPSULE, fromto=[0, 0, 0.0, 0, 0, -Ls], size=[0.007, 0, 0], mass=SHAFT_M - m_cw,
                  contype=0, conaffinity=0, rgba=[.25, .25, .25, 1])
    if sw_comp:
        club.add_geom(name="butt_weight", type=mujoco.mjtGeom.mjGEOM_SPHERE, pos=[0, 0, 0], size=[0.008, 0, 0], mass=m_cw, contype=0, conaffinity=0, group=5, rgba=[0, 0, 0, 0])
    Rb_loc = g["R"].T @ g["Rb_w"]                      # head box frame in club local frame
    c_loc = g["R"].T @ g["c_off_w"] + np.array([0, 0, -Ls])
    face_ctr_loc = c_loc + Rb_loc[:, 0] * g["half"][0]
    if head == "box":
        club.add_geom(name="head", type=mujoco.mjtGeom.mjGEOM_BOX, pos=c_loc.tolist(), quat=mat2quat(Rb_loc).tolist(), size=g["half"].tolist(), mass=HEAD_M,
                  contype=2, conaffinity=3, solref=[0.002, 1], solimp=[0.95, 0.99, 0.001, 0.5, 2], friction=[0.5, 0.01, 0.001], rgba=[.75, .75, .8, 1])
    elif head in ("realistic", "v4"):   # K34 opt-in sourced head (realistic_head_geometry); "v4" = v4 re-baseline values; box path above untouched
        hg = realistic_head_geometry(g) if head == "realistic" else realistic_head_geometry(g, v4=True); g["realistic"] = hg; Rt = g["R"].T; hos = np.array([0, 0, -Ls])
        loc = lambda w: (Rt @ w + hos).tolist(); Rw_loc = mat2quat(Rt @ hg["Rw"]).tolist()
        club.add_geom(name="head", type=mujoco.mjtGeom.mjGEOM_BOX, pos=loc(hg["plate_c_w"]), quat=mat2quat(Rb_loc).tolist(), size=hg["plate_half"].tolist(), mass=0.0,
                      contype=2, conaffinity=2, solref=[0.002, 1], solimp=[0.95, 0.99, 0.001, 0.5, 2], friction=[0.5, 0.01, 0.001], rgba=[.75, .75, .8, 0.6])
        club.add_geom(name="head_shell", type=mujoco.mjtGeom.mjGEOM_BOX, pos=loc(hg["shell_c_w"]), quat=Rw_loc, size=hg["shell_half"].tolist(), mass=0.0,
                      contype=0, conaffinity=1, solref=[0.002, 1], solimp=[0.95, 0.99, 0.001, 0.5, 2], friction=[0.5, 0.01, 0.001], rgba=[.3, .3, .35, 0.5])
        club.add_geom(name="head_mass", type=mujoco.mjtGeom.mjGEOM_BOX, pos=loc(hg["cg_w"]), quat=Rw_loc, size=hg["mass_half"].tolist(), mass=hg["spec"]["mass"],
                      contype=0, conaffinity=0, group=5, rgba=[0, 0, 0, 0])
        face_ctr_loc = np.array(loc(hg["fc_w"])); c_loc = np.array(loc(hg["cg_w"]))
    else:
        raise ValueError(f"unknown head {head!r} (box|realistic)")
    gq = grip_quat or {}
    club.add_site(name="grip_lead", pos=[0, 0, 0], size=[0.01, 0, 0], group=4, quat=gq.get("grip_lead", [1, 0, 0, 0]))
    club.add_site(name="grip_trail", pos=[0, 0, -SHAFT_BELOW_GRIP], size=[0.01, 0, 0], group=4, quat=gq.get("grip_trail", [1, 0, 0, 0]))
    club.add_site(name="clubhead", pos=face_ctr_loc.tolist(), size=[0.01, 0, 0], group=4)
    club.add_site(name="head_com", pos=c_loc.tolist(), size=[0.01, 0, 0], group=4)
    spec.add_sensor(name="club_angvel", type=mujoco.mjtSensor.mjSENS_FRAMEANGVEL, objtype=mujoco.mjtObj.mjOBJ_BODY, objname="club")
    ball = spec.worldbody.add_body(name="ball", pos=[0.1, 0.5, 0.06])
    ball.add_freejoint(name="ball_free")
    ball.add_geom(name="ball_geom", type=mujoco.mjtGeom.mjGEOM_SPHERE, size=[R_BALL, 0, 0], mass=0.0459, contype=2, conaffinity=2,
                  solref=[0.002, 1], solimp=[0.95, 0.99, 0.001, 0.5, 2], friction=[0.5, 0.01, 0.001], rgba=[1, 1, 1, 1])
    # --- actuators: native position servos (PD target actions); torque cap = stock limit * force_scale, speed derate applied by the env
    for a in spec.actuators:
        kind = joint_kind(a.name); tau, _ = STOCK[kind]; tau *= force_scale
        kp = kp_scale * tau / 0.35                      # saturates at ~20 deg error [guess]
        kd = 0.06 * kp ** 0.5 * (1.0 if tau < 60 else 2.0) # light damping, tuned by the passive-hold test [guess]
        a.gaintype = mujoco.mjtGain.mjGAIN_FIXED; a.biastype = mujoco.mjtBias.mjBIAS_AFFINE
        a.gainprm[0] = kp; a.biasprm[0] = 0; a.biasprm[1] = -kp; a.biasprm[2] = -kd
        a.forcelimited = 1; a.forcerange = [-tau, tau]; a.ctrllimited = 0
    for j in spec.joints:
        if j.type == mujoco.mjtJoint.mjJNT_HINGE:
            tau, _ = STOCK[joint_kind(j.name)]; j.actfrclimited = 1; j.actfrcrange = [-tau * force_scale, tau * force_scale]
            j.armature = 0.01 if tau < 60 else 0.03
    return spec, g


def lead_trail(handed):
    return ("right", "left") if handed == "LH" else ("left", "right")


def solve_address(handed="LH", club_len=0.90, stance=0.28, ball_xy=(0.10, 0.50), verbose=False, quick=False, v4=False):
    """Kinematic IK for the address keyframe: both hands on the club grip, feet flat on the ground, CoM over the feet. Returns dict.
    v4=True: realistic head at V4_LIE_DEG with swingweight compensation; the club is placed so the realistic face centre sits behind the ball (same rule),
    sole 2 mm above ground, face square (head axes built square in world); ball at the same default tee height as the box head. Same IK otherwise."""
    spec, g = build_spec(handed, club_len) if not v4 else build_spec(handed, club_len, head="v4", lie_deg=V4_LIE_DEG, sw_comp=True)
    m = spec.compile(); d = mujoco.MjData(m)
    lead, trail = lead_trail(handed)
    jn = [m.actuator(i).name for i in range(m.nu)]
    jadr = {n: int(m.jnt_qposadr[m.joint(n).id]) for n in jn}
    lo = np.array([m.jnt_range[m.joint(n).id][0] for n in jn]); hi = np.array([m.jnt_range[m.joint(n).id][1] for n in jn])
    away, yaw = g["away"], (math.pi / 2 if handed == "LH" else -math.pi / 2)
    # club world pose at address: head face centre -> ball position - ...
    R = g["R"]
    bx, by = ball_xy
    by = abs(by) * (1 if handed == "LH" else -1)
    # lowest corner of the head box at z=0.002
    corners = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                corners.append(g["R"] @ (np.linalg.inv(g["R"]) @ g["Rb_w"]) @ (g["half"] * np.array([sx, sy, sz])))
    zmin_rel = min(c[2] for c in corners)  # relative to head centre (world-aligned)
    # head centre world position (x,y of face centre line at the ball)
    face_off_w = g["Rb_w"][:, 0] * g["half"][0]
    head_c = np.array([0, 0, 0.002 - zmin_rel])
    face_ctr = head_c + face_off_w
    head_c[0] = bx - R_BALL * g["n_w"][0] - face_off_w[0] - 0.0005; head_c[1] = by - face_off_w[1]
    face_ctr = head_c + face_off_w
    ball_ctr = np.array([bx, by, face_ctr[2] + TEE_ABOVE_FACE])
    # club frame origin: head centre = origin + R @ (c_loc); c_loc computed in build_spec:
    c_loc = g["R"].T @ g["c_off_w"] + np.array([0, 0, -club_len])
    origin = head_c - R @ c_loc
    if v4:   # realistic face centre (world offset from the hosel at address = hg['fc_w']) placed at the box rule's face-centre x,y; z from the soled geometry
        hg = g["realistic"]; fc_t = np.array([face_ctr[0], face_ctr[1], hg["sole_clear"] + hg["spec"]["fc_h"]])
        hosel_w = fc_t - hg["fc_w"]; origin = hosel_w - R @ np.array([0, 0, -club_len])
        ball_ctr = np.array([bx, by, hg["crown_z"]])   # v4 default tee: ball equator at the crown (62 mm above ground), ball bottom 40.665 mm
    club_quat = mat2quat(R)
    p_lead = origin; p_trail = origin + R @ np.array([0, 0, -SHAFT_BELOW_GRIP])
    # foot placement: stance centre at x=0; golfer faces +y (LH) / -y (RH); lead side +x
    foot_x = {lead: +stance / 2, trail: -stance / 2}
    fsite = {s: m.site(f"{s}_sole_site").id for s in ("left", "right")}
    hsite = {s: m.site(f"{s}_hand").id for s in ("left", "right")}
    bpel = m.body("pelvis").id
    prior = dict(hip_pitch=-0.45, hip_roll=0.0, hip_yaw=0.0, knee=0.8, ankle_pitch=-0.35, ankle_roll=0.0, waist_yaw=0.0, waist_roll=0.0,
                 waist_pitch=0.0, shoulder_pitch=0.3, shoulder_roll=0.0, shoulder_yaw=0.0, elbow=0.5, wrist_roll=0.0, wrist_pitch=0.0, wrist_yaw=0.0)
    q_prior = np.array([prior[joint_kind(n)] for n in jn])
    wprior = np.array([0.3 if joint_kind(n) in ("hip_pitch", "knee", "ankle_pitch") else 1.0 if "wrist" in n else 3.0 if n in ("waist_yaw_joint", "waist_roll_joint") else 0.4 for n in jn])
    # parameters: pelvis x y z, pitch, roll, 29 joints
    def setq(x):
        d.qpos[:] = m.qpos0
        d.qpos[0:3] = x[0:3]
        Rp = rz(yaw) @ ry(x[3]) @ rx(x[4])
        d.qpos[3:7] = mat2quat(Rp)
        for k, n in enumerate(jn): d.qpos[jadr[n]] = x[5 + k]
        cq = m.joint("club_free").qposadr[0]
        d.qpos[cq:cq + 3] = origin; d.qpos[cq + 3:cq + 7] = club_quat
        mujoco.mj_kinematics(m, d); mujoco.mj_comPos(m, d)
    def res(x):
        setq(x)
        r = []
        for s, p in ((lead, p_lead), (trail, p_trail)):
            r.extend(100.0 * (d.site_xpos[hsite[s]] - p))
        for s in ("left", "right"):
            pz = d.site_xpos[fsite[s]]
            r.append(100.0 * pz[2])
            r.append(30.0 * (pz[0] - foot_x[s]))
            zax = d.site_xmat[fsite[s]].reshape(3, 3)[:, 2]
            r.extend(50.0 * (zax - np.array([0, 0, 1.0]))[:2])
        com = d.subtree_com[bpel]
        fc = 0.5 * (d.site_xpos[fsite["left"]] + d.site_xpos[fsite["right"]])
        face_dir = np.array([-math.sin(yaw) * -1, math.cos(yaw) * 1, 0])  # facing = rz(yaw) @ [1,0,0]
        face_dir = rz(yaw) @ np.array([1.0, 0, 0])
        r.extend(40.0 * ((com[:2] - fc[:2]) - 0.02 * face_dir[:2]))
        r.extend((x[5:] - q_prior) * wprior)
        r.append(0.0 * x[0])
        return np.array(r)
    x0 = np.concatenate([[0, 0.05 * away * -1 * 0, 0.6, 0.3, 0.0], q_prior])
    x0[1] = by - away * -1 * 0.0 - 0.55 * (1 if handed == "LH" else -1) * 1.0  # pelvis roughly 0.5 m behind the ball line
    bl = np.concatenate([[-1, -1, 0.3, -1.0, -0.5], lo]); bu = np.concatenate([[1, 1, 0.9, 1.2, 0.5], hi])
    best = None
    for y0 in ([by - 0.45, by - 0.30, by - 0.55] if handed == "LH" else [by + 0.45, by + 0.30, by + 0.55]):
        x0[1] = y0
        s = least_squares(res, x0, bounds=(bl, bu), max_nfev=60 if quick else 400)
        if best is None or s.cost < best.cost: best = s
    x = best.x; setq(x)
    out = dict(handed=handed, club_len=club_len, cost=float(best.cost), toe_sign=g["toe_sign"],
               hand_err_mm=[float(1000 * np.linalg.norm(d.site_xpos[hsite[s]] - p)) for s, p in ((lead, p_lead), (trail, p_trail))],
               foot_z_mm=[float(1000 * d.site_xpos[fsite[s]][2]) for s in ("left", "right")],
               pelvis_pos=x[0:3].tolist(), pelvis_pitch=float(x[3]), pelvis_roll=float(x[4]), yaw=yaw,
               joints={n: float(x[5 + k]) for k, n in enumerate(jn)},
               club_pos=origin.tolist(), club_quat=club_quat.tolist(), ball_pos=ball_ctr.tolist(),
               pelvis_height=float(x[2]))
    # weld relposes (site2 relative to site1 frame): hand site -> club grip site
    rel = {}
    for s, gs in ((lead, "grip_lead"), (trail, "grip_trail")):
        hp, hR = d.site_xpos[hsite[s]].copy(), d.site_xmat[hsite[s]].reshape(3, 3).copy()
        gp, gR = d.site_xpos[m.site(gs).id].copy(), d.site_xmat[m.site(gs).id].reshape(3, 3).copy()
        rel[s] = dict(pos=(hR.T @ (gp - hp)).tolist(), quat=mat2quat(hR.T @ gR).tolist())
    out["weld_rel"] = rel
    # hand-site frame expressed in the club frame (used to orient the club grip sites so a site-to-site weld has zero residual at address)
    out["grip_quat_in_club"] = {}
    for s_, gs in ((lead, "grip_lead"), (trail, "grip_trail")):
        hR = d.site_xmat[hsite[s_]].reshape(3, 3).copy()
        out["grip_quat_in_club"][gs] = mat2quat(R.T @ hR).tolist()
    if v4: out.update(variant="v4", head="realistic", lie_deg=V4_LIE_DEG, sw_comp=True, v4_params=dict(V4), face_centre_z_ground_m=V4["fc_z_ground"])
    if verbose: print(json.dumps({k: v for k, v in out.items() if k not in ("joints", "weld_rel")}, indent=1))
    return out


def build_model(handed="LH", club_len=0.90, dt=DT, force_scale=1.0, addr=None, kp_scale=1.0, head="box", lie_deg=None, sw_comp=False):
    """Compile the full v5 model (welds included). addr = result of solve_address (or loaded json)."""
    addr = addr or load_address(handed, club_len)
    spec, g = build_spec(handed, club_len, dt, force_scale, kp_scale, grip_quat=addr.get("grip_quat_in_club"), head=head, **({} if lie_deg is None and not sw_comp else dict(lie_deg=lie_deg, sw_comp=sw_comp)))
    lead, trail = lead_trail(handed)
    for s, gs in ((lead, "grip_lead"), (trail, "grip_trail")):
        # site-to-site weld: MuJoCo makes the two site FRAMES coincide (position + orientation); grip sites are oriented from the IK solution
        eq = spec.add_equality(name=f"weld_{gs}", type=mujoco.mjtEq.mjEQ_WELD, objtype=mujoco.mjtObj.mjOBJ_SITE,
                               name1=f"{s}_hand", name2=gs, solref=[0.004, 1], solimp=[0.95, 0.99, 0.0005, 0.5, 2])
    # ball at address
    spec.body("ball").pos = addr["ball_pos"]
    model = spec.compile()
    return model, spec


def addr_path(handed, club_len):
    return os.path.join(os.path.dirname(__file__), "models", f"v5_address_{handed}_{int(round(club_len*100))}.json")

def load_address(handed="LH", club_len=0.90, variant=None):
    return json.load(open(addr_path(handed, club_len) if variant is None else addr_path(handed, club_len).replace(".json", f"_{variant}.json")))


def set_address(model, data, addr):
    mujoco.mj_resetData(model, data)
    data.qpos[0:3] = addr["pelvis_pos"]
    Rp = rz(addr["yaw"]) @ ry(addr["pelvis_pitch"]) @ rx(addr["pelvis_roll"])
    data.qpos[3:7] = mat2quat(Rp)
    for n, v in addr["joints"].items(): data.qpos[model.jnt_qposadr[model.joint(n).id]] = v
    cq = model.joint("club_free").qposadr[0]
    data.qpos[cq:cq + 3] = addr["club_pos"]; data.qpos[cq + 3:cq + 7] = addr["club_quat"]
    bq = model.joint("ball_free").qposadr[0]
    data.qpos[bq:bq + 3] = addr["ball_pos"]; data.qpos[bq + 3:bq + 7] = [1, 0, 0, 0]
    mujoco.mj_forward(model, data)


if __name__ == "__main__":
    import sys
    for L in [float(a) for a in sys.argv[1:]] or [0.90]:
        a = solve_address("LH", L, verbose=True, quick=True)


def write_xml(path, handed="LH", club_len=0.87, addr=None):
    """Write the compiled-equivalent XML (absolute meshdir into MENAGERIE_DIR; Menagerie is BSD-3 and not vendored)."""
    model, spec = build_model(handed, club_len, addr=addr)
    spec.meshdir = f"{MENAG}/unitree_g1/assets"
    xml = spec.to_xml()
    open(path, "w").write(xml)
    return path


# ---------------- K34 opt-in realistic driver head (--head realistic). Default head='box' is UNCHANGED (bit-identical model).
HEAD_REF_JSON = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "references", "driver_head_460cc_refs.json")   # main's sourced refs (aggregates only; per-model rule36 rows held); only rows[].nominal is read
# v4 re-baseline values (Data Agent branch driver-face-centre-height @ 857e373; data/references/driver_head_460cc_refs.json). v5 --head realistic is NOT affected.
# Each is a single parameter; changing any of them needs a v4 address re-solve (scripts/v4_address_solve.py).
V4 = dict(
    fc_z_ground=0.029,   # face-centre height above GROUND at address, 29 mm (26-33). DERIVED (patent Zup/CGZ US 12,649,090 + Wishon/PROCEED face geometry)
    sole_clear=0.0,      # sole ON the ground at address (fixes the v5 2 mm offset): crown 62 mm above ground, face bottom 29-27 = 2 mm (patent FIG.1A 2-6 mm)
    fc_shaft=0.039,      # face centre to shaft axis (CFZ) 39 mm (35-45). MANUFACTURER PATENT CLAIM (US 12,649,090 Tables 3-4); replaces the 35 mm estimate
    izz=5600e-7,         # Izz 5600 g cm2 (4800-7000; rule <=5900+100). MANUFACTURER CLAIM (n=1, Tour Edge 2023) / patent band (US 12,649,090 claim 1)
    tee_15in_bottom=0.0381,   # named option --tee_mode 1.5in: ball bottom on a 1.5 in tee (38.1 mm; Data Agent ~38.0). v4 DEFAULT tee = equator at the 62 mm crown (ball bottom 40.67 mm ~ 1.6 in; Golf Digest 'at least half above the crown')
)
V4_LIE_DEG = None        # v4 lie, read from the Data Agent JSON ('lie' nominal 58.5) at import (below)
SOLE_CLEAR = 0.002   # same 2 mm sole-to-ground clearance as the box head at address (solve_address)


# K34 estimates pinned so the realistic head stays as trained/swept after the Data Agent refs update (4f95e55) replaced these rows with
# 'face-centre height above ground at address (soled)' 29 mm (= 27 above the sole) and CFZ 39 mm. Not applied yet: changing them moves the face centre/ball (Trainer/v4 decision).
K34_PINNED = {"face-centre height when soled": 30.0, "shaft-axis offset to face centre (heel-toe)": 35.0}   # mm, ESTIMATES (reported in realistic_head_spec()[1])


def realistic_head_spec():
    """Nominal 460 cc driver head from the Data Agent's sourced table (values read directly from the JSON 'nominal' column; '~' rows are ESTIMATES).
    Returns SI values + list of estimate keys."""
    import re
    rows = {r["quantity"]: r for r in json.load(open(HEAD_REF_JSON))["rows"]}
    def num(q):
        if q not in rows: return K34_PINNED[q]
        return float(re.search(r"[-+]?\d+(\.\d+)?", rows[q]["nominal"]).group(0))
    est = [q for q, r in rows.items() if "estimate" in r["nominal"] or "estimate" in r.get("label", "")] + [q for q in K34_PINNED if q not in rows]
    s = dict(face_h=num("face height") * 1e-3, face_w=num("face width") * 1e-3, depth=num("head depth (front-back)") * 1e-3,
             heel_toe=num("heel-to-toe length (head)") * 1e-3, crown_h=num("sole-to-crown (crown height when soled)") * 1e-3,
             fc_h=num("face-centre height when soled") * 1e-3, mass=num("head mass") * 1e-3, loft=num("loft"), lie=num("lie"),
             izz=num("MOI vertical axis (heel-toe twist, Izz)") * 1e-7, iv=num("MOI horizontal (heel-toe) axis (Iv, face up/down rotation)") * 1e-7,
             cg_depth=num("CG depth behind face") * 1e-3, cg_h=num("CG height") * 1e-3, cg_shaft=num("CG distance from shaft axis") * 1e-3,
             fp=num("face progression (FP: leading edge ahead of shaft axis)") * 1e-3, fc_shaft=num("shaft-axis offset to face centre (heel-toe)") * 1e-3)
    return s, est


def realistic_head_geometry(g, v4=False):
    """Place the realistic head on the UNCHANGED shaft/address pose (same club frame, hosel at local z=-club_len, same hands/joints), soled 2 mm above
    the ground like the box head. All offsets are built in world address axes (x = target, toe = away from golfer, z = up) relative to the hosel, then
    expressed in the club frame. Geoms:
      head       : thin lofted CONTACT plate (ball only), front face = hitting face; envelope 130 x 80 mm (> 105 x 54 face) so off-face strikes register
                   with their true |dy|/|dz| and the env can flag them as misses. Its local axes (normal, toe, up) are used by the contact code exactly as before.
      head_shell : world-aligned 112 x 120 x 62 mm box (depth x heel-toe x crown), floor collisions only (sole/fat shots), massless; its top = crown.
      head_mass  : invisible, collision-free box carrying the 200 g at the CG; dims chosen so Izz = m(d^2+w^2)/12 ~ 4500 g cm2 and Iv = m(d^2+h^2)/12 ~ 3000.
    Lie: the address shaft angle stays LIE_DEG (56) because changing it needs a new address IK (new q_addr -> invalidates checkpoints); the sourced
    58.5 deg is reported, not applied (documented in TRAINING_NOTES)."""
    s, est = realistic_head_spec(); sc = SOLE_CLEAR
    if v4:   # v4 re-baseline overrides (V4 dict above); v5 realistic path unchanged
        sc = V4["sole_clear"]; s = dict(s, fc_h=V4["fc_z_ground"] - sc, fc_shaft=V4["fc_shaft"], izz=V4["izz"], lie=s["lie"])
        est = [q for q in est if q not in K34_PINNED]   # v4 takes face-centre height/offset from V4, never the K34 pinned fallback
    lie, loft = math.radians(g.get("lie_deg", LIE_DEG)), math.radians(LOFT_DEG)   # shaft lie of THIS club geometry (LIE_DEG 56 default, bit-identical; 58.5 in v4)
    # box-head soling (identical computation to solve_address) -> hosel world height at address
    corners = [g["Rb_w"] @ (g["half"] * np.array([sx, sy, sz])) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    hosel_z = SOLE_CLEAR - min(c[2] for c in corners) - g["c_off_w"][2]
    toe = g["toe_world"]; ez = np.array([0.0, 0.0, 1.0])
    def toe_off(d_perp, z_world):   # toe offset u so the point at height z is d_perp from the shaft axis (in the toe/up plane; shaft tilts toward the golfer)
        w = z_world - hosel_z; return (d_perp - w * math.cos(lie)) / math.sin(lie)
    z_fc = sc + s["fc_h"]
    x_fc = s["fp"] - s["fc_h"] * math.tan(loft)            # FP is at the leading edge (sole); lofted face sets back by fc_h*tan(loft) at face centre
    fc_w = np.array([x_fc, 0, 0]) + toe * toe_off(s["fc_shaft"], z_fc) + ez * (z_fc - hosel_z)
    z_cg = sc + s["cg_h"]
    cg_w = np.array([x_fc - s["cg_depth"], 0, 0]) + toe * toe_off(s["cg_shaft"], z_cg) + ez * (z_cg - hosel_z)
    PL_T = 0.004
    plate_half = np.array([PL_T, 0.065, 0.040])
    plate_c_w = fc_w - g["n_w"] * PL_T
    Rw = np.stack([np.array([1.0, 0, 0]), toe, np.cross([1.0, 0, 0], toe)], axis=1)   # world-aligned head axes (x, toe, up)
    shell_half = np.array([s["depth"], s["heel_toe"], s["crown_h"]]) / 2
    shell_c_w = np.array([s["fp"] - shell_half[0], 0, 0]) + toe * toe_off(s["fc_shaft"], z_fc) + ez * (sc + shell_half[2] - hosel_z)
    # inertia box: d^2+w^2 = 12 Izz/m, d^2+h^2 = 12 Iv/m, d = head depth -> w, h
    d2 = s["depth"] ** 2; w2 = 12 * s["izz"] / s["mass"] - d2; h2 = 12 * s["iv"] / s["mass"] - d2
    mass_half = np.sqrt([d2, max(w2, 1e-6), max(h2, 1e-6)]) / 2
    return dict(spec=s, estimates=est, hosel_z=hosel_z, fc_w=fc_w, cg_w=cg_w, plate_half=plate_half, plate_c_w=plate_c_w, Rw=Rw,
                shell_half=shell_half, shell_c_w=shell_c_w, mass_half=mass_half, crown_z=sc + s["crown_h"], sole_clear=sc)


V4_LIE_DEG = realistic_head_spec()[0]["lie"]   # 58.5 deg (Data Agent JSON 'lie' nominal; Wishon 58, PING G440 MAX 58.5, PROCEED 59)


def sw_compensation(handed="LH", club_len=1.15, lie_deg=None):
    """v4 swingweight compensation. With the realistic head the 200 g head CG sits further down the shaft than the box head centre, which moves the club
    balance point toward the head (+1.8% moment about the 14 in point). Restore BOTH the balance point and the swingweight of the box club exactly, at the
    same total mass (300 g), by moving m_butt from the (uniform) shaft+grip mass to a butt-end weight at the lead-grip origin (local z = 0):
    m_butt = 2 * HEAD_M * (z_box - z_real) / L, z = head CG coordinate along the shaft (club frame). Butt counterweights of 5-20 g are common practice."""
    g0 = club_geometry(handed, club_len); z_box = float((g0["R"].T @ g0["c_off_w"])[2] - club_len)
    g = club_geometry(handed, club_len) if lie_deg is None else club_geometry(handed, club_len, lie_deg)
    hg = realistic_head_geometry(g, v4=True); z_real = float((g["R"].T @ hg["cg_w"])[2] - club_len)
    return dict(m_butt=2 * HEAD_M * (z_box - z_real) / club_len, z_box=z_box, z_real=z_real)
