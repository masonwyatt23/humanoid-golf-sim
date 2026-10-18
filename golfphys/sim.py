"""End-to-end: Delivery (+Strike) -> impact -> flight -> bounce/roll -> ShotResult. Distances in metres (env units) and yards."""
import math
from dataclasses import dataclass
from .params import Params, load_params, R_BALL
from .impact import Delivery, Strike, impact, impact_vec, ball_launch_state
from .flight import fly
from .bounce import bounce_roll
from .aero import air_density

M2YD = 1.0 / 0.9144


@dataclass
class ShotResult:
    ball_speed_ms: float; ball_speed_mph: float; smash: float; launch_deg: float; azimuth_deg: float
    backspin_rpm: float; sidespin_rpm: float; spin_rpm: float; spin_axis_deg: float
    carry_m: float; total_m: float; roll_m: float; apex_m: float; hang_s: float; descent_deg: float
    land_speed_ms: float; landing_spin_rpm: float; lateral_carry_m: float; lateral_total_m: float
    carry_yd: float; total_yd: float; turf: str

    def asdict(self):
        return self.__dict__.copy()


def shot_from_launch(ball_speed, launch_deg, spin_rpm, p: Params = None, azimuth_deg=0.0, spin_axis_deg=0.0,
                     turf="normal", wind=(0, 0, 0), alt_m=0.0, temp_c=15.0, rh=0.0, tee_m=0.0, dt=0.01, roll=True):
    """Launch-monitor-style entry: ball speed (m/s), launch, total spin, axis (+ draw) -> shot."""
    p = p or load_params()
    L, az, ax = (math.radians(v) for v in (launch_deg, azimuth_deg, spin_axis_deg))
    v = (ball_speed * math.cos(L) * math.cos(az), ball_speed * math.cos(L) * math.sin(az), ball_speed * math.sin(L))
    w = spin_rpm * 2 * math.pi / 60
    left = (-math.sin(az), math.cos(az), 0.0)
    up = (-math.sin(L) * math.cos(az), -math.sin(L) * math.sin(az), math.cos(L))
    bs, ss = w * math.cos(ax), w * math.sin(ax)
    om = tuple(-bs * left[i] + ss * up[i] for i in range(3))
    return _run(v, om, p, turf, wind, alt_m, temp_c, rh, tee_m, dt, roll)


def _run(v, om, p, turf, wind, alt_m, temp_c, rh, tee_m, dt, roll):
    fl = fly((0.0, 0.0, R_BALL + tee_m), v, om, p, wind=wind, alt_m=alt_m, temp_c=temp_c, rh=rh, dt=dt)
    st = ball_launch_state(v, om)
    if roll:
        b = bounce_roll(fl.land_pos, fl.land_vel, fl.land_spin, turf)
        total = math.hypot(b["rest_x"], b["rest_y"]); lat_t = b["rest_y"]
    else:
        total, lat_t = fl.carry_m, fl.lateral_m
    ms = st["ball_speed"]
    return ShotResult(ms, ms / 0.44704, 0.0, st["launch_deg"], st["azimuth_deg"], st["backspin_rpm"], st["sidespin_rpm"], st["spin_rpm"],
                      st["spin_axis_deg"], fl.carry_m, total, total - fl.carry_m, fl.apex_m, fl.hang_s, fl.descent_deg, fl.land_speed,
                      fl.landing_spin_rpm, fl.lateral_m, lat_t, fl.carry_m * M2YD, total * M2YD, turf)


def simulate_shot(dlv: Delivery, strike: Strike = None, p: Params = None, turf="normal", wind=(0, 0, 0), alt_m=0.0,
                  temp_c=15.0, rh=0.0, tee_m=0.0, dt=0.01, roll=True) -> ShotResult:
    """Full chain from club delivery."""
    p = p or load_params()
    im = impact(dlv, strike, p)
    r = _run(tuple(im["v_ball"]), tuple(im["omega"]), p, turf, wind, alt_m, temp_c, rh, tee_m, dt, roll)
    r.smash = im["smash"]
    return r
