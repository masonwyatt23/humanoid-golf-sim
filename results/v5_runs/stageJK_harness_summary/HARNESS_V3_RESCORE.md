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

## K28/K29 independent scores (v3c default + v3d live), 2026-10-24

Labels: reference-guided residual with tracking assistance; reference re-tuned open-loop by CMA-ES, stock G1 torque, warm-started. v3d's spin, pelvis and timing bands are DERIVED, and its club-speed p10 robustness rule is LOW CONFIDENCE.
Procedure (same as K27c 300k): wrapper `_run_j_gateoff_gp_v3.py` (fixed v3 worker), arm 0.6, club 1.15, gate off, golfphys t/c, 24 deterministic eps (seeds 4000/8000/9000 x 8), robustness seeds 7000..7023 (joint +-1.5 deg, ball +-1 cm, gate friction U(0.7,1.05): applied 0.717-1.006, ball noise non-zero on 24/24). Run under taskset 0-1, 2 workers, OMP/MKL 2, V3_FRICTION_RANGE unset, one job at a time. The Trainer's K29a/b training had already exited normally (final.zip 15:07 ET) before the first job started.
- Snapshots: the Trainer's `_snap/` copies (untracked in the Trainer repo) were copied into `_evalsnap/` with md5s verified against both `_snap/` and the live run dirs (`_evalsnap_md5_K28_K29.txt`). Layout: env obs 116 / act 29 == ckpt == vecnorm for all 14. Keys: stageK27_ref_s1/tuned_keys_flat.json, md5 94471d78 (121 keys, 12 pc|), same file as `_ro_trainer_493dae5_k27ref`. res_mult 0.25 on the 9 lower-body/waist groups, res_scale 0.5 (args.json).
- Code exports: K28 @ `_ro_trainer_dfc30a7` (= K28 harness commit b0f7c5e plus the committed K27 keys file; no env/train/golfphys/scripts diff vs 142daf3..b0f7c5e). K29 @ `_ro_trainer_6c18fd0` (Trainer HEAD; the only train change since b0f7c5e is f0b82be --sep_lo/--sep_span, a reward-only change).
- v3c: `_batch_v3c_K28_K29.sh` (15:07-15:17 ET). v3d: LIVE `--harness v3d` runs (`_batch_v3d_live_K28_K29.sh`, 15:18-15:29 ET). For all 14, the live v3d result equals `apply_v3d_flagged()` applied to the v3c JSON: same verdict, same counts, and every row's status and values identical.
- Trainer comparison: our v3c matches the Trainer's `<ckpt>_v3.json` (harness v3c) exactly for all 14: counts, every row status, gate fractions, and the spin, t/c and club percentiles. Our v3d matches the Trainer's `_v3d.json` exactly where one exists (K28a 400k, K28b 400k, all six K29). The Trainer has no v3d JSON for K28a 100k/200k/300k or K28b 100k/200k/300k.

| ckpt | Trainer commit | v3c | v3c FAIL | v3c WARN | v3d | v3d FAIL | v3d WARN | gate contact/SD/foot | club p10/median | spin med/p10/p90 | t/c med/p10/p90 | club mph | carry/total yd | spin rpm | pelvis dps | arm->club ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| K28b_s63_400k | dfc30a7 | FAIL 12/5/1 | robustness | kseq_order, kseq_timing, pelvis_dps, spin_rpm, total_over_carry | FAIL 13/4/1 | robustness | kseq_timing, pelvis_dps, spin_rpm, total_over_carry | 1.00/0.96/0.96 | 0.81 (59.7/73.4) | 3750/1576/4419 | 1.318/1.254/1.963 | 73.8 | 129/167 | 3951 | 231 | 12 |
| K28b_s63_300k | dfc30a7 | FAIL 12/5/1 | robustness | kseq_order, kseq_timing, pelvis_dps, spin_rpm, total_over_carry | FAIL 13/4/1 | robustness | kseq_timing, pelvis_dps, spin_rpm, total_over_carry | 1.00/0.92/0.96 | 0.81 (59.5/73.4) | 3653/2041/4371 | 1.290/1.241/1.769 | 73.9 | 135/172 | 3886 | 231 | 12 |
| K28a_s62_400k | dfc30a7 | FAIL 12/4/2 | spin_rpm, robustness | kseq_order, kseq_timing, pelvis_dps, total_over_carry | FAIL 13/3/2 | spin_rpm, robustness | kseq_timing, pelvis_dps, total_over_carry | 1.00/0.96/0.92 | 0.81 (59.6/73.4) | 4106/1684/4756 | 1.316/1.232/1.802 | 73.8 | 125/157 | 4617 | 233 | 12 |
| K28a_s62_100k | dfc30a7 | FAIL 12/5/1 | robustness | kseq_order, kseq_timing, pelvis_dps, spin_rpm, total_over_carry | FAIL 14/3/1 | robustness | pelvis_dps, spin_rpm, total_over_carry | 1.00/0.88/0.88 | 0.73 (53.6/73.4) | 3970/1952/4702 | 1.308/1.246/2.594 | 73.7 | 133/170 | 3726 | 240 | 20 |
| K29b_s65_300k | 6c18fd0 | FAIL 12/3/3 | spin_rpm, total_over_carry, robustness | kseq_order, kseq_timing, pelvis_dps | FAIL 13/2/3 | spin_rpm, total_over_carry, robustness | kseq_timing, pelvis_dps | 1.00/0.92/1.00 | 0.82 (60.3/73.8) | 4131/1402/4649 | 1.387/1.248/2.090 | 74.2 | 109/154 | 4887 | 224 | 12 |
| K29a_s64_300k | 6c18fd0 | FAIL 12/3/3 | spin_rpm, total_over_carry, robustness | kseq_order, kseq_timing, pelvis_dps | FAIL 13/2/3 | spin_rpm, total_over_carry, robustness | kseq_timing, pelvis_dps | 1.00/0.88/0.96 | 0.77 (56.2/73.4) | 3689/1608/4512 | 1.403/1.282/2.892 | 73.8 | 116/161 | 4106 | 207 | 16 |
| K28a_s62_200k | dfc30a7 | FAIL 11/5/2 | spin_rpm, robustness | kseq_order, kseq_timing, pelvis_dps, grf_lead_vertical_bw, total_over_carry | FAIL 13/3/2 | spin_rpm, robustness | kseq_timing, grf_lead_vertical_bw, total_over_carry | 1.00/0.92/0.92 | 0.88 (64.6/73.2) | 4175/2475/4568 | 1.307/1.240/1.646 | 73.5 | 119/155 | 4464 | 252 | 16 |
| K28a_s62_300k | dfc30a7 | FAIL 11/5/2 | spin_rpm, robustness | kseq_order, kseq_timing, pelvis_dps, grf_lead_vertical_bw, total_over_carry | FAIL 12/4/2 | spin_rpm, robustness | kseq_timing, pelvis_dps, grf_lead_vertical_bw, total_over_carry | 1.00/0.92/0.96 | 0.99 (72.2/72.9) | 4041/3385/4810 | 1.314/1.245/1.543 | 72.9 | 124/160 | 4173 | 247 | 12 |
| K28b_s63_100k | dfc30a7 | FAIL 12/4/2 | spin_rpm, robustness | kseq_order, kseq_timing, pelvis_dps, total_over_carry | FAIL 13/3/2 | spin_rpm, robustness | kseq_timing, pelvis_dps, total_over_carry | 1.00/1.00/0.83 | 0.99 (72.8/73.5) | 4178/3329/4750 | 1.260/1.203/1.450 | 73.9 | 120/155 | 4751 | 248 | 12 |
| K28b_s63_200k | dfc30a7 | FAIL 13/3/2 | spin_rpm, robustness | kseq_order, kseq_timing, pelvis_dps | FAIL 14/2/2 | spin_rpm, robustness | kseq_timing, pelvis_dps | 1.00/1.00/0.88 | 0.73 (53.9/73.7) | 3955/1767/4638 | 1.275/1.208/2.339 | 74.1 | 137/168 | 4105 | 226 | 12 |
| K29a_s64_100k | 6c18fd0 | FAIL 12/4/2 | spin_rpm, robustness | kseq_order, kseq_timing, pelvis_dps, total_over_carry | FAIL 13/3/2 | spin_rpm, robustness | kseq_timing, pelvis_dps, total_over_carry | 1.00/0.96/1.00 | 0.81 (59.4/73.3) | 3890/1724/4522 | 1.394/1.267/1.828 | 73.6 | 122/162 | 4186 | 224 | 16 |
| K29a_s64_200k | 6c18fd0 | FAIL 12/3/3 | spin_rpm, total_over_carry, robustness | kseq_order, kseq_timing, pelvis_dps | FAIL 13/2/3 | spin_rpm, total_over_carry, robustness | kseq_timing, pelvis_dps | 1.00/0.92/1.00 | 0.72 (52.6/73.4) | 3562/1656/4371 | 1.474/1.282/3.124 | 73.7 | 114/159 | 4128 | 217 | 16 |
| K29b_s65_100k | 6c18fd0 | FAIL 12/4/2 | spin_rpm, robustness | kseq_order, kseq_timing, pelvis_dps, total_over_carry | FAIL 13/3/2 | spin_rpm, robustness | kseq_timing, pelvis_dps, total_over_carry | 1.00/0.88/0.88 | 0.78 (57.4/73.9) | 4054/1633/4764 | 1.292/1.222/2.705 | 74.0 | 133/166 | 4194 | 237 | 12 |
| K29b_s65_200k | 6c18fd0 | FAIL 12/4/2 | spin_rpm, robustness | kseq_order, kseq_timing, pelvis_dps, total_over_carry | FAIL 13/3/2 | spin_rpm, robustness | kseq_timing, pelvis_dps, total_over_carry | 1.00/0.92/0.92 | 0.82 (60.2/73.7) | 4012/1459/4718 | 1.320/1.228/2.021 | 74.0 | 136/170 | 4020 | 236 | 12 |

No checkpoint passes under v3c or v3d. All 14 FAIL robustness, and 12 of 14 also fail the v3d club p10 >= 0.93x median rule (only K28a 300k and K28b 100k reach 0.99, and both fail on spin). The spin-band-only flag never fires (no v3d PASS).
Best by FAIL count, then WARNs: v3d K28a_s62 100k 14/3/1 is the first row where v3d kseq_timing passes (arm 20 ms before club). It still WARNs pelvis 240 < 250 dps, spin 3726 > 3700 and t/c, and it FAILs robustness (start-dir 0.88, foot 0.88, spin p90 4702, t/c p90 2.59, club p10 0.73x). Under v3c the best rows are K28b 400k / 300k and K28a 100k, at 12/5/1.
K29a/b (sep_lo 20 ms, spin_hi 2800) did not move arm->club timing to >= 20 ms (12-16 ms), and spin got worse: deterministic spin 4020-4887 rpm, a FAIL on all six rows.

## K29a/b 400k, K30a/b, K31a 200k — v3c (default) + live v3d with strike rows and face-edge side-by-side model (2026-10-24, Evaluator)

Label: reference-guided residual with tracking assistance; reference re-tuned open-loop by CMA-ES, stock G1 torque, warm-started. Harness: scott-e 4bb0801..eaf3f9e (v3c verdict rules unchanged; v3d derived bands, club p10 LOW confidence, strike-height PROVISIONAL at 26.5 mm = measured spec single brand). RO Trainer exports per row; snapshots md5'd in _evalsnap_md5_K29_K30.txt; 116/29 layout and K27 ref keys (md5 94471d78…) verified. arm 0.6, club 1.15, 24 det eps, gate off, golfphys, robustness seeds 7000-7023 (friction 0.7-1.05).

| ckpt (export) | v3c P/W/F | v3d P/W/F | v3d fails | gate contact/start/foot | club p10/med | det spin | rob spin med/p10/p90 | rob t/c med/p10/p90 | det dz / dy mm | face-edge model (det spin cap/lin/r2207; launch) | Trainer v3c / v3d |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K31a_s68_200k (c79bac2) | 12/5/1 | 13/5/1 | robustness | 1.00/1.00/1.00 | 0.81 | 3945 | 3629/1950/4225 | 1.34/1.26/1.84 | -20.8 / 11.9 | 2931/3228/2819; spin pass, launch fail → FAIL | 12/5/1 / 13/4/1 |
| K29a_s64_400k (6c18fd0) | 12/4/2 | 13/4/2 | spin_rpm, robustness | 1.00/0.96/0.96 | 0.99 | 4246 | 3934/3001/4574 | 1.42/1.29/1.92 | -24.3 / 19.6 | 3069/3481/no data; spin no_data, launch no_data → FAIL | 12/4/2 / 13/3/2 |
| K29b_s65_400k (6c18fd0) | 12/3/3 | 13/2/4 | spin_rpm, total_over_carry, robustness, strike_height | 1.00/1.00/1.00 | 0.99 | 4356 | 4001/2769/4688 | 1.36/1.27/1.61 | -26.8 / 10.4 | off face (|dz| > 26.5) → n/a (off face) | 12/3/3 / 13/2/3 |
| K30a_s66_100k (4a955d8) | 13/4/1 | 14/4/1 | robustness | 1.00/0.92/0.83 | 0.69 | 3781 | 3771/1767/4639 | 1.32/1.22/3.35 | -15.2 / 12.7 | 3140/3229/3279; spin pass, launch pass → FAIL | 13/4/1 / 14/3/1 |
| K30a_s66_200k (4a955d8) | 12/4/2 | 13/4/2 | spin_rpm, robustness | 1.00/0.92/0.96 | 0.82 | 4310 | 3816/2154/4685 | 1.31/1.23/1.79 | -22.7 / 10.8 | 3142/3505/no data; spin no_data, launch no_data → FAIL | 12/4/2 / 13/3/2 |
| K30a_s66_300k (4a955d8) | 12/4/2 | 13/4/2 | spin_rpm, robustness | 1.00/0.92/0.96 | 0.88 | 4455 | 4082/2598/4514 | 1.35/1.26/1.87 | -25.4 / 14.4 | 3145/3600/no data; spin no_data, launch no_data → FAIL | 12/4/2 / 13/3/2 |
| K30b_s67_100k (4a955d8) | 12/3/3 | 13/2/4 | spin_rpm, total_over_carry, robustness, strike_height | 0.92/0.92/0.92 | 0.98 | 4535 | 3918/3142/4339 | 1.39/1.31/1.83 | -29.6 / 12.7 | off face (|dz| > 26.5) → n/a (off face) | 12/3/3 / 13/2/3 |
| K30b_s67_200k (4a955d8) | 12/3/3 | 13/2/4 | spin_rpm, total_over_carry, robustness, strike_height | 1.00/1.00/0.96 | 0.98 | 4470 | 4048/2140/4635 | 1.44/1.30/1.90 | -29.3 / 13.5 | off face (|dz| > 26.5) → n/a (off face) | 12/3/3 / 13/2/3 |
| K30b_s67_300k (4a955d8) | 12/3/3 | 13/3/3 | spin_rpm, total_over_carry, robustness | 1.00/0.96/1.00 | 0.76 | 4124 | 3595/1533/4352 | 1.46/1.29/3.33 | -24.1 / 17.2 | 2958/3368/no data; spin no_data, launch no_data → FAIL | 12/3/3 / 13/2/3 |
| K30b_s67_400k (4a955d8) | 12/3/3 | 13/2/4 | spin_rpm, total_over_carry, robustness, strike_height | 1.00/0.88/1.00 | 0.74 | 4660 | 3843/1389/4640 | 1.50/1.29/3.11 | -31.4 / 15.3 | off face (|dz| > 26.5) → n/a (off face) | 12/3/3 / 13/2/3 |

* v3c: all 10 rows match the Trainer's JSONs exactly. v3d: differences vs the Trainer are only the new PROVISIONAL `mine/strike_height` row (Trainer v3d predates it): +1 WARN (15 < |dz| < 26.5) or +1 FAIL (|dz| ≥ 26.5: K29b 400k, K30b 100k/200k/400k).
* K31a 200k matches the Trainer's quoted numbers (12/5/1 v3c, 13/4/1 v3d before strike row, 1.00/1.00/1.00, spin 3629/4225, t/c p90 1.84, club p10 0.81x); deterministic dz −20.8 mm (Trainer −24 median is over its own strike log).
* Best row: K30a 100k — v3c 13/4/1, v3d 14/4/1 (only FAIL = robustness: foot 0.83, club p10 0.69x, t/c p90 3.35); dz −15.2 mm (warn edge). K31a 200k is the first with all three robustness rates 1.00 but fails on club p10 0.81x and t/c p90 1.84.
* Full pass: NONE under v3c or v3d, and none under the face-edge side-by-side model (no face-edge-model-only flags, no spin-band-only flags). No cinematic render.


## Tee / face geometry pass-through + K32a_s72 100k/200k (v3c old tee, v3d crown-level tee + tee-0 counterfactual), 2026-10-24, Evaluator

Label: reference-guided residual with tracking assistance (K32 keys = K27 + knee|lead|imp -0.45, il|right_elbow 0), trained at tee_dz 0.020 with face_h 0.053. RO export `_ro_trainer_13f0d2b` (Trainer HEAD; env/train identical to 8e91bd0, which adds --tee_dz/--ball_dx; `JEnv.configure(**kw)` setattr's any non-None key and `JEnv.reset` copies tee_dz/ball_dx/face_h to the env). Snapshots md5-identical to `_snap/` and the live run dir (`_evalsnap_md5_K32a.txt`); layout obs 116 / act 29 == ckpt == vecnorm; keys stageK32_ref_s1/tuned_keys_flat.json md5 91cbc936 (export == Trainer). arm 0.6, club 1.15, 24 det eps, gate off, golfphys, robustness 7000-7023, taskset 0-1, 2 workers, OMP/MKL 2. No K33* snapshot existed in `_snap/` at run time. No Trainer crown/tee_mode function exists yet (13f0d2b).

Harness changes:
* `_j_worker_gp_v3.py` CFG and `render_blender/export_v5j_trajectory.py` CFG: + `tee_dz, ball_dx, face_h, tee_mode` (parity test key list updated). configure() skips None, so old args (no keys) are unchanged.
* Worker env `V3_TEE`: `args` (default) | float m | `crown`. `crown` = harness `tee_geometry()`: crown_z = clubhead-site z + head half-height (0.032) x face-up z at the address pose (reset, tee 0); tee_dz = crown_z - ball_centre_z. HOOK: if the env exposes `crown_tee_dz()` (Trainer tee_mode work) it is used and must agree with the harness value within 0.5 mm, else the worker aborts. `V3_FACE_H`: `none` = 64 mm head box, float = m, unset = args.json.
* INFO rows (all v3 harnesses, never gating): `mine/tee_dz_info`, `mine/face_h_info`, `mine/tee_height_info` (ball centre / ball bottom = tee peg / crown / face centre / sole, from env geometry). Result JSON carries `tee_info`.
* `harness_v3d.apply_v3d_flagged(r, r_tee0)`: if v3d PASSes only at the new tee and the tee-0 run (v3c JSON re-graded by apply_v3d) does not → `not a pass (new-tee-only)`; `tee0_counterfactual` recorded.
* Regression: K30a_s66 100k deterministic-only re-score (args tee, export 4a955d8): all 28 deterministic rows (status + values) and the deterministic strike dy/dz identical to the committed v3c JSON; only differences are the absent robustness rows (det-only) and the 3 new INFO rows.

Crown-level tee derived from sim head geometry; crown-level per GOLF.com / Golf Digest / Golf Monthly advice: **tee_dz = 21.46 mm** (Trainer's fixed 0.020 is 1.46 mm lower; equator 1.5 mm below crown). Geometry at address: ball centre 59.9 mm / bottom 38.5 mm (1.52 in) at tee 0; head-box crown at the face 81.3 mm; face centre (clubhead site) 49.9 mm; sole 2.0 mm; face-up tilt 10.5 deg. Crown tee: ball centre 81.3 mm, bottom 60.0 mm (2.36 in), ball centre 27.0 mm above face centre along face-up. At 0.020: bottom 58.5 mm (2.30 in).

FLAG face_h: K32a args.json has face_h 0.053 (non-default): off-face contacts become misses (ball disabled). At tee 0 this turns all 24 K32a 100k deterministic swings into misses (true contact 0), so the primary rows below use V3_FACE_H=none (64 mm box, the physics every earlier row was scored with); the args-face_h runs are kept as sensitivity JSONs (`*_tee0_v3c_*`, `*_teecrown_v3d_*`, `*_teeargs_v3d_*`).

| ckpt | run | tee mm | v3c / v3d P/W/F | FAILs | WARNs | rob contact/start/foot | club p10/med | det spin | rob spin med/p10/p90 | rob t/c med/p10/p90 | det dz / dy mm | rob dz med (p10) | face-edge model | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| K32a 100k | v3c old tee | 0 | 12/3/3 | spin_rpm, total_over_carry, robustness | kseq order/timing, pelvis | 1.00/0.96/0.83 | 0.75 | 4304 | 3596/1424/4550 | 1.44/1.28/3.07 | -27.5 / 7.3 | -20.7 (-31.2) | – | – |
| K32a 100k | v3d tee-0 cf | 0 | 13/2/4 | spin_rpm, total_over_carry, robustness, strike_height | kseq timing, pelvis | same | 0.75 | 4304 | same | same | -27.5 (off face) | -20.7 | n/a (off face) | – |
| K32a 100k | v3d crown | 21.5 | 15/2/2 | total_over_carry, robustness | kseq timing, pelvis | 1.00/0.92/0.83 | 0.75 | 2914 | 2003/978/3862 | 1.45/1.27/2.72 | -7.2 / 11.4 | -4.0 (-21.0) | FAIL (rob spin p10) | new-tee-only no (FAIL) |
| K32a 100k | v3d own args (info) | 20.0, face_h .053 | 15/2/2 | total_over_carry, robustness | kseq timing, pelvis | 0.96/0.88/0.83 | 0.74 | 3013 | 2054/972/3659 | 1.44/1.30/2.73 | -8.6 / 11.1 | -3.2 (-17.8) | FAIL | – |
| K32a 200k | v3c old tee | 0 | 12/4/2 | total_over_carry, robustness | kseq order/timing, pelvis, spin_rpm | 1.00/0.92/0.88 | 0.82 | 3680 | 3965/1521/4504 | 1.42/1.31/2.28 | -20.2 / 9.6 | -23.8 (-30.9) | – | – |
| K32a 200k | v3d tee-0 cf | 0 | 14/3/2 | total_over_carry, robustness | kseq timing, pelvis, strike_height | same | 0.82 | 3680 | same | same | -20.2 / 9.6 | -23.8 | FAIL | – |
| K32a 200k | v3d crown | 21.5 | 15/3/1 | robustness | kseq timing, pelvis, total_over_carry | 1.00/0.88/0.92 | 0.82 | 3081 | 2764/1194/4192 | 1.42/1.29/2.45 | -10.1 / 13.0 | -8.1 (-22.4) | FAIL (rob spin p10) | new-tee-only no (FAIL) |
| K32a 200k | v3d own args (info) | 20.0, face_h .053 | 15/3/1 | robustness | kseq timing, pelvis, total_over_carry | 0.88/0.83/0.79 | 0.81 | 3128 | 2699/1188/3782 | 1.44/1.29/2.46 | -10.8 / 12.7 | -7.7 (-22.8) | FAIL | – |

* Own-args runs reproduce the Trainer's nominal dz -8.6 / -10.8 mm; det-median spin 3013 / 3128 vs the Trainer's nominal 2926 / 3010. Robustness median dz -3.2 / -7.7 mm (Trainer ~-9).
* The crown tee lowers spin ~1100-1400 rpm (det) and removes the spin FAIL; every row still FAILs robustness (club p10 0.75-0.82x < 0.93, foot/start < 0.90, rob spin p10 < 1200, t/c p90). No full pass under v3c, v3d, or the face-edge model; new-tee-only flag never fires.
* Tee realism: GOLF.com (Top 100 Teachers poll, ~1.5 in peg; half the ball above the crown), Golf Digest (about half the ball above the crown), Golf Monthly (equator level with the crown). The sim default peg (38.5 mm = 1.52 in) already matches the 1.5 in guidance; crown-level on the 64 mm box needs 60 mm (2.36 in), because the box's face centre sits 49.9 mm up. A real ~53 mm face soled on the ground has its centre ~27 mm up and crown ~55 mm, so 'equator at crown' there means ball bottom ~34 mm (~1.3-1.5 in). On the sim box the crown-level ball centre is 27.0 mm above the face centre, i.e. just above a 53 mm face's top edge (26.5 mm) if that face were centred on the clubhead site.
