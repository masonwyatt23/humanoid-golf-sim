# V19a plan (club-speed phase; PAUSED 2026-10-25 18:2x ET per Mason pause order)

> LOCAL / Trainer-only planning note. Grades below marked local are NOT official. cmd, watcher and launch files it names are not in this repo.

**Warm starts (snapshot dirs; ckpt base = dir/ckpt_N, vecnorm = ckpt_N_vecnorm.pkl, args.json alongside)**
- V18w_s661 100k: OFFICIAL best (scott-e aeed7260, 13/5/1, .958/.958/.875, plant 21/24; robustness t/c med 1.414, spin p90 4239 fail). Snapshot: <local-path>/results/v5_runs/_snap/V18w_s661_100000/ckpt_100000, keys stageV12X_ref_s1.
- V18s_s631 100k (LOCAL plant baseline): <local-path>/results/v5_runs/_snap/V18s_s631_100000/ckpt_100000.
- V18l_s590 50k (earlier official, plant baseline): <local-path>/results/v5_runs/_snap/V18l_s590_50000/ckpt_50000.

**Runs so far**
- V19a_s700 (warm V18s 100k, --spd_cur 3 from slow_lo 71, 2 workers, 200k): finished. Curriculum NEVER fired (train median 70.5 < 71). Local grades (official worker code @cb2d3683): all ckpts 11/6/1, club median 70.4-70.5 mph, triple 50k .917/.875/.833, 100k .875/.792/.792, 150k .917/.833/.833, 200k .875/.792/.792, t/c med 1.41, spin p90 4006-4206. Null. Latest ckpt: results/v5_runs/stageV19a_s700/ckpt_200000 (+ _vecnorm.pkl).
- V19c_s701 (= V19a retry: warm V18w 100k, slow_lo 70, 1 worker, nice 10): stopped by pause at ~28k steps, BEFORE first ckpt (50k) - **no checkpoint**. One promotion logged (step 28058, median 70.6, contact .915 -> slow_lo 73). Rerun from scratch.

**Speed-curriculum flag (train/v5_train_j.py, 951df2bd, default off)**
--spd_cur S (mph step; None = off), --spd_cur_c (train-episode contact floor, default .9), --spd_cur_max (default 120). Callback-side (not an env flag, so not in FLAG GUARD; inert unless set). Keeps a deque of the last 200 training-episode (contact, club_mph); every >=100 new episodes, if contact rate >= spd_cur_c and median contacted club mph >= current slow_lo, slow_lo += S on all envs (env_method). Logged to <run>/spd_cur.jsonl. Start slow_lo must be BELOW the current median (70.5) or it never fires (V19a).

**Relaunch command (V19a first; within 4-core cap: 2 workers + learner = 3 cores; run uptime first, golf 1-min load <= 5)**
`nice -n 10 $(cat results/v5_runs/v19c_cmd.txt | sed 's/^nice -n 10 //; s/--seed 701/--seed 702/; s/stageV19c/stageV19a2/')` - i.e. the V19c command (warm V18w 100k, --init_opt, slow_lo 70, --spd_cur 3 --spd_cur_c 0.9, 200k, h_every 50000) with --workers 1 if the refit is running, --workers 2 if alone. Grade 50k/100k/150k/200k one at a time afterwards (WATCH_EVAL_REPO=<local-path> WATCH_KS="50000 100000 150000 200000" scripts/v12_watch_er.sh stageV19a2, nice -n 10).
Watch the t/c and spin tails: speed must not worsen robustness t/c (V18w med 1.414) or spin p90 (4239).

**Speed-reference refit V12Sp (scripts/v12u_ref_fit.py V12S_* option, ce940872, default off)**
- State: results/v5_runs/stageV12Sp_ref_s1/fit_state.json (gen 5 of 30; best so far keys in tuned_keys_flat.json); cmd results/v5_runs/stageV12Sp_ref_s1/cmd.txt.
- Gens 0-4 PROXY (zero-residual reference, 48 noisy starts): noisy median club 70.2-70.9 mph (V12X 70.7), contact .86-.94, plant .86-.94. No speed gain yet.
- v7_ref_fit has no resume: relaunch = same cmd with --init results/v5_runs/stageV12Sp_ref_s1/tuned_keys_flat.json --gens 25 --out results/v5_runs/stageV12Sp2_ref_s1/fit_state.json, prefixed nice -n 10 (2 procs).
- **Gate for V19b:** train V19b (refit keys, warm V18w 100k, 100k steps) ONLY if proxy club speed >= +5 mph (>= 75.7 noisy median) with no proxy contact/plant loss vs V12X (holdout V12U_PID0=2100 V7_NS=48: contact .857, plant .816). Never concurrently with V19a.

**Why speed is capped (Trainer-local results/v19/baseline_speed.md, not in this repo pending a count relabel):** stock wrist torque-speed derate binds (L wrist yaw qd/vmax 1.15, 73% saturated); shortening t_down gives no speed (proxy). Gains must come from body rotation (pelvis 245 deg/s).
