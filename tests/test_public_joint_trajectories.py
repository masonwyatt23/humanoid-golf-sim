import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)
PATH = os.path.join(ROOT, "data", "references", "public_joint_trajectories_110plus.json")
D = json.load(open(PATH))
CH = D["channels"]
REQUIRED = {"pelvis_rotation", "thorax_rotation", "x_factor", "lead_arm_to_trunk", "trail_arm_to_trunk",
            "lead_elbow_flexion", "trail_elbow_flexion", "lead_wrist_set_angle", "trail_wrist_angle"}


def test_meta_labels_and_no_private_data():
    m = D["_meta"]
    assert m["contains_instagram_or_mason_derived_data"] is False
    assert m["derived_from_cmu_multisense_amass_golfdb"] is False
    assert m["synthetic_interpolation"] is True
    txt = json.dumps(D).lower().replace("contains_instagram_or_mason_derived_data", "")
    txt = txt.replace("derived_from_cmu_multisense_amass_golfdb", "")
    for bad in ("instagram", "mason", "imit_private", "p1_s", "cmu", "multisense", "amass", "golfdb"):
        assert bad not in txt, bad
    assert "left_handed_mirror_rule" in m and "right_handed_convention" in m
    assert set(m["speed_classes_mph"]) == {110, 120, 130}
    assert m["extrapolated_beyond_published_speed_support"]["130"] is True


def test_grid_and_shapes():
    g = D["_meta"]["sampling_grid"]
    assert (g["t_start_s"], g["t_end_s"], g["dt_s"], g["n"]) == (-0.30, 0.10, 0.01, 41)
    assert set(CH) == REQUIRED
    for c, e in CH.items():
        for mph, cur in e["speed_class_curves"].items():
            t = np.array(cur["t_s"])
            assert t.shape == (41,)
            assert np.all(np.diff(t) > 0)  # strictly increasing time
            assert abs(t[0] + 0.30) < 1e-9 and abs(t[-1] - 0.10) < 1e-9
            for k in ("angle_deg", "angular_speed_deg_s", "published_support_mask"):
                assert len(cur[k]) == 41, (c, k)
            if cur.get("sd_angle_deg") is not None:
                assert len(cur["sd_angle_deg"]) == 41 and len(cur["band_total_deg"]) == 41
            pg = cur["phase_grid"]
            assert len(pg["phase"]) == 101 and pg["phase"][0] == 0 and pg["phase"][-1] == 1
            assert len(pg["angle_deg"]) == 101
            assert np.all(np.diff(pg["time_to_impact_s"]) > 0)
            assert abs(pg["time_to_impact_s"][-1]) < 1e-9
            assert np.all(np.isfinite(cur["angle_deg"]))


def test_each_channel_has_required_labels():
    for c, e in CH.items():
        assert e["synthetic_interpolation"] is True, c
        assert isinstance(e["interpolation"], str) and e["interpolation"]
        assert e["confidence"]
        assert e["lh_mirror"] in ("negate", "no sign change")
        assert len(e["source_keyframes"]) == 2
        for kf in e["source_keyframes"]:
            for k in ("value_deg", "sd_deg", "citation", "n", "speed_class_mph", "tag", "phase"):
                assert k in kf, (c, k)
            assert kf["citation"]
        if c != "x_factor":
            assert e["source_keyframes"][0]["value_deg"] is not None
            assert e["source_keyframes"][1]["value_deg"] is not None
    for c in ("pelvis_rotation", "thorax_rotation"):
        assert CH[c]["lh_mirror"] == "negate"
    assert CH["trail_elbow_flexion"]["lh_mirror"] == "no sign change"
    for s in D["sources"].values():
        assert isinstance(s, str) and len(s) > 20


def test_keyframes_reproduced_and_monotone_downswing():
    for c, e in CH.items():
        if c == "x_factor":
            continue
        a0 = e["source_keyframes"][0]["value_deg"]
        a1 = e["source_keyframes"][1]["value_deg"]
        for mph, cur in e["speed_class_curves"].items():
            T = cur["downswing_duration_s"]
            pg = cur["phase_grid"]
            ang = np.array(pg["angle_deg"])
            assert abs(ang[0] - a0) < 1e-2 and abs(ang[-1] - a1) < 1e-2, (c, mph)
            d = np.diff(ang) * np.sign(a1 - a0)
            assert np.all(d >= -1e-6), (c, mph)  # monotone top -> impact
            t = np.array(cur["t_s"])
            ang_t = np.array(cur["angle_deg"])
            i = int(np.argmin(np.abs(t)))
            assert abs(ang_t[i] - a1) < 1e-2
            # held at top before the downswing starts
            pre = t <= -T - 1e-9
            if pre.any():
                assert np.allclose(ang_t[pre], a0, atol=1e-2)
            mask = np.array(cur["published_support_mask"])
            assert np.all(mask == ((t >= -T - 1e-9) & (t <= 1e-9)))
            assert 0.19 < T < 0.27


def test_peak_speed_and_timing_follow_citations():
    for c in ("pelvis_rotation", "thorax_rotation"):
        for mph, cur in CH[c]["speed_class_curves"].items():
            assert not cur["flags"]
            w = np.abs(np.array(cur["angular_speed_deg_s"]))
            assert w.max() <= cur["peak_speed_used_deg_s"] * 1.02
            assert w.max() >= cur["peak_speed_used_deg_s"] * 0.93
            t = np.array(cur["t_s"])
            assert abs(t[int(w.argmax())] - cur["peak_time_ms_before_impact"] / 1000) <= 0.011
    p110 = CH["pelvis_rotation"]["speed_class_curves"]["110"]["peak_speed_used_deg_s"]
    assert abs(p110 - 391.6) < 3  # Madrid 394 at 110.4 mph, 110 mph class
    for c, e in CH.items():
        if c == "x_factor":
            continue
        for mph, cur in e["speed_class_curves"].items():
            assert abs(cur["integral_residual_before_normalisation_deg"]) < 0.5


def test_speed_scaling_directions():
    for c in ("pelvis_rotation", "thorax_rotation"):
        sc = CH[c]["speed_class_curves"]
        assert sc["110"]["peak_speed_used_deg_s"] < sc["120"]["peak_speed_used_deg_s"] < sc["130"]["peak_speed_used_deg_s"]
    T = D["_meta"]["downswing_duration_s"]
    assert T["110"] > T["120"] > T["130"]
    alt = D["_meta"]["downswing_duration_s_alt_within"]
    assert all(alt[k] < T[k] for k in ("120", "130"))


def test_xfactor_and_bands():
    xf = CH["x_factor"]["speed_class_curves"]["110"]
    assert abs(xf["angle_deg"][0] + 61.0) < 0.5  # Madrid X-factor at top (closed sign)
    p = np.array(CH["pelvis_rotation"]["speed_class_curves"]["110"]["angle_deg"])
    th = np.array(CH["thorax_rotation"]["speed_class_curves"]["110"]["angle_deg"])
    assert np.allclose(np.array(xf["angle_deg"]), th - p, atol=0.01)
    for c in ("pelvis_rotation", "thorax_rotation", "x_factor"):
        cur = CH[c]["speed_class_curves"]["110"]
        assert np.all(np.array(cur["band_total_deg"]) >= np.array(cur["sd_angle_deg"]) - 1e-6)
    for c in ("lead_arm_to_trunk", "lead_wrist_set_angle", "trail_wrist_angle"):
        assert CH[c]["speed_class_curves"]["110"]["sd_angle_deg"] is None  # no published SD retrieved
    r = D["_meta"]["recommended_soft_reward_usage"]
    assert "downswing" in r["window"] and "low" in r["total_weight"]
    w = r["per_channel_weights_and_tolerance_deg"]
    assert sum(v["w"] for v in w.values()) <= 1.0 + 1e-9


def test_generator_reproduces_json():
    from scripts import gen_public_joint_trajectories_110plus as G
    d = G.build()
    assert json.loads(json.dumps(d)) == D
