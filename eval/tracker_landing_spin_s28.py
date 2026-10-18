"""Stage 28 (report only): descent angle / landing speed via FlightTracker.install(track_landing=True) on the HYPOTHETICAL power tier at loft -27/-29 (20 eps, seed 6000, scripted zero residual),
and env spin-formula check: rpm = spin_k*|v|*sin(el+2deg). Writes results/tracker_landing_spin_s28.json. Defaults unchanged."""
import json, sys, math
import numpy as np
from eval.env_factory import make_env
from eval.flight_tracker import FlightTracker
from eval.eval_scripted_cfg import base as B
CFG = "configs/fast_scripted_v4_power_elbowrange.json"
def kw_for(loft):
    cfg = json.load(open(CFG)); cfg.pop("description", None); cfg.pop("hypothetical", None)
    kw = dict(B); kw.update(cfg); kw["impact_model"] = {"gain": 1.20, "dz0": 0.017, "k_off": 0.4, "spin_k": 130, "k_side": 3500}; kw["loft_deg"] = loft
    kw["script"] = {**B["script"], **cfg.get("script", {})}; kw["flight_steps"] = 900; return kw
out = {"label": "HYPOTHETICAL power tier, scripted, 20 eps seed 6000, single no-roll metres", "rows": {}}
for loft in (-27, -29, -31):
    env = make_env(kw_for(loft)); ft = FlightTracker(env).install(track_landing=True); zero = np.zeros(env.action_space.shape, dtype=np.float32); S = []
    for ep in range(20):
        env.reset(seed=6000 + ep); ft.reset(); done = False; info = {}
        while not done:
            _, _, te, tr, info = env.step(zero); ft.step(); done = te or tr
        S.append(ft.summary(info))
    ft.close()
    g = lambda k: float(np.nanmean([s[k] for s in S]))
    row = {k: g(k) for k in ("carry", "launch_elev_deg", "sep_rpm", "descent_angle_deg", "landing_speed_mps", "ball_speed_sep")}
    row["descent_std"] = float(np.nanstd([s["descent_angle_deg"] for s in S])); row["n_landed_desc"] = int(np.sum(np.isfinite([s["descent_angle_deg"] for s in S])))
    out["rows"][str(loft)] = row; print(loft, row, flush=True)
# analytic sensitivity of env formula
k, spd = 130.0, out["rows"]["-29"]["ball_speed_sep"]
out["spin_formula"] = {"rpm_at_launch": {str(el): k * spd * math.sin(math.radians(el + 2)) for el in (8, 10, 11.2, 12.5, 14)},
  "d_rpm_per_deg_launch": k * spd * math.cos(math.radians(13)) * math.pi / 180, "ball_speed_used_mps": spd}
json.dump(out, open("results/tracker_landing_spin_s28.json", "w"), indent=1); print(json.dumps(out["spin_formula"], indent=1))
