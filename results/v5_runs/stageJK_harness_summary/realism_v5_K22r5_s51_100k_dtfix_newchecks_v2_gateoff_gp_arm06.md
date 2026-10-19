# K22r5_s51 100k: independent Evaluator score (dt-fixed J wrapper, v2 bands 08835a4, gate off, golfphys t/c)

Label: reference-guided residual with tracking assistance; reference re-tuned open-loop by CMA-ES, stock G1 torque, warm-started.

**Verdict: FAIL, 13 P / 3 W / 1 F.**
- The only FAIL is lead GRF, peak 2.59 BW.
- WARNs: sequence_timing (arm 12 ms), pelvis peak 191 dps, spin 3371.
- Matches the Trainer's committed JSON (stageJ_harness/K22r5_s51_100000.json) row for row.

## The GRF FAIL is a single-sample post-impact contact spike
- The harness GRF row takes the max over the **whole logged episode**, including follow-through: `eval/realism_check.py` uses `grf[:n]`, not `[:impact]`.
- The 2.5894 BW peak is at **t - t_contact = +42 ms, after impact**.
  - At 2 ms resolution the lead GRF reads 1.244 at +38 ms, 0.000 at +40 ms, 2.589 at +42 ms and 1.245 at +44 ms.
  - So the foot momentarily loses contact and re-impacts: one 2 ms sample.
- Before impact the peak is 2.3675 BW at -74 ms, also a single-sample spike (0.558 -> 2.368 -> 1.385 at 2 ms). That would be a WARN with only 0.03 BW of margin.
  - Before impact, only 2 samples (8 ms) exceed 1.7 BW at 4 ms; 3 samples (6 ms) at 2 ms.
- The verdict is the harness verdict, unchanged. Whether to gate on post-impact samples and single-sample spikes is a separate question for the Orchestrator and the Data Agent.

## Provenance
- **Checkpoint:** Trainer `_snap/K22r5_s51_100000`, copied to `_evalsnap/K22r5_s51_100k/` (gitignored).
  - ckpt_100000.zip md5 114b88a21aa8375456a4cf00b4fac4da (same as stageK22r5_s51/ckpt_100000.zip)
  - vecnorm md5 e1e30a27cb3a5747d564194f77d26f58
  - args.json md5 c1c8e2d28143f63b0c85b9a1f6a73f87
- **Env code:** read-only `git archive 49de3ef` export at `<local-path>`.
  - The clone had no uncommitted train/env edits. HEAD was 7be0864, which is harness-only after 49de3ef.
  - Changes 63d6e65 -> 49de3ef:
    - env/v5_ref.py: `pc|<kind>|a` blend.
    - train/v5_train_j.py: spin penalty uses spin_hi/spin_scale.
  - Obs/action layout unchanged: EXTRA=4; env and policy are obs (116,) / act (29,).
- **Ref keys: CHANGED family.** stageK22e_ref_s1/tuned_keys_flat.json, md5 68b007811f5a4dd79e8312b812afe713. Same hash in the clone, at 49de3ef, and in the export (committed in fecf374).
  - 115 entries; this replaces K22c.
  - pc curves:
    - hip_yaw: c 0.0827, a 1
    - waist_yaw: c 0.0781, a 1
    - hip_roll: c 0.1029, a 1
    - shoulder (6 joints): c 0.0242, a 0.092 (new)
    - elbow (2 joints): c 0.0223, a 0.106 (new)
  - Read correctly: the ref velocity peaks at c before t_imp for hip_yaw / waist_yaw / hip_roll (0.083 / 0.078 / 0.103 s).
  - Shoulder and elbow are blended at a ~0.1, so their peaks (0.023 / 0.014 s) are mixed with the ease curve, as intended.
- **Command:** `taskset -c 0-1 python results/overnight/_run_j_gateoff_gp.py <ckpt> --v5-repo <export> --json <this>.json`, run 2026-10-19 15:10 EDT.
  - OMP/MKL 2, 2 workers, arm 0.6, club 1.15.
  - 24 deterministic eps (seeds 4000/8000/9000 x 8), gate off.
  - Trainer training jobs were running with affinity 0-7.

## Harness output
```

REALISM FAIL  K22r5_s51_100k/ckpt_100000  [v5 (G1, club_len 1.15, tether 0, strike gate OFF, arm_dist 0.6 [BEnv, as B2-B4/C train])]  episodes 24 (true contact 24)  pass 13 warn 3 fail 1 skip 8 info 1 (not gating)
  PASS  swing/kinematic_sequence_order
  WARN  swing/kinematic_sequence_timing_ms_before_club_peak  - outside band: {'arm': 12} (pro means 87/68/65 ms, amateur 78/59/64)
  WARN  swing/peak_speed_pelvis_deg_s  - 0.47 x target at 71 mph (target EXTRAPOLATED beyond measured 88-109 mph)
  PASS  swing/peak_speed_thorax_deg_s
  PASS  swing/peak_speed_arm_deg_s
  PASS  swing/peak_speed_club_deg_s
  PASS  swing/x_factor_top_deg
  SKIP  swing/actuator_torque_speed_limits
  SKIP  swing/pelvis_yaw_avg_torque_Nm
  FAIL  swing/grf_lead_vertical_bw  - peak lead-foot vertical force in body weights; min < 0 means the foot pulls on the ground
  PASS  shot/smash
  PASS  shot/club_speed_mph
  WARN  shot/spin_rpm  - driver spin gate (published windows, derived thresholds)
  PASS  shot/launch_deg
  SKIP  shot/descent_deg
  PASS  shot/total_over_carry
  PASS  shot/carry_vs_golfphys_yd
  PASS  mine/segments_rotate
  SKIP  mine/ground_contact_weight_shift
  SKIP  mine/joint_limits
  SKIP  mine/torque_saturation_smoothness
  SKIP  mine/tempo
  SKIP  mine/carry_vs_trackman_band
  PASS  mine/start_direction
  PASS  mine/lead_foot_plant
  INFO  mine/total_over_carry_speed_matched (golfphys model, info only, not gating)  - actual total/carry 1.248 vs golfphys speed-matched minimum 1.239 at 101.1 mph ball speed (launch 16 deg, backspin 3000 rpm); golfphys MODEL number, not a measurement and not a reference band: golfphys roll (bounce_roll, normal turf) is validated only on normal turf at tour speeds (roll_aoa_validation total/carry 1.07-1.13; TrackMan rows, tests/test_golfphys_total.py) and is UNCALIBRATED at low (~60 mph club) speed; info only, does not affect the verdict
  -- sample interval: 4.0 ms measured from the logged sim time (worker declared 4.0 ms; 0 episodes disagree); tie tolerance 20 ms and thresholds unchanged
```

## Key numbers (all 24 episodes identical)
- Club 70.6 mph, ball 101.1 mph, smash 1.432. Launch 14.40 deg, spin 3371 rpm (back 3365 / side +214).
- golfphys carry 133.6 yd, total 166.7 yd, descent 27.1 deg.
- **t/c = 1.2475006780898485** (env 1.2470971061519216). PASS, 0.0025 under the 1.25 pass edge.
- X-factor 61.4 (PASS). Azimuth 4.01 deg; lateral 11.56 yd = 8.65 yd/100 (pass <= 13.5).

## Order and timing
- Peaks: pelvis 1.196 s, thorax 1.264 s, arm 1.296 s, club 1.308 s.
- Lead before the club peak: pelvis 112, thorax 44, arm 12 ms.
- **Order PASS:** strictly increasing, and every adjacent gap is at least 0.5 x the 20 ms tie tolerance (10 ms).
  - Gaps: 68 / 32 / 12 ms. The arm-club gap of 12 ms is just over 10 ms.
  - Previously arm-club was -4 to +8 ms (WARN).
- **Timing WARN:** arm 12 ms is below its 15-110 band. Pelvis 112 and thorax 44 are inside their bands.

## Spin_hi wiring (verified)
- Up to and including 63d6e65 (K22r4), the spin penalty was hard-coded at 3000/2000, so spin_hi and spin_scale were unused.
- Fixed in 042205d (2026-10-19 14:39 EDT): it now uses `self.spin_hi` / `self.spin_scale`.
- K22r5 (process start 14:54 EDT) trained after the fix, with spin_hi 2900 / scale 1000.
- Spin 3371 sits above the knee, at a penalty of 12 x 0.471 = 5.65. The policy is not riding a cap here.

## Sanity checks (probe, seed 4000)
- **Contact:** 24/24, 0 fouls. Club 70.6 mph, above 60.
- **Lead foot planted:**
  - Lead GRF is 0 at 1 of 75 samples in the last 300 ms (-146 ms).
  - At least 0.75 BW in the last 50 ms; 1.30 BW at contact.
  - Heel and toe rise at most 0.2 cm.
- **Direction is ball-derived:** golfphys launch velocity vs the fixed +x line.
- **Strike:**
  - Face -3.9, path -2.1, face-to-path -1.8 deg.
  - AoA -0.1, dynamic loft 18.8 deg (high).
  - Offset +0.20 cm toe, -0.74 cm low. Sidespin +214 rpm.
- **Trail foot (not gated):**
  - About 0.45 BW at address and 0.43 at the top.
  - Loaded in 26% of samples from -300 to -130 ms (mean 0.19 BW).
  - Fully unloaded from -146 ms through impact.
