"""v3 wrapper (2026-10-19, PROVISIONAL harness additions): same as _run_j_gateoff_gp.py, but uses _j_worker_gp_v3.py (perturb= support) and turns on
the v3 rules by default: --grf-method butter (PRIMARY: Data Agent notes; 4th-order zero-lag 50 Hz, window top->impact+20 ms, >=3-sample guard) and --robustness 24 (seeds 7000..7023). Per-substep
traces (seg1) whenever the GRF rule needs them; the default rows are computed from the default-cadence view (legacy_view), as with --timing-res-ms.
Usage: python _run_j_gateoff_gp_v3.py <ckpt_base> --v5-repo <trainer export> --json out.json [--grf-method ...] [--robustness N]"""
import os, sys, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # this evaluator checkout
TRAINER = os.environ.get("HGS_TRAINER_REPO") or os.path.join(os.path.dirname(ROOT), "humanoid-golf-scott")   # Trainer checkout (env var, else sibling dir)
sys.path.insert(0, ROOT)
spec = importlib.util.spec_from_file_location("v5rj", os.path.join(TRAINER, "scripts", "v5_realism_j.py")); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
import eval.realism_check as RC
_o = m.worker_args
def _wa(a, repo, ck, arm, sd):
    x = _o(a, repo, ck, arm, sd); x[1] = os.path.join(ROOT, "results", "overnight", "_j_worker_gp_v3.py")
    return x + (["seg1"] if (getattr(a, "timing_res_ms", None) or RC._fine_grf(a)) else [])
RC.worker_args = _wa
extra = sys.argv[2:]
if "--grf-method" not in extra: extra += ["--grf-method", "butter"]
if "--robustness" not in extra: extra += ["--robustness", "24"]
sys.argv = [sys.argv[0], sys.argv[1], "--env", "v5", "--club-len", "1.15", "--arm-dist", "0.6", "--eps-per-seed", "8", "--seeds", "4000,8000,9000", "--workers", "2"] + extra
RC.main()
