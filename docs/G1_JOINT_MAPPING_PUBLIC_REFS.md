# Rough G1 mapping of the public joint references (+ velocities and planar decomposition)

Files: `data/references/g1_joint_mapping_public_refs.json` (generator `scripts/gen_g1_joint_mapping_public_refs.py`), `data/references/public_joint_velocities_110plus.json` (`scripts/gen_public_joint_velocities_110plus.py`), `data/references/planar_swing_decomposition_public_refs.json` (`scripts/planar_swing_decomposition.py`). Tests: `tests/test_g1_addendum.py`.

**Status: ROUGH.** Joint names, ranges and actuators were READ from `env/models/humanoid_golf_v5_g1_{rh,lh}.xml` and `humanoid_golf_v4_power.xml` (read-only). Axes and signs were checked by forward kinematics (read-only MuJoCo FK, G1 frame +x forward, +y left, +z up). The correspondence between a published human angle definition and a G1 joint is an assumption unless marked otherwise. All curves are synthetic interpolations (see `PUBLIC_JOINT_TRAJECTORIES_110PLUS.md`); no Instagram, CMU, MultiSense, AMASS or GolfDB data.

## Velocity channels (item 1)
`public_joint_velocities_110plus.json`: for every channel and speed class (110/120/130 mph), `velocity_deg_s` = central finite difference of the existing angle curves (10 ms grid), plus the generator's analytic speed for comparison, the cited peak speeds/timings (Madrid 2020, Cheetham 2008, Zheng 2008a, kseq-v2 slopes) and the peak used by the generator. Labelled DERIVED and SYNTHETIC. The 10 ms finite difference smears sharp peaks: at 110 mph the fd peak is 1-3% below the generator's (pelvis 390 vs 391, thorax 706 vs 708 deg/s, lead wrist 1066 vs 1095, trail wrist 1160 vs 1187). Sign = sign of d(angle)/dt (arm-to-trunk and elbow flexion decrease in the downswing, so their velocity is negative). The x-factor velocity is thorax minus pelvis.

## G1 joints (v5 env; all 29 joints actuated)
| Human channel | G1 joint (physical side by role) | Rule | Status |
|---|---|---|---|
| X-factor (thorax - pelvis) | `waist_yaw_joint` (range +-2.618) | RH: yaw = +x_factor, LH: -x_factor (G1 yaw + = CCW from above) | sign UNVERIFIED in a run; magnitude fine |
| Pelvis rotation | none (free-base yaw; hips + ground) | world yaw about address heading, RH +, LH - | UNVERIFIED; no pelvis joint in v5 |
| Waist pitch / roll | `waist_pitch_joint`, `waist_roll_joint` (+-0.52) | no public channel; pitch + = forward lean, roll + lifts G1-left shoulder (FK) | no reference |
| Arm to trunk | `*_shoulder_pitch_joint` (-3.09..2.67) | pitch = -(elevation - 5 deg); roll=yaw=0 | UNVERIFIED (Zheng definition and plane) |
| Shoulder roll / yaw | `*_shoulder_roll_joint`, `*_shoulder_yaw_joint` | carry plane tilt; no public channel | no reference |
| Elbow flexion | `*_elbow_joint` (-1.047..2.094) | q = (80 - flexion)/55 rad (FK fit; flexion non-monotone above q~1.4) | ROUGH, +-~10 deg |
| Wrist set / hinge | `*_wrist_pitch_joint` or `*_wrist_yaw_joint` (+-1.614; stock 5 N*m); `*_wrist_roll_joint` (+-1.972, 25 N*m) is forearm roll | hinge magnitude w = 90 - interior (lead 71 deg release) | joint choice and sign UNVERIFIED; use magnitude and timing |

Unactuated joints: none in v5. In the older `humanoid_golf_v4_power.xml` the lead `left_elbow` and `left_shoulder_roll` have no motor (and there is no lead wrist, no pelvis yaw; the trunk joint is `chest_yaw` +-60 deg, so use the x-factor channel there).

**Role vs side conflict.** `docs/HANDEDNESS.md` and the trajectory file say env `right_*` is the TRAIL arm. That is the old simple/v4 convention. In v5 the model uses physical G1 sides: for the LEFT-handed golfer the physical right side faces the target, so `right_*` is the LEAD arm (`env/v5_body.py lead_trail`). Always pick the side through `lead_trail(handed)`.

## Left-handed mirror rule
Keep references in golfer roles. Yaw and roll joints (waist yaw/roll, shoulder roll/yaw, wrist roll/yaw) change sign between handedness (and between the two physical sides of one body; the v5 XMLs already mirror the right-side roll ranges); pitch joints (shoulder pitch, elbow, wrist pitch, waist pitch) do not. Pelvis, thorax and X-factor references (RH convention, + toward target) are negated for LH. Do not negate twice when an env already flips `chest_yaw` (old env). Not exercised in a training run.

## Reduced planar decomposition (item 3)
Chain (lead side, rates toward impact): `club_in_plane ~ trunk_in_plane + arm_swing + wrist_hinge + unexplained`.
- **Trunk:** the thorax angle is assumed to be a top-view projection of the shoulder line. Convert to rotation about the tilted spine axis, `psi = atan2(sin(psi_v)/cos(theta_s), cos(psi_v))`. The swing-plane normal is tilted phi from vertical, so the in-plane share is `cos(phi - theta_s)`; the remainder pitches the plane. ASSUMED theta_s = 35 deg, phi = 55 deg (share 0.94; sensitivity table in the JSON, 0.77-1.0 for 25-45 / 45-65 deg). Pure geometry.
- **Arm swing:** minus the rate of lead arm-to-trunk elevation, in-plane share assumed 1.
- **Wrist hinge:** rate of the lead wrist set angle (uncocking).
- Concept only is cited: Nesbit & Serrano 2005, J Sports Sci Med 4:520-533 (alpha main swing / beta plane pitch / gamma shaft roll) and Nesbit 2005, J Sports Sci Med 4:499-519 (downswing not in one fixed plane; hands vs clubhead planes differ about 9-12 deg). None of the numbers come from them.
- **Result at 110 mph:** in-plane angle swept top to impact: trunk 124 deg (50%), arm 55 deg (22%), wrist 71 deg (28%). Chain peak 2110 deg/s at 30 ms before impact (trunk 722, arm 322, wrist 1066) against a published club peak reference of about 2353 deg/s (Madrid 2020 anchor via kseq-v2): 0.90. The gap is hand translation, girdle and pelvis motion and mismatched definitions; it was not tuned, and the closeness is partly luck of the assumed ratios.
- G1 carriers: trunk = waist yaw (+pitch/roll to tilt the plane) plus pelvis yaw; arm swing = lead shoulder pitch (+roll/yaw to follow the plane) and elbow; hinge = lead wrist pitch or yaw (UNVERIFIED). Because waist_pitch is distal to waist_yaw in the G1 chain, waist yaw rotates the (forward-bent) torso about the pelvis vertical, not the spine axis: a spine-axis rotation needs yaw plus compensating pitch/roll (first-order only).

## Weak spots
1. Human angle definitions (Zheng) are secondary-source and unverified; the arm and wrist mappings inherit that.
2. Wrist hinge joint (pitch vs yaw) and sign unverified; the 5 N*m stock wrist torque limit was binding in earlier v5 tests.
3. Spine tilt and plane inclination are assumed; the in-plane share is sensitive to the difference only.
4. No references for waist roll/pitch or shoulder roll/yaw; pelvis has no v5 joint.
5. Velocity channels inherit all weaknesses of the synthetic curves (arm/elbow/wrist peaks use ASSUMED 109 mph reference).
