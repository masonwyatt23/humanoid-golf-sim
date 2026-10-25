# V17 official grading (Evaluator, 2026-10-25 ~3:15 PM ET)

This is the OFFICIAL grade. The Trainer's local numbers are not official.

**Checkpoint.** V18i_s560 150k (Trainer local v4 13/5/1). Reference-guided residual policy with tracking assistance, fresh-init lineage (init from R0V12T_s0 100k), on the V12X refit keys (`results/v5_runs/stageV12X_ref_s1/tuned_keys_flat.json`). Picked from the new V18h-V18k snapshots because it is the first local 13/5/1 that also keeps V18f's robustness triple and passes nominal spin. V18i 150k is also the warm start for V18k and the stageG2 goal run.

**Setup.** Same procedure as V16 (`_batch_V16.sh` -> `_batch_V17.sh`), plus the fixed v5 D-plane row (harness b9e38999, perturbed robustness episodes). All runs exited 0.
- Read-only Trainer export 94205e13 (Trainer box HEAD at grading time; env code unchanged since 4d22d58a, only training/diagnostic scripts differ; contains the V12X keys).
- args.json: env_v4 true, keys stageV12X_ref_s1.
- Keys md5 and snapshot md5s were verified (export = Trainer HEAD, same keys as V16; Evaluator copy = Trainer snapshot, all MATCH) and are not published here (Repo Agent rule).
- Layout pre-check LAYOUT_OK (obs 116, act 29, 121 keys).
- Worker: arm 0.6, club 1.15, 24 deterministic episodes, gate off, golfphys, robustness seeds 7000-7023, cores 0-1, 2 workers, BLAS threads 2.

| ckpt | v4 1.5in (gating) | v4 crown16 INFO | v3c 1.5in | v3d 1.5in |
|---|---|---|---|---|
| V18i_s560 150k | 13/5/1 FAIL | 13/5/1 | 12/4/2 | 13/5/1 |

**Only failing row: mine/robustness.** Triple contact 0.917 (22/24), start direction 0.875 (21/24), lead-foot plant 0.833 (20/24) vs 0.95/0.90/0.90 (same triple as V18f). Shot sub-requirements: club speed p10 56.3 mph = 0.80 x median (new slow-swing tail; V18f p10 70.2), smash p10 1.25 WARN, spin p10 867 / p90 4175 outside WARN, total/carry median 1.416 / p90 1.85 outside WARN. The club-speed p10 rule is low confidence.

**v4 1.5 in WARN rows:** kinematic_sequence_order, sequence timing (pelvis -24, thorax 12, arm 4 ms), peak pelvis 242.4 deg/s (< 250), lead-foot vertical GRF, shot/total_over_carry 1.309. Nominal spin 2561 now PASSES (V18f 3840 WARN). v3c makes sequence order a FAIL.
Nominal: club 70.7 mph, smash 1.426, spin 2561, launch 14.6, strike dz +3.1 mm, dy +0.3 mm (toe +), i.e. centred (V18f dz -13.5).

**Versus the Trainer's local run:** v4 1.5 in, crown and v3c identical check-for-check. v3d official 13/5/1 vs Trainer 12/5/1: +1 is mine/strike_height (absent from the Trainer's local v3d JSON, as before).

**Versus earlier official grades:** V18f 50k 12/6/1 (.917/.875/.833, spin 3840 WARN, dz -13.5); V18d 50k 13/5/1 (.917/.792/.875); V16y 50k 13/4/2 (.958/.917/.917). V18i 150k ties the best count and keeps V18f's triple with a centred strike, but adds a club-speed p10 tail.

**v5 (NON-GATING estimates):**
- heldout-1: .458/.333/.083 (V18f .458/.333/.083).
- heldout-2 excl. slope (28 eps): .857/.857/.786 (V18f .714).
- Driver per-club: smash, launch, spin pass; land angle WARN 25.3 deg. Task rows n/a.
- D-plane (perturbed robustness episodes, 22 distinct): start vs 0.85 x face 14/22 = 0.636 WARN (V18f .727), curve sign 21/21; start_err median -1.12, p10 -5.28, p90 +1.85, min -7.01, max +3.24 deg. Medians (world, + = left): face -1.14, path -0.65, start -2.00. Nominal (n = 1): face -2.13, start -2.14, err -0.33 (ok).

No full pass (robustness fails), so no cinematic render.
