# Driver face geometry + off-centre references, and a face-edge spec (Data Agent, 2026-10-24 ET)

Every row with URL, table/figure and label: `data/references/driver_face_offcentre_refs.{json,csv}`. Opt-in code: `data/driver_face_offcentre.py`.
No edits to golfphys/, env/, eval/, train/.

## Key numbers
| Quantity | Value | Label | Source |
|---|---|---|---|
| Face height | 53 mm (919THI), 50 mm (719MW); R22-07 test driver 53 mm | measured spec | Wishon spec tables; USGA/R&A R22-07 Sec 3 |
| Face width | 105 / 106 mm | measured spec | Wishon |
| Face area | 4800 mm2 (919THI) | measured spec | Wishon |
| Bulge | 13 in (Wishon x2), 11 in (R19 lab head); "11-13.5 in" modern high-COR | spec / lab / quote | Wishon; R19 4.2.1; Golf Digest (LA Golf quote) |
| Roll | 20 in (719MW), graduated (919THI), 10 in (R19 lab head); "12x12 or higher" typical 460cc | spec / lab / expert | Wishon; R19; Maltby |
| Spin vs height (100 mph robot) | 3165/2971/2564/2098/1862 rpm at -0.5/-0.25/0/+0.25/+0.5 in -> 51 rpm/mm | measured (secondary) / derived | Hotstix via Tutelman GE2 table |
| Launch vs height | 4.3/5.3/6.8/8.4/9.4 deg -> 0.20 deg/mm | measured / derived | same |
| Other VGE reports | 425 rpm per 0.5 in (Wishon, 105 mph) = 33 rpm/mm; 3300 rpm per 1.5 in (Upshaw) = 87 rpm/mm | reported, secondary | Tutelman launchOptimize |
| Smash centre / low / high (outside +/-4.5 mm) | 1.415 / 1.405 / 1.382 | measured means, derived ratio | MyGolfSpy vertical impact study |
| Ball speed to face edge | peak 2 mm above centre, lowest at both edges; spin DEcreases near bottom edge | derived from digitized figure, approximate (see R22-07 section) | R22-07 Fig 1-2 |
| Heel/toe distance loss | D = 12X^2 + 0.8X yd (MOI 4500, X in inches) | model (FE) | R19 Table 6 |

## golfphys vs data
| case | golfphys smash / spin / launch | data |
|---|---|---|
| 100 mph, DL 9.5, dz -12.7..+12.7 | spin slope 105 rpm/mm (3380 -> 723); launch 0.157 deg/mm; smash 1.479-1.488-1.459 | Hotstix 51 rpm/mm (range of reports 33-87); 0.20 deg/mm |
| 74 mph, DL 17.3, AoA +1, dz 0/-10/-15/-22/-25/-31 | 1.449/1.451/1.443/1.423/1.412/1.384; 2568/3336/3710/4210/4413/4792 rpm; 14.55/12.99/12.19/11.07/10.59/9.63 deg | no measured rows below -12.7 mm; -25/-31 mm are at/beyond a 53 mm face's bottom edge (-26.5) |
| toe/heel +/-15 mm (74 mph) | smash 1.407 (-2.9%), sidespin 450 rpm | R19 model: ~3 yd loss at 0.6 in for 4500 g cm2; robot Tables 4-5 not extracted |
Verdict: golfphys vertical gear effect is about 2x the measured Hotstix slope, never saturates, and keeps smash near 1.41-1.45 even
off the face; it has no face edge. Low strikes in the sim therefore gain spin they would not get and keep ball speed they would lose.

## Proposed face-edge spec (opt-in `face_edge_adjust`; SIDE-BY-SIDE scoring model only, never default; revised after Evaluator review of ec675dd)
- Input guard: only a golfphys CENTRE-strike result (`centre_dz_mm=0` or `y_high_m=0`) is accepted; otherwise ValueError (prevents double-counting gear effect).
- Gate: |dz| > 12.7 mm -> info (outside measured data); > 15 mm -> WARN; > 26.5 mm (or |dx| > 52.5) -> FAIL. Edge = measured spec, single brand (Wishon 919THI), provisional. `within_sim_box` reports |dz| <= 32 mm (sim's 64 mm box) as info.
- Vertical spin: 51.3 rpm/mm x (ball mph/148), where 148 mph is the TrajectoWare MODEL ball speed in Tutelman's table (not measured). Both `spin_rpm_capped` (dz clamped to +/-12.7) and `spin_rpm_linear` (derived extrapolation) are returned; a spin check passes only if BOTH pass. Levelling-off is supported by R22-07 Fig 2 (spin peaks near -15 mm, falls to -21) for one driver only.
- Launch: centre + 0.20 deg/mm x dz. Smash: R22-07 table (MEDIUM within -21..+21 mm, LOW beyond); the legacy MGS quadratic 1 - 8.6e-5 dz^2 is returned only for comparison (LOW). A pass that comes only from this model does not count.

| dz mm | status | smash | spin capped | spin linear (derived) | launch |
|---|---|---|---|---|---|
| 0 | measured_range | 1.449 | 2568 | 2568 | 14.55 |
| -10 | measured_range | 1.437 | 2940 | 2940 | 12.55 |
| -15 | info_outside_measured | 1.421 | 3040 | 3125 | 11.55 |
| -22 | warn | 1.389 | 3040 | 3385 | 10.15 |
| -25 | warn | 1.371 | 3040 | 3497 | 9.55 |
| -31 | fail (inside sim box) | - | - | - | - |
(74 mph, DL 17.3, AoA +1 centre result.)

Caveats: Hotstix launched ~7 deg at centre vs K30's 17.3 deg dynamic loft; Hotstix slopes are total-shot and already include face roll;
Wishon is a single brand; Tutelman's corrected model gives ~63 rpm/mm, which supports golfphys (105 rpm/mm) being ~2x too strong.

## Limits
Hotstix data is secondary (Golf Magazine 2009 via Tutelman), one driver, no ball speed. MGS bands are coarse. R22-07 constants are derived from a digitized figure (approximate, one driver); raw points held pending review. Bulge/roll vary by brand and are rarely published.

## R22-07 Figs 1-3: derived constants (derived from digitized figure, approximate; 2026-10-24 ET)
Source: R&A/USGA research report R22-07 'The effect of impact position on driving distance' (about 2022; header says 2006; cites the 2019 ODS; PDF dated Apr 2022). PDF obtained from the web.archive.org `id_` snapshot of the USGA URL (USGA itself returns Akamai 403). Figures are vector, so marker centres
were read from the PDF drawing commands (PyMuPDF) and axes calibrated linearly from tick-label positions. **The raw digitized point table is held locally pending counsel review (like the TrackMan 2010 chart rows) and is not in this repo;** only the derived constants below are published
(label 'derived from digitized figure, approximate'; est. +/-0.2 mph, +/-25 rpm, +/-0.3 mm). Face centre = 26.5 mm above the bottom of a 53 mm face; impacts at dz -21..+21 mm
(neutral tee -15..+21), one driver, robot ~115 mph, 6 shots per point. The ball-speed peak at dz +3 mm is real in all three series (report text: ~2 mm).

Ball speed vs centre (mean of series normalised to own max, then to dz 0): -21 0.936, -18 0.941, -15 0.948, -12 0.962, -9 0.976, -6 0.987, -3 0.994, 0 1, +3 1.001, +6 1.000, +9 0.991, +12 0.976, +15 0.963, +18 0.948, +21 0.925.
Model: piecewise-linear interpolation of that table (quadratic fit was rejected: RMSE 1.1 mph, max 3.0 mph, misses the flat top); below -21 mm extrapolate with the last segment (0.18 %/mm, derived).
0.59 mph (max 1.79) is the scatter of the individual tee series around the averaged table, not a fit error of a parametric curve; the 1-k*dz^2 fit gives 1.10 mph, so linear interpolation is kept.

| dz mm | old quadratic (MGS) | new R22-07 table |
|---|---|---|
| -10 | -0.9% | -2.7% |
| -15 | -1.9% | -5.0% |
| -22 | -4.2% | -6.5% (extrap. 1 mm) |
| -25 | -5.4% | -7.0% (extrap.) |
At 74 mph / centre smash 1.449 the new smash is 1.409 / 1.376 / 1.355 / 1.347. So a sim smash of ~1.35 at 22-25 mm low is CONSISTENT with R22-07;
what is unrealistic is any valid shot beyond the 26.5 mm face edge (e.g. -31 mm), which stays FAIL.

Spin (Fig 2): low strikes add +600 (-6), +852 (-12), +963 (-15, peak), then FALL to +539 at -21 mm; high strikes -1060 at +12 then recover near the crown.
This supports the levelling-off (now partly verified for one driver at 115 mph) and gives ~71 rpm/mm from 0 to -12 at 167 mph ball (~63 at 148), close to Tutelman's corrected model and below golfphys's ~105.
`face_edge_adjust` now returns `smash` (R22-07 table), `smash_legacy_quadratic`, and `spin_rpm_r2207` (Fig 2 delta x ball/167, inside -21..+21 only) alongside capped and linear spin.
Smash confidence: MEDIUM inside -21..+21 mm, LOW beyond. Suggest the Evaluator consider moving the "outside measured" info line from 12.7 to 21 mm for ball speed/spin (not changed here).

Output ranges: `smash` (R22-07) is None above +21 mm (no data) and extrapolates the last segment below -21 mm; `spin_rpm_r2207` is None beyond +/-21 mm.

Fig 3 launch (derived from digitized figure, approximate; raw points held locally, not in repo): slope 0.21 deg/mm over -12..+12 mm
(series: forward 0.216, intermediate 0.201, neutral 0.214), 0.26 deg/mm over 0..-12 mm, 0.28 deg/mm over -21..+21 (steepens near both edges;
neutral tee launches ~0.7 deg at -12/-15 mm). Consistent with Hotstix 0.20 and the Evaluator's rough 0.22-0.23 read.

### Fig 3 averaged launch-change table (derived from digitized figure, approximate)
`data/references/r2207_fig3_launch_delta_table.csv` (mean over tee series of launch minus that series' centre launch; n=2 at -18/-21 mm;
extraction script `data/extract_r2207_fig3.py`, local PDF only, not run in CI; raw per-series points held locally, counsel-pending):
-21: -7.46 | -18: -5.34 | -15: -4.25 | -12: -3.40 | -9: -1.54 | -6: -1.03 | -3: -0.62 | 0: +0.00 | 3: +0.60 | 6: +1.04 | 9: +1.48 | 12: +2.47 | 15: +3.16 | 18: +4.65 | 21: +7.45 (dz mm: deg).
`face_edge_adjust` now also returns `launch_deg_r2207` = centre launch + table (linear interpolation within +/-21 mm, None beyond);
MEDIUM, derived: one robot driver ~115 mph, launch change assumed speed-independent. `launch_deg` (Hotstix 0.20 deg/mm) stays the legacy output; defaults unchanged.
