# arm_dist: why the `_arm06` files supersede the earlier overnight B1-B4 scores

The earlier `realism_v5_*` files in this folder (no suffix) were scored with `eval/_v5_worker.py` building the Trainer's `TrainEnv` with **arm_dist = 0**.
Stage B2-B4 (and C) checkpoints train with **arm_dist = 0.6** (`train.v5_train_b.BEnv`: ball cannot be hit until the club head is 0.6 m from the tee; at address it is 0.06 m).
At arm_dist 0 a policy can tap the ball at address, so **contact counts and club speed in the unsuffixed files are artifacts** (e.g. B4 s1 final read 1.07 mph; B4 s0's 24/24 contact is not real). Do not cite them.

Files ending `_arm06` were re-scored with BEnv, arm_dist 0.6 (recorded as `arm_dist` in each JSON and in the `env` label), club_len 1.15, tether 0, friction nominal, deterministic, 24 episodes (seeds 4000/8000/9000 x 8), one process under `taskset -c 0-1`.
`eval.realism_check --env v5` now defaults to 0.6 (auto 0 only if the path contains `stageA`); override with `--arm-dist`. Stage A results (arm_dist 0, TrainEnv) remain valid as labelled.
`club_mph_median` = impact-time club-head speed, median over contact episodes. Every checkpoint below: realism FAIL (stock force_scale, hypothetical-free; none eligible for showcase).

| checkpoint | contact | impact mph (median) | failing checks |
|---|---|---|---|
| stageB_s0 ckpt_800000 (B1) | 0/24 | - | seq order, pelvis/thorax peak speed, lead-foot GRF |
| stageB_s1 ckpt_800000 (B1) | 24/24 | 16.4 | seq order, GRF, spin, launch, carry_positive |
| stageB2_s0 ckpt_1200000 | 24/24 | 39.8 | seq order, GRF, spin, launch, carry_positive |
| stageB2_s1 ckpt_1200000 | 24/24 | 25.5 | GRF, spin, launch, carry_positive |
| stageB3_s0 ckpt_1000000 | 24/24 | 63.3 | seq order, X-factor, GRF, spin, launch, carry_positive |
| stageB3_s0 ckpt_1200000 | 24/24 | 63.1 | seq order, GRF, spin, launch, carry_positive |
| stageB3_s1 ckpt_900000 | 24/24 | 14.0 | GRF, spin, launch, carry_positive |
| stageB3_s1 ckpt_1100000 | 24/24 | 26.3 | seq order, GRF, spin, launch, carry_positive |
| stageB4_s0 ckpt_2500000 | 24/24 | 7.0 | seq order, GRF, spin, total/carry |
| stageB4_s0 ckpt_3000000 | 0/24 | - | seq order, pelvis/thorax/arm peak speed, GRF |
| stageB4_s0 final | 0/24 | - | seq order, pelvis/thorax/arm peak speed, GRF |
| stageB4_s1 ckpt_2400000 | 24/24 | 25.5 | GRF, spin, launch, carry_positive |
| stageB4_s1 ckpt_3000000 | 24/24 | 36.4 | seq order, GRF, spin, launch, carry_positive |
| stageB4_s1 final | 24/24 | 36.8 | seq order, GRF, spin, launch, carry_positive |

Real-world reference: pro driver club speed ~88-109 mph. Several "carry_positive" fails are backward/closed-face strikes (carry 0). Lead-foot GRF 0 means unloaded (foot_forces() is a non-negative contact normal).

Added 2026-10-18 ~6:25 AM ET (same settings, arm_dist 0.6):

| checkpoint | contact | impact mph (median) | failing checks |
|---|---|---|---|
| stageC_s0 ckpt_1000000 | 0/24 | - | seq order, pelvis/arm peak speed (3.0x), GRF |
| stageC_s1 ckpt_1000000 | 0/24 | - | seq order, pelvis/arm peak speed (2.8x/2.4x), GRF |

Added 2026-10-18 ~7:25 AM ET (same settings, arm_dist 0.6, BEnv; Stage D here is the current D run from B4 s1 ckpt_3000000 after the v1-v3 runs were moved to `_stageD_v*`; Stage E is in progress, init from B3 s0):

| checkpoint | contact | impact mph (median) | failing checks |
|---|---|---|---|
| stageD_s0 ckpt_1000000 | 0/24 | - | seq order, pelvis/thorax/arm peak speed (2.9x/1.8x/2.2x), X-factor, GRF |
| stageD_s1 ckpt_1000000 | 0/24 | - | seq order (arm before club), pelvis/arm peak speed (2.9x/2.2x), GRF |
| stageE_s0 ckpt_900000 | 24/24 | 58.9 | seq order, GRF, spin, launch, carry_positive (segment speeds 1.7-2.9x, WARN only because 59 mph is extrapolated) |
| stageE_s1 ckpt_1000000 | 0/24 | - | seq order, pelvis/arm peak speed (1.8x/2.1x), X-factor, GRF |

Added 2026-10-18 ~8:30 AM ET, daytime watch (same settings: BEnv, arm_dist 0.6, club_len 1.15, 24 deterministic eps; the harness does NOT apply the Stage G strike gate). Stage F was stopped at ~1.76M; Stage G is in progress (s0 warm from F s1 ckpt_1600000, s1 warm from F s0 ckpt_1600000).

| checkpoint | contact | impact mph (median) | failing checks |
|---|---|---|---|
| stageF_s0 ckpt_1600000 | 24/24 | 67.0 | seq order, X-factor, GRF (21 BW), spin 0, launch 0, carry_positive (backward/closed strike) |
| stageF_s1 ckpt_1700000 | 24/24 | 57.9 | seq order, GRF (43 BW), spin 0, launch 0, carry_positive (pelvis 3.5x, WARN only as extrapolated) |
| stageF_s0 best_det (1.1M) | 24/24 | 7.6 | seq order, X-factor, GRF (26 BW), spin 450, total/carry 2.3 (tap, carry ~1 yd) |
| stageF_s1 best_det (1.2M) | 24/24 | 9.1 | seq order, GRF (43 BW), spin 199, total/carry 3.0 (tap, carry ~1 yd) |
| stageG_s0 ckpt_500000 | 0/24 | - (~90 mph whiff) | seq order, pelvis/thorax/arm peak speed (2.4x/2.0x/3.6x), X-factor, GRF (49 BW) |
| stageG_s1 ckpt_500000 | 24/24 | 6.3 | seq order, GRF (7.4 BW), spin 362, launch -2.0, total/carry 4.9 (tap) |

Added 2026-10-18 ~9:35 AM ET, daytime watch (same settings: BEnv, arm_dist 0.6, club_len 1.15, 24 deterministic eps; harness does not apply the Stage G strike gate). Stage G (started ~8:11 AM) is still training at ~1.17M steps but has written no checkpoint past 1.1M (08:43).

| checkpoint | contact | impact mph (median) | failing checks |
|---|---|---|---|
| stageG_s0 ckpt_1100000 | 24/24 | 7.2 | seq order, GRF (38 BW), spin 379, launch -2.4, total/carry 8.9 (tap) |
| stageG_s1 ckpt_1100000 | 24/24 | 6.0 | seq order, GRF (8.6 BW), spin 558, launch -7.1, total/carry 7.3 (tap) |
| stageG_s0 best_det | 24/24 | 11.1 | seq order, GRF (49 BW), spin 316, total/carry 4.3 (tap; launch 8.2 passes) |
| stageG_s1 best_det | 24/24 | 6.3 | seq order, GRF (7.4 BW), spin 362, launch -2.0, total/carry 4.9 (tap; same numbers as s1 ckpt_500000) |
| stageG_s0 ckpt_800000 | 24/24 | 8.9 | seq order (arm before club), GRF (39 BW), spin 446, total/carry 4.9 (tap) |
| stageG_s1 ckpt_800000 | 0/24 | - (~90 mph whiff) | seq order, pelvis/arm peak speed (1.9x/2.3x), X-factor, GRF (21.5 BW) |
| stageF_s0 ckpt_1800000 | 24/24 | 4.0 | seq order, X-factor, GRF (24 BW), spin 95, launch -3.0, total/carry 3.9 (tap) |
| stageF_s1 ckpt_1800000 | 24/24 | 11.4 | seq order, GRF (7.4 BW), spin 332, launch -4.2, total/carry 16.6 (tap) |

Added 2026-10-18 ~10:25 AM ET, daytime watch (same settings: BEnv, arm_dist 0.6, club_len 1.15, 24 deterministic eps; harness does not apply the Stage G strike gate). Stage G was restarted ~9:27 AM (s0 warm from F s1 ckpt_1600000, s1 from F s0 ckpt_1600000) and now writes a checkpoint every ~2-3 min (1.2M-2.3M). Scored a representative subset: s0's highest-mph checkpoint per the Trainer's eval.jsonl, and both seeds' latest. The Trainer's own arm0.6 evals for the unscored 1.2M-2.2M checkpoints show 5-15 mph taps (s0) or 0 contact (s1).

| checkpoint | contact | impact mph (median) | failing checks |
|---|---|---|---|
| stageG_s0 ckpt_1900000 | 24/24 | 15.4 | seq order (thorax/arm), GRF (7.4 BW), spin 145, launch 3.3, total/carry 7.7 (tap; segment speeds 1.5-2.9x, WARN only as extrapolated) |
| stageG_s0 ckpt_2300000 | 24/24 | 14.7 | seq order (thorax/arm), GRF (7.5 BW), spin 294, launch -1.3, total/carry 17.0 (tap) |
| stageG_s1 ckpt_2300000 | 24/24 | 4.3 | seq order (thorax/arm, arm/club), X-factor 82, GRF (17.3 BW), spin 518, launch -5.3, total/carry 3.4 (tap; smash 0.65) |

Added 2026-10-18 ~11:25 AM ET, daytime watch (same settings: BEnv, arm_dist 0.6, club_len 1.15, 24 deterministic eps; harness does not apply the Stage G strike gate). Stage G finished at 3M steps on both seeds (final.zip / ckpt_3000000 written ~10:35-10:36 AM). best_det was updated after the 9:31 scoring (s0 now step 2.4M, s1 now step 2.7M), so the earlier best_det results were kept as `realism_v5_stageG_s{0,1}best_det_0931run_arm06.*` and the new ones written under the usual names. Per the Trainer's eval.jsonl, s0 2.4M-3.0M are all 6-15 mph taps and s1 2.4M-3.0M are 0 contact except 2.7M (18.7 mph tap).

| checkpoint | contact | impact mph (median) | failing checks |
|---|---|---|---|
| stageG_s0 final (3.0M) | 24/24 | 15.8 | seq order (pelvis/thorax, thorax/arm), GRF (7.4 BW), spin 466, launch -3.3, total/carry 23.7 (tap, carry ~0) |
| stageG_s1 final (3.0M) | 0/24 | - (~90 mph whiff) | seq order (thorax/arm), thorax/arm peak speed (1.9x/2.5x), GRF (7.4 BW) |
| stageG_s0 best_det (2.4M) | 24/24 | 11.6 | seq order (thorax/arm), GRF (15.8 BW), spin 404, total/carry 3.1 (tap, carry ~2 yd; launch 11.5 passes) |
| stageG_s1 best_det (2.7M) | 24/24 | 18.7 | seq order (pelvis/thorax), GRF (18.7 BW), spin 181, launch 3.8, total/carry 8.0 (tap, carry ~3 yd) |

Added 2026-10-18 ~3:30 PM ET, daytime watch (same settings: BEnv, arm_dist 0.6, club_len 1.15, 24 deterministic eps; harness does not apply the Stage G strike gate). Stage H ran ~2:32-3:03 PM (s0 planar, STALLED at 1.0M with 0 contact; s1 non-planar, STALLED at 1.6M); Stage I (warm from H s1 best_det) started ~3:08 PM and reached only ~235k. The box rebooted ~3:13 PM and no training process is running now, so Stage I appears to have been killed, not finished. Stage I s1 best_det.zip has a different md5 from ckpt_100000.zip (same vecnorm), and its harness result (43 mph, no carry) does not match the Trainer's best_det.json (8.9 mph tap at 100k); worth checking.

| checkpoint | contact | impact mph (median) | failing checks |
|---|---|---|---|
| stageH_s0 final (1.0M) | 0/24 | - (~90 mph whiff) | seq order (arm/club), pelvis/thorax/arm peak speed (2.1x/2.3x/2.8x), X-factor 112, GRF (22.3 BW) |
| stageH_s1 best_det (1.5M) | 24/24 | 18.1 | seq order (pelvis/thorax, thorax/arm), GRF (7.4 BW), spin 229, total/carry 6.2 (tap, carry ~0.3 yd; launch 5.3 WARN) |
| stageH_s1 final (1.6M) | 24/24 | 16.9 | seq order (pelvis/thorax, thorax/arm), GRF (7.4 BW), spin 18, launch 0.2, total/carry 15.2 (tap) |
| stageI_s0 best_det (200k) | 24/24 | 12.4 | seq order (thorax/arm), GRF (20.7 BW), spin 257, launch 21.0, total/carry 2.1 (tap) |
| stageI_s1 best_det | 24/24 | 43.0 | seq order (pelvis/thorax, thorax/arm), GRF (8.7 BW), spin 0, launch 0, carry_positive (contact but no carry; likely closed/backward strike) |
| stageI_s1 ckpt_200000 | 24/24 | 5.4 | seq order (thorax/arm), GRF (39.2 BW), spin 79, launch -3.0, total/carry 5.4 (tap, smash 1.17) |

Added 2026-10-18 ~4:30 PM ET, daytime watch (same settings: BEnv, arm_dist 0.6, club_len 1.15, 24 deterministic eps; harness does not apply the Stage G strike gate). Stage I was restarted after the 3:13 PM reboot and ran to 1.2M on both seeds (final.zip ~4:04 PM, both seeds marked STALLED). best_det was updated after the 3:29 PM scoring (s0 now step 300k, s1 now step 700k), so the earlier results were kept as `realism_v5_stageI_s{0,1}best_det_1529run_arm06.*`. A new Stage J (`train.v5_train_j`, reference tracking, seeds 0/1) started ~4:27 PM; no checkpoints yet.

| checkpoint | contact | impact mph (median) | failing checks |
|---|---|---|---|
| stageI_s0 final (1.2M) | 24/24 | 8.8 | seq order (thorax/arm, arm/club), GRF (44.5 BW), spin 145, total/carry 3.6 (tap, carry ~0.2 yd; launch 11.4 passes) |
| stageI_s1 final (1.2M) | 24/24 | 70.4 | seq order (pelvis/thorax, thorax/arm), GRF (7.4 BW), spin 0, launch 0, carry_positive (contact but no carry). Does NOT match the Trainer's eval.jsonl at 1.2M (7.8 mph, carry 0.26); same s1-only mismatch seen on the 3:29 PM s1 best_det |
| stageI_s0 best_det (300k) | 24/24 | 12.0 | seq order (thorax/arm), GRF (31.0 BW), spin 77, total/carry 3.0 (tap, carry ~0.2 yd; launch 11.2 passes) |
| stageI_s1 best_det (700k) | 24/24 | 11.4 | seq order (thorax/arm, arm/club), GRF (7.4 BW), spin 370, launch -11.8, total/carry 30 (tap; matches Trainer's 10.6 mph) |

Added 2026-10-18 ~5:35 PM ET, daytime watch (club_len 1.15, arm_dist 0.6, 24 deterministic eps, strike gate OFF unless noted). Stage J (`train.v5_train_j`, reference-guided residual policy, obs 116) restarted ~4:44 PM after the abandoned `_stageJ_v1_ballspin_bug` run and is still training (~800k at 5:28 PM). The stock `_v5_worker.py` (BEnv, obs 112) cannot load Stage J, so these were scored with the Trainer's adapter (`scripts/v5_eval_j_worker.py` in commit f31bff4: builds JEnv from the run's args.json, rsi = start at address, track_w 0), scoring code in `eval.realism_check` unmodified. The env label printed in the .txt files still says "[BEnv ...]" because that string is hard-coded; the actual env is JEnv. Harness mph matches the Trainer's eval.jsonl at every scored step (46.2, 54.8, 24.7, 3.1 mph).

| checkpoint | contact | impact mph (median) | failing checks |
|---|---|---|---|
| stageJ_s0 best_det (500k) | 24/24 | 46.2 | seq order (pelvis/thorax, thorax/arm), X-factor 87.6, GRF (3.4 BW), total/carry 3.5; spin 2900 passes, launch 6.5 WARN, smash 1.17 WARN. Best Stage J result so far; Trainer eval carry ~17 m. Same result with strike gate 0.25 (`_gate025`, 0 fouls) |
| stageJ_s0 ckpt_600000 | 24/24 | 54.8 | seq order (thorax/arm), X-factor 88.4, GRF (4.0 BW), launch -3.3, total/carry 107 (carry ~0.6 m) |
| stageJ_s0 ckpt_800000 | 24/24 | 24.7 | seq order (thorax/arm), X-factor 82.4, spin 996, total/carry 2.4; GRF passes (1.7 BW), launch 13.6 passes |
| stageJ_s1 best_det (500k) | 24/24 | 3.1 | seq order (pelvis/thorax, arm/club), X-factor 100.9, GRF (7.0 BW), spin 344, launch 56.7, total/carry 1.6 (tap, smash 0.74) |
| stageJ_s1 ckpt_800000 | 0/24 | - (whiff) | seq order (thorax/arm), X-factor 112.5, GRF (3.9 BW) |

Added 2026-10-18 ~6:30 PM ET, daytime watch (club_len 1.15, arm_dist 0.6, 24 deterministic eps, strike gate OFF; Trainer's JEnv adapter `scripts/v5_eval_j_worker.py` via the `v5_realism_j.py` worker_args swap, with gate forced off by `results/overnight/_run_j_gateoff.py`; scoring code unmodified). Stage J was resumed ~6:04 PM (`--resume --reset_stall`) and is still training (s0 1.9M, s1 1.7M). s0 best_det moved to step 1.8M (Trainer best_score 18.3), so it is written as `realism_v5_stageJ_s0best_det_1800k_arm06.*` and the 500k result keeps its old name. Harness mph matches the Trainer's eval.jsonl (51.0, 50.2, 0, 0) and the Trainer's own gate-0.25 run of s0 ckpt_1800k (`stageJ_harness/s0_ckpt_1800k.json`, 51.0 mph, same 4 FAILs). s1 has had 0 contact at every eval since 600k.

| checkpoint | contact | impact mph (median) | failing checks |
|---|---|---|---|
| stageJ_s0 best_det (1.8M) | 24/24 | 51.0 | X-factor 97.7, GRF (3.85 BW), spin 4510, total/carry 1.62 (carry ~23 yd). Seq order is WARN only (thorax/arm within one 20 ms sample), first Stage J result without a hard seq-order FAIL; launch 16.7 WARN, smash 0.86 WARN, club speed 51 WARN; all four peak speeds and golfphys carry PASS |
| stageJ_s0 ckpt_1700000 | 24/24 | 50.2 | seq order (arm/club), X-factor 89.9, spin 4637, launch 2.3, total/carry 9.1 (carry ~6 yd); GRF 2.26 BW WARN |
| stageJ_s0 ckpt_1900000 | 0/24 | - (whiff, club peak 0.22x target) | seq order (thorax/arm), all four peak speeds (0.22-0.33x), X-factor 110.5 |
| stageJ_s1 ckpt_1700000 | 0/24 | - (whiff) | seq order (thorax/arm, arm/club), club peak speed 0.23x, X-factor 96.5, GRF (13.6 BW) |

Added 2026-10-18 ~7:30 PM ET, daytime watch (club_len 1.15, arm_dist 0.6, 24 deterministic eps, strike gate OFF via `results/overnight/_run_j_gateoff.py` and the Trainer's JEnv adapter; scoring code unmodified). Stage J s0 finished (`final.zip` and `STOP_REACHED` at 7:01 PM; `final.zip` and `best_det.zip` share an md5, and `best_det.json` says step 2.6M, best_score 23.9). Stage J s1 stopped at 2.1M (last checkpoint 6:41 PM, no process running). A new run `stageJ4_s1` (warm from `_snap/best_det`, t_down 0.27, T0 55) wrote 100k-300k by 7:05 PM and is not running now; `scripts.v5_ref_fit` is fitting a new reference into `stageK_ref/`. Harness mph matches the Trainer's eval.jsonl (46.9, 0, 0) and the Trainer's gate-0.25 harness run of s0 ckpt_2600k (`stageJ_harness/s0_ckpt_2600k.json`, 46.9 mph, same 4 FAILs). s0 best_det/final and s0 ckpt_2600000 score identically.

| checkpoint | contact | impact mph (median) | failing checks |
|---|---|---|---|
| stageJ_s0 best_det/final (2.6M) | 24/24 | 46.9 | seq order (arm peaks 35 ms after club), X-factor 93.3, GRF (4.0 BW), total/carry 2.58 (carry ~33 yd). First Stage J result where smash (1.34), spin (2702) and launch (8.7) all PASS; club speed 46.9 WARN; golfphys carry and all four peak speeds PASS |
| stageJ_s0 ckpt_2600000 | 24/24 | 46.9 | identical to best_det above |
| stageJ_s1 ckpt_2100000 | 0/24 | - (whiff, club peak 0.22x target) | seq order (thorax/arm), thorax and club peak speed (0.41x, 0.22x), GRF (10.4 BW) |
| stageJ4_s1 ckpt_300000 | 0/24 | - (whiff) | seq order (pelvis/thorax, arm/club), X-factor 95.0, GRF (6.9 BW); pelvis peak 1.40x WARN |

Added 2026-10-18 ~8:15 PM ET, overnight watch (club_len 1.15, arm_dist 0.6, 24 deterministic eps, strike gate OFF via `results/overnight/_run_j_gateoff.py` and the Trainer's JEnv adapter; scoring code unmodified). Stage K (`train.v5_train_j --tag stageK`, reference-guided residual policy with tracking assistance, re-timed `stageK_ref/tuned_keys.json` reference, hard X-factor cap 66, GRF 1.7) started 7:30 PM. s0 (res_scale 1.0) is training (1.0M at 8:07 PM); s1 (res_scale 0.7) hit `STOP_REACHED` at 500k (`final.zip`), was resumed with `--no_stop` at 7:56 PM and is at 800k. Both `best_det.json` files point at step 800k, so the ckpt_800000 files were scored in place of the moving `best_det.zip`. Harness mph matches the Trainer's eval.jsonl at every scored step (58.7, 52.7, 58.5, 48.5).

| checkpoint | contact | impact mph (median) | failing checks |
|---|---|---|---|
| stageK_s1 ckpt_800000 (= best_det) | 24/24 | 58.7 | total/carry 2.12 only (carry ~59 yd). Best result of the project: 12 PASS / 2 WARN / 1 FAIL. Seq order WARN only (thorax/arm within one 20 ms sample), club speed 58.7 WARN (below the 60 mph driver floor); X-factor 58.8, GRF 1.30 BW, smash 1.34, spin 2277, launch 10.7, all four peak speeds and golfphys carry PASS. Trainer eval lateral miss 14.4 m |
| stageK_s1 final (500k) | 24/24 | 58.5 | seq order (thorax/arm), spin 4847, total/carry 1.69; smash 1.18 WARN, pelvis/arm peak speed WARN; X-factor 56.0, GRF 0.98 BW, launch 11.9 PASS |
| stageK_s0 ckpt_800000 (= best_det) | 24/24 | 52.7 | seq order (arm/club), GRF (5.15 BW), spin 4069, total/carry 2.31; X-factor 56.1, launch 9.2 PASS |
| stageK_s0 ckpt_1000000 | 24/24 | 48.5 | seq order (arm/club), launch -0.1, total/carry 32 (carry ~3 yd); X-factor 58.3, GRF 1.46 BW, smash 1.31, spin 2679 PASS |

### 2026-10-18 ~8:45 PM ET: total/carry re-derived through golfphys (Orchestrator: do not waive; make it real)
`eval/golfphys_total.py` feeds each strike's measured ball speed, launch, azimuth, back/side spin through `golfphys.sim.shot_from_launch` (vendored from golfphys-lh-fix 357bc0c, LH fix included; roll=True vs roll=False, normal turf) and `realism_check --env v5` now uses that total/carry for the `total_over_carry` check. The env-logged numbers are kept alongside in `golfphys_total.env_*`.
**Correction:** the env-logged `total_m_model` is already golfphys with roll=True (`env/v5_shot.py`; only `carry_m_noroll` is no-roll), so the earlier "env has no roll" reading of the 2.1 ratio was wrong. The independent recompute agrees with the env to <=0.13 yd.
Verification: `tests/test_golfphys_total.py` against the 45+ TrackMan carry/total optimizer rows (`roll_aoa_validation.json`): carry max error <8 yd, total mean error +2.3 yd (max 14 yd), total/carry within 0.10 of the published ratio; sidespin sign round-trip. Verified for normal-turf, descent angle ~30-40 deg shots only.
| checkpoint (24 det. eps, club 1.15, arm 0.6, gate off) | carry yd (golfphys) | total yd (golfphys roll) | total/carry | env total/carry | descent deg | verdict |
|---|---|---|---|---|---|---|
| stageK_s1 ckpt_800000 | 59.3 | 126.0 | 2.125 | 2.119 | 13.3 | FAIL (this check only; 12 PASS / 2 WARN / 1 FAIL) |
| stageK_s0 ckpt_800000 | 32.3 | 75.4 | 2.331 | 2.312 | 11.0 | FAIL (7 PASS / 4 WARN / 4 FAIL) |
Caveat: the ratio is a real golfphys roll output, driven by the shallow descent (11-13 deg vs ~37 deg for a driver shot): the roll model is validated only against ~30-40 deg descents, so 2.1-2.3 is a model extrapolation, not a measured roll. It is not waived: the check stays FAIL until descent/launch are in the driver range.

Added 2026-10-18 ~9:15 PM ET, overnight watch (club_len 1.15, arm_dist 0.6, 24 deterministic eps, strike gate OFF via `results/overnight/_run_j_gateoff_gp.py`: the Trainer's JEnv adapter plus the golfphys total/carry worker; scoring code unmodified). All are reference-guided residual policies with tracking assistance (`train.v5_train_j`, `stageK_ref/tuned_keys.json`). New runs: `stageK2_s0` (stopped at 600k, 8:37 PM; snapshot `_snap/K2_s0_600k` has the same best_det md5) and `stageK3_s0/s1` (warm-started from that K2 snapshot at 8:53 PM, launch/descent/dynamic-loft/spin terms; s1 has double the launch and descent weights; both still training, 300k at 9:03 PM). stageK_s1 kept training with `--no_stop` up to 1.5M (0 contact at 1.5M in the Trainer's eval); its best_det is still step 800k (already scored). Harness club mph matches the Trainer's eval.jsonl at every scored step (62.8, 62.5, 63.0, 61.3, 52.4).

| checkpoint | contact | impact mph (median) | carry / total yd (golfphys) | failing checks |
|---|---|---|---|---|
| stageK3_s1 best_det (200k) | 24/24 | 62.8 | 67.6 / 84.4 (ratio 1.25, descent 28.4 deg) | GRF (2.93 BW peak, band 0.8-1.7), spin 5154. Seq order PASS, X-factor 63.6 PASS, total/carry 1.25 PASS (first Stage K pass of this check); launch 19.2 WARN, smash 1.12 WARN, pelvis timing WARN. 10 PASS / 3 WARN / 2 FAIL |
| stageK3_s1 ckpt_300000 | 24/24 | 61.3 | 54.4 / 78.3 (1.44, descent 21.2) | spin 4785, total/carry 1.44. Seq order PASS, launch 15.5 PASS, X-factor 62.7 PASS; GRF 1.79 BW WARN, smash 1.08 WARN. 10 PASS / 3 WARN / 2 FAIL |
| stageK3_s0 best_det (300k) | 24/24 | 62.5 | 54.8 / 92.6 (1.69, descent 16.2) | GRF (2.56 BW), spin 4098, total/carry 1.69. Seq order WARN (pelvis/thorax one sample), launch 12.0 PASS, X-factor 64.3 PASS. 8 PASS / 4 WARN / 3 FAIL |
| stageK2_s0 best_det (600k) | 24/24 | 63.0 | 47.8 / 87.3 (1.83, descent 15.3) | total/carry 1.83 only. GRF 1.02 BW PASS, launch 11.9 PASS, X-factor 63.9 PASS; seq order WARN, spin 3744 WARN, smash 1.06 WARN, pelvis peak 0.67x WARN. 9 PASS / 5 WARN / 1 FAIL |
| stageK_s1 ckpt_1400000 | 24/24 | 52.4 | 35.4 / 97.1 (2.74, descent 9.1) | seq order (thorax/arm), total/carry 2.74; club speed 52.4 WARN, GRF 2.13 BW WARN, smash 1.27 WARN; spin 2689 and launch 7.8 PASS |

No checkpoint passes all checks. The descent-angle terms in K3 moved total/carry into range for s1 best_det (descent 28 deg) but that came with high spin (4800-5200 rpm), low smash (1.08-1.12) and, on best_det, lead-foot GRF 2.9 BW.

Added 2026-10-18 ~10:15 PM ET, overnight watch (club_len 1.15, arm_dist 0.6, 24 deterministic eps, strike gate OFF via `results/overnight/_run_j_gateoff_gp.py`: Trainer's JEnv adapter plus golfphys total/carry; scoring code unmodified). All are reference-guided residual policies with tracking assistance (`train.v5_train_j`). `stageK3_s1` stopped at 1.0M (9:33 PM; best_det moved to 600k). New `stageK4_s0/s1` warm-started from `_snap/K3b_s0_500k` at 9:50 PM (spin, dynamic-loft, launch and smash terms; s1 adds `--spd_w 3`), both at 500k and still training at 10:10 PM. The moving K4 `best_det`/`ckpt_500000` files were copied to `results/overnight/_evalsnap/` before scoring (md5 checked). K3b_s0 500k was already scored (`*_snap500k_gateoff_gp_*`). Harness club mph matches the Trainer's best_det.json at every best_det scored (65.7, 63.5, 61.0).

| checkpoint | contact | impact mph (median) | carry / total yd (golfphys) | failing checks |
|---|---|---|---|---|
| stageK4_s0 best_det (100k) | 24/24 | 61.0 | 97.1 / 117.2 (1.21, descent 31.9) | spin 4087 only. Seq order PASS, X-factor 55.4, GRF 1.58 BW, smash 1.35, club speed, total/carry PASS; launch 19.8 WARN, pelvis timing WARN. 12 PASS / 2 WARN / 1 FAIL (ties the best count; first with seq order and total/carry both PASS and spin the only FAIL) |
| stageK4_s0 ckpt_500000 | 24/24 | 61.6 | 75.8 / 108.9 (1.44, descent 20.5) | total/carry 1.44 only. Spin 3889 WARN, smash 1.26 WARN, pelvis timing WARN; seq order, X-factor 63.3, GRF 1.41, launch 13.6 PASS. 11 PASS / 3 WARN / 1 FAIL |
| stageK4_s1 best_det (400k) | 24/24 | 63.5 | 75.6 / 107.5 (1.42, descent 21.7) | spin 4384, total/carry 1.42. Seq order WARN (thorax/arm one sample), smash 1.24 WARN, pelvis peak 0.65x WARN; X-factor 55.6, GRF 1.34, launch 14.7 PASS. 10 PASS / 3 WARN / 2 FAIL |
| stageK4_s1 ckpt_500000 | 24/24 | 60.7 | 69.2 / 123.2 (1.78, descent 14.0) | spin 4127, total/carry 1.78. Seq order, X-factor 57.4, GRF 1.25, smash 1.36, launch 9.4 PASS. 11 PASS / 2 WARN / 2 FAIL |
| stageK3_s1 best_det (600k) | 24/24 | 65.7 | 91.4 / 108.4 (1.19, descent 31.4) | seq order (thorax peaks before pelvis), spin 5309. X-factor 57.8, GRF 1.41, total/carry PASS; smash 1.26 and launch 19.0 WARN. 9 PASS / 4 WARN / 2 FAIL |
| stageK3_s1 ckpt_1000000 (final) | 0/24 | - (whiff) | - | arm peak speed 1.73x target; no shot checks computable |

No checkpoint passes all checks. Pattern: when descent is driver-like (~31 deg) total/carry passes but spin is 4100-5300 rpm and launch ~19-20 deg (too much dynamic loft); when spin/launch come down, descent drops to 14-21 deg and total/carry fails (1.4-1.8). Spin and descent are trading off against each other through loft rather than through lower spin loft / higher ball speed.

Added 2026-10-18 ~11:10 PM ET, overnight watch (club_len 1.15, arm_dist 0.6, 24 deterministic eps, strike gate OFF via `results/overnight/_run_j_gateoff_gp.py`: Trainer's JEnv adapter plus golfphys total/carry; scoring code unmodified). All are reference-guided residual policies with tracking assistance (`train.v5_train_j`). New `stageK4b_s0/s1` (started 10:14 PM; s0 warm-started from `_snap/K4_s0_100k`, s1 from `_snap/K3b_s0_500k` with `--spd_w 2`; spin_hi 2900, xf_hard 66, grf_lo 1.7). Checkpoints 100k/200k were saved at 10:18/10:22 PM; the processes were restarted at 10:59 PM and were still running at 11:08 PM. The 200k best_det and 100k files were copied to `results/overnight/_evalsnap/K4b_*` (with args.json) before scoring. `_stageK4a_s0/s1` are underscore-prefixed (abandoned) and were skipped. Harness club mph matches the Trainer's best_det.json (62.2, 47.5).

| checkpoint | contact | impact mph (median) | carry / total yd (golfphys) | failing checks |
|---|---|---|---|---|
| stageK4b_s1 best_det (200k) | 24/24 | 47.5 | 56.8 / 95.3 (1.68, descent 18.3) | total/carry 1.68 only. Seq order PASS, spin 2245 PASS (first in-band spin of Stage K), smash 1.42 PASS, launch 14.5, X-factor 57.8, GRF 1.33 PASS; club speed 47.5 WARN (below the 60 mph driver floor), pelvis timing WARN. 12 PASS / 2 WARN / 1 FAIL |
| stageK4b_s0 best_det (200k) | 24/24 | 62.2 | 40.7 / 89.5 (2.20, descent 11.4) | seq order (thorax peaks after arm), total/carry 2.20. X-factor 65.7 WARN, GRF 2.22 BW WARN, smash 1.08 WARN, spin 3988 WARN, pelvis timing WARN; launch 9.1 PASS. 8 PASS / 5 WARN / 2 FAIL |
| stageK4b_s0 ckpt_100000 | 24/24 | 60.3 | 27.2 / 69.2 (2.55, descent 10.3) | seq order (thorax/arm), total/carry 2.55. X-factor 59.8, GRF 1.56, launch 8.9 PASS; smash 0.95 and spin 3505 WARN. 10 PASS / 3 WARN / 2 FAIL |
| stageK4b_s1 ckpt_100000 | 0/24 | - (whiff) | - | seq order (arm/club), GRF 3.35 BW; no shot checks computable |

No checkpoint passes all checks. K4b s1 best_det fixed spin and smash (2245 rpm, 1.42) but at 47.5 mph and an 18 deg descent, so total/carry stays 1.68; K4b s0 regressed from its K4_s0 100k start (spin-only FAIL, descent 32 deg) to a low descent (11 deg) with sequence order broken.

### Oct 19 ~00:15 ET: Stage K4b s1 300k-1.4M and Stage K4c s0 100k-1.1M (gate off, golfphys total/carry, BEnv arm_dist 0.6, 24 det. eps)
Reference-guided residual with tracking assistance (JEnv adapter). All 23 FAIL.
- Near misses: K4c_s0 ckpt_900000 (61.8 mph, 24/24): only lead-leg GRF 3.15 BW fails; seq order PASS, total/carry 1.34 WARN, spin 3560 WARN.
- K4b_s1 ckpt_1000000 (63.3 mph, 24/24): only seq order fails (arm peaks before thorax); spin 3992 WARN, total/carry 1.32 WARN.
- K4b_s1 ckpt_700000 (62.2 mph): only seq order fails; spin/launch/total-carry WARN.
- K4b_s1 1.1M / 1.2M, K4c_s0 600k/700k/800k: only total/carry fails (1.45-2.65).
- Whiffs (0/24): K4b_s1 300k, 900k; K4c_s0 300k, 400k.

### Oct 19 ~01:20 ET: Stage K4c s0 1.2M-2.5M, K4b s1 1.5M/1.6M, K5 s2 100k-700k, K3b s0 100k-400k (gate off, golfphys total/carry, BEnv arm_dist 0.6, 24 det. eps)
Reference-guided residual with tracking assistance (JEnv adapter). All 27 FAIL (none passes every check).
- Best of project: K5_s2 ckpt_700000 (= best_det/final step, 60.8 mph, 24/24): 14 PASS / 0 WARN / 1 FAIL; only total/carry 1.36 fails (gate 1.04-1.25). Seq order + timing PASS, X-factor 57.9, lead GRF 1.31 BW, smash 1.43, spin 2949 (window 1800-3000), launch 15.98 (window 7-16), carry 103 yd vs golfphys 104. Spin, launch and club speed (floor 60) all sit right at their edges.
- Only total/carry fails: K5_s2 200k (1.89), 300k (1.37), 500k (1.49), 600k (1.54); K4c_s0 1.4M (=best_det, 1.58), 1.8M (2.14); K3b_s0 200k (2.55).
- K4c_s0 after 1.4M mostly breaks sequence order and drifts in speed (26-68 mph); 2.0M is fastest (68.2 mph) but fails seq, spin 4964, launch 20.9.
- Whiffs (0/24): K4c_s0 1.2M, 1.7M; K4b_s1 1.6M (= final; harness overall WARN only because shot checks skip with no contact; run marked STALLED).

### Oct 19 ~02:20 ET: Stage K6 s3/s4 100k-700k, K4c s0 2.6M/2.7M (gate off, golfphys total/carry, BEnv arm_dist 0.6, 24 det. eps)
Reference-guided residual with tracking assistance (JEnv adapter). All 16 FAIL (none passes every check). All 16 make contact 24/24 (no whiffs).
- Best: K6_s4 ckpt_200000 (= best_det, 64.5 mph): 13 PASS / 1 WARN / 1 FAIL; only total/carry 1.44 fails. Seq order + timing PASS, spin 2843, launch 13.6, smash 1.37, GRF 1.50 BW, X-factor 58.0. WARN is pelvis peak speed 265 deg/s (0.66x an extrapolated target).
- K6_s3 600k (65.5 mph): only spin 4480 fails; total/carry 1.33 WARN (closest to the gate this batch).
- Only total/carry fails: K6_s3 100k (1.45), 200k (1.44), 300k (1.52), 700k (1.49); K6_s4 100k (1.44), 300k (1.45), 400k (1.35), 500k (1.36), 600k (2.20, 45.7 mph), 700k (1.64, 47.3 mph).
- K6_s3 400k fails spin 4479 + t/c 1.57; K6_s3 500k fails GRF 2.41 BW, spin 5606, t/c 1.47.
- K4c_s0 2.6M fails spin 5254 + t/c 1.76; 2.7M fails GRF 2.61 BW + t/c 2.82 (launch 5.0).
- Every K6 checkpoint WARNs on pelvis peak speed (180-280 deg/s) and most on sequence timing (pelvis peaks ~175-205 ms before club).

### Oct 19 ~03:20 ET: Stage K7 s5/s6 100k-800k (gate off, golfphys total/carry, BEnv arm_dist 0.6, 24 det. eps)
Reference-guided residual with tracking assistance (JEnv adapter; K7 inits from K6_s4 200k). None passes every check: 14 FAIL, 2 WARN (zero FAILs but not a PASS). All 16 make contact 24/24 (no whiffs).
- First zero-FAIL results of the project: K7_s6 ckpt_400000 (65.8 mph): 11 PASS / 4 WARN / 0 FAIL; WARNs are sequence timing (pelvis peaks 180 ms before club, band 40-140), smash 1.30, spin 3339, total/carry 1.35. Seq order PASS, pelvis 302 deg/s PASS, X-factor 57.5, GRF 1.33 BW, launch 15.9.
- K7_s6 ckpt_800000 (= final step, 66.5 mph): 12 PASS / 3 WARN / 0 FAIL; WARNs are sequence timing (pelvis 180 ms), spin 3473, total/carry 1.34. Smash 1.43, launch 12.6, GRF 1.39 BW, pelvis 348 deg/s PASS.
- K7_s6 300k (62.4 mph): 14 PASS / 0 WARN / 1 FAIL; only total/carry 1.47 fails (spin 2421, launch 14.7, timing PASS).
- K7_s5 400k (13 PASS/1 WARN) and 700k (= best_det, 65.2 mph, 13 PASS/1 WARN): only total/carry fails (1.52, 1.39); 700k spin 2774, launch 14.3.
- K7_s6 700k (67.5 mph, fastest): fails spin 4731; t/c 1.26 WARN, GRF 1.94 WARN. K7_s5 800k (final) collapses to 36.1 mph (spin 804, t/c 2.85). K7_s5 100k fails seq order (pelvis after thorax).
- Remaining gap to a full PASS: total/carry (1.34-1.35 vs PASS <=1.25), spin (3300-3500 vs <=3000), and pelvis peaking too early (~180 ms before club).

### What is committed (repo port, 2026-10-19)
Committed to the public repo: this README and the 20 slim per-checkpoint JSONs in `results/v5_runs/stageJK_harness_summary/` (aggregate check verdicts and medians, no per-episode data), which cover the Stage J/J4 and Stage K s0/s1 rows above, plus one Stage K7 harness output, `realism_v5_stageK7_s6ckpt_800000_gateoff_gp_arm06.txt` (the Evaluator's independent K7_s6 800k score; aggregate check verdicts only, no per-episode data). Not committed (held locally by the Evaluator): every other `results/overnight/` output named in this file (the raw `realism_v5_*.json` / `.txt` harness outputs with per-episode data, including all K2-K6 rows above, and the K7 `.json` files, which carry a per-episode `golfphys_total.episodes` list; the other 15 K7 `.txt` summaries are also held locally, not committed), the `_evalsnap/` checkpoint copies and the `_run_j_gateoff*.py` local wrapper scripts (machine-specific paths). Numbers in the K2-K6 tables and the K7 rows other than K7_s6 800k are therefore Evaluator-reported [harness JSON held locally]; the Trainer's own harness JSONs for several K5-K7 checkpoints are committed separately in `results/v5_runs/stageJ_harness/`. All rows are reference-guided residual policies (script-distilled init + residual), NOT from-scratch; none passes every check.
