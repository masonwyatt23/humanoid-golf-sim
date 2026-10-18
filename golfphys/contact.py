"""Contact-point mechanics API for the env (PROPOSAL; nothing in env/ is edited).

contact_to_ball(...)   : head state at contact (MuJoCo-style quantities) -> ball initial velocity/spin.
env_contact_to_shot(.) : maps what the env already exposes at first contact (club lin vel, face normal, _face_off=(dy,dz), AoA)
                         to the model; returns a dict the env could apply to qvel / use for the analytic flight.
"""
import math
import numpy as np
from .params import Params, load_params
from .impact import impact_vec, ball_launch_state


def contact_to_ball(v_head_com, omega_head, n_face, toe_dir, p_contact, p_com, p: Params = None, m_head=None, e_override=None):
    """All vectors world frame. v_head_com: head CoM velocity; omega_head: head angular velocity (rad/s);
    n_face: unit face normal pointing toward the ball; toe_dir: unit vector toward the toe; p_contact / p_com: world positions
    of the contact point and head CoM. Returns dict(v_ball, omega_ball (rad/s world), launch fields, smash, offsets)."""
    p = p or load_params()
    r = np.asarray(p_contact, float) - np.asarray(p_com, float)
    v_c = np.asarray(v_head_com, float) + np.cross(np.asarray(omega_head, float), r)
    n = np.asarray(n_face, float); n = n / np.linalg.norm(n)
    toe = np.asarray(toe_dir, float); toe = toe - np.dot(toe, n) * n; toe /= np.linalg.norm(toe)
    up = np.cross(toe, n)
    x, y = float(np.dot(r, toe)), float(np.dot(r, up))
    res = impact_vec(v_c, n, toe, p, x, y, m_head=m_head, e_override=e_override)
    out = ball_launch_state(res["v_ball"], res["omega"])
    out.update(v_ball=res["v_ball"], omega_ball=res["omega"], smash=res["smash"], x_toe_m=x, y_high_m=y, m_eff=res["m_eff"],
               v_contact=v_c)
    return out


def env_contact_to_shot(club_vel, face_normal, face_off, handed="RH", toe_sign=1.0, p: Params = None, m_head=None):
    """Env adapter. Inputs the env already has at first contact:
      club_vel     = env._club_lin_vel() just before contact (world, m/s)
      face_normal  = world normal of the club-face geom pointing at the ball (R_geom @ local face axis)
      face_off     = env._face_off = (dy, dz) metres, club-geom local frame (y lateral, z vertical)
      handed       = 'RH'/'LH' (left-handers use 'LH'): sets the world direction of the toe (RH: -left of the face, LH: +left)
      toe_sign     = +1 if local +y points toward the toe, -1 otherwise (ASSUMPTION: verify against the club xml)
    Returns contact_to_ball's dict; v_ball / omega_ball are world-frame (the env writes qvel[0:3]=v_ball and body-frame
    angular qvel = xmat.T @ omega_ball, exactly as it already does for its own spin)."""
    p = p or load_params()
    n = np.asarray(face_normal, float); n = n / np.linalg.norm(n)
    hl = np.array([-n[1], n[0], 0.0]); hl /= max(np.linalg.norm(hl), 1e-9)
    toe = -hl if handed.upper().startswith("R") else hl
    dy, dz = (0.0, 0.0) if face_off is None else face_off
    up = np.cross(toe, n)
    pc = float(dy) * float(toe_sign) * toe + float(dz) * up
    return contact_to_ball(np.asarray(club_vel, float), np.zeros(3), n, toe, pc, np.zeros(3), p, m_head)
