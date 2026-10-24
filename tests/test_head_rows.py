"""Realistic-head pass-through (V3_HEAD, Trainer a9d917e): mine/head_info row, crown-tee label per head, face-edge threshold from env face_limits (2026-10-24)."""
import copy
import pytest
from pathlib import Path
from eval.realism_check import tee_info_rows
from eval import harness_v3d as H

G = dict(ball_centre_z_m=0.05987, ball_bottom_z_m=0.03853, ball_radius_m=0.021335, head_half_height_m=0.027, face_centre_z_m=0.032,
         crown_z_m=0.064, sole_min_z_m=0.002, ball_minus_face_centre_along_up_m=0.02348)
HEAD = dict(mode="realistic", source="env realistic head", face_limits_m=[0.027, 0.0525], expected={}, measured={}, estimates=["face-centre height when soled"], compromises="lie 56")
T = dict(mode="crown", args={}, tee_dz_used_m=0.00413, ball_dx_used_m=0.0, face_h_used_m=None, geometry=G, head=HEAD)

def test_head_info_row_only_when_present():
    assert "mine/head_info" not in tee_info_rows(dict(T, head=None))
    R = tee_info_rows(T); r = R["mine/head_info"]
    assert r["status"] == "info" and not r["gating"] and r["values"]["mode"] == "realistic" and r["values"]["face_limits_mm"] == [27.0, 52.5]
    assert "REALISTIC" in r["why"][0]

def test_crown_label_per_head():
    assert "REALISTIC HEAD crown tee" in tee_info_rows(T)["mine/tee_dz_info"]["why"][0]
    box = dict(T, head=dict(mode="box", face_limits_m=None))
    assert "COMPENSATES FOR THE OVERSIZED SIM HEAD" in tee_info_rows(box)["mine/tee_dz_info"]["why"][0]
    assert "COMPENSATES" in tee_info_rows(dict(T, head=None))["mine/tee_dz_info"]["why"][0]   # old workers (no head) = box

def test_face_edge_threshold():
    assert H.face_edge_for({})[0] == H.STRIKE_FACE_EDGE_MM == 26.5
    assert H.face_edge_for(dict(tee_info=dict(head=dict(mode="box", face_limits_m=None))))[0] == 26.5
    e, src = H.face_edge_for(dict(tee_info=T)); assert abs(e - 27.0) < 1e-9 and "env face_limits()" in src
    row = dict(status="info", values=dict(deterministic=dict(median_abs=26.8, median=-26.8)))
    assert H.strike_height_row(row)["status"] == "fail"
    r = H.strike_height_row(row, (e, src)); assert r["status"] == "warn" and r["expected"]["fail_at_mm"] == 27.0

def test_apply_v3d_uses_head_edge():
    C = {"mine/strike_dz_info": dict(status="info", passed=False, gating=False, values=dict(deterministic=dict(median_abs=26.8, median=-26.8)))}
    base = dict(checks=C, checks_passed=0, n_checks=0, n_warn=0, n_fail=0, verdict="")
    assert H.apply_v3d(base)["checks"]["mine/strike_height"]["status"] == "fail"
    assert H.apply_v3d(dict(copy.deepcopy(base), tee_info=T))["checks"]["mine/strike_height"]["status"] == "warn"

def test_worker_head_passthrough_source():
    w = Path(__file__).resolve().parents[1] / "results/overnight/_j_worker_gp_v3.py"
    if not w.exists(): pytest.skip("v3 worker is untracked (held); pass-through checked in the Evaluator repo")
    s = w.read_text()
    for k in ("V3_HEAD", "set_head", "face_limits()", "head geometry mismatch", "HEAD_TOL_M = 5e-4", "head_shell", "TEE_INFO = dict(head=HEAD_INFO"):
        assert k in s
