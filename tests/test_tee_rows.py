"""tee_dz / face_h / tee height INFO rows and the v3d 'not a pass (new-tee-only)' flag (2026-10-24)."""
import copy
from eval.realism_check import tee_info_rows
from eval import harness_v3d as H

T = dict(mode="crown", args=dict(tee_dz=0.02, ball_dx=None, face_h=0.053, tee_mode=None), tee_dz_used_m=0.0215, ball_dx_used_m=0.0, face_h_used_m=0.053,
         geometry=dict(ball_centre_z_m=0.0813, ball_bottom_z_m=0.0600, ball_radius_m=0.021335, head_half_height_m=0.032, face_centre_z_m=0.0499,
                       crown_z_m=0.0813, sole_min_z_m=0.002, ball_minus_face_centre_along_up_m=0.0274))

def test_no_rows_for_old_worker():
    assert tee_info_rows(None) == {}

def test_rows_info_only():
    R = tee_info_rows(T)
    assert set(R) == {"mine/tee_dz_info", "mine/face_h_info", "mine/tee_height_info"}
    assert all(r["status"] == "info" and not r["gating"] for r in R.values())
    v = R["mine/tee_height_info"]["values"]; assert abs(v["equator_minus_crown_mm"]) < 1e-9 and abs(v["ball_bottom_mm"] - 60.0) < 1e-9
    assert R["mine/face_h_info"]["values"]["non_default"] and abs(R["mine/tee_dz_info"]["values"]["tee_dz_args_mm"] - 20.0) < 1e-9

def _res(fail):
    C = {"a": dict(status="pass", passed=True), "b": dict(status="fail" if fail else "pass", passed=not fail)}
    return dict(checks=C, checks_passed=0, n_checks=2, n_warn=0, n_fail=0, verdict="")

def test_new_tee_only_flag(monkeypatch):
    monkeypatch.setattr(H, "face_edge_model_verdict", lambda out, fn: None)
    assert H.apply_v3d_flagged(_res(False), _res(True))["verdict"] == "not a pass (new-tee-only)"
    o = H.apply_v3d_flagged(_res(False), _res(False)); assert o["verdict"] == "PASS" and not o["new_tee_only"]
    assert H.apply_v3d_flagged(_res(False))["verdict"] == "PASS"
