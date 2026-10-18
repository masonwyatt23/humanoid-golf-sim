# Architecture: simulator, training, evaluation

Target organisation of the repo into three parts. **No existing file has been moved or renamed**; other clones and
cherry-picks depend on current paths. This page maps the existing paths onto the three parts. The packaging-level
restructure (a `src/` layout) is a separate, not-yet-done plan in the maintainers' notes.

## 1. The three parts

| Part | Role | Directory today |
|---|---|---|
| Simulator | Ball/club physics, launch and ball-flight models, course mode, validation suite | `sim/` (plus the physics-bearing files of `env/`, see below) |
| Training | Policy learning (scripted-residual PPO, imitation PPO; planned from-scratch effort) | `train/`, `imitation/` |
| Evaluation | Gates, leaderboard, dispersion, launch/smash reports, rendering | `eval/` |

Supporting directories: `env/` (MuJoCo environments and models), `data/` (reference-data pipeline), `configs/`
(scripted swing configs), `scripts/` (generators, smoke test), `results/` (committed result files), `tests/`.

## 2. Mapping of existing modules

### Simulator (`sim/` and physics in `env/`)
- `sim/golf_simulator.py`: launch-monitor style per-shot output from the analytic ball model (`shot_from_launch`, `shot_from_club`).
- `sim/validate_simulator.py`: checks the simulator against one published TrackMan PGA Tour driver row.
- `sim/course.py`: course-mode Monte Carlo on a synthetic course.
- `sim/launch_monitor_power.py`: launch-monitor report for the hypothetical power tier.
- `sim/dashboard.py`: builds `docs/dashboard.html` from committed results.
- `sim/validation/`: new, empty scaffold for a future validation suite (see section 3).
- Physics modules that live in `env/` today: `env/ball_flight_analytic.py` (analytic impact and flight model),
  `env/humanoid_golf_env.py` (MuJoCo contact, ball, impact model), `env/g1_golf_env.py` (actuator tiers), `env/models/*.xml`.
- Physics-related evaluation code that belongs conceptually to the simulator: `eval/flight_tracker.py`, `eval/validate_ball_model.py`,
  `eval/smash_anomaly.py`, `eval/smash_probe.py`, `eval/smash_probe2.py`, `eval/physics_probe.py`, `eval/strike_probe.py`.

### Training (`train/`, `imitation/`, scripted-swing envs)
- `train/train_residual.py`: residual PPO on a scripted swing (the current trainer).
- `train/train_ppo.py`: imitation PPO, style based. `train/train_all_styles.py`: loops it over styles.
- `imitation/reference_dataset.py`, `imitation/curriculum.py`: reference data and curriculum.
- `env/residual_golf_env.py`, `env/style_prior.py`: scripted swing plus residual and style-prior environments used by training.
- `scripts/auto_loop.py`: imitation annealing loop. Stage-search scripts in `eval/` (`param_search_s28.py`, `power_loft_scan_s25.py`,
  `klres_departure_s26.py`, `soft_departure_s27.py`) are training-side experiments that currently live in `eval/`.

### Evaluation (`eval/`)
- Gate and ranking: `eval/eval_gate.py`, `eval/dispersion_report.py`, `eval/leaderboard.py`, `eval/env_factory.py`, `eval/seed_summary.py`,
  `eval/gate_scripted_cfg.py`, `eval/eval_scripted_cfg.py`, `eval/strike_regime_rerun.py`.
- Reports: `eval/launch_report.py`, `eval/compare_styles.py`, `eval/style_match.py`, `eval/unified_style.py`.
- Rendering/export: `eval/render_showcase.py`, `eval/render_polished.py`, `eval/render_power_preview.py`, `eval/export_trajectory.py`.
- Ad-hoc diagnostics (several run on import, no `__main__` guard): `eval/scan_loft.py`, `eval/diag_launch.py`, `eval/outlier_diag.py`, `eval/shot_dist.py`.
- Known layering wart: `eval/eval_residual.py`, `eval/scan_cfg.py`, `eval/scan_loft.py` import `train.train_residual`.

## 3. Physics validation suite

What exists today (all against an analytic or MuJoCo ball model; none against measured launch-monitor data of this system):

| Concern | Real files |
|---|---|
| Analytic ball flight vs one published TrackMan PGA Tour row | `sim/validate_simulator.py`, results `results/golf_simulator_validation.{md,json}`, `tests/test_golf_simulator.py` |
| MuJoCo ball model vs analytic model | `eval/validate_ball_model.py`, `results/ball_model_validation.{md,json}`, `results/ball_flight_audit.md` |
| Smash factor / spin artifacts | `eval/smash_anomaly.py`, `results/smash_anomaly.md`, `eval/measure_sep_spin.py`, `results/ball_spin_measured.json`, smash gate in `eval/leaderboard.py` and `eval/launch_report.py` |
| Impact physics calibration | `tests/test_impact_physics_calibration.py`, `docs/research_impact_physics.md` |
| Flight tracking | `eval/flight_tracker.py`, `tests/test_flight_tracker.py` |
| Launch targets (speed/launch/spin ranges) | `docs/LAUNCH_MONITOR_98_120.md`, `docs/LAUNCH_TARGETS_120_132.md`, `tests/test_launch_monitor_98_120.py`, `tests/test_launch_targets_120_132.py`, `tests/test_launch_output.py` |
| Loft/env parameter dispersion | `tests/test_loft_env_params_dispersion.py` |
| Roll / total-vs-carry (model-only) | `docs/ROLL_AOA_ADDON_PROPOSAL.md`, `docs/RECOMMENDED_350YD_PARAMS.md` (uncalibrated roll, assumed total/carry ratio) |

### Gap list (not yet validated)
1. **No calibrated roll model.** Roll coefficients are model-only and uncalibrated; total distance relies on an assumed total/carry ratio.
2. **No club-face / impact model validation against launch-monitor data.** The impact model is checked against one published average row only; the simple impact model over-predicts backspin and carry error fails in `results/golf_simulator_validation.md`.
3. **`force_scale` 2.0 actuators are hypothetical.** Committed learned and scripted results use boosted actuators; power-tier results also depend on a hand-set impact gain and inflated smash.
4. **MuJoCo ball contact has a known smash artifact** (smash near 1.0 on boosted non-power rows); no restitution/compliance validation.
5. **Spin and drag coefficients are uncalibrated** for the MuJoCo ball; sidespin is largely absent, so dispersion is understated.
6. **Single benchmark row.** One TrackMan average row; no spread, no multiple clubs, no wind/altitude/turf.
7. **No automated test of `env/` physics** (contact, club-head kinematics) in `tests/`.
8. **No validation of actuator limits** against real humanoid hardware beyond documentation (`docs/research_humanoid_actuators.md`).

## 4. Where new work goes
- Physics checks: `sim/validation/` (new modules only; existing modules stay put until a coordinated move).
- From-scratch training: see `docs/FROM_SCRATCH_TRAINING_PLAN.md`.
- Evaluation of new policies: the existing `eval/` gate and leaderboard.
