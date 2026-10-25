# V9 official grading (Evaluator, 2026-10-24 ET)

This is the OFFICIAL grade. The Trainer's local numbers are not official.

Harness v4 (`--harness v4`) on the env_v4 head (V3_HEAD=v4; v4 address cross-check vs V4_SPEC passed on every row). Gating row: 1.5 in tee. Crown 1.6 in row is INFO only. v3c and v3d at 1.5 in are for continuity. Read-only Trainer export f7cbc55 (Trainer HEAD; contains ac13405, c46db64, 35f321b). Env vs 79d86eb: only `train/v5_train_j.py` changed (V9 plant_h_w reward term, flag pass-through fix and guard); no v4 geometry change. Worker: arm 0.6, club 1.15, 24 deterministic episodes, gate off, golfphys, robustness seeds 7000-7023. Layout pre-check LAYOUT_OK for all three (obs 116, act 29, 121 keys, keys md5 fd9386dc... matches Trainer HEAD). Snapshot md5s all MATCH (md5 record and batch script held locally with the raw results, not tracked).
Labels: J+ reference-guided residual with tracking assistance; K8+ reference re-tuned open-loop by CMA-ES, stock G1 torque, warm-started.

| ckpt | v4 1.5in (gating) | v4 crown INFO | v3c 1.5in | v3d 1.5in |
|---|---|---|---|---|
| V9a_s91 150k | 11/7/1 FAIL | 12/6/1 | 10/6/2 | 11/7/1 |
| V9a_s91 100k | 12/5/2 FAIL | 12/5/2 | 11/4/3 | 12/5/2 |
| V8a_s90 300k | 12/6/1 FAIL | 12/6/1 | 11/5/2 | 12/6/1 |

v4 1.5 in main row, 24/24 true contacts each. Robustness fractions are of 24 episodes.

| | V9a 150k | V9a 100k | V8a 300k |
|---|---|---|---|
| Fails | mine/robustness | mine/robustness, shot/total_over_carry 1.363 | mine/robustness |
| Strike dz / dy nominal (mm) | -7.15 / 12.83 | 2.37 / 16.72 | -3.25 / 16.18 |
| Strike dz / dy noise median (mm) | 0.59 / -1.26 (n=20) | -2.21 / 1.16 (n=23) | -2.18 / 4.06 (n=20) |
| Spin (rpm) | 3024 (warn) | 2336 | 2775 |
| Launch (deg) | 13.79 | 15.20 | 14.68 |
| Club speed (mph) | 69.3 | 69.2 | 69.3 |
| Smash | 1.421 | 1.398 | 1.402 |
| Total/carry | 1.338 (warn) | 1.363 (FAIL) | 1.350 (warn) |
| Robustness contact / start dir / plant | 0.83 / 0.71 / 0.38 | 0.96 / 0.71 / 0.33 | 0.83 / 0.67 / 0.25 |
| Robustness club-speed p10 (mph); t/c p90 | 55.7; 2.15 | 56.1; 2.27 | 55.3; 2.27 |

Common warnings (v4 main): kinematic_sequence_order, kinematic_sequence_timing, peak pelvis speed (<250 deg/s), lead GRF, lead_foot_plant; plus spin and t/c on 150k, t/c on V8a 300k. v3c additionally fails kinematic_sequence_order (pelvis/thorax inversion) on all three.

Nothing passes in full. No render.

Versus the Trainer's local claims: all counts, robustness fractions, t/c p90 and nominal dz match (150k 11/7/1, .83/.71/.38, 2.15, -7.2; 100k 12/5/2, contact 0.96; V8a 300k 12/6/1, .83/.67/.25, 2.27, -3.2, noise-median -2.2/+4.1 over 20). No differences found.

## Training-flag erratum (Trainer ac13405)

The Trainer found that the V5-V8 reward flags (noise_ramp, miss_w, dz_gate, rsi_full, loc_noclip, dz/dy_lin, res_l2_w, launch_lo_w, sd_w) never reached the training env, so V5-V8 checkpoints trained on the base reward. The grades above are unaffected (they score the checkpoints as they are); only descriptions of what those reward terms did are wrong.
