"""v5 soft-reward scaffolding (Stage 0: terms exist, are unit-testable on a recorded rollout, NOT tuned, NOT used for training yet).

All weights are untuned guesses. Priors are SOFT: capped per term, summed prior weight <= PRIOR_CAP (0.2) at the start and annealed to <= 0.05;
they never gate. Public numbers only: docs/SPEED_GAP_100_120_SPEC.md (Data Agent; interpolated/extrapolated, unverified) and plan section 5.
Private reference data (Mason clips) is NOT referenced here; `private_prior_hook` is a placeholder that must stay None in anything committed.
"""
import math
import numpy as np

# peak segment angular speeds, deg/s, ~100 mph interpolated (spec; unverified): pelvis, thorax, lead arm, club
TARGET_100 = dict(pelvis=442.0, thorax=665.0, lead_arm=886.0, club=2054.0)
TARGET_120 = dict(pelvis=519.0, thorax=803.0, lead_arm=1097.0, club=2500.0)   # extrapolated
PEAK_W, PEAK_SCALE, OVERSHOOT, PEAK_CLIP = 0.5, 0.15, 0.25, (-4.0, 0.0)
PRE_IMPACT_S = dict(pelvis=0.087, thorax=0.068, lead_arm=0.065, club=0.0)       # pros peak this long before impact (spec)
MIN_GAP_S = 0.005
XFACTOR_WINDOW_DEG = (54.0, 62.0)                                              # kseq-v2 (public: Madrid 61, Meister 56, Kwon 59; 54-62 at 100-110 mph)
PRIOR_CAP_START, PRIOR_CAP_END = 0.20, 0.05


def prior_cap(progress):
    """Anneal the total weight of all motion-prior-like terms from 0.20 to 0.05 as training progress goes 0 -> 1."""
    progress = min(max(progress, 0.0), 1.0)
    return PRIOR_CAP_START + (PRIOR_CAP_END - PRIOR_CAP_START) * progress


def peak_speed_term(peaks_degs, targets=TARGET_100):
    """Shortfall counts fully, overshoot at 0.25x, relative to a 15% scale; per segment w=0.5; clipped to [-4,0] (spec)."""
    tot = 0.0
    for k, tgt in targets.items():
        rel = (peaks_degs[k] - tgt) / (PEAK_SCALE * tgt)
        pen = -rel if rel < 0 else OVERSHOOT * rel
        tot += -PEAK_W * (pen if rel < 0 else pen)
    return float(np.clip(tot, *PEAK_CLIP))


def sequence_term(t_peak, t_impact, pelvis_slows_before_impact):
    """1/3 per adjacent pair peaking in order pelvis->thorax->lead_arm->club with >= 5 ms gap, +0.5 if the pelvis slows before impact."""
    order = ["pelvis", "thorax", "lead_arm", "club"]
    ok = sum(1 for a, b in zip(order[:-1], order[1:]) if t_peak[b] - t_peak[a] >= MIN_GAP_S)
    return ok / 3.0 + (0.5 if pelvis_slows_before_impact else 0.0)


def xfactor_term(xf_deg_max, thorax_speed_rises_after):
    """Window reward for peak pelvis-thorax separation; requires thorax speed to rise afterward so it cannot be farmed by standing twisted."""
    lo, hi = XFACTOR_WINDOW_DEG
    if not thorax_speed_rises_after: return 0.0
    if lo <= xf_deg_max <= hi: return 1.0
    d = (lo - xf_deg_max) if xf_deg_max < lo else (xf_deg_max - hi)
    return max(0.0, 1.0 - d / 20.0)


def lag_term(t_peak, t_impact, sigma=0.04):
    """SOFT: Gaussian (sigma 40 ms, so a 20 ms control step does not matter) on the pre-impact peak lags pelvis/thorax/lead_arm vs kseq-v2 targets 87/68/65 ms. Mean in [0,1]."""
    return float(np.mean([math.exp(-0.5 * (((t_impact - t_peak[k]) - v) / sigma) ** 2) for k, v in PRE_IMPACT_S.items() if k != "club"]))


def weight_shift_term(lead_share_top, lead_share_impact):
    """Lead-foot share of vertical GRF should rise from the top of the backswing to impact. [guess: ~60-80% lead at impact, not sourced]"""
    return float(np.clip((lead_share_impact - lead_share_top) / 0.4, 0.0, 1.0))


def ballflight_term(shot, target_carry_m=140.0):
    """Terminal ball-flight terms from a golfphys ShotResult-like dict/obj. Carry is NO-ROLL metres. Windows per plan section 5.1 (driver, tier-labelled)."""
    g = (lambda k: getattr(shot, k) if hasattr(shot, k) else shot[k])
    carry = min(g("carry_m") / target_carry_m, 1.0)
    launch = 1.0 if 9 <= g("launch_deg") <= 13 else max(0.0, 1 - min(abs(g("launch_deg") - 9), abs(g("launch_deg") - 13)) / 6)
    spin = 1.0 if 2000 <= g("spin_rpm") <= 3000 else max(0.0, 1 - min(abs(g("spin_rpm") - 2000), abs(g("spin_rpm") - 3000)) / 1500)
    smash = 1.0 if 1.40 <= g("smash") <= 1.50 else max(0.0, 1 - min(abs(g("smash") - 1.40), abs(g("smash") - 1.50)) / 0.3)
    lat = abs(g("lateral_carry_m"))
    lat_pen = 0.0 if lat <= 1.5 else min(((lat - 1.5) / 1.23) ** 2, 4.0)
    return dict(carry=carry, launch=launch, spin=spin, smash=smash, lateral_pen=-lat_pen)


def episode_terms(log, shot=None, progress=0.0, stage="A", targets=TARGET_100):
    """log: dict of arrays sampled every 5 ms: t, pelvis, thorax, lead_arm, club (deg/s speeds), xfactor_deg, lead_share, t_impact (or None).
    Returns dict of terms and the capped/annealed prior total. Stage A/B: prior terms are zero (plan section 6: sequence/X-factor weights 0 in stage A)."""
    t = np.asarray(log["t"]); ti = log.get("t_impact")
    out = {}
    if ti is None: ti = t[-1]
    pre = t <= ti
    peaks = {k: float(np.max(np.asarray(log[k])[pre])) for k in TARGET_100}
    tp = {k: float(t[pre][int(np.argmax(np.asarray(log[k])[pre]))]) for k in TARGET_100}
    pel = np.asarray(log["pelvis"])[pre]; slows = bool(pel[-1] < 0.9 * pel.max()) if len(pel) else False
    xf = np.asarray(log["xfactor_deg"])[pre]; th = np.asarray(log["thorax"])[pre]
    i_xf = int(np.argmax(np.abs(xf))) if len(xf) else 0
    rises = bool(len(th) and th[i_xf:].max() > 1.2 * th[i_xf]) if len(xf) else False
    ls = np.asarray(log["lead_share"])[pre]
    raw = dict(peak=peak_speed_term(peaks, targets), sequence=sequence_term(tp, ti, slows),
               lag=lag_term(tp, ti), xfactor=xfactor_term(float(np.abs(xf).max()) if len(xf) else 0.0, rises),
               weight_shift=weight_shift_term(float(ls[i_xf]) if len(ls) else 0.0, float(ls[-1]) if len(ls) else 0.0))
    out["raw_prior_terms"] = raw; out["peaks_degs"] = peaks; out["t_peak_before_impact_s"] = {k: ti - v for k, v in tp.items()}
    scale = {"lag": 1.0, "peak": 1.0 / 4.0, "sequence": 1.0 / 1.5, "xfactor": 1.0, "weight_shift": 1.0}   # normalise each to <= 1 in magnitude
    active = stage.upper() in ("C", "D")
    tot = sum(raw[k] * scale[k] for k in raw) / len(raw) if active else 0.0
    out["prior_total"] = float(np.clip(tot, -prior_cap(progress), prior_cap(progress)))
    out["prior_cap"] = prior_cap(progress)
    if shot is not None: out["ballflight"] = ballflight_term(shot)
    return out


private_prior_hook = None   # must stay None in committed code; local-only experiments may set it and must never commit its inputs
