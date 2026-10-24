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
| Ball speed to face edge | peak 2 mm above centre, lowest at both edges; spin DEcreases near bottom edge | measured, qualitative (figure not digitized) | R22-07 Fig 1-2 |
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
- Vertical spin: 51.3 rpm/mm x (ball mph/148), where 148 mph is the TrajectoWare MODEL ball speed in Tutelman's table (not measured). Both `spin_rpm_capped` (dz clamped to +/-12.7) and `spin_rpm_linear` (derived extrapolation) are returned; a spin check passes only if BOTH pass. The levelling-off is UNVERIFIED until R22-07 Fig 1/2 is read.
- Launch: centre + 0.20 deg/mm x dz. Smash: centre x (1 - 8.6e-5 dz^2), LOW confidence; a pass that comes only from this model does not count.

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
Hotstix data is secondary (Golf Magazine 2009 via Tutelman), one driver, no ball speed. MGS bands are coarse. R22-07 curve not digitized. Bulge/roll vary by brand and are rarely published.
