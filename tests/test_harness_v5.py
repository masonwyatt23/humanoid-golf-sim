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
    inside = lambda v, k: any(lo <= v <= hi for lo, hi in T[k])
    for s in H.HELDOUT_DR["seeds"]:
        dq, dv, mu, ball = H.sample_heldout(s, 29)
        assert not any(inside(abs(x), "joint_rad") for x in dq) and not any(inside(abs(x), "joint_vel") for x in dv)
        assert not any(inside(abs(x), "ball_m") for x in ball) and not inside(mu, "floor_mu")
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


@pytest.mark.parametrize("shape,lat,ok", [("draw", -6.0, True), ("draw", +6.0, False), ("fade", +6.0, True), ("fade", -6.0, False)])
def test_left_handed_draw_and_fade_world_frame(shape, lat, ok):
    """LH golfer: draw curves to world RIGHT (-y), fade to world LEFT (+y); RH is the mirror."""
    g = H.validate_goal(dict(target_carry_m=150, shape=shape, curve_m=6, handed="left"))
    t = H.task_episode(H.shot_geometry(dict(env_carry_m=150, azimuth_deg=0.0, env_lateral_m=lat)), g)
    assert t["shape_ok"] is ok
    g_rh = H.validate_goal(dict(target_carry_m=150, shape=shape, curve_m=6, handed="right"))
    assert H.task_episode(H.shot_geometry(dict(env_carry_m=150, azimuth_deg=0.0, env_lateral_m=-lat)), g_rh)["shape_ok"] is ok

def test_golfer_frame_fallback_converted_with_hand_sign():
    # humanoid_golf_env info: ball_lateral/launch_direction are golfer frame (x hand_sign). LH: golfer +6 -> world -6.
    geo = H.shot_geometry(dict(carry=150, ball_lateral=6.0, launch_direction=2.0), handed="left")
    assert geo["lateral_m"] == -6.0 and geo["azimuth_deg"] == -2.0 and geo["frame_source"].startswith("golfer")
    assert H.shot_geometry(dict(carry=150, ball_lateral=6.0, launch_direction=2.0), handed="right")["lateral_m"] == 6.0
    w = H.shot_geometry(dict(env_carry_m=150, azimuth_deg=1.0, env_lateral_m=3.0, ball_lateral=-99, launch_direction=-99), handed="left")
    assert w["lateral_m"] == 3.0 and w["frame_source"] == "world"   # world fields win

def test_rows_record_frame():
    rows, _ = H.task_accuracy([ep(150, 0, -6)], dict(target_carry_m=150, shape="draw", curve_m=6, handed="left"))
    assert all("world" in r["values"]["frame"] for r in rows.values())
    na, _ = H.task_accuracy([ep(150, 0, 0)]); assert all("world" in r["values"]["frame"] for r in na.values())


# ---------------- goal layout (Trainer a2c1c7a, reference main 3c7119db train/dr_goal.py)
def _encode_ref(g):   # copy of train.dr_goal.encode_goal (reference formula)
    c = g.get("club", "driver")
    return [float(c == "driver"), float(c == "7iron"), float(c == "pw"), float(g["target_carry"]) / 200.0, float(g["target_dir"]) / 10.0,
            {"draw": 1.0, "straight": 0.0, "fade": -1.0}[g.get("shape", "straight")], float(g.get("bend", 0.0)) / 10.0, 1.0 if g.get("handedness", "LH") == "RH" else -1.0]

def test_goal_set_is_fixed_driver_lh_and_roundtrips():
    assert len(H.GOAL_SET_V5) == 8 and all(g["club"] == "driver" and g["handedness"] == "LH" for g in H.GOAL_SET_V5)
    assert {g["shape"] for g in H.GOAL_SET_V5} == {"straight", "draw", "fade"} and H.GOAL_OBS_SLICE == (116, 124)
    for g in H.GOAL_SET_V5:
        d = H.decode_goal_obs(_encode_ref(g)); t = H.validate_goal(g)
        assert d["club"] == "driver" and d["shape"] == t["shape"] and d["handed"] == "left"
        assert d["target_carry_m"] == pytest.approx(g["target_carry"]) and d["target_dir_deg"] == pytest.approx(g["target_dir"]) and d["bend_deg"] == pytest.approx(g["bend"])

def test_trainer_goal_mapping():
    t = H.validate_goal(dict(club="pw", target_carry=100, target_dir=-2, shape="fade", bend=4, handedness="RH"))
    assert t["club"] == "wedge" and t["handed"] == "right" and t["bend_deg"] == 4 and t["target_dir_deg"] == -2
    assert H.validate_goal(dict(target_carry=150))["handed"] == "left"   # Trainer default handedness LH

def test_goal_from_obs_block_when_no_ep_goal():
    blk = _encode_ref(dict(club="driver", target_carry=130, target_dir=3, shape="draw", bend=5, handedness="LH"))
    g, src = H.find_goal(dict(goal=None, goal_obs_block=blk))
    assert src == "obs_block" and g["target_carry_m"] == pytest.approx(130) and g["shape"] == "draw"

@pytest.mark.parametrize("handed,shape,side,ok", [("LH", "draw", -400, True), ("LH", "draw", 400, False), ("LH", "fade", 400, True),
                                                  ("RH", "draw", 400, True), ("RH", "fade", -400, True)])
def test_bend_goal_graded_on_spin_axis_with_handedness(handed, shape, side, ok):
    """World spin axis + = curves left (golfphys). LH draw = curves world right = negative axis (Trainer spin_axis_target_deg mirrors for LH)."""
    g = H.validate_goal(dict(target_carry=150, target_dir=0, shape=shape, bend=5, handedness=handed))
    ax = math.degrees(math.atan2(side, 4000.0)); lat = 150 * math.tan(math.radians(ax)) * 0.6   # curve in the same world direction as the axis
    geo = H.shot_geometry(dict(env_carry_m=150, azimuth_deg=0.0, env_lateral_m=lat, sidespin_rpm=side, backspin_rpm=4000.0))
    assert abs(abs(geo["spin_axis_deg"]) - 5.71) < 0.05
    assert H.task_episode(geo, g)["shape_ok"] is ok

def test_trainer_goal_keys_match_if_clone_present():
    import os
    from pathlib import Path
    tr = os.environ.get("HGS_TRAINER_REPO") or str(Path(__file__).resolve().parents[1])   # main carries train/dr_goal.py itself
    f = Path(tr, "train", "dr_goal.py")
    if not f.exists(): pytest.skip("Trainer dr_goal.py not present")
    t = f.read_text()
    assert 'GOAL_KEYS = ("club_driver", "club_7iron", "club_pw", "target_carry", "target_dir", "shape", "bend", "handedness")' in t
    assert '1.0 if g.get("handedness", "LH") == "RH" else -1.0' in t and 'return -a if handed == "LH" else a' in t

# ---------------- final training DR (main 3c7119db) and held-out sets
def test_heldout1_disjoint_from_final_training_and_gap_kinds():
    assert H.assert_disjoint()
    kinds = {k: H.gap_kind(H.TRAINING_DR, H.HELDOUT_DR, k) for k in ("joint_rad", "joint_vel", "floor_mu", "ball_m")}
    assert kinds == {"joint_rad": "interpolation gap", "joint_vel": "interpolation gap", "floor_mu": "interpolation gap", "ball_m": "extrapolation"}
    T = H.TRAINING_DR
    assert T["joint_rad"] == [[0.0, 0.03], [0.05, 0.06]] and T["joint_vel"] == [[0.0, 0.06], [0.10, 0.12]]
    assert T["floor_mu"] == [[0.63, 1.07], [0.45, 0.54], [1.16, 1.25]] and T["ball_m"] == [[0.0, 0.012]] and T["seed_max"] == 900000

def test_heldout2_disjoint_and_extrapolation():
    assert H.assert_disjoint(H.TRAINING_DR, H.HELDOUT2_DR, other_sets=[H.HELDOUT_DR])
    assert min(H.HELDOUT2_DR["seeds"]) >= 920000 and not set(H.HELDOUT2_DR["seeds"]) & set(H.HELDOUT_DR["seeds"])
    assert all(H.gap_kind(H.TRAINING_DR, H.HELDOUT2_DR, k) == "extrapolation" for k in H.HELDOUT2_DR["dims"])

@pytest.mark.parametrize("k,val", [("torque_scale", [0.88, 0.92]), ("slope_grade", [0.06, 0.09]), ("loft_deg", [1.4, 2.0]),
                                   ("head_g", [[205.0, 212.0]]), ("latency_steps", [1, 2]),
                                   ("seg_trunk", [[0.88, 0.92]]), ("seg_trunk", [[1.08, 1.12]]), ("seg_thighcalf", [[0.80, 0.85]]),
                                   ("seg_thighcalf", [[1.16, 1.24]]), ("seg_foot", [[0.825, 0.86]]), ("seg_foot", [[1.14, 1.21]])])
def test_heldout2_overlap_detected(k, val):
    with pytest.raises(AssertionError): H.assert_disjoint(H.TRAINING_DR, dict(H.HELDOUT2_DR, **{k: val}))

def test_heldout_seed_guards():
    with pytest.raises(AssertionError): H.assert_disjoint(H.TRAINING_DR, dict(H.HELDOUT2_DR, seeds=[899999]))
    with pytest.raises(AssertionError): H.assert_disjoint(H.TRAINING_DR, dict(H.HELDOUT2_DR, seeds=[910005]), other_sets=[H.HELDOUT_DR])

def test_sample_heldout2_cycles_dims_within_ranges():
    H2 = H.HELDOUT2_DR; seen = {}
    for s in H2["seeds"]:
        d = H.sample_heldout2(s); seen.setdefault(d["dim"], []).append(d["value"])
    assert {k: len(v) for k, v in seen.items()} == {k: 4 for k in H2["dims"]}
    assert all(0.075 <= v <= 0.10 for v in seen["slope_grade"]) and all(0.85 <= v <= 0.89 for v in seen["torque_scale"])
    assert all(v == 2 for v in seen["latency_steps"]) and all(1.6 <= abs(v) <= 2.5 for v in seen["loft_deg"])
    assert all(185 <= v <= 189 or 211 <= v <= 215 for v in seen["head_g"])
    for k in ("seg_trunk", "seg_thighcalf", "seg_foot"): assert all(any(lo <= v <= hi for lo, hi in H2[k]) for v in seen[k])
    assert H.sample_heldout2(920003) == H.sample_heldout2(920003)
    p = H.heldout2_perturb(); assert p["seed0"] == 920000 and p["n"] == 32 and "heldout2" in p


# ---------------- segment mass (Trainer f253d5d), slope info-only, sidespin sign, D-plane
def test_segment_mass_training_and_heldout2_bands():
    T, H2 = H.TRAINING_DR, H.HELDOUT2_DR
    assert T["seg_trunk"] == [[0.92, 1.08]] and T["seg_thighcalf"] == [[0.84, 1.16]] and T["seg_foot"] == [[0.86, 1.14]]
    assert H2["seg_trunk"] == [[0.88, 0.90], [1.10, 1.12]] and H2["seg_thighcalf"] == [[0.76, 0.80], [1.20, 1.24]] and H2["seg_foot"] == [[0.79, 0.825], [1.175, 1.21]]
    assert "not_applied" not in H2
    for k, cv in (("seg_trunk", 0.04), ("seg_thighcalf", 0.08), ("seg_foot", 0.07)):   # training = 1 +- 2 CV; held-out ~2.5-3 SD
        assert T[k] == [[round(1 - 2 * cv, 2), round(1 + 2 * cv, 2)]]
        for lo, hi in H2[k]: assert 2.4 <= min(abs(lo - 1), abs(hi - 1)) / cv and max(abs(lo - 1), abs(hi - 1)) / cv <= 3.0 + 1e-9

def test_slope_is_info_only():
    assert H.HELDOUT2_DR["info_only_dims"] == ("slope_grade",) and "modelling gap; partial plumb-address option" in H.HELDOUT2_DR["info_only_why"]

@pytest.mark.parametrize("handed", ["LH", "RH"])
def test_sidespin_sign_world_left_regardless_of_hand(handed):
    """Trainer-confirmed: + sidespin / + spin axis curves toward +y (left, world) for either hand; LH draw -> -y, LH fade -> +y."""
    hs = 1.0 if handed == "RH" else -1.0
    for side in (400.0, -400.0):
        geo = H.shot_geometry(dict(env_carry_m=150, azimuth_deg=0.0, env_lateral_m=math.copysign(6.0, side), sidespin_rpm=side, backspin_rpm=4000.0))
        assert (geo["spin_axis_deg"] > 0) == (geo["curve_y_m"] > 0) == (side > 0)
    for shape, world_sign in (("draw", hs), ("fade", -hs)):
        g = H.validate_goal(dict(target_carry=150, target_dir=0, shape=shape, bend=5, handedness=handed))
        geo = H.shot_geometry(dict(env_carry_m=150, azimuth_deg=0.0, env_lateral_m=world_sign * 9.0, sidespin_rpm=world_sign * 400.0, backspin_rpm=4000.0))
        assert H.task_episode(geo, g)["shape_ok"]

def _imp(face, path, axis):
    return dict(impact_face_world_deg=face, impact_path_world_deg=path, impact_face_to_path_world_deg=face - path, impact_spin_loft_deg=14.0, impact_dloft_deg=12.0, impact_aoa_deg=-2.0, impact_spin_axis_deg=axis, impact_sidespin_rpm=axis * 50)

def test_dplane_row_world_keys_only():
    ep = lambda face, az, curve, axis, **kw: dict(contact=True, seed=1, impact=_imp(face, 0.0, axis), shot_extra=dict(env_carry_m=150, azimuth_deg=az, env_lateral_m=150 * math.tan(math.radians(az)) + curve, sidespin_rpm=axis * 50, backspin_rpm=3000.0), **kw)
    r = H.dplane_row([ep(4.0, 3.4, 5.0, 3.0), ep(-4.0, -3.4, -5.0, -3.0)])
    assert r["gating"] is False and r["status"] == "pass" and r["values"]["start_vs_085face_pass_frac"] == 1.0 and r["values"]["curve_sign_vs_axis_pass_frac"] == 1.0
    r = H.dplane_row([ep(4.0, -3.4, 5.0, -3.0)])
    assert r["values"]["start_vs_085face_pass_frac"] == 0.0 and r["values"]["curve_sign_vs_axis_pass_frac"] == 0.0
    # golfer-frame keys alone are never used
    assert H.dplane_row([dict(contact=True, face_yaw_deg=4.0, club_path_deg=1.0, shot_extra=dict(env_carry_m=150, azimuth_deg=3.4, env_lateral_m=5))])["status"] == "n/a"
    assert H.dplane_row([])["status"] == "n/a"
    import inspect; src = inspect.getsource(H.dplane_row); assert "face_yaw_deg\"]" not in src and "club_path_deg\"]" not in src and "face_path\"]" not in src
