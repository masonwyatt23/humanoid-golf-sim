# V18 official grading (Evaluator, 2026-10-25 ~3:30 PM ET)

This is the OFFICIAL grade. The Trainer's local numbers (patched local worker copy, Trainer b663c9f6) are not official.

**Checkpoint.** V18l_s590 50k: fresh init plus `--stance_obs` (Trainer 92703d2e: 4 extra obs = ball xy minus lead / trail sole xy), V12p recipe, V12X refit keys (`results/v5_runs/stageV12X_ref_s1/tuned_keys_flat.json`). Trainer local v4: 13/5/1, .96/.92/.88.

**Worker change (this commit).** `_j_worker_gp_v3.py` CFG now forwards `stance_obs` from args.json. `JEnv.configure()` skips None, so a snapshot whose args.json lacks the key (every pre-V18l snapshot) is configured exactly as before. Same key added to `render_blender/export_v5j_trajectory.py` (parity test) and to `_precheck_layout.py` (builds the 120-dim env when args.json sets it). Equivalent to the Trainer's local patch (`results/v10_diag/worker_patch/`), reviewed. New test `tests/test_worker_stance_obs.py`.

**Setup.** As V17 (`_batch_V17.sh` -> `_batch_V18.sh`). All runs exited 0.
- Read-only Trainer export b663c9f6 (Trainer box HEAD at grading time; includes 92703d2e). Since 94205e13 the only env-side change is `train/v5_train_j.py` (stance_obs obs block and its configure resize, both inert when the flag is off); env/, golfphys/ and eval/ unchanged.
- args.json: env_v4 true, stance_obs true, keys stageV12X_ref_s1.
- Keys md5 (same keys as V16/V17) and snapshot md5s were verified (export = Trainer HEAD; Evaluator copy = Trainer snapshot, all MATCH) and are not published here.
- Layout pre-check LAYOUT_OK (obs 120 = 116 + 4 stance, model 120, vecnorm 120, act 29, 121 keys).
- Worker: arm 0.6, club 1.15, 24 deterministic episodes, gate off, golfphys, robustness seeds 7000-7023, cores 0-1, 2 workers, BLAS threads 2. Trainer training runs were active; no Trainer grading or eval job was running.

| ckpt | v4 1.5in (gating) | v4 crown16 INFO | v3c 1.5in | v3d 1.5in |
|---|---|---|---|---|
| V18l_s590 50k | 13/5/1 FAIL | 13/5/1 | 12/4/2 | 13/5/1 |

**Only failing row: mine/robustness.** Triple contact 0.958 (23/24), start direction 0.917 (22/24), lead-foot plant 0.875 (21/24) vs 0.95/0.90/0.90: contact and start direction now pass, plant misses by one episode. Shot sub-requirements: club speed p10 60.5 mph = 0.86 x median 70.6 (< 0.93, LOW CONFIDENCE rule); smash p10 1.30 WARN; spin median 2419, p10 1066 / p90 4244 outside WARN; total/carry median 1.398 FAIL, p10 1.314, p90 1.881 FAIL.

**v4 1.5 in WARN rows:** kinematic_sequence_order (pelvis 1.324, thorax 1.288, arm 1.296, club 1.300 s), sequence timing (pelvis -24, thorax 12, arm 4 ms), peak pelvis 242.6 deg/s (< 250), lead-foot vertical GRF 1.755 BW, shot/total_over_carry 1.305.
Nominal: club 70.7 mph, smash 1.43, spin 2793 PASS, launch 13.9, strike dz +0.1 mm, dy +1.9 mm (toe +). Robustness strike: dy median -1.6, p10 -27.5, p90 +11.7 mm; dz median +4.1, p10 -21.3, p90 +14.0 mm (n 23).

**Versus the Trainer's local run:** v4 1.5 in, crown and v3c identical check-for-check. v3d official 13/5/1 vs Trainer 12/5/1: +1 is mine/strike_height (absent from the Trainer's local v3d JSON, as before).

**Regression (patched worker, old 116-obs snapshot).** V18i_s560 150k v4 1.5 in on export b663c9f6: 13/5/1, .917/.875/.833; result JSON identical to the V17 official JSON in every field.

**Versus earlier official grades:** V18i 150k 13/5/1 (.917/.875/.833, club p10 56.3); V18f 50k 12/6/1 (.917/.875/.833); V16y 50k 13/4/2 (.958/.917/.917). V18l ties V16y's contact/start and V18i's count; plant is one episode short, and the spin / t/c tails still fail.

**v5 (NON-GATING estimates):**
- heldout-1: .458/.333/.083 (V18i .458/.333/.083).
- heldout-2 excl. slope (28 eps): .821/.821/.821 (V18i .857/.857/.786).
- Driver per-club: smash, launch, spin pass; land angle FAIL 24.8 deg (warn floor 25). Task rows n/a.
- D-plane (perturbed robustness episodes, 23 distinct): start vs 0.85 x face 15/23 = 0.652 WARN (V18i .636), curve sign 22/22; start_err median -0.63, p10 -5.06, p90 +1.93, min -6.68, max +3.13 deg. Medians (world, + = left): face -1.48, path -2.23, start -2.07. Nominal (n = 1): face -1.72, start -1.46, err +0.01 (ok).

No full pass (robustness fails), so no cinematic render.

## Design note: what the robustness perturbation is meant to be

The spec describes the gate as small posture/state noise at address, applied to actuated joints. It says nothing about the stance or feet, and nothing about re-addressing the ball:
- `eval/robust_grf.py:3`: "A policy is re-run on N seeded episodes with small perturbations at address."
- `eval/robust_grf.py:5`: "initial actuated joint angles: uniform +/-JOINT_DEG (1.5 deg). The env has no joint-noise option; this is our own, inside the requested 1-2 deg."
- `results/overnight/_j_worker_gp_v3.py:16-17`: "perturb the state at address after reset (joint noise from rng(seed + 0x5EED)); ball offset and floor friction via the env's own ball_tol / friction_rand options."
- `results/overnight/_j_worker_gp_v3.py:241`: "perturb the address state (actuated joints only), then refresh derived quantities and the observation"; line 256 adds dq/dv to qpos/qvel and calls mj_forward, with no foot re-grounding and no re-address.

So a ~1 cm lead-foot shift from leg-joint offsets with the feet planted is a side effect of that implementation, not a stated intent: the spec targets posture noise and separately models ball position (+/-1 cm via ball_tol). The gate is left unchanged. Reading it as "the golfer starts with a slightly different stance and must cope" is consistent with the code; "a real golfer would re-address" would be a spec change (e.g. arm/torso-only noise, or a re-settle) and needs an Orchestrator decision.
