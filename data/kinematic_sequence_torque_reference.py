"""Published-biomechanics kinematic-sequence / joint-work / GRF reference + actuator feasibility helper.

Everything here derives from published studies only (see docs/KINEMATIC_SEQUENCE_TORQUE_REFERENCE.md and
data/references/kinematic_sequence_torque_reference.json). No Mason / Instagram-derived data.
Model-only: values above ~116 mph club speed are EXTRAPOLATED beyond every published group used, and joint-work
numbers come from single-swing inverse-dynamics models of 4 amateurs (Nesbit & Serrano 2005). Unverified.
"""
import json
import math
import os

from data import speed_gap_100_120 as _sg

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "references", "kinematic_sequence_torque_reference.json")
MS_TO_MPH = 2.23694

# Nesbit & Serrano 2005 (J Sports Sci Med 4:520-533) Table 2, male scratch golfer, top of backswing -> impact, J (N*m).
# CHS 52.0 m/s (116.3 mph). Single self-selected swing; model-derived (not measured) internal work.
NESBIT_CHS_MS = 52.0
NESBIT_WORK_J = {
    "right_ankle": 19.8, "left_ankle": -2.4, "right_knee": 38.4, "left_knee": -4.2,
    "right_hip": 297.0, "left_hip": 126.0, "lumbar": 342.0, "thoracic": 277.0,
    "right_shoulder": 63.0, "left_shoulder": 57.0, "right_elbow": 125.0, "left_elbow": 23.0,
    "right_wrist": 56.0, "left_wrist": 34.0,
}
NESBIT_TOTAL_J = 1452.0
# four subjects: (CHS m/s, total body work J) for the exponent fit (single swings, one female, mixed skill)
NESBIT_CHS_WORK = [(42.1, 878.0), (46.3, 1105.0), (49.7, 1429.0), (52.0, 1452.0)]
NESBIT_CHS_GRIP_TORQUE = [(42.1, 24.0), (46.3, 24.6), (49.7, 36.8), (52.0, 42.1)]  # max grip alpha torque N*m
NESBIT_CHS_PEAK_POWER = [(42.1, 1720.0), (46.3, 2310.0), (49.7, 3005.0), (52.0, 3875.0)]  # club peak power W
DOWNSWING_S = 0.23  # elite driver downswing duration (Hume 2005 citing Cochran & Stobbs); held constant (assumption)

GROUPS = {  # Nesbit joints -> body group
    "hips": ("right_hip", "left_hip"),
    "spine": ("lumbar", "thoracic"),
    "shoulders": ("right_shoulder", "left_shoulder"),
    "elbows": ("right_elbow", "left_elbow"),
    "wrists": ("right_wrist", "left_wrist"),
    "legs": ("right_ankle", "left_ankle", "right_knee", "left_knee"),
}

# Actuator tiers of env/g1_golf_env.py (torque N*m, speed rad/s), read-only copy. 'elite' is HYPOTHETICAL.
G1_TIERS = {
    "stock": {"pelvis_yaw": (176, 32), "waist_yaw": (88, 32), "waist_roll_pitch": (50, 32),
              "shoulder_axis": (25, 37), "elbow": (25, 37), "wrist_roll": (25, 37), "wrist_pitch_yaw": (5, 22)},
    "elite": {"pelvis_yaw": (500, 45), "waist_yaw": (250, 45), "waist_roll_pitch": (250, 45),
              "shoulder_axis": (75, 55), "elbow": (75, 55), "wrist_roll": (30, 55), "wrist_pitch_yaw": (30, 55)},
}
# simple MuJoCo envs (env/models/humanoid_golf_v3.xml, _v4_power.xml): peak joint torque = forcerange * gear, N*m
SIMPLE_ENV_TORQUE = {
    "v3": {"right_shoulder_pitch": 250, "right_shoulder_roll": 150, "right_elbow": 120, "right_wrist": 60,
           "left_shoulder_pitch": 150, "chest_yaw": 120, "right_hip_pitch": 250, "left_hip_pitch": 250},
    "v4_power": {"right_shoulder_pitch": 250, "right_shoulder_roll": 150, "right_elbow": 120, "right_wrist": 120,
                 "left_shoulder_pitch": 150, "chest_yaw": 120, "right_hip_pitch": 250, "left_hip_pitch": 250},
}
SIMPLE_ENV_DAMPING = {"v3": {"right_wrist": 2.0, "chest_yaw": 1.0}, "v4_power": {"right_wrist": 0.5, "chest_yaw": 1.0}}


def load():
    with open(JSON_PATH) as f:
        return json.load(f)


def mph_to_ms(mph):
    return mph / MS_TO_MPH


def powerlaw_exponent(points):
    """Least-squares exponent k of y = a*x^k on (x, y) pairs."""
    xs = [math.log(x) for x, _ in points]
    ys = [math.log(y) for _, y in points]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


WORK_EXPONENT = powerlaw_exponent(NESBIT_CHS_WORK)
POWER_EXPONENT = powerlaw_exponent(NESBIT_CHS_PEAK_POWER)
GRIP_TORQUE_SLOPE = (NESBIT_CHS_GRIP_TORQUE[-1][1] - NESBIT_CHS_GRIP_TORQUE[0][1]) / (
    NESBIT_CHS_GRIP_TORQUE[-1][0] - NESBIT_CHS_GRIP_TORQUE[0][0])


def tag_for_chs(chs_mph, lo_mph=94.2, hi_mph=116.3):
    """Nesbit subjects span 42.1-52.0 m/s = 94.2-116.3 mph."""
    return "measured-range" if lo_mph <= chs_mph <= hi_mph else "extrapolated"


def segment_peak_deg_s(seg, chs_mph):
    """Peak rotational speed (deg/s) from the Cheetham fit in data/speed_gap_100_120.py (interpolated 88-109, extrapolated outside)."""
    return _sg.target_deg_s(seg, chs_mph)


def joint_work_J(joint, chs_mph):
    return NESBIT_WORK_J[joint] * (mph_to_ms(chs_mph) / NESBIT_CHS_MS) ** WORK_EXPONENT


def group_work_J(group, chs_mph):
    return sum(joint_work_J(j, chs_mph) for j in GROUPS[group])


def total_work_J(chs_mph):
    return NESBIT_TOTAL_J * (mph_to_ms(chs_mph) / NESBIT_CHS_MS) ** WORK_EXPONENT


def avg_power_W(group, chs_mph, downswing_s=DOWNSWING_S):
    return group_work_J(group, chs_mph) / downswing_s


def grip_torque_Nm(chs_mph):
    """Linear fit through the four Nesbit subjects (max grip alpha torque at the club)."""
    return NESBIT_CHS_GRIP_TORQUE[-1][1] + GRIP_TORQUE_SLOPE * (mph_to_ms(chs_mph) - NESBIT_CHS_GRIP_TORQUE[-1][0])


def max_power_W(torque, speed):
    """Peak power of a motor whose torque falls linearly to 0 at `speed` (the env/g1_golf_env.py derate): tau*w/4."""
    return torque * speed / 4.0


def torque_at_speed(torque, speed, w):
    return max(0.0, torque * (1.0 - abs(w) / speed))


def g1_group_capacity_W(group, tier):
    t = G1_TIERS[tier]
    p = lambda k: max_power_W(*t[k])
    return {
        "hips": p("pelvis_yaw"),  # pelvis_yaw is the single stand-in for both hips
        "spine": p("waist_yaw"),  # yaw only (strict)
        "spine_all_axes": p("waist_yaw") + 2 * p("waist_roll_pitch"),
        "shoulders": 2 * 3 * p("shoulder_axis"),
        "elbows": 2 * p("elbow"),
        "wrists": 2 * (p("wrist_roll") + 2 * p("wrist_pitch_yaw")),  # all three axes at once (optimistic)
        "wrists_pitch_only": 2 * p("wrist_pitch_yaw"),  # the env's club-release axis
    }[group]


def g1_feasibility(chs_mph, tier, peak_over_avg=2.5):
    """required avg power / max available power per body group. >1 means infeasible even at optimal speed."""
    rows = {}
    for g, base in (("hips", "hips"), ("spine", "spine"), ("spine_all_axes", "spine"), ("shoulders", "shoulders"),
                    ("elbows", "elbows"), ("wrists", "wrists"), ("wrists_pitch_only", "wrists")):
        req = avg_power_W(base, chs_mph)
        cap = g1_group_capacity_W(g, tier)
        rows[g] = {"required_avg_W": req, "est_required_peak_W": req * peak_over_avg, "capacity_max_W": cap,
                   "ratio_avg": req / cap, "ratio_est_peak": req * peak_over_avg / cap}
    return rows


def check_json_consistency(d=None):
    d = d or load()
    errs = []
    for row in d["scaling_to_chs"]["rows"]:
        v = row["chs_mph"]
        for seg in _sg.ORDER:
            if abs(row["segment_peak_deg_s"][seg] - segment_peak_deg_s(seg, v)) > 1.0:
                errs.append(("segment", v, seg))
        if abs(row["total_body_work_J"] - total_work_J(v)) > 1.0:
            errs.append(("work", v))
    return errs
