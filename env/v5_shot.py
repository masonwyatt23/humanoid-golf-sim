"""Ball-flight adapter for the v5 env: MuJoCo club kinematics at first contact -> golfphys (vendored, Data Agent) -> ball state + shot.

Implements docs/GOLF_PHYSICS_SIM.md section 5 (`env_contact_to_shot`). Env-specific findings (no edits to the vendored package):
 * LH SIGN BUG in golfphys.impact_vec: `up = toe x n` points DOWN for a left-hander, so a high-face strike (y_high>0) gives MORE backspin and
   launches LOWER for LH, the opposite of RH [measured: tests/test_v5_stage0.py::test_golfphys_lh_up_axis_flip]. x_toe (draw/fade) is mirrored correctly.
   Workaround here: pass dz_high = -dz for LH so a physically high strike behaves like the RH mirror.
 * toe_sign: verified against the compiled club model by `verify_toe_sign` (head-box local +y is the toe for both LH and RH builds -> toe_sign=+1).
"""
import math
import numpy as np
import mujoco
from golfphys import load_params, env_contact_to_shot
from golfphys.sim import _run
from golfphys.params import R_BALL

_P = None
def params():
    global _P
    if _P is None: _P = load_params()
    return _P


def verify_toe_sign(model, data, handed):
    """Toe direction from XML geometry (head-box centre offset from the shaft axis, projected perpendicular to the face normal) versus the head geom's
    local +y axis. Returns (toe_sign, toe_world_geometric, dot_with_golfphys_toe)."""
    hid = model.geom("head").id; sid = model.geom("shaft").id
    ctr = data.geom_xpos[hid]; R = data.geom_xmat[hid].reshape(3, 3)
    bshaft = model.geom_bodyid[sid]
    shaft_dir = data.xmat[bshaft].reshape(3, 3)[:, 2]
    shaft_top = data.xpos[bshaft]
    v = ctr - shaft_top; perp = v - np.dot(v, shaft_dir) * shaft_dir        # head centre offset from the shaft axis
    n = R[:, 0]; toe_geo = perp - np.dot(perp, n) * n; toe_geo /= np.linalg.norm(toe_geo)
    toe_sign = float(np.sign(np.dot(R[:, 1], toe_geo)))
    hl = np.array([-n[1], n[0], 0.0]); hl /= np.linalg.norm(hl)
    gp_toe = -hl if handed.upper().startswith("R") else hl
    th = toe_geo.copy(); th[2] = 0.0; th /= np.linalg.norm(th)      # compare horizontally (the head offset also has a vertical component)
    return toe_sign, toe_geo, float(np.dot(th, gp_toe))


def shot_from_contact(club_vel, face_normal, dy, dz_high, handed="LH", toe_sign=1.0, ball_z=0.06, turf="normal", roll=True):
    """club_vel: world velocity of the face-centre point just before contact; face_normal: world normal toward the ball; dy: contact offset along toe (+toe);
    dz_high: contact offset above face centre (m, physical +up). Returns dict with ball state and golfphys ShotResult fields (carry_m has no roll)."""
    p = params()
    dz = -dz_high if handed.upper().startswith("L") else dz_high            # work around the LH 'up' axis flip in golfphys (see module docstring)
    out = env_contact_to_shot(np.asarray(club_vel, float), np.asarray(face_normal, float), (dy, dz), handed=handed, toe_sign=toe_sign, p=p)
    v, om = np.asarray(out["v_ball"], float), np.asarray(out["omega_ball"], float)
    r = _run(tuple(v), tuple(om), p, turf, (0, 0, 0), 0.0, 15.0, 0.0, max(ball_z - R_BALL, 0.0), 0.01, roll)
    r.smash = out["smash"]
    return dict(v_ball=v, omega_ball=om, shot=r, launch_deg=out["launch_deg"], backspin_rpm=out["backspin_rpm"], sidespin_rpm=out["sidespin_rpm"],
                azimuth_deg=out["azimuth_deg"], smash=out["smash"], ball_speed=out["ball_speed"], x_toe_m=out["x_toe_m"], y_high_m=out["y_high_m"])
