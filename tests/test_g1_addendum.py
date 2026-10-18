import json
import math
import os
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import gen_g1_joint_mapping_public_refs as G  # noqa: E402
import gen_public_joint_velocities_110plus as V  # noqa: E402
import planar_swing_decomposition as P  # noqa: E402

REF = os.path.join(ROOT, "data", "references")
TRAJ = json.load(open(os.path.join(REF, "public_joint_trajectories_110plus.json")))
VEL = json.load(open(os.path.join(REF, "public_joint_velocities_110plus.json")))
MAP = json.load(open(os.path.join(REF, "g1_joint_mapping_public_refs.json")))
PLN = json.load(open(os.path.join(REF, "planar_swing_decomposition_public_refs.json")))
BANNED = ("instagram", "imit_private", "p1_s", "multisense", "amass", "golfdb", "mason")


def _clean(d):
    t = json.dumps(d).lower()
    for ok in ("contains_instagram_or_mason_derived_data", "derived_from_cmu_multisense_amass_golfdb"):
        t = t.replace(ok, "")
    return t


def test_labels_and_no_private_data():
    for d in (VEL, MAP, PLN):
        m = d["_meta"]
        assert m["derived"] is True
        assert m["contains_instagram_or_mason_derived_data"] is False
        assert m["derived_from_cmu_multisense_amass_golfdb"] is False
        t = _clean(d)
        for b in BANNED:
            assert b not in t, b
    assert VEL["_meta"]["synthetic_interpolation"] is True and PLN["_meta"]["synthetic_interpolation"] is True
    assert "ROUGH" in MAP["_meta"]["status"]


def test_velocity_matches_derivative_of_angles_and_is_consistent_with_generator():
    assert set(VEL["channels"]) == set(TRAJ["channels"])
    for ch, e in TRAJ["channels"].items():
        for mph, cur in e["speed_class_curves"].items():
            v = VEL["channels"][ch]["speed_class_curves"][mph]
            fd = np.gradient(np.array(cur["angle_deg"]), np.array(cur["t_s"]))
            assert np.allclose(v["velocity_deg_s"], fd, atol=0.01)
            assert len(v["velocity_deg_s"]) == 41
            assert np.allclose(np.abs(v["velocity_deg_s"]), v["speed_deg_s"], atol=0.01)
            if v.get("generator_speed_deg_s") is not None:
                # finite difference on a 10 ms grid agrees with the analytic generator speed to ~12% of its peak (sharp late ramps smear on a 10 ms grid)
                assert v["max_fd_vs_generator_deg_s"] <= 0.12 * max(1.0, v["peak_speed_generator_deg_s"]) + 5, (ch, mph)
            # integral of velocity recovers the angle change (trapezoid, interior exact for central diff up to ends)
            a = np.array(cur["angle_deg"])
            t = np.array(cur["t_s"])
            vv = np.array(v["velocity_deg_s"])
            rec = np.sum(0.5 * (vv[1:] + vv[:-1]) * np.diff(t))
            assert abs(rec - (a[-1] - a[0])) < 0.5
    pel = VEL["channels"]["pelvis_rotation"]["speed_class_curves"]["110"]
    assert abs(pel["peak_speed_fd_deg_s"] - 394) < 25            # Madrid 2020 hip-line peak
    assert abs(pel["peak_time_ms_before_impact_fd"] - 87) < 20
    assert VEL["channels"]["pelvis_rotation"]["peak_speed_published"]["citation"] == "madrid2020"
    assert VEL["channels"]["x_factor"]["peak_speed_published"]


def test_velocity_script_rebuilds_same_file():
    assert V.build()["channels"]["thorax_rotation"]["speed_class_curves"]["120"]["velocity_deg_s"] == \
        VEL["channels"]["thorax_rotation"]["speed_class_curves"]["120"]["velocity_deg_s"]


def test_mapping_names_exist_in_xml_and_actuation():
    j5, a5 = G.parse_joints(G.V5)
    j4, a4 = G.parse_joints(G.V4)
    jl, _ = G.parse_joints(G.V5L)
    assert set(j5) == set(jl)
    mp = MAP["mapping"]
    assert mp["waist_yaw"]["g1_joint"] in j5 and mp["waist_yaw"]["g1_joint"] in a5
    for k in ("arm_to_trunk", "elbow"):
        for side in ("g1_joint_left", "g1_joint_right"):
            n = mp[k][side]
            assert n in j5 and n in a5
        assert mp[k]["range_rad_left"] == j5[mp[k]["g1_joint_left"]]["range"]
    for s in ("left", "right"):
        for k in ("roll", "pitch", "yaw"):
            assert f"{s}_wrist_{k}_joint" in j5
    assert MAP["_meta"]["v5_all_29_joints_actuated"] is True
    assert MAP["_meta"]["v4_power_unactuated_joints"] == ["left_elbow", "left_shoulder_roll"]
    for f in ("status",):
        for k in ("waist_yaw", "pelvis_rotation", "arm_to_trunk", "elbow", "wrist_hinge"):
            assert mp[k][f]
    assert "UNVERIFIED" in mp["wrist_hinge"]["status"] and "UNVERIFIED" in mp["pelvis_rotation"]["status"]
    assert "lh_mirror_rule" in MAP["_meta"]


def test_lead_trail_matches_env_helper_text():
    src = open(os.path.join(ROOT, "env", "v5_body.py")).read()
    assert 'return ("right", "left") if handed == "LH" else ("left", "right")' in src
    assert G.ctor("LH") == ("right", "left") and G.ctor("RH") == ("left", "right")


def test_conversions_in_range_and_mirror_signs():
    j5, _ = G.parse_joints(G.V5)
    lo, hi = map(float, j5["left_elbow_joint"]["range"].split())
    for flex in (130, 58, 40, 34):
        q = G.elbow_q_rad(flex)
        assert lo <= q <= hi
        assert abs(80 - 55 * q - flex) < 1e-9
    slo, shi = map(float, j5["left_shoulder_pitch_joint"]["range"].split())
    for e in (90, 43, 35, 23):
        assert slo <= G.shoulder_pitch_rad(e) <= shi
    assert G.shoulder_pitch_rad(90) < 0                     # forward flexion is negative
    for xf in (-61.0, -14.0):
        wy = j5["waist_yaw_joint"]["range"].split()
        assert float(wy[0]) < G.waist_yaw_rad(xf, "RH") < float(wy[1])
        assert G.waist_yaw_rad(xf, "LH") == -G.waist_yaw_rad(xf, "RH")
    assert abs(G.wrist_hinge_rad(165) - math.radians(-75)) < 1e-12
    assert abs(G.wrist_hinge_rad(94) - math.radians(-4)) < 1e-12
    # right-side roll/yaw ranges are mirrored in the XML (basis of the mirror rule)
    for k in ("shoulder_roll",):
        l = list(map(float, j5[f"left_{k}_joint"]["range"].split()))
        r = list(map(float, j5[f"right_{k}_joint"]["range"].split()))
        assert np.allclose(r, [-l[1], -l[0]])


def test_planar_geometry():
    assert abs(P.in_plane_share(35, 35) - 1.0) < 1e-12
    assert abs(P.in_plane_share(35, 55) - math.cos(math.radians(20))) < 1e-12
    # top-view <-> spine-axis angle: identity when tilt is zero, monotone and unwrap-safe at -103 deg
    x = np.linspace(-110, 40, 31)
    assert np.allclose(P.topview_to_spine_axis_deg(x, 0.0), x, atol=1e-9)
    y = P.topview_to_spine_axis_deg(x, 35.0)
    assert np.all(np.diff(y) > 0)
    assert abs(P.topview_to_spine_axis_deg([90.0], 35.0)[0] - 90.0) < 1e-9
    assert P.club_peak_reference(120.0) > P.club_peak_reference(110.0)


def test_planar_decomposition_outputs():
    for mph, c in PLN["classes"].items():
        sh = c["share_of_swept_in_plane_angle"]
        assert abs(sum(sh.values()) - 1.0) < 0.01
        assert all(v > 0 for v in sh.values())
        r = np.array(c["rates_deg_s"]["chain_sum"])
        parts = sum(np.array(c["rates_deg_s"][k]) for k in ("trunk_in_plane", "arm_swing", "wrist_hinge"))
        assert np.allclose(r, parts, atol=0.3)
        assert 0.5 < c["chain_peak_over_club_peak"] < 1.3
        assert c["peak_chain_sum_time_ms_before_impact"] > 0
    d = P.decompose(TRAJ, 110)
    assert d["peak_chain_sum_deg_s"] == PLN["classes"]["110"]["peak_chain_sum_deg_s"]
    # lower in-plane share lowers the trunk contribution
    lo = P.decompose(TRAJ, 110, theta_s_deg=35.0, phi_deg=75.0)
    assert lo["swept_in_plane_deg"]["trunk"] < d["swept_in_plane_deg"]["trunk"]
    assert "Nesbit" in " ".join(PLN["_meta"]["concept_citations"])


def test_scripts_do_not_modify_env_eval_train():
    out = subprocess.run(["git", "status", "--porcelain", "env", "eval", "train"], cwd=ROOT, capture_output=True, text=True).stdout
    assert out.strip() == ""
