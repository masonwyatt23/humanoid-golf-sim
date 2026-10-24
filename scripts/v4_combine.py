"""Combine a v4 MAIN (1.5 in) result with its 1.6 in crown INFO run via eval.harness_v4.apply_v4 (adds mine/v4_crown_tee_info, crown-tee-only flag) and
re-render the tee/head INFO rows with the current labels (v4 head label fix 2026-10-24; INFO rows only, counts unchanged). Usage: [V4_RESULTS_DIR=dir] python scripts/v4_combine.py <tag>..."""
import sys, os, json, copy
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from eval.harness_v4 import apply_v4
from eval.realism_check import tee_info_rows
O = os.environ.get("V4_RESULTS_DIR", "results/v5_runs/stageJK_harness_summary")   # dir holding the 15in + crown16 result JSONs
LAB = dict(policy="J+ reference-guided residual with tracking assistance; K8+ reference re-tuned open-loop by CMA-ES, stock G1 torque, warm-started",
           head="v4 head (sourced 460 cc, lie 58.5, Izz 5600 (n=1 manufacturer claim), CFZ 39, face centre 29 mm)",
           rules="derived bands labelled derived; robustness club-speed p10 rule LOW confidence; full pass = gating v4 1.5 in row passes everything incl. robustness; crown-only, spin-band-only, face-edge-model-only are not passes")
for t in sys.argv[1:]:
    p = lambda tt: os.path.join(O, f"realism_v5_{t}_{tt}_v4_gateoff_gp_arm06.json")
    if not (os.path.exists(p("15in")) and os.path.exists(p("crown16"))): print("SKIP", t); continue
    m = json.load(open(p("15in"))); c = json.load(open(p("crown16")))
    out = apply_v4(copy.deepcopy(m), copy.deepcopy(c)); out["checks"].update(tee_info_rows(out["tee_info"])); out["labels_v4"] = LAB
    out["combined_from"] = [os.path.basename(p("15in")), os.path.basename(p("crown16"))]
    json.dump(out, open(os.path.join(O, f"realism_v5_{t}_v4combined_gateoff_gp_arm06.json"), "w"), indent=1, default=float)
    cr = out["checks"]["mine/v4_crown_tee_info"]["values"]
    print(t, out["verdict"], out["checks_passed"], out["n_warn"], out["n_fail"], "crown_info:", cr["verdict"], cr["n_pass"], cr["n_warn"], cr["n_fail"], "crown_only:", out["v4_crown_tee_only"], out.get("v4_note"))
