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

Not committed: on branch scott-e `results/overnight/` is untracked (the earlier result commits such as 9b44bb1 sit on `backup-scott-e-pre-c4186d3`), so a commit here would add the whole folder to scott-e; left for the Orchestrator to decide.
