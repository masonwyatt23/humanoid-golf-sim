"""Stage 28: SCRIPTED-PARAMETER SEARCH (CMA-ES, black box; NOT neural/learned, NOT distilled) over scripted-swing params.
python -m eval.param_search_s28 <stock|power> <gens> <popsize> <workers>
Objective (maximise): mean_carry(m, single no-roll metres) + 0.1*peak_club_mph, hard constraints via penalty:
 contact>=0.99, lateral_std<=2.7 m; power also spin 1800-3000 rpm and smash<=1.50. 40 eps/candidate at fixed eval seed 6000 (gate seeds are 4000/8000/9000).
Finalists re-evaluated 100 eps at seed 7000. Output results/param_search_s28_<phase>.json"""
import sys, json, math, os, time
if os.environ.get("CMA_PKG_DIR"): sys.path.insert(0, os.environ["CMA_PKG_DIR"])   # optional local cma install
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
phase, GENS, POP, WORKERS = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
if phase == "stock":
    CFG = "configs/fast_scripted_v3_fs1_q23_dz016.json"; OV = {}
    SP = {"q_back": (1.9, 2.6), "t_back": (0.45, 0.9), "t_down": (0.075, 0.13), "wr_rel_start": (0.0, 0.3), "yaw_fin": (-0.08, 0.08),
          "loft_deg": (-50, -32), "ball_x": (0.38, 0.42), "ball_dz": (-0.024, -0.006)}
else:
    CFG = "configs/fast_scripted_v4_power_elbowrange.json"; OV = {"impact_model": {"gain": 1.20, "dz0": 0.017, "k_off": 0.4, "spin_k": 130, "k_side": 3500}, "loft_deg": -28}
    SP = {"q_back": (1.9, 2.5), "t_back": (0.45, 0.9), "t_down": (0.04, 0.09), "wr_rel_start": (0.0, 0.3), "yaw_fin": (-0.08, 0.08),
          "loft_deg": (-34, -24), "ball_x": (0.38, 0.42), "ball_dz": (-0.02, 0.0)}
SCRIPT_KEYS = {"q_back", "t_back", "t_down", "wr_rel_start", "yaw_fin"}
names = list(SP)
def build(x):  # x in real units dict
    import eval.dispersion_report as dr
    from eval.eval_scripted_cfg import base as B
    cfg = json.load(open(CFG)); cfg.pop("description", None); cfg.pop("hypothetical", None)
    kw = dict(B); kw.update(cfg); kw.update(OV); kw["script"] = {**B["script"], **cfg.get("script", {})}
    for k, v in x.items():
        if k in SCRIPT_KEYS: kw["script"][k] = float(v)
        else: kw[k] = float(v)
    kw["flight_steps"] = 900; return kw
def evaluate(job):
    x, n, seed = job
    import eval.dispersion_report as dr
    dr.REFS = []; dr.MASON_REFS = []; dr.MASON_V2_REFS = []
    try:
        d, _ = dr.run("x", build(x), n, seed, True, scripted=True)
        keys = ["contact_rate", "mean_carry", "lateral_std", "peak_club_mph_mean", "mean_y", "launch_elev_mean_deg", "smash_factor_mean", "backspin_rpm_mean", "mean_distance"]
        return {k: (None if (isinstance(d.get(k), float) and not math.isfinite(d[k])) else d.get(k)) for k in keys}
    except Exception as e:
        return {"error": repr(e)[:200]}
def lat(r): return math.sqrt(r["lateral_std"] ** 2 + (r.get("mean_y") or 0.0) ** 2)  # gate "lateral_std" is RMS about the target line (std about mean was a v1 bug: mean_y -3.5 m passed search, failed gate)
def fitness(r):
    if "error" in r or r.get("mean_carry") is None: return 1e3
    f = -(r["mean_carry"] + 0.1 * (r["peak_club_mph_mean"] or 0)); pen = 0.0
    if r["contact_rate"] < 0.99: pen += 50 + 500 * (0.99 - r["contact_rate"])
    if lat(r) > 2.7: pen += 10 + 20 * (lat(r) - 2.7)
    if phase == "power":
        sp, sm = r.get("backspin_rpm_mean"), r.get("smash_factor_mean")
        if sp is None or not (1800 <= sp <= 3000): pen += 10 + (0 if sp is None else 0.02 * min(abs(sp - 1800), abs(sp - 3000)))
        if sm is None or sm > 1.50: pen += 10 + (0 if sm is None else 100 * (sm - 1.5))
    return f + pen
def feasible(r):
    if "error" in r or r.get("mean_carry") is None: return False
    ok = r["contact_rate"] >= 0.99 and lat(r) <= 2.7
    if phase == "power": ok = ok and r["backspin_rpm_mean"] is not None and 1800 <= r["backspin_rpm_mean"] <= 3000 and r["smash_factor_mean"] <= 1.50
    return ok
def start_vec():
    cfg = json.load(open(CFG)); s = cfg.get("script", {}); v = []
    from env.residual_golf_env import DEFAULT_SCRIPT
    for k in names:
        val = s.get(k, DEFAULT_SCRIPT.get(k)) if k in SCRIPT_KEYS else OV.get(k, cfg.get(k))
        v.append(float(val))
    return v
def to_real(u): return {k: SP[k][0] + (SP[k][1] - SP[k][0]) * float(np.clip(ui, 0, 1)) for k, ui in zip(names, u)}
if __name__ == "__main__":
    import cma
    v0 = start_vec(); u0 = [(v - SP[k][0]) / (SP[k][1] - SP[k][0]) for v, k in zip(v0, names)]
    print("start", dict(zip(names, v0)), flush=True)
    es = cma.CMAEvolutionStrategy(u0, 0.15, {"popsize": POP, "bounds": [0, 1], "seed": 28, "verbose": -9})
    hist = []; t0 = time.time()
    ctx = mp.get_context("spawn")
    with ProcessPoolExecutor(max_workers=WORKERS, mp_context=ctx) as ex:
        base_r = ex.submit(evaluate, (to_real(u0), 40, 6000)).result()
        print("start-config 40ep@6000:", base_r, "fit", fitness(base_r), flush=True); hist.append({"gen": -1, "x": to_real(u0), "r": base_r, "fit": fitness(base_r)})
        for g in range(GENS):
            X = es.ask(); R = list(ex.map(evaluate, [(to_real(u), 40, 6000) for u in X])); F = [fitness(r) for r in R]; es.tell(X, F)
            for u, r, f in zip(X, R, F): hist.append({"gen": g, "x": to_real(u), "r": r, "fit": f})
            b = int(np.argmin(F)); print(f"gen {g} t={time.time()-t0:.0f}s best fit {F[b]:.2f} feas={feasible(R[b])} carry {R[b].get('mean_carry')} latRMS {lat(R[b]) if 'error' not in R[b] else None} contact {R[b].get('contact_rate')} club {R[b].get('peak_club_mph_mean')}", flush=True)
            json.dump({"phase": phase, "hist": hist}, open(f"results/param_search_s28_{phase}_hist.json", "w"))
        feas = sorted([h for h in hist if feasible(h["r"]) and h["gen"] >= 0], key=lambda h: h["fit"])
        top = feas[:3]; fin = []
        cands = [{"name": "start_config", "x": hist[0]["x"]}] + [{"name": f"top{i+1}", "x": h["x"]} for i, h in enumerate(top)]
        res100 = list(ex.map(evaluate, [(c["x"], 100, 7000) for c in cands]))
        for c, r in zip(cands, res100): c["r100_seed7000"] = r; c["feasible100"] = feasible(r); c["fit100"] = fitness(r); print(c, flush=True)
    json.dump({"phase": phase, "label": "SCRIPTED-PARAMETER SEARCH (CMA-ES), not neural/learned, not distilled; " + ("STOCK fs1" if phase == "stock" else "HYPOTHETICAL power tier, gain 1.20"),
               "eval": "40 eps seed 6000 per candidate; finalists 100 eps seed 7000; carry = single no-roll metres", "start_cfg": CFG, "override": OV, "bounds": SP, "finalists": cands}, open(f"results/param_search_s28_{phase}.json", "w"), indent=1)
