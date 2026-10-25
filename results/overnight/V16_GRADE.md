# V16 official grading (Evaluator, 2026-10-25 ~1:50 PM ET)

This is the OFFICIAL grade. The Trainer's local numbers are not official.

**Checkpoint.** V18f_s530 50k (Trainer local v4 12/6/1). Reference-guided residual policy with tracking assistance, from V18d 50k, on the V12X refit keys (`results/v5_runs/stageV12X_ref_s1/tuned_keys_flat.json`).

**Setup.** Same procedure as V15 (`_batch_V15.sh` -> `_batch_V16.sh`). Harness v4 on the env_v4 head; gating row = 1.5 in tee; crown 1.6 in INFO; v3c/v3d at 1.5 in; then v5 held-out. All runs exited 0.
- Read-only Trainer export 4d22d58a (Trainer box HEAD at grading time; contains the V12X keys).
- args.json: env_v4 true, tee_mode 1.5in, keys stageV12X_ref_s1.
- Keys md5 and snapshot md5s were verified (export = Trainer HEAD; Evaluator copy = Trainer snapshot, all MATCH) and are not published here (Repo Agent rule).
- Layout pre-check LAYOUT_OK (obs 116, act 29, 121 keys).
- Worker: arm 0.6, club 1.15, 24 deterministic episodes, gate off, golfphys, robustness seeds 7000-7023, cores 0-1, 2 workers, BLAS threads 2.

| ckpt | v4 1.5in (gating) | v4 crown16 INFO | v3c 1.5in | v3d 1.5in |
|---|---|---|---|---|
| V18f_s530 50k | 12/6/1 FAIL | 13/5/1 | 11/5/2 | 12/6/1 |

**Only failing row: mine/robustness.** Triple contact 0.917 (22/24), start direction 0.875 (21/24), lead-foot plant 0.833 (20/24) vs 0.95/0.90/0.90. Shot sub-requirements: total/carry median 1.375 / p90 1.72 outside WARN; spin p90 4286 outside WARN (p10 1559 WARN).

**v4 1.5 in WARN rows:** kinematic_sequence_order, sequence timing (pelvis -28, thorax 8, arm 0 ms), peak pelvis 243.2 deg/s (< 250), lead-foot vertical GRF (1.81 BW), shot/spin_rpm 3840 (new vs V18d), shot/total_over_carry 1.303. Crown INFO drops the spin WARN; v3c makes sequence order a FAIL.
Nominal: club 70.8 mph, smash 1.425, spin 3840, launch 11.4, strike dz -13.5 mm, dy -4.1 mm (toe +), slip 1.4 cm, turn 7.5 deg.

**Versus the Trainer's local run:** v4 1.5 in, crown and v3c identical check-for-check. v3d official 12/6/1 vs Trainer 11/6/1: +1 is mine/strike_height (absent from the Trainer's local v3d JSON, as before).

**Versus earlier official grades:** V18d 50k 13/5/1 (.917/.792/.875, dz -0.2, dy -2.6, spin 2855); V13h 50k 13/5/1 (.917/.75/.875); V16y 50k 13/4/2 (.958/.917/.917). V18f gains start direction vs V18d (.875) but loses plant (.833); the strike moved 13 mm low on the face, which raises nominal spin to a WARN.

**v5 (NON-GATING estimates, `--harness v5 --heldout-dr 24 --heldout2-dr 32`; v4 part reproduced 12/6/1):**
- heldout-1: .458/.333/.083 (V18d .375/.25/.083).
- heldout-2 excl. slope (28 eps): .714 (all three). Contact by dim: latency, loft, trunk, foot 4/4; head mass 3/4; torque 1/4; thigh+calf 0/4; slope 0/4 (info-only).
- Driver per-club: spin WARN 3840, land angle FAIL 22.4 deg; smash/launch pass. Task rows n/a.
- [NOMINAL-ONLY, n=1; superseded by the Correction below and results/overnight/DPLANE_CORRECTION.md] D-plane PASS 24/24 (start vs 0.85 x face) and curvature sign 24/24. Medians (world, + = left): face -0.16, path -0.95, start -1.09, start_err -0.95, spin axis +3.56, spin loft 19.1 deg. CAVEAT: the 24 deterministic episodes are identical (start_err spread 0.000 deg; same for V18d and V16y), so the D-plane row is effectively one nominal swing, not 24 independent checks. It says nothing directly about the perturbed robustness episodes.
- Contrast: V18d face -2.56 / start -3.17 / err -0.99 / axis +3.18 (pass, centred strike); V16y face -4.43 / start -1.26 / err +2.51 / axis -8.59 (fail, toe strike dy +16.8).

No full pass (robustness fails), so no cinematic render.

## Correction (2026-10-25 ~2:00 PM ET): v5 D-plane

The D-plane PASS 24/24 above was computed on the 24 deterministic nominal rollouts, which are identical (start_err spread 0.000 deg): it is ONE nominal swing, not 24 checks. The row now grades the perturbed v4 robustness episodes (seeds 7000-7023); see `DPLANE_CORRECTION.md` and `_batch_V16b.sh`. v4 verdict unchanged (12/6/1).
Corrected (perturbed, NON-GATING): V18f start vs 0.85 x face 16/22 = 0.727 (WARN), curve sign 21/21; start_err median -1.33, p10 -5.30, p90 +1.75, min -6.94, max +1.87 deg; 22 distinct. Nominal (n = 1): face -0.16, start -1.09, err -0.95 (ok).
