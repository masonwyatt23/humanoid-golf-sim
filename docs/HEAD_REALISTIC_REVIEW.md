# Review: Trainer a9d917e realistic driver head (`--head realistic`), Evaluator, 2026-10-24 ET
Read-only export of Trainer a9d917e. Probes: V5GolfEnv(club_len 1.15), reset seed 0, address pose.

| item | JSON (Data Agent bf9827b) | env measured | status |
|---|---|---|---|
| face height x width | 54 (range 50-58.5; no single head at 54) x 105 | face_limits 27.0 / 52.5 mm | OK; 54 is a chosen nominal, not one head |
| face-centre height above sole | ~30 ESTIMATE (low conf.) | 30.0 (32.0 above ground, 2 mm sole clearance) | matches, but UNSOURCED estimate; it controls strike dz |
| crown above sole | 62 (PROCEED 60-63.5) | shell 2.0 -> 64.0 mm above ground = 62.0 | OK |
| loft | 10.5 | 10.5 deg | OK |
| lie | 58.5 | 56 (kept) | documented compromise |
| FP | 20 | face centre 14.4 mm ahead (FP - 30 tan 10.5) | OK |
| CG depth / height / shaft dist | 40 / 31 / 35 | 39.1 along face normal (40 horizontal) / 31.0 above sole / 35 | OK (CG height reference plane unknown in rule36) |
| face-centre to shaft heel-toe | ~35 ESTIMATE (= CG distance) | 35 | unsourced estimate |
| heel-toe length | ~120 ESTIMATE | shell 120 | unsourced estimate (floor collisions only) |
| Izz / Iv | 4500 / 3000 (Iv low conf.) | mass box 112x120.2x73.9 -> 4499 / 3000 g cm2 | OK |
| mass | 200 | 200 g, club 300 g | OK; swingweight +1.8% documented |
| ball shift | - | x -29.81 mm, y +18.97 mm | matches Trainer (29.8 / 19) |
| default tee | - | ball centre 59.87, bottom 38.53 mm | matches |
| crown tee | equator at crown | tee_dz 4.135 mm, ball centre 64.0, bottom 42.67 mm above ground (40.67 above sole; JSON derived 40.7) | consistent |
| box head | - | strike_log K32a 200k byte-identical pre (569518e) vs a9d917e | confirmed |

Strike-height note: at address the default-tee ball centre is 27.9 mm above the face centre vertically, 23.48 mm along the face-up axis
(crown tee 27.55 mm, beyond the 27 mm face half-height). So a head returning to its soled address height would strike high/off-face; the
measured strike depends entirely on how high the policy brings the head at impact (K32a nominal: box dz -10.8, realistic default -2.4, crown +1.7 mm).
Not a geometry bug, but the strike-height row now dominates and the 30 mm face-centre ESTIMATE moves it 1:1.
Realistic-head contact plate envelope is 80 mm tall (top 71.3 mm above ground, bottom 8.8 mm below ground; ball-only collisions): contacts beyond 27 mm become misses via the off-face gate.
Crown tee label: for the realistic head the crown tee is NOT a compensation for an oversized head (default tee is only 4.1 mm below equator-at-crown); label 'realistic head, crown tee (equator at sourced 62 mm crown)'.
Earlier Evaluator ~34 mm peg estimate (unsourced) is superseded: sourced-derived ball bottom 40.7 mm above the sole.
Interaction: K32a args face_h 0.053 overrides the JSON 54 mm face under the realistic head (face_limits 26.5 mm) unless V3_FACE_H=none.
