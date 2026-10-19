"""Stage K17 open-loop reference re-fit: K11 objective (env K11_*) + lead-foot plant measured like the Evaluator (scott-e 08835a4):
top -> impact vs ADDRESS: slip (sole-site xy), turn (sole yaw), whole-foot airborne run (lead GRF<=1 N or heel AND toe >5 mm up) in 20 ms control steps.
Adds per-leg keys (hip_yaw/hip_pitch lead+trail, ankle_pitch lead, knee lead) so the pelvis can rotate over a planted lead foot. STOCK torque, zero residual.
Usage: K11_... K17_FOOT_W=15 python -m scripts.v5_ref_fit_k17 --init results/v5_runs/stageK16_ref/fit_state.json --out results/v5_runs/stageK17_ref/fit_state.json"""
import argparse, json, os, numpy as np
from multiprocessing import Pool
import scripts.v5_ref_fit_k11 as K
from env.v5_ref import TUNED_KEYS
LEG = [(g, r, s) for (g, r) in (("hip_yaw", "lead"), ("hip_yaw", "trail"), ("hip_pitch", "lead"), ("hip_pitch", "trail"), ("ankle_pitch", "lead"), ("knee", "lead")) for s in ("top", "imp", "fin")]
N0 = len(TUNED_KEYS) + 1 + len(K.EASE) + len(K.PHASE); FW = float(os.environ.get("K17_FOOT_W", "15")); FP_W = float(os.environ.get("K17_FP_W", "0")); SM_W = float(os.environ.get("K17_SM_W", "0")); PA_W = float(os.environ.get("K17_PA_W", "0")); SP_W = float(os.environ.get("K17_SPIN_W", "0")); GR_W = float(os.environ.get("K17_GRF_W", "0")); PD_W = float(os.environ.get("K19_PELDPS_W", "0")); AC_W = float(os.environ.get("K19_AC_W", "0")); TC_W = float(os.environ.get("K19_TC_W", "0")); TR_W = float(os.environ.get("K19_TRAIL_W", "0")); DL_W = float(os.environ.get("K19_DL_W", "0")); _b11 = K.build; _r11 = K.run
def build(x):
    keys, td = _b11(x[:N0])
    for k, v in zip(LEG, x[N0:]): keys[k] = keys.get(k, 0.0) + float(v)
    return keys, td
def sole(e):
    sid = e.m.site(f"{e.lead}_sole_site").id; P = e.d.site_xpos[sid]; R = e.d.site_xmat[sid].reshape(3, 3); hx = float(e.m.site_size[sid][0])
    return np.array([P[0], P[1], (P - hx * R[:, 0])[2], (P + hx * R[:, 0])[2], np.arctan2(R[1, 0], R[0, 0])], float)
def run(e, ref):
    st = dict(a=None, slip=0.0, turn=0.0, run=0, air=0, path=None, aoa=None, dl=None, tr=[]); step0 = e.step
    def step(a):
        out = step0(a); inf = out[-1] if isinstance(out[-1], dict) else {}
        if inf.get("club_path_deg") is not None and st["path"] is None and e.contact: st["path"] = float(inf["club_path_deg"]); st["aoa"] = float(inf.get("aoa_deg", 0.0) or 0.0); st["dl"] = float(inf.get("dynamic_loft_deg", 0.0) or 0.0)
        s = sole(e)
        if st["a"] is None: st["a"] = s
        if e.d.time >= ref.t_top and not e.contact:
            a0 = st["a"]; st["slip"] = max(st["slip"], float(np.hypot(*(s[:2] - a0[:2])))); st["turn"] = max(st["turn"], abs(float((np.degrees(s[4] - a0[4]) + 180) % 360 - 180)))
            gl = float(e.foot_forces()[0 if e.lead == "left" else 1]); air = gl <= 1.0 or (s[2] > a0[2] + 0.005 and s[3] > a0[3] + 0.005)
            st["run"] = st["run"] + 1 if air else 0; st["air"] = max(st["air"], st["run"])
            ff = e.foot_forces(); gt = float(ff[1 if e.lead == "left" else 0]); st["tr"].append((float(e.d.time), gt / max(gt + gl, 1e-6)))
        return out
    e.step = step
    try: r = _r11(e, ref)
    finally: del e.step
    r.update(slip_a=st["slip"], turn_a=st["turn"], air_steps=st["air"], path=st["path"], aoa=st["aoa"], dloft=st["dl"], trail_share=(float(np.mean([v for (tt, v) in st["tr"] if tt >= st["tr"][-1][0] - 0.15])) if st["tr"] else 0.0)); return r
K.build = build; K.run = run; K.FOOT_W = 0.0
def score(args):
    s, r = K.score(args)
    if "err" in r: return s, r
    if r.get("contact"): s += -FP_W * min(abs(r.get("face_path", 30.0)) / 10.0, 4.0) + SM_W * float(np.clip((r.get("smash", 0.0) - 0.9) / 0.45, 0, 1))
    if r.get("contact") and r.get("path") is not None: s -= PA_W * (min(max(abs(r["path"] - 2.0) - 3.0, 0.0) / 8.0, 3.0) + min(max(-1.0 - r["aoa"], r["aoa"] - 3.0, 0.0) / 4.0, 4.0))
    if r.get("contact"): s -= SP_W * float(np.clip((r.get("spin", 9000.0) - 2900.0) / 2000.0, 0, 3)) + GR_W * float(np.clip((r.get("grf5", 3.0) - 1.6) / 0.5, 0, 3))
    if r.get("contact"):
        s += PD_W * float(np.clip(r.get("pel_dps", 0.0) / 350.0, 0, 1)) - AC_W * float(np.clip(max(15.0 - r.get("arm_club_ms", 0.0), r.get("arm_club_ms", 0.0) - 60.0, 0.0) / 15.0, 0, 2))
        s -= TC_W * float(np.clip((r.get("tc", 2.0) - 1.22) / 0.15, 0, 3)) + TR_W * float(np.clip((0.15 - r.get("trail_share", 0.0)) / 0.15, 0, 1)) + DL_W * float(np.clip(max((r.get("dloft") or 20.0) - 14.0, 10.0 - (r.get("dloft") or 20.0), 0.0) / 4.0, 0, 2))
    s -= FW * (min(r["slip_a"] / 0.05, 5.0) + min(r["turn_a"] / 20.0, 5.0) + min(r["air_steps"] / 3.0, 5.0))
    return float(s), r
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--init", required=True)
    ap.add_argument("--gens", type=int, default=150); ap.add_argument("--pop", type=int, default=40); ap.add_argument("--procs", type=int, default=6); ap.add_argument("--sigma", type=float, default=0.05)
    ap.add_argument("--leg_sigma", type=float, default=0.15); ap.add_argument("--cap", type=float, default=80.0); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--mph_w", type=float, default=3.0); ap.add_argument("--eval_only", action="store_true")
    a = ap.parse_args(); os.makedirs(os.path.dirname(a.out), exist_ok=True); n = N0 + len(LEG); rng = np.random.default_rng(a.seed); mu0 = np.zeros(n)
    bx = json.load(open(a.init))["best"]["x"]; mu0[:len(bx)] = bx
    if a.eval_only: s, r = score((mu0, a.cap, a.mph_w)); print(round(s, 2), json.dumps(r)); raise SystemExit
    if os.path.exists(a.out): st = json.load(open(a.out)); mu, sig, g0, best = np.array(st["mu"]), np.array(st["sig"]), st["gen"], st["best"]
    else: mu, sig, g0, best = mu0, np.full(n, a.sigma), 0, dict(score=-1e9, x=None, r=None); sig[N0:] = a.leg_sigma
    with Pool(a.procs) as pool:
        for g in range(g0, a.gens):
            X = np.vstack([mu[None], mu + sig * rng.standard_normal((a.pop - 1, n))]); X[:, :len(TUNED_KEYS)] = np.clip(X[:, :len(TUNED_KEYS)], -1.8, 1.8); X[:, len(TUNED_KEYS):N0] = np.clip(X[:, len(TUNED_KEYS):N0], -2, 2); X[:, N0:] = np.clip(X[:, N0:], -1.0, 1.0)
            res = pool.map(score, [(x, a.cap, a.mph_w) for x in X]); S = np.array([s for s, _ in res]); o = np.argsort(-S); el = o[: a.pop // 4]
            if S[o[0]] > best["score"]: best = dict(score=float(S[o[0]]), x=X[o[0]].tolist(), r=res[o[0]][1])
            mu = 0.5 * mu + 0.5 * X[el].mean(0); sig = np.maximum(0.7 * sig + 0.3 * X[el].std(0), 0.01)
            json.dump(dict(mu=mu.tolist(), sig=sig.tolist(), gen=g + 1, best=best), open(a.out, "w"))
            rr = res[o[0]][1]; print(g, round(float(S[o[0]]), 2), {k: (round(rr[k], 2) if isinstance(rr.get(k), float) else rr.get(k)) for k in ("contact", "mph", "smash", "path", "aoa", "spin", "launch", "tc", "az", "face_path", "slip_a", "turn_a", "air_steps", "grf5", "pel_lead_ms", "pel_dps", "arm_club_ms", "trail_share", "tc", "dloft")}, flush=True)
            keys, td = build(np.array(best["x"])); json.dump(dict(keys={"|".join(k): v for k, v in keys.items()}, t_down=td, r=best["r"]), open(a.out.replace("fit_state", "tuned_keys_k17"), "w"), indent=1)
            json.dump({"|".join(k): v for k, v in keys.items()}, open(a.out.replace("fit_state.json", "tuned_keys_flat.json"), "w"), indent=1)
