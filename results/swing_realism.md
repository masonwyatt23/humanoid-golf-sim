# Swing realism: does the rolled-out swing look and behave like a real golf swing?

**Protocol:** deterministic rollouts, gate seeds [4000, 8000, 9000] x 8 episodes (seed+i), gate env kwargs; per-check status = most common over true-contact episodes; medians for values. bands marked DERIVED are built from published mean+-SD, not published thresholds; Data Agent checks use data/references/realism_thresholds.json (tags there).

Swing checks (`swing/*`) and shot checks (`shot/*`) are the Data Agent's `realism.checks.check_swing_realism` / `check_shot_realism` (file untouched); `mine/*` are this harness's extra structural checks (`eval/swing_realism.py`). Status per check: pass / warn / fail / skip (skip = input absent, e.g. spin). **Verdict = FAIL if any check fails, WARN if any warns (no fail), PASS only if none warn or fail.** Only PASS is eligible for showcase/qualifying. Extrapolated reference rows can only WARN. No human-attainable-power claim is made; force_scale 2 and the power tier are hypothetical.

| model | tier | verdict | pass | warn | fail | skip |
|---|---|---|---|---|---|---|
| imit20_fs1_q23_dart_s51 | stock (force_scale 1) | **FAIL** | 2 | 5 | 11 | 5 |
| imit16_fs1_dart_s51 | stock (force_scale 1) | **FAIL** | 3 | 5 | 10 | 5 |
| imit18_power_dart_s51 | hypothetical power tier (impact gain 1.28 inflated) | **FAIL** | 4 | 6 | 8 | 5 |
| imit18_power_dart_s51@gain1.2 | hypothetical power tier (impact gain 1.2, no spin model) | **FAIL** | 5 | 6 | 7 | 5 |
| scripted_v3 | force_scale 2 (hypothetical-strength actuators) | **FAIL** | 3 | 8 | 7 | 5 |
| scripted_v3_fs1_q23_dz016 | stock (force_scale 1) | **FAIL** | 2 | 5 | 11 | 5 |
| ppo_v4yaw_s43 | force_scale 2 + impact gain (HYPOTHETICAL) | **FAIL** | 3 | 7 | 9 | 5 |
| ppo15_klres_s101 | force_scale 2 (hypothetical-strength) | **FAIL** | 3 | 8 | 7 | 5 |
| ppo20_klres_s111 | stock (force_scale 1) | **FAIL** | 2 | 5 | 11 | 5 |
| ppo_resid_v3_s0 | older residual PPO (see its results JSON) | **FAIL** | 2 | 4 | 13 | 5 |

## Per-check status

| check | imit20_fs1_q23_dart_s51 | imit16_fs1_dart_s51 | imit18_power_dart_s51 | imit18_power_dart_s51@gain1.2 | scripted_v3 | scripted_v3_fs1_q23_dz016 | ppo_v4yaw_s43 | ppo15_klres_s101 | ppo20_klres_s111 | ppo_resid_v3_s0 |
|---|---|---|---|---|---|---|---|---|---|---|
| swing/kinematic_sequence_order | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN |
| swing/kinematic_sequence_timing_ms_before_club_peak | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN |
| swing/peak_speed_pelvis_deg_s | FAIL | FAIL | WARN | WARN | WARN | FAIL | WARN | WARN | FAIL | FAIL |
| swing/peak_speed_thorax_deg_s | FAIL | FAIL | WARN | WARN | WARN | FAIL | WARN | WARN | FAIL | FAIL |
| swing/peak_speed_arm_deg_s | FAIL | FAIL | WARN | WARN | WARN | FAIL | WARN | WARN | FAIL | FAIL |
| swing/peak_speed_club_deg_s | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | FAIL |
| swing/x_factor_top_deg | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| swing/actuator_torque_speed_limits | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP |
| swing/pelvis_yaw_avg_torque_Nm | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP |
| swing/grf_lead_vertical_bw | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| shot/smash | WARN | WARN | FAIL | PASS | WARN | WARN | FAIL | WARN | WARN | WARN |
| shot/club_speed_mph | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| shot/spin_rpm | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP |
| shot/launch_deg | WARN | PASS | PASS | PASS | PASS | WARN | PASS | PASS | WARN | FAIL |
| shot/descent_deg | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP |
| shot/total_over_carry | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN |
| shot/carry_vs_golfphys_yd | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP |
| mine/segments_rotate | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| mine/ground_contact_weight_shift | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| mine/joint_limits | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| mine/torque_saturation_smoothness | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | PASS |
| mine/tempo | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| mine/carry_vs_trackman_band | FAIL | WARN | PASS | PASS | WARN | FAIL | WARN | WARN | FAIL | FAIL |

## Why each model is not PASS

### imit20_fs1_q23_dart_s51 (script-distilled policy; stock (force_scale 1); 24 episodes)

- **WARN swing/kinematic_sequence_order**: peak order pelvis->thorax->arm->club; not resolvable at dt=20 ms (same sample or reversed by one sample): [('thorax', 'arm'), ('arm', 'club')]
- **WARN swing/kinematic_sequence_timing_ms_before_club_peak**: outside band: {'thorax': -60} (pro means 87/68/65 ms, amateur 78/59/64)
- **FAIL swing/peak_speed_pelvis_deg_s**: 0.00 x target at 101 mph (between measured groups) [value 0.0]
- **FAIL swing/peak_speed_thorax_deg_s**: 0.00 x target at 101 mph (between measured groups) [value 0.2]
- **FAIL swing/peak_speed_arm_deg_s**: 0.13 x target at 101 mph (between measured groups) [value 1905.85]
- **FAIL swing/x_factor_top_deg**: max |thorax - pelvis| before impact (published 24-59 deg, method dependent); stretch not checked [value 0.0]
- **FAIL swing/grf_lead_vertical_bw**: peak lead-foot vertical force in body weights; min < 0 means the foot pulls on the ground
- **WARN shot/smash**: ball speed / club speed; 1.50 is a COR (0.83) and 200 g head ceiling [value 1.016]
- **WARN shot/launch_deg**: driver launch window (TrackMan 7.8-9.3 at AoA 0, Foresight 10-14) [value 17.805]
- **WARN shot/total_over_carry**: total/carry (normal turf 1.07-1.13, firm to ~1.2; env without roll gives 1.0) [value 0.997]
- **FAIL mine/segments_rotate**: pelvis does not rotate (peak 0.0 deg/s < 20, DERIVED) - the env pins the torso/pelvis (pin_torso=True); thorax does not rotate (peak 0.3 deg/s < 20, DERIVED)
- **FAIL mine/ground_contact_weight_shift**: feet do not collide with the ground in this model (0 of 2 foot geoms): ground reaction = 0 by construction
- **FAIL mine/joint_limits**: right_knee within 5% of a limit 100% of the swing (> 10%, DERIVED)
- **FAIL mine/torque_saturation_smoothness**: right_shoulder_pitch at its actuator cap 70% of the downswing (> 5%, DERIVED)
- **FAIL mine/tempo**: backswing:downswing 5.05:1 outside 2.5-4.0 (DERIVED around the published 3:1; TPI 3.2:1); downswing 145 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **FAIL mine/carry_vs_trackman_band**: carry 155 yd outside the TrackMan AoA -5..+5 optimizer band 225-250 yd at 101 mph

Key numbers: downswing 145 ms, backswing:downswing 5.05:1

### imit16_fs1_dart_s51 (script-distilled policy; stock (force_scale 1); 24 episodes)

- **WARN swing/kinematic_sequence_order**: peak order pelvis->thorax->arm->club; not resolvable at dt=20 ms (same sample or reversed by one sample): [('thorax', 'arm'), ('arm', 'club')]
- **WARN swing/kinematic_sequence_timing_ms_before_club_peak**: outside band: {'pelvis': 495, 'thorax': -5, 'arm': 0} (pro means 87/68/65 ms, amateur 78/59/64)
- **FAIL swing/peak_speed_pelvis_deg_s**: 0.00 x target at 99 mph (between measured groups) [value 0.0]
- **FAIL swing/peak_speed_thorax_deg_s**: 0.00 x target at 99 mph (between measured groups) [value 0.15000000000000002]
- **FAIL swing/peak_speed_arm_deg_s**: 2.15 x target at 99 mph (between measured groups) [value 1869.1]
- **FAIL swing/x_factor_top_deg**: max |thorax - pelvis| before impact (published 24-59 deg, method dependent); stretch not checked [value 0.0]
- **FAIL swing/grf_lead_vertical_bw**: peak lead-foot vertical force in body weights; min < 0 means the foot pulls on the ground
- **WARN shot/smash**: ball speed / club speed; 1.50 is a COR (0.83) and 200 g head ceiling [value 1.003]
- **WARN shot/total_over_carry**: total/carry (normal turf 1.07-1.13, firm to ~1.2; env without roll gives 1.0) [value 0.995]
- **FAIL mine/segments_rotate**: pelvis does not rotate (peak 0.0 deg/s < 20, DERIVED) - the env pins the torso/pelvis (pin_torso=True); thorax does not rotate (peak 0.3 deg/s < 20, DERIVED)
- **FAIL mine/ground_contact_weight_shift**: feet do not collide with the ground in this model (0 of 2 foot geoms): ground reaction = 0 by construction
- **FAIL mine/joint_limits**: right_knee within 5% of a limit 100% of the swing (> 10%, DERIVED)
- **FAIL mine/torque_saturation_smoothness**: right_shoulder_pitch at its actuator cap 69% of the downswing (> 5%, DERIVED)
- **FAIL mine/tempo**: backswing:downswing 5.21:1 outside 2.5-4.0 (DERIVED around the published 3:1; TPI 3.2:1); downswing 140 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **WARN mine/carry_vs_trackman_band**: carry 80 yd outside the TrackMan AoA -5..+5 optimizer band 218-242 yd at 99 mph (band extrapolated outside 100-120 mph, DERIVED: WARN only)

Key numbers: downswing 140 ms, backswing:downswing 5.21:1

### imit18_power_dart_s51 (script-distilled policy; hypothetical power tier (impact gain 1.28 inflated); 24 episodes)

- **WARN swing/kinematic_sequence_order**: peak order pelvis->thorax->arm->club; not resolvable at dt=20 ms (same sample or reversed by one sample): [('thorax', 'arm'), ('arm', 'club')]
- **WARN swing/kinematic_sequence_timing_ms_before_club_peak**: outside band: {'pelvis': 490, 'thorax': -10, 'arm': 0} (pro means 87/68/65 ms, amateur 78/59/64)
- **WARN swing/peak_speed_pelvis_deg_s**: 0.00 x target at 132 mph (target EXTRAPOLATED beyond measured 88-109 mph) [value 0.0]
- **WARN swing/peak_speed_thorax_deg_s**: 0.00 x target at 132 mph (target EXTRAPOLATED beyond measured 88-109 mph) [value 0.4]
- **WARN swing/peak_speed_arm_deg_s**: 2.04 x target at 132 mph (target EXTRAPOLATED beyond measured 88-109 mph) [value 2501.4]
- **FAIL swing/x_factor_top_deg**: max |thorax - pelvis| before impact (published 24-59 deg, method dependent); stretch not checked [value 0.0]
- **FAIL swing/grf_lead_vertical_bw**: peak lead-foot vertical force in body weights; min < 0 means the foot pulls on the ground
- **FAIL shot/smash**: ball speed / club speed; 1.50 is a COR (0.83) and 200 g head ceiling [value 1.564]
- **WARN shot/total_over_carry**: total/carry (normal turf 1.07-1.13, firm to ~1.2; env without roll gives 1.0) [value 0.999]
- **FAIL mine/segments_rotate**: pelvis does not rotate (peak 0.0 deg/s < 20, DERIVED) - the env pins the torso/pelvis (pin_torso=True); thorax does not rotate (peak 0.6 deg/s < 20, DERIVED)
- **FAIL mine/ground_contact_weight_shift**: feet do not collide with the ground in this model (0 of 2 foot geoms): ground reaction = 0 by construction
- **FAIL mine/joint_limits**: right_knee within 5% of a limit 100% of the swing (> 10%, DERIVED)
- **FAIL mine/torque_saturation_smoothness**: right_shoulder_pitch at its actuator cap 45% of the downswing (> 5%, DERIVED)
- **FAIL mine/tempo**: backswing:downswing 6.90:1 outside 2.5-4.0 (DERIVED around the published 3:1; TPI 3.2:1); downswing 105 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)

Key numbers: downswing 105 ms, backswing:downswing 6.90:1

### imit18_power_dart_s51@gain1.2 (script-distilled policy; hypothetical power tier (impact gain 1.2, no spin model); 24 episodes)

- **WARN swing/kinematic_sequence_order**: peak order pelvis->thorax->arm->club; not resolvable at dt=20 ms (same sample or reversed by one sample): [('thorax', 'arm'), ('arm', 'club')]
- **WARN swing/kinematic_sequence_timing_ms_before_club_peak**: outside band: {'pelvis': 490, 'thorax': -10, 'arm': 0} (pro means 87/68/65 ms, amateur 78/59/64)
- **WARN swing/peak_speed_pelvis_deg_s**: 0.00 x target at 132 mph (target EXTRAPOLATED beyond measured 88-109 mph) [value 0.0]
- **WARN swing/peak_speed_thorax_deg_s**: 0.00 x target at 132 mph (target EXTRAPOLATED beyond measured 88-109 mph) [value 0.4]
- **WARN swing/peak_speed_arm_deg_s**: 2.04 x target at 132 mph (target EXTRAPOLATED beyond measured 88-109 mph) [value 2501.4]
- **FAIL swing/x_factor_top_deg**: max |thorax - pelvis| before impact (published 24-59 deg, method dependent); stretch not checked [value 0.0]
- **FAIL swing/grf_lead_vertical_bw**: peak lead-foot vertical force in body weights; min < 0 means the foot pulls on the ground
- **WARN shot/total_over_carry**: total/carry (normal turf 1.07-1.13, firm to ~1.2; env without roll gives 1.0) [value 0.999]
- **FAIL mine/segments_rotate**: pelvis does not rotate (peak 0.0 deg/s < 20, DERIVED) - the env pins the torso/pelvis (pin_torso=True); thorax does not rotate (peak 0.6 deg/s < 20, DERIVED)
- **FAIL mine/ground_contact_weight_shift**: feet do not collide with the ground in this model (0 of 2 foot geoms): ground reaction = 0 by construction
- **FAIL mine/joint_limits**: right_knee within 5% of a limit 100% of the swing (> 10%, DERIVED)
- **FAIL mine/torque_saturation_smoothness**: right_shoulder_pitch at its actuator cap 45% of the downswing (> 5%, DERIVED)
- **FAIL mine/tempo**: backswing:downswing 6.90:1 outside 2.5-4.0 (DERIVED around the published 3:1; TPI 3.2:1); downswing 105 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)

Key numbers: downswing 105 ms, backswing:downswing 6.90:1

### scripted_v3 (SCRIPTED (not learned); force_scale 2 (hypothetical-strength actuators); 24 episodes)

- **WARN swing/kinematic_sequence_order**: peak order pelvis->thorax->arm->club; not resolvable at dt=20 ms (same sample or reversed by one sample): [('thorax', 'arm'), ('arm', 'club')]
- **WARN swing/kinematic_sequence_timing_ms_before_club_peak**: outside band: {'pelvis': 490, 'thorax': -10, 'arm': 0} (pro means 87/68/65 ms, amateur 78/59/64)
- **WARN swing/peak_speed_pelvis_deg_s**: 0.00 x target at 120 mph (target EXTRAPOLATED beyond measured 88-109 mph) [value 0.0]
- **WARN swing/peak_speed_thorax_deg_s**: 0.00 x target at 120 mph (target EXTRAPOLATED beyond measured 88-109 mph) [value 0.3]
- **WARN swing/peak_speed_arm_deg_s**: 2.15 x target at 120 mph (target EXTRAPOLATED beyond measured 88-109 mph) [value 2369.8]
- **FAIL swing/x_factor_top_deg**: max |thorax - pelvis| before impact (published 24-59 deg, method dependent); stretch not checked [value 0.0]
- **FAIL swing/grf_lead_vertical_bw**: peak lead-foot vertical force in body weights; min < 0 means the foot pulls on the ground
- **WARN shot/smash**: ball speed / club speed; 1.50 is a COR (0.83) and 200 g head ceiling [value 1.002]
- **WARN shot/total_over_carry**: total/carry (normal turf 1.07-1.13, firm to ~1.2; env without roll gives 1.0) [value 0.996]
- **FAIL mine/segments_rotate**: pelvis does not rotate (peak 0.0 deg/s < 20, DERIVED) - the env pins the torso/pelvis (pin_torso=True); thorax does not rotate (peak 0.5 deg/s < 20, DERIVED)
- **FAIL mine/ground_contact_weight_shift**: feet do not collide with the ground in this model (0 of 2 foot geoms): ground reaction = 0 by construction
- **FAIL mine/joint_limits**: 
- **FAIL mine/torque_saturation_smoothness**: right_shoulder_pitch at its actuator cap 16% of the downswing (> 5%, DERIVED)
- **FAIL mine/tempo**: backswing:downswing 6.00:1 outside 2.5-4.0 (DERIVED around the published 3:1; TPI 3.2:1); downswing 120 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **WARN mine/carry_vs_trackman_band**: carry 119 yd outside the TrackMan AoA -5..+5 optimizer band 282-311 yd at 120 mph (band extrapolated outside 100-120 mph, DERIVED: WARN only)

Key numbers: downswing 120 ms, backswing:downswing 6.00:1

### scripted_v3_fs1_q23_dz016 (SCRIPTED (not learned); stock (force_scale 1); 24 episodes)

- **WARN swing/kinematic_sequence_order**: peak order pelvis->thorax->arm->club; not resolvable at dt=20 ms (same sample or reversed by one sample): [('thorax', 'arm'), ('arm', 'club')]
- **WARN swing/kinematic_sequence_timing_ms_before_club_peak**: outside band: {'pelvis': 490, 'thorax': -10, 'arm': 0} (pro means 87/68/65 ms, amateur 78/59/64)
- **FAIL swing/peak_speed_pelvis_deg_s**: 0.00 x target at 101 mph (between measured groups) [value 0.0]
- **FAIL swing/peak_speed_thorax_deg_s**: 0.00 x target at 101 mph (between measured groups) [value 0.2]
- **FAIL swing/peak_speed_arm_deg_s**: 2.13 x target at 101 mph (between measured groups) [value 1905.85]
- **FAIL swing/x_factor_top_deg**: max |thorax - pelvis| before impact (published 24-59 deg, method dependent); stretch not checked [value 0.0]
- **FAIL swing/grf_lead_vertical_bw**: peak lead-foot vertical force in body weights; min < 0 means the foot pulls on the ground
- **WARN shot/smash**: ball speed / club speed; 1.50 is a COR (0.83) and 200 g head ceiling [value 1.016]
- **WARN shot/launch_deg**: driver launch window (TrackMan 7.8-9.3 at AoA 0, Foresight 10-14) [value 17.785]
- **WARN shot/total_over_carry**: total/carry (normal turf 1.07-1.13, firm to ~1.2; env without roll gives 1.0) [value 0.997]
- **FAIL mine/segments_rotate**: pelvis does not rotate (peak 0.0 deg/s < 20, DERIVED) - the env pins the torso/pelvis (pin_torso=True); thorax does not rotate (peak 0.3 deg/s < 20, DERIVED)
- **FAIL mine/ground_contact_weight_shift**: feet do not collide with the ground in this model (0 of 2 foot geoms): ground reaction = 0 by construction
- **FAIL mine/joint_limits**: right_knee within 5% of a limit 100% of the swing (> 10%, DERIVED)
- **FAIL mine/torque_saturation_smoothness**: right_shoulder_pitch at its actuator cap 70% of the downswing (> 5%, DERIVED)
- **FAIL mine/tempo**: backswing:downswing 5.05:1 outside 2.5-4.0 (DERIVED around the published 3:1; TPI 3.2:1); downswing 145 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **FAIL mine/carry_vs_trackman_band**: carry 156 yd outside the TrackMan AoA -5..+5 optimizer band 225-250 yd at 101 mph

Key numbers: downswing 145 ms, backswing:downswing 5.05:1

### ppo_v4yaw_s43 (residual PPO (yaw-only residual); force_scale 2 + impact gain (HYPOTHETICAL); 24 episodes)

- **WARN swing/kinematic_sequence_order**: peak order pelvis->thorax->arm->club; not resolvable at dt=20 ms (same sample or reversed by one sample): [('thorax', 'arm'), ('arm', 'club')]
- **WARN swing/kinematic_sequence_timing_ms_before_club_peak**: outside band: {'pelvis': 490, 'thorax': -10, 'arm': 5} (pro means 87/68/65 ms, amateur 78/59/64)
- **WARN swing/peak_speed_pelvis_deg_s**: 0.00 x target at 128 mph (target EXTRAPOLATED beyond measured 88-109 mph) [value 0.0]
- **WARN swing/peak_speed_thorax_deg_s**: 0.00 x target at 128 mph (target EXTRAPOLATED beyond measured 88-109 mph) [value 2.0]
- **WARN swing/peak_speed_arm_deg_s**: 2.13 x target at 128 mph (target EXTRAPOLATED beyond measured 88-109 mph) [value 2525.0]
- **FAIL swing/x_factor_top_deg**: max |thorax - pelvis| before impact (published 24-59 deg, method dependent); stretch not checked [value 0.1]
- **FAIL swing/grf_lead_vertical_bw**: peak lead-foot vertical force in body weights; min < 0 means the foot pulls on the ground
- **FAIL shot/smash**: ball speed / club speed; 1.50 is a COR (0.83) and 200 g head ceiling [value 1.484]
- **WARN shot/total_over_carry**: total/carry (normal turf 1.07-1.13, firm to ~1.2; env without roll gives 1.0) [value 0.999]
- **FAIL shot/carry_positive**: no carry (miss / air shot / ball never landed) [value 0.0]
- **FAIL mine/segments_rotate**: pelvis does not rotate (peak 0.0 deg/s < 20, DERIVED) - the env pins the torso/pelvis (pin_torso=True); thorax does not rotate (peak 2.1 deg/s < 20, DERIVED)
- **FAIL mine/ground_contact_weight_shift**: feet do not collide with the ground in this model (0 of 2 foot geoms): ground reaction = 0 by construction
- **FAIL mine/joint_limits**: 
- **FAIL mine/torque_saturation_smoothness**: right_shoulder_pitch at its actuator cap 39% of the downswing (> 5%, DERIVED)
- **FAIL mine/tempo**: backswing:downswing 6.55:1 outside 2.5-4.0 (DERIVED around the published 3:1; TPI 3.2:1); downswing 110 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **WARN mine/carry_vs_trackman_band**: carry 292 yd outside the TrackMan AoA -5..+5 optimizer band 306-336 yd at 128 mph (band extrapolated outside 100-120 mph, DERIVED: WARN only)

Key numbers: downswing 110 ms, backswing:downswing 6.55:1

### ppo15_klres_s101 (= init, not learned; force_scale 2 (hypothetical-strength); 24 episodes)

- **WARN swing/kinematic_sequence_order**: peak order pelvis->thorax->arm->club; not resolvable at dt=20 ms (same sample or reversed by one sample): [('thorax', 'arm'), ('arm', 'club')]
- **WARN swing/kinematic_sequence_timing_ms_before_club_peak**: outside band: {'pelvis': 490, 'thorax': -10, 'arm': 0} (pro means 87/68/65 ms, amateur 78/59/64)
- **WARN swing/peak_speed_pelvis_deg_s**: 0.00 x target at 120 mph (target EXTRAPOLATED beyond measured 88-109 mph) [value 0.0]
- **WARN swing/peak_speed_thorax_deg_s**: 0.00 x target at 120 mph (target EXTRAPOLATED beyond measured 88-109 mph) [value 0.2]
- **WARN swing/peak_speed_arm_deg_s**: 2.15 x target at 120 mph (target EXTRAPOLATED beyond measured 88-109 mph) [value 2369.75]
- **FAIL swing/x_factor_top_deg**: max |thorax - pelvis| before impact (published 24-59 deg, method dependent); stretch not checked [value 0.0]
- **FAIL swing/grf_lead_vertical_bw**: peak lead-foot vertical force in body weights; min < 0 means the foot pulls on the ground
- **WARN shot/smash**: ball speed / club speed; 1.50 is a COR (0.83) and 200 g head ceiling [value 1.002]
- **WARN shot/total_over_carry**: total/carry (normal turf 1.07-1.13, firm to ~1.2; env without roll gives 1.0) [value 0.996]
- **FAIL mine/segments_rotate**: pelvis does not rotate (peak 0.0 deg/s < 20, DERIVED) - the env pins the torso/pelvis (pin_torso=True); thorax does not rotate (peak 0.3 deg/s < 20, DERIVED)
- **FAIL mine/ground_contact_weight_shift**: feet do not collide with the ground in this model (0 of 2 foot geoms): ground reaction = 0 by construction
- **FAIL mine/joint_limits**: right_knee within 5% of a limit 100% of the swing (> 10%, DERIVED)
- **FAIL mine/torque_saturation_smoothness**: right_shoulder_pitch at its actuator cap 16% of the downswing (> 5%, DERIVED)
- **FAIL mine/tempo**: backswing:downswing 6.10:1 outside 2.5-4.0 (DERIVED around the published 3:1; TPI 3.2:1); downswing 120 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **WARN mine/carry_vs_trackman_band**: carry 119 yd outside the TrackMan AoA -5..+5 optimizer band 282-311 yd at 120 mph (band extrapolated outside 100-120 mph, DERIVED: WARN only)

Key numbers: downswing 120 ms, backswing:downswing 6.10:1

### ppo20_klres_s111 (= init, not learned; stock (force_scale 1); 24 episodes)

- **WARN swing/kinematic_sequence_order**: peak order pelvis->thorax->arm->club; not resolvable at dt=20 ms (same sample or reversed by one sample): [('thorax', 'arm'), ('arm', 'club')]
- **WARN swing/kinematic_sequence_timing_ms_before_club_peak**: outside band: {'pelvis': 490, 'thorax': -10, 'arm': 0} (pro means 87/68/65 ms, amateur 78/59/64)
- **FAIL swing/peak_speed_pelvis_deg_s**: 0.00 x target at 101 mph (between measured groups) [value 0.0]
- **FAIL swing/peak_speed_thorax_deg_s**: 0.00 x target at 101 mph (between measured groups) [value 0.2]
- **FAIL swing/peak_speed_arm_deg_s**: 2.13 x target at 101 mph (between measured groups) [value 1905.85]
- **FAIL swing/x_factor_top_deg**: max |thorax - pelvis| before impact (published 24-59 deg, method dependent); stretch not checked [value 0.0]
- **FAIL swing/grf_lead_vertical_bw**: peak lead-foot vertical force in body weights; min < 0 means the foot pulls on the ground
- **WARN shot/smash**: ball speed / club speed; 1.50 is a COR (0.83) and 200 g head ceiling [value 1.016]
- **WARN shot/launch_deg**: driver launch window (TrackMan 7.8-9.3 at AoA 0, Foresight 10-14) [value 17.805]
- **WARN shot/total_over_carry**: total/carry (normal turf 1.07-1.13, firm to ~1.2; env without roll gives 1.0) [value 0.997]
- **FAIL mine/segments_rotate**: pelvis does not rotate (peak 0.0 deg/s < 20, DERIVED) - the env pins the torso/pelvis (pin_torso=True); thorax does not rotate (peak 0.3 deg/s < 20, DERIVED)
- **FAIL mine/ground_contact_weight_shift**: feet do not collide with the ground in this model (0 of 2 foot geoms): ground reaction = 0 by construction
- **FAIL mine/joint_limits**: right_knee within 5% of a limit 100% of the swing (> 10%, DERIVED)
- **FAIL mine/torque_saturation_smoothness**: right_shoulder_pitch at its actuator cap 70% of the downswing (> 5%, DERIVED)
- **FAIL mine/tempo**: backswing:downswing 5.05:1 outside 2.5-4.0 (DERIVED around the published 3:1; TPI 3.2:1); downswing 145 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **FAIL mine/carry_vs_trackman_band**: carry 155 yd outside the TrackMan AoA -5..+5 optimizer band 225-250 yd at 101 mph

Key numbers: downswing 145 ms, backswing:downswing 5.05:1

### ppo_resid_v3_s0 (residual PPO (older); older residual PPO (see its results JSON); 24 episodes)

- **WARN swing/kinematic_sequence_order**: peak order pelvis->thorax->arm->club; not resolvable at dt=20 ms (same sample or reversed by one sample): [('thorax', 'arm'), ('arm', 'club')]
- **WARN swing/kinematic_sequence_timing_ms_before_club_peak**: outside band: {'pelvis': 20, 'thorax': -10, 'arm': 0} (pro means 87/68/65 ms, amateur 78/59/64)
- **FAIL swing/peak_speed_pelvis_deg_s**: 0.00 x target at 100 mph (between measured groups) [value 0.0]
- **FAIL swing/peak_speed_thorax_deg_s**: 0.03 x target at 100 mph (between measured groups) [value 16.45]
- **FAIL swing/peak_speed_arm_deg_s**: 0.16 x target at 100 mph (between measured groups) [value 140.1]
- **FAIL swing/peak_speed_club_deg_s**: 0.06 x target at 100 mph (between measured groups) [value 130.55]
- **FAIL swing/x_factor_top_deg**: max |thorax - pelvis| before impact (published 24-59 deg, method dependent); stretch not checked [value 0.4]
- **FAIL swing/grf_lead_vertical_bw**: peak lead-foot vertical force in body weights; min < 0 means the foot pulls on the ground
- **WARN shot/smash**: ball speed / club speed; 1.50 is a COR (0.83) and 200 g head ceiling [value 0.6585000000000001]
- **FAIL shot/launch_deg**: driver launch window (TrackMan 7.8-9.3 at AoA 0, Foresight 10-14) [value 47.805]
- **WARN shot/total_over_carry**: total/carry (normal turf 1.07-1.13, firm to ~1.2; env without roll gives 1.0) [value 0.993]
- **FAIL shot/carry_positive**: no carry (miss / air shot / ball never landed) [value -32.28738324576444]
- **FAIL mine/segments_rotate**: pelvis does not rotate (peak 0.0 deg/s < 20, DERIVED) - the env pins the torso/pelvis (pin_torso=True)
- **FAIL mine/ground_contact_weight_shift**: feet do not collide with the ground in this model (0 of 2 foot geoms): ground reaction = 0 by construction
- **FAIL mine/joint_limits**: 
- **FAIL mine/tempo**: backswing:downswing 0.65:1 outside 2.5-4.0 (DERIVED around the published 3:1; TPI 3.2:1); downswing 0 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **FAIL mine/carry_vs_trackman_band**: carry 67 yd outside the TrackMan AoA -5..+5 optimizer band 223-248 yd at 100 mph

Key numbers: downswing 0 ms, backswing:downswing 0.65:1

## Reconcile with the Data Agent's `data/references/realism_thresholds.json` (diff by key)

| key | this harness before | Data Agent (cited) | used now |
|---|---|---|---|
| x_factor top band (deg) | pass 39.4-70.7 (DERIVED, 2 SD of 50.8+-5.7 / 54.9+-7.9) | pass 40-65, warn 28-80, fail outside 20-90 (derived; Parker 54.9+-7.9, Myers, Hume) | Data Agent (via check_swing_realism x_factor_top_deg) |
| x_factor stretch | stretch >= 2 deg required (DERIVED) | not checked (published 1-3 deg joint-coordinate, ~10 deg sensor method) | Data Agent: dropped as a pass criterion |
| segment peak speeds | ~477/727/980/2254 deg/s (Cheetham 2001-style pro means) as text only | table by club speed (Cheetham 2008 two-group fit): at 100 mph 442/665/886/2054; 90, 120, 132 mph rows tagged extrapolated; pass ratio 0.7-1.3 | Data Agent (peak_speed_*_deg_s); extrapolated rows capped at WARN (Orchestrator rule) |
| kinematic order / timing | order + increasing peaks + decel before impact (DERIVED 95%) | order pelvis,thorax,arm,club; tie tolerance 20 ms (50 Hz control resolution); lead times pro 87/68/65 ms, warn bands | Data Agent (order, timing); my decel check dropped; my 'segments_rotate' guard kept (a static pelvis would otherwise pass 'order' by argmax-of-zeros) |
| ground reaction | peak lead vertical 0.84 BW (PMC3794489, single study) with half-BW floor | lead vertical pass 0.8-1.7 BW, warn 0.5-2.4, fail outside -0.02..3.0 (Worsfold, Han, Hirano, Hume) | Data Agent (grf_lead_vertical_bw); my contact/weight-shift check kept (published qualitative transfer, +0.10 share DERIVED) |
| smash | FAIL >1.50, WARN >1.49 / <1.30 (data/launch_output.py) | fail >1.5, warn >1.49 or <1.3 (published TrackMan/R&A) | identical; Data Agent's check_shot_realism used |
| launch angle | TrackMan AoA -5..+5 band (3.9-14.8 deg) | pass 7-16, warn 4-20, fail outside 2-25 (derived) | Data Agent |
| spin | 1800-3000 pass (DERIVED), absent in this env | pass 1800-3000, warn 1200-4000 | Data Agent; SKIPPED here because the v1 env has no spin |
| carry | inside TrackMan carry-optimizer band 100-120 mph | golfphys residual |<=15 yd| pass (skipped without spin); total/carry 1.04-1.25 pass | Data Agent for total/carry and golfphys carry (skipped w/o spin); my TrackMan band kept as an extra check, WARN only outside 100-120 mph |
| descent angle | not checked | pass 30-48, warn 25-55 | Data Agent (skipped: this env does not log descent) |
| tempo | ratio 2.5-4.0 (DERIVED around 3:1); downswing 210-390 ms (DERIVED from PMC9227529) | no tempo key | mine (kept; nothing to defer to) |
| joint limits / torque saturation | 5%-of-range / 98%-of-cap bands (DERIVED) | G1-tier torque-speed limits only (not this humanoid; check skipped) | mine (kept) |
| actuator torque-speed / power feasibility | - | G1 stock/elite tier tables | skipped (tier=None: this humanoid is not the G1) |

The Data Agent's file is not modified. Golfphys: `golfphys-lh-fix` (357bc0c) is already on main (05a482e), so the corrected left-hand high/low strike is what `check_shot_realism` uses; the old left-hand high-strike spin is not used anywhere in this harness (the v1 env has no spin).

## Model structure (measured, same for all v1 rows)

- Torso/pelvis pinned by the env each physics step (`pin_torso`): True (no pelvis translation or rotation, so the kinematic sequence cannot start at the pelvis, and the whole body cannot shift weight); equality constraints (hands grip only): [['0', 'left_hand', 'right_wrist']]
- Foot geoms: 2, with collision enabled: 0 (no ground reaction force exists)
- Model mass 32.25 kg; only one trunk rotation DOF (chest_yaw), pitch-only hips/knees/ankles.

## Check of the 'pelvis = 0 / X-factor = 0' finding (raw-trace audit, 2026-10-17): NOT a recording error

Rolled out one scripted v3 (fs1 q23 dz016), one scripted v3 (fs2) and one imit20 swing (seed 4000) and dumped raw MuJoCo state every 5 ms:
- What the harness reads: pelvis = body `torso`, thorax = body `chest`, lead arm = body `right_elbow`, club = body `right_wrist`; speed = |`data.cvel[body][:3]`| (world angular velocity, rad/s) x 180/pi = deg/s. X-factor = joint `chest_yaw` (`qpos[20]`, rad, relative to the pelvis because the pelvis does not turn) x 180/pi = deg.
- `pin_torso` really pins the pelvis: `env.pin_torso` is True (residual env default) and the env resets `qpos[7:14]` and `qvel[6:12]` every physics step; measured torso quaternion deviation 0.0, root qpos deviation 1.2e-5, root qvel max 0.05 (reset after each step, so sub-step noise).
- Raw `chest_yaw`: total range 0.0095 deg (scripted fs1), 0.0138 deg (scripted fs2), 0.0096 deg (imit20); max |qvel| 0.62-0.69 deg/s, against a joint range of +-45 deg. The chest does not rotate in these swings (`yaw_ff` 0.0, yaw channel not driven), so X-factor ~ 0 deg is real, not a units or indexing error. Even ppo_v4yaw_s43 reaches only 0.07 deg and ppo_resid_v3_s0 0.37 deg.

