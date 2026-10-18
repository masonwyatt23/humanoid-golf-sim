# golfphys: standalone ball / club flight simulator

Written 2026-10-17 (America/New_York). Package `golfphys/` (pure Python + numpy; scipy only for calibration), tests `tests/test_golfphys.py`, coefficients `data/references/golfphys_coefficients.json`, validation `docs/GOLF_PHYSICS_VALIDATION.md` + `data/references/golfphys_validation.json`. Imports nothing from `env/`, `eval/`, `train/` (a test enforces this) and uses no personal clip data. Nothing in `env/` was edited.
Frame and units: SI, +x target line, +y LEFT of the line, +z up. Env carry is metres with no roll; `ShotResult` gives metres and yards. Every parameter is tagged **calibrated** (fit to cited rows, with held-out checks), **assumption**, or **published** (value quoted from a source; source marked **fetched** = page/PDF read in full in this or the earlier validation session, **snippet** = search excerpt only).

## 1. Pipeline
`Delivery(+Strike)` -> `impact()` -> ball (speed, launch, azimuth, backspin, sidespin, axis) -> `fly()` (ODE) -> `bounce_roll()` -> `ShotResult`.

```python
from golfphys import load_params, Delivery, Strike, simulate_shot
r = simulate_shot(Delivery(club_speed=58.1, dynamic_loft_deg=13.5, aoa_deg=4.0, face_deg=0, path_deg=0, handed="LH"),
                  Strike(x_toe_m=0.0, y_high_m=0.0), turf="normal", wind=(0,0,0), alt_m=0, temp_c=15)
r.carry_m, r.total_m, r.carry_yd, r.total_yd, r.smash, r.launch_deg, r.spin_rpm, r.apex_m, r.descent_deg, r.hang_s, r.land_speed_ms, r.lateral_carry_m
```
Also `shot_from_launch(ball_speed, launch, spin, spin_axis_deg=, azimuth_deg=, ...)` (launch-monitor entry) and `fly(p0, v0, w0, params, rho/alt/temp/rh, wind)`.

## 2. Impact (`golfphys/impact.py`)
- **Normal**: Newtonian restitution with effective mass, `v_bn = (1+e) m_eff/(m_eff+M) * v_n`. Off-centre strikes lower the effective mass by rigid-body coupling, `1/m_eff = 1/m + x^2/Iv + y^2/Ih` (Ih 4000-5900 g cm^2, Iv = 1/2-2/3 Ih: **published**, Tutelman gear effect 3, *fetched*). This gives about -4.6 % ball speed at 1 in off-centre with no extra coefficient (the research note's 0.07-0.14/in loss coefficient was unverified and is not used).
- **Tangential**: ball tangential speed and spin come from one impulse `Jt = s_t * M * vt / 3.5` (`s_t = 1` is full rolling contact of a uniform sphere, spin = vt/(1.4 R)). `s_t` is a **calibrated** slip efficiency (0.866). Contact, spin axis `omega = -(R Jt / I) n x d` and the launch direction fall out of 3-D vector algebra, so **face-to-path, D-plane, spin-axis tilt and "start line ~85 % face" are emergent**, not hard-coded (checked in tests: 0.7-0.95 of the start-line change follows the face).
- **Mass / COR**: nominal 200 g head, `e0 = 0.854` effective (**calibrated**, absorbs head-mass/COR uncertainty; above the 0.83 legal COR because `m_head` is nominal, so do not read it as a measured COR). `e` speed slope fitted at ~0 and fixed at 0.
- **Bulge / roll**: the local face normal tilts by `x/R_bulge` (10 in) and `y/R_roll` (12 in): toe hits start toward the toe side, high hits launch higher (**assumption**: radii are common specs, unverified).
- **Gear effect**: added spin `16.4 * Vb(mph) * x(in)` rpm about `toe x n` (toe hit = draw for either hand; sign tested for RH and LH) and `25 * Vb * y(in)` about `up x n` (high hit = less backspin) (**published**, Tutelman GE3, *fetched*; **not validated** against off-centre launch-monitor data, none collected). With the bulge tilt the net 1-in toe-hit draw is about 1100 rpm at 150 mph vs 2490 for the gear term alone.
- Conventions: `face_deg`, `path_deg` positive = left; `aoa_deg` positive = ascending; `dynamic_loft_deg` = elevation of the face normal; spin loft = angle between club velocity and face normal (= DL - AoA on-line). `handed` sets which side the toe is on.
Sources (all **snippet** unless stated): Cochran & Stobbs oblique-impact model (friction -> roll -> backspin, via Tutelman design notes); Tutelman smash-factor and 3-D launch pages; TrackMan driver-fitting chart 2010 rows (*fetched*, used for calibration only).

## 3. Aerodynamic flight (`aero.py`, `flight.py`)
RK4, `dt = 0.01 s` default (carry converges to <0.01 yd between 0.02 and 0.002 s). `F = -1/2 rho A Cd |v_r| v_r + 1/2 rho A Cl |v_r|^2 (w x v_r)/|w x v_r| - m g`; `S = R |w_perp| / |v_r|`, `Re = rho V D / mu` (Sutherland viscosity); wind enters through the relative velocity; density from altitude (ISA), temperature, humidity (`air_density`). Spin decays exponentially at 4 %/s (**published**: Tutelman 3.3-4 %/s, *snippet*; Smits & Smith's velocity-dependent law is not implemented).
- `Cl = cl_scale * min(cap, 0.54 S^0.4)`: the Bearman & Harvey (1976) Fig. 9 curve fit for Re > 1.26e5 as quoted by secondary sources (*snippet*; the paper was not opened). Alternative `smits_smith_sec` (`1.99 S - 3.25 S^2`, a secondary implementation, **unverified**) and `env_legacy` are selectable for comparison.
- `Cd = cd_scale * [Cd0(Re) + k_s S]`; `Cd0` has a drag crisis near Re 6e4 (dimpled-ball crisis 4-6e4, *snippet*) then a slow rise (B&H qualitative). Plateau, Re slope, crisis width, sub-critical value, and `cl_cap` are **assumptions**.
- **Calibrated** (3 numbers): `cd_scale 0.736, cl_scale 0.773, cd_spin_slope 0.590` on 30 TrackMan carry-optimizer carries plus 3 landing-angle anchors (snippet). Two scales alone could not give both carry and a 38 deg landing angle; letting the spin-drag term float fixed it. Outputs: carry, lateral at carry, apex, time to apex, hang time, descent angle, landing speed, landing spin, optional trajectory.

## 4. Bounce and roll (`bounce.py`)
Oblique-sphere bounce: `e_n = e_a/(1 + v_n/20)`, tangential impulse `P = min(mu Jn, (1+beta) u / (1/M + R^2/I))` (Coulomb cap vs stick with tangential restitution), a turf-penetration drag `dv_h = plow * v_n`, ballistic hops, then slip-to-roll and constant deceleration `a_roll`. Structure follows the USGA/R&A bounce-model report finding that roll is set by landing angle (*fetched*). Parameters (normal): e_a 0.21, mu 0.75, beta 0.10, plow 0.20, a_roll 2.95 m/s^2: **lumped, effective, calibrated** on TrackMan carry-opt + Foresight totals; `e_a` and `a_roll` sit at/near their bounds, so they are not physical turf constants. **Firmness**: soft/firm change only `a_roll` (3.69 / 2.53), solved so a tour-average shot moves -5.31 / +4.49 yd vs normal (Broadie/ShotLink via the USGA PDF, *fetched*). That is the only firmness evidence; absolute soft/firm and venue spread (5-30 yd, USGA/R&A) are **not** validated. Slope handling is flat ground only.

## 5. Contact-point API for the env (PROPOSAL, `golfphys/contact.py`)
```python
contact_to_ball(v_head_com, omega_head, n_face, toe_dir, p_contact, p_com, params)  # -> v_ball, omega_ball (world), x_toe_m, y_high_m, smash, launch fields
env_contact_to_shot(club_vel, face_normal, face_off=(dy, dz), handed="LH", toe_sign=+1)
```
Contact-point velocity = `v_com + omega x (p_contact - p_com)`; offsets are projected on the toe and face-up axes (`toe x n`) and feed the effective mass, bulge/roll and gear terms. Mapping from what the env already has at first contact: `club_vel = env._club_lin_vel()` (pre-contact), `face_normal` = world normal of the club-face geom, `face_off = env._face_off` (dy, dz in the club-geom frame, metres), `handed` from the config (the golfer is left-handed for the reference swings, so `LH`). **`toe_sign` is an assumption** (does local +y point to the toe?) to check against the club XML. Suggested env hook (not applied): at the substep where the env currently scales `qvel[0:3]` by `gain` and writes spin from `spin_k`, call `env_contact_to_shot(...)`, set `qvel[0:3] = v_ball` and the free-joint angular qvel to `xmat.T @ omega_ball` (the env already does the frame conversion for its own spin). Replaces `impact_gain`, `spin_k`, `k_off`, `k_side` and `tm_v1` by physically-linked terms; keep the env's own flag default off. If using MuJoCo's soft contact instead, use the pre-contact `v_com` and the first-contact position, not post-contact velocities. Open items: head angular velocity at contact (the env's club geom may have none), and whether the env's club-head mass is 200 g.

## 6. Parameters and status (`data/references/golfphys_coefficients.json`)
23 parameters + 3 turf rows, each with `status`, `note`, `source`. Calibrated: `e0, s_t, cd_scale, cl_scale, cd_spin_slope`, normal-turf bounce set, firmness `a_roll`. Published: Ih/Iv, gear rates, spin decay. Everything else is an assumption. Rebuild: `python -m golfphys.validate --write && python -m golfphys.implications && python -m golfphys.build_coeffs` (about 2 min).

## 7. Known gaps
No launch-monitor off-centre data; no wet/fluffy lie, slope or rough; constant-rate spin decay; spin axis rifle component ignored in lift; ball moment of inertia = uniform sphere; chart rows go only to 120 mph club speed (130-145 mph is extrapolation, one Foresight table plus one snippet pair at >=124 mph); the TrackMan chart and `total` values are themselves model output (TrackMan help: flat, normal hardness).
