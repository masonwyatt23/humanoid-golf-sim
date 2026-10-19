"""Stage K11 (from K10): golfphys shot objectives in the reference: launch 11-15, spin 2200-2900, descent>=27, total/carry<=1.22; speed>=75; arm peak >=10 ms before club.
Stage K10 (from K8 fitter): + per-kind downswing start delays phase|hip_yaw / phase|waist (pelvis/waist timing), pelvis peak 60-120 ms before club (w10), arm-before-club soft separation, speed>=72 floor.
Stage K8 open-loop reference re-tune (STOCK torque/speed limits only; public-only reference start; zero residual; strike gate 0.25, arm 0.6, club 1.15).
Search: TUNED_KEYS keyframe deltas + t_down + ease exponents (wrist = lag/release timing, hip, waist, shoulder, elbow). Objective: legal forward-strike club speed
+ trunk/hip power (waist_yaw/hip_yaw peak |tau*qd|) + pelvis peak 100-150 ms before club peak + wrist lag retained ~80 ms before impact,
- wrist/shoulder torque-saturation time (300 ms pre-impact), - wrist torque in last 60 ms (passive release), - X-factor>65, - lead GRF>1.5 BW (5 ms), - launch outside 10-15.5, - spin>3000.
Resumable via --out state json. Rank-based ES (same as v5_ref_fit.py)."""
import argparse, json, os, numpy as np
from multiprocessing import Pool
from scripts.v5_ref_openloop import make_env, keys_from_vec
from env.v5_ref import SwingRef, TUNED_KEYS
from golfphys.sim import shot_from_launch
EASE = ["wrist", "hip", "waist", "shoulder", "elbow"]; PHASE = ["hip_yaw", "waist"]
_E = None; ORDER = os.environ.get('K11_ORDER') == '1'; AC_HI = float(os.environ.get('K11_AC_HI', '50')); PEL_W = float(os.environ.get('K11_PEL_W', '10'))
def build(x):
    n = len(TUNED_KEYS); keys = keys_from_vec(x[:n]); td = float(np.clip(0.24 + 0.05 * x[n], 0.20, 0.30))
    for i, g in enumerate(EASE): keys[("ease", g, "k")] = float(np.clip(1.6 * np.exp(0.5 * x[n + 1 + i]), 0.6, 4.0))
    m = n + 1 + len(EASE)
    for i, g in enumerate(PHASE): keys[("phase", g, "d")] = float(np.clip(0.03 * x[m + i], -0.05, 0.12))
    return keys, td
def run(e, ref):
    bw = float(np.sum(e.m.body_mass)) * 9.81; rec = []; orig = e._log_seg
    wr = [i for i in range(e.m.nu) if "wrist" in e.m.actuator(i).name]; sh = [i for i in range(e.m.nu) if "shoulder" in e.m.actuator(i).name]
    tr = [i for i in range(e.m.nu) if any(k in e.m.actuator(i).name for k in ("waist_yaw", "hip_yaw"))]
    lw = [i for i in wr if e.m.actuator(i).name.startswith(e.lead) and ("pitch" in e.m.actuator(i).name or "yaw" in e.m.actuator(i).name)]
    def seg():
        orig(); d = e.d; F = np.abs(d.actuator_force) / e.tau; qd = d.qvel[e.da]; fl, fr = e.foot_forces()
        rec.append((e.contact, F.copy(), np.abs(d.actuator_force * qd), d.qpos[e.qa][lw].copy() if hasattr(e, "qa") else None, (fl if e.lead == "left" else fr) / bw))
    e._log_seg = seg
    try:
        e.reset(seed=0); home = e.q_addr.copy(); e.act_scale[:] = 0.0; t = 0.0; info = {}; term = False; xf = 0.0; tilt = 0.0; zmin = 9.0; rec.clear()
        while t < ref.t_end + 0.1 and not term:
            e.q_addr = ref.q(t); _, _, term, trn, info = e.step(np.zeros(len(home))); t += 0.02; zmin = min(zmin, float(e.d.qpos[2]))
            if not e.contact and len(e.log['xfactor_deg']): xf = max(xf, abs(float(e.log['xfactor_deg'][-1])))
            tilt = max(tilt, float(np.degrees(np.arccos(np.clip(e.d.xmat[e.pel].reshape(3, 3)[2, 2], -1, 1)))))
            if trn: break
        e.q_addr = home
    finally: e._log_seg = orig
    r = dict(contact=bool(e.contact), foul=bool(e.foul), fell=bool(info.get("fell", False)), mph=float(info.get("club_speed_mph", 0.0)), carry=float(info.get("carry_m_noroll", 0.0)),
             launch=float(info.get("launch_deg", 0.0)), spin=float(info.get("spin_rpm", 0.0) or 0.0), xf=xf, tilt=tilt, zmin=zmin, min_head_ball=float(e.min_dist))
    bs = float(info.get("ball_speed_mph", 0.0) or 0.0)
    if r["contact"] and bs > 5 and r["launch"] > 0:
        try:
            shot_ = shot_from_launch(bs * 0.44704, r["launch"], max(r["spin"], 100.0), roll=True); r["descent"] = float(shot_.descent_deg); r["tc"] = float(shot_.total_m / max(shot_.carry_m, 1e-3)); r["smash"] = bs / max(r["mph"], 1e-3)
        except Exception: pass
    ic = next((i for i, x in enumerate(rec) if x[0]), None)
    pre = rec[max(0, (ic or len(rec)) - 60):(ic or len(rec))]
    if pre:
        F = np.array([x[1] for x in pre]); P = np.array([x[2] for x in pre])
        r["wr_sat"] = float((F[:, wr] >= 0.97).mean()); r["sh_sat"] = float((F[:, sh] >= 0.97).mean()); r["wr_last60"] = float(F[-12:, wr].mean())
        r["trunk_W"] = float(P[:, tr].max()); r["grf5"] = float(max(x[4] for x in rec[:ic] if True) if ic else max(x[4] for x in rec))
        if pre[0][3] is not None and len(pre) > 16: r["lag_deg"] = float(np.degrees(np.abs(pre[-16][3] - pre[-1][3]).sum()))   # lead wrist hinge still to release 80 ms before impact
    L = e.log
    if ic and len(L["t"]) > 3:
        n_ = max(int(np.searchsorted(np.array(L["t"]), e.t_contact, side="right")), 2); tt = np.array(L["t"][:n_])
        r["pel_lead_ms"] = 1000 * float(tt[int(np.argmax(np.abs(L["club"][:n_])))] - tt[int(np.argmax(np.abs(L["pelvis"][:n_])))]); r["pel_dps"] = float(np.max(np.abs(L["pelvis"][:n_])))
        pk_ = {k: float(tt[int(np.argmax(np.abs(L[k][:n_])))]) for k in ("pelvis", "thorax", "lead_arm", "club")}; r["thor_arm_ms"] = 1000 * (pk_["lead_arm"] - pk_["thorax"]); r["pel_thor_ms"] = 1000 * (pk_["thorax"] - pk_["pelvis"])
        r["arm_club_ms"] = 1000 * float(tt[int(np.argmax(np.abs(L["club"][:n_])))] - tt[int(np.argmax(np.abs(L["lead_arm"][:n_])))])
    return r
def score(args):
    global _E
    x, cap, mw = args
    if _E is None: _E = make_env()
    e = _E
    try:
        keys, td = build(x); ref = SwingRef(e.names, e.q_addr, e.lead, e.jlo, e.jhi, keys=keys, t_down=td); r = run(e, ref); r["t_down"] = td
    except Exception as ex: return -80.0, {"err": str(ex)[:80]}
    s = 0.0
    if r["contact"] and not r["foul"]:
        s += 20.0 + mw * min(r["mph"], cap) + 0.2 * min(r["carry"], 100.0)
        s += 4.0 * min(r.get("trunk_W", 0.0) / 1500.0, 1.0) + PEL_W * float(np.clip(1 - max(60 - r.get("pel_lead_ms", 0), r.get("pel_lead_ms", 0) - 120, 0) / 60, 0, 1))
        s += (8.0 * float(np.clip(1 - max(10.0 - r.get("arm_club_ms", 0.0), r.get("arm_club_ms", 0.0) - AC_HI, 0.0) / 20.0, -1, 1)) + 6.0 * float(np.clip((r.get("thor_arm_ms", -50.0) - 5.0) / 15.0, -1, 1))
              + 4.0 * float(np.clip((r.get("pel_thor_ms", -50.0) - 5.0) / 15.0, -1, 1))) if ORDER else 4.0 * float(np.clip((r.get("arm_club_ms", 0.0) - 10.0) / 10.0 + 1.0, -1, 1)) - 5.0 * max(75.0 - r["mph"], 0.0)
        s += 3.0 * min(r.get("lag_deg", 0.0) / 40.0, 1.0) - 6.0 * r.get("wr_sat", 0.0) - 3.0 * r.get("sh_sat", 0.0) - 4.0 * r.get("wr_last60", 0.0)
        s += 8.0 * float(np.clip(1 - max(11.0 - r["launch"], r["launch"] - 15.0, 0.0) / 6.0, 0, 1)) + 20.0 * float(np.clip(1 - max(2200.0 - r["spin"], r["spin"] - 2900.0, 0.0) / 7000.0, 0, 1))
        s += 6.0 * min(r.get("descent", 0.0) / 27.0, 1.0) + 8.0 * float(np.clip(1 - max(r.get("tc", 2.0) - 1.22, 0.0) / 0.4, 0, 1)) + 4.0 * float(np.clip((r.get("smash", 0.0) - 1.1) / 0.2, 0, 1))
    else: s += -40.0 * min(r["min_head_ball"], 1.0) - (10.0 if r["foul"] else 0.0)
    s -= 0.6 * max(r["xf"] - 65.0, 0.0) + 30.0 * max(r.get("grf5", 0.0) - 1.5, 0.0)
    s -= 0.4 * max(r["tilt"] - 30.0, 0.0) + 40.0 * max(0.6 - r["zmin"], 0.0) + (30.0 if r["fell"] else 0.0)
    return float(s), r
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="results/v5_runs/stageK8_ref/fit_state.json"); ap.add_argument("--init", default="results/v5_runs/stageK_ref/tuned_keys.json")
    ap.add_argument("--gens", type=int, default=60); ap.add_argument("--pop", type=int, default=48); ap.add_argument("--procs", type=int, default=6); ap.add_argument("--sigma", type=float, default=0.10)
    ap.add_argument("--cap", type=float, default=100.0); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--mph_w", type=float, default=1.0); ap.add_argument("--eval_only", action="store_true")
    a = ap.parse_args(); os.makedirs(os.path.dirname(a.out), exist_ok=True); n = len(TUNED_KEYS) + 1 + len(EASE) + len(PHASE); rng = np.random.default_rng(a.seed)
    mu0 = np.zeros(n)
    if a.init.endswith("fit_state.json"): bx = json.load(open(a.init))["best"]["x"]; mu0[:len(bx)] = bx
    else: init = json.load(open(a.init)); mu0[:len(TUNED_KEYS)] = [init.get("|".join(k), 0.0) for k in TUNED_KEYS]
    if a.eval_only: s, r = score((mu0, a.cap, a.mph_w)); print(round(s, 2), json.dumps(r)); raise SystemExit
    if os.path.exists(a.out): st = json.load(open(a.out)); mu, sig, g0, best = np.array(st["mu"]), np.array(st["sig"]), st["gen"], st["best"]
    else:
        mu, sig, g0, best = mu0, np.full(n, a.sigma), 0, dict(score=-1e9, x=None, r=None); sig[-len(PHASE):] = 0.5; wi = [i for i, k in enumerate(TUNED_KEYS) if k[0].startswith(('wr_', 'elbow', 'sh_')) and k[2] == 'imp']; sig[wi] = 0.25; sig[len(TUNED_KEYS) + 1:len(TUNED_KEYS) + 1 + len(EASE)] = 0.3
    with Pool(a.procs) as pool:
        for g in range(g0, a.gens):
            X = np.vstack([mu[None], mu + sig * rng.standard_normal((a.pop - 1, n))]); X[:, :len(TUNED_KEYS)] = np.clip(X[:, :len(TUNED_KEYS)], -1.8, 1.8); X[:, len(TUNED_KEYS):] = np.clip(X[:, len(TUNED_KEYS):], -2, 2)
            res = pool.map(score, [(x, a.cap, a.mph_w) for x in X]); S = np.array([s for s, _ in res]); o = np.argsort(-S); el = o[: a.pop // 4]
            if S[o[0]] > best["score"]: best = dict(score=float(S[o[0]]), x=X[o[0]].tolist(), r=res[o[0]][1])
            mu = 0.5 * mu + 0.5 * X[el].mean(0); sig = np.maximum(0.7 * sig + 0.3 * X[el].std(0), 0.01)
            json.dump(dict(mu=mu.tolist(), sig=sig.tolist(), gen=g + 1, best=best), open(a.out, "w"))
            print(g, round(float(S[o[0]]), 2), round(float(np.mean(S)), 2), {k: (round(v, 2) if isinstance(v, float) else v) for k, v in res[o[0]][1].items()}, flush=True)
            keys, td = build(np.array(best["x"])); json.dump(dict(keys={"|".join(k): v for k, v in keys.items()}, t_down=td, r=best["r"]), open(a.out.replace("fit_state", "tuned_keys_k11"), "w"), indent=1)
