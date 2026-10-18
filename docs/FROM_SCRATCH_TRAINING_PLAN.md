# From-scratch swing training plan (PLAN ONLY, not started as code)

Status: no from-scratch policy exists in this repo. Every committed policy is scripted or script-distilled (see README,
'Status and honesty'). This page defines what a from-scratch effort must satisfy so its results are comparable and honest.

## Goals
1. **Stock actuators:** `force_scale` 1.0 (the environment default). No boosted actuators in any headline result.
2. **No scripted teacher:** no scripted swing in the action path, no script-distillation, no residual on a script, no reference
   trajectories copied from a script. Human mocap/reference tracking may be used only if declared, with licence status
   (CMU files stay `needs_counsel`; Instagram-derived data stays out).
3. **Physics first:** train only on a simulator whose gaps are listed in `docs/ARCHITECTURE.md` (section 3), and report which gaps apply.
4. **Honest labelling:** every result states actuator tier, seeds, teacher (none), and whether roll is modelled (currently not calibrated).

## Reward and curriculum stages (proposed)
| Stage | Objective | Notes |
|---|---|---|
| A. Posture/balance | Stable address, no falling, joint limits respected | No ball reward |
| B. Swing arc | Club-head speed along a swing plane, bounded torques | Reward speed and path, not distance |
| C. Contact | True club-ball contact, centred strike, positive attack/launch | Penalise flat-launch exploits |
| D. Ball flight | Carry and launch from the MuJoCo/analytic ball, lateral dispersion | Add smash-aware term so inflated smash earns nothing |
| E. Robustness | Stochastic policy, observation/action noise, several seeds | Report seed spread, not best seed |

Advance a stage only when its entry check passes on at least 3 training seeds.

## Acceptance gates
A from-scratch policy counts only if all hold:
- **Showcase criterion unchanged:** the existing criterion in `eval/leaderboard.py` (section 'Showcase qualification criterion' in `results/leaderboard.md`): 100% true contact in deterministic and stochastic mode, carry above the documented threshold, lateral std within the threshold, launch elevation above the minimum. Thresholds are read from the code, not re-defined here.
- **Honest smash/launch checks:** smash (ball mph / impact club mph) inside the leaderboard's smash gate (flagged rows cannot be best/showcase); launch and spin plausible per `eval/launch_report.py` and `sim/validate_simulator.py`.
- **Stock tier:** `force_scale` 1.0; the leaderboard row must show it.
- **Teacher check:** no scripted-action or script-distillation dependency; the training config documents this.
- **Seed reliability:** 3 gate seeds (4000/8000/9000) plus at least 3 training seeds, with results files committed (no private gate files).
- **Beats the script claim:** only if it statistically beats the scripted baseline on the same protocol; otherwise reported as a negative result.

## Non-goals
Power-tier (`force_scale` 2) numbers, 350 yd claims, or any distance claim not backed by a validated roll model.

## Scaffold
`sim/validation/` exists as an empty importable package (tested in `tests/test_sim_validation_package.py`). It changes no existing import.
