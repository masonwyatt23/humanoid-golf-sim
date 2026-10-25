# Wrist sign / zero-offset mapping (reference column -> env `right_wrist`)

Provenance: the Mason v2 clips are derived from Mason's own screen-recorded social-media feed video; use of that data in a release needs Mason's consent (not yet given).

Status: UNVERIFIED. Video proxies (MediaPipe, ~30 fps, v2 clips only) plus static forward kinematics of the env XML. Nothing was trained or changed in env/, eval/, train/. Reproduce: `python data/wrist_sign_mapping.py` -> `data/references/wrist_sign_mapping.json`; tests: `tests/test_wrist_sign_mapping.py`.

## Answer
The stored trail-wrist impact 0.977 rad is the wrong number for the env, for two reasons: (1) it is a hand-vs-forearm *deviation magnitude* with an arbitrary zero, not a club angle; (2) the env wrist zero is a 90° L, not a straight line, so the ref zero and env zero differ by a large offset.

**Corrected mapping** (tolerance about ±0.15 rad, confidence low-to-medium):

| Source column | env_wrist_rad = |
|---|---|
| Mason v2 col 3 (unsigned, >=0; trail arm recomputed from landmarks) | **+1 · ref_rad − 1.31** |
| CMU col 3 (stored cocked = negative) | **−1 · ref_rad − 1.31** |
| MultiSense | none (wrist zero-filled, not measured) |

Because contact depends jointly on elbow and wrist, the better target at impact is the geometric condition **w_contact ≈ 0.173 − 0.564 · elbow_rad** (±0.1 rad, elbow 0–1.13 rad, v3 and v4_power identical).

## Evidence
(a) **Mason** (`data/process_video.py:168`): `wrist = 180 − angle(elbow, wrist, index)` (unsigned arccos, 0..180). 0 = straight forearm-hand line (interior 180°). It is a 3-D hand deviation that mixes flexion/extension and radial/ulnar deviation, so sign cannot be recovered from it. Event columns for Mason v2 are the anatomical RIGHT arm = LEAD arm for a lefty; the trail (club) arm values in `wrist_elbow_event_targets.json` were recomputed from landmarks.
(b) **CMU** (`data/convert_cmu_mocap.py:212-213` (held locally)): same 180 − interior formula, then `col3 = −dev` ("cocked = negative"). CMU trail medians: top −70.8°, impact −54.9° (magnitude falls toward impact, as true cock/uncock would). So CMU's stored sign is the **opposite** of the env's cocking direction.
(c) **MultiSense** (`convert_multisense_golf.py:79` (held locally)): wrist column is zeros; nothing to map.
(d) **Env** (`humanoid_golf_v3.xml` / `v4_power.xml`, identical geometry): the wrist is a hinge about +y; forearm runs along local +x, the club shaft along local −z. Computed by MuJoCo FK: interior(forearm, club) = 90° − w (deg): w=0 → 90° (L), w=−π/2 → 180° (club collinear with forearm), w=+π/2 → 0° (folded back). So **positive env w = club folded toward forearm (cocked); negative = straightening**, and **env zero is NOT straight; it is a pre-cocked 90° L.** The earlier assumption "cocked = negative in env" (carried from the CMU sign and the `wrist_cock=-0.5` configs) is inverted relative to the geometry; those configs work only because −0.5 happens to sit near the contact window.
Hinge torque: the env's own PD/ref code reads the ref column by position only, with no sign handling for Mason.

Why +1 for Mason: a larger hand deviation d means a smaller forearm-shaft interior I = 180 − (d + c0), so env w = 90 − I = d + c0 − 90°. The offset is c0 − 90°, with c0 the (unmeasured) static shaft-vs-hand angle.

## Offset from contact geometry (the experiment, run here)
Method: MuJoCo, torso pinned, ball at the env reset position (0.43, 0, 0.021), shoulder at (0.15, 0, 1.16). At fixed elbow and wrist, sweep shoulder pitch (−1.6..2.6) and take the minimum club-head-centre to ball-centre distance; "contact" = ≤0.06 m (head half-extent 0.05 + ball radius 0.021; box so approximate).

| elbow rad | best wrist rad | contact window (≤0.06 m) |
|---|---|---|
| 0.000 | +0.16 | +0.06..+0.26 |
| 0.349 (env reset) | −0.02 | −0.12..+0.08 |
| 0.420 | −0.06 | −0.16..+0.04 |
| 0.650 | −0.18 | −0.30..−0.08 |
| 0.853 (Mason s06 impact) | −0.30 | −0.42..−0.20 |
| 0.981 (CMU median impact) | −0.38 | −0.50..−0.28 |
| 1.126 | −0.48 | −0.60..−0.36 |

The stored +0.977 gives min distance 0.53 m (elbow 0.349) and 0.64 m (elbow 0.853): no contact. −0.977 also fails (0.41 / 0.29 m). The offset needed to put Mason s06 impact (0.977) in its window: −1.277; the same fit on CMU's median impact: −1.338. They agree within 0.06 rad (independent data and sign convention), mean −1.31, implying c0 ≈ 15° (plausible for a shaft-hand angle, but unmeasured).

## Per-clip impact values under the mapping (Mason v2, handedness verified left)
env = ref + (−1.31). "window" = contact window at that clip's own impact elbow.
Clips whose impact elbow is 1.6–2.1 rad (91–122°) look suspect (the s06 value is 0.85); treat their rows as low confidence.

| clip | ref top | ref impact | impact elbow | env top | env impact | window at that elbow | inside |
|---|---|---|---|---|---|---|---|
| mason_v2_p1_s03 | 0.538 | 0.433 | 1.909 | -0.77 | -0.875 | -1.20..-0.84 | yes |
| mason_v2_p1_s04 | 0.585 | 0.967 | 1.716 | -0.723 | -0.341 | -1.04..-0.72 | no |
| mason_v2_p1_s05 | 0.527 | 0.646 | 1.838 | -0.781 | -0.662 | -1.14..-0.80 | no |
| mason_v2_p1_s06 | 0.703 | 0.977 | 0.853 | -0.604 | -0.33 | -0.42..-0.20 | yes |
| mason_v2_p2_s01 | 0.586 | 0.588 | 1.597 | -0.721 | -0.72 | -0.94..-0.64 | yes |
| mason_v2_p2_s02 | 0.538 | 0.606 | 2.126 | -0.77 | -0.702 | -1.42..-0.98 | no |
| mason_v2_p2_s11 | 0.41 | 0.757 | 1.257 | -0.898 | -0.55 | -0.68..-0.44 | yes |
| mason_v2_p2_s13 | 0.579 | 1.129 | 1.967 | -0.728 | -0.179 | -1.26..-0.88 | no |
| CMU median (trail) | n/a | n/a | 0.981 | -0.072 | -0.35 | contact wrist -0.38 | yes |

Best clip `mason_v2_p1_s06`: env top −0.60 rad, env impact −0.33 rad (window −0.42..−0.20; best −0.30).

## Caveats
* Static FK only: no dynamics, free shoulder pitch, torso pinned. In the sim the PD wrist lags: a −0.01 command at impact was at about −0.19 when contact occurred, so command a bit earlier or stiffer.
* The offset is constrained only by the contact window (about ±0.1 rad wide) and the env's stylised geometry (arm horizontal at pitch 0, club vertical), not by human anatomy. It is a fitted mapping.
* Mason's `d` rises from top to impact in most clips (opposite of true uncocking), so `d` is not pure cock; the +1 sign rests on the geometric argument and the CMU sign flip, not on the Mason data itself. Top-of-backswing env values (−0.6 Mason, −0.07 CMU) are not constrained by any contact test.
* Recipe for the Trainer: at the impact pose set elbow, call `contact_wrist()` in `data/wrist_sign_mapping.py` (or use the linear fit), then drive a replay with `wrist_cock`/`wr_end` at those values and check `true_contact` and the commanded vs achieved angle.
* Mason-derived values here are v2 clips only (self-owned); no Instagram-derived v1 data used. Consent note for Mason's footage still applies.
