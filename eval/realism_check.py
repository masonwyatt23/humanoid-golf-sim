"""One-command realism check for a checkpoint / results JSON.
  python -m eval.realism_check <model.zip | results/<name>.json | <name>> [--env v1|v5] [--eps-per-seed 8] [--club-len 1.05] [--seeds 4000,8000,9000] [--json out.json]
v1 (default): rolls the model out under ITS OWN env kwargs (the results JSON's env_kwargs_full / args, as the gates do) with eval/swing_realism.py's recorder.
v5: the Trainer's G1 env (local commit 71197e6, NOT on origin/main). Run from the Trainer's checkout via a subprocess (`--v5-repo`, default $V5_REPO or the Trainer worktree) because its `env` package collides with this repo's.
    <ckpt> is the checkpoint base (ckpt_*.zip / final.zip with a sibling *_vecnorm.pkl). Uses their tether 0, friction nominal, deterministic.
Prints PASS/WARN/FAIL/SKIP per check and the overall verdict (only PASS is showcase/qualifying-eligible). Run it under `taskset -c 0-1` with OMP/MKL/OPENBLAS threads <= 2."""
import argparse, json, os, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_V5 = os.environ.get("V5_REPO", "/workspace/artifacts/humanoid-golf-scott")

def _v1_spec(target):
    from eval import swing_realism as SR
    p = Path(target); name = p.stem
    if p.suffix == ".zip" and p.parent.name != "models":                       # arbitrary zip: need a sibling results json
        cand = p.with_suffix(".json")
        if cand.exists(): name = p.stem
    for r in SR.registry():
        if r["key"] == name or r.get("model") == name: return r
    rj = ROOT / "results" / f"{name}.json"
    if not rj.exists() and p.suffix == ".json" and p.exists(): rj = p
    if not rj.exists(): sys.exit(f"no results JSON for '{name}' (needs results/{name}.json with env_kwargs_full or args)")
    J = json.loads(rj.read_text()); spec = dict(key=name, kind="policy", tier=J.get("tier", "unknown (see its results JSON)"), label="policy (realism_check)")
    if "env_kwargs_full" not in J and "args" not in J: sys.exit(f"{rj} has neither env_kwargs_full nor args")
    return spec

def run_v1(a):
    from eval import swing_realism as SR
    SR.SEEDS = tuple(int(s) for s in a.seeds.split(","))
    spec = _v1_spec(a.target)
    return SR.evaluate([spec], a.eps_per_seed, a.workers)[spec["key"]]

def resolve_arm_dist(target, arm_dist=None):
    """Stage A -> 0 (TrainEnv); Stage B/C and anything else -> 0.6 (BEnv). Explicit value wins."""
    if arm_dist is not None: return float(arm_dist)
    return 0.0 if "stageA" in str(target) else 0.6

def gate_label(g):
    return "strike gate OFF" if g is None else f"strike gate ON (nx>={g}, v_x>0, v.n>0; foul ends episode)"

def worker_args(a, repo, ck, arm, sd):
    g = getattr(a, "strike_gate_nx", None)
    x = [sys.executable, str(ROOT / "eval" / "_v5_worker.py"), str(repo), os.path.abspath(ck), str(a.club_len), str(sd), str(a.eps_per_seed), "{OUT}", str(arm), "off" if g is None else str(g)]
    if getattr(a, "timing_res_ms", None) or _fine_grf(a): x.append("seg1")   # v3 GRF rule also needs per-substep (2 ms) traces; default rows use legacy_view     # opt-in: worker logs every physics substep (2 ms at dt 0.002); default argv unchanged
    return x

def _fine_grf(a): return getattr(a, "grf_method", "legacy") not in (None, "legacy")

def _strike_mm(r):
    """Strike offset at impact (mm) from the v3 worker's per-episode 'strike' record (env info dy/dz); {} if not logged."""
    s = r.get("strike") or {}
    return {} if s.get("dz_m") is None else dict(strike_dy_mm=1000.0 * float(s["dy_m"]), strike_dz_mm=1000.0 * float(s["dz_m"]), strike_centre=s.get("centre"))

def _pct(xs):
    xs = [float(x) for x in xs if x is not None]
    if not xs: return None
    q = np.percentile(xs, [50, 10, 90]); return dict(median=float(q[0]), p10=float(q[1]), p90=float(q[2]), n=len(xs))

def strike_info_rows(det_eps, rob_eps=None):
    """INFO rows mine/strike_dy_info / mine/strike_dz_info (mm; never gating). dy toward the toe, dz up the face, from the clubhead site (face centre).
    det_eps / rob_eps: per-episode dicts carrying strike_dy_mm / strike_dz_mm (contact episodes only)."""
    R = {}
    for ax in ("dy", "dz"):
        k = f"strike_{ax}_mm"; d = _pct([e.get(k) for e in det_eps]); rb = _pct([e.get(k) for e in (rob_eps or [])]) if rob_eps else None
        if d is not None: d["median_abs"] = float(np.median([abs(float(e[k])) for e in det_eps if e.get(k) is not None]))
        if d is None: continue   # not logged (pre-strike worker): no row, so counts are unchanged
        R[f"mine/strike_{ax}_info"] = dict(status="info", passed=False, tag="info_only", gating=False,
            values=dict(deterministic=d, robustness=rb, units="mm", axis="toe (+)" if ax == "dy" else "up the face (+)"),
            why=[f"INFO only (not gating): strike {ax} at impact, mm from the face centre (env info['{ax}'])"], ref=None)
    return R

def tee_info_rows(T):
    """INFO rows (never gating) from the worker's tee_info: mine/tee_dz_info, mine/face_h_info, mine/tee_height_info (ball centre / bottom above ground from env geometry).
    No rows when the worker predates tee_info, so counts are unchanged."""
    if not T: return {}
    G = T.get("geometry") or {}; A_ = T.get("args") or {}; mm = lambda v: None if v is None else 1000.0 * float(v)
    mk = lambda vals, why: dict(status="info", passed=False, tag="info_only", gating=False, values=vals, why=[why], ref=None)
    R = {"mine/tee_dz_info": mk(dict(tee_dz_used_mm=mm(T.get("tee_dz_used_m")), tee_dz_args_mm=mm(A_.get("tee_dz")), tee_mode_args=A_.get("tee_mode"), harness_tee=T.get("mode"),
                                     ball_dx_used_mm=mm(T.get("ball_dx_used_m")), ball_dx_args_mm=mm(A_.get("ball_dx")), crown=T.get("crown")),
                             ("INFO only: tee offset used (V3_TEE=%s; 'crown' = derived from sim head geometry, crown-level per GOLF.com / Golf Digest / Golf Monthly advice)" % T.get("mode")) + ("; CROWN TEE COMPENSATES FOR THE OVERSIZED SIM HEAD (64 mm box; the default tee is already ~1.5 in): a v3d pass counts only if it also passes at the default tee (Orchestrator, Oct 24); interim until the v4 sourced head" if T.get("mode") == "crown" else "")),
         "mine/face_h_info": mk(dict(face_h_used_mm=mm(T.get("face_h_used_m")), face_h_args_mm=mm(A_.get("face_h")), head_box_height_mm=mm(2 * G["head_half_height_m"]) if G.get("head_half_height_m") else None,
                                     non_default=T.get("face_h_used_m") is not None),
                                "INFO only: env face_h used (None = 64 mm head box; non-None = off-face contacts beyond face_h/2 become misses, which changes what is scored)")}
    if G:
        R["mine/tee_height_info"] = mk(dict(ball_centre_mm=mm(G["ball_centre_z_m"]), ball_bottom_mm=mm(G["ball_bottom_z_m"]), ball_bottom_in=G["ball_bottom_z_m"] / 0.0254,
                                            crown_mm=mm(G["crown_z_m"]), face_centre_mm=mm(G["face_centre_z_m"]), equator_minus_crown_mm=mm(G["ball_centre_z_m"] - G["crown_z_m"]),
                                            ball_minus_face_centre_along_up_mm=mm(G["ball_minus_face_centre_along_up_m"]), sole_mm=mm(G["sole_min_z_m"])),
                                       "INFO only: address geometry above ground (env, after reset): ball centre / bottom (tee peg), head-box crown at the face, face centre")
    return R

def _robust_ep(r, bw):
    """Per-episode numbers for mine/robustness (same definitions as the deterministic rows: golfphys t/c and lateral, ball azimuth, address-referenced plant)."""
    from eval import swing_realism as SR
    from eval.golfphys_total import golfphys_total
    sh = {k: v for k, v in (r.get("shot") or {}).items() if v is not None}; x = r.get("shot_extra") or {}
    out = dict(seed=r.get("seed"), contact=bool(r.get("contact")), perturb=r.get("perturb"))
    if not out["contact"] or not sh.get("ball_speed_mph"): return out
    gp = None
    if sh.get("launch_deg") is not None and x.get("backspin_rpm") is not None and (sh.get("carry_m_noroll") or 0) > 0:
        gp = golfphys_total(sh["ball_speed_mph"], sh["launch_deg"], x["backspin_rpm"], x.get("sidespin_rpm") or 0.0, x.get("azimuth_deg") or 0.0)
    az = x.get("azimuth_deg"); lat = abs(gp["lateral_carry_yd"]) / gp["noroll_carry_yd"] * 100.0 if gp and gp.get("lateral_carry_yd") is not None and (gp.get("noroll_carry_yd") or 0) > 0 else None
    out["sd_status"] = SR.check_start_direction(abs(az) if az is not None else None, lat)[1]["status"]
    fm = None
    if r.get("lead_foot"):
        q = legacy_view(r); imp = q["impact_idx"]; i_top, top_m = SR.top_index(q["t"], q["club_dps"], imp, q.get("t_top"))
        g = np.array(q["grf"], float).reshape(-1, 2)[:, 0 if q["lead"] == "left" else 1]
        fm = SR.lead_foot_plant_metrics(q["t"], q["lead_foot"], g[:len(q["t"])], imp, i_top, q.get("foot_length_m"))
    out["foot_status"] = SR.check_lead_foot_plant(fm, 1, "logged")[1]["status"]
    out.update(club_speed_mph=sh.get("club_speed_mph"), smash=sh.get("smash"), launch_deg=sh.get("launch_deg"), spin_rpm=sh.get("spin_rpm"),
               total_over_carry=(gp or {}).get("total_over_carry"), az_abs=abs(az) if az is not None else None, lat_per100=lat, **_strike_mm(r))
    return out

def resolve_harness(a):
    """Fill unset v3 options from --harness: v3b -> butter + 24 robustness eps (+ wide info row); v2 -> legacy GRF, no robustness."""
    v2 = getattr(a, "harness", "v3c") == "v2"
    if getattr(a, "grf_method", None) is None: a.grf_method = "legacy" if v2 else "butter"
    if getattr(a, "robustness", None) is None: a.robustness = 0 if v2 else 24
    a.robust_wide_info = (not v2) and a.robustness > 0
    return a

def run_robustness(a, repo, ck, arm, env, P=None):
    """mine/robustness (PROVISIONAL, GATING): N seeded perturbed episodes through the v3 J worker. Returns (row, per-episode list)."""
    from eval import robust_grf as RG
    n = int(a.robustness); s0 = int(a.robust_seed0); P = dict(P or RG.default_perturb()); P.update(seed0=s0, n=n)
    x = worker_args(a, repo, ck, arm, s0)
    if "_v3" not in os.path.basename(x[1]):
        return dict(status="skip", passed=False, values=None, why=[f"worker {os.path.basename(x[1])} has no perturb support (needs _j_worker_gp_v3.py)"], ref=None, tag="derived"), []
    x[6] = str(n); x = [y for y in x if y != "seg1"] + ["seg1", "perturb=" + json.dumps({k: P[k] for k in ("joint_deg", "joint_vel", "ball_tol_m", "friction_rand", "friction_range")})]
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f: outp = f.name
    subprocess.run([outp if y == "{OUT}" else y for y in x], check=True, cwd=str(repo), env=env)
    J = json.load(open(outp)); os.unlink(outp)
    if J.get("perturb_spec") is None: return dict(status="skip", passed=False, values=None, why=["worker did not apply the perturbation"], ref=None, tag="derived"), []
    E = [_robust_ep(r, J["bw_N"]) for r in J["eps"]]
    P["floor_mu_nominal"] = J.get("floor_mu_nominal")
    P["floor_mu_note"] = J.get("floor_mu_note")
    return RG.robustness_row(E, P, [s0 + i for i in range(n)]), E

LEGACY_DT = 0.005   # sample interval the v5 path ASSUMED before the 2026-10-19 dt fix (JEnv/BEnv actually log every 4 ms); kept only for reporting
DT_TOL = 0.05       # relative disagreement between declared and measured sample interval that is flagged

def episode_dt(r, declared=None):
    """Sample interval (s) of ONE episode's logged traces, MEASURED from the worker's logged sim time r['t'] (median spacing). The worker's declared dt is
    only a cross-check: pre-fix workers declared 0.005 while logging every 4 ms (seg_every = round(0.005/0.002) = 2 substeps), which inflated every
    timing x1.25. Falls back to the declared dt only if the episode has fewer than 2 samples. Returns (dt, mismatch_flag)."""
    t = np.asarray(r.get("t") or [], float)
    if len(t) < 2:
        if declared is None: raise ValueError("episode has no time axis and the worker declared no dt")
        return float(declared), False
    dt = float(np.median(np.diff(t)))
    if not dt > 0: raise ValueError(f"non-increasing time axis (median spacing {dt})")
    return dt, (declared is not None and abs(float(declared) - dt) > DT_TOL * dt)
SEQ_ROWS = ("kinematic_sequence_order", "kinematic_sequence_timing_ms_before_club_peak")

def legacy_view(r):
    """Default-cadence view of a per-substep (seg1) episode: keep the samples the default worker would have logged (sub_count % seg_every_default == 0),
    so the default (20 ms tie tolerance) rows of a --timing-res-ms run are computed from exactly the default traces."""
    if r.get("seg_every", None) in (None, r.get("seg_every_default")) or not r.get("sub"): return r
    k = int(r["seg_every_default"]); keep = [i for i, s in enumerate(r["sub"]) if s % k == 0]; q = dict(r)
    for f in ("t", "pelvis_dps", "thorax_dps", "arm_dps", "club_dps", "xfactor_deg", "lead_share", "grf", "grf_h", "sub", "lead_foot"):
        if f in r: q[f] = [r[f][i] for i in keep]
    t = np.array(q["t"]); tc = r.get("t_contact")
    q["impact_idx"] = int(np.argmax(t >= tc)) if tc is not None and (t >= tc).any() else len(t) - 1; q["seg_every"] = k
    return q

def timing_res_rows(r, res_ms, chs_mph):
    """Kinematic-sequence order + timing rows for ONE episode at an opt-in timing resolution: the episode's own per-substep traces on the MEASURED sample
    interval (median diff of the logged sim time, not the assumed 5 ms) with the tie tolerance set to res_ms instead of the default 20 ms. Real samples, no interpolation."""
    from realism.checks import check_swing_realism, load_thresholds
    from eval import swing_realism as SR
    import copy
    t = np.array(r["t"], float); dt = float(np.median(np.diff(t))); T2 = copy.deepcopy(load_thresholds()); T2["sequence"]["tie_tolerance_ms"]["value"] = float(res_ms)
    w = np.radians(np.array([r["pelvis_dps"], r["thorax_dps"], r["arm_dps"], r["club_dps"]]).T); n = len(w)
    jt = dict(pelvis_w=w[:, 0], thorax_w=w[:, 1], arm_w=w[:, 2], club_w=w[:, 3])
    res = check_swing_realism(jt, dt, chs_mph=chs_mph if chs_mph and chs_mph > 0 else None, impact_idx=int(r["impact_idx"]), thresholds=T2)
    return [c for c in SR._compact(res, cap_extrapolated=True) if c["name"] in SEQ_ROWS], dt

def run_v5(a):
    from eval import swing_realism as SR
    repo = Path(a.v5_repo); ck = str(Path(a.target).with_suffix("")) if a.target.endswith(".zip") else a.target
    if not (repo / "env" / "v5_golf_env.py").exists(): sys.exit(f"v5 env not found in {repo} (it is a Trainer-local commit, not on origin/main)")
    if not Path(ck + "_vecnorm.pkl").exists(): sys.exit(f"missing {ck}_vecnorm.pkl (PPO checkpoints need VecNormalize stats)")
    arm = resolve_arm_dist(a.target, a.arm_dist); seeds = [int(s) for s in a.seeds.split(",")]; eps = []; bw = None; TEE = None; env = dict(os.environ, OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2", NUMEXPR_NUM_THREADS="2")
    for sd in seeds:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f: outp = f.name
        subprocess.run([outp if x == "{OUT}" else x for x in worker_args(a, repo, ck, arm, sd)], check=True, cwd=str(repo), env=env)
        J = json.load(open(outp)); os.unlink(outp); bw = J["bw_N"]; TEE = J.get("tee_info") or TEE
        for r_ in J["eps"]: r_["_declared_dt"] = J.get("dt")
        eps += J["eps"]
    out = []; gp_rows = []; tres = getattr(a, "timing_res_ms", None)
    for r_raw in eps:
        r = legacy_view(r_raw) if (tres or _fine_grf(a)) else r_raw
        w = np.radians(np.array([r["pelvis_dps"], r["thorax_dps"], r["arm_dps"], r["club_dps"]]).T); n = len(w); imp = r["impact_idx"]
        grf = np.array(r["grf"]).reshape(-1, 2); lead_i = 0 if r["lead"] == "left" else 1; sh = {k: v for k, v in r["shot"].items() if v is not None}
        club = sh.get("club_speed_mph", 0.0)
        jt = dict(pelvis_w=w[:, 0], thorax_w=w[:, 1], arm_w=w[:, 2], club_w=w[:, 3], pelvis=np.zeros(n), thorax=np.radians(np.array(r["xfactor_deg"])), grf_lead_vertical_bw=grf[:n, lead_i] / bw)
        shot = {}
        gp = None
        if sh and sh.get("ball_speed_mph") and sh.get("launch_deg") is not None and r.get("shot_extra") and r["shot_extra"].get("backspin_rpm") is not None and (sh["carry_m_noroll"] or 0) > 0:
            from eval.golfphys_total import golfphys_total
            x = r["shot_extra"]; gp = golfphys_total(sh["ball_speed_mph"], sh["launch_deg"], x["backspin_rpm"], x.get("sidespin_rpm") or 0.0, x.get("azimuth_deg") or 0.0)
            gp.update(env_carry_yd=sh["carry_m_noroll"] * SR.M2YD, env_total_yd=sh["total_m_model"] * SR.M2YD if sh.get("total_m_model") is not None else None)
        if sh:
            shot = dict(club_speed_mph=club, ball_speed_mph=sh.get("ball_speed_mph"), launch_deg=sh.get("launch_deg"), spin_rpm=sh.get("spin_rpm"), carry_yd=sh["carry_m_noroll"] * SR.M2YD if sh.get("carry_m_noroll") is not None else None,
                        total_yd=sh["total_m_model"] * SR.M2YD if sh.get("total_m_model") is not None else None)
            if gp:                                   # total/carry from the independent golfphys recompute (roll model) instead of the env-logged total; env number kept in gp_rows
                shot["total_yd"] = gp["total_yd"]; shot["carry_yd"] = gp["carry_yd"]
        pk = [float(np.degrees(w[:, j]).max()) for j in range(4)]
        dt_ep, dt_mis = episode_dt(r, r_raw.get("_declared_dt"))   # MEASURED sample interval (dt fix); tie tolerance (20 ms) and thresholds unchanged
        gp_rows.append(dict(seed=r.get("seed"), contact=bool(r["contact"]), **(gp or {}))) if gp else None
        out.append(dict(true_contact=bool(r["contact"]), club_mph=club, ball_mph=sh.get("ball_speed_mph"), gp_toc=(gp or {}).get("total_over_carry"), da_swing=SR.da_swing(jt, dt_ep, club, imp), dt_used=dt_ep, dt_declared=r_raw.get("_declared_dt"), dt_mismatch=dt_mis, da_shot=SR.da_shot(shot) if shot else [], seg_peak_dps=pk))
        x_ = r.get("shot_extra") or {}; az = x_.get("azimuth_deg") if r["contact"] else None
        lat = abs(gp["lateral_carry_yd"]) / gp["noroll_carry_yd"] * 100.0 if gp and gp.get("lateral_carry_yd") is not None and (gp.get("noroll_carry_yd") or 0) > 0 else None
        foot_m = top_m = None
        if r.get("lead_foot") and r.get("grf") is not None:
            i_top, top_m = SR.top_index(r["t"], r["club_dps"], imp, r.get("t_top"))
            grf = np.array(r["grf"], float).reshape(-1, 2); lead_i = 0 if r["lead"] == "left" else 1
            flen = r.get("foot_length_m")
            foot_m = SR.lead_foot_plant_metrics(r["t"], r["lead_foot"], grf[:len(r["t"]), lead_i], imp, i_top, flen)
        out[-1].update(az_abs=(abs(az) if az is not None else None), lat_per100=lat, foot_metrics=foot_m, top_method=top_m)
        out[-1].update(_strike_mm(r_raw))
        if _fine_grf(a):   # v3 GRF rule on the raw per-substep trace: window top -> impact, de-spiked
            from eval import robust_grf as RG
            gr = np.array(r_raw["grf"], float).reshape(-1, 2)[:, lead_i] / bw; tr = r_raw["t"]; ir = int(r_raw["impact_idx"])
            it, _m = SR.top_index(tr, r_raw["club_dps"], ir, r_raw.get("t_top"))
            post = RG.POST_IMPACT_S if a.grf_method == "butter" else 0.0
            pk_, mn_, k_ = RG.despike_peak(tr, gr, it, ir, a.grf_method, a.grf_cutoff_hz or RG.BUTTER_CUTOFF_HZ, a.grf_order or RG.BUTTER_ORDER, post_s=post)
            sens_ = {hz: RG.despike_peak(tr, gr, it, ir, "butter", hz, RG.BUTTER_ORDER, post_s=post)[0] for hz in RG.SENS_CUTOFFS_HZ} if a.grf_method == "butter" else {}
            out[-1].update(grf_v3=(pk_, mn_), grf_k=k_, grf_sens=sens_, grf_raw_whole=float((grf[:n, lead_i] / bw).max()))
            if r_raw.get("grf_h"):   # v3c INFO: lead-foot shear/vertical ratio, top -> impact
                gh = np.array(r_raw["grf_h"], float).reshape(-1, 2)[:, lead_i] / bw
                out[-1]["shear"] = RG.shear_ratio(tr, gh, gr, it, ir)
        if tres:
            rows_f, dt_f = timing_res_rows(r_raw, tres, club); out[-1].update(da_tres=rows_f, dt_fine=dt_f, seg_every_fine=r_raw.get("seg_every"), dt_logged_default=float(np.median(np.diff(np.array(r["t"], float)))))
    ok = [e for e in out if e["true_contact"]] or out; C = {}
    C.update(SR.agg_da(ok, "da_swing", "swing")); C.update(SR.agg_da(ok, "da_shot", "shot"))
    pk = {n: SR.med([e["seg_peak_dps"][j] for e in ok]) for j, n in enumerate(("pelvis", "thorax", "arm", "club"))}; bad = [n for n, v in pk.items() if v < SR.MOVE_MIN_DPS]
    k, v = SR._mine("segments_rotate", not bad, [f"{n} does not rotate (peak {pk[n]:.1f} deg/s)" for n in bad], pk, "DERIVED 20 deg/s"); C[k] = v
    for nm in ("ground_contact_weight_shift", "joint_limits", "torque_saturation_smoothness", "tempo", "carry_vs_trackman_band"):
        C[f"mine/{nm}"] = dict(status="skip", passed=False, values=None, why=["not implemented for the v5 recorder (v1 recorder only)"], ref=None, tag="derived")
    k, v = SR.check_start_direction(SR.med([e["az_abs"] for e in ok]), SR.med([e["lat_per100"] for e in ok])); C[k] = v          # GATING, PROVISIONAL (R22-01)
    fe = [e for e in ok if e.get("foot_metrics")]
    if fe:
        keys = ("airborne_max_ctrl_steps", "airborne_max_s", "slip_m", "slip_frac", "turn_deg", "foot_length_m")
        med_m = {k: SR.med([e["foot_metrics"][k] for e in fe if e["foot_metrics"].get(k) is not None]) for k in keys}
        # if every episode skipped turn, keep turn_deg None
        if all(e["foot_metrics"].get("turn_deg") is None for e in fe): med_m["turn_deg"] = None
        k, v = SR.check_lead_foot_plant(med_m, len(fe), (sorted({e["top_method"] for e in fe}) or [None])[0]); C[k] = v
    else:
        k, v = SR.check_lead_foot_plant(None, 0, None); C[k] = v   # GATING, PROVISIONAL (Data Agent judgement)
    k, v = SR.info_total_over_carry_speed_matched(SR.med([e["ball_mph"] for e in ok if e.get("gp_toc") is not None]), SR.med([e["gp_toc"] for e in ok]))   # INFO ONLY: not gating, ignored by summarize
    C[k] = v
    if _fine_grf(a):
        from eval import robust_grf as RG
        from realism.checks import load_thresholds
        band = load_thresholds()["grf"]["lead_vertical_bw"]["value"]
        src = a.grf_source or (RG.GRF_SOURCE if a.grf_method == "butter" and (a.grf_cutoff_hz in (None, RG.BUTTER_CUTOFF_HZ)) and (a.grf_order in (None, RG.BUTTER_ORDER))
                               else "fallback, no source: sustained >=3 consecutive 2 ms samples (k=%s)" % sorted({e.get("grf_k") for e in ok}, key=str) if a.grf_method == "sustain3" else "NO SOURCE GIVEN")
        sens = {hz: [e["grf_sens"][hz] for e in ok if e.get("grf_sens") and e["grf_sens"].get(hz) is not None] for hz in RG.SENS_CUTOFFS_HZ} if a.grf_method == "butter" else None
        row, info = RG.grf_rows([e["grf_v3"] for e in ok if e.get("grf_v3") and e["grf_v3"][0] is not None], a.grf_method, src, band, [e["grf_raw_whole"] for e in ok if e.get("grf_raw_whole") is not None], sens)
        C["swing/grf_lead_vertical_bw"] = row; C["mine/grf_lead_vertical_raw_info"] = info
        if getattr(a, "harness", None) == "v3c": C["mine/lead_foot_shear_ratio_info"] = RG.shear_row([e.get("shear") for e in ok])
    ROB = None
    from eval import robust_grf as RG
    if getattr(a, "robustness", 0):
        C["mine/robustness"], ROB = run_robustness(a, repo, ck, arm, env, RG.default_perturb(getattr(a, "harness", "v3c")))
        if getattr(a, "robust_wide_info", False):   # INFO only: same seeds/noise, env friction U(0.5, 1.2); never gating
            from eval import robust_grf as RG
            w, _ = run_robustness(a, repo, ck, arm, env, RG.wide_perturb(getattr(a, "harness", "v3c")))
            w = dict(w, status="info", passed=False, tag="info_only", gating=False, verdict_if_gating=w.get("status"), why=["INFO only (not gating): robustness under the env's wide friction U(0.5, 1.2)"] + list(w.get("why") or []))
            C["mine/robustness_wide_friction_info"] = w
            if getattr(a, "harness", None) == "v3c":   # INFO only: fixed mu 1.1 stress value (above any golf-shoe value in the notes)
                w, _ = run_robustness(a, repo, ck, arm, env, RG.stress_perturb())
                C["mine/robustness_stress_friction_info"] = dict(w, status="info", passed=False, tag="info_only", gating=False, verdict_if_gating=w.get("status"), why=["INFO only (not gating): robustness at a fixed floor mu 1.1 (stress value; turf_friction_NOTES.md)"] + list(w.get("why") or []))
    if getattr(a, "harness", None) != "v2":   # INFO rows, all v3 harnesses (v3b/v3c/v3d); counts unchanged
        C.update(strike_info_rows([e for e in ok if e["true_contact"]], [e for e in (ROB or []) if e.get("contact")]))
        C.update(tee_info_rows(TEE))
    S = SR.summarize(C); TR = None
    if tres:
        F = SR.agg_da(ok, "da_tres", "swing"); alt = dict(C); alt.update(F); S2 = SR.summarize(alt)
        segs = sorted({e.get("seg_every_fine") for e in ok}, key=str); per_sub = segs == [1]
        method = ("env substeps: worker logged segment speeds at EVERY physics substep (real samples, no interpolation)" if per_sub else
                  f"WARNING: worker did NOT log per substep (seg_every {segs}); rows use the default-cadence traces") + "; rows use the MEASURED sample interval and a %g ms tie tolerance" % tres
        TR = dict(timing_res_ms=float(tres), method=method, per_substep=per_sub,
                  sample_interval_ms=1000 * SR.med([e["dt_fine"] for e in ok]), default_rows=dict(tie_tolerance_ms=20, assumed_sample_interval_ms=1000 * SR.med([e["dt_used"] for e in ok]), pre_fix_assumed_ms=1000 * LEGACY_DT, measured_logged_interval_ms=1000 * SR.med([e["dt_logged_default"] for e in ok])),
                  checks={k.replace("swing/", f"swing@{tres:g}ms/"): v for k, v in F.items()}, verdict_if_these_rows_gate=S2["verdict"], n_warn_if_gate=S2["n_warn"], n_fail_if_gate=S2["n_fail"],
                  gating=False, note="verdict above is the DEFAULT (20 ms) verdict; these rows are reported alongside and do not change it")
    STK = [{k: e.get(k) for k in ("strike_dy_mm", "strike_dz_mm", "strike_centre")} for e in ok if e["true_contact"] and e.get("strike_dz_mm") is not None]
    return dict(tee_info=TEE, strike_episodes=STK, harness_v3=dict(harness=getattr(a, "harness", None), robust_wide_info=getattr(a, "robust_wide_info", False), grf_method=getattr(a, "grf_method", "legacy"), grf_source=getattr(a, "grf_source", None), robustness_n=getattr(a, "robustness", 0), robust_seed0=getattr(a, "robust_seed0", None)), robustness_episodes=ROB, timing_resolution=TR, key=Path(ck).parent.name + "/" + Path(ck).name, arm_dist=arm, strike_gate_nx=getattr(a, "strike_gate_nx", None), n_foul=sum(1 for r in eps if r.get("foul")), env=f"v5 (G1, club_len {a.club_len}, tether 0, {gate_label(getattr(a, 'strike_gate_nx', None))}, arm_dist {arm}{' [BEnv, as B2-B4/C train]' if arm > 0 else ' [TrainEnv; tap-at-address possible]'})", n_episodes=len(out), true_contact=sum(e["true_contact"] for e in out), checks=C, checks_passed=S["n_pass"], n_checks=S["n_checks"], n_warn=S["n_warn"], n_fail=S["n_fail"], n_skip=S["n_skip"], n_info=S["n_info"], verdict=S["verdict"],
                club_mph_median=SR.med([e["club_mph"] for e in ok]), golfphys_total=_gp_summary(gp_rows),
                sample_interval=dict(used_ms=1000 * SR.med([e["dt_used"] for e in out]), declared_ms=(1000 * float(out[0]["dt_declared"]) if out and out[0]["dt_declared"] is not None else None),
                                     n_declared_mismatch=sum(1 for e in out if e["dt_mismatch"]), method="measured median spacing of the worker's logged sim time per episode (dt fix 2026-10-19; pre-fix assumed 5 ms)"))

def _gp_summary(rows):
    """Per-run summary of the golfphys total/carry recompute (medians over true-contact episodes with carry>0). env_* = the env-logged golfphys numbers (carry no roll; total = golfphys roll=True)."""
    from eval import swing_realism as SR
    R = [x for x in rows if x.get("contact") and x.get("carry_yd", 0) > 0]
    if not R: return dict(n=0, note="no contact episode with carry>0; total/carry not computable")
    m = lambda k: SR.med([x[k] for x in R if x.get(k) is not None])
    return dict(n=len(R), source="eval/golfphys_total.py: golfphys.sim.shot_from_launch from measured ball speed / launch / azimuth / back+side spin, roll=True vs roll=False, normal turf (verified vs TrackMan rows, tests/test_golfphys_total.py)",
                carry_yd_median=m("carry_yd"), total_yd_median=m("total_yd"), total_over_carry_median=m("total_over_carry"), descent_deg_median=m("descent_deg"),
                env_carry_yd_median_noroll=m("env_carry_yd"), env_total_yd_median=m("env_total_yd"), env_total_over_carry_median=SR.med([x["env_total_yd"] / x["env_carry_yd"] for x in R if x.get("env_total_yd") and x.get("env_carry_yd")]),
                total_over_carry_max=max(x["total_over_carry"] for x in R), total_over_carry_min=min(x["total_over_carry"] for x in R),
                max_abs_total_diff_vs_env_yd=max(abs(x["total_yd"] - x["env_total_yd"]) for x in R if x.get("env_total_yd") is not None), episodes=R)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter); ap.add_argument("target"); ap.add_argument("--env", default="v1", choices=["v1", "v5"])
    ap.add_argument("--eps-per-seed", type=int, default=8); ap.add_argument("--seeds", default="4000,8000,9000"); ap.add_argument("--workers", type=int, default=2); ap.add_argument("--club-len", type=float, default=1.05)
    ap.add_argument("--arm-dist", type=float, default=None, help="v5 only: 0.6 (default, BEnv) for Stage B/C; 0 (TrainEnv) auto for paths containing stageA"); ap.add_argument("--strike-gate-nx", type=float, default=None, help="v5 only, default OFF: Trainer Stage G+ strike gate (e.g. 0.25), same definition as V5GolfEnv.strike_gate_nx"); ap.add_argument("--v5-repo", default=DEFAULT_V5); ap.add_argument("--json", default="")
    ap.add_argument("--timing-res-ms", type=float, default=None, help="v5 only, opt-in (default OFF = 20 ms tie tolerance, verdict unchanged): ALSO report kinematic-sequence order/timing from per-physics-substep traces with this tie tolerance (e.g. 5), alongside the default rows; not gating")
    ap.add_argument("--grf-method", default=None, choices=["legacy", "sustain3", "butter", "raw"], help="v5 only. legacy (default) = v2 whole-episode raw peak; others = v3 PROVISIONAL rule: window top->impact on per-substep traces, de-spiked (butter = PRIMARY: 4th-order zero-lag Butterworth 50 Hz, window top->impact+20 ms, >=3-sample guard, 12/14 Hz sensitivity info; sustain3 = fallback >=3 consecutive 2 ms samples, top->impact); old value kept as INFO")
    ap.add_argument("--grf-cutoff-hz", type=float, default=None); ap.add_argument("--grf-order", type=int, default=None); ap.add_argument("--grf-source", default=None)
    ap.add_argument("--harness", default="v3c", choices=["v3c", "v3d", "v3b", "v2"], help="v3d (opt-in, under review): the v3c run re-graded by eval/harness_v3d.py (spin 2000-3700 at 70-85 mph, pelvis floor 250, arm->club >=20 ms, club p10 >=0.93x median; docs/HARNESS_V3D_NOTES.md). v3c (default): Butterworth lead-GRF window + mine/robustness gate (friction 0.7-1.05, turf_friction_NOTES.md) + wide (0.5-1.2) and stress (1.1) friction info rows + lead-foot shear ratio info. v3b: gate friction 0.9-1.1 + wide info row. v2: reproduce the v2 rules (whole-episode raw GRF, no robustness rows)"); ap.add_argument("--robustness", type=int, default=None, help="v5 only, PROVISIONAL GATING row mine/robustness: N perturbed episodes (0 = off; v3 runs use 24)"); ap.add_argument("--robust-seed0", type=int, default=7000)
    a = ap.parse_args(); v3d = a.harness == "v3d"
    if v3d: a.harness = "v3c"   # v3d = same v3c episodes, re-graded
    resolve_harness(a); r = run_v5(a) if a.env == "v5" else run_v1(a)
    if v3d:
        from eval.harness_v3d import apply_v3d_flagged; a.harness = "v3d"; r = apply_v3d_flagged(r)
    print(f"\nREALISM {r['verdict']}  {r['key']}  [{r['env'] if 'env' in r else ''}]  episodes {r['n_episodes']} (true contact {r['true_contact']})  pass {r['checks_passed']} warn {r['n_warn']} fail {r['n_fail']} skip {r['n_skip']}" + (f" info {r['n_info']} (not gating)" if r.get('n_info') else ""))
    for n, c in r["checks"].items():
        print(f"  {c['status'].upper():5s} {n}" + (f"  - {'; '.join(x for x in c['why'] if x)[:200]}" if c["status"] in ("fail", "warn") else "") + (f"  - {'; '.join(x for x in c['why'] if x)}" if c["status"] == "info" else ""))
    SI = r.get("sample_interval")
    if SI: print(f"  -- sample interval: {SI['used_ms']:.1f} ms measured from the logged sim time (worker declared {SI['declared_ms'] if SI['declared_ms'] is not None else 'n/a'} ms; {SI['n_declared_mismatch']} episodes disagree); tie tolerance 20 ms and thresholds unchanged")
    TR = r.get("timing_resolution")
    if TR:
        d = TR["default_rows"]; print(f"  -- timing resolution (opt-in, reported ALONGSIDE, not gating): default rows above = 20 ms tie tolerance on default-cadence traces (sample interval used {d['assumed_sample_interval_ms']:.1f} ms = measured {d['measured_logged_interval_ms']:.1f} ms; pre-fix assumed {d.get('pre_fix_assumed_ms', 5):.0f} ms)")
        print(f"     {TR['timing_res_ms']:g} ms rows: {'per-physics-substep traces' if TR['per_substep'] else 'WARNING: NOT per-substep traces'}, measured sample interval {TR['sample_interval_ms']:.1f} ms, tie tolerance {TR['timing_res_ms']:g} ms; verdict if these rows gated: {TR['verdict_if_these_rows_gate']}")
        for n, c in TR["checks"].items(): print(f"  {c['status'].upper():5s} {n}  value {c.get('values', c.get('value'))}" + (f"  - {'; '.join(x for x in c['why'] if x)[:200]}" if c["status"] in ("fail", "warn") else ""))
    if a.json: Path(a.json).write_text(json.dumps(r, indent=1, default=float))
    return 0
if __name__ == "__main__": main()
