# K19a_s39 300k: independent Evaluator score (dt-fixed J wrapper, v2 bands 08835a4, gate off, golfphys t/c)

**Verdict: WARN 12 P / 5 W / 0 F. NOT a full PASS.**
- Blocking WARNs: sequence_order, sequence_timing (pelvis 152, arm -4), pelvis peak 161 dps, lead GRF 1.81, t/c 1.348.
- Matches the Trainer's committed JSON (stageJ_harness/K19a_s39_300000.json) row-for-row.

- Checkpoint: Trainer `_snap/K19a_s39_300000` (local 1f4aebc), copied to `_evalsnap/K19a_s39_300k/` (gitignored).
  - ckpt_300000.zip md5 bc74adcfcdbec602cbe6772f3299b303 (same as stageK19a_s39/ckpt_300000.zip)
  - vecnorm md5 bc3940ed6d739a9519ccfb61980f4e9f
  - args.json md5 cd1c3ad25da944184eebf2c5c4c93f85
- Run at 2026-10-19 12:14 EDT.
## Provenance
- **Env code:** read-only, from a `git archive 1f4aebc` export of the Trainer clone: `<local-path>`, passed with `--v5-repo`.
  - The live clone has an UNCOMMITTED edit to train/v5_train_j.py: a K20 `tc_w` reward term, default 0, reward only. The export avoids it.
  - Since 4ce9461 there have been no committed changes to train/, env/, golfphys/, scripts/v5_eval_j_worker.py or scripts/v5_realism_j.py. EXTRA=4, so the obs/action layout is unchanged.
  - Nothing was merged into scott-e.
- **Command:** `taskset -c 0-1 python results/overnight/_run_j_gateoff_gp.py <ckpt> --v5-repo <local-path> --json <this>.json`.
  - OMP/MKL 2, 2 workers, arm 0.6, club 1.15.
  - 24 deterministic eps (seeds 4000/8000/9000 x 8), gate off.
- **Concurrency:** a Trainer K20a training job was running with affinity 0-7, which overlaps 0-1. Rollouts are deterministic, so only wall time is affected.
- **Ref keys:** stageK19_ref_s1/tuned_keys_flat.json, md5 e5b896a7c6f2971487fc8a5056704afb (same in the export and the clone).

Label: reference-guided residual with tracking assistance; reference re-tuned open-loop by CMA-ES, stock G1 torque, warm-started.

## Harness output
```

REALISM WARN  K19a_s39_300k/ckpt_300000  [v5 (G1, club_len 1.15, tether 0, strike gate OFF, arm_dist 0.6 [BEnv, as B2-B4/C train])]  episodes 24 (true contact 24)  pass 12 warn 5 fail 0 skip 8 info 1 (not gating)
  WARN  swing/kinematic_sequence_order  - peak order pelvis->thorax->arm->club; not resolvable at dt=20 ms (same sample or reversed by one sample): [('arm', 'club')]
  WARN  swing/kinematic_sequence_timing_ms_before_club_peak  - outside band: {'pelvis': 152, 'arm': -4} (pro means 87/68/65 ms, amateur 78/59/64)
  WARN  swing/peak_speed_pelvis_deg_s  - 0.40 x target at 73 mph (target EXTRAPOLATED beyond measured 88-109 mph)
  PASS  swing/peak_speed_thorax_deg_s
  PASS  swing/peak_speed_arm_deg_s
  PASS  swing/peak_speed_club_deg_s
  PASS  swing/x_factor_top_deg
  SKIP  swing/actuator_torque_speed_limits
  SKIP  swing/pelvis_yaw_avg_torque_Nm
  WARN  swing/grf_lead_vertical_bw  - peak lead-foot vertical force in body weights; min < 0 means the foot pulls on the ground
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
  INFO  mine/total_over_carry_speed_matched (golfphys model, info only, not gating)  - actual total/carry 1.348 vs golfphys speed-matched minimum 1.212 at 106.7 mph ball speed (launch 16 deg, backspin 3000 rpm); golfphys MODEL number, not a measurement and not a reference band: golfphys roll (bounce_roll, normal turf) is validated only on normal turf at tour speeds (roll_aoa_validation total/carry 1.07-1.13; TrackMan rows, tests/test_golfphys_total.py) and is UNCALIBRATED at low (~60 mph club) speed; info only, does not affect the verdict
  -- sample interval: 4.0 ms measured from the logged sim time (worker declared 4.0 ms; 0 episodes disagree); tie tolerance 20 ms and thresholds unchanged
```

## Key numbers (all 24 episodes are identical: deterministic policy, rsi mode 0)
- Club 72.8 mph, ball 106.7 mph, smash 1.466. Launch 12.35 deg, spin 2710 rpm (back 2686 / side -360).
- golfphys carry 139.3 yd, total 187.8 yd, descent 23.1 deg.
- **t/c = 1.3477050230250076 (golfphys).** Env model: 1.3473571816740177.
  - min = max = median over 24 eps (1 unique value).
  - 0.0023 below the 1.35 FAIL line.
- Azimuth 1.80 deg; lateral -8.86 yd = 6.36 yd/100.
- Lead GRF peak 1.81 BW (0.11 above the 1.7 pass bound).

## Sanity checks (probe, seed 4000)
- Contact 24/24, fouls 0. Club 72.8 mph, above the 60 mph WARN line.
- **Lead foot planted.**
  - Lead GRF is zero at only 1 of 75 samples in the 300 ms before contact (isolated, at -172 ms).
  - Min 1.23 BW in the last 50 ms; 1.38 BW at contact.
  - Toe rise at most 0.4 cm; heel up to 1.6 cm (heel-only lift is allowed).
  - Not gated: trail-foot GRF is 0 from -160 ms.
- **Direction is ball-derived:** golfphys ball launch velocity vs the fixed +x line.
- **Strike is square.**
  - Face +2.4 deg, path +0.35 deg, face-to-path +2.0 deg.
  - AoA +1.9 deg, dynamic loft 15.8 deg.
  - Offset +0.13 cm toe, -0.69 cm low. Sidespin -360 rpm.
## Verdict rules (realism/checks.py, data/references/realism_thresholds.json)
- **sequence_order:** FAIL only if a peak is reversed by more than tie_tolerance (20 ms).
  - A pair that is in the same sample, or reversed by up to 20 ms, is WARN ("not resolvable"). Arm 4 ms after club is therefore a WARN.
  - Since the dt fix, 20 ms is 5 samples at 4 ms, not the "one sample" the message text says.
  - Exception: a thorax/arm swap of up to 30 ms is also a WARN.
- **sequence_timing:** this row is WARN-only and can never FAIL. The bands are pelvis 40-140, thorax 25-110, arm 15-110 ms.
- **total_over_carry:** pass 1.04-1.25, warn 0.99-1.35. Above 1.35 is a FAIL, because `_band` requires a value to sit inside the warn band for a WARN (fail_outside 1.45 never applies).
- **lead GRF:** pass 0.8-1.7, warn 0.5-2.4. Above 2.4 is a FAIL.
- **Full PASS** requires n_warn = 0.
