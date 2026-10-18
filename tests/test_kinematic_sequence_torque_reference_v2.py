import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data import kinematic_sequence_torque_reference as K

PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "references", "kinematic_sequence_torque_reference_v2.json")
D = json.load(open(PATH))
READ_TAGS = {"fetched-full", "abstract", "snippet"}
ALL_TAGS = READ_TAGS | {"n/a", "carried-v1"}
MPH = 2.23694


def _dp(i):
    return [d for d in D["datapoints"] if d["id"] == i][0]


def test_meta_and_private_data():
    assert D["_meta"]["contains_instagram_or_mason_derived_data"] is False
    txt = json.dumps(D).lower().replace("contains_instagram_or_mason_derived_data", "")
    for bad in ("instagram", "mason", "imit_private", "p1_s"):
        assert bad not in txt
    assert D["_meta"]["version"] == 2


def test_every_datapoint_has_source_tag_and_category():
    ids = set()
    for d in D["datapoints"]:
        assert d["id"] not in ids
        ids.add(d["id"])
        assert d["cat"] in set("abcde")
        assert d["tag"] in ALL_TAGS
        assert d["source"] in D["sources"] or d["tag"] == "derived"
        if d["tag"] in READ_TAGS:
            s = D["sources"][d["source"]]
            assert s["url"].startswith("http") and s["tag"] == d["tag"] or d["tag"] == "snippet" and d["source"].endswith("numbers") or d["tag"] == "snippet"
        if d["tag"] in READ_TAGS:
            assert d["level"] in {"measured", "secondary", "model", "derived"}
        if d.get("conflict"):
            assert d["conflict"] in D["conflicts"]
    for s in D["sources"].values():
        assert s["url"].startswith("http") and s["tag"] in READ_TAGS


def test_tag_counts_match_meta():
    counts = {}
    for d in D["datapoints"]:
        counts[d["tag"]] = counts.get(d["tag"], 0) + 1
    assert counts == D["_meta"]["datapoint_counts_by_tag"]
    assert sum(counts.values()) == D["_meta"]["datapoint_count_total"]
    assert counts["fetched-full"] > counts["snippet"] > 0


def test_snippet_and_abstract_never_used_as_measured_without_flag():
    for d in D["datapoints"]:
        if d["tag"] == "snippet":
            assert "summary" in d["note"].lower() or "snippet" in d["note"].lower() or "explainer" in d["note"].lower() or "from drkwongolf" in d["note"].lower() or d["source"].endswith("numbers") or d["source"] in D["sources"]
    assert _dp("b_horan_peak_speeds")["tag"] == "snippet"
    assert _dp("c_han_corr")["tag"] == "abstract"


def test_key_published_values():
    assert _dp("b_madrid_peak_club")["value"] == 2364 and _dp("b_madrid_peak_club")["n"] == 66
    assert abs(_dp("b_madrid_peak_club")["chs_mph"] - 110.4) < 0.01
    assert _dp("a_okamoto_grip_torque")["value"] == 40.9
    assert _dp("c_meister_free_moment")["value"]["hard"] == 1.19
    assert _dp("e_madrid_downswing")["value"] == 253
    assert _dp("b_ichikawa_pelvis")["n"] == 1 and _dp("b_ichikawa_pelvis")["chs_mph"] > 137
    assert D["sources"]["sprigings2000"]["tag"] == "fetched-full"
    assert D["datapoints"][[d["id"] for d in D["datapoints"]].index("a_sprigings_limits")]["value"]["Tmax_Nm"] == {"spine": 180, "shoulder": 120, "wrist": 60}


def test_hip_torque_conversion():
    bwht = 83.0 * 9.81 * 1.80
    d = _dp("a_foxworth_hip_trail_extensor")
    assert abs(d["n_m_assumed_83kg_180m"] - 10.64 * bwht / 100) < 0.2
    assert "ASSUMED" in d["note"]


def test_slopes_and_downswing_derivations():
    s = D["derived"]["madrid_within_group_slopes_deg_s_per_m_s"]
    assert abs(s["values"]["club"] - 0.906 * 115 / 2.1) < 0.02
    assert abs(s["downswing_time_ms_per_m_s"] - (-0.481 * 26 / 2.1)) < 0.02
    rows = {r["chs_mph"]: r for r in D["derived"]["downswing_duration_by_chs"]["rows"]}
    assert abs(rows[110.4]["within_group_madrid_ms"] - 253) < 1
    assert rows[120.0]["within_group_madrid_ms"] < rows[110.4]["within_group_madrid_ms"]
    assert rows[132.0]["within_group_madrid_ms"] < rows[120.0]["within_group_madrid_ms"]
    assert 220 < rows[120.0]["between_group_bourgain_ms"] < 250


def test_delta_vs_v1_matches_v1_module():
    for r in D["derived"]["segment_peak_by_chs"]["rows"]:
        for key, seg in (("pelvis_hip_line", "pelvis"), ("thorax_shoulder_line", "thorax"), ("arm_upper_lever", "lead_arm"), ("club", "club")):
            v = r["segments"][key]
            assert abs(v["v1_two_group_fit"] - K.segment_peak_deg_s(seg, r["chs_mph"])) <= 1.0
            assert abs(v["v1_minus_madrid"] - (v["v1_two_group_fit"] - v["madrid_anchor_plus_within_group_slope"])) <= 1.01
    r120 = [r for r in D["derived"]["segment_peak_by_chs"]["rows"] if r["chs_mph"] == 120.0][0]["segments"]
    assert r120["pelvis_hip_line"]["madrid_anchor_plus_within_group_slope"] < r120["pelvis_hip_line"]["v1_two_group_fit"]


def test_free_moment_and_grip_torque_fits():
    xs, ys = [27.4, 31.6, 35.4], [0.83, 1.00, 1.19]
    k = sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)
    assert abs(D["derived"]["free_moment_by_chs"]["fit"]["proportional_k_Nm_per_kg_per_m_s"] - k) < 1e-3
    g = {r["chs_mph"]: r for r in D["derived"]["grip_torque_by_chs"]["rows"]}
    assert abs(g[100.0]["v1_linear_fit_Nm"] - K.grip_torque_Nm(100.0)) < 0.2
    assert abs(g[120.0]["okamoto_anchor_plus_nesbit_slope_Nm"] - (40.9 + K.GRIP_TORQUE_SLOPE * (120 / MPH - 45.8))) < 0.2
    assert g[120.0]["okamoto_anchor_plus_nesbit_slope_Nm"] > g[120.0]["v1_linear_fit_Nm"]
    ratio = D["derived"]["peak_over_average_power"]["ratio"]
    assert 3.5 < ratio < 3.9


def test_conflicts_and_gaps_listed():
    for c in ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10"):
        assert c in D["conflicts"]
    gaps = " ".join(D["remaining_gaps"]).lower()
    assert "lumbar" in gaps and "112 mph" in gaps and "han 2019" in gaps
    assert any(d["tag"] == "n/a" for d in D["datapoints"])
