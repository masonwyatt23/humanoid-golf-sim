# V12 official grading (Evaluator, 2026-10-25 ~12:15 AM ET)

This is the OFFICIAL grade. The Trainer's local numbers are not official.

**Checkpoints.** V10l_s104 100k and 150k. They were picked by the hourly watch as the new snapshots (V10f to V10n) with the best Trainer-local v4 robustness; the Trainer is also continuing V10o/V10p from V10l 100k (474e6c5). These are reference-guided residual policies with tracking assistance. The reference was re-tuned open-loop by CMA-ES, with stock G1 torque, warm-started (from V10e_s98 50k). Keys: stageV10h_ref_s1 (Trainer 8597c2f, V10h reference refit).

**Setup.** Harness v4 (`--harness v4`) on the env_v4 head (V3_HEAD=v4). The v4 address cross-check against V4_SPEC passed on all 8 rows (every run exited 0). The gating row is the 1.5 in tee. The crown 1.6 in row ('v4 head, 1.6 in crown tee (equator at sourced crown)') is INFO only. v3c and v3d at 1.5 in are kept for continuity.
- Read-only Trainer export 474e6c5 (HEAD at grading time; contains 8597c2f). No .py change versus 55fa733 (the V11 export).
- args.json: env_v4 true, tee_mode 1.5in, keys `results/v5_runs/stageV10h_ref_s1/tuned_keys_flat.json`.
- Keys md5 54aaa5312174ee1f68e17d382553492a, identical in the export and the Trainer HEAD.
- Layout pre-check: LAYOUT_OK on both (obs 116, act 29, 121 keys).
- Snapshot md5s: all MATCH (md5 record and batch script held locally with the raw results, not tracked).
- Worker: arm 0.6, club 1.15, 24 deterministic episodes, gate off, golfphys, robustness seeds 7000-7023, cores 0-1.

Derived bands are derived, not published. The club-speed p10 rule has low confidence. Izz 5600 is an n=1 manufacturer claim.

| ckpt | v4 1.5in (gating) | v4 crown16 INFO | v3c 1.5in | v3d 1.5in |
|---|---|---|---|---|
| V10l_s104 100k | 13/5/1 FAIL | 14/4/1 | 11/5/2 | 13/5/1 |
| V10l_s104 150k | 13/5/1 FAIL | 13/5/1 | 11/5/2 | 13/5/1 |

v4 1.5 in main row. Both checkpoints had 24/24 true contacts. Robustness is out of 24 perturbed episodes.

| | V10l 100k | V10l 150k |
|---|---|---|
| Fails | robustness | robustness |
| Warnings | kin. seq. order/timing, lead GRF, spin, total/carry | same |
| Peak pelvis (deg/s, floor 250) | 256.2 (pass) | 254.7 (pass) |
| Strike dz / dy nominal (mm) | -8.04 / 9.20 | -9.46 / 8.21 |
| Strike dz / dy noise median (mm) | -1.89 / 0.28 (n=20) | -4.37 / -1.14 (n=20) |
| Spin (rpm) | 3112 (warn) | 3202 (warn) |
| Launch (deg) | 13.35 | 12.86 |
| Club speed (mph) | 68.6 | 68.6 |
| Smash | 1.431 | 1.433 |
| Total/carry | 1.337 (warn) | 1.339 (warn) |
| Robustness contact / start dir / plant | 0.83 / 0.75 / 0.67 | 0.83 / 0.71 / 0.62 |
| Robustness club p10 / median (mph); t/c median, p90; spin p90 | 68.7 / 69.4; 1.40, 1.64; 4087 | 68.5 / 69.3; 1.42, 1.69; 4330 |

Robustness also flags the spin p90 and total/carry median and p90 as outside band. v3c additionally fails kinematic_sequence_order.

**Versus the Trainer's local claims.** The v4 1.5 in, crown and v3c rows are identical (counts and every check status; the robustness block matches exactly). The v3d row is +1 pass for both (13/5/1 vs 12/5/1) because the Trainer's v3d JSON omits `mine/strike_height`, the same cause as V10/V11.

**Full pass: none.** Neither checkpoint passes v4 harness + v4 head + 1.5 in tee with every check passing, robustness included. There is no render.
