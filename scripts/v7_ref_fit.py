"""V7 open-loop reference refit in the v4 env (V5_ENV_V4=1 required), tee 1.5 in, aimed at face centre. Starts from a flat keys file (default K32);
x = per-key deltas (joint keys 0.05 rad/unit, il 0.03, phase 0.01 s, ease k x exp(0.1 x), pc 0.1). t_down fixed. Stock torque (env unchanged).
Scorer fixes vs v5_ref_fit*: contact only counts if the env registered a real on-face strike (e.contact and not e.off_face; ball_hit_info dz/dy logged), tee_mode 1.5in, and AoA
is read from the env's per-step info. Objective = mean over a nominal start + NS noisy address starts (harness scale: joints U(+-0.026 rad), vel U(+-0.05), ball +-1 cm,
floor mu U(0.7,1.05)) of per-start terms, minus dz/dy spread across starts. Terms: contact base + club mph (cap 85); dz in [0,+3] mm; |dy|<=5 mm; plant (slip/lift);
aim (|az|<=3, |face-path|<=4); AoA 0..+3; launch 12-15; smash>=1.40; arm->club peak >=20 ms; pelvis peak >=250 deg/s; lead GRF <=1.7 BW (soft)."""
import os, sys, json, argparse, numpy as np
from multiprocessing import Pool
assert os.environ.get("V5_ENV_V4") == "1", "run with V5_ENV_V4=1"
import scripts.v5_ref_fit_k11 as K
from scripts.v5_ref_openloop import make_env
from env.v5_ref import SwingRef
MM = 1e-3; NS = int(os.environ.get("V7_NS", "6")); TD = float(os.environ.get("V7_TDOWN", "0.2723206007952667"))
BASE = None; KEYS = None; _E = None
def scale(k):
    g = k[0]; return 0.03 if g == "il" else 0.01 if g == "phase" else 0.1 if g == "pc" else 0.05
def build(x):
    out = {}
    for k, v, xi in zip(KEYS, BASE, x):
        if k[0] == "ease": out[k] = float(np.clip(v * np.exp(0.1 * xi), 0.6, 4.0))
        elif k[0] == "phase": out[k] = float(np.clip(v + 0.01 * xi, -0.05, 0.12))
        elif k[0] == "il": out[k] = float(np.clip(v + 0.03 * xi, -0.5, 0.5))
        else: out[k] = float(v + scale(k) * xi)
    return out
def one(e, ref, pid):
    r0 = e.reset; st = e.step; last = {}
    def reset(*a, **kw):
        out = r0(*a, **kw)
        if pid is not None:
            g = np.random.default_rng(7000 + pid); e.d.qpos[e.qa] += g.uniform(-0.026, 0.026, len(e.qa)); e.d.qvel[e.da] += g.uniform(-0.05, 0.05, len(e.da))
            e.m.geom_friction[e.floor, 0] = g.uniform(0.7, 1.05); e.tee[:2] += g.uniform(-0.01, 0.01, 2); import mujoco; mujoco.mj_forward(e.m, e.d)
        return out
    def step(a):
        o = st(a); i = o[4]
        if "aoa_deg" in i and e.contact and "aoa" not in last: last["aoa"] = float(i["aoa_deg"])
        return o
    e.reset = reset; e.step = step
    try: r = K.run(e, ref)
    finally:
        del e.reset; del e.step; e.m.geom_friction[e.floor, 0] = 1.0
    hit = e.ball_hit_info or {}; on = bool(e.contact) and not getattr(e, "off_face", False) and not r.get("foul")
    r.update(on_face=on, dz=hit.get("dz") if on else None, dy=hit.get("dy") if on else None, aoa=last.get("aoa"))
    return r
def term(r, cap=85.0):
    if not r["on_face"]: return -40.0 * min(r.get("min_head_ball", 1.0) / 0.1, 1.0) - 30.0 - (20.0 if r.get("fell") else 0.0)
    dz, dy = r["dz"] / MM, r["dy"] / MM; s = 40.0 + 2.0 * min(r["mph"], cap)
    s -= 10.0 * min(max(0.0 - dz, dz - 3.0, 0.0) / 2.0, 5.0) + 8.0 * min(max(abs(dy) - 5.0, 0.0) / 3.0, 5.0)
    s -= 15.0 * min(max(r.get("foot_slip", 0) - 0.03, 0) / 0.02, 3) + 15.0 * min(max(r.get("foot_lift", 0) - 0.01, 0) / 0.01, 3)
    s -= 5.0 * min(max(abs(r.get("az", 0)) - 3.0, 0) / 2.0, 4) + 5.0 * min(max(abs(r.get("face_path", 0)) - 4.0, 0) / 2.0, 4)
    a = r.get("aoa"); s -= 5.0 * (min(max(0.0 - a, a - 3.0, 0.0) / 2.0, 4) if a is not None else 4)
    la = r.get("launch", 0); s -= 5.0 * min(max(12.0 - la, la - 15.0, 0) / 1.5, 4)
    s += 10.0 * float(np.clip((r.get("smash", 0) - 1.30) / 0.1, 0, 1)); s -= 5.0 * min(max(20.0 - r.get("arm_club_ms", 0), 0) / 10.0, 3)
    s -= 5.0 * min(max(250.0 - r.get("pel_dps", 0), 0) / 50.0, 3) + 5.0 * min(max(r.get("grf5", 0) - 1.7, 0) / 0.3, 3) + (30.0 if r.get("fell") else 0.0)
    return float(s)
def score(x):
    global _E
    if _E is None: _E = make_env(); _E.detail_info = True; _E.tee_mode = "1.5in"
    e = _E
    try: ref = SwingRef(e.names, e.q_addr, e.lead, e.jlo, e.jhi, keys=build(x), t_down=TD)
    except Exception as ex: return -200.0, {"err": str(ex)[:80]}
    R = []
    for pid in [None] + list(range(NS)):
        try: R.append(one(e, ref, pid))
        except Exception as ex: R.append(dict(on_face=False, min_head_ball=1.0, err=str(ex)[:60]))
    S = [term(r) for r in R]; on = [r for r in R if r["on_face"]]
    sp = (np.std([r["dz"] for r in on]) / MM + np.std([r["dy"] for r in on]) / MM) if len(on) >= 2 else 20.0
    s = float(np.mean(S)) - 3.0 * min(sp, 20.0)
    n0 = R[0]; summ = dict(nom_on=n0["on_face"], nom_dz=n0.get("dz") and n0["dz"] / MM, nom_dy=n0.get("dy") and n0["dy"] / MM, nom_mph=n0.get("mph"), nom_spin=n0.get("spin"), nom_launch=n0.get("launch"),
                          nom_aoa=n0.get("aoa"), nom_smash=n0.get("smash"), contact_rate=len(on) / len(R), dz_med=float(np.median([r["dz"] for r in on]) / MM) if on else None,
                          dy_med=float(np.median([r["dy"] for r in on]) / MM) if on else None, spread=float(sp), spin_med=float(np.median([r["spin"] for r in on])) if on else None,
                          launch_med=float(np.median([r["launch"] for r in on])) if on else None, arm_club_ms=n0.get("arm_club_ms"), pel_dps=n0.get("pel_dps"), slip=n0.get("foot_slip"), az=n0.get("az"))
    return s, summ
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--init", default="results/v5_runs/stageK32_ref_s1/tuned_keys_flat.json")
    ap.add_argument("--gens", type=int, default=80); ap.add_argument("--pop", type=int, default=24); ap.add_argument("--procs", type=int, default=2); ap.add_argument("--sigma", type=float, default=0.5); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--eval_only", action="store_true")
    a = ap.parse_args()
    d = json.load(open(a.init)); KEYS = [tuple(k.split("|")) for k in d]; BASE = [float(v) for v in d.values()]; n = len(KEYS)
    import scripts.v7_ref_fit as M; M.KEYS, M.BASE = KEYS, BASE   # workers import this module by name
    if a.eval_only: print(json.dumps(score(np.zeros(n)), default=float)); raise SystemExit
    os.makedirs(os.path.dirname(a.out), exist_ok=True); rng = np.random.default_rng(a.seed)
    if os.path.exists(a.out): st = json.load(open(a.out)); mu, sig, g0, best = np.array(st["mu"]), np.array(st["sig"]), st["gen"], st["best"]
    else: mu, sig, g0, best = np.zeros(n), np.full(n, a.sigma), 0, dict(score=-1e9, x=None, r=None)
    def init(k, b):
        import scripts.v7_ref_fit as M2; M2.KEYS, M2.BASE = k, b
    with Pool(a.procs, initializer=init, initargs=(KEYS, BASE)) as pool:
        for g in range(g0, a.gens):
            X = np.vstack([mu[None], mu + sig * rng.standard_normal((a.pop - 1, n))]); X = np.clip(X, -6, 6)
            res = pool.map(M.score, list(X)); S = np.array([s for s, _ in res]); o = np.argsort(-S); el = o[: a.pop // 4]
            if S[o[0]] > best["score"]: best = dict(score=float(S[o[0]]), x=X[o[0]].tolist(), r=res[o[0]][1])
            mu = 0.5 * mu + 0.5 * X[el].mean(0); sig = np.maximum(0.7 * sig + 0.3 * X[el].std(0), 0.05)
            json.dump(dict(mu=mu.tolist(), sig=sig.tolist(), gen=g + 1, best=best, init=a.init, ns=NS, t_down=TD), open(a.out, "w"))
            json.dump({"|".join(k): v for k, v in build(np.array(best["x"])).items()}, open(a.out.replace("fit_state.json", "tuned_keys_flat.json"), "w"), indent=1)
            print(g, round(float(S[o[0]]), 1), round(float(np.mean(S)), 1), {k: (round(v, 2) if isinstance(v, float) else v) for k, v in res[o[0]][1].items()}, flush=True)
