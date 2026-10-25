"""V8 refit: v7_ref_fit objective (same scorer fixes, tee 1.5in, v4 env, stock torque) with launch 12-15 deg near-hard on each start AND on the noisy-start median,
AoA window 0..+4, club mph protected (>=67 nominal), plus spread terms for start direction (std of launch azimuth across starts) and dz/dy (as V7).
Warm start: --init = V7 keys (CMA mean x=0 at the V7 keys). Run with V5_ENV_V4=1: python -m scripts.v8_ref_fit --out ... --init results/v5_runs/stageV7_ref_s1/tuned_keys_flat.json"""
import sys, numpy as np
import scripts.v7_ref_fit as V
MM = V.MM; _t7 = V.term
def term(r, cap=85.0):
    s = _t7(r, cap)
    if not r["on_face"]: return s
    a = r.get("aoa"); s += 5.0 * (min(max(0.0 - a, a - 3.0, 0.0) / 2.0, 4) if a is not None else 4) - 5.0 * (min(max(0.0 - a, a - 4.0, 0.0) / 2.0, 4) if a is not None else 4)   # AoA window 0..4 (V8)
    la = r.get("launch", 0); s -= 25.0 * min(max(12.0 - la, la - 15.0, 0) / 1.0, 4)   # near-hard launch
    return float(s)
def score(x):
    if V._E is None: V._E = V.make_env(); V._E.detail_info = True; V._E.tee_mode = "1.5in"
    e = V._E
    try: ref = V.SwingRef(e.names, e.q_addr, e.lead, e.jlo, e.jhi, keys=V.build(x), t_down=V.TD)
    except Exception as ex: return -300.0, {"err": str(ex)[:80]}
    R = []
    for pid in [None] + list(range(V.NS)):
        try: R.append(V.one(e, ref, pid))
        except Exception as ex: R.append(dict(on_face=False, min_head_ball=1.0, err=str(ex)[:60]))
    S = [term(r) for r in R]; on = [r for r in R if r["on_face"]]
    sp = (np.std([r["dz"] for r in on]) / MM + np.std([r["dy"] for r in on]) / MM) if len(on) >= 2 else 20.0
    azs = float(np.std([r.get("az", 0) for r in on])) if len(on) >= 2 else 10.0
    lam = float(np.median([r["launch"] for r in on])) if on else 0.0; n0 = R[0]
    s = float(np.mean(S)) - 3.0 * min(sp, 20.0) - 6.0 * min(azs, 10.0) - 40.0 * min(max(12.0 - lam, lam - 15.0, 0.0), 4.0) - 10.0 * min(max(67.0 - (n0.get("mph") or 0), 0.0), 10.0)
    summ = dict(nom_on=n0["on_face"], nom_dz=n0.get("dz") and n0["dz"] / MM, nom_dy=n0.get("dy") and n0["dy"] / MM, nom_mph=n0.get("mph"), nom_spin=n0.get("spin"), nom_launch=n0.get("launch"),
                nom_aoa=n0.get("aoa"), nom_smash=n0.get("smash"), nom_tc=n0.get("tc"), contact_rate=len(on) / len(R), dz_med=float(np.median([r["dz"] for r in on]) / MM) if on else None,
                dy_med=float(np.median([r["dy"] for r in on]) / MM) if on else None, spread=float(sp), az_std=azs, az_med=float(np.median([r.get("az", 0) for r in on])) if on else None,
                spin_med=float(np.median([r["spin"] for r in on])) if on else None, launch_med=lam, tc_med=float(np.median([r.get("tc", 9) for r in on])) if on else None,
                arm_club_ms=n0.get("arm_club_ms"), pel_dps=n0.get("pel_dps"), slip=n0.get("foot_slip"), az=n0.get("az"))
    return s, summ
V.term = term; V.score = score
if __name__ == "__main__":
    sys.argv[0] = "v7"; import runpy; runpy.run_module("scripts.v7_ref_fit", run_name="__main__", alter_sys=False)
