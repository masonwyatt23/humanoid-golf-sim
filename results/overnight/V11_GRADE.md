# V11 official grading (Evaluator, 2026-10-24 ~11:40 PM ET)

This is the OFFICIAL grade. The Trainer's local numbers are not official.

**Checkpoints.** V10e_s98 100k and 50k, as requested by the Trainer. These are reference-guided residual policies with tracking assistance. The reference was re-tuned open-loop by CMA-ES, with stock G1 torque, warm-started (from V10a_s95 50k). The V10 keys (stageV10c_ref_s1, Trainer 9ba1b8f) come from a reference refit that adds a lead-foot slip/turn term on noisy starts, plus speed-consistency and pelvis terms (598d40c, 9ba1b8f).

**Setup.** Harness v4 (`--harness v4`) on the env_v4 head (V3_HEAD=v4). The v4 address cross-check against V4_SPEC passed on all 8 rows. The gating row is the 1.5 in tee. The crown 1.6 in row is INFO only. v3c and v3d at 1.5 in are kept for continuity.
- Read-only Trainer export 55fa733 (HEAD; contains 6d479b2, 9ba1b8f and 598d40c).
- The env/training code differs from f7cbc55 only by the V9_DEBUG print in `train/v5_train_j.py` make(). There is no v4 geometry change and no reward or obs layout change.
- Both args.json files have env_v4 true, tee_mode 1.5in and keys `results/v5_runs/stageV10c_ref_s1/tuned_keys_flat.json` (the same as v10e_cmd.txt).
- The keys md5 is 6f3ef762a46255ab90d1c1201a04ef4c. It is identical in the export, in the Trainer HEAD and at 9ba1b8f.
- Layout pre-check: LAYOUT_OK on both (obs 116, act 29, 121 keys).
- Snapshot md5s: all MATCH (md5 record and batch script held locally with the raw results, not tracked).
- Worker: arm 0.6, club 1.15, 24 deterministic episodes, gate off, golfphys, robustness seeds 7000-7023, cores 0-1.

Derived bands are derived, not published. The club-speed p10 rule has low confidence. Izz 5600 is an n=1 manufacturer claim.

| ckpt | v4 1.5in (gating) | v4 crown16 INFO | v3c 1.5in | v3d 1.5in |
|---|---|---|---|---|
| V10e_s98 100k | 13/5/1 FAIL | 13/5/1 | 11/5/2 | 13/5/1 |
| V10e_s98 50k | 13/5/1 FAIL | 12/6/1 | 12/4/2 | 13/5/1 |

v4 1.5 in main row. Both checkpoints had 24/24 true contacts. Robustness is out of 24 perturbed episodes.

| | V10e 100k | V10e 50k |
|---|---|---|
| Fails | robustness | robustness |
| Warnings | kin. seq. order/timing, lead GRF, spin, total/carry | kin. seq. order/timing, pelvis, lead GRF, total/carry |
| Peak pelvis (deg/s, floor 250) | 251.9 (pass) | 247.0 (warn) |
| Strike dz / dy nominal (mm) | -12.83 / 4.94 | -7.57 / 1.66 |
| Strike dz / dy noise median (mm) | -6.93 / -3.67 (n=20) | -1.07 / -2.92 (n=19) |
| Spin (rpm) | 3444 (warn) | 3000 |
| Launch (deg) | 13.39 | 13.45 |
| Club speed (mph) | 68.7 | 69.2 |
| Smash | 1.437 | 1.450 |
| Total/carry | 1.303 (warn) | 1.331 (warn) |
| Robustness contact / start dir / plant | 0.83 / 0.79 / 0.50 | 0.79 / 0.75 / 0.58 |
| Robustness club p10 / median (mph); t/c median, p90 | 68.7 / 69.3; 1.35, 1.64 | 68.8 / 69.4; 1.39, 1.73 |

Robustness also flags the spin p90 (4136 and 4143 rpm) and the total/carry p90 as outside the WARN band.

**Versus the Trainer's local claims.** The v4 1.5 in, crown and v3c rows are identical: counts, fails, warnings, robustness fractions, strike and shot values. The v3d row is +1 pass for both checkpoints (13/5/1 vs 12/5/1), because the Trainer's v3d JSON omits `mine/strike_height`, the same cause as in V10. The Trainer's message did not list the nominal spin warn (3444 rpm) on 100k.

**Full pass: none.** Neither checkpoint passes v4 harness + v4 head + 1.5 in tee with every check passing, robustness included. There is no render.
