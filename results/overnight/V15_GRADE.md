# V15 official grading (Evaluator, 2026-10-25 ~1:20 PM ET)

This is the OFFICIAL grade. The Trainer's local numbers are not official.

**Checkpoint.** V18d_s511 50k (Trainer local v4 13/5/1). Reference-guided residual policy with tracking assistance, warm-started from V13h_s240 50k, on the V12V refit keys (`results/v5_runs/stageV12V_ref_s1/tuned_keys_flat.json`). Chosen from the new V18c/V18d/V18e snapshots as the best robustness-only fail; it is the first graded snapshot since V13h where nominal total/carry is a WARN rather than a FAIL alongside a robustness triple at or above V13h.

**Setup.** Same procedure as V14 (`_batch_V14.sh` -> `_batch_V15.sh`). Harness v4 on the env_v4 head; gating row = 1.5 in tee; crown 1.6 in INFO; v3c/v3d at 1.5 in. All runs exited 0.
- Read-only Trainer export 2a511cb9 (Trainer box HEAD at grading time; contains the V12V keys).
- args.json: env_v4 true, tee_mode 1.5in, keys stageV12V_ref_s1.
- Keys md5 and snapshot md5s (checkpoint, vecnorm, args) were verified (export = Trainer HEAD; Evaluator copy = Trainer snapshot, all MATCH) and are not published here (Repo Agent rule).
- Layout pre-check LAYOUT_OK (obs 116, act 29, 121 keys).
- Worker: arm 0.6, club 1.15, 24 deterministic episodes, gate off, golfphys, robustness seeds 7000-7023, cores 0-1, 2 workers, BLAS threads 2.

| ckpt | v4 1.5in (gating) | v4 crown16 INFO | v3c 1.5in | v3d 1.5in |
|---|---|---|---|---|
| V18d_s511 50k | 13/5/1 FAIL | 13/5/1 | 12/4/2 | 13/5/1 |

**Only failing row: mine/robustness.** Triple contact 0.917 (22/24), start direction 0.792 (19/24), lead-foot plant 0.875 (21/24) vs 0.95/0.90/0.90. Shot sub-requirements also fail: total/carry median 1.369 / p90 1.828 outside WARN, spin p10 701 / p90 4228 outside WARN; club speed p10 55.8 = 0.80 x median (rule LOW CONFIDENCE), smash p10 1.231 and launch p90 16.4 leave PASS.

**v4 1.5 in WARN rows:** kinematic_sequence_order, sequence timing (pelvis -24, thorax 12, arm 4 ms), peak pelvis speed 221.4 deg/s (< 250), lead-foot vertical GRF (1.98 BW filtered), shot/total_over_carry 1.285 (WARN band; PASS 1.04-1.25, DERIVED).
Nominal: club 70.3 mph, smash 1.427, spin 2855, launch 14.7, carry vs golfphys -0.1 yd, strike dz -0.2 mm, dy -2.6 mm (toe +), slip 1.6 cm.

**Versus the Trainer's local run:** v4 1.5 in, crown and v3c identical check-for-check. v3d official 13/5/1 vs Trainer 12/5/1: the +1 is mine/strike_height, absent from the Trainer's local v3d JSON (as in V12-V14).

**Versus earlier official grades:** V13h 50k 13/5/1 (.917/.75/.875, t/c 1.348 WARN, pelvis 243.7); V16y/V17f 50k 13/4/2 (.958/.917/.917, t/c 1.403/1.438 FAIL). V18d keeps the nominal t/c WARN and centres the strike (dy -2.6 vs +16.8 mm on V16y) but gives back the V16y/V17f robustness triple, and pelvis speed drops to 221.4.

**v5 held-out DR (NON-GATING estimates, `--harness v5 --heldout-dr 24 --heldout2-dr 32`; v4 part reproduced 13/5/1):**
- heldout-1: .375/.25/.083 (V16y .54/.33/.17, V13h .46/.33/.12).
- heldout-2 excl. slope (28 eps): .79/.79/.79 (V16y .82). Slope 0/4 (info-only).
- Driver per-club: smash/launch/spin pass, land angle WARN 26.1 deg (V16y FAIL 20.7). D-plane PASS: start vs 0.85 x face 24/24, curvature sign 24/24 (V16y/V17f 0/24). Task rows n/a (not goal-conditioned).

No full pass (robustness fails), so no cinematic render.
