"""Builds data/references/realism_thresholds.json. Published/derived numbers are copied from the kseq-reference branch (b78e5eb)
JSON (git show) and from data/references/launch_targets_120_132_limits.json (already in this branch); thresholds are tagged.
Run: python scripts/build_realism_thresholds.py   (needs the kseq-reference branch in the same repo)"""
import json, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
K = json.loads(subprocess.check_output(["git", "show", "kseq-reference:data/references/kinematic_sequence_torque_reference.json"], cwd=ROOT))
L = json.load(open(ROOT / "data/references/launch_targets_120_132_limits.json"))
T = lambda value, source, tag, note="": dict(value=value, source=source, tag=tag, note=note)

rows = K["scaling_to_chs"]["rows"]
scal = [dict(chs_mph=r["chs_mph"], segment_peak_deg_s=r["segment_peak_deg_s"], tag=("extrapolated" if r["chs_mph"] in (90, 120, 132) else "interpolated"),
             grip_torque_Nm=r["grip_torque_Nm"]) for r in rows]
feas = {tier: {chs: {g: round(v["ratio_avg"], 3) for g, v in groups.items()} for chs, groups in d.items()} for tier, d in K["feasibility_g1_env"]["by_tier_and_chs"].items()}
out = {
 "label": "Thresholds for realism/ (check_swing_realism, check_shot_realism). Every entry: value, source, tag. Tags: published (value printed in a source), derived (computed from published numbers), assumption (my choice, no source), extrapolated (outside every published population), model (golfphys output, not a measurement). No Mason / Instagram data.",
 "generated": "2026-10-17 America/New_York",
 "upstream": {"kseq": "branch kseq-reference b78e5eb data/references/kinematic_sequence_torque_reference.json", "launch_limits": "data/references/launch_targets_120_132_limits.json (golfphys branch ancestry)", "golfphys": "branch golfphys 0c2bca2"},
 "measured_chs_range_mph": T([88, 109], "Cheetham 2008 amateur 88 / pro 109 mph (Parker 103, Myers n/a)", "published", "inside this range segment peaks are interpolated between measured groups; outside it they are extrapolated"),
 "sequence": {
  "order": T(["pelvis", "thorax", "arm", "club"], "Cheetham 2008 (pros), Parker 2018, Tinmark 2007 (n=47)", "published", "proximal-to-distal peak speed order"),
  "lead_before_club_peak_ms_pro": T({"pelvis": 87, "thorax": 68, "arm": 65, "club": 0}, "Cheetham 2008 Table (pros)", "published"),
  "lead_before_club_peak_ms_amateur": T({"pelvis": 78, "thorax": 59, "arm": 64, "club": 0}, "Cheetham 2008 (amateurs; thorax/arm order swapped on average)", "published"),
  "lead_band_ms_warn": T({"pelvis": [40, 140], "thorax": [25, 110], "arm": [15, 110]}, "derived: roughly +/-50 % around the Cheetham means", "assumption", "warn outside; sim control rate 50 Hz gives only 20 ms resolution"),
  "tie_tolerance_ms": T(20, "env control dt = 0.02 s (docs/EVAL_PROTOCOL / env substeps)", "assumption", "peaks closer than this are treated as simultaneous (warn, not fail)"),
  "swap_warn_ms": T(30, "Cheetham amateurs: arm/thorax order swapped by 5 ms on average", "derived", "thorax/arm swapped by <= this: warn"),
 },
 "peak_speed": {
  "rows_by_chs": T(scal, "kseq-reference scaling_to_chs (Cheetham two-group power-law fit, data/speed_gap_100_120.py)", "derived", "rows tagged extrapolated at 90, 120, 132 mph; 100 and 110 are between measured groups"),
  "pass_ratio": T([0.7, 1.3], "published spread: pelvis 358-519 deg/s across studies (Cheetham/Parker/Myers), Parker SD 10-16 %; definitions (resultant vs yaw) differ", "assumption"),
  "warn_ratio": T([0.5, 1.7], "same", "assumption", "outside warn_ratio = fail"),
 },
 "x_factor": {
  "top_of_backswing_deg": T({"pass": [40, 65], "warn": [28, 80], "fail_outside": [20, 90]}, "Parker 54.9+-7.9 (elite), Myers 44.2/49.5/59.1, Hume review 24-38 (long vs short hitters), Burden 70; kseq doc recommends 45-62", "derived", "method dependent (joint-coordinate vs sensor)"),
  "stretch_deg": T("not checked", "Parker 2.9+-3.4; joint-coordinate studies 1-3 deg; Cheetham sensor method ~10+ deg", "published", "small stretch must not be penalised (kseq recommendation 3)"),
 },
 "actuators": {
  "g1_tiers_tau_Nm_w_rad_s": T(K["actuator_limits_read_from_env"]["g1_tiers"], "env/g1_golf_env.py tier table, read by kseq-reference", "published", "stock = Unitree G1 rated; elite = HYPOTHETICAL"),
  "joint_to_limit_key": T({"pelvis_yaw": "pelvis_yaw", "waist_yaw_joint": "waist_yaw", "waist_roll_joint": "waist_roll_pitch", "waist_pitch_joint": "waist_roll_pitch",
                           "shoulder_pitch_joint": "shoulder_axis", "shoulder_roll_joint": "shoulder_axis", "shoulder_yaw_joint": "shoulder_axis", "elbow_joint": "elbow",
                           "wrist_roll_joint": "wrist_roll", "wrist_pitch_joint": "wrist_pitch_yaw", "wrist_yaw_joint": "wrist_pitch_yaw"}, "env/g1_golf_env.py", "published", "matched by suffix after left_/right_"),
  "torque_overshoot_fail_ratio": T(1.01, "env derates torque linearly to 0 at rated speed; exceeding the peak is a simulation/clipping bug", "assumption"),
  "derate_overshoot_warn_ratio": T(1.05, "tau_avail = tau_max * (1 - |w|/w_rated)", "assumption"),
  "feasibility_ratio_avg_by_tier_chs": T(feas, "kseq-reference feasibility_g1_env (required avg power from Nesbit work scaled to CHS / 0.23 s over max available tau*w/4); groups hips, spine, spine_all_axes, shoulders, elbows, wrists, wrists_pitch_only", "derived", "120/132 rows extrapolated; > 1 means infeasible on average, peak need ~2.5x average"),
  "feasibility_warn_fail_ratio": T([1.0, 2.0], "kseq: ratio_avg > 1 infeasible; est. peak 2.5x", "assumption"),
  "human_wrist_torque_cap_Nm": T(60, "Sprigings & Neal 2000 simulation limit (search summary only, unverified)", "published", "S-tag in kseq doc; warn only"),
 },
 "power_budget": {
  "pelvis_yaw_avg_torque_Nm_downswing": T({"pass": [100, 350], "warn": [50, 500]}, "derived in kseq doc section 5: 150-300 N*m average at 100-116 mph (Barrentine/Hume shear couple + Nesbit hip work 423 J)", "derived", "neither is a measured peak"),
  "downswing_window_s": T(0.23, "Nesbit/Hume elite downswing, held constant", "assumption"),
  "grip_torque_Nm_by_chs": T([[r["chs_mph"], r["grip_torque_Nm"]] for r in scal], "Nesbit 2005 linear fit through 4 swings, extrapolated >116 mph", "derived"),
  "grip_torque_pass_ratio": T([0.6, 1.6], "n=84 Nesbit 22-40 N*m about the fit; wide for definition differences", "assumption"),
 },
 "grf": {
  "lead_vertical_bw": T({"pass": [0.8, 1.7], "warn": [0.5, 2.4], "fail_outside": [-0.02, 3.0]}, "Worsfold 2007 front 0.84; Han 2019 1.12+-0.22 (S); Hirano 2023 1.51; Hume review 1.6-2.0 (per foot or summed unclear); studies differ ~2x", "derived", "no GRF target is defensible; this only catches non-physical traces (pulling down on the ground, > 3 BW)"),
 },
 "shot": {
  "smash_driver": T({"fail_above": L["limits"]["smash"]["driver"]["hard_ceiling"], "warn_above": L["limits"]["smash"]["driver"]["expected_centre_strike_max"], "warn_below": 1.30}, "launch_targets_120_132_limits.json gate_recommendation (TrackMan smash blog, R&A WLD, PGA Tour pdf)", "published",
              "1.50 is a COR/mass ceiling; Burke 141 mph ~1.50 single shot"),
  "spin_rpm_driver": T({"pass": [1800, 3000], "warn": [1200, 4000], "fail_outside": [1200, 4000], "note": "warn bands 1200-1800 and 3000-4000 per gate_recommendation (1500-1800/3000-3500 explicitly; the gap is warn)"}, "launch_targets_120_132_limits.json gate_recommendation", "derived",
              "driver at 120-132 mph; tour average 2545-2686, WLD 2789"),
  "launch_deg_driver": T({"pass": [7.0, 16.0], "warn": [4.0, 20.0], "fail_outside": [2.0, 25.0]}, "TrackMan optimizer 7.8-9.3 at AoA 0 (120-132 mph), Foresight window 10-14, WLD 11.2, tour 10.4-11.2", "derived"),
  "descent_deg_driver": T({"pass": [30, 48], "warn": [25, 55], "fail_outside": [18, 60]}, "tour 36-39 (snippet, roll_aoa_validation descent anchors); golfphys gives 33-50 over normal launch/spin", "derived"),
  "total_over_carry": T({"pass": [1.04, 1.25], "warn": [0.99, 1.35], "fail_outside": [0.99, 1.45]}, "roll_aoa_validation (normal turf 1.07-1.13, firm ~1.2); TrackMan total optimizer 1.17-1.22", "derived", "total < carry is impossible; 1% slack for averaged gate rows (env has no roll: ratio ~1.00 warns)"),
  "golfphys_carry_residual_yd": T({"pass": 15, "warn": 35}, "golfphys vs TrackMan chart within ~3 yd (consistency only); vs Foresight 14-33 yd lower at 120-145 mph (unresolved vendor disagreement)", "model", "residual = reported carry - golfphys carry from reported ball speed/launch/spin"),
  "spin_axis_abs_deg": T({"warn": 10, "fail": 30}, "stock scatter spec; MyGolfSpy centre-bin axis tilt -3..-6 deg", "assumption", "only when the shot dict carries spin_axis_deg"),
  "club_speed_range_mph": T([60, 150], "R&A WLD 145 mph, record ball speed 241.6 mph (Berkshire) -> club speed ~165 mph; sim below 60 mph is not a driver swing", "assumption", "warn outside"),
 },
}
json.dump(out, open(ROOT / "data/references/realism_thresholds.json", "w"), indent=1)
print("wrote", len(json.dumps(out)), "bytes")
