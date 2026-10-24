"""Harness v3d (PROPOSED, Orchestrator-approved for review; v3c stays the default). Opt-in with `--harness v3d`.
v3d = v3c run (same episodes, friction gate U(0.7,1.05), info rows) + the re-graded rows below. Sources: docs/HARNESS_V3D_NOTES.md
(Trainer band check 2026-10-24: Cheetham 2008 full text, Lynn 2013, TrackMan 2010 fitting chart, USGA/R&A R22-01, Shaw 2023 abstract).
 (1) shot/spin_rpm: PASS 2000-3700 rpm when club speed is 70-85 mph (DERIVED: TrackMan optimizer envelope 75-85 mph; R22 measured means inside);
     WARN band 1200-4000 unchanged; outside 70-85 mph the v3c grade is kept. Applied to the deterministic row and to robustness spin median/p10/p90.
 (2) swing/peak_speed_pelvis_deg_s: absolute floor 250 deg/s (DERIVED: Cheetham 2008 amateur 395-2x68=259 at 88 mph, lowered for ~74 mph). PASS >=250,
     WARN below (row was WARN-capped as extrapolated in v3c); info target ~340 (DERIVED, Cheetham between-group slope; Lynn 2013 within-group r~0).
 (3) swing/kinematic_sequence_order + _timing: thorax/arm tie or inversion up to 30 ms allowed; REQUIRE arm peak >=20 ms before the club peak
     (DERIVED: Cheetham amateur arm 64-2x23=18 ms); pelvis must peak first and >=15 ms before the club (design choice); upper bound 150 ms (amateur 78+-38).
     Failing the requirement = WARN (same severity class as v3c timing; a WARN blocks a PASS verdict).
 (4) lead-foot slip/rotation unchanged (PROVISIONAL, no sourced numbers).
 (5) mine/robustness: additionally FAIL if club speed p10 < 0.93 x median (LOW CONFIDENCE: Shaw 2023 JSCR abstract CV<=5.8%; elite SD 0.5-2.1 mph from a snippet).
 (6) mine/strike_height (PROVISIONAL, Orchestrator-approved 2026-10-24): deterministic median |dz| (strike height from the face centre, mm).
     PASS <= 15 mm (DESIGN CHOICE, not sourced); WARN > 15 mm; FAIL >= STRIKE_FACE_EDGE_MM = 26.5 mm (measured spec, single brand: Wishon 919THI
     53x105 mm face, provisional). Info: mine/strike_within_sim_box_info (|dz| <= 32 mm sim head-box half-height, sim geometry) and
     mine/strike_outside_measured_info (|dz| > 12.7 mm = outside measured Hotstix data).
 (7) Side-by-side face-edge ball model (INFO rows, never the default): golfphys CENTRE strike (dz = 0, same club vel/normal/dy) -> data/driver_face_offcentre
     face_edge_adjust with the real dz, CAPPED (+/-12.7 mm as written) and LINEAR (extrapolated). Spin passes under the model only if BOTH pass.
     A verdict that would be PASS only under this model is 'not a pass (face-edge-model-only)'. Labels: 148 mph is a MODEL value (TrajectoWare);
     smash LOW confidence; leveling off beyond 12.7 mm UNVERIFIED until R22-07 Fig 1 is read; 51.3 rpm/mm and 0.201 deg/mm derived from measured Hotstix data (secondary source).
     Skipped (no row) when the run did not log strike offsets.
 Info flag: if the v3d verdict is PASS only because of (1), verdict becomes 'not a pass (spin-band-only)'.
"""
import copy
SPIN_PASS_V3D = (2000.0, 3700.0); SPIN_WARN = (1200.0, 4000.0); SPIN_SPEED_RANGE = (70.0, 85.0); SPIN_PASS_V3C = (1800.0, 3000.0)
PELVIS_FLOOR_DPS = 250.0; PELVIS_INFO_TARGET_DPS = 340.0
TA_INVERSION_MS = 30.0; ARM_CLUB_MIN_MS = 20.0; PELVIS_CLUB_MIN_MS = 15.0; SEQ_MAX_MS = 150.0
CLUB_P10_MIN_FRAC = 0.93
STRIKE_DZ_WARN_MM = 15.0; STRIKE_FACE_EDGE_MM = 26.5   # SINGLE source of the face-edge FAIL threshold: 53 mm / 2. MEASURED SPEC, SINGLE BRAND (Wishon 919THI 53x105 mm), PROVISIONAL
                              # (data/references/driver_face_offcentre_refs.*; Orchestrator-approved Oct 24). Was 32.0 = sim head-box half-height. 15 mm WARN = design choice (not sourced)
SIM_BOX_HALF_HEIGHT_MM = 32.0  # sim geometry (env/models/humanoid_golf_v5_g1_{lh,rh}.xml head box size z 0.032), not a real-driver source; INFO row only
MEASURED_DZ_MM = 12.7          # Hotstix robot data span +/-0.5 in (secondary source); INFO row only

def strike_height_status(med_abs_dz_mm):
    if med_abs_dz_mm is None: return "skip"
    return "fail" if med_abs_dz_mm >= STRIKE_FACE_EDGE_MM else "warn" if med_abs_dz_mm > STRIKE_DZ_WARN_MM else "pass"

def strike_extent_rows(info_row):
    d = ((info_row or {}).get("values") or {}).get("deterministic") or {}; m = d.get("median_abs")
    if m is None: return {}
    mk = lambda ok, why: dict(status="info", passed=False, tag="info_only", gating=False, values=dict(median_abs_dz_mm=m, flag=ok), why=[why])
    return {"mine/strike_within_sim_box_info": mk(m <= SIM_BOX_HALF_HEIGHT_MM, f"INFO: median |dz| {m:.1f} mm {'within' if m <= SIM_BOX_HALF_HEIGHT_MM else 'OUTSIDE'} the sim head-box half-height {SIM_BOX_HALF_HEIGHT_MM:g} mm (sim geometry)"),
            "mine/strike_outside_measured_info": mk(m > MEASURED_DZ_MM, f"INFO: median |dz| {m:.1f} mm {'> ' + format(MEASURED_DZ_MM, 'g') + ' mm: outside measured Hotstix data' if m > MEASURED_DZ_MM else 'within the measured Hotstix span +/-12.7 mm'}")}

def face_edge_eval(centre, dz_mm):
    """Side-by-side model for one episode. centre MUST be a golfphys CENTRE strike (dz_used_m == 0) - guards against double counting the
    off-centre effect (golfphys gear effect + face_edge_adjust). Returns capped (as written, +/-12.7 mm saturation) and linear (extrapolated)."""
    if not centre or centre.get("error"): raise ValueError(f"no centre-strike golfphys result: {centre}")
    if centre.get("dz_used_m") is None or abs(float(centre["dz_used_m"])) > 1e-12:
        raise ValueError(f"face_edge_adjust needs a golfphys CENTRE strike (dz_used_m == 0), got dz_used_m={centre.get('dz_used_m')!r}: would double count")
    from data.driver_face_offcentre import face_edge_adjust, GEAR_V_RPM_PER_MM_AT_148
    from eval.golfphys_total import golfphys_total
    cap = face_edge_adjust(centre, dz_mm)
    if not cap["valid"]: return dict(status=cap["status"], valid=False, capped=None, linear=None)
    k = GEAR_V_RPM_PER_MM_AT_148 * centre["ball_speed_mph"] / 148.0
    lin = dict(cap, spin_rpm=max(0.0, centre["spin_rpm"] - k * dz_mm))
    out = dict(status=cap["status"], valid=True)
    for nm, m in (("capped", cap), ("linear", lin)):
        bs = centre["ball_speed_mph"] * m["smash"] / centre["smash"]
        try: gp = golfphys_total(bs, m["launch_deg"], m["spin_rpm"], 0.0, 0.0); carry = gp.get("carry_yd"); toc = gp.get("total_over_carry")
        except Exception: carry = toc = None
        out[nm] = dict(spin_rpm=m["spin_rpm"], launch_deg=m["launch_deg"], smash=m["smash"], ball_speed_mph=bs, carry_yd=carry, total_over_carry=toc)
    return out

def _q(xs):
    import numpy as np
    xs = [float(x) for x in xs if x is not None]
    if not xs: return None
    a = np.percentile(xs, [50, 10, 90]); return dict(median=float(a[0]), p10=float(a[1]), p90=float(a[2]), n=len(xs))

FACE_EDGE_LABELS = ["148 mph is a MODEL value (TrajectoWare)", "smash: LOW confidence", "leveling off beyond 12.7 mm UNVERIFIED until R22-07 Fig 1 is read",
                    "51.3 rpm/mm and 0.201 deg/mm DERIVED from measured Hotstix data (secondary source)", "side-by-side model only, never the default ball model"]

def face_edge_rows(det_eps, rob_eps=None):
    """INFO rows mine/spin_face_edge_{capped,linear}_info (+ launch/smash/carry/total-over-carry) over deterministic and robustness episodes."""
    R = {}
    ev = lambda E: [face_edge_eval(e["strike_centre"], e["strike_dz_mm"]) for e in E if e.get("strike_centre") and e.get("strike_dz_mm") is not None]
    D, B = ev(det_eps), ev(rob_eps or [])
    if not D: return R
    for nm in ("capped", "linear"):
        g = lambda E, f: _q([x[nm][f] for x in E if x["valid"]])
        R[f"mine/spin_face_edge_{nm}_info"] = dict(status="info", passed=False, tag="info_only", gating=False, model=nm,
            values=dict(deterministic={f: g(D, f) for f in ("spin_rpm", "launch_deg", "smash", "carry_yd", "total_over_carry", "ball_speed_mph")},
                        robustness={f: g(B, f) for f in ("spin_rpm", "launch_deg", "smash", "carry_yd", "total_over_carry")} if B else None,
                        n_off_face=dict(deterministic=sum(1 for x in D if not x["valid"]), robustness=sum(1 for x in B if not x["valid"]))),
            why=[f"INFO: side-by-side face-edge model ({nm}{', +/-12.7 mm saturation as written' if nm == 'capped' else ', extrapolated linearly beyond 12.7 mm'}) on a golfphys centre strike"] + FACE_EDGE_LABELS)
    return R

def face_edge_model_verdict(r_v3d, spin_fn):
    """Verdict if spin (deterministic + robustness median/p10/p90) came from the side-by-side model; spin passes only if BOTH capped and linear pass."""
    C = r_v3d["checks"]; cap, lin = C.get("mine/spin_face_edge_capped_info"), C.get("mine/spin_face_edge_linear_info")
    if not (cap and lin): return None
    club = (C.get("shot/club_speed_mph") or {}).get("values"); W = {"skip": -1, "pass": 0, "warn": 1, "fail": 2}
    def worst(*ss): return max(ss, key=lambda x: W.get(x, -1))
    det = [m["values"]["deterministic"]["spin_rpm"] for m in (cap, lin)]
    if None in det: return dict(verdict="n/a (off face)")
    sdet = worst(*(spin_fn(d["median"], club) for d in det))
    C2 = copy.deepcopy(C); C2["shot/spin_rpm"] = dict(C2.get("shot/spin_rpm") or {}, status=sdet, passed=sdet == "pass")
    rb = C2.get("mine/robustness")
    if rb and rb.get("values", {}).get("shot", {}).get("spin_rpm") and cap["values"]["robustness"] and lin["values"]["robustness"]:
        cm = (rb["values"]["shot"].get("club_speed_mph") or {}).get("median")
        st = {q: worst(*(spin_fn(m["values"]["robustness"]["spin_rpm"][q], cm) for m in (cap, lin))) for q in ("median", "p10", "p90")}
        C2["mine/robustness"] = _regrade_robust(rb, True, st)
    S = summarize(C2)
    return dict(verdict=S["verdict"], n_pass=S["n_pass"], n_warn=S["n_warn"], n_fail=S["n_fail"], spin_status_det=sdet, rule="spin passes only if BOTH capped and linear pass")

def strike_height_row(info_row):
    d = ((info_row or {}).get("values") or {}).get("deterministic") or {}; m = d.get("median_abs")
    s = strike_height_status(m)
    return dict(status=s, passed=s == "pass", tag="provisional", gating=True, values=dict(median_abs_dz_mm=m, median_dz_mm=d.get("median")),
                expected=dict(pass_max_mm=STRIKE_DZ_WARN_MM, fail_at_mm=STRIKE_FACE_EDGE_MM),
                why=[f"PROVISIONAL (v3d only): deterministic median |dz| {m:.1f} mm; WARN > {STRIKE_DZ_WARN_MM:g} mm (design choice, not sourced), FAIL >= {STRIKE_FACE_EDGE_MM:g} mm face edge (STRIKE_FACE_EDGE_MM = 53/2 mm, measured spec, single brand (Wishon 919THI 53x105 mm), provisional)"] if m is not None else ["no strike data"],
                ref="docs/HARNESS_V3D_NOTES.md (strike height)")
_W = {"skip": -1, "info": -1, "pass": 0, "warn": 1, "fail": 2}

def spin_status(rpm, club_mph, v3d=True):
    if rpm is None: return "skip"
    lo, hi = SPIN_PASS_V3D if (v3d and club_mph is not None and SPIN_SPEED_RANGE[0] <= club_mph <= SPIN_SPEED_RANGE[1]) else SPIN_PASS_V3C
    if lo <= rpm <= hi: return "pass"
    return "warn" if SPIN_WARN[0] <= rpm <= SPIN_WARN[1] else "fail"

def pelvis_status(dps): return "skip" if dps is None else ("pass" if dps >= PELVIS_FLOOR_DPS else "warn")

def sequence_status(ms_before_club):
    """ms_before_club: {'pelvis','thorax','arm'} -> ms before club peak (positive = earlier). Returns (status, why)."""
    p, t, a = (ms_before_club.get(k) for k in ("pelvis", "thorax", "arm")); why = []
    if None in (p, t, a): return "skip", ["missing timing"]
    if a < ARM_CLUB_MIN_MS: why.append(f"arm peaks {a:g} ms before club (< {ARM_CLUB_MIN_MS:g} ms required, DERIVED Cheetham amateur 64-2x23)")
    if p < PELVIS_CLUB_MIN_MS: why.append(f"pelvis {p:g} ms before club (< {PELVIS_CLUB_MIN_MS:g})")
    if p < max(t, a): why.append(f"pelvis is not first (pelvis {p:g}, thorax {t:g}, arm {a:g} ms)")
    if a - t > TA_INVERSION_MS: why.append(f"arm peaks {a - t:g} ms before thorax (> {TA_INVERSION_MS:g} ms inversion allowed)")
    if max(p, t, a) > SEQ_MAX_MS: why.append(f"a peak is > {SEQ_MAX_MS:g} ms before club")
    return ("warn" if why else "pass"), why

def summarize(C):
    st = [c["status"] for c in C.values()]; n = {x: st.count(x) for x in ("pass", "warn", "fail", "skip", "info")}
    return dict(verdict="FAIL" if n["fail"] else "WARN" if n["warn"] else "PASS", n_pass=n["pass"], n_warn=n["warn"], n_fail=n["fail"], n_skip=n["skip"], n_info=n["info"], n_checks=len(st) - n["skip"] - n["info"])

def _regrade_robust(row, v3d_spin=True, spin_status_override=None):
    v = row.get("values") or {}; sh = v.get("shot") or {}
    if not sh: return row
    row = copy.deepcopy(row); v = row["values"]; sh = v["shot"]; club_med = (sh.get("club_speed_mph") or {}).get("median")
    if "spin_rpm" in sh: sh["spin_rpm"]["status"] = dict(spin_status_override) if spin_status_override else {q: spin_status(sh["spin_rpm"][q], club_med, v3d_spin) for q in ("median", "p10", "p90")}
    fails, warns = [], []
    if v.get("contact_frac", 0) < 0.95: fails.append(f"contact {v['contact_frac']:.2f} < 0.95")
    if v.get("start_direction_pass_frac", 0) < 0.90: fails.append(f"start_direction pass {v['start_direction_pass_frac']:.2f} < 0.90")
    if v.get("lead_foot_plant_pass_frac", 0) < 0.90: fails.append(f"lead_foot_plant pass {v['lead_foot_plant_pass_frac']:.2f} < 0.90")
    for k, s in sh.items():
        bad = [q for q, x in s["status"].items() if x == "fail"]
        if bad: fails.append(f"{k} {'/'.join(bad)} outside WARN band")
        elif any(x == "warn" for x in s["status"].values()): warns.append(f"{k} leaves PASS band")
    c = sh.get("club_speed_mph") or {}; ratio = (c["p10"] / c["median"]) if c.get("median") else None
    v["club_p10_over_median"] = ratio; v["club_p10_rule"] = f">= {CLUB_P10_MIN_FRAC} x median (v3d, LOW CONFIDENCE: Shaw 2023 abstract CV<=5.8%)"
    if ratio is not None and ratio < CLUB_P10_MIN_FRAC: fails.append(f"club speed p10 {c['p10']:.1f} = {ratio:.2f} x median (< {CLUB_P10_MIN_FRAC}, v3d LOW CONFIDENCE)")
    row["status"] = "fail" if fails else "warn" if warns else "pass"; row["passed"] = row["status"] == "pass"; row["why"] = fails + warns
    return row

def apply_v3d(r, _spin=True):
    """Re-grade a v3c result dict (same episodes) under v3d. Pure function of the recorded values; returns a new dict."""
    r = copy.deepcopy(r); C = r["checks"]; club = (C.get("shot/club_speed_mph") or {}).get("values")
    if "shot/spin_rpm" in C:
        s = spin_status(C["shot/spin_rpm"]["values"], club, _spin); C["shot/spin_rpm"].update(status=s, passed=s == "pass", expected="v3d: 2000-3700 at 70-85 mph (DERIVED, TrackMan optimizer envelope), WARN 1200-4000" if _spin else C["shot/spin_rpm"].get("expected"))
    k = "swing/peak_speed_pelvis_deg_s"
    if k in C:
        s = pelvis_status(C[k]["values"]); C[k].update(status=s, passed=s == "pass", expected=f"v3d floor >= {PELVIS_FLOOR_DPS:g} deg/s (DERIVED, Cheetham 2008 amateur -2 SD, lowered); info target ~{PELVIS_INFO_TARGET_DPS:g}", info_target_dps=PELVIS_INFO_TARGET_DPS, why=[f"{C[k]['values']} deg/s vs floor {PELVIS_FLOOR_DPS:g}"])
    kt, ko = "swing/kinematic_sequence_timing_ms_before_club_peak", "swing/kinematic_sequence_order"
    if kt in C and isinstance(C[kt].get("values"), dict):
        s, why = sequence_status(C[kt]["values"]); C[kt].update(status=s, passed=s == "pass", why=why, expected=dict(arm_to_club_min_ms=ARM_CLUB_MIN_MS, thorax_arm_inversion_max_ms=TA_INVERSION_MS, pelvis_min_ms=PELVIS_CLUB_MIN_MS, max_ms=SEQ_MAX_MS))
        if ko in C:  # order: pelvis first, club last, thorax/arm tie or inversion <= 30 ms allowed
            tv = C[kt]["values"]; ok = tv["pelvis"] >= max(tv["thorax"], tv["arm"]) and min(tv.values()) > 0 and tv["arm"] - tv["thorax"] <= TA_INVERSION_MS
            C[ko].update(status="pass" if ok else "warn", passed=ok, why=["v3d: pelvis first, club last, thorax/arm tie or inversion <= 30 ms allowed (DERIVED)"])
    if "mine/robustness" in C and C["mine/robustness"].get("status") not in ("skip",): C["mine/robustness"] = _regrade_robust(C["mine/robustness"], _spin)
    if (C.get("mine/strike_dz_info") or {}).get("status") == "info": C["mine/strike_height"] = strike_height_row(C["mine/strike_dz_info"])
    if (C.get("mine/strike_dz_info") or {}).get("status") == "info": C.update(strike_extent_rows(C["mine/strike_dz_info"]))
    S = summarize(C)
    r.update(checks_passed=S["n_pass"], n_checks=S["n_checks"], n_warn=S["n_warn"], n_fail=S["n_fail"], n_skip=S["n_skip"], n_info=S["n_info"], verdict=S["verdict"])
    r["harness_v3"] = dict(r.get("harness_v3") or {}, harness="v3d", base_run="v3c")
    return r

def apply_v3d_flagged(r):
    out = apply_v3d(r, True)
    if out["verdict"] == "PASS" and apply_v3d(r, False)["verdict"] != "PASS":
        out["verdict"] = "not a pass (spin-band-only)"; out["spin_band_only"] = True
    else: out["spin_band_only"] = False
    fm = face_edge_model_verdict(out, lambda rpm, club: spin_status(rpm, club, True))
    out["face_edge_model"] = fm; out["face_edge_model_only"] = False
    if fm and fm.get("verdict") == "PASS" and out["verdict"] != "PASS":
        out["face_edge_model_only"] = True; out["face_edge_model"]["note"] = "not a pass (face-edge-model-only)"
    return out
