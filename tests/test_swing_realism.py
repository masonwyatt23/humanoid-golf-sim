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

def test_da_wrappers_and_static_pelvis_guard():
    # Data Agent functions are called; a static pelvis must not sneak through (peak_speed fails; my segments_rotate guard catches it too)
    R = synth(); jr = np.tile([[-1.0, 1.0]], (12, 1)); caps = np.full(12, 10.0)
    e = sr.analyse(R, jr, caps, 11, 300.0, dict(true_contact=True, impact_club_speed=45.0, peak_ball_speed=60.0, launch_elev_deg=12.0, carry=200.0))
    st = {c["name"]: c["status"] for c in e["da_swing"]}; assert st["peak_speed_pelvis_deg_s"] == "fail"
    assert {c["name"]: c["status"] for c in e["da_shot"]}["smash"] in ("pass", "warn", "fail")
    assert e["ks"]["pelvis"]["peak_dps"] < sr.MOVE_MIN_DPS

def test_extrapolated_rows_only_warn():
    res = dict(checks=[dict(name="x", status="fail", value=1, expected=2, reason="r", extrapolated=True), dict(name="y", status="fail", value=1, expected=2, reason="r", extrapolated=False)])
    c = {x["name"]: x["status"] for x in sr._compact(res, cap_extrapolated=True)}; assert c == {"x": "warn", "y": "fail"}

def test_verdict_tristate_and_aggregation():
    mk = lambda st: dict(status=st)
    assert sr.summarize({"a": mk("pass"), "b": mk("skip")})["verdict"] == "PASS"
    assert sr.summarize({"a": mk("pass"), "b": mk("warn")})["verdict"] == "WARN"
    assert sr.summarize({"a": mk("warn"), "b": mk("fail")})["verdict"] == "FAIL"
    eps = [dict(k=[dict(name="n", status=x, value=1.0, expected=None, reason=x, extrapolated=False)]) for x in ("pass", "warn", "warn", "fail")]
    assert sr.agg_da(eps, "k", "p")["p/n"]["status"] == "warn"                 # most common
    eps = [dict(k=[dict(name="n", status=x, value=1.0, expected=None, reason=x, extrapolated=False)]) for x in ("pass", "fail")]
    assert sr.agg_da(eps, "k", "p")["p/n"]["status"] == "fail"                 # tie -> worse

def test_committed_results_verdicts_consistent():
    p = ROOT / "results" / "swing_realism.json"
    if not p.exists(): return
    J = json.loads(p.read_text())
    for k, m in J["models"].items():
        st = [c["status"] for c in m["checks"].values()]
        assert m["checks_passed"] == st.count("pass") and m["n_fail"] == st.count("fail") and m["n_warn"] == st.count("warn")
        assert m["verdict"] == ("FAIL" if "fail" in st else "WARN" if "warn" in st else "PASS"), k
        assert math.isfinite(m["checks"]["mine/tempo"]["values"]["downswing_s"])

def test_realism_check_cli_importable_and_v5_worker_isolated():
    import importlib; importlib.import_module("eval.realism_check")
    w = (ROOT / "eval" / "_v5_worker.py").read_text(); assert "from eval" not in w and "import eval" not in w     # must not import this repo's packages (env/ collides with the Trainer's)
