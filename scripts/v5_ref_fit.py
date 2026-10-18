"""Open-loop fit of Stage J reference keyframe deltas (sim only, public-only reference as the starting point; simple rank-based evolution strategy, no external deps).
Objective (zero residual, strike gate on, arm 0.6, club 1.15): legal forward strike speed (mph, capped), carry, balance (tilt/pelvis height), no fall. Resumable via --out json state."""
import argparse, json, os, time, numpy as np
from multiprocessing import Pool
from scripts.v5_ref_openloop import make_env, run_open_loop, keys_from_vec
from env.v5_ref import SwingRef, TUNED_KEYS
_E = None
def score(args):
    global _E
    x, tdown, cap = args
    if _E is None: _E = make_env()
    e = _E
    try:
        ref = SwingRef(e.names, e.q_addr, e.lead, e.jlo, e.jhi, keys=keys_from_vec(x), t_down=tdown)
        r = run_open_loop(e, ref)
    except Exception as ex: return -50.0, {}
    s = 0.0
    if r["contact"]: s += 20.0 + min(r["mph"], cap) + 0.5 * min(r["carry"], 100.0)
    else: s += -40.0 * min(r["min_head_ball"], 1.0) - (10.0 if r["foul"] else 0.0)
    s -= 0.4 * max(r["max_tilt_deg"] - 30.0, 0.0) + 40.0 * max(0.6 - r["min_pelvis_z"], 0.0) + (30.0 if r["fell"] else 0.0)
    return float(s), r
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="results/v5_runs/stageJ_ref/fit_state.json"); ap.add_argument("--gens", type=int, default=150); ap.add_argument("--pop", type=int, default=48)
    ap.add_argument("--procs", type=int, default=3); ap.add_argument("--tdown", type=float, default=0.27); ap.add_argument("--sigma", type=float, default=0.12); ap.add_argument("--cap", type=float, default=100.0); ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(); os.makedirs(os.path.dirname(a.out), exist_ok=True); n = len(TUNED_KEYS); rng = np.random.default_rng(a.seed)
    if os.path.exists(a.out): st = json.load(open(a.out)); mu, sig, g0, best = np.array(st["mu"]), np.array(st["sig"]), st["gen"], st["best"]
    else: mu, sig, g0, best = np.zeros(n), np.full(n, a.sigma), 0, dict(score=-1e9, x=None, r=None)
    with Pool(a.procs) as pool:
        for g in range(g0, a.gens):
            X = np.vstack([mu[None], mu + sig * rng.standard_normal((a.pop - 1, n))]); X = np.clip(X, -1.8, 1.8)
            res = pool.map(score, [(x, a.tdown, a.cap) for x in X]); S = np.array([s for s, _ in res]); o = np.argsort(-S); el = o[: a.pop // 4]
            if S[o[0]] > best["score"]: best = dict(score=float(S[o[0]]), x=X[o[0]].tolist(), r=res[o[0]][1])
            mu = 0.5 * mu + 0.5 * X[el].mean(0); sig = np.maximum(0.7 * sig + 0.3 * X[el].std(0), 0.01)
            json.dump(dict(mu=mu.tolist(), sig=sig.tolist(), gen=g + 1, best=best), open(a.out, "w"))
            if g % 5 == 0: print(g, round(float(S[o[0]]), 2), round(float(np.mean(S)), 2), {k: (round(v, 2) if isinstance(v, float) else v) for k, v in res[o[0]][1].items()}, flush=True)
    json.dump({"|".join(k): v for k, v in keys_from_vec(np.array(best["x"])).items()}, open(a.out.replace("fit_state", "tuned_keys"), "w"), indent=1)
