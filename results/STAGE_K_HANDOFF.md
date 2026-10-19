# Stage K checkpoints for the Evaluator (reference-guided residual RL, public refs only; harness adapter scripts/v5_eval_j_worker.py, club 1.15, arm 0.6, gate nx 0.25)
- results/v5_runs/stageK_s1/best_det.zip (+_vecnorm.pkl): 800k, det full swing contact 1.0, 58.7 mph, carry 54 m (no roll). Snapshot: results/v5_runs/_snap/K_s1_800k/
- results/v5_runs/stageK_s1/ckpt_500000.zip: det 58.5 mph / 46.8 m; harness 7/5/3.
- Running: stageK_s1 (to ~2M) and stageK2_s0 (warm from K s1 800k, ord2 order-separation reward, T0 70). New best_det files appear in their dirs; eval.jsonl lists per-100k det metrics.
- Reference: results/v5_runs/stageK_ref/tuned_keys.json (open-loop 64.6 mph / 57.8 m). Residual (0.7*0.2 rad) + tracking floor 0.3: NOT pure RL.

## Stage K3 (latest)
- BEST: results/v5_runs/_snap/K3b_s0_500k/ckpt_500000.zip (+_vecnorm.pkl, args.json): det 63.2 mph, carry 83.9 m, descent 29.2, total/carry 1.25, smash 1.30, GRF 1.01 BW (5 ms), X-factor 55.8; harness FAIL on spin only (4693 rpm); JSON results/v5_runs/stageJ_harness/K3b_s0_500k.json.
- results/v5_runs/_snap/K3_s1_600k (65.7 mph/83.6 m, fails order+spin), K3_s1_200k (10/3/2), K2_s0_600k (63 mph/43.8 m, 9/5/1 before descent terms).
- Adapter: PYTHONPATH=hgs-scott-lb python scripts/v5_realism_j.py <ckpt.zip> (reads args.json next to the ckpt).
