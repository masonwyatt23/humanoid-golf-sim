# Modern 460cc driver head: sourced geometry, mass, MOI, CG, tee height (Data Agent, 2026-10-24 ET)
Full rows (URL, table, label, confidence): `data/references/driver_head_460cc_refs.{json,csv}`. Unpublished values are marked estimate/derived.

## Key values
| Quantity | Nominal | Range | Label | Conf. | Source |
|---|---|---|---|---|---|
| Volume | 460 cc | <=460 (+10) | rule | high | USGA Equipment Rules Pt 2 4b(i) |
| Sole-to-crown (crown height) | 62 mm | 60.0-63.5 (median 61.5, n=3, PROCEED); <=71.12 rule | spec / rule | medium | PROCEED spec tables; USGA |
| Face height | 54 mm | 50-58.5 (median 53.25, n=4, Wishon/PROCEED) | spec | medium | Wishon, PROCEED |
| Face width | 105 mm | 105-106 | spec | medium | Wishon |
| Head depth (front-back) | 112 mm | 111-113 | spec | medium | Wishon |
| Heel-toe length | ~120 mm (estimate) | <=127 rule | rule / estimate | low | USGA |
| Face-centre height soled | 29 mm | 27-31 (bound 21-36) | derived from patent-claimed Zup/CGZ + face geometry | medium (range) | TaylorMade US 12,649,090; PROCEED; Wishon (see section below) |
| Head mass | 200 g | 192.7-203.4 (median 199.0, rule36 n=21); 202-203 (n=2, Wishon/PING) | measured / spec | high | rule36.net, Wishon, PING |
| Loft / lie | 10.5 / 58.5 deg | 9-12 / 58-59 | spec | high | PING, Wishon, PROCEED |
| MOI vertical axis (Izz) | 4500 g cm2 | 3895-5104 (median 4389, rule36 n=21, 2005-10 era); 5004-5025 (n=1, Wishon); <=5900+100 rule. Modern: see below | measured / spec / rule | medium | rule36, Wishon, USGA, Tutelman |
| MOI horizontal (heel-toe) axis | 3000 g cm2 | 2000-3900 (1/2-2/3 of Izz) | model | low | Tutelman GE3 |
| CG depth behind face | 40 mm | 36.3-45.2 (rule36); 35-38 (PROCEED) | measured / spec | medium | rule36, PROCEED |
| CG height | 31 mm | 29.8-33.4 (rule36; reference plane UNKNOWN, not stated on page) | measured | medium | rule36 |
| CG distance from shaft axis | 35 mm | 29.5-41.5 (rule36); 38-41.5 (PROCEED) | measured / spec | medium | rule36, PROCEED |
| Face progression | 20 mm | 17.5-22.3 | measured / spec | high | rule36, PROCEED, Wishon |
| Shaft axis to face centre (CFZ) | 39 mm | 35-45 (38-40 narrowest band) | manufacturer patent claim (single manufacturer's design range) | medium | TaylorMade US 12,649,090 Tables 3-4 |
| Tee length | - | <=101.6 mm (4 in) | rule | high | USGA Pt 6 |

## Tee height
Equator at crown => ball centre = crown height; tee top (ball bottom) = crown - 21.3 mm. Real head (crown 62): **ball bottom ~41 mm above ground (1.6 in), ball centre ~62 mm**
(range 38.7-42.2 for crown 60-63.5). Cross-checks: Golf Digest (E. Michael Johnson, 10 Mar 2016, https://www.golfdigest.com/story/an-important-reminder-to-give-yourself-ideal-launch-and-distance-this-spring, opened and verified) "at least half the ball is above the crown of the club"; MyGolfSpy measured a 1.5 in (38 mm) tee beat 0.5 in by
14 yd carry with impact >4 mm higher on the face (PING G410 LST). R22-07 tee "positions" are fore-aft, not height, so they do not constrain tee height. Tee length limit 101.6 mm.
The Orchestrator's ~34 mm: as ground-to-ball-bottom it puts the ball centre at 55 mm, i.e. the equator ~7 mm BELOW a 62 mm real crown and ~26 mm below the sim crown. Corrected: **~41 mm (real head) / ~60 mm (sim head) ground to ball bottom**; 34 mm is only right if the crown were ~55 mm.

## Sim head (env/v5_body.py, read-only) vs real
| | sim | real nominal (range) |
|---|---|---|
| shape | box 90 deep x 110 wide x 64 tall | 112 deep, face 105 x 54, crown 62 |
| face-centre height at address | 49.9 mm (Trainer: 50) | 29 (27-31, derived) |
| crown height | 81.3 mm (Trainer: 81) - box tilted by 10.5 deg loft, so the box corner rises | 62 (60-63.5); rule <=71.1 -> sim exceeds the rule limit |
| ball centre / bottom | 59.9 / 38.6 mm (TEE_ABOVE_FACE = +10 mm, marked [guess]) | 62 / 41 |
| ball equator vs crown | 21 mm BELOW crown | at crown |
| mass | 200 g | 200 (193-203) |
| Izz (uniform box) | 3367 g cm2 | 4500 (3900-5100, <=5900) |
| I about heel-toe axis | 2033 g cm2 | ~3000 (2000-3900, model) |
| CG depth / height | 45 / 41.7 mm | 40 (36-45) / 31 (30-33) |
| CG / face centre offset toe-ward from hosel | 50 mm | 35 (29.5-41.5) |
| face ahead of shaft axis | ~45 mm (head centre on the shaft line) | FP 20 (17.5-22) |
| loft / lie | 10.5 / 56 | 10.5 / 58-59 |
Strikes: median y_high -24.9 (K28b/K30, n=200), -23.4 (K31, n=100), -24.0 (K31cd, n=200); p90 about -11 mm.

Reading: negative y_high = ball BELOW face centre, i.e. the sim face centre arrives higher than the ball. The ball is set only 10 mm above the sim's face
centre, while on a real driver teed equator-at-crown the ball centre sits ~30 mm above face centre (62 vs ~30 mm). Plausible contributors (not proven):
(1) the tee: raising the ball to equator-at-sim-crown (+21.4 mm, ball centre 81.3 mm) would move strikes up ~21 mm if the swing is unchanged, i.e. median -24 -> about -3 mm;
(2) a 64 mm box tilted by loft is 81 mm tall at address, 10 mm over the 71.1 mm rule limit and ~19 mm taller than a real crown; (3) the face sits ~45 mm ahead of the shaft axis vs ~20 mm real,
which changes where the face meets the ball as the shaft leans/rotates through impact. Recommended realistic set (for the Trainer/Env owner to decide): face height 54 mm, crown 62 mm,
depth 112, width ~105-120, CG 40 behind face / 31 high / 35 from shaft axis, FP 20, Izz ~4500 (<=5900), Ih ~3000, lie 58.5, ball bottom ~41 mm (centre 62). The env already has a `tee_dz` flag (K32).

## rule36.net table (http://www.rule36.net/spec/driver_head.htm, "Driver head Specifications")
Column headers verbatim: モデル名 | 体積 (CC) | 重量 (g) | 慣性 モーメント (g・cm3) | ロフト | リアルロフト | フェース角 | FP (mm) | 重心距離 (mm) | 重心深度 (mm) | 重心高 (mm) | 重心角.
English (agent translation): model | volume | mass | MOI (page prints g・cm3, taken as g cm2) | loft | real loft | face angle | face progression | CG distance | CG depth | CG height | CG angle.
The page states no brand, MOI axis, method, or reference plane for CG height (重心高): **CG-height reference plane is unknown** (ground-when-soled is plausible but unverified).
The 21 per-model rows themselves are **held locally pending counsel review** (third-party compiled table); only aggregates are published here. The aggregates use only the rows >=440 cc (n=21); the two smaller heads, LEGACY TYPE S (439.2 cc) and LEGACY Tour (431.2 cc), are excluded. The MOI minimum is 3895 (an earlier report said 3893; that figure was LEGACY Tour, 431 cc).

## Face-centre height above the ground at address (rev. 2026-10-24 ET, Evaluator fixes)
**Value: 29 mm, likely range 27-31 mm, outer bound 21-36 mm. Label: derived. Confidence: medium for the range, low for the exact value.** No manufacturer publishes this number.

Definition. The face centre is set by a template, slid until the heel and toe edge readings are equal and the sole and crown edge readings are equal. Source: R&A/USGA TPX3004 Rev. 2.0 (9 April 2019), section 2.1 b, https://www.usga.org/content/dam/usga/pdf/2019/equipment-standards/TPX3004%20Protocol%20for%20Measuring%20the%20Flexibility%20of%20a%20Golf%20Clubhead.pdf. usga.org returned Access Denied, so I opened the archive.org copy and confirmed section 2.1 b (i)-(ii). The Pendulum Technical Description Report sec. 2.2 (archive.org copy) gives marking repeatability within 2.1 mm at 99%. The face centre is the midpoint between the face edges, not half the crown height.

Derivation chain:
1. CG height above ground (Zup) is 18-30 mm across the patent's example bands, 23-27 mm in the narrowest band, and 20-28 mm in claim 1. Source: TaylorMade US 12,649,090, https://patents.us/US12649090. Label: manufacturer patent claim.
2. CGZ, the CG height relative to the face centre, is -10 to 0 mm across the bands and -4 to -3 mm in the narrowest. Tutelman's example also puts the CG about 5 mm below mid-face (https://www.tutelman.com/golf/clubs/centerOfGravity2.php).
3. Route A: face-centre height = Zup - CGZ, which gives 21-35 mm for claim 1 combined with a CGZ band of -7 to -1 mm, and 26-31 mm for the narrowest bands.
4. Route B: face height is measured from the lowest face point to the highest, so face centre = low + h/2. The lowest face point is 2-6 mm (patent FIG. 1A item 164). Face height is 50-58.5 mm (n=4 manufacturer spec heads). Result: (2..6) + (50..58.5)/2 = 27-35.3 mm.
5. Crown cross-check: the patent's effective face height is the crown height minus 2-7 mm. With crown 60-63.5 mm, centre = (2..6) + (53..61.5)/2 = 28.5-36.8 mm.
6. Result: routes A and B overlap at 27-31 mm, so the value is 29 mm and the outer bound stays 21-36 mm. The routes are only partly independent, since both rely on US 12,649,090.

## Face-centre to shaft axis, heel-toe length, modern Izz
- Face-centre to shaft-axis distance (CFZ) is 35-45 mm across the example bands and 38-40 mm in the narrowest; nominal 39 mm. **Caveat: this is a single manufacturer's (TaylorMade) design range**, not a cross-industry measurement. It is distinct from FP. The CG analogue DELTA2 is 34-42 mm. The face centre sits 9-18 mm ahead of the hosel centre point (CFY).
- Heel-to-toe: the rule is <=127 mm, measured at 60 deg lie between vertical projections of the outermost heel and toe points. If the heel point is not clearly defined, it is taken 22.23 mm above the ground (Rule 4b(i)). No head-specific spec was found, so the ~120 mm nominal is an estimate.
- Modern Izz: the conforming range is 4800-5900 g cm2 (rule cap 5900 + 100 tolerance), nominal 5600. The 5600 is a manufacturer claim (n=1, Tour Edge 2023 press release; its "g/ cm2" is a typo for g cm2). TaylorMade's patent bands run 4800-7000 g cm2, and the top of that range is beyond the rule cap.

## Tee-height check
MyGolfSpy measures tee height "from ground level", so a 1.5 in tee puts the tee top at 38.1 mm. Taking the ball bottom at the tee top, the ball centre is 38.1 + 21.335 = 59.4 mm and the equator is 2.6 mm below a 62 mm crown, i.e. a little under half the ball is above the crown. Golf Digest's "at least half above the crown" needs a ball bottom of at least 40.7 mm for a 62 mm crown. The ball centre is about 30 mm above the 29 mm face centre, which is consistent with MyGolfSpy's higher impact with the 1.5 in tee.

## Data policy
Only aggregates (range, median, n) with attribution are kept in git. The per-model and per-example breakdowns (manufacturer spec heads, patent example bands, rule36 heads) are held locally in /workspace/held_research_bands/.
