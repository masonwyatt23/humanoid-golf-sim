# V18 strike-spread diagnosis (LOCAL, NOT OFFICIAL)
Data: spread_diag.py (face_log_h rollouts + logged perturbation components). Perturbed seeds are 8000-8047 (non-gating, used to fit) and 7000-7023 (GATING, held-out test). Ridge regression per component group; R2 = leave-one-out on pooled ~66 contacts, plus fit-on-8000s/test-on-gating. Full table: spread_regress_V18.txt.
| group (V18i 150k) | dy LOO R2 | dy gating R2 | dz LOO R2 |
|---|---|---|---|
| leg joint offsets (12) | .45 | .39 | <0 |
| trunk (3) | <0 | <0 | <0 |
| arms (8) | <0 | <0 | <0 |
| wrists (6) | <0 | 0 | <0 |
| joint velocities (29) | <0 | <0 | <0 |
| ball x / ball y | <0 / .14 | 0 / .07 | <0 |
| floor mu | 0 | 0 | 0 |
V18k 100k and V18f 50k show the same pattern (legs dy LOO .42/.56). Top single joint: right (lead) hip pitch r=+.56, right knee +.35. Ball offset (+-10 mm tee tolerance) explains almost nothing. dz is not explained by any group (noise or nonlinear).
State at takeaway (spread_state.py, V18i, 44 contacts on seeds 8000-8047): leg joint error vs the reference has already decayed (RMS sd 0.1 deg), but the lead sole has MOVED (x/y sd 10/11 mm; corr with dy -.41/-.64). Pelvis y and ball-minus-head also correlate (-.45/+.49).
Interpretation: the leg-joint offset at reset displaces the planted stance (foot slides/settles), and the displacement persists after joints re-track. A joint address-settle phase would not undo it (joints are already settled at t=0.1 s; extending the reference wait without retraining breaks the policy: TW .3 -> 6/48 contacts). Ball-minus-head is already in the obs, but foot position relative to the ball is not.
Fix tried: --stance_obs (default off; ball xy minus lead/trail sole xy, +4 dims). CAVEAT: the Evaluator worker only forwards its CFG list, so an official grade needs an Evaluator change. Local grades for this run use a PATCHED COPY of the worker at <local-path> (adds stance_obs to CFG); the Evaluator worktrees are untouched.
Run V18l: fresh init (R0V12T zero-residual padded +4 dims, verified action diff 0.0), V12p recipe, V12X keys, --stance_obs, s590, 100k.

## Club speed vs heel (added after official V18i 150k flagged a club-speed p10 of 56.3 mph)
Slow means below 0.9x the median club speed.
- V18i 150k on GATING seeds: median 70.7 mph, p10 56.3 (matches official). Slow 4, heel (dy<-8) 7, both 3. The one slow non-heel episode has dy -6 mm.
- V18i 150k on seeds 8000-8047: slow 3/44, all heel (dy -23/-30/-50 mm). corr(mph, dy) +.48 on both seed sets.
- V18k 100k: slow 3+2, of which 2+2 are heel; corr +.40/+.58. V18f 50k: weak (+.20/-.26).
- Same driver: for V18i, the lead-sole y shift at takeaway correlates with club speed (-.44) and with dy (-.64).
Reading: the slow episodes are almost all heel strikes, but most heel strikes are not slow (18 heel vs 3 slow on the 8000s). The slow tail is the extreme end of the same stance-displacement failure: the lead foot shifted at reset gives a heel strike and, when large, a slowed swing.

## V18l result (stance_obs, fresh init). LOCAL, PATCHED WORKER COPY, NOT OFFICIAL
Grader: <local-path> a copy of the hgs-scott-lb worker with 'stance_obs' added to CFG; harness_v4.py is identical to hgs-v4 @915348c. The watcher commits 5d00087a/ff8fe4a3 and the _v4.json labels say "Evaluator v4 worker @915348c". That is WRONG for these two runs: the worker was the patched copy.
- 50k: 13/5/1, contact/SD/plant .96/.92/.88, nominal dz +0.1 mm. This meets the 1-fail trigger (C>=.92, SD>=.83, F>=.88). Robustness still fails on spin p10/p90 and t/c.
- 100k: 13/5/1, .92/.83/.83.
- But the strike spread did NOT shrink:
  - face_log_h 50k (GATING seeds): D-plane .591, heel 6/22 (V18i 150k: .591, 7/22).
  - Non-gating seeds 8000-8047, V18i 150k / V18l 50k / V18l 100k: dy sd 14.7/15.9/14.0 mm, heel .41/.38/.39, D-plane .57/.53/.55.
- Conclusion: the 50k gate gain is within 24-episode noise, not a fix. stance_obs at 50-100k of fresh-init training does not use the stance information enough to compensate.

Label (port): LOCAL, Trainer-only, not an Evaluator grade. The CAVEAT above is outdated: since Evaluator cb2d3683 (on main) the worker forwards stance_obs from args.json; the official V18l 50k grade is results/overnight/V18_GRADE.md. The patched-worker diff (results/v10_diag/worker_patch/) is HELD (redundant with cb2d3683, machine paths). D-plane figures here are from face_log_h (world face, corrected sign; Trainer-only), not the INVALID V12V/W/X refit proxy. Local grade counts are not backed by committed harness JSONs.
