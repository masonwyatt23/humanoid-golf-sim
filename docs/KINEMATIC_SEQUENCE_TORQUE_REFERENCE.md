# Kinematic-sequence, joint-work/torque and GRF reference (published biomechanics only) + env feasibility

Status: **published-only, model-only above ~116 mph, unverified where tagged.** No Mason / Instagram-derived number appears here.
Data: `data/references/kinematic_sequence_torque_reference.json` (built by `scripts/gen_kinematic_sequence_torque_reference.py`); loader/helpers: `data/kinematic_sequence_torque_reference.py`; test: `tests/test_kinematic_sequence_torque_reference.py`. Builds on `docs/SPEED_GAP_100_120_SPEC.md` (same Cheetham fit is reused).

Tags. Read level: **F** full text/table read, **X** search excerpt of body text, **A** abstract only, **S** search summary only (unverified). Value level: *measured* (printed in source), *secondary* (printed in a review), *interp* (between published groups), *extrap* (beyond all groups), *derived* (computed here, assumptions stated).

## 1. Sources and what was actually read
| id | Source | Population | Tag |
|---|---|---|---|
| Cheetham 2008 | Science & Golf V ch.4 (year 2008 confirmed by Parker's reference list), http://www.waddengolfacademy.com/biomechanics/Cheetham%20Rose%20Neal%20Comparison_of_Kinematic_Sequence.pdf | 19 amateurs 88 mph, 19 tour pros 109 mph | F |
| Parker 2018 | Halmstad ms, https://www.diva-portal.org/smash/get/diva2:1242118/FULLTEXT01.pdf | 15 elite (10 M/5 F, hcp <= -2), CHS 46.0 m/s = 103 mph | F |
| Myers 2008 | J Sports Sci 26:181, https://exss.unc.edu/wp-content/uploads/sites/779/2013/01/Myers_jss_2008.pdf | 100 recreational (hcp 8.1), grouped by ball speed 55.7/65.6/75.4 m/s | F |
| Nesbit & Serrano 2005 | JSSM 4:520, https://www.jssm.org/volume04/iss4/cap/jssm-04-520.pdf | 4 amateurs, CHS 42.1-52.0 m/s (94-116 mph), single swings, model joint work | F |
| Nesbit 2005 | JSSM 4:499, https://www.jssm.org/volume04/iss4/cap/jssm-04-499.pdf | 84 M + 1 F amateurs; club-level torque/force/power | F |
| Hume, Keogh, Reid 2005 | Sports Med 35:429 (review), http://www.waddengolfacademy.com/biomechanics/Hume%20Keogh%20Role%20of%20golf_biomechanics.pdf | secondary data (Geisler, Barrentine, Milburn, McTeigue) | F (upgrades the earlier "snippet" tag) |
| Cheetham 2001 | X-factor stretch, https://www.philcheetham.com/wp-content/uploads/2011/11/Stretching-the-X-Factor-Paper.pdf | 10 skilled (8 pros + 1 long-drive champion + 1 collegiate) vs 9 hcp>=15, 5-iron | F |
| Tinmark 2007 | https://www.diva-portal.org/smash/get/diva2:25224/FULLTEXT01.pdf | 47 skilled (11 pro) | F (numbers only in figures) |
| Zheng 2008 a,b | https://doi.org/10.1055/s-2007-989229 ; https://pubmed.ncbi.nlm.nih.gov/18563677/ | 18 pros...; 25 PGA vs 25 LPGA | A |
| Worsfold 2007, 2008 | https://pmc.ncbi.nlm.nih.gov/articles/PMC3794489/ ; .../PMC3761900/ | natural-turf force plates, 24 golfers | A / X |
| Okuda 2010 | https://www.jssm.org/volume09/iss1/cap/jssm-09-127.pdf | 13 skilled vs 17 low skilled | X |
| Hirano 2023 | https://kokushikan.repo.nii.ac.jp/records/2000021 | 1 pro (case) | A |
| Han 2019 | https://www.tandfonline.com/doi/full/10.1080/14763141.2019.1586983 | 63 skilled; numeric value only via a secondary search summary | A + S |
| Sprigings & Neal 2000; Neal & Wilson 1985; Kwon 2013 | doi 10.1123/jab.16.4.356 ; 10.1123/ijsb.1.3.221 ; pubmed 24245049 | simulation / 6 / 18 skilled | **S** (primary not read) |
| Holt & Holt 2013 | https://www.golfsciencejournal.org/article/4958-long-driving-the-sadlowski-case.pdf | one long-drive champion, qualitative | F (no data; not used for numbers) |

Requested but **not retrieved in usable numeric form**: Lynn, Ball & Best (primary), Wallace/Koenig/Mann (primary; only the Hume-review statements), Ae, Hellstrom 2009, TPI numeric tables, Chu 2010 beyond its abstract, Kwon/Han long-drive studies (none found). **No numeric biomechanics for a measured 120+ mph (long-drive) population was found.**

## 2. Kinematic sequence: peak angular speeds (deg/s) by population
| Segment | Amateur (Cheetham, 88 mph) | Elite amateur (Parker, 103 mph) | Recreational low/mid/high ball speed (Myers) | Pro (Cheetham, 109 mph) | Pro (Hume/Geisler, secondary) | Pro (Zheng, CHS n/a) |
|---|---|---|---|---|---|---|
| Pelvis | 395 | 475 +-75 | 358 / 410 / 434 | 477 | 498 | - |
| Thorax / shoulder | 583 | 708 +-70 | 591 / 675 / 767 | 727 | 723 | - |
| Lead arm | 763 | 1055 +-149 | - | 980 | 1165 | - |
| Club | 1790 | - | - | 2254 | 2090 | 2413 +-442 (shaft) |
| Joint speeds (pro) | | | | | | R wrist 1183 +-299, L wrist 1085 +-338, R elbow ext 854 +-150 |

Definitions differ (resultant 3-axis vs transverse-plane yaw vs swing-plane), so rows are not pooled; Parker/Myers thorax and arm values sit above Cheetham's pros. Long-drive: **no data**. LPGA (Zheng): club 2049, wrists 864/816, elbow 705 (female pros, separate population).

**Timing** (before impact): pros pelvis 87 ms, thorax 68, arm 65, club 0 (Cheetham, measured); amateurs 78/59/64 (mean order pelvis, arm, thorax). Tinmark (n=47): order pelvis, upper torso, hand at every shot type, group and expertise, timing not significantly changed by group (figures only). Nesbit: joint work peaks distal to proximal (hips/spine first, wrists last), total body work peaks ~4 ms before impact, wrist torques cross zero before impact. Whether offsets change at 120+ mph: **not published**.

## 3. How things scale with club speed, 90 -> 132 mph (derived)
Segment peaks from the Cheetham two-group fit (`data/speed_gap_100_120.py`, k 0.88-1.17; Myers' within-group fit gives lower k: pelvis 0.64, thorax 0.86). Joint work = Nesbit scratch-golfer work x (v/52 m/s)^2.55 (least squares through 4 swings). Avg power = work / 0.23 s (elite downswing, Hume; held constant, assumption). Grip torque = linear fit through 4 Nesbit swings (1.83 N*m per m/s).
| CHS mph | Basis | Pelvis | Thorax | Lead arm | Club (deg/s) | Body work J | Avg power W: hips / spine / shoulders / elbows / wrists | Grip torque N*m | Club peak power W |
|---|---|---|---|---|---|---|---|---|---|
| 90 | extrap (below Nesbit range) | 403 | 597 | 783 | 1834 | 755 | 956 / 1399 / 271 / 334 / 203 | 21 | 1477 |
| 100 | interp | 442 | 665 | 886 | 2054 | 987 | 1250 / 1830 / 355 / 438 / 266 | 29 | 2195 |
| 110 | interp (Nesbit) / interp (Cheetham) | 481 | 734 | 991 | 2276 | 1259 | 1595 / 2334 / 452 / 558 / 339 | 37 | 3141 |
| 120 | **extrap** | 519 | 803 | 1097 | 2500 | 1572 | 1991 / 2914 / 565 / 697 / 424 | 45 | 4356 |
| 132 | **extrap** | 565 | 886 | 1226 | 2770 | 2005 | 2539 / 3716 / 720 / 889 / 540 | 55 | 6233 |
Take-aways: body work and power rise ~2.5x and ~3.8x per unit speed (CHS 100 -> 132 = x2.0 work, x2.8 club peak power), faster than segment speeds (x1.2-1.3). Core (hips + spine) carries ~70% of internal work at every skill level (Nesbit), shoulders + arms ~25%, legs ~4%, so the proximal joints are where a robot runs out first. Hume's review gives a different split for the *velocity contribution* (wrist 70%, shoulders 20%, spine 5%, hips 5%), a different metric. 90 mph is below every measured Nesbit swing.

## 4. X-factor and X-factor stretch
| Source | Population | X-factor at top (deg) | Stretch | Note |
|---|---|---|---|---|
| Parker 2018 | 15 elite | 54.9 +-7.9 | 2.9 +-3.4 deg | top X-factor **negatively** associated with CHS (beta -0.24); stretch positive (+0.27) |
| Myers 2008 | recreational by ball speed | 44.2 / 49.5 / 59.1 | max 45.6 / 51.7 / 61.8 (stretch 1.4 / 2.2 / 2.7 deg, derived) | max separation velocity 278 / 312 / 390 deg/s |
| Cheetham 2001 | skilled vs hcp>=15 | n.s. difference | 19% vs 13% (one skilled player 60.1 -> 73.5 deg) | 5-iron, 30 Hz, T3 sensor |
| Hume review | long vs short PGA hitters (McLean) | 38 vs 24 | | PGA 32, senior 29, amateur 34 (McTeigue); Burden amateur 70 |
| Kwon 2013 (S) | 18 skilled | method-dependent | | X-factor parameters not correlated with CHS |
Methods differ (stretch is ~1-3 deg in joint-coordinate studies vs ~10+ deg in Cheetham's sensor method); use X-factor 45-62 deg as the *range* a thorax-over-pelvis joint needs, and treat stretch as a small additive (a few deg), not a hard target. Env link: `chest_yaw` is +-45 deg in v3 (below the 55 deg elite mean and Myers' high group) and +-60 deg in v4_power (just enough); G1 `waist_yaw_joint` is +-150 deg.

## 5. Ground reaction forces and torque about the vertical axis (driver)
| Source | Population | Quantity | Value | Tag |
|---|---|---|---|---|
| Worsfold 2007 | 24 golfers, natural turf | peak vertical force back / front foot | 0.49 / 0.84 BW (range 0.33 / 0.83) | A, measured |
| Hume review (Barrentine 1994 etc.) | pros + amateurs, driver/5-iron | peak vertical / AP / ML | 1.6-2.0 / 0.4-0.6 / 0.2-0.3 BW (per foot or summed unclear) | F, secondary |
| Hume review | | lead leg 0.02 s after impact | 133 N lateral, 950 N vertical, 23 N*m torque | F, secondary |
| Han 2019 (S) | 63 skilled | lead-foot peak vertical, driver | 1.12 +-0.22 BW | **unverified** (summary) |
| Hirano 2023 | 1 pro | front-leg peak vertical | 1.51 BW | A (CHS unknown) |
| Okuda 2010 | skilled vs low skilled | lead-foot peak vertical | >1 BW both, no difference; skilled shift weight earlier | X |
| Hume review | elite | weight shift | 50-60% back foot at set-up, ~40% lead at top, transfer to lead foot in downswing | F, secondary |
| Worsfold 2008 / Barrentine via it | turf / PGA & low hcp | foot torque about vertical, driver | front Tzmax 17-19, back 6-7 N*m (turf); Barrentine back 17-18, front 23-26 N*m | X |
Estimates differ ~2x between studies (surface, shoe, "peak" definition), so no single GRF target is defensible. Derived sanity check (assumptions: stance width 0.45 m, BW 83 kg): a couple of opposing AP shear forces of 0.4-0.6 BW gives ~150-220 N*m about the vertical axis, plus 40-50 N*m of foot pivot torque. That is the same order as the ~290 N*m average hip torque implied by Nesbit's hip work (423 J over ~1.47 rad of pelvis turn; derived), so the `pelvis_yaw` stand-in needs roughly 150-300 N*m *average* at 100-116 mph. Neither number is a measured peak. Long-drive GRF: **no data** (Holt 2013 only asserts speed).

## 6. Joint work, torque and power (published)
* Nesbit & Serrano 2005 (F), scratch male, CHS 52.0 m/s: joint work J, top of backswing to impact: R/L hip 297/126, lumbar 342, thoracic 277, R/L shoulder 63/57, R/L elbow 125/23, R/L wrist 56/34, R/L knee 38/-4, R/L ankle 20/-2; total 1452 J (core 71.8%, arms 24.7%, legs 3.6%). Other subjects: 1429 J (49.7 m/s), 1105 (46.3), 878 (42.1, female). Club work 355 J, club KE 334 J, peak club power 3875 W (hcp5 3005, hcp13 2310, F18 1720). Efficiency 20-27%.
* Nesbit 2005 (F): club-grip torque (alpha, swing) max 42.1 N*m scratch, 36.8, 24.6, 24.0; n=84 table 30.9 +-9.2 N*m (22-40), beta 10.8, gamma 1.4; linear force 395 +-84 N. The text's n=84 statistics partly match the 4-subject subset ranges (ambiguous). Wrist torque is positive up to mid-downswing and crosses zero before impact, so the wrists are not driving at impact.
* Sprigings & Neal 2000 (S, unverified): simulation limits 180 N*m spine, 120 shoulder, 60 wrist; optimised wrist peak ~20-25 N*m; wrist torque worth ~9% CHS at 44 m/s (99 mph).
* Neal & Wilson 1985 (S): club-level only; **no hip/shoulder peak torque** retrieved.
* **Peak lumbar / hip / shoulder torque in N*m was not found in any retrieved source.** Only joint work (J) is published for them, so torque below is *derived* from work.

## 7. Env joints and actuator limits (read-only from `env/`)
| Body | G1 env (`env/g1_golf_env.py`, tier stock N*m @ rad/s / elite HYPOTHETICAL) | Simple env (`humanoid_golf_v3/_v4_power.xml`, N*m = forcerange x gear; no rated speed) |
|---|---|---|
| pelvis yaw | `pelvis_yaw` 176 @ 32 / 500 @ 45 (stand-in for 2 hips) | none (hips are pitch only: `right/left_hip_pitch` 250) |
| spine | `waist_yaw_joint` 88 @ 32 / 250 @ 45; `waist_roll/pitch` 50 @ 32 / 250 @ 45 | `chest_yaw` 120 (damping 1.0), range +-45 v3, +-60 v4 |
| shoulder | `*_shoulder_pitch/roll/yaw_joint` 25 @ 37 / 75 @ 55 each | `right_shoulder_pitch` 250, `right_shoulder_roll` 150, `left_shoulder_pitch` 150; `left_shoulder_roll` **unactuated** |
| elbow | `*_elbow_joint` 25 @ 37 / 75 @ 55 | `right_elbow` 120; `left_elbow` **unactuated** |
| wrist | `*_wrist_roll` 25 @ 37 / 30 @ 55; `*_wrist_pitch/yaw` 5 @ 22 / 30 @ 55 | `right_wrist` 60 (v3, damping 2.0), 120 (v4_power, damping 0.5), 25 (h12wrist); no left wrist |
| legs | rigid PD (no GRF realism) | hip 250, knee 200, ankle 80 pitch only |
Env arm roles: `right_*` is the trail arm and `left_*` the lead arm for both handednesses (`docs/HANDEDNESS.md`); the published "lead arm" speed target maps to `left_*`.

## 8. Feasibility check (derived; avg required power / max available power, > 1 = infeasible)
Required avg power = Nesbit work scaled to CHS / 0.23 s. Available = tau*w/4 (best point of the env's linear torque-speed derate), summed over the DOFs listed. Peak need is probably ~2.5x average (club model only), so ratios below understate difficulty.
| Group | G1 stock 100 | stock 120 | stock 132 | G1 elite 100 | elite 120 | elite 132 |
|---|---|---|---|---|---|---|
| Hips -> pelvis_yaw | 0.89 | **1.41** | **1.80** | 0.22 | 0.35 | 0.45 |
| Spine, waist yaw only | **2.60** | **4.14** | **5.28** | 0.65 | **1.04** | **1.32** |
| Spine, all 3 waist axes | **1.22** | **1.94** | **2.47** | 0.22 | 0.35 | 0.44 |
| Shoulders (3 DOF x 2) | 0.26 | 0.41 | 0.52 | 0.06 | 0.09 | 0.12 |
| Elbows (2) | 0.95 | **1.51** | **1.92** | 0.21 | 0.34 | 0.43 |
| Wrists, all 3 axes | 0.46 | 0.74 | 0.94 | 0.11 | 0.17 | 0.22 |
| Wrists, pitch only (club release axis) | **4.84** | **7.7** | **9.8** | 0.32 | 0.51 | 0.65 |
Speed check (rad/s; derived from extrapolated targets): at 120 mph pelvis 9.1, lead arm 19.1, relative wrist (club minus arm) 24.5, pro right wrist scaled to 120 mph ~22.7 (Zheng, assumes 109 mph for the Zheng pros). Rated speeds: stock pelvis/waist 32, shoulder/elbow 37, wrist pitch/yaw **22**, elite 45-55. So stock wrist pitch/yaw has **zero torque available** at ~24 rad/s; pelvis/shoulder speeds are fine.
Torque checks, simple env: required grip torque ~29 N*m at 100 mph, ~45 at 120, ~55 at 132 (derived/extrap). v3 wrist (60 N*m) clears 45 but its damping (2.0 N*m*s/rad) costs ~49 N*m of drag at 24.5 rad/s, leaving ~11 net at the fastest point; v4_power (120 N*m, damping 0.5) leaves ~108 net but is 2x Sprigings' 60 N*m human wrist limit (S), i.e. super-human. h12wrist (25 N*m) is below every grip-torque row. `chest_yaw` 120 N*m is 67% of Sprigings' 180 N*m spine figure (S); +-45 deg v3 range is short of the 55 deg elite X-factor.
**Findings.** (1) G1 *stock* can't do the core: hips (1.4x at 120 mph), waist (1.9-4.1x), elbows (1.5x) and especially the wrist release axis (7.7x power, and over the rated speed) fall short; shoulders are fine. (2) The *elite* hypothetical tier clears everything at 120 and 132 mph except waist-yaw-only (1.04 / 1.32x; fine if roll/pitch share the load) and is the minimum tier for a 120 mph story. (3) A realistic hardware envelope (docs/research_humanoid_actuators.md: H1-2 waist 200 N*m @ 23 rad/s, wrists 19-30 N*m) sits between stock and elite; expect <120 mph unless wrist and waist power are boosted. (4) All 120/132 rows rest on extrapolated work and the fixed 0.23 s downswing; the *direction* (core and wrist power are the bottleneck, shoulders are not) is robust across the Nesbit subjects.

## 9. Recommendations for the Trainer (reward / target use)
1. Targets by CHS: use section 3 segment peaks (public, speed-gap spec); treat >116 mph as extrapolated.
2. Add a pelvis_yaw average torque/power budget from section 8 rather than a GRF target; GRF numbers are too inconsistent. If a GRF diagnostic is wanted, log lead-leg vertical load in BW and expect 0.8-1.5 BW, transfer timing before lead-arm-parallel (Okuda).
3. Keep the sequence bonus (pelvis, thorax, arm, club with pelvis deceleration); do not penalise small X-factor stretch (1-3 deg in most studies).
4. Wrist: do not demand wrist torque at impact (published torque crosses zero before impact); budget ~30-45 N*m peak mid-downswing at 100-120 mph.
5. For torque-limited runs report the section 8 ratios per tier next to the results; label 120/132 as extrapolated.

## 10. Unverified / not found (explicit)
* Everything >116 mph (extrapolated); long-drive biomechanics (none found); Holt's >150 mph claim has no data.
* Peak joint torques (lumbar, hip, shoulder) in N*m; the hip torque quoted is derived from work and an assumed pelvis range.
* Work exponent 2.55 and 2.5x peak/avg power from four single swings; fixed 0.23 s downswing.
* Han 2019 1.12 BW, Sprigings & Neal limits and 9% effect, Neal & Wilson, Kwon 2013: search summaries only.
* Lynn, Ball & Best, Wallace/Koenig/Mann primary, Ae, Hellstrom 2009, TPI numeric: not retrieved. GRF magnitudes disagree ~2x across studies.
* Myers CHS estimates (ball speed / 1.45 smash) are an assumption; Myers did not measure CHS.
