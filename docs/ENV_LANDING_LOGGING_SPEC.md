# Env landing / per-shot logging spec (for the Trainer)

Status: **specification only**. `env/`, `eval/`, `train/` were read, not edited. Nothing here has been run in the env; every "where to add" pointer is from reading the code and is **unverified** until implemented. Schema: `data/schemas/landing_shot_row.schema.json`; example: `data/references/landing_shot_row_example.json` (made-up round numbers, labelled ILLUSTRATIVE).

Goal: one JSON row per shot so that (a) `golfphys.bounce.bounce_roll` / `data/roll_aoa_addon.py` can estimate roll and total from the *env's own* landing state instead of a launch-only guess, and (b) `realism.checks.check_shot_realism` can run its `descent_deg`, `spin_rpm`, `spin_axis_deg`, `total_over_carry` and `carry_vs_golfphys_yd` checks (they currently SKIP because gate JSONs carry only means and no spin/descent). The env flight model has **no roll**, so env `total` is approximately `carry`; roll/total in the row are model-only and go under `model_only`.

## Conventions
- World frame (MuJoCo, as in `eval/flight_tracker.py`): **+x target line, +y LEFT of target, +z up**; metres, m/s, rad/s, degrees, rpm. Ball start x is taken from the first trajectory sample (`start_x`), so `carry_m = x_land - start_x`. Note: the env's existing `info["carry"]` is the absolute landing x (`bp[0]`), not minus start x; they coincide only if the ball starts at x = 0. Log which one you used (the spec wants minus start).
- Left-handed env = mirror about the x-z plane (`y -> -y`, `docs/HANDEDNESS.md`; `hand_sign = -1`). The env already mirrors `ball_lateral` and `launch_direction` in `info`. For the log use `frame = "golfer"`: every **y-derived or azimuth-like quantity is multiplied by `hand_sign`** (lateral offset, azimuths, face yaw, club path, sidespin, spin axis, the y and rotation components of the raw vectors if you store them in golfer frame). Backspin, loft, AoA, descent, speed, apex, carry are mirror-invariant. If you store raw vectors in world frame set `frame = "world_raw"` and do not mix the two in one file.
- Signs after conversion (golfer frame, both hands): azimuth/face/path **+ = left of the target line**; face yaw + = face pointing left of target (closed for an RH golfer, open for an LH golfer); club path + = moving left (out-to-in for RH, in-to-out for LH); dynamic loft = elevation of the face normal above horizontal, + lofted; AoA = elevation of the head velocity, + ascending; sidespin + = about +z (curves the ball left); spin axis = atan2(sidespin, backspin), + = left. Backspin positive number; the env writes world spin as `[0, -rpm, k_side*dy] * 2*pi/60` (backspin about **-y**, so Magnus lifts a +x ball).
- Missing = `null`, never 0 or NaN (the schema forbids NaN; `json.dump(allow_nan=False)`).

## Fields: existing source vs what to add
| Row field | Unit | Existing source (read-only finding) | Add / note |
|---|---|---|---|
| `true_contact` | bool | `env.true_contact`, `info["true_contact"]` | exists |
| `landed` | bool | `env._landed` (info only exposes `carry` > 0) | expose `landed` in `info` |
| `impact.t_s` | s | `FlightTracker.t_impact` (`d.time` at first true contact) | exists |
| `impact.club_speed_mps` | m/s | `info["impact_club_speed"]` = max(prev-substep, current-substep head speed); tracker also has `club_pre` | exists. Report which |
| `impact.face_yaw_deg`, `dynamic_loft_deg` | deg | not logged. Env has `geom_xmat[club_head]` at the substep where `_face_off` is set (`humanoid_golf_env.step`, the `if not self.true_contact:` block) | at that substep, `n = R_geom @ e_face` (local face axis; the face offset uses local y = lateral, z = vertical, so the face normal is presumably local x, **unverified**; check the XML `club_head` box with `euler="0 3 0"`). `face_yaw = atan2(n_y, n_x)`, `dyn_loft = asin(n_z)` (sign so lofted = +) , both with `hand_sign` for yaw |
| `impact.club_path_deg`, `aoa_deg` | deg | not logged; head velocity is computed in `_club_speed()` (`mj_objectVelocity`, linear part `v[3:]`) | use the head velocity **before** the contact substep (`club_pre` logic, tracker keeps `_hist` speeds only). `path = atan2(v_y, v_x)`, `aoa = atan2(v_z, hypot(v_x, v_y))` |
| `impact.contact_dy_m`, `contact_dz_m` | m | `env._face_off = (dy, dz)` from `_contact_face_off()` (club-geom local y, z of the contact point) | exists; expose in `info`. Toe vs heel sign depends on `toe_sign` (`docs/GEAR_EFFECT_VALIDATION.md`, `golfphys.contact.env_contact_to_shot`): LH env `toe_sign=+1` (simple env), unverified for the G1 env |
| `impact.ball_speed_sep_mps` | m/s | `FlightTracker.v_sep` norm (`ball_speed_sep` in `summary()`); env `_sep_v` | exists |
| `impact.launch_deg` | deg | `FlightTracker.launch_elev_deg()` (from `v_sep`). Do **not** use `info["launch_elevation"]` (taken at peak-speed sample, kept as `launch_elev_env_peakspeed_deg`) | exists |
| `impact.launch_azimuth_deg` | deg | `info["launch_direction"]` (already * hand_sign) | exists |
| `impact.backspin_rpm` / `sidespin_rpm` / `spin_axis_deg` | rpm, deg | `info["sep_rpm"]` = backspin from the `impact_model` formula `spin_k*|v|*sin(el+2deg)` (clipped 0-6000); sidespin = `k_side*dy` rad/s in world z (not exposed) | expose `_sep_rpm` (exists) and sidespin `k_side*dy*60/2pi`. Only valid when `impact_model` is set |
| `flight.apex_m` | m | `FlightTracker.summary()["max_height"]` is the max z of the **whole** trajectory (includes club-tee period); tracker `_land_apex` only when `track_landing=True` | log max ball z between separation and touchdown (ball z minus ball radius if you want height above ground; state which) |
| `flight.flight_time_s` | s | not logged | `t_land - t_sep`; `d.time` at separation (`_sep_v` set) and at touchdown |
| `landing.t_s`, `x_m`, `y_m` | s, m | `env._landed` flag is set at `bp[2] < 0.03` (or first ground contact in tee mode) with `carry = bp[0]`; **y at landing not stored** (`ball_lateral` is the current y each step) | store `bp[1]*hand_sign` and `d.time` in the same `_landed` branch |
| `landing.descent_angle_deg`, `speed_mps`, `v_world_mps` | deg, m/s | `FlightTracker.install(track_landing=True)`: `land_v` = ball velocity at first descent through `z < LAND_Z (0.03 m)` after apex > `LAND_MIN_APEX (0.5 m)`; `landing_summary()` gives `descent_angle_deg`, `landing_speed_mps` | exists (opt-in, keep default off to leave outputs unchanged). Use the same rule as the env carry (`z < 0.03`); tee mode uses first ground contact instead, so make the tracker follow `env._landed`. Velocity should be sampled on the substep **before** the ground contact solver changes it (the tracker samples after `mj_step`; a z<0.03 sample may already include contact impulse - **unverified**; log one shot at substep resolution to check) |
| `landing.spin_rpm`, `spin_world_rad_s` | rpm, rad/s | not logged. Aero code reads `d.cvel[ball][:3]` (world angular velocity) | read at the same substep as `land_v`. Env has no spin decay model other than MuJoCo damping (check); logging this shows what the env actually delivers |
| `carry_m` | m | `info["carry"]` (absolute x of first landing; 0.0 if never landed) | subtract start x; keep `landed` separate |
| `total_m` | m | `FlightTracker.summary()["total_dist"]` (final x - start x) | exists; env has no roll, so expect `total ~ carry` |

## Rules for the tracker
1. One row per episode; written at episode end with `json.dumps(row, allow_nan=False)`. No per-substep arrays in the row.
2. A shot that never contacts or never lands still gets a row (`true_contact`/`landed` false, nulls for missing fields).
3. Exclude/flag the existing non-physical episodes (`nonphysical_substeps > 0`); put `"nonphysical": true` in the row instead of clipping.
4. Keep logging opt-in and default outputs unchanged (as `track_landing` already does).
5. Rows are env-model output. Do not describe them as measurements; `label` must say hypothetical/stock tier, no roll, model-only.

## How the data feeds the models
- `golfphys.bounce.bounce_roll(land_pos, land_vel, land_spin, turf=...)`: `land_pos = (x_m, y_m, ~0)`, `land_vel = landing.v_world_mps`, `land_spin = landing.spin_world_rad_s`; **both in world frame, so use the `world_raw` vectors** (or mirror y back) before calling. Returns roll/total in metres; put the result in `model_only`, with the turf firmness named. There is no `golfphys.roll` module; roll lives in `golfphys/bounce.py` and the heuristic in `data/roll_aoa_addon.py` (`estimate_roll_yd`, `estimate_total_from_m`).
- `realism.checks.check_shot_realism(shot)` keys: `club_speed_ms` <- `impact.club_speed_mps`; `ball_speed_ms` <- `impact.ball_speed_sep_mps`; `launch_deg` <- `impact.launch_deg`; `spin_rpm` <- `impact.backspin_rpm`; `spin_axis_deg`; `carry_m`; `total_m` (use the model total, not env total, or `total_over_carry` will read 1.0); `descent_deg` <- `landing.descent_angle_deg`.
- Roll/AoA validation (`docs/ROLL_AOA_VALIDATION.md`) said the env spin formula runs ~900 rpm below the TrackMan chart; logging `backspin_rpm` and `landing.spin_rpm` per shot lets that be rechecked directly.

## Sanity checks to run on logged rows (all model/physics consistency, not truth)
`descent_angle_deg` between ~25 and 55 for a driver (published tour driver ~36-39, env previously 35-44 on the hypothetical power tier); `landing.speed_mps` below `ball_speed_sep_mps`; `carry_m` vs `golfphys.sim.shot_from_launch` carry for the same speed/launch/spin within the thresholds in `data/references/realism_thresholds.json`; `|y_m|` consistent with `launch_azimuth_deg` and sidespin sign after the LH mirror.

## Sample row
See `data/references/landing_shot_row_example.json` (illustrative values only).
