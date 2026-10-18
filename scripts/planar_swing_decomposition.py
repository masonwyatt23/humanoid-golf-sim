"""Reduced planar-swing decomposition computed from data/references/public_joint_trajectories_110plus.json.

Question: which joints carry the swing IN the swing plane? Planar chain (lead side), all rates positive toward impact:
    club_in_plane_rate ~= trunk_in_plane_rate + arm_swing_rate + wrist_hinge_rate  (+ unexplained: hand translation, shoulder-girdle motion, definitions)

  trunk : thorax rotation. The published angle is treated as a top-view (horizontal-plane) projection of the shoulder line (ASSUMED; Madrid 'on-plane'
          line, see trajectory file). Convert to a rotation psi about the tilted spine axis (tilt theta_s from vertical):  psi = atan2(sin(psi_v)/cos(theta_s), cos(psi_v)).
          The swing-plane normal n is tilted phi from vertical toward the ball side (plane inclination phi from horizontal), so the angle between spine axis u and n is
          (phi - theta_s) and the in-plane share of the trunk rate is cos(phi - theta_s). Pure geometry; theta_s, phi are ASSUMED parameters (35 and 55 deg), swept in the output.
  arm   : -d(lead_arm_to_trunk)/dt (arm lowering toward the ball). In-plane share ASSUMED 1 (the published angle's plane is not verified).
  wrist : +d(lead_wrist_set_angle)/dt (uncocking = hinge, in plane by definition of the hinge).
Cited for the concept (not for numbers): Nesbit & Serrano 2005, J Sports Sci Med 4:520-533 (alpha = main swing rotation, beta = swing-plane pitch, gamma = shaft roll);
Nesbit 2005, J Sports Sci Med 4:499-519 (downswing is not in one fixed plane; hands and clubhead planes differ by about 9-12 deg). The angle values here are NOT from those papers.
Comparison reference: Madrid 2020 club peak angular speed (via kinematic_sequence_torque_reference_v2.json: 2362 deg/s at 110.4 mph + 49.61 deg/s per m/s).
Run: python scripts/planar_swing_decomposition.py
"""
import json
import math
import pathlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
TRAJ = ROOT / "data" / "references" / "public_joint_trajectories_110plus.json"
OUT = ROOT / "data" / "references" / "planar_swing_decomposition_public_refs.json"
THETA_S_DEG = 35.0   # ASSUMED spine tilt from vertical at/after address
PHI_DEG = 55.0       # ASSUMED driver swing-plane inclination from horizontal
CLUB_PEAK_ANCHOR = (110.4, 2362.0)   # Madrid 2020 anchor via kseq-v2 (mph, deg/s)
CLUB_SLOPE_DEG_S_PER_M_S = 49.61     # Madrid within-group slope (regression-diluted lower bound)
MPH = 0.44704


def _trapz(y, x):
    return float(np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(x)))


def in_plane_share(theta_s_deg=THETA_S_DEG, phi_deg=PHI_DEG):
    return math.cos(math.radians(phi_deg - theta_s_deg))


def topview_to_spine_axis_deg(psi_v_deg, theta_s_deg=THETA_S_DEG):
    """Top-view angle of a line in the plane perpendicular to a spine axis tilted theta_s -> rotation angle about the spine axis (unwrap-safe)."""
    pv = np.radians(np.asarray(psi_v_deg, float))
    return np.degrees(np.unwrap(np.arctan2(np.sin(pv) / math.cos(math.radians(theta_s_deg)), np.cos(pv))))


def club_peak_reference(mph):
    return CLUB_PEAK_ANCHOR[1] + CLUB_SLOPE_DEG_S_PER_M_S * (mph * MPH - CLUB_PEAK_ANCHOR[0] * MPH)


def decompose(traj, mph, theta_s_deg=THETA_S_DEG, phi_deg=PHI_DEG):
    ch = traj["channels"]
    cur = lambda name: ch[name]["speed_class_curves"][str(mph)]
    t = np.asarray(cur("thorax_rotation")["t_s"], float)
    psi = topview_to_spine_axis_deg(cur("thorax_rotation")["angle_deg"], theta_s_deg)
    share = in_plane_share(theta_s_deg, phi_deg)
    trunk_full = np.gradient(psi, t)                        # rate about the spine axis
    trunk = trunk_full * share                              # in-plane component
    trunk_out = trunk_full * math.sin(math.radians(phi_deg - theta_s_deg))
    arm = -np.gradient(np.asarray(cur("lead_arm_to_trunk")["angle_deg"], float), t)
    wrist = np.gradient(np.asarray(cur("lead_wrist_set_angle")["angle_deg"], float), t)
    total = trunk + arm + wrist
    down = (t >= -cur("thorax_rotation").get("downswing_duration_s", 0.25) - 1e-9) & (t <= 1e-9)
    # angle swept in plane top -> impact by each element (integral of rate over the downswing window)
    sw = {n: float(_trapz(x[down], t[down])) for n, x in (("trunk", trunk), ("arm", arm), ("wrist", wrist))}
    tot_sw = sum(sw.values())
    i = int(np.argmax(np.where(down, total, -1e9)))
    j = int(np.argmin(np.abs(t + 0.01)))   # last downswing sample before impact
    club_ref = club_peak_reference(mph)
    return {
        "mph": mph, "theta_s_deg": theta_s_deg, "phi_deg": phi_deg, "trunk_in_plane_share": round(share, 3),
        "t_s": t.tolist(),
        "rates_deg_s": {"trunk_in_plane": np.round(trunk, 1).tolist(), "arm_swing": np.round(arm, 1).tolist(),
                        "wrist_hinge": np.round(wrist, 1).tolist(), "chain_sum": np.round(total, 1).tolist(),
                        "trunk_out_of_plane": np.round(trunk_out, 1).tolist()},
        "swept_in_plane_deg": {k: round(v, 1) for k, v in sw.items()},
        "share_of_swept_in_plane_angle": {k: round(v / tot_sw, 3) for k, v in sw.items()},
        "peak_chain_sum_deg_s": round(float(total[i]), 1), "peak_chain_sum_time_ms_before_impact": round(float(-t[i] * 1000), 1),
        "chain_sum_at_last_downswing_sample_deg_s": round(float(total[j]), 1),
        "contributions_at_peak_deg_s": {"trunk": round(float(trunk[i]), 1), "arm": round(float(arm[i]), 1), "wrist": round(float(wrist[i]), 1)},
        "club_peak_published_reference_deg_s": round(club_ref, 0),
        "chain_peak_over_club_peak": round(float(total[i]) / club_ref, 3),
        "unexplained_note": "chain sum is below the club peak: hand-path translation, shoulder-girdle and pelvis contributions and the different definitions of the published lines are not in the chain. Not tuned to match.",
    }


def build():
    traj = json.loads(TRAJ.read_text())
    out = {"_meta": {
        "title": "Reduced planar-swing decomposition from public joint trajectories (geometry + published curves)",
        "version": 1, "generated_by": "scripts/planar_swing_decomposition.py", "derived": True, "synthetic_interpolation": True,
        "contains_instagram_or_mason_derived_data": False, "derived_from_cmu_multisense_amass_golfdb": False,
        "status": "DERIVED from SYNTHETIC curves plus ASSUMED geometry (spine tilt 35 deg, plane inclination 55 deg). Not measured; nothing here is a published decomposition.",
        "concept_citations": ["Nesbit & Serrano 2005, J Sports Sci Med 4:520-533 (alpha main swing / beta plane pitch / gamma shaft roll Euler decomposition of the club)",
                              "Nesbit 2005, J Sports Sci Med 4:499-519 (not a single fixed plane; hands vs clubhead plane differ ~9-12 deg)"],
        "assumed_parameters": {"theta_s_deg": THETA_S_DEG, "phi_deg": PHI_DEG, "arm_in_plane_share": 1.0,
                               "topview_angle_assumption": "thorax_rotation is a top-view projection of the shoulder line"},
        "geometry": "psi = atan2(sin(psi_v)/cos(theta_s), cos(psi_v)); in-plane share of rotation about spine axis = cos(phi - theta_s); the rest (sin) tilts/pitches the plane.",
        "chain": "club_in_plane_rate ~= trunk_in_plane + arm_swing + wrist_hinge + unexplained",
        "g1_carriers_in_plane": {"trunk": ["waist_yaw_joint", "waist_pitch_joint", "waist_roll_joint", "free-base pelvis yaw via hips"],
                                 "arm_swing": ["lead shoulder_pitch (+roll/yaw to follow the plane)", "lead elbow (arm length/radius)"],
                                 "wrist_hinge": ["lead wrist_pitch or wrist_yaw (which one depends on forearm roll and hand frame: UNVERIFIED)"],
                                 "status": "assumed, see data/references/g1_joint_mapping_public_refs.json"},
    }, "classes": {}, "sensitivity_in_plane_share": {}}
    for mph in traj["_meta"]["speed_classes_mph"]:
        out["classes"][str(mph)] = decompose(traj, mph)
    for th in (25, 35, 45):
        for ph in (45, 55, 65):
            out["sensitivity_in_plane_share"][f"theta_s={th}_phi={ph}"] = round(in_plane_share(th, ph), 3)
    return out


def main():
    OUT.write_text(json.dumps(build(), indent=1) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
