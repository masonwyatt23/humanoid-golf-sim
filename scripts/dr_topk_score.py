"""STEP2(c): score one checkpoint on the v4 gate (1.5 in main row, robustness seeds 7000-7023) AND the Evaluator's v5-heldout-1 set (seeds 910000-910023)
in ONE run of the Evaluator harness (--harness v5, hgs-scott-lb checkout containing 1a98372). Scoring only; the DR trainer never sees these seeds/bands.
LOCAL RUN, NOT an official Evaluator score. Env: HGS_EVAL_REPO (required), HGS_PY (default: this interpreter), CPUS (taskset list, default 6-7).
Usage: dr_topk_score.py <ckpt_base> <out.json>"""
import json, os, subprocess, sys, time
ER = os.environ.get("HGS_EVAL_REPO") or sys.exit("set HGS_EVAL_REPO (Evaluator checkout containing harness v5)"); TR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ck, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
env = dict(os.environ, V3_HEAD="v4", V3_TEE="1.5in", PYTHONPATH=".", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1"); env.pop("V3_FRICTION_RANGE", None); env.pop("V3_FACE_H", None)
load = os.getloadavg(); t0 = time.time()
p = subprocess.run(["taskset", "-c", os.environ.get("CPUS", "6-7"), os.environ.get("HGS_PY") or sys.executable, "results/overnight/_run_j_gateoff_gp_v3.py", ck, "--v5-repo", TR, "--harness", "v5", "--heldout-dr", "24", "--no-robust-info", "--json", out + ".raw.json"], cwd=ER, env=env, capture_output=True, text=True)
if p.returncode: print(p.stderr[-1500:]); sys.exit(1)
r = json.load(open(out + ".raw.json")); v = ((r.get("checks") or {}).get("mine/robustness") or {}).get("values") or {}
hv = (((r.get("v5") or {}).get("rows") or {}).get("v5/heldout_dr_robustness") or {}).get("values") or {}
K = ("contact_frac", "start_direction_pass_frac", "lead_foot_plant_pass_frac")
row = dict(ckpt=ck, label="LOCAL RUN of Evaluator harness v5 (v4 verdict + non-gating v5-heldout-1), NOT official", v4_verdict=r.get("verdict"), v4_passed=r.get("checks_passed"), v4_fail=r.get("n_fail"),
           v4=[v.get(k) for k in K], heldout=[hv.get(k) for k in K], wall_s=round(time.time() - t0, 1), load_before=[round(x, 2) for x in load], load_after=[round(x, 2) for x in os.getloadavg()])
json.dump(row, open(out, "w"), indent=1); print(json.dumps(row))
