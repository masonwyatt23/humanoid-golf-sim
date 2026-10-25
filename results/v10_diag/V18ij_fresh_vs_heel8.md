# V18i (fresh init) / V18j (policy-side heel8). LOCAL, NOT OFFICIAL
Grades: local Evaluator v4 worker @915348c, 1.5in tee. face_log_h numbers are on GATING seeds 7000-7023.
| run | grade | C/SD/F | nominal dz (mm) | face_log_h D-plane | heel (dy<-8 mm) |
|---|---|---|---|---|---|
| V18f 50k (ref) | 12/6/1 | .92/.88/.83 | -13.5 | .727 (16/22) | 7/22 |
| V18i 50k / 100k / 150k (zero-residual R0V12T init, V12p recipe, V12X keys) | 13/5/1 each | .92/.83/.83, .92/.75/.83, .92/.88/.83 | +6.1/+3.4/+3.1 | 150k: .591 (13/22) | 7/22 |
| V18j 50k / 100k (warm V18f 50k, heel8_w 30, hstart_frac .5) | 13/5/1, 11/6/2 (spin) | .92/.88/.83, .92/.83/.83 | -12.5/-15.9 | 50k: .682 (15/22) | 7/22 |
- Fresh init: no -14 mm dz drift (nominal dz +3..+6 mm), so the dz offset comes from the warm V18d/V18f lineage. The heel tail on noisy starts persists (7/22), so it is not a warm-policy artefact.
- heel8 term (100k, warm): no change to the heel count (7/22) or nominal dz. D-plane .682 is below V18f .727. Not a fix.
- Start direction is still not solved: the misses are still heel strikes (and one or two toe strikes) through gear effect.

Label (port): LOCAL, Trainer-only. Grades are Trainer-local runs (no committed harness JSONs, except official V18f in V16_GRADE.md and V18i 150k in V17_GRADE.md); face_log_h D-plane values are backed by results/v17_face/faceh_*.csv (world face, corrected sign).
