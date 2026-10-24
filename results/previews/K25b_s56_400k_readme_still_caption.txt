K25b_s56 400k (Trainer snapshot results/v5_runs/_snap/K25b_s56_400000, Trainer commit 5cb4d43), seed 4000, ~50 ms before impact (sim sample 258 of impact 268 on the 5 ms grid), 1280x720, no overlay text.
Method: reference-guided residual with tracking assistance, reference re-tuned open-loop by CMA-ES, stock G1 torque, warm-started.
Seed-4000 episode: club 72.2 mph, ball 103.7 mph, smash 1.44, launch 11.5 deg, spin 3293 rpm, carry 130 yd (model total 173 yd).
Harness v3c (47f30f8, PROVISIONAL rules): FAIL, 14 pass / 3 warn / 1 fail. FAIL: robustness (perturbed-start gate: spin p10/p90 and total/carry spread; foot planted 0.83 < 0.90). WARN: pelvis peak speed, nominal spin, total/carry.
Not a full realism pass. Best of the v3c-scored rows by fewest FAILs, then WARNs, then robustness.
Render: build_and_render.py (evaluator-exporter-nopath 8dcb9af, clip policy, frame 131 @24 fps, Eevee, 2 threads); trajectory exported with the path-free exporter patched to apply the run's full configure() (res_mult + newer keys), matching the harness worker.
