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
    assert out["mine/strike_within_sim_box_info"]["values"]["flag"] is True and out["mine/strike_outside_measured_info"]["values"]["flag"] is True and "mine/strike_outside_measured_launch_info" not in out and out["mine/strike_beyond_r2207_info"]["values"]["flag"] is True
    assert out["mine/strike_within_sim_box_info"]["status"] == "info"

def test_face_edge_guard_rejects_non_centre():
    with pytest.raises(ValueError): H.face_edge_eval(dict(C0, dz_used_m=-0.024), -24.0)   # raised by the Data Agent module's own guard
    with pytest.raises(ValueError): H.face_edge_eval({k: v for k, v in C0.items() if k != "dz_used_m"}, -24.0)
    with pytest.raises(ValueError): H.face_edge_eval(None, -24.0)

def test_face_edge_capped_vs_linear():
    r = H.face_edge_eval(C0, -24.0); k = 51.3 * 107 / 148
    assert r["capped"]["spin_rpm"] == pytest.approx(2600 + k * 12.7) and r["linear"]["spin_rpm"] == pytest.approx(2600 + k * 24)
    r = H.face_edge_eval(C0, -5.0); assert r["capped"]["spin_rpm"] == pytest.approx(r["linear"]["spin_rpm"])
    assert H.face_edge_eval(C0, -30.0)["valid"] is False   # beyond 26.5 mm half-height: off face
    r = H.face_edge_eval(C0, -15.0); assert r["r2207"]["spin_rpm"] == pytest.approx(2600 + 963 * 107 / 167)

def test_r2207_in_spin_rule_and_no_data():
    # within 21 mm: r2207 enters; capped/linear pass at 2000 centre but r2207 2000+963*107/167=2617 pass too -> pass
    R = H.face_edge_rows(_eps_c([-15.0], 2000.0)); C = {"shot/spin_rpm": dict(status="fail", values=4300.0), "shot/club_speed_mph": dict(status="pass", values=74.0)}; C.update(R)
    fn = lambda rpm, club: H.spin_status(rpm, club, True)
    assert H.face_edge_model_verdict(dict(checks=C), fn)["spin_status_det"] == "pass"
    # make r2207 fail only: centre 3100 -> capped 3100+37*12.7=3571 pass, linear 3100+37*15=3656 pass, r2207 3717 warn
    R = H.face_edge_rows(_eps_c([-15.0], 3100.0)); C.update(R); assert H.face_edge_model_verdict(dict(checks=C), fn)["spin_status_det"] == "warn"
    # beyond 21 mm: r2207 None -> no data, not pass
    R = H.face_edge_rows(_eps_c([-23.0], 2000.0)); C2 = {k: v for k, v in C.items() if "r2207" not in k}; C2.update(R)
    assert "mine/spin_face_edge_r2207_info" not in R or R["mine/spin_face_edge_r2207_info"]["values"]["deterministic"]["spin_rpm"] is None
    fm = H.face_edge_model_verdict(dict(checks=C2), fn); assert fm["spin_status_det"] == "no_data" and fm["verdict"] != "PASS"

def test_smash_primary_r2207_and_legacy_info():
    r = H.face_edge_eval(C0, -15.0); assert r["capped"]["smash"] == pytest.approx(1.45 * 0.9495) and r["smash_confidence"].startswith("MEDIUM")
    assert H.face_edge_eval(C0, -23.0)["smash_confidence"].startswith("LOW")
    assert "mine/smash_legacy_quadratic_info" in H.face_edge_rows(_eps_c([-15.0]))

def test_r2207_info_rows_present():
    R = H.face_edge_rows(_eps_c([-15.0]))
    assert R["mine/spin_face_edge_r2207_info"]["status"] == "info" and R["mine/smash_r2207_info"]["status"] == "info"
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


def test_launch_r2207_k30_inputs_and_rule():
    c = dict(C0, launch_deg=14.55, spin_rpm=2568.0)
    for dz, l22, lh in ((-10, 12.39, 12.55), (-15, 10.30, 11.55), (-21, 7.09, 10.35)):
        r = H.face_edge_eval(c, float(dz)); assert r["launch"]["r2207"] == pytest.approx(l22, abs=0.01) and r["launch"]["hotstix"] == pytest.approx(lh, abs=0.01)
    assert H.face_edge_eval(c, -23.0)["launch"]["r2207"] is None
    fn = lambda rpm, club: H.spin_status(rpm, club, True)
    def verdict(dz, launch0):
        E = [dict(strike_dy_mm=0.0, strike_dz_mm=dz, strike_centre=dict(C0, launch_deg=launch0, spin_rpm=2000.0))]
        C = {"shot/spin_rpm": dict(status="fail", values=4300.0), "shot/club_speed_mph": dict(status="pass", values=74.0), "shot/launch_deg": dict(status="pass", values=launch0)}; C.update(H.face_edge_rows(E))
        return H.face_edge_model_verdict(dict(checks=C), fn)
    assert verdict(-10.0, 14.55)["launch_status_det"] == "pass"
    assert verdict(-21.0, 11.0)["launch_status_det"] == "fail"        # r2207 ~3.5 deg < 7 while Hotstix 6.8 also < 7
    assert verdict(-21.0, 13.5)["launch_status_det"] == "fail"        # Hotstix 9.3 in band but r2207 ~6.0 out: BOTH required
    v = verdict(-23.0, 14.55); assert v["launch_status_det"] == "no_data" and v["verdict"] != "PASS"
    R = H.face_edge_rows([dict(strike_dy_mm=0.0, strike_dz_mm=-15.0, strike_centre=dict(C0))]); assert R["mine/launch_face_edge_r2207_info"]["status"] == "info"

def test_apply_v3d_builds_face_edge_rows_from_strike_episodes():
    r = _res([-15.0]); r["strike_episodes"] = [dict(strike_dy_mm=0.0, strike_dz_mm=-15.0, strike_centre=dict(C0))]
    r["robustness_episodes"] = [dict(contact=True, strike_dy_mm=0.0, strike_dz_mm=-10.0, strike_centre=dict(C0)), dict(contact=False)]
    out = H.apply_v3d_flagged(r)
    assert "mine/spin_face_edge_capped_info" in out["checks"] and out["face_edge_model"] is not None
    assert out["checks"]["mine/spin_face_edge_capped_info"]["values"]["robustness"]["spin_rpm"]["n"] == 1
