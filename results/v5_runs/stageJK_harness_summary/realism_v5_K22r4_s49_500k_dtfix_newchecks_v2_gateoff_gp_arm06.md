# K22r4_s49 500k: independent Evaluator score (dt-fixed J wrapper, v2 bands 08835a4, gate off, golfphys t/c)

Label: reference-guided residual with tracking assistance. Reference re-tuned open-loop by CMA-ES, stock G1 torque, warm-started.

The K22 reference adds explicit bell-velocity curves for pelvis yaw, thorax (waist) yaw and hip roll (weight shift).

**Verdict: WARN, 12 P / 5 W / 0 F. Not a full PASS.**
- Blocking WARNs: sequence_order, sequence_timing (arm 8 ms), pelvis peak 229 dps (0.57x), X-factor 66.6, t/c 1.289.
- Lead GRF PASSES (1.54 BW).
- Matches the Trainer's committed JSON (stageJ_harness/K22r4_s49_500000.json) row for row.

## Provenance
- **Checkpoint:** Trainer `_snap/K22r4_s49_500000` (commit 63d6e65), copied to `_evalsnap/K22r4_s49_500k/` (gitignored).
  - ckpt_500000.zip md5 3d76b63935f70c87791445a84385e053 (= stageK22r4_s49/ckpt_500000.zip)
  - vecnorm md5 0e3abf4282628ace719a914b190b755c
  - args.json md5 fa5c5dfe222940e341f626f1f8ac8251
- **Env code:** read-only `git archive 63d6e65` export at `<local-path>`, passed via `--v5-repo`.
  - The clone has uncommitted edits to env/v5_ref.py (a `pc|<kind>|a` blend, default 1.0) and scripts/v5_ref_fit_k22.py.
  - The K22c keys contain no `a` entries, so committed and uncommitted SwingRef give the same reference.
  - Committed changes since 1f4aebc:
    - env/v5_ref.py: K22 `pc` curves.
    - train/v5_train_j.py: `tc_w` reward only.
    - worker: passes `tc_w`.
  - **Obs/action layout unchanged:** EXTRA = 4. The K22r4 policy is obs (116,) / act (29,), the same as K19a.
- **Ref keys:** stageK22c_ref_s1/tuned_keys_flat.json, md5 e173eb3e151140bfae52c66e7e125528. The same hash in the clone, at 63d6e65, and in the export.
  - 109 entries: 90 keyframe, 8 ease, 5 phase, 6 pc.
  - Verified in JEnv / SwingRef:
    - pc_grp = hip_yaw (c 0.0891, w 0.0430), waist_yaw (c 0.0782, w 0.0521), hip_roll (c 0.1038, w 0.0562).
    - Joints mapped: L/R hip_yaw, waist_yaw, L/R hip_roll.
    - The ref velocity peaks at exactly c before t_imp (0.089 / 0.078 / 0.104 s).
- **Command:** `taskset -c 0-1 python results/overnight/_run_j_gateoff_gp.py <ckpt> --v5-repo <export> --json <this>.json`, 2026-10-19 14:37 EDT.
  - OMP/MKL 2, 2 workers, arm 0.6, club 1.15.
  - 24 deterministic eps (seeds 4000/8000/9000 x 8), gate off.

## Harness output
```

REALISM WARN  K22r4_s49_500k/ckpt_500000  [v5 (G1, club_len 1.15, tether 0, strike gate OFF, arm_dist 0.6 [BEnv, as B2-B4/C train])]  episodes 24 (true contact 24)  pass 12 warn 5 fail 0 skip 8 info 1 (not gating)
  WARN  swing/kinematic_sequence_order  - peak order pelvis->thorax->arm->club; not resolvable at dt=20 ms (same sample or reversed by one sample): [('arm', 'club')]
  WARN  swing/kinematic_sequence_timing_ms_before_club_peak  - outside band: {'arm': 8} (pro means 87/68/65 ms, amateur 78/59/64)
  WARN  swing/peak_speed_pelvis_deg_s  - 0.57 x target at 71 mph (target EXTRAPOLATED beyond measured 88-109 mph)
  PASS  swing/peak_speed_thorax_deg_s
  PASS  swing/peak_speed_arm_deg_s
  PASS  swing/peak_speed_club_deg_s
  WARN  swing/x_factor_top_deg  - max |thorax - pelvis| before impact (published 24-59 deg, method dependent); stretch not checked
  SKIP  swing/actuator_torque_speed_limits
  SKIP  swing/pelvis_yaw_avg_torque_Nm
  PASS  swing/grf_lead_vertical_bw
  PASS  shot/smash
  PASS  shot/club_speed_mph
  PASS  shot/spin_rpm
  PASS  shot/launch_deg
  SKIP  shot/descent_deg
  WARN  shot/total_over_carry  - total/carry (normal turf 1.07-1.13, firm to ~1.2; env without roll gives 1.0)
  PASS  shot/carry_vs_golfphys_yd
  PASS  mine/segments_rotate
  SKIP  mine/ground_contact_weight_shift
  SKIP  mine/joint_limits
  SKIP  mine/torque_saturation_smoothness
  SKIP  mine/tempo
  SKIP  mine/carry_vs_trackman_band
  PASS  mine/start_direction
  PASS  mine/lead_foot_plant
  INFO  mine/total_over_carry_speed_matched (golfphys model, info only, not gating)  - actual total/carry 1.289 vs golfphys speed-matched minimum 1.226 at 103.7 mph ball speed (launch 16 deg, backspin 3000 rpm); golfphys MODEL number, not a measurement and not a reference band: golfphys roll (bounce_roll, normal turf) is validated only on normal turf at tour speeds (roll_aoa_validation total/carry 1.07-1.13; TrackMan rows, tests/test_golfphys_total.py) and is UNCALIBRATED at low (~60 mph club) speed; info only, does not affect the verdict
  -- sample interval: 4.0 ms measured from the logged sim time (worker declared 4.0 ms; 0 episodes disagree); tie tolerance 20 ms and thresholds unchanged
```

## Key numbers (all 24 episodes identical)
- Club 71.5 mph, ball 103.7 mph, smash 1.452.
- Launch 13.53 deg, spin 2907 rpm (back 2907 / side -29).
- golfphys carry 137.3 yd, total 177.0 yd, descent 25.1 deg.
- **t/c = 1.2894205792995732** (env 1.288956198802527), 1 unique value. FAIL above 1.35, so the margin is 0.061.
- **Lead GRF peak = 1.5361186703837884 BW** (PASS, 0.8-1.7). Margin 0.164 BW to the pass edge, 0.864 BW to FAIL (2.4).
- **X-factor = 66.62216197409994 deg.** Bands: pass 40-65, warn 28-80, FAIL above 80, so the margin is 13.4 deg.
  - The maximum occurs at t = 1.136 s, during the downswing (stretch). At the top (t = 1.0 s) it is 65.2.
- Azimuth 2.84 deg; lateral 6.45 yd = 4.70 yd/100.
- Pelvis peaks 104 ms before the club (band 40-140); pelvis peak 229.1 dps = 0.57 x target.

## Sanity checks (probe, seed 4000)
- **Contact:** 24/24, 0 fouls. Club 71.5 mph, above the 60 mph WARN line.
- **Lead foot planted:** lead GRF is 0 at 2 of 75 samples in the last 300 ms (isolated, at -138 and -126 ms). It stays at least 0.92 BW in the last 50 ms and is 1.37 BW at contact. Heel and toe each rise at most 0.4 cm.
- **Trail foot (not gated):** about 0.45 BW at address and 0.53 at the top.
  - From -300 to -130 ms it is loaded in 30% of samples (mean 0.14 BW).
  - It is fully unloaded from -130 ms through impact.
- **Direction is ball-derived:** golfphys ball launch velocity against the fixed +x line.
- **Strike:** square.
  - Face -2.9, path -3.3, face-to-path +0.3 deg.
  - AoA +0.7, dynamic loft 17.2.
  - Offset -0.07 cm (heel), -0.55 cm (low). Sidespin -29 rpm.
- **Spin vs reward:** 2907 rpm.
  - It is above the Trainer's `spin_hi` 2700, but in JEnv `spin_hi` is not used by the K18 spin penalty (`spin_w * clip((spin - 3000) / 2000)`).
  - So 2907 sits 93 rpm under the 3000 rpm penalty knee and the harness pass edge.
