# V12T reference refit: source of the commit-message numbers (36127f6a)
LOCAL, NOT official. Values are the refit's own internal proxies from scripts.v10_ref_fit, not Evaluator grades.
Source: logs/v12Tref.log (gen 0-29). Command: results/v5_runs/stageV12T_ref_s1/cmd.txt (V7_NS=48, V7_PID0=2000, init V12S keys, 30 gens, pop 24, seed 17). All per-gen rows are in V12T_refit_summary.json.

Final logged row (gen 29, score -92.7): contact_rate 0.98, h_plant 0.92, h_sd 0.88, h_slip_pass 0.94, pel_med 233.81, mph_p10 69.03, nom_tc 1.42, nom_dz 9.28 mm.

Corrections to the 36127f6a message:
- (Superseded in part by the Correction below: the PID0 values had no effect.) It said "holdout 48 noisy starts". That is inaccurate. PID0=2000 draws were new relative to V12S's fit (PID0=1000), but V12T was fit ON these same 48 draws. So .98/.92/.88 is an in-sample figure, not holdout.
- h_sd is the refit proxy (contact & |az|<=6 & |face-path|<=3), not the harness start-direction test (|az|<=7 & lateral<=13.5 yd/100).
- Contact varies gen to gen (.92 in gens 25-28, .98 in gen 29), so the .98 figure is not stable.

Label (port): contact .98 / h_plant .92 above are IN-SAMPLE refit proxies (fit on the same 48 draws; per the correction below these were pid 0-47, not PID0=2000), not held-out; contact .98 is unstable (.92 in gens 25-28).
- Harness reference (Trainer-local, NOT official): zero-residual probe R0V12T 100k scored 13/4/2 on v4, robustness contact/start-dir/plant .875/.708/.875 (`results/v5_runs/stageJ_harness/R0V12T_s0_100000_v3_tee15in_v4h_v4.json`).
Held (port): the V12p/V12r 100k figures (.96/.75/.92) are not in a committed results file and stay held.

Correction (07:40 ET): the earlier text says the V12T/V12S fits used PID0=2000 and PID0=1000 draws. That is wrong. v8_ref_fit.score loops pid over range(NS) and ignores V7_PID0, so both fits used the same draws, pid 0-47 (noise rng 7000+pid). Every V12S/V12T 'holdout' figure is therefore IN-SAMPLE. Whether these draws match the harness robustness seeds 7000-7023 has not been checked. Disjoint held-out refit-proxy numbers (pid 5000-5047, not the harness) are in V12T_holdout_pid5000.json and V12U_refit_summary.md.
