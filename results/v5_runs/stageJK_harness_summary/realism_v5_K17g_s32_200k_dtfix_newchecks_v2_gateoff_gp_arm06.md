# K17g_s32 200k: independent Evaluator score (dt-fixed J wrapper, v2 bands 08835a4, gate off, golfphys t/c)

Label: reference-guided residual with tracking assistance; reference re-tuned open-loop by CMA-ES, stock G1 torque, warm-started.

- Checkpoint: Trainer `results/v5_runs/_snap/K17g_s32_200000` (Trainer commit 277c201, local), copied to `results/overnight/_evalsnap/K17g_s32_200k/` (gitignored)
  - ckpt_200000.zip md5 1166b849776ece268e557891fb624c1d (same as stageK17g_s32/ckpt_200000.zip)
  - ckpt_200000_vecnorm.pkl md5 f5ffb5391627db62c0ecb4d22f71aac2; args.json md5 b94b5578f22781c0924dfdf9e70bee0c
  - ref keys stageK17d_ref/tuned_keys_flat.json md5 e8ebb28785d2e797b11b6e68cc0eb931
- Env code: JEnv read-only from the Trainer clone at d10bed8, which has the same train/ env/ as 277c201 (d10bed8 only touches scripts/hz.sh and scripts/v5_ref_fit_k17.py). The obs/action layout is unchanged (EXTRA=4). The K16/K17 additions (aim_w, foot_w, early_w, plant_term) are reward/info only. The eval worker does not set them, so no plant_break termination. Nothing merged into scott-e.
- Command: `taskset -c 0-1 python results/overnight/_run_j_gateoff_gp.py results/overnight/_evalsnap/K17g_s32_200k/ckpt_200000 --json <this>.json`, run 2026-10-19 10:31 EDT
  - Settings: OMP/MKL 2, 2 workers, arm 0.6, club 1.15, 24 deterministic eps (seeds 4000/8000/9000 x 8), gate off, rsi (1,0,0), track_w 0, friction_rand off.
  - Contention: Trainer jobs (K17f/K17g training, the K17h ref fit, K17f harness) were running with affinity 0-7, which overlaps 0-1. The rollouts are deterministic, so this affects wall time only.

## Harness output
```

REALISM FAIL  K17g_s32_200k/ckpt_200000  [v5 (G1, club_len 1.15, tether 0, strike gate OFF, arm_dist 0.6 [BEnv, as B2-B4/C train])]  episodes 24 (true contact 24)  pass 10 warn 4 fail 3 skip 8 info 1 (not gating)
  WARN  swing/kinematic_sequence_order  - peak order pelvis->thorax->arm->club; not resolvable at dt=20 ms (same sample or reversed by one sample): [('arm', 'club')]
  WARN  swing/kinematic_sequence_timing_ms_before_club_peak  - outside band: {'arm': 0} (pro means 87/68/65 ms, amateur 78/59/64)
  WARN  swing/peak_speed_pelvis_deg_s  - 0.33 x target at 78 mph (target EXTRAPOLATED beyond measured 88-109 mph)
  PASS  swing/peak_speed_thorax_deg_s
  PASS  swing/peak_speed_arm_deg_s
  PASS  swing/peak_speed_club_deg_s
  PASS  swing/x_factor_top_deg
  SKIP  swing/actuator_torque_speed_limits
  SKIP  swing/pelvis_yaw_avg_torque_Nm
  FAIL  swing/grf_lead_vertical_bw  - peak lead-foot vertical force in body weights; min < 0 means the foot pulls on the ground
  WARN  shot/smash  - ball speed / club speed; 1.50 is a COR (0.83) and 200 g head ceiling
  PASS  shot/club_speed_mph
  FAIL  shot/spin_rpm  - driver spin gate (published windows, derived thresholds)
  PASS  shot/launch_deg
  SKIP  shot/descent_deg
  FAIL  shot/total_over_carry  - total/carry (normal turf 1.07-1.13, firm to ~1.2; env without roll gives 1.0)
  PASS  shot/carry_vs_golfphys_yd
  PASS  mine/segments_rotate
  SKIP  mine/ground_contact_weight_shift
  SKIP  mine/joint_limits
  SKIP  mine/torque_saturation_smoothness
  SKIP  mine/tempo
  SKIP  mine/carry_vs_trackman_band
  PASS  mine/start_direction
  PASS  mine/lead_foot_plant
  INFO  mine/total_over_carry_speed_matched (golfphys model, info only, not gating)  - actual total/carry 1.548 vs golfphys speed-matched minimum 1.421 at 74.3 mph ball speed (launch 16 deg, backspin 3000 rpm); golfphys MODEL number, not a measurement and not a reference band: golfphys roll (bounce_roll, normal turf) is validated only on normal turf at tour speeds (roll_aoa_validation total/carry 1.07-1.13; TrackMan rows, tests/test_golfphys_total.py) and is UNCALIBRATED at low (~60 mph club) speed; info only, does not affect the verdict
  -- sample interval: 4.0 ms measured from the logged sim time (worker declared 4.0 ms; 0 episodes disagree); tie tolerance 20 ms and thresholds unchanged
```

## Key numbers (median of 24; all 24 episodes are identical: deterministic policy, rsi mode 0)
- Club speed 78.4 mph; ball speed 74.3 mph; **smash 0.947** (WARN)
- Launch 12.94 deg; spin 6270 rpm (back 5051 / side 3715)
- golfphys carry 57.8 yd, total 89.5 yd, t/c 1.548. Env carry 58.0 yd, total 89.5 yd.
- Azimuth 0.89 deg; lateral 3.47 yd at a 57.8 yd carry = 6.00 yd/100. Lead GRF peak 2.45 BW.

## Sanity checks (Evaluator probe, seed 4000)
- Contact is 24/24, with 0 fouls. Club speed is 78.4 mph, above the 60 mph warn line.
- The lead foot is genuinely planted.
  - Over the 300 ms before contact, lead GRF is 0 at only 2 of 75 samples (isolated 4 ms contact chatter at -176 and -84 ms; longest run is 1 sample).
  - Lead GRF is 1.17 BW at the contact sample. The heel stays down (z within 2 mm of address) and the toe rises about 2 cm near impact, which is allowed.
  - Not gated: the trail-foot GRF is 0 from about 140 ms before contact, so all weight is on the lead foot.
- Azimuth comes from the ball.
  - It is golfphys `env_contact_to_shot`: the ball launch velocity's horizontal angle in the world frame, measured against a fixed +x target line. Lateral comes from the golfphys flight.
  - Neither is a learned target. The aim reward (aim_w) uses the same ball azimuth.
- Artifact concern: the delivery is a glancing blow. It is not a driver strike.
  - Face -3.5 deg vs path +22.9 deg (|face-to-path| about 26 deg), attack angle -19.4 deg, dynamic loft 19.6 deg.
  - Strike offset is +1.1 cm toe and +1.5 cm high.
  - This produces smash 0.95, 3715 rpm sidespin and a 58 yd carry. Start direction passes because the ball starts along the face. Lateral/100 looks small partly because the carry is short.
