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
     outside-measured flags: mine/strike_outside_measured_info (|dz| > 21 mm, R22-07 range for speed, spin AND launch),
     mine/strike_beyond_r2207_info (|dz| > 21 mm). Launch under the model passes only if BOTH Hotstix and R22-07 Fig 3 launch are in band.
 (7) Side-by-side face-edge ball model (INFO rows, never the default): golfphys CENTRE strike (dz = 0, same club vel/normal/dy) -> data/driver_face_offcentre
     face_edge_adjust with the real dz, CAPPED (+/-12.7 mm as written) and LINEAR (extrapolated). Spin passes under the model only if BOTH pass.
     A verdict that would be PASS only under this model is 'not a pass (face-edge-model-only)'. Labels: 148 mph is a MODEL value (TrajectoWare);
     smash LOW confidence; R22-07 Fig 2: spin rises to a peak near -15 mm, then falls (capped variant kept for comparison); 51.3 rpm/mm and 0.201 deg/mm derived from measured Hotstix data (secondary source).
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
MEASURED_DZ_MM = 12.7          # Hotstix robot data span +/-0.5 in (secondary source): launch flag only
LAUNCH_BAND = (7.0, 16.0)      # same band as shot/launch_deg (derived)
R2207_DZ_MM = 21.0             # R22-07 Fig 1-2 digitized span (-21..+21 mm): ball speed/smash and spin flag

def face_edge_for(r):
    """FAIL threshold (mm) + label. Realistic head (tee_info.head.mode == 'realistic'): the ENV's face_limits() vertical half-height (27 mm for the
    Data Agent's 54 mm nominal face). Otherwise STRIKE_FACE_EDGE_MM (26.5, Wishon 919THI)."""
    H_ = ((r or {}).get("tee_info") or {}).get("head") or {}
    if H_.get("mode") in ("realistic", "v4") and H_.get("face_limits_m"):
        return 1000.0 * float(H_["face_limits_m"][0]), "env face_limits() vertical half-height (realistic head; Data Agent JSON face height, cross-checked 0.5 mm)"
    return STRIKE_FACE_EDGE_MM, "STRIKE_FACE_EDGE_MM = 53/2 mm, measured spec, single brand (Wishon 919THI 53x105 mm), provisional"

def strike_height_status(med_abs_dz_mm, edge_mm=None):
    if med_abs_dz_mm is None: return "skip"
    edge_mm = STRIKE_FACE_EDGE_MM if edge_mm is None else edge_mm
    return "fail" if med_abs_dz_mm >= edge_mm else "warn" if med_abs_dz_mm > STRIKE_DZ_WARN_MM else "pass"

def strike_extent_rows(info_row):
    d = ((info_row or {}).get("values") or {}).get("deterministic") or {}; m = d.get("median_abs")
    if m is None: return {}
    mk = lambda ok, why: dict(status="info", passed=False, tag="info_only", gating=False, values=dict(median_abs_dz_mm=m, flag=ok), why=[why])
    return {"mine/strike_within_sim_box_info": mk(m <= SIM_BOX_HALF_HEIGHT_MM, f"INFO: median |dz| {m:.1f} mm {'within' if m <= SIM_BOX_HALF_HEIGHT_MM else 'OUTSIDE'} the sim head-box half-height {SIM_BOX_HALF_HEIGHT_MM:g} mm (sim geometry)"),
            "mine/strike_outside_measured_info": mk(m > R2207_DZ_MM, f"INFO: median |dz| {m:.1f} mm {'>' if m > R2207_DZ_MM else '<='} {R2207_DZ_MM:g} mm (R22-07 measured range for ball speed/smash, spin and launch; only 2 of 3 tee series reach +/-18/21 mm)"),
            "mine/strike_beyond_r2207_info": mk(m > R2207_DZ_MM, f"INFO: median |dz| {m:.1f} mm {'> 21 mm: beyond R22-07 data - smash extrapolated (LOW), r2207 spin None' if m > R2207_DZ_MM else '<= 21 mm: within R22-07 data'}")}

def face_edge_eval(centre, dz_mm):
    """Side-by-side model for one episode (Data Agent module at e413c36, which owns the centre-strike guard: face_edge_adjust raises ValueError
    unless centre_dz_mm == 0, so golfphys's own gear effect is never counted twice). The worker's centre re-run records dz_used_m (= 0).
    capped / linear / r2207 spin; smash = R22-07 ratio (MEDIUM, derived, |dz| <= 21 mm; LOW beyond); legacy quadratic smash kept as info."""
    if not centre or centre.get("error") or centre.get("dz_used_m") is None: raise ValueError(f"no centre-strike golfphys result: {centre}")
    from data.driver_face_offcentre import face_edge_adjust
    from eval.golfphys_total import golfphys_total
    m = face_edge_adjust(dict(centre, centre_dz_mm=1000.0 * float(centre["dz_used_m"])), dz_mm)
    out = dict(status=m["status"], valid=m["valid"], capped=None, linear=None, r2207=None)
    if not m["valid"]: return out
    def fly(spin, smash):
        bs = centre["ball_speed_mph"] * smash / centre["smash"]
        try: gp = golfphys_total(bs, m["launch_deg"], spin, 0.0, 0.0); return bs, gp.get("carry_yd"), gp.get("total_over_carry")
        except Exception: return bs, None, None
    sm = m.get("smash"); sconf = "MEDIUM, derived (R22-07 one robot driver ~115 mph; ratio assumed speed-independent)" if abs(dz_mm) <= R2207_DZ_MM else "LOW (beyond R22-07 21 mm: extrapolated)"
    if sm is None: sm, sconf = m["smash_legacy_quadratic"], "LOW (legacy quadratic; R22-07 undefined above +21 mm)"
    out.update(smash_confidence=sconf, smash_legacy_quadratic=m["smash_legacy_quadratic"],
               launch=dict(hotstix=m["launch_deg"], r2207=m.get("launch_deg_r2207")))   # r2207 launch: R22-07 Fig 3 table, MEDIUM, derived; None beyond +/-21 mm
    for nm, spin in (("capped", m["spin_rpm_capped"]), ("linear", m["spin_rpm_linear"]), ("r2207", m.get("spin_rpm_r2207"))):
        if spin is None: continue   # r2207 spin None beyond +/-21 mm = 'no data'
        bs, carry, toc = fly(spin, sm)
        out[nm] = dict(spin_rpm=spin, launch_deg=m["launch_deg"], smash=sm, ball_speed_mph=bs, carry_yd=carry, total_over_carry=toc)
    return out

def _q(xs):
    import numpy as np
    xs = [float(x) for x in xs if x is not None]
    if not xs: return None
    a = np.percentile(xs, [50, 10, 90]); return dict(median=float(a[0]), p10=float(a[1]), p90=float(a[2]), n=len(xs))

FACE_EDGE_LABELS = ["148 mph is a MODEL value (TrajectoWare)", "R22-07 = R&A/USGA equipment research report 'The effect of impact position on driving distance' (~2022; PDF header says Nov 2006 but it cites the 2019 ODS; PDF author metadata Andrew Johnson); spin rises to a peak near -15 mm then falls", "smash: LOW confidence", "leveling off beyond 12.7 mm UNVERIFIED until R22-07 Fig 1 is read",
                    "51.3 rpm/mm and 0.201 deg/mm DERIVED from measured Hotstix data (secondary source)", "side-by-side model only, never the default ball model"]

def face_edge_rows(det_eps, rob_eps=None):
    """INFO rows mine/spin_face_edge_{capped,linear}_info (+ launch/smash/carry/total-over-carry) over deterministic and robustness episodes."""
    R = {}
    ev = lambda E: [face_edge_eval(e["strike_centre"], e["strike_dz_mm"]) for e in E if e.get("strike_centre") and e.get("strike_dz_mm") is not None]
    D, B = ev(det_eps), ev(rob_eps or [])
    if not D: return R
    for nm in ("capped", "linear", "r2207"):
        g = lambda E, f: _q([x[nm][f] for x in E if x["valid"] and x.get(nm)])
        key = f"mine/spin_face_edge_{nm}_info"
        R[key] = dict(status="info", passed=False, tag="info_only", gating=False, model=nm,
            values=dict(deterministic={f: g(D, f) for f in ("spin_rpm", "launch_deg", "smash", "carry_yd", "total_over_carry", "ball_speed_mph")},
                        robustness={f: g(B, f) for f in ("spin_rpm", "launch_deg", "smash", "carry_yd", "total_over_carry")} if B else None,
                        n_off_face=dict(deterministic=sum(1 for x in D if not x["valid"]), robustness=sum(1 for x in B if not x["valid"]))),
            why=[f"INFO: side-by-side face-edge model ({nm}{', +/-12.7 mm saturation as written' if nm == 'capped' else ', extrapolated linearly beyond 12.7 mm' if nm == 'linear' else ': digitized R22-07 Fig 1-2, under Evaluator review; NOT in any verdict'}) on a golfphys centre strike"] + FACE_EDGE_LABELS)
    lg = lambda E, k: _q([x["launch"][k] for x in E if x["valid"] and x.get("launch")])
    R["mine/launch_face_edge_r2207_info"] = dict(status="info", passed=False, tag="info_only", gating=False,
        values=dict(deterministic=dict(r2207=lg(D, "r2207"), hotstix=lg(D, "hotstix")), robustness=dict(r2207=lg(B, "r2207"), hotstix=lg(B, "hotstix")) if B else None,
                    n_r2207_none=dict(deterministic=sum(1 for x in D if x["valid"] and x.get("launch") and x["launch"]["r2207"] is None))),
        why=["INFO: launch under R22-07 Fig 3 averaged table (MEDIUM, derived; None beyond +/-21 mm; only 2 of 3 tee series reach +/-18/21 mm) next to Hotstix 0.20 deg/mm"])
    lq = _q([x["smash_legacy_quadratic"] for x in D if x["valid"]])
    if lq: R["mine/smash_legacy_quadratic_info"] = dict(status="info", passed=False, tag="info_only", gating=False, values=dict(deterministic=lq, robustness=_q([x["smash_legacy_quadratic"] for x in B if x["valid"]])),
        why=["INFO: legacy quadratic smash (MyGolfSpy-derived, LOW confidence), superseded by the R22-07 ratio"])
    if "mine/spin_face_edge_r2207_info" in R:
        r = R["mine/spin_face_edge_r2207_info"]["values"]
        R["mine/smash_r2207_info"] = dict(status="info", passed=False, tag="info_only", gating=False, model="r2207",
            values=dict(deterministic=r["deterministic"]["smash"], robustness=(r["robustness"] or {}).get("smash")),
            why=["INFO: smash under digitized R22-07 Fig 1-2 (ball-speed ratio vs dz): MEDIUM, derived for |dz| <= 21 mm (one robot driver ~115 mph, ratio assumed speed-independent); LOW beyond"])
    return R

def face_edge_model_verdict(r_v3d, spin_fn):
    """Verdict if spin (deterministic median + robustness median/p10/p90) came from the side-by-side model. Spin passes only if capped AND
    linear AND r2207 all pass where r2207 is defined (|dz| <= 21 mm); r2207 undefined = 'no_data' (not a pass, not a fail)."""
    C = r_v3d["checks"]; M = [C.get(f"mine/spin_face_edge_{n}_info") for n in ("capped", "linear")]; r22 = C.get("mine/spin_face_edge_r2207_info")
    if not all(M): return None
    club = (C.get("shot/club_speed_mph") or {}).get("values"); W = {"skip": -1, "no_data": -1, "pass": 0, "warn": 1, "fail": 2}
    def combo(vals, r22v, club_):
        if None in vals: return "fail"
        ss = [spin_fn(v, club_) for v in vals]
        if r22v is not None: ss.append(spin_fn(r22v, club_))
        w = max(ss, key=lambda x: W.get(x, -1))
        return "no_data" if (w == "pass" and r22v is None) else w
    g = lambda m, part, q: (((m or {}).get("values") or {}).get(part) or {}).get("spin_rpm", {}) and ((((m or {}).get("values") or {}).get(part) or {}).get("spin_rpm") or {}).get(q)
    if any(g(m, "deterministic", "median") is None for m in M): return dict(verdict="n/a (off face)")
    sdet = combo([g(m, "deterministic", "median") for m in M], g(r22, "deterministic", "median"), club)
    C2 = copy.deepcopy(C); C2["shot/spin_rpm"] = dict(C2.get("shot/spin_rpm") or {}, status=sdet, passed=sdet == "pass"); nod = sdet == "no_data"
    rb = C2.get("mine/robustness"); st = None
    if rb and rb.get("values", {}).get("shot", {}).get("spin_rpm") and all(m["values"].get("robustness") for m in M):
        cm = (rb["values"]["shot"].get("club_speed_mph") or {}).get("median")
        st = {q: combo([g(m, "robustness", q) for m in M], g(r22, "robustness", q), cm) for q in ("median", "p10", "p90")}
        C2["mine/robustness"] = _regrade_robust(rb, True, st); nod = nod or "no_data" in st.values()
    lr = (C.get("mine/launch_face_edge_r2207_info") or {}).get("values", {}).get("deterministic") or {}
    lh, l22 = (lr.get("hotstix") or {}).get("median"), (lr.get("r2207") or {}).get("median"); slaunch = None
    if lh is not None and "shot/launch_deg" in C2:
        inb = lambda x: LAUNCH_BAND[0] <= x <= LAUNCH_BAND[1]
        slaunch = "fail" if (not inb(lh) or (l22 is not None and not inb(l22))) else ("no_data" if l22 is None else "pass")
        C2["shot/launch_deg"] = dict(C2["shot/launch_deg"], status=slaunch, passed=slaunch == "pass"); nod = nod or slaunch == "no_data"
    S = summarize(C2); v = S["verdict"]
    if v == "PASS" and nod: v = "no data (r2207 undefined)"
    return dict(verdict=v, n_pass=S["n_pass"], n_warn=S["n_warn"], n_fail=S["n_fail"], spin_status_det=sdet, spin_status_robust=st, launch_status_det=slaunch, launch_rule="BOTH Hotstix 0.20 deg/mm and R22-07 Fig 3 launch in 7-16 deg (deterministic median); r2207 None = no data",
                rule="spin passes only if capped AND linear AND r2207 (where defined, |dz|<=21 mm) pass; r2207 undefined = no data")

def strike_height_row(info_row, edge=None):
    d = ((info_row or {}).get("values") or {}).get("deterministic") or {}; m = d.get("median_abs")
    edge_mm, edge_src = edge or (STRIKE_FACE_EDGE_MM, "STRIKE_FACE_EDGE_MM = 53/2 mm, measured spec, single brand (Wishon 919THI 53x105 mm), provisional")
    s = strike_height_status(m, edge_mm)
    return dict(status=s, passed=s == "pass", tag="provisional", gating=True, values=dict(median_abs_dz_mm=m, median_dz_mm=d.get("median")),
                expected=dict(pass_max_mm=STRIKE_DZ_WARN_MM, fail_at_mm=edge_mm, fail_at_source=edge_src),
                why=[f"PROVISIONAL (v3d only): deterministic median |dz| {m:.1f} mm; WARN > {STRIKE_DZ_WARN_MM:g} mm (design choice, not sourced), FAIL >= {edge_mm:g} mm face edge ({edge_src})"] if m is not None else ["no strike data"],
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
    if (C.get("mine/strike_dz_info") or {}).get("status") == "info": C["mine/strike_height"] = strike_height_row(C["mine/strike_dz_info"], face_edge_for(r))
    if (C.get("mine/strike_dz_info") or {}).get("status") == "info": C.update(strike_extent_rows(C["mine/strike_dz_info"]))
    if r.get("strike_episodes") and "mine/spin_face_edge_capped_info" not in C:   # side-by-side face-edge model (INFO rows) from the run's per-episode strike records
        C.update(face_edge_rows(r["strike_episodes"], [e for e in (r.get("robustness_episodes") or []) if e.get("contact")]))
    S = summarize(C)
    r.update(checks_passed=S["n_pass"], n_checks=S["n_checks"], n_warn=S["n_warn"], n_fail=S["n_fail"], n_skip=S["n_skip"], n_info=S["n_info"], verdict=S["verdict"])
    r["harness_v3"] = dict(r.get("harness_v3") or {}, harness="v3d", base_run="v3c")
    return r

def apply_v3d_flagged(r, r_tee0=None):
    """r_tee0 (optional): the SAME checkpoint scored at tee_dz 0 (the v3c run). If r is PASS but apply_v3d(r_tee0) is not, the verdict is
    'not a pass (new-tee-only)': it passes only because of the crown-level tee."""
    out = apply_v3d(r, True)
    out["new_tee_only"] = False
    if r_tee0 is not None:
        cf = apply_v3d(r_tee0, True); out["tee0_counterfactual"] = dict(verdict=cf["verdict"], n_pass=cf["checks_passed"], n_warn=cf["n_warn"], n_fail=cf["n_fail"],
                                                                        fails=sorted(k for k, v in cf["checks"].items() if v.get("status") == "fail"))
        if out["verdict"] == "PASS" and cf["verdict"] != "PASS": out["verdict"] = "not a pass (new-tee-only)"; out["new_tee_only"] = True
    if out["verdict"] == "PASS" and apply_v3d(r, False)["verdict"] != "PASS":
        out["verdict"] = "not a pass (spin-band-only)"; out["spin_band_only"] = True
    else: out["spin_band_only"] = False
    fm = face_edge_model_verdict(out, lambda rpm, club: spin_status(rpm, club, True))
    out["face_edge_model"] = fm; out["face_edge_model_only"] = False
    if fm and fm.get("verdict") == "PASS" and out["verdict"] != "PASS":
        out["face_edge_model_only"] = True; out["face_edge_model"]["note"] = "not a pass (face-edge-model-only)"
    return out
