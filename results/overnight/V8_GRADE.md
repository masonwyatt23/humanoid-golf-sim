# V8 official grading (Evaluator, 2026-10-24 ET)

Harness v4 (`--harness v4`) on the env_v4 head (V3_HEAD=v4; v4 address cross-check vs V4_SPEC passed). Gating row: 1.5 in tee. Crown 1.6 in row is INFO only. v3c and v3d at 1.5 in are for continuity. Read-only Trainer export 79d86eb (Trainer HEAD; contains e34f054 ref keys and 98c346a flags; v4 head geometry unchanged since 54b49c6). Worker: arm 0.6, club 1.15, 24 deterministic episodes, gate off, golfphys, robustness seeds 7000-7023. Layout pre-check LAYOUT_OK for both (obs 116, act 29, keys md5 match Trainer HEAD). Snapshot md5s and batch script held locally with the raw results (not tracked).
Labels: J+ reference-guided residual with tracking assistance; K8+ reference re-tuned open-loop by CMA-ES, stock G1 torque, warm-started.

| ckpt | v4 1.5in (gating) | v4 crown INFO | v3c 1.5in | v3d 1.5in |
|---|---|---|---|---|
| V8a_s90 100k | 12/6/1 FAIL | 12/6/1 | 11/5/2 | 12/6/1 |
| V8b_s89 250k | 11/6/2 FAIL | 12/5/2 | 11/4/3 | 11/6/2 |

The v4 1.5 in values are from 24/24 true contacts. Robustness figures are fractions of 24 episodes.

| | V8a 100k | V8b 250k |
|---|---|---|
| Fails | mine/robustness | mine/robustness, shot/total_over_carry 1.912 |
| Strike dz / dy, nominal (mm) | -2.66 / 3.83 | -21.15 (warn) / 15.42 |
| Strike dz median under noise (mm) | -4.55 (n=19) | -4.49 (n=21) |
| Spin (rpm) | 2738 | 3549 (warn) |
| Launch (deg) | 13.98 | 6.85 (warn) |
| Club speed (mph, median) | 70.06 | 68.85 |
| Smash | 1.444 | 1.400 |
| Total/carry | 1.311 (warn) | 1.912 (FAIL) |
| Robustness contact / start direction / plant | 0.79 / 0.46 / 0.25 | 0.88 / 0.71 / 0.58 |
| Robustness club-speed p10 (mph) | 52.3 | 68.3 |

Nothing passes in full. There's no render.

How this compares with the Trainer's local claims: the counts and robustness fractions match for both checkpoints, and so do V8a's t/c of 1.31 and nominal dz of -2.7. There is one difference: the Trainer reports V8a's median dz under noise as -1.0 mm, but here it's -4.55 mm. Here the median is taken over the 19 robustness contacts. I haven't verified the cause. The likely reason is a different episode set or noise draw in the Trainer's local measurement. The Trainer named the V8b checkpoint as being in the "s88 lineage", but the snapshot is V8b_s89_250000 (seed 89, init V7a_s87 200k).

## Training-flag erratum (Trainer ac13405)

The Trainer found that the V5-V8 reward flags (noise_ramp, miss_w, dz_gate, rsi_full, loc_noclip, dz/dy_lin, res_l2_w, launch_lo_w, sd_w) never reached the training env, so V5-V8 checkpoints trained on the base reward. The grades above are unaffected (they score the checkpoints as they are); only descriptions of what those reward terms did are wrong.
