# V10i 100k: training-env strike dz == golfphys/harness dz (2026-10-24 ET)
Check: `scripts/v10_dz_check.py results/v5_runs/_snap/V10i_s101_100000/ckpt_100000`. It builds JEnv the way strike_log/diag_dz_terms do (harness-like, rsi 1/0/0) with dz_lin_w 45 / dz_tgt 0.0015 configured. It hooks env.v5_golf_env.shot_from_contact (the golfphys call the harness scores) and compares that dz with `info['dz']`, the value the dz_lin_w reward term reads.
Seeds 7000-7005 (deterministic policy, no start noise configured in this check):
| seed | golfphys dz (mm) | info['dz'] seen by reward (mm) |
|---|---|---|
| 7000-7005 (all) | -18.04 | -18.04 |
The harness nominal strike_dz_info for V10i 100k is -18.0 mm. So the dz term sees the true strike height with the correct sign and units, and the low-strike drift is not a measurement bug. Local check, not an official Evaluator result.
