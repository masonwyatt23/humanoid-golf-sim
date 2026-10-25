"""Run the Evaluator's UNMODIFIED eval.realism_check scoring (hgs-scott-lb, branch scott-e) on a Stage J checkpoint by swapping only the worker script.
Usage (cwd = hgs-scott-lb, PYTHONPATH=hgs-scott-lb): python <this> <ckpt_base> --json out.json   (club 1.15, arm 0.6, gate 0.25, 3 seeds x 8 eps)"""
import sys, os, json
EV = os.environ.get("HGS_EVAL_REPO") or sys.exit("set HGS_EVAL_REPO to the Evaluator checkout (hgs-scott-lb, branch scott-e)")
sys.path.insert(0, EV)
from pathlib import Path
import eval.realism_check as RC
TR = os.environ.get("HGS_TRAINER_REPO") or sys.exit("set HGS_TRAINER_REPO to the Trainer checkout")
def worker_args(a, repo, ck, arm, sd):
    g = getattr(a, "strike_gate_nx", None)
    return [sys.executable, TR + "/scripts/v5_eval_j_worker.py", str(repo), os.path.abspath(ck), str(a.club_len), str(sd), str(a.eps_per_seed), "{OUT}", str(arm), "off" if g is None else str(g)]
RC.worker_args = worker_args
if __name__ == "__main__":
    sys.argv = [sys.argv[0], sys.argv[1], "--env", "v5", "--club-len", "1.15", "--arm-dist", "0.6", "--strike-gate-nx", "0.25", "--eps-per-seed", "8", "--seeds", "4000,8000,9000"] + sys.argv[2:]
    out = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
    try: RC.main()
    finally:   # slim JSON (Repo Agent): drop per-episode golfphys blocks
        if out and os.path.exists(out):
            d = json.load(open(out))
            def strip(o):
                if isinstance(o, dict):
                    for k in list(o):
                        if k == "golfphys_total" and isinstance(o[k], dict): o[k].pop("episodes", None)
                        strip(o[k])
                elif isinstance(o, list):
                    for v in o: strip(v)
            strip(d); json.dump(d, open(out, "w"), indent=1, default=float)
