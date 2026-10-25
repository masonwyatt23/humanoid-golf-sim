"""Generate data/references/public_joint_trajectories_110plus.json.

Public-only reference joint-angle trajectories for a 110+ mph driver swing, normalised by time-to-impact
(t = 0 at impact, negative before). SYNTHETIC INTERPOLATION: published sources give keyframe angles, peak
angular speeds and peak timings, never full curves. Each channel is built as

    angle(t) = angle_top + integral of a speed profile omega(t),

where omega(t) is a shape-preserving PCHIP through: 0 at the top of backswing, a power-law ramp
P*s**k up to the cited peak speed P at the cited peak time, then a PCHIP tail to the speed at impact.
The ramp exponent k is solved (bisection) so the integral equals the cited top->impact angle change exactly.
Angles at top and impact are therefore the cited keyframes; peak speed and peak time are the cited values
unless a channel is reported as infeasible (then P is reduced and flagged).

Inputs are numbers printed in published open papers (see SOURCES). No Instagram/personal swing data and no
CMU / MultiSense / AMASS / GolfDB values are used. Re-running reproduces the JSON byte-for-byte.

    python scripts/gen_public_joint_trajectories_110plus.py
"""
import json
import math
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "references" / "public_joint_trajectories_110plus.json"

MPH_TO_MS = 0.44704
T_GRID = np.round(np.arange(-0.30, 0.10 + 1e-9, 0.01), 2)
PHASE_N = 101
POST_IMPACT_TAU_S = 0.05  # ASSUMED exponential decay of speed after impact (no published curve)
SD_TIMING_S = 0.026  # Madrid 2020 downswing-duration SD (26 ms), used as time-alignment uncertainty

SOURCES = {
    "madrid2020": "Madrid, Avalos, Levine, Tuttle, Becker, Kwon. Appl Sci 10(17):5728 (2020), open access CC BY. 66 skilled males, driver CHS 110.4+-4.8 mph, 500 Hz optical (values via data/references/kinematic_sequence_torque_reference_v2.json, tag fetched-full)",
    "cheetham2008": "Cheetham PJ, Rose GA, Hinrichs RN, Neal RJ, Mottram RE, Hurrion PD, Vint PF. Science and Golf V, 2008, 30-36. 19 PGA tour pros, driver, mean CHS 109 mph, 240 Hz electromagnetic (peak-timing values via kinematic_sequence_torque_reference.json)",
    "cheetham2014": "Cheetham PJ. Doctoral dissertation, Arizona State University, Aug 2014 (philcheetham.com/media/Phillip-Cheetham-Doctoral-Dissertation-2014.pdf). 94 PGA/European tour pros, driver, mean CHS 48.4 m/s = 108.3 mph, 240 Hz electromagnetic; Tables 8-9, Study 2 text. Full text read",
    "zheng2008a": "Zheng N, Barrentine SW, Fleisig GS, Andrews JR. Int J Sports Med 29(6):487-493 (2008). 18 professional males, driver, 240 Hz optical; CHS not reported. Abstract read (trunk 60+-7 deg at top); remaining top/impact/timing values are SECONDARY, read from lecture notes (Lehman, MSKPlus course, Mar 2012, thebodymechanic.ca) quoting the paper, not checked against the primary table",
    "zheng2008b": "Zheng N, Barrentine SW, Fleisig GS, Andrews JR. Int J Sports Med 29:965-970 (2008). 25 PGA + 25 LPGA pros; abstract read: pelvis orientation at top PGA 42+-7 deg, pelvis rotation at impact PGA -42+-12 deg (their sign convention)",
    "kseq_v2_derived": "data/references/kinematic_sequence_torque_reference_v2.json 'derived': Madrid within-group slopes (deg/s per m/s) pelvis 13.2, thorax 13.83; downswing-duration slopes -5.96 (within-group Madrid) and -2.5 (between-group Bourgain 2020) ms per m/s; regression-diluted lower bounds, extrapolation above ~116 mph unsupported",
}

# --- keyframes -------------------------------------------------------------------------------------
# RH convention. Rotation: + = toward target (open), backswing negative. Others: raw published angle (deg).
# speed class of every published value is given in 'speed_class_mph' (CHS of the source group; None = not reported).
def kf(name, t_phase, value, sd, src, n, speed, how, note=""):
    return dict(keyframe=name, phase=t_phase, value_deg=value, sd_deg=sd, citation=src, n=n,
                speed_class_mph=speed, tag=how, note=note)


CH = {}

CH["pelvis_rotation"] = dict(
    description="Pelvis rotation about the vertical axis relative to the target line; + toward target (open), backswing negative (RH)",
    kind="rotation",
    keyframes=[
        kf("top", 0.0, -42.0, 7.0, "zheng2008b", 25, None, "measured-abstract",
           "PGA pelvis 'orientation' at peak of backswing, 42+-7 deg; sign taken as closed (away from target) per HANDEDNESS.md convention; CHS not reported"),
        kf("impact", 1.0, 41.0, 9.0, "cheetham2014", 94, 108.3, "measured-full-text",
           "pelvis open 41+-9 deg at impact (Table 8); Hi-HTV subgroup 37+-6, Lo-HTV 43+-7 (Table 9). Cross-check: Zheng PGA 42+-12 magnitude; McTeigue 32; Horan male 44 (as tabulated in Cheetham 2014 Table 10, secondary)"),
    ],
    peak_speed=dict(value_deg_s=394.0, sd=62.0, anchor_mph=110.4, citation="madrid2020", tag="measured (on-plane hip line, not 3-axis resultant)",
                    scaling="madrid_slope", slope_deg_s_per_m_s=13.2,
                    alt_value="Cheetham 2008 3-axis resultant pelvis peak 477 deg/s at 109 mph; kseq-v2 two-group fit 482 (110) / 519 (120) / 565 (132)"),
    peak_time=dict(kind="ms_before_impact", value=-87.0, sd_ms=18.0, citation="madrid2020", note="hip-line peak -87+-18 ms; Cheetham 2008 pelvis -87 ms (SD 19) agrees; held constant across speed (ASSUMED)"),
    speed_at_impact=dict(value_deg_s=262.0, sd=63.0, citation="madrid2020", tag="measured", scaling="ratio_to_peak"),
    confidence="medium-high at impact (n=94 tour pros), medium at top (n=25, magnitude/sign by convention); curve between is synthetic",
    confidence_rank=2,
)

# thorax: top derived = pelvis_top - X-factor_top (Madrid 61+-9), impact measured
CH["thorax_rotation"] = dict(
    description="Thorax (upper torso) rotation about the vertical axis relative to the target line; + toward target (open), backswing negative (RH)",
    kind="rotation",
    keyframes=[
        kf("top", 0.0, -103.0, 11.4, "madrid2020+zheng2008b", "66+25", None, "derived",
           "DERIVED: pelvis top (-42, Zheng PGA) minus X-factor at top (61+-9, Madrid 2020 driver CHS 110.4, functional-swing-plane method). SD = sqrt(7^2+9^2) assuming independence. Mixes two studies/methods; compare Zheng 'trunk rotation 60+-7' (probably upper torso relative to pelvis, i.e. X-factor-like, UNVERIFIED) and lecture-note summary 'thorax ~90 deg' (secondary, method dependent)"),
        kf("impact", 1.0, 27.0, 9.0, "cheetham2014", 94, 108.3, "measured-full-text",
           "thorax open 27+-9 deg at impact (Table 8); Hi-HTV 23+-7, Lo-HTV 31+-9 (Table 9); Cheetham 2014 Table 10 secondary: McTeigue 26, Myers 20-25, Horan 26-29"),
    ],
    peak_speed=dict(value_deg_s=711.0, sd=63.0, anchor_mph=110.4, citation="madrid2020", tag="measured (on-plane shoulder line)",
                    scaling="madrid_slope", slope_deg_s_per_m_s=13.83,
                    alt_value="Cheetham 2008 thorax peak 727 deg/s at 109 mph; kseq-v2 two-group fit 737 (110) / 803 (120) / 886 (132)"),
    peak_time=dict(kind="ms_before_impact", value=-84.0, sd_ms=25.0, citation="madrid2020", note="shoulder-line peak -84+-25 ms; Cheetham 2008 thorax -68 ms (SD 14) is later; Madrid used; held constant (ASSUMED)"),
    speed_at_impact=dict(value_deg_s=610.0, sd=65.0, citation="madrid2020", tag="measured", scaling="ratio_to_peak"),
    confidence="medium-low: impact from n=94 tour pros, top is a derived mix of two studies/methods (absolute thorax top angle method-dependent by tens of degrees)",
    confidence_rank=3,
)

ZH_NOTE = "Zheng 2008a pro group via secondary lecture notes (top = 'peak of backswing'); angle definition not verified against primary table; CHS not reported"

def zheng_channel(desc, top, imp, p_speed, p_frac, role, mapping_note, rank, imp_ratio, cite_extra=""):
    return dict(
        description=desc,
        kind="angle",
        keyframes=[
            kf("top", 0.0, top, None, "zheng2008a", 18, None, "measured-secondary", ZH_NOTE),
            kf("impact", 1.0, imp, None, "zheng2008a", 18, None, "measured-secondary", ZH_NOTE + cite_extra),
        ],
        peak_speed=dict(value_deg_s=p_speed, sd=None, anchor_mph=109.0, citation="zheng2008a", tag="measured-secondary",
                        scaling="linear_in_chs_assumed", slope_deg_s_per_m_s=None,
                        alt_value="Zheng pro CHS not reported; repo precedent (kinematic_sequence_torque_reference.json) assumes 109 mph for linear scaling"),
        peak_time=dict(kind="fraction_of_downswing", value=p_frac, sd_ms=None, citation="zheng2008a",
                       note="timing of peak speed as fraction of downswing (100% = impact), secondary notes"),
        speed_at_impact=dict(value_deg_s=None, sd=None, citation="none", tag="ASSUMED: ratio to peak = %.2f (no published value)" % imp_ratio,
                             scaling="ratio_to_peak", ratio=imp_ratio),
        role=role, mapping_note=mapping_note,
        confidence="low: single secondary source (n=18 pros, CHS unreported), no SDs retrieved, angle definition unverified",
        confidence_rank=rank,
    )

CH["lead_arm_to_trunk"] = zheng_channel(
    "Lead (target-side) upper-arm elevation relative to the trunk (Zheng 'left arm to trunk' for a RH golfer), degrees",
    90.0, 35.0, 355.0, 0.69, "lead", "NO direct env joint: env left_shoulder_pitch/roll (lead arm) are in the env's own frame. Mapping UNVERIFIED; use change (-55 deg top->impact) not absolute values", 4, 0.85)
CH["trail_arm_to_trunk"] = zheng_channel(
    "Trail upper-arm elevation relative to the trunk (Zheng 'right arm to trunk' for a RH golfer), degrees",
    43.0, 23.0, 248.0, 0.52, "trail", "env right_shoulder_pitch/roll = trail arm (HANDEDNESS.md). Absolute mapping UNVERIFIED", 5, 0.50)
CH["lead_elbow_flexion"] = zheng_channel(
    "Lead elbow flexion angle (0 = straight), degrees (Zheng 'left elbow flexion'); lecture-note value 58 deg at top is surprisingly large and should be treated with caution",
    58.0, 34.0, 235.0, 0.83, "lead", "env left_elbow is UNACTUATED in the simple env (env_joint_mapping note); flexion sign convention env vs Zheng unverified", 5, 0.85)
CH["trail_elbow_flexion"] = zheng_channel(
    "Trail elbow flexion angle (0 = straight), degrees (Zheng 'right elbow flexion')",
    130.0, 40.0, 854.0, 0.99, "trail", "env right_elbow range 0..150 deg (humanoid_golf_v4_power.xml). Convention match assumed (0 = straight), UNVERIFIED. Zheng peak right-elbow extension speed 854+-150 deg/s is in the abstract (measured)", 4, 0.95)
CH["lead_wrist_set_angle"] = zheng_channel(
    "Lead wrist 'set' angle = interior angle between lead forearm and club shaft (180 = in line), degrees; 94 at top (cocked) to 165 at impact",
    94.0, 165.0, 1085.0, 0.88, "lead", "env w=0 is a 90 deg L; repo note: interior angle = 90 - w_deg, so top 94 -> w -4 deg, impact 165 -> w -75 deg. CAUTION: the env's own ball-contact solution is w ~ 0.173 - 0.564*elbow_rad (about -0.1 rad), i.e. env interior ~96 deg at contact, because env arm/club geometry is stylised. Absolute values do NOT map; only the release magnitude (+71 deg) and timing are transferable. UNVERIFIED",
    3, 0.85,
    cite_extra=" Cross-check: Cheetham 2014 (n=94 tour pros, driver, 108.3 mph) mean lead forearm-to-club angle at impact 161 deg (19 deg short of straight), lead wrist ~2 deg flexed at impact; Zheng peak left-wrist speed 1085+-338 deg/s is in the abstract (measured)")
CH["trail_wrist_angle"] = zheng_channel(
    "Trail wrist angle (Zheng 'right wrist', forearm-to-club interior angle assumed), degrees; 75 at top to 118 at impact",
    75.0, 118.0, 1183.0, 0.95, "trail", "env right_wrist = trail (club-hand) wrist, same 90-deg-L zero. Zheng 'right wrist' definition not verified to be forearm-to-club interior angle. Absolute mapping UNVERIFIED; peak right-wrist speed 1183+-299 deg/s is in the abstract (measured)", 4, 0.95)

# speed classes
CLASSES = [110, 120, 130]
EXTRAPOLATED = {110: False, 120: True, 130: True}
CHS_ANCHOR_MS = 110.4 * MPH_TO_MS
T_ANCHOR = 0.253
SLOPE_BETWEEN = -0.0025  # s per m/s (Bourgain-based, kseq-v2)
SLOPE_WITHIN = -0.00596  # s per m/s (Madrid within group)


def t_down(mph, slope=SLOPE_BETWEEN):
    return T_ANCHOR + slope * (mph * MPH_TO_MS - CHS_ANCHOR_MS)


def peak_speed(ch, mph):
    ps = ch["peak_speed"]
    v = mph * MPH_TO_MS
    if ps["scaling"] == "madrid_slope":
        return ps["value_deg_s"] + ps["slope_deg_s_per_m_s"] * (v - ps["anchor_mph"] * MPH_TO_MS)
    return ps["value_deg_s"] * mph / ps["anchor_mph"]


def build_speed(T, tp, P, w_bi, k, post=False):
    """Speed knots on s in [0,1] over [top, peak] (ramp P*s^k) and a tail peak -> impact. t measured from top."""
    ss = np.linspace(0, 1, 9)
    ramp_t = ss * tp
    ramp_w = P * ss ** k
    tail_s = np.linspace(0, 1, 6)[1:]
    tail_t = tp + tail_s * (T - tp)
    # tail: smooth monotone from P to w_bi (smoothstep shape keeps zero slope at the peak)
    tail_w = P + (w_bi - P) * (3 * tail_s ** 2 - 2 * tail_s ** 3)
    return PchipInterpolator(np.r_[ramp_t, tail_t], np.r_[ramp_w, tail_w])


def area(T, tp, P, w_bi, k):
    f = build_speed(T, tp, P, w_bi, k)
    x = np.linspace(0, T, 4001)
    return np.trapezoid(f(x), x)


def solve_channel(ch, mph, T):
    a0 = ch["keyframes"][0]["value_deg"]
    a1 = ch["keyframes"][1]["value_deg"]
    d = abs(a1 - a0)
    sgn = 1.0 if a1 >= a0 else -1.0
    P0 = peak_speed(ch, mph)
    pt = ch["peak_time"]
    if pt["kind"] == "ms_before_impact":
        tp = T + pt["value"] / 1000.0
    else:
        tp = pt["value"] * T
    si = ch["speed_at_impact"]
    if si["scaling"] == "ratio_to_peak":
        ratio = si["ratio"] if si.get("ratio") is not None else si["value_deg_s"] / ch["peak_speed"]["value_deg_s"]
    ratio0 = ratio
    P = P0
    flags = []
    kmin, kmax = 0.05, 12.0

    def feasible(P_, r_):
        lo = area(T, tp, P_, r_ * P_, kmax)
        hi = area(T, tp, P_, r_ * P_, kmin)
        return lo, hi

    lo, hi = feasible(P, ratio)
    if d < lo:  # peak speed + tail would move the joint too far: lower speed at impact first
        for r in (0.6, 0.4, 0.2, 0.0):
            lo, hi = feasible(P, r)
            if lo <= d <= hi:
                ratio = r
                flags.append("speed_at_impact_ratio_reduced_to_%.2f_to_fit_cited_angle_change" % r)
                break
    if not (lo <= d <= hi):
        # last resort: rescale peak speed so the cited angle change is met; the cited peak is then NOT reproduced
        target = d
        lo_s, hi_s = 0.02, 1.5
        for _ in range(60):
            m = 0.5 * (lo_s + hi_s)
            a_ = area(T, tp, P0 * m, ratio * P0 * m, 1.0)
            if a_ > target:
                hi_s = m
            else:
                lo_s = m
        P = P0 * 0.5 * (lo_s + hi_s)
        k = 1.0
        flags.append("PEAK_SPEED_NOT_REPRODUCED: cited peak %.0f deg/s is inconsistent with cited angle change %.0f deg over %.0f ms; peak scaled by %.2f" % (P0, d, T * 1000, P / P0))
    else:
        l, h = kmin, kmax
        for _ in range(80):
            m = math.sqrt(l * h)
            if area(T, tp, P, ratio * P, m) > d:
                l = m
            else:
                h = m
        k = math.sqrt(l * h)
    w_bi = ratio * P
    return dict(a0=a0, a1=a1, sgn=sgn, T=T, tp=tp, P=P, P_cited_scaled=P0, w_bi=w_bi, ratio=ratio, ratio_default=ratio0, k=k, flags=flags)


def evaluate(sol, t):
    """angle at time t (s, impact = 0)."""
    T, tp = sol["T"], sol["tp"]
    f = build_speed(T, tp, sol["P"], sol["w_bi"], sol["k"])
    x = np.linspace(0, T, 4001)
    cum = np.concatenate([[0], np.cumsum(0.5 * (f(x)[1:] + f(x)[:-1]) * np.diff(x))])
    sol["quadrature_residual_deg"] = float(cum[-1] - abs(sol["a1"] - sol["a0"]))
    cum *= (abs(sol["a1"] - sol["a0"]) / cum[-1])  # remove quadrature residue
    ang = np.empty_like(t, dtype=float)
    omega = np.empty_like(t, dtype=float)
    for i, ti in enumerate(t):
        tau = ti + T  # time since top
        if tau <= 0:
            ang[i], omega[i] = sol["a0"], 0.0
        elif tau <= T:
            ang[i] = sol["a0"] + sol["sgn"] * np.interp(tau, x, cum)
            omega[i] = sol["sgn"] * float(f(tau))
        else:
            dt_ = ti
            ang[i] = sol["a1"] + sol["sgn"] * sol["w_bi"] * POST_IMPACT_TAU_S * (1 - math.exp(-dt_ / POST_IMPACT_TAU_S))
            omega[i] = sol["sgn"] * sol["w_bi"] * math.exp(-dt_ / POST_IMPACT_TAU_S)
    return ang, omega


def sd_curve(ch, t, T):
    k0, k1 = ch["keyframes"]
    if k0["sd_deg"] is None or k1["sd_deg"] is None:
        return None
    ph = np.clip((t + T) / T, 0, 1)
    return k0["sd_deg"] + (k1["sd_deg"] - k0["sd_deg"]) * ph


def r(x, n=3):
    return None if x is None else round(float(x), n)


def build():
    out = {
        "_meta": {
            "title": "Public-only reference joint-angle trajectories for a 110+ mph driver swing (synthetic interpolation between published keyframes)",
            "version": 1,
            "generated_by": "scripts/gen_public_joint_trajectories_110plus.py",
            "contains_instagram_or_mason_derived_data": False,
            "derived_from_cmu_multisense_amass_golfdb": False,
            "synthetic_interpolation": True,
            "status": "SYNTHETIC reference built from published keyframes, peak speeds and peak timings. NOT measured curves. No published source gives a full time-normalised curve for a 110+ mph group. Values at 120 and 130 mph are extrapolated (no published joint-angle study above ~112 mph with angles).",
            "right_handed_convention": "Rotation channels: + = toward target (open), backswing negative (RH). Time t in seconds, t = 0 at ball impact, negative before. phase = (t + T_downswing) / T_downswing: 0 at top of backswing, 1 at impact.",
            "left_handed_mirror_rule": {
                "summary": "Express everything in golfer ROLES (trail/lead), not physical left/right (docs/HANDEDNESS.md). Rotation about the vertical axis (pelvis_rotation, thorax_rotation, x_factor; env chest_yaw / pelvis yaw): NEGATE for a left-hander (backswing positive, impact negative) if the env's own handedness flip is NOT already applied; ResidualGolfEnv already multiplies the chest_yaw target by -1 for handedness='left', so feed this file's RH values to the env's handedness layer and do not negate twice. Sagittal/planar angles (elbow flexion, wrist set angle, arm-to-trunk elevation): NO sign change. Roles: env right_* = TRAIL arm, left_* = LEAD arm for both handednesses. +y is the golfer's left (RH) / handedness-mirrored lateral in the env.",
                "status": "rule restated from docs/HANDEDNESS.md and data/mirror_references.py (negate pelvis/thorax/x-factor; planar flexion invariant). Not tested against this file. UNVERIFIED for env roll joints.",
            },
            "env_mapping_summary": {
                "pelvis_rotation": "G1 env pelvis_yaw_joint; NO pelvis yaw in the simple env (v3/v4_power) -- use as thorax-minus-pelvis only if the Trainer's env has it",
                "thorax_rotation": "simple env chest_yaw (+-45 deg v3, +-60 deg v4_power); G1 waist_yaw_joint. NOTE: -103 deg thorax at top exceeds chest_yaw range +-60 deg; env chest_yaw is likely pelvis-relative (an X-factor-like quantity), so consider x_factor channel instead (UNVERIFIED)",
                "x_factor": "pelvis-relative thorax rotation = the likely match for env chest_yaw if the pelvis is fixed (UNVERIFIED)",
                "lead_arm_to_trunk / trail_arm_to_trunk": "env shoulder_pitch/roll; no verified mapping",
                "elbows": "env right_elbow (trail, actuated), left_elbow (lead, unactuated in simple env)",
                "wrists": "env right_wrist (trail hinge); no lead wrist in simple env. w = 90 - interior_angle_deg (repo note), absolute values inconsistent with env contact solution",
            },
            "sampling_grid": {"t_start_s": -0.30, "t_end_s": 0.10, "dt_s": 0.01, "n": int(len(T_GRID)),
                              "note": "t < -T_downswing is the end of the backswing: angle HELD at the top keyframe (extrapolation, not published). t > 0 is follow-through: speed decays exponentially with tau=0.05 s (ASSUMED). Published support exists ONLY for -T_downswing <= t <= 0."},
            "speed_classes_mph": CLASSES,
            "speed_scaling_rule": {
                "angles": "Top and impact keyframe angles are held FIXED across speed classes (ASSUMED). Basis: X-factor is not correlated with club speed within homogeneous skilled groups (Kwon 2013 abstract, kseq-v2 d_kwon_no_correlation; Parker 2018 beta -0.24), but this is not evidence that every joint angle is speed-invariant.",
                "downswing_duration": "T(v) = 0.253 s - 0.0025 s per (m/s) * (v - 49.35 m/s) (between-group Bourgain-based slope; default). Alternative within-group Madrid slope -0.00596 s per m/s gives shorter T (see 'downswing_duration_s_alt_within'). Anchor 253+-26 ms at 110.4 mph (Madrid 2020). Cite: kseq-v2 'downswing_duration_by_chs'. Above ~116 mph UNSUPPORTED extrapolation.",
                "pelvis_thorax_peak_speed": "Madrid anchor at 110.4 mph + within-group slope (13.2 and 13.83 deg/s per m/s; regression-diluted lower bounds; kseq-v2 derived). Extrapolated above ~116 mph.",
                "arm_elbow_wrist_peak_speed": "Linear in club speed from Zheng pro values with ASSUMED reference 109 mph (CHS unreported; same assumption as kinematic_sequence_torque_reference.json). ASSUMED.",
                "peak_timing": "pelvis/thorax: ms before impact held constant (ASSUMED); arm/elbow/wrist: fixed fraction of downswing (Zheng, secondary).",
                "speed_at_impact": "pelvis/thorax: ratio to peak from Madrid held constant (ASSUMED). Arm/elbow/wrist: ASSUMED ratios (0.5-0.95), no published values.",
            },
            "interpolation": {
                "method": "angle = angle_top + integral of PCHIP speed profile; speed ramp P*s^k to the cited peak at the cited peak time, smoothstep tail to the speed at impact; k solved so top->impact change equals the cited keyframes",
                "kind": "monotone (speed >= 0 so angle is monotone between top and impact)",
                "synthetic_interpolation": True,
                "why_not_plain_pchip": "plain PCHIP through only top/impact keyframes would give a near-linear sweep with peak speed ~ mean speed (e.g. ~330 deg/s for the pelvis vs cited peak 394), which contradicts the published kinematic sequence",
            },
            "tolerance_bands": {
                "published_sd_channels": ["pelvis_rotation", "thorax_rotation", "x_factor"],
                "sd_angle_deg": "linear in phase between keyframe SDs (derived; SDs are between-subject at the keyframe, not along the curve)",
                "timing_term": "band_total_deg = sqrt(sd_angle^2 + (0.026 s * |omega|)^2); 0.026 s = Madrid downswing-duration SD, a time-alignment allowance (derived)",
                "other_channels": "No published SD retrieved: sd_deg is null and band is null. Use tolerance_deg_recommended (ASSUMED).",
            },
            "recommended_soft_reward_usage": {
                "status": "SUGGESTION, not tuned or tested in any training run",
                "window": "downswing only: -T_downswing <= t <= -0.01 s (phase 0..~0.96). Weight 0 before the top and after impact (no published support).",
                "form": "r_t = sum_c w_c * exp(-0.5 * (err_c / tol_c)^2), err_c = env_angle_c(t) - ref_c(t); use rotation channels first",
                "total_weight": "low: keep the whole prior <= ~5% of the per-step reward (suggested 0.02-0.05), annealed to 0 once speed at impact and the sequence reward are met, so the prior can not override ball-flight rewards",
                "per_channel_weights_and_tolerance_deg": {
                    "pelvis_rotation": {"w": 0.25, "tol_deg": "max(band_total, 12)"},
                    "thorax_rotation": {"w": 0.20, "tol_deg": "max(band_total, 15) -- or use x_factor instead"},
                    "x_factor": {"w": 0.25, "tol_deg": "max(band_total, 12)"},
                    "lead_arm_to_trunk": {"w": 0.10, "tol_deg": 20},
                    "trail_arm_to_trunk": {"w": 0.0, "tol_deg": 20, "note": "start at 0 (weakest-supported)"},
                    "lead_elbow_flexion": {"w": 0.0, "tol_deg": 20, "note": "env lead elbow is unactuated"},
                    "trail_elbow_flexion": {"w": 0.05, "tol_deg": 25},
                    "lead_wrist_set_angle": {"w": 0.0, "tol_deg": 20, "note": "use release magnitude/timing only; absolute value does not map to env w"},
                    "trail_wrist_angle": {"w": 0.0, "tol_deg": 20, "note": "same caveat as lead wrist"},
                },
                "use_timing_not_absolutes": "For elbow/wrist, prefer rewarding the phase of release (peak-speed time as fraction of downswing) and the change in angle, because env contact geometry fixes absolute values (see lead_wrist_set_angle mapping_note).",
            },
            "license_note": "Numbers are published facts/means cited to their papers; the curves are original constructions by this repo (MIT). Papers are cited, not reproduced; Madrid 2020 is CC BY (attribution given). No third-party data tables are copied wholesale. See docs/PUBLIC_JOINT_TRAJECTORIES_110PLUS.md.",
        },
        "sources": SOURCES,
        "channels": {},
        "derived_checks": {},
    }
    tg = T_GRID
    sols_all = {}
    for mph in CLASSES:
        T = t_down(mph)
        sols = {c: solve_channel(ch, mph, T) for c, ch in CH.items()}
        sols_all[mph] = (T, sols)
    out["_meta"]["downswing_duration_s"] = {str(m): r(sols_all[m][0], 4) for m in CLASSES}
    out["_meta"]["downswing_duration_s_alt_within"] = {str(m): r(t_down(m, SLOPE_WITHIN), 4) for m in CLASSES}
    out["_meta"]["extrapolated_beyond_published_speed_support"] = {str(m): EXTRAPOLATED[m] for m in CLASSES}

    traj = {}
    for c, ch in CH.items():
        entry = {
            "description": ch["description"], "kind": ch["kind"], "unit": "deg",
            "right_handed_sign": "+ toward target (open); backswing negative" if ch["kind"] == "rotation" else "as published (see description)",
            "lh_mirror": "negate" if ch["kind"] == "rotation" else "no sign change",
            "role": ch.get("role"), "env_mapping_note": ch.get("mapping_note"),
            "source_keyframes": ch["keyframes"],
            "peak_speed_published": ch["peak_speed"], "peak_time_published": ch["peak_time"], "speed_at_impact": ch["speed_at_impact"],
            "interpolation": "angle = top + integral of PCHIP speed profile (ramp P*s^k to cited peak, smoothstep tail); see _meta.interpolation",
            "synthetic_interpolation": True,
            "confidence": ch["confidence"], "confidence_rank_1best_5worst": ch["confidence_rank"],
            "tolerance_deg_recommended": None,
            "speed_class_curves": {},
        }
        for mph in CLASSES:
            T, sols = sols_all[mph]
            s = sols[c]
            ang, om = evaluate(s, tg)
            sd = sd_curve(ch, tg, T)
            ph_grid = np.linspace(0, 1, PHASE_N)
            ang_p, om_p = evaluate(s, ph_grid * T - T)
            band = None
            if sd is not None:
                band = np.sqrt(sd ** 2 + (SD_TIMING_S * om) ** 2)
            inside = (tg >= -T - 1e-9) & (tg <= 1e-9)
            entry["speed_class_curves"][str(mph)] = {
                "downswing_duration_s": r(T, 4),
                "peak_speed_used_deg_s": r(abs(s["P"]), 1),
                "peak_time_ms_before_impact": r((s["tp"] - T) * 1000, 1),
                "speed_at_impact_used_deg_s": r(s["w_bi"], 1),
                "ramp_exponent_k": r(s["k"], 3),
                "flags": s["flags"],
                "integral_residual_before_normalisation_deg": r(s.get("quadrature_residual_deg"), 4),
                "t_s": [float(x) for x in tg],
                "angle_deg": [r(x, 3) for x in ang],
                "angular_speed_deg_s": [r(x, 1) for x in om],
                "sd_angle_deg": None if sd is None else [r(x, 2) for x in sd],
                "band_total_deg": None if band is None else [r(x, 2) for x in band],
                "published_support_mask": [bool(x) for x in inside],
                "phase_grid": {"phase": [r(x, 2) for x in ph_grid], "angle_deg": [r(x, 3) for x in ang_p], "angular_speed_deg_s": [r(x, 1) for x in om_p],
                               "time_to_impact_s": [r(x, 4) for x in (ph_grid * T - T)]},
            }
        out["channels"][c] = entry
        traj[c] = entry

    # derived X-factor = thorax - pelvis
    xf = {"description": "X-factor = thorax rotation minus pelvis rotation (derived from the two channels above); + = thorax more toward target (open) than pelvis; in RH convention the top value is negative of the usual positive 'X-factor' magnitude (-61 here = 61 deg of torso-pelvis separation, closed)",
          "kind": "rotation", "unit": "deg", "lh_mirror": "negate", "role": "derived",
          "source_keyframes": [
              kf("top", 0.0, -61.0, 9.0, "madrid2020", 66, 110.4, "measured", "X-factor at top 61+-9 deg (functional swing plane); defines the thorax top keyframe; also max 62+-8"),
              kf("impact", 1.0, None, None, "derived", None, None, "derived", "thorax(27) - pelvis(41) = -14 deg (closed) by construction; Madrid 2020 measured X-factor at impact 9+-8 deg (different sign convention/method; magnitude agreement within 1 SD of Madrid); Meister 2011 5-iron pros 24-33 deg; Chu 2010 12.3+-9.1")],
          "interpolation": "difference of the two integrated channels (not independently interpolated)",
          "synthetic_interpolation": True,
          "confidence": "medium-low: top from Madrid (n=66), impact is a difference of two means from different studies",
          "confidence_rank_1best_5worst": 3,
          "speed_class_curves": {}}
    for mph in CLASSES:
        T = sols_all[mph][0]
        p = traj["pelvis_rotation"]["speed_class_curves"][str(mph)]
        th = traj["thorax_rotation"]["speed_class_curves"][str(mph)]
        a = [r(th["angle_deg"][i] - p["angle_deg"][i], 3) for i in range(len(tg))]
        om = [r(th["angular_speed_deg_s"][i] - p["angular_speed_deg_s"][i], 1) for i in range(len(tg))]
        # X-factor SD: published 9 deg at top (Madrid); at impact RSS of the two impact SDs (9, 9), independence ASSUMED
        ph = np.clip((tg + T) / T, 0, 1)
        sd_x = 9.0 + (math.sqrt(81 + 81) - 9.0) * ph
        band = np.sqrt(sd_x ** 2 + (SD_TIMING_S * np.array(om)) ** 2)
        xf["speed_class_curves"][str(mph)] = {
            "downswing_duration_s": r(T, 4), "t_s": [float(x) for x in tg], "angle_deg": a, "angular_speed_deg_s": om,
            "sd_angle_deg": [r(x, 2) for x in sd_x], "band_total_deg": [r(x, 2) for x in band],
            "published_support_mask": p["published_support_mask"],
            "phase_grid": {"phase": p["phase_grid"]["phase"],
                           "angle_deg": [r(a_ - b_, 3) for a_, b_ in zip(th["phase_grid"]["angle_deg"], p["phase_grid"]["angle_deg"])],
                           "angular_speed_deg_s": [r(a_ - b_, 1) for a_, b_ in zip(th["phase_grid"]["angular_speed_deg_s"], p["phase_grid"]["angular_speed_deg_s"])],
                           "time_to_impact_s": p["phase_grid"]["time_to_impact_s"]}}
    out["channels"]["x_factor"] = xf
    top = xf["speed_class_curves"]["110"]
    i_imp = int(np.argmin(np.abs(tg)))
    out["derived_checks"] = {
        "x_factor_impact_derived_deg_110": top["angle_deg"][i_imp],
        "x_factor_impact_published_madrid": "9 +- 8 deg (magnitude)",
        "pelvis_peak_speed_check": {str(m): {"cited_scaled": r(sols_all[m][1]["pelvis_rotation"]["P_cited_scaled"], 1), "used": r(sols_all[m][1]["pelvis_rotation"]["P"], 1)} for m in CLASSES},
        "thorax_peak_speed_check": {str(m): {"cited_scaled": r(sols_all[m][1]["thorax_rotation"]["P_cited_scaled"], 1), "used": r(sols_all[m][1]["thorax_rotation"]["P"], 1)} for m in CLASSES},
        "channels_with_peak_speed_not_reproduced": sorted({f"{c}@{m}" for m in CLASSES for c, s in sols_all[m][1].items() if any(fl.startswith("PEAK_SPEED_NOT_REPRODUCED") for fl in s["flags"])}),
        "channels_with_reduced_impact_speed": sorted({f"{c}@{m}" for m in CLASSES for c, s in sols_all[m][1].items() if any("ratio_reduced" in fl for fl in s["flags"])}),
        "note": "Peak-timing sequence in the curves follows the published order for pelvis (-87 ms) -> thorax (-84 ms): the 3 ms gap is within published SD (18-25 ms) and contradicts Cheetham 2008 (68 ms for thorax); sequence order is not guaranteed by this file.",
    }
    # per-channel recommended tolerances (assumed)
    for c in out["channels"]:
        out["channels"][c]["tolerance_deg_recommended"] = {"pelvis_rotation": 12, "thorax_rotation": 15, "x_factor": 12}.get(c, 20 if "elbow" not in c else 25)
    return out


def main():
    d = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(d, indent=1) + "\n")
    print("wrote", OUT, OUT.stat().st_size, "bytes")
    for c, e in d["channels"].items():
        for m, cur in e["speed_class_curves"].items():
            print(c, m, cur.get("ramp_exponent_k"), cur.get("peak_speed_used_deg_s"), cur.get("flags"))


if __name__ == "__main__":
    main()
