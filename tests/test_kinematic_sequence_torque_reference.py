import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data import kinematic_sequence_torque_reference as K
from data import speed_gap_100_120 as sg

D = K.load()
TAGS = {"measured", "measured-secondary", "measured-qualitative", "interpolated", "extrapolated", "derived", "synthesis-only", "abstract"}


def test_meta_and_no_private_data():
    assert D["_meta"]["contains_instagram_or_mason_derived_data"] is False
    txt = json.dumps(D).lower().replace("contains_instagram_or_mason_derived_data", "")
    for bad in ("instagram", "mason", "imit_private", "p1_s"):
        assert bad not in txt
    assert D["populations"]["long_drive"]["status"].startswith("NO numeric")


def test_sources_and_tags():
    for r in D["kinematic_sequence"]["peak_angular_speed"]:
        assert r["source"] in D["sources"] and r["tag"] in TAGS and r["value"] > 0
    for sec in ("x_factor", "ground_reaction_forces"):
        for r in D[sec]:
            assert r["source"] in D["sources"] and r["tag"] in TAGS
    for s in D["sources"].values():
        assert s["url"].startswith("http") and s["tag"] in {"F", "X", "A", "S"}


def test_scaling_matches_module_and_speed_gap():
    assert K.check_json_consistency(D) == []
    r120 = [r for r in D["scaling_to_chs"]["rows"] if r["chs_mph"] == 120][0]
    assert abs(r120["segment_peak_deg_s"]["pelvis"] - sg.target_deg_s("pelvis", 120)) < 0.2
    assert r120["tag"] == "extrapolated" and K.tag_for_chs(105) == "measured-range"
    s = [K.segment_peak_deg_s(g, 120) for g in sg.ORDER]
    assert s == sorted(s)


def test_work_power_scaling_monotonic():
    assert abs(K.total_work_J(116.3) - 1452) < 15
    assert K.total_work_J(132) > K.total_work_J(120) > K.total_work_J(100)
    assert 2.0 < K.WORK_EXPONENT < 3.0
    assert abs(sum(K.NESBIT_WORK_J.values()) - K.NESBIT_TOTAL_J) < 2
    assert K.grip_torque_Nm(116.3) > 40


def test_feasibility_findings():
    stock = K.g1_feasibility(120, "stock")
    elite = K.g1_feasibility(120, "elite")
    assert stock["hips"]["ratio_avg"] > 1 and stock["spine"]["ratio_avg"] > 1 and stock["wrists_pitch_only"]["ratio_avg"] > 1
    assert stock["shoulders"]["ratio_avg"] < 1
    assert elite["hips"]["ratio_avg"] < 1 and elite["wrists"]["ratio_avg"] < 1
    assert K.max_power_W(88, 32) == 704.0
    assert K.torque_at_speed(5, 22, 24.5) == 0.0
