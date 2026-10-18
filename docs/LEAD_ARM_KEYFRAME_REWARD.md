# Lead-arm keyframe reward targets (learned-policy run)

> **Derived from Mason's Instagram swing references (aggregates only).** Built only from aggregates (median/IQR) already tracked in `data/references/mason_keyframe_targets.json` and constants in `wrist_sign_mapping.json`. No per-clip values, clips, handles or URLs. Flag `instagram_derived: true`. Mason approved use of his own Instagram-derived swing data (t108u). Third-party content in the source recordings was never reviewed; see `docs/RELEASE_QUESTIONS_FOR_COUNSEL.md`.
> **UNVERIFIED.** 2-D MediaPipe proxies from ~30 fps feed recordings, 7-8 left-handed clips, mostly down-the-line. Nothing here was run in training; `env/`, `eval/`, `train/` were read only.

Files: `data/references/lead_arm_keyframe_reward.json`, generator `data/lead_arm_keyframe_reward.py`, test `tests/test_lead_arm_keyframe_reward.py`.

## Role mapping (do not mix up arms)
Env `right_*` = TRAIL (club) arm, `left_*` = LEAD arm for both handedness (`docs/HANDEDNESS.md`). Mason's reference columns 0-3 (named `right_*` in the file) are his anatomical right = **lead** arm (left-hander) -> env `left_*`. Reference column 4 is the TRAIL shoulder -> env `right_shoulder_pitch`. The trail-arm wrist/elbow targets live in `wrist_elbow_event_targets.json`, not here.

| Ref column | Env joint | Env status in v3 / v4_power (read from XML) | Use |
|---|---|---|---|
| 0 right_shoulder_pitch | `left_shoulder_pitch` | **actuated** (motor, gear 40) | primary, weight 0.6 |
| 1 right_shoulder_roll | `left_shoulder_roll` | **passive** hinge, no motor | excluded (low-confidence proxy; roll sign flips for left-handed env) |
| 2 right_elbow | `left_elbow` | **passive** hinge, no motor | reward-only, weight 0.2; set 0 unless `grip=True` |
| 3 right_wrist | none | **no lead-wrist joint** (`left_hand` is a sphere) | derived hand-deviation proxy only; weight 0 |

"Lead arm angle" quantities (shoulder, elbow) are readable from `qpos`, but only the shoulder is controllable; the elbow follows only via the `left_grip` equality (inactive by default, `grip=False`). A reward on passive joints cannot be driven directly by the policy.

## Sign conventions
- Shoulder pitch (reference): 0 = hanging, negative = raised. Env sign of `left_shoulder_pitch` is **not verified**; use the normalised form y=(q-q_addr)/(q_top-q_addr) (as `env._load_keyframes` does) or check sign with one FK step.
- Wrist: positive env `right_wrist` = cocked (`docs/WRIST_SIGN_MAPPING.md`) - that is the **trail** wrist. The stored lead "wrist" is an unsigned hand-deviation magnitude. The offset -1.31 rad (tolerance 0.15) was fitted to the trail wrist's contact geometry and **must not** be applied to the lead wrist.
- Elbow: unsigned flexion; env `left_elbow` range -10..150 deg, assumed flexion-positive (unverified).

## Targets (deg, median [q25, q75], sigma = suggested, floor 8 deg)
| Event | left_shoulder_pitch | left_elbow | (lead wrist proxy, not used) |
|---|---|---|---|
| address (prior only) | 20.8 [17.1, 24.6] | 28.8 [21.6, 29.9] | 59.1 |
| top | -64.7 [-68.9, -60.7] | 47.8 [45.0, 51.4] | 13.9 |
| impact (n=7) | -0.1 [-4.0, 1.2] | 59.2 [55.1, 63.1], sigma 8.3 | 45.8 |
| finish (weak anchor) | -83.8 [-85.4, -79.9] | 94.1 [84.6, 110.6], sigma 16.9 | 24.5 |

Roll values are in the JSON (not rewarded).

## Event timing (offset corrected)
Median joint-axis event times of the clips used (video-time events minus the ~0.4 s `joint_axis_offset_s`, from `event_offsets_s`): takeaway -0.025 s, top 0.45 s, impact 0.609 s, finish 1.11 s (backswing 0.475 s, downswing 0.159 s, follow 0.501 s). **Do not use these seconds as a speed target**: the clips look sped up (0.48 s backswing is implausible) and 30 fps gives +-1 frame (~33 ms) event error. Index by event **phase** in **simulated time** (ref dt 0.01 s vs env control dt 0.02 s, `docs/REFSET_TIMING_AUDIT.md`), and use the tempo-ratio band 2.88-3.53 (median 3.06). Landmark impact is early vs the club low point by ~0.067 s (+-0.05): detect sim impact as club low point minus 0.067 s.

## Recommended reward form
`r_lead = (1/K) * sum_{k in top, impact, finish} exp( - sum_j w_j ((q_j(t_k) - mu_jk)/(s*sigma_jk))^2 / sum_j w_j )`, K=3, weights above, best-matching sample in a +-0.06 s window around each event, curriculum s = 2.0 -> 1.0 (s<1 unsupported by the data). Prefer the normalised form for sign/offset robustness. Address is not rewarded (the video axis starts at/after takeaway in most clips). Suggest lead-arm share of total tracking reward <= 0.3 because only one joint is actuated; weights are judgment, not fitted. Legs weight 0 (low confidence, hip values exceed env limits).

## Command lead
`docs/WRIST_PD_LAG.md` (sim probe, v3 fs2): the wrist lags ~0.12 rad at impact on a fast ramp; **leading the wrist command by ~0.06 s** removes it (+0.003 rad). That was measured for the **trail** `right_wrist` only. The lead shoulder PD lag was not measured; the same lead is a hypothesis (unverified) - run a step test before using it. Score angles at the applied-target time (the replay log's command is 20 ms ahead of the applied one).

## Unverified list
All angles (video proxies, small n); env shoulder-pitch sign; lead-elbow flexion sign; any effect on swing quality; weights/sigma curriculum; the lead-shoulder lag. Event seconds are for reference only.
