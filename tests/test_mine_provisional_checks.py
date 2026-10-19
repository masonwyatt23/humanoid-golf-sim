"""PROVISIONAL gating checks (Orchestrator 2026-10-19; Data Agent bands 2026-10-19): mine/start_direction (USGA/R&A R22-01,
medium confidence) and mine/lead_foot_plant (Data Agent judgement, low confidence). Bands, worst-of logic, skip when not
logged, PROVISIONAL label + confidence note, top-of-backswing on the episode time axis, address-referenced plant metrics,
post-impact ignored, gating in summarize."""
import numpy as np
from eval import swing_realism as SR

def _st(kv): return kv[1]["status"]

def test_start_direction_bands_r22_and_worst_of_two():
    # pass <=7 / <=13.5; warn <=9 / <=17; fail above
    assert _st(SR.check_start_direction(6.9, 13.4)) == "pass"
    assert _st(SR.check_start_direction(7.1, 13.4)) == "warn"
    assert _st(SR.check_start_direction(9.1, 1.0)) == "fail"
    assert _st(SR.check_start_direction(1.0, 13.6)) == "warn"
    assert _st(SR.check_start_direction(1.0, 17.1)) == "fail"
    assert _st(SR.check_start_direction(8.0, 16.0)) == "warn"          # worst of warn/warn
    assert _st(SR.check_start_direction(8.0, 17.5)) == "fail"          # worst of warn/fail
    assert _st(SR.check_start_direction(None, None)) == "skip"
    assert _st(SR.check_start_direction(2.0, None)) == "pass"          # one component available

def test_start_direction_cites_r22_and_provisional_medium():
    k, v = SR.check_start_direction(1.0, 1.0)
    blob = " ".join(v["why"]) + " " + (v.get("ref") or "")
    assert k == "mine/start_direction" and "PROVISIONAL" in blob
    assert "R22-01" in blob or "USGA" in blob
    assert "medium confidence" in blob
    assert SR.PROV == "PROVISIONAL"

def test_lead_foot_airborne_slip_turn_bands():
    # airborne: fail >=3 ctrl steps; warn at 60% => 1.8
    def m(air_steps=0.0, slip_frac=0.0, turn=0.0):
        return dict(airborne_max_ctrl_steps=air_steps, airborne_max_s=air_steps * SR.CTRL_DT,
                    slip_m=slip_frac * SR.FOOT_LENGTH_M, slip_frac=slip_frac, turn_deg=turn, foot_length_m=SR.FOOT_LENGTH_M)
    assert _st(SR.check_lead_foot_plant(m(1.0, 0.10, 5), 1, "logged")) == "pass"
    assert _st(SR.check_lead_foot_plant(m(2.0, 0.10, 5), 1, "logged")) == "warn"   # 2 >= 1.8
    assert _st(SR.check_lead_foot_plant(m(3.0, 0.10, 5), 1, "logged")) == "fail"
    assert _st(SR.check_lead_foot_plant(m(0.0, 0.20, 5), 1, "logged")) == "warn"   # 20% > 15% warn, <=25%
    assert _st(SR.check_lead_foot_plant(m(0.0, 0.26, 5), 1, "logged")) == "fail"
    assert _st(SR.check_lead_foot_plant(m(0.0, 0.10, 13), 1, "logged")) == "warn"  # 13 > 12
    assert _st(SR.check_lead_foot_plant(m(0.0, 0.10, 21), 1, "logged")) == "fail"
    assert _st(SR.check_lead_foot_plant(None)) == "skip"

def test_lead_foot_turn_skipped_when_absent():
    m = dict(airborne_max_ctrl_steps=0.0, airborne_max_s=0.0, slip_m=0.0, slip_frac=0.0, turn_deg=None, foot_length_m=0.20)
    k, v = SR.check_lead_foot_plant(m, 1, "logged")
    assert v["status"] == "pass" and "turn not logged" in v["why"][0]

def test_rows_labelled_provisional_with_confidence():
    for k, v in (SR.check_start_direction(9, 1), SR.check_lead_foot_plant(
            dict(airborne_max_ctrl_steps=0, airborne_max_s=0, slip_m=0, slip_frac=0, turn_deg=0, foot_length_m=0.2), 1, "logged")):
        blob = " ".join(v["why"]) + " " + (v.get("ref") or "")
        assert k.startswith("mine/") and "PROVISIONAL" in blob
        assert ("medium confidence" in blob) or ("low confidence" in blob)

def _swing(dt=0.004, t_top=0.6, t_imp=1.0, slip_m=0.0, turn_deg=0.0, air_s=0.0, heel_only_m=0.0):
    t = np.arange(0, 1.3, dt); n = len(t)
    club = np.where(t < t_top, 300 * np.sin(np.pi * t / t_top) ** 2 + 5, 2000 * np.clip((t - t_top) / (t_imp - t_top), 0, 1))
    club = np.where(t > t_imp, 2000 * np.exp(-(t - t_imp) / 0.05), club)
    F = np.zeros((n, 6)); F[:, 2:5] = 0.035; F[:, 5] = 0.1
    mid = (t > t_top) & (t <= t_imp); u = np.clip((t - t_top) / max(t_imp - t_top, 1e-9), 0, 1); bump = np.sin(np.pi * u)
    F[mid, 0] += slip_m * bump[mid]
    F[mid, 5] += np.radians(turn_deg) * bump[mid]
    F[mid, 3] += heel_only_m * bump[mid]          # heel-only lift: toe stays down
    F[t > t_imp, 2:] += 0.5; F[t > t_imp, 0] += 0.5   # big post-impact: must not count
    g = np.full(n, 200.0)
    if air_s > 0:
        # airborne burst ending just before impact
        t0 = t_imp - air_s; g[(t >= t0) & (t <= t_imp)] = 0.0
    imp = int(np.argmax(t >= t_imp)); return t, club, F, g, imp

def test_top_index_logged_and_fallback():
    t, club, F, g, imp = _swing()
    i, m = SR.top_index(t, club, imp, 0.6); assert m == "logged" and abs(t[i] - 0.6) < 0.004
    i, m = SR.top_index(t, club, imp, None); assert m == "fallback_min_club_speed" and abs(t[i] - 0.6) <= 0.012

def test_lead_foot_metrics_address_ref_and_post_impact_ignored():
    t, club, F, g, imp = _swing(slip_m=0.04, turn_deg=10.0, air_s=0.0, heel_only_m=0.05)
    i, _ = SR.top_index(t, club, imp, 0.6)
    m = SR.lead_foot_plant_metrics(t, F, g, imp, i)
    assert m is not None
    assert abs(m["slip_m"] - 0.04) < 0.005
    assert abs(m["turn_deg"] - 10.0) < 1.0
    assert m["airborne_max_ctrl_steps"] < 1.0          # heel-only lift is NOT whole-foot airborne
    assert _st(SR.check_lead_foot_plant(m, 1, "logged")) == "warn"   # slip 4 cm = 20% of 20 cm foot -> warn

def test_lead_foot_airborne_run_fails():
    t, club, F, g, imp = _swing(air_s=0.08)            # 0.08 s = 4 control steps
    i, _ = SR.top_index(t, club, imp, 0.6)
    m = SR.lead_foot_plant_metrics(t, F, g, imp, i)
    assert m["airborne_max_ctrl_steps"] >= 3.0
    assert _st(SR.check_lead_foot_plant(m, 1, "logged")) == "fail"

def test_new_rows_gate_the_verdict():
    ok = dict(airborne_max_ctrl_steps=0, airborne_max_s=0, slip_m=0, slip_frac=0, turn_deg=0, foot_length_m=0.2)
    bad = dict(ok, airborne_max_ctrl_steps=4.0, airborne_max_s=0.08)
    C = dict([SR.check_start_direction(1, 1), SR.check_lead_foot_plant(ok, 1, "logged")]); assert SR.summarize(C)["verdict"] == "PASS"
    C = dict([SR.check_start_direction(1, 1), SR.check_lead_foot_plant(bad, 1, "logged")]); assert SR.summarize(C)["verdict"] == "FAIL"
    C = dict([SR.check_start_direction(None, None), SR.check_lead_foot_plant(None)]); s = SR.summarize(C); assert s["n_skip"] == 2 and s["n_fail"] == 0
