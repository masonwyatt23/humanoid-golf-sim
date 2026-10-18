"""350-yd-at-130-mph exploration with the calibrated chain (model output; NOT a measurement). Writes into golfphys_validation.json."""
import json, itertools
from pathlib import Path
import numpy as np
from . import load_params
from .impact import Delivery
from .sim import simulate_shot

ROOT = Path(__file__).resolve().parent.parent
p = load_params(); MPH = 0.44704
out = {}
for club in (120, 130, 132):
    for turf in ("soft", "normal", "firm"):
        best = None
        for aoa, dl in itertools.product((0, 2, 4, 5, 6, 8), np.arange(8, 19.1, 0.5)):
            r = simulate_shot(Delivery(club * MPH, float(dl), float(aoa)), p=p, turf=turf)
            if r.spin_rpm < 1500: continue
            if best is None or r.total_yd > best[0].total_yd: best = (r, aoa, dl)
        r, aoa, dl = best
        out[f"{club}mph_{turf}"] = dict(aoa=aoa, dynamic_loft=float(dl), smash=round(r.smash, 3), ball_mph=round(r.ball_speed_mph, 1), launch=round(r.launch_deg, 1),
                                         spin=round(r.spin_rpm), carry_yd=round(r.carry_yd, 1), total_yd=round(r.total_yd, 1), roll_yd=round(r.total_yd - r.carry_yd, 1),
                                         descent=round(r.descent_deg, 1), apex_m=round(r.apex_m, 1))
# wind/altitude sensitivity at the 130 mph normal optimum
o = out["130mph_normal"]
sens = {}
for name, kw in {"sea_level_15C": {}, "1000m_alt": dict(alt_m=1000), "30C_sea": dict(temp_c=30), "5mps_tailwind": dict(wind=(5, 0, 0)), "5mps_headwind": dict(wind=(-5, 0, 0))}.items():
    r = simulate_shot(Delivery(130 * MPH, o["dynamic_loft"], o["aoa"]), p=p, **kw)
    sens[name] = dict(carry_yd=round(r.carry_yd, 1), total_yd=round(r.total_yd, 1))
res = dict(grid="AoA {0,2,4,5,6,8} x dynamic loft 8-19 step 0.5, spin>=1500 rpm, centre strike, path=face=0; best TOTAL per club speed and turf", best=out, sensitivity_130_normal_optimum=sens)
f = ROOT / "data/references/golfphys_validation.json"
d = json.load(open(f)); d["implications_350"] = res; json.dump(d, open(f, "w"), indent=1, default=float)
print(json.dumps(res, indent=1))
