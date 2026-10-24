# Harness v3 re-score (PROVISIONAL), 2026-10-19

Harness commit ae026ab. Wrapper `_run_j_gateoff_gp_v3.py`: arm 0.6, club 1.15, gate off, golfphys t/c, 24 deterministic eps (seeds 4000/8000/9000 x 8).
Deterministic default rows are identical to v2 for all six checkpoints. Only `swing/grf_lead_vertical_bw` changed; `mine/grf_lead_vertical_raw_info` and `mine/robustness` are new.

| ckpt | v2 P/W/F | v3 P/W/F | GRF v2 raw | GRF v3 (butter 50 Hz) | 12/14 Hz | robustness | contact / SD / foot pass | spread failures |
|---|---|---|---|---|---|---|---|---|
| K22r5_s51 100k | FAIL 13/3/1 | FAIL 14/3/1 | 2.589 F | 1.365 P | 1.369/1.368 | FAIL | 0.83 / 0.58 / 0.79 | spin med 4028 F; t/c med 1.36, p90 1.96 F |
| K22r4_s49 500k | WARN 12/5/0 | FAIL 12/5/1 | 1.536 P | 1.475 P | 1.476/1.484 | FAIL | 0.79 / 0.79 / 0.67 | t/c med 1.37 F |
| K19a_s39 300k | WARN 12/5/0 | FAIL 13/4/1 | 1.812 W | 1.408 P | 1.432/1.402 | FAIL | 0.83 / 0.75 / 0.58 | t/c med 1.40 F; spin p90 4131 F |
| K19a_s39 400k | WARN 12/5/0 | FAIL 13/4/1 | 2.124 W | 1.513 P | 1.486/1.438 | FAIL | 0.79 / 0.79 / 0.46 | t/c med 1.39 F; spin p90 4350 F |
| K18e_s37 200k | WARN 11/6/0 | FAIL 12/5/1 | 2.293 W | 1.570 P | 1.536/1.535 | FAIL | 0.92 / 0.75 / 0.46 | t/c med 1.42 F; spin p10 1096 / p90 4454 F |
| K12_s18 400k (regression) | FAIL 12/3/2 | FAIL 11/4/3 | 1.521 P | 0.707 W | 0.649/0.670 | FAIL | 0.96 / 0.00 / 0.00 | spin p90 4663 F; t/c p90 1.84 F |

Robustness: seeds 7000..7023; joint angle U(+-1.5 deg), joint vel U(+-0.05 rad/s), ball xy U(+-1 cm), friction_rand ON (floor mu U(0.5,1.2), nominal 1.000).

**Label fix (2026-10-19):** these JSONs originally recorded `floor_mu_nominal` 0.978. That was one random U(0.5, 1.2) draw, mislabeled as nominal. The model value is 1.000 (`env/v5_body.py:86`). Corrected in the JSONs; verdicts unaffected.
Caveat: the env's friction range is wide relative to nominal; on K22r5 all 4 contact misses fell at mu 0.58-0.67. A friction-off ablation has not been run.
Trainer K23b (pid 1585104) was running unpinned (affinity 0-7) during these runs, so it shares cores 0-1.

## v3b re-score (harness 67a3e1c, PROVISIONAL, Orchestrator-approved), 2026-10-19

What changed from v3:
- The robustness gate now draws floor friction from U(0.9, 1.1), centred on the model value 1.0. This range is PROVISIONAL and has no turf source.
- The env's U(0.5, 1.2) range moves to the INFO row `mine/robustness_wide_friction_info`. It does not gate.
- Joint and ball noise are unchanged, and the seeds are still 7000..7023.
- The v3 rules are now the default; `--harness v2` reproduces v2 exactly (checked on K22r5).

Checks:
- Every non-robustness row is identical to v3 for all six checkpoints.
- The wide-friction info row reproduces the v3 robustness numbers exactly.
- Floor mu drawn across the 24 gate episodes ranged 0.910-1.075.

Robustness cells give contact / start-dir pass / foot pass, then spin and t/c as median/p10/p90.

| ckpt | v3 | v3b | GRF (50 Hz) | robustness gate, mu U(0.9,1.1) | wide-friction INFO, mu U(0.5,1.2) |
|---|---|---|---|---|---|
| K22r5_s51 100k | FAIL 14/3/1 | FAIL 14/3/1 | 1.365 P | FAIL 1.00/0.88/0.96; spin 3748/1320/4900; t/c 1.355/1.293/3.232 | (fail) 0.83/0.58/0.79; spin 4028/1802/4842; t/c 1.365/1.290/1.961 |
| K22r4_s49 500k | FAIL 12/5/1 | FAIL 12/5/1 | 1.475 P | FAIL 1.00/0.96/0.83; spin 3133/1216/3934; t/c 1.374/1.324/2.997 | (fail) 0.79/0.79/0.67; spin 3192/2204/3739; t/c 1.368/1.313/1.435 |
| K19a_s39 300k | FAIL 13/4/1 | FAIL 13/4/1 | 1.408 P | FAIL 1.00/0.88/0.67; spin 3515/1278/4491; t/c 1.536/1.342/2.076 | (fail) 0.83/0.75/0.58; spin 3672/1651/4131; t/c 1.396/1.314/1.679 |
| K19a_s39 400k | FAIL 13/4/1 | FAIL 13/4/1 | 1.513 P | FAIL 1.00/0.79/0.54; spin 3373/1245/4073; t/c 1.391/1.294/2.927 | (fail) 0.79/0.79/0.46; spin 3732/2468/4350; t/c 1.389/1.282/1.451 |
| K18e_s37 200k | FAIL 12/5/1 | FAIL 12/5/1 | 1.570 P | FAIL 1.00/0.79/0.50; spin 3765/949/4604; t/c 1.471/1.273/3.434 | (fail) 0.92/0.75/0.46; spin 3470/1096/4454; t/c 1.419/1.261/2.505 |
| K12_s18 400k | FAIL 11/4/3 | FAIL 11/4/3 | 0.707 W | FAIL 1.00/0.00/0.00; spin 3010/1399/4486; t/c 1.267/1.159/1.918 | (fail) 0.96/0.00/0.00; spin 3179/1254/4663; t/c 1.279/1.133/1.844 |

Contact is 24/24 under the gate friction for every checkpoint. All six still FAIL robustness on foot plant, start direction, t/c and/or spin spread.

## v3c re-score (harness 47f30f8, PROVISIONAL, Orchestrator-approved; default), 2026-10-24

Gate friction U(0.7, 1.05) per episode (applied 0.717-1.006 on seeds 7000..7023, all rows); deterministic rows at mu 1.0; wide U(0.5,1.2) and stress 1.1 friction and the lead-foot shear ratio are INFO only.
Worker `_run_j_gateoff_gp_v3.py`, taskset 0-1, 2 workers, OMP/MKL 2, V3_FRICTION_RANGE unset.
- First 7 rows: Oct 19 job files (written to disk before the job died), verified complete: harness v3c, 24 gate eps, all robustness/info rows present, mu in range. Not re-run.
- New rows (Trainer read-only exports, md5-snapshotted into `_evalsnap/`, obs 116 / action 29 match env+ckpt+vecnorm):
  K23b 300k @ a1d67c8 (keys stageK22e_ref_s1, md5 68b00781); K25b 400k @ 5cb4d43 (stageK25_ref_s1, fa0b5a95); K27a 400k @ 9225b4a (stageK22e_ref_s1, 68b00781);
  K27b 400k and K27c 300k @ 493dae5 (env/train/golfphys/scripts identical to 142daf3) + the Trainer's UNCOMMITTED stageK27_ref_s1/tuned_keys_flat.json (md5 94471d78, 121 keys, 12 pc|) copied into `_ro_trainer_493dae5_k27ref`.
- Trainer comparison: K27a/K27b/K27c Trainer v3c JSONs match exactly (counts, rows, gate fractions, spin/t-c percentiles). K23b (Trainer pre-v3b v3 run) and K25b (Trainer v3b, friction 0.9-1.1) have the same 14/3/1 counts under their older harness.

Counts are P/W/F. Gate cells: contact / start-dir pass / foot pass fractions (need 0.95/0.90/0.90).

| ckpt | v3c | FAIL rows | WARN rows | gate contact/SD/foot | spin med/p10/p90 | t/c med/p10/p90 | shear peak (info) |
|---|---|---|---|---|---|---|---|
| K12_s18_400k | FAIL 11/4/3 | start_direction, lead_foot_plant, robustness | kseq_order, kseq_timing, grf_lead_vertical_bw, total_over_carry | 0.92/0.00/0.00 | 3158/1557/5023 | 1.276/1.146/1.927 | 1.02 |
| K18e_s37_200k | FAIL 12/5/1 | robustness | kseq_order, kseq_timing, pelvis_dps, spin_rpm, total_over_carry | 0.96/0.62/0.50 | 2597/995/4458 | 1.531/1.272/3.357 | 0.49 |
| K19a_s39_300k | FAIL 13/4/1 | robustness | kseq_order, kseq_timing, pelvis_dps, total_over_carry | 1.00/0.79/0.62 | 2783/1089/3882 | 1.427/1.315/3.021 | 0.65 |
| K19a_s39_400k | FAIL 13/4/1 | robustness | kseq_order, kseq_timing, pelvis_dps, total_over_carry | 1.00/0.79/0.54 | 3103/1125/3715 | 1.406/1.294/3.257 | 0.84 |
| K22r4_s49_500k | FAIL 12/5/1 | robustness | kseq_order, kseq_timing, pelvis_dps, x_factor_top_deg, total_over_carry | 0.96/0.92/0.92 | 2545/1313/3546 | 1.425/1.314/3.675 | 0.78 |
| K22r5_s51_100k | FAIL 14/3/1 | robustness | kseq_timing, pelvis_dps, spin_rpm | 0.92/0.75/0.83 | 2943/1330/4476 | 1.386/1.264/2.996 | 0.76 |
| K24a_s53_200k | FAIL 13/4/1 | robustness | kseq_timing, pelvis_dps, spin_rpm, total_over_carry | 1.00/1.00/1.00 | 3143/984/4199 | 1.528/1.327/3.185 | 0.73 |
| K23b_s52_300k | FAIL 14/3/1 | robustness | kseq_timing, pelvis_dps, total_over_carry | 0.96/0.83/0.96 | 2235/941/4091 | 1.782/1.301/3.453 | 0.69 |
| K25b_s56_400k | FAIL 14/3/1 | robustness | pelvis_dps, spin_rpm, total_over_carry | 1.00/0.92/0.83 | 3273/999/4385 | 1.487/1.326/3.388 | 0.97 |
| K27a_s59_400k | FAIL 12/3/3 | spin_rpm, total_over_carry, robustness | kseq_order, kseq_timing, pelvis_dps | 0.96/0.96/0.92 | 4103/3572/4583 | 1.517/1.357/1.743 | 0.57 |
| K27b_s60_400k | FAIL 13/3/2 | spin_rpm, robustness | kseq_order, kseq_timing, pelvis_dps | 1.00/1.00/0.75 | 4094/1976/4585 | 1.281/1.204/1.866 | 0.86 |
| K27c_s61_300k | FAIL 12/4/2 | spin_rpm, robustness | kseq_order, kseq_timing, pelvis_dps, total_over_carry | 1.00/0.92/0.96 | 3978/2073/4683 | 1.305/1.233/1.759 | 0.81 |

No row passes. Every row FAILs robustness (spin and/or t/c spread). Best by FAIL count, then WARNs, then robustness: K25b_s56 400k (14/3/1, contact 1.00, start-dir 0.92, foot 0.83; t/c median 1.49).

## v3d re-grade (harness 6b0db8c, opt-in, UNDER REVIEW; v3c stays default), 2026-10-24

v3d re-grades the same v3c episodes (`eval/harness_v3d.py`; rules and citations in `docs/HARNESS_V3D_NOTES.md`). JSONs: `*_dtfix_newchecks_v3d_gateoff_gp_arm06.json`.
A live `--harness v3d` run of K25b 400k reproduced the re-grade exactly (all row statuses, 14/3/1 FAIL).
Club p10/median: the new robustness rule needs >= 0.93 (LOW CONFIDENCE). Arm->club: ms the arm peaks before the club (v3d needs >= 20).

| ckpt | v3d | FAIL rows | WARN rows | gate contact/SD/foot | club p10/median | spin med/p10/p90 (v3d status) | pelvis dps | arm->club ms |
|---|---|---|---|---|---|---|---|---|
| K12_s18_400k | FAIL 10/5/3 | start_direction, lead_foot_plant, robustness | kseq_order, kseq_timing, grf_lead_vertical_bw, spin_rpm, total_over_carry | 0.92/0.00/0.00 | 0.74 | 3158/1557/5023 (P/W/F) | 376 | -4 |
| K18e_s37_200k | FAIL 14/3/1 | robustness | kseq_timing, pelvis_dps, total_over_carry | 0.96/0.62/0.50 | 0.64 | 2597/995/4458 (P/F/F) | 153 | 4 |
| K19a_s39_300k | FAIL 13/4/1 | robustness | kseq_order, kseq_timing, pelvis_dps, total_over_carry | 1.00/0.79/0.62 | 0.70 | 2783/1089/3882 (P/F/W) | 161 | -4 |
| K19a_s39_400k | FAIL 13/4/1 | robustness | kseq_order, kseq_timing, pelvis_dps, total_over_carry | 1.00/0.79/0.54 | 0.72 | 3103/1125/3715 (P/F/W) | 152 | -4 |
| K22r4_s49_500k | FAIL 13/4/1 | robustness | kseq_timing, pelvis_dps, x_factor_top_deg, total_over_carry | 0.96/0.92/0.92 | 0.67 | 2545/1313/3546 (P/W/P) | 229 | 8 |
| K22r5_s51_100k | FAIL 15/2/1 | robustness | kseq_timing, pelvis_dps | 0.92/0.75/0.83 | 0.66 | 2943/1330/4476 (P/W/F) | 191 | 12 |
| K24a_s53_200k | FAIL 13/4/1 | robustness | kseq_timing, pelvis_dps, spin_rpm, total_over_carry | 1.00/1.00/1.00 | 0.70 | 3143/984/4199 (P/F/F) | 165 | 12 |
| K23b_s52_300k | FAIL 14/3/1 | robustness | kseq_timing, pelvis_dps, total_over_carry | 0.96/0.83/0.96 | 0.75 | 2235/941/4091 (P/F/F) | 181 | 12 |
| K25b_s56_400k | FAIL 14/3/1 | robustness | kseq_timing, pelvis_dps, total_over_carry | 1.00/0.92/0.83 | 0.66 | 3273/999/4385 (P/F/F) | 192 | 16 |
| K27a_s59_400k | FAIL 13/2/3 | spin_rpm, total_over_carry, robustness | kseq_timing, pelvis_dps | 0.96/0.96/0.92 | 0.99 | 4103/3572/4583 (F/P/F) | 179 | 8 |
| K27b_s60_400k | FAIL 15/1/2 | spin_rpm, robustness | kseq_timing | 1.00/1.00/0.75 | 0.81 | 4094/1976/4585 (F/W/F) | 254 | 12 |
| K27c_s61_300k | FAIL 14/2/2 | spin_rpm, robustness | kseq_timing, total_over_carry | 1.00/0.92/0.96 | 0.82 | 3978/2073/4683 (W/P/F) | 252 | 8 |

| ckpt | v3c | v3d | changed rows (v3c -> v3d) |
|---|---|---|---|
| K12_s18_400k | FAIL 11/4/3 | FAIL 10/5/3 | spin_rpm pass->warn |
| K18e_s37_200k | FAIL 12/5/1 | FAIL 14/3/1 | kseq_order warn->pass; spin_rpm warn->pass |
| K19a_s39_300k | FAIL 13/4/1 | FAIL 13/4/1 | - |
| K19a_s39_400k | FAIL 13/4/1 | FAIL 13/4/1 | - |
| K22r4_s49_500k | FAIL 12/5/1 | FAIL 13/4/1 | kseq_order warn->pass |
| K22r5_s51_100k | FAIL 14/3/1 | FAIL 15/2/1 | spin_rpm warn->pass |
| K24a_s53_200k | FAIL 13/4/1 | FAIL 13/4/1 | - |
| K23b_s52_300k | FAIL 14/3/1 | FAIL 14/3/1 | - |
| K25b_s56_400k | FAIL 14/3/1 | FAIL 14/3/1 | kseq_timing pass->warn; spin_rpm warn->pass |
| K27a_s59_400k | FAIL 12/3/3 | FAIL 13/2/3 | kseq_order warn->pass |
| K27b_s60_400k | FAIL 13/3/2 | FAIL 15/1/2 | kseq_order warn->pass; pelvis_dps warn->pass |
| K27c_s61_300k | FAIL 12/4/2 | FAIL 14/2/2 | kseq_order warn->pass; pelvis_dps warn->pass |

No row passes under v3c or v3d, so the spin-band-only flag never fires. Every row still FAILs robustness. Under v3d, 11 of 12 also fail the new club-speed p10 rule (only K27a, 0.99, clears it).
The arm->club >= 20 ms requirement holds the timing row at WARN for every checkpoint (max 16 ms, K25b), and it flips K25b's timing from PASS to WARN.
Under v3d, K27b 400k ranks highest by count (15/1/2), but it still has 2 FAILs. The best row by the agreed order (fewest FAILs) is K22r5 100k at 15/2/1, which has 1 FAIL.
