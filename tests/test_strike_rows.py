"""Strike-offset info rows (all v3 harnesses) and the v3d PROVISIONAL mine/strike_height row."""
import re
from pathlib import Path
from eval import realism_check as RC
from eval import harness_v3d as H

def _eps(dz, dy=5.0): return [dict(strike_dy_mm=dy, strike_dz_mm=z) for z in dz]

def _res(det_dz):
    C = {"shot/spin_rpm": dict(status="pass", passed=True, values=2500.0), "shot/club_speed_mph": dict(status="pass", passed=True, values=74.0)}
    C.update(RC.strike_info_rows(_eps(det_dz), _eps([-20.0] * 4)))
    return dict(checks=C)

def test_info_rows_values_and_status():
    R = RC.strike_info_rows(_eps([-10, -20, -30]), _eps([-5, -25]))
    dz = R["mine/strike_dz_info"]; assert dz["status"] == "info" and not dz["gating"]
    assert dz["values"]["deterministic"]["median"] == -20 and dz["values"]["deterministic"]["median_abs"] == 20
    assert dz["values"]["robustness"]["n"] == 2 and R["mine/strike_dy_info"]["values"]["deterministic"]["median"] == 5

def test_info_rows_absent_when_not_logged():
    assert RC.strike_info_rows([{}, {}], []) == {}

def test_strike_mm_from_worker_record():
    assert RC._strike_mm(dict(strike=dict(dy_m=0.004, dz_m=-0.025))) == dict(strike_dy_mm=4.0, strike_dz_mm=-25.0, strike_centre=None)
    assert RC._strike_mm({}) == {}

def test_info_rows_do_not_change_counts():
    from eval import swing_realism as SR
    C = {"a": dict(status="pass"), "b": dict(status="warn")}; s0 = SR.summarize(C)
    C.update(RC.strike_info_rows(_eps([-25.0]))); s1 = SR.summarize(C)
    assert (s0["n_pass"], s0["n_warn"], s0["n_fail"], s0["n_checks"]) == (s1["n_pass"], s1["n_warn"], s1["n_fail"], s1["n_checks"])

def test_strike_height_thresholds():
    assert H.strike_height_status(None) == "skip"
    assert H.strike_height_status(15.0) == "pass" and H.strike_height_status(15.1) == "warn"
    assert H.STRIKE_FACE_EDGE_MM == 26.5
    assert H.strike_height_status(26.4) == "warn" and H.strike_height_status(26.5) == "fail"

def test_v3d_adds_gating_row_uses_abs_median():
    out = H.apply_v3d(_res([-25.0, -26.0, 10.0]))
    row = out["checks"]["mine/strike_height"]; assert row["status"] == "warn" and row["tag"] == "provisional"
    assert out["n_warn"] == 1 and out["verdict"] == "WARN"
    assert H.apply_v3d(_res([-27.0, -33.0, -40.0]))["checks"]["mine/strike_height"]["status"] == "fail"
    assert H.apply_v3d(_res([-3.0]))["checks"]["mine/strike_height"]["status"] == "pass"

def test_v3d_no_row_without_strike_data():
    r = dict(checks={"shot/spin_rpm": dict(status="pass", passed=True, values=2500.0)})
    assert "mine/strike_height" not in H.apply_v3d(r)["checks"]

def test_face_edge_matches_sim_geometry():
    root = Path(__file__).resolve().parents[1]; xs = list((root / "env" / "models").glob("humanoid_golf_v5_g1_*h.xml"))
    if not xs:
        import pytest; pytest.skip("v5 G1 models not in this checkout")
    for x in xs:
        m = re.search(r'<geom name="head" size="([\d.]+) ([\d.]+) ([\d.]+)"', x.read_text()); assert m and abs(float(m.group(3)) * 1000 - H.SIM_BOX_HALF_HEIGHT_MM) < 1e-9

def test_worker_records_strike():
    src = (Path(__file__).resolve().parents[1] / "results" / "overnight" / "_j_worker_gp_v3.py").read_text()
    assert 'strike=(dict(dy_m=' in src and 'ball_hit_info["dz"]' in src


import pytest
C0 = dict(dz_used_m=0.0, smash=1.45, spin_rpm=2600.0, launch_deg=14.0, ball_speed_mph=107.0)

def test_extent_info_rows():
    out = H.apply_v3d(_res([-24.0]))["checks"]
    assert out["mine/strike_within_sim_box_info"]["values"]["flag"] is True and out["mine/strike_outside_measured_info"]["values"]["flag"] is True
    assert out["mine/strike_within_sim_box_info"]["status"] == "info"

def test_face_edge_guard_rejects_non_centre():
    with pytest.raises(ValueError): H.face_edge_eval(dict(C0, dz_used_m=-0.024), -24.0)
    with pytest.raises(ValueError): H.face_edge_eval({k: v for k, v in C0.items() if k != "dz_used_m"}, -24.0)
    with pytest.raises(ValueError): H.face_edge_eval(None, -24.0)

def test_face_edge_capped_vs_linear():
    r = H.face_edge_eval(C0, -24.0); k = 51.3 * 107 / 148
    assert r["capped"]["spin_rpm"] == pytest.approx(2600 + k * 12.7) and r["linear"]["spin_rpm"] == pytest.approx(2600 + k * 24)
    r = H.face_edge_eval(C0, -5.0); assert r["capped"]["spin_rpm"] == pytest.approx(r["linear"]["spin_rpm"])
    assert H.face_edge_eval(C0, -30.0)["valid"] is False   # beyond 26.5 mm half-height: off face

def _eps_c(dz, spin=2600.0): return [dict(strike_dy_mm=0.0, strike_dz_mm=z, strike_centre=dict(C0, spin_rpm=spin)) for z in dz]

def test_face_edge_rows_and_both_must_pass():
    R = H.face_edge_rows(_eps_c([-20.0] * 3, 3000.0), _eps_c([-20.0] * 4, 3000.0))
    cap, lin = R["mine/spin_face_edge_capped_info"], R["mine/spin_face_edge_linear_info"]
    assert cap["status"] == "info" and lin["values"]["robustness"]["spin_rpm"]["n"] == 4
    C = {"shot/spin_rpm": dict(status="fail", values=4300.0), "shot/club_speed_mph": dict(status="pass", values=74.0)}; C.update(R)
    fm = H.face_edge_model_verdict(dict(checks=C), lambda rpm, club: H.spin_status(rpm, club, True))
    # capped ~3471 pass (<=3700), linear ~3742 > 3700 -> warn: BOTH must pass
    assert fm["spin_status_det"] == "warn"

def test_face_edge_model_only_flag():
    R = H.face_edge_rows(_eps_c([-3.0]))
    C = {"shot/spin_rpm": dict(status="fail", passed=False, values=4300.0), "shot/club_speed_mph": dict(status="pass", passed=True, values=74.0)}; C.update(R)
    out = H.apply_v3d_flagged(dict(checks=C))
    assert out["verdict"] == "FAIL" and out["face_edge_model_only"] is True and out["face_edge_model"]["note"] == "not a pass (face-edge-model-only)"
