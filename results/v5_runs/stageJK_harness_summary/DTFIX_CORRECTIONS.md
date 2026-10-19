# dt correction for the Evaluator's Stage K7-K12 harness timings (2026-10-19)

**Correction:** every Evaluator kinematic-sequence timing reported for Stage J/K before this date (the K7-K12 rows on branch `evaluator-k7-k12-summary`, the README_arm_dist tables, and the overnight relays) is **inflated by 1.25x**. JEnv/V5GolfEnv log segment speeds every 2 physics substeps of 2 ms (= 4 ms), but the harness read them as 5 ms samples. For example, "pelvis 145 ms before club" was really 116 ms. Shot numbers (club mph, carry, total/carry, spin) are unaffected.

The fix (local commit `bbb9a7e` on scott-e; not part of this branch) makes the harness use each episode's measured sample spacing from the logged sim time. The 20 ms tie tolerance and all thresholds are unchanged. The JSONs here are the re-scored rows: gate off, golfphys, arm_dist 0.6, club 1.15, 24 deterministic episodes. They contain summary data only; per-episode rows are kept local.

Labels: reference-guided residual policies with tracking assistance (not from scratch), stock G1 torque, strike gate off, single training seed, model-only physics. **No row passes every check.**

| row | old p/w/f verdict | new p/w/f verdict | pelvis ms old->new | thorax/arm ms new | order old->new | mph/carry/t-c unchanged | new fails | new warns |
| K10_s11_200000 | 10/5/0 WARN | 10/5/0 WARN | 145.0 (warn) -> 116.0 (warn) | 24.0/-12.0 | warn -> warn | yes | - | kinematic_sequence_order,kinematic_sequence_timing_ms_before_club_peak,peak_speed_thorax_deg_s,spin_rpm,total_over_carry |
| K10b_s13_400000 | 12/2/1 FAIL | 12/2/1 FAIL | 150.0 (warn) -> 120.0 (warn) | 32.0/-4.0 | warn -> warn | yes | spin_rpm | kinematic_sequence_order,kinematic_sequence_timing_ms_before_club_peak |
| K11_s16_500000 | 13/1/1 FAIL | 14/0/1 FAIL | 150.0 (warn) -> 120.0 (pass) | 40.0/76.0 | fail -> fail | yes | kinematic_sequence_order | - |
| K12_s17_200000 | 10/5/0 WARN | 10/5/0 WARN | 155.0 (warn) -> 124.0 (warn) | 40.0/-4.0 | warn -> warn | yes | - | kinematic_sequence_order,kinematic_sequence_timing_ms_before_club_peak,grf_lead_vertical_bw,spin_rpm,total_over_carry |
| K12_s17_300000 | 11/4/0 WARN | 11/4/0 WARN | 160.0 (warn) -> 128.0 (warn) | 40.0/0.0 | warn -> warn | yes | - | kinematic_sequence_order,kinematic_sequence_timing_ms_before_club_peak,spin_rpm,total_over_carry |
| K12_s17_400000 | 12/3/0 WARN | 12/3/0 WARN | 155.0 (warn) -> 124.0 (warn) | 40.0/0.0 | warn -> warn | yes | - | kinematic_sequence_order,kinematic_sequence_timing_ms_before_club_peak,total_over_carry |
| K12_s18_100000 | 12/3/0 WARN | 12/3/0 WARN | 160.0 (warn) -> 128.0 (warn) | 40.0/0.0 | warn -> warn | yes | - | kinematic_sequence_order,kinematic_sequence_timing_ms_before_club_peak,spin_rpm |
| K12_s18_400000 | 12/3/0 WARN | 12/3/0 WARN | 145.0 (warn) -> 116.0 (warn) | 40.0/-4.0 | warn -> warn | yes | - | kinematic_sequence_order,kinematic_sequence_timing_ms_before_club_peak,total_over_carry |
| K7_s6_400000 | 11/4/0 WARN | 11/4/0 WARN | 180.0 (warn) -> 144.0 (warn) | 40.0/16.0 | pass -> pass | yes | - | kinematic_sequence_timing_ms_before_club_peak,smash,spin_rpm,total_over_carry |
| K7_s6_800000 | 12/3/0 WARN | 12/3/0 WARN | 180.0 (warn) -> 144.0 (warn) | 36.0/12.0 | pass -> pass | yes | - | kinematic_sequence_timing_ms_before_club_peak,spin_rpm,total_over_carry |
| K8_s8_300000 | 10/5/0 WARN | 10/5/0 WARN | 170.0 (warn) -> 136.0 (warn) | 32.0/0.0 | warn -> warn | yes | - | kinematic_sequence_order,kinematic_sequence_timing_ms_before_club_peak,spin_rpm,launch_deg,total_over_carry |
| K8_s8_400000 | 12/3/0 WARN | 12/3/0 WARN | 165.0 (warn) -> 132.0 (warn) | 32.0/0.0 | warn -> warn | yes | - | kinematic_sequence_order,kinematic_sequence_timing_ms_before_club_peak,spin_rpm |
| K8_s8_600000 | 11/4/0 WARN | 11/4/0 WARN | 180.0 (warn) -> 144.0 (warn) | 32.0/0.0 | warn -> warn | yes | - | kinematic_sequence_order,kinematic_sequence_timing_ms_before_club_peak,spin_rpm,total_over_carry |
| K8_s8_700000 | 11/4/0 WARN | 11/4/0 WARN | 160.0 (warn) -> 128.0 (warn) | 28.0/-8.0 | warn -> warn | yes | - | kinematic_sequence_order,kinematic_sequence_timing_ms_before_club_peak,spin_rpm,total_over_carry |
| K9_s9_100000 | 12/3/0 WARN | 12/3/0 WARN | 160.0 (warn) -> 128.0 (warn) | 28.0/-8.0 | warn -> warn | yes | - | kinematic_sequence_order,kinematic_sequence_timing_ms_before_club_peak,total_over_carry |
| K9_s9_200000 | 10/5/0 WARN | 10/5/0 WARN | 160.0 (warn) -> 128.0 (warn) | 28.0/-4.0 | warn -> warn | yes | - | kinematic_sequence_order,kinematic_sequence_timing_ms_before_club_peak,peak_speed_thorax_deg_s,grf_lead_vertical_bw,total_over_carry |
| K9_s9_300000 | 12/3/0 WARN | 12/3/0 WARN | 160.0 (warn) -> 128.0 (warn) | 32.0/0.0 | warn -> warn | yes | - | kinematic_sequence_order,kinematic_sequence_timing_ms_before_club_peak,total_over_carry |
| K14a_s21_300000 | - | 14/0/1 FAIL | - -> 120.0 (pass) | 36.0/80.0 | - -> fail | n/a (no old Evaluator score) | kinematic_sequence_order | - |

