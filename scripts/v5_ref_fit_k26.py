"""K26 ref fit: K25 (robust-averaged K22-family objective) + explicit impact shaft-lean keys il|<joint> (gaussian bump about impact, env/v5_ref.py)
on lead wrist roll/yaw/pitch, lead elbow, both shoulder pitch; dynamic-loft band 11-13, spin<=2800, t/c<=1.22 (K25 extra with K26 bands). Stock torque."""
import os
os.environ.setdefault("K25_DL_HI", "13")
import scripts.v5_ref_fit_k25 as K25
from scripts.v5_ref_fit_k25 import *
IL = [g for g in os.environ.get("K26_IL", "right_wrist_roll_joint,right_wrist_yaw_joint,right_wrist_pitch_joint,right_elbow_joint,right_shoulder_pitch_joint,left_shoulder_pitch_joint").split(",") if g]
N = K22.N + len(IL); DLW = float(os.environ.get("K26_DL_W", "25"))
def build(x):
    keys, td = K22.build(x[:K22.N])
    for i, j in enumerate(IL): keys[("il", j)] = float(np.clip(0.1 * x[K22.N + i], -0.5, 0.5))
    return keys, td
K.build = build
def extra2(r):
    if not r.get("contact"): return 0.0
    dl = r.get("dloft", 20.0)
    DL0, DL1 = (float(v) for v in os.environ.get("K26_DL", "11,13").split(",")); LA0, LA1 = (float(v) for v in os.environ.get("K26_LA", "0,99").split(",")); la = r.get("launch", 0.0)
    return -DLW * min(max(DL0 - dl, dl - DL1, 0.0) / 2.0, 4.0) - DLW * min(max(LA0 - la, la - LA1, 0.0) / 1.0, 4.0) - float(os.environ.get("K26_AOA_W", "0")) * min(max(1.0 - (r.get("aoa") if r.get("aoa") is not None else -10.0), (r.get("aoa") or 0.0) - 3.0, 0.0) / 2.0, 4.0) - K25.W * (min(max(r.get("spin", 5000.0) - float(os.environ.get("K26_SPIN_HI", "2800")), 0.0) / 400.0, 6.0) + min(max(r.get("tc", 1.6) - float(os.environ.get("K26_TC_HI", "1.22")), 0.0) / 0.04, 5.0))
def score(args):
    S = []; R = None
    for pid in [None] + list(range(K25.NP)):
        K25._PID[0] = pid; s, r = K25._s(args); s += extra2(r) + 0.5 * K25.W * float(np.clip((r.get("descent", 0.0) - 24.0) / 6.0, 0.0, 1.0)) * bool(r.get("contact")); S.append(s); R = R or r
        if "err" in r: break
    K25._PID[0] = None; R = dict(R); R["s_nom"] = S[0]; R["s_min"] = min(S); return float(np.mean(S)), R
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--init", required=True)
    ap.add_argument("--gens", type=int, default=400); ap.add_argument("--pop", type=int, default=48); ap.add_argument("--procs", type=int, default=6); ap.add_argument("--sigma", type=float, default=0.05)
    ap.add_argument("--leg_sigma", type=float, default=0.05); ap.add_argument("--pc_sigma", type=float, default=0.3); ap.add_argument("--cap", type=float, default=85.0); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--mph_w", type=float, default=4.0); ap.add_argument("--eval_only", action="store_true")
    a = ap.parse_args(); os.makedirs(os.path.dirname(a.out), exist_ok=True); rng = np.random.default_rng(a.seed); mu0 = np.zeros(N)
    bx = json.load(open(a.init))["best"]["x"]; mu0[:len(bx)] = bx[:N]
    if a.eval_only: s, r = score((mu0, a.cap, a.mph_w)); print(round(s, 2), json.dumps(r)); raise SystemExit
    if os.path.exists(a.out): st = json.load(open(a.out)); mu, sig, g0, best = np.array(st["mu"]), np.array(st["sig"]), st["gen"], st["best"]
    else: mu, sig, g0, best = mu0, np.full(N, a.sigma), 0, dict(score=-1e9, x=None, r=None); sig[K22.K7.N0:K22.K20.N] = a.leg_sigma; sig[K22.K20.N:] = a.pc_sigma; sig[K22.N:] = 1.0
    with Pool(a.procs) as pool:
        for g in range(g0, a.gens):
            X = np.vstack([mu[None], mu + sig * rng.standard_normal((a.pop - 1, N))]); X[:, :len(K22.TUNED_KEYS)] = np.clip(X[:, :len(K22.TUNED_KEYS)], -1.8, 1.8); X[:, len(K22.TUNED_KEYS):] = np.clip(X[:, len(K22.TUNED_KEYS):], -3, 4)
            res = pool.map(score, [(x, a.cap, a.mph_w) for x in X]); S = np.array([s for s, _ in res]); o = np.argsort(-S); el = o[: a.pop // 4]
            if S[o[0]] > best["score"]: best = dict(score=float(S[o[0]]), x=X[o[0]].tolist(), r=res[o[0]][1])
            mu = 0.5 * mu + 0.5 * X[el].mean(0); sig = np.maximum(0.7 * sig + 0.3 * X[el].std(0), 0.01)
            json.dump(dict(mu=mu.tolist(), sig=sig.tolist(), gen=g + 1, best=best), open(a.out, "w"))
            rr = res[o[0]][1]; print(g, round(float(S[o[0]]), 2), {k: (round(rr[k], 2) if isinstance(rr.get(k), float) else rr.get(k)) for k in ("contact", "mph", "smash", "spin", "launch", "tc", "az", "face_path", "slip_a", "turn_a", "air_steps", "grf5", "pel_lead_ms", "pel_dps", "thor_arm_ms", "arm_club_ms", "trail_share")}, flush=True)
            keys, td = build(np.array(best["x"])); json.dump(dict(keys={"|".join(k): v for k, v in keys.items()}, t_down=td, r=best["r"]), open(a.out.replace("fit_state", "tuned_keys_k17"), "w"), indent=1)
            json.dump({"|".join(k): v for k, v in keys.items()}, open(a.out.replace("fit_state.json", "tuned_keys_flat.json"), "w"), indent=1)
