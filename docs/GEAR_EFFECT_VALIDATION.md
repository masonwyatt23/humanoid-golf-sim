# Off-centre (gear-effect / bulge-roll) validation of golfphys

Data: `data/references/gear_effect_measured_data.json` (URLs, read tags, caveats, exclusions).
Residuals: `data/references/gear_effect_validation.json` (script `scripts/gear_effect_validation.py`).
Model: golfphys@0c2bca2 coefficients, unchanged (bulge R 10 in, roll R 12 in, Tutelman 16.4 horizontal /
25 rpm/mph/in vertical gear effect, effective-mass ball-speed loss).

## Sources
| id | URL | read |
|---|---|---|
| Hot Stix 2009 (vertical, offsets in inches) | tutelman.com/golf/ballflight/gearEffect2.php ; collegeofgolf.keiseruniversity.edu/maxing-driver-distance/ | fetched_text |
| MyGolfSpy 2016 vertical (bins, offsets unknown) | mygolfspy.com/labs/mygolfspy-labs-the-impact-location-study/ | fetched_text + fetched_image (tables) |
| MyGolfSpy 2016 horizontal (bins) | mygolfspy.com/labs/mgs-labs-horizontal-impact-study/ | fetched_text + fetched_image |
| Golf Digest 2026 robot | golfdigest.com/story/drivers-2026-robotic-testing-data-gear-questions ; .../driver-analysis-robot-testing-mishit-locations | fetched_text (charts not read) |
| TrackMan blog | trackman.com/blog/club-data-definitions | fetched_text |
| TrackMan S10 fundamentals | troxhammargk.se/media/t4dn2xcy/trackman-s-10-fundamentals.pdf | snippet only |
| Upshaw (via Tutelman) | tutelman.com gearEffect2 | fetched_text, secondary quote |
The USGA PDF was Access Denied and R&A figures were not digitised; not used.

## Vertical, Hot Stix (offset known): baseline residuals (model - measured)
| offset in | dLaunch meas / model | spin meas / model | dDist meas / model total |
|---|---|---|---|
| -0.5 | 4.3 / 4.8 (dL residual +0.5) | 3165 / 3896 (+731) | -11 / -19.0 |
| -0.25 | 5.3 / 5.8 | 2971 / 3235 (+264) | -7 / -9.5 |
| 0 | 6.8 | 2564 | 0 |
| +0.25 | 8.4 / 7.8 | 2098 / 1900 (-198) | +6 / +7.0 |
| +0.5 | 9.4 / 8.7 | 1862 / 1259 (-603) | +10 / +10.7 |

Baseline RMS: launch 0.57 deg, spin 502 rpm, distance 4.2 yd. Model spin sensitivity is ~1.9x too high.
Leave-one-out fit (R_roll, gear_v): held-out RMS launch 0.24 deg, spin 114 rpm (vs 0.57 / 502 baseline).
All-offset fit: R_roll = 8.9 in, gear_v = 18.8 rpm/mph/in. Grid supports R_roll 9-10 in, gear_v 18-20.
Not applied to golfphys (the Trainer/Mason decide). Caveat: 5 points, one data set, one robot/driver.

## Vertical, MyGolfSpy (bins, offsets unknown) - consistency only
Measured high-bin: dLaunch +1.25, dSpin -481, dSmash -0.033; low-bin: -1.40, +432, -0.010. Offsets implied by
launch vs spin disagree under the baseline (about 9 mm vs 5-6 mm), and agree better after the Hot Stix fit (7 vs 12 mm
on one view). Centre shot: model smash 1.471 vs 1.415 measured (ball 151.5 vs 145.7 mph) and spin 2827 vs 2658:
the model centre is a little hot on this club/speed (not off-centre).

## Horizontal (MyGolfSpy bins)
Signs correct in 6/6 bin groups (toe -> draw spin axis, ball left; heel -> fade). Gear scale k (measured vs
model at the implied offset) = 0.95, range 0.72-1.29. Weak: bin offsets are unknown, so k is degenerate with
the offset. TrackMan geometry: model 10 mm toe -> 2.25 deg face open vs published ~2.0; low 10 mm -> 1.88 vs 2.0
(implied radius ~11.3 in): consistent.

## Not modelled / gaps
Heel/toe ball speed and carry asymmetry: the model gives toe = heel = -17.5 yd at 0.75 in (Golf Digest 95 mph driver
robot; the model centre carry only reaches 219.4 yd) while measured toe is about -5 and heel -12 to -15. The model
ball speed loss is symmetric in y. Upshaw secondary quote: model 1.5 in spin difference 3686 vs 3300 rpm
(delivery assumed). TrackMan smash pair 0.935 -> implied 23 mm (plausibility only, offset not stated).

## Verdict and confidence
- Vertical gear effect/roll: CAN be validated and calibrated: the leave-one-out hold-out confirms improvement
  (spin RMS 502 -> 114 rpm). Confidence moderate (single 5-point source).
- Horizontal gear/bulge: sign and geometry validated; magnitude NOT validated (offsets unknown). Low confidence.
- Heel/toe speed/carry asymmetry: gap, a model limitation, not calibratable from the data in hand.
- Needed to close: a per-shot impact-location dataset (face-sensor / impact tape) with ball data.
