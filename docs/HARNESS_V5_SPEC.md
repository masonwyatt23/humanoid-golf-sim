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
- golfer-frame bend `curve_draw = s·curve_y`, where s = +1 for a right-hander and −1 for a left-hander, so a positive value is a draw. **The sign convention must be confirmed by the Trainer against the env.**
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

## (c) Held-out DR test set

The **training DR** used here was read from the Trainer clone at box HEAD 4c3ad3d (`train/v5_train_j.py`, `results/v5_runs/v11o_cmd.txt` and the V9-V11 `args.json`):

| parameter | training range |
|---|---|
| joint angle noise | ±0.03 rad per actuated joint (`init_qn`) |
| joint velocity noise | ±0.06 rad/s (`init_qvn`) |
| floor μ | U(0.65, 1.05) (`fr_rand`) |
| ball xy | ±12 mm per axis (`ball_tol`) |

The env's Stage A `friction_rand` U(0.5, 1.2) is off in J runs. **Cross-check against the Data Agent DR rows (PENDING, 7b9faa3; cited as pending):**
- Langdown, Bridge & Li (Int J Golf Sci 2(1)) report skilled within-golfer stance-to-ball variability at address with SD 11.0 mm (single study). On that scale, training ball ±12 mm is about 1.1 SD and the held-out 13-18 mm is about 1.2-1.6 SD: plausible, and outside training.
- Penner 2002 ball-turf friction (0.25-0.4, green) is ball/green friction, not foot/floor, so it does not apply to floor μ.
- The driver DR rows (head mass 190-210 g from one supplier, lie 56-60, loft ±2) are not randomised in training today. They are candidate new DR dimensions.
- **No held-out range moved.** The set stays disjoint (asserted).

**This table must be re-checked against the Trainer's new heavy-DR config before any held-out number is quoted.** Update `TRAINING_DR` in `eval/harness_v5.py`; the disjointness test then re-checks it.

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

First measured value: V10l_s104 100k (RO export 474e6c5, v4 env, 1.5 in tee) gave **contact 0.50, start direction 0.29, plant 0.08** on the held-out set. Robustness on the in-distribution gate for the same run was 0.83/0.75/0.67.

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
