"""Run the Evaluator's UNMODIFIED eval.realism_check scoring (hgs-scott-lb, branch scott-e) on a Stage J checkpoint by swapping only the worker script.
Usage (cwd = hgs-scott-lb, PYTHONPATH=hgs-scott-lb): python <this> <ckpt_base> --json out.json   (club 1.15, arm 0.6, gate 0.25, 3 seeds x 8 eps)"""
import sys, os, json
sys.path.insert(0, "/workspace/artifacts/hgs-scott-lb")
from pathlib import Path
import eval.realism_check as RC
TR = "/workspace/artifacts/humanoid-golf-scott"
def worker_args(a, repo, ck, arm, sd):
    g = getattr(a, "strike_gate_nx", None)
    return [sys.executable, TR + "/scripts/v5_eval_j_worker.py", str(repo), os.path.abspath(ck), str(a.club_len), str(sd), str(a.eps_per_seed), "{OUT}", str(arm), "off" if g is None else str(g)]
RC.worker_args = worker_args
if __name__ == "__main__":
    sys.argv = [sys.argv[0], sys.argv[1], "--env", "v5", "--club-len", "1.15", "--arm-dist", "0.6", "--strike-gate-nx", "0.25", "--eps-per-seed", "8", "--seeds", "4000,8000,9000"] + sys.argv[2:]
    RC.main()
