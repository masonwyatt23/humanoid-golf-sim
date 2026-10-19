"""Stage K22 ground-up reference: K20 vector + explicit bell-velocity (erf) downswing curves per kind: pelvis (hip_yaw), weight shift (hip_roll),
thorax (waist_yaw), lead arm (shoulder, elbow). Each: c = peak-velocity time before impact, w = width. Objective = K19/K20 env weights.
x layout: [K20 vector] + [c,w for PC kinds]. STOCK torque, zero residual."""
import argparse, json, os, numpy as np
from multiprocessing import Pool
import scripts.v5_ref_fit_k20 as K20
import scripts.v5_ref_fit_k17 as K7
import scripts.v5_ref_fit_k11 as K
from env.v5_ref import TUNED_KEYS
_PC = dict([("hip_yaw", 0.10), ("hip_roll", 0.12), ("waist_yaw", 0.07), ("shoulder", float(os.environ.get("K22_SH_C0", "0.035"))), ("elbow", 0.03)]); ARM = [g for g in os.environ.get("K22_ARM", "").split(",") if g]; PC = [(g, _PC[g]) for g in os.environ.get("K22_PC", "hip_yaw,hip_roll,waist_yaw,shoulder,elbow").split(",")]; N = K20.N + 2 * len(PC) + 3 * len(ARM)
def build(x):
    keys, td = K20.build(x[:K20.N]); o = K20.N
    for i, (g, c0) in enumerate(PC):
        keys[("pc", g, "c")] = float(np.clip(c0 + 0.04 * x[o + 2 * i], 0.0, 0.22)); keys[("pc", g, "w")] = float(np.clip(0.05 * np.exp(0.4 * x[o + 2 * i + 1]), 0.012, 0.15))
    o += 2 * len(PC)
    for i, g in enumerate(ARM):   # gentle arm curve: peak 15-40 ms before impact, small blend weight
        keys[("pc", g, "c")] = float(np.clip(0.025 + 0.01 * x[o + 3 * i], 0.015, 0.04)); keys[("pc", g, "w")] = float(np.clip(0.04 * np.exp(0.3 * x[o + 3 * i + 1]), 0.015, 0.1)); keys[("pc", g, "a")] = float(np.clip(0.1 + 0.1 * x[o + 3 * i + 2], 0.0, 1.0))
    return keys, td
XF_W = float(os.environ.get("K22_XF_W", "0")); _s7 = K7.score
def score(args):
    s, r = _s7(args)
    if r.get("contact"): s -= XF_W * max(r.get("xf", 0.0) - 62.0, 0.0)
    return s, r
K7.score = score
K.build = build
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--init", required=True)
    ap.add_argument("--gens", type=int, default=400); ap.add_argument("--pop", type=int, default=48); ap.add_argument("--procs", type=int, default=6); ap.add_argument("--sigma", type=float, default=0.05)
    ap.add_argument("--leg_sigma", type=float, default=0.05); ap.add_argument("--pc_sigma", type=float, default=0.3); ap.add_argument("--cap", type=float, default=85.0); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--mph_w", type=float, default=4.0); ap.add_argument("--eval_only", action="store_true")
    a = ap.parse_args(); os.makedirs(os.path.dirname(a.out), exist_ok=True); rng = np.random.default_rng(a.seed); mu0 = np.zeros(N)
    bx = json.load(open(a.init))["best"]["x"]; mu0[:len(bx)] = bx
    if a.eval_only: s, r = K7.score((mu0, a.cap, a.mph_w)); print(round(s, 2), json.dumps(r)); raise SystemExit
    if os.path.exists(a.out): st = json.load(open(a.out)); mu, sig, g0, best = np.array(st["mu"]), np.array(st["sig"]), st["gen"], st["best"]
    else: mu, sig, g0, best = mu0, np.full(N, a.sigma), 0, dict(score=-1e9, x=None, r=None); sig[K7.N0:K20.N] = a.leg_sigma; sig[K20.N:] = a.pc_sigma
    with Pool(a.procs) as pool:
        for g in range(g0, a.gens):
            X = np.vstack([mu[None], mu + sig * rng.standard_normal((a.pop - 1, N))]); X[:, :len(TUNED_KEYS)] = np.clip(X[:, :len(TUNED_KEYS)], -1.8, 1.8); X[:, len(TUNED_KEYS):] = np.clip(X[:, len(TUNED_KEYS):], -3, 4)
            res = pool.map(K7.score, [(x, a.cap, a.mph_w) for x in X]); S = np.array([s for s, _ in res]); o = np.argsort(-S); el = o[: a.pop // 4]
            if S[o[0]] > best["score"]: best = dict(score=float(S[o[0]]), x=X[o[0]].tolist(), r=res[o[0]][1])
            mu = 0.5 * mu + 0.5 * X[el].mean(0); sig = np.maximum(0.7 * sig + 0.3 * X[el].std(0), 0.01)
            json.dump(dict(mu=mu.tolist(), sig=sig.tolist(), gen=g + 1, best=best), open(a.out, "w"))
            rr = res[o[0]][1]; print(g, round(float(S[o[0]]), 2), {k: (round(rr[k], 2) if isinstance(rr.get(k), float) else rr.get(k)) for k in ("contact", "mph", "smash", "spin", "launch", "tc", "az", "face_path", "slip_a", "turn_a", "air_steps", "grf5", "pel_lead_ms", "pel_dps", "thor_arm_ms", "arm_club_ms", "trail_share")}, flush=True)
            keys, td = build(np.array(best["x"])); json.dump(dict(keys={"|".join(k): v for k, v in keys.items()}, t_down=td, r=best["r"]), open(a.out.replace("fit_state", "tuned_keys_k17"), "w"), indent=1)
            json.dump({"|".join(k): v for k, v in keys.items()}, open(a.out.replace("fit_state.json", "tuned_keys_flat.json"), "w"), indent=1)
