"""Harness v4 (2026-10-24): V4_SPEC cross-check, main row = 1.5 in tee, 1.6 in crown tee info-only, face-edge edge from env face_limits, pending-flag error."""
import pytest
from pathlib import Path
from eval import harness_v4 as H4
from eval import harness_v3d as H3

GOOD = {k: v["value"] for k, v in H4.V4_SPEC.items()}

def test_spec_numbers():
    assert abs(H4.V4_SPEC["tee_15in_ball_centre_m"]["value"] - 0.059435) < 1e-9
    assert abs(H4.V4_SPEC["tee_16in_ball_centre_m"]["value"] - 0.061975) < 1e-9
    assert H4.V4_SPEC["face_centre_z_ground_m"]["value"] == 0.029 and H4.V4_SPEC["cfz_m"]["value"] == 0.039
    assert H4.V4_SPEC["lie_deg"]["value"] == 58.5 and H4.V4_SPEC["izz_gcm2"]["value"] == 5600.0

def test_check_v4_tolerances():
    assert H4.check_v4(GOOD) == {}
    assert H4.check_v4(dict(GOOD, face_centre_z_ground_m=0.0294)) == {}
    assert "face_centre_z_ground_m" in H4.check_v4(dict(GOOD, face_centre_z_ground_m=0.0296))
    assert "lie_deg" in H4.check_v4(dict(GOOD, lie_deg=58.65)) and H4.check_v4(dict(GOOD, lie_deg=58.45)) == {}
    assert "izz_gcm2" in H4.check_v4(dict(GOOD, izz_gcm2=5670)) and H4.check_v4(dict(GOOD, izz_gcm2=5650)) == {}
    assert "cfz_m" in H4.check_v4({k: v for k, v in GOOD.items() if k != "cfz_m"})

def _r(fail=False, head="v4", tee="1.5in"):
    C = {"a": dict(status="pass", passed=True), "b": dict(status="fail" if fail else "pass", passed=not fail)}
    return dict(checks=C, checks_passed=0, n_checks=2, n_warn=0, n_fail=0, verdict="", tee_info=dict(mode=tee, head=dict(mode=head, face_limits_m=[0.027, 0.0525])))

def test_main_row_rules(monkeypatch):
    monkeypatch.setattr(H3, "face_edge_model_verdict", lambda out, fn: None)
    assert H4.apply_v4(_r())["verdict"] == "PASS"
    assert H4.apply_v4(_r(head="realistic"))["verdict"].startswith("not v4")
    assert H4.apply_v4(_r(tee="crown"))["verdict"] == "not v4 (main row must be the 1.5 in tee)"
    o = H4.apply_v4(_r(fail=True), _r(tee="crown"))
    assert o["verdict"] == "FAIL" and o["v4_crown_tee_only"] and o["v4_note"] == "not a pass (crown-tee-only)"
    row = o["checks"]["mine/v4_crown_tee_info"]; assert not row["gating"] and row["label"] == H4.V4_CROWN_LABEL
    assert o["harness_v3"]["harness"] == "v4"

def test_face_edge_v4():
    e, src = H3.face_edge_for(dict(tee_info=dict(head=dict(mode="v4", face_limits_m=[0.027, 0.0525]))))
    assert abs(e - 27.0) < 1e-9 and "env face_limits()" in src

def test_worker_v4_hooks():
    w = Path(__file__).resolve().parents[1] / "results/overnight/_j_worker_gp_v3.py"
    if not w.exists(): pytest.skip("v3 worker is untracked (held); checked in the Evaluator repo")
    s = w.read_text()
    for k in ("set_env_v4", "pending Trainer flag", "V3_TEE == '1.5in'", "def _v4_measure", "check_v4", "c['env_v4'] = True"):
        assert k in s

def test_worker_v4_args_and_tee_mapping():
    w = Path(__file__).resolve().parents[1] / "results/overnight/_j_worker_gp_v3.py"
    if not w.exists(): pytest.skip("v3 worker is untracked (held); checked in the Evaluator repo")
    s = w.read_text()
    assert "'v4' if A.get('env_v4')" in s                                   # env_v4 from args.json
    assert "if HEAD == 'v4' and V3_TEE in ('args', ''): V3_TEE = '1.5in'" in s   # main row forced to 1.5 in whatever args says
    assert "args_tee_mode=A.get('tee_mode')" in s and "args_env_v4=A.get('env_v4')" in s
    for k in ("json_ball_z_m", "dict_sole_clear_m", "dict_izz_gcm2", "json_v4_params", "swingweight"):
        assert k in s

def test_crown_row_tolerance_vs_trainer_default():
    # Trainer 54b49c6 v4 default tee = equator at the 62 mm crown (ball centre 62.0 mm); spec 1.6 in = 61.975 mm
    assert H4.check_v4(dict(GOOD, tee_16in_ball_centre_m=0.062)) == {}
