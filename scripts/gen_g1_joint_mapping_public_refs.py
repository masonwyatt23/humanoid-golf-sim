"""Rough G1 mapping of the public human joint-angle references. Reads env/models/*.xml READ-ONLY for joint names/ranges/actuators.

Everything about sign and axis was checked by forward kinematics (read-only MuJoCo FK on env/models/humanoid_golf_v5_g1_rh.xml, qpos0, other joints 0)
on 2026-10-18, but the mapping from published human angle definitions to G1 joints is ROUGH and mostly UNVERIFIED (labels per entry).
No Instagram/CMU/MultiSense/AMASS/GolfDB data. Run: python scripts/gen_g1_joint_mapping_public_refs.py
"""
import json
import math
import pathlib
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "references" / "g1_joint_mapping_public_refs.json"
V5 = ROOT / "env" / "models" / "humanoid_golf_v5_g1_rh.xml"
V5L = ROOT / "env" / "models" / "humanoid_golf_v5_g1_lh.xml"
V4 = ROOT / "env" / "models" / "humanoid_golf_v4_power.xml"

# FK measurements (read-only, G1 own frame: +x forward, +y left, +z up; arm of the LEFT side, other joints 0). Interior angle from link origins -> approximate.
FK_ELBOW_FLEXION_DEG = {"q_rad": [-1.0, -0.5, 0.0, 0.5, 1.0], "flexion_deg": [135, 107, 80, 52, 25],
                        "linear_fit": "flexion_deg = 80 - 55 * q_rad (valid for q in [-1.05, 1.0]; flexion rises again beyond q ~ 1.4)"}
ELBOW_Q0_FLEX_DEG, ELBOW_SLOPE_DEG_PER_RAD = 80.0, -55.0
SHOULDER_REST_FORWARD_DEG = 5.0   # at shoulder_pitch=0 the upper arm hangs ~5 deg forward of vertical (FK)


def parse_joints(path):
    root = ET.parse(path).getroot()
    joints = {}
    for j in root.iter("joint"):
        n = j.get("name")
        if n:
            joints[n] = {"type": j.get("type", "hinge"), "range": j.get("range"), "axis": j.get("axis")}
    act = set()
    for a in root.find("actuator"):
        if a.get("joint"):
            act.add(a.get("joint"))
    return joints, act


def ctor(side_handed):
    """(lead_side, trail_side) PHYSICAL G1 sides. v5: LH golfer lead = physical right (env/v5_body.py lead_trail)."""
    return ("right", "left") if side_handed == "LH" else ("left", "right")


def waist_yaw_rad(x_factor_deg, handed="RH"):
    """x_factor in the reference (RH convention: + toward target, backswing negative). G1 waist_yaw + = CCW seen from above (FK: left shoulder moves back).
    RH golfer (G1 faces -y, target on golfer's left): backswing is CW = negative yaw -> yaw = +x_factor. LH: yaw = -x_factor. UNVERIFIED vs an actual env run."""
    s = 1.0 if handed == "RH" else -1.0
    return math.radians(s * x_factor_deg)


def elbow_q_rad(flexion_deg):
    """G1 elbow joint angle for a given flexion (0 = straight): q = (80 - flex) / 55 (FK-fitted, approximate, same sign for both hands/sides)."""
    return (ELBOW_Q0_FLEX_DEG - flexion_deg) / (-ELBOW_SLOPE_DEG_PER_RAD)


def shoulder_pitch_rad(arm_elevation_deg):
    """Sagittal-plane arm elevation from hanging (positive = forward/up) -> G1 shoulder_pitch (negative = forward flexion, FK). Roll/yaw assumed 0."""
    return -math.radians(arm_elevation_deg - SHOULDER_REST_FORWARD_DEG)


def wrist_hinge_rad(set_angle_deg, address_set_angle_deg=None, sign=+1.0):
    """Hinge magnitude only: w = 90 - interior (repo note); sign of the G1 joint (pitch vs yaw) UNVERIFIED -> `sign` is an explicit parameter."""
    w = 90.0 - set_angle_deg
    return sign * math.radians(w)


def build():
    j5, a5 = parse_joints(V5)
    j4, a4 = parse_joints(V4)
    jl, _ = parse_joints(V5L)
    rng = lambda n: j5[n]["range"]
    def jinfo(n, role, human, rule, status, note=""):
        return {"g1_joint_left": n.replace("{S}", "left") if "{S}" in n else n, "g1_joint_right": n.replace("{S}", "right") if "{S}" in n else n,
                "range_rad_left": rng(n.replace("{S}", "left")), "range_rad_right": rng(n.replace("{S}", "right")),
                "actuated_v5": all(x in a5 for x in ([n.replace("{S}", "left"), n.replace("{S}", "right")] if "{S}" in n else [n])),
                "role_lh_lead_physical": "right" if "{S}" in n else None, "human_channel": human, "rule": rule, "status": status, "note": note}
    m = {
        "waist_yaw": {"g1_joint": "waist_yaw_joint", "range_rad": rng("waist_yaw_joint"), "axis": "z of waist_yaw_link (+ = CCW from above, FK-checked)",
                      "actuated_v5": "waist_yaw_joint" in a5, "human_channel": "x_factor (thorax - pelvis rotation)",
                      "rule": "waist_yaw_rad = +x_factor_rad (RH golfer), -x_factor_rad (LH golfer); x_factor in the reference RH convention (+ toward target)",
                      "status": "UNVERIFIED sign vs a real env run; magnitude: top -61 deg, impact -14 deg (derived) is well inside +-150 deg",
                      "note": "v5 address waist_yaw ~ -1 deg (LH_105) so the x_factor=0 address assumption is fine. Absolute thorax -103 deg exceeds nothing here because it is pelvis-relative."},
        "pelvis_rotation": {"g1_joint": "NONE (free-base pelvis yaw in v5)", "human_channel": "pelvis_rotation",
                            "rule": "world yaw of the free base relative to address heading: d_yaw = +pelvis_deg (RH) / -pelvis_deg (LH) about world z (LH G1 is yawed +90 deg, LH backswing = CCW = +z)",
                            "status": "UNVERIFIED. v5 has no pelvis yaw joint; pelvis turn comes from hips + ground reaction. g1_golf_env.py (old env, cannot be read as v5) adds a hinge named pelvis_yaw (+-1.6 rad); v4_power has none.",
                            "note": "Use as a reward target on measured pelvis heading, not as a joint position target."},
        "waist_pitch": {"g1_joint": "waist_pitch_joint", "range_rad": rng("waist_pitch_joint"), "actuated_v5": True, "human_channel": "none (no public channel here)",
                        "rule": "+ = forward lean (FK: shoulders move +x and down); hold the address value", "status": "no reference supplied; sign FK-verified"},
        "waist_roll": {"g1_joint": "waist_roll_joint", "range_rad": rng("waist_roll_joint"), "actuated_v5": True, "human_channel": "none (no public channel here)",
                       "rule": "+ = about +x: G1-left shoulder rises (FK); lateral bend sign flips LH vs RH", "status": "no reference supplied; sign FK-verified"},
        "arm_to_trunk": {**jinfo("{S}_shoulder_pitch_joint", None, "lead_arm_to_trunk / trail_arm_to_trunk", "shoulder_pitch_rad = -(elevation_deg - 5 deg) in rad; roll=yaw=0 (assumed)",
                         "UNVERIFIED: Zheng 'arm to trunk' plane/definition not verified; elevation assumed sagittal and trunk-relative (G1 shoulder is distal of the waist joints, so trunk-relative is natural)",
                         "negative pitch = forward flexion (FK: q=-1.5 rad puts the upper arm horizontal forward). Lead top 90 -> -85 deg, impact 35 -> -30 deg. Trail top 43, impact 23."),
                         "roll_yaw_note": "shoulder_roll (+ abducts left arm; right-side range is mirrored) and shoulder_yaw carry the plane tilt; no public channel; do not constrain. Roll/yaw/wrist roll/wrist yaw flip sign between mirrored sides."},
        "elbow": {**jinfo("{S}_elbow_joint", None, "lead_elbow_flexion / trail_elbow_flexion", "q_rad = (80 - flexion_deg) / 55 (FK-fitted: flexion = 80 - 55 q)",
                  "ROUGH, FK-derived from link origins (+-~10 deg); Zheng flexion definition unverified; lead top 58 -> q 0.40, impact 34 -> 0.84; trail top 130 -> -0.91, impact 40 -> 0.73",
                  "pitch joints do not change sign LH vs RH. Range -1.047..2.094; trail top 130 deg flexion needs q=-0.91 (inside range, near the limit). Flexion is NOT monotone in q above ~1.4."),
                  "fk_table": FK_ELBOW_FLEXION_DEG},
        "wrist_hinge": {"candidates": ["{S}_wrist_pitch_joint (axis y)", "{S}_wrist_yaw_joint (axis z)", "{S}_wrist_roll_joint (axis x) is forearm roll, not hinge"],
                        "ranges_rad": {"wrist_pitch": rng("left_wrist_pitch_joint"), "wrist_yaw": rng("left_wrist_yaw_joint"), "wrist_roll": rng("left_wrist_roll_joint")},
                        "actuated_v5": all(f"{s}_wrist_{k}_joint" in a5 for s in ("left", "right") for k in ("roll", "pitch", "yaw")),
                        "stock_torque_nm": {"wrist_roll": 25, "wrist_pitch": 5, "wrist_yaw": 5, "source": "env/v5_body.py STOCK (read); docs/V5_STAGE0_REPORT.md: the 5 N*m limits were binding"},
                        "human_channel": "lead_wrist_set_angle (94 -> 165 deg), trail_wrist_angle (75 -> 118 deg)",
                        "rule": "hinge magnitude w = 90 - interior; lead top w=-4, impact w=-75 (release 71 deg); trail top 15, impact -28 (release 43). Which joint carries the cock depends on forearm roll and hand frame",
                        "status": "UNVERIFIED which of pitch/yaw is the hinge and the sign (FK at wrist_roll=0: pitch moves the hand in the vertical plane of the forearm, yaw in the horizontal plane; the golf grip orientation determines which is the cock plane). Use magnitude and timing only.",
                        "note": "Old g1_poses.json (another env) has wrist_yaw ~ 89 deg at address, i.e. that env used yaw for the grip rotation; not verified for v5."},
    }
    unact_v4 = sorted(set(j4) - a4 - {"root"})
    return {
        "_meta": {
            "title": "Rough mapping: public human pelvis/thorax/X-factor/arm/elbow/wrist references -> Unitree G1 joints (v5 env) and v4_power names",
            "version": 1, "generated_by": "scripts/gen_g1_joint_mapping_public_refs.py", "derived": True,
            "contains_instagram_or_mason_derived_data": False, "derived_from_cmu_multisense_amass_golfdb": False,
            "status": "ROUGH. Names, ranges and actuators READ from the XMLs; axes/signs FK-checked; the human->G1 correspondences are assumptions unless an entry says otherwise.",
            "read_only_sources": ["env/models/humanoid_golf_v5_g1_rh.xml", "env/models/humanoid_golf_v5_g1_lh.xml", "env/models/humanoid_golf_v4_power.xml", "env/v5_body.py (lead_trail, STOCK)", "docs/HANDEDNESS.md"],
            "g1_frame": "G1 faces +x in its own frame, +y left, +z up. v5 LH golfer: body yawed +90 deg (faces +y), physical RIGHT side toward the target = LEAD side (right_* = lead). v5 RH: yawed -90 deg, left_* = lead.",
            "conflict_with_older_docs": "docs/HANDEDNESS.md and the trajectory file state env right_* = TRAIL arm. That holds for the old simple/v4 env (right_* motors = club-hand arm for a RH golfer). In v5 (physical G1 sides) right_* is the LEAD arm for a LEFT-handed golfer. Always choose side by role through env/v5_body.py lead_trail(handed).",
            "lh_mirror_rule": {"summary": "Reference channels are in golfer ROLES (lead/trail). Pick the physical side with lead_trail(handed). Yaw and roll joints (waist_yaw, waist_roll, shoulder_roll, shoulder_yaw, wrist_roll, wrist_yaw) flip sign between handedness (and between the physical sides of one body); pitch joints (shoulder_pitch, elbow, wrist_pitch, waist_pitch) do not. x_factor/pelvis (RH convention + toward target) are negated for LH. The v5 XMLs already mirror right-side roll/yaw ranges, so an exactly mirrored pose is q_right_roll_or_yaw = -q_left.",
                               "status": "rule restated from HANDEDNESS.md and checked against the XML range mirroring and FK; not exercised in a training run"},
            "v5_all_29_joints_actuated": all(n in a5 for n in j5 if n.endswith("_joint") and not n.startswith(("floating", "club", "ball"))),
            "v4_power_unactuated_joints": unact_v4,
            "v4_power_names": {"waist": "chest_yaw (+-60 deg)", "shoulders": "{side}_shoulder_pitch/roll", "elbows": "{side}_elbow", "wrist": "right_wrist only (trail); no lead wrist", "no_pelvis_yaw": True},
            "weak_spots": ["human angle definitions (Zheng) unverified", "wrist hinge joint unverified", "wrist pitch/yaw stock torque 5 N*m", "no waist roll/pitch/shoulder roll/yaw references",
                           "pelvis has no joint in v5", "elbow FK-fit uses link origins"],
        },
        "mapping": m,
    }


def main():
    OUT.write_text(json.dumps(build(), indent=1) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
