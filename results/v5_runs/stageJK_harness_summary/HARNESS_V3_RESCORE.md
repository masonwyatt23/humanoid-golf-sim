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
