# D-plane proxy calibration against the official Evaluator (13:58 ET)
Source (read-only): <local-path> v5.rows['v5/dplane'].episodes.
- The official v5/dplane episodes are seeds 4000-4023 and all identical (std 0): it is a NOMINAL-shot check, not the robustness episodes.
- Conventions: the env is LEFT-handed, so face_world = env info face_yaw_deg * hs with hs = -1, i.e. face_world = -face_yaw; start = env shot azimuth_deg (world, + left). Test: |start - .85*face_world| <= 2.
- Local face_log nominal (with face_world = -face_yaw) matches official exactly: V16y err +2.51 (official +2.51, fail), V18d -0.99 (official -0.99, pass), V17f official +2.84 (fail). V13h local +1.54 (passed officially).
- Earlier proxies (face_log az - 0.85*face_yaw, and the V12V/W/X refit D-plane term) used the wrong sign AND scored noisy starts. So the refit D-plane term in V12V/V12W/V12X optimised the wrong quantity, and earlier "az - 0.85*face" medians in notes are not the Evaluator metric.
- Fix: scripts/v12u_ref_fit.py now uses world face (hs from env.handed) and scores the NOMINAL shot: d['dplane_nom'] = |az - .85*face_world|, with penalty V12U_DPL_W above 1.5 deg. The noisy-start rate 'dplane' is kept as info only.
- Gear-effect labelling stays: on noisy trainer starts az still tracks strike dy (r .82-.92), not face.
- (14:05) Fix-of-fix: the first edit dropped the az capture. The D-plane term now uses v7's per-start 'az' (shot azimuth) and the world face. Zero-residual reference nominal |start - .85*face_world|: V12V 0.02, V12W 0.52, V12X 0.12 deg, so all reference keys pass the D-plane on the nominal shot.

## Harness-noise calibration (14:15 ET) vs Evaluator b9e38999 perturbed D-plane
scripts/face_log_h.py reproduces the v4 worker perturbation: env reset(seed), ball_tol 0.01, floor mu U(0.7,1.05) from rng(seed+0xF41C), joint 1.5 deg / 0.05 rad/s from rng(seed+0x5EED). V18f 50k seeds 7000-7023 match the official per-episode face_world/start EXACTLY (all 22 contacts, the same 2 misses 7000/7007). Fields: face_world = -face_yaw (LH env), start = shot azimuth.
- Pass .727 (16/22) = official. err = start - .85*face_world: r(err, strike dy) = .98, r(err, dz) = -.39; all 6 fails are heel strikes (dy -14.9 to -39.1 mm; passes are all >= -8.4 mm). r(err, dz) is weak.
- So the pulls (2-5 deg left of the face prediction) are gear-effect pulls from HEEL strikes, not face/path. Target: the heel-strike tail on noisy starts (dy < -10 mm), without pushing the nominal strike back to the toe.

Label (port): LOCAL, Trainer-only, not the harness or an Evaluator grade.
- The first bullet ("v5/dplane is nominal-only") describes the harness BEFORE Evaluator b9e38999; the harness now grades the perturbed robustness episodes (results/overnight/DPLANE_CORRECTION.md).
- Harness-noise match: the committed results/v17_face/faceh_V18f_s530_50000.csv gives start vs 0.85 x face_world 16/22 = .727 and err min/max -6.94/+1.87, matching the official V18f row in DPLANE_CORRECTION.md (the median -1.37 vs -1.33 and p10 -5.15 vs -5.30 differ slightly; the CSV is 2-decimal rounded). The per-episode "EXACT" match is Trainer-reported: the official per-episode values are not published on main (episode blocks stripped).
- Heel-strike gear effect: r(err, strike dy) = .977 computed from that CSV (22 contacts); all 6 fails have dy -14.9..-39.1 mm. Start-direction pulls are a heel-strike gear effect, not face/path. Local, single checkpoint.
- V12U_DZ_W, V12U_DY2_W and V12U_DPL_W in scripts/v12u_ref_fit.py all default 0.
