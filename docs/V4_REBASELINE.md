# V4 re-baseline (Evaluator, 2026-10-24 ~18:08-18:40 ET): harness v4 on the Trainer's first --env_v4 checkpoints

**Result: no full pass.** Every gating row (harness v4, v4 head, 1.5 in tee) FAILs on `mine/robustness` and `shot/total_over_carry`; no crown-only pass either.

- Scored code: read-only export of Trainer 54b49c6 (`git archive`; Trainer env/train code unchanged 54b49c6..HEAD 4c7a586, which only adds scripts/data/results).
- Checkpoints: V4a_s80 50k-200k (warm-started from K34a 100k), V4b_s81 50k-300k (warm-started from K32a 200k); args.json `env_v4: true`. Copies in
  `<local-path>/_evalsnap/<tag>/`, md5 of zip + vecnorm + args.json vs the Trainer snapshot: all 36 MATCH (`results/v5_runs/stageJK_harness_summary/_evalsnap_md5_V4rebase.txt`).
- Layout pre-check per checkpoint (`scripts/v4_precheck_layout.py`): obs 116 = model = vecnorm, action 29 = model; ref keys `stageK32_ref_s1/tuned_keys_flat.json` (121 keys)
  md5 in the export = Trainer HEAD: all LAYOUT_OK.
- Runs (batch script held locally (machine paths); one job at a time, 2 CPUs, 2 workers, BLAS threads 2; runner defaults confirmed: arm 0.6, club 1.15, 24 deterministic eps
  (seeds 4000/8000/9000 x 8), gate off, golfphys, butter GRF, robustness 24 eps seeds 7000-7023):
  (1) `--harness v4`, V3_HEAD=v4, V3_TEE=1.5in = MAIN/gating; (2) `--harness v4`, V3_TEE=crown = INFO "v4 head, 1.6 in crown tee (equator at sourced crown)"
  (the Trainer's v4 default tee, ball centre 62.0 mm); (3) v3c and (4) v3d at 1.5 in on the v4 head (continuity).
  `realism_v5_<tag>_v4combined_gateoff_gp_arm06.json` = `eval/harness_v4.apply_v4(main, crown)` (adds `mine/v4_crown_tee_info`; `v4_crown_tee_only` false everywhere).
  Raw crown JSONs carry verdict "not v4 (main row must be the 1.5 in tee)" by design (INFO row, not a gating verdict).
- Labels: J+ "reference-guided residual with tracking assistance"; K8+ also "reference re-tuned open-loop by CMA-ES, stock G1 torque, warm-started";
  head "v4 head (sourced 460 cc, lie 58.5, Izz 5600 (n=1 manufacturer claim), CFZ 39, face centre 29 mm)"; spin band, sequence and robustness magnitudes are DERIVED;
  robustness club-speed p10 >= 0.93x median rule is LOW confidence. Full pass = the gating row passes everything incl. robustness; crown-only, spin-band-only
  and face-edge-model-only passes are not passes.

## v4 address cross-check (worker `_v4_measure`, every v4 run; all within V4_SPEC tolerance)
face centre 29.000 mm above ground (spec 29), CFZ 39.000 (39), lie 58.50 deg (58.5), Izz 5600.0 g cm2 (5600), ball centre 59.435 mm at 1.5 in (59.435) and
62.000 mm at the crown tee (spec 61.975, |diff| 0.025 < 0.5), face_limits 27.0 / 52.5 mm (27 / 52.5). Identical for all 10 V4 checkpoints and K34a 200k.

## Table (gating = v4 1.5in MAIN column; P/W/F = pass/warn/fail rows; deterministic medians from the MAIN row)
| ckpt | v4 1.5in MAIN P/W/F (gating) | v4 crown INFO P/W/F | v3c 1.5in | v3d 1.5in | main fails | main warns | club mph | smash | launch | spin | strike dz / dy mm | robust contact / start dir / plant | club p10/med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V4a_s80_50k | FAIL 13/4/2 | 12/5/2 | 12/4/2 | 13/4/2 | robustness, total_over_carry | kinematic_sequence_order, kinematic_sequence_timing_ms_before_club_peak, peak_speed_pelvis_deg_s, peak_speed_thorax_deg_s | 70.3 | 1.426 | 13.8 | 2173 | -0.6 / -12.5 | 0.79 / 0.50 / 0.71 | 0.83 |
| V4a_s80_100k | FAIL 13/4/2 | 13/4/2 | 12/4/2 | 13/4/2 | robustness, total_over_carry | kinematic_sequence_order, kinematic_sequence_timing_ms_before_club_peak, peak_speed_pelvis_deg_s, peak_speed_thorax_deg_s | 70.1 | 1.421 | 11.7 | 2976 | -11.7 / -12.8 | 0.67 / 0.46 / 0.67 | 0.82 |
| V4a_s80_150k | FAIL 13/4/2 | 14/3/2 | 11/5/2 | 13/4/2 | robustness, total_over_carry | strike_height, kinematic_sequence_order, kinematic_sequence_timing_ms_before_club_peak, peak_speed_thorax_deg_s | 70.2 | 1.404 | 11.2 | 3320 | -16.7 / -14.1 | 0.75 / 0.54 / 0.67 | 0.93 |
| V4a_s80_200k | FAIL 13/4/2 | 13/4/2 | 12/4/2 | 13/4/2 | robustness, total_over_carry | strike_height, spin_rpm, kinematic_sequence_order, kinematic_sequence_timing_ms_before_club_peak | 69.9 | 1.408 | 9.3 | 3604 | -22.6 / -9.8 | 0.71 / 0.54 / 0.62 | 0.99 |
| V4b_s81_50k | FAIL 13/4/2 | 13/4/2 | 12/4/2 | 13/4/2 | robustness, total_over_carry | kinematic_sequence_order, kinematic_sequence_timing_ms_before_club_peak, peak_speed_pelvis_deg_s, peak_speed_thorax_deg_s | 70.3 | 1.445 | 12.9 | 2255 | -0.7 / -7.5 | 0.79 / 0.54 / 0.75 | 0.82 |
| V4b_s81_100k | FAIL 13/4/2 | 13/4/2 | 12/4/2 | 13/4/2 | robustness, total_over_carry | kinematic_sequence_order, kinematic_sequence_timing_ms_before_club_peak, peak_speed_pelvis_deg_s, peak_speed_thorax_deg_s | 70.3 | 1.423 | 11.3 | 2979 | -11.2 / -12.6 | 0.79 / 0.54 / 0.75 | 0.81 |
| V4b_s81_150k | FAIL 13/4/2 | 12/5/2 | 11/5/2 | 13/4/2 | robustness, total_over_carry | strike_height, kinematic_sequence_order, kinematic_sequence_timing_ms_before_club_peak, peak_speed_thorax_deg_s | 70.2 | 1.401 | 9.7 | 3456 | -19.6 / -13.5 | 0.71 / 0.50 / 0.67 | 0.92 |
| V4b_s81_200k | FAIL 13/4/2 | 13/4/2 | 12/4/2 | 13/4/2 | robustness, total_over_carry | kinematic_sequence_order, kinematic_sequence_timing_ms_before_club_peak, peak_speed_pelvis_deg_s, peak_speed_thorax_deg_s | 70.4 | 1.446 | 12.3 | 2901 | -9.4 / -7.3 | 0.71 / 0.54 / 0.71 | 0.80 |
| V4b_s81_250k | FAIL 13/4/2 | 13/4/2 | 11/5/2 | 13/4/2 | robustness, total_over_carry | kinematic_sequence_order, kinematic_sequence_timing_ms_before_club_peak, peak_speed_pelvis_deg_s, peak_speed_thorax_deg_s | 70.9 | 1.430 | 11.2 | 3056 | -12.4 / -10.7 | 0.75 / 0.58 / 0.71 | 0.93 |
| V4b_s81_300k | FAIL 14/3/2 | 14/3/2 | 11/5/2 | 14/3/2 | robustness, total_over_carry | kinematic_sequence_order, kinematic_sequence_timing_ms_before_club_peak, peak_speed_thorax_deg_s | 70.7 | 1.449 | 11.2 | 3003 | -12.6 / -5.8 | 0.67 / 0.54 / 0.67 | 0.90 |
| K32a_s72_200k | BLOCKED (v4 cross-check stop, see below) | | | | | | | | | | | | |
| K34a_s78_200k | FAIL 12/5/2 | 12/5/2 | n/a (ref) | n/a (ref) | robustness, total_over_carry | strike_height, spin_rpm, kinematic_sequence_order, kinematic_sequence_timing_ms_before_club_peak, peak_speed_thorax_deg_s | 69.9 | 1.382 | 10.0 | 3325 | -17.7 / -17.5 | 0.75 / 0.46 / 0.71 | 0.94 |

All rows: 24/24 deterministic true contact. Robustness fails on contact 0.67-0.79 (< 0.95), start direction 0.46-0.58 (< 0.90), lead-foot plant 0.62-0.75 (< 0.90),
total/carry median outside the WARN band, plus club-speed p10 < 0.93x median (LOW confidence rule) at V4a 50k/100k and all V4b checkpoints (V4b 250k 0.925 rounds to 0.93 but is flagged).
`shot/total_over_carry` (golfphys total/carry, band 1.04-1.25) is 1.36-1.50 everywhere. The v3c column differs from v4/v3d only by v3c's bands (same episodes,
byte-identical shot numbers), which is the expected v4 construction (v3c episodes, v3d bands).
Trend: strike dz goes low with training on both seeds (V4a -0.6 -> -22.6 mm, V4b -0.7 -> -12.6 mm), and spin rises with it (2173 -> 3604 rpm on V4a);
strike_height WARNs (> 15 mm, design choice) at V4a 150k/200k and V4b 150k; club speed stays ~70 mph.

## Cross-head references
- K34 pick: K34a_s78 200k. From the Trainer's own v3d realistic-head default-tee JSONs (stageJ_harness/K34*_v3d_teedefault_realhead_local.json, LOCAL NOT OFFICIAL):
  K34b 50k-200k and 300k have 0/24 deterministic contact (their 1-fail counts lack every shot row), so only K34a 50k-300k and K34b 250k were comparable;
  among those, fewest FAILs (2: robustness, total_over_carry) then best robustness (contact 0.79, start direction 0.71, plant 0.75) -> K34a 200k.
  Under v4: FAIL 12/5/2 (main), crown INFO 12/5/2; no pass.
- K32a_s72 200k: BLOCKED. The worker's v4 cross-check stopped the run: face_half_h measured 26.5 mm vs spec 27.0 (tol 0.5) because K32a's args.json carries
  face_h 0.053 (its training sensitivity setting) and the runner passes args face_h through. All other v4 quantities were not reached. Fix = rerun with
  V3_FACE_H=none (v4 sourced face); queued after the K33/K34 two-head batch, not part of this table.

## vs the Trainer's own local copies (stageJ_harness/V4*_v3*_tee15in_v4_local.json, *_v3d_teedefault_v4_local.json and its scratch *_15in_v3.json; all labelled
"LOCAL NOT OFFICIAL" by the Trainer)
- v3c 1.5in: identical P/W/F, row statuses and shot numbers for all 10 checkpoints (both Trainer copies).
- v4 main / v3d 1.5in vs the Trainer's v3d tee15in, and v4 crown vs its v3d teedefault: same episodes (club, spin, contact identical), same FAIL rows;
  our rows add `mine/strike_height` (+ strike/face-edge INFO rows) that the Trainer's local copy predates, so we count +1 PASS, or +1 WARN where
  strike_height WARNs (V4a 150k/200k, V4b 150k). No other status differs.
- The Trainer's stageJ_harness/V4*_<N>.json (v2 box-head script) is not a v4 score (box head; e.g. V4a 50k club 73.4 mph vs 70.3 on the v4 head).

## Label fix (this commit)
`mine/head_info` said "sim head box (default)" and the crown `mine/tee_dz_info` said "compensates for the oversized sim head" for v4 runs (INFO text only;
no status/count effect). Fixed in eval/realism_check.py and eval/harness_v3d.py (v4 wording), test added; the `v4combined` JSONs carry the corrected rows,
raw per-run JSON/TXT keep the text they were scored with.
