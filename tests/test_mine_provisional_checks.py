"""PROVISIONAL gating checks (Orchestrator 2026-10-19): mine/start_direction and mine/lead_foot_plant. Bands, worst-of logic, skip when not logged,
row text carries the PROVISIONAL label, top-of-backswing detection on the episode's own time axis, post-impact motion ignored, and gating in summarize."""
import numpy as np
from eval import swing_realism as SR

def _st(kv): return kv[1]["status"]

def test_start_direction_bands_and_worst_of_two():
    assert _st(SR.check_start_direction(3.9, 6.9)) == "pass"
    assert _st(SR.check_start_direction(4.1, 6.9)) == "warn" and _st(SR.check_start_direction(8.1, 1.0)) == "fail"
    assert _st(SR.check_start_direction(1.0, 7.5)) == "warn" and _st(SR.check_start_direction(1.0, 14.5)) == "fail"
    assert _st(SR.check_start_direction(5.0, 15.0)) == "fail"                      # worst of warn/fail
    assert _st(SR.check_start_direction(None, None)) == "skip"
    assert _st(SR.check_start_direction(2.0, None)) == "pass"                      # one component available

def test_lead_foot_bands():
    f = lambda l, s: _st(SR.check_lead_foot_plant(l, s, 24, "logged"))
    assert f(3.0, 5.0) == "pass" and f(3.1, 1) == "warn" and f(1, 5.1) == "warn" and f(6.1, 1) == "fail" and f(1, 10.1) == "fail" and f(4, 11) == "fail"
    assert _st(SR.check_lead_foot_plant(None, None)) == "skip"

def test_rows_are_labelled_provisional_and_named_mine():
    for k, v in (SR.check_start_direction(9, 1), SR.check_lead_foot_plant(1, 1, 3, "logged"), SR.check_lead_foot_plant(None, None)):
        assert k.startswith("mine/") and SR.PROV in " ".join(v["why"]) and "PROVISIONAL, pending Data Agent sourcing" in SR.PROV

def _swing(dt=0.004, t_top=0.6, t_imp=1.0, lift=(0.0, 0.0), slip=0.0, post=0.0):
    t = np.arange(0, 1.3, dt); club = np.where(t < t_top, 300 * np.sin(np.pi * t / t_top) ** 2 + 5, 2000 * np.clip((t - t_top) / (t_imp - t_top), 0, 1))
    club = np.where(t > t_imp, 2000 * np.exp(-(t - t_imp) / 0.05), club)
    F = np.zeros((len(t), 5)); F[:, 2:] = 0.035
    mid = (t > t_top) & (t <= t_imp); bump = np.sin(np.pi * np.clip((t - t_top) / (t_imp - t_top), 0, 1))
    F[mid, 3] += lift[0] * bump[mid]; F[mid, 4] += lift[1] * bump[mid]; F[mid, 0] += slip * bump[mid]
    F[t > t_imp, 2:] += post; F[t > t_imp, 0] += post                              # big post-impact motion: must not count
    F[t < t_top, 2:] += 0.08                                                       # backswing motion before the top: must not count
    imp = int(np.argmax(t >= t_imp)); return t, club, F, imp

def test_top_index_logged_and_fallback():
    t, club, F, imp = _swing()
    i, m = SR.top_index(t, club, imp, 0.6); assert m == "logged" and abs(t[i] - 0.6) < 0.004
    i, m = SR.top_index(t, club, imp, None); assert m == "fallback_min_club_speed" and abs(t[i] - 0.6) <= 0.012

def test_lead_foot_motion_top_to_impact_only():
    t, club, F, imp = _swing(lift=(0.045, 0.01), slip=0.02, post=0.5)
    i, _ = SR.top_index(t, club, imp, 0.6); F[i, 2:] = 0.035                       # pose at the top is the reference
    lift, slip = SR.lead_foot_motion(t, F, imp, i)
    assert abs(lift - 4.5) < 0.1 and abs(slip - 2.0) < 0.1                         # heel lift 4.5 cm (warn band), slip 2 cm; post-impact 50 cm ignored
    assert _st(SR.check_lead_foot_plant(lift, slip, 1, "logged")) == "warn"

def test_new_rows_gate_the_verdict():
    C = dict([SR.check_start_direction(1, 1), SR.check_lead_foot_plant(1, 1, 1, "logged")]); assert SR.summarize(C)["verdict"] == "PASS"
    C = dict([SR.check_start_direction(1, 1), SR.check_lead_foot_plant(7, 1, 1, "logged")]); assert SR.summarize(C)["verdict"] == "FAIL"
    C = dict([SR.check_start_direction(None, None), SR.check_lead_foot_plant(None, None)]); s = SR.summarize(C); assert s["n_skip"] == 2 and s["n_fail"] == 0
