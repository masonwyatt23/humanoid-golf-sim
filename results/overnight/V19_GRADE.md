# V19 official grading (Evaluator, 2026-10-25 ~6:10 PM ET)

This is the OFFICIAL grade. The Trainer's local numbers (local run of the Evaluator worker, Trainer 7f5445e0 era) are not official.

**Checkpoint.** V18w_s661 100k (Trainer cmd b869788b): continues V18v 100k (+optimizer state), lr 1e-5, +100k steps, seed 661; `--stance_obs`, `--reground_frac 0.5` (training-side), V12X refit keys (`results/v5_runs/stageV12X_ref_s1/tuned_keys_flat.json`). Labels: stage J and later = reference-guided residual with tracking assistance; K8+ also = reference re-tuned open-loop by CMA-ES, stock G1 torque, warm-started. Trainer local v4: 13/5/1, .958/.958/.875, club p10 70.0 mph.

**Setup.** As V18 (`_batch_V18.sh` -> `_batch_V19.sh`, plus the v4.1 row from `_batch_V41.sh`). No harness code changed. All runs exited 0 (wall 6:06-6:11 PM ET).
- Read-only Trainer export 7f5445e0 (Trainer box HEAD at grading time; contains b869788b). Since b663c9f6 (V18) the env-side change is `train/v5_train_j.py` (training options) plus `train/reground_v41.py` (training-side); env/, golfphys/ and eval/ unchanged.
- args.json: env_v4 true, stance_obs true, tee_mode 1.5in, keys stageV12X_ref_s1.
- Keys md5 (same keys as V16-V18) and snapshot md5s were verified (export = Trainer HEAD; Evaluator copy = Trainer snapshot, all MATCH) and are not published here.
- Layout pre-check LAYOUT_OK (obs 120 = 116 + 4 stance, model 120, vecnorm 120, act 29, 121 keys). v4 address cross-check passed (face centre 29 mm, CFZ 39 mm, lie 58.5, Izz 5600 = n=1 manufacturer claim, ball centre 59.4 mm at 1.5 in, 62 mm crown).
- Worker: arm 0.6, club 1.15, 24 deterministic episodes, gate off, golfphys, robustness seeds 7000-7023, cores 0-1, 2 workers, BLAS threads 2. One job at a time. A Trainer grading job (V19a) was running on other cores at the same time.

| ckpt | v4 1.5in (gating) | v4 crown16 INFO (v4 head, 1.6 in crown tee (equator at sourced crown)) | v3c 1.5in | v3d 1.5in |
|---|---|---|---|---|
| V18w_s661 100k | 13/5/1 FAIL | 13/5/1 | 12/4/2 | 13/5/1 |

**Only failing row on v4 1.5 in: mine/robustness.** Triple contact 0.958 (23/24; seed 7002 misses), start direction 0.958 (23/24), lead-foot plant 0.875 (21/24; 7002 plus foot WARN on 7012, 7021) vs 0.95/0.90/0.90: contact and start direction pass, plant misses by one episode (same as V18l). Shot sub-requirements: club speed median 70.6, p10 70.0 mph = 0.99 x median (passes the >= 0.93 rule, which is LOW CONFIDENCE); smash p10 1.34 pass; launch pass; spin median 2708, p10 1214 WARN, p90 4239 FAIL; total/carry median 1.414 FAIL, p10 1.323 WARN, p90 1.814 FAIL.

**v4 1.5 in WARN rows:** kinematic_sequence_order, sequence timing (pelvis -24, thorax 12, arm 4 ms; DERIVED bands), peak pelvis 247.9 deg/s (< 250, DERIVED floor), lead-foot vertical GRF 1.76 BW, shot/total_over_carry 1.321.
Nominal: club 70.6 mph, smash 1.431, spin 2589 PASS, launch 14.05, carry 131.6 yd (golfphys), strike dz +1.7 mm, dy +3.2 mm (toe +); strike_height pass. Robustness strike (n 23): dz median +0.0, p10 -22.1, p90 +16.0 mm; dy median +0.9, p10 -20.5, p90 +14.5 mm. Robustness INFO rows: wide friction .79/.75/.75; stress mu 1.1 .79/.75/.75 (club p10 55.7).

Crown16 INFO: same counts; robustness .958/.958/.875, club p10 70.0, spin p10 1093 / p90 4204 FAIL, launch p90 WARN; nominal spin 2403, strike dz +4.3, dy +3.7 mm.
v3c: 12/4/2 (robustness + kinematic_sequence_order FAIL under v3c bands, as before).

**v4.1 robustness (re-grounded, info only, non-gating)** (same JSON as a separate run with `--reground`; its v4 part is identical to the v4 main JSON in every field): .833/.833/.792 (contact 20/24, start 20/24, plant 19/24), club p10 67.4 mph (0.95 x median), spin p90 FAIL, t/c median/p90 FAIL -> would FAIL if gating. Sole residuals before 15.5 mm median (max 27.2), after < 0.001 mm. Worse than v4 on all three fractions, like V18l (.833/.792/.833), V18i and V18f. A v4.1-only pass would not be a full pass; there is none here anyway.

**Versus the Trainer's local run:** v4 1.5 in, crown16 and v3c identical: same counts, same per-episode robustness and strike records, same checks in every field (only key/label and an extra per-episode golfphys_total listing in our JSON differ). v3d official 13/5/1 vs Trainer 12/5/1: +1 is mine/strike_height (pass; absent from the Trainer's local v3d JSON along with the face-edge INFO rows, as in prior grades). No other difference. The Trainer did not run v4.1, heldout or D-plane rows.

**Versus earlier official grades:** V18l 50k 13/5/1 (.958/.917/.875, club p10 60.5); V18i 150k 13/5/1 (.917/.875/.833, 56.3); V16y 50k 13/4/2 (.958/.917/.917). V18w is the best official v4 robustness triple so far on contact/start (start .958 is new), plant still one episode short, and the club-speed tail is fixed (p10 70.0). The remaining shot failures are spin p90 and total/carry median/p90.

**v5 (NON-GATING estimates):**
- heldout-1: .500/.375/.125 (V18l .458/.333/.083); club p10 45.7 WARN.
- heldout-2 excl. slope (28 eps): .857/.857/.786 (V18l .821/.821/.821). Slope (4 eps, modelling gap, excluded): 0/4.
- Driver per-club: smash 1.431, launch 14.05, spin 2589 pass; land angle FAIL 24.5 deg (warn floor 25, derived band). Task rows n/a (not goal-conditioned). The heldout run logged 3 MuJoCo QACC-instability warnings (V18l: 4), in held-out episodes.
- D-plane (perturbed robustness episodes, 23 distinct; thresholds are our assumption): start vs 0.85 x face 11/23 = 0.478 FAIL (< 0.60; V18l .652 WARN), curve sign 21/21 pass; start_err median -0.21, p10 -4.42, p90 +2.62, min -6.42, max +3.87 deg. Medians (world, + = left): face -1.47, path -1.45, start -0.88. Nominal (n = 1): face -2.73, path -2.67, start -2.10, err +0.22 (ok).

**Verdict: NOT a full pass.** v4 at 1.5 in fails on robustness (plant .875 < .90; spin p90 and total/carry tails). No cinematic render.

Summary script: `_summ_V19.py [trainer_clone]`.
