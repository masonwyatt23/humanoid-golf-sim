# Stage K checkpoints for the Evaluator (reference-guided residual RL, public refs only; harness adapter scripts/v5_eval_j_worker.py, club 1.15, arm 0.6, gate nx 0.25)
- results/v5_runs/stageK_s1/best_det.zip (+_vecnorm.pkl): 800k, det full swing contact 1.0, 58.7 mph, carry 54 m (no roll). Snapshot: results/v5_runs/_snap/K_s1_800k/
- results/v5_runs/stageK_s1/ckpt_500000.zip: det 58.5 mph / 46.8 m; harness 7/5/3.
- Running: stageK_s1 (to ~2M) and stageK2_s0 (warm from K s1 800k, ord2 order-separation reward, T0 70). New best_det files appear in their dirs; eval.jsonl lists per-100k det metrics.
- Reference: results/v5_runs/stageK_ref/tuned_keys.json (open-loop 64.6 mph / 57.8 m). Residual (0.7*0.2 rad) + tracking floor 0.3: NOT pure RL.
