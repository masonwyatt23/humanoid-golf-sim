"""Harness v5 (opt-in): task-accuracy metrics, per-club band loading, held-out DR disjointness. v4 is untouched (tests/test_harness_v4.py)."""
import copy, hashlib, math, re
import numpy as np
import pytest
from eval import harness_v5 as H

def ep(carry, az, lat, seed=0, contact=True, goal=None):
    return dict(seed=seed, contact=contact, shot_extra=dict(env_carry_m=carry, azimuth_deg=az, env_lateral_m=lat), goal=goal)

def test_not_goal_conditioned_is_na():
    rows, per = H.task_accuracy([ep(200, 0, 0)])
    assert per == [] and set(rows) == {"v5/task_carry_error", "v5/task_direction_error", "v5/task_lateral_error", "v5/task_draw_fade"}
    assert all(r["status"] == "n/a" and r["gating"] is False for r in rows.values())

def test_curvature_and_errors():
    g = H.validate_goal(dict(club="7iron", target_carry_m=150, target_dir_deg=0, shape="draw", curve_m=6, handed="right"))
    geo = H.shot_geometry(dict(env_carry_m=150, azimuth_deg=-2.0, env_lateral_m=150 * math.tan(math.radians(-2.0)) + 6.0))
    assert geo["curve_y_m"] == pytest.approx(6.0)
    t = H.task_episode(geo, g)
    assert t["shape_sign_ok"] and t["shape_ok"] and t["curve_draw_m"] == pytest.approx(6.0)
    assert t["carry_err_m"] == pytest.approx(0) and t["dir_err_deg"] == pytest.approx(-2.0)
    assert t["lateral_err_m"] == pytest.approx(150 * math.tan(math.radians(-2.0)))

def test_left_handed_draw_sign_flips():
    g = H.validate_goal(dict(target_carry_m=150, shape="draw", curve_m=6, handed="left"))
    geo = H.shot_geometry(dict(env_carry_m=150, azimuth_deg=0.0, env_lateral_m=-6.0))
    assert H.task_episode(geo, g)["shape_ok"]
    geo2 = H.shot_geometry(dict(env_carry_m=150, azimuth_deg=0.0, env_lateral_m=+6.0))
    assert not H.task_episode(geo2, g)["shape_sign_ok"]

def test_task_rows_rates_and_cli_goal():
    goal = dict(club="wedge", target_carry_m=100, target_dir_deg=0, shape="straight")
    eps = [ep(100, 0, 0, i) for i in range(8)] + [ep(130, 15, 60, 9), ep(0, 0, 0, 10, contact=False)]
    rows, per = H.task_accuracy(eps, goal)
    c = rows["v5/task_carry_error"]
    assert c["values"]["n_contact"] == 9 and c["values"]["pass_rate"] == pytest.approx(8 / 9) and c["status"] == "pass" and c["gating"] is False
    assert rows["v5/task_direction_error"]["values"]["goal_source"] == "cli"
    assert rows["v5/task_draw_fade"]["values"]["sign_rate"] == pytest.approx(8 / 9)

def test_episode_goal_takes_precedence():
    g_ep = dict(target_carry_m=100); g_cli = dict(target_carry_m=200)
    g, src = H.find_goal(dict(goal=g_ep), None, g_cli)
    assert src == "episode" and g["target_carry_m"] == 100

@pytest.mark.parametrize("bad", [dict(), dict(target_carry_m=-1), dict(target_carry_m=100, club="putter"), dict(target_carry_m=100, shape="hook")])
def test_goal_validation(bad):
    with pytest.raises(ValueError): H.validate_goal(bad)

def test_club_bands_load_and_status():
    d = H.load_club_bands()
    assert set(H.CLUBS) <= set(d["clubs"])
    for c in ("7iron", "wedge"):
        cb = d["clubs"][c]; assert cb["status"] == "pending counsel" and not cb.get("bands") and "tour_average" not in cb and "75a97112" in cb["source_pointer"]
    for c in H.CLUBS: assert d["clubs"][c]["gating_in_v5"] is False
    b = d["clubs"]["driver"]["bands"]   # driver bands unchanged (v3d/v4)
    assert b["smash"]["fail_above"] == 1.5 and b["launch_deg"]["pass"] == [7.0, 16.0] and b["spin_rpm"]["pass"] == [2000, 3700] and b["land_angle_deg"]["pass"] == [30, 48]

def test_no_trackman_numbers_committed():
    txt = H.BANDS_PATH.read_text()
    # held values are checked by hash so the test itself does not quote counsel-pending numbers
    held = {'8d5dd23bf2a3fa2a', '4ecbf57547986d31', '4d378aa7873acb30', '5825f1c45eceb8ec', '38a8a3d7680c6ee9', '01877130966ade4c'}
    toks = set(re.findall(r"\d+(?:\.\d+)?", txt))
    assert not {hashlib.sha256(x.encode()).hexdigest()[:16] for x in toks} & held

@pytest.mark.parametrize("club", ["7iron", "wedge"])
def test_pending_club_reports_na(club):
    rows = H.club_band_rows(dict(smash=1.3, launch_deg=16.0, spin_rpm=7000, land_angle_deg=50), club)
    assert list(rows) == [f"v5/club_{club}_bands"] and rows[f"v5/club_{club}_bands"]["status"] == "n/a" and rows[f"v5/club_{club}_bands"]["gating"] is False

def test_driver_band_rows_grade():
    rows = H.club_band_rows(dict(smash=1.43, launch_deg=13.35, spin_rpm=4500, land_angle_deg=None), "driver")
    assert rows["v5/club_driver_smash"]["status"] == "pass" and rows["v5/club_driver_spin_rpm"]["status"] == "fail"
    assert rows["v5/club_driver_land_angle_deg"]["status"] == "skip" and all(r["gating"] is False for r in rows.values())

def test_pending_club_with_numbers_rejected(tmp_path):
    import json
    d = copy.deepcopy(H.load_club_bands()); d["clubs"]["7iron"]["bands"] = {"spin_rpm": {"pass": [1, 2], "warn": [0, 3]}}
    p = tmp_path / "b.json"; p.write_text(json.dumps(d))
    with pytest.raises(ValueError): H.load_club_bands(p)

def test_club_bands_reject_gating(tmp_path):
    d = H.load_club_bands(); d = copy.deepcopy(d); d["clubs"]["wedge"]["gating_in_v5"] = True
    p = tmp_path / "b.json"; import json; p.write_text(json.dumps(d))
    with pytest.raises(ValueError): H.load_club_bands(p)

def test_heldout_disjoint_from_training_and_harness_seeds():
    assert H.assert_disjoint()

@pytest.mark.parametrize("k,val", [("joint_rad", [0.02, 0.04]), ("joint_vel", [0.05, 0.08]), ("ball_m", [0.01, 0.02])])
def test_disjointness_check_fails_on_overlap(k, val):
    held = dict(H.HELDOUT_DR, **{k: val})
    with pytest.raises(AssertionError): H.assert_disjoint(H.TRAINING_DR, held)

def test_disjointness_check_fails_on_friction_or_seed_overlap():
    with pytest.raises(AssertionError): H.assert_disjoint(H.TRAINING_DR, dict(H.HELDOUT_DR, floor_mu=[[1.0, 1.1]]))
    with pytest.raises(AssertionError): H.assert_disjoint(H.TRAINING_DR, dict(H.HELDOUT_DR, seeds=[7005]))
    with pytest.raises(AssertionError): H.assert_disjoint(H.TRAINING_DR, H.HELDOUT_DR, training_seeds=[910003])

def test_sampler_values_outside_training_box():
    T = H.TRAINING_DR
    for s in H.HELDOUT_DR["seeds"]:
        dq, dv, mu, ball = H.sample_heldout(s, 29)
        assert (np.abs(dq) > T["joint_rad"][1]).all() and (np.abs(dv) > T["joint_vel"][1]).all() and (np.abs(ball) > T["ball_m"][1]).all()
        assert not (T["floor_mu"][0][0] <= mu <= T["floor_mu"][0][1])
    a = H.sample_heldout(910000, 29); b = H.sample_heldout(910000, 29)
    assert all(np.array_equal(np.atleast_1d(x), np.atleast_1d(y)) for x, y in zip(a, b))   # deterministic

def test_heldout_payload_and_apply_v5_keeps_v4_verdict():
    P = H.heldout_perturb()
    assert P["n"] == 24 and P["seed0"] == 910000 and P["joint_deg"] == 0.0 and "heldout" in P
    r4 = dict(verdict="FAIL", checks={}, v5_shot_medians=dict(smash=1.43, spin_rpm=3112, launch_deg=13.35, land_angle_deg=None))
    out = H.apply_v5(r4, [ep(200, 0, 0)])
    assert out["verdict"] == "FAIL" and out["v5"]["v4_verdict"] == "FAIL" and out["v5"]["club"] == "driver"
    assert all(r.get("gating") is False for r in out["v5"]["rows"].values())
    assert out["v5"]["rows"]["v5/heldout_dr_robustness"]["status"] == "skip"
