"""Turf bounce and roll. Ball lands with (v, omega); repeated oblique bounces with normal restitution
e_n = e_a / (1 + vn / v_ref) and Coulomb-limited tangential impulse (same stick/slip logic as a sphere on a plane),
then sliding -> rolling with constant rolling-resistance deceleration a_roll.
Structural basis: USGA/R&A bounce-model report (fetched; roll set by landing angle, roughly constant yards) - the
parameters below are CALIBRATED here (see JSON + docs/GOLF_PHYSICS_VALIDATION.md); firmness scalings are tied to ONE relative
published statistic (Broadie/ShotLink soft vs medium vs firm tee-shot totals, fetched via USGA PDF) and are NOT absolute.
"""
import math
from .params import R_BALL, M_BALL, I_BALL, G

# e_a, v_ref (m/s), mu (Coulomb), plow (turf penetration drag), beta (tangential restitution: contact-point velocity reversal fraction), a_roll (m/s^2)
TURF = {
    "soft": dict(e_a=0.33, v_ref=20.0, mu=0.55, beta=0.5, plow=0.3, a_roll=2.4),
    "normal": dict(e_a=0.45, v_ref=20.0, mu=0.55, beta=0.5, plow=0.3, a_roll=1.5),
    "firm": dict(e_a=0.55, v_ref=20.0, mu=0.50, beta=0.5, plow=0.3, a_roll=1.1),
}


def _load_json():
    import json
    from .params import JSON
    try:
        t = json.load(open(JSON)).get("turf", {})
        for k, v in t.items():
            TURF[k] = {kk: vv for kk, vv in v.items() if kk in ("e_a", "v_ref", "mu", "beta", "plow", "a_roll")}
    except FileNotFoundError:
        pass


def set_turf(table):
    TURF.update(table)


_load_json()


def bounce_roll(land_pos, land_vel, land_spin, turf="normal", slope_deg=0.0, max_bounces=12, turf_params=None):
    """Return dict(total_ground_m (x distance from p0 handled by caller), roll_m, path, n_bounces, rest_pos).
    Flat ground (slope ignored unless nonzero: crude uphill/downhill factor on rolling decel)."""
    tp = turf_params or TURF[turf]
    e_a, v_ref, mu, a_roll = tp["e_a"], tp["v_ref"], tp["mu"], tp["a_roll"]
    beta = tp.get("beta", 0.0); plow = tp.get("plow", 0.0)
    x, y = land_pos[0], land_pos[1]
    vx, vy, vz = land_vel
    wx, wy, wz = land_spin
    nb = 0
    k = 1.0 / M_BALL + R_BALL ** 2 / I_BALL     # = 3.5/M
    while vz < 0 and nb < max_bounces:
        vn = -vz
        if vn < 1.5:
            break
        en = e_a / (1.0 + vn / v_ref)
        # contact point slip velocity (horizontal): u = v_h + w x r, r=(0,0,-R) -> (-R wy, +R wx)
        ux, uy = vx - R_BALL * wy, vy + R_BALL * wx
        um = math.hypot(ux, uy)
        Jn = M_BALL * (1 + en) * vn
        if um > 1e-9:
            P = min(mu * Jn, (1.0 + beta) * um / k)   # Coulomb cap vs stick with tangential restitution beta
            dx, dy = ux / um, uy / um
            vx -= P / M_BALL * dx; vy -= P / M_BALL * dy
            # dw = r x F / I with r=(0,0,-R), F=-P d  ->  (-R P dy, R P dx, 0)/I
            wx += -R_BALL * P * dy / I_BALL
            wy += R_BALL * P * dx / I_BALL
        # turf penetration drag (divot/crater + grass): horizontal speed loss proportional to normal impact speed
        hs = math.hypot(vx, vy)
        if hs > 1e-9:
            f = max(0.0, hs - plow * vn) / hs
            vx *= f; vy *= f
        vz = en * vn
        # ballistic hop (drag neglected): time of flight and horizontal advance
        th = 2 * vz / G
        x += vx * th; y += vy * th
        vz = -vz
        nb += 1
        wx *= 0.98; wy *= 0.98
    # sliding -> rolling
    ux, uy = vx - R_BALL * wy, vy + R_BALL * wx
    um = math.hypot(ux, uy)
    if um > 1e-6:
        ts = um / (k * M_BALL * mu * G)      # du/dt = -(1/M + R^2/I) * mu*M*g
        dxu, dyu = ux / um, uy / um
        a_ball = mu * G
        x += vx * ts - 0.5 * a_ball * dxu * ts * ts; y += vy * ts - 0.5 * a_ball * dyu * ts * ts
        vx -= a_ball * dxu * ts; vy -= a_ball * dyu * ts
    sp = math.hypot(vx, vy)
    if sp > 1e-6:
        d = sp * sp / (2 * a_roll)
        x += vx / sp * d; y += vy / sp * d
    return dict(rest_x=x, rest_y=y, n_bounces=nb, roll_start_speed=sp)
