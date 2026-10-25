# V12T reference refit: source of the commit-message numbers (36127f6a)
LOCAL, NOT official. Values are the refit's own internal proxies from scripts.v10_ref_fit, not Evaluator grades.
Source: logs/v12Tref.log (gen 0-29). Command: results/v5_runs/stageV12T_ref_s1/cmd.txt (V7_NS=48, V7_PID0=2000, init V12S keys, 30 gens, pop 24, seed 17). All per-gen rows are in V12T_refit_summary.json.

Final logged row (gen 29, score -92.7): contact_rate 0.98, h_plant 0.92, h_sd 0.88, h_slip_pass 0.94, pel_med 233.81, mph_p10 69.03, nom_tc 1.42, nom_dz 9.28 mm.

Corrections to the 36127f6a message:
- It said "holdout 48 noisy starts". That is inaccurate. PID0=2000 draws were new relative to V12S's fit (PID0=1000), but V12T was fit ON these same 48 draws. So .98/.92/.88 is an in-sample figure, not holdout.
- h_sd is the refit proxy (contact & |az|<=6 & |face-path|<=3), not the harness start-direction test (|az|<=7 & lateral<=13.5 yd/100).
- Contact varies gen to gen (.92 in gens 25-28, .98 in gen 29), so the .98 figure is not stable.

Label (port): contact .98 / h_plant .92 above are IN-SAMPLE refit proxies (fit on the same 48 draws, PID0=2000), not held-out; contact .98 is unstable (.92 in gens 25-28).
Held (port): one sentence about harness figures for R0V12T was removed because it is not backed by a committed file.
