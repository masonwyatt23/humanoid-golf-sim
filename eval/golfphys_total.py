"""Independent total-distance recompute for the realism harness: feed a strike's measured launch conditions (ball speed, launch, azimuth, back/side spin)
through golfphys (this repo's vendored copy = Data Agent branch golfphys-lh-fix 357bc0c; flight + bounce_roll roll model, normal turf) and return carry / total / total-over-carry.
The env's own `total_m_model` is the SAME golfphys with roll=True (env/v5_shot.py), `carry_m_noroll` is its no-roll carry; this module re-derives both from the logged launch state so the number is checked, not trusted.
Distances are carry/total from the tee along the ball's launch line (hypot of x,y), yards. Model-only: golfphys roll is validated only for normal turf (roll_aoa_validation, total/carry 1.07-1.13) and is not calibrated for very low-speed / low-launch shots."""
import math
M2YD = 1.0 / 0.9144
MPH = 0.44704

def golfphys_total(ball_mph, launch_deg, backspin_rpm, sidespin_rpm=0.0, azimuth_deg=0.0, turf="normal"):
    from golfphys.sim import shot_from_launch
    spin = math.hypot(backspin_rpm, sidespin_rpm); axis = math.degrees(math.atan2(sidespin_rpm, backspin_rpm))
    kw = dict(azimuth_deg=azimuth_deg, spin_axis_deg=axis, turf=turf, tee_m=0.0)
    r = shot_from_launch(ball_mph * MPH, launch_deg, spin, roll=True, **kw)
    n = shot_from_launch(ball_mph * MPH, launch_deg, spin, roll=False, **kw)
    carry = r.carry_m * M2YD; total = r.total_m * M2YD
    return dict(carry_yd=carry, total_yd=total, noroll_carry_yd=n.carry_m * M2YD, total_over_carry=(total / carry if carry > 0 else None), descent_deg=r.descent_deg, backspin_rpm=r.backspin_rpm, sidespin_rpm=r.sidespin_rpm,
                lateral_carry_yd=n.lateral_carry_m * M2YD)   # signed lateral offset at landing (no-roll flight), yd
