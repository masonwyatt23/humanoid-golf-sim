# V10 official grading (Evaluator hourly watch, 2026-10-24 ~11:20 PM ET)

This is the OFFICIAL grade. The Trainer's local numbers are not official.

**Selection.** I read the Trainer's own stageJ_harness v4 1.5 in JSONs for every unscored V8/V9/V10 snapshot that has one (V8a_s90 600k, V8b_s89 50k-400k except 250k, V9a_s91 50k/200k/250k/300k, V9b_s92 50k-500k, V9c_s93 50k-300k, V9d_s94 50k-300k, V10a_s95 50k-250k, V10b_s96 50k). No Trainer JSON claims a full pass. I ranked by fewest fails, then most passes, then robustness (sum of the contact, start-direction and plant fractions). Six checkpoints tie at a Trainer-claimed 12/6/1, failing only on robustness. The top 3 are V9b_s92 300k (0.875/0.54/0.54), V9b_s92 150k (0.875/0.58/0.42) and V9a_s91 50k (0.83/0.625/0.33). I also graded V8b_s89 400k because it has the highest Trainer pass count, 14/3/2. V9a_s91 50k scored above the V9a 100k/150k checkpoints that were graded earlier, because those runs were selected before the 50k JSON existed. Not graded: V9b 450k/500k, V8a 600k and V10b 50k, which have 3 fails or 0/24 contacts in the Trainer's JSON. V10a 300k had no Trainer JSON yet, and V10b 100k+ is still being evaluated.

**Setup.** Harness v4 (`--harness v4`) on the env_v4 head (V3_HEAD=v4). The v4 address cross-check against V4_SPEC passed on all 16 rows. Gating row: 1.5 in tee. The crown 1.6 in row ('v4 head, 1.6 in crown tee (equator at sourced crown)') is INFO only. v3c and v3d at 1.5 in are kept for continuity. I reused the read-only Trainer export f7cbc55 after re-verifying it: it is byte-identical to `git archive f7cbc55` for every .py/.json/.xml file. Trainer HEAD 1d2c8d7 differs from f7cbc55 only by a V9_DEBUG print in `train/v5_train_j.py` make(), with no env geometry change. All four args.json have env_v4 true and tee_mode 1.5in. V9a/V9b use keys stageV8_ref_s1 (training code at ac13405, the V9 flag pass-through fix). V8b uses stageV7_ref_s1 (pre-ac13405 training code; eval geometry is unchanged vs 79d86eb/f7cbc55). Layout pre-check gave LAYOUT_OK on all four (obs 116, act 29, keys md5 matches Trainer HEAD). Snapshot md5s all MATCH (md5 record and batch script held locally with the raw results, not tracked). Worker: arm 0.6, club 1.15, 24 deterministic episodes, gate off, golfphys, robustness seeds 7000-7023, cores 0-1 only.

Labels: J+ stages are a reference-guided residual with tracking assistance. K8+ stages add a reference re-tuned open-loop by CMA-ES, stock G1 torque, warm-started. Derived bands are derived, not published. The club-speed p10 rule has low confidence. Izz 5600 is an n=1 manufacturer claim.

| ckpt | v4 1.5in (gating) | v4 crown16 INFO | v3c 1.5in | v3d 1.5in |
|---|---|---|---|---|
| V9b_s92 300k | 12/6/1 FAIL | 12/6/1 | 11/5/2 | 12/6/1 |
| V9b_s92 150k | 12/6/1 FAIL | 13/5/1 | 11/5/2 | 12/6/1 |
| V9a_s91 50k | 12/6/1 FAIL | 12/6/1 | 11/5/2 | 12/6/1 |
| V8b_s89 400k | 14/3/2 FAIL | 14/3/2 | 13/2/3 | 14/3/2 |

The table below covers the v4 1.5 in main row. Every checkpoint had 24/24 true contacts. Robustness fractions are out of 24 episodes.

| | V9b 300k | V9b 150k | V9a 50k | V8b 400k |
|---|---|---|---|---|
| Fails | robustness | robustness | robustness | robustness, total_over_carry 1.782 |
| Warnings (besides kin. seq. order/timing, pelvis) | lead GRF, t/c, lead_foot_plant | spin, t/c, lead_foot_plant | lead GRF, t/c, lead_foot_plant | none |
| Peak pelvis (deg/s, floor 250) | 198.0 | 209.3 | 203.2 | 225.8 |
| Strike dz / dy nominal (mm) | -4.60 / 4.01 | -6.03 / 4.28 | 0.40 / 14.39 | -12.14 / 12.79 |
| Strike dz / dy noise median (mm) | 4.32 / -10.01 (n=21) | -0.72 / -4.39 (n=21) | -1.57 / 2.86 (n=20) | -0.25 / 12.83 (n=18) |
| Spin (rpm) | 2887 | 3047 (warn) | 2512 | 2897 |
| Launch (deg) | 13.42 | 12.91 | 15.25 | 8.51 |
| Club speed (mph) | 70.0 | 69.9 | 69.4 | 68.3 |
| Smash | 1.444 | 1.441 | 1.409 | 1.438 |
| Total/carry | 1.337 (warn) | 1.335 (warn) | 1.329 (warn) | 1.782 (FAIL) |
| Robustness contact / start dir / plant | 0.88 / 0.54 / 0.54 | 0.88 / 0.58 / 0.42 | 0.83 / 0.62 / 0.33 | 0.75 / 0.58 / 0.67 |
| Robustness club-speed p10 (mph); t/c median, p90 | 54.2; 1.55, 2.89 | 49.4; 1.37, 2.84 | 55.1; 1.55, 2.40 | 64.6; 2.22, 3.61 |

The robustness gate needs contact >= 95%, and no checkpoint is close: the best is 0.875. The face-edge model verdict is also FAIL on all four.

**Versus the Trainer's local claims.** On the v4 1.5 in main row and the v3c row, every count, fail/warn list, robustness fraction, strike dz/dy and shot value is identical for all four checkpoints. The only difference is on the v3d row, where my count is +1 pass on every checkpoint (V9 12/6/1 vs Trainer 11/6/1; V8b 14/3/2 vs 13/3/2). The cause is that the Trainer's v3d JSON omits the `mine/strike_height` check, which passes in mine. That row's verdict and fails are unchanged.

**Full pass: none.** No graded checkpoint passes v4 harness + v4 head + 1.5 in tee + all rows including the robustness gate. No render.

## Training-flag erratum (Trainer ac13405)

The Trainer found that the V5-V8 reward flags (noise_ramp, miss_w, dz_gate, rsi_full, loc_noclip, dz/dy_lin, res_l2_w, launch_lo_w, sd_w) never reached the training env, so V5-V8 checkpoints trained on the base reward. The grades above are unaffected (they score the checkpoints as they are); only descriptions of what those reward terms did are wrong.
