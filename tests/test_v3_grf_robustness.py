"""v3 PROVISIONAL harness additions (2026-10-19): lead-GRF rule (window top->impact+20 ms, zero-lag 4th-order Butterworth 50 Hz, >=3-sample guard,
raw value kept as INFO) and mine/robustness (perturbed-start gate). Defaults keep the v2 behaviour."""
import types
import numpy as np, pytest
from eval import robust_grf as RG
from eval import realism_check as RC

def _trace(dt=0.002, T=1.4, base=1.2):
    t = np.arange(0, T, dt); g = np.full_like(t, base); return t, g

def test_single_sample_spike_removed_by_butter_and_sustain():
    t, g = _trace(); i_top = int(1.0 / 0.002); i_imp = int(1.3 / 0.002); g[i_imp - 37] = 2.37
    assert RG.despike_peak(t, g, i_top, i_imp, "raw")[0] == pytest.approx(2.37)
    pk_b = RG.despike_peak(t, g, i_top, i_imp, "butter", 50, 4, post_s=0.02)[0]; pk_s = RG.despike_peak(t, g, i_top, i_imp, "sustain3")[0]
    assert pk_b < 1.5 and pk_s == pytest.approx(1.2)

def test_sustained_plateau_kept():
    t, g = _trace(); i_top, i_imp = 500, 650; g[560:580] = 2.0           # 40 ms plateau
    assert RG.despike_peak(t, g, i_top, i_imp, "sustain3")[0] == pytest.approx(2.0)
    assert RG.despike_peak(t, g, i_top, i_imp, "butter", 50, 4, post_s=0.02)[0] > 1.9

def test_window_excludes_follow_through_beyond_jitter_allowance():
    t, g = _trace(); i_top, i_imp = 500, 650; g[i_imp + 21:i_imp + 30] = 3.5   # sustained, +42..+58 ms after impact
    assert RG.despike_peak(t, g, i_top, i_imp, "butter", 50, 4, post_s=0.02)[0] < 1.5
    assert RG.despike_peak(t, g, i_top, i_imp, "raw")[0] == pytest.approx(1.2)
    g2 = g.copy(); g2[i_imp + 3:i_imp + 9] = 3.5                                    # inside +20 ms
    assert RG.despike_peak(t, g2, i_top, i_imp, "butter", 50, 4, post_s=0.02)[0] > 2.4

def test_pre_top_excluded():
    t, g = _trace(); g[100:140] = 3.0
    assert RG.despike_peak(t, g, 500, 650, "butter", 50, 4, post_s=0.02)[0] < 1.5

def test_butter_rejects_cutoff_above_nyquist():
    t, g = _trace(dt=0.004)
    with pytest.raises(ValueError): RG.despike_peak(t, g, 10, 100, "butter", 200, 4)

def test_grf_status_rule_unchanged():
    band = dict(pass_=None)
    from realism.checks import load_thresholds
    b = load_thresholds()["grf"]["lead_vertical_bw"]["value"]
    assert RG.grf_status(1.5, 0.0, b) == "pass" and RG.grf_status(2.3, 0.0, b) == "warn" and RG.grf_status(2.5, 0.0, b) == "fail" and RG.grf_status(1.5, -0.1, b) == "fail"

def test_grf_rows_labels_and_info():
    from realism.checks import load_thresholds
    b = load_thresholds()["grf"]["lead_vertical_bw"]["value"]
    row, info = RG.grf_rows([(1.4, 0.0)] * 3, "butter", RG.GRF_SOURCE, b, [2.59] * 3, {12.0: [1.3] * 3, 14.0: [1.31] * 3})
    assert row["status"] == "pass" and row["values"]["peak"] == pytest.approx(1.4) and "PROVISIONAL" in row["why"][0]
    assert info["status"] == "info" and info["values"]["peak"] == pytest.approx(2.59) and set(info["sensitivity"]) == {"12Hz", "14Hz"}
    for s in ("50 Hz", "Rachnavy", "MEDIUM confidence", "NO consensus", "zero-lag is OUR choice", "Worsfold 2007", "Liu 2025", "Lin 2023", "Han 2019",
              "EVENT-JITTER ALLOWANCE", "0.84 BW", "NO source"):
        assert s in RG.GRF_SOURCE

def _ep(contact=True, sd="pass", foot="pass", cs=72.0, sm=1.45, la=12.0, sp=2600.0, tc=1.2):
    return dict(contact=contact, sd_status=sd, foot_status=foot, club_speed_mph=cs if contact else None, smash=sm if contact else None, launch_deg=la if contact else None,
                spin_rpm=sp if contact else None, total_over_carry=tc if contact else None)

def test_robustness_pass_warn_fail():
    seeds = list(range(7000, 7024)); P = RG.default_perturb()
    assert RG.robustness_row([_ep()] * 24, P, seeds)["status"] == "pass"
    E = [_ep()] * 20 + [_ep(sp=3500.0)] * 4                                        # p90 spin in WARN band
    assert RG.robustness_row(E, P, seeds)["status"] == "warn"
    E = [_ep()] * 22 + [_ep(contact=False)] * 2                                    # 91.7% contact < 95%
    assert RG.robustness_row(E, P, seeds)["status"] == "fail"
    E = [_ep()] * 21 + [_ep(sd="warn")] * 3                                        # 87.5% SD pass < 90%
    assert RG.robustness_row(E, P, seeds)["status"] == "fail"
    E = [_ep()] * 21 + [_ep(foot="fail")] * 3
    assert RG.robustness_row(E, P, seeds)["status"] == "fail"
    E = [_ep()] * 20 + [_ep(tc=1.5)] * 4                                           # p90 t/c > 1.35 -> FAIL
    assert RG.robustness_row(E, P, seeds)["status"] == "fail"
    assert RG.robustness_row([], P, seeds)["status"] == "skip"

def test_robustness_records_seeds_and_magnitudes():
    v = RG.robustness_row([_ep()] * 24, RG.default_perturb(), list(range(7000, 7024)))["values"]
    assert v["seeds"][0] == 7000 and v["seeds"][-1] == 7023 and v["perturb"]["joint_deg"] == 1.5 and v["perturb"]["ball_tol_m"] == 0.01 and v["perturb"]["friction_rand"] is False and v["perturb"]["friction_range"] == [0.9, 1.1]

def test_shot_status_uses_harness_bands():
    assert RG.shot_status("spin_rpm", 2600) == "pass" and RG.shot_status("spin_rpm", 3500) == "warn" and RG.shot_status("spin_rpm", 4500) == "fail"
    assert RG.shot_status("total_over_carry", 1.2) == "pass" and RG.shot_status("total_over_carry", 1.3) == "warn" and RG.shot_status("total_over_carry", 1.36) == "fail"
    assert RG.shot_status("smash", 1.45) == "pass" and RG.shot_status("club_speed_mph", 55) == "warn"

def test_legacy_namespace_keeps_v2_worker_args():
    a = types.SimpleNamespace(grf_method="legacy", robustness=0, timing_res_ms=None, strike_gate_nx=None, club_len=1.15, eps_per_seed=8)
    assert not RC._fine_grf(a) and "seg1" not in RC.worker_args(a, "/r", "/c", 0.6, 4000)
    a.grf_method = "butter"; assert RC._fine_grf(a) and "seg1" in RC.worker_args(a, "/r", "/c", 0.6, 4000)


# ---- v3b (2026-10-19): v3 rules are the default; --harness v2 reproduces v2 ----
def _ns(**k):
    d = dict(harness="v3b", grf_method=None, robustness=None, timing_res_ms=None, strike_gate_nx=None, club_len=1.15, eps_per_seed=8); d.update(k)
    return types.SimpleNamespace(**d)

def test_v3b_is_default_cli():
    import sys as _s
    ap_args = RC.resolve_harness(_ns())
    assert ap_args.grf_method == "butter" and ap_args.robustness == 24 and ap_args.robust_wide_info is True

def test_harness_v2_flag_reproduces_v2():
    a = RC.resolve_harness(_ns(harness="v2"))
    assert a.grf_method == "legacy" and a.robustness == 0 and a.robust_wide_info is False and not RC._fine_grf(a)
    assert "seg1" not in RC.worker_args(a, "/r", "/c", 0.6, 4000)

def test_explicit_options_override_harness_defaults():
    a = RC.resolve_harness(_ns(grf_method="sustain3", robustness=8))
    assert a.grf_method == "sustain3" and a.robustness == 8

def test_gate_friction_narrow_and_wide_info_variant():
    p, w = RG.default_perturb(), RG.wide_perturb()
    assert p["friction_rand"] is False and p["friction_range"] == [0.9, 1.1] and "U(0.9,1.1)" in RG.friction_desc(p)
    assert w["friction_rand"] is True and w["friction_range"] is None and "U(0.5,1.2)" in RG.friction_desc(w)
    for k in ("joint_deg", "joint_vel", "ball_tol_m", "seed0", "n"): assert p[k] == w[k]

def test_wide_info_row_does_not_gate():
    from eval import swing_realism as SR
    C = {"a": dict(status="pass"), "mine/robustness_wide_friction_info": dict(status="info")}
    S = SR.summarize(C); assert S["verdict"] == "PASS" and S["n_checks"] == 1 and S["n_info"] == 1
