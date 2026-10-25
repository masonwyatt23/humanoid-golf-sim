"""Goal-conditioned driver task (DREnv --goal_sample / --goal_w / --goal_curr; all default off). LOCAL, NOT OFFICIAL.
Conventions match harness v5 (hgs scott-e abce0a9 eval/harness_v5.py): world +y = left of the +x target line; golfphys + spin axis curves
toward +y for either hand; LH draw curves -y, LH fade +y; bend = commanded |spin axis| (deg); shape graded on the golfer-frame axis (+ = draw).
TRAINING goal distribution (a superset of, and not identical to, the Evaluator's 8 fixed GOAL_SET_V5 goals: carry 110-170 m, dir -12..+12 deg,
4 straight / 2 draw / 2 fade, bends 4-5 deg):
  club driver; handedness LH; target_carry ~ U(100, 180) m; target_dir ~ U(-15, +15) deg (world, + = left);
  shape fade/straight/draw w.p. 0.25/0.50/0.25; bend = 0 for straight, ~ U(2, 6) deg for draw/fade.
  Optional curriculum --goal_curr F (fraction of training): c = min(1, 0.25 + 0.75 * progress / F); carry U(140 - 40c, 140 + 40c),
  dir U(-15c, +15c), P(draw) = P(fade) = 0.25c, bend U(2, 2 + 4c). Default (no --goal_curr) = full ranges from the start.
Goal RNG is a separate np.random.Generator (seeded from the reset seed / env seed), so DR draws are unchanged by the sampler.
TASK REWARD (--goal_w W > 0; episode end, contact episodes only; 0 otherwise):
  r = W * (exp(-0.5 (carry_err_pct / 5)^2) + exp(-0.5 (dir_err_deg / 4)^2) + r_shape)
  carry_err_pct = 100 |carry_m_noroll - target_carry| / target_carry; dir_err_deg = azimuth_deg (golfphys start dir, world) - target_dir
  straight: r_shape = exp(-0.5 (curve_y_m / 5)^2), curve_y_m = lateral_carry_m - carry * tan(azimuth)
  draw/fade: ax_g = draw_sign * spin_axis_deg (draw_sign = -1 LH, +1 RH); tgt = +bend (draw) / -bend (fade);
             r_shape = exp(-0.5 ((ax_g - tgt) / max(2, 0.5 bend))^2)
  (sigmas = the harness pass bands: carry 5 %, curve 5 m, bend max(2, 50 %); direction 4 deg is tighter than the 7 deg pass band, ours)."""
import math, numpy as np

CARRY = (100.0, 180.0); DIR = 15.0; SHAPES = ("fade", "straight", "draw"); P_SHAPE = (0.25, 0.5, 0.25); BEND = (2.0, 6.0)

def sample_goal(rng, c=1.0):
    c = float(min(max(c, 0.0), 1.0)); mid = 0.5 * (CARRY[0] + CARRY[1]); half = 0.5 * (CARRY[1] - CARRY[0])
    u = rng.random(); pd = P_SHAPE[0] * c; sh = "fade" if u < pd else "draw" if u < 2 * pd else "straight"
    bend = 0.0 if sh == "straight" else float(rng.uniform(BEND[0], BEND[0] + (BEND[1] - BEND[0]) * c))
    return dict(club="driver", target_carry=round(float(rng.uniform(mid - half * c, mid + half * c)), 2), target_dir=round(float(rng.uniform(-DIR * c, DIR * c)), 3),
                shape=sh, bend=round(bend, 3), handedness="LH")

def curr_c(progress, goal_curr):
    return 1.0 if not goal_curr else min(1.0, 0.25 + 0.75 * float(progress) / float(goal_curr))

def task_reward(info, goal, w):
    if w <= 0 or not info.get("contact") or "carry_m_noroll" not in info: return 0.0, None
    carry = float(info["carry_m_noroll"]); az = float(info.get("azimuth_deg", 0.0)); lat = float(info.get("lateral_carry_m", 0.0))
    tc = float(goal["target_carry"]); ce = 100.0 * abs(carry - tc) / max(tc, 1.0); de = az - float(goal.get("target_dir", 0.0))
    curve = lat - carry * math.tan(math.radians(az)); sh = goal.get("shape", "straight"); bend = abs(float(goal.get("bend", 0.0)))
    if sh == "straight": rs = math.exp(-0.5 * (curve / 5.0) ** 2); axg = None
    else:
        sgn = -1.0 if str(goal.get("handedness", "LH")).upper() == "LH" else 1.0; axg = sgn * float(info.get("spin_axis_deg", 0.0)); tgt = bend if sh == "draw" else -bend
        rs = math.exp(-0.5 * ((axg - tgt) / max(2.0, 0.5 * bend)) ** 2)
    rc = math.exp(-0.5 * (ce / 5.0) ** 2); rd = math.exp(-0.5 * (de / 4.0) ** 2)
    return w * (rc + rd + rs), dict(goal_r=round(w * (rc + rd + rs), 4), goal_rc=round(rc, 4), goal_rd=round(rd, 4), goal_rs=round(rs, 4), goal_carry_err_pct=round(ce, 3),
                                    goal_dir_err_deg=round(de, 3), goal_curve_y_m=round(curve, 3), goal_axis_golfer_deg=(round(axg, 3) if axg is not None else None))
