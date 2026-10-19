"""PROVISIONAL harness additions (Orchestrator-approved 2026-10-19):

A) mine/robustness: GATING for any full PASS. A policy is re-run on N seeded episodes with small perturbations at address. The deterministic
   24-episode rows are unchanged. The perturbation is applied by the J worker (results/overnight/_j_worker_gp_v3.py, `perturb=` argument):
     * initial actuated joint angles: uniform +/-JOINT_DEG (1.5 deg). The env has no joint-noise option; this is our own, inside the requested 1-2 deg.
     * actuated joint velocities: uniform +/-JOINT_VEL (0.05 rad/s). Our own choice; "small".
     * ball position: the env's own `ball_tol_m` option (V5GolfEnv.reset: tee xy += uniform(-1, 1, 2) * ball_tol) at 0.01 m = +/-1 cm.
     * floor friction: v3b gate U(0.9, 1.1) drawn by the worker (PROVISIONAL, no turf source, centred on model mu 1.0); the env's U(0.5, 1.2) is the INFO row mine/robustness_wide_friction_info.
   Requirements across the N episodes:
     contact >= 95%; start_direction PASS >= 90%; lead_foot_plant PASS >= 90%; for club speed, smash, launch, spin and t/c (golfphys), the median
     episode is not FAIL and both p10 and p90 are not FAIL (inside the WARN band).
   Verdict: FAIL if any requirement fails. WARN if all hold but a median, p10 or p90 leaves the PASS band. Otherwise PASS.

B) Lead-GRF rule (PRIMARY per the Data Agent notes, see GRF_SOURCE): 4th-order zero-lag Butterworth 50 Hz, window top -> impact + 20 ms (jitter allowance, ours), >=3-sample guard; 12/14 Hz sensitivity as info.
   Earlier fallback kept as an option:
   method "sustain3" (fallback, no source): a value counts only if sustained for >= 3 consecutive 2 ms samples. Equivalently, the peak is the
   max over the window of the rolling minimum over k samples, with k = ceil(6 ms / dt). With 2 ms (per-substep) traces k = 3.
   method "butter": zero-lag Butterworth low-pass (scipy filtfilt), with cutoff_hz and order passed in; use only with a cited source.
   method "raw": the windowed raw max.
   Bands are unchanged (data/references/realism_thresholds.json grf.lead_vertical_bw). The old whole-episode raw peak is kept as INFO
   mine/grf_lead_vertical_raw_info.
"""
import math
import numpy as np

PROV = "PROVISIONAL"
JOINT_DEG = 1.5; JOINT_VEL = 0.05; BALL_TOL_M = 0.01
# v3b (Orchestrator-approved 2026-10-19): gate friction U(0.9, 1.1), PROVISIONAL, no turf source, centred on the model floor mu 1.0 (env/v5_body.py:86).
# The env's own U(0.5, 1.2) (env/v5_golf_env.py:149, a Stage A training randomisation, off in the J trainer) is kept as the INFO row mine/robustness_wide_friction_info.
FRICTION_RAND = False; FRICTION_RANGE = (0.9, 1.1); WIDE_FRICTION_RANGE = (0.5, 1.2)
ROBUST_SEED0 = 7000; ROBUST_N = 24
REQ_CONTACT = 0.95; REQ_SD = 0.90; REQ_FOOT = 0.90
SUSTAIN_S = 0.006           # 3 x 2 ms
_W = {"skip": -1, "info": -1, "pass": 0, "warn": 1, "fail": 2}

def default_perturb():
    return dict(joint_deg=JOINT_DEG, joint_vel=JOINT_VEL, ball_tol_m=BALL_TOL_M, friction_rand=FRICTION_RAND, friction_range=list(FRICTION_RANGE), seed0=ROBUST_SEED0, n=ROBUST_N)

def wide_perturb():
    """INFO variant: same joint/ball noise and seeds, floor friction from the env's own friction_rand U(0.5, 1.2)."""
    return dict(default_perturb(), friction_rand=True, friction_range=None)

def friction_desc(p):
    r = p.get("friction_range")
    return (f"floor friction U({r[0]:g},{r[1]:g}) (PROVISIONAL, no turf source, centred on model mu 1.0; worker rng seed+0xF41C)" if r else
            "floor friction U(0.5,1.2) (env friction_rand)" if p.get("friction_rand") else "floor friction fixed at model nominal")

FLOOR_MU_NOTE = ("floor_mu_nominal = floor geom friction of a freshly compiled model (env/v5_body.py build_model, floor friction [1.0, 0.005, 0.0001]), "
                 "read before any reset/randomisation. Until the 2026-10-19 label fix the worker read it after the env's construction-time reset, which had "
                 "already drawn U(0.5, 1.2): the 0.978 in earlier v3 JSONs was one random draw, mislabeled as nominal; verdicts unaffected.")

def nominal_floor_mu(build_model, handed, club_len, dt, force_scale, addr):
    """Floor sliding friction of a freshly compiled v5 model (no reset, no randomisation)."""
    import mujoco
    m, _ = build_model(handed, club_len, dt=dt, force_scale=force_scale, addr=addr)
    return float(m.geom_friction[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "floor"), 0])

# ---------------- B) GRF ----------------
GRF_NOTES = "grf_filter_window_NOTES.md (Data Agent 2026-10-19; held locally, not in git)"
BUTTER_CUTOFF_HZ = 50.0; BUTTER_ORDER = 4; POST_IMPACT_S = 0.020; SENS_CUTOFFS_HZ = (12.0, 14.0)
GRF_SOURCE = ("PRIMARY: 4th-order Butterworth low-pass 50 Hz, zero-lag (filtfilt), applied before the peak - Rachnavy et al. 2026 (PMC13111475, 4th-order 50 Hz) "
              "and Liu et al. 2026 (PMC13272296, 50 Hz); MEDIUM confidence, NO consensus (GRF cutoffs 6-50 Hz in the literature: Lin 2023 / Li 2026 6 Hz, "
              "Harada 2023 12 Hz, Chen 2024 14 Hz); zero-lag is OUR choice (not stated for GRF in any source). Secondary guard: >=3 consecutive samples "
              "(harness heuristic, no source). WINDOW: top of backswing -> impact is supported (Worsfold 2007 PMC3794489, Liu 2025 PMC12416643, "
              "Lin 2023 PMC10215287, Han 2019 MED/31042142: lead-foot peak in the downswing, before impact) + 20 ms EVENT-JITTER ALLOWANCE (our choice, "
              "not a literature value). BAND: 1.7 BW upper limit has NO source (PROVISIONAL, unverified); the only confirmed driver figure is 0.84 BW lead foot "
              "(Worsfold 2007). Notes: " + GRF_NOTES)

def _guard(w, t, k_samples=3):
    """Secondary guard: a value counts only if sustained for >= k consecutive samples (rolling min over k, then max)."""
    if len(w) < k_samples: return float(np.min(w))
    from numpy.lib.stride_tricks import sliding_window_view
    return float(sliding_window_view(np.asarray(w, float), k_samples).min(axis=1).max())

def despike_peak(t, g, i_top, i_imp, method="butter", cutoff_hz=BUTTER_CUTOFF_HZ, order=BUTTER_ORDER, post_s=0.0, guard=True):
    """Windowed (t[i_top] .. t[i_imp] + post_s), de-spiked peak of a lead-GRF trace (any unit). Returns (peak, min_raw_in_window, k_or_None).
    method: butter = zero-lag Butterworth (filtfilt) on the WHOLE trace, then window, then optional >=3-sample guard;
            sustain3 = >=3 consecutive 2 ms samples (k = ceil(6 ms / dt)); raw = windowed raw max."""
    t = np.asarray(t, float); g = np.asarray(g, float).reshape(-1)
    n = min(len(t), len(g)); t, g = t[:n], g[:n]; i_imp = min(int(i_imp), n - 1); i_top = max(0, min(int(i_top), i_imp))
    i_end = int(np.searchsorted(t, t[i_imp] + post_s + 1e-9, side="right")) - 1 if post_s > 0 else i_imp
    i_end = max(i_imp, min(i_end, n - 1)); w = g[i_top:i_end + 1]
    if len(w) == 0: return None, None, None
    mn = float(w.min())
    if method == "raw": return float(w.max()), mn, None
    dt = float(np.median(np.diff(t))) if n > 1 else 0.002
    if method == "sustain3":
        k = max(1, int(math.ceil(SUSTAIN_S / dt - 1e-9))); return _guard(w, t, k), mn, k
    if method == "butter":
        if not cutoff_hz or not order: raise ValueError("butter needs cutoff_hz and order")
        nyq = 0.5 / dt
        if cutoff_hz >= nyq: raise ValueError(f"cutoff {cutoff_hz} Hz >= Nyquist {nyq:.0f} Hz (sample interval {dt*1000:.1f} ms)")
        from scipy.signal import butter, filtfilt
        b, a = butter(int(order), float(cutoff_hz) / nyq); f = filtfilt(b, a, g)[i_top:i_end + 1]
        return (_guard(f, t, 3) if guard else float(f.max())), mn, (3 if guard else None)
    raise ValueError(f"unknown GRF method {method}")

def grf_status(peak, mn, band):
    """Same rule as realism/checks.py grf_lead_vertical_bw: FAIL if min < fail_outside lo or peak > fail_outside hi, else _band(peak)."""
    from realism.checks import _band
    if mn < band["fail_outside"][0] or peak > band["fail_outside"][1]: return "fail"
    return _band(peak, band["pass"], band["warn"], band["fail_outside"])

def grf_rows(per_ep, method, source_note, band, raw_whole, sens=None):
    """per_ep: list of (peak_bw, min_bw). Returns (swing row dict, info row dict). Status = most common per-episode status (ties -> worse), value = median."""
    st = [grf_status(p, m, band) for p, m in per_ep]; cnt = {}
    for s in st: cnt[s] = cnt.get(s, 0) + 1
    s0 = sorted(cnt, key=lambda k: (-cnt[k], -_W[k]))[0] if cnt else "skip"
    pk = float(np.median([p for p, _ in per_ep])) if per_ep else None; mn = float(np.median([m for _, m in per_ep])) if per_ep else None
    why = (f"peak lead-foot vertical force in body weights, WINDOWED top of backswing -> impact (+20 ms jitter allowance when method=butter), de-spiked ({method}); "
           f"bands unchanged (pass {band['pass']}, warn {band['warn']}, FAIL outside warn); {PROV}")
    row = dict(status=s0, passed=(s0 == "pass"), values=dict(peak=None if pk is None else round(pk, 3), min=None if mn is None else round(mn, 3), method=method),
               expected=band["pass"], why=[why], ref=source_note, tag="derived", extrapolated=False, episode_status_counts=cnt)
    info = dict(status="info", passed=False, values=dict(peak=round(float(np.median(raw_whole)), 3) if raw_whole else None),
                why=["OLD rule, INFO only: whole-episode raw lead-GRF peak (includes follow-through and single-sample contact spikes); not gating"],
                ref="previous swing/grf_lead_vertical_bw definition (eval/realism_check.py, v2)", tag="info_only", gating=False)
    if sens:
        info["sensitivity"] = {f"{hz:g}Hz": round(float(np.median(v)), 3) for hz, v in sens.items() if v}
        info["why"].append("sensitivity (INFO, not gating): same window + guard with 4th-order zero-lag Butterworth at " + ", ".join(f"{k} -> {v} BW" for k, v in info["sensitivity"].items()) + " (lower cutoffs lower the peak)")
    return row, info

# ---------------- A) robustness ----------------
def _pct(xs, q): return float(np.percentile(np.asarray(xs, float), q))

def shot_status(name, value):
    """Status of one shot number under the realism/checks.py driver bands (same code path as the deterministic rows)."""
    from realism.checks import check_shot_realism
    if value is None: return "skip"
    if name == "total_over_carry": shot = dict(carry_yd=100.0, total_yd=100.0 * value)
    else: shot = {name: value}
    res = check_shot_realism(shot, use_golfphys=False) if "use_golfphys" in check_shot_realism.__code__.co_varnames else check_shot_realism(shot)
    key = {"club_speed_mph": "club_speed_mph", "smash": "smash", "launch_deg": "launch_deg", "spin_rpm": "spin_rpm", "total_over_carry": "total_over_carry"}[name]
    for c in res["checks"]:
        if c["name"] == key: return c["status"]
    return "skip"

SHOT_KEYS = ("club_speed_mph", "smash", "launch_deg", "spin_rpm", "total_over_carry")

def robustness_row(eps, perturb, seeds):
    """eps: list of dicts with contact (bool), sd_status, foot_status, and the SHOT_KEYS (None if no contact). Returns the mine/robustness row."""
    n = len(eps)
    if n == 0:
        return dict(status="skip", passed=False, values=None, why=["no perturbed episodes run"], ref=None, tag="derived")
    c = [e for e in eps if e.get("contact")]
    fc = len(c) / n; fsd = sum(e.get("sd_status") == "pass" for e in c) / n; ffoot = sum(e.get("foot_status") == "pass" for e in c) / n
    fails, warns, stats = [], [], {}
    if fc < REQ_CONTACT: fails.append(f"contact {fc:.0%} < {REQ_CONTACT:.0%}")
    if fsd < REQ_SD: fails.append(f"start_direction PASS {fsd:.0%} < {REQ_SD:.0%}")
    if ffoot < REQ_FOOT: fails.append(f"lead_foot_plant PASS {ffoot:.0%} < {REQ_FOOT:.0%}")
    for k in SHOT_KEYS:
        xs = [e[k] for e in c if e.get(k) is not None]
        if not xs: fails.append(f"{k}: no values"); continue
        m, p10, p90 = float(np.median(xs)), _pct(xs, 10), _pct(xs, 90)
        s = {q: shot_status(k, v) for q, v in (("median", m), ("p10", p10), ("p90", p90))}
        stats[k] = dict(median=m, p10=p10, p90=p90, status=s)
        bad = [q for q, v in s.items() if v == "fail"]
        if bad: fails.append(f"{k} {'/'.join(bad)} outside WARN band (median {m:.3g}, p10 {p10:.3g}, p90 {p90:.3g})")
        elif any(v == "warn" for v in s.values()): warns.append(f"{k} leaves PASS band ({', '.join(q for q, v in s.items() if v == 'warn')}; median {m:.3g}, p10 {p10:.3g}, p90 {p90:.3g})")
    st = "fail" if fails else "warn" if warns else "pass"
    why = [("; ".join(fails + warns) if (fails or warns) else "all requirements hold inside PASS bands") +
           f"; {n} perturbed eps, seeds {seeds[0]}..{seeds[-1]}; {PROV}"]
    vals = dict(n=n, contact_frac=fc, start_direction_pass_frac=fsd, lead_foot_plant_pass_frac=ffoot, shot=stats, perturb=perturb, seeds=list(seeds))
    ref = (f"Orchestrator-approved robustness gate 2026-10-19 ({PROV}): contact >={REQ_CONTACT:.0%}, start_direction PASS >={REQ_SD:.0%}, lead_foot_plant PASS >={REQ_FOOT:.0%}, "
           "shot median and p10/p90 inside WARN band; WARN if any leaves PASS band. Magnitudes: joints +/-1.5 deg, +/-0.05 rad/s (ours); ball +/-1 cm (env ball_tol_m); "
           + friction_desc(perturb))
    return dict(status=st, passed=(st == "pass"), values=vals, why=why, ref=ref, tag="derived")
