"""Build data/references/lead_arm_keyframe_reward.json from AGGREGATE data already tracked on main only:
mason_keyframe_targets.json (medians/IQR/sigma; reference cols 0-3 = Mason's anatomical right arm = LEAD arm for a lefty)
and wrist_sign_mapping.json (only the mapping constants). No per-clip Mason values are copied.
Run: python -m data.lead_arm_keyframe_reward"""
import json, statistics
from pathlib import Path
R = Path(__file__).resolve().parent / "references"
# reference column name (anatomical, file naming) -> env joint (golfer role: left_* = LEAD)
MAP = {
 "right_shoulder_pitch": dict(env_joint="left_shoulder_pitch", env_status="ACTUATED in v3/v4_power (motor gear 40, forcerange 3.75; v3)",
        weight=0.6, role="primary"),
 "right_shoulder_roll": dict(env_joint="left_shoulder_roll", env_status="PASSIVE hinge (no motor; damping 0.5); readable from qpos, reward-only",
        weight=0.0, role="excluded (low confidence video proxy; roll sign flips for left-handed env per docs/HANDEDNESS.md)"),
 "right_elbow": dict(env_joint="left_elbow", env_status="PASSIVE hinge (no motor; range -10..150 deg); readable from qpos, reward-only. Only follows if grip=True couples left_hand to right_wrist (default grip=False)",
        weight=0.2, role="secondary, reward-only; set 0 unless grip=True"),
 "right_wrist": dict(env_joint=None, env_status="NO lead-wrist joint exists (left_hand is a 0.03 m sphere); reward-only DERIVED quantity (hand-deviation proxy), not computable from qpos without a defined construction",
        weight=0.0, role="excluded; do NOT confuse with env right_wrist (trail) -- see docs/WRIST_SIGN_MAPPING.md"),
}
def main():
    K = json.load(open(R / "mason_keyframe_targets.json")); W = json.load(open(R / "wrist_sign_mapping.json"))
    used = [c for c in K["clips_used"]]
    off = K["event_offsets_s"]
    med = lambda f: round(statistics.median(f(off[c]) for c in used), 3)
    ev = {"takeaway_s": med(lambda o: o["takeaway"]), "top_s": med(lambda o: o["top"]), "impact_s": med(lambda o: o["impact"]), "finish_s": med(lambda o: o["finish"])}
    dur = {"backswing_s": round(ev["top_s"] - ev["takeaway_s"], 3), "downswing_s": round(ev["impact_s"] - ev["top_s"], 3), "follow_s": round(ev["finish_s"] - ev["impact_s"], 3)}
    phases = {}
    for ph in ("address", "top", "impact", "finish"):
        phases[ph] = {}
        for col, m in MAP.items():
            j = K["keyframes"][ph]["joints"][col]
            phases[ph][m["env_joint"] or "lead_wrist_derived"] = {k: j[k] for k in ("n", "median_deg", "q25_deg", "q75_deg", "sigma_suggested_deg", "confidence")}
            phases[ph][m["env_joint"] or "lead_wrist_derived"]["median_rad"] = round(j["median_deg"] * 3.141592653589793 / 180, 3)
    joints = {}
    for col, m in MAP.items():
        joints[m["env_joint"] or "lead_wrist_derived"] = dict(reference_column=col, **m)
    out = {
     "version": "lead_arm_keyframe_reward_v1",
     "instagram_derived": True,
     "status": "UNVERIFIED video proxies (2-D MediaPipe, ~30 fps feed screen recordings). Aggregates only (median/IQR over the clips_used of mason_keyframe_targets.json). Derived from Mason's Instagram swing references (aggregates only); Mason approved use of his own data (see docs/INSTAGRAM_DERIVED_MANIFEST.md).",
     "source_files": ["data/references/mason_keyframe_targets.json", "data/references/wrist_sign_mapping.json"],
     "n_clips": len(used), "handedness": "left (native); lead arm = env left_* joints; env right_* = TRAIL (docs/HANDEDNESS.md)",
     "role_mapping": "Mason reference cols 0-3 (file names right_*) = anatomical right = LEAD arm for a left-hander -> env left_* ; ref col 4 (left_shoulder_pitch) = anatomical left = TRAIL shoulder -> env right_shoulder_pitch. Not interchangeable with the trail-arm targets in wrist_elbow_event_targets.json.",
     "units": "degrees in the reference convention (shoulder pitch: 0 = arm hanging, negative = raised; elbow/wrist: unsigned flexion/deviation); *_rad = deg converted, same convention",
     "sign_conventions": {
        "env_wrist": "positive env right_wrist = cocked (docs/WRIST_SIGN_MAPPING.md); that is the TRAIL wrist. Lead wrist has no env joint. Stored lead 'wrist' values are unsigned hand-deviation magnitudes (0 = straight line); the +1*ref - 1.31 rad offset in wrist_sign_mapping.json (tolerance 0.15 rad) was fitted to the TRAIL wrist's contact geometry and must NOT be applied to the lead wrist.",
        "mapping_constants_copied": W["mapping"]["mason_v2_col3_unsigned"],
        "shoulder_pitch": "reference: negative = raised. Env sign of left_shoulder_pitch NOT verified here (env/ read-only, nothing run); use the sign/offset-invariant normalised form y=(q-q_addr)/(q_top-q_addr) as env._load_keyframes already does, or confirm the sign with a one-step FK check before using absolute degrees.",
        "elbow": "reference unsigned flexion; env left_elbow range -10..150 deg, assumed flexion-positive (UNVERIFIED)"},
     "joints": joints,
     "events": {
        "definition": "median offset-corrected joint-axis event times of clips_used from event_offsets_s (joint-axis time, i.e. video-time event minus the ~0.4 s joint_axis_offset_s; do not reuse the uncorrected t_top)",
        "median_times_s": ev, "median_durations_s": dur,
        "tempo_ratio_median": K["tempo"]["tempo_ratio"]["median"], "tempo_ratio_band": K["tempo"]["tempo_ratio_recommended_band"],
        "caveat": "Absolute seconds come from edited/possibly sped-up ~30 fps clips (0.48 s backswing is implausible); use PHASE (event-relative) indexing and the tempo-ratio band, not these seconds, as the timing target. NOT a speed target.",
        "impact_note": f"landmark impact is EARLY vs hand low point by {K['impact_lowpoint_lag_s']} s (+-0.05); detect sim impact as club-low-point minus {K['impact_lowpoint_lag_s']} s",
        "finish_note": "finish = arm-speed settle heuristic; weak anchor",
        "time_indexing": "event/phase in SIMULATED time; reference dt 0.01 s vs env control dt 0.02 s (docs/REFSET_TIMING_AUDIT.md)"},
     "phases": phases,
     "reward": {
        "events_rewarded": ["top", "impact", "finish"], "address": "initial-state prior only, not rewarded",
        "form": "r_lead = (1/K) * sum_{k in {top,impact,finish}} exp( - sum_j w_j * ((q_j(t_k) - mu_jk) / (s * sigma_jk))^2 / sum_j w_j ), weights from joints[*].weight; per-event gaussian in a window of +-0.06 s taking the best-matching sample (timing tolerance ~ +-1 frame at 30 fps)",
        "normalised_variant": "for sign/offset robustness use y=(q-q_addr)/(q_top-q_addr) with sigma=sigma_deg/|top-addr| (same as env._load_keyframes)",
        "sigma": "per-joint sigma_suggested_deg (max of MAD-sigma and the 8 deg floor); s curriculum 2.0 -> 1.0; s<1 not supported by the data",
        "weights": {"left_shoulder_pitch": 0.6, "left_elbow": 0.2, "others": 0.0, "note": "lead-arm share of total tracking reward: suggest <= 0.3 of r_track since only 1 joint is actuated and the rest are proxies; weights are a judgment, not fitted"},
        "timing_tolerance_s": 0.06,
        "wrist_command_lead": "docs/WRIST_PD_LAG.md recommends leading the TRAIL wrist command by ~0.06 s (probe: lag ~0.12 rad at impact -> +0.003 at lead 0.06; sim only, v3 fs2). It was measured for right_wrist only. The lead shoulder pitch PD lag was NOT measured; consider the same lead as a hypothesis (UNVERIFIED) and measure with data/wrist_pd_lag_probe.py-style step test before adopting. Score angles at the applied-target time, not the post-step command (20 ms offset)."},
     "caveats": ["Aggregates over 7-8 clips, mostly down-the-line; view-dependent 2-D proxies.", "impact keyframe has n=7 (one clip had no valid rows).",
        "Lead elbow/roll are passive in the env, so the policy cannot directly control them; reward on them is only achievable via the grip coupling or body motion.",
        "Instagram-derived: third-party content in source recordings never reviewed."]}
    (R / "lead_arm_keyframe_reward.json").write_text(json.dumps(out, indent=1))
    return out
if __name__ == "__main__":
    main(); print("wrote", R / "lead_arm_keyframe_reward.json")
