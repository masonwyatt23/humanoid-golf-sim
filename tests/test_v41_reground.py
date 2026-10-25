"""Harness v4.1 re-grounding (NON-GATING info row): off by default, v4 path unchanged; residual bound when on."""
import os, sys, glob, json
import numpy as np, pytest
ROOT = os.path.join(os.path.dirname(__file__), ".."); sys.path.insert(0, ROOT)
W = os.path.join(ROOT, "results", "overnight", "_j_worker_gp_v3.py")

def test_default_perturb_has_no_reground():
    from eval import robust_grf as RG
    assert "reground" not in RG.default_perturb("v3c") and "reground" not in RG.wide_perturb("v3c")

def test_flag_default_off():
    src = open(os.path.join(ROOT, "eval", "realism_check.py")).read()
    assert '"--reground", action="store_true"' in src and 'getattr(a, "reground", False)' in src

def test_worker_v4_path_guarded():
    src = open(W).read()
    assert src.count("PERT.get('reground')") == 2 and "if _RG is not None: pinfo['reground']" in src

def test_v41_row_is_info_and_labelled():
    from eval import realism_check as RC
    row = dict(status="fail", passed=False, values=dict(contact_frac=1.0), why=["x"])
    E = [dict(perturb=dict(reground=dict(method="m", before=dict(pos_max_m=0.01, rot_max_deg=1.0, dxyz_m=[[0, 0.01, 0], [0, 0, 0]]),
                                         after=dict(pos_max_m=1e-7, rot_max_deg=1e-6, dxyz_m=[[0, 0, 0], [0, 0, 0]]))))]
    g = RC.v41_row(dict(checks={"mine/robustness": {}}), (row, E), False, False)
    assert g["status"] == "info" and g["gating"] is False and g["verdict_if_gating"] == "fail" and g["label"] == RC.V41_LABEL
    assert abs(g["reground"]["before_lateral_mm"]["max"] - 10.0) < 1e-9 and g["reground"]["after_pos_mm"]["max"] < 1e-3

def _env_repo():
    c = [os.environ.get("HGS_TRAINER_REPO", "")] + sorted(glob.glob(os.path.join(ROOT, "..", "_ro_trainer_*")))
    return next((p for p in c if p and os.path.exists(os.path.join(p, "env", "v5_golf_env.py"))), None)

@pytest.mark.skipif(_env_repo() is None, reason="no Trainer env checkout available")
def test_reground_residual_bound():
    sys.path.insert(0, _env_repo())
    mujoco = pytest.importorskip("mujoco")
    from env.v5_golf_env import V5GolfEnv
    from eval.reground import sole_poses, reground, TOL_POS_M
    e = V5GolfEnv()
    for s in range(7000, 7004):
        e.reset(seed=0); mujoco.mj_forward(e.m, e.d); T = sole_poses(e.m, e.d); q_up = e.d.qpos[e.qa[12:]].copy()
        rg = np.random.default_rng(s + 0x5EED); e.d.qpos[e.qa] += np.radians(1.5) * rg.uniform(-1, 1, len(e.qa)); mujoco.mj_forward(e.m, e.d); q_up = e.d.qpos[e.qa[12:]].copy()
        st = reground(e.m, e.d, T)
        assert st["after"]["pos_max_m"] < TOL_POS_M and st["after"]["rot_max_deg"] < 0.1
        assert np.array_equal(e.d.qpos[e.qa[12:]], q_up)   # waist/arm/wrist noise kept exactly
