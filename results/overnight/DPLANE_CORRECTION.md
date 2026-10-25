# v5 D-plane correction (Evaluator, 2026-10-25 ~2:00 PM ET)

**What was wrong.** `v5/dplane` was computed on the deterministic nominal rollouts (`a._v5_eps`, the 24 harness episodes), not on the perturbed robustness episodes. The deterministic rollouts are identical copies of one swing (start_err spread 0.000 deg), so every D-plane fraction reported in V13_GRADE.md (V13h), V14_GRADE.md (V16y/V17f "0/24"), V15_GRADE.md (V18d "24/24") and V16_GRADE.md (V18f "24/24") was a NOMINAL-ONLY, n = 1 result. Impact logging was present on the robustness episodes; `_robust_ep` simply did not keep the impact keys and the row was never given them.

**Fix.** `run_robustness` keeps seed/contact/shot_extra/impact for the main v4 robustness DR (seeds 7000-7023); `dplane_row(eps, rob_eps)` grades those, reports the nominal swing as `values.nominal` (n = 1), adds `distinct_starts` and start_err median/p10/p90/min/max, and returns n/a if all graded episodes are identical. Earlier grade docs are not rewritten; this note supersedes their D-plane lines. v4 verdicts are unchanged.

**Corrected numbers** (`_batch_V16b.sh`, same exports as the original grades; v4 part reproduced; NON-GATING):

| ckpt | start vs 0.85 x face | curve sign | start_err med / p10 / p90 (min..max) deg | face / start med deg | nominal (n=1) |
|---|---|---|---|---|---|
| V18f_s530 50k | 16/22 = .727 WARN | 21/21 | -1.33 / -5.30 / +1.75 (-6.94..+1.87) | -0.50 / -1.64 | err -0.95 ok |
| V18d_s511 50k | 9/22 = .409 FAIL | 19/19 | -1.97 / -5.63 / +1.57 (-7.01..+3.13) | -1.70 / -3.34 | err -0.99 ok |
| V16y_s402 50k | 10/23 = .435 FAIL | 19/19 | +1.77 / -2.52 / +5.16 (-3.78..+6.47) | -4.08 / -2.30 | err +2.51 not ok |

n = contact episodes with impact keys; all distinct. Across the perturbed episodes start correlates only weakly with face (r = 0.41 V18f, 0.33 V18d, 0.38 V16y; start SD about twice face SD), so start direction under perturbation is only partly face-driven; V18f's misses are starts left of the face prediction (pulls).
