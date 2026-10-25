"""Scan scripted-speed settings on model variants with the v4 contact/impact model (2 workers). python -m eval.variant_scan  (edit GRID below or pass JSON list of override dicts as argv[1])"""
import sys, json, subprocess, os
from concurrent.futures import ThreadPoolExecutor
IM = {"contact_damp": 0.3, "impact_model": {"gain": 1.28, "dz0": -0.019, "k_off": 0.4, "spin_k": 130, "k_side": 3500}}
grid = json.loads(sys.argv[1]) if len(sys.argv) > 1 else [dict(model_xml=m, **{"script.t_down": t}) for m in ("humanoid_golf_v4_power.xml", "humanoid_golf_h12wrist.xml") for t in (0.065, 0.055)]
def run(ov):
    cfg = dict(IM, **ov); r = subprocess.run([os.environ.get("HGS_PY", sys.executable), "-m", "eval.smash_probe2", json.dumps(cfg), "20"], capture_output=True, text=True, env=dict(os.environ, OMP_NUM_THREADS="1", PYTHONPATH="."))
    line = [l for l in r.stdout.splitlines() if "smash" in l]
    return json.dumps(ov) + " -> " + (line[-1].split("smash", 1)[1] if line else "ERR " + r.stderr[-200:])
with ThreadPoolExecutor(2) as ex:
    for res in ex.map(run, grid): print(res, flush=True)
