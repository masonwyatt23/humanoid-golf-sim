# Stage K checkpoints for the Evaluator (reference-guided residual RL, public refs only; harness adapter scripts/v5_eval_j_worker.py, club 1.15, arm 0.6, gate nx 0.25)
- results/v5_runs/stageK_s1/best_det.zip (+_vecnorm.pkl): 800k, det full swing contact 1.0, 58.7 mph, carry 54 m (no roll). Snapshot: results/v5_runs/_snap/K_s1_800k/
- results/v5_runs/stageK_s1/ckpt_500000.zip: det 58.5 mph / 46.8 m; harness 7/5/3.
- Running: stageK_s1 (to ~2M) and stageK2_s0 (warm from K s1 800k, ord2 order-separation reward, T0 70). New best_det files appear in their dirs; eval.jsonl lists per-100k det metrics.
- Reference: results/v5_runs/stageK_ref/tuned_keys.json (open-loop 64.6 mph / 57.8 m). Residual (0.7*0.2 rad) + tracking floor 0.3: NOT pure RL.

## Stage K3 (latest)
- BEST: results/v5_runs/_snap/K3b_s0_500k/ckpt_500000.zip (+_vecnorm.pkl, args.json): det 63.2 mph, carry 83.9 m, descent 29.2, total/carry 1.25, smash 1.30, GRF 1.01 BW (5 ms), X-factor 55.8; harness FAIL on spin only (4693 rpm); JSON results/v5_runs/stageJ_harness/K3b_s0_500k.json.
- results/v5_runs/_snap/K3_s1_600k (65.7 mph/83.6 m, fails order+spin), K3_s1_200k (10/3/2), K2_s0_600k (63 mph/43.8 m, 9/5/1 before descent terms).
- Adapter: PYTHONPATH=hgs-scott-lb python scripts/v5_realism_j.py <ckpt.zip> (reads args.json next to the ckpt).

## K4 status (2026-10-18 ~22:15 ET)
- Best so far: snapshot results/v5_runs/_snap/K4_s0_100k (61.0 mph, total/carry 1.21, descent 32, smash 1.35, spin 4087, launch 19.8; Evaluator 12/2/1, only spin fails). Also _snap/K4_s1_100k, K3b_s0_500k.
- Original K4 runs (T0 80) collapsed (fell) at 200k; moved to results/v5_runs/_stageK4a_s*. Relaunched as stageK4b s0 (from K4 s0 100k) and s1 (from K3b 500k), T0 70, dl window 17-22, launch<=16, spin<=2900 penalty. Alive (pids 222554/222555), eval every 100k.
- Physics: spin<3000 + launch<=16 + total/carry<=1.25 are jointly infeasible at ~63 mph (golfphys: 24.7 deg descent/1.38 at 63; 28/1.27 at 70; 31.6/1.20 at 80 mph).

## K4c (2026-10-18 ~23:15 ET)
- Snapshots: _snap/K4b_s1_200000 (47.5 mph, spin 2245, smash 1.42, launch 14.5, only t/c 1.68 fails), _snap/K4b_s0_100000/200000 (regressed: order/XF/GRF fail).
- K4b s0 stopped (moved to _stageK4b_s0_old). New stageK4c s0 warm from K4b s1 200k with speed bonus 4, desc_w 4, XF hard 65 (cap w 0.3), GRF w 0.6, T_step 5. K4b s1 (pid 222555) continues unchanged.

## K5 (2026-10-19 ~00:50 ET) — stageK5 s2, warm from K4c s0 900k, lr 1e-4, grf_lo 1.5 w 2.5 (5 ms), K4c terms otherwise
- Snapshots _snap/K5_s2_{100000,300000,400000,500000}. Harness JSONs stageJ_harness/K5_s2_{300000,400000}.json.
- 300k: 61.9 mph, spin 3060 (warn), launch 18.2 (warn), t/c 1.37 (only FAIL), GRF 1.38 PASS, smash 1.25 warn, order warn (thorax/arm same sample), pelvis timing warn.
- 400k: 65.4 mph, GRF PASS, spin 4036 FAIL, t/c 1.39 FAIL, order FAIL (pelvis/thorax).
- Running: K4c s0 (227376), K5 s2 (700k steps cap).

## K6 (2026-10-19 ~01:30 ET) — from K5 s2 700k (snapshot _snap/K5_s2_700000; 60.8 mph, 14/0/1, only t/c 1.36)
- K4c s0 stopped. stageK6 s3 (desc_w 6) and s4 (desc_w 3): lr 7e-5, spd_w 5, spin_hi 2800 w5, launch_hi 15.5 (margin), GRF/XF/order as K5. 700k steps cap.
- Note: golfphys needs ~70 mph for descent 28/t/c 1.27 with spin<3000, launch<=16; at 61-63 mph t/c ~1.36-1.38 is the physical floor, so K6 can only pass t/c by gaining speed.
- K6 interim (~400k): harness (stageJ_harness/K6_*.json): s4 200k = 64.5 mph, spin 2843, launch 13.6, only FAIL total/carry (1.43), 1 warn (pelvis peak speed 0.66x); s4 400k = 63.9 mph, spin 2939, launch 16.3 (warn), t/c 1.35 FAIL; s3 200k = 60.9 mph, spin 2779, t/c 1.44 FAIL. Snapshots _snap/K6_s{3,4}_*. Both runs alive (334331 s3, 334332 s4).

## K7 (2026-10-19 ~02:45 ET) — from K6 s4 200k (snapshot _snap/K6_s4_200000)
- Torque check (scripts/v5_torque_sat.py, 5 ms samples, 300 ms before impact, K6 s4 200k at 64.9 mph): wrists (5 N*m stock) saturated 32-68% of samples and at ~rated speed; shoulders/elbows (25 N*m) hit the cap intermittently (2-32%); waist_yaw peak 0.88 of 88 N*m, hips <=0.87, never saturated. => distal arm/wrist chain is torque-limited at ~65 mph; pelvis/hip/waist have headroom, so extra speed must come from the trunk/pelvis.
- stageK7 s5 (spd_w 5, pel_w 3, pel_t_w 2) and s6 (spd_w 7, pel_w 5, pel_t_w 3): new pelvis peak-speed term (toward 400 deg/s) + pelvis-peak 100-150 ms before club-peak term; speed curriculum T0 67 step 3; lr 7e-5; GRF 1.5/w2.5 fine, XF hard 65, order terms; spin<=2800, launch<=15.5. 800k cap.
- K7 interim: s6 400k (snapshot _snap/K7_s6_400000, harness stageJ_harness/K7_s6_400000.json) = FIRST 0-FAIL verdict (WARN): 11 pass / 4 warn / 0 fail, 24/24 contact, 65.8 mph, pelvis peak 301.5 deg/s PASS, order PASS, X-factor 57.5, GRF 1.33, launch 15.93; warns: pelvis timing 180 ms, smash 1.297, spin 3339, total/carry 1.347 (warn band). s6 300k: 14/0/1 (t/c fail), 62.4 mph, spin 2421 pass, pelvis timing 75 ms pass.
- Speed still plateaus at 62-66 mph across K4-K7 (curriculum T rose to 79 without median gain): consistent with the distal (wrist 5 N*m, shoulder 25 N*m) torque limit found by v5_torque_sat.py.

## K7 result (2026-10-19 ~03:15 ET) — reference-guided residual RL; not a realism pass
- Runs stageK7 s5/s6 ended normally at the 800k cap (not crashed). Snapshots _snap/K7_s{5,6}_{100..800}k.
- Harness (24 det eps, gate on): s6 800k = 12 pass / 3 warn / 0 fail, 66.5 mph, 24/24 (warns: pelvis timing 180 ms, spin 3473, t/c 1.343). s6 400k = 11/4/0, 65.8 mph. s6 300k 14/0/1 (t/c), s5 700k 13/1/1 (t/c 1.392), s6 600k 13/1/1 (t/c 1.393). No checkpoint >=67.5 mph; det median peaked 67.5 (s6 700k, spin 4731).
- Torque saturation (scripts/v5_torque_sat.py, s6 800k, 65.6 mph, 300 ms pre-impact, 5 ms samples): wrists (5 N*m) at the torque cap 48-72% of samples and at/above rated speed (qd/vmax up to 1.04; torque+speed use 0.92-1.00); shoulders (25 N*m) at cap 15-25%; elbows 0.90 peak; waist_yaw 0.89 of 88 N*m, hips <0.9, never at cap. Conclusion: distal arm/wrist chain is torque- and speed-saturated at ~65 mph under stock G1 limits; trunk/hips have some headroom but the policy cannot route it through the saturated wrists. 70+ mph is not reached with stock torque in this setup.

