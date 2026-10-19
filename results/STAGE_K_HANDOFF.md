# Stage K checkpoints for the Evaluator (reference-guided residual RL, public refs only; harness adapter scripts/v5_eval_j_worker.py, club 1.15, arm 0.6, gate nx 0.25)
- results/v5_runs/stageK_s1/best_det.zip (+_vecnorm.pkl): 800k, det full swing contact 1.0, 58.7 mph, carry 54 m (no roll). Snapshot: results/v5_runs/_snap/K_s1_800k/
- results/v5_runs/stageK_s1/ckpt_500000.zip: det 58.5 mph / 46.8 m; harness 7/5/3.
- Running: stageK_s1 (to ~2M) and stageK2_s0 (warm from K s1 800k, ord2 order-separation reward, T0 70). New best_det files appear in their dirs; eval.jsonl lists per-100k det metrics.
- Reference: results/v5_runs/stageK_ref/tuned_keys.json (open-loop 64.6 mph / 57.8 m). Residual (0.7*0.2 rad) + tracking floor 0.3: NOT pure RL.

## Stage K3 (latest)
- BEST: results/v5_runs/_snap/K3b_s0_500k/ckpt_500000.zip (+_vecnorm.pkl, args.json): det 63.2 mph, carry 83.9 m, descent 29.2, total/carry 1.25, smash 1.30, GRF 1.01 BW (5 ms), X-factor 55.8; harness FAIL on spin only (4693 rpm); JSON results/v5_runs/stageJ_harness/K3b_s0_500k.json.
- results/v5_runs/_snap/K3_s1_600k (65.7 mph/83.6 m, fails order+spin), K3_s1_200k (10/3/2), K2_s0_600k (63 mph/43.8 m, 9/5/1 before descent terms).
- Adapter: PYTHONPATH=hgs-scott-lb python scripts/v5_realism_j.py <ckpt.zip> (reads args.json next to the ckpt).

## K4 status (2026-10-18 ~22:15 ET)
- Best so far: snapshot results/v5_runs/_snap/K4_s0_100k (61.0 mph, total/carry 1.21, descent 32, smash 1.35, spin 4087, launch 19.8; Evaluator 12/2/1, only spin fails). Also _snap/K4_s1_100k, K3b_s0_500k.
- Original K4 runs (T0 80) collapsed (fell) at 200k; moved to results/v5_runs/_stageK4a_s*. Relaunched as stageK4b s0 (from K4 s0 100k) and s1 (from K3b 500k), T0 70, dl window 17-22, launch<=16, spin<=2900 penalty. Alive (pids 222554/222555), eval every 100k.
- Physics: spin<3000 + launch<=16 + total/carry<=1.25 are jointly infeasible at ~63 mph (golfphys: 24.7 deg descent/1.38 at 63; 28/1.27 at 70; 31.6/1.20 at 80 mph).

## K4c (2026-10-18 ~23:15 ET)
- Snapshots: _snap/K4b_s1_200000 (47.5 mph, spin 2245, smash 1.42, launch 14.5, only t/c 1.68 fails), _snap/K4b_s0_100000/200000 (regressed: order/XF/GRF fail).
- K4b s0 stopped (moved to _stageK4b_s0_old). New stageK4c s0 warm from K4b s1 200k with speed bonus 4, desc_w 4, XF hard 65 (cap w 0.3), GRF w 0.6, T_step 5. K4b s1 (pid 222555) continues unchanged.
