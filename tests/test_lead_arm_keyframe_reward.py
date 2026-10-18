import json
from pathlib import Path
R = Path(__file__).resolve().parent.parent / "data/references"
d = json.load(open(R / "lead_arm_keyframe_reward.json"))
K = json.load(open(R / "mason_keyframe_targets.json"))

def test_flags_and_aggregate_only():
    assert d["instagram_derived"] is True and "UNVERIFIED" in d["status"]
    s = json.dumps(d)
    assert not any(c in s for c in K["clips_used"]), "per-clip ids must not appear"
    assert d["n_clips"] == len(K["clips_used"])

def test_env_names_and_roles():
    assert set(d["joints"]) == {"left_shoulder_pitch", "left_shoulder_roll", "left_elbow", "lead_wrist_derived"}
    assert not any(j.startswith("right_") for j in d["joints"]), "env right_* is TRAIL"
    assert d["joints"]["lead_wrist_derived"]["env_joint"] is None and d["joints"]["lead_wrist_derived"]["weight"] == 0.0
    assert d["joints"]["left_shoulder_pitch"]["weight"] > d["joints"]["left_elbow"]["weight"] > 0

def test_values_match_source_medians():
    for ph in ("address", "top", "impact", "finish"):
        for env_j, col in (("left_shoulder_pitch", "right_shoulder_pitch"), ("left_elbow", "right_elbow")):
            assert d["phases"][ph][env_j]["median_deg"] == K["keyframes"][ph]["joints"][col]["median_deg"]
            e = d["phases"][ph][env_j]; assert e["q25_deg"] <= e["median_deg"] <= e["q75_deg"] and e["sigma_suggested_deg"] >= 8.0

def test_events_ordered_and_lead_note():
    t = d["events"]["median_times_s"]
    assert t["takeaway_s"] < t["top_s"] < t["impact_s"] < t["finish_s"]
    assert "0.06" in d["reward"]["wrist_command_lead"] and "WRIST_PD_LAG" in d["reward"]["wrist_command_lead"]
