# K18e_s37 200k: independent Evaluator score (dt-fixed J wrapper, v2 bands 08835a4, gate off, golfphys t/c)

Label: reference-guided residual with tracking assistance. The reference was re-tuned open-loop by CMA-ES, with stock G1 torque, warm-started.

**Verdict: WARN, 11 P / 6 W / 0 F. This is NOT a full PASS: all 6 WARNs block it, because `summarize` gives PASS only when n_warn = 0.**

## Provenance
- **Checkpoint:** Trainer `results/v5_runs/_snap/K18e_s37_200000` (Trainer commit 4ce9461, local), copied to `results/overnight/_evalsnap/K18e_s37_200k/` (gitignored).
  - ckpt_200000.zip md5 69cceda8a452297765fd51e3b8543f65 (same as stageK18e_s37/ckpt_200000.zip)
  - ckpt_200000_vecnorm.pkl md5 ce08aa4f45663c67ac5ecd0f11ae85ea
  - args.json md5 0ca27bd106a6759405739fa119b253c2
  - ref keys stageK18s_ref/tuned_keys_flat.json md5 ddb19dfdf7c45462a13aac0e2fa5a337
- **Env code:** JEnv, used read-only from the Trainer clone.
  - The clone HEAD moved 072f28f -> fcf2a78 during the run, but both commits only add harness JSONs. train/ and env/ are identical to 4ce9461, with no uncommitted changes.
  - The changes since 277c201 (6c2f364 K18 strike terms strike_w / smash2_w / ctr2_w) only affect reward and info.
  - The obs/action layout is unchanged: EXTRA = 4, and `_xobs` and action scaling are unchanged.
  - Nothing was merged into scott-e.
- **Command:** `taskset -c 0-1 python results/overnight/_run_j_gateoff_gp.py results/overnight/_evalsnap/K18e_s37_200k/ckpt_200000 --json <this>.json`, run 2026-10-19 11:28 EDT.
  - OMP/MKL 2, 2 workers, arm 0.6, club 1.15.
  - 24 deterministic episodes (seeds 4000/8000/9000 x 8), gate off.
- **Contention:** Trainer K18e/K18f training and a harness run were active with affinity 0-7, which overlaps 0-1. Rollouts are deterministic, so only wall time is affected.

## Harness output
```

REALISM WARN  K18e_s37_200k/ckpt_200000  [v5 (G1, club_len 1.15, tether 0, strike gate OFF, arm_dist 0.6 [BEnv, as B2-B4/C train])]  episodes 24 (true contact 24)  pass 11 warn 6 fail 0 skip 8 info 1 (not gating)
  WARN  swing/kinematic_sequence_order  - peak order pelvis->thorax->arm->club; not resolvable at dt=20 ms (same sample or reversed by one sample): [('arm', 'club')]
  WARN  swing/kinematic_sequence_timing_ms_before_club_peak  - outside band: {'arm': 4} (pro means 87/68/65 ms, amateur 78/59/64)
  WARN  swing/peak_speed_pelvis_deg_s  - 0.38 x target at 74 mph (target EXTRAPOLATED beyond measured 88-109 mph)
  PASS  swing/peak_speed_thorax_deg_s
  PASS  swing/peak_speed_arm_deg_s
  PASS  swing/peak_speed_club_deg_s
  PASS  swing/x_factor_top_deg
  SKIP  swing/actuator_torque_speed_limits
  SKIP  swing/pelvis_yaw_avg_torque_Nm
  WARN  swing/grf_lead_vertical_bw  - peak lead-foot vertical force in body weights; min < 0 means the foot pulls on the ground
  PASS  shot/smash
  PASS  shot/club_speed_mph
  WARN  shot/spin_rpm  - driver spin gate (published windows, derived thresholds)
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
  INFO  mine/total_over_carry_speed_matched (golfphys model, info only, not gating)  - actual total/carry 1.317 vs golfphys speed-matched minimum 1.220 at 105.0 mph ball speed (launch 16 deg, backspin 3000 rpm); golfphys MODEL number, not a measurement and not a reference band: golfphys roll (bounce_roll, normal turf) is validated only on normal turf at tour speeds (roll_aoa_validation total/carry 1.07-1.13; TrackMan rows, tests/test_golfphys_total.py) and is UNCALIBRATED at low (~60 mph club) speed; info only, does not affect the verdict
  -- sample interval: 4.0 ms measured from the logged sim time (worker declared 4.0 ms; 0 episodes disagree); tie tolerance 20 ms and thresholds unchanged
```

## Key numbers (median of 24; all 24 episodes are identical: deterministic policy, rsi mode 0)
- **Speed:** club 74.1 mph, ball 105.0 mph, smash 1.418.
- **Launch and spin:** launch 11.87 deg; spin 3227 rpm (back 3227 / side 33).
- **Distance:** golfphys carry 134.9 yd, total 177.6 yd, t/c 1.317. The env gives carry 135.0 and total 177.7.
- **Direction:** azimuth 2.04 deg (start right), lateral 4.41 yd = 3.29 yd/100.
- **Lead GRF:** peak 2.29 BW.

## Band margins (realism/checks.py `_band` + data/references/realism_thresholds.json)
`_band`: PASS inside `pass`. WARN only if inside `warn` AND inside `fail_outside`. Anything else is FAIL.

| Row | Value | PASS band | WARN band | Effective FAIL | Margin to FAIL |
|---|---|---|---|---|---|
| Lead GRF | 2.29 BW | 0.8-1.7 | 0.5-2.4 | > 2.4 or min < -0.02 (the 3.0 fail_outside bound is never reached) | 0.11 BW |
| Spin | 3227 rpm | 1800-3000 | 1200-4000 | outside warn | 773 rpm |
| t/c | 1.317 | 1.04-1.25 | 0.99-1.35 | > 1.35 | 0.033 |

## Sanity checks (Evaluator probe, seed 4000)
- **Contact and speed:** contact 24/24, 0 fouls. Club speed 74.1 mph, above the 60 mph WARN line.
- **Lead foot is planted:**
  - Lead GRF is never zero in the 300 ms before contact (0/75 samples).
  - Lead GRF is at least 0.94 BW in the last 50 ms and 1.06 BW at contact.
  - The toe stays down (at most +0.4 cm above address). The heel rose up to 3.3 cm between top and impact; heel-only lift is allowed.
  - Not gated: trail-foot GRF is 0 from 146 ms before contact.
- **Direction is ball-derived:** golfphys `env_contact_to_shot` ball launch velocity against the fixed +x target line; lateral from the golfphys flight.
- **Strike geometry:**

| Quantity | Value |
|---|---|
| Face | +3.6 deg |
| Path | +5.8 deg |
| Face-to-path | -2.2 deg |
| Attack angle | -2.2 deg |
| Dynamic loft | 15.8 deg |
| Contact offset | +1.03 cm toe, -0.53 cm (low) |
| Sidespin | 33 rpm |

  - The strike is square and non-glancing. The K17g glancing-blow artifact is gone.
