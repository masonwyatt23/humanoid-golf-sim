# Validation of the model-only roll / AoA add-on against more published data

Written 2026-10-17 (America/New_York). **MODEL-ONLY / UNCALIBRATED**: this checks a Data-Agent heuristic (`data/roll_aoa_addon.py`) against published numbers. It is not a calibration and changes no add-on default. No Instagram-derived or Mason-clip data. Code `data/roll_aoa_validation.py`, data `data/references/roll_aoa_validation.json` (88 datapoints, each with URL and tag), tests `tests/test_roll_aoa_validation.py`.
Tags: **fetched** = page/PDF opened and read in full this session (PDFs via curl + pdftotext, pages via WebFetch); **snippet** = search-result excerpt/synthesis only. Residual = model - published; yards unless stated.

## 1. What was collected
| Set | n | Tag | URL (short) | Use |
|---|---|---|---|---|
| TrackMan Driver Fitting Charts 2010, CARRY and TOTAL optimizer, club 75-120 mph x AoA -5/0/+5 (carry, total, launch, spin, **dynamic loft**) | 60 rows | fetched | wishongolf.com/.../TrackMan-Driver-Optimization_2010.pdf | roll residuals, launch/spin/AoA checks (6 rows were already used by the add-on) |
| Foresight "Optimized Driver Launch Data", club 69-145 mph (ranges; midpoints used) | 12 rows | fetched | help.foresightsports.com/.../47208228295187 | roll residuals at 124-145 mph (replaces the 2 snippet pairs the add-on used) |
| R&A World-Long-Drive report Table 4, PGA-avg and LPGA-avg launch simulated (Volvik ball) | 2 pairs | fetched | assets.randa.org/.../R07 ... World Long Drive.pdf | residuals (simulation, not measurement); WLD mean carry 352 has no total |
| Andrew Rice / TrackMan chart, 65-105 mph, +5 AoA, "normal ground" | 7 | snippet | andrewricegolf.com/.../optimal-driver-numbers | residuals; spin assumed 2050 (stated range 1900-2200) |
| Tim Burke 141.3 mph, 1850 rpm, AoA ~+8 (page fetched; carry 380.6 / total 409.5 **only in a search synthesis**) | 1 | snippet | golf.com/.../long-drive-champ-golfer-trackman-numbers | residual (weak); launch unknown, 11 deg assumed |
| Golf Digest driver test 220.6 carry / 241.2 total (no speed/launch/spin) | 1 | snippet | golfdigest.com/.../fade-with-driver-draw-with-three-wood... | ratio sanity only, excluded from residuals |
| Landing-angle datapoints (TrackMan PGA avg 38 deg, 2023 PGA 39, 2023 LPGA 36, USGA "38-39", USGA/R&A ODS mean 37.6) | 5 | 2 fetched, 3 snippet | trackmangolf PDF, smashfactorlab.com, usga.org, R&A bounce report | `estimate_descent_deg` check |
| USGA/R&A "Proposed Bounce Model" report: 8 turf experiments (slope, intercept, roll at 39 deg), PGA ShotLink 2016-18 and 2007 fits, proposed linear model **roll = 79.1 - 1.6 x descent angle** | table | fetched | assets-us-01.kc-usercontent.com/.../Proposed Bounce Model ... .pdf | descent sensitivity, absolute roll, constant-yards finding |
| USGA "Golf Course Effects on Hitting Distance" (Broadie ShotLink firmness coefficients, 2018 moisture test) | table | fetched | usga.org/.../Golf-Course-Distance-Effects-Final.pdf | firmness check |
| TrackMan help: "Total is calculated ... flat surface, normal hardness" | - | fetched | support.trackmangolf.com/.../39727276786843 | caveat: TrackMan totals are model output |

Pairs: 83 carry/total pairs (74 fetched, 9 snippet) vs the add-on's 9 (7 fetched/2 snippet), of which 7 overlap; 82 are used in residuals. **Not found / not usable:** Arccos publishes total distance only (no carry, descent or speed split; snippet); Golf Digest has one pair; the Sackett PDF now returns 404 (its "1.5-2 yd per degree" stays an unverified snippet claim, and is superseded by the fetched USGA slopes below); peer-reviewed run-of-ball papers (Penner 2001 doi 10.1139/p02-035, Rho and Lee 2010) were seen as abstracts only, not read. Published roll **by firmness for drivers at 120+ mph does not exist** in anything I could open; firmness evidence is indirect (section 4).
Data-quality flags: TrackMan chart roll is non-monotone in several rows (e.g. carry-optimizer 100 mph 0 deg: 235/272 = roll 37 vs 24 neighbours; **120 mph +5 deg 310/350 = roll 40 vs 26 at 115 mph**; the "350 at 120 mph" headline is one of these). 8 rows flagged by a data-internal rule (roll > 8 yd from the median of the same optimizer and AoA); stats are reported with and without them (no material change). USGA report quotes the ShotLink mean at 39 deg as 22 yd in text but ~26.5 in a figure caption; both kept.

## 2. Roll residuals (model "normal" vs published; n = 82)
| Group | n | bias (roll yd) | MAE | RMSE | bias in total/carry |
|---|---|---|---|---|---|
| ALL | 82 | **-14.7** | 16.5 | 19.7 | -0.076 |
| TrackMan CARRY optimizer | 30 | -8.3 | 8.6 | 10.4 | -0.042 |
| TrackMan TOTAL optimizer | 30 | **-26.1** | 26.1 | 26.7 | -0.129 |
| Foresight midpoints (69-145 mph) | 12 | +1.0 | 7.6 | 9.4 | -0.009 |
| R&A simulations | 2 | +1.2 | 4.4 | 4.5 | +0.003 |
| Rice/TrackMan +5 AoA, low spin | 7 | -28.4 | 28.4 | 29.2 | -0.154 |
| Burke 141 mph (snippet, weak) | 1 | +14.2 | - | - | +0.037 |
| club 100-110 mph | 22 | -13.4 | 14.0 | 17.4 | -0.055 |
| club 115-120 mph | 13 | -7.5 | 10.3 | 13.3 | -0.027 |
| club >= 124 mph (Foresight x4, Burke) | 5 | **+10.2** | 10.2 | 11.6 | +0.027 |
| AoA -5 / 0 / +5 (TrackMan, no outliers) | 18/17/17 | -15.8 / -17.0 / -19.3 | | | |

Reading: the add-on is fine as a **normal-turf, tour-like** estimate (R&A, Foresight 97-131 mph, carry-optimizer within ~8 yd) but (a) **under-predicts low-spin / +AoA / total-optimized shots by 25-30 yd** (TrackMan 1636-2000 rpm rows have 42-58 yd of calculated roll; model gives ~30), and (b) **over-predicts at the highest speeds** because it scales roll with carry.
**Structural finding:** published roll is close to *constant yards*, not a fraction of carry. Regressing roll on carry gives slope 0.013 (Foresight, 69-145 mph, roll 21-32 yd), 0.019 (TrackMan carry-opt), 0.052 (total-opt, 42-58 yd) and -0.037 (Rice), versus the add-on's implicit ~0.09-0.12. The USGA/R&A experiments say the same: roll is set by landing angle (slope -0.74 to -2.45, median -1.7 yd/deg over 8 test sets; ShotLink -1.52; Quintavalla 2007 -1.24), largely independent of speed. The add-on's descent slope is -1.0 to -1.3 yd/deg for 250-325 yd carry (`roll_vs_descent`): inside the published range, slightly shallow (~0.3-0.5 yd/deg).
Absolute roll at 39 deg: published tests 15-37 yd (ShotLink 22-30); add-on 21.5-27.9 for 250-325 yd carry: inside. The USGA proposed linear model gives only 16.7 at 39 deg (the add-on is 5-11 yd above it).
Descent heuristic (3 snippet points): residuals 0.0 (anchor), -2.2 (PGA 2023), **+3.5 (LPGA 2023, wrong direction: it ignores speed)**. Too few points to refit; keep "prefer a simulated descent angle".

## 3. AoA / launch / spin relations (TrackMan chart, 60 rows, dynamic loft given per row)
- `tutelman_launch(AoA, DL - AoA)` vs chart launch: **bias +0.12 deg, MAE 0.30 deg, RMSE 0.35** (carry-opt +0.01/0.30; total-opt +0.24/0.29). **Supported.** An OLS on the chart gives launch = 0.07 + 0.16 x AoA + 0.84 x dynamic loft, i.e. +0.16 deg per AoA degree at fixed dynamic loft, matching the add-on's +0.14.
- **Env-formula spin (`env_spin_rpm`, spin_k = 130) vs chart spin at the chart's ball speed and launch: bias -897 rpm, MAE 1002, RMSE 1217** (carry-opt -1039, total-opt -756). The env formula produces ~1400-2000 rpm where published rows have 1600-3700. That is the env's own formula (copied, not mine), so it is a flag for the Trainer, not an add-on bug: `aoa_sensitivity` spin numbers inherit it.
- Chart-implied spin model: spin = 1.49 x ball_mph x (dynamic loft - AoA), RMSE 35 rpm on 60 rows (fits one chart; **unverified elsewhere**; a candidate diagnostic only).
- Empirical sensitivity at fixed club speed, AoA -5 to +5 (optimizer rows, dynamic loft also moves): launch +0.51-0.56 deg/deg, spin **-109 to -122 rpm/deg**, dynamic loft +0.41-0.47 deg/deg. The add-on's two bracketing cases (fixed dynamic loft +0.14 deg, +28 rpm; fixed spin loft +1.0 deg, +188 rpm) bracket the launch number (0.14 < 0.55 < 1.0) but **both have the opposite spin sign to the chart**, because in the chart a higher AoA comes with a lower delivered loft. Practical reading unchanged (AoA lowers spin only if delivered loft drops), now with numbers: about -0.3 deg dynamic loft per +1 deg AoA when optimizing.

## 4. Firmness (the only strata I could test)
TrackMan/Foresight/Rice totals are normal-hardness by definition (TrackMan help) or unspecified, so "normal" residuals above are the normal-firmness test. Firm and soft have no paired driver carry/total data; evidence is relative:
- Broadie ShotLink (fetched): vs firm fairways, medium -4.49 yd and soft -9.80 yd of tee-shot **total** distance (so soft vs medium -5.3, firm vs medium +4.5).
- USGA 2018 field test (fetched): +5-8% soil moisture cut bounce-and-roll 2-15 yd, average 5-10. Lehigh CC one fairway: roll at 39 deg 25 yd pre-irrigation, 15 post (ratio 0.6). Johnson 2008 five venues: roll 5-30 yd at 64 mph/36 deg/2250 rpm (R&A report, via the bounce paper).
- Add-on at carry 296 m, launch 10.4, spin 2400: soft -19 yd, firm +18, very_firm +30 vs normal. **Data-implied: soft about -5 (multiplier ~0.8, or 0.6 from Lehigh), firm about +4.5 (multiplier ~1.15).** The add-on's soft 0.35 and firm 1.6 / very_firm 2.0 are wider than the tour evidence; the venue spread (5-30 yd) shows real turf can span a wide range, so they are not falsified as extremes, but they are **not supported as typical** soft/firm values. Reference only: with firm=1.6 the add-on over-predicts Foresight by +16 yd (n = 12) and >=124 mph by +33.
Residual summary by firmness: normal: bias -14.7 overall, +1 on Foresight; firm (reference): bias -2.3 overall, +16 on Foresight, +33 at >=124 mph; soft/very_firm: no paired data.

## 5. Coefficient adjustments: none supported
A least-squares refit of (BASE_ROLL_FRAC, DESC_COEF, SPIN_COEF) on the TrackMan chart (52 non-outlier rows) gives 0.160 / 0.0241 / 0.000278 and cuts in-sample bias to -1.9 but **degrades held-out MAE from 14.2 to 20.0** (Foresight bias +1 -> +23, R&A +1 -> +19; Rice improves -28 -> -10). The chart's roll is TrackMan's own calculated value and is roughly constant yards, which a fraction-of-carry model cannot reproduce. So **no change to defaults** (separate-commit rule not triggered; add-on untouched). Candidate structural change, proposed not applied: model roll as constant-ish yards set by descent angle (USGA slope -1.6 yd/deg, normal-turf roll ~20-30 yd at 36-39 deg) with spin as a modifier, and log the env descent angle and landing speed so it can be used. Optional reference-only multipliers for reporting firm/soft bounds: soft 0.6-0.8, firm 1.15-1.3, with very_firm flagged unsupported.

## 6. Trainer-friendly confidence: "350 yd total at normal firmness" (model-only, uncalibrated)
Needed roll for 350 total: **29.6 yd at 293 m carry, 26.3 at 296 m, 23.0 at 299 m** (carry 320.4 / 323.7 / 327.0 yd).
Roll evidence at this operating point: Foresight 124-145 mph rows 25-32.5 yd (fetched, midpoints); Burke 141 mph 28.9 (snippet, weak); ShotLink tour mean at 39 deg 22-30; USGA/R&A linear model 26 yd at 33 deg, 23 at 35, 18 at 38, 15 at 40; add-on 32-33 yd; TrackMan total-optimizer 120 mph low-spin rows 50-58 yd (TrackMan-calculated, only for ~1650-2400 rpm and +5 deg AoA).
**Verdict: plausible, not established. At 296 m carry the central roll estimate (~26 +/- 6 yd) sits almost exactly on the 26.3 yd needed, so total ~ 350 +/- 8 yd, roughly a coin flip. 299 m carry: more likely than not. 293 m: less likely.** The earlier add-on table (353-360 yd, "margin to spare") is the optimistic end: its 32-33 yd roll is ~4 yd above Foresight at similar speed and ~9-15 yd above the USGA model at 36-38 deg. It becomes likely (>~55 yd roll cases, 380+) only if the shot truly lands flat (<~33 deg) with low spin (<~2000 rpm), as in TrackMan's total-optimizer rows. Confidence: **low-to-moderate**; carry itself (293-299 m) is the bigger lever (1 m carry = 1.1 yd total), and 350 yd of **carry** remains unsupported. The env does not report descent angle, firmness or landing speed, so the roll side is a prior, not a prediction; asking the env to log descent angle and landing speed would let the USGA linear model be a second, independent estimate. Foresight vs TrackMan/R&A carry disagreement at 130 mph (~20-40 yd) is untouched by this work.

## 7. Caveats
Foresight rows are range midpoints; Rice spin and Burke launch are assumed; TrackMan totals are calculated, flat, normal hardness; several sets are third-party transcriptions or snippets (tagged); residuals mix tour, long-drive and optimizer conditions; 130+ mph has only 5 points. Nothing here is a measurement of the humanoid or of Mason.
