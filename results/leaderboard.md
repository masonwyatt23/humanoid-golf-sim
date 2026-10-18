# Leaderboard

No evaluated models with smash inside 1.30-1.49. **NO model meets the showcase criterion (hypothetical-strength actuators if force_scale>1; carry >= 30 m, lateral std <= 2.73 m, launch elev >= 5 deg, contact 100%); see qualification table.** **SMASH GATE (launch_report thresholds, smash = det ball mph / impact club mph): rows outside 1.30-1.49 are flagged (FAIL >1.50, WARN >1.49 or <1.30) and cannot be a best/top/showcase row; 75 of 79 evaluated rows are flagged, 4 are not (see 'Smash flag' section).** Rows `imit_w075_s51/52/53` are excluded: INVALID config (eval rebuilt the env from args and dropped v3 settings; see TRAINING_NOTES CORRECTION; superseded by imit2/imit3). Rows with script_weight<1 are BLENDS (executed command = script_weight x scripted + rest learned), shown in the per-row summary. **Shown side by side, neither promoted as 'learned from Mason' (both imitate the scripted swing; force_scale 2 hypothetical-strength actuators): imit9_w000_s51: best lateral spread (script-free imitation of the scripted v3 swing; passes the 3-seed headline gate for s51/s52/s53) but NOISE-FRAGILE: det carry 120.0 m / lat std 0.96 m; quick noise sigma 0.005: 69 m (58%), sigma 0.01: 36 m (30%) (10 eps, vs clean 120 m) | imit3_w050_s51: best under observation/action noise (50% script-distilled policy / 50% scripted blend): det carry 119.4 m / lat std 2.20 m; quick noise sigma 0.005: 89 m (74%), sigma 0.01: 105 m (88%) (10 eps, vs clean 119 m).**

Ranking criterion: (1) true club-ball contact rate averaged over deterministic and stochastic modes, higher first; (2) ties broken by mean carry (m, averaged over both modes, mean over all episodes). Distance is not used.

Full ranking (scripted baseline included): imit18_power_dart_s51 > imit18_power_dart_s52 > ppo_v4power48_s71 > ppo_v4power_s62 > ppo_v4power_s61 > ppo_v4yaw_s42 > ppo_v4yaw_s43 > best_v4yaw_s41 > ppo20_soft_s121 > ppo20_klres_s111 > imit20_fs1_q23_dart_s51 > imit3_w050_s51 > imit9_w000_s52 > best_imit_scriptfree_elbow48_s51 > scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] > imit9_w000_s53 > best_learned_yaw_s31 > best_learned_yaw_s32 > imit3_w075_s53 > imit15_dart_s53 > imit3_w075_s51 > imit13_w000_s52 > ppo15_klres_s101 > imit2_w075_s52 > best_imit_scriptfree_s51_NOTPASS_lat3.56 > best_imit_w050_s52 > imit3_w075_s52 > imit2_w075_s53 > ppo_resid_v3_left_an3_s1 > imit3_w025_s51 > imit5_w000_s52 > ppo_v3tiny_s22 > best_carry_analytic > imit3_w000_s52 > ppo_resid_v3_left_an4_s2 > ppo_resid_v3_left_an1_s0 > ppo_v3flt_all_s33 > ppo_v3tiny_s23 > imit7_w000_s51 > imit8_w000_s51 > ppo_v3tiny_s21 > ppo_resid_v3_left_an6_s4 > best_imit_scriptfree_s51_seed4000-8000only > ppo_resid_v3_left_an9_s7 > imit4_w000_s51 > imit3_w025_s52 > imit4_w000_s52 > ppo_resid_v3_r3_s0 > ppo_resid_v3_left_an10_s8 > ppo_resid_v3_ladder_s0 > scripted (not learned) [STOCK motors force_scale 1: fast v3 swing, default elbow] > ppo_resid_v3_r2_s0 > scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] > imit2_w075_s51 > imit19_masonmapped_dart_s51 > scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] > scripted_baseline[ladder cfg: right, loft 6, default ball_x] > ppo_resid_v3_left_fast1_s10 > best_gate_flat_123mph > ppo_resid_v3_left_an5_s3 > ppo_resid_v3_left_an8_s6 > ppo_resid_v3_left_an7_s5 > imit15_dart_s51 > imit15_dart_s52 > ppo15_anneal_s91 > ppo15_soft_s122 > ppo15_bcreg_s61 > ppo15_bcreg_s62 > imit16_fs1_dart_s51 > imit14_w000_s51 > ppo15_stoch_s71 > imit13_w000_s51 > imit10_w000_s51_tr > ppo_scott > ppo_resid_v3_s0 > ppo_scott_prev_backup > ppo_scott_curr > ppo_scott_final2 > ppo_scott_baseline


## Motor strength x label (read this before any carry number)

| model | motor strength | label | det carry m (yd) | det lat std m | det club mph | smash (ball/impact club, det) | smash flag | landed (det) | qualifies (carry>=30 m, lat<=2.73, 100% contact, smash 1.30-1.49) |
|---|---|---|---|---|---|---|---|---|---|

**imit19_masonmapped_dart_s51 caution (SLOW-SWING / LOW-SPEED ARTIFACT, not better accuracy):** trainer gate JSONs (3 seeds x 100 eps, force_scale 2, results/imit_private/gate_imit19_* [gate JSON held locally, Trainer-reported; untracked at tip 2026-10-18, still in git history]) show det club 87.6 mph, carry 58.2-58.4 m, launch 13.9-14.0 deg and lateral std only 0.04-0.11 m (stoch 0.04-0.26), against imit15_dart_s53 at 120 mph, 110-113 m, 0.5-2.1 m. It hits ~27% slower, carries about half as far and its lateral spread is 10-30x smaller (0.1-0.2% of carry vs 0.5-1.9% for imit15), so the tiny spread follows from low club speed and a short, tame swing (script t_down 0.08, wrist_cock -0.6, wr_end -0.09), not from precision at a comparable drive. Do not rank it on lateral std. Its wrist/arm style claims are also covered by the lead/trail arm VOID.

| ppo20_soft_s121 | stock (force_scale 1) | [REALISM NOT EVALUATED] weakly changed from init, no demonstrated gain (PPO soft-selection from imit20_fs1_q23_dart_s51: selected checkpoint 24 != init, but RMS departure from init is only 0.00038 rad; policy-vs-script RMS 0.0815 -> 0.0374 rad, i.e. moved TOWARD the script, not away from it) | init policy's label applies | 139.8 (153) | 1.95 | 100.7 | 1.001 | WARN smash<1.30 | 100% | no |
| ppo20_klres_s111 | stock (force_scale 1) | [REALISM FAIL 0/8] = init, not learned (PPO fine-tune from imit20_fs1_q23_dart_s51: selected checkpoint = init, policy-vs-script diff unchanged) | init policy's label applies | 139.6 (153) | 2.29 | 100.7 | 1.002 | WARN smash<1.30 | 100% | no |
| imit20_fs1_q23_dart_s51 | stock (force_scale 1) | [REALISM FAIL 0/8] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 139.6 (153) | 2.29 | 100.7 | 1.002 | WARN smash<1.30 | 100% | no |
| imit16_fs1_dart_s51 | stock (force_scale 1) | [REALISM FAIL 0/8] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 72.8 (80) | 3.15 | 97.9 | 0.992 | WARN smash<1.30 | 98% | no |
| ppo_scott/ppo_scott_carry1 | stock (force_scale 1) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 0.1 (0) | 0.06 | 0.8 | 5.090 | FAIL smash>1.50 | 20% | no |
| ppo_scott_final2/ppo_scott_prev2_backup | stock (force_scale 1) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 0.1 (0) | 0.98 | 7.7 | 4.128 | FAIL smash>1.50 | 16% | no |
| ppo_scott_curr | stock (force_scale 1) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 0.0 (0) | 0.00 | 14.3 | 1.322 | ok | 0% | no |
| ppo_scott_prev_backup | stock (force_scale 1) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 0.0 (0) | 0.00 | 2.2 | 0.988 | WARN smash<1.30 | 0% | no |
| ppo_scott_baseline | stock (force_scale 1) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 0.0 (0) | 0.00 | nan | n/m | n/m smash (no ball/impact speed) | 0% | no |
| scripted (not learned) [STOCK motors force_scale 1: fast v3  | stock (force_scale 1) | [REALISM FAIL 0/8] SCRIPTED (not learned) | 74.8 (82) | 1.29 | 98.3 | 1.005 | WARN smash<1.30 | 100% | no |
| ppo_v4yaw_s42 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] HYPOTHETICAL: effectively scripted (yaw-only residual under fs2 + impact gain 1.28); not a stock-motor policy | 243.3 (266) | 1.66 | 128.3 | 1.440 | ok | 94% | no |
| ppo_v4yaw_s43 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM FAIL 1/8] HYPOTHETICAL: effectively scripted (yaw-only residual under fs2 + impact gain 1.28); not a stock-motor policy | 243.0 (266) | 1.65 | 128.3 | 1.440 | ok | 94% | no |
| best_v4yaw_s41/ppo_v4yaw_s41 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] HYPOTHETICAL: effectively scripted (yaw-only residual under fs2 + impact gain 1.28); not a stock-motor policy | 243.6 (266) | 1.67 | 128.3 | 1.440 | ok | 94% | no |
| imit3_w050_s51 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED BLEND 50% policy / 50% scripted (imitation of the script) | 119.4 (131) | 2.20 | 120.4 | 1.008 | WARN smash<1.30 | 100% | no |
| imit9_w000_s52 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 120.1 (131) | 0.99 | 120.5 | 1.007 | WARN smash<1.30 | 100% | no |
| best_imit_scriptfree_elbow48_s51/imit9_w000_s51 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 120.0 (131) | 0.96 | 120.5 | 1.007 | WARN smash<1.30 | 100% | no |
| imit14_w000_s51 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 116.1 (127) | 5.77 | 117.8 | 0.968 | WARN smash<1.30 | 96% | no |
| imit15_dart_s51 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 117.1 (128) | 1.63 | 120.3 | 1.006 | WARN smash<1.30 | 100% | no |
| imit9_w000_s53 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 115.9 (127) | 0.70 | 120.5 | 1.006 | WARN smash<1.30 | 100% | no |
| best_learned_yaw_s31/ppo_v3flt_yaw_s31 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 114.3 (125) | 1.61 | 120.3 | 1.005 | WARN smash<1.30 | 100% | no |
| best_learned_yaw_s32/ppo_v3flt_yaw_s32 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 113.9 (125) | 1.59 | 120.3 | 1.005 | WARN smash<1.30 | 100% | no |
| imit3_w075_s53 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED BLEND 25% policy / 75% scripted (imitation of the script) | 112.0 (122) | 2.27 | 120.3 | 0.996 | WARN smash<1.30 | 92% | no |
| imit15_dart_s53 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 112.9 (123) | 1.27 | 120.3 | 1.004 | WARN smash<1.30 | 100% | no |
| imit3_w075_s51 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED BLEND 25% policy / 75% scripted (imitation of the script) | 113.1 (124) | 0.73 | 120.2 | 1.003 | WARN smash<1.30 | 100% | no |
| imit15_dart_s52 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 113.6 (124) | 1.69 | 119.4 | 0.985 | WARN smash<1.30 | 98% | no |
| imit13_w000_s52 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 113.1 (124) | 1.67 | 120.3 | 1.003 | WARN smash<1.30 | 98% | no |
| ppo15_klres_s101 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM FAIL 0/8] = init, not learned (PPO fine-tune from imit15_dart_s53: selected checkpoint = init, policy-vs-script diff unchanged) | init policy's label applies | 112.9 (123) | 1.27 | 120.3 | 1.004 | WARN smash<1.30 | 100% | no |
| ppo15_anneal_s91 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] BLEND 100/0 | 106.9 (117) | 9.80 | 120.8 | 0.964 | WARN smash<1.30 | 98% | no |
| imit13_w000_s51 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 110.7 (121) | 1.63 | 118.9 | 0.965 | WARN smash<1.30 | 96% | no |
| imit2_w075_s52 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED BLEND 25% policy / 75% scripted (imitation of the script) | 117.8 (129) | 2.96 | 120.6 | 0.999 | WARN smash<1.30 | 92% | no |
| best_imit_scriptfree_s51_NOTPASS_lat3.56/imit3_w000_s51 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 109.4 (120) | 3.97 | 120.6 | 0.995 | WARN smash<1.30 | 94% | no |
| ppo15_soft_s122 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] = init, not learned (PPO fine-tune from imit15_dart_s53: selected checkpoint = init, policy-vs-script diff unchanged) | init policy's label applies | 112.9 (123) | 1.27 | 120.3 | 1.004 | WARN smash<1.30 | 100% | no |
| best_imit_w050_s52/imit3_w050_s52 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED BLEND 50% policy / 50% scripted (imitation of the script) | 107.7 (118) | 0.23 | 120.4 | 1.003 | WARN smash<1.30 | 100% | no |
| imit3_w075_s52 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED BLEND 25% policy / 75% scripted (imitation of the script) | 108.4 (119) | 1.10 | 120.3 | 0.998 | WARN smash<1.30 | 94% | no |
| imit2_w075_s53 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED BLEND 25% policy / 75% scripted (imitation of the script) | 116.9 (128) | 3.57 | 120.7 | 0.997 | WARN smash<1.30 | 92% | no |
| ppo_resid_v3_left_an3_s1 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 108.3 (118) | 6.45 | 114.5 | 0.765 | WARN smash<1.30 | 100% | no |
| imit3_w025_s51 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED BLEND 75% policy / 25% scripted (imitation of the script) | 105.1 (115) | 0.11 | 120.5 | 0.999 | WARN smash<1.30 | 100% | no |
| imit5_w000_s52 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 103.9 (114) | 4.42 | 120.9 | 0.988 | WARN smash<1.30 | 92% | no |
| ppo_v3tiny_s22 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 105.7 (116) | 4.67 | 118.4 | 0.995 | WARN smash<1.30 | 92% | no |
| ppo15_bcreg_s61 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] BLEND 100/0 | 101.2 (111) | 11.19 | 118.3 | 0.965 | WARN smash<1.30 | 96% | no |
| best_carry_analytic/ppo_resid_v3_left_an2_s0 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 112.4 (123) | 7.40 | 114.6 | 0.762 | WARN smash<1.30 | 100% | no |
| imit3_w000_s52 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 105.1 (115) | 5.53 | 119.1 | 0.993 | WARN smash<1.30 | 92% | no |
| ppo_resid_v3_left_an4_s2 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 97.2 (106) | 6.69 | 111.8 | 0.694 | WARN smash<1.30 | 100% | no |
| ppo_resid_v3_left_an1_s0 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 111.0 (121) | 6.87 | 114.7 | 0.744 | WARN smash<1.30 | 100% | no |
| ppo15_bcreg_s62 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] BLEND 100/0 | 103.6 (113) | 0.18 | 118.4 | 0.999 | WARN smash<1.30 | 100% | no |
| imit10_w000_s51_tr | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 101.5 (111) | 0.05 | 112.2 | 0.915 | WARN smash<1.30 | 94% | no |
| ppo_v3flt_all_s33 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 95.0 (104) | 5.13 | 120.3 | 0.961 | WARN smash<1.30 | 98% | no |
| ppo_v3tiny_s23 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 94.3 (103) | 2.84 | 119.0 | 0.961 | WARN smash<1.30 | 92% | no |
| imit7_w000_s51 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 89.2 (98) | 8.02 | 120.7 | 0.938 | WARN smash<1.30 | 90% | no |
| imit8_w000_s51 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 96.6 (106) | 0.25 | 121.3 | 0.948 | WARN smash<1.30 | 90% | no |
| ppo_v3tiny_s21 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 84.5 (92) | 4.43 | 119.0 | 0.941 | WARN smash<1.30 | 90% | no |
| ppo_resid_v3_left_an6_s4 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 104.4 (114) | 7.93 | 113.1 | 0.779 | WARN smash<1.30 | 98% | no |
| best_imit_scriptfree_s51_seed4000-8000only/imit5_w000_s51 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 93.9 (103) | 4.80 | 119.3 | 0.971 | WARN smash<1.30 | 94% | no |
| ppo_resid_v3_left_an9_s7 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 103.5 (113) | 7.20 | 110.5 | 0.737 | WARN smash<1.30 | 100% | no |
| imit4_w000_s51 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 93.5 (102) | 5.43 | 118.0 | 0.973 | WARN smash<1.30 | 90% | no |
| ppo15_stoch_s71 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] BLEND 100/0 | 93.7 (102) | 2.95 | 114.5 | 0.946 | WARN smash<1.30 | 96% | no |
| imit3_w025_s52 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED BLEND 75% policy / 25% scripted (imitation of the script) | 88.9 (97) | 5.31 | 123.3 | 0.911 | WARN smash<1.30 | 90% | no |
| imit4_w000_s52 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 88.4 (97) | 2.68 | 118.2 | 0.960 | WARN smash<1.30 | 90% | no |
| ppo_resid_v3_r3_s0 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 103.4 (113) | 8.91 | 108.5 | 0.754 | WARN smash<1.30 | 100% | no |
| ppo_resid_v3_left_an10_s8 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 108.7 (119) | 5.61 | 107.0 | 0.883 | WARN smash<1.30 | 94% | no |
| ppo_resid_v3_ladder_s0 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 99.6 (109) | 8.23 | 111.0 | 0.718 | WARN smash<1.30 | 100% | no |
| ppo_resid_v3_r2_s0 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 86.9 (95) | 8.45 | 107.3 | 0.673 | WARN smash<1.30 | 100% | no |
| imit2_w075_s51 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED BLEND 25% policy / 75% scripted (imitation of the script) | 49.3 (54) | 0.58 | 120.5 | 0.858 | WARN smash<1.30 | 72% | no |
| imit19_masonmapped_dart_s51 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 58.3 (64) | 0.14 | 87.6 | 0.897 | WARN smash<1.30 | 100% | no |
| ppo_resid_v3_s0 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM FAIL 1/8] LEARNED residual on scripted swing | 57.1 (62) | 31.46 | 100.5 | 0.658 | WARN smash<1.30 | 100% | no |
| ppo_resid_v3_left_fast1_s10 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 15.8 (17) | 0.02 | 122.3 | 0.893 | WARN smash<1.30 | 100% | no |
| best_gate_flat_123mph/ppo_resid_v3_left_fast2_s11 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 15.0 (16) | 0.02 | 123.6 | 0.889 | WARN smash<1.30 | 100% | no |
| ppo_resid_v3_left_an5_s3 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 10.0 (11) | 0.13 | 117.0 | 0.875 | WARN smash<1.30 | 76% | no |
| ppo_resid_v3_left_an8_s6 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 10.9 (12) | 0.10 | 118.5 | 0.851 | WARN smash<1.30 | 76% | no |
| ppo_resid_v3_left_an7_s5 | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM NOT EVALUATED] LEARNED residual on scripted swing | 9.2 (10) | 0.26 | 115.3 | 0.887 | WARN smash<1.30 | 68% | no |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, bal | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM FAIL 0/8] SCRIPTED (not learned) | 115.7 (127) | 1.70 | 120.3 | 1.005 | WARN smash<1.30 | 100% | no |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM FAIL 0/8] SCRIPTED (not learned) | 69.4 (76) | 0.01 | 120.4 | 0.987 | WARN smash<1.30 | 96% | no |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +- | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM FAIL 0/8] SCRIPTED (not learned) | 53.9 (59) | 1.98 | 107.8 | 0.904 | WARN smash<1.30 | 80% | no |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | 2x (force_scale 2, hypothetical-strength actuators) | [REALISM FAIL 0/8] SCRIPTED (not learned) | 36.7 (40) | 2.73 | 107.9 | 0.877 | WARN smash<1.30 | 56% | no |
| imit18_power_dart_s51 | power tier (hypothetical: fs 2 + wrist 120 N m + chest +-60; distances INFLATED: impact gain 1.28, smash ~1.6) | [REALISM FAIL 0/8] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 313.9 (343) | 2.18 | 132.4 | 1.603 | FAIL smash>1.50 | 100% | no |
| imit18_power_dart_s52 | power tier (hypothetical: fs 2 + wrist 120 N m + chest +-60; distances INFLATED: impact gain 1.28, smash ~1.6) | [REALISM NOT EVALUATED] SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0) | 313.9 (343) | 2.18 | 132.4 | 1.603 | FAIL smash>1.50 | 100% | no |
| ppo_v4power48_s71 | power tier (hypothetical: fs 2 + wrist 120 N m + chest +-60; distances INFLATED: impact gain 1.28, smash ~1.6) | [REALISM NOT EVALUATED] HYPOTHETICAL: effectively scripted (yaw-only residual under fs2 + impact gain 1.28); not a stock-motor policy | 311.4 (341) | 2.15 | 132.4 | 1.585 | FAIL smash>1.50 | 100% | no |
| ppo_v4power_s62 | power tier (hypothetical: fs 2 + wrist 120 N m + chest +-60; distances INFLATED: impact gain 1.28, smash ~1.6) | [REALISM NOT EVALUATED] HYPOTHETICAL: effectively scripted (yaw-only residual under fs2 + impact gain 1.28); not a stock-motor policy | 279.7 (306) | 1.86 | 132.3 | 1.500 | WARN smash>1.49 | 100% | no |
| ppo_v4power_s61 | power tier (hypothetical: fs 2 + wrist 120 N m + chest +-60; distances INFLATED: impact gain 1.28, smash ~1.6) | [REALISM NOT EVALUATED] HYPOTHETICAL: effectively scripted (yaw-only residual under fs2 + impact gain 1.28); not a stock-motor policy | 279.2 (305) | 1.82 | 132.3 | 1.499 | WARN smash>1.49 | 100% | no |

## Sim carry vs launch-monitor-model carry (MODEL-BASED; the MuJoCo carry columns elsewhere are unchanged)

MuJoCo carry = ball flown in MuJoCo with the env's own aero (Cd 0.26, Cl=min(1.7 S, 0.3)) and whatever spin the contact produced. 'Model carry' = `sim/golf_simulator.shot_from_launch` (analytic drag + Magnus, validated vs TrackMan within its stated tolerance) at the sim's own mean ball speed and launch with an ASSUMED tour backspin of 2700 rpm. 'Model carry @ smash 1.48' keeps the policy's club speed and launch but sets ball speed = 1.48 x club speed (a legal-driver smash), same 2700 rpm. Measured env backspin (6 det episodes, `results/ball_spin_measured.json`) is shown where available. Real-world reading: only the last column answers 'what would a 1.48-smash driver do at this club speed'; sim smash ~1.0 rows (v3 envs) are far SHORT of real distance, sim smash >1.5 rows (power tier, `impact_model` gain 1.28) are at/above the legal-driver limit.

| model | motor strength | club mph (peak) | sim ball mph | sim smash (impact) | launch deg | measured backspin rpm | MuJoCo carry m | model carry m (sim ball spd/launch, 2700 rpm) | model carry m @ smash 1.48 | MuJoCo / model |
|---|---|---|---|---|---|---|---|---|---|---|
| ppo20_soft_s121 | stock (force_scale 1) | 101 | 101 | 1.00 | 17.7 | n/m | 140 | 124 | 221 | 1.12 |
| ppo20_klres_s111 | stock (force_scale 1) | 101 | 101 | 1.00 | 17.7 | n/m | 140 | 124 | 221 | 1.12 |
| imit20_fs1_q23_dart_s51 | stock (force_scale 1) | 101 | 101 | 1.00 | 17.7 | n/m | 140 | 124 | 221 | 1.12 |
| imit16_fs1_dart_s51 | stock (force_scale 1) | 98 | 97 | 0.99 | 11.5 | 17 | 73 | 99 | 204 | 0.74 |
| scripted (not learned) [STOCK motors force_scale 1: fast v3  | stock (force_scale 1) | 98 | 99 | 1.01 | 12.7 | n/m | 75 | 107 | 208 | 0.70 |
| ppo_v4yaw_s42 | 2x (force_scale 2, hypothetical-strength actuators) | 128 | 185 | 1.44 | 10.9 | n/m | 243 | 276 | 284 | 0.88 |
| ppo_v4yaw_s43 | 2x (force_scale 2, hypothetical-strength actuators) | 128 | 185 | 1.44 | 10.9 | n/m | 243 | 276 | 284 | 0.88 |
| best_v4yaw_s41/ppo_v4yaw_s41 | 2x (force_scale 2, hypothetical-strength actuators) | 128 | 185 | 1.44 | 10.9 | n/m | 244 | 276 | 284 | 0.88 |
| imit3_w050_s51 | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 121 | 1.01 | 12.3 | n/m | 119 | 155 | 267 | 0.77 |
| imit9_w000_s52 | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 121 | 1.01 | 12.9 | n/m | 120 | 157 | 267 | 0.76 |
| best_imit_scriptfree_elbow48_s51/imit9_w000_s51 | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 121 | 1.01 | 12.9 | 920 | 120 | 157 | 267 | 0.76 |
| imit14_w000_s51 | 2x (force_scale 2, hypothetical-strength actuators) | 118 | 115 | 0.97 | 12.9 | n/m | 116 | 144 | 261 | 0.80 |
| imit15_dart_s51 | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 121 | 1.01 | 12.2 | n/m | 117 | 155 | 267 | 0.76 |
| imit9_w000_s53 | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 121 | 1.01 | 12.9 | n/m | 116 | 157 | 267 | 0.74 |
| best_learned_yaw_s31/ppo_v3flt_yaw_s31 | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 121 | 1.01 | 12.2 | n/m | 114 | 154 | 266 | 0.74 |
| best_learned_yaw_s32/ppo_v3flt_yaw_s32 | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 121 | 1.01 | 12.2 | n/m | 114 | 154 | 266 | 0.74 |
| imit3_w075_s53 | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 120 | 1.00 | 11.2 | n/m | 112 | 148 | 265 | 0.76 |
| imit15_dart_s53 | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 121 | 1.00 | 12.3 | n/m | 113 | 154 | 267 | 0.73 |
| imit3_w075_s51 | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 121 | 1.00 | 12.2 | n/m | 113 | 153 | 266 | 0.74 |
| imit15_dart_s52 | 2x (force_scale 2, hypothetical-strength actuators) | 119 | 119 | 0.99 | 12.3 | 362 | 114 | 149 | 264 | 0.76 |
| imit13_w000_s52 | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 121 | 1.00 | 12.0 | n/m | 113 | 153 | 266 | 0.74 |
| ppo15_klres_s101 | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 121 | 1.00 | 12.3 | n/m | 113 | 154 | 267 | 0.73 |
| ppo15_anneal_s91 | 2x (force_scale 2, hypothetical-strength actuators) | 121 | 117 | 0.96 | 11.3 | n/m | 107 | 143 | 267 | 0.75 |
| imit13_w000_s51 | 2x (force_scale 2, hypothetical-strength actuators) | 119 | 116 | 0.97 | 12.2 | n/m | 111 | 144 | 263 | 0.77 |
| imit2_w075_s52 | 2x (force_scale 2, hypothetical-strength actuators) | 121 | 120 | 1.00 | 11.3 | n/m | 118 | 150 | 266 | 0.79 |
| best_imit_scriptfree_s51_NOTPASS_lat3.56/imit3_w000_s51 | 2x (force_scale 2, hypothetical-strength actuators) | 121 | 120 | 1.00 | 11.2 | n/m | 109 | 148 | 266 | 0.74 |
| ppo15_soft_s122 | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 121 | 1.00 | 12.3 | n/m | 113 | 154 | 267 | 0.73 |
| best_imit_w050_s52/imit3_w050_s52 | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 121 | 1.00 | 12.3 | n/m | 108 | 154 | 267 | 0.70 |
| imit3_w075_s52 | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 120 | 1.00 | 11.4 | n/m | 108 | 149 | 265 | 0.73 |
| imit2_w075_s53 | 2x (force_scale 2, hypothetical-strength actuators) | 121 | 120 | 1.00 | 11.3 | n/m | 117 | 150 | 266 | 0.78 |
| ppo_resid_v3_left_an3_s1 | 2x (force_scale 2, hypothetical-strength actuators) | 115 | 88 | 0.76 | 30.6 | n/m | 108 | 108 | 235 | 1.00 |
| imit3_w025_s51 | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 120 | 1.00 | 12.2 | n/m | 105 | 153 | 267 | 0.69 |
| imit5_w000_s52 | 2x (force_scale 2, hypothetical-strength actuators) | 121 | 119 | 0.99 | 11.1 | n/m | 104 | 147 | 266 | 0.71 |
| ppo_v3tiny_s22 | 2x (force_scale 2, hypothetical-strength actuators) | 118 | 118 | 0.99 | 11.3 | n/m | 106 | 144 | 260 | 0.73 |
| ppo15_bcreg_s61 | 2x (force_scale 2, hypothetical-strength actuators) | 118 | 115 | 0.96 | 11.6 | n/m | 101 | 138 | 261 | 0.73 |
| best_carry_analytic/ppo_resid_v3_left_an2_s0 | 2x (force_scale 2, hypothetical-strength actuators) | 115 | 87 | 0.76 | 31.4 | n/m | 112 | 107 | 233 | 1.05 |
| imit3_w000_s52 | 2x (force_scale 2, hypothetical-strength actuators) | 119 | 118 | 0.99 | 11.3 | n/m | 105 | 145 | 262 | 0.73 |
| ppo_resid_v3_left_an4_s2 | 2x (force_scale 2, hypothetical-strength actuators) | 112 | 78 | 0.69 | 33.9 | n/m | 97 | 89 | 221 | 1.09 |
| ppo_resid_v3_left_an1_s0 | 2x (force_scale 2, hypothetical-strength actuators) | 115 | 85 | 0.74 | 31.7 | n/m | 111 | 104 | 232 | 1.07 |
| ppo15_bcreg_s62 | 2x (force_scale 2, hypothetical-strength actuators) | 118 | 118 | 1.00 | 11.8 | n/m | 104 | 147 | 261 | 0.70 |
| imit10_w000_s51_tr | 2x (force_scale 2, hypothetical-strength actuators) | 112 | 106 | 0.91 | 11.9 | n/m | 101 | 119 | 245 | 0.86 |
| ppo_v3flt_all_s33 | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 116 | 0.96 | 10.5 | n/m | 95 | 136 | 264 | 0.70 |
| ppo_v3tiny_s23 | 2x (force_scale 2, hypothetical-strength actuators) | 119 | 114 | 0.96 | 9.8 | n/m | 94 | 129 | 259 | 0.73 |
| imit7_w000_s51 | 2x (force_scale 2, hypothetical-strength actuators) | 121 | 113 | 0.94 | 8.4 | n/m | 89 | 119 | 261 | 0.75 |
| imit8_w000_s51 | 2x (force_scale 2, hypothetical-strength actuators) | 121 | 115 | 0.95 | 9.9 | n/m | 97 | 132 | 266 | 0.73 |
| ppo_v3tiny_s21 | 2x (force_scale 2, hypothetical-strength actuators) | 119 | 112 | 0.94 | 8.5 | n/m | 84 | 117 | 256 | 0.72 |
| ppo_resid_v3_left_an6_s4 | 2x (force_scale 2, hypothetical-strength actuators) | 113 | 88 | 0.78 | 28.7 | n/m | 104 | 109 | 237 | 0.96 |
| best_imit_scriptfree_s51_seed4000-8000only/imit5_w000_s51 | 2x (force_scale 2, hypothetical-strength actuators) | 119 | 116 | 0.97 | 9.9 | n/m | 94 | 133 | 260 | 0.70 |
| ppo_resid_v3_left_an9_s7 | 2x (force_scale 2, hypothetical-strength actuators) | 110 | 81 | 0.74 | 32.6 | n/m | 104 | 96 | 223 | 1.08 |
| imit4_w000_s51 | 2x (force_scale 2, hypothetical-strength actuators) | 118 | 115 | 0.97 | 9.7 | n/m | 94 | 130 | 257 | 0.72 |
| ppo15_stoch_s71 | 2x (force_scale 2, hypothetical-strength actuators) | 114 | 110 | 0.95 | 11.6 | n/m | 94 | 126 | 251 | 0.74 |
| imit3_w025_s52 | 2x (force_scale 2, hypothetical-strength actuators) | 123 | 112 | 0.91 | 6.8 | n/m | 89 | 107 | 263 | 0.83 |
| imit4_w000_s52 | 2x (force_scale 2, hypothetical-strength actuators) | 118 | 114 | 0.96 | 9.9 | n/m | 88 | 128 | 258 | 0.69 |
| ppo_resid_v3_r3_s0 | 2x (force_scale 2, hypothetical-strength actuators) | 109 | 82 | 0.75 | 32.8 | n/m | 103 | 97 | 219 | 1.07 |
| ppo_resid_v3_left_an10_s8 | 2x (force_scale 2, hypothetical-strength actuators) | 107 | 94 | 0.88 | 25.3 | n/m | 109 | 120 | 231 | 0.91 |
| ppo_resid_v3_ladder_s0 | 2x (force_scale 2, hypothetical-strength actuators) | 111 | 80 | 0.72 | 33.1 | n/m | 100 | 93 | 222 | 1.07 |
| ppo_resid_v3_r2_s0 | 2x (force_scale 2, hypothetical-strength actuators) | 107 | 72 | 0.67 | 36.1 | n/m | 87 | 79 | 208 | 1.10 |
| imit2_w075_s51 | 2x (force_scale 2, hypothetical-strength actuators) | 121 | 103 | 0.86 | 1.4 | n/m | 49 | 33 | 224 | 1.51 |
| imit19_masonmapped_dart_s51 | 2x (force_scale 2, hypothetical-strength actuators) | 88 | 67 | 0.90 | 13.8 | n/m | 58 | 49 | 178 | 1.18 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, bal | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 121 | 1.01 | 12.2 | n/m | 116 | 154 | 266 | 0.75 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball | 2x (force_scale 2, hypothetical-strength actuators) | 120 | 119 | 0.99 | 9.0 | n/m | 69 | 136 | 261 | 0.51 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +- | 2x (force_scale 2, hypothetical-strength actuators) | 108 | 98 | 0.90 | 11.5 | n/m | 54 | 99 | 233 | 0.54 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | 2x (force_scale 2, hypothetical-strength actuators) | 108 | 95 | 0.88 | 9.2 | n/m | 37 | 83 | 227 | 0.44 |
| imit18_power_dart_s51 | power tier (hypothetical: fs 2 + wrist 120 N m + chest +-60; distances INFLATED: impact gain 1.28, smash ~1.6) | 132 | 212 | 1.60 | 12.6 | 3088 | 314 | 316 | 294 | 0.99 |
| imit18_power_dart_s52 | power tier (hypothetical: fs 2 + wrist 120 N m + chest +-60; distances INFLATED: impact gain 1.28, smash ~1.6) | 132 | 212 | 1.60 | 12.6 | n/m | 314 | 317 | 294 | 0.99 |
| ppo_v4power48_s71 | power tier (hypothetical: fs 2 + wrist 120 N m + chest +-60; distances INFLATED: impact gain 1.28, smash ~1.6) | 132 | 210 | 1.59 | 12.6 | 3077 | 311 | 313 | 294 | 0.99 |
| ppo_v4power_s62 | power tier (hypothetical: fs 2 + wrist 120 N m + chest +-60; distances INFLATED: impact gain 1.28, smash ~1.6) | 132 | 198 | 1.50 | 11.7 | n/m | 280 | 298 | 294 | 0.94 |
| ppo_v4power_s61 | power tier (hypothetical: fs 2 + wrist 120 N m + chest +-60; distances INFLATED: impact gain 1.28, smash ~1.6) | 132 | 198 | 1.50 | 11.7 | n/m | 279 | 297 | 294 | 0.94 |

n/m = not measured. Spin for non-power rows is the contact-friction spin MuJoCo produced (tens to ~900 rpm in the v3 envs, far below a real driver's ~2700), which is why their MuJoCo carry is much shorter than the model carry at the same ball speed: low spin means little lift. Power-tier rows get ~3080 rpm from the hand-set `impact_model` (spin_k 130), and a ball speed 1.28x the contact result. The hypothetical club speed (132 mph, `t_down` 0.06 s) and smash ~1.55-1.59 are what make 300+ m, not a unit error: at the same inputs the analytic model gives ~307 m and a 1.48 smash would give ~295 m.

Peak club speed = max club_head linear speed over every physics substep of the swing, measured per episode (mean / max over episodes); mph = m/s x 2.23694; % of target = peak / 53.64 m/s (120 mph). Impact club speed = club_head linear speed at first club-ball contact; smash factor = peak ball speed / impact club speed (contact shots with club speed > 0.05 m/s, averaged).

Current env fingerprint `c66fd89099c7` (env + XML hash). 50 episodes, seeds 4000..4049. +y = left, miss = |final y| > 0.5 m. Distance = final ball x (total); carry = x at landing after flight, 0 if never landed (mean over all episodes). **CAVEAT (arm mapping): arm columns 0-3 of every DTW below compare the env's right_* chain (the TRAIL/club arm for a lefty, env/residual_golf_env.py ~l.153-157, 228) with reference cols 0-3. For native mason_v2 refs those cols are Mason's anatomical right = LEAD arm, so the arm part of dtw_mason_v2 (all11 and upper5; eval/style_match.py UPPER_COLS=slice(0,5), dispersion_report.py l.72-74) is VOID: lead/trail arm bug, see Trainer. Leg columns are not affected by the arm issue. dtw_to_reference_style_rad vs scott/rory/scheffler/average uses the same column indices (dispersion_report.py l.71); synthetic/v1 refs are stored in trail/lead roles so they are probably unaffected, UNVERIFIED.** DTW = mean joint-trajectory DTW (rad) to each reference; non-Scott columns are pure reference-style distances.

| Model(s) | Steps | Mode | Contact | Mean dist (m) | Max dist (m) | Mean carry (m) | Landed | Lateral std (m) | Left | Right | Peak ball spd (m/s) | Impact club spd (m/s) | Smash | Peak club spd mean/max (m/s) | Peak club mph mean/max | % of 120 mph mean/max | Launch elev mean deg (std) [flat?] | DTW native Mason v2, mean of 11 refs (11j / upper5) | DTW average | DTW rory | DTW scheffler | DTW scott |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ppo_scott_prev_backup | 30000 | deter | 100% | 2.76 | 2.76 | 0.000 | 0% | 0.000 | 0% | 0% | 0.94 | 0.95 | 0.99 (n=50) | 1.00 / 1.00 | 2.2 / 2.2 | 1.9% / 1.9% | 25.0 (0.0) | 2.359 / 1.786 | 1.755 | 1.812 | 1.844 | 1.781 |
| ppo_scott_prev_backup | 30000 | stoch | 52% | 4.58 | 13.62 | 0.000 | 0% | 1.244 | 20% | 16% | 2.00 | 2.96 | 0.60 (n=26) | 22.77 / 30.50 | 50.9 / 68.2 | 42.5% / 56.9% | 4.7 (6.3) FLAT | 3.414 / 2.566 | 2.963 | 2.963 | 2.974 | 2.956 |
| ppo_scott_curr | 30000 | deter | 100% | 3.01 | 3.01 | 0.000 | 0% | 0.000 | 0% | 0% | 0.77 | 0.58 | 1.32 (n=50) | 6.41 / 6.41 | 14.3 / 14.3 | 12.0% / 12.0% | 11.3 (0.0) | 3.494 / 2.771 | 2.768 | 2.778 | 2.757 | 2.792 |
| ppo_scott_curr | 30000 | stoch | 36% | 4.47 | 12.37 | 0.024 | 4% | 2.512 | 24% | 8% | 2.71 | 1.92 | 1.03 (n=18) | 23.27 / 33.50 | 52.1 / 74.9 | 43.4% / 62.5% | 10.1 (12.7) | 3.377 / 2.544 | 2.896 | 2.895 | 2.898 | 2.891 |
| ppo_scott_baseline | 30000 | deter | 0% | 0.30 | 0.30 | 0.000 | 0% | 0.000 | 0% | 0% | 0.71 | nan | nan (n=0) | n/a | n/a | n/a (50 sim-unstable eps excluded; raw max 7.07e+05 m/s) | nan (nan) | 4.642 / 3.957 | 4.128 | 4.138 | 4.257 | 4.009 |
| ppo_scott_baseline | 30000 | stoch | 0% | 0.94 | 7.90 | 0.000 | 0% | 0.384 | 0% | 8% | 1.04 | nan | nan (n=0) | n/a | n/a | n/a (50 sim-unstable eps excluded; raw max 3.55e+05 m/s) | nan (nan) | 8.685 / 7.297 | 8.287 | 8.309 | 8.364 | 8.180 |
| ppo_scott<br>ppo_scott_carry1 | 100000 | deter | 98% | 0.47 | 0.59 | 0.102 | 20% | 0.062 | 0% | 0% | 0.50 | 0.10 | 1.51 (n=27) | 0.35 / 0.58 | 0.8 / 1.3 | 0.6% / 1.1% | 48.4 (24.9) | 2.259 / 1.572 | 1.278 | 1.289 | 1.264 | 1.302 |
| ppo_scott<br>ppo_scott_carry1 | 100000 | stoch | 68% | 0.88 | 6.41 | 0.413 | 32% | 0.297 | 2% | 2% | 2.49 | 1.47 | 1.88 (n=15) | 26.48 / 57.32 | 59.2 / 128.2 | 49.4% / 106.9% | 36.4 (28.8) | 3.165 / 2.390 | 2.686 | 2.688 | 2.702 | 2.675 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | 60000 | deter | 48% | 1.80 | 9.80 | 0.091 | 16% | 0.980 | 14% | 10% | 0.69 | 0.17 | 15.91 (n=5) | 3.45 / 12.64 | 7.7 / 28.3 | 6.4% / 23.6% | 34.2 (34.5) | 3.019 / 2.521 | 2.292 | 2.300 | 2.303 | 2.297 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | 60000 | stoch | 46% | 2.69 | 11.55 | 0.142 | 28% | 3.420 | 18% | 16% | 2.52 | 0.74 | 1.66 (n=4) | 23.03 / 35.61 | 51.5 / 79.7 | 42.9% / 66.4% | 36.8 (28.5) | 3.374 / 2.493 | 2.867 | 2.863 | 2.882 | 2.859 |
| ppo_resid_v3_s0 | 60000 | deter | 100% | 57.12 | 69.85 | 57.123 | 100% | 31.455 | 30% | 70% | 29.55 | 44.91 | 0.66 (n=50) | 44.92 / 45.52 | 100.5 / 101.8 | 83.7% / 84.9% | 49.6 (6.0) | 1.917 / 1.294 | 0.922 | 0.912 | 0.931 | 0.912 |
| ppo_resid_v3_s0 | 60000 | stoch | 64% | 38.16 | 289.76 | 20.830 | 52% | 17.980 | 28% | 22% | 18.17 | 49.58 | 0.57 (n=32) | 49.73 / 63.08 | 111.2 / 141.1 | 92.7% / 117.6% | 16.6 (35.1) | 2.347 / 1.877 | 1.304 | 1.302 | 1.312 | 1.297 |
| ppo_resid_v3_r2_s0 | 60000 | deter | 100% | 86.95 | 105.44 | 86.947 | 100% | 8.446 | 42% | 58% | 32.29 | 47.96 | 0.67 (n=50) | 47.96 / 48.14 | 107.3 / 107.7 | 89.4% / 89.7% | 36.1 (3.6) | 1.925 / 1.334 | 0.954 | 0.945 | 0.961 | 0.946 |
| ppo_resid_v3_r2_s0 | 60000 | stoch | 100% | 110.46 | 332.87 | 60.467 | 84% | 13.191 | 46% | 36% | 35.48 | 47.89 | 0.74 (n=50) | 47.89 / 50.96 | 107.1 / 114.0 | 89.3% / 95.0% | 26.3 (19.6) | 2.005 / 1.434 | 1.004 | 0.995 | 1.009 | 0.997 |
| ppo_resid_v3_r3_s0 | 100000 | deter | 100% | 103.44 | 152.86 | 103.438 | 100% | 8.908 | 46% | 52% | 36.56 | 48.51 | 0.75 (n=50) | 48.51 / 48.89 | 108.5 / 109.4 | 90.4% / 91.1% | 32.8 (5.1) | 1.912 / 1.296 | 0.928 | 0.918 | 0.937 | 0.918 |
| ppo_resid_v3_r3_s0 | 100000 | stoch | 100% | 123.91 | 343.53 | 66.750 | 82% | 10.718 | 38% | 46% | 36.22 | 48.77 | 0.74 (n=50) | 48.77 / 52.36 | 109.1 / 117.1 | 90.9% / 97.6% | 26.7 (17.4) | 1.963 / 1.369 | 0.972 | 0.963 | 0.980 | 0.964 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | 0 | deter | 100% | 177.22 | 331.62 | 36.672 | 56% | 2.733 | 8% | 20% | 42.31 | 48.23 | 0.88 (n=50) | 48.23 / 48.33 | 107.9 / 108.1 | 89.9% / 90.1% | 9.2 (13.2) FLAT | 2.045 / 1.482 | 1.029 | 1.021 | 1.036 | 1.021 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | 0 | stoch | 100% | 177.22 | 331.62 | 36.672 | 56% | 2.733 | 8% | 20% | 42.31 | 48.23 | 0.88 (n=50) | 48.23 / 48.33 | 107.9 / 108.1 | 89.9% / 90.1% | 9.2 (13.2) FLAT | 2.045 / 1.482 | 1.029 | 1.021 | 1.036 | 1.021 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | 0 | deter | 100% | 118.44 | 326.09 | 53.934 | 80% | 1.985 | 4% | 10% | 43.59 | 48.21 | 0.90 (n=50) | 48.21 / 48.27 | 107.8 / 108.0 | 89.9% / 90.0% | 11.5 (11.6) | 2.177 / 1.659 | 1.196 | 1.195 | 1.203 | 1.193 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | 0 | stoch | 100% | 118.44 | 326.09 | 53.934 | 80% | 1.985 | 4% | 10% | 43.59 | 48.21 | 0.90 (n=50) | 48.21 / 48.27 | 107.8 / 108.0 | 89.9% / 90.0% | 11.5 (11.6) | 2.177 / 1.659 | 1.196 | 1.195 | 1.203 | 1.193 |
| ppo_resid_v3_ladder_s0 | 150000 | deter | 100% | 99.64 | 134.14 | 99.639 | 100% | 8.232 | 46% | 50% | 35.67 | 49.64 | 0.72 (n=50) | 49.64 / 49.88 | 111.0 / 111.6 | 92.5% / 93.0% | 33.1 (4.4) | 1.905 / 1.299 | 0.946 | 0.936 | 0.953 | 0.936 |
| ppo_resid_v3_ladder_s0 | 150000 | stoch | 100% | 94.48 | 339.80 | 69.082 | 92% | 14.276 | 44% | 36% | 36.77 | 49.72 | 0.74 (n=50) | 49.72 / 54.95 | 111.2 / 122.9 | 92.7% / 102.4% | 25.4 (19.2) | 2.044 / 1.475 | 1.049 | 1.041 | 1.055 | 1.041 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | 0 | deter | 100% | 80.70 | 289.84 | 69.405 | 96% | 0.013 | 0% | 0% | 53.10 | 53.80 | 0.99 (n=50) | 53.80 / 53.94 | 120.4 / 120.7 | 100.3% / 100.6% | 9.0 (2.9) | 2.242 / 1.778 | 1.308 | 1.309 | 1.306 | 1.315 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | 0 | stoch | 100% | 80.70 | 289.84 | 69.405 | 96% | 0.013 | 0% | 0% | 53.10 | 53.80 | 0.99 (n=50) | 53.80 / 53.94 | 120.4 / 120.7 | 100.3% / 100.6% | 9.0 (2.9) | 2.242 / 1.778 | 1.308 | 1.309 | 1.306 | 1.315 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | 0 | deter | 100% | 115.71 | 186.55 | 115.710 | 100% | 1.699 | 2% | 12% | 54.09 | 53.80 | 1.01 (n=50) | 53.80 / 53.90 | 120.3 / 120.6 | 100.3% / 100.5% | 12.2 (1.4) | 2.060 / 1.524 | 1.106 | 1.101 | 1.110 | 1.105 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | 0 | stoch | 100% | 115.71 | 186.55 | 115.710 | 100% | 1.699 | 2% | 12% | 54.09 | 53.80 | 1.01 (n=50) | 53.80 / 53.90 | 120.3 / 120.6 | 100.3% / 100.5% | 12.2 (1.4) | 2.060 / 1.524 | 1.106 | 1.101 | 1.110 | 1.105 |
| scripted (not learned) [STOCK motors force_scale 1: fast v3 swing, default elbow] | 0 | deter | 100% | 74.83 | 87.24 | 74.830 | 100% | 1.294 | 6% | 2% | 44.17 | 43.94 | 1.01 (n=50) | 43.94 / 44.10 | 98.3 / 98.6 | 81.9% / 82.2% | 12.7 (1.6) | 2.187 / 1.732 | 1.245 | 1.247 | 1.242 | 1.255 |
| scripted (not learned) [STOCK motors force_scale 1: fast v3 swing, default elbow] | 0 | stoch | 100% | 74.83 | 87.24 | 74.830 | 100% | 1.294 | 6% | 2% | 44.17 | 43.94 | 1.01 (n=50) | 43.94 / 44.10 | 98.3 / 98.6 | 81.9% / 82.2% | 12.7 (1.6) | 2.187 / 1.732 | 1.245 | 1.247 | 1.242 | 1.255 |
| ppo_resid_v3_left_an1_s0 | 150000 | deter | 100% | 111.02 | 159.40 | 111.023 | 100% | 6.874 | 54% | 42% | 38.16 | 51.30 | 0.74 (n=50) | 51.30 / 51.67 | 114.7 / 115.6 | 95.6% / 96.3% | 31.7 (3.6) | 1.897 / 1.279 | 0.943 | 0.933 | 0.951 | 0.932 |
| ppo_resid_v3_left_an1_s0 | 150000 | stoch | 100% | 105.04 | 344.00 | 84.609 | 94% | 9.149 | 46% | 44% | 37.21 | 50.86 | 0.73 (n=50) | 50.86 / 53.93 | 113.8 / 120.6 | 94.8% / 100.5% | 29.9 (15.5) | 1.965 / 1.370 | 0.994 | 0.985 | 1.001 | 0.984 |
| ppo_resid_v3_left_an3_s1 | 150000 | deter | 100% | 108.33 | 162.26 | 108.329 | 100% | 6.447 | 56% | 36% | 39.17 | 51.20 | 0.76 (n=50) | 51.20 / 51.45 | 114.5 / 115.1 | 95.5% / 95.9% | 30.6 (7.5) | 1.931 / 1.322 | 0.959 | 0.949 | 0.967 | 0.949 |
| ppo_resid_v3_left_an3_s1 | 150000 | stoch | 100% | 110.89 | 334.78 | 104.193 | 98% | 8.116 | 56% | 34% | 38.32 | 50.84 | 0.75 (n=50) | 50.84 / 52.42 | 113.7 / 117.3 | 94.8% / 97.7% | 30.4 (8.1) | 1.922 / 1.311 | 0.950 | 0.939 | 0.957 | 0.939 |
| ppo_resid_v3_left_an4_s2 | 150000 | deter | 100% | 97.16 | 162.98 | 97.155 | 100% | 6.691 | 54% | 46% | 34.72 | 50.00 | 0.69 (n=50) | 50.00 / 50.31 | 111.8 / 112.5 | 93.2% / 93.8% | 33.9 (4.0) | 1.914 / 1.303 | 0.944 | 0.934 | 0.951 | 0.935 |
| ppo_resid_v3_left_an4_s2 | 150000 | stoch | 100% | 98.78 | 170.36 | 98.779 | 100% | 9.355 | 42% | 52% | 35.96 | 49.82 | 0.72 (n=50) | 49.82 / 52.13 | 111.4 / 116.6 | 92.9% / 97.2% | 33.9 (6.6) | 1.923 / 1.314 | 0.949 | 0.938 | 0.956 | 0.939 |
| ppo_resid_v3_left_an5_s3 | 150000 | deter | 100% | 94.87 | 357.37 | 9.995 | 76% | 0.135 | 0% | 0% | 45.74 | 52.28 | 0.87 (n=50) | 52.28 / 52.58 | 117.0 / 117.6 | 97.5% / 98.0% | -3.8 (2.2) FLAT | 2.435 / 1.963 | 1.340 | 1.342 | 1.340 | 1.339 |
| ppo_resid_v3_left_an5_s3 | 150000 | stoch | 100% | 141.01 | 359.56 | 14.418 | 64% | 1.377 | 20% | 8% | 46.36 | 52.13 | 0.89 (n=50) | 52.13 / 53.58 | 116.6 / 119.9 | 97.2% / 99.9% | -1.1 (8.6) FLAT | 2.292 / 1.780 | 1.225 | 1.223 | 1.229 | 1.220 |
| best_carry_analytic<br>ppo_resid_v3_left_an2_s0 | 150000 | deter | 100% | 112.35 | 160.27 | 112.352 | 100% | 7.400 | 46% | 48% | 39.07 | 51.25 | 0.76 (n=50) | 51.25 / 51.56 | 114.6 / 115.3 | 95.5% / 96.1% | 31.4 (4.2) | 1.891 / 1.267 | 0.936 | 0.925 | 0.944 | 0.925 |
| best_carry_analytic<br>ppo_resid_v3_left_an2_s0 | 150000 | stoch | 100% | 115.29 | 353.00 | 88.093 | 92% | 7.283 | 52% | 36% | 37.82 | 51.15 | 0.74 (n=50) | 51.15 / 52.73 | 114.4 / 117.9 | 95.4% / 98.3% | 29.1 (13.1) | 1.945 / 1.341 | 0.973 | 0.963 | 0.981 | 0.963 |
| ppo_resid_v3_left_an6_s4 | 150000 | deter | 100% | 111.07 | 335.10 | 104.365 | 98% | 7.928 | 52% | 38% | 39.37 | 50.56 | 0.78 (n=50) | 50.56 / 51.37 | 113.1 / 114.9 | 94.3% / 95.8% | 28.7 (8.2) | 1.933 / 1.328 | 0.967 | 0.957 | 0.975 | 0.957 |
| ppo_resid_v3_left_an6_s4 | 150000 | stoch | 100% | 148.38 | 348.47 | 81.852 | 80% | 6.944 | 48% | 36% | 39.94 | 50.84 | 0.79 (n=50) | 50.84 / 52.90 | 113.7 / 118.3 | 94.8% / 98.6% | 23.0 (13.9) | 1.920 / 1.309 | 0.947 | 0.937 | 0.955 | 0.937 |
| ppo_resid_v3_left_an8_s6 | 120000 | deter | 100% | 96.53 | 359.26 | 10.852 | 76% | 0.100 | 0% | 0% | 45.10 | 52.98 | 0.85 (n=50) | 52.98 / 53.29 | 118.5 / 119.2 | 98.8% / 99.4% | -5.1 (2.8) FLAT | 2.444 / 1.973 | 1.350 | 1.353 | 1.354 | 1.348 |
| ppo_resid_v3_left_an8_s6 | 120000 | stoch | 100% | 75.10 | 360.91 | 11.518 | 82% | 0.378 | 8% | 2% | 44.62 | 52.73 | 0.85 (n=50) | 52.73 / 54.21 | 118.0 / 121.3 | 98.3% / 101.1% | -4.9 (2.4) FLAT | 2.495 / 2.042 | 1.394 | 1.395 | 1.397 | 1.392 |
| ppo_resid_v3_left_an7_s5 | 120000 | deter | 100% | 120.72 | 355.37 | 9.175 | 68% | 0.264 | 0% | 32% | 45.74 | 51.55 | 0.89 (n=50) | 51.55 / 52.24 | 115.3 / 116.9 | 96.1% / 97.4% | -3.4 (2.1) FLAT | 2.376 / 1.897 | 1.283 | 1.281 | 1.288 | 1.278 |
| ppo_resid_v3_left_an7_s5 | 120000 | stoch | 100% | 147.65 | 357.35 | 7.852 | 60% | 0.478 | 0% | 24% | 45.67 | 51.67 | 0.88 (n=50) | 51.67 / 53.23 | 115.6 / 119.1 | 96.3% / 99.2% | -3.2 (2.7) FLAT | 2.309 / 1.799 | 1.246 | 1.243 | 1.249 | 1.240 |
| ppo_resid_v3_left_an9_s7 | 120000 | deter | 100% | 103.50 | 143.64 | 103.502 | 100% | 7.195 | 58% | 42% | 36.38 | 49.39 | 0.74 (n=50) | 49.39 / 49.97 | 110.5 / 111.8 | 92.1% / 93.2% | 32.6 (4.1) | 1.909 / 1.301 | 0.943 | 0.933 | 0.952 | 0.932 |
| ppo_resid_v3_left_an9_s7 | 120000 | stoch | 100% | 126.58 | 337.38 | 81.941 | 86% | 7.357 | 50% | 38% | 37.48 | 49.42 | 0.76 (n=50) | 49.42 / 52.31 | 110.6 / 117.0 | 92.1% / 97.5% | 28.4 (14.4) | 1.925 / 1.320 | 0.948 | 0.937 | 0.956 | 0.937 |
| ppo_resid_v3_left_an10_s8 | 120000 | deter | 100% | 127.55 | 324.46 | 108.723 | 94% | 5.612 | 52% | 30% | 42.23 | 47.83 | 0.88 (n=50) | 47.83 / 48.45 | 107.0 / 108.4 | 89.2% / 90.3% | 25.3 (9.0) | 1.919 / 1.316 | 0.949 | 0.939 | 0.955 | 0.940 |
| ppo_resid_v3_left_an10_s8 | 120000 | stoch | 100% | 129.20 | 338.04 | 61.034 | 78% | 5.203 | 42% | 24% | 39.74 | 48.12 | 0.83 (n=50) | 48.12 / 50.04 | 107.6 / 111.9 | 89.7% / 93.3% | 16.9 (16.5) | 2.051 / 1.489 | 1.040 | 1.032 | 1.045 | 1.033 |
| ppo_resid_v3_left_fast1_s10 | 100000 | deter | 100% | 15.78 | 23.95 | 15.779 | 100% | 0.021 | 0% | 0% | 48.79 | 54.65 | 0.89 (n=50) | 54.65 / 54.73 | 122.3 / 122.4 | 101.9% / 102.0% | -5.1 (1.6) FLAT | 2.669 / 2.273 | 1.503 | 1.511 | 1.510 | 1.506 |
| ppo_resid_v3_left_fast1_s10 | 100000 | stoch | 100% | 15.05 | 21.00 | 15.048 | 100% | 0.288 | 2% | 0% | 47.90 | 54.65 | 0.88 (n=50) | 54.65 / 55.18 | 122.2 / 123.4 | 101.9% / 102.9% | -5.0 (1.3) FLAT | 2.674 / 2.279 | 1.502 | 1.507 | 1.507 | 1.503 |
| best_gate_flat_123mph<br>ppo_resid_v3_left_fast2_s11 | 100000 | deter | 100% | 15.02 | 22.08 | 15.015 | 100% | 0.017 | 0% | 0% | 49.14 | 55.24 | 0.89 (n=50) | 55.24 / 55.32 | 123.6 / 123.8 | 103.0% / 103.1% | -5.4 (1.4) FLAT | 2.665 / 2.265 | 1.506 | 1.507 | 1.505 | 1.508 |
| best_gate_flat_123mph<br>ppo_resid_v3_left_fast2_s11 | 100000 | stoch | 100% | 28.64 | 358.99 | 15.047 | 96% | 0.089 | 2% | 0% | 48.15 | 55.21 | 0.87 (n=50) | 55.21 / 55.72 | 123.5 / 124.6 | 102.9% / 103.9% | -5.0 (1.5) FLAT | 2.626 / 2.212 | 1.479 | 1.484 | 1.484 | 1.480 |
| ppo_v3tiny_s22 | 60000 | deter | 100% | 127.22 | 278.96 | 105.669 | 92% | 4.668 | 10% | 20% | 52.62 | 52.91 | 0.99 (n=50) | 52.91 / 53.03 | 118.4 / 118.6 | 98.6% / 98.9% | 11.3 (3.6) | 2.039 / 1.497 | 1.079 | 1.074 | 1.083 | 1.077 |
| ppo_v3tiny_s22 | 60000 | stoch | 100% | 121.65 | 275.49 | 100.002 | 92% | 8.377 | 10% | 18% | 51.61 | 53.02 | 0.97 (n=50) | 53.02 / 53.90 | 118.6 / 120.6 | 98.9% / 100.5% | 9.8 (6.1) | 2.072 / 1.536 | 1.106 | 1.102 | 1.111 | 1.104 |
| ppo_v3tiny_s23 | 60000 | deter | 100% | 116.38 | 281.28 | 94.311 | 92% | 2.836 | 6% | 10% | 51.11 | 53.19 | 0.96 (n=50) | 53.19 / 53.75 | 119.0 / 120.2 | 99.2% / 100.2% | 9.8 (6.4) | 2.088 / 1.560 | 1.121 | 1.117 | 1.125 | 1.121 |
| ppo_v3tiny_s23 | 60000 | stoch | 100% | 126.44 | 276.12 | 99.069 | 90% | 9.186 | 12% | 8% | 52.56 | 53.23 | 0.99 (n=50) | 53.23 / 54.03 | 119.1 / 120.9 | 99.2% / 100.7% | 10.4 (4.4) | 2.052 / 1.513 | 1.091 | 1.086 | 1.094 | 1.089 |
| ppo_v3tiny_s21 | 60000 | deter | 100% | 111.78 | 276.21 | 84.489 | 90% | 4.427 | 4% | 6% | 50.02 | 53.18 | 0.94 (n=50) | 53.18 / 53.31 | 119.0 / 119.3 | 99.1% / 99.4% | 8.5 (7.3) | 2.119 / 1.602 | 1.145 | 1.142 | 1.149 | 1.144 |
| ppo_v3tiny_s21 | 60000 | stoch | 100% | 118.70 | 271.57 | 102.636 | 94% | 8.955 | 12% | 10% | 52.11 | 53.16 | 0.98 (n=50) | 53.16 / 54.13 | 118.9 / 121.1 | 99.1% / 100.9% | 10.5 (5.5) | 2.069 / 1.536 | 1.103 | 1.099 | 1.107 | 1.102 |
| ppo_v3flt_all_s33 | 30000 | deter | 100% | 100.70 | 284.74 | 95.003 | 98% | 5.132 | 2% | 0% | 51.66 | 53.78 | 0.96 (n=50) | 53.78 / 53.88 | 120.3 / 120.5 | 100.3% / 100.4% | 10.5 (6.0) | 2.126 / 1.614 | 1.165 | 1.162 | 1.167 | 1.165 |
| ppo_v3flt_all_s33 | 30000 | stoch | 100% | 110.41 | 281.27 | 99.163 | 96% | 9.747 | 8% | 6% | 51.24 | 53.80 | 0.95 (n=50) | 53.80 / 53.92 | 120.3 / 120.6 | 100.3% / 100.5% | 9.2 (7.2) | 2.108 / 1.583 | 1.138 | 1.134 | 1.142 | 1.137 |
| best_learned_yaw_s32<br>ppo_v3flt_yaw_s32 | 30000 | deter | 100% | 113.90 | 186.22 | 113.904 | 100% | 1.586 | 4% | 12% | 54.07 | 53.80 | 1.01 (n=50) | 53.80 / 53.90 | 120.3 / 120.6 | 100.3% / 100.5% | 12.2 (1.4) | 2.068 / 1.536 | 1.115 | 1.110 | 1.118 | 1.114 |
| best_learned_yaw_s32<br>ppo_v3flt_yaw_s32 | 30000 | stoch | 100% | 113.98 | 186.20 | 113.978 | 100% | 1.582 | 4% | 12% | 54.06 | 53.80 | 1.00 (n=50) | 53.80 / 53.90 | 120.3 / 120.6 | 100.3% / 100.5% | 12.2 (1.4) | 2.066 / 1.532 | 1.111 | 1.106 | 1.114 | 1.110 |
| best_learned_yaw_s31<br>ppo_v3flt_yaw_s31 | 30000 | deter | 100% | 114.25 | 186.20 | 114.250 | 100% | 1.614 | 2% | 12% | 54.07 | 53.80 | 1.01 (n=50) | 53.80 / 53.90 | 120.3 / 120.6 | 100.3% / 100.5% | 12.2 (1.4) | 2.066 / 1.533 | 1.112 | 1.107 | 1.115 | 1.110 |
| best_learned_yaw_s31<br>ppo_v3flt_yaw_s31 | 30000 | stoch | 100% | 114.78 | 186.14 | 114.779 | 100% | 1.935 | 4% | 12% | 54.07 | 53.80 | 1.01 (n=50) | 53.80 / 53.90 | 120.3 / 120.6 | 100.3% / 100.5% | 12.2 (1.4) | 2.063 / 1.529 | 1.109 | 1.104 | 1.112 | 1.107 |
| ppo_v4yaw_s43 | 30000 | deter | 100% | 261.13 | 309.87 | 243.011 | 94% | 1.648 | 42% | 38% | 82.60 | 57.36 | 1.44 (n=50) | 57.36 / 57.52 | 128.3 / 128.7 | 106.9% / 107.2% | 10.9 (2.0) | 1.847 / 1.190 | 0.910 | 0.898 | 0.921 | 0.896 |
| ppo_v4yaw_s43 | 30000 | stoch | 100% | 262.39 | 309.87 | 244.277 | 94% | 1.739 | 44% | 40% | 82.70 | 57.36 | 1.44 (n=50) | 57.36 / 57.52 | 128.3 / 128.7 | 106.9% / 107.2% | 10.9 (2.0) | 1.843 / 1.184 | 0.906 | 0.894 | 0.917 | 0.891 |
| ppo_v4yaw_s42 | 30000 | deter | 100% | 261.40 | 309.50 | 243.290 | 94% | 1.660 | 42% | 40% | 82.61 | 57.36 | 1.44 (n=50) | 57.36 / 57.52 | 128.3 / 128.7 | 106.9% / 107.2% | 10.9 (2.0) | 1.846 / 1.189 | 0.909 | 0.897 | 0.920 | 0.895 |
| ppo_v4yaw_s42 | 30000 | stoch | 100% | 262.03 | 309.50 | 249.951 | 96% | 1.654 | 44% | 40% | 82.55 | 57.36 | 1.44 (n=50) | 57.36 / 57.52 | 128.3 / 128.7 | 106.9% / 107.2% | 10.9 (2.0) | 1.843 / 1.184 | 0.906 | 0.894 | 0.917 | 0.892 |
| best_v4yaw_s41<br>ppo_v4yaw_s41 | 30000 | deter | 100% | 261.71 | 309.87 | 243.591 | 94% | 1.670 | 52% | 36% | 82.60 | 57.36 | 1.44 (n=50) | 57.36 / 57.52 | 128.3 / 128.7 | 106.9% / 107.2% | 10.9 (2.0) | 1.845 / 1.187 | 0.909 | 0.897 | 0.920 | 0.894 |
| best_v4yaw_s41<br>ppo_v4yaw_s41 | 30000 | stoch | 100% | 261.52 | 309.88 | 243.409 | 94% | 1.692 | 50% | 36% | 82.49 | 57.36 | 1.44 (n=50) | 57.36 / 57.52 | 128.3 / 128.7 | 106.9% / 107.2% | 10.9 (2.0) | 1.845 / 1.187 | 0.908 | 0.896 | 0.919 | 0.893 |
| imit2_w075_s51 | 15000 | deter | 100% | 126.57 | 286.60 | 49.278 | 72% | 0.582 | 4% | 2% | 46.23 | 53.88 | 0.86 (n=50) | 53.88 / 53.98 | 120.5 / 120.7 | 100.4% / 100.6% | 1.4 (9.5) FLAT | 2.161 / 1.642 | 1.168 | 1.166 | 1.175 | 1.166 |
| imit2_w075_s51 | 15000 | stoch | 100% | 124.70 | 281.63 | 80.579 | 84% | 4.286 | 8% | 6% | 50.01 | 53.87 | 0.93 (n=50) | 53.87 / 54.12 | 120.5 / 121.1 | 100.4% / 100.9% | 6.6 (8.5) | 2.104 / 1.574 | 1.131 | 1.127 | 1.136 | 1.128 |
| imit2_w075_s52 | 15000 | deter | 100% | 139.93 | 283.49 | 117.839 | 92% | 2.963 | 8% | 26% | 53.82 | 53.89 | 1.00 (n=50) | 53.89 / 54.01 | 120.6 / 120.8 | 100.5% / 100.7% | 11.3 (3.7) | 2.007 / 1.446 | 1.051 | 1.045 | 1.056 | 1.047 |
| imit2_w075_s52 | 15000 | stoch | 100% | 131.14 | 290.92 | 103.222 | 90% | 2.728 | 2% | 22% | 52.46 | 53.88 | 0.97 (n=50) | 53.88 / 54.10 | 120.5 / 121.0 | 100.5% / 100.9% | 9.7 (6.2) | 2.047 / 1.498 | 1.086 | 1.081 | 1.091 | 1.083 |
| imit2_w075_s53 | 15000 | deter | 100% | 139.24 | 292.69 | 116.877 | 92% | 3.569 | 6% | 24% | 53.84 | 53.98 | 1.00 (n=50) | 53.98 / 54.09 | 120.7 / 121.0 | 100.6% / 100.8% | 11.3 (3.7) | 2.010 / 1.449 | 1.055 | 1.049 | 1.060 | 1.051 |
| imit2_w075_s53 | 15000 | stoch | 100% | 112.71 | 279.75 | 96.121 | 94% | 1.007 | 2% | 10% | 51.41 | 53.99 | 0.95 (n=50) | 53.99 / 54.26 | 120.8 / 121.4 | 100.7% / 101.2% | 8.9 (7.7) | 2.106 / 1.581 | 1.141 | 1.137 | 1.144 | 1.139 |
| imit3_w075_s51 | 8000 | deter | 100% | 113.09 | 182.73 | 113.093 | 100% | 0.733 | 2% | 10% | 53.91 | 53.73 | 1.00 (n=50) | 53.73 / 53.83 | 120.2 / 120.4 | 100.2% / 100.3% | 12.2 (1.4) | 2.062 / 1.527 | 1.110 | 1.106 | 1.114 | 1.109 |
| imit3_w075_s51 | 8000 | stoch | 100% | 112.42 | 182.78 | 112.425 | 100% | 0.670 | 2% | 8% | 53.90 | 53.73 | 1.00 (n=50) | 53.73 / 53.82 | 120.2 / 120.4 | 100.2% / 100.3% | 12.2 (1.4) | 2.066 / 1.533 | 1.115 | 1.110 | 1.118 | 1.114 |
| imit3_w075_s52 | 8000 | deter | 100% | 124.97 | 277.56 | 108.424 | 94% | 1.097 | 6% | 12% | 53.63 | 53.76 | 1.00 (n=50) | 53.76 / 53.90 | 120.3 / 120.6 | 100.2% / 100.5% | 11.4 (3.3) | 2.046 / 1.503 | 1.091 | 1.086 | 1.095 | 1.089 |
| imit3_w075_s52 | 8000 | stoch | 100% | 124.70 | 276.34 | 108.181 | 94% | 1.365 | 4% | 10% | 53.64 | 53.76 | 1.00 (n=50) | 53.76 / 53.91 | 120.3 / 120.6 | 100.2% / 100.5% | 11.4 (3.3) | 2.049 / 1.508 | 1.095 | 1.090 | 1.099 | 1.093 |
| imit3_w075_s53 | 8000 | deter | 100% | 134.13 | 281.13 | 111.950 | 92% | 2.267 | 6% | 16% | 53.60 | 53.80 | 1.00 (n=50) | 53.80 / 53.91 | 120.3 / 120.6 | 100.3% / 100.5% | 11.2 (3.7) | 2.023 / 1.469 | 1.065 | 1.059 | 1.070 | 1.062 |
| imit3_w075_s53 | 8000 | stoch | 100% | 131.49 | 286.87 | 114.637 | 94% | 2.248 | 6% | 16% | 53.77 | 53.80 | 1.00 (n=50) | 53.80 / 53.91 | 120.3 / 120.6 | 100.3% / 100.5% | 11.5 (3.3) | 2.026 / 1.474 | 1.068 | 1.062 | 1.072 | 1.065 |
| imit3_w050_s51 | 8000 | deter | 100% | 119.39 | 190.07 | 119.392 | 100% | 2.203 | 6% | 18% | 54.22 | 53.81 | 1.01 (n=50) | 53.81 / 53.92 | 120.4 / 120.6 | 100.3% / 100.5% | 12.3 (1.4) | 2.052 / 1.512 | 1.100 | 1.095 | 1.104 | 1.099 |
| imit3_w050_s51 | 8000 | stoch | 100% | 120.45 | 186.89 | 120.450 | 100% | 2.154 | 4% | 16% | 54.22 | 53.81 | 1.01 (n=50) | 53.81 / 53.92 | 120.4 / 120.6 | 100.3% / 100.5% | 12.2 (1.4) | 2.045 / 1.501 | 1.090 | 1.085 | 1.094 | 1.088 |
| best_imit_w050_s52<br>imit3_w050_s52 | 8000 | deter | 100% | 107.74 | 162.79 | 107.739 | 100% | 0.232 | 0% | 4% | 53.98 | 53.84 | 1.00 (n=50) | 53.84 / 53.94 | 120.4 / 120.7 | 100.4% / 100.6% | 12.3 (1.3) | 2.086 / 1.560 | 1.133 | 1.129 | 1.136 | 1.133 |
| best_imit_w050_s52<br>imit3_w050_s52 | 8000 | stoch | 100% | 109.70 | 171.77 | 109.699 | 100% | 0.294 | 0% | 4% | 53.99 | 53.84 | 1.00 (n=50) | 53.84 / 53.95 | 120.4 / 120.7 | 100.4% / 100.6% | 12.3 (1.3) | 2.075 / 1.544 | 1.123 | 1.119 | 1.126 | 1.123 |
| imit3_w025_s51 | 8000 | deter | 100% | 105.11 | 166.65 | 105.109 | 100% | 0.108 | 0% | 2% | 53.81 | 53.86 | 1.00 (n=50) | 53.86 / 53.99 | 120.5 / 120.8 | 100.4% / 100.7% | 12.2 (1.3) | 2.095 / 1.573 | 1.145 | 1.142 | 1.148 | 1.146 |
| imit3_w025_s51 | 8000 | stoch | 100% | 106.16 | 157.84 | 106.157 | 100% | 0.091 | 0% | 2% | 53.83 | 53.87 | 1.00 (n=50) | 53.87 / 54.00 | 120.5 / 120.8 | 100.4% / 100.7% | 12.2 (1.3) | 2.087 / 1.563 | 1.136 | 1.132 | 1.138 | 1.136 |
| imit3_w025_s52 | 8000 | deter | 100% | 117.07 | 286.49 | 88.949 | 90% | 5.314 | 6% | 2% | 50.19 | 55.12 | 0.91 (n=50) | 55.12 / 55.67 | 123.3 / 124.5 | 102.8% / 103.8% | 6.8 (8.8) | 2.119 / 1.588 | 1.140 | 1.136 | 1.146 | 1.137 |
| imit3_w025_s52 | 8000 | stoch | 100% | 125.17 | 284.62 | 91.405 | 88% | 5.708 | 6% | 4% | 51.20 | 55.11 | 0.93 (n=50) | 55.11 / 55.64 | 123.3 / 124.5 | 102.7% / 103.7% | 7.9 (8.0) | 2.086 / 1.548 | 1.113 | 1.108 | 1.118 | 1.110 |
| imit3_w000_s52 | 8000 | deter | 100% | 127.37 | 287.04 | 105.147 | 92% | 5.529 | 8% | 10% | 52.85 | 53.24 | 0.99 (n=50) | 53.24 / 55.22 | 119.1 / 123.5 | 99.3% / 102.9% | 11.3 (3.6) | 2.043 / 1.501 | 1.084 | 1.078 | 1.087 | 1.081 |
| imit3_w000_s52 | 8000 | stoch | 100% | 119.80 | 291.44 | 91.859 | 90% | 1.613 | 6% | 10% | 50.95 | 53.37 | 0.95 (n=50) | 53.37 / 55.06 | 119.4 / 123.2 | 99.5% / 102.7% | 8.3 (7.7) | 2.103 / 1.575 | 1.123 | 1.119 | 1.127 | 1.121 |
| best_imit_scriptfree_s51_NOTPASS_lat3.56<br>imit3_w000_s51 | 8000 | deter | 100% | 125.97 | 277.24 | 109.442 | 94% | 3.969 | 4% | 14% | 53.65 | 53.91 | 1.00 (n=50) | 53.91 / 54.04 | 120.6 / 120.9 | 100.5% / 100.7% | 11.2 (3.6) | 2.049 / 1.506 | 1.090 | 1.084 | 1.094 | 1.087 |
| best_imit_scriptfree_s51_NOTPASS_lat3.56<br>imit3_w000_s51 | 8000 | stoch | 100% | 127.77 | 275.81 | 111.273 | 94% | 2.569 | 6% | 12% | 53.85 | 53.91 | 1.00 (n=50) | 53.91 / 54.04 | 120.6 / 120.9 | 100.5% / 100.8% | 11.5 (3.2) | 2.040 / 1.494 | 1.085 | 1.079 | 1.089 | 1.082 |
| imit4_w000_s52 | 10000 | deter | 100% | 116.46 | 286.53 | 88.377 | 90% | 2.680 | 6% | 8% | 50.75 | 52.86 | 0.96 (n=50) | 52.86 / 54.53 | 118.2 / 122.0 | 98.6% / 101.7% | 9.9 (7.1) | 2.089 / 1.559 | 1.119 | 1.115 | 1.123 | 1.118 |
| imit4_w000_s52 | 10000 | stoch | 100% | 100.97 | 275.83 | 84.570 | 94% | 6.943 | 2% | 10% | 48.27 | 53.19 | 0.91 (n=50) | 53.19 / 54.87 | 119.0 / 122.7 | 99.2% / 102.3% | 6.1 (10.0) | 2.170 / 1.657 | 1.180 | 1.176 | 1.183 | 1.177 |
| imit4_w000_s51 | 10000 | deter | 100% | 121.42 | 284.65 | 93.506 | 90% | 5.426 | 6% | 4% | 51.32 | 52.75 | 0.97 (n=50) | 52.75 / 54.76 | 118.0 / 122.5 | 98.3% / 102.1% | 9.7 (6.2) | 2.072 / 1.536 | 1.105 | 1.100 | 1.109 | 1.102 |
| imit4_w000_s51 | 10000 | stoch | 100% | 107.43 | 280.51 | 91.042 | 94% | 3.778 | 4% | 6% | 49.72 | 52.67 | 0.94 (n=50) | 52.67 / 54.08 | 117.8 / 121.0 | 98.2% / 100.8% | 9.0 (7.7) | 2.119 / 1.600 | 1.149 | 1.145 | 1.152 | 1.149 |
| imit5_w000_s52 | 0 | deter | 100% | 126.53 | 294.69 | 103.883 | 92% | 4.425 | 2% | 6% | 53.38 | 54.03 | 0.99 (n=50) | 54.03 / 55.40 | 120.9 / 123.9 | 100.7% / 103.3% | 11.1 (3.6) | 2.040 / 1.493 | 1.083 | 1.078 | 1.087 | 1.081 |
| imit5_w000_s52 | 0 | stoch | 100% | 111.16 | 278.38 | 105.590 | 98% | 4.785 | 4% | 14% | 52.75 | 53.95 | 0.98 (n=50) | 53.95 / 55.44 | 120.7 / 124.0 | 100.6% / 103.4% | 10.6 (5.4) | 2.092 / 1.564 | 1.133 | 1.129 | 1.136 | 1.133 |
| best_imit_scriptfree_s51_seed4000-8000only<br>imit5_w000_s51 | 0 | deter | 100% | 109.96 | 278.07 | 93.871 | 94% | 4.800 | 0% | 4% | 51.78 | 53.34 | 0.97 (n=50) | 53.34 / 55.12 | 119.3 / 123.3 | 99.4% / 102.8% | 9.9 (6.3) | 2.102 / 1.580 | 1.138 | 1.134 | 1.141 | 1.138 |
| best_imit_scriptfree_s51_seed4000-8000only<br>imit5_w000_s51 | 0 | stoch | 100% | 113.18 | 272.43 | 91.578 | 92% | 6.295 | 0% | 2% | 51.99 | 53.44 | 0.97 (n=50) | 53.44 / 55.13 | 119.6 / 123.3 | 99.6% / 102.8% | 10.1 (5.7) | 2.095 / 1.572 | 1.135 | 1.131 | 1.137 | 1.134 |
| ppo_v4power_s61 | 30000 | deter | 100% | 279.19 | 332.27 | 279.194 | 100% | 1.822 | 42% | 38% | 88.69 | 59.15 | 1.50 (n=50) | 59.15 / 59.27 | 132.3 / 132.6 | 110.3% / 110.5% | 11.7 (2.1) | 1.831 / 1.163 | 0.874 | 0.861 | 0.894 | 0.855 |
| ppo_v4power_s61 | 30000 | stoch | 100% | 279.59 | 332.24 | 279.591 | 100% | 1.883 | 48% | 38% | 88.76 | 59.15 | 1.50 (n=50) | 59.15 / 59.27 | 132.3 / 132.6 | 110.3% / 110.5% | 11.7 (2.1) | 1.831 / 1.162 | 0.873 | 0.860 | 0.893 | 0.854 |
| ppo_v4power_s62 | 30000 | deter | 100% | 279.69 | 332.25 | 279.685 | 100% | 1.856 | 56% | 36% | 88.73 | 59.15 | 1.50 (n=50) | 59.15 / 59.27 | 132.3 / 132.6 | 110.3% / 110.5% | 11.7 (2.1) | 1.830 / 1.161 | 0.872 | 0.859 | 0.893 | 0.853 |
| ppo_v4power_s62 | 30000 | stoch | 100% | 279.20 | 332.23 | 279.199 | 100% | 1.934 | 54% | 40% | 88.72 | 59.15 | 1.50 (n=50) | 59.15 / 59.27 | 132.3 / 132.6 | 110.3% / 110.5% | 11.7 (2.1) | 1.832 / 1.163 | 0.874 | 0.861 | 0.894 | 0.855 |
| imit7_w000_s51 | 0 | deter | 100% | 117.15 | 281.65 | 89.213 | 90% | 8.020 | 2% | 8% | 50.63 | 53.95 | 0.94 (n=50) | 53.95 / 55.03 | 120.7 / 123.1 | 100.6% / 102.6% | 8.4 (7.9) | 2.102 / 1.576 | 1.132 | 1.127 | 1.135 | 1.129 |
| imit7_w000_s51 | 0 | stoch | 100% | 102.33 | 176.46 | 102.333 | 100% | 5.806 | 2% | 2% | 52.33 | 53.95 | 0.97 (n=50) | 53.95 / 54.92 | 120.7 / 122.8 | 100.6% / 102.4% | 10.7 (5.9) | 2.110 / 1.590 | 1.152 | 1.147 | 1.154 | 1.151 |
| ppo_v4power48_s71 | 30000 | deter | 100% | 311.39 | 330.99 | 311.393 | 100% | 2.151 | 54% | 36% | 93.81 | 59.18 | 1.59 (n=50) | 59.18 / 59.19 | 132.4 / 132.4 | 110.3% / 110.3% | 12.6 (0.0) | 1.783 / 1.082 | 0.840 | 0.826 | 0.863 | 0.817 |
| ppo_v4power48_s71 | 30000 | stoch | 100% | 311.15 | 330.94 | 311.152 | 100% | 2.143 | 52% | 36% | 93.71 | 59.18 | 1.58 (n=50) | 59.18 / 59.19 | 132.4 / 132.4 | 110.3% / 110.3% | 12.6 (0.0) | 1.783 / 1.082 | 0.840 | 0.826 | 0.863 | 0.817 |
| imit8_w000_s51 | 0 | deter | 100% | 124.65 | 288.52 | 96.635 | 90% | 0.248 | 2% | 0% | 51.39 | 54.21 | 0.95 (n=50) | 54.21 / 54.51 | 121.3 / 121.9 | 101.1% / 101.6% | 9.9 (6.9) | 2.057 / 1.504 | 1.091 | 1.085 | 1.097 | 1.087 |
| imit8_w000_s51 | 0 | stoch | 100% | 132.60 | 288.68 | 93.571 | 86% | 0.877 | 0% | 4% | 51.65 | 54.24 | 0.95 (n=50) | 54.24 / 54.66 | 121.3 / 122.3 | 101.1% / 101.9% | 10.0 (6.3) | 2.043 / 1.485 | 1.082 | 1.075 | 1.088 | 1.077 |
| imit9_w000_s53 | 0 | deter | 100% | 115.87 | 183.26 | 115.871 | 100% | 0.696 | 2% | 4% | 54.20 | 53.86 | 1.01 (n=50) | 53.86 / 53.87 | 120.5 / 120.5 | 100.4% / 100.4% | 12.9 (0.2) | 2.051 / 1.500 | 1.094 | 1.088 | 1.099 | 1.090 |
| imit9_w000_s53 | 0 | stoch | 100% | 113.84 | 186.08 | 113.842 | 100% | 0.732 | 2% | 2% | 53.69 | 53.89 | 1.00 (n=50) | 53.89 / 55.44 | 120.6 / 124.0 | 100.5% / 103.3% | 12.4 (3.5) | 2.061 / 1.514 | 1.102 | 1.097 | 1.107 | 1.099 |
| imit10_w000_s51_tr | 20000 | deter | 94% | 101.52 | 126.68 | 101.493 | 94% | 0.054 | 0% | 0% | 47.17 | 51.56 | 0.99 (n=47) | 50.15 / 53.63 | 112.2 / 120.0 | 93.5% / 100.0% | 11.9 (1.3) | 2.081 / 1.545 | 1.097 | 1.093 | 1.098 | 1.097 |
| imit10_w000_s51_tr | 20000 | stoch | 98% | 105.44 | 275.15 | 93.063 | 84% | 1.084 | 4% | 8% | 44.35 | 48.11 | 0.93 (n=49) | 48.87 / 54.67 | 109.3 / 122.3 | 91.1% / 101.9% | 11.8 (13.0) | 2.075 / 1.529 | 1.094 | 1.089 | 1.096 | 1.093 |
| best_imit_scriptfree_elbow48_s51<br>imit9_w000_s51 | 0 | deter | 100% | 119.97 | 184.51 | 119.973 | 100% | 0.958 | 2% | 4% | 54.22 | 53.85 | 1.01 (n=50) | 53.85 / 53.86 | 120.5 / 120.5 | 100.4% / 100.4% | 12.9 (0.2) | 2.030 / 1.469 | 1.077 | 1.070 | 1.083 | 1.072 |
| best_imit_scriptfree_elbow48_s51<br>imit9_w000_s51 | 0 | stoch | 100% | 116.98 | 185.76 | 116.976 | 100% | 0.645 | 2% | 0% | 54.21 | 53.85 | 1.01 (n=50) | 53.85 / 53.88 | 120.5 / 120.5 | 100.4% / 100.5% | 12.9 (0.2) | 2.043 / 1.487 | 1.090 | 1.084 | 1.095 | 1.086 |
| imit9_w000_s52 | 0 | deter | 100% | 120.08 | 185.44 | 120.078 | 100% | 0.991 | 2% | 6% | 54.24 | 53.85 | 1.01 (n=50) | 53.85 / 53.86 | 120.5 / 120.5 | 100.4% / 100.4% | 12.9 (0.2) | 2.032 / 1.471 | 1.078 | 1.071 | 1.084 | 1.073 |
| imit9_w000_s52 | 0 | stoch | 100% | 119.28 | 186.35 | 119.285 | 100% | 0.969 | 4% | 4% | 54.23 | 53.85 | 1.01 (n=50) | 53.85 / 53.87 | 120.4 / 120.5 | 100.4% / 100.4% | 12.9 (0.3) | 2.036 / 1.478 | 1.082 | 1.076 | 1.088 | 1.078 |
| imit13_w000_s51 | 0 | deter | 96% | 110.74 | 183.55 | 110.729 | 96% | 1.626 | 2% | 12% | 51.95 | 53.82 | 1.00 (n=48) | 53.18 / 54.28 | 118.9 / 121.4 | 99.1% / 101.2% | 12.2 (1.6) | 2.082 / 1.547 | 1.125 | 1.121 | 1.129 | 1.124 |
| imit13_w000_s51 | 0 | stoch | 98% | 111.13 | 183.78 | 111.118 | 98% | 1.631 | 2% | 8% | 52.97 | 53.79 | 1.00 (n=49) | 53.49 / 53.88 | 119.7 / 120.5 | 99.7% / 100.4% | 12.2 (1.4) | 2.079 / 1.544 | 1.127 | 1.123 | 1.131 | 1.126 |
| imit13_w000_s52 | 0 | deter | 100% | 118.78 | 282.45 | 113.133 | 98% | 1.668 | 4% | 10% | 53.89 | 53.76 | 1.00 (n=50) | 53.76 / 53.85 | 120.3 / 120.5 | 100.2% / 100.4% | 12.0 (2.4) | 2.055 / 1.509 | 1.108 | 1.103 | 1.112 | 1.105 |
| imit13_w000_s52 | 0 | stoch | 100% | 117.13 | 285.62 | 111.420 | 98% | 1.328 | 2% | 10% | 53.92 | 53.82 | 1.00 (n=50) | 53.82 / 55.00 | 120.4 / 123.0 | 100.3% / 102.5% | 12.0 (2.4) | 2.062 / 1.519 | 1.116 | 1.111 | 1.120 | 1.114 |
| imit14_w000_s51 | 0 | deter | 96% | 116.12 | 185.60 | 116.107 | 96% | 5.768 | 22% | 28% | 51.62 | 53.35 | 1.01 (n=48) | 52.67 / 53.41 | 117.8 / 119.5 | 98.2% / 99.6% | 12.9 (1.1) | 2.072 / 1.526 | 1.118 | 1.113 | 1.122 | 1.115 |
| imit14_w000_s51 | 0 | stoch | 100% | 119.48 | 186.82 | 118.078 | 98% | 5.395 | 22% | 32% | 52.18 | 51.73 | 1.01 (n=50) | 52.86 / 53.44 | 118.2 / 119.5 | 98.6% / 99.6% | 12.4 (4.5) | 2.069 / 1.522 | 1.129 | 1.123 | 1.134 | 1.126 |
| imit15_dart_s51 | 0 | deter | 100% | 117.11 | 183.56 | 117.107 | 100% | 1.629 | 4% | 10% | 54.14 | 53.80 | 1.01 (n=50) | 53.80 / 53.85 | 120.3 / 120.5 | 100.3% / 100.4% | 12.2 (1.4) | 2.050 / 1.503 | 1.101 | 1.096 | 1.105 | 1.098 |
| imit15_dart_s51 | 0 | stoch | 98% | 115.72 | 183.55 | 115.712 | 98% | 1.602 | 2% | 10% | 53.54 | 53.80 | 1.01 (n=49) | 53.80 / 53.87 | 120.3 / 120.5 | 100.3% / 100.4% | 12.2 (1.4) | 2.063 / 1.519 | 1.106 | 1.101 | 1.110 | 1.104 |
| imit16_fs1_dart_s51 | 0 | deter | 100% | 73.60 | 89.12 | 72.762 | 98% | 3.150 | 6% | 2% | 43.39 | 43.75 | 0.99 (n=50) | 43.77 / 44.05 | 97.9 / 98.5 | 81.6% / 82.1% | 11.5 (8.9) | 2.189 / 1.729 | 1.253 | 1.255 | 1.251 | 1.263 |
| imit16_fs1_dart_s51 | 0 | stoch | 98% | 73.63 | 87.79 | 73.625 | 98% | 0.886 | 2% | 2% | 43.17 | 43.93 | 1.00 (n=49) | 43.63 / 44.06 | 97.6 / 98.6 | 81.3% / 82.1% | 12.8 (1.5) | 2.193 / 1.733 | 1.245 | 1.247 | 1.243 | 1.254 |
| imit15_dart_s52 | 0 | deter | 98% | 113.56 | 183.56 | 113.553 | 98% | 1.695 | 2% | 10% | 53.01 | 53.80 | 1.00 (n=49) | 53.36 / 53.85 | 119.4 / 120.5 | 99.5% / 100.4% | 12.3 (1.4) | 2.068 / 1.529 | 1.118 | 1.113 | 1.122 | 1.115 |
| imit15_dart_s52 | 0 | stoch | 100% | 112.16 | 183.54 | 111.188 | 98% | 1.613 | 2% | 10% | 53.12 | 52.91 | 1.00 (n=50) | 53.35 / 53.87 | 119.3 / 120.5 | 99.5% / 100.4% | 12.1 (1.6) | 2.077 / 1.543 | 1.142 | 1.138 | 1.146 | 1.141 |
| imit15_dart_s53 | 0 | deter | 100% | 112.86 | 174.97 | 112.864 | 100% | 1.265 | 0% | 10% | 54.03 | 53.79 | 1.00 (n=50) | 53.79 / 53.85 | 120.3 / 120.5 | 100.3% / 100.4% | 12.3 (1.4) | 2.069 / 1.533 | 1.117 | 1.112 | 1.121 | 1.115 |
| imit15_dart_s53 | 0 | stoch | 100% | 113.20 | 172.35 | 113.198 | 100% | 1.253 | 0% | 10% | 54.02 | 53.79 | 1.00 (n=50) | 53.79 / 53.88 | 120.3 / 120.5 | 100.3% / 100.4% | 12.3 (1.4) | 2.067 / 1.529 | 1.119 | 1.114 | 1.123 | 1.117 |
| imit19_masonmapped_dart_s51 | 0 | deter | 100% | 58.26 | 64.98 | 58.257 | 100% | 0.145 | 0% | 2% | 30.12 | 33.57 | 0.90 (n=50) | 39.14 / 39.21 | 87.6 / 87.7 | 73.0% / 73.1% | 13.8 (1.1) | 2.124 / 1.614 | 1.074 | 1.088 | 1.049 | 1.104 |
| imit19_masonmapped_dart_s51 | 0 | stoch | 100% | 59.87 | 68.27 | 59.871 | 100% | 0.288 | 0% | 2% | 30.13 | 33.57 | 0.90 (n=50) | 39.14 / 39.22 | 87.6 / 87.7 | 73.0% / 73.1% | 13.8 (1.1) | 2.110 / 1.595 | 1.053 | 1.066 | 1.028 | 1.082 |
| imit18_power_dart_s51 | 0 | deter | 100% | 313.89 | 328.85 | 313.887 | 100% | 2.177 | 48% | 38% | 94.87 | 59.19 | 1.60 (n=50) | 59.19 / 59.19 | 132.4 / 132.4 | 110.3% / 110.4% | 12.6 (0.0) | 1.782 / 1.081 | 0.834 | 0.819 | 0.856 | 0.810 |
| imit18_power_dart_s51 | 0 | stoch | 100% | 313.79 | 329.40 | 313.790 | 100% | 2.177 | 48% | 38% | 94.87 | 59.19 | 1.60 (n=50) | 59.19 / 59.21 | 132.4 / 132.5 | 110.3% / 110.4% | 12.6 (0.0) | 1.782 / 1.081 | 0.834 | 0.819 | 0.856 | 0.810 |
| imit18_power_dart_s52 | 0 | deter | 100% | 313.89 | 328.83 | 313.891 | 100% | 2.177 | 48% | 38% | 94.87 | 59.19 | 1.60 (n=50) | 59.19 / 59.19 | 132.4 / 132.4 | 110.3% / 110.4% | 12.6 (0.0) | 1.782 / 1.081 | 0.834 | 0.819 | 0.856 | 0.810 |
| imit18_power_dart_s52 | 0 | stoch | 100% | 313.78 | 329.76 | 313.775 | 100% | 2.171 | 48% | 38% | 94.88 | 59.19 | 1.60 (n=50) | 59.19 / 59.22 | 132.4 / 132.5 | 110.3% / 110.4% | 12.6 (0.0) | 1.782 / 1.081 | 0.834 | 0.819 | 0.856 | 0.810 |
| ppo15_bcreg_s61 | 0 | deter | 98% | 106.66 | 271.59 | 101.222 | 96% | 11.188 | 8% | 2% | 51.32 | 53.20 | 0.98 (n=49) | 52.87 / 53.28 | 118.3 / 119.2 | 98.6% / 99.3% | 11.6 (4.0) | 2.102 / 1.577 | 1.134 | 1.130 | 1.136 | 1.134 |
| ppo15_bcreg_s61 | 0 | stoch | 100% | 123.92 | 286.16 | 101.683 | 92% | 5.751 | 8% | 12% | 51.47 | 53.11 | 0.97 (n=50) | 53.11 / 54.49 | 118.8 / 121.9 | 99.0% / 101.6% | 10.2 (5.8) | 2.056 / 1.509 | 1.089 | 1.083 | 1.093 | 1.086 |
| ppo15_bcreg_s62 | 0 | deter | 100% | 103.58 | 162.59 | 103.577 | 100% | 0.177 | 0% | 4% | 52.89 | 52.93 | 1.00 (n=50) | 52.93 / 52.97 | 118.4 / 118.5 | 98.7% / 98.7% | 11.8 (2.2) | 2.097 / 1.573 | 1.146 | 1.142 | 1.149 | 1.146 |
| ppo15_bcreg_s62 | 0 | stoch | 98% | 118.63 | 276.99 | 91.446 | 88% | 5.224 | 8% | 6% | 49.49 | 52.87 | 0.95 (n=49) | 52.53 / 53.48 | 117.5 / 119.6 | 97.9% / 99.7% | 9.1 (6.9) | 2.087 / 1.550 | 1.111 | 1.107 | 1.116 | 1.109 |
| ppo15_stoch_s71 | 0 | deter | 96% | 93.73 | 137.15 | 93.720 | 96% | 2.949 | 0% | 2% | 49.00 | 51.80 | 0.98 (n=48) | 51.17 / 51.85 | 114.5 / 116.0 | 95.4% / 96.7% | 11.6 (3.6) | 2.123 / 1.611 | 1.155 | 1.152 | 1.156 | 1.157 |
| ppo15_stoch_s71 | 0 | stoch | 100% | 105.34 | 271.19 | 89.406 | 94% | 4.598 | 6% | 12% | 48.50 | 51.93 | 0.93 (n=50) | 51.93 / 54.06 | 116.2 / 120.9 | 96.8% / 100.8% | 8.2 (8.3) | 2.141 / 1.618 | 1.161 | 1.158 | 1.166 | 1.160 |
| ppo15_anneal_s91 | 0 | deter | 98% | 106.86 | 177.25 | 106.855 | 98% | 9.803 | 12% | 6% | 52.45 | 54.42 | 0.98 (n=49) | 54.02 / 54.51 | 120.8 / 121.9 | 100.7% / 101.6% | 11.3 (5.3) | 2.103 / 1.574 | 1.138 | 1.134 | 1.142 | 1.136 |
| ppo15_anneal_s91 | 0 | stoch | 100% | 120.45 | 266.45 | 115.121 | 98% | 5.249 | 10% | 20% | 53.86 | 54.40 | 0.99 (n=50) | 54.40 / 55.71 | 121.7 / 124.6 | 101.4% / 103.9% | 11.6 (4.4) | 2.059 / 1.508 | 1.106 | 1.100 | 1.111 | 1.103 |
| imit20_fs1_q23_dart_s51 | 0 | deter | 100% | 139.63 | 150.49 | 139.629 | 100% | 2.289 | 6% | 12% | 45.10 | 45.00 | 1.00 (n=50) | 45.00 / 45.17 | 100.7 / 101.0 | 83.9% / 84.2% | 17.7 (1.8) | 1.958 / 1.415 | 0.962 | 0.953 | 0.965 | 0.957 |
| imit20_fs1_q23_dart_s51 | 0 | stoch | 100% | 139.13 | 148.96 | 139.134 | 100% | 2.486 | 8% | 12% | 45.01 | 44.99 | 1.00 (n=50) | 44.99 / 45.17 | 100.6 / 101.0 | 83.9% / 84.2% | 17.8 (1.8) | 1.959 / 1.416 | 0.963 | 0.954 | 0.966 | 0.958 |
| ppo15_klres_s101 | 0 | deter | 100% | 112.86 | 174.97 | 112.864 | 100% | 1.265 | 0% | 10% | 54.03 | 53.79 | 1.00 (n=50) | 53.79 / 53.85 | 120.3 / 120.5 | 100.3% / 100.4% | 12.3 (1.4) | 2.069 / 1.533 | 1.117 | 1.112 | 1.121 | 1.115 |
| ppo15_klres_s101 | 0 | stoch | 100% | 115.77 | 275.24 | 110.268 | 98% | 1.060 | 2% | 10% | 53.80 | 53.80 | 1.00 (n=50) | 53.80 / 53.91 | 120.3 / 120.6 | 100.3% / 100.5% | 12.0 (2.2) | 2.066 / 1.527 | 1.118 | 1.114 | 1.122 | 1.117 |
| ppo20_klres_s111 | 0 | deter | 100% | 139.63 | 150.49 | 139.629 | 100% | 2.289 | 6% | 12% | 45.10 | 45.00 | 1.00 (n=50) | 45.00 / 45.17 | 100.7 / 101.0 | 83.9% / 84.2% | 17.7 (1.8) | 1.958 / 1.415 | 0.962 | 0.953 | 0.965 | 0.957 |
| ppo20_klres_s111 | 0 | stoch | 100% | 139.32 | 144.22 | 139.320 | 100% | 1.385 | 8% | 4% | 45.13 | 45.00 | 1.00 (n=50) | 45.00 / 45.18 | 100.7 / 101.1 | 83.9% / 84.2% | 17.7 (1.8) | 1.960 / 1.417 | 0.964 | 0.955 | 0.967 | 0.959 |
| ppo20_soft_s121 | 0 | deter | 100% | 139.82 | 150.35 | 139.823 | 100% | 1.950 | 6% | 14% | 45.06 | 45.00 | 1.00 (n=50) | 45.00 / 45.17 | 100.7 / 101.0 | 83.9% / 84.2% | 17.7 (1.8) | 1.957 / 1.414 | 0.961 | 0.951 | 0.963 | 0.955 |
| ppo20_soft_s121 | 0 | stoch | 100% | 139.53 | 144.40 | 139.530 | 100% | 0.958 | 4% | 10% | 44.97 | 44.99 | 1.00 (n=50) | 44.99 / 45.18 | 100.6 / 101.1 | 83.9% / 84.2% | 17.8 (1.7) | 1.958 / 1.414 | 0.961 | 0.952 | 0.964 | 0.956 |
| ppo15_soft_s122 | 0 | deter | 100% | 112.86 | 174.97 | 112.864 | 100% | 1.265 | 0% | 10% | 54.03 | 53.79 | 1.00 (n=50) | 53.79 / 53.85 | 120.3 / 120.5 | 100.3% / 100.4% | 12.3 (1.4) | 2.069 / 1.533 | 1.117 | 1.112 | 1.121 | 1.115 |
| ppo15_soft_s122 | 0 | stoch | 98% | 115.87 | 283.50 | 104.721 | 94% | 1.198 | 2% | 4% | 52.61 | 53.79 | 1.00 (n=49) | 53.42 / 53.92 | 119.5 / 120.6 | 99.6% / 100.5% | 11.7 (2.8) | 2.071 / 1.534 | 1.119 | 1.115 | 1.123 | 1.118 |

## Per-row summary: learned fraction, style distance, sequencing (proxy)

Learned fraction = what the JSON args record (residual caps / env type), never guessed. DTW = native mason_v2 recommended set, mean over refs (all 11 joints, rad; arm columns VOID: lead/trail arm bug, see Trainer). Sequencing = time of peak |angular velocity| per segment relative to first true contact (ms; negative = before impact), measured every 5 ms of simulated time within [impact-0.30 s, impact+0.05 s]; proximal-to-distal = hips -> chest yaw -> shoulder -> elbow -> wrist -> club-head speed peaks non-decreasing (5 ms ties count as in order). PROXY: single-joint angular speeds, the sim has no pelvis yaw joint, club speed is the head geom speed.

| Model(s) | Mode | Learned fraction (from JSON args) | DTW all11 mean | Peak t rel. impact ms: hips / chest yaw / shoulder / elbow / wrist / club | Prox-to-distal | wrist-shoulder lag s | elbow-shoulder lag s |
|---|---|---|---|---|---|---|---|
| ppo_scott_prev_backup | deter | direct policy control (HumanoidGolfEnv; no scripted base) | 2.359 | 18 / nan / -2 / 38 / 38 / 18 | 0% (n=50) | 0.040 | 0.040 |
| ppo_scott_prev_backup | stoch | direct policy control (HumanoidGolfEnv; no scripted base) | 3.414 | 5 / nan / 14 / 25 / -16 / 41 | 0% (n=16) | -0.030 | 0.000 |
| ppo_scott_curr | deter | direct policy control (HumanoidGolfEnv; no scripted base) | 3.494 | 0 / nan / -20 / -60 / 40 / 20 | 0% (n=50) | 0.060 | -0.040 |
| ppo_scott_curr | stoch | direct policy control (HumanoidGolfEnv; no scripted base) | 3.377 | 38 / nan / 38 / 38 / -42 / 38 | 0% (n=2) | -0.080 | 0.000 |
| ppo_scott_baseline | deter | direct policy control (HumanoidGolfEnv; no scripted base) | 4.642 | n/a | nan% (n=0) | nan | nan |
| ppo_scott_baseline | stoch | direct policy control (HumanoidGolfEnv; no scripted base) | 8.685 | n/a | nan% (n=0) | nan | nan |
| ppo_scott<br>ppo_scott_carry1 | deter | direct policy control (HumanoidGolfEnv; no scripted base) | 2.259 | -119 / nan / -151 / 27 / 37 / -51 | 0% (n=30) | 0.130 | 0.180 |
| ppo_scott<br>ppo_scott_carry1 | stoch | direct policy control (HumanoidGolfEnv; no scripted base) | 3.165 | -6 / nan / -6 / 17 / -125 / 1 | 0% (n=10) | -0.040 | 0.030 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | deter | direct policy control (HumanoidGolfEnv; no scripted base) | 3.019 | 10 / nan / -116 / -116 / -52 / 5 | 0% (n=4) | 0.050 | 0.000 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | stoch | direct policy control (HumanoidGolfEnv; no scripted base) | 3.374 | -6 / nan / 4 / 34 / 4 / 4 | 0% (n=2) | 0.000 | 0.030 |
| ppo_resid_v3_s0 | deter | residual on scripted swing: cap +-[0.4, 0.4, 0.4, 0.25] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.917 | 48 / -70 / -3 / -11 / 45 / -1 | 0% (n=50) | 0.050 | -0.010 |
| ppo_resid_v3_s0 | stoch | residual on scripted swing: cap +-[0.4, 0.4, 0.4, 0.25] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.347 | -10 / -124 / -10 / -27 / 30 / -2 | 0% (n=32) | 0.040 | -0.022 |
| ppo_resid_v3_r2_s0 | deter | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.925 | -18 / -58 / -13 / 16 / 46 / -3 | 0% (n=50) | 0.060 | 0.030 |
| ppo_resid_v3_r2_s0 | stoch | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.005 | -14 / -151 / -9 / 19 / 45 / -2 | 0% (n=50) | 0.055 | 0.025 |
| ppo_resid_v3_r3_s0 | deter | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.912 | -16 / -40 / -11 / 23 / 47 / -2 | 0% (n=50) | 0.060 | 0.035 |
| ppo_resid_v3_r3_s0 | stoch | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.963 | -13 / -161 / -10 / 21 / 46 / -3 | 0% (n=50) | 0.055 | 0.030 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | deter | 0% (scripted, zero residual) | 2.045 | -20 / 4 / -10 / 19 / 44 / -1 | 0% (n=50) | 0.055 | 0.030 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | stoch | 0% (scripted, zero residual) | 2.045 | -20 / 4 / -10 / 19 / 44 / -1 | 0% (n=50) | 0.055 | 0.030 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | deter | 0% (scripted, zero residual) | 2.177 | -20 / 4 / -10 / 19 / 44 / -0 | 0% (n=50) | 0.055 | 0.030 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | stoch | 0% (scripted, zero residual) | 2.177 | -20 / 4 / -10 / 19 / 44 / -0 | 0% (n=50) | 0.055 | 0.030 |
| ppo_resid_v3_ladder_s0 | deter | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.905 | -12 / -57 / -8 / -3 / 42 / -3 | 0% (n=50) | 0.050 | 0.005 |
| ppo_resid_v3_ladder_s0 | stoch | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.044 | -14 / -94 / -11 / 7 / 44 / -3 | 0% (n=50) | 0.055 | 0.015 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | deter | 0% (scripted, zero residual) | 2.242 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | stoch | 0% (scripted, zero residual) | 2.242 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | deter | 0% (scripted, zero residual) | 2.060 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | stoch | 0% (scripted, zero residual) | 2.060 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| scripted (not learned) [STOCK motors force_scale 1: fast v3 swing, default elbow] | deter | 0% (scripted, zero residual) | 2.187 | -5 / 5 / -5 / 25 / 50 / -5 | 0% (n=50) | 0.055 | 0.030 |
| scripted (not learned) [STOCK motors force_scale 1: fast v3 swing, default elbow] | stoch | 0% (scripted, zero residual) | 2.187 | -5 / 5 / -5 / 25 / 50 / -5 | 0% (n=50) | 0.055 | 0.030 |
| ppo_resid_v3_left_an1_s0 | deter | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.897 | -12 / -87 / -12 / 18 / 46 / -2 | 0% (n=50) | 0.060 | 0.030 |
| ppo_resid_v3_left_an1_s0 | stoch | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.965 | -13 / -150 / -10 / 17 / 45 / -3 | 0% (n=50) | 0.055 | 0.025 |
| ppo_resid_v3_left_an3_s1 | deter | residual on scripted swing: cap +-[0.1, 0.1, 0.1, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.931 | -14 / 3 / -9 / 15 / 45 / -4 | 0% (n=50) | 0.055 | 0.025 |
| ppo_resid_v3_left_an3_s1 | stoch | residual on scripted swing: cap +-[0.1, 0.1, 0.1, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.922 | -12 / -107 / -11 / 16 / 45 / -2 | 0% (n=50) | 0.055 | 0.027 |
| ppo_resid_v3_left_an4_s2 | deter | residual on scripted swing: cap +-[0.1, 0.1, 0.1, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.914 | -13 / 46 / -13 / 16 / 46 / -3 | 0% (n=50) | 0.060 | 0.030 |
| ppo_resid_v3_left_an4_s2 | stoch | residual on scripted swing: cap +-[0.1, 0.1, 0.1, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.923 | -12 / -85 / -10 / 16 / 45 / -2 | 0% (n=50) | 0.055 | 0.025 |
| ppo_resid_v3_left_an5_s3 | deter | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.435 | -15 / 12 / -13 / 10 / 45 / -2 | 0% (n=50) | 0.060 | 0.025 |
| ppo_resid_v3_left_an5_s3 | stoch | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.292 | -15 / -55 / -14 / 11 / 45 / -3 | 0% (n=50) | 0.060 | 0.025 |
| best_carry_analytic<br>ppo_resid_v3_left_an2_s0 | deter | residual on scripted swing: cap +-[0.1, 0.1, 0.1, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.891 | -13 / 12 / -9 / 16 / 46 / -3 | 0% (n=50) | 0.055 | 0.030 |
| best_carry_analytic<br>ppo_resid_v3_left_an2_s0 | stoch | residual on scripted swing: cap +-[0.1, 0.1, 0.1, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.945 | -14 / -135 / -11 / 16 / 45 / -3 | 0% (n=50) | 0.055 | 0.025 |
| ppo_resid_v3_left_an6_s4 | deter | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.933 | -16 / -53 / -16 / 17 / 44 / -2 | 0% (n=50) | 0.060 | 0.030 |
| ppo_resid_v3_left_an6_s4 | stoch | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.920 | -15 / -95 / -11 / 16 / 45 / -3 | 0% (n=50) | 0.055 | 0.025 |
| ppo_resid_v3_left_an8_s6 | deter | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.444 | -14 / -49 / -14 / 15 / 45 / -4 | 0% (n=50) | 0.060 | 0.030 |
| ppo_resid_v3_left_an8_s6 | stoch | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.495 | -15 / -141 / -14 / 15 / 45 / -2 | 0% (n=50) | 0.060 | 0.030 |
| ppo_resid_v3_left_an7_s5 | deter | residual on scripted swing: cap +-[0.04, 0.04, 0.03, 0.02] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.376 | -15 / -59 / -13 / 16 / 45 / -3 | 0% (n=50) | 0.060 | 0.030 |
| ppo_resid_v3_left_an7_s5 | stoch | residual on scripted swing: cap +-[0.04, 0.04, 0.03, 0.02] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.309 | -15 / -121 / -14 / 16 / 45 / -3 | 0% (n=50) | 0.060 | 0.030 |
| ppo_resid_v3_left_an9_s7 | deter | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.909 | -13 / -2 / -9 / 18 / 45 / -2 | 0% (n=50) | 0.055 | 0.025 |
| ppo_resid_v3_left_an9_s7 | stoch | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.925 | -13 / -169 / -10 / 18 / 44 / -2 | 0% (n=50) | 0.055 | 0.027 |
| ppo_resid_v3_left_an10_s8 | deter | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.919 | -11 / 43 / -7 / 18 / 43 / -2 | 0% (n=50) | 0.050 | 0.025 |
| ppo_resid_v3_left_an10_s8 | stoch | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.051 | -14 / -143 / -9 / 18 / 46 / -3 | 0% (n=50) | 0.055 | 0.030 |
| ppo_resid_v3_left_fast1_s10 | deter | residual on scripted swing: cap +-[0.02, 0.02, 0.01, 0.02] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.669 | -16 / -2 / -16 / -1 / 43 / -1 | 0% (n=50) | 0.060 | 0.015 |
| ppo_resid_v3_left_fast1_s10 | stoch | residual on scripted swing: cap +-[0.02, 0.02, 0.01, 0.02] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.674 | -15 / -160 / -15 / -1 / 45 / -3 | 0% (n=50) | 0.060 | 0.015 |
| best_gate_flat_123mph<br>ppo_resid_v3_left_fast2_s11 | deter | residual on scripted swing: cap +-[0.02, 0.02, 0.01, 0.02] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.665 | -15 / -50 / -15 / -1 / 44 / -2 | 0% (n=50) | 0.060 | 0.015 |
| best_gate_flat_123mph<br>ppo_resid_v3_left_fast2_s11 | stoch | residual on scripted swing: cap +-[0.02, 0.02, 0.01, 0.02] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.626 | -16 / -120 / -16 / -1 / 44 / -3 | 0% (n=50) | 0.060 | 0.015 |
| ppo_v3tiny_s22 | deter | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.039 | -13 / 1 / -13 / 16 / 46 / -3 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v3tiny_s22 | stoch | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.072 | -13 / -113 / -13 / 16 / 45 / -2 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v3tiny_s23 | deter | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.088 | -13 / 1 / -13 / 15 / 46 / -3 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v3tiny_s23 | stoch | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.052 | -14 / -115 / -14 / 15 / 45 / -3 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v3tiny_s21 | deter | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.119 | -15 / 49 / -15 / 14 / 44 / -1 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v3tiny_s21 | stoch | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.069 | -14 / -6 / -13 / 14 / 45 / -2 | 0% (n=50) | 0.060 | 0.027 |
| ppo_v3flt_all_s33 | deter | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.02; % of control from policy = not defined/unknown | 2.126 | -15 / 7 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v3flt_all_s33 | stoch | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.02; % of control from policy = not defined/unknown | 2.108 | -15 / -139 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| best_learned_yaw_s32<br>ppo_v3flt_yaw_s32 | deter | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 2.068 | -15 / 20 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| best_learned_yaw_s32<br>ppo_v3flt_yaw_s32 | stoch | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 2.066 | -15 / -170 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| best_learned_yaw_s31<br>ppo_v3flt_yaw_s31 | deter | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 2.066 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| best_learned_yaw_s31<br>ppo_v3flt_yaw_s31 | stoch | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 2.063 | -15 / -180 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v4yaw_s43 | deter | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.847 | -15 / 4 / -15 / -5 / 44 / -0 | 0% (n=50) | 0.060 | 0.010 |
| ppo_v4yaw_s43 | stoch | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.843 | -15 / -85 / -15 / -5 / 44 / -0 | 0% (n=50) | 0.060 | 0.010 |
| ppo_v4yaw_s42 | deter | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.846 | -15 / 1 / -15 / -5 / 44 / -0 | 0% (n=50) | 0.060 | 0.010 |
| ppo_v4yaw_s42 | stoch | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.843 | -15 / -165 / -15 / -5 / 44 / -0 | 0% (n=50) | 0.060 | 0.010 |
| best_v4yaw_s41<br>ppo_v4yaw_s41 | deter | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.845 | -15 / -40 / -15 / -5 / 44 / -0 | 0% (n=50) | 0.060 | 0.010 |
| best_v4yaw_s41<br>ppo_v4yaw_s41 | stoch | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.845 | -15 / -138 / -15 / -5 / 44 / -0 | 0% (n=50) | 0.060 | 0.010 |
| imit2_w075_s51 | deter | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command = 75% scripted + 25% script-distilled policy (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.161 | -15 / 3 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit2_w075_s51 | stoch | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command = 75% scripted + 25% script-distilled policy (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.104 | -15 / 0 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit2_w075_s52 | deter | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command = 75% scripted + 25% script-distilled policy (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.007 | -15 / 10 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit2_w075_s52 | stoch | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command = 75% scripted + 25% script-distilled policy (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.047 | -15 / 10 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit2_w075_s53 | deter | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command = 75% scripted + 25% script-distilled policy (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.010 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit2_w075_s53 | stoch | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command = 75% scripted + 25% script-distilled policy (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.106 | -15 / 0 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w075_s51 | deter | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command = 75% scripted + 25% script-distilled policy (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.062 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w075_s51 | stoch | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command = 75% scripted + 25% script-distilled policy (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.066 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w075_s52 | deter | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command = 75% scripted + 25% script-distilled policy (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.046 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w075_s52 | stoch | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command = 75% scripted + 25% script-distilled policy (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.049 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w075_s53 | deter | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command = 75% scripted + 25% script-distilled policy (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.023 | -15 / 3 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w075_s53 | stoch | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command = 75% scripted + 25% script-distilled policy (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.026 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w050_s51 | deter | IMITATION OF THE SCRIPT, 50% script: BLEND: executed command = 50% scripted + 50% script-distilled policy (script_weight=0.5, learn_scale=[1.2, 0.35, 0.075, 0.075]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.052 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w050_s51 | stoch | IMITATION OF THE SCRIPT, 50% script: BLEND: executed command = 50% scripted + 50% script-distilled policy (script_weight=0.5, learn_scale=[1.2, 0.35, 0.075, 0.075]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.045 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| best_imit_w050_s52<br>imit3_w050_s52 | deter | IMITATION OF THE SCRIPT, 50% script: BLEND: executed command = 50% scripted + 50% script-distilled policy (script_weight=0.5, learn_scale=[1.2, 0.35, 0.075, 0.075]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.086 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| best_imit_w050_s52<br>imit3_w050_s52 | stoch | IMITATION OF THE SCRIPT, 50% script: BLEND: executed command = 50% scripted + 50% script-distilled policy (script_weight=0.5, learn_scale=[1.2, 0.35, 0.075, 0.075]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.075 | -15 / 3 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w025_s51 | deter | IMITATION OF THE SCRIPT, 25% script: BLEND: executed command = 25% scripted + 75% script-distilled policy (script_weight=0.25, learn_scale=[1.8, 0.525, 0.1125, 0.1125]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.095 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w025_s51 | stoch | IMITATION OF THE SCRIPT, 25% script: BLEND: executed command = 25% scripted + 75% script-distilled policy (script_weight=0.25, learn_scale=[1.8, 0.525, 0.1125, 0.1125]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.087 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w025_s52 | deter | IMITATION OF THE SCRIPT, 25% script: BLEND: executed command = 25% scripted + 75% script-distilled policy (script_weight=0.25, learn_scale=[1.8, 0.525, 0.1125, 0.1125]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.119 | -16 / 4 / -16 / 14 / 40 / -1 | 0% (n=50) | 0.055 | 0.030 |
| imit3_w025_s52 | stoch | IMITATION OF THE SCRIPT, 25% script: BLEND: executed command = 25% scripted + 75% script-distilled policy (script_weight=0.25, learn_scale=[1.8, 0.525, 0.1125, 0.1125]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.086 | -16 / 3 / -16 / 14 / 42 / -1 | 0% (n=50) | 0.055 | 0.030 |
| imit3_w000_s52 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.043 | -14 / 5 / -14 / 15 / 45 / -4 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w000_s52 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.103 | -15 / 5 / -14 / 15 / 45 / -4 | 0% (n=50) | 0.060 | 0.030 |
| best_imit_scriptfree_s51_NOTPASS_lat3.56<br>imit3_w000_s51 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.049 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| best_imit_scriptfree_s51_NOTPASS_lat3.56<br>imit3_w000_s51 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.040 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit4_w000_s52 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.089 | -14 / 11 / -14 / 15 / 46 / -4 | 0% (n=50) | 0.060 | 0.030 |
| imit4_w000_s52 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.170 | -14 / -79 / -14 / 14 / 45 / -4 | 0% (n=50) | 0.060 | 0.025 |
| imit4_w000_s51 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.072 | -15 / -38 / -14 / -1 / 45 / -2 | 0% (n=50) | 0.060 | 0.015 |
| imit4_w000_s51 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.119 | -15 / -99 / -15 / 5 / 45 / -2 | 0% (n=50) | 0.060 | 0.020 |
| imit5_w000_s52 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.040 | -15 / 4 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit5_w000_s52 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.092 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| best_imit_scriptfree_s51_seed4000-8000only<br>imit5_w000_s51 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.102 | -14 / 2 / -14 / 16 / 45 / -4 | 0% (n=50) | 0.060 | 0.030 |
| best_imit_scriptfree_s51_seed4000-8000only<br>imit5_w000_s51 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.095 | -14 / 1 / -14 / 15 / 45 / -4 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v4power_s61 | deter | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.831 | -13 / -28 / -18 / 21 / -3 / -3 | 0% (n=50) | 0.015 | 0.040 |
| ppo_v4power_s61 | stoch | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.831 | -13 / -93 / -18 / 21 / -3 / -3 | 0% (n=50) | 0.015 | 0.040 |
| ppo_v4power_s62 | deter | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.830 | -13 / -33 / -18 / 21 / -3 / -3 | 0% (n=50) | 0.015 | 0.040 |
| ppo_v4power_s62 | stoch | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.832 | -13 / -73 / -18 / 21 / -3 / -3 | 0% (n=50) | 0.015 | 0.040 |
| imit7_w000_s51 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.102 | -15 / 5 / -15 / 15 / 45 / -4 | 0% (n=50) | 0.060 | 0.030 |
| imit7_w000_s51 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.110 | -15 / 3 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v4power48_s71 | deter | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.783 | -13 / -28 / -18 / 21 / -3 / -3 | 0% (n=50) | 0.015 | 0.040 |
| ppo_v4power48_s71 | stoch | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.783 | -13 / -113 / -18 / 21 / -3 / -3 | 0% (n=50) | 0.015 | 0.040 |
| imit8_w000_s51 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.057 | -15 / 5 / -15 / 15 / 42 / -3 | 0% (n=50) | 0.057 | 0.030 |
| imit8_w000_s51 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.043 | -15 / 5 / -15 / 14 / 44 / -1 | 0% (n=50) | 0.060 | 0.030 |
| imit9_w000_s53 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.051 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit9_w000_s53 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.061 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit10_w000_s51_tr | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.081 | -15 / 19 / -15 / 19 / 19 / -0 | 0% (n=47) | 0.035 | 0.035 |
| imit10_w000_s51_tr | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.075 | -15 / 19 / -15 / 19 / 19 / -0 | 0% (n=49) | 0.035 | 0.035 |
| best_imit_scriptfree_elbow48_s51<br>imit9_w000_s51 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.030 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| best_imit_scriptfree_elbow48_s51<br>imit9_w000_s51 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.043 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit9_w000_s52 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.032 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit9_w000_s52 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.036 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit13_w000_s51 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.082 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=48) | 0.060 | 0.030 |
| imit13_w000_s51 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.079 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=49) | 0.060 | 0.030 |
| imit13_w000_s52 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.055 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit13_w000_s52 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.062 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit14_w000_s51 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.072 | -14 / 0 / -14 / 15 / 45 / -4 | 0% (n=48) | 0.060 | 0.030 |
| imit14_w000_s51 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.069 | -14 / 0 / -14 / 15 / 45 / -4 | 0% (n=50) | 0.060 | 0.030 |
| imit15_dart_s51 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.050 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit15_dart_s51 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.063 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=49) | 0.060 | 0.030 |
| imit16_fs1_dart_s51 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad | 2.189 | -5 / 5 / -5 / 25 / 50 / -5 | 0% (n=50) | 0.055 | 0.030 |
| imit16_fs1_dart_s51 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad | 2.193 | -5 / 2 / -5 / 25 / 50 / -5 | 0% (n=49) | 0.055 | 0.030 |
| imit15_dart_s52 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.068 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=49) | 0.060 | 0.030 |
| imit15_dart_s52 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.077 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit15_dart_s53 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.069 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit15_dart_s53 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.067 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit19_masonmapped_dart_s51 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.124 | 47 / 2 / -43 / -13 / -3 / -23 | 0% (n=50) | 0.040 | 0.030 |
| imit19_masonmapped_dart_s51 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.110 | 47 / 2 / -43 / -13 / -3 / -23 | 0% (n=50) | 0.040 | 0.030 |
| imit18_power_dart_s51 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 1.782 | -13 / 1 / -18 / 21 / -3 / -3 | 0% (n=50) | 0.015 | 0.040 |
| imit18_power_dart_s51 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 1.782 | -13 / 1 / -18 / 21 / -3 / -3 | 0% (n=50) | 0.015 | 0.040 |
| imit18_power_dart_s52 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 1.782 | -13 / 1 / -18 / 21 / -3 / -3 | 0% (n=50) | 0.015 | 0.040 |
| imit18_power_dart_s52 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 1.782 | -13 / 1 / -18 / 21 / -3 / -3 | 0% (n=50) | 0.015 | 0.040 |
| ppo15_bcreg_s61 | deter | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-None rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.102 | -15 / -9 / -15 / 15 / 45 / -5 | 0% (n=49) | 0.060 | 0.030 |
| ppo15_bcreg_s61 | stoch | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-None rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.056 | -15 / -120 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| ppo15_bcreg_s62 | deter | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-None rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.097 | -15 / 4 / -15 / 14 / 44 / -0 | 0% (n=50) | 0.060 | 0.030 |
| ppo15_bcreg_s62 | stoch | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-None rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.087 | -15 / -120 / -15 / 14 / 44 / -0 | 0% (n=49) | 0.060 | 0.030 |
| ppo15_stoch_s71 | deter | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-None rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.123 | -15 / -28 / -15 / 15 / 45 / -5 | 0% (n=48) | 0.060 | 0.030 |
| ppo15_stoch_s71 | stoch | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-None rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.141 | -15 / -120 / -15 / 14 / 44 / -3 | 0% (n=50) | 0.060 | 0.030 |
| ppo15_anneal_s91 | deter | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-None rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.103 | -13 / -8 / -13 / -3 / 46 / -3 | 0% (n=49) | 0.060 | 0.010 |
| ppo15_anneal_s91 | stoch | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-None rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.059 | -13 / -3 / -13 / -2 / 46 / -3 | 0% (n=50) | 0.060 | 0.010 |
| imit20_fs1_q23_dart_s51 | deter | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad | 1.958 | -7 / 2 / -2 / 27 / 47 / -2 | 0% (n=50) | 0.050 | 0.030 |
| imit20_fs1_q23_dart_s51 | stoch | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: executed command = 0% scripted + 100% script-distilled policy (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad | 1.959 | -7 / 2 / -2 / 28 / 48 / -2 | 0% (n=50) | 0.050 | 0.030 |
| ppo15_klres_s101 | deter | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-None rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.069 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| ppo15_klres_s101 | stoch | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-None rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.066 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| ppo20_klres_s111 | deter | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-None rad | 1.958 | -7 / 2 / -2 / 27 / 47 / -2 | 0% (n=50) | 0.050 | 0.030 |
| ppo20_klres_s111 | stoch | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-None rad | 1.960 | -7 / 2 / -2 / 27 / 47 / -2 | 0% (n=50) | 0.050 | 0.030 |
| ppo20_soft_s121 | deter | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-None rad | 1.957 | -7 / 2 / -2 / 27 / 47 / -2 | 0% (n=50) | 0.050 | 0.030 |
| ppo20_soft_s121 | stoch | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-None rad | 1.958 | -7 / 2 / -2 / 27 / 48 / -2 | 0% (n=50) | 0.050 | 0.030 |
| ppo15_soft_s122 | deter | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-None rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.069 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| ppo15_soft_s122 | stoch | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-None rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.071 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=49) | 0.060 | 0.030 |

**Mason reference (proxy, `data/references/mason_target_features.json`, file mtime 2026-10-17 15:58; schema mason_target_features/v1; self-filmed ~30 fps 2D MediaPipe angles, ?-swing set, events +-1 frame, tempo +-15%):** arm-only sequencing, times in seconds from takeoff within [top, impact+0.15 s]: shoulder_R peak 0.60, elbow_R 0.67, wrist_R 0.64; wrist-minus-shoulder lag median 0.02 s; elbow-minus-shoulder (from medians) 0.07 s. Pelvis/thorax sequencing is UNAVAILABLE for Mason (reported 'unavailable'), so hips/torso rows cannot be compared. The Data Agent's regenerated (0.4 s timing fix) version is used only if the file in this tree is that version (check the mtime above); no sequencing number is taken from anywhere else. Sim lags and Mason lags are different windows/definitions: indicative only.

## Distance in yards (1 m = 1.09361 yd) - det / stoch separate

Total = carry + roll = final ball x minus start x along the target line at episode end (450-step horizon; ball may still be rolling; analytic-ball runs end early). Carry = first-landing distance (0 if never landed). Means over all episodes.

| Model(s) | Mode | Carry m | Carry yd | Total m | Total yd | Roll m (landed shots) | Max total yd |
|---|---|---|---|---|---|---|---|
| ppo_scott_prev_backup | deter | 0.0 | 0.0 | 2.3 | 2.5 | nan | 3 |
| ppo_scott_prev_backup | stoch | 0.0 | 0.0 | 4.1 | 4.5 | nan | 14 |
| ppo_scott_curr | deter | 0.0 | 0.0 | 2.6 | 2.8 | nan | 3 |
| ppo_scott_curr | stoch | 0.0 | 0.0 | 4.0 | 4.4 | nan | 13 |
| ppo_scott_baseline | deter | 0.0 | 0.0 | -0.0 | -0.1 | nan | -0 |
| ppo_scott_baseline | stoch | 0.0 | 0.0 | 0.6 | 0.6 | nan | 8 |
| ppo_scott<br>ppo_scott_carry1 | deter | 0.1 | 0.1 | 0.0 | 0.0 | nan | 0 |
| ppo_scott<br>ppo_scott_carry1 | stoch | 0.4 | 0.5 | 0.5 | 0.5 | nan | 7 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | deter | 0.1 | 0.1 | 1.4 | 1.5 | nan | 10 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | stoch | 0.1 | 0.2 | 2.3 | 2.5 | nan | 12 |
| ppo_resid_v3_s0 | deter | 57.1 | 62.5 | 56.7 | 62.0 | 0.0 | 76 |
| ppo_resid_v3_s0 | stoch | 20.8 | 22.8 | 37.7 | 41.3 | nan | 316 |
| ppo_resid_v3_r2_s0 | deter | 86.9 | 95.1 | 86.5 | 94.6 | 0.0 | 115 |
| ppo_resid_v3_r2_s0 | stoch | 60.5 | 66.1 | 110.0 | 120.3 | nan | 364 |
| ppo_resid_v3_r3_s0 | deter | 103.4 | 113.1 | 103.0 | 112.7 | 0.0 | 167 |
| ppo_resid_v3_r3_s0 | stoch | 66.8 | 73.0 | 123.5 | 135.0 | nan | 375 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | deter | 36.7 | 40.1 | 176.8 | 193.3 | nan | 362 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | stoch | 36.7 | 40.1 | 176.8 | 193.3 | nan | 362 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | deter | 53.9 | 59.0 | 118.0 | 129.1 | nan | 356 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | stoch | 53.9 | 59.0 | 118.0 | 129.1 | nan | 356 |
| ppo_resid_v3_ladder_s0 | deter | 99.6 | 109.0 | 99.2 | 108.5 | 0.0 | 146 |
| ppo_resid_v3_ladder_s0 | stoch | 69.1 | 75.5 | 94.0 | 102.9 | nan | 371 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | deter | 69.4 | 75.9 | 80.3 | 87.8 | nan | 317 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | stoch | 69.4 | 75.9 | 80.3 | 87.8 | nan | 317 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | deter | 115.7 | 126.5 | 115.3 | 126.1 | 0.0 | 204 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | stoch | 115.7 | 126.5 | 115.3 | 126.1 | 0.0 | 204 |
| scripted (not learned) [STOCK motors force_scale 1: fast v3 swing, default elbow] | deter | 74.8 | 81.8 | 74.4 | 81.4 | 0.0 | 95 |
| scripted (not learned) [STOCK motors force_scale 1: fast v3 swing, default elbow] | stoch | 74.8 | 81.8 | 74.4 | 81.4 | 0.0 | 95 |
| ppo_resid_v3_left_an1_s0 | deter | 111.0 | 121.4 | 110.6 | 121.0 | 0.0 | 174 |
| ppo_resid_v3_left_an1_s0 | stoch | 84.6 | 92.5 | 104.6 | 114.4 | nan | 376 |
| ppo_resid_v3_left_an3_s1 | deter | 108.3 | 118.5 | 107.9 | 118.0 | 0.0 | 177 |
| ppo_resid_v3_left_an3_s1 | stoch | 104.2 | 113.9 | 110.5 | 120.8 | nan | 366 |
| ppo_resid_v3_left_an4_s2 | deter | 97.2 | 106.3 | 96.7 | 105.8 | 0.0 | 178 |
| ppo_resid_v3_left_an4_s2 | stoch | 98.8 | 108.0 | 98.4 | 107.6 | 0.0 | 186 |
| ppo_resid_v3_left_an5_s3 | deter | 10.0 | 10.9 | 94.4 | 103.3 | nan | 390 |
| ppo_resid_v3_left_an5_s3 | stoch | 14.4 | 15.8 | 140.6 | 153.7 | nan | 393 |
| best_carry_analytic<br>ppo_resid_v3_left_an2_s0 | deter | 112.4 | 122.9 | 111.9 | 122.4 | 0.0 | 175 |
| best_carry_analytic<br>ppo_resid_v3_left_an2_s0 | stoch | 88.1 | 96.3 | 114.9 | 125.6 | nan | 386 |
| ppo_resid_v3_left_an6_s4 | deter | 104.4 | 114.1 | 110.6 | 121.0 | nan | 366 |
| ppo_resid_v3_left_an6_s4 | stoch | 81.9 | 89.5 | 148.0 | 161.8 | nan | 381 |
| ppo_resid_v3_left_an8_s6 | deter | 10.9 | 11.9 | 96.1 | 105.1 | nan | 392 |
| ppo_resid_v3_left_an8_s6 | stoch | 11.5 | 12.6 | 74.7 | 81.7 | nan | 394 |
| ppo_resid_v3_left_an7_s5 | deter | 9.2 | 10.0 | 120.3 | 131.6 | nan | 388 |
| ppo_resid_v3_left_an7_s5 | stoch | 7.9 | 8.6 | 147.2 | 161.0 | nan | 390 |
| ppo_resid_v3_left_an9_s7 | deter | 103.5 | 113.2 | 103.1 | 112.7 | 0.0 | 157 |
| ppo_resid_v3_left_an9_s7 | stoch | 81.9 | 89.6 | 126.1 | 138.0 | nan | 368 |
| ppo_resid_v3_left_an10_s8 | deter | 108.7 | 118.9 | 127.1 | 139.0 | nan | 354 |
| ppo_resid_v3_left_an10_s8 | stoch | 61.0 | 66.7 | 128.8 | 140.8 | nan | 369 |
| ppo_resid_v3_left_fast1_s10 | deter | 15.8 | 17.3 | 15.4 | 16.8 | 0.0 | 26 |
| ppo_resid_v3_left_fast1_s10 | stoch | 15.0 | 16.5 | 14.7 | 16.0 | 0.0 | 23 |
| best_gate_flat_123mph<br>ppo_resid_v3_left_fast2_s11 | deter | 15.0 | 16.4 | 14.6 | 16.0 | 0.0 | 24 |
| best_gate_flat_123mph<br>ppo_resid_v3_left_fast2_s11 | stoch | 15.0 | 16.5 | 28.3 | 30.9 | nan | 392 |
| ppo_v3tiny_s22 | deter | 105.7 | 115.6 | 126.8 | 138.7 | nan | 305 |
| ppo_v3tiny_s22 | stoch | 100.0 | 109.4 | 121.3 | 132.6 | nan | 301 |
| ppo_v3tiny_s23 | deter | 94.3 | 103.1 | 116.0 | 126.8 | nan | 307 |
| ppo_v3tiny_s23 | stoch | 99.1 | 108.3 | 126.0 | 137.8 | nan | 302 |
| ppo_v3tiny_s21 | deter | 84.5 | 92.4 | 111.4 | 121.8 | nan | 302 |
| ppo_v3tiny_s21 | stoch | 102.6 | 112.2 | 118.3 | 129.4 | nan | 297 |
| ppo_v3flt_all_s33 | deter | 95.0 | 103.9 | 100.3 | 109.7 | nan | 311 |
| ppo_v3flt_all_s33 | stoch | 99.2 | 108.4 | 110.0 | 120.3 | nan | 307 |
| best_learned_yaw_s32<br>ppo_v3flt_yaw_s32 | deter | 113.9 | 124.6 | 113.5 | 124.1 | 0.0 | 203 |
| best_learned_yaw_s32<br>ppo_v3flt_yaw_s32 | stoch | 114.0 | 124.6 | 113.6 | 124.2 | 0.0 | 203 |
| best_learned_yaw_s31<br>ppo_v3flt_yaw_s31 | deter | 114.3 | 124.9 | 113.9 | 124.5 | 0.0 | 203 |
| best_learned_yaw_s31<br>ppo_v3flt_yaw_s31 | stoch | 114.8 | 125.5 | 114.4 | 125.1 | 0.0 | 203 |
| ppo_v4yaw_s43 | deter | 243.0 | 265.8 | 260.7 | 285.1 | nan | 338 |
| ppo_v4yaw_s43 | stoch | 244.3 | 267.1 | 262.0 | 286.5 | nan | 338 |
| ppo_v4yaw_s42 | deter | 243.3 | 266.1 | 261.0 | 285.4 | nan | 338 |
| ppo_v4yaw_s42 | stoch | 250.0 | 273.3 | 261.6 | 286.1 | nan | 338 |
| best_v4yaw_s41<br>ppo_v4yaw_s41 | deter | 243.6 | 266.4 | 261.3 | 285.8 | nan | 338 |
| best_v4yaw_s41<br>ppo_v4yaw_s41 | stoch | 243.4 | 266.2 | 261.1 | 285.6 | nan | 338 |
| imit2_w075_s51 | deter | 49.3 | 53.9 | 126.2 | 138.0 | nan | 313 |
| imit2_w075_s51 | stoch | 80.6 | 88.1 | 124.3 | 135.9 | nan | 308 |
| imit2_w075_s52 | deter | 117.8 | 128.9 | 139.5 | 152.6 | nan | 310 |
| imit2_w075_s52 | stoch | 103.2 | 112.9 | 130.7 | 143.0 | nan | 318 |
| imit2_w075_s53 | deter | 116.9 | 127.8 | 138.8 | 151.8 | nan | 320 |
| imit2_w075_s53 | stoch | 96.1 | 105.1 | 112.3 | 122.8 | nan | 305 |
| imit3_w075_s51 | deter | 113.1 | 123.7 | 112.7 | 123.2 | 0.0 | 199 |
| imit3_w075_s51 | stoch | 112.4 | 122.9 | 112.0 | 122.5 | 0.0 | 199 |
| imit3_w075_s52 | deter | 108.4 | 118.6 | 124.6 | 136.2 | nan | 303 |
| imit3_w075_s52 | stoch | 108.2 | 118.3 | 124.3 | 135.9 | nan | 302 |
| imit3_w075_s53 | deter | 112.0 | 122.4 | 133.7 | 146.3 | nan | 307 |
| imit3_w075_s53 | stoch | 114.6 | 125.4 | 131.1 | 143.4 | nan | 313 |
| imit3_w050_s51 | deter | 119.4 | 130.6 | 119.0 | 130.1 | 0.0 | 207 |
| imit3_w050_s51 | stoch | 120.5 | 131.7 | 120.1 | 131.3 | 0.0 | 204 |
| best_imit_w050_s52<br>imit3_w050_s52 | deter | 107.7 | 117.8 | 107.3 | 117.4 | 0.0 | 178 |
| best_imit_w050_s52<br>imit3_w050_s52 | stoch | 109.7 | 120.0 | 109.3 | 119.5 | 0.0 | 187 |
| imit3_w025_s51 | deter | 105.1 | 114.9 | 104.7 | 114.5 | 0.0 | 182 |
| imit3_w025_s51 | stoch | 106.2 | 116.1 | 105.8 | 115.7 | 0.0 | 172 |
| imit3_w025_s52 | deter | 88.9 | 97.3 | 116.7 | 127.6 | nan | 313 |
| imit3_w025_s52 | stoch | 91.4 | 100.0 | 124.8 | 136.5 | nan | 311 |
| imit3_w000_s52 | deter | 105.1 | 115.0 | 127.0 | 138.9 | nan | 313 |
| imit3_w000_s52 | stoch | 91.9 | 100.5 | 119.4 | 130.6 | nan | 318 |
| best_imit_scriptfree_s51_NOTPASS_lat3.56<br>imit3_w000_s51 | deter | 109.4 | 119.7 | 125.6 | 137.3 | nan | 303 |
| best_imit_scriptfree_s51_NOTPASS_lat3.56<br>imit3_w000_s51 | stoch | 111.3 | 121.7 | 127.4 | 139.3 | nan | 301 |
| imit4_w000_s52 | deter | 88.4 | 96.6 | 116.1 | 126.9 | nan | 313 |
| imit4_w000_s52 | stoch | 84.6 | 92.5 | 100.6 | 110.0 | nan | 301 |
| imit4_w000_s51 | deter | 93.5 | 102.3 | 121.0 | 132.4 | nan | 311 |
| imit4_w000_s51 | stoch | 91.0 | 99.6 | 107.0 | 117.1 | nan | 306 |
| imit5_w000_s52 | deter | 103.9 | 113.6 | 126.1 | 137.9 | nan | 322 |
| imit5_w000_s52 | stoch | 105.6 | 115.5 | 110.8 | 121.1 | nan | 304 |
| best_imit_scriptfree_s51_seed4000-8000only<br>imit5_w000_s51 | deter | 93.9 | 102.7 | 109.6 | 119.8 | nan | 304 |
| best_imit_scriptfree_s51_seed4000-8000only<br>imit5_w000_s51 | stoch | 91.6 | 100.2 | 112.8 | 123.3 | nan | 297 |
| ppo_v4power_s61 | deter | 279.2 | 305.3 | 278.8 | 304.9 | 0.0 | 363 |
| ppo_v4power_s61 | stoch | 279.6 | 305.8 | 279.2 | 305.3 | 0.0 | 363 |
| ppo_v4power_s62 | deter | 279.7 | 305.9 | 279.3 | 305.4 | 0.0 | 363 |
| ppo_v4power_s62 | stoch | 279.2 | 305.3 | 278.8 | 304.9 | 0.0 | 363 |
| imit7_w000_s51 | deter | 89.2 | 97.6 | 116.8 | 127.7 | nan | 308 |
| imit7_w000_s51 | stoch | 102.3 | 111.9 | 101.9 | 111.5 | 0.0 | 193 |
| ppo_v4power48_s71 | deter | 311.4 | 340.5 | 311.0 | 340.1 | 0.0 | 362 |
| ppo_v4power48_s71 | stoch | 311.2 | 340.3 | 310.8 | 339.8 | 0.0 | 361 |
| imit8_w000_s51 | deter | 96.6 | 105.7 | 124.3 | 135.9 | nan | 315 |
| imit8_w000_s51 | stoch | 93.6 | 102.3 | 132.2 | 144.6 | nan | 315 |
| imit9_w000_s53 | deter | 115.9 | 126.7 | 115.5 | 126.3 | 0.0 | 200 |
| imit9_w000_s53 | stoch | 113.8 | 124.5 | 113.4 | 124.1 | 0.0 | 203 |
| imit10_w000_s51_tr | deter | 101.5 | 111.0 | 101.1 | 110.6 | nan | 138 |
| imit10_w000_s51_tr | stoch | 93.1 | 101.8 | 105.0 | 114.9 | nan | 300 |
| best_imit_scriptfree_elbow48_s51<br>imit9_w000_s51 | deter | 120.0 | 131.2 | 119.6 | 130.8 | 0.0 | 201 |
| best_imit_scriptfree_elbow48_s51<br>imit9_w000_s51 | stoch | 117.0 | 127.9 | 116.6 | 127.5 | 0.0 | 203 |
| imit9_w000_s52 | deter | 120.1 | 131.3 | 119.7 | 130.9 | 0.0 | 202 |
| imit9_w000_s52 | stoch | 119.3 | 130.5 | 118.9 | 130.0 | 0.0 | 203 |
| imit13_w000_s51 | deter | 110.7 | 121.1 | 110.3 | 120.7 | nan | 200 |
| imit13_w000_s51 | stoch | 111.1 | 121.5 | 110.7 | 121.1 | nan | 201 |
| imit13_w000_s52 | deter | 113.1 | 123.7 | 118.4 | 129.5 | nan | 308 |
| imit13_w000_s52 | stoch | 111.4 | 121.9 | 116.7 | 127.7 | nan | 312 |
| imit14_w000_s51 | deter | 116.1 | 127.0 | 115.7 | 126.6 | nan | 203 |
| imit14_w000_s51 | stoch | 118.1 | 129.1 | 119.1 | 130.2 | nan | 204 |
| imit15_dart_s51 | deter | 117.1 | 128.1 | 116.7 | 127.6 | 0.0 | 200 |
| imit15_dart_s51 | stoch | 115.7 | 126.5 | 115.3 | 126.1 | nan | 200 |
| imit16_fs1_dart_s51 | deter | 72.8 | 79.6 | 73.2 | 80.1 | nan | 97 |
| imit16_fs1_dart_s51 | stoch | 73.6 | 80.5 | 73.2 | 80.1 | nan | 96 |
| imit15_dart_s52 | deter | 113.6 | 124.2 | 113.2 | 123.8 | nan | 200 |
| imit15_dart_s52 | stoch | 111.2 | 121.6 | 111.8 | 122.2 | nan | 200 |
| imit15_dart_s53 | deter | 112.9 | 123.4 | 112.5 | 123.0 | 0.0 | 191 |
| imit15_dart_s53 | stoch | 113.2 | 123.8 | 112.8 | 123.4 | 0.0 | 188 |
| imit19_masonmapped_dart_s51 | deter | 58.3 | 63.7 | 57.9 | 63.3 | 0.0 | 71 |
| imit19_masonmapped_dart_s51 | stoch | 59.9 | 65.5 | 59.5 | 65.0 | 0.0 | 74 |
| imit18_power_dart_s51 | deter | 313.9 | 343.3 | 313.5 | 342.8 | 0.0 | 359 |
| imit18_power_dart_s51 | stoch | 313.8 | 343.2 | 313.4 | 342.7 | 0.0 | 360 |
| imit18_power_dart_s52 | deter | 313.9 | 343.3 | 313.5 | 342.8 | 0.0 | 359 |
| imit18_power_dart_s52 | stoch | 313.8 | 343.1 | 313.4 | 342.7 | 0.0 | 360 |
| ppo15_bcreg_s61 | deter | 101.2 | 110.7 | 106.3 | 116.2 | nan | 297 |
| ppo15_bcreg_s61 | stoch | 101.7 | 111.2 | 123.5 | 135.1 | nan | 313 |
| ppo15_bcreg_s62 | deter | 103.6 | 113.3 | 103.2 | 112.8 | 0.0 | 177 |
| ppo15_bcreg_s62 | stoch | 91.4 | 100.0 | 118.2 | 129.3 | nan | 302 |
| ppo15_stoch_s71 | deter | 93.7 | 102.5 | 93.3 | 102.1 | nan | 150 |
| ppo15_stoch_s71 | stoch | 89.4 | 97.8 | 104.9 | 114.8 | nan | 296 |
| ppo15_anneal_s91 | deter | 106.9 | 116.9 | 106.5 | 116.4 | nan | 193 |
| ppo15_anneal_s91 | stoch | 115.1 | 125.9 | 120.1 | 131.3 | nan | 291 |
| imit20_fs1_q23_dart_s51 | deter | 139.6 | 152.7 | 139.2 | 152.3 | 0.0 | 164 |
| imit20_fs1_q23_dart_s51 | stoch | 139.1 | 152.2 | 138.7 | 151.7 | 0.0 | 162 |
| ppo15_klres_s101 | deter | 112.9 | 123.4 | 112.5 | 123.0 | 0.0 | 191 |
| ppo15_klres_s101 | stoch | 110.3 | 120.6 | 115.4 | 126.2 | nan | 301 |
| ppo20_klres_s111 | deter | 139.6 | 152.7 | 139.2 | 152.3 | 0.0 | 164 |
| ppo20_klres_s111 | stoch | 139.3 | 152.4 | 138.9 | 151.9 | 0.0 | 157 |
| ppo20_soft_s121 | deter | 139.8 | 152.9 | 139.4 | 152.5 | 0.0 | 164 |
| ppo20_soft_s121 | stoch | 139.5 | 152.6 | 139.1 | 152.2 | 0.0 | 157 |
| ppo15_soft_s122 | deter | 112.9 | 123.4 | 112.5 | 123.0 | 0.0 | 191 |
| ppo15_soft_s122 | stoch | 104.7 | 114.5 | 115.5 | 126.3 | nan | 310 |

## Configs used (each model evaluated with its own)

- **ppo_scott_prev_backup** (30000 steps): results/train_scott_prev_backup.json; env = `{"curriculum": true, "pin_torso": true, "address_pose": "fixed", "torque_scale": 3.0}`
- **ppo_scott_curr** (30000 steps): launch cmd `--curriculum --pin_torso --address_pose fixed --torque_scale 3 --tag _curr`; no train JSON; env = `{"curriculum": true, "pin_torso": true, "address_pose": "fixed", "torque_scale": 3.0}`
- **ppo_scott_baseline** (30000 steps): launch cmd `--timesteps 30000 --tag _baseline` (default env); no train JSON; env = `{}`
- **ppo_scott/ppo_scott_carry1** (100000 steps): results/train_scott.json; env = `{"curriculum": true, "pin_torso": true, "address_pose": "fixed", "torque_scale": 4.0, "randomize_reset": true, "forward_reward": true, "carry_reward": true, "ball_damping": 0.05, "action_smoothing": 0.3, "shoulder_range_deg": 150.0}`
- **ppo_scott_final2/ppo_scott_prev2_backup** (60000 steps): results/train_scott_final2.json; env = `{"curriculum": true, "pin_torso": true, "address_pose": "fixed", "torque_scale": 3.0, "randomize_reset": true, "forward_reward": true}`
- **ppo_resid_v3_s0** (60000 steps): results/ppo_resid_v3_s0.json args; ball_dz ABSENT in args (flag predates run) -> env default 0.0 used, true training value UNKNOWN; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.4, 0.4, 0.4, 0.25], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 6.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.0, "handedness": "right", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_r2_s0** (60000 steps): results/ppo_resid_v3_r2_s0.json args; ball_dz ABSENT in args (flag predates run) -> env default 0.0 used, true training value UNKNOWN; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.2, 0.2, 0.2, 0.1], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 6.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.0, "handedness": "right", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_r3_s0** (100000 steps): results/ppo_resid_v3_r3_s0.json args; ball_dz ABSENT in args (flag predates run) -> env default 0.0 used, true training value UNKNOWN; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.2, 0.2, 0.2, 0.1], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 6.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.0, "handedness": "right", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **scripted_baseline[ladder cfg: right, loft 6, default ball_x]** (0 steps): zero-residual action with results/ppo_resid_v3_ladder_s0.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.2, 0.2, 0.2, 0.1], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 6.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "right", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm]** (0 steps): zero-residual action; trainer config from TRAINING_NOTES / eval/eval_scripted_cfg.py base + ball_x 0.422, ball_x_noise 0.005, loft 7, left; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.08, 0.05, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 7.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "ball_x": 0.422, "ball_x_noise": 0.005}`
- **ppo_resid_v3_ladder_s0** (150000 steps): results/ppo_resid_v3_ladder_s0.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.2, 0.2, 0.2, 0.1], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 6.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "right", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01]** (0 steps): zero-residual; configs/fast_scripted_v2_lofted.json (trainer) applied over eval/eval_scripted_cfg.py base (as the trainer's eval_scripted_cfg usage); env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.1, 0.08, 0.05, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "loft_deg": -26, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.01, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1}`
- **scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01]** (0 steps): zero-residual; configs/fast_scripted_v3.json (trainer) applied over eval/eval_scripted_cfg.py base (as the trainer's eval_scripted_cfg usage); env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.1, 0.08, 0.05, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "loft_deg": -31, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1}`
- **scripted (not learned) [STOCK motors force_scale 1: fast v3 swing, default elbow]** (0 steps): zero-residual; configs/fast_scripted_v3.json (trainer) applied over eval/eval_scripted_cfg.py base (as the trainer's eval_scripted_cfg usage); env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.1, 0.08, 0.05, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 1.0, "kp": 700, "kd": 23.33, "loft_deg": -31, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1}`
- **ppo_resid_v3_left_an1_s0** (150000 steps): results/ppo_resid_v3_left_an1_s0.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.2, 0.2, 0.2, 0.1], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 8.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an3_s1** (150000 steps): results/ppo_resid_v3_left_an3_s1.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.1, 0.1, 0.03], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 8.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an4_s2** (150000 steps): results/ppo_resid_v3_left_an4_s2.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.1, 0.1, 0.03], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 7.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an5_s3** (150000 steps): results/ppo_resid_v3_left_an5_s3.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.08, 0.05, 0.03], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 7.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **best_carry_analytic/ppo_resid_v3_left_an2_s0** (150000 steps): results/ppo_resid_v3_left_an2_s0.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.1, 0.1, 0.03], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 8.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an6_s4** (150000 steps): results/ppo_resid_v3_left_an6_s4.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.08, 0.05, 0.03], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 7.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an8_s6** (120000 steps): results/ppo_resid_v3_left_an8_s6.json args; env = `{"ball_x": 0.4, "ball_x_noise": 0.015, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.08, 0.05, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 7.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an7_s5** (120000 steps): results/ppo_resid_v3_left_an7_s5.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.04, 0.04, 0.03, 0.02], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 7.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an9_s7** (120000 steps): results/ppo_resid_v3_left_an9_s7.json args; env = `{"ball_x": 0.43, "ball_x_noise": 0.015, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.08, 0.05, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 7.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an10_s8** (120000 steps): results/ppo_resid_v3_left_an10_s8.json args; env = `{"ball_x": 0.422, "ball_x_noise": 0.005, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.08, 0.05, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 7.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_fast1_s10** (100000 steps): results/ppo_resid_v3_left_fast1_s10.json args; env = `{"ball_x": 0.39, "ball_x_noise": 0.005, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6}, "residual_scale": [0.02, 0.02, 0.01, 0.02], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 9.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.5, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **best_gate_flat_123mph/ppo_resid_v3_left_fast2_s11** (100000 steps): results/ppo_resid_v3_left_fast2_s11.json args; env = `{"ball_x": 0.39, "ball_x_noise": 0.005, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6}, "residual_scale": [0.02, 0.02, 0.01, 0.02], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 9.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.5, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_v3tiny_s22** (60000 steps): results/ppo_v3tiny_s22.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_v3tiny_s23** (60000 steps): results/ppo_v3tiny_s23.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_v3tiny_s21** (60000 steps): results/ppo_v3tiny_s21.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_v3flt_all_s33** (30000 steps): results/ppo_v3flt_all_s33.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "tempo_scale": 0.02, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **best_learned_yaw_s32/ppo_v3flt_yaw_s32** (30000 steps): results/ppo_v3flt_yaw_s32.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "tempo_scale": 0.0, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.0, 0.0, 0.0, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **best_learned_yaw_s31/ppo_v3flt_yaw_s31** (30000 steps): results/ppo_v3flt_yaw_s31.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "tempo_scale": 0.0, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.0, 0.0, 0.0, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_v4yaw_s43** (30000 steps): results/ppo_v4yaw_s43.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "tempo_scale": 0.0, "contact_damp": 0.3, "impact_model": {"gain": 1.28, "dz0": -0.019, "k_off": 0.4, "spin_k": 130, "k_side": 3500}, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.065, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.0, 0.0, 0.0, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_v4yaw_s42** (30000 steps): results/ppo_v4yaw_s42.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "tempo_scale": 0.0, "contact_damp": 0.3, "impact_model": {"gain": 1.28, "dz0": -0.019, "k_off": 0.4, "spin_k": 130, "k_side": 3500}, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.065, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.0, 0.0, 0.0, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **best_v4yaw_s41/ppo_v4yaw_s41** (30000 steps): results/ppo_v4yaw_s41.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "tempo_scale": 0.0, "contact_damp": 0.3, "impact_model": {"gain": 1.28, "dz0": -0.019, "k_off": 0.4, "spin_k": 130, "k_side": 3500}, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.065, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.0, 0.0, 0.0, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **imit2_w075_s51** (15000 steps): results/imit2_w075_s51.json env_kwargs_full (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.75, "learn_scale": [0.6, 0.175, 0.0375, 0.0375], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit2_w075_s52** (15000 steps): results/imit2_w075_s52.json env_kwargs_full (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.75, "learn_scale": [0.6, 0.175, 0.0375, 0.0375], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit2_w075_s53** (15000 steps): results/imit2_w075_s53.json env_kwargs_full (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.75, "learn_scale": [0.6, 0.175, 0.0375, 0.0375], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit3_w075_s51** (8000 steps): results/imit3_w075_s51.json env_kwargs_full (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.75, "learn_scale": [0.6, 0.175, 0.0375, 0.0375], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit3_w075_s52** (8000 steps): results/imit3_w075_s52.json env_kwargs_full (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.75, "learn_scale": [0.6, 0.175, 0.0375, 0.0375], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit3_w075_s53** (8000 steps): results/imit3_w075_s53.json env_kwargs_full (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.75, "learn_scale": [0.6, 0.175, 0.0375, 0.0375], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit3_w050_s51** (8000 steps): results/imit3_w050_s51.json env_kwargs_full (script_weight=0.5, learn_scale=[1.2, 0.35, 0.075, 0.075]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.5, "learn_scale": [1.2, 0.35, 0.075, 0.075], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **best_imit_w050_s52/imit3_w050_s52** (8000 steps): results/imit3_w050_s52.json env_kwargs_full (script_weight=0.5, learn_scale=[1.2, 0.35, 0.075, 0.075]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.5, "learn_scale": [1.2, 0.35, 0.075, 0.075], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit3_w025_s51** (8000 steps): results/imit3_w025_s51.json env_kwargs_full (script_weight=0.25, learn_scale=[1.8, 0.525, 0.1125, 0.1125]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.25, "learn_scale": [1.8, 0.525, 0.1125, 0.1125], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit3_w025_s52** (8000 steps): results/imit3_w025_s52.json env_kwargs_full (script_weight=0.25, learn_scale=[1.8, 0.525, 0.1125, 0.1125]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.25, "learn_scale": [1.8, 0.525, 0.1125, 0.1125], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit3_w000_s52** (8000 steps): results/imit3_w000_s52.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **best_imit_scriptfree_s51_NOTPASS_lat3.56/imit3_w000_s51** (8000 steps): results/imit3_w000_s51.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit4_w000_s52** (10000 steps): results/imit4_w000_s52.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.2, "lat_angular": true, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit4_w000_s51** (10000 steps): results/imit4_w000_s51.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.2, "lat_angular": true, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit5_w000_s52** (0 steps): results/imit5_w000_s52.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **best_imit_scriptfree_s51_seed4000-8000only/imit5_w000_s51** (0 steps): results/imit5_w000_s51.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **ppo_v4power_s61** (30000 steps): results/ppo_v4power_s61.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "tempo_scale": 0.0, "contact_damp": 0.3, "flight_steps": 900, "impact_model": {"gain": 1.28, "dz0": 0.017, "k_off": 0.4, "spin_k": 130, "k_side": 3500}, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.06, "t_back": 0.6, "wr_end": -0.1, "yaw_ff": 0.0}, "residual_scale": [0.0, 0.0, 0.0, 0.05], "model_xml": "humanoid_golf_v4_power.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_v4power_s62** (30000 steps): results/ppo_v4power_s62.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "tempo_scale": 0.0, "contact_damp": 0.3, "flight_steps": 900, "impact_model": {"gain": 1.28, "dz0": 0.017, "k_off": 0.4, "spin_k": 130, "k_side": 3500}, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.06, "t_back": 0.6, "wr_end": -0.1, "yaw_ff": 0.0}, "residual_scale": [0.0, 0.0, 0.0, 0.05], "model_xml": "humanoid_golf_v4_power.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **imit7_w000_s51** (0 steps): results/imit7_w000_s51.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **ppo_v4power48_s71** (30000 steps): results/ppo_v4power48_s71.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "tempo_scale": 0.0, "contact_damp": 0.3, "flight_steps": 900, "elbow_base": 0.48, "impact_model": {"gain": 1.28, "dz0": 0.017, "k_off": 0.4, "spin_k": 130, "k_side": 3500}, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.06, "t_back": 0.6, "wr_end": -0.1, "yaw_ff": 0.0}, "residual_scale": [0.0, 0.0, 0.0, 0.05], "model_xml": "humanoid_golf_v4_power.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **imit8_w000_s51** (0 steps): results/imit8_w000_s51.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "elbow_base": 0.48, "_env": "residual"}`
- **imit9_w000_s53** (0 steps): results/imit9_w000_s53.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "elbow_base": 0.48, "_env": "residual"}`
- **imit10_w000_s51_tr** (20000 steps): results/imit10_w000_s51_tr.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": true, "key_weight": 2.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "elbow_base": 0.48, "_env": "residual"}`
- **best_imit_scriptfree_elbow48_s51/imit9_w000_s51** (0 steps): results/imit9_w000_s51.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "elbow_base": 0.48, "_env": "residual"}`
- **imit9_w000_s52** (0 steps): results/imit9_w000_s52.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "elbow_base": 0.48, "_env": "residual"}`
- **imit13_w000_s51** (0 steps): results/imit13_w000_s51.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.17, "elbow_base": 0.4, "_env": "residual"}`
- **imit13_w000_s52** (0 steps): results/imit13_w000_s52.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.17, "elbow_base": 0.4, "_env": "residual"}`
- **imit14_w000_s51** (0 steps): results/imit14_w000_s51.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0, "wrist_cock": -0.5, "yaw_back": 0.0, "yaw_fin": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": true, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.17, "elbow_base": 0.4, "_env": "residual"}`
- **imit15_dart_s51** (0 steps): results/imit15_dart_s51.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.17, "elbow_base": 0.4, "_env": "residual"}`
- **imit16_fs1_dart_s51** (0 steps): results/imit16_fs1_dart_s51.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 1.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.17, "elbow_base": 0.4, "_env": "residual"}`
- **imit15_dart_s52** (0 steps): results/imit15_dart_s52.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.17, "elbow_base": 0.4, "_env": "residual"}`
- **imit15_dart_s53** (0 steps): results/imit15_dart_s53.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.17, "elbow_base": 0.4, "_env": "residual"}`
- **imit19_masonmapped_dart_s51** (0 steps): results/imit19_masonmapped_dart_s51.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.08, "t_back": 0.6, "wr_end": -0.09, "yaw_ff": 0.0, "el_end": 0.853, "elbow_back": 1.126, "q_fin": -0.43, "wrist_cock": -0.6, "wr_rel_start": 0.6, "wr_lead": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -38, "ball_dz": 0.0, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.17, "elbow_base": 0.4, "_env": "residual"}`
- **imit18_power_dart_s51** (0 steps): results/imit18_power_dart_s51.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.06, "t_back": 0.6, "wr_end": -0.1, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v4_power.xml", "sh_noise": 0.05, "el_noise": 0.1, "contact_damp": 0.3, "impact_model": {"gain": 1.28, "dz0": 0.017, "k_off": 0.4, "spin_k": 130, "k_side": 3500}, "elbow_base": 0.45, "flight_steps": 900, "_env": "residual"}`
- **imit18_power_dart_s52** (0 steps): results/imit18_power_dart_s52.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.06, "t_back": 0.6, "wr_end": -0.1, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v4_power.xml", "sh_noise": 0.05, "el_noise": 0.1, "contact_damp": 0.3, "impact_model": {"gain": 1.28, "dz0": 0.017, "k_off": 0.4, "spin_k": 130, "k_side": 3500}, "elbow_base": 0.45, "flight_steps": 900, "_env": "residual"}`
- **ppo15_bcreg_s61** (0 steps): results/ppo15_bcreg_s61.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.17, "elbow_base": 0.4, "_env": "residual"}`
- **ppo15_bcreg_s62** (0 steps): results/ppo15_bcreg_s62.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.3, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.17, "elbow_base": 0.4, "_env": "residual"}`
- **ppo15_stoch_s71** (0 steps): results/ppo15_stoch_s71.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.17, "elbow_base": 0.4, "_env": "residual"}`
- **ppo15_anneal_s91** (0 steps): results/ppo15_anneal_s91.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.17, "elbow_base": 0.4, "_env": "residual"}`
- **imit20_fs1_q23_dart_s51** (0 steps): results/imit20_fs1_q23_dart_s51.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.3, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -41, "ball_dz": -0.016, "tee_height": 0.04, "force_scale": 1.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.17, "elbow_base": 0.4, "_env": "residual"}`
- **ppo15_klres_s101** (0 steps): results/ppo15_klres_s101.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.17, "elbow_base": 0.4, "_env": "residual"}`
- **ppo20_klres_s111** (0 steps): results/ppo20_klres_s111.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.3, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -41, "ball_dz": -0.016, "tee_height": 0.04, "force_scale": 1.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.17, "elbow_base": 0.4, "_env": "residual"}`
- **ppo20_soft_s121** (0 steps): results/ppo20_soft_s121.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.3, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -41, "ball_dz": -0.016, "tee_height": 0.04, "force_scale": 1.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.17, "elbow_base": 0.4, "_env": "residual"}`
- **ppo15_soft_s122** (0 steps): results/ppo15_soft_s122.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "lat_angular": false, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "track_time_fix": false, "key_weight": 0.0, "key_s": 2.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.17, "elbow_base": 0.4, "_env": "residual"}`

## Showcase qualification criterion

A model qualifies only if ALL hold (deterministic mode unless stated, physics protocol, 50 eps): true contact 100% in both modes; mean carry >= 30 m (documented threshold; the scripted baseline carries ~38 m on this protocol); lateral std <= 2.73 m (the trainer's gate baseline); mean launch elevation >= 5 deg (ball velocity at the end of club-ball contact; rules out the flat/negative-launch exploit). Among qualifiers: highest mean carry over det+stoch.

| Model | contact==100% (det and stoch) | mean carry >= 30 m (det) | lateral std <= 2.73 m (det) | mean launch elev >= 5 deg, not flat (det) | eligible: smash within 1.30-1.49 (ball mph / impact club mph, det) and not hypothetical-demoted (yaw-only residual under boosted impact) | Qualifies |
|---|---|---|---|---|---|---|
| imit18_power_dart_s51 | yes | yes | yes | yes | NO | no |
| imit18_power_dart_s52 | yes | yes | yes | yes | NO | no |
| ppo_v4power48_s71 | yes | yes | yes | yes | NO | no |
| ppo_v4power_s62 | yes | yes | yes | yes | NO | no |
| ppo_v4power_s61 | yes | yes | yes | yes | NO | no |
| ppo_v4yaw_s42 | yes | yes | yes | yes | NO | no |
| ppo_v4yaw_s43 | yes | yes | yes | yes | NO | no |
| best_v4yaw_s41/ppo_v4yaw_s41 | yes | yes | yes | yes | NO | no |
| ppo20_soft_s121 | yes | yes | yes | yes | NO | no |
| ppo20_klres_s111 | yes | yes | yes | yes | NO | no |
| imit20_fs1_q23_dart_s51 | yes | yes | yes | yes | NO | no |
| imit3_w050_s51 | yes | yes | yes | yes | NO | no |
| imit9_w000_s52 | yes | yes | yes | yes | NO | no |
| best_imit_scriptfree_elbow48_s51/imit9_w000_s51 | yes | yes | yes | yes | NO | no |
| imit9_w000_s53 | yes | yes | yes | yes | NO | no |
| best_learned_yaw_s31/ppo_v3flt_yaw_s31 | yes | yes | yes | yes | NO | no |
| best_learned_yaw_s32/ppo_v3flt_yaw_s32 | yes | yes | yes | yes | NO | no |
| imit3_w075_s53 | yes | yes | yes | yes | NO | no |
| imit15_dart_s53 | yes | yes | yes | yes | NO | no |
| imit3_w075_s51 | yes | yes | yes | yes | NO | no |
| imit13_w000_s52 | yes | yes | yes | yes | NO | no |
| ppo15_klres_s101 | yes | yes | yes | yes | NO | no |
| imit2_w075_s52 | yes | yes | NO | yes | NO | no |
| best_imit_scriptfree_s51_NOTPASS_lat3.56/imit3_w000_s51 | yes | yes | NO | yes | NO | no |
| best_imit_w050_s52/imit3_w050_s52 | yes | yes | yes | yes | NO | no |
| imit3_w075_s52 | yes | yes | yes | yes | NO | no |
| imit2_w075_s53 | yes | yes | NO | yes | NO | no |
| ppo_resid_v3_left_an3_s1 | yes | yes | NO | yes | NO | no |
| imit3_w025_s51 | yes | yes | yes | yes | NO | no |
| imit5_w000_s52 | yes | yes | NO | yes | NO | no |
| ppo_v3tiny_s22 | yes | yes | NO | yes | NO | no |
| best_carry_analytic/ppo_resid_v3_left_an2_s0 | yes | yes | NO | yes | NO | no |
| imit3_w000_s52 | yes | yes | NO | yes | NO | no |
| ppo_resid_v3_left_an4_s2 | yes | yes | NO | yes | NO | no |
| ppo_resid_v3_left_an1_s0 | yes | yes | NO | yes | NO | no |
| ppo_v3flt_all_s33 | yes | yes | NO | yes | NO | no |
| ppo_v3tiny_s23 | yes | yes | NO | yes | NO | no |
| imit7_w000_s51 | yes | yes | NO | yes | NO | no |
| imit8_w000_s51 | yes | yes | yes | yes | NO | no |
| ppo_v3tiny_s21 | yes | yes | NO | yes | NO | no |
| ppo_resid_v3_left_an6_s4 | yes | yes | NO | yes | NO | no |
| best_imit_scriptfree_s51_seed4000-8000only/imit5_w000_s51 | yes | yes | NO | yes | NO | no |
| ppo_resid_v3_left_an9_s7 | yes | yes | NO | yes | NO | no |
| imit4_w000_s51 | yes | yes | NO | yes | NO | no |
| imit3_w025_s52 | yes | yes | NO | yes | NO | no |
| imit4_w000_s52 | yes | yes | yes | yes | NO | no |
| ppo_resid_v3_r3_s0 | yes | yes | NO | yes | NO | no |
| ppo_resid_v3_left_an10_s8 | yes | yes | NO | yes | NO | no |
| ppo_resid_v3_ladder_s0 | yes | yes | NO | yes | NO | no |
| ppo_resid_v3_r2_s0 | yes | yes | NO | yes | NO | no |
| imit2_w075_s51 | yes | yes | yes | NO | NO | no |
| imit19_masonmapped_dart_s51 | yes | yes | yes | yes | NO | no |
| ppo_resid_v3_left_fast1_s10 | yes | NO | yes | NO | NO | no |
| best_gate_flat_123mph/ppo_resid_v3_left_fast2_s11 | yes | NO | yes | NO | NO | no |
| ppo_resid_v3_left_an5_s3 | yes | NO | yes | NO | NO | no |
| ppo_resid_v3_left_an8_s6 | yes | NO | yes | NO | NO | no |
| ppo_resid_v3_left_an7_s5 | yes | NO | yes | NO | NO | no |
| imit15_dart_s51 | NO | yes | yes | yes | NO | no |
| imit15_dart_s52 | NO | yes | yes | yes | NO | no |
| ppo15_anneal_s91 | NO | yes | NO | yes | NO | no |
| ppo15_soft_s122 | NO | yes | yes | yes | NO | no |
| ppo15_bcreg_s61 | NO | yes | NO | yes | NO | no |
| ppo15_bcreg_s62 | NO | yes | yes | yes | NO | no |
| imit16_fs1_dart_s51 | NO | yes | NO | yes | NO | no |
| imit14_w000_s51 | NO | yes | NO | yes | NO | no |
| ppo15_stoch_s71 | NO | yes | NO | yes | NO | no |
| imit13_w000_s51 | NO | yes | yes | yes | NO | no |
| imit10_w000_s51_tr | NO | yes | yes | yes | NO | no |
| ppo_scott/ppo_scott_carry1 | NO | NO | yes | yes | NO | no |
| ppo_resid_v3_s0 | NO | yes | NO | yes | NO | no |
| ppo_scott_prev_backup | NO | NO | yes | yes | NO | no |
| ppo_scott_curr | NO | NO | yes | yes | NO | no |
| ppo_scott_final2/ppo_scott_prev2_backup | NO | NO | yes | yes | NO | no |
| ppo_scott_baseline | NO | NO | yes | yes | NO | no |

## Smash flag

Smash = det mean ball mph / det mean impact club mph (ratio of means; NOT smash_factor_mean). Thresholds from eval/launch_report.py (derived, not published): FAIL >1.50, WARN >1.49 or <1.30. Flagged rows cannot be the best/top/showcase row. DEMOTED rows (ppo_v4yaw_*: force_scale 2 + impact gain 1.28 with a yaw-only residual, so effectively the scripted swing under an inflated power impact model) are labelled HYPOTHETICAL and are also ineligible. Boosted v3 policies sit at ~0.9-1.0 (ball barely faster than the club: not a real-contact smash) and the v4/power impact-model rows at 1.44-1.60.

| model | smash | flag | demotion |
|---|---|---|---|
| ppo_scott | 5.090 | FAIL smash>1.50 | - |
| ppo_scott_final2 | 4.128 | FAIL smash>1.50 | - |
| imit18_power_dart_s52 | 1.603 | FAIL smash>1.50 | - |
| imit18_power_dart_s51 | 1.603 | FAIL smash>1.50 | - |
| ppo_v4power48_s71 | 1.585 | FAIL smash>1.50 | HYPOTHETICAL, effectively scripted: force_scale 2 + impact gain 1.28 (inflated), yaw-only residual (res_scale [0.0, 0.0, 0.0, 0.05]); not a stock-motor policy |
| ppo_v4power_s62 | 1.500 | WARN smash>1.49 | HYPOTHETICAL, effectively scripted: force_scale 2 + impact gain 1.28 (inflated), yaw-only residual (res_scale [0.0, 0.0, 0.0, 0.05]); not a stock-motor policy |
| ppo_v4power_s61 | 1.499 | WARN smash>1.49 | HYPOTHETICAL, effectively scripted: force_scale 2 + impact gain 1.28 (inflated), yaw-only residual (res_scale [0.0, 0.0, 0.0, 0.05]); not a stock-motor policy |
| ppo_v4yaw_s42 | 1.440 | ok (1.30-1.49) | HYPOTHETICAL, effectively scripted: force_scale 2 + impact gain 1.28 (inflated), yaw-only residual (res_scale [0.0, 0.0, 0.0, 0.05]); not a stock-motor policy |
| ppo_v4yaw_s43 | 1.440 | ok (1.30-1.49) | HYPOTHETICAL, effectively scripted: force_scale 2 + impact gain 1.28 (inflated), yaw-only residual (res_scale [0.0, 0.0, 0.0, 0.05]); not a stock-motor policy |
| best_v4yaw_s41 | 1.440 | ok (1.30-1.49) | HYPOTHETICAL, effectively scripted: force_scale 2 + impact gain 1.28 (inflated), yaw-only residual (res_scale [0.0, 0.0, 0.0, 0.05]); not a stock-motor policy |
| ppo_scott_curr | 1.322 | ok (1.30-1.49) | - |
| imit3_w050_s51 | 1.008 | WARN smash<1.30 | - |
| imit9_w000_s52 | 1.007 | WARN smash<1.30 | - |
| best_imit_scriptfree_elbow48_s51 | 1.007 | WARN smash<1.30 | - |
| imit9_w000_s53 | 1.006 | WARN smash<1.30 | - |
| imit15_dart_s51 | 1.006 | WARN smash<1.30 | - |
| best_learned_yaw_s31 | 1.005 | WARN smash<1.30 | - |
| best_learned_yaw_s32 | 1.005 | WARN smash<1.30 | - |
| imit15_dart_s53 | 1.004 | WARN smash<1.30 | - |
| ppo15_klres_s101 | 1.004 | WARN smash<1.30 | - |
| ppo15_soft_s122 | 1.004 | WARN smash<1.30 | - |
| imit3_w075_s51 | 1.003 | WARN smash<1.30 | - |
| best_imit_w050_s52 | 1.003 | WARN smash<1.30 | - |
| imit13_w000_s52 | 1.003 | WARN smash<1.30 | - |
| imit20_fs1_q23_dart_s51 | 1.002 | WARN smash<1.30 | - |
| ppo20_klres_s111 | 1.002 | WARN smash<1.30 | - |
| ppo20_soft_s121 | 1.001 | WARN smash<1.30 | - |
| ppo15_bcreg_s62 | 0.999 | WARN smash<1.30 | - |
| imit3_w025_s51 | 0.999 | WARN smash<1.30 | - |
| imit2_w075_s52 | 0.999 | WARN smash<1.30 | - |
| imit3_w075_s52 | 0.998 | WARN smash<1.30 | - |
| imit2_w075_s53 | 0.997 | WARN smash<1.30 | - |
| imit3_w075_s53 | 0.996 | WARN smash<1.30 | - |
| best_imit_scriptfree_s51_NOTPASS_lat3.56 | 0.995 | WARN smash<1.30 | - |
| ppo_v3tiny_s22 | 0.995 | WARN smash<1.30 | - |
| imit3_w000_s52 | 0.993 | WARN smash<1.30 | - |
| imit16_fs1_dart_s51 | 0.992 | WARN smash<1.30 | - |
| imit5_w000_s52 | 0.988 | WARN smash<1.30 | - |
| ppo_scott_prev_backup | 0.988 | WARN smash<1.30 | - |
| imit15_dart_s52 | 0.985 | WARN smash<1.30 | - |
| imit4_w000_s51 | 0.973 | WARN smash<1.30 | - |
| best_imit_scriptfree_s51_seed4000-8000only | 0.971 | WARN smash<1.30 | - |
| imit14_w000_s51 | 0.968 | WARN smash<1.30 | - |
| imit13_w000_s51 | 0.965 | WARN smash<1.30 | - |
| ppo15_bcreg_s61 | 0.965 | WARN smash<1.30 | - |
| ppo15_anneal_s91 | 0.964 | WARN smash<1.30 | - |
| ppo_v3tiny_s23 | 0.961 | WARN smash<1.30 | - |
| ppo_v3flt_all_s33 | 0.961 | WARN smash<1.30 | - |
| imit4_w000_s52 | 0.960 | WARN smash<1.30 | - |
| imit8_w000_s51 | 0.948 | WARN smash<1.30 | - |
| ppo15_stoch_s71 | 0.946 | WARN smash<1.30 | - |
| ppo_v3tiny_s21 | 0.941 | WARN smash<1.30 | - |
| imit7_w000_s51 | 0.938 | WARN smash<1.30 | - |
| imit10_w000_s51_tr | 0.915 | WARN smash<1.30 | - |
| imit3_w025_s52 | 0.911 | WARN smash<1.30 | - |
| imit19_masonmapped_dart_s51 | 0.897 | WARN smash<1.30 | - |
| ppo_resid_v3_left_fast1_s10 | 0.893 | WARN smash<1.30 | - |
| best_gate_flat_123mph | 0.889 | WARN smash<1.30 | - |
| ppo_resid_v3_left_an7_s5 | 0.887 | WARN smash<1.30 | - |
| ppo_resid_v3_left_an10_s8 | 0.883 | WARN smash<1.30 | - |
| ppo_resid_v3_left_an5_s3 | 0.875 | WARN smash<1.30 | - |
| imit2_w075_s51 | 0.858 | WARN smash<1.30 | - |
| ppo_resid_v3_left_an8_s6 | 0.851 | WARN smash<1.30 | - |
| ppo_resid_v3_left_an6_s4 | 0.779 | WARN smash<1.30 | - |
| ppo_resid_v3_left_an3_s1 | 0.765 | WARN smash<1.30 | - |
| best_carry_analytic | 0.762 | WARN smash<1.30 | - |
| ppo_resid_v3_r3_s0 | 0.754 | WARN smash<1.30 | - |
| ppo_resid_v3_left_an1_s0 | 0.744 | WARN smash<1.30 | - |
| ppo_resid_v3_left_an9_s7 | 0.737 | WARN smash<1.30 | - |
| ppo_resid_v3_ladder_s0 | 0.718 | WARN smash<1.30 | - |
| ppo_resid_v3_left_an4_s2 | 0.694 | WARN smash<1.30 | - |
| ppo_resid_v3_r2_s0 | 0.673 | WARN smash<1.30 | - |
| ppo_resid_v3_s0 | 0.658 | WARN smash<1.30 | - |
| ppo_scott_baseline | n/m | n/m smash (no ball/impact speed) | - |

## Swing realism (results/swing_realism.md; eval/swing_realism.py)

A row is eligible for best/top/showcase/qualifying only if the harness PASSES all 8 checks. NOT EVALUATED = unverified = not eligible.

- **ppo_resid_v3_s0**: FAIL (1/8); failed: kinematic_sequence, x_factor, joint_limits, ground_reaction, tempo, ball_flight_tables, smash_spin_flags
- **scripted_baseline[ladder cfg: right, loft 6, default ball_x]**: FAIL (0/8); failed: kinematic_sequence, x_factor, joint_limits, torque_power, ground_reaction, tempo, ball_flight_tables, smash_spin_flags
- **scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm]**: FAIL (0/8); failed: kinematic_sequence, x_factor, joint_limits, torque_power, ground_reaction, tempo, ball_flight_tables, smash_spin_flags
- **scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_en**: FAIL (0/8); failed: kinematic_sequence, x_factor, joint_limits, torque_power, ground_reaction, tempo, ball_flight_tables, smash_spin_flags
- **scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_**: FAIL (0/8); failed: kinematic_sequence, x_factor, joint_limits, torque_power, ground_reaction, tempo, ball_flight_tables, smash_spin_flags
- **scripted (not learned) [STOCK motors force_scale 1: fast v3 swing, default elbow]**: FAIL (0/8); failed: kinematic_sequence, x_factor, joint_limits, torque_power, ground_reaction, tempo, ball_flight_tables, smash_spin_flags
- **ppo_v4yaw_s43**: FAIL (1/8); failed: kinematic_sequence, x_factor, joint_limits, torque_power, ground_reaction, tempo, ball_flight_tables
- **imit16_fs1_dart_s51**: FAIL (0/8); failed: kinematic_sequence, x_factor, joint_limits, torque_power, ground_reaction, tempo, ball_flight_tables, smash_spin_flags
- **imit18_power_dart_s51**: FAIL (0/8); failed: kinematic_sequence, x_factor, joint_limits, torque_power, ground_reaction, tempo, ball_flight_tables, smash_spin_flags
- **imit20_fs1_q23_dart_s51**: FAIL (0/8); failed: kinematic_sequence, x_factor, joint_limits, torque_power, ground_reaction, tempo, ball_flight_tables, smash_spin_flags
- **ppo15_klres_s101**: FAIL (0/8); failed: kinematic_sequence, x_factor, joint_limits, torque_power, ground_reaction, tempo, ball_flight_tables, smash_spin_flags
- **ppo20_klres_s111**: FAIL (0/8); failed: kinematic_sequence, x_factor, joint_limits, torque_power, ground_reaction, tempo, ball_flight_tables, smash_spin_flags
- 67 other rows: NOT EVALUATED.

## Verdicts (from each run's results JSON)

- **ppo15_klres_s101**: = init, not learned (PPO fine-tune from imit15_dart_s53: selected checkpoint = init, policy-vs-script diff unchanged)
- **ppo20_klres_s111**: = init, not learned (PPO fine-tune from imit20_fs1_q23_dart_s51: selected checkpoint = init, policy-vs-script diff unchanged)
- **ppo20_soft_s121**: weakly changed from init, no demonstrated gain (PPO soft-selection from imit20_fs1_q23_dart_s51: selected checkpoint 24 != init, but RMS departure from init is only 0.00038 rad; policy-vs-script RMS 0.0815 -> 0.0374 rad, i.e. moved TOWARD the script, not away from it)
- **ppo15_soft_s122**: = init, not learned (PPO fine-tune from imit15_dart_s53: selected checkpoint = init, policy-vs-script diff unchanged)


**None qualifies.**

Flat/negative-launch flag (mean elevation < 5 deg or >= 50% of shots below it): ppo_scott_prev_backup [sto 4.7 deg], scripted_baseline[ladder cfg: right, loft 6, default ball_x] [det 9.2 deg, sto 9.2 deg], ppo_resid_v3_left_an5_s3 [det -3.8 deg, sto -1.1 deg], ppo_resid_v3_left_an8_s6 [det -5.1 deg, sto -4.9 deg], ppo_resid_v3_left_an7_s5 [det -3.4 deg, sto -3.2 deg], ppo_resid_v3_left_fast1_s10 [det -5.1 deg, sto -5.0 deg], best_gate_flat_123mph/ppo_resid_v3_left_fast2_s11 [det -5.4 deg, sto -5.0 deg], imit2_w075_s51 [det 1.4 deg]

## Left-handed models: trainer gate JSON vs verified (this leaderboard, same protocol: MuJoCo physics, flight tracker, 450-step horizon, deterministic, 50 eps, seeds 4000+)

Verified = this run. Trainer gate = `results/gate_<name>.json` (`eval.eval_gate`; gate: carry > 11.98 m AND lateral std < 2.73 m AND contact >= 99%). Trainer 'analytic' = `results/<name>.json` policy block (100 eps, analytic flight from the MuJoCo launch vector with ASSUMED backspin, episode ends 3 steps after contact) - NOT re-verified here, different protocol.

| Model | Source | Contact | Landed | Mean carry (m) | Lateral std (m) | Peak club mph mean | Gate pass |
|---|---|---|---|---|---|---|---|
| ppo_resid_v3_left_an1_s0 | verified (this run, det) | 100% | 100% | 111.02 | 6.87 | 114.7 | FAIL |
| ppo_resid_v3_left_an1_s0 | trainer gate JSON (det) | 100% | 100% | 110.28 | 7.53 | 114.5 | FAIL |
| ppo_resid_v3_left_an1_s0 | trainer analytic (100 eps) | 100% | 100% | 93.13 | 6.61 | 114.0 (impact) | n/a |
| ppo_resid_v3_left_an3_s1 | verified (this run, det) | 100% | 100% | 108.33 | 6.45 | 114.5 | FAIL |
| ppo_resid_v3_left_an3_s1 | trainer gate JSON (det) | 100% | 100% | 108.60 | 6.74 | 114.6 | FAIL |
| ppo_resid_v3_left_an3_s1 | trainer analytic (100 eps) | 100% | 100% | 87.88 | 5.91 | 114.8 (impact) | n/a |
| ppo_resid_v3_left_an4_s2 | verified (this run, det) | 100% | 100% | 97.16 | 6.69 | 111.8 | FAIL |
| ppo_resid_v3_left_an4_s2 | trainer gate JSON (det) | 100% | 100% | 96.13 | 6.68 | 111.7 | FAIL |
| ppo_resid_v3_left_an4_s2 | trainer analytic (100 eps) | 100% | 100% | 78.82 | 5.87 | 111.5 (impact) | n/a |
| ppo_resid_v3_left_an5_s3 | verified (this run, det) | 100% | 76% | 9.99 | 0.13 | 117.0 | FAIL |
| ppo_resid_v3_left_an5_s3 | trainer gate JSON (det) | 100% | 72% | 9.57 | 0.14 | 117.0 | FAIL |
| ppo_resid_v3_left_an5_s3 | trainer analytic (100 eps) | 100% | 100% | 19.44 | 0.01 | 117.2 (impact) | n/a |
| best_carry_analytic | verified (this run, det) | 100% | 100% | 112.35 | 7.40 | 114.6 | FAIL |
| ppo_resid_v3_left_an6_s4 | verified (this run, det) | 100% | 98% | 104.37 | 7.93 | 113.1 | FAIL |
| ppo_resid_v3_left_an6_s4 | trainer gate JSON (det) | 100% | 98% | 99.80 | 6.95 | 113.0 | FAIL |
| ppo_resid_v3_left_an6_s4 | trainer analytic (100 eps) | 100% | 100% | 89.06 | 6.63 | 112.9 (impact) | n/a |
| ppo_resid_v3_left_an8_s6 | verified (this run, det) | 100% | 76% | 10.85 | 0.10 | 118.5 | FAIL |
| ppo_resid_v3_left_an8_s6 | trainer analytic (100 eps) | 100% | 100% | 24.42 | 0.01 | 118.5 (impact) | n/a |
| ppo_resid_v3_left_an7_s5 | verified (this run, det) | 100% | 68% | 9.17 | 0.26 | 115.3 | FAIL |
| ppo_resid_v3_left_an7_s5 | trainer analytic (100 eps) | 100% | 100% | 19.88 | 0.01 | 115.2 (impact) | n/a |
| ppo_resid_v3_left_an9_s7 | verified (this run, det) | 100% | 100% | 103.50 | 7.20 | 110.5 | FAIL |
| ppo_resid_v3_left_an9_s7 | trainer gate JSON (det) | 100% | 100% | 103.33 | 8.17 | 110.4 | FAIL |
| ppo_resid_v3_left_an9_s7 | trainer analytic (100 eps) | 100% | 100% | 85.32 | 6.61 | 110.5 (impact) | n/a |
| ppo_resid_v3_left_an10_s8 | verified (this run, det) | 100% | 94% | 108.72 | 5.61 | 107.0 | FAIL |
| ppo_resid_v3_left_an10_s8 | trainer analytic (100 eps) | 100% | 100% | 92.72 | 5.74 | 107.2 (impact) | n/a |
| ppo_resid_v3_left_fast1_s10 | verified (this run, det) | 100% | 100% | 15.78 | 0.02 | 122.3 | PASS |
| ppo_resid_v3_left_fast1_s10 | trainer analytic (100 eps) | 100% | 100% | 28.57 | 0.02 | 122.2 (impact) | n/a |
| best_gate_flat_123mph | verified (this run, det) | 100% | 100% | 15.02 | 0.02 | 123.6 | PASS |
| ppo_v3tiny_s22 | verified (this run, det) | 100% | 92% | 105.67 | 4.67 | 118.4 | FAIL |
| ppo_v3tiny_s22 | trainer gate JSON (det) | 100% | 94% | 105.08 | 5.23 | 118.4 | FAIL |
| ppo_v3tiny_s22 | trainer analytic (100 eps) | 100% | 100% | 140.62 | 0.14 | 118.4 (impact) | n/a |
| ppo_v3tiny_s23 | verified (this run, det) | 100% | 92% | 94.31 | 2.84 | 119.0 | FAIL |
| ppo_v3tiny_s23 | trainer gate JSON (det) | 100% | 87% | 93.63 | 4.43 | 118.9 | FAIL |
| ppo_v3tiny_s23 | trainer analytic (100 eps) | 100% | 100% | 131.80 | 0.14 | 118.9 (impact) | n/a |
| ppo_v3tiny_s21 | verified (this run, det) | 100% | 90% | 84.49 | 4.43 | 119.0 | FAIL |
| ppo_v3tiny_s21 | trainer gate JSON (det) | 100% | 88% | 86.42 | 6.45 | 118.9 | FAIL |
| ppo_v3tiny_s21 | trainer analytic (100 eps) | 100% | 100% | 120.95 | 0.10 | 119.0 (impact) | n/a |
| ppo_v3flt_all_s33 | verified (this run, det) | 100% | 98% | 95.00 | 5.13 | 120.3 | FAIL |
| ppo_v3flt_all_s33 | trainer gate JSON (det) | 100% | 99% | 104.98 | 10.23 | 120.3 | FAIL |
| ppo_v3flt_all_s33 | trainer analytic (100 eps) | 100% | 97% | 100.59 | 9.35 | 120.3 (impact) | n/a |
| best_learned_yaw_s32 | verified (this run, det) | 100% | 100% | 113.90 | 1.59 | 120.3 | PASS |
| best_learned_yaw_s31 | verified (this run, det) | 100% | 100% | 114.25 | 1.61 | 120.3 | PASS |
| ppo_v4yaw_s43 | verified (this run, det) | 100% | 94% | 243.01 | 1.65 | 128.3 | PASS |
| ppo_v4yaw_s43 | trainer gate JSON (det) | 100% | 94% | 242.63 | 2.31 | 128.3 | PASS |
| ppo_v4yaw_s43 | trainer analytic (100 eps) | 100% | 94% | 246.47 | 2.14 | 128.3 (impact) | n/a |
| ppo_v4yaw_s42 | verified (this run, det) | 100% | 94% | 243.29 | 1.66 | 128.3 | PASS |
| ppo_v4yaw_s42 | trainer gate JSON (det) | 100% | 94% | 242.96 | 2.37 | 128.3 | PASS |
| ppo_v4yaw_s42 | trainer analytic (100 eps) | 100% | 94% | 246.25 | 2.16 | 128.3 (impact) | n/a |
| best_v4yaw_s41 | verified (this run, det) | 100% | 94% | 243.59 | 1.67 | 128.3 | PASS |
| imit2_w075_s51 | verified (this run, det) | 100% | 72% | 49.28 | 0.58 | 120.5 | PASS |
| imit2_w075_s51 | trainer gate JSON (det) | 100% | 67% | 45.78 | 2.24 | 120.5 | PASS |
| imit2_w075_s51 | trainer analytic (100 eps) | 100% | 68% | 51.42 | 0.61 | 120.4 (impact) | n/a |
| imit2_w075_s52 | verified (this run, det) | 100% | 92% | 117.84 | 2.96 | 120.6 | FAIL |
| imit2_w075_s52 | trainer gate JSON (det) | 100% | 93% | 112.62 | 2.82 | 120.5 | FAIL |
| imit2_w075_s52 | trainer analytic (100 eps) | 100% | 100% | 114.15 | 2.29 | 120.6 (impact) | n/a |
| imit2_w075_s53 | verified (this run, det) | 100% | 92% | 116.88 | 3.57 | 120.7 | FAIL |
| imit2_w075_s53 | trainer gate JSON (det) | 100% | 91% | 109.78 | 3.04 | 120.7 | FAIL |
| imit2_w075_s53 | trainer analytic (100 eps) | 100% | 100% | 114.43 | 2.22 | 120.7 (impact) | n/a |
| imit3_w075_s51 | verified (this run, det) | 100% | 100% | 113.09 | 0.73 | 120.2 | PASS |
| imit3_w075_s51 | trainer gate JSON (det) | 100% | 100% | 113.39 | 1.51 | 120.2 | PASS |
| imit3_w075_s51 | trainer analytic (100 eps) | 100% | 100% | 106.96 | 0.35 | 120.2 (impact) | n/a |
| imit3_w075_s52 | verified (this run, det) | 100% | 94% | 108.42 | 1.10 | 120.3 | PASS |
| imit3_w075_s52 | trainer gate JSON (det) | 100% | 97% | 110.77 | 1.73 | 120.3 | PASS |
| imit3_w075_s52 | trainer analytic (100 eps) | 100% | 100% | 106.09 | 0.36 | 120.4 (impact) | n/a |
| imit3_w075_s53 | verified (this run, det) | 100% | 92% | 111.95 | 2.27 | 120.3 | PASS |
| imit3_w075_s53 | trainer gate JSON (det) | 100% | 96% | 111.73 | 3.04 | 120.3 | FAIL |
| imit3_w075_s53 | trainer analytic (100 eps) | 100% | 100% | 110.97 | 1.36 | 120.3 (impact) | n/a |
| imit3_w050_s51 | verified (this run, det) | 100% | 100% | 119.39 | 2.20 | 120.4 | PASS |
| imit3_w050_s51 | trainer gate JSON (det) | 100% | 100% | 117.43 | 2.39 | 120.4 | PASS |
| imit3_w050_s51 | trainer analytic (100 eps) | 100% | 98% | 111.12 | 1.57 | 120.3 (impact) | n/a |
| best_imit_w050_s52 | verified (this run, det) | 100% | 100% | 107.74 | 0.23 | 120.4 | PASS |
| imit3_w025_s51 | verified (this run, det) | 100% | 100% | 105.11 | 0.11 | 120.5 | PASS |
| imit3_w025_s51 | trainer gate JSON (det) | 100% | 100% | 108.48 | 2.97 | 120.4 | FAIL |
| imit3_w025_s51 | trainer analytic (100 eps) | 100% | 90% | 85.00 | 1.94 | 116.8 (impact) | n/a |
| imit3_w025_s52 | verified (this run, det) | 100% | 90% | 88.95 | 5.31 | 123.3 | FAIL |
| imit3_w025_s52 | trainer gate JSON (det) | 100% | 92% | 94.73 | 6.25 | 122.8 | FAIL |
| imit3_w025_s52 | trainer analytic (100 eps) | 100% | 100% | 107.35 | 0.43 | 120.5 (impact) | n/a |
| imit3_w000_s52 | verified (this run, det) | 100% | 92% | 105.15 | 5.53 | 119.1 | FAIL |
| imit3_w000_s52 | trainer gate JSON (det) | 100% | 91% | 90.02 | 5.04 | 118.3 | FAIL |
| imit3_w000_s52 | trainer analytic (100 eps) | 100% | 100% | 106.79 | 5.02 | 120.6 (impact) | n/a |
| best_imit_scriptfree_s51_NOTPASS_lat3.56 | verified (this run, det) | 100% | 94% | 109.44 | 3.97 | 120.6 | FAIL |
| imit4_w000_s52 | verified (this run, det) | 100% | 90% | 88.38 | 2.68 | 118.2 | PASS |
| imit4_w000_s52 | trainer analytic (100 eps) | 100% | 90% | 88.85 | 3.58 | 117.9 (impact) | n/a |
| imit4_w000_s51 | verified (this run, det) | 100% | 90% | 93.51 | 5.43 | 118.0 | FAIL |
| imit4_w000_s51 | trainer analytic (100 eps) | 100% | 94% | 69.38 | 3.82 | 110.8 (impact) | n/a |
| imit5_w000_s52 | verified (this run, det) | 100% | 92% | 103.88 | 4.42 | 120.9 | FAIL |
| imit5_w000_s52 | trainer analytic (100 eps) | 100% | 99% | 115.92 | 3.83 | 120.3 (impact) | n/a |
| best_imit_scriptfree_s51_seed4000-8000only | verified (this run, det) | 100% | 94% | 93.87 | 4.80 | 119.3 | FAIL |
| ppo_v4power_s61 | verified (this run, det) | 100% | 100% | 279.19 | 1.82 | 132.3 | PASS |
| ppo_v4power_s61 | trainer gate JSON (det) | 100% | 100% | 278.05 | 2.34 | 132.3 | PASS |
| ppo_v4power_s61 | trainer analytic (100 eps) | 100% | 100% | 280.59 | 2.40 | 132.3 (impact) | n/a |
| ppo_v4power_s62 | verified (this run, det) | 100% | 100% | 279.69 | 1.86 | 132.3 | PASS |
| ppo_v4power_s62 | trainer gate JSON (det) | 100% | 100% | 278.02 | 2.28 | 132.3 | PASS |
| ppo_v4power_s62 | trainer analytic (100 eps) | 100% | 100% | 280.18 | 2.40 | 132.3 (impact) | n/a |
| imit7_w000_s51 | verified (this run, det) | 100% | 90% | 89.21 | 8.02 | 120.7 | FAIL |
| imit7_w000_s51 | trainer gate JSON (det) | 100% | 100% | 109.50 | 4.55 | 120.4 | FAIL |
| imit7_w000_s51 | trainer analytic (100 eps) | 100% | 98% | 104.34 | 1.48 | 120.3 (impact) | n/a |
| ppo_v4power48_s71 | verified (this run, det) | 100% | 100% | 311.39 | 2.15 | 132.4 | PASS |
| ppo_v4power48_s71 | trainer analytic (100 eps) | 100% | 100% | 303.90 | 2.58 | 132.4 (impact) | n/a |
| imit8_w000_s51 | verified (this run, det) | 100% | 90% | 96.63 | 0.25 | 121.3 | PASS |
| imit8_w000_s51 | trainer gate JSON (det) | 100% | 79% | 81.62 | 1.42 | 121.7 | FAIL |
| imit8_w000_s51 | trainer analytic (100 eps) | 100% | 86% | 79.67 | 0.77 | 122.2 (impact) | n/a |
| imit9_w000_s53 | verified (this run, det) | 100% | 100% | 115.87 | 0.70 | 120.5 | PASS |
| imit9_w000_s53 | trainer analytic (100 eps) | 100% | 100% | 119.23 | 1.18 | 120.4 (impact) | n/a |
| imit10_w000_s51_tr | verified (this run, det) | 94% | 94% | 101.49 | 0.05 | 112.2 | FAIL |
| imit10_w000_s51_tr | trainer analytic (100 eps) | 96% | 88% | 94.56 | 0.20 | 106.4 (impact) | n/a |
| best_imit_scriptfree_elbow48_s51 | verified (this run, det) | 100% | 100% | 119.97 | 0.96 | 120.5 | PASS |
| imit9_w000_s52 | verified (this run, det) | 100% | 100% | 120.08 | 0.99 | 120.5 | PASS |
| imit9_w000_s52 | trainer analytic (100 eps) | 100% | 100% | 116.20 | 0.30 | 120.5 (impact) | n/a |
| imit13_w000_s51 | verified (this run, det) | 96% | 96% | 110.73 | 1.63 | 118.9 | FAIL |
| imit13_w000_s51 | trainer analytic (100 eps) | 98% | 97% | 109.12 | 2.58 | 120.4 (impact) | n/a |
| imit13_w000_s52 | verified (this run, det) | 100% | 98% | 113.13 | 1.67 | 120.3 | PASS |
| imit13_w000_s52 | trainer analytic (100 eps) | 100% | 100% | 110.49 | 3.46 | 120.4 (impact) | n/a |
| imit14_w000_s51 | verified (this run, det) | 96% | 96% | 116.11 | 5.77 | 117.8 | FAIL |
| imit14_w000_s51 | trainer analytic (100 eps) | 100% | 100% | 124.79 | 9.98 | 119.3 (impact) | n/a |
| imit15_dart_s51 | verified (this run, det) | 100% | 100% | 117.11 | 1.63 | 120.3 | PASS |
| imit15_dart_s51 | trainer analytic (100 eps) | 100% | 100% | 116.36 | 2.78 | 120.4 (impact) | n/a |
| imit16_fs1_dart_s51 | verified (this run, det) | 100% | 98% | 72.76 | 3.15 | 97.9 | FAIL |
| imit16_fs1_dart_s51 | trainer gate JSON (det) | 100% | 99% | 74.18 | 1.23 | 98.1 | PASS |
| imit16_fs1_dart_s51 | trainer analytic (100 eps) | 100% | 100% | 73.96 | 0.47 | 98.3 (impact) | n/a |
| imit15_dart_s52 | verified (this run, det) | 98% | 98% | 113.55 | 1.69 | 119.4 | FAIL |
| imit15_dart_s52 | trainer gate JSON (det) | 99% | 99% | 113.03 | 1.50 | 119.9 | PASS |
| imit15_dart_s52 | trainer analytic (100 eps) | 100% | 100% | 115.21 | 4.37 | 120.4 (impact) | n/a |
| imit15_dart_s53 | verified (this run, det) | 100% | 100% | 112.86 | 1.27 | 120.3 | PASS |
| imit15_dart_s53 | trainer analytic (100 eps) | 100% | 100% | 114.45 | 2.02 | 120.3 (impact) | n/a |
| imit19_masonmapped_dart_s51 | verified (this run, det) | 100% | 100% | 58.26 | 0.14 | 87.6 | PASS |
| imit19_masonmapped_dart_s51 | trainer analytic (100 eps) | 100% | 100% | 59.49 | 0.05 | 75.1 (impact) | n/a |
| imit18_power_dart_s51 | verified (this run, det) | 100% | 100% | 313.89 | 2.18 | 132.4 | PASS |
| imit18_power_dart_s51 | trainer analytic (100 eps) | 100% | 100% | 305.65 | 2.62 | 132.4 (impact) | n/a |
| imit18_power_dart_s52 | verified (this run, det) | 100% | 100% | 313.89 | 2.18 | 132.4 | PASS |
| imit18_power_dart_s52 | trainer analytic (100 eps) | 100% | 100% | 305.96 | 2.61 | 132.4 (impact) | n/a |
| ppo15_bcreg_s61 | verified (this run, det) | 98% | 96% | 101.22 | 11.19 | 118.3 | FAIL |
| ppo15_bcreg_s61 | trainer analytic (100 eps) | 100% | 100% | 108.32 | 8.50 | 119.0 (impact) | n/a |
| ppo15_bcreg_s62 | verified (this run, det) | 100% | 100% | 103.58 | 0.18 | 118.4 | PASS |
| ppo15_bcreg_s62 | trainer analytic (100 eps) | 100% | 100% | 107.33 | 0.80 | 118.5 (impact) | n/a |
| ppo15_stoch_s71 | verified (this run, det) | 96% | 96% | 93.72 | 2.95 | 114.5 | FAIL |
| ppo15_stoch_s71 | trainer analytic (100 eps) | 100% | 100% | 99.02 | 3.66 | 115.9 (impact) | n/a |
| ppo15_anneal_s91 | verified (this run, det) | 98% | 98% | 106.85 | 9.80 | 120.8 | FAIL |
| ppo15_anneal_s91 | trainer analytic (100 eps) | 100% | 99% | 108.87 | 7.29 | 121.9 (impact) | n/a |
| imit20_fs1_q23_dart_s51 | verified (this run, det) | 100% | 100% | 139.63 | 2.29 | 100.7 | PASS |
| imit20_fs1_q23_dart_s51 | trainer analytic (100 eps) | 100% | 100% | 139.96 | 0.69 | 100.7 (impact) | n/a |
| ppo15_klres_s101 | verified (this run, det) | 100% | 100% | 112.86 | 1.27 | 120.3 | PASS |
| ppo15_klres_s101 | trainer analytic (100 eps) | 100% | 100% | 114.45 | 2.02 | 120.3 (impact) | n/a |
| ppo20_klres_s111 | verified (this run, det) | 100% | 100% | 139.63 | 2.29 | 100.7 | PASS |
| ppo20_klres_s111 | trainer analytic (100 eps) | 100% | 100% | 139.96 | 0.69 | 100.7 (impact) | n/a |
| ppo20_soft_s121 | verified (this run, det) | 100% | 100% | 139.82 | 1.95 | 100.7 | PASS |
| ppo20_soft_s121 | trainer analytic (100 eps) | 100% | 100% | 140.05 | 0.39 | 100.6 (impact) | n/a |
| ppo15_soft_s122 | verified (this run, det) | 100% | 100% | 112.86 | 1.27 | 120.3 | PASS |
| ppo15_soft_s122 | trainer analytic (100 eps) | 100% | 100% | 114.45 | 2.02 | 120.3 (impact) | n/a |

## DTW vs NATIVE Mason v2 references [arm columns VOID: lead/trail arm bug, see Trainer] (recommended, non-partial, license self_owned/commercial_ok; mean DTW rad: all 11 joints / upper-body 5)

**DTW provenance:** scored against `data/references/mason_v2_*.npz` (npz mtimes unchanged, 2026-10-16 03:39); these do NOT read `mason_target_features.json` or `mason_impact_geometry_targets.json`, so the Data Agent regeneration (0.4 s timing fix) does not alter any DTW number here, and no DTW value used pre-fix target values. `mason_impact_geometry_targets.json` was not present in this working tree when this was generated.  **CAVEATS: 2D-proxy joint angles from single-view MediaPipe, screen-recorded ~30 fps (tempo +-15%), not retargeted to the MuJoCo humanoid, no club data, leg joints weak; native left-handed footage, `right_*` columns = anatomical right = LEAD arm of a left-hander, whereas the env's `right_*` joints are the swinging arm of its own model (mapping/sign conventions NOT calibrated). Indicative only. MultiSense (right-handed, CC0, different protocol) deliberately NOT scored here.**

Refs: `p1_s06` (q=0.76, oblique, mirrored=False), `p1_s11` (q=0.76, face_on, mirrored=False), `p2_s02` (q=0.75, down_the_line, mirrored=False), `p2_s01` (q=0.7, down_the_line, mirrored=False), `p1_s04` (q=0.69, down_the_line, mirrored=False), `p1_s03` (q=0.69, down_the_line, mirrored=False), `p2_s13` (q=0.68, down_the_line, mirrored=False), `p2_s10` (q=0.68, down_the_line, mirrored=False), `p1_s05` (q=0.66, down_the_line, mirrored=False), `p2_s11` (q=0.66, down_the_line, mirrored=False), `p3_s09_unmirrored` (q=0.83, down_the_line, mirrored=True)

| Model(s) | Mode | p1_s06 | p1_s11 | p2_s02 | p2_s01 | p1_s04 | p1_s03 | p2_s13 | p2_s10 | p1_s05 | p2_s11 | p3_s09_unmirrored | mean over refs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ppo_scott_prev_backup | deter | 2.358 / 1.914 | 2.452 / 1.592 | 2.516 / 1.924 | 2.473 / 2.013 | 2.384 / 1.795 | 2.230 / 1.679 | 2.267 / 1.611 | 2.301 / 1.799 | 2.382 / 1.864 | 2.230 / 1.763 | 2.361 / 1.693 | 2.359 / 1.786 |
| ppo_scott_prev_backup | stoch | 3.384 / 2.627 | 3.528 / 2.695 | 3.531 / 2.590 | 3.474 / 2.612 | 3.416 / 2.547 | 3.371 / 2.507 | 3.412 / 2.545 | 3.369 / 2.538 | 3.375 / 2.570 | 3.334 / 2.484 | 3.358 / 2.510 | 3.414 / 2.566 |
| ppo_scott_curr | deter | 3.551 / 2.982 | 3.615 / 2.808 | 3.752 / 2.980 | 3.661 / 2.986 | 3.586 / 2.806 | 3.485 / 2.790 | 3.423 / 2.736 | 3.500 / 2.797 | 3.516 / 2.867 | 3.459 / 2.720 | 2.886 / 2.009 | 3.494 / 2.771 |
| ppo_scott_curr | stoch | 3.359 / 2.583 | 3.469 / 2.601 | 3.510 / 2.611 | 3.458 / 2.635 | 3.399 / 2.533 | 3.359 / 2.526 | 3.320 / 2.466 | 3.347 / 2.539 | 3.352 / 2.564 | 3.298 / 2.472 | 3.282 / 2.450 | 3.377 / 2.544 |
| ppo_scott_baseline | deter | 3.868 / 3.317 | 4.866 / 4.311 | 4.260 / 3.439 | 4.214 / 3.462 | 4.750 / 4.059 | 5.142 / 4.378 | 5.131 / 4.336 | 4.910 / 4.229 | 4.578 / 3.869 | 5.153 / 4.451 | 4.192 / 3.674 | 4.642 / 3.957 |
| ppo_scott_baseline | stoch | 7.809 / 6.680 | 8.766 / 7.368 | 8.035 / 6.772 | 8.029 / 6.803 | 8.932 / 7.472 | 9.335 / 7.777 | 9.262 / 7.696 | 9.085 / 7.636 | 8.705 / 7.330 | 9.393 / 7.857 | 8.183 / 6.874 | 8.685 / 7.297 |
| ppo_scott<br>ppo_scott_carry1 | deter | 2.214 / 1.657 | 2.492 / 1.609 | 2.422 / 1.669 | 2.360 / 1.705 | 2.261 / 1.531 | 2.075 / 1.387 | 2.242 / 1.491 | 2.168 / 1.551 | 2.166 / 1.560 | 2.085 / 1.440 | 2.364 / 1.694 | 2.259 / 1.572 |
| ppo_scott<br>ppo_scott_carry1 | stoch | 3.096 / 2.353 | 3.237 / 2.380 | 3.323 / 2.481 | 3.275 / 2.512 | 3.150 / 2.340 | 3.114 / 2.335 | 3.050 / 2.250 | 3.091 / 2.346 | 3.114 / 2.383 | 3.041 / 2.290 | 3.322 / 2.624 | 3.165 / 2.390 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | deter | 3.025 / 2.608 | 3.215 / 2.665 | 3.209 / 2.629 | 3.168 / 2.679 | 3.006 / 2.465 | 2.901 / 2.405 | 2.905 / 2.373 | 2.917 / 2.447 | 2.962 / 2.482 | 2.842 / 2.363 | 3.056 / 2.616 | 3.019 / 2.521 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | stoch | 3.313 / 2.494 | 3.489 / 2.599 | 3.492 / 2.534 | 3.454 / 2.558 | 3.360 / 2.449 | 3.334 / 2.432 | 3.336 / 2.437 | 3.317 / 2.447 | 3.321 / 2.478 | 3.275 / 2.391 | 3.428 / 2.605 | 3.374 / 2.493 |
| ppo_resid_v3_s0 | deter | 1.822 / 1.294 | 2.203 / 1.435 | 2.103 / 1.367 | 1.963 / 1.362 | 1.887 / 1.190 | 1.779 / 1.228 | 1.834 / 1.204 | 1.808 / 1.244 | 1.798 / 1.248 | 1.761 / 1.174 | 2.129 / 1.487 | 1.917 / 1.294 |
| ppo_resid_v3_s0 | stoch | 2.065 / 1.712 | 2.887 / 2.302 | 2.473 / 1.873 | 2.426 / 1.958 | 2.411 / 1.928 | 2.141 / 1.747 | 2.343 / 1.862 | 2.304 / 1.903 | 2.297 / 1.845 | 2.167 / 1.725 | 2.301 / 1.788 | 2.347 / 1.877 |
| ppo_resid_v3_r2_s0 | deter | 1.851 / 1.340 | 2.231 / 1.481 | 2.120 / 1.407 | 1.983 / 1.403 | 1.912 / 1.238 | 1.772 / 1.264 | 1.866 / 1.258 | 1.833 / 1.291 | 1.822 / 1.294 | 1.790 / 1.222 | 1.993 / 1.475 | 1.925 / 1.334 |
| ppo_resid_v3_r2_s0 | stoch | 1.885 / 1.396 | 2.353 / 1.640 | 2.177 / 1.473 | 2.054 / 1.488 | 2.010 / 1.365 | 1.857 / 1.373 | 1.980 / 1.400 | 1.935 / 1.410 | 1.913 / 1.391 | 1.873 / 1.326 | 2.025 / 1.514 | 2.005 / 1.434 |
| ppo_resid_v3_r3_s0 | deter | 1.826 / 1.299 | 2.194 / 1.428 | 2.098 / 1.360 | 1.954 / 1.353 | 1.889 / 1.195 | 1.772 / 1.240 | 1.841 / 1.217 | 1.812 / 1.251 | 1.799 / 1.255 | 1.770 / 1.188 | 2.076 / 1.473 | 1.912 / 1.296 |
| ppo_resid_v3_r3_s0 | stoch | 1.858 / 1.352 | 2.278 / 1.541 | 2.144 / 1.421 | 2.015 / 1.430 | 1.948 / 1.282 | 1.818 / 1.306 | 1.910 / 1.307 | 1.873 / 1.327 | 1.856 / 1.327 | 1.821 / 1.258 | 2.068 / 1.504 | 1.963 / 1.369 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | deter | 1.900 / 1.421 | 2.432 / 1.740 | 2.211 / 1.514 | 2.096 / 1.530 | 2.063 / 1.433 | 1.877 / 1.403 | 2.017 / 1.443 | 1.974 / 1.468 | 1.967 / 1.450 | 1.897 / 1.363 | 2.061 / 1.537 | 2.045 / 1.482 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | stoch | 1.900 / 1.421 | 2.432 / 1.740 | 2.211 / 1.514 | 2.096 / 1.530 | 2.063 / 1.433 | 1.877 / 1.403 | 2.017 / 1.443 | 1.974 / 1.468 | 1.967 / 1.450 | 1.897 / 1.363 | 2.061 / 1.537 | 2.045 / 1.482 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | deter | 2.010 / 1.597 | 2.666 / 2.042 | 2.376 / 1.748 | 2.307 / 1.792 | 2.186 / 1.607 | 1.941 / 1.490 | 2.109 / 1.597 | 2.081 / 1.631 | 2.098 / 1.624 | 1.968 / 1.469 | 2.205 / 1.655 | 2.177 / 1.659 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | stoch | 2.010 / 1.597 | 2.666 / 2.042 | 2.376 / 1.748 | 2.307 / 1.792 | 2.186 / 1.607 | 1.941 / 1.490 | 2.109 / 1.597 | 2.081 / 1.631 | 2.098 / 1.624 | 1.968 / 1.469 | 2.205 / 1.655 | 2.177 / 1.659 |
| ppo_resid_v3_ladder_s0 | deter | 1.826 / 1.303 | 2.200 / 1.432 | 2.100 / 1.367 | 1.959 / 1.361 | 1.890 / 1.196 | 1.770 / 1.238 | 1.841 / 1.218 | 1.811 / 1.251 | 1.800 / 1.257 | 1.769 / 1.185 | 1.995 / 1.479 | 1.905 / 1.299 |
| ppo_resid_v3_ladder_s0 | stoch | 1.897 / 1.419 | 2.411 / 1.710 | 2.210 / 1.506 | 2.099 / 1.537 | 2.045 / 1.412 | 1.910 / 1.413 | 2.021 / 1.448 | 1.973 / 1.435 | 1.949 / 1.428 | 1.901 / 1.355 | 2.072 / 1.565 | 2.044 / 1.475 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | deter | 2.142 / 1.797 | 2.756 / 2.173 | 2.491 / 1.965 | 2.464 / 2.037 | 2.203 / 1.698 | 1.952 / 1.533 | 2.118 / 1.658 | 2.114 / 1.718 | 2.141 / 1.732 | 2.004 / 1.534 | 2.278 / 1.718 | 2.242 / 1.778 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | stoch | 2.142 / 1.797 | 2.756 / 2.173 | 2.491 / 1.965 | 2.464 / 2.037 | 2.203 / 1.698 | 1.952 / 1.533 | 2.118 / 1.658 | 2.114 / 1.718 | 2.141 / 1.732 | 2.004 / 1.534 | 2.278 / 1.718 | 2.242 / 1.778 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | deter | 1.983 / 1.544 | 2.448 / 1.764 | 2.274 / 1.674 | 2.178 / 1.686 | 2.029 / 1.426 | 1.868 / 1.376 | 1.965 / 1.412 | 1.952 / 1.465 | 1.958 / 1.479 | 1.877 / 1.339 | 2.132 / 1.604 | 2.060 / 1.524 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | stoch | 1.983 / 1.544 | 2.448 / 1.764 | 2.274 / 1.674 | 2.178 / 1.686 | 2.029 / 1.426 | 1.868 / 1.376 | 1.965 / 1.412 | 1.952 / 1.465 | 1.958 / 1.479 | 1.877 / 1.339 | 2.132 / 1.604 | 2.060 / 1.524 |
| scripted (not learned) [STOCK motors force_scale 1: fast v3 swing, default elbow] | deter | 2.101 / 1.750 | 2.680 / 2.092 | 2.393 / 1.889 | 2.333 / 1.915 | 2.162 / 1.658 | 1.897 / 1.524 | 2.114 / 1.649 | 2.077 / 1.683 | 2.078 / 1.677 | 2.007 / 1.548 | 2.208 / 1.667 | 2.187 / 1.732 |
| scripted (not learned) [STOCK motors force_scale 1: fast v3 swing, default elbow] | stoch | 2.101 / 1.750 | 2.680 / 2.092 | 2.393 / 1.889 | 2.333 / 1.915 | 2.162 / 1.658 | 1.897 / 1.524 | 2.114 / 1.649 | 2.077 / 1.683 | 2.078 / 1.677 | 2.007 / 1.548 | 2.208 / 1.667 | 2.187 / 1.732 |
| ppo_resid_v3_left_an1_s0 | deter | 1.815 / 1.282 | 2.181 / 1.404 | 2.092 / 1.345 | 1.950 / 1.337 | 1.878 / 1.171 | 1.784 / 1.226 | 1.828 / 1.193 | 1.801 / 1.228 | 1.791 / 1.237 | 1.758 / 1.164 | 1.992 / 1.484 | 1.897 / 1.279 |
| ppo_resid_v3_left_an1_s0 | stoch | 1.854 / 1.345 | 2.289 / 1.548 | 2.148 / 1.416 | 2.020 / 1.430 | 1.958 / 1.282 | 1.837 / 1.310 | 1.914 / 1.309 | 1.881 / 1.327 | 1.866 / 1.330 | 1.823 / 1.253 | 2.026 / 1.520 | 1.965 / 1.370 |
| ppo_resid_v3_left_an3_s1 | deter | 1.836 / 1.313 | 2.238 / 1.480 | 2.122 / 1.380 | 1.989 / 1.386 | 1.917 / 1.220 | 1.808 / 1.258 | 1.862 / 1.239 | 1.839 / 1.276 | 1.829 / 1.282 | 1.784 / 1.202 | 2.021 / 1.505 | 1.931 / 1.322 |
| ppo_resid_v3_left_an3_s1 | stoch | 1.830 / 1.303 | 2.223 / 1.461 | 2.112 / 1.369 | 1.975 / 1.371 | 1.907 / 1.213 | 1.802 / 1.250 | 1.855 / 1.229 | 1.827 / 1.264 | 1.821 / 1.271 | 1.775 / 1.191 | 2.019 / 1.497 | 1.922 / 1.311 |
| ppo_resid_v3_left_an4_s2 | deter | 1.833 / 1.306 | 2.202 / 1.435 | 2.107 / 1.374 | 1.967 / 1.369 | 1.893 / 1.199 | 1.783 / 1.241 | 1.845 / 1.220 | 1.818 / 1.254 | 1.808 / 1.262 | 1.770 / 1.186 | 2.030 / 1.482 | 1.914 / 1.303 |
| ppo_resid_v3_left_an4_s2 | stoch | 1.836 / 1.312 | 2.217 / 1.455 | 2.113 / 1.379 | 1.975 / 1.378 | 1.905 / 1.216 | 1.791 / 1.252 | 1.856 / 1.235 | 1.828 / 1.269 | 1.818 / 1.275 | 1.779 / 1.198 | 2.030 / 1.486 | 1.923 / 1.314 |
| ppo_resid_v3_left_an5_s3 | deter | 2.069 / 1.720 | 2.987 / 2.471 | 2.502 / 1.866 | 2.479 / 2.014 | 2.480 / 2.023 | 2.345 / 1.944 | 2.543 / 1.975 | 2.429 / 1.959 | 2.356 / 1.927 | 2.307 / 1.870 | 2.289 / 1.824 | 2.435 / 1.963 |
| ppo_resid_v3_left_an5_s3 | stoch | 1.995 / 1.593 | 2.773 / 2.188 | 2.387 / 1.712 | 2.330 / 1.820 | 2.326 / 1.801 | 2.190 / 1.751 | 2.360 / 1.786 | 2.269 / 1.771 | 2.208 / 1.743 | 2.163 / 1.687 | 2.207 / 1.727 | 2.292 / 1.780 |
| best_carry_analytic<br>ppo_resid_v3_left_an2_s0 | deter | 1.807 / 1.268 | 2.174 / 1.391 | 2.085 / 1.332 | 1.942 / 1.324 | 1.871 / 1.158 | 1.779 / 1.214 | 1.820 / 1.178 | 1.794 / 1.215 | 1.784 / 1.223 | 1.749 / 1.151 | 1.999 / 1.487 | 1.891 / 1.267 |
| best_carry_analytic<br>ppo_resid_v3_left_an2_s0 | stoch | 1.844 / 1.325 | 2.256 / 1.502 | 2.132 / 1.398 | 2.001 / 1.404 | 1.931 / 1.248 | 1.818 / 1.279 | 1.885 / 1.264 | 1.854 / 1.297 | 1.843 / 1.300 | 1.802 / 1.224 | 2.032 / 1.512 | 1.945 / 1.341 |
| ppo_resid_v3_left_an6_s4 | deter | 1.844 / 1.324 | 2.240 / 1.484 | 2.130 / 1.393 | 1.997 / 1.399 | 1.915 / 1.229 | 1.804 / 1.261 | 1.862 / 1.243 | 1.837 / 1.280 | 1.831 / 1.287 | 1.785 / 1.205 | 2.020 / 1.505 | 1.933 / 1.328 |
| ppo_resid_v3_left_an6_s4 | stoch | 1.827 / 1.299 | 2.219 / 1.457 | 2.109 / 1.359 | 1.971 / 1.363 | 1.907 / 1.214 | 1.795 / 1.253 | 1.859 / 1.233 | 1.830 / 1.264 | 1.820 / 1.271 | 1.780 / 1.197 | 2.000 / 1.487 | 1.920 / 1.309 |
| ppo_resid_v3_left_an8_s6 | deter | 2.082 / 1.734 | 3.000 / 2.486 | 2.516 / 1.878 | 2.492 / 2.029 | 2.495 / 2.040 | 2.332 / 1.931 | 2.555 / 1.994 | 2.447 / 1.975 | 2.372 / 1.944 | 2.294 / 1.857 | 2.294 / 1.838 | 2.444 / 1.973 |
| ppo_resid_v3_left_an8_s6 | stoch | 2.107 / 1.779 | 3.076 / 2.585 | 2.558 / 1.942 | 2.547 / 2.098 | 2.549 / 2.116 | 2.392 / 2.002 | 2.618 / 2.085 | 2.501 / 2.052 | 2.423 / 2.007 | 2.349 / 1.928 | 2.325 / 1.873 | 2.495 / 2.042 |
| ppo_resid_v3_left_an7_s5 | deter | 2.050 / 1.678 | 2.900 / 2.355 | 2.460 / 1.808 | 2.419 / 1.937 | 2.423 / 1.937 | 2.269 / 1.859 | 2.463 / 1.969 | 2.370 / 1.895 | 2.304 / 1.858 | 2.244 / 1.792 | 2.237 / 1.775 | 2.376 / 1.897 |
| ppo_resid_v3_left_an7_s5 | stoch | 2.007 / 1.606 | 2.793 / 2.211 | 2.403 / 1.723 | 2.347 / 1.834 | 2.347 / 1.820 | 2.214 / 1.772 | 2.381 / 1.849 | 2.290 / 1.785 | 2.231 / 1.755 | 2.176 / 1.700 | 2.209 / 1.735 | 2.309 / 1.799 |
| ppo_resid_v3_left_an9_s7 | deter | 1.831 / 1.303 | 2.199 / 1.434 | 2.104 / 1.369 | 1.962 / 1.362 | 1.890 / 1.197 | 1.782 / 1.245 | 1.842 / 1.217 | 1.815 / 1.253 | 1.804 / 1.259 | 1.771 / 1.188 | 1.999 / 1.485 | 1.909 / 1.301 |
| ppo_resid_v3_left_an9_s7 | stoch | 1.834 / 1.309 | 2.224 / 1.466 | 2.111 / 1.374 | 1.972 / 1.373 | 1.913 / 1.225 | 1.799 / 1.268 | 1.870 / 1.249 | 1.839 / 1.275 | 1.824 / 1.278 | 1.791 / 1.213 | 1.998 / 1.486 | 1.925 / 1.320 |
| ppo_resid_v3_left_an10_s8 | deter | 1.838 / 1.317 | 2.222 / 1.463 | 2.116 / 1.383 | 1.980 / 1.384 | 1.904 / 1.216 | 1.775 / 1.248 | 1.853 / 1.237 | 1.824 / 1.270 | 1.815 / 1.275 | 1.778 / 1.200 | 2.009 / 1.478 | 1.919 / 1.316 |
| ppo_resid_v3_left_an10_s8 | stoch | 1.904 / 1.427 | 2.431 / 1.738 | 2.217 / 1.520 | 2.106 / 1.545 | 2.061 / 1.438 | 1.891 / 1.410 | 2.025 / 1.457 | 1.978 / 1.469 | 1.966 / 1.454 | 1.902 / 1.365 | 2.077 / 1.552 | 2.051 / 1.489 |
| ppo_resid_v3_left_fast1_s10 | deter | 2.231 / 1.948 | 3.347 / 2.932 | 2.714 / 2.221 | 2.731 / 2.334 | 2.757 / 2.363 | 2.513 / 2.167 | 2.808 / 2.420 | 2.716 / 2.314 | 2.630 / 2.216 | 2.475 / 2.089 | 2.437 / 1.998 | 2.669 / 2.273 |
| ppo_resid_v3_left_fast1_s10 | stoch | 2.231 / 1.949 | 3.346 / 2.932 | 2.714 / 2.205 | 2.731 / 2.335 | 2.757 / 2.358 | 2.535 / 2.190 | 2.824 / 2.439 | 2.721 / 2.352 | 2.630 / 2.216 | 2.489 / 2.104 | 2.432 / 1.994 | 2.674 / 2.279 |
| best_gate_flat_123mph<br>ppo_resid_v3_left_fast2_s11 | deter | 2.216 / 1.945 | 3.330 / 2.914 | 2.703 / 2.141 | 2.722 / 2.328 | 2.740 / 2.359 | 2.539 / 2.195 | 2.822 / 2.416 | 2.705 / 2.297 | 2.613 / 2.219 | 2.490 / 2.108 | 2.432 / 1.992 | 2.665 / 2.265 |
| best_gate_flat_123mph<br>ppo_resid_v3_left_fast2_s11 | stoch | 2.195 / 1.911 | 3.277 / 2.844 | 2.674 / 2.106 | 2.686 / 2.279 | 2.701 / 2.311 | 2.493 / 2.138 | 2.761 / 2.299 | 2.656 / 2.240 | 2.574 / 2.173 | 2.452 / 2.059 | 2.419 / 1.975 | 2.626 / 2.212 |
| ppo_v3tiny_s22 | deter | 1.963 / 1.515 | 2.417 / 1.724 | 2.250 / 1.632 | 2.149 / 1.640 | 2.013 / 1.401 | 1.848 / 1.361 | 1.952 / 1.394 | 1.934 / 1.442 | 1.937 / 1.453 | 1.866 / 1.326 | 2.104 / 1.575 | 2.039 / 1.497 |
| ppo_v3tiny_s22 | stoch | 1.978 / 1.540 | 2.473 / 1.797 | 2.279 / 1.657 | 2.184 / 1.683 | 2.052 / 1.454 | 1.872 / 1.392 | 1.987 / 1.437 | 1.967 / 1.485 | 1.977 / 1.497 | 1.889 / 1.360 | 2.130 / 1.597 | 2.072 / 1.536 |
| ppo_v3tiny_s23 | deter | 1.993 / 1.563 | 2.497 / 1.830 | 2.294 / 1.690 | 2.205 / 1.709 | 2.068 / 1.479 | 1.885 / 1.409 | 2.000 / 1.460 | 1.984 / 1.509 | 1.993 / 1.519 | 1.904 / 1.377 | 2.144 / 1.613 | 2.088 / 1.560 |
| ppo_v3tiny_s23 | stoch | 1.975 / 1.530 | 2.435 / 1.749 | 2.267 / 1.652 | 2.169 / 1.667 | 2.022 / 1.418 | 1.854 / 1.371 | 1.961 / 1.409 | 1.945 / 1.457 | 1.949 / 1.469 | 1.873 / 1.337 | 2.116 / 1.583 | 2.052 / 1.513 |
| ppo_v3tiny_s21 | deter | 2.010 / 1.590 | 2.552 / 1.901 | 2.321 / 1.723 | 2.237 / 1.752 | 2.108 / 1.535 | 1.904 / 1.443 | 2.036 / 1.509 | 2.019 / 1.555 | 2.031 / 1.565 | 1.930 / 1.415 | 2.162 / 1.630 | 2.119 / 1.602 |
| ppo_v3tiny_s21 | stoch | 1.982 / 1.544 | 2.464 / 1.786 | 2.276 / 1.668 | 2.179 / 1.685 | 2.048 / 1.450 | 1.871 / 1.392 | 1.983 / 1.435 | 1.966 / 1.484 | 1.972 / 1.494 | 1.890 / 1.359 | 2.125 / 1.598 | 2.069 / 1.536 |
| ppo_v3flt_all_s33 | deter | 2.031 / 1.619 | 2.556 / 1.906 | 2.338 / 1.764 | 2.260 / 1.787 | 2.101 / 1.534 | 1.909 / 1.441 | 2.029 / 1.504 | 2.019 / 1.560 | 2.031 / 1.571 | 1.929 / 1.414 | 2.180 / 1.648 | 2.126 / 1.614 |
| ppo_v3flt_all_s33 | stoch | 2.006 / 1.581 | 2.528 / 1.868 | 2.317 / 1.708 | 2.231 / 1.743 | 2.089 / 1.505 | 1.898 / 1.426 | 2.018 / 1.483 | 2.004 / 1.533 | 2.017 / 1.546 | 1.915 / 1.395 | 2.162 / 1.629 | 2.108 / 1.583 |
| best_learned_yaw_s32<br>ppo_v3flt_yaw_s32 | deter | 1.991 / 1.556 | 2.461 / 1.781 | 2.283 / 1.690 | 2.189 / 1.702 | 2.036 / 1.438 | 1.871 / 1.383 | 1.971 / 1.423 | 1.959 / 1.476 | 1.966 / 1.490 | 1.882 / 1.347 | 2.139 / 1.609 | 2.068 / 1.536 |
| best_learned_yaw_s32<br>ppo_v3flt_yaw_s32 | stoch | 1.989 / 1.553 | 2.456 / 1.774 | 2.281 / 1.686 | 2.186 / 1.698 | 2.034 / 1.434 | 1.870 / 1.381 | 1.969 / 1.419 | 1.957 / 1.472 | 1.964 / 1.487 | 1.880 / 1.344 | 2.136 / 1.607 | 2.066 / 1.532 |
| best_learned_yaw_s31<br>ppo_v3flt_yaw_s31 | deter | 1.989 / 1.553 | 2.457 / 1.776 | 2.281 / 1.686 | 2.186 / 1.698 | 2.035 / 1.435 | 1.870 / 1.381 | 1.969 / 1.420 | 1.958 / 1.473 | 1.964 / 1.488 | 1.881 / 1.345 | 2.137 / 1.608 | 2.066 / 1.533 |
| best_learned_yaw_s31<br>ppo_v3flt_yaw_s31 | stoch | 1.987 / 1.549 | 2.453 / 1.770 | 2.278 / 1.681 | 2.183 / 1.693 | 2.032 / 1.431 | 1.869 / 1.379 | 1.967 / 1.416 | 1.955 / 1.469 | 1.961 / 1.484 | 1.879 / 1.342 | 2.134 / 1.606 | 2.063 / 1.529 |
| ppo_v4yaw_s43 | deter | 1.741 / 1.180 | 2.105 / 1.291 | 2.036 / 1.239 | 1.888 / 1.218 | 1.823 / 1.058 | 1.789 / 1.167 | 1.768 / 1.088 | 1.745 / 1.132 | 1.731 / 1.140 | 1.708 / 1.082 | 1.984 / 1.492 | 1.847 / 1.190 |
| ppo_v4yaw_s43 | stoch | 1.737 / 1.174 | 2.099 / 1.283 | 2.032 / 1.232 | 1.883 / 1.211 | 1.820 / 1.052 | 1.787 / 1.163 | 1.766 / 1.084 | 1.742 / 1.127 | 1.728 / 1.135 | 1.705 / 1.078 | 1.980 / 1.490 | 1.843 / 1.184 |
| ppo_v4yaw_s42 | deter | 1.740 / 1.179 | 2.103 / 1.289 | 2.035 / 1.237 | 1.887 / 1.217 | 1.822 / 1.056 | 1.788 / 1.166 | 1.768 / 1.087 | 1.744 / 1.131 | 1.730 / 1.139 | 1.707 / 1.081 | 1.983 / 1.492 | 1.846 / 1.189 |
| ppo_v4yaw_s42 | stoch | 1.737 / 1.174 | 2.099 / 1.283 | 2.032 / 1.231 | 1.883 / 1.210 | 1.819 / 1.051 | 1.787 / 1.163 | 1.765 / 1.083 | 1.741 / 1.126 | 1.727 / 1.134 | 1.705 / 1.078 | 1.980 / 1.490 | 1.843 / 1.184 |
| best_v4yaw_s41<br>ppo_v4yaw_s41 | deter | 1.739 / 1.178 | 2.102 / 1.288 | 2.034 / 1.236 | 1.886 / 1.215 | 1.821 / 1.055 | 1.788 / 1.165 | 1.767 / 1.086 | 1.743 / 1.130 | 1.730 / 1.138 | 1.707 / 1.080 | 1.982 / 1.491 | 1.845 / 1.187 |
| best_v4yaw_s41<br>ppo_v4yaw_s41 | stoch | 1.739 / 1.177 | 2.101 / 1.286 | 2.034 / 1.235 | 1.885 / 1.214 | 1.821 / 1.054 | 1.788 / 1.165 | 1.767 / 1.086 | 1.743 / 1.129 | 1.729 / 1.137 | 1.706 / 1.080 | 1.981 / 1.491 | 1.845 / 1.187 |
| imit2_w075_s51 | deter | 2.007 / 1.592 | 2.630 / 1.999 | 2.345 / 1.699 | 2.268 / 1.770 | 2.169 / 1.602 | 1.944 / 1.486 | 2.090 / 1.570 | 2.063 / 1.606 | 2.096 / 1.623 | 1.956 / 1.456 | 2.199 / 1.654 | 2.161 / 1.642 |
| imit2_w075_s51 | stoch | 1.989 / 1.559 | 2.529 / 1.868 | 2.304 / 1.672 | 2.216 / 1.715 | 2.093 / 1.504 | 1.901 / 1.426 | 2.021 / 1.484 | 2.002 / 1.528 | 2.019 / 1.541 | 1.913 / 1.394 | 2.155 / 1.622 | 2.104 / 1.574 |
| imit2_w075_s52 | deter | 1.928 / 1.460 | 2.364 / 1.652 | 2.213 / 1.565 | 2.103 / 1.570 | 1.981 / 1.344 | 1.841 / 1.329 | 1.921 / 1.343 | 1.903 / 1.390 | 1.903 / 1.401 | 1.840 / 1.285 | 2.082 / 1.563 | 2.007 / 1.446 |
| imit2_w075_s52 | stoch | 1.953 / 1.501 | 2.433 / 1.742 | 2.251 / 1.611 | 2.151 / 1.629 | 2.027 / 1.411 | 1.866 / 1.367 | 1.962 / 1.398 | 1.943 / 1.445 | 1.950 / 1.458 | 1.869 / 1.328 | 2.114 / 1.589 | 2.047 / 1.498 |
| imit2_w075_s53 | deter | 1.930 / 1.464 | 2.369 / 1.657 | 2.216 / 1.570 | 2.107 / 1.575 | 1.983 / 1.347 | 1.844 / 1.330 | 1.922 / 1.345 | 1.904 / 1.392 | 1.905 / 1.403 | 1.840 / 1.286 | 2.087 / 1.566 | 2.010 / 1.449 |
| imit2_w075_s53 | stoch | 2.000 / 1.574 | 2.529 / 1.869 | 2.308 / 1.703 | 2.222 / 1.733 | 2.089 / 1.505 | 1.906 / 1.426 | 2.017 / 1.481 | 2.002 / 1.529 | 2.017 / 1.543 | 1.914 / 1.391 | 2.166 / 1.635 | 2.106 / 1.581 |
| imit3_w075_s51 | deter | 1.984 / 1.546 | 2.453 / 1.770 | 2.276 / 1.677 | 2.181 / 1.689 | 2.031 / 1.428 | 1.870 / 1.376 | 1.966 / 1.414 | 1.952 / 1.466 | 1.959 / 1.481 | 1.877 / 1.340 | 2.135 / 1.606 | 2.062 / 1.527 |
| imit3_w075_s51 | stoch | 1.988 / 1.553 | 2.460 / 1.779 | 2.280 / 1.684 | 2.187 / 1.696 | 2.034 / 1.435 | 1.872 / 1.380 | 1.969 / 1.420 | 1.957 / 1.472 | 1.964 / 1.487 | 1.880 / 1.345 | 2.138 / 1.609 | 2.066 / 1.533 |
| imit3_w075_s52 | deter | 1.968 / 1.521 | 2.426 / 1.734 | 2.257 / 1.643 | 2.157 / 1.653 | 2.016 / 1.404 | 1.860 / 1.363 | 1.953 / 1.394 | 1.938 / 1.444 | 1.943 / 1.458 | 1.867 / 1.325 | 2.117 / 1.591 | 2.046 / 1.503 |
| imit3_w075_s52 | stoch | 1.971 / 1.526 | 2.432 / 1.742 | 2.260 / 1.649 | 2.162 / 1.659 | 2.019 / 1.409 | 1.861 / 1.366 | 1.956 / 1.399 | 1.941 / 1.449 | 1.946 / 1.462 | 1.869 / 1.329 | 2.120 / 1.593 | 2.049 / 1.508 |
| imit3_w075_s53 | deter | 1.945 / 1.485 | 2.388 / 1.684 | 2.231 / 1.598 | 2.125 / 1.605 | 1.995 / 1.369 | 1.848 / 1.342 | 1.934 / 1.364 | 1.917 / 1.412 | 1.919 / 1.424 | 1.850 / 1.301 | 2.098 / 1.573 | 2.023 / 1.469 |
| imit3_w075_s53 | stoch | 1.948 / 1.490 | 2.393 / 1.690 | 2.236 / 1.606 | 2.130 / 1.614 | 1.998 / 1.374 | 1.850 / 1.345 | 1.937 / 1.368 | 1.921 / 1.417 | 1.923 / 1.429 | 1.852 / 1.304 | 2.101 / 1.576 | 2.026 / 1.474 |
| imit3_w050_s51 | deter | 1.974 / 1.530 | 2.437 / 1.748 | 2.264 / 1.655 | 2.166 / 1.665 | 2.022 / 1.412 | 1.865 / 1.368 | 1.957 / 1.401 | 1.944 / 1.452 | 1.949 / 1.466 | 1.870 / 1.330 | 2.126 / 1.599 | 2.052 / 1.512 |
| imit3_w050_s51 | stoch | 1.967 / 1.520 | 2.424 / 1.731 | 2.257 / 1.643 | 2.157 / 1.653 | 2.015 / 1.401 | 1.860 / 1.362 | 1.951 / 1.392 | 1.938 / 1.442 | 1.942 / 1.456 | 1.865 / 1.323 | 2.119 / 1.593 | 2.045 / 1.501 |
| best_imit_w050_s52<br>imit3_w050_s52 | deter | 2.008 / 1.582 | 2.488 / 1.815 | 2.304 / 1.723 | 2.215 / 1.738 | 2.051 / 1.462 | 1.883 / 1.396 | 1.983 / 1.442 | 1.974 / 1.497 | 1.984 / 1.514 | 1.892 / 1.361 | 2.161 / 1.626 | 2.086 / 1.560 |
| best_imit_w050_s52<br>imit3_w050_s52 | stoch | 1.996 / 1.564 | 2.471 / 1.793 | 2.291 / 1.702 | 2.200 / 1.715 | 2.041 / 1.444 | 1.879 / 1.386 | 1.974 / 1.427 | 1.964 / 1.481 | 1.972 / 1.497 | 1.884 / 1.350 | 2.152 / 1.619 | 2.075 / 1.544 |
| imit3_w025_s51 | deter | 2.016 / 1.596 | 2.505 / 1.839 | 2.312 / 1.738 | 2.228 / 1.755 | 2.059 / 1.477 | 1.887 / 1.405 | 1.991 / 1.455 | 1.982 / 1.511 | 1.992 / 1.527 | 1.899 / 1.373 | 2.168 / 1.632 | 2.095 / 1.573 |
| imit3_w025_s51 | stoch | 2.009 / 1.584 | 2.491 / 1.820 | 2.305 / 1.726 | 2.217 / 1.741 | 2.053 / 1.465 | 1.882 / 1.398 | 1.985 / 1.445 | 1.975 / 1.500 | 1.985 / 1.516 | 1.894 / 1.364 | 2.161 / 1.626 | 2.087 / 1.563 |
| imit3_w025_s52 | deter | 1.993 / 1.563 | 2.546 / 1.887 | 2.313 / 1.684 | 2.228 / 1.728 | 2.110 / 1.523 | 1.929 / 1.440 | 2.033 / 1.493 | 2.018 / 1.543 | 2.036 / 1.552 | 1.925 / 1.401 | 2.176 / 1.649 | 2.119 / 1.588 |
| imit3_w025_s52 | stoch | 1.980 / 1.540 | 2.491 / 1.817 | 2.288 / 1.661 | 2.195 / 1.692 | 2.069 / 1.470 | 1.899 / 1.407 | 1.999 / 1.449 | 1.983 / 1.499 | 1.996 / 1.511 | 1.898 / 1.367 | 2.152 / 1.622 | 2.086 / 1.548 |
| imit3_w000_s52 | deter | 1.969 / 1.519 | 2.419 / 1.727 | 2.252 / 1.637 | 2.151 / 1.646 | 2.014 / 1.404 | 1.856 / 1.366 | 1.952 / 1.396 | 1.939 / 1.445 | 1.942 / 1.458 | 1.868 / 1.328 | 2.108 / 1.584 | 2.043 / 1.501 |
| imit3_w000_s52 | stoch | 1.995 / 1.559 | 2.522 / 1.859 | 2.298 / 1.694 | 2.209 / 1.711 | 2.090 / 1.504 | 1.904 / 1.430 | 2.019 / 1.481 | 2.005 / 1.530 | 2.019 / 1.536 | 1.920 / 1.398 | 2.147 / 1.625 | 2.103 / 1.575 |
| best_imit_scriptfree_s51_NOTPASS_lat3.56<br>imit3_w000_s51 | deter | 1.967 / 1.518 | 2.431 / 1.740 | 2.258 / 1.640 | 2.158 / 1.651 | 2.023 / 1.411 | 1.866 / 1.369 | 1.959 / 1.400 | 1.944 / 1.449 | 1.950 / 1.462 | 1.871 / 1.329 | 2.120 / 1.594 | 2.049 / 1.506 |
| best_imit_scriptfree_s51_NOTPASS_lat3.56<br>imit3_w000_s51 | stoch | 1.963 / 1.512 | 2.416 / 1.720 | 2.250 / 1.631 | 2.149 / 1.641 | 2.011 / 1.395 | 1.859 / 1.358 | 1.948 / 1.386 | 1.933 / 1.436 | 1.937 / 1.449 | 1.862 / 1.319 | 2.114 / 1.588 | 2.040 / 1.494 |
| imit4_w000_s52 | deter | 1.995 / 1.562 | 2.494 / 1.823 | 2.296 / 1.694 | 2.206 / 1.715 | 2.068 / 1.477 | 1.891 / 1.406 | 1.999 / 1.455 | 1.986 / 1.506 | 1.995 / 1.518 | 1.901 / 1.372 | 2.154 / 1.620 | 2.089 / 1.559 |
| imit4_w000_s52 | stoch | 2.025 / 1.617 | 2.627 / 1.996 | 2.359 / 1.748 | 2.286 / 1.804 | 2.170 / 1.610 | 1.959 / 1.493 | 2.088 / 1.569 | 2.074 / 1.619 | 2.093 / 1.626 | 1.967 / 1.462 | 2.224 / 1.680 | 2.170 / 1.657 |
| imit4_w000_s51 | deter | 1.978 / 1.541 | 2.469 / 1.791 | 2.280 / 1.664 | 2.185 / 1.686 | 2.051 / 1.452 | 1.874 / 1.390 | 1.985 / 1.433 | 1.967 / 1.484 | 1.974 / 1.495 | 1.887 / 1.356 | 2.138 / 1.602 | 2.072 / 1.536 |
| imit4_w000_s51 | stoch | 2.010 / 1.594 | 2.547 / 1.893 | 2.324 / 1.730 | 2.242 / 1.761 | 2.102 / 1.526 | 1.906 / 1.436 | 2.030 / 1.500 | 2.014 / 1.548 | 2.027 / 1.562 | 1.924 / 1.407 | 2.186 / 1.639 | 2.119 / 1.600 |
| imit5_w000_s52 | deter | 1.961 / 1.509 | 2.414 / 1.718 | 2.251 / 1.629 | 2.152 / 1.639 | 2.008 / 1.392 | 1.860 / 1.357 | 1.946 / 1.384 | 1.931 / 1.434 | 1.936 / 1.447 | 1.861 / 1.318 | 2.115 / 1.590 | 2.040 / 1.493 |
| imit5_w000_s52 | stoch | 2.003 / 1.573 | 2.502 / 1.833 | 2.305 / 1.709 | 2.220 / 1.728 | 2.062 / 1.475 | 1.892 / 1.407 | 1.994 / 1.454 | 1.981 / 1.506 | 1.994 / 1.521 | 1.899 / 1.373 | 2.163 / 1.627 | 2.092 / 1.564 |
| best_imit_scriptfree_s51_seed4000-8000only<br>imit5_w000_s51 | deter | 2.008 / 1.584 | 2.520 / 1.859 | 2.309 / 1.720 | 2.223 / 1.741 | 2.080 / 1.499 | 1.893 / 1.421 | 2.011 / 1.477 | 1.996 / 1.528 | 2.008 / 1.539 | 1.912 / 1.391 | 2.158 / 1.624 | 2.102 / 1.580 |
| best_imit_scriptfree_s51_seed4000-8000only<br>imit5_w000_s51 | stoch | 2.009 / 1.582 | 2.507 / 1.843 | 2.305 / 1.718 | 2.218 / 1.738 | 2.070 / 1.488 | 1.888 / 1.413 | 2.002 / 1.466 | 1.989 / 1.518 | 2.000 / 1.530 | 1.906 / 1.382 | 2.154 / 1.620 | 2.095 / 1.572 |
| ppo_v4power_s61 | deter | 1.706 / 1.138 | 2.088 / 1.273 | 2.021 / 1.211 | 1.873 / 1.184 | 1.800 / 1.017 | 1.804 / 1.156 | 1.741 / 1.040 | 1.725 / 1.102 | 1.709 / 1.105 | 1.689 / 1.055 | 1.993 / 1.513 | 1.831 / 1.163 |
| ppo_v4power_s61 | stoch | 1.705 / 1.137 | 2.087 / 1.271 | 2.021 / 1.210 | 1.872 / 1.183 | 1.800 / 1.016 | 1.803 / 1.156 | 1.740 / 1.040 | 1.724 / 1.101 | 1.708 / 1.104 | 1.689 / 1.055 | 1.992 / 1.513 | 1.831 / 1.162 |
| ppo_v4power_s62 | deter | 1.705 / 1.136 | 2.086 / 1.270 | 2.020 / 1.208 | 1.871 / 1.181 | 1.799 / 1.015 | 1.803 / 1.155 | 1.740 / 1.039 | 1.724 / 1.100 | 1.708 / 1.103 | 1.688 / 1.054 | 1.991 / 1.512 | 1.830 / 1.161 |
| ppo_v4power_s62 | stoch | 1.706 / 1.138 | 2.088 / 1.273 | 2.021 / 1.211 | 1.873 / 1.184 | 1.800 / 1.017 | 1.804 / 1.157 | 1.741 / 1.040 | 1.725 / 1.102 | 1.709 / 1.105 | 1.689 / 1.055 | 1.993 / 1.513 | 1.832 / 1.163 |
| imit7_w000_s51 | deter | 1.998 / 1.570 | 2.521 / 1.858 | 2.306 / 1.695 | 2.217 / 1.729 | 2.085 / 1.500 | 1.899 / 1.422 | 2.015 / 1.477 | 1.998 / 1.525 | 2.014 / 1.540 | 1.910 / 1.388 | 2.162 / 1.626 | 2.102 / 1.576 |
| imit7_w000_s51 | stoch | 2.016 / 1.597 | 2.533 / 1.874 | 2.320 / 1.735 | 2.237 / 1.763 | 2.084 / 1.506 | 1.903 / 1.424 | 2.013 / 1.480 | 2.001 / 1.533 | 2.016 / 1.550 | 1.912 / 1.391 | 2.178 / 1.641 | 2.110 / 1.590 |
| ppo_v4power48_s71 | deter | 1.641 / 1.048 | 2.014 / 1.165 | 1.967 / 1.109 | 1.813 / 1.075 | 1.749 / 0.921 | 1.798 / 1.101 | 1.687 / 0.951 | 1.671 / 1.015 | 1.652 / 1.018 | 1.644 / 0.983 | 1.977 / 1.510 | 1.783 / 1.082 |
| ppo_v4power48_s71 | stoch | 1.642 / 1.048 | 2.015 / 1.166 | 1.967 / 1.110 | 1.813 / 1.075 | 1.749 / 0.921 | 1.798 / 1.101 | 1.687 / 0.951 | 1.672 / 1.016 | 1.653 / 1.018 | 1.644 / 0.983 | 1.977 / 1.510 | 1.783 / 1.082 |
| imit8_w000_s51 | deter | 1.962 / 1.503 | 2.437 / 1.741 | 2.266 / 1.637 | 2.165 / 1.651 | 2.029 / 1.412 | 1.886 / 1.366 | 1.960 / 1.391 | 1.949 / 1.444 | 1.961 / 1.462 | 1.864 / 1.316 | 2.148 / 1.619 | 2.057 / 1.504 |
| imit8_w000_s51 | stoch | 1.953 / 1.490 | 2.414 / 1.710 | 2.252 / 1.615 | 2.149 / 1.629 | 2.013 / 1.389 | 1.876 / 1.353 | 1.945 / 1.372 | 1.934 / 1.424 | 1.945 / 1.442 | 1.854 / 1.302 | 2.136 / 1.610 | 2.043 / 1.485 |
| imit9_w000_s53 | deter | 1.974 / 1.518 | 2.421 / 1.720 | 2.269 / 1.655 | 2.169 / 1.668 | 2.012 / 1.396 | 1.879 / 1.356 | 1.944 / 1.376 | 1.938 / 1.434 | 1.948 / 1.454 | 1.856 / 1.305 | 2.149 / 1.622 | 2.051 / 1.500 |
| imit9_w000_s53 | stoch | 1.978 / 1.526 | 2.439 / 1.743 | 2.278 / 1.663 | 2.179 / 1.680 | 2.026 / 1.414 | 1.888 / 1.368 | 1.956 / 1.392 | 1.949 / 1.449 | 1.961 / 1.469 | 1.865 / 1.317 | 2.156 / 1.630 | 2.061 / 1.514 |
| imit10_w000_s51_tr | deter | 1.990 / 1.548 | 2.469 / 1.788 | 2.288 / 1.680 | 2.194 / 1.697 | 2.056 / 1.462 | 1.883 / 1.384 | 1.993 / 1.443 | 1.978 / 1.493 | 1.986 / 1.503 | 1.888 / 1.354 | 2.165 / 1.642 | 2.081 / 1.545 |
| imit10_w000_s51_tr | stoch | 1.971 / 1.516 | 2.442 / 1.756 | 2.278 / 1.647 | 2.179 / 1.664 | 2.054 / 1.446 | 1.894 / 1.384 | 1.989 / 1.428 | 1.974 / 1.478 | 1.984 / 1.489 | 1.886 / 1.344 | 2.175 / 1.666 | 2.075 / 1.529 |
| best_imit_scriptfree_elbow48_s51<br>imit9_w000_s51 | deter | 1.951 / 1.484 | 2.389 / 1.677 | 2.247 / 1.614 | 2.141 / 1.624 | 1.993 / 1.361 | 1.870 / 1.335 | 1.926 / 1.346 | 1.918 / 1.402 | 1.926 / 1.422 | 1.840 / 1.281 | 2.132 / 1.608 | 2.030 / 1.469 |
| best_imit_scriptfree_elbow48_s51<br>imit9_w000_s51 | stoch | 1.964 / 1.504 | 2.409 / 1.703 | 2.261 / 1.639 | 2.158 / 1.650 | 2.005 / 1.381 | 1.875 / 1.347 | 1.937 / 1.363 | 1.929 / 1.420 | 1.939 / 1.440 | 1.849 / 1.294 | 2.143 / 1.617 | 2.043 / 1.487 |
| imit9_w000_s52 | deter | 1.953 / 1.487 | 2.392 / 1.680 | 2.249 / 1.617 | 2.143 / 1.627 | 1.995 / 1.364 | 1.870 / 1.337 | 1.928 / 1.349 | 1.919 / 1.404 | 1.928 / 1.424 | 1.842 / 1.283 | 2.133 / 1.609 | 2.032 / 1.471 |
| imit9_w000_s52 | stoch | 1.957 / 1.494 | 2.399 / 1.689 | 2.254 / 1.626 | 2.149 / 1.636 | 1.999 / 1.371 | 1.872 / 1.341 | 1.931 / 1.355 | 1.923 / 1.411 | 1.932 / 1.431 | 1.845 / 1.288 | 2.136 / 1.612 | 2.036 / 1.478 |
| imit13_w000_s51 | deter | 1.998 / 1.559 | 2.467 / 1.787 | 2.292 / 1.687 | 2.202 / 1.707 | 2.054 / 1.455 | 1.890 / 1.397 | 1.985 / 1.436 | 1.976 / 1.493 | 1.982 / 1.504 | 1.894 / 1.360 | 2.158 / 1.636 | 2.082 / 1.547 |
| imit13_w000_s51 | stoch | 1.996 / 1.560 | 2.467 / 1.786 | 2.292 / 1.695 | 2.199 / 1.709 | 2.046 / 1.447 | 1.887 / 1.390 | 1.978 / 1.427 | 1.968 / 1.484 | 1.977 / 1.499 | 1.887 / 1.350 | 2.166 / 1.634 | 2.079 / 1.544 |
| imit13_w000_s52 | deter | 1.973 / 1.527 | 2.435 / 1.742 | 2.270 / 1.660 | 2.173 / 1.670 | 2.020 / 1.406 | 1.873 / 1.364 | 1.953 / 1.390 | 1.942 / 1.446 | 1.950 / 1.462 | 1.865 / 1.320 | 2.156 / 1.616 | 2.055 / 1.509 |
| imit13_w000_s52 | stoch | 1.979 / 1.536 | 2.447 / 1.757 | 2.278 / 1.674 | 2.182 / 1.685 | 2.025 / 1.416 | 1.875 / 1.370 | 1.958 / 1.399 | 1.948 / 1.455 | 1.957 / 1.472 | 1.870 / 1.326 | 2.162 / 1.622 | 2.062 / 1.519 |
| imit14_w000_s51 | deter | 1.983 / 1.534 | 2.439 / 1.746 | 2.279 / 1.658 | 2.181 / 1.671 | 2.044 / 1.428 | 1.901 / 1.389 | 1.977 / 1.415 | 1.967 / 1.470 | 1.973 / 1.483 | 1.887 / 1.343 | 2.160 / 1.643 | 2.072 / 1.526 |
| imit14_w000_s51 | stoch | 1.984 / 1.536 | 2.425 / 1.730 | 2.286 / 1.666 | 2.186 / 1.676 | 2.034 / 1.415 | 1.901 / 1.387 | 1.963 / 1.400 | 1.957 / 1.458 | 1.966 / 1.476 | 1.881 / 1.336 | 2.179 / 1.664 | 2.069 / 1.522 |
| imit15_dart_s51 | deter | 1.969 / 1.521 | 2.429 / 1.734 | 2.264 / 1.650 | 2.165 / 1.661 | 2.016 / 1.400 | 1.870 / 1.361 | 1.950 / 1.386 | 1.938 / 1.440 | 1.945 / 1.456 | 1.863 / 1.317 | 2.146 / 1.610 | 2.050 / 1.503 |
| imit15_dart_s51 | stoch | 1.978 / 1.530 | 2.435 / 1.743 | 2.273 / 1.660 | 2.176 / 1.672 | 2.037 / 1.426 | 1.885 / 1.380 | 1.970 / 1.411 | 1.957 / 1.463 | 1.963 / 1.476 | 1.878 / 1.336 | 2.144 / 1.617 | 2.063 / 1.519 |
| imit16_fs1_dart_s51 | deter | 2.099 / 1.738 | 2.669 / 2.077 | 2.401 / 1.891 | 2.339 / 1.916 | 2.160 / 1.647 | 1.908 / 1.525 | 2.107 / 1.636 | 2.079 / 1.676 | 2.080 / 1.674 | 2.006 / 1.539 | 2.234 / 1.695 | 2.189 / 1.729 |
| imit16_fs1_dart_s51 | stoch | 2.105 / 1.746 | 2.677 / 2.084 | 2.395 / 1.888 | 2.332 / 1.912 | 2.170 / 1.659 | 1.909 / 1.529 | 2.117 / 1.648 | 2.088 / 1.687 | 2.087 / 1.683 | 2.011 / 1.545 | 2.227 / 1.685 | 2.193 / 1.733 |
| imit15_dart_s52 | deter | 1.986 / 1.544 | 2.451 / 1.764 | 2.280 / 1.676 | 2.185 / 1.689 | 2.038 / 1.431 | 1.881 / 1.381 | 1.970 / 1.413 | 1.959 / 1.471 | 1.966 / 1.484 | 1.881 / 1.341 | 2.154 / 1.625 | 2.068 / 1.529 |
| imit15_dart_s52 | stoch | 1.993 / 1.557 | 2.452 / 1.770 | 2.294 / 1.698 | 2.199 / 1.709 | 2.041 / 1.442 | 1.892 / 1.394 | 1.973 / 1.424 | 1.965 / 1.480 | 1.975 / 1.497 | 1.887 / 1.352 | 2.176 / 1.647 | 2.077 / 1.543 |
| imit15_dart_s53 | deter | 1.991 / 1.553 | 2.458 / 1.773 | 2.287 / 1.691 | 2.192 / 1.704 | 2.034 / 1.432 | 1.877 / 1.379 | 1.967 / 1.414 | 1.957 / 1.470 | 1.966 / 1.487 | 1.877 / 1.339 | 2.156 / 1.620 | 2.069 / 1.533 |
| imit15_dart_s53 | stoch | 1.987 / 1.548 | 2.457 / 1.772 | 2.283 / 1.685 | 2.189 / 1.697 | 2.032 / 1.428 | 1.877 / 1.377 | 1.965 / 1.410 | 1.954 / 1.466 | 1.964 / 1.483 | 1.876 / 1.336 | 2.154 / 1.621 | 2.067 / 1.529 |
| imit19_masonmapped_dart_s51 | deter | 2.044 / 1.643 | 2.546 / 1.972 | 2.265 / 1.707 | 2.203 / 1.750 | 2.108 / 1.582 | 1.876 / 1.441 | 2.087 / 1.569 | 2.024 / 1.567 | 2.030 / 1.587 | 1.953 / 1.436 | 2.225 / 1.499 | 2.124 / 1.614 |
| imit19_masonmapped_dart_s51 | stoch | 2.031 / 1.623 | 2.523 / 1.944 | 2.252 / 1.685 | 2.183 / 1.724 | 2.097 / 1.564 | 1.868 / 1.429 | 2.077 / 1.552 | 2.013 / 1.550 | 2.016 / 1.568 | 1.945 / 1.423 | 2.203 / 1.485 | 2.110 / 1.595 |
| imit18_power_dart_s51 | deter | 1.643 / 1.050 | 2.012 / 1.164 | 1.965 / 1.107 | 1.810 / 1.072 | 1.749 / 0.923 | 1.798 / 1.101 | 1.688 / 0.954 | 1.671 / 1.016 | 1.652 / 1.018 | 1.644 / 0.985 | 1.969 / 1.502 | 1.782 / 1.081 |
| imit18_power_dart_s51 | stoch | 1.643 / 1.050 | 2.012 / 1.164 | 1.965 / 1.107 | 1.810 / 1.072 | 1.749 / 0.923 | 1.798 / 1.101 | 1.688 / 0.954 | 1.671 / 1.016 | 1.652 / 1.018 | 1.644 / 0.985 | 1.969 / 1.502 | 1.782 / 1.081 |
| imit18_power_dart_s52 | deter | 1.643 / 1.050 | 2.012 / 1.164 | 1.965 / 1.107 | 1.810 / 1.072 | 1.749 / 0.923 | 1.798 / 1.101 | 1.688 / 0.954 | 1.671 / 1.016 | 1.652 / 1.018 | 1.644 / 0.985 | 1.969 / 1.502 | 1.782 / 1.081 |
| imit18_power_dart_s52 | stoch | 1.643 / 1.050 | 2.012 / 1.164 | 1.965 / 1.107 | 1.810 / 1.072 | 1.749 / 0.923 | 1.798 / 1.101 | 1.688 / 0.954 | 1.671 / 1.016 | 1.652 / 1.018 | 1.644 / 0.985 | 1.969 / 1.502 | 1.782 / 1.081 |
| ppo15_bcreg_s61 | deter | 2.017 / 1.588 | 2.499 / 1.830 | 2.316 / 1.730 | 2.229 / 1.743 | 2.075 / 1.492 | 1.898 / 1.416 | 2.008 / 1.469 | 1.997 / 1.524 | 2.006 / 1.537 | 1.910 / 1.383 | 2.172 / 1.633 | 2.102 / 1.577 |
| ppo15_bcreg_s61 | stoch | 1.964 / 1.514 | 2.439 / 1.749 | 2.261 / 1.634 | 2.164 / 1.654 | 2.031 / 1.419 | 1.873 / 1.371 | 1.965 / 1.404 | 1.949 / 1.453 | 1.956 / 1.466 | 1.872 / 1.331 | 2.139 / 1.599 | 2.056 / 1.509 |
| ppo15_bcreg_s62 | deter | 2.015 / 1.591 | 2.507 / 1.840 | 2.313 / 1.736 | 2.227 / 1.754 | 2.062 / 1.478 | 1.885 / 1.405 | 1.992 / 1.456 | 1.983 / 1.512 | 1.996 / 1.529 | 1.898 / 1.372 | 2.187 / 1.634 | 2.097 / 1.573 |
| ppo15_bcreg_s62 | stoch | 1.982 / 1.542 | 2.479 / 1.803 | 2.286 / 1.662 | 2.192 / 1.689 | 2.073 / 1.475 | 1.895 / 1.410 | 2.004 / 1.456 | 1.986 / 1.503 | 1.996 / 1.513 | 1.903 / 1.374 | 2.157 / 1.624 | 2.087 / 1.550 |
| ppo15_stoch_s71 | deter | 2.034 / 1.619 | 2.537 / 1.884 | 2.332 / 1.765 | 2.253 / 1.785 | 2.098 / 1.533 | 1.903 / 1.436 | 2.031 / 1.507 | 2.017 / 1.559 | 2.029 / 1.570 | 1.927 / 1.412 | 2.193 / 1.648 | 2.123 / 1.611 |
| ppo15_stoch_s71 | stoch | 2.019 / 1.599 | 2.563 / 1.913 | 2.340 / 1.744 | 2.258 / 1.778 | 2.124 / 1.550 | 1.934 / 1.457 | 2.050 / 1.516 | 2.038 / 1.569 | 2.054 / 1.582 | 1.936 / 1.420 | 2.239 / 1.673 | 2.141 / 1.618 |
| ppo15_anneal_s91 | deter | 2.010 / 1.578 | 2.506 / 1.835 | 2.317 / 1.720 | 2.228 / 1.743 | 2.077 / 1.485 | 1.905 / 1.414 | 2.005 / 1.461 | 1.998 / 1.519 | 2.011 / 1.534 | 1.905 / 1.375 | 2.175 / 1.648 | 2.103 / 1.574 |
| ppo15_anneal_s91 | stoch | 1.969 / 1.521 | 2.436 / 1.741 | 2.273 / 1.652 | 2.177 / 1.667 | 2.025 / 1.406 | 1.886 / 1.367 | 1.955 / 1.390 | 1.946 / 1.446 | 1.956 / 1.464 | 1.866 / 1.318 | 2.161 / 1.623 | 2.059 / 1.508 |
| imit20_fs1_q23_dart_s51 | deter | 1.891 / 1.431 | 2.292 / 1.586 | 2.144 / 1.476 | 2.006 / 1.471 | 1.968 / 1.337 | 1.745 / 1.337 | 1.950 / 1.381 | 1.884 / 1.398 | 1.853 / 1.375 | 1.858 / 1.340 | 1.951 / 1.434 | 1.958 / 1.415 |
| imit20_fs1_q23_dart_s51 | stoch | 1.892 / 1.432 | 2.294 / 1.588 | 2.145 / 1.477 | 2.008 / 1.473 | 1.969 / 1.338 | 1.746 / 1.338 | 1.950 / 1.382 | 1.885 / 1.399 | 1.854 / 1.377 | 1.859 / 1.341 | 1.953 / 1.435 | 1.959 / 1.416 |
| ppo15_klres_s101 | deter | 1.991 / 1.553 | 2.458 / 1.773 | 2.287 / 1.691 | 2.192 / 1.704 | 2.034 / 1.432 | 1.877 / 1.379 | 1.967 / 1.414 | 1.957 / 1.470 | 1.966 / 1.487 | 1.877 / 1.339 | 2.156 / 1.620 | 2.069 / 1.533 |
| ppo15_klres_s101 | stoch | 1.986 / 1.546 | 2.456 / 1.771 | 2.281 / 1.680 | 2.187 / 1.693 | 2.031 / 1.427 | 1.877 / 1.376 | 1.964 / 1.409 | 1.953 / 1.464 | 1.962 / 1.481 | 1.875 / 1.335 | 2.153 / 1.619 | 2.066 / 1.527 |
| ppo20_klres_s111 | deter | 1.891 / 1.431 | 2.292 / 1.586 | 2.144 / 1.476 | 2.006 / 1.471 | 1.968 / 1.337 | 1.745 / 1.337 | 1.950 / 1.381 | 1.884 / 1.398 | 1.853 / 1.375 | 1.858 / 1.340 | 1.951 / 1.434 | 1.958 / 1.415 |
| ppo20_klres_s111 | stoch | 1.893 / 1.433 | 2.295 / 1.590 | 2.146 / 1.479 | 2.009 / 1.474 | 1.969 / 1.339 | 1.746 / 1.338 | 1.951 / 1.383 | 1.886 / 1.400 | 1.855 / 1.377 | 1.859 / 1.341 | 1.954 / 1.436 | 1.960 / 1.417 |
| ppo20_soft_s121 | deter | 1.890 / 1.429 | 2.290 / 1.584 | 2.143 / 1.474 | 2.005 / 1.469 | 1.967 / 1.335 | 1.744 / 1.336 | 1.949 / 1.380 | 1.883 / 1.396 | 1.852 / 1.374 | 1.858 / 1.339 | 1.950 / 1.432 | 1.957 / 1.414 |
| ppo20_soft_s121 | stoch | 1.890 / 1.430 | 2.291 / 1.585 | 2.144 / 1.475 | 2.006 / 1.470 | 1.967 / 1.336 | 1.745 / 1.336 | 1.950 / 1.380 | 1.884 / 1.397 | 1.852 / 1.375 | 1.858 / 1.339 | 1.951 / 1.433 | 1.958 / 1.414 |
| ppo15_soft_s122 | deter | 1.991 / 1.553 | 2.458 / 1.773 | 2.287 / 1.691 | 2.192 / 1.704 | 2.034 / 1.432 | 1.877 / 1.379 | 1.967 / 1.414 | 1.957 / 1.470 | 1.966 / 1.487 | 1.877 / 1.339 | 2.156 / 1.620 | 2.069 / 1.533 |
| ppo15_soft_s122 | stoch | 1.989 / 1.549 | 2.458 / 1.775 | 2.283 / 1.682 | 2.190 / 1.695 | 2.040 / 1.438 | 1.882 / 1.383 | 1.972 / 1.420 | 1.962 / 1.475 | 1.970 / 1.490 | 1.881 / 1.343 | 2.157 / 1.626 | 2.071 / 1.534 |

## Contact regressions (vs best earlier-trained checkpoint, same mode)

- ppo_scott_prev_backup [stochastic]: contact 52% < best previous 100% (ppo_v4yaw_s43)
- ppo_scott_curr [stochastic]: contact 36% < best previous 100% (ppo_v4yaw_s43)
- ppo_scott_baseline [deterministic]: contact 0% < best previous 100% (ppo_v4yaw_s43)
- ppo_scott_baseline [stochastic]: contact 0% < best previous 100% (ppo_v4yaw_s43)
- ppo_scott/ppo_scott_carry1 [deterministic]: contact 98% < best previous 100% (ppo_v4yaw_s43)
- ppo_scott/ppo_scott_carry1 [stochastic]: contact 68% < best previous 100% (ppo_v4yaw_s43)
- ppo_scott_final2/ppo_scott_prev2_backup [deterministic]: contact 48% < best previous 100% (ppo_v4yaw_s43)
- ppo_scott_final2/ppo_scott_prev2_backup [stochastic]: contact 46% < best previous 100% (ppo_v4yaw_s43)
- ppo_resid_v3_s0 [stochastic]: contact 64% < best previous 100% (ppo_v4yaw_s43)
- imit10_w000_s51_tr [deterministic]: contact 94% < best previous 100% (ppo_v4yaw_s43)
- imit10_w000_s51_tr [stochastic]: contact 98% < best previous 100% (ppo_v4yaw_s43)
- imit13_w000_s51 [deterministic]: contact 96% < best previous 100% (ppo_v4yaw_s43)
- imit13_w000_s51 [stochastic]: contact 98% < best previous 100% (ppo_v4yaw_s43)
- imit14_w000_s51 [deterministic]: contact 96% < best previous 100% (ppo_v4yaw_s43)
- imit15_dart_s51 [stochastic]: contact 98% < best previous 100% (ppo_v4yaw_s43)
- imit16_fs1_dart_s51 [stochastic]: contact 98% < best previous 100% (ppo_v4yaw_s43)
- imit15_dart_s52 [deterministic]: contact 98% < best previous 100% (ppo_v4yaw_s43)
- ppo15_bcreg_s61 [deterministic]: contact 98% < best previous 100% (ppo_v4yaw_s43)
- ppo15_bcreg_s62 [stochastic]: contact 98% < best previous 100% (ppo_v4yaw_s43)
- ppo15_stoch_s71 [deterministic]: contact 96% < best previous 100% (ppo_v4yaw_s43)
- ppo15_anneal_s91 [deterministic]: contact 98% < best previous 100% (ppo_v4yaw_s43)
- ppo15_soft_s122 [stochastic]: contact 98% < best previous 100% (ppo_v4yaw_s43)

## History (all evaluated checkpoints)

| Checkpoint(s) | Steps | Env | Det contact | Stoch contact |
|---|---|---|---|---|
| ppo_scott(30k, old), ppo_scott_prev_backup | 30000 | pre-v2-physics | 100% | 18% |
| ppo_scott_final2, ppo_scott(60k) | 60000 | pre-v2-physics | 98% | 52% |
| ppo_scott_baseline | 30000 | f0a3f737fc77 | 0% | 0% |
| ppo_scott_baseline | 30000 | ae180bdc10a3 | 0% | 0% |
| ppo_scott_baseline | 30000 | e9a0050d94b6 | 0% | 0% |
| ppo_scott_baseline | 30000 | 9145629439d4 | 0% | 0% |
| ppo_scott_baseline | 30000 | 25d5c5608c4d | 0% | 0% |
| ppo_scott_baseline | 30000 | 59bc5ea99d60 | 0% | 0% |
| ppo_scott_baseline | 30000 | 99f124d7b5dd | 0% | 0% |
| ppo_scott_baseline | 30000 | 95e60a7e2ccf | 0% | 0% |
| ppo_scott_baseline | 30000 | df95da5d35d6 | 0% | 0% |
| ppo_scott_baseline | 30000 | 7a2ffa104b56 | 0% | 0% |
| ppo_scott_baseline | 30000 | 536694401cb9 | 0% | 0% |
| ppo_scott_curr | 30000 | f0a3f737fc77 | 100% | 34% |
| ppo_scott_curr | 30000 | ae180bdc10a3 | 100% | 34% |
| ppo_scott_curr | 30000 | e9a0050d94b6 | 100% | 34% |
| ppo_scott_curr | 30000 | 9145629439d4 | 100% | 34% |
| ppo_scott_curr | 30000 | 25d5c5608c4d | 100% | 34% |
| ppo_scott_curr | 30000 | 59bc5ea99d60 | 100% | 34% |
| ppo_scott_curr | 30000 | 99f124d7b5dd | 100% | 34% |
| ppo_scott_curr | 30000 | 95e60a7e2ccf | 100% | 34% |
| ppo_scott_curr | 30000 | df95da5d35d6 | 100% | 34% |
| ppo_scott_curr | 30000 | 7a2ffa104b56 | 100% | 34% |
| ppo_scott_curr | 30000 | 536694401cb9 | 100% | 34% |
| ppo_scott_prev_backup | 30000 | f0a3f737fc77 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | ae180bdc10a3 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | e9a0050d94b6 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 9145629439d4 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 25d5c5608c4d | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 59bc5ea99d60 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 99f124d7b5dd | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 95e60a7e2ccf | 100% | 38% |
| ppo_scott_prev_backup | 30000 | df95da5d35d6 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 7a2ffa104b56 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 536694401cb9 | 100% | 38% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | f0a3f737fc77 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | ae180bdc10a3 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | e9a0050d94b6 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 9145629439d4 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 25d5c5608c4d | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 59bc5ea99d60 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 99f124d7b5dd | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 95e60a7e2ccf | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | df95da5d35d6 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 7a2ffa104b56 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 536694401cb9 | 48% | 60% |
| ppo_scott, ppo_scott_carry1 | 100000 | f0a3f737fc77 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | ae180bdc10a3 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | e9a0050d94b6 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 9145629439d4 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 25d5c5608c4d | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 59bc5ea99d60 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 99f124d7b5dd | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 95e60a7e2ccf | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | df95da5d35d6 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 7a2ffa104b56 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 536694401cb9 | 98% | 66% |
| ppo_resid_v3_s0 | 60000 | 99f124d7b5dd | n/a | n/a |
| ppo_resid_v3_s0 | 60000 | 95e60a7e2ccf | 100% | 60% |
| ppo_resid_v3_s0 | 60000 | df95da5d35d6 | 100% | 60% |
| ppo_resid_v3_s0 | 60000 | 7a2ffa104b56 | 100% | 60% |
| ppo_resid_v3_s0 | 60000 | 536694401cb9 | 100% | 60% |
| ppo_resid_v3_r2_s0 | 60000 | 99f124d7b5dd | n/a | n/a |
| ppo_resid_v3_r2_s0 | 60000 | 95e60a7e2ccf | 100% | 100% |
| ppo_resid_v3_r2_s0 | 60000 | df95da5d35d6 | 100% | 100% |
| ppo_resid_v3_r2_s0 | 60000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_r2_s0 | 60000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_r3_s0 | 100000 | 99f124d7b5dd | n/a | n/a |
| ppo_resid_v3_r3_s0 | 100000 | 95e60a7e2ccf | 100% | 100% |
| ppo_resid_v3_r3_s0 | 100000 | df95da5d35d6 | 100% | 100% |
| ppo_resid_v3_r3_s0 | 100000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_r3_s0 | 100000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_ladder_s0 | 150000 | 99f124d7b5dd | n/a | n/a |
| ppo_resid_v3_ladder_s0 | 150000 | 95e60a7e2ccf | 100% | 100% |
| ppo_resid_v3_ladder_s0 | 150000 | df95da5d35d6 | 100% | 100% |
| ppo_resid_v3_ladder_s0 | 150000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_ladder_s0 | 150000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an1_s0 | 150000 | 99f124d7b5dd | 100% | 100% |
| ppo_resid_v3_left_an1_s0 | 150000 | 95e60a7e2ccf | 100% | 100% |
| ppo_resid_v3_left_an1_s0 | 150000 | df95da5d35d6 | 100% | 100% |
| ppo_resid_v3_left_an1_s0 | 150000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an1_s0 | 150000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an2_s0, best_carry_analytic | 150000 | 99f124d7b5dd | 100% | 100% |
| ppo_resid_v3_left_an2_s0, best_carry_analytic | 150000 | 95e60a7e2ccf | 100% | 100% |
| ppo_resid_v3_left_an2_s0, best_carry_analytic | 150000 | df95da5d35d6 | 100% | 100% |
| ppo_resid_v3_left_an2_s0, best_carry_analytic | 150000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an2_s0, best_carry_analytic | 150000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | 99f124d7b5dd | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | 95e60a7e2ccf | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | df95da5d35d6 | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an4_s2 | 150000 | df95da5d35d6 | 100% | 100% |
| ppo_resid_v3_left_an4_s2 | 150000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an4_s2 | 150000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_an4_s2 | 150000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an5_s3 | 150000 | df95da5d35d6 | 100% | 100% |
| ppo_resid_v3_left_an5_s3 | 150000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an5_s3 | 150000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_an5_s3 | 150000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an6_s4 | 150000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an6_s4 | 150000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_an6_s4 | 150000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an7_s5 | 120000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an7_s5 | 120000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_an7_s5 | 120000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an8_s6 | 120000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an8_s6 | 120000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_an8_s6 | 120000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an9_s7 | 120000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an9_s7 | 120000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_an9_s7 | 120000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an10_s8 | 120000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an10_s8 | 120000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_an10_s8 | 120000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_fast1_s10 | 100000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_fast1_s10 | 100000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_fast1_s10 | 100000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_fast2_s11, best_gate_flat_123mph | 100000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_fast2_s11, best_gate_flat_123mph | 100000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_fast2_s11, best_gate_flat_123mph | 100000 | 536694401cb9 | 100% | 100% |
| ppo_v3tiny_s22 | 60000 | 737c4d124c92 | 100% | 100% |
| ppo_v3tiny_s22 | 60000 | 536694401cb9 | 100% | 100% |
| ppo_v3tiny_s21 | 60000 | 737c4d124c92 | 100% | 100% |
| ppo_v3tiny_s21 | 60000 | 536694401cb9 | 100% | 100% |
| ppo_v3tiny_s23 | 60000 | 737c4d124c92 | 100% | 100% |
| ppo_v3tiny_s23 | 60000 | 536694401cb9 | 100% | 100% |
| ppo_v3flt_all_s33 | 30000 | 536694401cb9 | 100% | 100% |
| ppo_v3flt_yaw_s32, best_learned_yaw_s32 | 30000 | 536694401cb9 | 100% | 100% |
| ppo_v3flt_yaw_s31, best_learned_yaw_s31 | 30000 | 536694401cb9 | 100% | 100% |
| imit_w075_s53 | 0 | 30178ef58c6a | 100% | 100% |
| imit_w075_s51 | 0 | 30178ef58c6a | 100% | 100% |
| imit_w075_s52 | 0 | 30178ef58c6a | 100% | 100% |
| imit2_w075_s53 | 15000 | 30178ef58c6a | 100% | 100% |
| imit2_w075_s51 | 15000 | 30178ef58c6a | 100% | 100% |
| imit2_w075_s52 | 15000 | 30178ef58c6a | 100% | 100% |
| imit3_w075_s51 | 8000 | 30178ef58c6a | 100% | 100% |
| imit3_w075_s52 | 8000 | 30178ef58c6a | 100% | 100% |
| imit3_w050_s51 | 8000 | 30178ef58c6a | 100% | 100% |
| imit3_w050_s52 | 8000 | 30178ef58c6a | 100% | 100% |
| imit3_w075_s53 | 8000 | 30178ef58c6a | 100% | 100% |
| imit3_w025_s52 | 8000 | 30178ef58c6a | 100% | 100% |
| imit3_w025_s51 | 8000 | 30178ef58c6a | 100% | 100% |
| imit3_w000_s51, best_imit_scriptfree_s51_NOTPASS_lat3.56 | 8000 | 30178ef58c6a | 100% | 100% |
| imit4_w000_s52 | 10000 | 30178ef58c6a | 100% | 100% |
| imit4_w000_s51 | 10000 | 30178ef58c6a | 100% | 100% |
| imit5_w000_s52 | 0 | 30178ef58c6a | 100% | 100% |
| imit5_w000_s51 | 0 | 30178ef58c6a | 100% | 100% |
| best_carry_analytic, ppo_resid_v3_left_an2_s0 | 150000 | 53db5ffb5eff | 100% | 100% |
| best_carry_analytic, ppo_resid_v3_left_an2_s0 | 150000 | 2341d588d952 | 100% | 100% |
| best_gate_flat_123mph, ppo_resid_v3_left_fast2_s11 | 100000 | 53db5ffb5eff | 100% | 100% |
| best_gate_flat_123mph, ppo_resid_v3_left_fast2_s11 | 100000 | 2341d588d952 | 100% | 100% |
| best_imit_scriptfree_s51_NOTPASS_lat3.56, imit3_w000_s51 | 8000 | 53db5ffb5eff | 100% | 100% |
| best_imit_scriptfree_s51_NOTPASS_lat3.56, imit3_w000_s51 | 8000 | 2341d588d952 | 100% | 100% |
| best_imit_scriptfree_s51_seed4000-8000only, imit5_w000_s51 | 0 | 53db5ffb5eff | 100% | 100% |
| best_imit_scriptfree_s51_seed4000-8000only, imit5_w000_s51 | 0 | 2341d588d952 | 100% | 100% |
| best_imit_w050_s52, imit3_w050_s52 | 8000 | 53db5ffb5eff | 100% | 100% |
| best_imit_w050_s52, imit3_w050_s52 | 8000 | 2341d588d952 | 100% | 100% |
| best_learned_yaw_s31, ppo_v3flt_yaw_s31 | 30000 | 53db5ffb5eff | 100% | 100% |
| best_v4yaw_s41, ppo_v4yaw_s41 | 30000 | 53db5ffb5eff | 100% | 100% |
| best_learned_yaw_s32, ppo_v3flt_yaw_s32 | 30000 | 53db5ffb5eff | 100% | 100% |
| best_learned_yaw_s31, ppo_v3flt_yaw_s31 | 30000 | 2341d588d952 | 100% | 100% |
| best_v4yaw_s41, ppo_v4yaw_s41 | 30000 | 2341d588d952 | 100% | 100% |
| best_learned_yaw_s32, ppo_v3flt_yaw_s32 | 30000 | 2341d588d952 | 100% | 100% |
| imit2_w075_s51 | 15000 | 53db5ffb5eff | 100% | 100% |
| imit2_w075_s52 | 15000 | 53db5ffb5eff | 100% | 100% |
| imit2_w075_s51 | 15000 | 2341d588d952 | 100% | 100% |
| imit2_w075_s52 | 15000 | 2341d588d952 | 100% | 100% |
| imit2_w075_s53 | 15000 | 53db5ffb5eff | 100% | 100% |
| imit2_w075_s53 | 15000 | 2341d588d952 | 100% | 100% |
| imit3_w000_s52 | 8000 | 53db5ffb5eff | 100% | 100% |
| imit3_w000_s52 | 8000 | 2341d588d952 | 100% | 100% |
| imit3_w025_s51 | 8000 | 53db5ffb5eff | 100% | 100% |
| imit3_w025_s51 | 8000 | 2341d588d952 | 100% | 100% |
| imit3_w025_s52 | 8000 | 53db5ffb5eff | 100% | 100% |
| imit3_w025_s52 | 8000 | 2341d588d952 | 100% | 100% |
| imit3_w050_s51 | 8000 | 53db5ffb5eff | 100% | 100% |
| imit3_w050_s51 | 8000 | 2341d588d952 | 100% | 100% |
| imit3_w075_s51 | 8000 | 53db5ffb5eff | 100% | 100% |
| imit3_w075_s51 | 8000 | 2341d588d952 | 100% | 100% |
| imit3_w075_s52 | 8000 | 53db5ffb5eff | 100% | 100% |
| imit3_w075_s52 | 8000 | 2341d588d952 | 100% | 100% |
| imit3_w075_s53 | 8000 | 53db5ffb5eff | 100% | 100% |
| imit3_w075_s53 | 8000 | 2341d588d952 | 100% | 100% |
| imit4_w000_s51 | 10000 | 53db5ffb5eff | 100% | 100% |
| imit4_w000_s51 | 10000 | 2341d588d952 | 100% | 100% |
| imit4_w000_s52 | 10000 | 53db5ffb5eff | 100% | 100% |
| imit4_w000_s52 | 10000 | 2341d588d952 | 100% | 100% |
| imit5_w000_s52 | 0 | 53db5ffb5eff | 100% | 100% |
| imit5_w000_s52 | 0 | 2341d588d952 | 100% | 100% |
| imit_w075_s51 | 0 | 53db5ffb5eff | 100% | 100% |
| imit_w075_s51 | 0 | 2341d588d952 | 100% | 100% |
| imit_w075_s52 | 0 | 53db5ffb5eff | 100% | 100% |
| imit_w075_s52 | 0 | 2341d588d952 | 100% | 100% |
| imit_w075_s53 | 0 | 53db5ffb5eff | 100% | 100% |
| ppo_resid_v3_ladder_s0 | 150000 | 53db5ffb5eff | 100% | 100% |
| imit_w075_s53 | 0 | 2341d588d952 | 100% | 100% |
| ppo_resid_v3_ladder_s0 | 150000 | 2341d588d952 | 100% | 100% |
| ppo_resid_v3_left_an1_s0 | 150000 | 53db5ffb5eff | 100% | 100% |
| ppo_resid_v3_left_an10_s8 | 120000 | 53db5ffb5eff | 100% | 100% |
| ppo_resid_v3_left_an1_s0 | 150000 | 2341d588d952 | 100% | 100% |
| ppo_resid_v3_left_an10_s8 | 120000 | 2341d588d952 | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | 53db5ffb5eff | 100% | 100% |
| ppo_resid_v3_left_an5_s3 | 150000 | 53db5ffb5eff | 100% | 100% |
| ppo_resid_v3_left_an4_s2 | 150000 | 53db5ffb5eff | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | 2341d588d952 | 100% | 100% |
| ppo_resid_v3_left_an5_s3 | 150000 | 2341d588d952 | 100% | 100% |
| ppo_resid_v3_left_an4_s2 | 150000 | 2341d588d952 | 100% | 100% |
| ppo_resid_v3_left_an7_s5 | 120000 | 53db5ffb5eff | 100% | 100% |
| ppo_resid_v3_left_an8_s6 | 120000 | 53db5ffb5eff | 100% | 100% |
| ppo_resid_v3_left_an9_s7 | 120000 | 53db5ffb5eff | 100% | 100% |
| ppo_resid_v3_left_an6_s4 | 150000 | 53db5ffb5eff | 100% | 100% |
| ppo_resid_v3_left_fast1_s10 | 100000 | 53db5ffb5eff | 100% | 100% |
| ppo_resid_v3_left_an7_s5 | 120000 | 2341d588d952 | 100% | 100% |
| ppo_resid_v3_left_an8_s6 | 120000 | 2341d588d952 | 100% | 100% |
| ppo_resid_v3_left_an9_s7 | 120000 | 2341d588d952 | 100% | 100% |
| ppo_resid_v3_left_an6_s4 | 150000 | 2341d588d952 | 100% | 100% |
| ppo_resid_v3_left_fast1_s10 | 100000 | 2341d588d952 | 100% | 100% |
| ppo_resid_v3_r2_s0 | 60000 | 53db5ffb5eff | 100% | 100% |
| ppo_resid_v3_r2_s0 | 60000 | 2341d588d952 | 100% | 100% |
| ppo_resid_v3_r3_s0 | 100000 | 53db5ffb5eff | 100% | 100% |
| ppo_resid_v3_s0 | 60000 | 53db5ffb5eff | 100% | 64% |
| ppo_resid_v3_r3_s0 | 100000 | 2341d588d952 | 100% | 100% |
| ppo_resid_v3_s0 | 60000 | 2341d588d952 | 100% | 64% |
| ppo_scott, ppo_scott_carry1 | 100000 | 53db5ffb5eff | 98% | 68% |
| ppo_scott_baseline | 30000 | 53db5ffb5eff | 0% | 0% |
| ppo_scott, ppo_scott_carry1 | 100000 | 2341d588d952 | 98% | 68% |
| ppo_scott_baseline | 30000 | 2341d588d952 | 0% | 0% |
| ppo_scott_curr | 30000 | 53db5ffb5eff | 100% | 36% |
| ppo_scott_prev2_backup, ppo_scott_final2 | 60000 | 53db5ffb5eff | 48% | 46% |
| ppo_scott_curr | 30000 | 2341d588d952 | 100% | 36% |
| ppo_scott_prev2_backup, ppo_scott_final2 | 60000 | 2341d588d952 | 48% | 46% |
| ppo_v3flt_all_s33 | 30000 | 53db5ffb5eff | 100% | 100% |
| ppo_scott_prev_backup | 30000 | 53db5ffb5eff | 100% | 52% |
| ppo_v3flt_all_s33 | 30000 | 2341d588d952 | 100% | 100% |
| ppo_scott_prev_backup | 30000 | 2341d588d952 | 100% | 52% |
| ppo_v3tiny_s21 | 60000 | 53db5ffb5eff | 100% | 100% |
| ppo_v3tiny_s21 | 60000 | 2341d588d952 | 100% | 100% |
| ppo_v4power_s62 | 30000 | 53db5ffb5eff | 100% | 100% |
| ppo_v4power_s61 | 30000 | 53db5ffb5eff | 100% | 100% |
| ppo_v3tiny_s22 | 60000 | 53db5ffb5eff | 100% | 100% |
| ppo_v3tiny_s23 | 60000 | 53db5ffb5eff | 100% | 100% |
| ppo_v4power_s62 | 30000 | 2341d588d952 | 100% | 100% |
| ppo_v4power_s61 | 30000 | 2341d588d952 | 100% | 100% |
| ppo_v3tiny_s22 | 60000 | 2341d588d952 | 100% | 100% |
| ppo_v3tiny_s23 | 60000 | 2341d588d952 | 100% | 100% |
| ppo_v4yaw_s42 | 30000 | 53db5ffb5eff | 100% | 100% |
| ppo_v4yaw_s43 | 30000 | 53db5ffb5eff | 100% | 100% |
| ppo_v4yaw_s42 | 30000 | 2341d588d952 | 100% | 100% |
| ppo_v4yaw_s43 | 30000 | 2341d588d952 | 100% | 100% |
| best_imit_scriptfree_elbow48_s51, imit9_w000_s51 | 0 | 2341d588d952 | 100% | 100% |
| imit7_w000_s51 | 0 | 2341d588d952 | 100% | 100% |
| imit8_w000_s51 | 0 | 2341d588d952 | 100% | 100% |
| imit9_w000_s52 | 0 | 2341d588d952 | 100% | 100% |
| ppo_v4power48_s71 | 30000 | 2341d588d952 | 100% | 100% |
| imit9_w000_s53 | 0 | 2341d588d952 | 100% | 100% |
| ppo_scott_prev_backup | 30000 | 833a022042ef | 100% | 52% |
| ppo_scott_prev_backup | 30000 | 36680f639c27 | 100% | 52% |
| ppo_scott_curr | 30000 | 833a022042ef | 100% | 36% |
| ppo_scott_curr | 30000 | 36680f639c27 | 100% | 36% |
| ppo_scott_baseline | 30000 | 833a022042ef | 0% | 0% |
| ppo_scott_baseline | 30000 | 36680f639c27 | 0% | 0% |
| ppo_scott, ppo_scott_carry1 | 100000 | 833a022042ef | 98% | 68% |
| ppo_scott, ppo_scott_carry1 | 100000 | 36680f639c27 | 98% | 68% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 833a022042ef | 48% | 46% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 36680f639c27 | 48% | 46% |
| ppo_resid_v3_s0 | 60000 | 833a022042ef | 100% | 64% |
| ppo_resid_v3_s0 | 60000 | 36680f639c27 | 100% | 64% |
| ppo_resid_v3_r2_s0 | 60000 | 833a022042ef | 100% | 100% |
| ppo_resid_v3_r2_s0 | 60000 | 36680f639c27 | 100% | 100% |
| ppo_resid_v3_r3_s0 | 100000 | 833a022042ef | 100% | 100% |
| ppo_resid_v3_r3_s0 | 100000 | 36680f639c27 | 100% | 100% |
| ppo_resid_v3_ladder_s0 | 150000 | 833a022042ef | 100% | 100% |
| ppo_resid_v3_ladder_s0 | 150000 | 36680f639c27 | 100% | 100% |
| ppo_resid_v3_left_an1_s0 | 150000 | 833a022042ef | 100% | 100% |
| ppo_resid_v3_left_an1_s0 | 150000 | 36680f639c27 | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | 833a022042ef | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | 36680f639c27 | 100% | 100% |
| ppo_resid_v3_left_an4_s2 | 150000 | 833a022042ef | 100% | 100% |
| ppo_resid_v3_left_an4_s2 | 150000 | 36680f639c27 | 100% | 100% |
| ppo_resid_v3_left_an5_s3 | 150000 | 833a022042ef | 100% | 100% |
| ppo_resid_v3_left_an5_s3 | 150000 | 36680f639c27 | 100% | 100% |
| best_carry_analytic, ppo_resid_v3_left_an2_s0 | 150000 | 833a022042ef | 100% | 100% |
| best_carry_analytic, ppo_resid_v3_left_an2_s0 | 150000 | 36680f639c27 | 100% | 100% |
| ppo_resid_v3_left_an6_s4 | 150000 | 833a022042ef | 100% | 100% |
| ppo_resid_v3_left_an6_s4 | 150000 | 36680f639c27 | 100% | 100% |
| ppo_resid_v3_left_an8_s6 | 120000 | 833a022042ef | 100% | 100% |
| ppo_resid_v3_left_an8_s6 | 120000 | 36680f639c27 | 100% | 100% |
| ppo_resid_v3_left_an7_s5 | 120000 | 833a022042ef | 100% | 100% |
| ppo_resid_v3_left_an7_s5 | 120000 | 36680f639c27 | 100% | 100% |
| ppo_resid_v3_left_an9_s7 | 120000 | 833a022042ef | 100% | 100% |
| ppo_resid_v3_left_an9_s7 | 120000 | 36680f639c27 | 100% | 100% |
| ppo_resid_v3_left_an10_s8 | 120000 | 833a022042ef | 100% | 100% |
| ppo_resid_v3_left_an10_s8 | 120000 | 36680f639c27 | 100% | 100% |
| ppo_resid_v3_left_fast1_s10 | 100000 | 833a022042ef | 100% | 100% |
| ppo_resid_v3_left_fast1_s10 | 100000 | 36680f639c27 | 100% | 100% |
| best_gate_flat_123mph, ppo_resid_v3_left_fast2_s11 | 100000 | 833a022042ef | 100% | 100% |
| best_gate_flat_123mph, ppo_resid_v3_left_fast2_s11 | 100000 | 36680f639c27 | 100% | 100% |
| ppo_v3tiny_s22 | 60000 | 833a022042ef | 100% | 100% |
| ppo_v3tiny_s22 | 60000 | 36680f639c27 | 100% | 100% |
| ppo_v3tiny_s23 | 60000 | 833a022042ef | 100% | 100% |
| ppo_v3tiny_s23 | 60000 | 36680f639c27 | 100% | 100% |
| ppo_v3tiny_s21 | 60000 | 833a022042ef | 100% | 100% |
| ppo_v3tiny_s21 | 60000 | 36680f639c27 | 100% | 100% |
| ppo_v3flt_all_s33 | 30000 | 833a022042ef | 100% | 100% |
| ppo_v3flt_all_s33 | 30000 | 36680f639c27 | 100% | 100% |
| best_learned_yaw_s32, ppo_v3flt_yaw_s32 | 30000 | 833a022042ef | 100% | 100% |
| best_learned_yaw_s32, ppo_v3flt_yaw_s32 | 30000 | 36680f639c27 | 100% | 100% |
| best_learned_yaw_s31, ppo_v3flt_yaw_s31 | 30000 | 833a022042ef | 100% | 100% |
| best_learned_yaw_s31, ppo_v3flt_yaw_s31 | 30000 | 36680f639c27 | 100% | 100% |
| ppo_v4yaw_s43 | 30000 | 833a022042ef | 100% | 100% |
| ppo_v4yaw_s43 | 30000 | 36680f639c27 | 100% | 100% |
| ppo_v4yaw_s42 | 30000 | 833a022042ef | 100% | 100% |
| ppo_v4yaw_s42 | 30000 | 36680f639c27 | 100% | 100% |
| best_v4yaw_s41, ppo_v4yaw_s41 | 30000 | 833a022042ef | 100% | 100% |
| best_v4yaw_s41, ppo_v4yaw_s41 | 30000 | 36680f639c27 | 100% | 100% |
| imit_w075_s51 | 0 | 833a022042ef | 100% | 100% |
| imit_w075_s51 | 0 | 36680f639c27 | 100% | 100% |
| imit_w075_s53 | 0 | 833a022042ef | 100% | 100% |
| imit_w075_s53 | 0 | 36680f639c27 | 100% | 100% |
| imit_w075_s52 | 0 | 833a022042ef | 100% | 100% |
| imit_w075_s52 | 0 | 36680f639c27 | 100% | 100% |
| imit2_w075_s51 | 15000 | 833a022042ef | 100% | 100% |
| imit2_w075_s51 | 15000 | 36680f639c27 | 100% | 100% |
| imit2_w075_s52 | 15000 | 833a022042ef | 100% | 100% |
| imit2_w075_s53 | 15000 | 833a022042ef | 100% | 100% |
| imit2_w075_s52 | 15000 | 36680f639c27 | 100% | 100% |
| imit2_w075_s53 | 15000 | 36680f639c27 | 100% | 100% |
| imit3_w075_s51 | 8000 | 833a022042ef | 100% | 100% |
| imit3_w075_s52 | 8000 | 833a022042ef | 100% | 100% |
| imit3_w075_s51 | 8000 | 36680f639c27 | 100% | 100% |
| imit3_w075_s52 | 8000 | 36680f639c27 | 100% | 100% |
| imit3_w075_s53 | 8000 | 833a022042ef | 100% | 100% |
| imit3_w075_s53 | 8000 | 36680f639c27 | 100% | 100% |
| imit3_w050_s51 | 8000 | 833a022042ef | 100% | 100% |
| imit3_w050_s51 | 8000 | 36680f639c27 | 100% | 100% |
| best_imit_w050_s52, imit3_w050_s52 | 8000 | 833a022042ef | 100% | 100% |
| best_imit_w050_s52, imit3_w050_s52 | 8000 | 36680f639c27 | 100% | 100% |
| imit3_w025_s51 | 8000 | 833a022042ef | 100% | 100% |
| imit3_w025_s51 | 8000 | 36680f639c27 | 100% | 100% |
| imit3_w025_s52 | 8000 | 833a022042ef | 100% | 100% |
| imit3_w025_s52 | 8000 | 36680f639c27 | 100% | 100% |
| imit3_w000_s52 | 8000 | 833a022042ef | 100% | 100% |
| imit3_w000_s52 | 8000 | 36680f639c27 | 100% | 100% |
| best_imit_scriptfree_s51_NOTPASS_lat3.56, imit3_w000_s51 | 8000 | 833a022042ef | 100% | 100% |
| best_imit_scriptfree_s51_NOTPASS_lat3.56, imit3_w000_s51 | 8000 | 36680f639c27 | 100% | 100% |
| imit4_w000_s52 | 10000 | 833a022042ef | 100% | 100% |
| imit4_w000_s51 | 10000 | 833a022042ef | 100% | 100% |
| imit4_w000_s52 | 10000 | 36680f639c27 | 100% | 100% |
| imit4_w000_s51 | 10000 | 36680f639c27 | 100% | 100% |
| imit5_w000_s52 | 0 | 833a022042ef | 100% | 100% |
| imit5_w000_s52 | 0 | 36680f639c27 | 100% | 100% |
| best_imit_scriptfree_s51_seed4000-8000only, imit5_w000_s51 | 0 | 833a022042ef | 100% | 100% |
| best_imit_scriptfree_s51_seed4000-8000only, imit5_w000_s51 | 0 | 36680f639c27 | 100% | 100% |
| ppo_v4power_s61 | 30000 | 833a022042ef | 100% | 100% |
| ppo_v4power_s62 | 30000 | 833a022042ef | 100% | 100% |
| ppo_v4power_s61 | 30000 | 36680f639c27 | 100% | 100% |
| ppo_v4power_s62 | 30000 | 36680f639c27 | 100% | 100% |
| imit7_w000_s51 | 0 | 30fc5e622b69 | 100% | 100% |
| imit7_w000_s51 | 0 | 833a022042ef | 100% | 100% |
| imit7_w000_s51 | 0 | 36680f639c27 | 100% | 100% |
| ppo_v4power48_s71 | 30000 | 30fc5e622b69 | 100% | 100% |
| ppo_v4power48_s71 | 30000 | 833a022042ef | 100% | 100% |
| ppo_v4power48_s71 | 30000 | 36680f639c27 | 100% | 100% |
| imit8_w000_s51 | 0 | 30fc5e622b69 | 100% | 100% |
| imit8_w000_s51 | 0 | 833a022042ef | 100% | 100% |
| imit8_w000_s51 | 0 | 36680f639c27 | 100% | 100% |
| imit9_w000_s53 | 0 | 30fc5e622b69 | 100% | 100% |
| imit9_w000_s53 | 0 | 833a022042ef | 100% | 100% |
| imit9_w000_s53 | 0 | 36680f639c27 | 100% | 100% |
| imit10_w000_s51_tr | 20000 | 833a022042ef | 94% | 98% |
| imit10_w000_s51_tr | 20000 | 36680f639c27 | 94% | 98% |
| best_imit_scriptfree_elbow48_s51, imit9_w000_s51 | 0 | 833a022042ef | 100% | 100% |
| best_imit_scriptfree_elbow48_s51, imit9_w000_s51 | 0 | 36680f639c27 | 100% | 100% |
| imit9_w000_s52 | 0 | 30fc5e622b69 | 100% | 100% |
| imit9_w000_s52 | 0 | 833a022042ef | 100% | 100% |
| imit9_w000_s52 | 0 | 36680f639c27 | 100% | 100% |
| imit13_w000_s51 | 0 | 30fc5e622b69 | 96% | 98% |
| imit13_w000_s51 | 0 | 833a022042ef | 96% | 98% |
| imit13_w000_s51 | 0 | 36680f639c27 | 96% | 98% |
| imit13_w000_s52 | 0 | 30fc5e622b69 | 100% | 100% |
| imit13_w000_s52 | 0 | 833a022042ef | 100% | 100% |
| imit13_w000_s52 | 0 | 36680f639c27 | 100% | 100% |
| imit14_w000_s51 | 0 | 30fc5e622b69 | 96% | 100% |
| imit14_w000_s51 | 0 | 833a022042ef | 96% | 100% |
| imit14_w000_s51 | 0 | 36680f639c27 | 96% | 100% |
| imit15_dart_s51 | 0 | 30fc5e622b69 | 100% | 98% |
| imit15_dart_s51 | 0 | 833a022042ef | 100% | 98% |
| imit15_dart_s51 | 0 | 36680f639c27 | 100% | 98% |
| imit16_fs1_dart_s51 | 0 | 833a022042ef | 100% | 98% |
| imit16_fs1_dart_s51 | 0 | 36680f639c27 | 100% | 98% |
| imit15_dart_s52 | 0 | 833a022042ef | 98% | 100% |
| imit15_dart_s52 | 0 | 36680f639c27 | 98% | 100% |
| imit15_dart_s53 | 0 | 833a022042ef | 100% | 100% |
| imit19_masonmapped_dart_s51 | 0 | 833a022042ef | 100% | 100% |
| imit15_dart_s53 | 0 | 36680f639c27 | 100% | 100% |
| imit19_masonmapped_dart_s51 | 0 | 36680f639c27 | 100% | 100% |
| imit18_power_dart_s51 | 0 | 36680f639c27 | 100% | 100% |
| ppo15_bcreg_s61 | 0 | c66fd89099c7 | 98% | 100% |
| ppo15_bcreg_s62 | 0 | c66fd89099c7 | 100% | 98% |
| ppo15_stoch_s71 | 0 | c66fd89099c7 | 96% | 100% |
| ppo15_anneal_s91 | 0 | c66fd89099c7 | 98% | 100% |
| imit20_fs1_q23_dart_s51 | 0 | c66fd89099c7 | 100% | 100% |
| ppo15_klres_s101 | 0 | c66fd89099c7 | 100% | 100% |
| ppo20_klres_s111 | 0 | c66fd89099c7 | 100% | 100% |
| ppo20_soft_s121 | 0 | c66fd89099c7 | 100% | 100% |
| ppo15_soft_s122 | 0 | c66fd89099c7 | 100% | 98% |

## Noise robustness + track_score (QUICK GATE: 10 deterministic episodes, seeds 4000+, small N so noisy; screened models only)

Gaussian noise of the given sigma is added to EVERY observation and EVERY action (action clipped to [-1,1]). **Noise PASS (QUICK) = contact stays 100% AND mean carry >= 80% of the clean full-N deterministic mean carry at that sigma** (threshold is my choice, not the trainer's; lateral spread is shown but not part of the pass). Provisional: not used for ranking or qualification.
**VOID for the shoulder/wrist parts and any 'Mason-shaped wrist' claim: lead/trail arm bug reported by the Trainer (trail key scores 0.02); `env/residual_golf_env.py` `_load_keyframes` (right_shoulder_pitch/right_wrist columns) and `_track_score` col map {sh:1, yaw:2, wr:3} used that arm mapping. Treat track_score as UNVERIFIED until the Trainer fixes it; only the yaw part is not affected by the arm mix-up.** track_score = trainer definition (`ResidualGolfEnv._track_score`: mean over shoulder-pitch / chest-yaw / wrist-hinge of exp(-MSE(time-normalised swing shape vs unified-refset reference shape)/0.15), 1 = identical shape); **defined only for runs trained with track_set + track_weight>0 (imit* runs); n/a for every other row (undefined, not zero)**. The trainer logs it in `info` but had not reported it per run; here: run's own track config, deterministic, N=10.

| model | kind | clean carry m / lat std | sigma 0.005: contact, carry m (% of clean), lat std | noise pass 0.005 | sigma 0.01: contact, carry m (% of clean), lat std | noise pass 0.01 | track_score (mean / min) |
|---|---|---|---|---|---|---|---|
| ppo_resid_v3_s0 | residual on scripted swing: cap +-[0.4, 0.4, 0.4, 0.25] rad  | 57.1 / 31.46 | 100%, 50.0 (88%), 29.41 | PASS | 100%, 57.6 (101%), 27.39 | PASS | n/a (undefined: no track config) |
| ppo_resid_v3_r2_s0 | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad ( | 86.9 / 8.45 | 100%, 89.3 (103%), 6.13 | PASS | 100%, 91.6 (105%), 10.93 | PASS | n/a (undefined: no track config) |
| ppo_resid_v3_r3_s0 | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad ( | 103.4 / 8.91 | 100%, 104.2 (101%), 7.50 | PASS | 100%, 97.8 (95%), 5.45 | PASS | n/a (undefined: no track config) |
| ppo_resid_v3_ladder_s0 | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad ( | 99.6 / 8.23 | 100%, 95.3 (96%), 5.75 | PASS | 100%, 101.1 (101%), 10.95 | PASS | n/a (undefined: no track config) |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | SCRIPTED (not learned) | 115.7 / 1.70 | 100%, 91.9 (79%), 9.00 | FAIL | 100%, 109.5 (95%), 1.83 | PASS | n/a (undefined: no track config) |
| ppo_resid_v3_left_an1_s0 | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad ( | 111.0 / 6.87 | 100%, 105.4 (95%), 5.86 | PASS | 100%, 107.1 (96%), 6.86 | PASS | n/a (undefined: no track config) |
| ppo_resid_v3_left_an3_s1 | residual on scripted swing: cap +-[0.1, 0.1, 0.1, 0.03] rad  | 108.3 / 6.45 | 100%, 115.6 (107%), 6.57 | PASS | 100%, 100.7 (93%), 5.73 | PASS | n/a (undefined: no track config) |
| ppo_resid_v3_left_an4_s2 | residual on scripted swing: cap +-[0.1, 0.1, 0.1, 0.03] rad  | 97.2 / 6.69 | 100%, 91.6 (94%), 6.05 | PASS | 100%, 100.7 (104%), 7.79 | PASS | n/a (undefined: no track config) |
| best_carry_analytic | residual on scripted swing: cap +-[0.1, 0.1, 0.1, 0.03] rad  | 112.4 / 7.40 | 100%, 111.9 (100%), 8.41 | PASS | 100%, 110.8 (99%), 6.91 | PASS | n/a (undefined: no track config) |
| ppo_resid_v3_left_an6_s4 | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.03] ra | 104.4 / 7.93 | 100%, 89.2 (85%), 6.10 | PASS | 100%, 104.6 (100%), 7.95 | PASS | n/a (undefined: no track config) |
| ppo_resid_v3_left_an9_s7 | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.05] ra | 103.5 / 7.20 | 100%, 107.8 (104%), 9.10 | PASS | 100%, 106.5 (103%), 8.84 | PASS | n/a (undefined: no track config) |
| ppo_resid_v3_left_an10_s8 | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.05] ra | 108.7 / 5.61 | 100%, 96.5 (89%), 6.31 | PASS | 100%, 100.2 (92%), 3.83 | PASS | n/a (undefined: no track config) |
| ppo_v3tiny_s22 | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] r | 105.7 / 4.67 | 100%, 102.5 (97%), 3.96 | PASS | 100%, 115.8 (110%), 6.20 | PASS | n/a (undefined: no track config) |
| ppo_v3tiny_s23 | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] r | 94.3 / 2.84 | 100%, 111.0 (118%), 4.94 | PASS | 100%, 87.6 (93%), 0.14 | PASS | n/a (undefined: no track config) |
| ppo_v3tiny_s21 | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] r | 84.5 / 4.43 | 100%, 117.5 (139%), 2.61 | PASS | 100%, 87.8 (104%), 11.42 | PASS | n/a (undefined: no track config) |
| ppo_v3flt_all_s33 | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] r | 95.0 / 5.13 | 100%, 102.7 (108%), 10.80 | PASS | 100%, 104.4 (110%), 10.44 | PASS | n/a (undefined: no track config) |
| best_learned_yaw_s32 | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad  | 113.9 / 1.59 | 100%, 109.5 (96%), 1.60 | PASS | 100%, 109.6 (96%), 1.59 | PASS | n/a (undefined: no track config) |
| best_learned_yaw_s31 | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad  | 114.3 / 1.61 | 100%, 109.5 (96%), 1.60 | PASS | 100%, 109.6 (96%), 1.59 | PASS | n/a (undefined: no track config) |
| ppo_v4yaw_s43 | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad  | 243.0 / 1.65 | 100%, 212.7 (88%), 1.77 | PASS | 100%, 212.7 (88%), 1.77 | PASS | n/a (undefined: no track config) |
| ppo_v4yaw_s42 | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad  | 243.3 / 1.66 | 100%, 215.1 (88%), 1.80 | PASS | 100%, 215.1 (88%), 1.80 | PASS | n/a (undefined: no track config) |
| best_v4yaw_s41 | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad  | 243.6 / 1.67 | 100%, 213.8 (88%), 1.80 | PASS | 100%, 213.1 (87%), 1.87 | PASS | n/a (undefined: no track config) |
| imit2_w075_s51 | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command | 49.3 / 0.58 | 100%, 87.1 (177%), 12.29 | PASS | 100%, 87.4 (177%), 3.21 | PASS | 0.052 / 0.007 |
| imit2_w075_s52 | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command | 117.8 / 2.96 | 100%, 97.4 (83%), 1.76 | PASS | 100%, 79.3 (67%), 0.03 | FAIL | 0.196 / 0.005 |
| imit2_w075_s53 | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command | 116.9 / 3.57 | 100%, 78.9 (67%), 0.82 | FAIL | 100%, 86.7 (74%), 6.45 | FAIL | 0.058 / 0.013 |
| imit3_w075_s51 | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command | 113.1 / 0.73 | 100%, 90.6 (80%), 0.70 | PASS | 100%, 106.6 (94%), 3.74 | PASS | 0.085 / 0.003 |
| imit3_w075_s52 | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command | 108.4 / 1.10 | 100%, 91.2 (84%), 0.81 | PASS | 100%, 90.1 (83%), 0.03 | PASS | 0.166 / 0.016 |
| imit3_w075_s53 | IMITATION OF THE SCRIPT, 75% script: BLEND: executed command | 112.0 / 2.27 | 100%, 101.9 (91%), 1.33 | PASS | 100%, 72.7 (65%), 2.12 | FAIL | 0.060 / 0.002 |
| imit3_w050_s51 | IMITATION OF THE SCRIPT, 50% script: BLEND: executed command | 119.4 / 2.20 | 100%, 88.9 (74%), 4.43 | FAIL | 100%, 105.4 (88%), 3.43 | PASS | 0.067 / 0.014 |
| best_imit_w050_s52 | IMITATION OF THE SCRIPT, 50% script: BLEND: executed command | 107.7 / 0.23 | 100%, 101.4 (94%), 3.17 | PASS | 100%, 87.3 (81%), 0.38 | PASS | n/a (undefined: no track config) |
| imit3_w025_s51 | IMITATION OF THE SCRIPT, 25% script: BLEND: executed command | 105.1 / 0.11 | 100%, 82.2 (78%), 3.16 | FAIL | 100%, 99.0 (94%), 8.55 | PASS | 0.092 / 0.072 |
| imit3_w025_s52 | IMITATION OF THE SCRIPT, 25% script: BLEND: executed command | 88.9 / 5.31 | 100%, 95.0 (107%), 0.04 | PASS | 100%, 106.8 (120%), 6.01 | PASS | 0.015 / 0.000 |
| imit3_w000_s52 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 105.1 / 5.53 | 100%, 106.1 (101%), 17.04 | PASS | 100%, 84.5 (80%), 1.08 | PASS | 0.023 / 0.000 |
| best_imit_scriptfree_s51_NOTPASS_lat3.56 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 109.4 / 3.97 | 100%, 102.6 (94%), 12.49 | PASS | 100%, 107.2 (98%), 5.24 | PASS | n/a (undefined: no track config) |
| imit4_w000_s52 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 88.4 / 2.68 | 100%, 64.9 (73%), 0.75 | FAIL | 100%, 80.6 (91%), 0.09 | PASS | 0.004 / 0.000 |
| imit4_w000_s51 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 93.5 / 5.43 | 100%, 94.3 (101%), 1.48 | PASS | 100%, 93.0 (99%), 8.06 | PASS | 0.002 / 0.000 |
| imit5_w000_s52 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 103.9 / 4.42 | 100%, 88.2 (85%), 14.42 | PASS | 100%, 120.1 (116%), 12.19 | PASS | 0.048 / 0.001 |
| best_imit_scriptfree_s51_seed4000-8000only | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 93.9 / 4.80 | 100%, 91.2 (97%), 0.05 | PASS | 100%, 113.2 (121%), 3.39 | PASS | n/a (undefined: no track config) |
| ppo_v4power_s61 | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad  | 279.2 / 1.82 | 100%, 255.7 (92%), 1.90 | PASS | 100%, 253.7 (91%), 1.88 | PASS | n/a (undefined: no track config) |
| ppo_v4power_s62 | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad  | 279.7 / 1.86 | 100%, 254.2 (91%), 1.91 | PASS | 100%, 254.2 (91%), 1.91 | PASS | n/a (undefined: no track config) |
| imit7_w000_s51 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 89.2 / 8.02 | 100%, 81.9 (92%), 1.33 | PASS | 100%, 97.5 (109%), 2.85 | PASS | 0.029 / 0.000 |
| ppo_v4power48_s71 | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad  | 311.4 / 2.15 | 100%, 312.3 (100%), 2.04 | PASS | 100%, 312.3 (100%), 2.04 | PASS | n/a (undefined: no track config) |
| imit8_w000_s51 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 96.6 / 0.25 | 100%, 85.8 (89%), 0.05 | PASS | 100%, 80.4 (83%), 0.06 | PASS | 0.010 / 0.000 |
| imit9_w000_s53 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 115.9 / 0.70 | 100%, 82.8 (71%), 0.66 | FAIL | 100%, 73.0 (63%), 0.08 | FAIL | 0.013 / 0.000 |
| imit10_w000_s51_tr | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 101.5 / 0.05 | - | - | - | - | 0.443 / 0.435 |
| best_imit_scriptfree_elbow48_s51 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 120.0 / 0.96 | 100%, 69.1 (58%), 0.05 | FAIL | 90%, 35.6 (30%), 1.44 | FAIL | n/a (undefined: no track config) |
| imit9_w000_s52 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 120.1 / 0.99 | 100%, 74.2 (62%), 0.05 | FAIL | 100%, 85.0 (71%), 0.88 | FAIL | 0.000 / 0.000 |
| imit13_w000_s51 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 110.7 / 1.63 | - | - | - | - | 0.028 / 0.000 |
| imit13_w000_s52 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 113.1 / 1.67 | 100%, 108.0 (96%), 2.00 | PASS | 100%, 98.5 (87%), 2.53 | PASS | 0.031 / 0.000 |
| imit14_w000_s51 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 116.1 / 5.77 | - | - | - | - | 0.468 / 0.042 |
| imit15_dart_s51 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 117.1 / 1.63 | 100%, 100.0 (85%), 2.21 | PASS | 100%, 95.3 (81%), 2.81 | PASS | 0.027 / 0.000 |
| imit16_fs1_dart_s51 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 72.8 / 3.15 | 100%, 74.0 (102%), 3.21 | PASS | 100%, 71.6 (98%), 0.05 | PASS | 0.045 / 0.001 |
| imit15_dart_s52 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 113.6 / 1.69 | - | - | - | - | 0.026 / 0.000 |
| imit15_dart_s53 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 112.9 / 1.27 | 100%, 93.1 (83%), 3.85 | PASS | 100%, 84.8 (75%), 10.54 | FAIL | 0.133 / 0.004 |
| imit19_masonmapped_dart_s51 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 58.3 / 0.14 | 100%, 63.4 (109%), 0.05 | PASS | 100%, 61.8 (106%), 0.06 | PASS | 0.309 / 0.278 |
| imit18_power_dart_s51 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 313.9 / 2.18 | 100%, 288.5 (92%), 1.80 | PASS | 100%, 297.8 (95%), 1.94 | PASS | 0.019 / 0.001 |
| imit18_power_dart_s52 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 313.9 / 2.18 | 100%, 288.4 (92%), 1.80 | PASS | 100%, 297.9 (95%), 2.03 | PASS | 0.002 / 0.001 |
| ppo15_bcreg_s61 | BLEND: executed command = 0% scripted + 100% learned (script | 101.2 / 11.19 | - | - | - | - | 0.216 / 0.177 |
| ppo15_bcreg_s62 | BLEND: executed command = 0% scripted + 100% learned (script | 103.6 / 0.18 | 100%, 102.6 (99%), 2.77 | PASS | 100%, 69.1 (67%), 9.08 | FAIL | 0.236 / 0.003 |
| ppo15_stoch_s71 | BLEND: executed command = 0% scripted + 100% learned (script | 93.7 / 2.95 | - | - | - | - | 0.210 / 0.000 |
| ppo15_anneal_s91 | BLEND: executed command = 0% scripted + 100% learned (script | 106.9 / 9.80 | - | - | - | - | 0.250 / 0.141 |
| imit20_fs1_q23_dart_s51 | SCRIPT-FREE IMITATION of the scripted v3 swing: BLEND: execu | 139.6 / 2.29 | 100%, 138.6 (99%), 0.14 | PASS | 100%, 139.7 (100%), 0.29 | PASS | 0.033 / 0.001 |
| ppo15_klres_s101 | BLEND: executed command = 0% scripted + 100% learned (script | 112.9 / 1.27 | 100%, 93.1 (83%), 3.85 | PASS | 100%, 84.8 (75%), 10.54 | FAIL | 0.133 / 0.004 |
| ppo20_klres_s111 | BLEND: executed command = 0% scripted + 100% learned (script | 139.6 / 2.29 | 100%, 138.6 (99%), 0.14 | PASS | 100%, 139.7 (100%), 0.29 | PASS | 0.033 / 0.001 |
| ppo20_soft_s121 | BLEND: executed command = 0% scripted + 100% learned (script | 139.8 / 1.95 | 100%, 138.5 (99%), 0.14 | PASS | 100%, 139.9 (100%), 0.28 | PASS | 0.061 / 0.001 |
| ppo15_soft_s122 | BLEND: executed command = 0% scripted + 100% learned (script | 112.9 / 1.27 | 100%, 93.1 (83%), 3.85 | PASS | 100%, 84.8 (75%), 10.54 | FAIL | 0.133 / 0.004 |

## HYPOTHETICAL TIER (force_scale > 1): 3-seed headline gate, kept separate from learned vs scripted

**DISTANCES INFLATED for power-tier rows** (env impact_model gain 1.28 gives smash ~1.55-1.60 > the ~1.48 legal limit; see results/ball_flight_audit.md); do not quote them as real-world distance. **force_scale 2 (hypothetical-strength actuators)**: boosted actuator force caps; not human- or robot-attainable. Source: `results/gate_<name>_seed<seed>.json` (eval_gate, headline tier: det AND stoch contact>=99%, lateral std<=2.73 m, launch 5-20 deg, carry>=min_carry, landed>=90%). 'Effectively scripted' = policy det carry within 1% and lateral std within 15% (or 0.3 m) of the zero-residual script in the same file on every seed; such rows are NOT learned drives. A model counts as passing only if ALL of seeds 4000/8000/9000 pass.

| model | label | force_scale | flight_steps | residual cap (res_scale) | seed | episodes | det carry m / yd | det lat std m | stoch lat std m | landed (det) | launch deg | club mph | script lat std m | noise quick (carry m, % of clean; sigma 0.005 / 0.01) | headline |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| imit15_dart_s52 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 4000 | 100 | 111.8 / 122 | 1.46 | 1.69 | 99% | 12.3 | 119.9 | 0.01 | not measured | PASS (min_carry 11.98) |
| imit15_dart_s52 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 5000 | 100 | 115.2 / 126 | 4.37 | 4.75 | 100% | 12.3 | 120.4 | 0.02 | not measured | FAIL (min_carry 11.98) |
| imit15_dart_s52 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 8000 | 100 | 112.6 / 123 | 0.54 | 0.77 | 100% | 12.4 | 120.4 | 0.01 | not measured | PASS (min_carry 11.98) |
| imit15_dart_s52 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 9000 | 100 | 110.0 / 120 | 2.14 | 1.07 | 100% | 11.7 | 120.4 | 0.01 | not measured | PASS (min_carry 11.98) |
| imit15_dart_s53 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 4000 | 100 | 112.2 / 123 | 1.45 | 1.26 | 99% | 12.3 | 119.9 | 0.01 | 93 (83%) / 85 (75%) FAIL | PASS (min_carry 11.98) |
| imit15_dart_s53 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 8000 | 100 | 112.9 / 123 | 0.54 | 1.08 | 100% | 12.4 | 120.4 | 0.01 | 93 (83%) / 85 (75%) FAIL | PASS (min_carry 11.98) |
| imit15_dart_s53 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 9000 | 100 | 110.5 / 121 | 2.10 | 1.38 | 100% | 12.3 | 120.4 | 0.01 | 93 (83%) / 85 (75%) FAIL | PASS (min_carry 11.98) |
| imit18_power_dart_s51 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | 900 | [0.01, 0.01, 0.01, 0.01] | 4000 | 100 | 309.9 / 339 | 2.34 | 2.34 | 100% | 12.6 | 132.4 | 0.10 | 288 (92%) / 298 (95%) PASS | PASS (min_carry 11.98) |
| imit18_power_dart_s51 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | 900 | [0.01, 0.01, 0.01, 0.01] | 8000 | 100 | 307.3 / 336 | 2.36 | 2.35 | 100% | 12.6 | 132.4 | 0.13 | 288 (92%) / 298 (95%) PASS | PASS (min_carry 11.98) |
| imit18_power_dart_s51 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | 900 | [0.01, 0.01, 0.01, 0.01] | 9000 | 100 | 306.2 / 335 | 2.53 | 2.53 | 100% | 12.6 | 132.4 | 0.11 | 288 (92%) / 298 (95%) PASS | PASS (min_carry 11.98) |
| imit18_power_dart_s52 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | 900 | [0.01, 0.01, 0.01, 0.01] | 4000 | 100 | 310.0 / 339 | 2.34 | 2.34 | 100% | 12.6 | 132.4 | 0.10 | 288 (92%) / 298 (95%) PASS | PASS (min_carry 11.98) |
| imit18_power_dart_s52 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | 900 | [0.01, 0.01, 0.01, 0.01] | 8000 | 100 | 307.8 / 337 | 2.36 | 2.36 | 100% | 12.6 | 132.4 | 0.13 | 288 (92%) / 298 (95%) PASS | PASS (min_carry 11.98) |
| imit18_power_dart_s52 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | 900 | [0.01, 0.01, 0.01, 0.01] | 9000 | 100 | 306.2 / 335 | 2.53 | 2.52 | 100% | 12.6 | 132.4 | 0.11 | 288 (92%) / 298 (95%) PASS | PASS (min_carry 11.98) |
| imit19_masonmapped_dart_s51 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 4000 | 100 | 58.4 / 64 | 0.11 | 0.21 | 100% | 13.9 | 87.6 | 0.01 | 63 (109%) / 62 (106%) PASS | PASS (min_carry 11.98) |
| imit19_masonmapped_dart_s51 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 8000 | 100 | 58.2 / 64 | 0.04 | 0.04 | 100% | 14.0 | 87.6 | 0.01 | 63 (109%) / 62 (106%) PASS | PASS (min_carry 11.98) |
| imit19_masonmapped_dart_s51 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 9000 | 100 | 58.4 / 64 | 0.11 | 0.26 | 100% | 13.9 | 87.6 | 0.02 | 63 (109%) / 62 (106%) PASS | PASS (min_carry 11.98) |
| imit5_w000_s51 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 8000 | 100 | 96.6 / 106 | 2.42 | 1.51 | 94% | 9.4 | 122.0 | 0.01 | 91 (97%) / 113 (121%) PASS | PASS (min_carry 11.98) |
| imit5_w000_s51 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 9000 | 100 | 60.5 / 66 | 0.08 | 0.21 | 75% | 4.6 | 119.8 | 0.01 | 91 (97%) / 113 (121%) PASS | FAIL (min_carry 11.98) |
| imit7_w000_s51 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 8000 | 100 | 104.0 / 114 | 7.10 | 4.43 | 92% | 9.8 | 120.9 | 0.01 | 82 (92%) / 97 (109%) PASS | FAIL (min_carry 30.0) |
| imit7_w000_s51 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 9000 | 100 | 89.4 / 98 | 1.50 | 2.78 | 82% | 9.8 | 120.1 | 0.01 | 82 (92%) / 97 (109%) PASS | FAIL (min_carry 30.0) |
| imit8_w000_s51 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 8000 | 100 | 107.6 / 118 | 0.03 | 0.03 | 100% | 13.2 | 120.9 | 0.01 | 86 (89%) / 80 (83%) PASS | PASS (min_carry 30.0) |
| imit9_w000_s51 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 4000 | 100 | 119.3 / 130 | 1.17 | 1.30 | 100% | 12.9 | 120.4 | 0.01 | 69 (58%) / 36 (30%) FAIL | PASS (min_carry 30.0) |
| imit9_w000_s51 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 8000 | 100 | 120.7 / 132 | 1.39 | 1.15 | 100% | 13.0 | 120.5 | 0.01 | 69 (58%) / 36 (30%) FAIL | PASS (min_carry 30.0) |
| imit9_w000_s51 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 9000 | 100 | 118.2 / 129 | 1.27 | 1.57 | 100% | 12.9 | 120.5 | 0.01 | 69 (58%) / 36 (30%) FAIL | PASS (min_carry 30.0) |
| imit9_w000_s52 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 4000 | 100 | 118.1 / 129 | 0.85 | 1.40 | 100% | 12.9 | 120.4 | 0.01 | 74 (62%) / 85 (71%) FAIL | PASS (min_carry 30.0) |
| imit9_w000_s52 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 8000 | 100 | 122.1 / 133 | 1.42 | 1.43 | 100% | 13.0 | 120.4 | 0.01 | 74 (62%) / 85 (71%) FAIL | PASS (min_carry 30.0) |
| imit9_w000_s52 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 9000 | 100 | 119.0 / 130 | 1.54 | 1.55 | 100% | 12.9 | 120.4 | 0.01 | 74 (62%) / 85 (71%) FAIL | PASS (min_carry 30.0) |
| imit9_w000_s53 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 4000 | 100 | 116.9 / 128 | 1.11 | 0.82 | 100% | 12.9 | 120.5 | 0.01 | 83 (71%) / 73 (63%) FAIL | PASS (min_carry 30.0) |
| imit9_w000_s53 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 8000 | 100 | 116.6 / 128 | 1.32 | 1.26 | 100% | 13.0 | 120.5 | 0.01 | 83 (71%) / 73 (63%) FAIL | PASS (min_carry 30.0) |
| imit9_w000_s53 | SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators) | 2 | None | [0.01, 0.01, 0.01, 0.01] | 9000 | 100 | 114.6 / 125 | 1.15 | 0.79 | 100% | 12.9 | 120.5 | 0.01 | 83 (71%) / 73 (63%) FAIL | PASS (min_carry 30.0) |
| ppo15_anneal_s91 | POLICY DIFFERS FROM SCRIPT (hypothetical actuators; learned fraction: see leaderboard row) | 2 | None | None | 4000 | 100 | 110.5 / 121 | 9.50 | 8.22 | 98% | 11.5 | 121.2 | 0.01 | not measured | FAIL (min_carry 11.98) |
| ppo15_anneal_s91 | POLICY DIFFERS FROM SCRIPT (hypothetical actuators; learned fraction: see leaderboard row) | 2 | None | None | 8000 | 100 | 116.7 / 128 | 6.93 | 6.34 | 96% | 11.9 | 122.1 | 0.01 | not measured | FAIL (min_carry 11.98) |
| ppo15_anneal_s91 | POLICY DIFFERS FROM SCRIPT (hypothetical actuators; learned fraction: see leaderboard row) | 2 | None | None | 9000 | 100 | 82.7 / 90 | 13.03 | 7.39 | 85% | 8.3 | 122.1 | 0.01 | not measured | FAIL (min_carry 11.98) |
| ppo15_bcreg_s61 | POLICY DIFFERS FROM SCRIPT (hypothetical actuators; learned fraction: see leaderboard row) | 2 | None | None | 4000 | 100 | 104.0 / 114 | 10.42 | 6.49 | 97% | 11.3 | 118.7 | 0.01 | not measured | FAIL (min_carry 11.98) |
| ppo15_bcreg_s61 | POLICY DIFFERS FROM SCRIPT (hypothetical actuators; learned fraction: see leaderboard row) | 2 | None | None | 8000 | 100 | 107.6 / 118 | 8.33 | 6.29 | 99% | 11.4 | 119.0 | 0.01 | not measured | FAIL (min_carry 11.98) |
| ppo15_bcreg_s61 | POLICY DIFFERS FROM SCRIPT (hypothetical actuators; learned fraction: see leaderboard row) | 2 | None | None | 9000 | 100 | 111.4 / 122 | 9.87 | 6.36 | 97% | 11.8 | 119.0 | 0.01 | not measured | FAIL (min_carry 11.98) |
| ppo15_bcreg_s62 | POLICY DIFFERS FROM SCRIPT (hypothetical actuators; learned fraction: see leaderboard row) | 2 | None | None | 4000 | 100 | 105.0 / 115 | 0.49 | 6.07 | 99% | 12.0 | 118.1 | 0.01 | 103 (99%) / 69 (67%) FAIL | FAIL (min_carry 11.98) |
| ppo15_bcreg_s62 | POLICY DIFFERS FROM SCRIPT (hypothetical actuators; learned fraction: see leaderboard row) | 2 | None | None | 8000 | 100 | 106.5 / 117 | 0.15 | 3.02 | 100% | 12.2 | 118.4 | 0.01 | 103 (99%) / 69 (67%) FAIL | FAIL (min_carry 11.98) |
| ppo15_bcreg_s62 | POLICY DIFFERS FROM SCRIPT (hypothetical actuators; learned fraction: see leaderboard row) | 2 | None | None | 9000 | 100 | 103.9 / 114 | 0.10 | 7.53 | 100% | 12.2 | 118.4 | 0.01 | 103 (99%) / 69 (67%) FAIL | FAIL (min_carry 11.98) |
| ppo15_stoch_s71 | POLICY DIFFERS FROM SCRIPT (hypothetical actuators; learned fraction: see leaderboard row) | 2 | None | None | 4000 | 100 | 92.9 / 102 | 0.03 | 4.90 | 97% | 11.3 | 114.8 | 0.01 | not measured | FAIL (min_carry 11.98) |
| ppo15_stoch_s71 | POLICY DIFFERS FROM SCRIPT (hypothetical actuators; learned fraction: see leaderboard row) | 2 | None | None | 8000 | 100 | 95.5 / 104 | 0.03 | 5.50 | 100% | 11.7 | 115.9 | 0.01 | not measured | FAIL (min_carry 11.98) |
| ppo15_stoch_s71 | POLICY DIFFERS FROM SCRIPT (hypothetical actuators; learned fraction: see leaderboard row) | 2 | None | None | 9000 | 100 | 94.7 / 104 | 0.03 | 4.40 | 99% | 11.3 | 115.9 | 0.01 | not measured | FAIL (min_carry 11.98) |
| ppo_v4power48_s71 | EFFECTIVELY SCRIPTED (force_scale 2, hypothetical-strength actuators) | 2 | 900 | [0.0, 0.0, 0.0, 0.05] | 4000 | 100 | 308.4 / 337 | 2.32 | 2.33 | 100% | 12.6 | 132.4 | 2.32 | 312 (100%) / 312 (100%) PASS | PASS (min_carry 30.0) |
| ppo_v4power48_s71 | EFFECTIVELY SCRIPTED (force_scale 2, hypothetical-strength actuators) | 2 | 900 | [0.0, 0.0, 0.0, 0.05] | 8000 | 100 | 307.2 / 336 | 2.36 | 2.39 | 100% | 12.6 | 132.4 | 2.36 | 312 (100%) / 312 (100%) PASS | PASS (min_carry 30.0) |
| ppo_v4power48_s71 | EFFECTIVELY SCRIPTED (force_scale 2, hypothetical-strength actuators) | 2 | 900 | [0.0, 0.0, 0.0, 0.05] | 9000 | 100 | 305.3 / 334 | 2.51 | 2.55 | 100% | 12.6 | 132.4 | 2.51 | 312 (100%) / 312 (100%) PASS | PASS (min_carry 30.0) |
| ppo_v4power_s61 | EFFECTIVELY SCRIPTED (force_scale 2, hypothetical-strength actuators) | 2 | 900 | [0.0, 0.0, 0.0, 0.05] | 4000 | 100 | 277.9 / 304 | 2.38 | 2.48 | 100% | 11.6 | 132.3 | 2.29 | 256 (92%) / 254 (91%) PASS | PASS (min_carry 11.98) |
| ppo_v4power_s61 | EFFECTIVELY SCRIPTED (force_scale 2, hypothetical-strength actuators) | 2 | 900 | [0.0, 0.0, 0.0, 0.05] | 8000 | 100 | 283.4 / 310 | 2.53 | 2.66 | 100% | 12.3 | 132.3 | 2.51 | 256 (92%) / 254 (91%) PASS | PASS (min_carry 11.98) |
| ppo_v4power_s61 | EFFECTIVELY SCRIPTED (force_scale 2, hypothetical-strength actuators) | 2 | 900 | [0.0, 0.0, 0.0, 0.05] | 9000 | 100 | 278.7 / 305 | 17.13 | 17.44 | 99% | 11.5 | 132.3 | 17.58 | 256 (92%) / 254 (91%) PASS | FAIL (min_carry 11.98) |
| ppo_v4power_s62 | EFFECTIVELY SCRIPTED (force_scale 2, hypothetical-strength actuators) | 2 | 900 | [0.0, 0.0, 0.0, 0.05] | 4000 | 100 | 278.0 / 304 | 2.28 | 2.47 | 100% | 11.6 | 132.3 | 2.29 | 254 (91%) / 254 (91%) PASS | PASS (min_carry 11.98) |
| ppo_v4power_s62 | EFFECTIVELY SCRIPTED (force_scale 2, hypothetical-strength actuators) | 2 | 900 | [0.0, 0.0, 0.0, 0.05] | 8000 | 100 | 283.2 / 310 | 2.51 | 2.46 | 100% | 12.3 | 132.3 | 2.51 | 254 (91%) / 254 (91%) PASS | PASS (min_carry 11.98) |
| ppo_v4power_s62 | EFFECTIVELY SCRIPTED (force_scale 2, hypothetical-strength actuators) | 2 | 900 | [0.0, 0.0, 0.0, 0.05] | 9000 | 100 | 278.1 / 304 | 17.59 | 16.87 | 99% | 11.5 | 132.3 | 17.58 | 254 (91%) / 254 (91%) PASS | FAIL (min_carry 11.98) |

### imit18 power tier (hypothetical, no spin model): HEADLINE gain-1.20 re-gates vs the inflated gain-1.28 default

Trainer gates (100 eps x seeds 4000/8000/9000), env `impact_gain` overridden. **Use the gain 1.20 rows as the headline power tier**; gain 1.28 (313.8 m class, smash ~1.6) is INFLATED. Smash = mean ball mph / mean impact club mph; flags use the launch_report thresholds (fail >1.50, warn >1.49 or <1.30; derived, not published). A flagged row is not eligible as a showcase/top row. Gain 1.0 exactly was not gated. Rows marked `held` have no backing file in the repo (Trainer-reported, file held on the box).

| model | gain | loft deg | seed | club mph | ball mph | smash | smash flag | launch deg | det carry m / yd | det lat std m | stoch lat std m | landed | headline | backing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| imit18_power_dart_s51 | 1.28 | -31 | 4000 | 132.4 | 209 | 1.577 | FAIL smash>1.50 | 12.6 | 309.9 / 339 | 2.34 | 2.34 | 100% | PASS | held locally (not in repo) `imit_private/gate_imit18_power_dart_s51.json` |
| imit18_power_dart_s51 | 1.28 | -31 | 8000 | 132.4 | 206 | 1.559 | FAIL smash>1.50 | 12.6 | 307.3 / 336 | 2.36 | 2.35 | 100% | PASS | held locally (not in repo) `imit_private/gate_imit18_power_dart_s51_seed8000.json` |
| imit18_power_dart_s51 | 1.28 | -31 | 9000 | 132.4 | 206 | 1.552 | FAIL smash>1.50 | 12.6 | 306.2 / 335 | 2.53 | 2.53 | 100% | PASS | held locally (not in repo) `imit_private/gate_imit18_power_dart_s51_seed9000.json` |
| imit18_power_dart_s51 | 1.2 | -31 | 4000 | 132.4 | 196 | 1.479 | ok | 12.6 | 295.3 / 323 | 2.17 | 2.16 | 100% | PASS | held locally (not in repo) `gain120/gate_imit18_power_dart_s51.json` |
| imit18_power_dart_s51 | 1.2 | -31 | 8000 | 132.4 | 194 | 1.462 | ok | 12.6 | 292.4 / 320 | 2.17 | 2.17 | 100% | PASS | held locally (not in repo) `gain120/gate_imit18_power_dart_s51_seed8000.json` |
| imit18_power_dart_s51 | 1.2 | -31 | 9000 | 132.4 | 193 | 1.456 | ok | 12.6 | 291.3 / 319 | 2.33 | 2.33 | 100% | PASS | held locally (not in repo) `gain120/gate_imit18_power_dart_s51_seed9000.json` |
| imit18_power_dart_s51 | 1.2 | -29 | 4000 | 132.4 | 197 | 1.492 | WARN smash>1.49 | 11.2 | 294.9 / 323 | 2.10 | 2.10 | 100% | PASS | held locally (not in repo) `power_gain120_loft29/gate_imit18_power_dart_s51.json` |
| imit18_power_dart_s51 | 1.2 | -29 | 8000 | 132.4 | 195 | 1.475 | ok | 11.2 | 291.6 / 319 | 2.10 | 2.12 | 100% | PASS | held locally (not in repo) `power_gain120_loft29/gate_imit18_power_dart_s51_seed8000.json` |
| imit18_power_dart_s51 | 1.2 | -29 | 9000 | 132.4 | 194 | 1.469 | ok | 11.2 | 290.4 / 318 | 2.26 | 2.26 | 100% | PASS | held locally (not in repo) `power_gain120_loft29/gate_imit18_power_dart_s51_seed9000.json` |
| imit18_power_dart_s51 | 1.2 | -28 | 4000 | 132.4 | 198 | 1.496 | WARN smash>1.49 | 10.4 | 292.3 / 320 | 2.02 | 2.03 | 100% | PASS | held locally (not in repo) `power_gain120_loft28/gate_imit18_power_dart_s51.json` |
| imit18_power_dart_s51 | 1.2 | -28 | 8000 | 132.4 | 196 | 1.479 | ok | 10.5 | 288.9 / 316 | 2.02 | 2.00 | 100% | PASS | held locally (not in repo) `power_gain120_loft28/gate_imit18_power_dart_s51_seed8000.json` |
| imit18_power_dart_s51 | 1.2 | -28 | 9000 | 132.4 | 195 | 1.473 | ok | 10.5 | 287.5 / 314 | 2.17 | 2.18 | 100% | PASS | held locally (not in repo) `power_gain120_loft28/gate_imit18_power_dart_s51_seed9000.json` |
| imit18_power_dart_s51 | 1.2 | -27 | 4000 | 132.4 | 198 | 1.498 | WARN smash>1.49 | 9.7 | 288.0 / 315 | 1.94 | 1.92 | 100% | PASS | held locally (not in repo) `power_gain120_loft27/gate_imit18_power_dart_s51.json` |
| imit18_power_dart_s51 | 1.2 | -27 | 8000 | 132.4 | 196 | 1.482 | ok | 9.7 | 284.3 / 311 | 1.93 | 1.91 | 100% | PASS | held locally (not in repo) `power_gain120_loft27/gate_imit18_power_dart_s51_seed8000.json` |
| imit18_power_dart_s51 | 1.2 | -27 | 9000 | 132.4 | 195 | 1.475 | ok | 9.7 | 282.1 / 308 | 2.02 | 2.05 | 100% | PASS | held locally (not in repo) `power_gain120_loft27/gate_imit18_power_dart_s51_seed9000.json` |
| imit18_power_dart_s51 | 1.2 | -25 | 4000 | 132.4 | 198 | 1.499 | WARN smash>1.49 | 8.3 | 270.1 / 295 | 1.60 | 1.54 | 100% | PASS | held locally (not in repo) `power_gain120_loft25/gate_imit18_power_dart_s51.json` |
| imit18_power_dart_s51 | 1.2 | -25 | 8000 | 132.4 | 196 | 1.482 | ok | 8.3 | 265.3 / 290 | 1.56 | 1.52 | 100% | PASS | held locally (not in repo) `power_gain120_loft25/gate_imit18_power_dart_s51_seed8000.json` |
| imit18_power_dart_s51 | 1.2 | -25 | 9000 | 132.4 | 195 | 1.473 | ok | 8.3 | 263.0 / 288 | 1.63 | 1.65 | 100% | PASS | held locally (not in repo) `power_gain120_loft25/gate_imit18_power_dart_s51_seed9000.json` |
| imit18_power_dart_s51 | 1.02 | -31 | 4000 | 132.4 | 167 | 1.258 | WARN smash<1.30 | 12.6 | 252.1 / 276 | 1.68 | 1.68 | 100% | PASS | held locally (not in repo) `gain102/gate_imit18_power_dart_s51.json` |
| imit18_power_dart_s51 | 1.02 | -31 | 8000 | 132.4 | 165 | 1.244 | WARN smash<1.30 | 12.6 | 248.1 / 271 | 1.63 | 1.66 | 100% | PASS | held locally (not in repo) `gain102/gate_imit18_power_dart_s51_seed8000.json` |
| imit18_power_dart_s51 | 1.02 | -31 | 9000 | 132.4 | 164 | 1.238 | WARN smash<1.30 | 12.6 | 247.4 / 271 | 1.79 | 1.78 | 100% | PASS | held locally (not in repo) `gain102/gate_imit18_power_dart_s51_seed9000.json` |
| imit18_power_dart_s52 | 1.28 | -31 | 4000 | 132.4 | 209 | 1.577 | FAIL smash>1.50 | 12.6 | 310.0 / 339 | 2.34 | 2.34 | 100% | PASS | held locally (not in repo) `imit_private/gate_imit18_power_dart_s52.json` |
| imit18_power_dart_s52 | 1.28 | -31 | 8000 | 132.4 | 207 | 1.563 | FAIL smash>1.50 | 12.6 | 307.8 / 337 | 2.36 | 2.36 | 100% | PASS | held locally (not in repo) `imit_private/gate_imit18_power_dart_s52_seed8000.json` |
| imit18_power_dart_s52 | 1.28 | -31 | 9000 | 132.4 | 205 | 1.552 | FAIL smash>1.50 | 12.6 | 306.2 / 335 | 2.53 | 2.52 | 100% | PASS | held locally (not in repo) `imit_private/gate_imit18_power_dart_s52_seed9000.json` |
| imit18_power_dart_s52 | 1.2 | -31 | 4000 | 132.4 | 196 | 1.479 | ok | 12.6 | 295.5 / 323 | 2.17 | 2.17 | 100% | PASS | held locally (not in repo) `gain120/gate_imit18_power_dart_s52.json` |
| imit18_power_dart_s52 | 1.2 | -31 | 8000 | 132.4 | 194 | 1.466 | ok | 12.6 | 293.0 / 320 | 2.17 | 2.18 | 100% | PASS | held locally (not in repo) `gain120/gate_imit18_power_dart_s52_seed8000.json` |
| imit18_power_dart_s52 | 1.2 | -31 | 9000 | 132.4 | 193 | 1.456 | ok | 12.6 | 291.2 / 319 | 2.33 | 2.33 | 100% | PASS | held locally (not in repo) `gain120/gate_imit18_power_dart_s52_seed9000.json` |

### STOCK motors (force_scale 1): 3-seed headline gates, Stage 25/26 (Trainer)

Gate = eval_gate headline protocol (100 eps x seeds 4000/8000/9000). Smash = mean ball mph / mean impact club mph: ~1.0 means the ball leaves barely faster than the club (not a real-contact smash; flagged WARN <1.30 by the smash gate), so these carries are far SHORT of real driver distance. Rows marked held have no backing file in the repo.

| model | seed | loft | club mph | ball mph | smash | smash flag | launch deg | det carry m / yd | det lat std m | stoch lat std m | headline | backing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| stock scripted q_back 2.3 dz 0.016 (SCRIPTED, not learned) | 4000 | -41 | 100.7 | 101 | 1.005 | WARN smash<1.30 | 17.6 | 140.1 / 153 | 1.59 | 1.59 | PASS | held locally (not in repo) `imit_private/gate_stock_fs1_q23_dz016_scripted.json` |
| stock scripted q_back 2.3 dz 0.016 (SCRIPTED, not learned) | 8000 | -41 | 100.6 | 101 | 1.004 | WARN smash<1.30 | 17.6 | 139.7 / 153 | 0.83 | 0.83 | PASS | held locally (not in repo) `imit_private/gate_stock_fs1_q23_dz016_scripted_seed8000.json` |
| stock scripted q_back 2.3 dz 0.016 (SCRIPTED, not learned) | 9000 | -41 | 100.7 | 101 | 1.006 | WARN smash<1.30 | 17.5 | 140.0 / 153 | 0.48 | 0.48 | PASS | held locally (not in repo) `imit_private/gate_stock_fs1_q23_dz016_scripted_seed9000.json` |
| imit16_fs1_dart_s51 (script-distilled) | 4000 | -31 | 98.1 | 98 | 0.997 | WARN smash<1.30 | 12.2 | 74.2 / 81 | 1.23 | 0.15 | PASS | in repo `results/gate_imit16_fs1_dart_s51_seed4000.json` |
| imit16_fs1_dart_s51 (script-distilled) | 8000 | -31 | 98.4 | 99 | 1.003 | WARN smash<1.30 | 13.0 | 73.7 / 81 | 0.21 | 0.35 | PASS | in repo `results/gate_imit16_fs1_dart_s51_seed8000.json` |
| imit16_fs1_dart_s51 (script-distilled) | 9000 | -31 | 98.4 | 99 | 1.004 | WARN smash<1.30 | 12.9 | 74.8 / 82 | 0.18 | 0.19 | PASS | in repo `results/gate_imit16_fs1_dart_s51_seed9000.json` |
| imit20_fs1_q23_dart_s51 (script-distilled) | 4000 | -41 | 100.7 | 101 | 1.006 | WARN smash<1.30 | 17.5 | 140.1 / 153 | 2.01 | 1.75 | PASS | held locally (not in repo) `imit_private/gate_imit20_fs1_q23_dart_s51.json` |
| imit20_fs1_q23_dart_s51 (script-distilled) | 8000 | -41 | 100.6 | 101 | 1.004 | WARN smash<1.30 | 17.6 | 139.8 / 153 | 1.01 | 1.34 | PASS | held locally (not in repo) `imit_private/gate_imit20_fs1_q23_dart_s51_seed8000.json` |
| imit20_fs1_q23_dart_s51 (script-distilled) | 9000 | -41 | 100.7 | 101 | 1.007 | WARN smash<1.30 | 17.5 | 140.4 / 154 | 0.54 | 1.21 | PASS | held locally (not in repo) `imit_private/gate_imit20_fs1_q23_dart_s51_seed9000.json` |

**imit15_dart_s52 note:** the lateral std 4.37 m (with a ~190 m outlier) comes from a seed-5000 TRAIN-env run (`results/imit_private/gate_imit15_dart_s52_seed5000.json`, headline FAIL). Seed 5000 is NOT a gate seed; it is not a gate result. The authoritative 3-seed gates (4000/8000/9000) pass with lateral std 1.46/0.54/2.14 m (Trainer files) and 1.5/0.91/2.11 m (repo `results/gate_imit15_dart_s52_seed*.json`). Both sets are listed; the 3-seed gates decide.

3/3-seed pass: imit15_dart_s52: YES, imit15_dart_s53: YES, imit18_power_dart_s51: YES, imit18_power_dart_s52: YES, imit19_masonmapped_dart_s51: YES, imit5_w000_s51: NO, imit7_w000_s51: NO, imit8_w000_s51: NO, imit9_w000_s51: YES, imit9_w000_s52: YES, imit9_w000_s53: YES, ppo15_anneal_s91: NO, ppo15_bcreg_s61: NO, ppo15_bcreg_s62: NO, ppo15_stoch_s71: NO, ppo_v4power48_s71: YES, ppo_v4power_s61: NO, ppo_v4power_s62: NO

