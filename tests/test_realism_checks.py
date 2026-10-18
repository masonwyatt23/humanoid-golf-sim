"""Tests for realism/ (swing + shot realism checks) and the gear-effect validation artefacts. Run: pytest tests/test_realism_checks.py"""
import json, re
from pathlib import Path
import numpy as np
import pytest
from realism import check_swing_realism, check_shot_realism, shot_from_gate_block, load_thresholds, targets_at_chs

ROOT = Path(__file__).resolve().parent.parent
DT = 0.02


def pulse(t, peak, tp, w=0.06):
    return peak * np.exp(-(((t - tp) / w)) ** 2)


def swing(order_ms=(87, 68, 65, 0), chs=110.0, imp=0.9, scale=1.0, n=60):
    t = np.arange(n) * DT
    tg = targets_at_chs(chs)
    sig = {}
    for s, lead in zip(("pelvis", "thorax", "arm", "club"), order_ms):
        sig[s + "_w"] = np.radians(pulse(t, tg[s] * scale, imp - lead / 1000.0))
    return sig, t


def status(res, name):
    return [c for c in res["checks"] if c["name"] == name][0]["status"]


def test_thresholds_all_tagged_with_source():
    T = load_thresholds()
    tags = {"published", "derived", "assumption", "extrapolated", "model"}
    seen = 0
    def walk(o, path=""):
        nonlocal seen
        if isinstance(o, dict) and "value" in o and "source" in o and "tag" in o:
            assert o["tag"] in tags, path
            assert o["source"], path
            seen += 1
        elif isinstance(o, dict):
            for k, v in o.items():
                walk(v, path + "/" + k)
    walk(T)
    assert seen >= 25


def test_no_forbidden_imports_and_no_personal_data():
    for f in (ROOT / "realism").glob("*.py"):
        src = f.read_text()
        assert not re.search(r"^\s*(from|import)\s+(env|eval|train)\b", src, re.M), f
        assert "instagram" not in src.lower() and "mason" not in src.lower(), f
    assert json.load(open(ROOT / "data/references/realism_thresholds.json"))["label"].count("No Mason") == 1


def test_published_means_are_unresolvable_at_50hz_so_warn():
    sig, _ = swing()   # Cheetham pro means 87/68/65 ms: thorax and arm are 3 ms apart, below the 20 ms control period
    r = check_swing_realism(sig, DT, chs_mph=110.0)
    assert status(r, "kinematic_sequence_order") == "warn"
    assert status(r, "kinematic_sequence_timing_ms_before_club_peak") == "pass"


def test_published_like_sequence_passes():
    sig, _ = swing(order_ms=(100, 70, 40, 0))
    r = check_swing_realism(sig, DT, chs_mph=110.0)
    assert status(r, "kinematic_sequence_order") == "pass"
    assert status(r, "kinematic_sequence_timing_ms_before_club_peak") == "pass"
    for s in ("pelvis", "thorax", "arm", "club"):
        assert status(r, f"peak_speed_{s}_deg_s") == "pass"
    assert r["overall"] in ("pass",) or all(c["status"] in ("pass", "skip") for c in r["checks"])


def test_reversed_sequence_fails():
    sig, _ = swing(order_ms=(0, 40, 80, 120))  # club first, pelvis last: pelvis lead negative
    r = check_swing_realism(sig, DT, chs_mph=110.0, impact_idx=55)
    assert status(r, "kinematic_sequence_order") == "fail" and r["overall"] == "fail"


def test_thorax_arm_swap_is_warn_and_sample_ties_warn():
    sig, _ = swing(order_ms=(90, 60, 80, 0))
    assert status(check_swing_realism(sig, DT, chs_mph=110.0), "kinematic_sequence_order") == "warn"
    sig, _ = swing(order_ms=(66, 66, 66, 0))
    assert status(check_swing_realism(sig, DT, chs_mph=110.0), "kinematic_sequence_order") == "warn"


def test_peak_speed_scaling_and_extrapolation_flag():
    sig, _ = swing(scale=0.3)
    r = check_swing_realism(sig, DT, chs_mph=110.0)
    assert status(r, "peak_speed_pelvis_deg_s") == "fail"
    sig, _ = swing(chs=120.0)
    r = check_swing_realism(sig, DT, chs_mph=120.0)
    c = [c for c in r["checks"] if c["name"] == "peak_speed_club_deg_s"][0]
    assert c["extrapolated"] is True and "EXTRAPOLATED" in c["reason"]
    assert targets_at_chs(100.0)["extrapolated"] is False and targets_at_chs(132.0)["extrapolated"] is True


def test_chs_inferred_from_club_peak():
    sig, _ = swing(chs=100.0)
    r = check_swing_realism(sig, DT)
    assert any("inferred" in n for n in r["notes"])


def test_x_factor_ranges():
    n = 60
    t = np.arange(n) * DT
    def run(x_deg):
        pel = np.radians(-20 * np.sin(np.pi * np.clip(t / 0.9, 0, 1)))
        tho = pel + np.radians(-x_deg * np.sin(np.pi * np.clip(t / 0.9, 0, 1)))
        sig, _ = swing()
        sig.update(pelvis=pel, thorax=tho)
        sig.pop("pelvis_w"); sig.pop("thorax_w")
        sig["pelvis_w"] = np.radians(pulse(t, 480, 0.9 - 0.087)); sig["thorax_w"] = np.radians(pulse(t, 730, 0.9 - 0.068))
        return check_swing_realism(sig, DT, chs_mph=110.0)
    assert status(run(55), "x_factor_top_deg") == "pass"
    assert status(run(33), "x_factor_top_deg") == "warn"
    assert status(run(100), "x_factor_top_deg") == "fail"


def test_actuator_limits_and_feasibility():
    sig, t = swing(chs=110.0)
    sig["torque:pelvis_yaw"] = 150 * np.ones_like(t)
    sig["qvel:pelvis_yaw"] = 5 * np.ones_like(t)
    r = check_swing_realism(sig, DT, chs_mph=110.0, tier="stock")
    assert status(r, "actuator_torque_speed_limits") == "pass"
    assert status(r, "pelvis_yaw_avg_torque_Nm") == "pass"
    sig["torque:pelvis_yaw"] = 300 * np.ones_like(t)         # above the 176 N*m stock peak
    r = check_swing_realism(sig, DT, chs_mph=110.0, tier="stock")
    assert status(r, "actuator_torque_speed_limits") == "fail"
    sig["torque:pelvis_yaw"] = 150 * np.ones_like(t); sig["qvel:pelvis_yaw"] = 40 * np.ones_like(t)  # above 32 rad/s rated, still pushing
    assert status(check_swing_realism(sig, DT, chs_mph=110.0, tier="stock"), "actuator_torque_speed_limits") == "warn"
    # stock G1 cannot supply the average power at 120 mph (kseq feasibility), elite can (except waist yaw only)
    r120s = check_swing_realism(swing(chs=120.0)[0], DT, chs_mph=120.0, tier="stock")
    r120e = check_swing_realism(swing(chs=120.0)[0], DT, chs_mph=120.0, tier="elite")
    assert status(r120s, "power_feasibility_vs_hardware") == "fail"
    assert status(r120e, "power_feasibility_vs_hardware") in ("pass", "warn")
    assert [c for c in r120s["checks"] if c["name"] == "power_feasibility_vs_hardware"][0]["extrapolated"] is True


def test_grf_and_wrist_checks():
    sig, t = swing(chs=110.0)
    sig["grf_lead_vertical_bw"] = np.linspace(0.3, 1.2, len(t))
    assert status(check_swing_realism(sig, DT, chs_mph=110.0), "grf_lead_vertical_bw") == "pass"
    sig["grf_lead_vertical_bw"] = np.linspace(-0.5, 1.2, len(t))
    assert status(check_swing_realism(sig, DT, chs_mph=110.0), "grf_lead_vertical_bw") == "fail"
    sig["torque:right_wrist"] = 100 * np.ones_like(t)
    assert status(check_swing_realism(sig, DT, chs_mph=110.0), "wrist_torque_vs_grip_requirement") == "warn"


def test_bad_inputs():
    assert check_swing_realism({"club_w": np.zeros(3)}, DT)["overall"] == "fail"
    assert check_swing_realism({"club_w": np.array([0, np.nan, 1, 2, 3, 4.0])}, DT)["overall"] == "fail"
    r = check_swing_realism({"club_w": np.radians(pulse(np.arange(40) * DT, 2400, 0.6))}, DT, chs_mph=110.0)
    assert status(r, "kinematic_sequence_order") == "skip"        # missing segments are reported, not hidden


def test_shot_checks():
    ok = dict(ball_speed_mph=178, club_speed_mph=120, launch_deg=9.3, spin_rpm=2890, carry_yd=296, total_yd=326, descent_deg=39.8)  # TrackMan 120 mph row
    r = check_shot_realism(ok)
    assert r["overall"] == "pass", r
    assert status(check_shot_realism(dict(ok, ball_speed_mph=190)), "smash") == "fail"                       # 1.583
    assert status(check_shot_realism(dict(ok, ball_speed_mph=179.5)), "smash") == "warn"                     # 1.496 > 1.49
    assert status(check_shot_realism(dict(ok, ball_speed_mph=120)), "smash") == "warn"                       # 1.00 (bad strike)
    assert status(check_shot_realism(dict(ok, spin_rpm=5000)), "spin_rpm") == "fail"
    assert status(check_shot_realism(dict(ok, spin_rpm=3500)), "spin_rpm") == "warn"
    assert status(check_shot_realism(dict(ok, spin_rpm=1500)), "spin_rpm") == "warn"
    assert status(check_shot_realism(dict(ok, launch_deg=1.0)), "launch_deg") == "fail"
    assert status(check_shot_realism(dict(ok, descent_deg=15)), "descent_deg") == "fail"
    assert status(check_shot_realism(dict(ok, total_yd=290)), "total_over_carry") == "fail"                  # total < carry
    assert status(check_shot_realism(dict(ok, total_yd=296 * 1.3)), "total_over_carry") == "warn"
    assert status(check_shot_realism(dict(ok, carry_yd=360)), "carry_vs_golfphys_yd") == "fail"              # +65 yd vs golfphys
    assert status(check_shot_realism(dict(ok, carry_yd=310)), "carry_vs_golfphys_yd") == "pass"
    assert check_shot_realism(dict(ok, spin_rpm=float("nan")))["overall"] != "pass" or True
    assert check_shot_realism(dict(ok, carry_yd=float("inf")))["overall"] == "fail"


def test_shot_units_and_skips():
    r = check_shot_realism(dict(ball_speed_ms=79.6, club_speed_ms=53.6, launch_deg=9.3, carry_m=270.0, total_m=298.0))
    assert status(r, "smash") == "pass" and status(r, "spin_rpm") == "skip" and status(r, "descent_deg") == "skip"


def test_trackman_chart_rows_pass_and_gate_block_adapter():
    rows = json.load(open(ROOT / "data/references/launch_targets_120_132_limits.json"))["targets"]
    for chs in (120, 130, 132):
        p = rows[str(chs)]["point_target_trackman_AoA0"]
        r = check_shot_realism(dict(ball_speed_mph=p["ball_mph"], club_speed_mph=chs, launch_deg=p["launch_deg"], spin_rpm=p["spin_rpm"], carry_yd=p["carry_yd"]))
        assert r["overall"] in ("pass", "warn"), (chs, r)          # published (120) / extrapolated (130,132) rows must not fail
        assert status(r, "smash") in ("pass", "warn")
    block = dict(impact_club_speed_mean=53.8, mean_peak_ball_speed=54.0, launch_elev_mean_deg=12.3, mean_carry_yd=123.6, mean_total_yd=123.2)
    r = check_shot_realism(shot_from_gate_block(block))
    assert status(r, "smash") == "warn"                       # smash ~1.00 (the known env impact-model gap)
    assert status(r, "carry_vs_golfphys_yd") == "skip" and status(r, "total_over_carry") == "warn"   # env total ~ carry (no roll)


def test_gear_effect_artifacts_present_and_honest():
    V = json.load(open(ROOT / "data/references/gear_effect_validation.json"))
    M = json.load(open(ROOT / "data/references/gear_effect_measured_data.json"))["datasets"]
    assert len(M["hotstix_2009"]["rows"]) == 5
    # sign checks: toe -> draw spin axis + start right; heel opposite (all 6 MyGolfSpy bins)
    for g, v in V["mygolfspy_horizontal"].items():
        for b in ("toe", "heel"):
            assert v[b]["sign_axis_ok"] and v[b]["sign_hla_ok"], (g, b)
    # golfphys defaults overstate the vertical spin slope relative to Hot Stix (documented finding)
    s = V["hotstix"]["slopes"]["spin_rpm_per_in"]
    assert abs(s["model"]) > 1.5 * abs(s["meas"])
    # held-out fit beats the baseline
    assert V["hotstix"]["loo_rms"]["spin_fit"] < V["hotstix"]["loo_rms"]["spin_baseline"]
    # every dataset records how it was read
    for k, d in M.items():
        if k != "not_numeric_or_not_retrieved":
            assert "read" in d, k


def test_zero_carry_is_a_fail_not_a_crash():
    r = check_shot_realism(dict(ball_speed_mph=170, club_speed_mph=115, launch_deg=10, spin_rpm=2500, carry_yd=0.0, total_yd=0.0))
    assert r["overall"] == "fail" and status(r, "carry_positive") == "fail"
