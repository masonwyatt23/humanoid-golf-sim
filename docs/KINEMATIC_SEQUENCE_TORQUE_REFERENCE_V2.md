# Kinematic-sequence / torque / GRF / X-factor reference, v2 (open published sources only)

Extends `docs/KINEMATIC_SEQUENCE_TORQUE_REFERENCE.md` (v1, branch `kseq-reference` b78e5eb). Data: `data/references/kinematic_sequence_torque_reference_v2.json` (built by `scripts/gen_kinematic_sequence_torque_reference_v2.py`); test: `tests/test_kinematic_sequence_torque_reference_v2.py`. No unpublished, private-clip or video-derived number is used. Only open-access PDFs/pages and public abstracts were read; nothing was fetched around a paywall.

**Read tags** (every datapoint in the JSON carries one): **fetched-full** = full text/tables read; **abstract** = abstract/landing page only; **snippet** = search-engine summary only (unverified, do not rely on it); **n/a** = searched, nothing found. **Value level**: measured, secondary (quoted in another fetched paper), model (simulation output), derived (computed here, assumptions stated).

Counts: 75 JSON entries = 62 fetched-full, 4 abstract, 6 snippet, 2 explicit "n/a" gap rows, 1 carried-over v1 row (72 are new data entries; 13 of the fetched-full ones are Foxworth hip torques/conversion).

## 1. New sources (what was actually read)
| id | Source / population / n / club speed | Tag |
|---|---|---|
| Madrid 2020 | MDPI Appl Sci 10:5728, https://www.mdpi.com/2076-3417/10/17/5728; 66 skilled males hcp<=3, driver CHS **110.4+-4.8 mph** | fetched-full (Tables 1-4) |
| Ichikawa 2024 | JHSE 19:874, https://www.jhse.es/index.php/jhse/article/download/analysis-long-drive-distance-golf-player/36; **one** long-drive pro, 106 kg, CHS **137 mph**, 30 drives | fetched-full |
| R&A WLD 2019 | https://assets.randa.org/...R07 - Analysis of Trackman data gathered at World Long Drive.pdf; 304 men, CHS 145 mph (launch data only) | fetched-full |
| Meister 2011 | J Appl Biomech 27:242, waddengolfacademy.com PDF; 10 pro + 5 amateur males, **5-iron**, 61-79 mph | fetched-full |
| Bourgain 2020 | MDPI Proceedings 49:45, https://www.mdpi.com/2504-3900/49/1/45; 9 pros (108.5 mph) + 19 amateurs (90.6 mph), driver | fetched-full |
| Okuda 2010 | JSSM 9:127, jssm.org PDF; 13 skilled + 17 low-skilled, driver, vertical GRF | fetched-full |
| Worsfold 2007/2008 | PMC3794489, PMC3761900; 24 golfers, natural turf | fetched-full |
| Foxworth 2013 | JOSPT 43:660, https://www.jospt.org/doi/10.2519/jospt.2013.4417; 20 male amateurs, driver 89-94 mph | fetched-full |
| Okamoto (ISBS) | https://commons.nmu.edu/cgi/viewcontent.cgi?article=1254&context=isbs; 3 pros, 102 mph | fetched-full |
| Sprigings & Neal 2000 | simulation; scanned PDF read as page images (no text layer); torque curves read from a figure (+-5 N*m) | fetched-full (model) |
| Lynn 2013 | Int J Golf Sci 2:116 (open PDF); 15 elite + 14 recreational, 5-iron | fetched-full |
| Callaway 2012 | PMC3362989; 56 subjects, 7/8-iron | fetched-full |
| Chu 2010 | J Sports Sci 28:1251 (PDF copy); 308 golfers, event values only | fetched-full |
| Watson 2026 | Sports Med review of GRF/CoP, PMC13198453; secondary values for Han 2019, Ball & Best, Williams, Bourgain, Peterson | fetched-full (secondary) |
| Han 2019 (GRF), Han 2019 (styles), Kwon 2013, Healy 2011, Horan 2012 | abstracts/landing pages only | abstract |
| Horan 2012 numbers, Healy CHS, lumbar loads, Sonic 258 ms, TPI 233-296 ms, Kwon-lab GRF explainer | search summaries / public web explainer only | snippet |
Requested but not obtained in usable numeric form: Neal & Wilson 1985, Nesbit beyond v1, Ball & Best primaries, Wallace/Koenig/Mann, Hellstrom 2009 (paywalled/not retrievable); Sasaki and Brown (long-drive/high-CHS) have no hit; Han/Kwon/Choi long-drive: none exists in the open literature found.

## 2. (b) Kinematic sequence for high-CHS populations
| Quantity | Value | Population / n / CHS | Tag |
|---|---|---|---|
| Peak downswing hip line / shoulder line / upper lever / club (on-plane) | 394+-62 / 711+-63 / 1142+-67 / 2364+-115 deg/s; wrist uncocking 1615+-138 | 66 skilled, 110.4 mph | fetched-full |
| Same at impact (hip / shoulder / upper lever) | 262 / 610 / 725 deg/s | same | fetched-full |
| Time of downswing peak before impact (hip / shoulder / upper lever) | -87 / -84 / -73 ms (14 ms window) | same | fetched-full |
| Pelvis peak (5-iron) | 428 elite vs 399 recreational deg/s; r with CHS 0.017; peak occurs 102 vs 80 ms before impact | 29, 88-92 mph | fetched-full |
| Pelvis peak (7/8-iron, K-Vest) | 503 low-handicap vs 380 high-handicap deg/s | 56 | fetched-full |
| Thorax / pelvis peak, professionals | 650 / 507 deg/s | 14 pros, 112 mph | **snippet** |
| **Long-drive player, near impact** | pelvis 284-325, torso 610-650, arm 460-480 deg/s; grip speed 22 mph | **1 player, 137 mph** | fetched-full (n=1) |
| Population CHS only (no joint data) | men 145 mph, ball 214, smash 1.48, launch 11.2, 2789 rpm, carry 352 yd; women 116 mph | 304 + 131 drives | fetched-full |
Findings. (1) Within 66 skilled players, speed correlates with peak speeds (r = 0.45 hips, 0.46 shoulders, 0.55 upper lever, 0.91 club); peaks of hips/shoulders/upper lever land within 14 ms of each other, only the club peak is clearly later. The clean proximal-to-distal order is in the **transition** (hip, shoulder, upper lever, club), not at the downswing peaks. (2) The only long-drive datum does **not** show body speeds above the 110 mph group (see C2). (3) Pelvis peaks sit at 428-507 deg/s across 92-112 mph groups with no consistent rise (C1).

## 3. (a) Joint torques in N*m
| Quantity | Value | Basis | Tag |
|---|---|---|---|
| Club-grip (hand-club) torque, max | **40.9+-2.9 N*m**, force 340 N, at 87% of downswing | 3 pros, 102.4 mph | fetched-full |
| Club peak power (total / force / torque) | 2813 / 2113 / 738 W; work 213 J (15% by torque) | same | fetched-full |
| Model trunk torque | ~75 N*m early, ~95 near impact | **simulation**, 44 m/s (98 mph), 80 kg | fetched-full (model) |
| Model shoulder torque | 83 early, ~100 near impact | same | fetched-full (model) |
| Model wrist torque | ~20-25 at the end; adds 3.6 m/s (~9%) | same | fetched-full (model) |
| Model limits (inputs) | spine 180, shoulder 120, wrist 60 N*m; wmax 20/30/60 rad/s | Neal et al. 1999 | fetched-full |
| Peak hip torque, trail extensor / lead extensor | 10.64 / 5.28 % BW*Ht (**about 156 / 77 N*m** for an assumed 83 kg, 1.80 m golfer, derived) | 20 amateurs, driver, ~92 mph | fetched-full |
| Hip internal rotators trail / lead | 2.70 / 3.21 % BW*Ht (about 40 / 47 N*m, **87 N*m both**, derived); ext. rotators 2.38 / 1.43 | same | fetched-full |
| Hip flexors / abductors | 6.6 / 5.7-6.3 % BW*Ht | same | fetched-full |
| L4/L5 compression near impact | ~6 BW (~4300 N); force, not torque | EMG-assisted model | **snippet** |
Still **not found**: a measured peak lumbar/trunk-axial or shoulder torque in N*m. Hip torques correlate with CHS (r 0.46-0.65, most components).

## 4. (c) GRF
| Quantity | Value | Population / CHS | Tag |
|---|---|---|---|
| Max vertical per foot, lead / trail (lab, artificial turf) | pros 1.18 / 0.64 BW; amateurs 1.24 / 0.70 | 9 pros (108.5 mph), 19 amateurs | fetched-full |
| Max vertical lead / trail (lab) | skilled 1.09 / 0.98; low-skilled 1.13 / 0.89 BW | 13 + 17, CHS n/a | fetched-full |
| Max vertical back / front (natural turf, driver) | 0.49 / 0.84 BW | 24 golfers | fetched-full |
| Max horizontal per foot, lead / trail | pros 0.16 / 0.13 BW; amateurs 0.19 / 0.13 | 28 | fetched-full |
| Early-downswing lead-foot load | 59% BW skilled vs 33% low-skilled | 30 | fetched-full |
| Free moment about the vertical axis | **1.19 +-0.08 N*m/kg** at hard effort (about 99 N*m for 83 kg); 0.83 and 1.00 at easy/medium; occurs in early downswing | 10 pros, **5-iron**, 61 / 71 / 79 mph | fetched-full |
| Foot torsional torque (turf), driver | front Tz 17-19, back 6-7 N*m; low-handicap back foot 18.2 | 24 | fetched-full |
| GRF-parameter correlations with CHS (driver) | lead-foot backward force r=0.46, lead away 0.45, trail forward 0.29; moment about vertical axis dominated by the **pivoting moment** (F/B shear forces of both feet) | 63 skilled | abstract + secondary |
Pros did **not** exceed amateurs in per-foot peaks in the one driver study with both groups (Bourgain); between-golfer GRF-CHS correlations in mixed-skill samples (r 0.5-0.8) are partly skill confounding. No GRF datum exists above ~118 mph.

## 5. (d) X-factor by club speed
| Source | Value | Tag |
|---|---|---|
| Madrid (66, 110 mph, driver) | top 61+-9, max 62+-8, at impact 9+-8, range 74+-9; stretch 5+-3 / 1+-2 / 6+-4 deg; r(CHS) 0.27 (top), stretch n.s. | fetched-full |
| Meister (10 pros, 5-iron, 61-79 mph) | peak 52 / 54 / 56, at impact 24 / 28 / 33 deg for easy/medium/hard; pelvis 44-46 and torso 94-99 deg barely change | fetched-full |
| Kwon 2013 (18 skilled, 102 mph) | max 59, stretch 1-8 deg; not correlated with CHS | abstract + secondary |
| Chu 2010 (308, heterogeneous) | top 49.0+-11.6, at impact 12.3+-9.1 | fetched-full |
Derived: slope 1.1 deg per m/s between golfers (Madrid) or 0.5 deg per m/s within golfers (Meister) gives about **63-66 deg at the top at 120 mph** (extrapolated, weak: r=0.27).

## 6. (e) Downswing duration vs club speed
| Source | Value | Tag |
|---|---|---|
| Madrid | 253+-26 ms (early 136, late 118; backswing 769; ratio 3.0:1), r = -0.48 with CHS | fetched-full |
| Bourgain | pros 260+-20 ms (108.5 mph) vs amateurs 280+-20 (90.6 mph) | fetched-full |
| Okamoto | 280+-20 ms at 102.4 mph (0.26-0.30 s) | fetched-full |
| Han styles (via Madrid) | 236 / 272 / 256 ms for LBS / LDS / LSA styles | secondary |
| Sonic 258+-8 ms; TPI 233-296 ms | summaries | snippet |
| Sprigings simulation | 380 ms (measured pro 340 ms) | fetched-full (model, C8) |
| Long-drive player | not reported | n/a |

## 7. Deltas vs v1 and tightened ranges
| Item | v1 | v2 | Why / tag |
|---|---|---|---|
| Downswing time | fixed 230 ms | **228-250 ms at 120 mph** (Madrid within-group slope gives 228, Bourgain between-group 242; at 132 mph 196-229, unsupported) | derived from measured 253-280 ms at 90-110 mph |
| Pelvis peak at 120 / 132 mph | 519 / 565 deg/s (3-axis fit) | **450-519 / 521-565**; upper bound only (C1, C2) | Madrid-anchored slope 450 / 521 |
| Thorax at 120 / 132 | 803 / 886 | 770-803 / 844-886 | Madrid on-plane 770 / 844 |
| Lead arm / upper lever at 120 / 132 | 1097 / 1226 | 1097-1217 / 1226-1311 (definition-dependent) | Madrid 1217 / 1311 |
| Club at 120 / 132 | 2500 / 2770 | 2500-2575 / 2770-2841 | Madrid 2575 / 2841; agrees within 4% |
| Top X-factor | 45-62 deg | **54-62 at 100-110 mph; ~63-66 at 120 (extrapolated)** | Madrid 61, Meister 56, Parker 55, Kwon 59 |
| X-factor at impact | not given | 9+-8 (FSP method) vs 33+-6 (Meister): method-dependent (C6) | |
| Club-grip torque, 100 / 120 / 132 mph | 29 / 45 / 55 N*m (Nesbit fit) | **39 / 55 / 65** (Okamoto 40.9 at 102 mph + Nesbit slope) | measured n=3 anchor beats v1 fit by ~30% (C7) |
| Peak/average power ratio (club) | 2.5 | **2.5-3.7** | Okamoto 2813 W peak / 761 W avg |
| Peak trunk torque (model) | none (Sprigings limits only: 180 N*m) | 75-95 N*m at 98 mph; scaled 91-141 N*m at 120 mph (v to v^2) | simulation only |
| Hip torque | derived 290 N*m average from work | measured peaks: trail extensor ~156, axial rotators ~87 N*m both (83 kg, 93 mph) | different quantity (C9) |
| Vertical-axis moment | derived couple 150-220 N*m + foot torque 40-50 | free moment ~99 N*m at hard 5-iron effort; extrapolated **143-166 N*m (proportional-linear) at 120 mph, 157-186 at 132** (model, 3 points) | |
| Lead-foot peak vertical | 0.8-1.5 BW | **1.09-1.24 BW lab; 0.84 turf** | four studies |
| Long-drive segment speeds | none | one 137 mph player, no rise in body speeds | n=1 |

## 8. Updated scaling fits (only where supported)
* Segment speeds: within-group slopes from Madrid (hip line 13.2, shoulder line 13.8, upper lever 17.6, club 49.6 deg/s per m/s). Regression-diluted lower bounds; kept as a **band** next to v1, not a replacement.
* Downswing time: -6.0 ms per m/s (within group, r=-0.48) or -2.5 ms per m/s (between groups).
* Free moment: proportional k = 0.0321 N*m/kg per m/s or linear 0.0449 slope; 3 points, 5-iron, extrapolated 1.5-2x.
* Grip torque: anchor 40.9 N*m at 45.8 m/s, slope 1.83 N*m per m/s.
* **Not updated** (unsupported): joint-work exponent 2.55 (no new work data), peak GRF vs CHS (no usable numeric trend), X-factor stretch trend.

## 9. Conflicts (also in the JSON `conflicts` field)
* **C1** pelvis peak vs CHS: Madrid r=0.45 vs Lynn 0.017; group means 428-507 deg/s flat from 92 to 112 mph. v1's pelvis extrapolation is an upper bound.
* **C2** the single long-drive player has pelvis/torso/arm speeds near impact not above the 110 mph skilled group (definition mismatch; n=1). v1 extrapolated body speeds to 132 mph are unsupported upper bounds; CHS beyond ~120 mph may depend more on club length/loft, body mass and release than on faster trunk rotation.
* **C3** horizontal GRF 0.13-0.19 BW per foot (Bourgain) vs 0.4-0.6 BW (v1 review).
* **C4** lead-foot vertical 1.09-1.24 BW (lab) vs 0.84 (turf).
* **C5** free moment ~99 N*m vs foot torsional torque ~25 N*m: different quantities; do not use Tz as the pelvis requirement.
* **C6** X-factor at impact 9 vs 33 deg: computation method.
* **C7** v1 grip-torque fit under-predicts a measured 41 N*m by ~30%, club power by 15-20%.
* **C8** simulated downswing 380 ms vs measured 250-280.
* **C9** measured hip axial torque ~87 N*m (both hips) vs v1's 290 N*m energy-equivalent.
* **C10** X-factor stretch 1-6 deg vs Cheetham's ~19%.

## 10. Recommendations
1. Use the v2 band (min-max of v1 and Madrid-anchored) for 120 mph peak segment targets and call 132 mph unsupported; weight the pelvis target to the low end.
2. For torque limits, 120 mph requires about 55 N*m at the hand-club interface (Okamoto-anchored) and a trunk yaw torque in the ~90-140 N*m range (model-scaled); `chest_yaw` 120 N*m and G1 elite waist_yaw 250 N*m cover it, G1 stock waist_yaw 88 N*m (at 32 rad/s) does not at 120 mph.
3. Downswing time: use 230-250 ms at 120 mph (not a hard 230), recompute v1 average power with 0.25 s as the low-power case (about -8%).
4. Do not set a numeric GRF reward; log lead-foot VGRF in BW (expect 0.8-1.25 BW) and a vertical-axis moment diagnostic (order 100-170 N*m at driver effort, extrapolated).
5. Keep long-drive claims out of numeric targets until a real full-text study with joint speeds above 120 mph exists.

## 11. Remaining gaps
* Measured peak lumbar/trunk-axial and shoulder torque (N*m): none found.
* Any joint-level data above ~112 mph other than one 137 mph near-impact set; Horan 2012 numbers are snippet-level, full text needed.
* Han 2019 GRF means (63 skilled), Ball & Best and Wallace/Koenig/Mann primaries, Hellstrom 2009, Healy segment peaks: paywalled/abstract only.
* Madrid on-plane vs Cheetham 3-axis definitions: no conversion found.
* Torque and GRF scaling above 52 m/s (116 mph) remain assumptions.
