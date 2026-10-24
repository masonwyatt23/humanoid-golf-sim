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

## Orchestrator decision (Oct 24, 2026)
- Realistic-head crown-tee rows are labelled 'realistic head, crown tee (equator at sourced crown)'. Box crown-tee rows keep 'compensates for the oversized sim head'. The default-tee pass requirement stays.
- K33 and K34 are scored on BOTH heads (box and realistic) until harness v4.
- Harness v4 will follow the Trainer's v4 address solve (lie 58.5 deg, swingweight compensated, realistic head), with a single re-baseline at that point.
- K34 drops face_h 0.053 and tee_dz 0.020 (Trainer), so the realistic head's own 54 mm face (27 mm edge) applies.

## Follow-up: Data Agent driver-face-centre-height @ 857e373 (Evaluator, 2026-10-24 ET)
Sources re-opened: US 12,649,090 B2 on Google Patents (Tables 3-4 text, CFZ definition, claim 1); USGA TPX3004 Rev 2.0 (usga.org PDF, sec. 2.1b template);
USGA Pendulum Technical Description Report sec. 2.2 (usga.org, 2.1 mm at 99%); First Call 2023-03-02 (Tour Edge "5600 g/cm2"); MyGolfSpy tee test ("measured from ground level").
Table 3 values quoted correctly (aggregated across the patent examples, as in the refs): CGZ -10..0 mm (narrowest -4..-3); ZUP 18-30 mm (narrowest 23-27); CFZ 35-45 mm (narrowest 38-40); IZZ 480-700 kg mm2 (narrowest 560-600); claim 1 Zup 20-28, Izz 560-700.
1. Face-centre height. Route A (Zup - CGZ, both ground-plane/CF frame, head soled) correct: 21-35 (wider band), 26-31 (narrowest band). Route B has an error: Wishon/PROCEED face height and the
   patent's effective face height are face DIMENSIONS (lowest to highest face point), not top-of-face heights above ground. Correct: centre = low + h/2 = (2..6) + (50..58.5)/2 = 27-35.3
   (crown cross-check: (2..6) + (53..61.5)/2 = 28.5-36.8). Overlap A (narrowest band) with corrected B = 27-31; 29 survives. Routes share the patent (Zup/CGZ and lowest-face-point 2-6): only partly independent.
   Frame: 29 is above GROUND; env face centre is 30 above SOLE + 2 mm sole clearance = 32 above ground, so the env is 3 mm high (not 1). Same swing: dz +~3 mm; ball at address 23.5 -> ~26.4 mm up the face (edge 27).
2. CFZ 39: definition (CF projected along y onto vertical shaft-axis plane, shortest distance to shaft axis) matches the env's perpendicular-in-shaft-plane offset. Env 35 -> 39 moves the face centre ~4.8 mm toe-ward (4/sin 56).
3. Heel-toe ~120: estimate; env uses it only for the floor-collision shell. Immaterial.
4. Izz 5600: single published manufacturer claim (n=1, one head; Tour Edge 2023 press release), attributed, not measured or a multi-model aggregate; verified (unit printed g/cm2). Patent axis = CG z perpendicular to ground with head soled, face angle 0; a 1.5-4 deg lie difference vs the rule's 60 deg cannot explain values above 5900+100, so the patent band's upper part is simply beyond the rule cap.
5. Tee: 38.1 + 21.335 = 59.435 mm (env default 59.87, +0.43). Equator 2.6 mm below a 62 mm crown on a soled head; in the env (2 mm clearance) 4.13 mm below the 64 mm shell top.
