#!/usr/bin/env python3
"""Autonomous imitation-annealing loop (safe to run unattended).
For each seed (<= --max_parallel pipelines at once) and each stage w in --stages (script weight, descending):
  train (train.train_imitate: distill teacher + PPO fine-tune, warm start from previous stage) -> gate-eval (eval.eval_gate, evaluator protocol, det + stochastic)
  -> append a row to results/TRAINING_NOTES.md (file-locked) -> commit ONLY this loop's own files -> advance only if the stage gate passes (else one retry with
  more distillation data, then stop that seed). Logs: logs/auto_loop_<seed>.log. No pushing, no messaging; OMP_NUM_THREADS=1.
  python scripts/auto_loop.py --seeds 51 52 53 --stages 0.75 0.5 0.25 0.0 --prefix imit
Gate (both deterministic AND stochastic): contact>=99%, lateral std<=2.73 m, 5<=launch mean<=20 deg, carry>=30 m, landed>=90%. Ideal flags (launch 8-14, carry>=100) are only reported.
"""
import argparse, fcntl, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PY = os.environ.get("HGS_PY", sys.executable); ENV = dict(os.environ, OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", PYTHONPATH=str(ROOT))
LOCK = ROOT / "logs" / ".auto_loop.lock"


def log(seed, msg):
    line = f"[{time.strftime('%H:%M:%S')}] seed {seed}: {msg}"; print(line, flush=True)
    with open(ROOT / "logs" / f"auto_loop_{seed}.log", "a") as f: f.write(line + "\n")


def run(cmd, logf):
    with open(ROOT / "logs" / logf, "w") as f: return subprocess.run(cmd, cwd=ROOT, env=ENV, stdout=f, stderr=subprocess.STDOUT).returncode


def passes(m):
    ok = m["contact_rate"] >= 0.99 and m["lateral_std"] <= 2.73 and 5 <= m["launch_elev_mean_deg"] <= 20 and m["mean_carry"] >= 30 and m["landed_fraction"] >= 0.90
    return bool(ok)


def locked(fn):
    with open(LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try: return fn()
        finally: fcntl.flock(lk, fcntl.LOCK_UN)


def commit(paths, msg):
    def f():
        ex = [p for p in paths if (ROOT / p).exists()]
        subprocess.run(["git", "add", "--"] + ex, cwd=ROOT); subprocess.run(["git", "commit", "-q", "-m", msg, "--"] + ex, cwd=ROOT)
    locked(f)


def note(text):
    def f():
        with open(ROOT / "results" / "TRAINING_NOTES.md", "a") as fh: fh.write(text)
    locked(f)


def stage(seed, prefix, w, prev, retry, a):
    name = f"{prefix}_w{int(w * 100):03d}_s{seed}"; fct = max(1.0 - w, 0.25); ls = [round(fct * x, 4) for x in (2.4, 0.7, 0.15, 0.15)]
    cmd = [PY, "-m", "train.train_imitate", "--name", name, "--seed", str(seed), "--stage_w", str(w), "--learn_scale"] + [str(x) for x in ls] + ["--ppo_steps", str(a.ppo_steps), "--track_weight", str(a.track_weight)]
    if retry: cmd += ["--bc_eps", "300", "--bc_epochs", "600", "--bc_noise", "0.005"]
    if prev: cmd += ["--init_model", prev]
    log(seed, f"TRAIN {name} w={w} learn_scale={ls} retry={retry}")
    if run(cmd, f"{name}.log") != 0: log(seed, "train failed"); return None
    log(seed, "GATE"); run([PY, "-m", "eval.eval_gate", name, "100", "4000"], f"gate_{name}.log")
    gp = ROOT / "results" / f"gate_{name}.json"
    if not gp.exists(): log(seed, "gate failed"); return None
    g = json.load(open(gp)); r = json.load(open(ROOT / "results" / f"{name}.json")); d, s, z = g["policy_det"], g["policy_stoch"], g["scripted_zero_residual"]
    ok = passes(d) and passes(s); L = r["learned"]
    row = (f"| {name} | {w} | {L['action_norm_frac_from_policy']:.2f} / {L['traj_rms_dev_from_v3_script_rad']:.3f} | det {d['mean_carry']:.1f} / {d['mean_distance']:.1f} | stoch {s['mean_carry']:.1f} / {s['mean_distance']:.1f} | "
           f"{d['lateral_std']:.2f} / {s['lateral_std']:.2f} | {d['launch_elev_mean_deg']:.1f} / {s['launch_elev_mean_deg']:.1f} | {d['contact_rate']:.2f} | {d['peak_club_mph_mean']:.1f} | {'PASS' if ok else 'FAIL'} |\n")
    note(row)
    commit([f"models/.gitkeep", f"results/{name}.json", f"results/gate_{name}.json", f"logs/{name}.log", f"logs/gate_{name}.log", f"logs/auto_loop_{seed}.log", "results/TRAINING_NOTES.md"], f"auto_loop: {name} {'PASS' if ok else 'FAIL'}")
    log(seed, f"{name} gate {'PASS' if ok else 'FAIL'} det carry {d['mean_carry']:.1f} lat {d['lateral_std']:.2f} launch {d['launch_elev_mean_deg']:.1f}; stoch carry {s['mean_carry']:.1f} lat {s['lateral_std']:.2f}")
    return name if ok else False


def pipeline(seed, a):
    prev = None
    for w in a.stages:
        res = stage(seed, a.prefix, w, prev, False, a)
        if res is False: res = stage(seed, a.prefix, w, prev, True, a)
        if not res: log(seed, f"STOP at w={w}"); return
        prev = res
    log(seed, "ALL STAGES PASSED (script-free)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seeds", type=int, nargs="+", default=[51]); ap.add_argument("--stages", type=float, nargs="+", default=[0.75, 0.5, 0.25, 0.0])
    ap.add_argument("--prefix", default="imit"); ap.add_argument("--max_parallel", type=int, default=3); ap.add_argument("--ppo_steps", type=int, default=8000); ap.add_argument("--track_weight", type=float, default=2.0); ap.add_argument("--seed_summary", action="store_true", help="opt-in: after the pipelines, write mean/min across training seeds (eval.seed_summary)")
    a = ap.parse_args(); a.max_parallel = min(a.max_parallel, 3)   # hard cap of 3 parallel pipelines
    (ROOT / "logs").mkdir(exist_ok=True)
    with ThreadPoolExecutor(a.max_parallel) as ex: list(ex.map(lambda s: pipeline(s, a), a.seeds))
    if a.seed_summary: subprocess.run([sys.executable, "-m", "eval.seed_summary", f"{a.prefix}_w000"], cwd=str(ROOT), env=dict(os.environ, PYTHONPATH=str(ROOT)))
