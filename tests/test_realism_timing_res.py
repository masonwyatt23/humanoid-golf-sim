"""Opt-in --timing-res-ms for eval.realism_check (v5): default argv/verdict unchanged; per-substep traces resolve a 6 ms arm->club lead that the
default 20 ms tie tolerance cannot; legacy_view reproduces the default-cadence traces exactly."""
import types
import numpy as np
from eval import realism_check as RC

def _ep(lead_ms=(110, 40, 6), dt=0.002, seg_every=1, seg_default=2, t_imp=1.0):
    t = np.arange(dt, 1.2 + 1e-9, dt); sub = list(range(1, len(t) + 1))
    pk = {"club": t_imp, "pelvis": t_imp - lead_ms[0] / 1e3, "thorax": t_imp - lead_ms[1] / 1e3, "arm": t_imp - lead_ms[2] / 1e3}
    g = lambda c, a: (a * np.exp(-0.5 * ((t - c) / 0.03) ** 2)).tolist()
    r = dict(t=t.tolist(), pelvis_dps=g(pk["pelvis"], 450), thorax_dps=g(pk["thorax"], 750), arm_dps=g(pk["arm"], 1000), club_dps=g(pk["club"], 2000),
             xfactor_deg=[0.0] * len(t), lead_share=[0.5] * len(t), grf=[[300.0, 300.0]] * len(t), sub=sub, seg_every=seg_every, seg_every_default=seg_default, t_contact=t_imp)
    r["impact_idx"] = int(np.argmax(t >= t_imp)); return r

def _row(rows, name): return next(c for c in rows if c["name"] == name)

def test_default_worker_args_unchanged():
    a = types.SimpleNamespace(club_len=1.15, eps_per_seed=8, strike_gate_nx=None)
    assert RC.worker_args(a, "/repo", "/ck", 0.6, 4000)[-1] == "off"                 # no flag -> argv exactly as before (no 'seg1')
    a.timing_res_ms = None; assert RC.worker_args(a, "/repo", "/ck", 0.6, 4000)[-1] == "off"
    a.timing_res_ms = 5.0; assert RC.worker_args(a, "/repo", "/ck", 0.6, 4000)[-1] == "seg1"

def test_cli_default_off():
    src = open(RC.__file__).read(); assert '"--timing-res-ms", type=float, default=None' in src

def test_legacy_view_keeps_default_cadence():
    r = _ep(); q = RC.legacy_view(r)
    assert len(q["t"]) == len(r["t"]) // 2 and all(s % 2 == 0 for s in q["sub"])
    assert np.allclose(np.diff(q["t"]), 0.004) and q["t"][q["impact_idx"]] >= 1.0 - 1e-9 > q["t"][q["impact_idx"] - 1]
    assert RC.legacy_view(_ep(seg_every=2)) is not None and len(RC.legacy_view(_ep(seg_every=2))["t"]) == len(r["t"])   # already default cadence: untouched

def test_5ms_resolves_6ms_arm_club_lead_that_20ms_cannot():
    r = _ep(lead_ms=(110, 40, 6))
    fine, dt = RC.timing_res_rows(r, 5, 80.0); assert abs(dt - 0.002) < 1e-9
    assert _row(fine, "kinematic_sequence_order")["status"] == "pass"
    coarse, _ = RC.timing_res_rows(r, 20, 80.0)                                       # same traces, default 20 ms tie tolerance
    assert _row(coarse, "kinematic_sequence_order")["status"] == "warn"

def test_5ms_still_warns_on_true_tie_and_fails_real_swap():
    tie, _ = RC.timing_res_rows(_ep(lead_ms=(110, 40, -4)), 5, 80.0)                    # arm 4 ms AFTER club: within one 5 ms tolerance -> warn, not pass
    assert _row(tie, "kinematic_sequence_order")["status"] == "warn"
    swap, _ = RC.timing_res_rows(_ep(lead_ms=(110, 30, 70)), 5, 80.0)                   # thorax 40 ms after arm -> fail
    assert _row(swap, "kinematic_sequence_order")["status"] == "fail"

def test_timing_uses_measured_interval():
    rows, _ = RC.timing_res_rows(_ep(lead_ms=(110, 40, 6)), 5, 80.0)
    v = _row(rows, "kinematic_sequence_timing_ms_before_club_peak")["value"]
    assert abs(v["pelvis"] - 110) <= 4 and abs(v["thorax"] - 40) <= 4                    # real ms on the measured 2 ms grid (not scaled by an assumed 5 ms)
