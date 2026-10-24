# Harness v4 (Evaluator, 2026-10-24 ET): v3d bands on the sourced v4 head/address

> **Status: PROVISIONAL, opt-in (`--harness v4`).** The default harness stays v3c and is unchanged. Single seed, model-only physics. No row passes every check; no v4 rows are scored yet. Never compare pass/warn/fail counts across harness versions (v3c, v3d, v4 use different bands and envs).
Status: READY, cross-check PENDING the Trainer's v4 flag being committed (seen only in the Trainer's dirty tree as `--env_v4` / `env.set_env_v4()` /
`--tee_mode 1.5in`; not scored, not probed: harness scores read-only exports of commits only).

## What v4 is
`--harness v4` = the v3c episodes, re-graded with the v3d bands and rules UNCHANGED (spin 2000-3700 at 70-85 mph derived, WARN 1200-4000; pelvis floor 250 deg/s;
thorax/arm tie or inversion <= 30 ms; arm->club >= 20 ms; robustness club p10 >= 0.93x median, low confidence; strike_height WARN > 15 mm design choice,
FAIL >= env face_limits() vertical half-height, 27 mm for the 54 mm face), plus:
- the env must be v4 (`V3_HEAD=v4`), and the worker cross-checks the address after reset against `eval/harness_v4.V4_SPEC` and stops on any mismatch:
  face centre 29 mm above GROUND (+-0.5), CFZ 39 mm (+-0.5), lie 58.5 deg (+-0.1), Izz 5600 g cm2 (+-1%), ball centre 59.435 mm at the 1.5 in tee and
  61.975 mm at the 1.6 in crown tee (+-0.5), face_limits 27 / 52.5 mm (+-0.5). Everything is recorded in `tee_info.head` (mode v4, measured, expected, geometry).
- MAIN row = 1.5 in tee (`V3_TEE=1.5in`, default under `--harness v4`). The 1.6 in crown tee is a separate run scored as INFO row `mine/v4_crown_tee_info`,
  labelled "v4 head, 1.6 in crown tee (equator at sourced crown)". A pass at the crown tee alone is NOT a pass (`v4_note: not a pass (crown-tee-only)`).
- Not a pass either: spin-band-only, face-edge-model-only (v3d flags carried over).
- Labels: v4 results are "v4 head (sourced 460 cc, lie 58.5, Izz 5600, CFZ 39, face centre 29 mm)"; J+ "reference-guided residual with tracking assistance"; K8+ also "reference re-tuned open-loop by CMA-ES, stock G1 torque, warm-started".

## Why (vs v3d)
v3d graded a 64 mm box head (or the K34 realistic head with unsourced face-centre height 30 above the sole + 2 mm clearance = 32 above ground).
v4 uses the sourced values: Data Agent driver-face-centre-height @ 857e373, reviewed in scott-e ebb6e4a (route B corrected; overlap 27-31 mm);
US 12,649,090 B2 Tables 3-4 (Zup, CGZ, CFZ, Izz bands) and claim 1; USGA TPX3004 Rev 2.0 sec. 2.1b (face centre = template midpoint, usga.org);
Izz 5600 g cm2: single published manufacturer claim (n=1, one head; Tour Edge 2023 press release), attributed, not measured or an aggregate; MyGolfSpy tee test (1.5 in "measured from ground level").

## Probe definitions (worker `_v4_measure`)
face centre = env clubhead site z; CFZ = face centre projected along world x (target) onto the vertical plane containing the shaft axis, shortest distance to
the shaft axis (US 12,649,090 definition); lie = asin(|shaft axis z|); Izz = head_mass box about its up axis, m (hx^2 + hy^2) / 3; tees = ball centre z after reset.

## Re-baseline plan (one pass, after the Trainer commits the v4 flag and its first v4 checkpoints)
1. Export the commit read-only (`_ro_trainer_<hash>`), run the probe only (1 episode) and record the cross-check numbers.
2. Score, one job at a time (taskset -c 0-1, 2 workers, OMP/MKL 2), 24 deterministic eps + robustness 7000-7023, arm 0.6, club 1.15, gate off, golfphys:
   - Trainer's first v4 checkpoints: v4 main (1.5 in) + v4 crown info (1.6 in); v3c and v3d at the same 1.5 in tee for continuity.
   - Cross-head references: K32a 200k and K34 (best K34a/b snapshot) under v4 main + crown info, plus their existing v3c/v3d box/realistic rows (no rescoring of those).
3. Table: v4 main rows only gate; crown rows info; face_h 0.053 rows sensitivity only. Any full-pass claim names "harness v4" and its commit.

## Trainer 54b49c6 (`--env_v4`) wired and probed (2026-10-24 ET)
Read-only export of Trainer 54b49c6 (flag, V4 dict, sw_compensation and env/models/v5_address_LH_{87,95,105,115}_v4.json all committed).
Tee mapping (no rename): MAIN/gating = Trainer tee_mode '1.5in' (forced by the worker under v4 whatever args.json says; args env_v4/tee_mode recorded in tee_info);
the Trainer's v4 DEFAULT tee (equator at the 62 mm crown, ball centre 62.0 mm) = the 1.6 in crown INFO row (spec 61.975, |diff| 0.025 mm).
Worker cross-check also compares against the address JSON (lie, face-centre height, ball z, v4_params) and the env V4 dict (fc_z_ground, fc_shaft, izz, sole_clear, tee_15in_bottom).
Probe (club 1.15, LH, seed 0): face centre 29.000 mm above ground; CFZ 39.000 mm; lie 58.50 deg; Izz 5600.0 g cm2 (head_mass box m(d^2+w^2)/12, d = depth 112 mm, w from Izz);
ball centre 59.435 (1.5in) / 62.000 mm (default = crown); face_limits 27 / 52.5 mm; sole 0.000 mm (sole ON the ground); crown 62.000 mm above ground.
Swingweight: compiled club 300 g, along-shaft COM -0.99355 m and moment about the 14 in point 0.191386 kg m, identical to the box club. sw_compensation(1.15) returns
m_butt 5.673 g (head CG 16.31 mm further down the shaft); TRAINING_NOTES says 5.47 g / 15.7 mm (doc mismatch, behaviour correct). Club COM lateral offset changes (x 0 -> -16.9 mm, y 16.5 -> 23.3 mm in the club frame).
Smoke (K32a 200k, Trainer scripts/v4_smoke.py rerun from the export, 25 seeds): CSV byte-identical to the Trainer's. Policy: default/crown tee 22/25 hits, median dz 0.09, dy -18.04 mm,
spin 2128, launch 12.84, smash 1.38, 69.76 mph; 1.5 in tee 22/25, dz -2.33, dy -20.89, spin 2290, launch 12.42, smash 1.37, 69.76 mph; 2/25 off-face at each tee.
