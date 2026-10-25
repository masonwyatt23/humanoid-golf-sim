# V13 official grading (Evaluator, 2026-10-25 ~4:35 AM ET)

This is the OFFICIAL grade. The Trainer's local numbers are not official.

**Checkpoint.** V13h_s240 50k (Trainer's new local best; Trainer harness JSONs in a0986ad, local worker @915348c). Reference-guided residual policy with tracking assistance, NEW V12T reference keys (refit with noisy-start contact/plant/start-direction plus turn terms) and a turn margin (turn_m_w 3, turn_tgt 6.5). V13h 100k was not graded (Trainer reports a club p10 fail).

**Setup.** Same procedure as V12 (`_batch_V12.sh` -> `_batch_V13.sh`). Harness v4 on the env_v4 head (V3_HEAD=v4). Gating row = 1.5 in tee; crown 1.6 in row is INFO only; v3c and v3d at 1.5 in for continuity. Every run exited 0 (v4 address cross-check passed).
- Read-only Trainer export 5b8dbd4 (Trainer box HEAD at grading time; contains a0986ad).
- args.json: env_v4 true, tee_mode 1.5in, keys `results/v5_runs/stageV12T_ref_s1/tuned_keys_flat.json`.
- Keys md5 02bdf7cf8781f919e1924910799a1aab, identical in the export and the Trainer HEAD.
- Layout pre-check: LAYOUT_OK (obs 116, act 29, 121 keys).
- Snapshot md5s: all MATCH (Evaluator-verified; the md5 list `_evalsnap_md5_V13.txt` is not published here under repo hygiene rules).
- Worker: arm 0.6, club 1.15, 24 deterministic episodes, gate off, golfphys, robustness seeds 7000-7023, cores 0-1, 2 workers, BLAS threads 2.

| ckpt | v4 1.5in (gating) | v4 crown16 INFO | v3c 1.5in | v3d 1.5in |
|---|---|---|---|---|
| V13h_s240 50k | 13/5/1 FAIL | 13/4/2 | 11/5/2 | 13/5/1 |

**v4 1.5 in main row: 13/5/1 FAIL (robustness only).**
- WARN: kinematic_sequence_order (thorax/arm), kinematic_sequence_timing (pelvis -28, thorax 12, arm 4 ms), peak_speed_pelvis 243.7 deg/s (< 250), grf_lead_vertical_bw, total_over_carry 1.348.
- FAIL: mine/robustness: contact 0.92 (22/24), start direction 0.75, lead-foot plant 0.875 (gate 0.95/0.90/0.90); spin p10/p90 (1186/4165) and total/carry median/p90 (1.44/1.87) outside WARN; smash p10 leaves PASS.
- Nominal: club 70.0 mph, spin 3054, launch 12.8, strike dz -4.4 / dy +10.9 mm, lead-foot slip 1.4 cm, turn 7.5 deg.
- Crown INFO adds a total_over_carry FAIL. v3c adds the strict order FAIL and a spin WARN. Crown-only is not a pass in any case.

**Versus V10l_s104 100k (V12 official):** same tally 13/5/1; robustness .92/.75/.88 vs .83/.75/.67 (contact and plant better, start direction unchanged); pelvis 243.7 vs 256.2 deg/s (now a WARN).

**Versus the Trainer's local run:** v4 1.5 in matches check-for-check (47/47 identical); v3c identical. v3d official 13/5/1 vs Trainer 12/5/1: the +1 is mine/strike_height, which the Trainer's local v3d JSON lacks (same as V12).

**v5 held-out DR (NON-GATING estimates, `--harness v5 --heldout-dr 24 --heldout2-dr 32`, same 1.5 in row; v4 part reproduced 13/5/1):**
- heldout-1 (seeds 910000-910023): contact .46, start .33, plant .12 (V10l 100k: .50/.29/.08).
- heldout-2 excluding slope (28 eps): .75/.68/.75. Contact by dim: torque, latency, loft, foot 4/4; head mass 3/4; trunk 2/4; thigh+calf 0/4. Slope 0/4 (info-only, modelling gap).
- Task-accuracy rows n/a (not goal-conditioned). Driver per-club: smash/launch/spin pass, land angle 22.7 deg FAIL (non-gating). D-plane PASS. [NOMINAL-ONLY, n=1: graded on identical deterministic rollouts; see results/overnight/DPLANE_CORRECTION.md; V13h not re-run]

No full pass, so no cinematic render.
