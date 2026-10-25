# Harness v4.1 robustness INFO row (re-grounded): NON-GATING

Decided by the Orchestrator on 2026-10-25 ET: **v4 stays the official gate, unchanged.** v4.1 is a clearly labelled info row. A full pass is claimed only on v4. A pass on v4.1 alone would be reported as exactly that. No snapshot passes either one.

## Rationale
The robustness perturbation is meant to be posture noise only (eval/robust_grf.py header). v4 adds the noise as qpos offsets on the actuated joints, then calls mj_forward, and it never re-grounds the feet (`if PERT:` block in results/overnight/_j_worker_gp_v3.py). The floating base stays fixed, so leg-joint noise moves the feet. The Trainer found that the lead-foot lateral shift at takeaway correlates with strike dy at r -.64. That is a moved stance, not posture noise. A real golfer would re-address the ball.

## Method (eval/reground.py, option `--reground`, default OFF)
- **Same perturbation as v4:** seeds 7000-7023, the same joint-noise draws (+/-1.5 deg) and joint-velocity draws (+/-0.05 rad/s), ball offset +/-1 cm, and v3b friction U(0.9, 1.1).
- **Foot correction:** after the noise and mj_forward, a damped-least-squares IK runs over the floating base (6 dof) plus the 12 leg dofs. It drives both `{left,right}_sole_site` back to their unperturbed address world position and orientation. That is 12 equations in 18 unknowns, solved as the minimum-norm change from the perturbed pose, so the leg noise is only partly removed. Leg joints are clipped to their ranges. It converges in about 3 iterations.
- **What stays as v4 made it:** the waist, arm and wrist noise is kept exactly. The club free body moves with the base's rigid transform, so the hand-club relation is the one v4 produced. The ball is not touched, and base qvel is set to 0.
- **Grading:** the row uses exactly the v3d/v4 chain that grades `mine/robustness`: the same contact, start and plant triple and the same tails, including the club p10 rule. It is stored as `mine/robustness_v4_1_reground_info` with status info and gating False. `verdict_if_gating` holds the grade it would have received.
- **Caveat:** this restores the feet, not the whole address. Moving the base moves the hands and club with it. In an offline probe of the 24 address states, the base shifted by a median of 6.0 mm (max 14.2 mm) and the clubhead moved relative to the ball by a median of 9.3 mm (max 13.3 mm). v4.1 is "feet re-grounded". It is not a full re-address with the clubhead behind the ball.

## Foot residuals: max over both soles, 24 seeds (the address state is the same for every snapshot)
| | position mm (median / max) | orientation deg (median / max) | lateral \|dy\| mm (median / max) |
|---|---|---|---|
| v4 (after noise, no re-grounding) | 15.5 / 27.2 | 2.19 / 4.44 | 11.2 / 22.9 |
| v4.1 (re-grounded) | 0.0002 / 0.0007 | 2e-6 / 1.5e-5 | 0.00002 / 0.0001 |

## Results: v4 1.5in main row, RO export b663c9f6, V12X keys, harness as V18_GRADE.md
| Snapshot | v4 tally (official) | v4 triple | v4.1 triple (info) | v4.1 tails failing | v4.1 verdict if it gated |
|---|---|---|---|---|---|
| V18l_s590 50k | 13/5/1 FAIL | .958/.917/.875 | .833/.792/.833 | spin p90 4220, t/c median 1.372 and p90 1.665 | FAIL |
| V18i_s560 150k | 13/5/1 FAIL | .917/.875/.833 | .875/.875/.833 | spin p10 1035 and p90 4142, t/c p90 1.761, club p10 59.4 (0.84x median) | FAIL |
| V18f_s530 50k | 12/6/1 FAIL | .917/.875/.833 | .875/.833/.875 | spin p90 4134, t/c p90 1.531 | FAIL |

- Re-grounding does **not** help these policies. V18l gets clearly worse: contact .958 -> .833, start .917 -> .792, plant .875 -> .833.
- The club-speed tails tighten: V18l p10 goes from 60.5 to 68.6 mph (0.86x -> 0.97x median).
- So the 1 cm stance shift is not what limits robustness here. The likely reasons are that the policies were trained on the un-grounded address, and that re-grounding moves the clubhead about 9 mm relative to the ball (see Caveat).
- n = 24 per row, so a single episode moves a fraction by .042.
- In each --reground run, every check other than the new row matches the official v4 JSON exactly.

## Regression (option OFF)
V18i_s560 150k, v4 1.5in, rerun with the patched worker and harness: the JSON and TXT are byte-identical to the V17 official files.
