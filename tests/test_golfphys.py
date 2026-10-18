"""Tests for golfphys (standalone ball/club flight model). Run: pytest tests/test_golfphys.py"""
import json, math, re
from dataclasses import replace
from pathlib import Path
import numpy as np
import pytest
from golfphys import (load_params, Delivery, Strike, impact, simulate_shot, fly, air_density, bounce_roll, contact_to_ball,
                      env_contact_to_shot)
from golfphys.impact import impact_vec, delivery_vectors
from golfphys.sim import shot_from_launch
from golfphys.params import R_BALL, M_BALL

ROOT = Path(__file__).resolve().parent.parent
MPH = 0.44704
P = load_params()
VAL = json.load(open(ROOT / "data/references/golfphys_validation.json"))
COEF = json.load(open(ROOT / "data/references/golfphys_coefficients.json"))


def test_air_density():
    assert air_density(0, 15, 0) == pytest.approx(1.225, abs=0.003)
    assert air_density(1500) < air_density(0)
    assert air_density(0, 30) < air_density(0, 5)
    assert air_density(0, 25, 0.9) < air_density(0, 25, 0.0)


def test_vacuum_limit_matches_analytic_range():
    p = replace(P, cd_scale=0.0, cl_scale=0.0, cd_spin_slope=0.0, cd_plateau=0.0, cd_sub=0.0, cd_re_slope=0.0)
    v, L = 60.0, math.radians(30)
    r = fly((0, 0, R_BALL), (v * math.cos(L), 0, v * math.sin(L)), (0, 0, 0), p, dt=0.002)
    assert r.carry_m == pytest.approx(v * v * math.sin(2 * L) / 9.80665, rel=0.01)
    assert r.apex_m == pytest.approx((v * math.sin(L)) ** 2 / (2 * 9.80665), rel=0.01)


def test_dt_convergence():
    a = shot_from_launch(75, 11, 2600, P, roll=False, dt=0.02).carry_yd
    b = shot_from_launch(75, 11, 2600, P, roll=False, dt=0.002).carry_yd
    assert abs(a - b) < 0.1


def test_spin_adds_carry_then_hang_and_headwind_hurts():
    base = shot_from_launch(75, 11, 2500, P, roll=False)
    assert shot_from_launch(75, 11, 0, P, roll=False).carry_yd < base.carry_yd      # lift helps
    assert shot_from_launch(75, 11, 2500, P, roll=False, wind=(-5, 0, 0)).carry_yd < base.carry_yd
    assert shot_from_launch(75, 11, 2500, P, roll=False, alt_m=1500).carry_yd > base.carry_yd
    assert 5.5 < base.hang_s < 8.5 and 30 < base.descent_deg < 50


def test_sidespin_curves_left_for_positive_draw():
    r = shot_from_launch(75, 11, 2500, P, spin_axis_deg=10, roll=False)
    assert r.lateral_carry_m > 5
    assert shot_from_launch(75, 11, 2500, P, spin_axis_deg=-10, roll=False).lateral_carry_m < -5


def test_impact_centre_hit_limits():
    d = Delivery(50.0, 0.0, 0.0)           # zero loft: pure normal hit
    r = impact(d, p=P)
    ideal = (1 + P.e0) * P.m_head / (P.m_head + M_BALL)
    assert r["smash"] == pytest.approx(ideal, rel=1e-3)
    assert abs(r["backspin_rpm"]) < 1 and abs(r["launch_deg"]) < 1e-6


def test_spin_loft_drives_spin_and_launch_is_below_dynamic_loft():
    lo = impact(Delivery(50.0, 10.0, 0.0), p=P); hi = impact(Delivery(50.0, 16.0, 0.0), p=P)
    assert hi["backspin_rpm"] > lo["backspin_rpm"] and hi["launch_deg"] > lo["launch_deg"]
    assert lo["launch_deg"] < 10.0
    up = impact(Delivery(50.0, 12.0, 5.0), p=P); dn = impact(Delivery(50.0, 12.0, -5.0), p=P)
    assert up["backspin_rpm"] < dn["backspin_rpm"]                         # same dynamic loft, higher AoA = less spin loft


def test_face_to_path_and_start_line():
    r = impact(Delivery(50.0, 12.0, 0.0, face_deg=2.0, path_deg=-2.0), p=P)   # closed face relative to path
    assert r["sidespin_rpm"] > 300
    assert 0.5 < r["azimuth_deg"] / 2.0 + 0 < 1.6 or r["azimuth_deg"] > 0        # starts left of target, mostly along face
    frac = (r["azimuth_deg"] - (-2.0)) / 4.0
    assert 0.7 < frac < 0.95                                               # D-plane: ball starts ~80-90 % along face (Tutelman ~85)
    o = impact(Delivery(50.0, 12.0, 0.0, face_deg=-2.0, path_deg=2.0), p=P)
    assert o["sidespin_rpm"] == pytest.approx(-r["sidespin_rpm"], rel=0.02)


def test_gear_effect_signs_rh_and_lh():
    x = 0.0254
    rh = impact(Delivery(50.0, 12.0, 0.0), Strike(x_toe_m=x), P); assert rh["sidespin_rpm"] > 1000    # toe hit -> draw
    lh = impact(Delivery(50.0, 12.0, 0.0, handed="LH"), Strike(x_toe_m=x), P); assert lh["sidespin_rpm"] < -1000
    # gear term alone (flat face) = 16.4 * Vb(mph) * 1 in (Tutelman GE3)
    flat = impact(Delivery(50.0, 12.0, 0.0), Strike(x_toe_m=x), replace(P, bulge_radius=1e9, roll_radius=1e9))
    assert flat["sidespin_rpm"] == pytest.approx(16.4 * flat["ball_speed"] / MPH, rel=0.02)
    # with bulge the ball also starts toward the toe side (right for RH) and net draw is smaller than the pure gear term
    assert rh["azimuth_deg"] < -2 and rh["sidespin_rpm"] < flat["sidespin_rpm"]
    c = impact(Delivery(50.0, 12.0, 0.0), p=P)
    hi = impact(Delivery(50.0, 12.0, 0.0), Strike(y_high_m=x), P); lo = impact(Delivery(50.0, 12.0, 0.0), Strike(y_high_m=-x), P)
    assert hi["backspin_rpm"] < c["backspin_rpm"] < lo["backspin_rpm"]
    assert hi["launch_deg"] > c["launch_deg"]                                # roll radius raises launch on high hits


def test_off_centre_smash_loss_grows_quadratically():
    s = [impact(Delivery(50.0, 12.0, 0.0), Strike(x_toe_m=d), P)["smash"] for d in (0, 0.0127, 0.0254, 0.0381)]
    assert s[0] > s[1] > s[2] > s[3]
    l1, l2 = s[0] - s[2], s[0] - s[1]
    assert l1 > 2.5 * l2


def test_chart_agreement_within_stated_tolerance():
    # TrackMan 2010 chart row (115 mph, AoA 0, dynamic loft 9.8+... use stored validation rows): rms residuals of the calibrated impact
    f = VAL["impact_fit"]
    assert f["fit_residuals"]["d_smash"]["rmse"] < 0.006
    assert f["heldout_tm_total_opt"]["d_smash"]["rmse"] < 0.006
    assert f["heldout_tm_total_opt"]["d_launch"]["rmse"] < 0.5
    assert abs(f["heldout_tm_total_opt"]["rel_spin"]["bias"]) < 0.05
    e = VAL["impact_speed_extrapolation"]["heldout_110_120"]
    assert e["d_smash"]["rmse"] < 0.01


def test_live_impact_reproduces_stored_chart_rows():
    raw = json.load(open(ROOT / "data/references/roll_aoa_validation.json"))["datapoints"]
    row = next(x for x in raw if x["id"] == "tm_carry_115_+0")
    r = impact(Delivery(row["club_mph"] * MPH, row["dynamic_loft_deg"], row["aoa_deg"]), p=P)
    assert r["ball_speed"] / MPH == pytest.approx(row["ball_mph"], abs=1.5)
    assert r["launch_deg"] == pytest.approx(row["launch_deg"], abs=0.5)
    assert r["backspin_rpm"] == pytest.approx(row["spin_rpm"], rel=0.05)


def test_calibrated_carry_matches_tm_chart_row():
    raw = json.load(open(ROOT / "data/references/roll_aoa_validation.json"))["datapoints"]
    row = next(x for x in raw if x["id"] == "tm_total_115_+5")
    r = shot_from_launch(row["ball_mph"] * MPH, row["launch_deg"], row["spin_rpm"], P, roll=False)
    assert r.carry_yd == pytest.approx(row["carry_yd"], abs=8)      # held-out group (total optimizer)


def test_bounce_monotonic_and_bounded():
    fl = fly((0, 0, R_BALL), (60, 0, 18), (0, -260, 0), P)
    soft = bounce_roll(fl.land_pos, fl.land_vel, fl.land_spin, "soft")["rest_x"]
    nor = bounce_roll(fl.land_pos, fl.land_vel, fl.land_spin, "normal")["rest_x"]
    firm = bounce_roll(fl.land_pos, fl.land_vel, fl.land_spin, "firm")["rest_x"]
    assert fl.land_pos[0] < soft < nor < firm
    assert (firm - fl.land_pos[0]) < 80
    # steeper descent -> less roll (USGA/R&A: roll falls with landing angle)
    rolls = []
    for L, S in ((9, 1800), (12, 2600), (16, 3400)):
        x = shot_from_launch(78, L, S, P, roll=True)
        rolls.append((x.descent_deg, x.roll_m))
    rolls.sort()
    assert rolls[0][1] > rolls[-1][1]


def test_roll_slope_in_published_band():
    s = VAL["roll_vs_descent"]["model_slope_yd_per_deg"]
    assert -2.45 <= s <= -0.74            # range of the 8 fetched USGA/R&A experiments


def test_firmness_calibration_matches_its_single_target():
    c = VAL["firmness_calibration"]["check_at_tour_avg"]
    assert c["soft"] == pytest.approx(-5.31, abs=0.05) and c["firm"] == pytest.approx(4.49, abs=0.05)


def test_full_chain_130mph_moderate_case_in_published_ballpark():
    r = simulate_shot(Delivery(130 * MPH, 13.5, 4.0), p=P)
    assert 1.45 < r.smash < 1.51 and 10 < r.launch_deg < 14 and 1800 < r.spin_rpm < 3200
    assert 300 < r.carry_yd < 360 and r.total_yd > r.carry_yd + 10


def test_contact_api_zero_offset_equals_impact():
    d = Delivery(50.0, 12.0, 2.0)
    vc, n, toe = delivery_vectors(d)
    a = impact_vec(vc, n, toe, P)
    b = contact_to_ball(vc, np.zeros(3), n, toe, np.zeros(3), np.zeros(3), P)
    assert np.allclose(a["v_ball"], b["v_ball"]) and np.allclose(a["omega"], b["omega_ball"])


def test_contact_api_offset_and_head_rotation():
    d = Delivery(50.0, 12.0, 0.0)
    vc, n, toe = delivery_vectors(d)
    up = np.cross(toe, n)
    b = contact_to_ball(vc, np.zeros(3), n, toe, 0.0254 * toe, np.zeros(3), P)
    ref = impact(d, Strike(x_toe_m=0.0254), P)
    assert np.allclose(b["v_ball"], ref["v_ball"]) and b["x_toe_m"] == pytest.approx(0.0254)
    # head spinning about the vertical axis changes the contact-point velocity (rotation about 'up' moves a toe point along +/- n)
    b2 = contact_to_ball(vc, 20.0 * up, n, toe, 0.0254 * toe, np.zeros(3), P)
    assert not np.allclose(b2["v_contact"], vc)


def test_env_adapter_matches_direct_model_for_lh():
    d = Delivery(55.0, 13.0, 3.0, handed="LH")
    vc, n, toe = delivery_vectors(d)
    out = env_contact_to_shot(vc, n, (0.01, 0.005), handed="LH", toe_sign=1.0, p=P)
    ref = impact(d, Strike(x_toe_m=0.01, y_high_m=0.005), P)
    assert out["ball_speed"] == pytest.approx(ref["ball_speed"], rel=1e-9)
    assert out["backspin_rpm"] == pytest.approx(ref["backspin_rpm"], rel=1e-6)
    out2 = env_contact_to_shot(vc, n, None, handed="LH", p=P)
    assert out2["x_toe_m"] == 0.0


def test_validation_report_heldout_numbers():
    c = VAL["carry_residuals_calibrated_yd"]
    assert c["tm_total_opt"]["rmse"] < 5 and c["rice"]["rmse"] < 8           # held-out groups
    assert c["foresight"]["bias"] < -10                                      # documented source disagreement (model < Foresight)
    t = VAL["total_residuals_yd"]
    assert t["tm_total_opt"]["rmse"] < 8
    assert VAL["dt_convergence_carry_yd"]["0.02"] == pytest.approx(VAL["dt_convergence_carry_yd"]["0.002"], abs=0.1)


def test_every_coefficient_is_labelled():
    for k, v in COEF["params"].items():
        assert v["status"] in ("calibrated", "assumption", "published"), k
        assert v["source"] != "" or v["status"] == "assumption", k
    assert COEF["no_personal_clip_data"] is True


def test_standalone_no_env_eval_train_imports_and_no_mason_data():
    for f in (ROOT / "golfphys").glob("*.py"):
        t = f.read_text()
        assert not re.search(r"^\s*(from|import)\s+(env|eval|train)\b", t, re.M), f
        assert "mason" not in t.lower(), f
        if f.name != "build_coeffs.py":
            assert "instagram" not in t.lower(), f
