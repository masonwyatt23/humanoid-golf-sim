# Modern 460cc driver head: sourced geometry, mass, MOI, CG, tee height (Data Agent, 2026-10-24 ET)
Full rows (URL, table, label, confidence): `data/references/driver_head_460cc_refs.{json,csv}`. Unpublished values are marked estimate/derived.

## Key values
| Quantity | Nominal | Range | Label | Conf. | Source |
|---|---|---|---|---|---|
| Volume | 460 cc | <=460 (+10) | rule | high | USGA Equipment Rules Pt 2 4b(i) |
| Sole-to-crown (crown height) | 62 mm | 60.0-63.5 (PROCEED 455R/460R); <=71.12 rule | spec / rule | medium | PROCEED spec tables; USGA |
| Face height | 54 mm | 50 (Wishon 719MW), 53 (919THI, R22-07 head), 53.5-58.5 (PROCEED) | spec | medium | Wishon, PROCEED |
| Face width | 105 mm | 105-106 | spec | medium | Wishon |
| Head depth (front-back) | 112 mm | 111-113 | spec | medium | Wishon |
| Heel-toe length | ~120 mm (estimate) | <=127 rule | rule / estimate | low | USGA |
| Face-centre height soled | ~30 mm (estimate) | ~27-33 | derived (not published) | low | from face height |
| Head mass | 200 g | 192.7-203.4 (rule36 n=21), 202 (919THI), 203 (G440 MAX) | measured / spec | high | rule36.net, Wishon, PING |
| Loft / lie | 10.5 / 58.5 deg | 9-12 / 58-59 | spec | high | PING, Wishon, PROCEED |
| MOI vertical axis (Izz) | 4500 g cm2 | 3895-5104 (rule36, 2005-10 Callaway), 5004-5025 (919THI), <=5900+100 rule | measured / spec / rule | medium | rule36, Wishon, USGA, Tutelman |
| MOI horizontal (heel-toe) axis | 3000 g cm2 | 2000-3900 (1/2-2/3 of Izz) | model | low | Tutelman GE3 |
| CG depth behind face | 40 mm | 36.3-45.2 (rule36); 35-38 (PROCEED) | measured / spec | medium | rule36, PROCEED |
| CG height | 31 mm | 29.8-33.4 (rule36; reference plane UNKNOWN, not stated on page) | measured | medium | rule36 |
| CG distance from shaft axis | 35 mm | 29.5-41.5 (rule36); 38-41.5 (PROCEED) | measured / spec | medium | rule36, PROCEED |
| Face progression | 20 mm | 17.5-22.3 | measured / spec | high | rule36, PROCEED, Wishon |
| Shaft axis to face centre (heel-toe) | ~35 mm (estimate) | 29.5-41.5 | derived (= CG distance) | low | rule36 |
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
| face-centre height at address | 49.9 mm (Trainer: 50) | ~30 (estimate) |
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
