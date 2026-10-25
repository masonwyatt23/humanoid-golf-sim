# V14 official grading (Evaluator, 2026-10-25 ~10:50 AM ET)

This is the OFFICIAL grade. The Trainer's local numbers are not official.

**Checkpoints.** V16y_s402 50k and V17f_s422 50k (Trainer local v4 13/4/2 each). Reference-guided residual policies with tracking assistance on the V12U refit keys (`results/v5_runs/stageV12U_ref_s1/tuned_keys_flat.json`, Trainer eb5c38c0; refit diagnostics in results/v10_diag).

**Setup.** Same procedure as V13 (`_batch_V13.sh` -> `_batch_V14.sh`). Harness v4 on the env_v4 head; gating row = 1.5 in tee; crown 1.6 in INFO; v3c/v3d at 1.5 in. All runs exited 0.
- Read-only Trainer export eafa270c (Trainer box HEAD at grading time; contains eb5c38c0).
- args.json (both): env_v4 true, tee_mode 1.5in, keys stageV12U_ref_s1.
- Keys md5 and snapshot md5s (checkpoint, vecnorm, args) were verified (export = Trainer HEAD; Evaluator copy = Trainer snapshot, all MATCH) and are not published here (Repo Agent rule).
- Layout pre-check LAYOUT_OK on both (obs 116, act 29, 121 keys).
- Worker: arm 0.6, club 1.15, 24 deterministic episodes, gate off, golfphys, robustness seeds 7000-7023, cores 0-1, 2 workers, BLAS threads 2.

| ckpt | v4 1.5in (gating) | v4 crown16 INFO | v3c 1.5in | v3d 1.5in |
|---|---|---|---|---|
| V16y_s402 50k | 13/4/2 FAIL | 13/4/2 | 12/3/3 | 13/4/2 |
| V17f_s422 50k | 13/4/2 FAIL | 13/4/2 | 12/3/3 | 13/4/2 |

**Robustness gate triple CONFIRMED passing on both:** contact 0.958 (23/24), start direction 0.917 (22/24), lead-foot plant 0.917 (22/24) vs 0.95/0.90/0.90. First official checkpoints to clear all three. mine/robustness still FAILS on its shot sub-requirements:
- V16y: total/carry median 1.519 / p90 2.053 outside WARN, spin p90 4035 outside WARN (p10 1569 WARN), smash p10 1.268 leaves PASS.
- V17f: total/carry median 1.516 / p90 2.159, spin p90 4107 (p10 1533 WARN), smash p10 1.263.

**v4 1.5 in rows (both):** FAIL shot/total_over_carry (nominal 1.403 V16y, 1.438 V17f) and mine/robustness. WARN kinematic_sequence_order, sequence timing (pelvis -28, thorax 8, arm 0 ms), peak pelvis speed (234.9 V16y, 238.3 V17f deg/s < 250), lead-foot vertical GRF. Crown INFO and v3d have the same warn/fail set; v3c turns sequence order into a FAIL.
Nominal V16y / V17f: club 69.8 / 69.7 mph, spin 2911 / 2953, launch 12.3 / 11.8, strike dz -2.0 / -3.1 mm, dy +16.8 / +18.5 mm, slip 1.5 / 1.5 cm, lead-foot turn 6.2 / 6.2 deg.

**Versus the Trainer's local run:** v4 1.5 in, crown and v3c identical check-for-check on both. v3d official 13/4/2 vs Trainer 12/4/2: the +1 is mine/strike_height, absent from the Trainer's local v3d JSON (as in V12/V13).

**Versus V13h 50k (V13 official):** triple .958/.917/.917 vs .917/.75/.875; but nominal total/carry went from WARN (1.348) to FAIL, so 13/5/1 -> 13/4/2; pelvis 243.7 -> 234.9/238.3.

**v5 held-out DR (NON-GATING estimates, `--harness v5 --heldout-dr 24 --heldout2-dr 32`; v4 part reproduced 13/4/2):**
- heldout-1: V16y .54/.33/.17, V17f .54/.375/.17 (V13h .46/.33/.12).
- heldout-2 excl. slope (28 eps): .82/.82/.82 both. Contact by dim: torque, latency, loft, trunk, foot 4/4; head mass 3/4; thigh+calf 0/4; slope 0/4 (info-only).
- Driver per-club land angle FAIL (20.7 / 19.7 deg); smash/launch/spin pass. D-plane FAIL (start vs 0.85 x face 0/24; curvature sign 24/24). Task rows n/a (not goal-conditioned).

No full pass (total/carry fails), so no cinematic render.
