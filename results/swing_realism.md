# Swing realism: does the rolled-out swing look and behave like a real golf swing?

**Protocol:** deterministic rollouts, gate seeds [4000, 8000, 9000] x 8 episodes (seed+i), gate env kwargs; medians over true-contact episodes. every band marked DERIVED is built from published mean+-SD, not a published threshold. References are cited in `eval/swing_realism.py` (Cheetham et al. kinematic sequence; Korean-pro / elite / Stanford X-factor; PMC9227529 downswing times; TPI tempo; PMC3794489 GRF and friction; TrackMan optimizer rows).

**Overall verdict = PASS only if all 8 checks pass.** No human-attainable-power claim is made; force_scale 2 and the power tier are hypothetical.

| model | tier | verdict | passed | kinematic_sequence | x_factor | joint_limits | torque_power | ground_reaction | tempo | ball_flight_tables | smash_spin_flags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| imit20_fs1_q23_dart_s51 | stock (force_scale 1) | **FAIL** | 0/8 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| imit16_fs1_dart_s51 | stock (force_scale 1) | **FAIL** | 0/8 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| imit18_power_dart_s51 | hypothetical power tier (impact gain 1.28 inflated) | **FAIL** | 0/8 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| imit18_power_dart_s51@gain1.2 | hypothetical power tier (impact gain 1.2, no spin model) | **FAIL** | 1/8 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | PASS |
| scripted_v3 | force_scale 2 (hypothetical-strength actuators) | **FAIL** | 0/8 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| scripted_v3_fs1_q23_dz016 | stock (force_scale 1) | **FAIL** | 0/8 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| ppo_v4yaw_s43 | force_scale 2 + impact gain (HYPOTHETICAL) | **FAIL** | 1/8 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | PASS |
| ppo15_klres_s101 | force_scale 2 (hypothetical-strength) | **FAIL** | 0/8 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| ppo20_klres_s111 | stock (force_scale 1) | **FAIL** | 0/8 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| ppo_resid_v3_s0 | older residual PPO (see its results JSON) | **FAIL** | 1/8 | FAIL | FAIL | FAIL | PASS | FAIL | FAIL | FAIL | FAIL |

## Why each model fails

### imit20_fs1_q23_dart_s51 (script-distilled policy; stock (force_scale 1); 24 episodes)

- **FAIL 1_kinematic_sequence**: pelvis does not rotate (peak 0.0 deg/s < 20): structural - the env pins the torso/pelvis (pin_torso=True, qpos/qvel reset every physics step); thorax does not rotate (peak 0.3 deg/s < 20): structural
- **FAIL 2_x_factor**: peak X-factor 0.0 deg outside 39.4-70.7 (DERIVED from 50.8+-5.7 / 54.9+-7.9); no X-factor stretch in the early downswing (0.0 deg < 2, DERIVED); the pelvis is pinned by the env (no pelvis rotation), so 'X-factor' here is chest yaw alone vs a fixed pelvis
- **FAIL 3_joint_limits**: right_knee within 5% of a limit 100% of the swing (> 10%, DERIVED)
- **FAIL 4_torque_power**: right_shoulder_pitch at its actuator cap 70% of the downswing (> 5%, DERIVED)
- **FAIL 5_ground_reaction**: feet do not collide with the ground in this model (0 of 2 foot geoms have collision enabled): ground reaction = 0.00 BW by construction; no weight shift measurable (no foot force)
- **FAIL 6_tempo**: backswing:downswing 5.05:1 outside 2.5-4.0 (DERIVED around the published 3:1); downswing 145 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **FAIL 7_ball_flight_tables**: carry 155 yd outside the TrackMan AoA -5..+5 optimizer band 225-250 yd at 101 mph; launch 17.8 deg outside the same band 9.4-14.8 deg
- **FAIL 8_smash_spin_flags**: WARN smash<1.30 (poor/non-physical contact?); spin is not simulated (hand-set backspin), so no spin check is possible

Key numbers: downswing 145 ms, backswing:downswing 5.05:1, X-factor peak 0.0 deg, club 100.9 mph, smash 1.02, carry 155 yd, peak power 7068 W

### imit16_fs1_dart_s51 (script-distilled policy; stock (force_scale 1); 24 episodes)

- **FAIL 1_kinematic_sequence**: pelvis does not rotate (peak 0.0 deg/s < 20): structural - the env pins the torso/pelvis (pin_torso=True, qpos/qvel reset every physics step); thorax does not rotate (peak 0.3 deg/s < 20): structural
- **FAIL 2_x_factor**: peak X-factor 0.0 deg outside 39.4-70.7 (DERIVED from 50.8+-5.7 / 54.9+-7.9); no X-factor stretch in the early downswing (0.0 deg < 2, DERIVED); the pelvis is pinned by the env (no pelvis rotation), so 'X-factor' here is chest yaw alone vs a fixed pelvis
- **FAIL 3_joint_limits**: right_knee within 5% of a limit 100% of the swing (> 10%, DERIVED)
- **FAIL 4_torque_power**: right_shoulder_pitch at its actuator cap 69% of the downswing (> 5%, DERIVED)
- **FAIL 5_ground_reaction**: feet do not collide with the ground in this model (0 of 2 foot geoms have collision enabled): ground reaction = 0.00 BW by construction; no weight shift measurable (no foot force)
- **FAIL 6_tempo**: backswing:downswing 5.21:1 outside 2.5-4.0 (DERIVED around the published 3:1); downswing 140 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **FAIL 7_ball_flight_tables**: carry 80 yd outside the TrackMan AoA -5..+5 optimizer band 218-242 yd at 99 mph (band extrapolated outside 100-120 mph, DERIVED)
- **FAIL 8_smash_spin_flags**: WARN smash<1.30 (poor/non-physical contact?); spin is not simulated (hand-set backspin), so no spin check is possible

Key numbers: downswing 140 ms, backswing:downswing 5.21:1, X-factor peak 0.0 deg, club 98.5 mph, smash 1.00, carry 80 yd, peak power 6899 W

### imit18_power_dart_s51 (script-distilled policy; hypothetical power tier (impact gain 1.28 inflated); 24 episodes)

- **FAIL 1_kinematic_sequence**: pelvis does not rotate (peak 0.0 deg/s < 20): structural - the env pins the torso/pelvis (pin_torso=True, qpos/qvel reset every physics step); thorax does not rotate (peak 0.6 deg/s < 20): structural
- **FAIL 2_x_factor**: peak X-factor 0.0 deg outside 39.4-70.7 (DERIVED from 50.8+-5.7 / 54.9+-7.9); no X-factor stretch in the early downswing (0.0 deg < 2, DERIVED); the pelvis is pinned by the env (no pelvis rotation), so 'X-factor' here is chest yaw alone vs a fixed pelvis
- **FAIL 3_joint_limits**: right_knee within 5% of a limit 100% of the swing (> 10%, DERIVED)
- **FAIL 4_torque_power**: right_shoulder_pitch at its actuator cap 45% of the downswing (> 5%, DERIVED)
- **FAIL 5_ground_reaction**: feet do not collide with the ground in this model (0 of 2 foot geoms have collision enabled): ground reaction = 0.00 BW by construction; no weight shift measurable (no foot force)
- **FAIL 6_tempo**: backswing:downswing 6.90:1 outside 2.5-4.0 (DERIVED around the published 3:1); downswing 105 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **FAIL 7_ball_flight_tables**: launch 12.6 deg outside the same band 3.9-11.2 deg
- **FAIL 8_smash_spin_flags**: FAIL smash>1.50; spin is not simulated (hand-set backspin), so no spin check is possible

Key numbers: downswing 105 ms, backswing:downswing 6.90:1, X-factor peak 0.0 deg, club 132.4 mph, smash 1.56, carry 338 yd, peak power 18112 W

### imit18_power_dart_s51@gain1.2 (script-distilled policy; hypothetical power tier (impact gain 1.2, no spin model); 24 episodes)

- **FAIL 1_kinematic_sequence**: pelvis does not rotate (peak 0.0 deg/s < 20): structural - the env pins the torso/pelvis (pin_torso=True, qpos/qvel reset every physics step); thorax does not rotate (peak 0.6 deg/s < 20): structural
- **FAIL 2_x_factor**: peak X-factor 0.0 deg outside 39.4-70.7 (DERIVED from 50.8+-5.7 / 54.9+-7.9); no X-factor stretch in the early downswing (0.0 deg < 2, DERIVED); the pelvis is pinned by the env (no pelvis rotation), so 'X-factor' here is chest yaw alone vs a fixed pelvis
- **FAIL 3_joint_limits**: right_knee within 5% of a limit 100% of the swing (> 10%, DERIVED)
- **FAIL 4_torque_power**: right_shoulder_pitch at its actuator cap 45% of the downswing (> 5%, DERIVED)
- **FAIL 5_ground_reaction**: feet do not collide with the ground in this model (0 of 2 foot geoms have collision enabled): ground reaction = 0.00 BW by construction; no weight shift measurable (no foot force)
- **FAIL 6_tempo**: backswing:downswing 6.90:1 outside 2.5-4.0 (DERIVED around the published 3:1); downswing 105 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **FAIL 7_ball_flight_tables**: launch 12.6 deg outside the same band 3.9-11.2 deg

Key numbers: downswing 105 ms, backswing:downswing 6.90:1, X-factor peak 0.0 deg, club 132.4 mph, smash 1.47, carry 322 yd, peak power 18112 W

### scripted_v3 (SCRIPTED (not learned); force_scale 2 (hypothetical-strength actuators); 24 episodes)

- **FAIL 1_kinematic_sequence**: pelvis does not rotate (peak 0.0 deg/s < 20): structural - the env pins the torso/pelvis (pin_torso=True, qpos/qvel reset every physics step); thorax does not rotate (peak 0.5 deg/s < 20): structural
- **FAIL 2_x_factor**: peak X-factor 0.0 deg outside 39.4-70.7 (DERIVED from 50.8+-5.7 / 54.9+-7.9); no X-factor stretch in the early downswing (0.0 deg < 2, DERIVED); the pelvis is pinned by the env (no pelvis rotation), so 'X-factor' here is chest yaw alone vs a fixed pelvis
- **FAIL 3_joint_limits**
- **FAIL 4_torque_power**: right_shoulder_pitch at its actuator cap 16% of the downswing (> 5%, DERIVED)
- **FAIL 5_ground_reaction**: feet do not collide with the ground in this model (0 of 2 foot geoms have collision enabled): ground reaction = 0.00 BW by construction; no weight shift measurable (no foot force)
- **FAIL 6_tempo**: backswing:downswing 6.00:1 outside 2.5-4.0 (DERIVED around the published 3:1); downswing 120 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **FAIL 7_ball_flight_tables**: carry 119 yd outside the TrackMan AoA -5..+5 optimizer band 282-311 yd at 120 mph (band extrapolated outside 100-120 mph, DERIVED); launch 12.7 deg outside the same band 6.0-12.5 deg
- **FAIL 8_smash_spin_flags**: WARN smash<1.30 (poor/non-physical contact?); spin is not simulated (hand-set backspin), so no spin check is possible

Key numbers: downswing 120 ms, backswing:downswing 6.00:1, X-factor peak 0.0 deg, club 120.4 mph, smash 1.00, carry 119 yd, peak power 16215 W

### scripted_v3_fs1_q23_dz016 (SCRIPTED (not learned); stock (force_scale 1); 24 episodes)

- **FAIL 1_kinematic_sequence**: pelvis does not rotate (peak 0.0 deg/s < 20): structural - the env pins the torso/pelvis (pin_torso=True, qpos/qvel reset every physics step); thorax does not rotate (peak 0.3 deg/s < 20): structural
- **FAIL 2_x_factor**: peak X-factor 0.0 deg outside 39.4-70.7 (DERIVED from 50.8+-5.7 / 54.9+-7.9); no X-factor stretch in the early downswing (0.0 deg < 2, DERIVED); the pelvis is pinned by the env (no pelvis rotation), so 'X-factor' here is chest yaw alone vs a fixed pelvis
- **FAIL 3_joint_limits**: right_knee within 5% of a limit 100% of the swing (> 10%, DERIVED)
- **FAIL 4_torque_power**: right_shoulder_pitch at its actuator cap 70% of the downswing (> 5%, DERIVED)
- **FAIL 5_ground_reaction**: feet do not collide with the ground in this model (0 of 2 foot geoms have collision enabled): ground reaction = 0.00 BW by construction; no weight shift measurable (no foot force)
- **FAIL 6_tempo**: backswing:downswing 5.05:1 outside 2.5-4.0 (DERIVED around the published 3:1); downswing 145 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **FAIL 7_ball_flight_tables**: carry 156 yd outside the TrackMan AoA -5..+5 optimizer band 225-250 yd at 101 mph; launch 17.8 deg outside the same band 9.4-14.8 deg
- **FAIL 8_smash_spin_flags**: WARN smash<1.30 (poor/non-physical contact?); spin is not simulated (hand-set backspin), so no spin check is possible

Key numbers: downswing 145 ms, backswing:downswing 5.05:1, X-factor peak 0.0 deg, club 100.9 mph, smash 1.02, carry 156 yd, peak power 7068 W

### ppo_v4yaw_s43 (residual PPO (yaw-only residual); force_scale 2 + impact gain (HYPOTHETICAL); 24 episodes)

- **FAIL 1_kinematic_sequence**: pelvis does not rotate (peak 0.0 deg/s < 20): structural - the env pins the torso/pelvis (pin_torso=True, qpos/qvel reset every physics step); thorax does not rotate (peak 2.1 deg/s < 20): structural
- **FAIL 2_x_factor**: peak X-factor 0.1 deg outside 39.4-70.7 (DERIVED from 50.8+-5.7 / 54.9+-7.9); no X-factor stretch in the early downswing (0.0 deg < 2, DERIVED); the pelvis is pinned by the env (no pelvis rotation), so 'X-factor' here is chest yaw alone vs a fixed pelvis
- **FAIL 3_joint_limits**
- **FAIL 4_torque_power**: right_shoulder_pitch at its actuator cap 39% of the downswing (> 5%, DERIVED)
- **FAIL 5_ground_reaction**: feet do not collide with the ground in this model (0 of 2 foot geoms have collision enabled): ground reaction = 0.00 BW by construction; no weight shift measurable (no foot force)
- **FAIL 6_tempo**: backswing:downswing 6.55:1 outside 2.5-4.0 (DERIVED around the published 3:1); downswing 110 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **FAIL 7_ball_flight_tables**: carry 292 yd outside the TrackMan AoA -5..+5 optimizer band 306-336 yd at 128 mph (band extrapolated outside 100-120 mph, DERIVED); launch 11.6 deg outside the same band 4.6-11.6 deg

Key numbers: downswing 110 ms, backswing:downswing 6.55:1, X-factor peak 0.1 deg, club 128.4 mph, smash 1.48, carry 292 yd, peak power 18261 W

### ppo15_klres_s101 (= init, not learned; force_scale 2 (hypothetical-strength); 24 episodes)

- **FAIL 1_kinematic_sequence**: pelvis does not rotate (peak 0.0 deg/s < 20): structural - the env pins the torso/pelvis (pin_torso=True, qpos/qvel reset every physics step); thorax does not rotate (peak 0.3 deg/s < 20): structural
- **FAIL 2_x_factor**: peak X-factor 0.0 deg outside 39.4-70.7 (DERIVED from 50.8+-5.7 / 54.9+-7.9); no X-factor stretch in the early downswing (0.0 deg < 2, DERIVED); the pelvis is pinned by the env (no pelvis rotation), so 'X-factor' here is chest yaw alone vs a fixed pelvis
- **FAIL 3_joint_limits**: right_knee within 5% of a limit 100% of the swing (> 10%, DERIVED)
- **FAIL 4_torque_power**: right_shoulder_pitch at its actuator cap 16% of the downswing (> 5%, DERIVED)
- **FAIL 5_ground_reaction**: feet do not collide with the ground in this model (0 of 2 foot geoms have collision enabled): ground reaction = 0.00 BW by construction; no weight shift measurable (no foot force)
- **FAIL 6_tempo**: backswing:downswing 6.10:1 outside 2.5-4.0 (DERIVED around the published 3:1); downswing 120 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **FAIL 7_ball_flight_tables**: carry 119 yd outside the TrackMan AoA -5..+5 optimizer band 282-311 yd at 120 mph (band extrapolated outside 100-120 mph, DERIVED); launch 12.8 deg outside the same band 6.0-12.5 deg
- **FAIL 8_smash_spin_flags**: WARN smash<1.30 (poor/non-physical contact?); spin is not simulated (hand-set backspin), so no spin check is possible

Key numbers: downswing 120 ms, backswing:downswing 6.10:1, X-factor peak 0.0 deg, club 120.4 mph, smash 1.00, carry 119 yd, peak power 16215 W

### ppo20_klres_s111 (= init, not learned; stock (force_scale 1); 24 episodes)

- **FAIL 1_kinematic_sequence**: pelvis does not rotate (peak 0.0 deg/s < 20): structural - the env pins the torso/pelvis (pin_torso=True, qpos/qvel reset every physics step); thorax does not rotate (peak 0.3 deg/s < 20): structural
- **FAIL 2_x_factor**: peak X-factor 0.0 deg outside 39.4-70.7 (DERIVED from 50.8+-5.7 / 54.9+-7.9); no X-factor stretch in the early downswing (0.0 deg < 2, DERIVED); the pelvis is pinned by the env (no pelvis rotation), so 'X-factor' here is chest yaw alone vs a fixed pelvis
- **FAIL 3_joint_limits**: right_knee within 5% of a limit 100% of the swing (> 10%, DERIVED)
- **FAIL 4_torque_power**: right_shoulder_pitch at its actuator cap 70% of the downswing (> 5%, DERIVED)
- **FAIL 5_ground_reaction**: feet do not collide with the ground in this model (0 of 2 foot geoms have collision enabled): ground reaction = 0.00 BW by construction; no weight shift measurable (no foot force)
- **FAIL 6_tempo**: backswing:downswing 5.05:1 outside 2.5-4.0 (DERIVED around the published 3:1); downswing 145 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **FAIL 7_ball_flight_tables**: carry 155 yd outside the TrackMan AoA -5..+5 optimizer band 225-250 yd at 101 mph; launch 17.8 deg outside the same band 9.4-14.8 deg
- **FAIL 8_smash_spin_flags**: WARN smash<1.30 (poor/non-physical contact?); spin is not simulated (hand-set backspin), so no spin check is possible

Key numbers: downswing 145 ms, backswing:downswing 5.05:1, X-factor peak 0.0 deg, club 100.9 mph, smash 1.02, carry 155 yd, peak power 7068 W

### ppo_resid_v3_s0 (residual PPO (older); older residual PPO (see its results JSON); 24 episodes)

- **FAIL 1_kinematic_sequence**: pelvis does not rotate (peak 0.0 deg/s < 20): structural - the env pins the torso/pelvis (pin_torso=True, qpos/qvel reset every physics step)
- **FAIL 2_x_factor**: peak X-factor 0.4 deg outside 39.4-70.7 (DERIVED from 50.8+-5.7 / 54.9+-7.9); no X-factor stretch in the early downswing (0.0 deg < 2, DERIVED); the pelvis is pinned by the env (no pelvis rotation), so 'X-factor' here is chest yaw alone vs a fixed pelvis
- **FAIL 3_joint_limits**
- **FAIL 5_ground_reaction**: feet do not collide with the ground in this model (0 of 2 foot geoms have collision enabled): ground reaction = 0.00 BW by construction; no weight shift measurable (no foot force)
- **FAIL 6_tempo**: backswing:downswing 0.65:1 outside 2.5-4.0 (DERIVED around the published 3:1); downswing 0 ms outside the human 210-390 ms (published pro 310+-40 ms, recreational 250+-20 ms)
- **FAIL 7_ball_flight_tables**: carry 67 yd outside the TrackMan AoA -5..+5 optimizer band 223-248 yd at 100 mph; launch 47.8 deg outside the same band 9.5-14.9 deg
- **FAIL 8_smash_spin_flags**: WARN smash<1.30 (poor/non-physical contact?); spin is not simulated (hand-set backspin), so no spin check is possible

Key numbers: downswing 0 ms, backswing:downswing 0.65:1, X-factor peak 0.4 deg, club 100.3 mph, smash 0.66, carry 67 yd, peak power 70 W

## Model structure (measured, same for all rows)

- Torso/pelvis pinned by the env each physics step (`pin_torso`): True (no pelvis translation or rotation, so the kinematic sequence cannot start at the pelvis, and the whole body cannot shift weight); equality constraints (hands grip only): [['0', 'left_hand', 'right_wrist']]
- Foot geoms: 2, with collision enabled: 0 (no ground reaction force exists)
- Model mass 32.25 kg; only one trunk rotation DOF (chest_yaw), pitch-only hips/knees/ankles.

## Check of the 'pelvis = 0 / X-factor = 0' finding (raw-trace audit, 2026-10-17): NOT a recording error

Rolled out one scripted v3 (fs1 q23 dz016), one scripted v3 (fs2) and one imit20 swing (seed 4000) and dumped raw MuJoCo state every 5 ms:
- What the harness reads: pelvis = body `torso`, thorax = body `chest`, lead arm = body `right_elbow`, club = body `right_wrist`; speed = |`data.cvel[body][:3]`| (world angular velocity, rad/s) x 180/pi = deg/s. X-factor = joint `chest_yaw` (`qpos[20]`, rad, relative to the pelvis because the pelvis does not turn) x 180/pi = deg.
- `pin_torso` really pins the pelvis: `env.pin_torso` is True (residual env default) and the env resets `qpos[7:14]` and `qvel[6:12]` every physics step; measured torso quaternion deviation 0.0, root qpos deviation 1.2e-5, root qvel max 0.05 (it is reset after each step, so the residual is sub-step noise).
- Raw `chest_yaw`: total range 0.0095 deg (scripted fs1), 0.0138 deg (scripted fs2), 0.0096 deg (imit20); max |qvel| 0.62-0.69 deg/s, against a joint range of +-45 deg. The chest does not rotate in these swings (the scripts have `yaw_ff` 0.0 and the yaw channel is not driven), so X-factor ~ 0 deg and the thorax speed ~ 0.3-0.7 deg/s are real, not units or indexing errors. Even the yaw-residual PPO (ppo_v4yaw_s43) reaches only 0.07 deg and the older ppo_resid_v3_s0 0.37 deg.

