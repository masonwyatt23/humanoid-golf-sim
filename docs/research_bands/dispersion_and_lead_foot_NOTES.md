# Driver dispersion bands and lead-foot plant: source notes

Written 2026-10-19, around 9:40 AM America/New_York, by the PureGolf Data Agent for the Golf Style Evaluator.
Companion files (not committed):
- `driver_dispersion_bands.csv`: 29 rows
- `lead_foot_plant_bands.csv`: 12 rows

## Rules used
- Every number was read from a page or PDF fetched on 2026-10-19. Nothing is recalled or estimated.
- Anything derived here is marked COMPUTED. That covers yd per 100 yd, ft→yd conversions, means of per-driver means, and normal-distribution inversions.
- `measurement_type` separates **MEASURED** data from model fits, secondary reports and **DESCRIPTIVE** (instruction-article) sources.
- No video was downloaded. Instruction articles were read as text only.
- Bands are proposals. Where a threshold is my engineering choice and not a sourced figure, it says **UNSOURCED**.

---

## Part B: driver start direction and lateral miss

### Sources

1. **USGA/R&A R22-01 (May 2019), Tables 6–7.** This is the core source.
   - It gives launch direction mean and SD (deg) and carry side mean and SD (yd) for driver shots, by sex and skill group.
   - Male pros are 12,334 PGA Tour TrackMan competition shots (2018). The amateurs come from TrackMan range sessions, plus a few indoor stereoscopic launch-monitor shots in Cat 1.
   - These SDs are **pooled across golfers and include mishits**. A single consistent player will be tighter, so bands built on them are lenient.
   - The report does not define the left/right sign.
   - Two oddities, kept as published:
     - Female pros show a launch-direction SD of 1.3°, which does not fit their carry-side SD of 14.7 yd.
     - Male pros show a carry SD of 66.9 yd against a total SD of 22.1 yd.

   | Group | Club mph | Launch dir mean ± SD (°) | Carry side mean ± SD (yd) | Carry (yd) | Side SD per 100 yd carry (COMPUTED) |
   |---|---|---|---|---|---|
   | PGA Tour pros | 113.7 | −0.2 ± 3.3 | −0.4 ± 17.5 | 262.2 | **6.7** |
   | Male Cat 1 | 100.5 | 0.9 ± 3.4 | −1.3 ± 17.8 | 215.1 | 8.3 |
   | Male Cat 2 | 91.4 | 0.7 ± 4.4 | 5.3 ± 17.8 | 183.6 | 9.7 |
   | Male Cat 3 | 85.8 | −0.2 ± 4.6 | 4.4 ± 19.3 | 163.3 | 11.8 |
   | Male Cat 4 | 89.6 | −0.1 ± 5.3 | 13.1 ± 19.2 | 163.1 | 11.8 |
   | Female pros | 93.8 | 1.2 ± 1.3 (suspect) | 0.6 ± 14.7 | 216.7 | 6.8 |
   | Female Cat 1 | 86.3 | 1.1 ± 3.2 | −3.7 ± 11.9 | 173.6 | 6.9 |
   | Female Cat 2–4 | 77.0–62.6 | 0.0 to −0.4 ± 3.9–6.5 | 2.2–5.0 ± 9.3–12.5 | 135.8–76.5 | 8.2–16.3 |

2. **Broadie & Ko, Winter Simulation Conference 2009, Table 2.**
   - This is the shot-*endpoint* direction SD fitted to Golfmetrics amateur data: 5.5° (SE 0.2) for 78–82 scorers and 7.9° (SE 0.6) for 96–107 scorers.
   - The endpoint angle includes curvature and roll, so it is not launch direction.
   - **There is no PGA Tour σα in this paper.** The "Every Shot Counts" book was not accessible, so no tour figure from Broadie is included.

3. **PGA Tour ShotLink stats.**
   - 2026 season, fetched from pgatour.com page data, through week ending 2026-10-19:
     - Distance from fairway **edge** on misses: 27′4″ (9.1 yd).
     - Distance from fairway **centre** on hits: 20′1″ (6.7 yd).
     - Fairway hit: 62.26%. Left rough: 12.96%. Right rough: 13.49%. Other miss: 5.17%. Left/right tendency: 50.2/49.8.
     - Average club speed: 116.92 mph. Average carry: 287.6 yd.
   - 2022-23 season summary PDF:
     - Driving accuracy: 58.6%. Left rough: 14.57%. Right rough: 16.29%.
     - Centre: 24′11″. Edge: 28′10″. I assigned these two from the PDF column layout.
   - ShotLink publishes **no lateral SD**. Edge and centre distances are conditional on a miss or a hit and refer to fairway geometry, so they can't be turned into yd/100 without fairway widths. They're useful as sanity context only.

4. **MyGolfSpy 2018 Most Wanted, indoor GCQuad.**
   - Mean "offline" was 16.0 yd at 176.1 yd carry for the 75–90 mph group (**9.1 yd/100**) and 19.1 yd at 259.6 yd carry for the 105+ mph group (**7.4 yd/100**). All of these are COMPUTED means across drivers.
   - Offline is most likely unsigned. If so, a normal distribution's mean absolute value is about 0.8 σ, which means σ ≈ 9–11 yd/100 for these amateur testers. That fits R22 Cat 1–2.

5. **PING study (Shephard & Henrikson) in Scott Lynn's slides.** Offline mean ± SD by ground-force style: −2.61 ± 22.99, −5.57 ± 28.08 and 0.20 ± 18.25 yd. There is no carry figure, so no ratio. These are slides, not peer reviewed.

6. **On-course outcome data, no yards.**
   - Shot Scope driver-only miss-pattern rows (via MyGolfSpy): held locally pending counsel (vendor data), removed from the tip of driver_dispersion_bands.csv on 2026-10-25; not in git at the tip.
   - Arccos 2024 season, via the FOGOLF/Golfweek summary: men at 0–4.9 hcp drive 250.0 yd, hit 49.3% of fairways, and 12.0% of drives end in a penalty or recovery.
   - Lou Stagner, from Arccos data: 7.0% of drives by 0–5 index players finish more than 40 yd from the fairway centre.
     - If that were a zero-mean normal, it would imply σ ≈ 22 yd, about 8.8 yd per 100 yd of *total* (COMPUTED, low confidence because real tails are heavier).

**Excluded:**
- "Benchmark" tables from t5golf.com and thescratchproject.co.uk: no stated data source.
- TrackMan's tour-averages page: no launch direction.
- The Trackman 4 reliability paper (J Sports Sci 2024): does not report launch direction or side.
- Betzler et al. 2012: the face-angle SD tables are paywalled. Its data is pooled into R22 anyway.

### Proposed gating band (PROVISIONAL until the Evaluator reviews it)

Ratios are unitless, so yd per 100 yd is the same as m per 100 m and works directly with the sim's metre carry. The band is symmetric, so mirroring a left-handed swing doesn't matter.

| Check | Pass | Warn | Fail | Rationale |
|---|---|---|---|---|
| Single-shot launch direction \|LD\| | ≤ 7.0° | 7.0–9.0° | > 9.0° | About 2 SD of R22 tour (3.3°) and male Cat 1 (3.4°) is 6.6–6.8°. About 2 SD of male Cat 2 (4.4°) is 8.8°. |
| Single-shot lateral at landing, per 100 yd carry | ≤ 13.5 | 13.5–17 | > 17 | 2 × 6.7 (tour) and 2 × 8.3 (Cat 1). At 280 yd carry, pass means ≤ 38 yd. |
| Batch (≥ 10 shots) SD of LD | ≤ 4.5° | — | > 4.5° | Between tour (3.3) and Cat 2 (4.4). |
| Batch SD of lateral per 100 yd | ≤ 9 | — | > 9 | Tour 6.7 and Cat 1 8.3. MGS indoor σ is about 9–11 for amateurs. |
| Batch mean LD bias | \|mean\| ≤ 2° | — | > 2° | **UNSOURCED** choice. R22 group means are within ±1.2°, but individual players aim and shape, so this should stay soft. |

Confidence:
- **Medium** for launch direction. It rests on one large source, R22, with 12,334 tour shots.
- **Medium-low** for lateral at landing. Carry side includes curvature and wind, the R22 SDs are pooled across golfers, and only R22 and MGS supply yd per carry.
- ShotLink, Shot Scope and Arccos agree qualitatively (tour misses are about 50/50 left/right) but give no SD.

---

## Part C: lead-foot plant, top of backswing to impact

### Bottom line: numeric displacement data is thin
I found **no public peer-reviewed or published-metric source giving lead-foot vertical lift (cm) or horizontal slip (cm) from top to impact** in pro driver swings.
- Koenig, Tamres & Mann (MIT) tracked shoe motion with LED arrays but report it only qualitatively: "the shoes exhibited significant movement, with the high handicappers having the greatest total amount of movement".
- Worsfold et al. report forces and a friction ratio, not slip distance.
- Sportsbox and TPI: no public numeric foot metric was found.
- A Korean paper (KJAB) reportedly gives lead-ankle plantarflexion velocity in the downswing, but it couldn't be fetched, so it was **not used**.
- Rambarran & Kendall 2001 is about heel-wedge insoles, not foot motion. It was excluded, and its "63.5 mm (1/4 inch)" text is internally inconsistent anyway.

### What the data does say (numeric, kinetic)
- **Lead-foot pressure at impact** (McGhie data in Lynn's slides; 23 golfers, 86 drives, 109.6 mph): 75.9 ± 17.7%, **range 3.6–100%**. At the top it is 21.7 ± 14.0%.
- **Ball et al. (ISBS 2002):** 12 of 40 golfers used a "Reverse" style, with centre of pressure at only 43% toward the front foot at contact. Their handicap and club speed did not differ from the Front Foot group.
- **PING / Lynn:** 36% of amateur swings were vertical-force dominant.
- **Worsfold et al.:** shear/vertical ratio 0.62 ± 0.03 at both feet with every shoe and club. Driver peak vertical force: front foot 0.83 BW, back foot 0.33 BW.
- **Koenig et al.:** vertical force reaches a minimum shortly **after** impact on both feet, so unloading after impact is normal.

### Legitimate exceptions (descriptive sources, no numbers)

| Window | Style | Source |
|---|---|---|
| Pre-swing (outside the window) | Foot lifts before takeaway: Berkshire lifts the left foot, plants it, then lifts the right | GOLF.com 2020 |
| Backswing → transition | Lead heel up at the top, slammed down to start the downswing (Nicklaus, Bubba Watson) | GOLF.com; Golfmagic |
| Transition (pre-impact) | Lead foot replants slightly closed before impact (Reed) | Golf Smart Academy |
| Late downswing / impact | Most of the lead shoe in the air near the bottom of the swing (Scheffler) | GOLF.com 2024 |
| Transition → impact | Hard vertical push off the lead foot (J. Thomas) | GOLF.com 2025 |
| Post-impact | Lead foot spins and slides back (Woodland, Reed); lead foot lifts and repositions (Scheffler) | Golf Digest; Golf Smart Academy; GOLF.com |

### Proposed band (PROVISIONAL; numeric limits are UNSOURCED engineering choices)
1. **Window:** from top of backswing to impact only. Ignore everything after impact, because spin, slide and lift there are documented in elite players.
2. **Vertical:** measure height against the **address** pose, not the top. Otherwise heel-up players (Nicklaus, Bubba) show "negative lift".
   - Allow any heel-only or toe-only lift.
   - **Fail only if the whole lead foot has no ground contact** for more than a short run of frames before impact. I suggest ≥ 3 control steps (UNSOURCED).
   - A partial lift at impact (Scheffler) must pass.
3. **Horizontal slip:** track the contact-patch centroid from top to impact. Suggested limit: ≤ 25% of the sim foot's length, plus foot yaw ≤ 20° (both UNSOURCED). The aim is to catch sim "skating" while allowing a Reed-style replant. Tune both against the sim's own distribution.
4. **Don't gate on lead-foot load.** Real impacts range from 3.6% to 100% lead pressure, and the Reverse style is legit.
5. **Physics check:** if the sim foot slips while the shear/normal ratio is below about 0.62, treat it as a friction-model artefact, not a style (Worsfold).

Confidence: **low** for any numeric lift or slip threshold, because there's no data. **Medium** that the window, reference and exception rules match the published descriptions.

## Gaps
- No published within-player launch-direction SD for tour players. R22 SDs are pooled.
- No ShotLink lateral SD. Broadie's tour dispersion figures are in a book I couldn't access.
- No numeric lead-foot lift or slip, top to impact, from any public source. Shoe-tracking studies (MIT) report only qualitatively. Williams & Cavanagh 1983 couldn't be fetched (PubMed 403).
- Arccos figures come through a secondary summary and a newsletter, not Arccos's own report page.
