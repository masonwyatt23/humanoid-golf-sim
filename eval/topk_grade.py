"""Fast top-k checkpoint grading for long runs (harness v5 spec section 'top-k'; usable every 250k steps).

Stage 1 PRE-SCREEN (cheap, NOT a grade): v4 env, 1.5 in main row only, 8 deterministic episodes (seed block 4000) + 8 robustness episodes
(seeds 7000-7007, the v4 gate perturbation), no wide/stress friction info rows (--no-robust-info). Up to --jobs snapshots run concurrently
(default 2), all pinned to the CPUs in --cpus (default 0-1). Ranking key (best first): robustness contact, start-direction and plant fractions
(their minimum, then sum), then fewer v4 FAILs, then more v4 passes.
Stage 2 FULL GRADE of the top-k only: the official rows (v4 1.5 in main + v4 crown info [+ v3c, v3d with --full-rows]) exactly as the batch scripts.
Pre-screen numbers are NEVER reported as grades; only stage-2 rows are official.

Paths come from args / env (no machine paths): --v5-repo (read-only Trainer export), HGS_PY or sys.executable.
Usage: python eval/topk_grade.py --v5-repo <ro_export> --out <dir> --k 2 <ckpt_base> [<ckpt_base> ...]"""
import argparse, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "results" / "overnight" / "_run_j_gateoff_gp_v3.py"
PRESCREEN_ARGS = ["--harness", "v4", "--seeds", "4000", "--eps-per-seed", "8", "--robustness", "8", "--no-robust-info"]

def tag_of(ck): p = Path(ck); return f"{p.parent.name}__{p.name}"

def _run(ck, v5_repo, extra, out_json, tee, cpus, py):
    env = dict(os.environ, V3_HEAD="v4", V3_TEE=tee, OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2", NUMEXPR_NUM_THREADS="2")
    env.pop("V3_FRICTION_RANGE", None); env.pop("V3_FACE_H", None)
    cmd = ["taskset", "-c", cpus, py, str(RUNNER), str(ck), "--v5-repo", str(v5_repo)] + extra + ["--json", str(out_json)]
    t0 = time.time(); p = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return dict(rc=p.returncode, wall_s=time.time() - t0, stderr_tail=p.stderr[-400:] if p.returncode else "")

def rank_key(r):
    """r: realism JSON (v4). Higher is better -> returned tuple sorted descending."""
    v = ((r.get("checks") or {}).get("mine/robustness") or {}).get("values") or {}
    fr = [float(v.get(k) or 0.0) for k in ("contact_frac", "start_direction_pass_frac", "lead_foot_plant_pass_frac")]
    return (min(fr), sum(fr), -int(r.get("n_fail", 99)), int(r.get("checks_passed", 0)))

def prescreen(cks, v5_repo, out, jobs=2, cpus="0-1", py=None):
    py = py or os.environ.get("HGS_PY") or sys.executable; out = Path(out); out.mkdir(parents=True, exist_ok=True)
    def one(ck):
        j = out / f"prescreen_{tag_of(ck)}.json"; m = _run(ck, v5_repo, PRESCREEN_ARGS, j, "1.5in", cpus, py)
        r = json.loads(j.read_text()) if m["rc"] == 0 and j.exists() else None
        return dict(ck=str(ck), tag=tag_of(ck), json=str(j), **m, key=list(rank_key(r)) if r else None, verdict=(r or {}).get("verdict"),
                    counts=(f"{r['checks_passed']}/{r['n_warn']}/{r['n_fail']}" if r else None))
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=max(1, int(jobs))) as ex: res = list(ex.map(one, cks))
    ok = sorted([x for x in res if x["key"]], key=lambda x: x["key"], reverse=True)
    return dict(label="PRE-SCREEN ONLY (8 det + 8 robustness eps, v4 1.5in main row, no friction info rows) - NOT a grade", jobs=jobs, cpus=cpus,
                wall_total_s=time.time() - t0, ranked=ok, failed=[x for x in res if not x["key"]])

def full_grade(ck, v5_repo, out, cpus="0-1", py=None, full_rows=False):
    py = py or os.environ.get("HGS_PY") or sys.executable; out = Path(out); t = tag_of(ck); rows = {}
    plan = [("v4_15in", ["--harness", "v4"], "1.5in"), ("v4_crown16", ["--harness", "v4"], "crown")]
    if full_rows: plan += [("v3c_15in", [], "1.5in"), ("v3d_15in", ["--harness", "v3d"], "1.5in")]
    t0 = time.time()
    for name, extra, tee in plan:
        j = out / f"full_{t}_{name}.json"; rows[name] = dict(json=str(j), **_run(ck, v5_repo, extra, j, tee, cpus, py))
        if rows[name]["rc"] != 0 and name == "v4_15in": break
    return dict(ck=str(ck), rows=rows, wall_s=time.time() - t0)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ckpts", nargs="+"); ap.add_argument("--v5-repo", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--k", type=int, default=2); ap.add_argument("--jobs", type=int, default=2); ap.add_argument("--cpus", default="0-1")
    ap.add_argument("--full-rows", action="store_true", help="stage 2 also runs v3c and v3d rows (as the official batch scripts)")
    ap.add_argument("--prescreen-only", action="store_true")
    a = ap.parse_args()
    P = prescreen(a.ckpts, a.v5_repo, a.out, a.jobs, a.cpus); summ = dict(prescreen=P, full=[])
    for x in P["ranked"]: print(f"PRESCREEN {x['tag']}  key {['%.2f' % v if isinstance(v, float) else v for v in x['key']]}  ({x['counts']})  {x['wall_s']:.1f}s")
    for x in P["failed"]: print(f"PRESCREEN FAILED {x['tag']} rc={x['rc']} {x['stderr_tail'][-200:]}")
    print(f"PRESCREEN total {P['wall_total_s']:.1f}s for {len(a.ckpts)} snapshots (jobs {a.jobs})")
    if not a.prescreen_only:
        for x in P["ranked"][:a.k]:
            F = full_grade(x["ck"], a.v5_repo, a.out, a.cpus, full_rows=a.full_rows); summ["full"].append(F); print(f"FULL {x['tag']} {F['wall_s']:.1f}s rc={[r['rc'] for r in F['rows'].values()]}")
    Path(a.out, "topk_summary.json").write_text(json.dumps(summ, indent=1))
if __name__ == "__main__": main()
