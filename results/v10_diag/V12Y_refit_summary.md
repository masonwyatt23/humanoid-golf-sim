# V12Y refit + V18h (local, NOT official)
- V12Y refit: warm V12X keys, fit seeds 8000-8047 (v7 noise, harness magnitudes; disjoint from gating 7000-7023), new terms HEEL8_W 40 (dy<-8 mm rate), DPLR_W 40 (noisy-start D-plane rate, world face) + V12X weights (HEEL_W 0).
- RESULT: NO IMPROVEMENT. Best of 30 gens x 24 = gen-0 init sample (score -980.7); tuned_keys_flat.json is byte-identical to V12X (byte-identity re-verified at port time against the a70853ae V12X keys).
  Commit a794a7ff's "V12Y refit keys" = V12X keys. Held-out seeds 9100-9147 for V12X and V12Y identical: contact .86, h_sd2 .81, heel8 .17, D-plane noisy .76, nominal |dy| 2.3 mm, nominal dz -0.9 mm, t/c med 1.35, plant .82.
- V18h (warm V18f 50k, "V12Y" = V12X keys, s550) is effectively a V18f reseed:
  - 50k 12/6/1 C/SD/F .92/.83/.83, ndz -14.8 mm; 100k 11/6/2 (.79/.75/.71, spin + robustness fail). No trigger.
  - face_log_h V18h 50k (GATING seeds 7000-7023): D-plane .571 (12/21 contacts), below V18f .727. Fails mostly heel (dy -9.7..-33.5) plus two toe (+11). Nominal dy -3.7, dz -14.8 mm.
- Takeaway: the reference-side heel-tail/noisy D-plane terms could not find a direction from V12X at sigma .12; noisy-start heel tail appears policy-side (dz -14 offset under warm policies), not reference-side.

Label (port): NULL RESULT. The V12Y keys are byte-identical to V12X (verified at port time), so no separate V12Y keys file is committed; use `results/v5_runs/stageV12X_ref_s1/tuned_keys_flat.json`. Held-out seeds 9100-9147 numbers are LOCAL refit proxies, NOT harness (`results/v10_diag/V12X_holdout_seeds9100.json`; the V12Y held-out summary is identical and not committed separately). Its "D-plane noisy" uses the corrected world-face term (1689f832), unlike the INVALID V12V/W/X proxies. V18h harness grades are Trainer-local, not backed by a committed results file; the V18h D-plane .571 comes from `results/v17_face/faceh_V18h_s550_50000.csv` (local, Trainer-only).
