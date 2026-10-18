"""Realism checks.  check_swing_realism(joint_traces, dt, ...) and check_shot_realism(shot, ...) return
{"overall": "pass|warn|fail", "checks": [ {name, status, value, expected, reason, source, tag, extrapolated}, ... ], "notes": [...]}.
Statuses rank pass < warn < fail; overall = worst.  Checks that cannot run because an input trace is absent are reported as
status "skip" (never silently dropped) and do not affect overall.

joint_traces (all numpy-like 1-D arrays, same length, sampled every dt seconds):
  segment angles (rad, about the swing/yaw axis; unwrapped here):   "pelvis", "thorax", "arm" (lead arm), "club"
  or segment angular speeds (rad/s), which take precedence:        "pelvis_w", "thorax_w", "arm_w", "club_w"
  actuator checks:                                                  "torque:<joint>" (N*m), "qvel:<joint>" (rad/s)
  ground reaction (optional):                                       "grf_lead_vertical_bw" (lead-foot vertical force / body weight)
Everything is published-biomechanics based; see the JSON for tags.  120+ mph rows are extrapolated and flagged as such."""
from __future__ import annotations
import json, math
from functools import lru_cache
from pathlib import Path
import numpy as np

PASS, WARN, FAIL, SKIP = "pass", "warn", "fail", "skip"
_RANK = {SKIP: -1, PASS: 0, WARN: 1, FAIL: 2}
JSON = Path(__file__).resolve().parent.parent / "data/references/realism_thresholds.json"
SEG = ("pelvis", "thorax", "arm", "club")


@lru_cache(maxsize=1)
def load_thresholds(path: str = str(JSON)) -> dict:
    return json.load(open(path))


def _res(name, status, value, expected, reason, thr=None, extrapolated=False):
    return dict(name=name, status=status, value=value, expected=expected, reason=reason,
                source=(thr or {}).get("source"), tag=(thr or {}).get("tag"), extrapolated=bool(extrapolated))


def _overall(checks):
    r = max((_RANK[c["status"]] for c in checks), default=0)
    return {v: k for k, v in _RANK.items()}[max(r, 0)] if r >= 0 else PASS


def _band(x, pass_rng, warn_rng, fail_rng=None):
    """pass inside pass_rng; warn inside warn_rng; fail otherwise (fail_rng, when given, overrides the outer bound of warn)."""
    if pass_rng[0] <= x <= pass_rng[1]:
        return PASS
    outer = fail_rng or warn_rng
    if warn_rng[0] <= x <= warn_rng[1] and outer[0] <= x <= outer[1]:
        return WARN
    return FAIL


# ---------------------------------------------------------------------------------------------- targets
def targets_at_chs(chs_mph: float) -> dict:
    """Interpolated published/derived segment peak speeds (deg/s) at a club speed, with an `extrapolated` flag."""
    th = load_thresholds()["peak_speed"]["rows_by_chs"]["value"]
    xs = [r["chs_mph"] for r in th]
    out = {s: float(np.interp(chs_mph, xs, [r["segment_peak_deg_s"][k] for r in th])) for s, k in
           (("pelvis", "pelvis"), ("thorax", "thorax"), ("arm", "lead_arm"), ("club", "club"))}
    lo, hi = load_thresholds()["measured_chs_range_mph"]["value"]
    out["extrapolated"] = bool(chs_mph < lo - 1e-9 or chs_mph > hi + 1e-9)
    out["chs_mph"] = float(chs_mph)
    return out


def _infer_chs(club_peak_deg_s: float) -> float:
    th = load_thresholds()["peak_speed"]["rows_by_chs"]["value"]
    return float(np.interp(club_peak_deg_s, [r["segment_peak_deg_s"]["club"] for r in th], [r["chs_mph"] for r in th]))


# ---------------------------------------------------------------------------------------------- swing
def _speed_deg_s(jt, seg, dt):
    if f"{seg}_w" in jt:
        return np.abs(np.degrees(np.asarray(jt[f"{seg}_w"], float)))
    if seg in jt:
        a = np.unwrap(np.asarray(jt[seg], float))
        return np.abs(np.degrees(np.gradient(a, dt)))
    return None


def _smooth(x, n=3):
    if len(x) < n + 2:
        return x
    k = np.ones(n) / n
    return np.convolve(np.pad(x, n // 2, mode="edge"), k, mode="valid")


def check_swing_realism(joint_traces: dict, dt: float, chs_mph: float | None = None, impact_idx: int | None = None,
                        tier: str | None = None, thresholds: dict | None = None) -> dict:
    """Kinematic-sequence order/timing, peak speeds vs club speed, X-factor, actuator feasibility and torque/GRF budget.
    chs_mph: club-head speed at impact (mph); if None it is inferred from the club's peak angular speed (reported in notes).
    impact_idx: sample index of impact (default: index of the club's peak speed).  tier: 'stock'|'elite' enables actuator checks."""
    T = thresholds or load_thresholds()
    checks, notes = [], []
    jt = {k: np.asarray(v, float) for k, v in joint_traces.items()}
    n = max((len(v) for v in jt.values()), default=0)
    if n < 5:
        return dict(overall=FAIL, checks=[_res("input", FAIL, n, ">= 5 samples", "traces too short or empty")], notes=notes)
    if not np.all([np.isfinite(v).all() for v in jt.values()]):
        return dict(overall=FAIL, checks=[_res("input", FAIL, None, "finite values", "NaN/inf in a trace")], notes=notes)
    spd = {s: _speed_deg_s(jt, s, dt) for s in SEG}
    spd = {s: (_smooth(v) if v is not None else None) for s, v in spd.items()}
    have_all = all(v is not None for v in spd.values())

    # impact index and window
    club = spd["club"]
    if impact_idx is None:
        impact_idx = int(np.argmax(club)) if club is not None else n - 1
    win0 = max(0, impact_idx - int(round(0.5 / dt)))
    sl = slice(win0, impact_idx + 1)
    notes.append(f"impact_idx={impact_idx} (t={impact_idx * dt:.3f}s); peak window {win0 * dt:.3f}-{impact_idx * dt:.3f}s; sample resolution {dt * 1000:.0f} ms")

    # club speed / targets
    if chs_mph is None and club is not None:
        chs_mph = _infer_chs(float(club[sl].max()))
        notes.append(f"chs_mph inferred from club peak speed: {chs_mph:.1f} mph (inversion of the Cheetham-fit table; pass chs_mph to override)")
    tg = targets_at_chs(chs_mph) if chs_mph else None

    # 1. kinematic sequence order + timing
    if have_all:
        tpk = {s: (win0 + int(np.argmax(spd[s][sl]))) * dt for s in SEG}
        tol = T["sequence"]["tie_tolerance_ms"]["value"] / 1000.0
        order = T["sequence"]["order"]["value"]
        times = [tpk[s] for s in order]
        thr = T["sequence"]["order"]
        eps = 1e-6
        bad = [(order[i], order[i + 1]) for i in range(3) if times[i] > times[i + 1] + tol + eps]          # reversed by more than one sample
        near = [(order[i], order[i + 1]) for i in range(3) if times[i + 1] - times[i] < 0.5 * tol and (order[i], order[i + 1]) not in bad]   # same sample, or reversed by one sample
        if not bad:
            st = WARN if near else PASS
            why = "peak order pelvis->thorax->arm->club" + (f"; not resolvable at dt={tol * 1000:.0f} ms (same sample or reversed by one sample): {near}" if near else "")
        else:
            swap = (bad == [("thorax", "arm")] and (times[1] - times[2]) <= T["sequence"]["swap_warn_ms"]["value"] / 1000.0 + eps)
            if swap:
                st, why = WARN, "thorax and arm peaks swapped by <= %d ms (amateur mean order, Cheetham)" % T["sequence"]["swap_warn_ms"]["value"]
            else:
                st, why = FAIL, f"peak order violated: {bad}"
        checks.append(_res("kinematic_sequence_order", st, {s: round(tpk[s], 3) for s in SEG}, order, why, thr))
        lead = {s: (tpk["club"] - tpk[s]) * 1000.0 for s in ("pelvis", "thorax", "arm")}
        band = T["sequence"]["lead_band_ms_warn"]["value"]
        outs = {s: round(lead[s]) for s in lead if not (band[s][0] <= lead[s] <= band[s][1])}
        checks.append(_res("kinematic_sequence_timing_ms_before_club_peak", WARN if outs else PASS, {s: round(v) for s, v in lead.items()}, band,
                           ("outside band: %s (pro means 87/68/65 ms, amateur 78/59/64)" % outs) if outs else "inside warn band around the published means", T["sequence"]["lead_band_ms_warn"]))
    else:
        checks.append(_res("kinematic_sequence_order", SKIP, None, None, "needs pelvis, thorax, arm and club traces"))

    # 2. peak speeds vs club speed
    if tg:
        ps = T["peak_speed"]
        for s in SEG:
            if spd[s] is None:
                checks.append(_res(f"peak_speed_{s}", SKIP, None, None, f"no {s} trace")); continue
            pk = float(spd[s][sl].max()); ratio = pk / tg[s]
            st = _band(ratio, ps["pass_ratio"]["value"], ps["warn_ratio"]["value"])
            checks.append(_res(f"peak_speed_{s}_deg_s", st, round(pk, 1), f"{tg[s]:.0f} x {ps['pass_ratio']['value']}",
                               f"{ratio:.2f} x target at {chs_mph:.0f} mph" + (" (target EXTRAPOLATED beyond measured 88-109 mph)" if tg["extrapolated"] else " (between measured groups)"),
                               ps["rows_by_chs"], tg["extrapolated"]))
        # peak speed cannot be compared when chs implied from the club itself -> note
    else:
        checks.append(_res("peak_speed", SKIP, None, None, "no club trace and no chs_mph"))

    # 3. X-factor at top of backswing (thorax minus pelvis angle)
    if "thorax" in jt and "pelvis" in jt:
        xf = np.degrees(np.unwrap(jt["thorax"]) - np.unwrap(jt["pelvis"]))[: impact_idx + 1]
        xtop = float(np.max(np.abs(xf)))
        b = T["x_factor"]["top_of_backswing_deg"]["value"]
        st = _band(xtop, b["pass"], b["warn"], b["fail_outside"])
        checks.append(_res("x_factor_top_deg", st, round(xtop, 1), b["pass"], "max |thorax - pelvis| before impact (published 24-59 deg, method dependent); stretch not checked", T["x_factor"]["top_of_backswing_deg"]))
    else:
        checks.append(_res("x_factor_top_deg", SKIP, None, None, "needs pelvis and thorax angle traces (not speeds)"))

    # 4. actuator limits (needs tier + torque/qvel traces) and static feasibility
    act = T["actuators"]
    if tier:
        tiers = act["g1_tiers_tau_Nm_w_rad_s"]["value"][tier]
        j2k = act["joint_to_limit_key"]["value"]
        worst_over, worst_derate, viol = 0.0, 0.0, []
        for key in [k for k in jt if k.startswith("torque:")]:
            jname = key.split(":", 1)[1]
            base = jname.replace("left_", "").replace("right_", "")
            lk = j2k.get(jname) or j2k.get(base)
            if lk is None:
                notes.append(f"no actuator limit mapping for joint {jname}; skipped"); continue
            tau_max, w_rated = tiers[lk]
            tau = np.abs(jt[key]); w = np.abs(jt.get(f"qvel:{jname}", np.zeros_like(tau)))
            over = float(np.max(tau) / tau_max)
            avail = tau_max * np.clip(1 - w / w_rated, 0, 1)
            der = float(np.max(tau / np.maximum(avail, 1e-9) * (tau > 0.05 * tau_max)))
            worst_over, worst_derate = max(worst_over, over), max(worst_derate, der)
            if over > act["torque_overshoot_fail_ratio"]["value"]:
                viol.append((jname, "peak torque %.0f > %s tier limit %.0f N*m" % (np.max(tau), tier, tau_max)))
            elif der > act["derate_overshoot_warn_ratio"]["value"]:
                viol.append((jname, "torque exceeds the speed-derated limit by %.0f %% (w up to %.1f of rated %.0f rad/s)" % ((der - 1) * 100, np.max(w), w_rated)))
        any_trace = any(k.startswith("torque:") for k in jt)
        if any_trace:
            st = FAIL if worst_over > act["torque_overshoot_fail_ratio"]["value"] else (WARN if viol else PASS)
            checks.append(_res("actuator_torque_speed_limits", st, dict(peak_over_max=round(worst_over, 3), derate_ratio=round(worst_derate, 3)), f"<= {act['torque_overshoot_fail_ratio']['value']}",
                               "; ".join(f"{j}: {m}" for j, m in viol) or "all joints inside tier limits", act["g1_tiers_tau_Nm_w_rad_s"]))
        else:
            checks.append(_res("actuator_torque_speed_limits", SKIP, None, None, "no torque:<joint> traces"))
        if chs_mph:
            fr = act["feasibility_ratio_avg_by_tier_chs"]["value"][tier]
            xs = sorted(int(k) for k in fr)
            groups = {g: float(np.interp(chs_mph, xs, [fr[str(x)][g] for x in xs])) for g in fr[str(xs[0])]}
            lo, hi = act["feasibility_warn_fail_ratio"]["value"]
            worst = max(groups.values())
            st = FAIL if worst > hi else (WARN if worst > lo else PASS)
            bad = {g: round(v, 2) for g, v in groups.items() if v > lo}
            checks.append(_res("power_feasibility_vs_hardware", st, {g: round(v, 2) for g, v in groups.items()}, f"each group <= {lo}",
                               (f"at {chs_mph:.0f} mph the {tier} tier cannot supply average power for {bad} (derived, avg power; peak need ~2.5x)" if bad else f"{tier} tier supplies the average power at {chs_mph:.0f} mph (derived)"),
                               act["feasibility_ratio_avg_by_tier_chs"], chs_mph > 116 or chs_mph < 100))
    else:
        checks.append(_res("actuator_torque_speed_limits", SKIP, None, None, "pass tier='stock'|'elite' to enable"))

    # 5. torque/power budget and GRF
    pb = T["power_budget"]
    if "torque:pelvis_yaw" in jt:
        wlen = int(round(pb["downswing_window_s"]["value"] / dt))
        seg = np.abs(jt["torque:pelvis_yaw"])[max(0, impact_idx - wlen): impact_idx + 1]
        avg = float(seg.mean()); b = pb["pelvis_yaw_avg_torque_Nm_downswing"]["value"]
        checks.append(_res("pelvis_yaw_avg_torque_Nm", _band(avg, b["pass"], b["warn"]), round(avg, 1), b["pass"],
                           "mean |torque| over the last 0.23 s before impact (published-derived 150-300 N*m at 100-116 mph)", pb["pelvis_yaw_avg_torque_Nm_downswing"], bool(chs_mph and chs_mph > 116)))
    else:
        checks.append(_res("pelvis_yaw_avg_torque_Nm", SKIP, None, None, "no torque:pelvis_yaw trace"))
    wr = [k for k in jt if k.startswith("torque:") and "wrist" in k]
    if wr and chs_mph:
        tab = pb["grip_torque_Nm_by_chs"]["value"]; req = float(np.interp(chs_mph, [a for a, _ in tab], [b for _, b in tab]))
        pk = float(max(np.max(np.abs(jt[k])) for k in wr)); lo, hi = pb["grip_torque_pass_ratio"]["value"]
        st = PASS if lo * req <= pk <= hi * req else WARN
        cap = act["human_wrist_torque_cap_Nm"]["value"]
        why = f"peak wrist torque {pk:.0f} N*m vs ~{req:.0f} N*m grip torque needed at {chs_mph:.0f} mph (Nesbit fit; wrist torque crosses zero before impact)"
        if pk > cap:
            st = WARN; why += f"; above the {cap} N*m human wrist cap (Sprigings & Neal, unverified)"
        checks.append(_res("wrist_torque_vs_grip_requirement", st, round(pk, 1), [round(lo * req), round(hi * req)], why, pb["grip_torque_Nm_by_chs"], bool(chs_mph > 116)))
    g = jt.get("grf_lead_vertical_bw")
    if g is not None:
        b = T["grf"]["lead_vertical_bw"]["value"]; pk, mn = float(g.max()), float(g.min())
        st = FAIL if (mn < b["fail_outside"][0] or pk > b["fail_outside"][1]) else _band(pk, b["pass"], b["warn"], b["fail_outside"])
        checks.append(_res("grf_lead_vertical_bw", st, dict(peak=round(pk, 2), min=round(mn, 2)), b["pass"], "peak lead-foot vertical force in body weights; min < 0 means the foot pulls on the ground", T["grf"]["lead_vertical_bw"]))
    else:
        checks.append(_res("grf_lead_vertical_bw", SKIP, None, None, "no grf_lead_vertical_bw trace (the G1 env holds the legs rigid: no GRF realism)"))
    return dict(overall=_overall(checks), checks=checks, notes=notes)


# ---------------------------------------------------------------------------------------------- shot
def _pick(d, *keys):
    for k in keys:
        if k in d and d[k] is not None and not (isinstance(d[k], float) and math.isnan(d[k])):
            return float(d[k])
    return None


def check_shot_realism(shot: dict, thresholds: dict | None = None, use_golfphys: bool = True) -> dict:
    """shot: dict with any of ball_speed_mph|ball_speed_ms, club_speed_mph|club_speed_ms, smash, launch_deg|launch_elevation_deg, spin_rpm|backspin_rpm,
    spin_axis_deg, carry_yd|carry_m, total_yd|total_m, descent_deg.  Missing fields -> 'skip'.  Driver thresholds."""
    T = thresholds or load_thresholds(); S = T["shot"]
    checks, notes = [], []
    bs = _pick(shot, "ball_speed_mph"); bs = bs if bs is not None else (_pick(shot, "ball_speed_ms") or 0) / 0.44704 or None
    cs = _pick(shot, "club_speed_mph"); cs = cs if cs is not None else ((_pick(shot, "club_speed_ms") or 0) / 0.44704 or None)
    smash = _pick(shot, "smash") or (bs / cs if bs and cs else None)
    launch = _pick(shot, "launch_deg", "launch_elevation_deg"); spin = _pick(shot, "spin_rpm", "backspin_rpm")
    carry = _pick(shot, "carry_yd"); carry = carry if carry is not None else ((_pick(shot, "carry_m") or 0) / 0.9144 or None)
    total = _pick(shot, "total_yd"); total = total if total is not None else ((_pick(shot, "total_m") or 0) / 0.9144 or None)
    desc = _pick(shot, "descent_deg"); axis = _pick(shot, "spin_axis_deg")
    vals = [bs, cs, smash, launch, spin, carry, total, desc]
    if any(v is not None and not math.isfinite(v) for v in vals):
        return dict(overall=FAIL, checks=[_res("input", FAIL, None, "finite values", "non-finite field in shot")], notes=notes)

    if smash is not None:
        t = S["smash_driver"]["value"]
        st = FAIL if smash > t["fail_above"] else WARN if (smash > t["warn_above"] or smash < t["warn_below"]) else PASS
        checks.append(_res("smash", st, round(smash, 3), f"{t['warn_below']}..{t['warn_above']} (hard ceiling {t['fail_above']})",
                           "ball speed / club speed; 1.50 is a COR (0.83) and 200 g head ceiling" if st != PASS else "inside expected range", S["smash_driver"]))
    else:
        checks.append(_res("smash", SKIP, None, None, "need smash or ball+club speed"))
    if cs is not None:
        lo, hi = S["club_speed_range_mph"]["value"]
        checks.append(_res("club_speed_mph", PASS if lo <= cs <= hi else WARN, round(cs, 1), [lo, hi], "driver swing speed range", S["club_speed_range_mph"], cs > 116))
    if spin is not None:
        b = S["spin_rpm_driver"]["value"]
        st = _band(spin, b["pass"], b["warn"], b["fail_outside"])
        checks.append(_res("spin_rpm", st, round(spin), b["pass"], "driver spin gate (published windows, derived thresholds)", S["spin_rpm_driver"], bool(cs and cs > 120)))
    else:
        checks.append(_res("spin_rpm", SKIP, None, None, "no spin in shot (gate JSONs do not carry per-shot spin)"))
    if launch is not None:
        b = S["launch_deg_driver"]["value"]
        checks.append(_res("launch_deg", _band(launch, b["pass"], b["warn"], b["fail_outside"]), round(launch, 2), b["pass"], "driver launch window (TrackMan 7.8-9.3 at AoA 0, Foresight 10-14)", S["launch_deg_driver"]))
    if desc is not None:
        b = S["descent_deg_driver"]["value"]
        checks.append(_res("descent_deg", _band(desc, b["pass"], b["warn"], b["fail_outside"]), round(desc, 1), b["pass"], "descent angle (tour 36-39; golfphys 33-50)", S["descent_deg_driver"]))
    else:
        checks.append(_res("descent_deg", SKIP, None, None, "no descent angle (log it: golfphys ShotResult.descent_deg)"))
    if carry is not None and carry <= 0:
        checks.append(_res("carry_positive", FAIL, carry, "> 0", "no carry (miss / air shot / ball never landed)"))
    elif carry is not None and total is not None:
        r = total / carry; b = S["total_over_carry"]["value"]
        st = _band(r, b["pass"], b["warn"], b["fail_outside"])
        checks.append(_res("total_over_carry", st, round(r, 3), b["pass"], "total/carry (normal turf 1.07-1.13, firm to ~1.2; env without roll gives 1.0)", S["total_over_carry"]))
    if axis is not None:
        b = S["spin_axis_abs_deg"]["value"]
        checks.append(_res("spin_axis_abs_deg", FAIL if abs(axis) > b["fail"] else WARN if abs(axis) > b["warn"] else PASS, round(axis, 1), f"<= {b['warn']}", "spin axis tilt", S["spin_axis_abs_deg"]))
    # golfphys consistency: reported carry vs model carry from the reported launch conditions
    if use_golfphys and bs and launch is not None and spin is not None and carry is not None and carry > 0:
        try:
            from golfphys.sim import shot_from_launch
            r = shot_from_launch(bs * 0.44704, launch, spin, spin_axis_deg=axis or 0.0)
            res = carry - r.carry_yd; b = S["golfphys_carry_residual_yd"]["value"]
            st = PASS if abs(res) <= b["pass"] else WARN if abs(res) <= b["warn"] else FAIL
            checks.append(_res("carry_vs_golfphys_yd", st, round(res, 1), f"|residual| <= {b['pass']}", f"reported carry {carry:.0f} vs golfphys {r.carry_yd:.0f} yd from ball speed/launch/spin (model-only; Foresight tables sit 14-33 yd above golfphys at 120-145 mph)",
                               S["golfphys_carry_residual_yd"], bool(cs and cs > 120)))
            if total is not None:
                notes.append(f"golfphys total on normal turf {r.total_yd:.0f} yd (reported {total:.0f}); golfphys descent {r.descent_deg:.1f} deg")
        except Exception as e:  # pragma: no cover
            notes.append(f"golfphys unavailable: {e}")
    else:
        checks.append(_res("carry_vs_golfphys_yd", SKIP, None, None, "needs ball speed, launch, spin and carry in the shot (gate JSON rows carry no spin)"))
    return dict(overall=_overall(checks), checks=checks, notes=notes)


def shot_from_gate_block(pb: dict) -> dict:
    """Adapter: one `policy_det` / `policy_stoch` block of a results/gate_*.json file -> shot dict (means; the gate JSON has no per-shot rows or spin).
    Uses impact club speed (m/s), mean peak ball speed, launch elevation, carry and total (yd)."""
    out = dict(club_speed_ms=pb.get("impact_club_speed_mean"), ball_speed_ms=pb.get("mean_peak_ball_speed"), launch_deg=pb.get("launch_elev_mean_deg"),
               carry_yd=pb.get("mean_carry_yd"), total_yd=pb.get("mean_total_yd"))
    return {k: v for k, v in out.items() if v is not None and not (isinstance(v, float) and math.isnan(v))}
