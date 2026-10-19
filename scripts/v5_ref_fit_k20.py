"""Stage K20 reference search: K17/K19 objective (env K11_*/K17_*/K19_*) with a looser lower body: extra per-stage leg keys
(trail hip_roll/knee/ankle_pitch, lead hip_roll extra, hip_pitch both), separate ease exponents for hip_yaw / knee / ankle and
per-kind downswing delays for hip_pitch / knee / ankle (weight shift + hip clearance timing). STOCK torque, zero residual.
x layout: [K17 vector (N0 + 18 leg keys)] + [extra leg keys] + [ease hip_yaw, knee, ankle] + [phase hip_pitch, knee, ankle]."""
import argparse, json, os, numpy as np
from multiprocessing import Pool
import scripts.v5_ref_fit_k17 as K7
import scripts.v5_ref_fit_k11 as K
from env.v5_ref import TUNED_KEYS
XLEG = [(g, r, s) for (g, r) in (("hip_roll", "trail"), ("knee", "trail"), ("ankle_pitch", "trail"), ("hip_roll", "lead"), ("hip_pitch", "both")) for s in ("top", "imp", "fin")]
XE = ["hip_yaw", "knee", "ankle"]; XP = ["hip_pitch", "knee", "ankle"]; N17 = K7.N0 + len(K7.LEG); N = N17 + len(XLEG) + len(XE) + len(XP)
def build(x):
    keys, td = K7.build(x[:N17]); o = N17
    for k, v in zip(XLEG, x[o:o + len(XLEG)]): keys[k] = keys.get(k, 0.0) + float(v)
    o += len(XLEG)
    for i, g in enumerate(XE): keys[("ease", g, "k")] = float(np.clip(1.6 * np.exp(0.5 * x[o + i]), 0.6, 4.0))
    o += len(XE)
    for i, g in enumerate(XP): keys[("phase", g, "d")] = float(np.clip(0.03 * x[o + i], -0.06, 0.12))
    return keys, td
K.build = build
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--init", required=True)
    ap.add_argument("--gens", type=int, default=400); ap.add_argument("--pop", type=int, default=40); ap.add_argument("--procs", type=int, default=6); ap.add_argument("--sigma", type=float, default=0.05)
    ap.add_argument("--leg_sigma", type=float, default=0.04); ap.add_argument("--ep_sigma", type=float, default=0.1); ap.add_argument("--cap", type=float, default=82.0); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--mph_w", type=float, default=4.0); ap.add_argument("--eval_only", action="store_true")
    a = ap.parse_args(); os.makedirs(os.path.dirname(a.out), exist_ok=True); rng = np.random.default_rng(a.seed); mu0 = np.zeros(N)
    bx = json.load(open(a.init))["best"]["x"]; mu0[:len(bx)] = bx
    if len(bx) == N17: mu0[N17 + len(XLEG)] = bx[len(TUNED_KEYS) + 1 + K.EASE.index("hip")]   # hip_yaw ease starts at the old shared hip ease
    if a.eval_only: s, r = K7.score((mu0, a.cap, a.mph_w)); print(round(s, 2), json.dumps(r)); raise SystemExit
    if os.path.exists(a.out): st = json.load(open(a.out)); mu, sig, g0, best = np.array(st["mu"]), np.array(st["sig"]), st["gen"], st["best"]
    else: mu, sig, g0, best = mu0, np.full(N, a.sigma), 0, dict(score=-1e9, x=None, r=None); sig[K7.N0:] = a.leg_sigma; sig[N17 + len(XLEG):] = a.ep_sigma
    with Pool(a.procs) as pool:
        for g in range(g0, a.gens):
            X = np.vstack([mu[None], mu + sig * rng.standard_normal((a.pop - 1, N))]); X[:, :len(TUNED_KEYS)] = np.clip(X[:, :len(TUNED_KEYS)], -1.8, 1.8); X[:, len(TUNED_KEYS):K7.N0] = np.clip(X[:, len(TUNED_KEYS):K7.N0], -2, 2)
            X[:, K7.N0:N17 + len(XLEG)] = np.clip(X[:, K7.N0:N17 + len(XLEG)], -1.5, 1.5); X[:, N17 + len(XLEG):] = np.clip(X[:, N17 + len(XLEG):], -2, 4)
            res = pool.map(K7.score, [(x, a.cap, a.mph_w) for x in X]); S = np.array([s for s, _ in res]); o = np.argsort(-S); el = o[: a.pop // 4]
            if S[o[0]] > best["score"]: best = dict(score=float(S[o[0]]), x=X[o[0]].tolist(), r=res[o[0]][1])
            mu = 0.5 * mu + 0.5 * X[el].mean(0); sig = np.maximum(0.7 * sig + 0.3 * X[el].std(0), 0.01)
            json.dump(dict(mu=mu.tolist(), sig=sig.tolist(), gen=g + 1, best=best), open(a.out, "w"))
            rr = res[o[0]][1]; print(g, round(float(S[o[0]]), 2), {k: (round(rr[k], 2) if isinstance(rr.get(k), float) else rr.get(k)) for k in ("contact", "mph", "smash", "spin", "launch", "tc", "az", "face_path", "slip_a", "turn_a", "air_steps", "grf5", "pel_lead_ms", "pel_dps", "thor_arm_ms", "arm_club_ms", "trail_share")}, flush=True)
            keys, td = build(np.array(best["x"])); json.dump(dict(keys={"|".join(k): v for k, v in keys.items()}, t_down=td, r=best["r"]), open(a.out.replace("fit_state", "tuned_keys_k17"), "w"), indent=1)
            json.dump({"|".join(k): v for k, v in keys.items()}, open(a.out.replace("fit_state.json", "tuned_keys_flat.json"), "w"), indent=1)
