# v5 Stage 0 report (no learning): body, env, ball physics, go/no-go

Written 2026-10-17 (America/New_York). Follows `docs/FROM_SCRATCH_SWING_PLAN.md` (763eecd) Stage 0. Raw numbers: `results/v5_stage0.json` (`python scripts/v5_stage0_check.py`, ~20 s). Tests: `tests/test_v5_stage0.py` (11) + `tests/test_golfphys.py` (23).
Labels: **[measured]** this box; **[read]** from a file; **[guess]** my assumption. Nothing pushed; no training launched; v3/v4/g1 envs untouched.

## What was built (new files only)
| File | Purpose |
|---|---|
| `golfphys/` (+`VENDORED.md`, coefficients/validation JSON, doc, tests) | Data Agent's ball model, copied unmodified from branch `golfphys` 0c2bca2 (commit ac77329). |
| `env/v5_body.py` | MjSpec builder from Menagerie `unitree_g1` (BSD-3): 29 actuated DoF (6+6 legs, 3 waist, 7+7 arms = 3-DoF shoulder, elbow, wrist roll/pitch/yaw), free base, foot box soles with friction 1.0 (condim 6) and touch + ankle force/torque sensors, club welded into both hands, IK address solver. |
| `env/models/humanoid_golf_v5_g1_{lh,rh}.xml` | Exported models (`meshdir` relative to the XML, into a MuJoCo Menagerie checkout next to the repo or `$MENAGERIE_DIR`; not vendored). `v5_address_*.json`: solved address poses (LH/RH, club 0.87 and 1.15 m). |
| `env/v5_shot.py` | `env_contact_to_shot` adapter + `verify_toe_sign`. |
| `env/v5_golf_env.py` | Gymnasium env `V5GolfEnv` (112-dim obs, 29-dim action = PD target offsets from address, torque cap + linear speed derate every 5 ms, ball held until first club-head contact, golfphys flight, 5 ms segment logging). Has a `tether` flag (pelvis pinned) for pipeline tests only. |
| `env/v5_reward.py` | Soft-reward scaffolding (ball flight, kinematic sequence, X-factor, weight shift, annealed prior cap). Not tuned, not used for training. |
| `scripts/v5_sanity_swing.py`, `scripts/v5_stage0_check.py` | Pipeline-only trunk-sweep motion and the check suite. |

## Design decisions and honest flags
1. **Club length 0.87 m, not 1.15 m (gate G0 outcome).** A 1.15 m club is kinematically reachable on G1 (hand error 0.05 mm) but only with the waist pitch at -0.47 rad of a -0.52 limit, pelvis pitched back, lead elbow nearly straight: no range left to swing. 0.87 m = a 1.17 m driver scaled by G1/human height (1.32/1.78 = 0.74) gives a natural address (waist pitch 0.00, knees 0.85 rad). **Consequence: a shorter club lowers head speed for the same joint rates, so the plan's 100 mph target is harder on this body**; the 1.15 m address is saved (`v5_address_*_115.json`) if wanted. The env takes `club_len`.
2. **Stock torque = Menagerie `actuatorfrcrange`, force_scale 1 [read, verified in code and a test against the base model]:** hip pitch/yaw 88, hip roll 139, knee 139, ankle 50 (this resolves the plan's ankle "guess": the XML says 50), waist yaw 88, waist roll/pitch 50, shoulder/elbow/wrist roll 25, wrist pitch/yaw 5 N*m. Rated speeds are from the plan table (published, not re-fetched; ankle 37 and waist roll/pitch 20 rad/s are **[guess]**).
3. **Grip.** Two site-to-site welds (lead hand on top, trail hand 0.11 m below), solref 0.004. MuJoCo makes the two site frames coincide, so the grip sites are oriented from the IK solution (hand orientation on the club is whatever the solution gives; it is not a realistic palm wrap **[limitation]**). No finger model.
4. **Collisions:** only soles-floor, club head-floor and head-ball. No body self-collision and no club-body collision (reward terms must use distances if wanted) **[limitation]**.
5. **Left-handed = physical mirror.** Golfer faces +y, target is +x, lead arm = physical right (verified: right shoulder x > left, lead hand higher on the shaft). A right-handed build (`handed="RH"`) exists for the mirror test.
6. **Club head sits on the ground at address** (supports ~15 N, 4.6% of weight), as a real sole would.
7. **Stock wrist limits are binding [measured]:** in crude arm-lift swings the 5 N*m wrist pitch deflected 0.3-0.6 rad against the club, and the unpinned robot lost balance (pelvis z fell from 0.74 to 0.4-0.6 m within ~1.5 s). That is the real learning problem, not a bug I could find; it is why the sanity motion is trunk-only.

## Verification [measured unless stated]
| Check | Result |
|---|---|
| Model loads | nq 50, nv 47, nu 29, 33 bodies, 2 welds, 13 sensors, mass 33.69 kg (G1 33.34 + club 0.30 + ball 0.046) |
| Stock limits | all 29 joint torque limits equal Menagerie (test) |
| PD hold, zero action (action 0 = address pose), 2 s, dt 0.0005/0.001/0.002 | no fall; pelvis z 0.741 -> 0.737; foot slip 0.32 mm; weld drift 0.04 mm; 5 s hold at dt 0.001 also stable (slip 0.68 mm) |
| Passive (zero torque) | collapses at 0.28 s (expected: unactuated G1 cannot stand) |
| Ground reaction at rest | feet 95.3% of weight, feet + club head on floor 99.9% (touch sensors agree: 95.3% feet). Within the plan's +-5% for total ground force; feet-only alone is 4.7% low because the club head carries 15 N. |
| Weld/grip drift | < 0.05 mm holding; <= 0.8 mm during the trunk sweeps (limit 5 mm) |
| Mirror, G1 kinematics | random 20 poses, L/R swap + roll/yaw sign flip: max body-position mirror error 1e-5 m |
| Mirror, LH vs RH addresses | max joint diff 0.0007 rad, club pose mirror error 0 m |
| Toe sign vs club XML | head-box local +y is the toe in both LH and RH builds, so **toe_sign = +1** (cos 0.993 with golfphys' horizontal toe) |
| Flight mirror through the adapter | LH vs mirrored RH: carry equal to 1e-6, lateral negated, backspin equal, for centre, toe, high and toe+high strikes |
| Contact detection | detects head-ball contact at dt 0.0005, 0.001 and 0.002 on the trunk sweeps; ball velocity/spin written from golfphys |
| Pipeline-only sweep (tethered and unpinned) | contact in 3/4 (tethered) and 4/4 (unpinned) variants, 3-21 mph club speed, 4-27 mph ball speed, carry 0.2-1.0 m (no roll). **Not a swing and not a performance number.** |
| Throughput under load (box load ~5-6/8 cores, random actions, full env) | dt 0.0005: 460-480 steps/s; dt 0.001: 830-845; dt 0.002: 1460-1480 control steps/s (one core) |
| Reward scaffolding | terms evaluated on a recorded sweep and on a synthetic ideal sequence (unit test); prior cap 0.20 at progress 0, 0.05 at progress 1; stage A prior total is 0 |

## Findings about the vendored golfphys (reported, not edited)
**LH sign bug in `impact_vec`:** the face-up axis `toe x n` points DOWN for a left-hander, so a high-face strike gives 4053 rpm backspin for LH versus 1716 for the same strike RH (should be equal), and the bulge tilt launches LH high strikes lower. Toe/heel (sidespin, start line) is mirrored correctly. The env adapter compensates by negating the high-offset for LH (verified by the mirror test); the package itself should be fixed by the Data Agent. Also: `env_contact_to_shot` takes `club_vel` only (no head angular velocity); the env passes the face-centre point velocity from MuJoCo (includes rotation), measured just before the contact substep.

## Go / no-go for Stage A
- **Go (conditional):** model builds, stands 2-5 s under PD, club welded (<0.05 mm), mirror checks pass, toe sign verified, contact + golfphys pipeline works, ball is not computed by the old env formulas.
- **Conditions / blockers:**
  1. Throughput is under the plan's >= 600 steps/s only at dt 0.0005 (about 470 under load; an idle core was not available to re-measure). Use dt 0.002 (1470/s) for Stage A and re-validate at 0.001 and 0.0005; contact detection agrees at all three on the sweeps, but head speeds there were only <= 22 mph, so **tunnelling at 100 mph (4.5 cm per substep at dt 0.001, 9 cm at 0.002) is untested**. Add a swept-segment contact test before trusting dt 0.002 for fast swings.
  2. Balance under a real swing is open: the unpinned robot fell with arm-lift motions. Stage A needs the plan's curriculum (pelvis tether -> free) and a foot-friction randomisation; the tether flag exists.
  3. Club 0.87 m vs 1.15 m must be decided by the user/Orchestrator (head-speed implications above).
  4. Vendored golfphys LH bug should be reported to the Data Agent (adapter workaround is in place and tested).
  5. Spec numbers (segment speeds, X-factor window, weight-shift target) remain unverified extrapolations; priors stay soft and capped. No private reference data is read or committed (test enforces no references in the new files).
