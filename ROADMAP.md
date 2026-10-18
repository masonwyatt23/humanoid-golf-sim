# ROADMAP

Highest-value next steps for the humanoid golf system:

1. **Unitree G1 / H1 model** — Replace the simplified humanoid with a real humanoid MJCF for better morphology match and eventual sim-to-real.
2. **WHAM / GVHMR reconstruction** — Swap MediaPipe for high-quality monocular 3D mesh recovery from PureGolf-style public swing videos.
3. **Curriculum training at scale** — Run the staged curriculum (contact → style → ball flight) for 500k–2M steps on GPU with many parallel environments.
4. **Ball spin and launch metrics** — Add clubface angle, path, and spin estimation so policies can be evaluated like Trackman data.
5. **Proper IK retargeting** — Map reconstructed human motion onto the humanoid with contact-aware optimization.
6. **Multi-style policies** — Train and compare Scott, Scheffler, and Rory styles side-by-side with the compare_styles script.
7. **Transfer to ashlrai org** — Move the repository into the AshlrAI GitHub organization once admin access is available.
8. **Real physics simulator** — Organise around simulator / training / evaluation (`docs/ARCHITECTURE.md`); close the validation gaps listed there (calibrated roll, impact/club-face validation, stock-actuator evidence).
9. **From-scratch swing training** — Stock `force_scale` 1.0, no scripted teacher, staged curriculum and honest gates (`docs/FROM_SCRATCH_TRAINING_PLAN.md`). Plan only; not started.

## Historical notes (commit 6bf1217; superseded)

- **cvel fix:** `ball_vel` was read from `data.cvel[ball][:3]` (the *angular* part of MuJoCo's `cvel`); it now uses `[3:6]` (linear velocity) in both the observation and the reward.
- Later reward changes (post-contact velocity bonus, stronger contact rewards) and the early "0.74 m carry / 100% contact" milestone predate the current evaluator and are not current results. Current numbers are in the README Status table and `results/leaderboard.md`.

## Status notes

- `data/process_video.py` exists (MediaPipe pipeline). WHAM/GVHMR extraction is still only documented in `docs/WHAM_GVHMR.md`, not implemented.
- `results/*.json` are committed (gate files, leaderboard, validation). Trained models (`models/*.zip`) are not committed and no Release exists.
- **Actuators:** every scripted and learned result so far (v3, imit3/5/9, v4 power tier) uses `force_scale` 2.0, i.e. hypothetical-strength actuators; no `force_scale` 1.0 re-evaluation is committed in the results files.
- Stage 20/21 (see README/CHANGELOG): imit15_dart_s53 passes 3 gate seeds (`force_scale` 2, script-distilled; s52's own JSON failed lateral, so DART stays seed-unreliable); a Mason-mapped-wrist script strikes with launch >= 10 deg but only about 88 mph / 58 m (`force_scale` 2); stock-motor imit16 about 98 mph / 74 m (one seed).
- Stage 22 (see CHANGELOG): imit18 power-tier (hypothetical, `force_scale` 2) passes 3 gate seeds but its distances are INFLATED (smash 1.5-1.6) until the `impact_model` gain is fixed; `ppo_bcreg` (first attempt at a non-script-distilled policy) was a regression; its gate JSONs and the imit18 gates are held pending review. Next: lateral/launch-aware reward, smash fix.
- Stage 23 (see CHANGELOG): imit18 at impact gain 1.28 is INFLATED; gain 1.20 (smash ~1.47, ~292-295 m, Trainer-reported, gate JSONs held) is the credible power-tier number. `ppo15_stoch_s71` (DART-then-PPO) regressed.
- Stage 19 (Trainer's finding, see README): the 'Mason-shaped wrist (key 0.88)' claim is VOID (lead-arm Mason values were used on trail-arm joints; 0.02 under the role-correct trail key). The Mason wrist target is not reproduced by any script that also strikes well (notes only).
- Stage 18 findings (see README): stock motors (`force_scale` 1) cost ~22 mph on the same scripted swing (notes only); full-elbow-range imitation is seed-unreliable (imit13_s52 fails); DART noise helps one seed (imit15). Next: a committed stock-motor learned result and multi-seed DART runs.
- The README Status table is the source of truth for results: Stage 6 scripted swing, Stage 8 yaw-only residual, Stage 9 hypothetical 128 mph tier, Stage 10 imitation annealing (script-free stage not yet reached), and the `sim/` simulator. Next steps there: confirm the gate constants with the Trainer/Evaluator (README "What 'PASS' means"), run the 0.25 and 0.0 script-weight stages with more seeds, and calibrate spin/contact against measured data.
