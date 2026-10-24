"""Re-grade a slim v3c harness JSON with the Evaluator's eval/harness_v3d.py (v3d, opt-in). Writes <snap>_v3d.json next to the input.
usage: python scripts/v3d_regrade.py <snap>_v3.json [--eval-repo PATH]   (or set V3D_EVAL_REPO; the repo must contain eval/harness_v3d.py)"""
import sys, os, json, argparse
ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("--eval-repo", default=os.environ.get("V3D_EVAL_REPO", "."))
a = ap.parse_args(); sys.path.insert(0, os.path.abspath(a.eval_repo))
from eval.harness_v3d import apply_v3d_flagged
d = json.load(open(a.src)); r = apply_v3d_flagged(d); out = a.src.replace("_v3.json", "_v3d.json")
json.dump(r, open(out, "w"), indent=1, default=float)
c = r["checks"]; print(os.path.basename(a.src).replace("_v3.json", ""), "v3d", r.get("checks_passed"), r.get("n_warn"), r.get("n_fail"), r.get("verdict"), r.get("v3d_flag", ""))
for k, v in c.items():
    if v["status"] in ("warn", "fail"): print("   ", k, v["status"], str(v.get("values"))[:120])
