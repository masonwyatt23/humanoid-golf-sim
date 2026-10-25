# Lead-foot turn margin (2026-10-25 04:15 ET). Local Evaluator 915348c, 1.5in, NOT official.
Nominal lead-foot turn comes from mine/lead_foot_plant in the *_v3d_tee15in_v4h.json files. The harness does not log a per-episode turn for noisy starts, so no noise-median turn is available from these JSONs.
In the hgs-v4 worktree I score with (eval/swing_realism.py), the warn thresholds are 60% of the fail limits: turn warn >12 deg (fail >20), slip warn >3 cm (fail >5 cm). A warn counts as a plant non-pass.
| recipe | ckpt | contact/start/plant | nominal turn (deg) | nominal slip (cm) |
|---|---|---|---|---|
| V10l 100k (reference point) | V10l_s104_100000 | .83/.75/.67 | 10.0 | 2.2 |
| (a) turn_m_w 3, tgt 6.5, warm V10l 100k, V10h keys | V12q 100k | .83/.67/.67 | 10.2 | 2.2 |
| (a) same, seed 193 | V12s 100k | .83/.79/.67 | 10.8 | 2.5 |
| (b) V12T keys (refit with harness-style plant, contact, start-dir terms; ref turn 6.5 nominal / 6.7 noisy-start median (in-sample refit proxy on the 48 fit draws, pid 0-47 since v8's scorer ignored V7_PID0; not held-out)), from zero residual, + turn_m_w | V12p 100k | .96/.75/.92 | 7.2 | 1.4 |
| (b) same, seed 192 | V12r 100k | .96/.75/.92 | 6.8 | 1.3 |
| (b) + dz_tgt -4 mm | V12y / V12z 100k | .92/.67-.71/.88 | 7.3 / 7.7 | 1.4 |
- The turn-margin penalty alone, warm from V10l, does not move nominal turn (~10 deg); the residual keeps the V10h-key foot pattern.
- The refit keys (V12T) do move it: turn 6.6-7.7, plant .88-.92, contact .92-.96. The remaining fails are nominal t/c (1.37-1.43 vs ~1.363) and robustness: start dir .67-.75, club p10 ~.8.
