# K24a_s53 200k: independent Evaluator score, harness v3b (scott-e default), gate off, arm 0.6, club 1.15, golfphys t/c

**Verdict: FAIL, 13 P / 4 W / 1 F.** The only FAIL is `mine/robustness`. The deterministic rows give 13 P / 4 W / 0 F, with 24/24 true contact and 0 fouls.

## Provenance
- **Checkpoint:** `results/v5_runs/_snap/K24a_s53_200000`, snapshotted to `_evalsnap/K24a_s53_200k` (gitignored). md5s:
  - `ckpt_200000.zip` 4c037b5d6e40460c4eacfcb14ebed3d0
  - `ckpt_200000_vecnorm.pkl` 1e1e7cdf7589d6172c8fc8a95691dc88
  - `args.json` 98ab460178db4754b80d771d9d2cc0f2
- **Env code:** read-only `git archive 7ae3e24` export at `<local-path>`.
  - Trainer HEAD has since moved to 31eb571, but `git diff 7ae3e24 HEAD -- env train golfphys` is empty; the newer commits only add harness JSONs.
  - The Trainer clone has uncommitted edits outside env/train/golfphys.
- **Layout:** obs 116 (env) = 116 (checkpoint) = 116 (vecnorm); action 29 = 29.
- **Ref keys:** `stageK22e_ref_s1/tuned_keys_flat.json`, md5 68b00781…, identical to the K22r5 export. 115 keys, 12 of them `pc|` keys.
- **V3_FRICTION_RANGE:** unset.
- **Run:** taskset 0-1, 2 workers, OMP/MKL 2.

## Deterministic rows (24 eps, seeds 4000/8000/9000 x 8)
| row | status | value |
|---|---|---|
| kinematic_sequence_order | PASS | peaks pelvis 1.196 < thorax 1.260 < arm 1.296 < club 1.308 s |
| kinematic_sequence_timing_ms_before_club_peak | WARN | pelvis 112, thorax 48, arm 12 ms |
| peak_speed_pelvis_deg_s | WARN | 165.2 |
| peak_speed_thorax_deg_s | PASS | 550.8 |
| peak_speed_arm_deg_s | PASS | 902.5 |
| peak_speed_club_deg_s | PASS | 1979.6 |
| x_factor_top_deg | PASS | 61.6 |
| grf_lead_vertical_bw (Butterworth 50 Hz, window top->impact+20 ms) | PASS | 1.333 BW (raw whole-episode INFO 1.927) |
| shot/smash | PASS | 1.426 |
| shot/club_speed_mph | PASS | 70.6 |
| shot/spin_rpm | WARN | 3798 |
| shot/launch_deg | PASS | 12.39 |
| shot/total_over_carry | WARN | 1.286 |
| shot/carry_vs_golfphys_yd | PASS | -0.2 |
| mine/segments_rotate | PASS | |
| mine/start_direction | PASS | azimuth 2.73 deg, 6.97 yd/100 yd |
| mine/lead_foot_plant | PASS | airborne 0, slip 0.69 cm (3.5%), turn 3.0 deg |
| skips | - | torque limits, pelvis torque, descent, weight shift, joint limits, torque saturation, tempo, trackman band |

**Shot:** ball 100.6 mph, carry 115.2 m, total 148.1 m (model), lateral 8.0 m, descent 24.3 deg, backspin 3784 rpm, sidespin +324 rpm.

## Robustness (seeds 7000..7023; joints U(+-1.5 deg), U(+-0.05 rad/s); ball U(+-1 cm))
Shot metrics are median / p10 / p90.

| | gate, mu U(0.9,1.1) | INFO, mu U(0.5,1.2) |
|---|---|---|
| status | **FAIL** | info (FAIL if it gated) |
| applied mu range | 0.910-1.075 | 0.581-1.173 |
| ball offset, abs max | 0.96 cm, 24/24 eps nonzero | 0.96 cm, 24/24 |
| contact | 1.000 | 0.875 |
| start-dir pass | 1.000 | 0.792 |
| foot pass | 1.000 | 0.875 |
| club mph | 70.31 / 45.63 / 70.64 | 70.41 / 46.83 / 70.63 |
| smash | 1.378 / 1.160 / 1.438 | 1.398 / 1.061 / 1.423 |
| launch | 10.81 / 7.95 / 12.66 | 10.97 / 8.87 / 13.07 |
| spin | 3451 / 1193 / 4376 (p10, p90 FAIL) | 3665 / 1122 / 4303 |
| t/c | 1.465 / 1.316 / 3.377 (median, p90 FAIL) | 1.385 / 1.331 / 3.055 |

## Artifact checks (probe, seed 4000, 8 identical episodes, 2 ms traces)
- **Contact:** 8/8, 0 fouls, club 70.6 mph.
- **Lead foot (right) planted:**
  - GRF is 0 at 1 of 150 samples in the last 300 ms (-146 ms).
  - Minimum 0.71 BW in the last 50 ms; 1.43 BW at contact.
  - Heel and toe rise at most 0.18 / 0.19 cm.
  - Post-impact peak 2.54 BW (re-contact, outside the window).
- **Direction is ball-derived:** golfphys launch azimuth 2.73 deg.
- **Strike:** face-to-path -1.04 deg, AoA -0.42 deg, dynamic loft 17.8 deg, sidespin +324 rpm. The worker does not log the impact offset for this env.
- **Trail foot (not gated):**
  - 0.00 BW at the first sample and 0.44 BW at the top.
  - Loaded (>0.05 BW) in 31% of samples from -300 to -130 ms (mean 0.17 BW).
  - Unloaded from -150 ms through impact.
- **Spin vs the Trainer's reward cap:**
  - The penalty is `spin_w * clip((spin - spin_hi)/spin_scale, 0, 1)` with spin_w 12, spin_hi 2600, scale 1000 (`train/v5_train_j.py:92`), so it saturates at 3600 rpm.
  - Nominal spin 3798 is past saturation: the penalty is pinned at its 12.0 maximum and gives no gradient at this spin.

## Differences from the Trainer's claims
1. **Nominal order, direction and foot PASS:** confirmed. All deterministic rows match the Trainer's v3 JSON exactly.
2. **Robustness FAIL on spin and t/c:** confirmed, but the numbers differ.
   - Trainer: spin median 3648, p90 4615; t/c median 1.49.
   - The Trainer's own JSON says 3646 / 4622 and t/c 1.531.
   - Mine: spin 3451 / 4376, t/c 1.465.
   - Cause: the Trainer's run used the v3 worker before the fix. K24's JEnv.reset() resets `env.ball_tol` to 0 (and `friction_rand` to False) on every reset, so **the Trainer's robustness runs had no ball perturbation** (all 24 ball offsets are 0.0).
   - **Their wide-friction info row was not wide either:** contact, start direction and foot all 1.00, versus my 0.875 / 0.792 / 0.875 at mu 0.58-1.17.
   - The gate friction itself was applied in their run (mu 0.910-1.075, matching mine), because the worker draws it after reset.
   - With the fix, spin p10 1193 also FAILs, which is not in the claim.
3. **The Trainer's other K24a JSON** (`K24a_s53_200000.json`): WARN 13/4/0, with the robustness rows skipped ("worker v5_eval_j_worker.py has no perturb support") and GRF 1.442, versus 1.333 with 2 ms traces. That file cannot support any gate verdict.
4. **Train on test:** K24a was trained with the gate's own perturbation family (`args.json`: fr_rand 0.9-1.1, ball_tol 0.012, init_qn 0.03 rad ~1.7 deg, init_qvn 0.06). It uses its own rng2, so the draws differ, but the distribution is close to the gate's. Its gate contact, start-dir and foot pass of 1.00 should be read in that light.
