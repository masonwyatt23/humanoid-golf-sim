"""floor_mu_nominal must be the compiled model's floor friction (1.0), never a post-randomisation read."""
import glob, json, os, sys, pytest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
from eval.robust_grf import nominal_floor_mu
TR = os.environ.get("V5_TRAINER_EXPORT", "")  # optional local Trainer export; test skips when unset

class _M:
    import numpy as _np; geom_friction = _np.array([[1.0, 0.005, 0.0001]])
def test_helper_reads_fresh_model(monkeypatch):
    mj = pytest.importorskip("mujoco"); monkeypatch.setattr(mj, "mj_name2id", lambda m, t, n: 0)
    assert nominal_floor_mu(lambda *a, **k: (_M(), None), "LH", 1.15, 0.002, 1.0, None) == 1.0

@pytest.mark.skipif(not TR or not os.path.isdir(TR), reason="trainer export absent")
def test_real_model_nominal_is_one_even_after_random_draw():
    pytest.importorskip("mujoco"); sys.path.insert(0, TR)
    from env.v5_body import build_model
    from env.v5_golf_env import V5GolfEnv
    e = V5GolfEnv(dt=0.002, seed=1, friction_rand=True); e.reset(seed=5)
    assert abs(nominal_floor_mu(build_model, e.handed, e.club_len, e._dt_arg, e.force_scale, e.addr) - 1.0) < 1e-12

def test_committed_v3b_jsons_carry_corrected_label():
    fs = glob.glob(os.path.join(ROOT, "results/v5_runs/stageJK_harness_summary/*_v3b_gateoff_gp_arm06.json"))
    if not fs: pytest.skip("v3b summary JSONs absent")
    assert len(fs) >= 6  # six v3b re-scores + later independent v3b scores (e.g. K24a s53 200k)
    for f in fs:
        s = open(f).read(); assert "0.9776" not in s and '"floor_mu_nominal": 1.0' in s
