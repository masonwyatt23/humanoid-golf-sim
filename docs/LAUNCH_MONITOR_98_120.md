# Driver launch-monitor reference: 98 and 120 mph club speed

**Mason has no launch-monitor numbers yet.** His 120+ mph is self-reported and unverified. Everything below is published or model data, not a measurement of Mason.

Files: `data/references/launch_monitor_98_120_tables.json`, generator `data/launch_monitor_98_120.py` (imports `env/ball_flight_analytic.py` read-only, run in `<local-path>/golfvenv`), test `tests/test_launch_monitor_98_120.py`. Compared with `data/references/impact_physics_calibration.json` (R1/R2).

## Sources (fetched vs snippet)
| id | type | verification |
|---|---|---|
| TrackMan Driver Fitting Chart (carry and total optimizer, 75-120 mph, AoA -5/0/+5, 2010) https://wishongolf.com/wp-content/uploads/2012/07/TrackMan-Driver-Optimization_2010.pdf | vendor optimizer output (theoretical centre strikes) | **fetched** (PDF read) |
| TrackMan PGA Tour averages PDF https://support.trackmangolf.com/hc/en-us/article_attachments/7349802113051/PGA_Tour_average.pdf | vendor measured tour averages | **fetched** (driver row read) |
| Foresight Ball Launch Data reference tables https://help.foresightsports.com/hc/en-us/articles/47208228295187-Ball-Launch-Data-Performance-Reference-Tables | vendor reference tables | **fetched** |
| TrackMan blog "Combine" male-amateur averages (trackman.com/blog/what-is-club-speed, /ball-speed, /launch-angle, /spin-rate, /smash-factor) | vendor | **snippet only** - unverified; carry column via a synthesis |
| USGA TPX3006 overall-distance test (usga.org PDF; FAQ page) | governing body | **snippet only** - unverified (120 mph / 10 deg / 2520 rpm / ref ball 175 mph / 317 yd) |
| TrackMan 2023 tour averages (via the repo calibration file) | vendor | not re-fetched; snippet upstream |
Not found/not used: Golf Digest and Titleist fitting numbers (no usable table obtained), published research papers beyond Tutelman (snippet, earlier work).

## 98 mph (no published 98 mph row; interpolated)
| Source | Ball mph | Smash | Launch | Spin rpm | Carry yd |
|---|---|---|---|---|---|
| TrackMan carry optimizer, AoA 0 (linear 95->100) | 142.8 | 1.457 | 12.3 | 3116 | 229 (total ~261, weak) |
| TrackMan total optimizer, AoA 0 (linear) | 144.8 | 1.478 | 10.2 | 2568 | 223 (total ~272) |
| Foresight optimal table (interp 97->103) | 141.7 | 1.446 | 10-14 | 3083-2092 | 235-253 |
| TrackMan Combine amateur (interp 10 HCP 95 mph -> 5 HCP 101 mph; different groups, snippet) | 142.5 | 1.454 | 11.6 | 3090 | 214 |
Attack angle: optimizer dynamic loft 14.6 deg at AoA 0; at 100 mph AoA -5/+5 gives launch 9.6/14.9 deg, spin 3722/2538, carry 222/247 yd. Summary ranges in the JSON (carry-optimizer/Combine/tour-style rows only): smash 1.42-1.49, launch 11.2-12.4, spin ~2990-3120, carry 214-235. The total optimizer and Foresight windows are lower-spin (2570; 2092-3083).

## 120 mph (published rows; still above any measured average)
| Source | Ball mph | Smash | Launch | Spin rpm | Carry / total yd |
|---|---|---|---|---|---|
| TrackMan carry optimizer AoA 0 (dyn loft 11.0) | 178 | 1.483 | 9.3 | 2890 | 296 / 321 |
| same, AoA -5 | 176 | 1.467 | 6.1 | 3433 | 281 / 305 |
| same, AoA +5 | 179 | 1.492 | 12.6 | 2343 | 310 / 350 |
| TrackMan total optimizer AoA 0 | 179 | 1.492 | 7.7 | 2382 | 290 / 340 |
| Foresight optimal (interp 117->124) | 174.3 | 1.453 | 10-14 | 2757-1757 | 307-335 / 327-365 |
| USGA ball test condition (not an average) | 175 (ref) | 1.458 | 10 | 2520 | limit 317 total |
| Nearest measured: TrackMan PGA Tour 113 mph (AoA -1.3) | 167 | 1.48 | 10.9 | 2686 | 275 |
Foresight "faster swing" 1W: 112 mph, 165, 11.2 deg, 2685 rpm, 270 yd. 120 mph values are optimizer or test values, an extrapolation of measured data.

## Comparison with the env model (read-only run)
Conditions: TrackMan dynamic loft and AoA 0 (assumes dynamic loft = env face loft; unverified). Default = env file unchanged; patched = local copy with R1/R2 (K 5.6, e 0.845).
| | Target | Env default | Patched R1/R2 |
|---|---|---|---|
| 98 mph spin / launch / smash / carry | 3116 / 12.3 / 1.457 / 229 | 3523 / 11.7 / 1.442 / 211 | 2202 / 12.8 / 1.453 / 222 |
| 120 mph spin / launch / smash / carry | 2890 / 9.3 / 1.483 / 296 | 3270 / 8.9 / 1.462 / 276 | 2044 / 9.7 / 1.473 / 288 |

## Impact-model fix targets (recommendations; env/ untouched)
1. **Spin constant K (hard-coded 3.5 in `Jt=min(mu*Jn, M*vt/3.5)`; mu never binds):** the optimizer rows at 98 and 120 mph are both matched at **K ~3.96** (spin_scale ~0.88; default is 13% high). The earlier tour-point fit (K 5.6) gives only 0.71x of these rows. The two disagree because they assume different spin loft; fit on measured spin loft. Interim K 4.0-5.6; prefer ~4.0 for optimizer-consistent 98-120 mph work. Fitted to optimizer rows, not player data.
2. **Spin targets:** ~3100 rpm at 98 mph; ~2890 at 120 mph (2520 USGA, 2343 at AoA +5, 3433 at AoA -5).
3. **Smash cap:** published 1.45-1.49 (optimizer 1.46 at 100, 1.48 at 120; tour 1.48-1.49). Default 1.44-1.47 is fine; cap centre-strike smash at 1.49-1.50.
4. **Launch:** env is 0.4-0.6 deg below the table at equal dynamic loft; low priority until dynamic loft is measured.
5. **Carry:** default is 7-8% short; K patch alone leaves about -3%, so part of the gap is aerodynamics (Cd/Cl), not spin. Do not use carry as a spin diagnostic.

## Unverified list
TrackMan Combine amateur numbers and carry; USGA figures; 2023 tour averages; all interpolated 98 mph and 117-124 mph rows (linear, stated per row); Foresight method; dynamic loft = env loft assumption; K fits (two points from optimizer rows). Optimizer tables are 2010 and theoretical. Re-fit with Mason's own launch-monitor data when it exists.
