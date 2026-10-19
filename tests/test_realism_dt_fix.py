"""dt fix (2026-10-19): the v5 default path must use the MEASURED sample interval of the worker's logged sim time, not a hard-coded 5 ms.
JEnv/BEnv log every 2 substeps of 2 ms = 4 ms; reading 4 ms samples as 5 ms inflated every kinematic-sequence timing x1.25.
Tie tolerance (20 ms) and all thresholds are unchanged."""
import numpy as np, pytest
from eval import realism_check as RC
from eval import swing_realism as SR
from realism.checks import load_thresholds
from tests.test_realism_timing_res import _ep, _row

def test_episode_dt_is_measured_and_flags_wrong_declaration():
    r = _ep(dt=0.004, seg_every=2)
    dt, mis = RC.episode_dt(r, 0.005); assert abs(dt - 0.004) < 1e-12 and mis          # pre-fix workers declared 5 ms
    dt, mis = RC.episode_dt(r, 0.004); assert abs(dt - 0.004) < 1e-12 and not mis
    dt, mis = RC.episode_dt(_ep(dt=0.005), None); assert abs(dt - 0.005) < 1e-12 and not mis   # a worker that really resamples to 5 ms is read as 5 ms
    assert RC.episode_dt(dict(t=[1.0]), 0.004) == (0.004, False)
    with pytest.raises(ValueError): RC.episode_dt(dict(t=[]), None)

def _jt(r):
    w = np.radians(np.array([r["pelvis_dps"], r["thorax_dps"], r["arm_dps"], r["club_dps"]]).T)
    return dict(pelvis_w=w[:, 0], thorax_w=w[:, 1], arm_w=w[:, 2], club_w=w[:, 3])

def test_measured_dt_gives_true_ms_and_5ms_assumption_inflates_x125():
    r = _ep(lead_ms=(116, 40, 36), dt=0.004, seg_every=2)
    dt, _ = RC.episode_dt(r, 0.005)
    good = _row(SR.da_swing(_jt(r), dt, 80.0, r["impact_idx"]), "kinematic_sequence_timing_ms_before_club_peak")["value"]
    bad = _row(SR.da_swing(_jt(r), 0.005, 80.0, r["impact_idx"]), "kinematic_sequence_timing_ms_before_club_peak")["value"]
    assert abs(good["pelvis"] - 116) <= 4 and abs(good["thorax"] - 40) <= 4
    assert abs(bad["pelvis"] / good["pelvis"] - 1.25) < 0.03                               # the bug this fixes

def test_thresholds_and_tie_tolerance_unchanged():
    assert load_thresholds()["sequence"]["tie_tolerance_ms"]["value"] == 20

def test_no_hardcoded_5ms_in_default_path_and_workers_declare_true_dt():
    src = open(RC.__file__).read()
    assert "da_swing(jt, 0.005" not in src and "da_swing(jt, dt_ep" in src
    for f in (RC.ROOT / "eval" / "_v5_worker.py", RC.ROOT / "results" / "overnight" / "_j_worker_gp.py"):
        dump = [l for l in open(f).read().splitlines() if l.startswith("json.dump(")]
        assert len(dump) == 1 and "dt=0.005" not in dump[0] and "dt=float(e.dt) * SEG_DEF" in dump[0], f
