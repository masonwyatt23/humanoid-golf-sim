# golfphys validation report

2026-10-17 (America/New_York). Reproduce: `python -m golfphys.validate --write` -> `data/references/golfphys_validation.json` (all rows included). Data: `data/references/roll_aoa_validation.json` (88 points; TrackMan 2010 driver-fitting chart 60 rows *fetched*, Foresight table 12 midpoints *fetched*, R&A WLD report 2 simulated pairs *fetched*, Rice chart 7 rows *snippet*, Burke 1 *snippet*, landing-angle points). Residual = model - published; yards unless stated. **Caveat that matters:** the TrackMan chart rows are TrackMan's own calculated/optimized output (smooth, club speed 75-120 mph), so agreement with them shows consistency with TrackMan's model, not with field measurements. Foresight midpoints are ranges. No Mason or Instagram-derived data were used.

## 1. What was fit and what was held out
| Stage | Fit on | Held out |
|---|---|---|
| Impact (2 params e0, s_t) | 30 TM carry-optimizer rows (smash, launch, spin) | 30 TM total-optimizer rows; also fit club <=105 -> test 110-120 mph; also fit on total-opt -> test carry-opt |
| Aero (3 params) | 30 TM carry-opt carries + 3 snippet landing-angle anchors | TM total-opt carries, Foresight (12), R&A sim (2), Rice (7, snippet) |
| Bounce/roll (5 params) | TM carry-opt totals (30) + Foresight totals (12) | TM total-opt (30), Rice (7), R&A sim (2) |
| Firmness (1 param each) | one relative statistic (Broadie/ShotLink) | nothing available |

## 2. Impact residuals (model with measured club speed, dynamic loft, AoA)
| Set | n | smash bias / RMSE | launch bias / RMSE (deg) | spin bias / RMSE (rpm) |
|---|---|---|---|---|
| Uncalibrated defaults (e0 .845, s_t .62) | 60 | -0.008 / 0.008 | +0.42 / 0.43 | -826 / 844 (-30 %) |
| Fit: TM carry-opt | 30 | 0.000 / 0.003 | -0.24 / 0.25 | -57 / 60 (-1.8 %) |
| **Held out: TM total-opt** | 30 | -0.001 / 0.003 | -0.19 / 0.20 | -46 / 49 (-1.8 %) |
| Fit <=105 mph -> **test 110-120 mph** | 18 | +0.001 / 0.003 | -0.16 / 0.17 | -45 / 50 |
| Fit total-opt -> **test carry-opt** | 30 | +0.001 / 0.004 | -0.25 / 0.27 | -40 / 43 |
Parameters moved by < 0.5 % across these fits (e0 0.854-0.855, s_t 0.866-0.871): stable. Reading: the physical structure (loft/AoA -> spin loft -> tangential impulse) reproduces the chart's launch to 0.2 deg and spin to 2 %. Note the earlier validation found the env's spin formula 900 rpm low against the same rows; the uncalibrated `s_t = 0.62` (the research note's K = 5.6 equivalent) is 30 % low here because this model also lowers launch tangential speed, so do not combine the two. Smash is capped at about 1.49-1.50 by e0 and head mass (Burke 141 mph published ~1.50; Foresight midpoints 1.44-1.46; model centre hit 1.493 at every speed since `e` has no speed slope). **Foresight smash (1.45) and TrackMan chart smash (1.47-1.50) disagree**, model follows the chart.

## 3. Aerodynamic / carry residuals (ball speed, launch, spin given from the table; flight only)
| Group | role | n | bias | MAE | RMSE | range |
|---|---|---|---|---|---|---|
| TM carry-opt | fit | 30 | -0.5 | 0.8 | 1.2 | -3.2..+1.2 |
| TM total-opt | held out | 30 | +2.5 | 2.6 | 3.0 | -1.6..+5.3 |
| Rice/TrackMan +5 AoA (snippet) | held out | 7 | +0.3 | 3.2 | 4.4 | -10.2..+3.7 (65 mph row) |
| R&A simulation | held out | 2 | +4.4 | 4.4 | 4.8 | +2.5..+6.3 |
| **Foresight midpoints** | held out | 12 | **-22.1** | 22.1 | 22.9 | -33.0..-13.7 |
Uncalibrated shape models vs TM carry-opt: B&H-fit -14.6 yd bias, Smits-Smith secondary -19.4, env legacy -12.6 (all too short). Landing-angle check (3 snippet rows, FIT): 38.6 vs 38, 38.1 vs 39, 34.0 vs 36 deg. **Foresight vs TrackMan carry (flagged, unresolved):** a model calibrated to TrackMan is 14-33 yd shorter than the Foresight table, growing with speed (-26 yd at 124 mph, -30 at 131, -33 at 145: Foresight 357 yd carry at 131 mph vs model 327). The two sources cannot both be right for the same ball/conditions; no field data here decides it. Stratified: held-out groups below 100 mph RMSE 7.9 and 100-120 mph RMSE 8.7 (dominated by Foresight); >=124 mph (4 Foresight rows) bias -29.6.

## 4. Total / roll residuals (model chain from measured launch conditions)
| Group | role | n | total bias | total RMSE | roll bias | roll RMSE |
|---|---|---|---|---|---|---|
| TM carry-opt | fit | 30 | +5.3 | 7.5 | +5.9 | 7.7 |
| Foresight | fit | 12 | -9.3 | 15.2 | +12.8 | 14.2 |
| **TM total-opt** | held out | 30 | **-0.9** | **5.0** | -3.3 | 6.7 |
| Rice (snippet) | held out | 7 | -3.9 | 5.7 | -4.3 | 4.5 |
| R&A simulation | held out | 2 | +18.6 | 18.6 | +14.2 | 14.2 |
All 81 rows: total bias +0.4, MAE 6.3, RMSE 8.7. For comparison the earlier add-on had roll bias -14.7 and RMSE 19.7 on these data, **and failed on low-spin/high-AoA total-optimizer rows (-26 yd); this model's held-out total-opt roll bias is -3.3 yd**, because roll now depends on the simulated landing angle and speed. Remaining failures: the Foresight rows are not fit well (roll model +12.8 at 124-145 mph where Foresight roll is only 25-32 yd), and the R&A simulation (older USGA bounce model, 19-21 yd roll) is +14 yd. TrackMan roll is non-monotone in some rows, so the 8 flagged rows (roll > 8 yd from the median) limit what any smooth model can show.
**Roll vs descent** (grid over launch/spin at 120 mph club, descent 30-53 deg): model slope **-1.58 yd/deg**, inside the published -0.74..-2.45 (median -1.7; ShotLink -1.52; USGA proposed -1.6, *fetched*); roll 14-53 yd. Roll at 39 deg is 35 yd vs published 15-37 (ShotLink 22-30): high end. Constant-yards behaviour (21-32 yd at 120-145 mph) is only partly reproduced: the model produces 33-39 yd of roll at the 130 mph power cases (grid optimum), above the 21-32 yd published at 124-145 mph.
**Firmness:** reproduces its single target (soft -5.31, firm +4.49 yd) by construction; absolute firm/soft and the venue spread are not tested. The previous add-on's soft 0.35 / firm 1.6 multipliers are replaced.

## 5. Numerical checks
dt 0.02 / 0.01 / 0.005 / 0.002 s carry on one row: 231.158 / 231.160 / 231.161 / 231.162 yd. Vacuum range and apex match analytic within 1 % (test). Unit tests: 23, `pytest tests/test_golfphys.py`.

## 6. Calibrated vs assumption
Calibrated: e0, s_t, cd_scale, cl_scale, cd_spin_slope, normal-turf bounce set (lumped), firmness `a_roll`. Published (quoted): Ih/Iv, gear-effect rates (Tutelman GE3 fetched), spin decay 3.3-4 %/s (snippet), B&H Cl 0.54 S^0.4 (snippet, paper unread). Assumed: bulge/roll radii, Cd0(Re) shape and crisis, off-centre COR (none beyond effective mass), uniform-sphere ball inertia, ISA/15 C sea-level for chart conditions (**the chart conditions are not stated**; a 5 C or 300 m shift moves carry by several yards, which is within the Foresight gap's order of magnitude only for large shifts).

## 7. 350 yd at 130 mph (model output, uncertainty stated)
Grid (AoA 0..8, dynamic loft 8-19, spin >= 1500 rpm, centre strike, normal turf, sea level 15 C) with the TrackMan-calibrated chain:
| Club | best total (normal) | carry | AoA / dyn loft | launch / spin | firm / soft total |
|---|---|---|---|---|---|
| 120 mph | 352 yd | 311 | +8 / 14.0 | 13.0 / 1551 | 358 / 346 |
| 130 mph | 378 yd | 339 | +8 / 13.5 | 12.6 / 1541 | 383 / 372 |
| 132 mph | 382 yd | 344 | +8 / 13.5 | 12.6 / 1564 | 388 / 376 (firm optimum +6 / 11.5) |
The optimum sits at the grid edge (AoA +8, spin about 1500, i.e. long-drive style, smash 1.50), so it is an upper-end case, not a realistic target. A **moderate** case, 130 mph, AoA +4, dynamic loft 13.5 (launch 11.9, spin 2650, smash 1.49): carry 329, total 354 yd. Sensitivities on the 130 mph optimum: 1000 m altitude +18 yd carry; 30 C +8; 5 m/s tail +22 / head -26 yd. Implications: (a) **350 yd total at 130 mph is reachable in the model with a +4 deg AoA and about 11.5-12 deg launch; it needs roughly 325-330 yd carry plus 25-35 yd roll**, consistent with the earlier add-on conclusion (plausible, not established; the model's roll is on the high side at those speeds). (b) **350 yd carry is not reached** (best 339-344 yd) under TrackMan calibration; it becomes thinkable only if Foresight's carries are right (+30 yd at 131 mph), which is unresolved. (c) 8-12 deg launch targets in earlier notes stay in range; spin below ~1800 rpm is where the model gains most and where real-world stability and smash are least certain, and it relies on chart-extrapolated aero beyond 120 mph.

## 8. Not done / follow-ups
Kinematic-sequence and joint-torque reference for the Trainer is not in this deliverable (existing `docs/` speed-gap spec covers peak speeds). Needs data: off-centre launch-monitor strikes (gear/bulge), measured landing angle/speed for 120+ mph, firmness-stratified roll. Env integration (section 5 of the sim doc) is a proposal only.
