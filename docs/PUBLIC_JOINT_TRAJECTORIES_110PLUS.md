# Public joint-angle trajectories for a 110+ mph driver swing (synthetic, published keyframes only)

Files: `data/references/public_joint_trajectories_110plus.json`, generator `scripts/gen_public_joint_trajectories_110plus.py`, tests `tests/test_public_joint_trajectories.py`.

**What it is.** A soft-prior reference for the Trainer: joint-angle curves for pelvis, thorax, X-factor, lead/trail arm, lead/trail elbow and lead/trail wrist, on a time-to-impact axis (t = 0 at impact, negative before; grid -0.30 to +0.10 s, dt 0.01 s) and on a normalised downswing phase 0..1 (0 = top of backswing, 1 = impact), for speed classes 110, 120 and 130 mph.

**What it is not.** Not measured curves. No open paper gives a full time-normalised curve for a 110+ mph group. Every channel is `synthetic_interpolation: true`. Values at 120 and 130 mph are extrapolated (the best fully read group is Madrid 2020, 110.4 mph; no joint-angle study above about 112 mph was found).

## Sources (all published; none from CMU, MultiSense, AMASS, GolfDB, or any personal/Instagram-derived swing)

| Key | Used for | Notes |
|---|---|---|
| Madrid et al. 2020, Appl Sci 10(17):5728 (CC BY) | X-factor at top 61 +- 9 deg; pelvis/shoulder-line peak speed 394 / 711 deg/s at -87 / -84 ms; speed at impact 262 / 610; downswing 253 +- 26 ms | 66 skilled males, driver 110.4 mph; numbers via `kinematic_sequence_torque_reference_v2.json` (fetched-full) |
| Cheetham 2014 dissertation (ASU) | pelvis open 41 +- 9, thorax open 27 +- 9 deg at impact; lead forearm-to-club angle 161 deg at impact | 94 tour pros, driver, 108.3 mph; full text read this session |
| Zheng et al. 2008b | pelvis at top 42 +- 7 deg | 25 PGA pros; abstract read |
| Zheng et al. 2008a | arm, elbow, wrist keyframes at top/impact; peak speeds and timing | 18 pros. Abstract read (speeds, trunk 60 +- 7). Top/impact angle table and % timing are **secondary**, read from a lecture-note summary (Lehman 2012) quoting the paper; not checked against the primary table. CHS not reported |
| Cheetham et al. 2008; kseq-v2 'derived' | peak timing cross-check, speed and duration slopes | already in the repo |

## Construction

1. Keyframes: top and impact angles per channel (table in JSON `source_keyframes`).
2. Speed profile: PCHIP through 0 at the top, a ramp `P * s^k` to the cited peak speed P at the cited peak time, then a smoothstep tail to the speed at impact. `k` is solved so the integral equals the cited top-to-impact change. Result: exact keyframe angles, exact peak speed and peak time, monotone angle between top and impact.
3. Plain PCHIP through only top and impact would give peak speed near the mean speed (about 330 deg/s for the pelvis against a cited 394), so it was not used.
4. Before the top: angle held at the top value. After impact: speed decays with tau = 0.05 s (assumed). Both are flagged in `published_support_mask`.
5. Thorax top (-103 deg) is **derived**: pelvis top (-42, Zheng PGA) minus X-factor top (61, Madrid). It mixes two studies and methods. The derived X-factor at impact is -14 deg (closed sign) against Madrid 9 +- 8 deg; the curve shows a small X-factor stretch (about 2 deg), inside the published 1-8 deg range.

## Speed scaling (110 / 120 / 130 mph)

- Angles at top and impact held fixed (ASSUMED; X-factor is not correlated with club speed in homogeneous skilled groups, Kwon 2013 / Parker 2018 via kseq-v2).
- Downswing time T(v) = 0.253 s - 0.0025 s per m/s x (v - 49.35 m/s): 253 / 242 / 231 ms (between-group slope, default). The within-group Madrid slope (-0.00596 s per m/s) gives shorter times, listed as `downswing_duration_s_alt_within` (about 228 and 201 ms at 120 and 130 mph; beyond ~116 mph unsupported).
- Pelvis/thorax peak speed: Madrid anchor plus within-group slope (13.2 and 13.83 deg/s per m/s, regression-diluted lower bounds).
- Arm/elbow/wrist peak speed: linear in club speed from Zheng values with an ASSUMED 109 mph reference. Peak timing: pelvis/thorax fixed ms before impact (ASSUMED); others fixed fraction of the downswing.
- Speed at impact: ratio to peak, Madrid for pelvis/thorax; ASSUMED ratios for the other channels (no published values).

## Right-handed convention and left-hand mirror

- RH: rotation + = toward target (open), backswing negative. Other angles as published.
- LH: express in golfer roles, not physical left/right (`docs/HANDEDNESS.md`). Negate pelvis, thorax and X-factor if the env's own handedness flip is not applied. `ResidualGolfEnv` already negates the `chest_yaw` target for left-handers, so do not negate twice. Planar angles (elbow flexion, wrist set angle, arm-to-trunk elevation): no sign change.
- Env roles: `right_*` = trail arm, `left_*` = lead arm for both hands; +y is the golfer's left for a right-hander.
- Mapping notes (all UNVERIFIED): thorax -103 deg exceeds env `chest_yaw` range (+-60 deg), so the env joint is probably pelvis-relative; prefer the `x_factor` channel there. `w = 90 - interior_angle_deg` (repo note), giving w about -4 deg at top and -75 deg at impact, but the env's own contact solution is w about 0.173 - 0.564 x elbow_rad, so absolute wrist values do not map. Use the release magnitude (+71 deg) and timing only. Lead elbow is unactuated in the simple env.

## Tolerance bands

Published SDs exist only for pelvis, thorax and X-factor keyframes. `sd_angle_deg` interpolates them linearly in phase (derived; between-subject SD, not along-curve). `band_total_deg` adds a time-alignment term 0.026 s x |speed| (Madrid downswing SD). Other channels have no retrieved SD: `sd_angle_deg` is null, and `tolerance_deg_recommended` (20-25 deg) is assumed.

## Recommended soft-reward use (suggestion, untested in any run)

Downswing window only (-T <= t <= -0.01 s), weight 0 outside. Per-step Gaussian `exp(-0.5 (err/tol)^2)`. Keep the total prior at about 0.02-0.05 of the per-step reward and anneal it away once speed at impact and the sequence reward are met. Start with pelvis, X-factor, thorax (or X-factor instead), lead arm, with suggested weights in the JSON. Elbow and wrist channels start at weight 0 or very low because env contact geometry fixes their absolute values.

## Weakest channels

1. `trail_arm_to_trunk`: the cited early peak (52% of downswing) with a 20-deg total change is inconsistent with a high speed at impact; the generator drives impact speed to zero and the ramp is very late (k about 6-10). Single secondary source.
2. `lead_elbow_flexion`: 58 deg at top is unusually large; single secondary source, env lead elbow unactuated.
3. `trail_wrist_angle` and `trail_elbow_flexion`: peaks at 95-99% of the downswing with a cited angle change force an extreme late ramp (k up to about 12; at 130 mph the impact-speed ratio is reduced).
4. `thorax_rotation` top: derived from two studies and methods.
5. `lead_wrist_set_angle`: best cross-checked (Zheng 165 vs Cheetham 161 at impact) but its absolute value does not map to the env wrist.

## License and attribution (MIT repo)

Numbers are published facts and means, cited to their papers; the curves are original constructions by this repo, released under MIT. Papers are cited, not reproduced; no table is copied wholesale. Madrid et al. 2020 is CC BY (attribution above). Zheng 2008a angle values are secondary and unverified against the primary table; counsel need not review them, but do not call them verified. This file contains no personal swing data, no CMU/MultiSense/AMASS/GolfDB values, and no player video or likeness.
