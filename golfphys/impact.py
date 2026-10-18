"""Club-ball impact: oblique two-body impact with effective head mass, tangential (roll/slip) impulse, bulge/roll and gear effect.

Frame: +x target line, +y left of line, +z up. Angles in degrees at the Delivery level.
Sign conventions (documented in docs/GOLF_PHYSICS_SIM.md):
  face_deg, path_deg  + = toward +y (LEFT of target; "closed" face / "in-to-out" path for a right-hander)
  aoa_deg             + = club ascending at impact
  dynamic_loft_deg    elevation of the face normal above horizontal (spin loft = dynamic loft - AoA when path/face are on-line)
  strike x_toe_m      + = toward the toe;  y_high_m + = above face centre
  handed              'RH' -> toe points to -y (away from the golfer); 'LH' -> +y
Sources: normal impact = Newtonian restitution with effective mass (Cochran & Stobbs 1968; Tutelman smash page - snippet);
tangential impulse limit M*vt/3.5 = rolling contact of a uniform sphere (same as env/ball_flight_analytic.py, derived here);
gear effect rates 16.4*Vb*x, 25*Vb*y rpm/(mph*in) = Tutelman GE3 (FETCHED, high confidence); effective mass with off-centre hit
1/m_eff = 1/m + x^2/Iv + y^2/Ih (rigid-body; Ih/Iv from Tutelman GE3).
"""
from dataclasses import dataclass
import math
import numpy as np
from .params import Params, R_BALL, M_BALL, I_BALL

MPH = 0.44704


@dataclass
class Delivery:
    club_speed: float            # m/s (head CoM speed along its velocity vector)
    dynamic_loft_deg: float
    aoa_deg: float = 0.0
    face_deg: float = 0.0        # face azimuth (+ left)
    path_deg: float = 0.0        # club path azimuth (+ left)
    handed: str = "RH"


@dataclass
class Strike:
    x_toe_m: float = 0.0
    y_high_m: float = 0.0


def _unit(a):
    a = np.asarray(a, float)
    return a / np.linalg.norm(a)


def delivery_vectors(d: Delivery):
    L, a, f, ps = (math.radians(v) for v in (d.dynamic_loft_deg, d.aoa_deg, d.face_deg, d.path_deg))
    vc = d.club_speed * np.array([math.cos(a) * math.cos(ps), math.cos(a) * math.sin(ps), math.sin(a)])
    n = np.array([math.cos(L) * math.cos(f), math.cos(L) * math.sin(f), math.sin(L)])
    left = np.array([-math.sin(f), math.cos(f), 0.0])
    toe = -left if d.handed.upper().startswith("R") else left
    return vc, n, toe


def e_normal(vn, p: Params):
    return max(0.5, p.e0 + p.e_slope * (vn - p.e_ref_speed))


def impact_vec(vc, n, toe, p: Params, x_toe=0.0, y_high=0.0, m_head=None, e_override=None):
    """General impact. vc: head velocity at the contact point (m/s, world); n: nominal face normal toward the ball;
    toe: unit vector toward the toe. Returns dict with v_ball (3), omega (3, rad/s), diagnostics."""
    m = m_head or p.m_head
    n = _unit(n); toe = _unit(toe - np.dot(toe, n) * n)
    up = np.cross(toe, n)                      # face-up axis
    # bulge / roll: local surface normal tilts toward the strike side
    ne = _unit(n + (x_toe / p.bulge_radius) * toe + (y_high / p.roll_radius) * up)
    vn = float(np.dot(vc, ne))
    vt = vc - vn * ne
    vtm = float(np.linalg.norm(vt))
    if vn <= 0:
        return dict(v_ball=np.zeros(3), omega=np.zeros(3), smash=0.0, m_eff=m, n_eff=ne, vn=vn, vt=vtm, spin_loft=0.0)
    inv_m = 1.0 / m + (x_toe ** 2) / p.I_head_v + (y_high ** 2) / p.I_head_h
    m_eff = 1.0 / inv_m
    e = e_override if e_override is not None else e_normal(vn, p)
    vbn = (1 + e) * m_eff / (m_eff + M_BALL) * vn
    sl = math.degrees(math.acos(max(-1, min(1, vn / max(np.linalg.norm(vc), 1e-9)))))
    s_t = max(0.0, p.s_t + p.s_t_slope * (sl - 12.0))
    d = vt / vtm if vtm > 1e-9 else np.zeros(3)
    Jt = s_t * M_BALL * vtm / 3.5               # full roll (s_t=1) -> spin = vt/(1.4 R)
    v_ball = vbn * ne + (Jt / M_BALL) * d
    omega = -(R_BALL * Jt / I_BALL) * np.cross(ne, d)
    if p.gear_mode == "tutelman":
        Vb = float(np.linalg.norm(v_ball)) / MPH
        rpm_h = p.gear_h_rpm_per_mph_in * Vb * (x_toe / 0.0254)    # toe hit -> draw
        rpm_v = p.gear_v_rpm_per_mph_in * Vb * (y_high / 0.0254)   # high hit -> less backspin
        omega = omega + (rpm_h * np.cross(toe, n) + rpm_v * np.cross(up, n)) * 2 * math.pi / 60.0
    return dict(v_ball=v_ball, omega=omega, smash=float(np.linalg.norm(v_ball) / np.linalg.norm(vc)),
                m_eff=m_eff, n_eff=ne, vn=vn, vt=vtm, spin_loft=sl, e=e)


def ball_launch_state(v_ball, omega):
    """Decompose into speed, launch elevation, azimuth (HLA, + left), backspin, sidespin (+ draw), spin axis (deg, + draw) and rifle spin."""
    v = np.asarray(v_ball, float); w = np.asarray(omega, float)
    sp = float(np.linalg.norm(v))
    hs = math.hypot(v[0], v[1])
    L = math.atan2(v[2], hs); az = math.atan2(v[1], v[0])
    left = np.array([-math.sin(az), math.cos(az), 0.0])
    up = np.array([-math.sin(L) * math.cos(az), -math.sin(L) * math.sin(az), math.cos(L)])
    fwd = v / max(sp, 1e-9)
    back = float(-np.dot(w, left)) * 60 / (2 * math.pi)
    side = float(np.dot(w, up)) * 60 / (2 * math.pi)
    rifle = float(np.dot(w, fwd)) * 60 / (2 * math.pi)
    return dict(ball_speed=sp, launch_deg=math.degrees(L), azimuth_deg=math.degrees(az), backspin_rpm=back, sidespin_rpm=side,
                spin_rpm=math.hypot(back, side), spin_axis_deg=math.degrees(math.atan2(side, back)), rifle_rpm=rifle)


def impact(dlv: Delivery, strike: Strike = None, p: Params = None, **kw):
    """Delivery (+ strike offset) -> ball launch state dict (ball_speed m/s, launch_deg, azimuth_deg, backspin_rpm, sidespin_rpm, ...)."""
    from .params import load_params
    p = p or load_params()
    strike = strike or Strike()
    vc, n, toe = delivery_vectors(dlv)
    r = impact_vec(vc, n, toe, p, strike.x_toe_m, strike.y_high_m, **kw)
    out = ball_launch_state(r["v_ball"], r["omega"])
    out.update(smash=r["smash"], m_eff=r["m_eff"], spin_loft_deg=r["spin_loft"], v_ball=r["v_ball"], omega=r["omega"])
    out["face_to_path_deg"] = dlv.face_deg - dlv.path_deg
    return out
