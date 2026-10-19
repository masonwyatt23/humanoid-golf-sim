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


## K8 (2026-10-19 ~03:30 ET) — STOCK torque/speed limits only; reference-guided residual RL
- New open-loop CMA/ES re-tune (scripts/v5_ref_fit_k8.py): TUNED_KEYS deltas + t_down + per-kind downswing ease exponents (wrist = lag/release timing, hip, waist, shoulder, elbow; env/v5_ref.py "ease|<kind>|k" keys, backward compatible: old ref still 64.63 mph). Objective: legal strike mph (x3) + trunk power + pelvis lead 100-150 ms + wrist lag retained 80 ms pre-impact - wrist/shoulder saturation - wrist torque last 60 ms - XF>65 - GRF>1.5 (5 ms) - launch outside 10-15.5 - spin>3000.
- Result (results/v5_runs/stageK8_ref_s1/, 200 gens): open-loop 76.5 mph (vs 64.6 old ref), legal gate-on strike, XF 64.7, GRF 1.45 (5 ms), tilt 30, no fall. But launch 24.9 / spin 8919 (residual must fix), and the gain came from arm/shoulder keyframes, not trunk: trunk power ~537 W (unchanged), wrist saturation 0.49 (unchanged), wrist torque last 60 ms 0.39 (higher), ease exponents ~1.6 (lag/release timing barely moved). First run with mph weight 1 (stageK8_ref/) gave only 65-67 mph.
- Residual runs stageK8 s7 (T0 70) / s8 (T0 75), warm from K7 s6 800k policy (same obs/action layout, new ref), K7 reward terms, 800k cap.

- (03:30 ET) K8 runs restarted after ~1 min with pelvis-timing band 60-120 ms before club peak (harness band 40-140), pel_t_w 4.

## K8 interim (2026-10-19 ~04:30 ET) — stock limits, reference-guided residual on the K8 76.5 mph open-loop ref
- Det evals (500k): s7 76-77 mph, carry 99-127 m, descent 30-32, t/c 1.15-1.20, spin 4154-6596; s8 72-75 mph, spin 2919-5709, t/c 1.19-1.38.
- Harness (24 det eps, all 24/24 contact; JSONs stageJ_harness/K8_*.json, snapshots _snap/K8_s{7,8}_{100..500}k):
  s8 400k: 12 pass / 3 warn / 0 fail, 72.0 mph (warns: order arm=club same sample, pelvis timing 165 ms, spin 3792).
  s8 300k: 10/5/0, 73.1 mph (spin 3434, launch 16.06, t/c 1.278 warns).
  s7 500k: 12/2/1, 76.6 mph, t/c passes; fail spin 4154.
- First 70+ mph clean strikes under stock limits. Remaining: spin <3000, pelvis peak 165-175 ms (band 40-140), arm/club peak separation.


## K9 (2026-10-19 ~04:25 ET) — stock limits, reference-guided residual on K8 ref
- K8 final: no full pass at the 800k cap (Evaluator: zero-fail s8 300/400/600/700k, best s8 400k 12/3/0 at 72 mph; s7 500k 76.6 mph only spin fails). Snapshots _snap/K8_s{7,8}_{100..800}k.
- stageK9 s9 from K8 s8 400k (T0 72), s10 from K8 s7 500k (T0 76): spin_w 8 (hi 2700, scale 1000), centered-strike ctr_w 4, dynamic loft window 15-20, pelvis timing band 60-120 ms (pel_t_w 8), new sep_w 4 (arm peak >= ~5-20 ms before club peak), ord2_w 3, lr 5e-5, 600k cap.
- Tried a later-hip ease (k 2.2/3.0) in the open-loop ref: pelvis lead only 156->152/132 ms and 3.0 broke the strike (18 mph); not used.


## K9 result (2026-10-19 ~05:20 ET) — no full pass
- Both runs ended at the 600k cap; snapshots _snap/K9_s{9,10}_{100..600}k; harness stageJ_harness/K9_*.json.
- Best: K9 s9 300k = 12 pass / 3 warn / 0 fail, 71.8 mph, 24/24; spin 2956 now PASSES; warns: order (arm/club same sample), pelvis timing 160 ms, t/c 1.295.
- s10 (from K8 s7 500k, 74 mph): sep term pulled the arm peak far forward (arm before thorax) -> order FAIL at 100/400/500k (10-11 pass).
- Pelvis peak sits at t=1.475-1.485 s in every K7-K9 policy (160-175 ms before club) regardless of pel_t_w 3-8: it is set by the reference waist_yaw/hip phase; residual (0.7*0.2 rad) does not move it. Needs a reference-level change (pelvis keyframe/phase timing in the ES) rather than a reward.
- spin vs t/c still trade at ~72 mph (s9 600k 73.1 mph spin 3121 t/c 1.36; s10 400k spin 3182 t/c 1.26).


## K10 (2026-10-19 ~05:05 ET) — stock limits, reference-guided residual
- env/v5_ref.py: new "phase|<kind>|d" keys = per-kind downswing start delay (s); waist delay shifts the public X-factor phase curve (backward compatible: K8 ref still 76.5 mph).
- scripts/v5_ref_fit_k10.py (K8 fitter + phase|hip_yaw, phase|waist delays; pelvis lead 60-120 ms weight 10; arm-before-club soft term; speed<72 penalty), init K8 best.
- Ref stageK10_ref_s1 (200 gens): open-loop 79.6 mph legal strike, pelvis peak 116 ms before club (K8 ref 156), arm 12 ms before club (K8 4), XF 64.6, GRF 1.0 (5 ms), trunk power 659 W (K8 537); waist delay 45 ms, hip_yaw delay 5 ms. Launch 19.5 / spin 8750 open-loop. s2 ref: 79.4 mph, pelvis 136 ms, arm-club 20 ms.
- Residual runs stageK10 s11 (sep_w 1) / s12 (sep_w 2) warm from K9 s9 300k on the s1 ref, lr 5e-5, 600k cap, K9 terms otherwise.

- (05:20 ET) Evaluator: s11 200k 78.7 mph 10/5/0; all s12 (sep_w 2) fail order -> s12 stopped at 400k (moved to _stageK10_s12_stopped, snapshots _snap/K10_s12_*). New stageK10b s13 from K10 s11 200k: sep_w 0.5, ord2_w 4, desc_w 6 (t/c), lr 3e-5, T0 78, 400k cap.

## K10 result (2026-10-19 ~06:15 ET) — no full pass
- s11 (sep_w 1) ran to 600k (600k collapsed to 53.6 mph). s12 stopped at 400k. K10b s13 (from s11 200k, sep 0.5, ord2 4, desc 6) ran to 400k.
- Harness: K10b s13 400k 12 pass/2 warn/1 fail, 75.9 mph (fail spin 4836; t/c and GRF pass; warns order arm/club same sample, pelvis 150 ms). s13 300k 11/3/1 (spin 4395, GRF 1.74 warn), s13 100k 11/3/1 (spin 4651), s11 500k 10/3/2 (order, spin). Evaluator: s11 200k 10/5/0 at 78.7 mph (best zero-fail of K10).
- At 75-79 mph the policies get t/c <=1.25 (descent 26-29) but only with spin 3800-5700; spin<3000 checkpoints have t/c 1.3-1.6. Pelvis peak moved 165->145-150 ms (band 40-140) via the ref phase delay but not inside the band. Arm/club peaks remain on the same 5 ms sample.
- Overall best zero-fail: K9 s9 300k (12/3/0, 71.8 mph, spin pass) and K8 s8 400k (12/3/0, 72 mph).


## K11 (2026-10-19 ~06:25 ET) — stock limits, reference-guided residual
- scripts/v5_ref_fit_k11.py: K10 fitter + golfphys shot objectives in the open-loop ref (launch 11-15, spin 2200-2900, descent>=27, t/c<=1.22, smash), speed>=75 floor, arm >=10 ms before club; wider sigma on impact wrist/elbow/shoulder keys.
- First pass (uncapped speed, stageK11_ref_s*): ES chased speed (83 mph) with spin ~9000. Second pass with speed cap 78 and wider spin window (stageK11b_ref_s*, 300 gens from the first):
  s1 ref = open-loop 78.6 mph, launch 14.4, spin 3587, descent 28.1, t/c 1.23, smash 1.30, pelvis 96 ms before club, arm 84 ms before club, GRF 1.2 (5 ms), XF 62.9. (K10 ref: spin 8750, smash 0.90.)
- Residual: stageK11 s14 from K10 s11 200k, s15 from K9 s9 300k, on the K11b s1 ref; ord2 4, sep 0.5, desc 4, lr 5e-5, 500k cap.

- (06:15 ET) Per Evaluator: replaced s15 (K9 s9 300k start, ~2 min old) with stageK11 s16 from K10b s13 400k: spin_w 12, dynamic loft window 13-18 (w4), AoA >= +1, rest as s14.

## K11 result (2026-10-19 ~07:05 ET) — no full pass; stock limits, reference-guided residual
- Runs stageK11 s14 (from K10 s11 200k) and s16 (from K10b s13 400k; spin_w 12, dloft 13-18, AoA>=+1) ended at the 500k cap. Snapshots _snap/K11_s{14,16}_{100..500}k; harness stageJ_harness/K11_*.json.
- BEST: K11 s16 500k = 13 pass / 1 warn / 1 fail, 80.0 mph, 24/24 contact. ALL shot checks pass (det: spin 2884, launch 14.2, descent 30.1, t/c 1.21, smash 1.45), GRF passes, X-factor passes. Only FAIL: kinematic order — arm peaks (1.555 s) before thorax (1.600 s); warn pelvis timing 150 ms.
- s14 400k 12/2/1 at 82.7 mph (order fail, t/c 1.267 warn). s14 500k det 83.6 mph spin 4146.
- Cause: the K11b ref objective "arm >=10 ms before club" let the ES move the arm peak 84 ms before club, ahead of the thorax (open-loop thorax-arm -88 ms).
- Follow-up refs with explicit pelvis<thorax<arm<club order objective (K11_ORDER=1): stageK11c_ref_s1 = 78.3 mph, spin 2889, launch 14.6, t/c 1.26, pelvis 104 ms before club, thorax 20 ms before arm, but club peak 16 ms BEFORE arm in open loop; stageK11d_ref_s1 (arm-club weight 8) still -12 ms. No residual trained on these yet.


## K12 (2026-10-19 ~07:10 ET) — stock limits, reference-guided residual
- stageK12 s17 (K11c ref) and s18 (K11d ref), both from K11 s16 500k, K11 s16 shot terms (spin_w 12, dloft 13-18, AoA>=+1), ord2_w 6 (was 4), pelvis 60-120 ms, lr 3e-5, 400k cap.

