# Harness v5 spec (opt-in, `--harness v5`) — Evaluator, 2026-10-25 ET

**Status: opt-in and NON-GATING.** Harness v4 (`eval/harness_v4.py`, `docs/HARNESS_V4_NOTES.md`) stays the gate for the first full pass.
A v5 run is the v4 run, with the same episodes and the same verdict (`r["verdict"]` is the v4 verdict). Extra rows go under `r["v5"]["rows"]`, and every one of them has `gating: false`.
Tested: on V10l_s104 100k (RO export 474e6c5), `--harness v5` reproduced the official v4 row check-for-check: 13/5/1 FAIL, robustness 0.83/0.75/0.67.

Code: `eval/harness_v5.py`; `eval/realism_check.py` (`--harness v5`, `--goal-spec`, `--club`, `--heldout-dr`, `--no-robust-info`);
`results/overnight/_j_worker_gp_v3.py` (optional `heldout` perturb key); `eval/topk_grade.py`; bands in `data/references/club_bands_v5.json`; tests in `tests/test_harness_v5.py`.

## (a) Task-accuracy metrics (goal-conditioned policies)

**Goal interface.** A goal is a dict. The harness takes the first one it finds, in this order:
1. the per-episode `ep["goal"]`, if the Trainer's worker logs the commanded goal;
2. `"goal"` in the run's `args.json`;
3. `--goal-spec` (a JSON string or file).

| key | meaning |
|---|---|
| `club` | `driver` \| `7iron` \| `wedge` |
| `target_carry_m` | > 0 |
| `target_dir_deg` | start line; + = world +y = left of the +x target line |
| `shape` | `straight` \| `draw` \| `fade` |
| `curve_m` | commanded \|bend\| at carry, in m |
| `handed` | `left` (default, the current LH model) \| `right` |

If no goal is found, all four task rows are reported as **`n/a (policy not goal-conditioned)`**. They are never scored as a fail.

**Per-episode values** come from the worker's `shot_extra`: `env_carry_m`, `azimuth_deg` and `env_lateral_m`.
- curvature `curve_y = lateral − carry·tan(azimuth)`, i.e. the bend away from the start line;
- golfer-frame bend `curve_draw = s·curve_y`, where s = +1 for a right-hander and −1 for a left-hander, so a positive value is a draw. ****Frame (confirmed by the Trainer 2026-10-25):** the sim world frame has +y = +azimuth = left of the target line (golfphys/impact.py face/path/HLA + left, sidespin/spin axis + draw; golfphys/sim.py `lateral_carry_m`; sim/golf_simulator.py `lateral_carry_yd` + left). v5 reads the WORLD-frame worker fields `shot_extra.azimuth_deg` / `env_lateral_m` (golfphys values from env.v5). Only if those are absent does it fall back to env/humanoid_golf_env.py `info['ball_lateral']` / `info['launch_direction']`, which are GOLFER frame (x hand_sign); it converts them explicitly (world = golfer x hand_sign, hand_sign +1 RH / -1 LH) and records `frame_source`. Draw/fade is a golfer-frame command: a LH draw curves to world right (-y), a LH fade to world left (+y). Every task row records `values.frame` and `values.shape_frame`.**
- carry error = carry − target, also given as a % of target;
- direction error = azimuth − target_dir;
- final lateral error = lateral − (target_carry·tan(target_dir) + commanded curve_y);
- shape OK:
  - straight: \|curve\| ≤ 5 m;
  - draw/fade: the sign matches the command and \|\|curve\| − curve_m\| ≤ max(2 m, 0.5·curve_m).

**Rows and thresholds.** All are provisional and held for counsel. The per-episode bands are listed below. Each row's status is the fraction of contact episodes passing: PASS ≥ 0.80, WARN ≥ 0.60, otherwise FAIL.

| row | per-episode pass / warn | source |
|---|---|---|
| `v5/task_carry_error` | ≤5% / ≤10% of target | assumption (ours) |
| `v5/task_direction_error` | ≤7° / ≤9° | reuses the v4 start-direction band (USGA/R&A R22-01) |
| `v5/task_lateral_error` | ≤7% / ≤10% of target carry | assumption (ours) |
| `v5/task_draw_fade` | shape OK (above); sign rate reported too | assumption (ours) |

## (b) Per-club bands (`data/references/club_bands_v5.json`)

**Revised 2026-10-25.** Per the PureGolf Data Agent, the TrackMan PGA and LPGA tour-average rows are **held pending counsel**. The goal-conditioned refs themselves are on main as 75a97112.
The numeric 7-iron and PW centres and widths that 1a98372 committed (taken from the TrackMan PGA PDF and Golf Monthly) are **withdrawn**. No harness band is built on the tour averages until counsel clears them.

| club | bands | status | v5 row |
|---|---|---|---|
| driver | **existing v3d/v4 driver bands, unchanged** (smash warn >1.49 / fail >1.50 / warn <1.30; launch pass 7-16 (warn 4-20); spin pass 2000-3700 (warn 1200-4000); land pass 30-48 (warn 25-55)) | sourced (realism_thresholds.json, harness_v3d) | `v5/club_driver_<metric>`, graded, NON-GATING |
| 7-iron | none committed | **pending counsel** (source pointer: Data Agent refs, 75a97112) | `v5/club_7iron_bands` = **n/a** |
| wedge (PW) | none committed | **pending counsel** | `v5/club_wedge_bands` = **n/a** |

The driver tour-average block, also TrackMan, is removed from the committed file. The driver bands themselves are unchanged.
When counsel clears the rows, the bands should come from the Data Agent refs. The LPGA rows may help bridge the speed gap.

Caveats carried from the Data Agent:
- One published tour-average smash value does not match its own ball/club speed ratio (flagged; values held pending counsel).
- There are no amateur-by-handicap iron/wedge data and nothing below about 70 mph (GAP). Any band for speed targets under 70 mph is **extrapolation** and must be labelled that way.
- The Shot Scope amateur figures (pending, 7b9faa3) are **total distance, not carry**. They must never be used as carry.

All club rows are non-gating. The loader rejects a pending-counsel club that carries numbers (tested).

**D-plane.** The Data Agent's D-plane functions are a MODEL from Tutelman 2007, after Jorgensen: spin axis from face-to-path and spin loft, centred strike, no gear effect.
They are **not wired in yet**. They need face angle, club path and spin loft at impact, and the worker does not log those yet; it logs face normal and club velocity only.
Once those are logged, v5 can add a non-gating "expected curvature sign from face-to-path" consistency row. For a left-handed golfer, mirror the lateral axis.
Until then, draw/fade is graded against the commanded `shape`/`curve_m` as in (a).

## (c) Held-out DR test sets

**Training DR (final).** Reference: main 3c7119db, `train/dr_goal.py` (`DR`, `SEED_MAX`), ported from Trainer a2c1c7a + 3d5f63e. DR is off unless `--dr` is set.

| parameter | training range |
|---|---|
| joint angle noise \|dq\| | 0-0.03 rad, or 0.05-0.06 rad (high band from curriculum stage 2, w.p. 0.2) |
| joint velocity noise \|dv\| | 0-0.06 rad/s, or 0.10-0.12 rad/s |
| floor μ | 0.63-1.07, or 0.45-0.54 / 1.16-1.25 |
| ball offset | N(0, 11 mm) per axis, capped at ±12 mm |
| slope | 0-7% grade on 50% of episodes |
| head mass | 190-210 g |
| loft | ±1.5° |
| segment masses | Clauser CVs (trunk 0.04, thigh 0.08, calf 0.08, foot 0.07), clipped at ±2 CV |
| torque | 0.90-1.00 × stock |
| latency | 20 ms (1 control step) on 25% of episodes |
| training env seeds | < 900000 (DREnv seed guard) |

These ranges are in `TRAINING_DR` in `eval/harness_v5.py`. `assert_disjoint()` treats every dimension as a list of intervals and counts touching intervals as overlap.

**Held-out set `v5-heldout-1`.** Every sampled component lies strictly outside its training range:

| parameter | held-out range |
|---|---|
| joint angle | \|dq\| ∈ [0.0325, 0.045] rad, random sign |
| joint velocity | \|dv\| ∈ [0.065, 0.09] rad/s |
| floor μ | ∈ [0.55, 0.62] ∪ [1.08, 1.15] |
| ball | \|dx\|, \|dy\| ∈ [13, 18] mm |
| seeds | 910000-910023, with rng `default_rng(seed + 0xD15C)` |

The seeds are disjoint from the harness's deterministic seeds (4000-4007, 8000-8007, 9000-9007) and from the v3/v4 robustness seeds (7000-7023).

`assert_disjoint()` raises an error on any range or seed overlap. `tests/test_harness_v5.py` covers the passing case and every overlap case.

The row `v5/heldout_dr_robustness` uses the same requirements as `mine/robustness` (contact ≥0.95, start direction ≥0.90, plant ≥0.90, shot p10/median/p90) and is NON-GATING.
The held-out μ band above 1.05 goes beyond the sourced turf range (0.7-1.05). It is a stress value, which is one reason the row does not gate.

**Disjointness re-check vs the final training DR (2026-10-25): PASS.** `v5-heldout-1` is unchanged.
Be aware that heldout-1 **joint noise (0.0325-0.045), velocity noise (0.065-0.09) and friction (0.55-0.62 / 1.08-1.15) now lie in the gaps BETWEEN training bands**. They are interpolation gaps, not extrapolation. Only the **ball offset (13-18 mm vs the 12 mm cap) is beyond** the training range. `gap_kind()` reports this, and it is tested.

**Held-out set `v5-heldout-2`** (OPT-IN with `--heldout2-dr 25`, NON-GATING; never part of the verdict. Ranges are UNSOURCED ESTIMATES (engineering choice) placed just outside the training DR; no TrackMan or counsel-pending values):
- Seeds 920000-920024, disjoint from training (< 900000), from heldout-1, and from the harness seeds.
- Episode i perturbs only `dims[i % 5]`, so each dimension gets 5 episodes. Joint, velocity and ball state noise stay nominal. The rng is `default_rng(seed + 0xD152)`.

| dim | held-out | how the worker applies it |
|---|---|---|
| slope_grade | 7.5-10% | gravity tilted at a random azimuth |
| torque_scale | 0.85-0.89 × stock | `e.tau` × scale |
| latency_steps | 2 (40 ms) | actions delayed 2 control steps (zeros first), as DREnv |
| loft_deg | \|1.6-2.5\|°, random sign | head geom rotated about +y, as DREnv |
| head_g | 185-189 or 211-215 g | club body mass/CoM/inertia at the head geom, as DREnv (swing dynamics only; golfphys head mass fixed) |

- Segment masses were added to heldout-2 later (see the segment-mass item below).
- All five dims are extrapolation (tested). Every overlap case and the seed guards are tested.

First heldout-2 run: V10l_s104 100k (RO export 474e6c5, v4 env, 1.5 in, 25 eps). Overall contact 0.80, start direction 0.80, plant 0.80.
By dimension: torque 5/5, latency 5/5, loft 5/5 and head mass 5/5 made contact; **slope 0/5**, with MuJoCo "QACC unstable" warnings on those episodes.
It is **not yet established** whether that comes from the policy (which was not trained with slope) or from tilting gravity after reset at address. Do not quote the slope result until this is checked.

First measured value: V10l_s104 100k (RO export 474e6c5, v4 env, 1.5 in tee) gave **contact 0.50, start direction 0.29, plant 0.08** on the held-out set. Robustness on the in-distribution gate for the same run was 0.83/0.75/0.67.

## (e) Goal-obs wiring (Trainer a2c1c7a, reference main 3c7119db)

- **Layout.** With `--goal_obs`, the obs is the 116-dim base plus a goal block at [116:124]:

  | index | content |
  |---|---|
  | 116 | driver |
  | 117 | 7-iron (always 0) |
  | 118 | PW (always 0) |
  | 119 | target carry m / 200 |
  | 120 | target direction deg / 10 (+ = left, world) |
  | 121 | shape (+1 draw / 0 straight / −1 fade) |
  | 122 | bend deg / 10 (spin-axis magnitude) |
  | 123 | handedness (+1 RH / −1 LH) |

  Only the driver is supported. The goal reward is off by default.
- **Pre-check (`_precheck_layout.py`).** It expects obs 116 + 8 = 124 when `args.json` has `goal_obs: true`, and 116 otherwise.
- **Worker (`_j_worker_gp_v3.py`).** For goal_obs runs only, it builds `train.dr_goal.DREnv` with `goal_obs=True` and DR off. Before each reset it calls `set_goal(V5_GOALS[i % n])` and logs `ep['goal']` plus the raw 8-float `goal_obs_block`.
  The reset calls `JEnv.reset` directly. With dr=False this is the same as `DREnv.reset` (a goal swap and then `JEnv.reset`), but it bypasses DREnv's *training* seed guard so evaluation and held-out seeds can run.
  Runs without goal_obs (every J/K/V run and stageDRa/DRb) take the unchanged JEnv path. Verified: V10l 100k `--harness v5` reproduced v4 13/5/1 and heldout-1 0.50/0.29/0.08 exactly.
- **Decoding.** v5 reads the goal from `ep['goal']` first (Trainer format, via `from_trainer_goal`), then run args, then `--goal-spec`, then the obs block (`decode_goal_obs`). In the mapping, `pw` becomes `wedge`, and `LH`/`RH` become `left`/`right`.
- **Fixed goal set `GOAL_SET_V5`.** Driver, LH. It is passed by `realism_check --harness v5` as `V5_GOALS` and cycled over episodes (carry m, dir °, shape, bend °):
  1. (130, 0, straight, 0)
  2. (110, 0, straight, 0)
  3. (150, 0, straight, 0)
  4. (130, +3, straight, 0)
  5. (130, −3, straight, 0)
  6. (130, 0, draw, 5)
  7. (130, 0, fade, 5)
  8. (130, +2, draw, 3)
- **Shape with a Trainer `bend`.** The sign comes from the world curvature mapped to the golfer frame (as in a6d0d91). The magnitude is the golfer-frame spin axis, atan2(sidespin, backspin) × hand_sign, compared with `bend`: within max(2°, 50%). This tolerance is an assumption (ours), provisional and held for counsel.
  When the goal has a bend but no curve in metres, the lateral error is measured against the start line (target_carry·tan(target_dir)).
- **Convention check.** The Trainer's `spin_axis_target_deg` mirrors the sign for LH, which matches our mapping: an LH draw has a negative world spin axis and curves to world right (tested for LH and RH draw and fade).
  D-plane start direction ≈ 0.85 × face. It is not graded, because the worker does not log face angle or path.
- **Sanity run.** None. No Trainer snapshot trained with `--goal_obs` exists yet (stageDRa_s201 and stageDRb_s202 have `goal_obs: false`).
  Instead, DREnv in the Trainer clone (whose `dr_goal.py` is identical to main 3c7119db) produced obs 124, and all 8 goals decoded exactly from obs[116:124].

## (d) Top-k checkpoint grading (`eval/topk_grade.py`)

**Stage 1, pre-screen.** This stage is not a grade and is never reported as one.
- v4 env, 1.5 in main row only;
- 8 deterministic episodes (seed block 4000) plus 8 robustness episodes (seeds 7000-7007);
- no wide/stress friction info rows (`--no-robust-info`);
- `--jobs` snapshots run concurrently (default 2), all under `taskset -c 0-1`.

Snapshots are ranked by min(robustness contact, start-direction and plant fractions), then by their sum, then by fewer v4 fails, then by more passes.

**Stage 2, full grade.** Only the top-k snapshots get the official rows: v4 1.5in main and v4 crown info, plus v3c/v3d with `--full-rows`.

**Measured timing** (box, cores 0-1, RO export 474e6c5, V10l_s104 snapshots):

| run | wall time |
|---|---|
| Before: official 4-row grade per snapshot (V12 batch log) | 162 s and 161 s |
| Before: v4 main row alone | 38-41 s |
| v4 main row run with `--harness v5` (adds 24 held-out episodes) | 48 s |
| Pre-screen, jobs 1 | 10.7 s per snapshot |
| Pre-screen, jobs 2 | 23.5 s for 4 snapshots, about 5.9 s per snapshot |

Example: 8 snapshots per 250k window take about 47 s to pre-screen at jobs 2. Full grading of the top 2 then takes about 324 s, so the total is about 6.2 min, against about 21.6 min to fully grade all 8.

Caveat: 8 robustness episodes give 1/8 resolution, so ties are common. V10l 100k and 150k tied in the pre-screen, and their official robustness was 0.83/0.75/0.67 vs 0.83/0.71/0.62. Use k ≥ 2.

Not done yet: one persistent process that loads the env once and swaps checkpoints. Today each snapshot loads its own worker process, which costs about 3 s.

## What the Trainer must provide
1. **Goal-obs layout.** The goal fields in the obs (indices and encoding), and the worker hook to set the commanded goal per episode and log it as `ep["goal"]` (keys above). The current HEAD obs is 116 with no goal.
2. **The heavy-DR training config.** Ranges for every randomised parameter, including any new ones (mass, actuator gains, latency, etc.), plus the seed scheme. Then `TRAINING_DR` and `HELDOUT_DR` get updated and re-tested.
3. **Lateral sign.** Confirmation of the `lateral_carry_m` / `azimuth_deg` sign (+y = left of target?) so the draw/fade sign is right for the LH model.
4. **Clubs.** 7-iron and wedge club models (length, loft, lie, head) if goal-conditioned clubs are trained. Iron/wedge bands are pending counsel, so those rows are n/a.
5. **Impact logging.** Face angle, club path and spin loft at impact, so the D-plane consistency row can be added.

## Relation to v4
- v4 code and its verdicts are unchanged, and the existing tests pass.
- `--harness v5` runs the v4 path, then calls `_apply_v5`.
- `--no-robust-info` is opt-in and used only by the pre-screen.
- The worker's `heldout` key is optional. Without it, the worker follows the v3/v4 code path byte-for-byte.

## (f) Trainer f253d5d answers (2026-10-25 ET; RO export of the Trainer box HEAD f253d5d)

- **Sidespin sign (Trainer-confirmed).** In the WORLD frame, positive sidespin / spin axis curves the ball toward +y (left), for either hand.
  A LH draw curves to −y and a LH fade to +y. `shot_geometry` and the bend/shape tests follow this (`test_sidespin_sign_world_left_regardless_of_hand`).
- **Impact logging and the D-plane row (`v5/dplane`, NON-GATING, info only).** With `--harness v5`, realism_check sets `V5_IMPACT_LOG=1`.
  The worker then rolls out in DREnv with `impact_log=True`, and only if the export's DREnv supports it; otherwise the row shows n/a.
  It records the WORLD-frame keys (+ = left) `impact_face_world_deg`, `impact_path_world_deg`, `impact_face_to_path_world_deg`, `impact_spin_loft_deg`, `impact_dloft_deg`, `impact_aoa_deg`, `impact_spin_axis_deg`, `impact_sidespin_rpm` on the contact step.
  - Grading (assumptions, ours): start direction (world azimuth) within 2° of 0.85 × face (world); curvature sign equals the spin-axis sign when |axis| ≥ 0.5° and |curve| ≥ 0.5 m.
  - The env's `face_yaw_deg`, `club_path_deg` and ep `face_path` are GOLFER frame (× hand_sign) and are never used here.
- **Segment mass (heldout-2).** Training: f = clip(1 + N(0, CV × breadth), 1 ± 2 CV), with inertia scaled by the same f, giving trunk 0.92–1.08, thigh/calf 0.84–1.16, foot 0.86–1.14.
  - Training CVs come from the Data Agent segment-mass rows committed in 75a97112 (`data/references/goalcond_club_shot_shape_dr_refs.csv`, single cadaver study). The held-out band placement is an UNSOURCED engineering estimate (≈2.5–3 SD, NON-GATING): trunk 0.88–0.90 or 1.10–1.12; thigh+calf (one factor) 0.76–0.80 or 1.20–1.24; foot 0.79–0.825 or 1.175–1.21.
  - Applied by the worker as mass and inertia × f on the Trainer's `train.dr_goal.SEG` bodies.
  - Heldout-2 is now 8 dims × 4 episodes, seeds 920000–920031. All dims are extrapolation, and the disjointness tests cover them.
- **Slope = modelling gap, info only.** Slope is applied as a gravity tilt while the address pose stays floor-perpendicular, so the golfer starts leaning about 4.6–5.7°.
  The Trainer found no reset bug; the QACC warnings come later, from the high DR bands.
  The slope episodes go to their own row, `v5/heldout2_slope_info`, labelled "modelling gap; partial plumb-address option exists on main (ea0b69da, configure(plumb_addr=True), effective only up to about 1% slope per the Trainer)", and are excluded from the heldout-2 aggregate.
  The Trainer reported plans to turn slope DR off in the next run.
- **Pipeline test.** `V10l_goal0_s104_100000` is V10l 100k with zero-padded goal inputs, so it IGNORES the goal (no goal training). This is a pipeline test on a goal-ignoring snapshot, not a grade.
  - Layout pre-check: LAYOUT_OK, obs 124.
  - Goals: `ep['goal']` was logged on all 24 episodes, covering all 8 goals.
  - v4: 13/5/1 FAIL with robustness 0.83/0.75/0.67, the same as V10l 100k.
  - Task pass rates: carry 0.125, direction 1.0, lateral 0.625, draw/fade 0.625 (expected for a goal-ignoring policy).
  - D-plane (n = 24): start within 2° of 0.85 × face 24/24; curvature sign matches the axis 24/24. Medians: face −4.6°, path −3.5°, start −2.7°, spin loft 17.2°, axis −8.0° (world).
  - Heldout-2 without slope (n = 28): contact, start direction and plant 0.71 each. Contact by dim: torque 4/4, latency 4/4, loft 4/4, head mass 3/4, trunk 2/4, thigh+calf 0/4, foot 3/4. Slope (info only) 0/4.
