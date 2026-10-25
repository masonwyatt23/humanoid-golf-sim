# Wrist and elbow targets at top of backswing and impact

Machine-readable: `data/references/wrist_elbow_event_targets.json` (built by `python -m data.wrist_elbow_event_targets`, tests in `tests/test_wrist_elbow_event_targets.py`).
All Mason numbers are **UNVERIFIED** monocular video proxies (MediaPipe world landmarks, ~30 fps source). They are not measured joint angles.
Provenance: the Mason clips are derived from Mason's own screen-recorded social-media feed video; use of that data in a release needs Mason's consent (not yet given).
> **Correction (PureGolf Data Agent finding, unverified):** the sign convention claim in this doc ("cocked is negative in the env") is wrong; per the Data Agent's forward-kinematics analysis, cocked is positive in the env. See `docs/WRIST_SIGN_MAPPING.md`.
Nothing in `env/`, `eval/`, `train/` was changed; the v3/v4_power XMLs were only read.

## 1. Biggest finding: arm roles do not match
- The env uses `right_*` = **trail (club) arm** and `left_*` = **lead arm** for both handednesses (`docs/HANDEDNESS.md`, which also says a left-hander's physical right limbs belong in the `left_*` columns).
- Mason's 11-column files store the **anatomical right** arm in cols 2/3 (`joint_convention` string in the npz, `data/process_video.py`). For Mason (left-handed) that is the **lead** arm. So the reference `right_elbow` / `right_wrist` columns that a name-matched reward compares with env `right_elbow` / `right_wrist` are Mason's **lead** arm against the env's **trail** arm.
- CMU and MultiSense cols 2/3 are the **trail** arm (`data/convert_cmu_mocap.py` (held locally): `T` is the trail side). So the unified set mixes roles: CMU/MultiSense are role-correct, Mason is not.
- I confirmed this by reading code and docs. I did not run the env or the reward.
- The trail arm (anatomical left for Mason) is not in the 11 columns. This job recomputes it from the stored 33-landmark world track with the same formulas as `landmarks_to_joints`. The lead arm values reproduce the stored columns within a few degrees (cross-check fields in the JSON), which supports the formula port.

## 2. Clips and events
- **Best clip: `mason_v2_p1_s06`, quality_score 0.756**, oblique view. Rule: highest `quality_score` among recommended, native, verified-left, non-partial, unflagged, non-flip-edit clips. `mason_v2_report.json` has an empty `clips` list, so scores come from the npz files. The requested `p1_s05` (0.662) is reported alongside. Runner-ups: p1_s03, p1_s04, p2_s01, p2_s02, p2_s11, p2_s13 (all down-the-line).
- Higher scorers excluded: `p3_s09_unmirrored` 0.83 (caption-flagged flip edit), p2_s05/p2_s08/p3_s08/p3_s09 (handedness detected right), `p1_s11` 0.756 (handedness unverified, excluded in unified_v2).
- **Event times:** `events_of()` = `t_top - t_start_in_video - axis_offset` (offset recovered per file, ~0.4 s for most clips, 0 for p1_s06). The audit's `get_events()` form (`t - t_start_in_video` only) is stored as `events_naive_s`. It lands 0.15-0.47 s later than the real frame on 7 of 8 clips, so it samples the wrong frames. For p1_s06 the two agree.
- Values are the median of landmark frames within ±0.03 s of the event, gated on landmark visibility > 0.5. Frame counts per event (1-3) are in the JSON. They are thin, especially at impact.

## 3. Targets (best clip p1_s06, degrees / radians, env convention)
Elbow flexion = 180 − interior(shoulder, elbow, wrist), ≥ 0. Wrist = 180 − interior(elbow, wrist, index-finger landmark), ≥ 0 and **unsigned**.

| event | env joint | role | deg | rad | limits v3 / v4_power |
|---|---|---|---|---|---|
| top | right_elbow | trail | 64.5 | 1.126 | 0..150, in range |
| top | right_wrist | trail | 40.3 | 0.703 (env value **−0.703 if cocked is negative**) | ±120, in range |
| top | left_elbow | lead | 44.7 | 0.780 | −10..150, in range (passive, no motor) |
| top | left_wrist | lead | 10.7 | 0.187 | no env joint |
| impact | right_elbow | trail | 48.9 | 0.853 | in range |
| impact | right_wrist | trail | 56.0 | 0.977 (sign unknown) | in range |
| impact | left_elbow | lead | 48.5 | 0.846 | in range (passive) |
| impact | left_wrist | lead | 49.1 | 0.857 | no env joint |

No value is outside the env limits. Wrist sign is the open question (section 5, H2).

**Spread across 8 clips** (p1_s05, p1_s06 and the six runner-ups; single-view, n = 8, not a population estimate):

| quantity | median | range |
|---|---|---|
| trail elbow at top | 89.3 | 64.5-96.3 |
| trail elbow at impact | 101.8 | 48.9-121.8 |
| trail wrist at top | 32.0 | 23.5-40.3 |
| trail wrist at impact | 40.2 | 24.8-64.7 |
| lead elbow at top | 47.9 | 39.1-59.8 |
| lead elbow at impact (n = 7) | 57.4 | 48.5-71.8 |
| lead wrist at top | 13.8 | 10.7-15.4 |
| lead wrist at impact (n = 7) | 44.0 | 38.1-68.1 |

p1_s06 (oblique) differs from the down-the-line clips: trail elbow at top is 64.5 vs 80-96 in most down-the-line clips (p1_s04 is 69), and at impact 48.9 vs 91-122 in most (p2_s11 is 72). Treat view as a confounder. The user-default `p1_s05` rows are in the JSON (`env_targets_user_default_clip`): trail elbow 90.4 / 105.3, trail wrist 30.2 / 37.0.

**Lead arm at impact** often fell back to the stored 11-column proxies because landmark visibility failed (`source` field per event).

## 4. Reference medians at the same events (trail arm, file-axis events)
| set | event | elbow flexion median (range) | wrist col 3 median |
|---|---|---|---|
| CMU subject 64, n = 10 (acknowledgment required, keep **needs_counsel**, no standalone redistribution) | top | 109.5 (107.2-114.7) | −70.8 (−85.2 to −63.0) |
| | impact | 56.2 (47.7-67.0) | −54.9 (−65.2 to −47.3) |
| MultiSense mirrored, n = 28 (**needs_counsel**, analysis only, do not publish) | top | 80.7 (68.6-102.6) | **not measured** (zero-filled) |
| | impact | 38.3 (19.9-54.1) | **not measured** |

- CMU is slow recreational mocap (tempo ~1.7) and uses the index-finger bone, so it is not like-for-like with Mason's landmark index.
- Mason's trail elbow at top (median 89) is below CMU (110) and above MultiSense (81). The impact values are higher for Mason (102 vs 56 / 38), so the trail arm is still bent at his detected impact. That may be an event-timing artifact (impact is detected ~0.067 s early vs hand low point).

## 5. Published biomechanics already in the repo
No numeric elbow or wrist angle at top/impact was found in the repo docs or `pro_swing_profiles.json`, and I did not fetch any. Do not use any invented range.
- Wrist release starts when the lead arm is ~30° below horizontal; wrist torque adds ~9% club speed in a 44 m/s simulation; wrist ~70% of linear club speed (Hume, Keogh & Reid 2005 quoting Sprigings & Neal 2000 and Milburn/Neal; https://pubmed.ncbi.nlm.nih.gov/15896091/). Secondary quotes, **unverified**.
- Wrist cock was the strongest of 15 club-speed predictors, 60.3% of variance (Robinson via Hume, same URL). Secondary.
- Arm→club gain 1274 deg/s (Cheetham 2008, https://www.academia.edu/5572510/Comparison_of_Kinematic_Sequence_Parameters_between_Amateur_and_Professional_Golfers). Wrist-only uncock speed is **unverified** (`docs/research_350yd_profile.md`).
- Forward-dynamics models use wrist torque ~90 N·m (from `docs/research_sim_realism.md`, search-snippet quality, unverified).
- Bryson: small lead-wrist hinge, qualitative (GOLF.com, Manzella, in `pro_swing_profiles.json`).
- Edinburgh DataShare wrist data (doi:10.7488/ds/3823) has wrist angular velocity, but it is gated and its license is unread.

## 6. Why the v3 wrist may never follow the reference (hypotheses, none run)
Env facts (read from XML, before any `force_scale`; the committed v3 and v4_power configs run `force_scale` 2.0, i.e. v3 at force_scale 2 = hypothetical-strength actuators, not stock): v3 right_wrist range ±120°, damping 2.0, peak torque 3 × 20 = 60 N·m. v4_power: damping 0.5, peak torque 6 × 20 = 120 N·m. v3 elbow: 120 N·m, damping 2.0. Left elbow has damping 0.5 and no motor. There is no left wrist joint.

- **H1 role mismatch (strongest, from reading code).** The reference `right_wrist` is Mason's lead wrist, while env `right_wrist` is the club-hand trail wrist. A name-matched reward asks the trail wrist to follow a lead-wrist signal: lead wrist ~10° at top and ~45° at impact vs trail wrist ~32° and ~40°. The two arms are not equivalent. Fix by reading the trail arm from this job's JSON, or by swapping the Mason columns in the reference.
- **H2 sign.** Mason wrist is stored as positive magnitude. CMU uses cocked = negative, and `configs/fast_scripted_v3_masonwrist.json` uses `wrist_cock = -0.5` (that config's old 'key 0.88' claim is VOID per the Trainer's Stage 19 notes: lead-arm values were used on trail-arm joints). If env cocked is negative and the reference is positive, the reward pulls the wrist the wrong way at top. At impact the unsigned value is as large as or larger than at top in most clips, so it is probably flexion/bowing, not cock. Use the sign only at top.
- **H3 torque and damping.** The earlier audit finds ~26.5 rad/s of uncock is needed at 130 mph, which leaves 12% of v3's 60 N·m at damping 2 (`docs/research_350yd_profile.md`). Mason's own reference is milder. A bang-bang estimate for p1_s06 (trail wrist 24° → 67° in 0.167 s, Δθ ≈ 0.75 rad) gives peak α ≈ 4Δθ/T² ≈ 108 rad/s². With the doc's club inertia of 0.291 kg·m² that is ~31 N·m plus ~18 N·m damping at peak ω ≈ 9 rad/s, about 49 of 60 N·m. So v3 can hardly follow the clip even at 0.167 s. My own estimate, unverified. Faster targets or any added torque load saturate it.
- **H4 range is not the problem.** Reference wrist magnitudes (≤ 95° in noisy clips, 24-67° for p1_s06) fit inside ±120°. The elbow targets also fit.
- **H5 noisy target.** The index-finger landmark jitters at ~30 fps. Peak wrist rates in the JSON run from 170 to 1850 deg/s across clips (90th-percentile speeds of a noisy signal). Vid2Player3D-style work suggests relaxing wrist tracking weight on noisy video. Track the **top-of-backswing wrist value** (more stable) and not frame-by-frame wrist motion.
- **H6 durations.** Backswing and downswing in these feed clips look compressed (sped-up edit suspected earlier). Following them needs rates the model cannot supply.

**Quickest diagnostic (no training):** replay the p1_s06 trail-arm wrist target as a joint position command on `right_wrist` with the env's PD (v3, then v4_power). Log commanded vs achieved angle, the fraction of steps where the motor is saturated (|ctrl·gear| at its limit), and the sign of achieved motion vs command. Do it twice, once with the reference as stored and once with the sign flipped. A big achieved-vs-commanded gap with a high saturation fraction means H3. A gap that shrinks when the sign is flipped means H2. A non-zero tracking reward that stays flat means H1.

## 7. Caveats
- Left-arm landmarks are often partly occluded in down-the-line views; per-event frame counts are low (1-3).
- Wrist deviation mixes flexion/extension with radial/ulnar deviation and is unsigned.
- Events are detector heuristics; impact is early vs hand low point by ~0.067 s (±0.05).
- MultiSense and CMU stay **needs_counsel**; nothing here is cleared for release.
