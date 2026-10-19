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
    if getattr(a, "timing_res_ms", None): x.append("seg1")     # opt-in: worker logs every physics substep (2 ms at dt 0.002); default argv unchanged
    return x

LEGACY_DT = 0.005   # sample interval the default v5 path ASSUMES for the logged traces (worker json "dt"); see timing_res_rows for the measured interval
SEQ_ROWS = ("kinematic_sequence_order", "kinematic_sequence_timing_ms_before_club_peak")

def legacy_view(r):
    """Default-cadence view of a per-substep (seg1) episode: keep the samples the default worker would have logged (sub_count % seg_every_default == 0),
    so the default (20 ms tie tolerance) rows of a --timing-res-ms run are computed from exactly the default traces."""
    if r.get("seg_every", None) in (None, r.get("seg_every_default")) or not r.get("sub"): return r
    k = int(r["seg_every_default"]); keep = [i for i, s in enumerate(r["sub"]) if s % k == 0]; q = dict(r)
    for f in ("t", "pelvis_dps", "thorax_dps", "arm_dps", "club_dps", "xfactor_deg", "lead_share", "grf", "sub"): q[f] = [r[f][i] for i in keep]
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
    arm = resolve_arm_dist(a.target, a.arm_dist); seeds = [int(s) for s in a.seeds.split(",")]; eps = []; bw = None; env = dict(os.environ, OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2", NUMEXPR_NUM_THREADS="2")
    for sd in seeds:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f: outp = f.name
        subprocess.run([outp if x == "{OUT}" else x for x in worker_args(a, repo, ck, arm, sd)], check=True, cwd=str(repo), env=env)
        J = json.load(open(outp)); os.unlink(outp); bw = J["bw_N"]; eps += J["eps"]
    out = []; gp_rows = []; tres = getattr(a, "timing_res_ms", None)
    for r_raw in eps:
        r = legacy_view(r_raw) if tres else r_raw
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
        gp_rows.append(dict(seed=r.get("seed"), contact=bool(r["contact"]), **(gp or {}))) if gp else None
        out.append(dict(true_contact=bool(r["contact"]), club_mph=club, ball_mph=sh.get("ball_speed_mph"), gp_toc=(gp or {}).get("total_over_carry"), da_swing=SR.da_swing(jt, 0.005, club, imp), da_shot=SR.da_shot(shot) if shot else [], seg_peak_dps=pk))
        if tres:
            rows_f, dt_f = timing_res_rows(r_raw, tres, club); out[-1].update(da_tres=rows_f, dt_fine=dt_f, seg_every_fine=r_raw.get("seg_every"), dt_logged_default=float(np.median(np.diff(np.array(r["t"], float)))))
    ok = [e for e in out if e["true_contact"]] or out; C = {}
    C.update(SR.agg_da(ok, "da_swing", "swing")); C.update(SR.agg_da(ok, "da_shot", "shot"))
    pk = {n: SR.med([e["seg_peak_dps"][j] for e in ok]) for j, n in enumerate(("pelvis", "thorax", "arm", "club"))}; bad = [n for n, v in pk.items() if v < SR.MOVE_MIN_DPS]
    k, v = SR._mine("segments_rotate", not bad, [f"{n} does not rotate (peak {pk[n]:.1f} deg/s)" for n in bad], pk, "DERIVED 20 deg/s"); C[k] = v
    for nm in ("ground_contact_weight_shift", "joint_limits", "torque_saturation_smoothness", "tempo", "carry_vs_trackman_band"):
        C[f"mine/{nm}"] = dict(status="skip", passed=False, values=None, why=["not implemented for the v5 recorder (v1 recorder only)"], ref=None, tag="derived")
    k, v = SR.info_total_over_carry_speed_matched(SR.med([e["ball_mph"] for e in ok if e.get("gp_toc") is not None]), SR.med([e["gp_toc"] for e in ok]))   # INFO ONLY: not gating, ignored by summarize
    C[k] = v
    S = SR.summarize(C); TR = None
    if tres:
        F = SR.agg_da(ok, "da_tres", "swing"); alt = dict(C); alt.update(F); S2 = SR.summarize(alt)
        segs = sorted({e.get("seg_every_fine") for e in ok}, key=str); per_sub = segs == [1]
        method = ("env substeps: worker logged segment speeds at EVERY physics substep (real samples, no interpolation)" if per_sub else
                  f"WARNING: worker did NOT log per substep (seg_every {segs}); rows use the default-cadence traces") + "; rows use the MEASURED sample interval and a %g ms tie tolerance" % tres
        TR = dict(timing_res_ms=float(tres), method=method, per_substep=per_sub,
                  sample_interval_ms=1000 * SR.med([e["dt_fine"] for e in ok]), default_rows=dict(tie_tolerance_ms=20, assumed_sample_interval_ms=1000 * LEGACY_DT, measured_logged_interval_ms=1000 * SR.med([e["dt_logged_default"] for e in ok])),
                  checks={k.replace("swing/", f"swing@{tres:g}ms/"): v for k, v in F.items()}, verdict_if_these_rows_gate=S2["verdict"], n_warn_if_gate=S2["n_warn"], n_fail_if_gate=S2["n_fail"],
                  gating=False, note="verdict above is the DEFAULT (20 ms) verdict; these rows are reported alongside and do not change it")
    return dict(timing_resolution=TR, key=Path(ck).parent.name + "/" + Path(ck).name, arm_dist=arm, strike_gate_nx=getattr(a, "strike_gate_nx", None), n_foul=sum(1 for r in eps if r.get("foul")), env=f"v5 (G1, club_len {a.club_len}, tether 0, {gate_label(getattr(a, 'strike_gate_nx', None))}, arm_dist {arm}{' [BEnv, as B2-B4/C train]' if arm > 0 else ' [TrainEnv; tap-at-address possible]'})", n_episodes=len(out), true_contact=sum(e["true_contact"] for e in out), checks=C, checks_passed=S["n_pass"], n_checks=S["n_checks"], n_warn=S["n_warn"], n_fail=S["n_fail"], n_skip=S["n_skip"], n_info=S["n_info"], verdict=S["verdict"],
                club_mph_median=SR.med([e["club_mph"] for e in ok]), golfphys_total=_gp_summary(gp_rows))

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
    a = ap.parse_args(); r = run_v5(a) if a.env == "v5" else run_v1(a)
    print(f"\nREALISM {r['verdict']}  {r['key']}  [{r['env'] if 'env' in r else ''}]  episodes {r['n_episodes']} (true contact {r['true_contact']})  pass {r['checks_passed']} warn {r['n_warn']} fail {r['n_fail']} skip {r['n_skip']}" + (f" info {r['n_info']} (not gating)" if r.get('n_info') else ""))
    for n, c in r["checks"].items():
        print(f"  {c['status'].upper():5s} {n}" + (f"  - {'; '.join(x for x in c['why'] if x)[:200]}" if c["status"] in ("fail", "warn") else "") + (f"  - {'; '.join(x for x in c['why'] if x)}" if c["status"] == "info" else ""))
    TR = r.get("timing_resolution")
    if TR:
        d = TR["default_rows"]; print(f"  -- timing resolution (opt-in, reported ALONGSIDE, not gating): default rows above = 20 ms tie tolerance on default-cadence traces (assumed {d['assumed_sample_interval_ms']:.0f} ms/sample, measured {d['measured_logged_interval_ms']:.1f} ms)")
        print(f"     {TR['timing_res_ms']:g} ms rows: {'per-physics-substep traces' if TR['per_substep'] else 'WARNING: NOT per-substep traces'}, measured sample interval {TR['sample_interval_ms']:.1f} ms, tie tolerance {TR['timing_res_ms']:g} ms; verdict if these rows gated: {TR['verdict_if_these_rows_gate']}")
        for n, c in TR["checks"].items(): print(f"  {c['status'].upper():5s} {n}  value {c.get('values', c.get('value'))}" + (f"  - {'; '.join(x for x in c['why'] if x)[:200]}" if c["status"] in ("fail", "warn") else ""))
    if a.json: Path(a.json).write_text(json.dumps(r, indent=1, default=float))
    return 0
if __name__ == "__main__": main()
