"""Tests for eval/swing_realism.py: analysis on synthetic rollouts (no MuJoCo), band helpers, and that the committed results file is consistent."""
import json, math
from pathlib import Path
import numpy as np
from eval import swing_realism as sr
ROOT = Path(__file__).resolve().parent.parent

def synth(n=120, imp=100, top=60, start=10):
    t = np.arange(n) * sr.DT; head = np.zeros((n, 3)); head[:, 2] = np.where(np.arange(n) <= top, np.arange(n) / top, 1 - (np.arange(n) - top) / 80)
    head[:, 0] = np.linspace(0, 0.5, n); ball = np.zeros((n, 3)); ball[imp:, 0] = np.linspace(0.01, 5, n - imp)
    W = np.zeros((n, 4)); W[:, 3] = np.radians(100 + 20 * np.arange(n))
    q = np.zeros((n, 12)); tau = np.zeros((n, 12)); return dict(t=t, head=head, ball=ball, w=W, q=q, qd=np.zeros((n, 12)), tau=tau, fz=np.zeros((n, 2)), fs=np.zeros((n, 2)), foot=np.zeros((n, 6)))

def test_phases_tempo_and_structural_zeros():
    R = synth(); jr = np.tile([[-1.0, 1.0]], (12, 1)); caps = np.full(12, 10.0)
    e = sr.analyse(R, jr, caps, 11, 300.0, dict(true_contact=True, impact_club_speed=45.0, peak_ball_speed=45.0, launch_elev_deg=15.0, carry=100.0))
    assert e["impact_idx"] == 100 and e["top_idx"] == 60 and e["start_idx"] > 0
    assert abs(e["downswing_s"] - 40 * sr.DT) < 1e-9 and abs(e["tempo_ratio"] - (60 - e["start_idx"]) / 40) < 1e-9
    assert e["ks"]["pelvis"]["peak_dps"] == 0.0 and e["xf_peak_deg"] == 0.0 and e["grf_total_peak_BW"] == 0.0
    assert abs(e["smash"] - 1.0) < 1e-9 and abs(e["carry_yd"] - 109.36) < 0.01

def test_joint_limit_and_saturation_fractions():
    R = synth(); jr = np.tile([[-1.0, 1.0]], (12, 1)); caps = np.full(12, 10.0); R["q"][:, 3] = 1.0; R["tau"][60:101, 5] = 10.0
    e = sr.analyse(R, jr, caps, 11, 300.0, dict(true_contact=True))
    assert e["limit_frac_per_joint"][3] == 1.0 and e["limit_frac_per_joint"][0] == 0.0 and e["sat_frac_per_act"][5] == 1.0 and e["sat_frac_per_act"][0] == 0.0

def test_reference_band_published_rows_and_extrapolation_flag():
    b = sr._ref_band(100.0); assert b["carry_yd"] == (222, 247) and not b["extrapolated"]       # published TrackMan AoA -5/+5 rows at 100 mph
    b = sr._ref_band(120.0); assert b["carry_yd"] == (281, 310)
    assert sr._ref_band(132.0)["extrapolated"] and sr._ref_band(98.0)["extrapolated"]

def test_derived_thresholds_documented():
    src = Path(sr.__file__).read_text()
    for k in ("XF_BAND", "TEMPO_RATIO", "DOWN_S", "SAT_TIME_MAX", "LIMIT_TIME_MAX"): assert f"{k} " in src and "DERIVED" in src
    assert "Cheetham" in src and "PMC9227529" in src and "PMC3794489" in src

def test_committed_results_verdicts_consistent():
    p = ROOT / "results" / "swing_realism.json"
    if not p.exists(): return
    J = json.loads(p.read_text())
    for k, m in J["models"].items():
        n = sum(c["passed"] for c in m["checks"].values())
        assert m["checks_passed"] == n and (m["verdict"] == "PASS") == (n == len(m["checks"]) == 8), k
        assert math.isfinite(m["checks"]["6_tempo"]["values"]["downswing_s"])
