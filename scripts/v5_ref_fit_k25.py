"""K25 ref fit: K22 family objective, scored as the mean over a nominal start plus NP perturbed starts
(robustness-gate noise: joints U(+-1.5 deg), vel U(+-0.05), ball +-1 cm, floor mu U(0.9,1.1)), with extra
low-dynamic-loft / high-descent / spin<=2700 / t/c<=1.22 terms. Stock torque. Reuses the K22 CLI loop."""
import os, sys, numpy as np
import scripts.v5_ref_fit_k22 as K22
import scripts.v5_ref_fit_k17 as K7
import scripts.v5_ref_fit_k11 as K
NP = int(os.environ.get("K25_NP", "2")); DL_HI = float(os.environ.get("K25_DL_HI", "13")); W = float(os.environ.get("K25_W", "6"))
_PID = [None]; _run = K.run
def run(e, ref):
    pid = _PID[0]; r0 = e.reset
    if pid is not None:
        def reset(*a, **k):
            out = r0(*a, **k); g = np.random.default_rng(1000 + pid)
            e.d.qpos[e.qa] += g.uniform(-np.radians(1.5), np.radians(1.5), len(e.qa)); e.d.qvel[e.da] += g.uniform(-0.05, 0.05, len(e.da))
            e.m.geom_friction[e.floor, 0] = g.uniform(0.9, 1.1)
            if hasattr(e, "tee"): e.tee[:2] += g.uniform(-0.01, 0.01, 2)
            import mujoco; mujoco.mj_forward(e.m, e.d); return out
        e.reset = reset
    try: return _run(e, ref)
    finally:
        if pid is not None: del e.reset; e.m.geom_friction[e.floor, 0] = 1.0
K.run = run
_s = K7.score   # K22-patched chain
def extra(r):
    if not r.get("contact"): return 0.0
    return -W * (min(max(r.get("dloft", 20.0) - DL_HI, 0.0) / 3.0, 3.0) + min(max(r.get("spin", 5000.0) - 2700.0, 0.0) / 500.0, 6.0) + min(max(r.get("tc", 1.6) - 1.22, 0.0) / 0.05, 4.0)) + 0.5 * W * float(np.clip((r.get("descent", 0.0) - 24.0) / 6.0, 0.0, 1.0))
def score(args):
    S = []; R = None
    for pid in [None] + list(range(NP)):
        _PID[0] = pid; s, r = _s(args); s += extra(r); S.append(s); R = R or r
        if "err" in r: break
    _PID[0] = None; R = dict(R); R["s_nom"] = S[0]; R["s_min"] = min(S); return float(np.mean(S)), R
K7.score = score
import argparse, json
from multiprocessing import Pool
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--init", required=True)
    ap.add_argument("--gens", type=int, default=400); ap.add_argument("--pop", type=int, default=48); ap.add_argument("--procs", type=int, default=6); ap.add_argument("--sigma", type=float, default=0.05)
    ap.add_argument("--leg_sigma", type=float, default=0.05); ap.add_argument("--pc_sigma", type=float, default=0.3); ap.add_argument("--cap", type=float, default=85.0); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--mph_w", type=float, default=4.0); ap.add_argument("--eval_only", action="store_true")
    a = ap.parse_args(); os.makedirs(os.path.dirname(a.out), exist_ok=True); rng = np.random.default_rng(a.seed); mu0 = np.zeros(K22.N)
    bx = json.load(open(a.init))["best"]["x"]; mu0[:len(bx)] = bx
    if a.eval_only: s, r = score((mu0, a.cap, a.mph_w)); print(round(s, 2), json.dumps(r)); raise SystemExit
    if os.path.exists(a.out): st = json.load(open(a.out)); mu, sig, g0, best = np.array(st["mu"]), np.array(st["sig"]), st["gen"], st["best"]
    else: mu, sig, g0, best = mu0, np.full(K22.N, a.sigma), 0, dict(score=-1e9, x=None, r=None); sig[K22.K7.N0:K22.K20.N] = a.leg_sigma; sig[K22.K20.N:] = a.pc_sigma
    with Pool(a.procs) as pool:
        for g in range(g0, a.gens):
            X = np.vstack([mu[None], mu + sig * rng.standard_normal((a.pop - 1, K22.N))]); X[:, :len(K22.TUNED_KEYS)] = np.clip(X[:, :len(K22.TUNED_KEYS)], -1.8, 1.8); X[:, len(K22.TUNED_KEYS):] = np.clip(X[:, len(K22.TUNED_KEYS):], -3, 4)
            res = pool.map(score, [(x, a.cap, a.mph_w) for x in X]); S = np.array([s for s, _ in res]); o = np.argsort(-S); el = o[: a.pop // 4]
            if S[o[0]] > best["score"]: best = dict(score=float(S[o[0]]), x=X[o[0]].tolist(), r=res[o[0]][1])
            mu = 0.5 * mu + 0.5 * X[el].mean(0); sig = np.maximum(0.7 * sig + 0.3 * X[el].std(0), 0.01)
            json.dump(dict(mu=mu.tolist(), sig=sig.tolist(), gen=g + 1, best=best), open(a.out, "w"))
            rr = res[o[0]][1]; print(g, round(float(S[o[0]]), 2), {k: (round(rr[k], 2) if isinstance(rr.get(k), float) else rr.get(k)) for k in ("contact", "mph", "smash", "spin", "launch", "tc", "az", "face_path", "slip_a", "turn_a", "air_steps", "grf5", "pel_lead_ms", "pel_dps", "thor_arm_ms", "arm_club_ms", "trail_share")}, flush=True)
            keys, td = K22.build(np.array(best["x"])); json.dump(dict(keys={"|".join(k): v for k, v in keys.items()}, t_down=td, r=best["r"]), open(a.out.replace("fit_state", "tuned_keys_k17"), "w"), indent=1)
            json.dump({"|".join(k): v for k, v in keys.items()}, open(a.out.replace("fit_state.json", "tuned_keys_flat.json"), "w"), indent=1)
