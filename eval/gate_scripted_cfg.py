"""Stage 26: headline-tier 3-seed gate for a SCRIPTED (zero-residual, not learned) config using eval_gate's exact protocol.
python -m eval.gate_scripted_cfg <config.json> <name> <episodes> <seed> [extra_override_json]; every row (det/stoch/scripted) is the scripted swing (stochastic == deterministic for zero residual).
Writes results/<name>.json stub (env_kwargs_full) then runs eval.eval_gate with dr.run forced scripted. GATE_OUT respected."""
import sys, json, runpy
from pathlib import Path
import eval.dispersion_report as dr
from eval.eval_scripted_cfg import base as B
ROOT = Path(__file__).resolve().parent.parent
cfgf, name, n, seed = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
ov = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
cfg = json.load(open(cfgf)); cfg.pop("description", None); cfg.pop("hypothetical", None)
kw = dict(B); kw.update(cfg); kw.update(ov); kw["script"] = {**B["script"], **cfg.get("script", {}), **ov.get("script", {})}
kw["flight_steps"] = 900; kw.pop("_env", None)
stub = ROOT / "results" / f"{name}.json"
if not stub.exists(): json.dump({"args": {}, "env_kwargs_full": kw, "note": "SCRIPTED zero-residual stub for eval_gate (not a learned policy)"}, open(stub, "w"), indent=1)
_run = dr.run
dr.run = lambda nm, k, e, s, det, scripted=False, workers=1, noise=0.0: _run(nm, k, e, s, True, scripted=True, workers=workers, noise=noise)
sys.argv = ["eval_gate", name, n, seed]
runpy.run_module("eval.eval_gate", run_name="__main__")
