# V12U reference refit (LOCAL refit proxies, NOT official, NOT Evaluator grades)
Command: results/v5_runs/stageV12U_ref_s1/cmd.txt (scripts/v12u_ref_fit.py, warm from V12T keys, 30 gens, pop 24, seed 21).
Objective: the V10 terms, plus h_sd2 (on-face & |az|<=7 & golfphys lateral per 100 yd <=13.5, harness-style), heel rate (on-face & dy < -10 mm) and median lateral. Weights: SD2 40, HEEL 30, LAT 5.
Draws: fit on pid 3000-3047 (V12U_PID0=3000). Held-out set: pid 5000-5047, disjoint from the fit draws (results/v10_diag/V12*_holdout_pid5000.json). Fit-draw column = last logged gen in logs/v12Uref.log.
| metric | V12T held-out | V12U held-out | V12U fit draws (gen 29) |
|---|---|---|---|
| contact_rate | 0.959 | 0.959 | 0.94 |
| h_sd2 | 0.854 | 0.896 | 0.9 |
| heel | 0.125 | 0.104 | 0.04 |
| lat_med | 3.939 | 4.733 | 5.19 |
| h_plant | 0.939 | 0.959 | 0.94 |
| h_turn_med | 6.102 | 5.059 | 5.82 |
| nom_tc | 1.422 | 1.471 | 1.44 |
| nom_dz | 9.279 | 3.095 | -3.43 |
| mph_p10 | 69.588 | 69.427 | 69.6 |
| pel_med | 226.189 | 224.081 | 222.62 |

Held-out, V12U vs V12T: start dir proxy .85 -> .90, heel .125 -> .10, plant .94 -> .96, contact .96 (same), turn median 6.1 -> 5.1 deg. Nominal ref dz +9.3 -> +3.1 mm. Nominal t/c 1.42 -> 1.47 (the reference alone, with no residual).
Downstream (local harness): V16a = U3 from V13h 50k on V12U keys, dz_tgt -6 mm. It struck at nominal dz -9.4 mm, failing t/c at both 50k and 100k (12/5/2, start dir .79/.75). The policy was trained against V12T's +9 mm reference. Autoqueue U6 retargets dz_tgt to 0.

Label (port): every held-out column here is a reference-refit PROXY on pid 5000-5047 (disjoint from fit pids 3000-3047), NOT the harness and not an Evaluator grade. The fit-draw column comes from a refit log that is not in the repo. V16a figures are Trainer-local and not backed by a committed results file.
