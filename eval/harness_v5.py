"""Harness v5 (opt-in, `--harness v5`; 2026-10-25). Spec: docs/HARNESS_V5_SPEC.md.

v5 = the v4 grade UNCHANGED (same episodes, same verdict, v4 stays the gate for the first full pass) PLUS non-gating rows under r["v5"]:
  (a) task accuracy vs a commanded goal (carry error, start-direction error, final lateral error, draw/fade curvature sign + magnitude);
      'n/a' when the policy is not goal-conditioned (no goal found in the episode, the run args or the CLI goal spec);
  (b) per-club bands (driver / 7-iron / wedge) from data/references/club_bands_v5.json; iron/wedge bands are HELD FOR COUNSEL;
  (c) held-out DR robustness: fixed seeds and parameter ranges DISJOINT from the Trainer's training DR (checked by assert_disjoint()).
Nothing here changes eval/harness_v4.py or its verdicts."""
import json, math, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANDS_PATH = ROOT / "data" / "references" / "club_bands_v5.json"
CLUBS = ("driver", "7iron", "wedge")
SHAPES = ("straight", "draw", "fade")
NA = "n/a (policy not goal-conditioned: no goal command in episode, run args or --goal-spec)"

# ---------------------------------------------------------------- (a) goal interface + task accuracy
# Goal spec (dict). Read in this order: per-episode ep["goal"] (if the Trainer's worker logs the commanded goal), run args.json "goal",
# CLI --goal-spec JSON. Keys (SI / deg):
#   club: 'driver' | '7iron' | 'wedge'           target_carry_m: float        target_dir_deg: float (start line, + = left of +x target line, world +y)
#   shape: 'straight' | 'draw' | 'fade'          curve_m: float >= 0 (commanded |bend| at carry, metres; 0 for straight)
#   handed: 'right' | 'left' (golfer handedness; decides which world side is a draw)
GOAL_KEYS = ("club", "target_carry_m", "target_dir_deg", "shape", "curve_m")

# Trainer goal layout (Trainer a2c1c7a, reference main 3c7119db train/dr_goal.py): set_goal({club: driver|7iron|pw, target_carry (m), target_dir (deg, + = left,
# world), shape: draw|straight|fade, bend (deg SPIN AXIS magnitude), handedness: LH|RH}); obs block [116:124] = (club_driver, club_7iron, club_pw, target_carry/200,
# target_dir/10, shape +1 draw/0/-1 fade, bend/10, handedness +1 RH/-1 LH). Driver only for now (7-iron/PW always 0).
GOAL_OBS_SLICE = (116, 124)
def from_trainer_goal(g):
    """Trainer set_goal/ep['goal'] dict -> harness goal keys (idempotent for harness-format dicts)."""
    if "target_carry" not in g and "target_carry_m" in g: return dict(g)
    club = {"pw": "wedge"}.get(g.get("club", "driver"), g.get("club", "driver"))
    return dict(club=club, target_carry_m=g["target_carry"], target_dir_deg=g.get("target_dir", 0.0), shape=g.get("shape", "straight"),
                bend_deg=abs(float(g.get("bend", 0.0) or 0.0)), handed=("right" if str(g.get("handedness", "LH")).upper() == "RH" else "left"))

def decode_goal_obs(block):
    """8-float goal block (obs[116:124]) -> harness goal dict (inverse of train.dr_goal.encode_goal)."""
    b = [float(x) for x in block]
    if len(b) != 8: raise ValueError("goal block must have 8 entries")
    club = "driver" if b[0] > 0.5 else "7iron" if b[1] > 0.5 else "wedge" if b[2] > 0.5 else "driver"
    shape = "draw" if b[5] > 0.5 else "fade" if b[5] < -0.5 else "straight"
    return dict(club=club, target_carry_m=b[3] * 200.0, target_dir_deg=b[4] * 10.0, shape=shape, bend_deg=abs(b[6] * 10.0), handed=("right" if b[7] > 0 else "left"))

# Fixed deterministic v5 goal set (driver, LH model), cycled over episodes by the worker (env V5_GOALS). Trainer set_goal format.
# Fixed, deterministic goal set (revised 2026-10-25 ET to be DISCRIMINATIVE): directions span -12..+12 deg (6 of 8 beyond the 7 deg direction pass band),
# carries 110-170 m (driver at the sim's ~70 mph club speed; >= ~10% apart so one carry passes at most 3 goals at the 5% band), straight/draw/fade covered.
# A constant shot (any single carry/direction) passes at most 50% (4/8) of the direction goals and at most 3/8 of the carry goals (tests/test_harness_v5.py).
GOAL_SET_V5 = [dict(club="driver", target_carry=c, target_dir=d, shape=sh, bend=bd, handedness="LH") for c, d, sh, bd in
               ((130, -12, "straight", 0), (155, 10, "draw", 4), (110, -3, "fade", 4), (170, 8, "straight", 0),
                (120, -10, "draw", 5), (145, 3, "straight", 0), (135, 12, "fade", 5), (160, -8, "straight", 0))]

def validate_goal(g):
    """Return a normalised goal dict or raise ValueError. Accepts harness keys or the Trainer set_goal format."""
    if not isinstance(g, dict): raise ValueError("goal must be a dict")
    if "target_carry" in g: g = from_trainer_goal(g)
    miss = [k for k in ("target_carry_m",) if g.get(k) is None]
    if miss: raise ValueError(f"goal missing {miss}")
    out = dict(club=g.get("club", "driver"), target_carry_m=float(g["target_carry_m"]), target_dir_deg=float(g.get("target_dir_deg", 0.0)),
               shape=g.get("shape", "straight"), curve_m=abs(float(g.get("curve_m", 0.0) or 0.0)), handed=g.get("handed", "left"),
               bend_deg=(abs(float(g["bend_deg"])) if g.get("bend_deg") is not None else None))
    if out["club"] not in CLUBS: raise ValueError(f"club {out['club']!r} not in {CLUBS}")
    if out["shape"] not in SHAPES: raise ValueError(f"shape {out['shape']!r} not in {SHAPES}")
    if out["handed"] not in ("left", "right"): raise ValueError("handed must be 'left' or 'right'")
    if out["target_carry_m"] <= 0: raise ValueError("target_carry_m must be > 0")
    return out

def find_goal(ep=None, run_args=None, cli_goal=None):
    for src, g in (("episode", (ep or {}).get("goal")), ("run_args", (run_args or {}).get("goal")), ("cli", cli_goal)):
        if g: return validate_goal(g), src
    blk = (ep or {}).get("goal_obs_block")
    if blk: return validate_goal(decode_goal_obs(blk)), "obs_block"
    return None, None

def draw_sign(handed):
    """World +y = left of the +x target line (MuJoCo right-handed frame, z up). A right-hander's draw curves left (+y), a left-hander's right (-y).
    Confirmed by the Trainer 2026-10-25: sim world frame +y / +azimuth = left of target (golfphys/impact.py, golfphys/sim.py lateral_carry_m,
    sim/golf_simulator.py lateral_carry_yd); env.v5 shot azimuth_deg / lateral_carry_m are golfphys world-frame values."""
    return 1.0 if handed == "right" else -1.0

FRAME = "world (+y = +azimuth = left of the +x target line; golfphys/env.v5 shot_extra azimuth_deg, env_lateral_m)"

def hand_sign(handed): return 1.0 if str(handed).lower().startswith("r") else -1.0

def shot_geometry(shot_extra, handed="left"):
    """WORLD-frame carry (m), start azimuth (deg), lateral at carry (m), curvature = lateral - carry*tan(azimuth) (m, world y).
    Preferred: worker shot_extra env_carry_m / azimuth_deg / env_lateral_m (golfphys world frame). Fallback ONLY when those are absent:
    env/humanoid_golf_env.py info 'ball_lateral' / 'launch_direction' (+ 'carry'), which are GOLFER frame (x hand_sign) -> world = golfer * hand_sign."""
    s = shot_extra or {}
    c, az, lat = s.get("env_carry_m"), s.get("azimuth_deg"), s.get("env_lateral_m"); src = "world"
    if (az is None or lat is None) and s.get("ball_lateral") is not None and s.get("launch_direction") is not None:
        hs = hand_sign(handed); lat = float(s["ball_lateral"]) * hs; az = float(s["launch_direction"]) * hs; c = s.get("carry", c); src = "golfer->world (x hand_sign)"
    if c is None or az is None or lat is None: return None
    c, az, lat = float(c), float(az), float(lat)
    side, back = s.get("sidespin_rpm"), s.get("backspin_rpm")
    axis = math.degrees(math.atan2(float(side), float(back))) if side is not None and back else None   # world: + = curves left (golfphys; Trainer-confirmed)
    return dict(carry_m=c, azimuth_deg=az, lateral_m=lat, curve_y_m=lat - c * math.tan(math.radians(az)), frame_source=src, spin_axis_deg=axis)

# Thresholds (PROVISIONAL, ours, NON-GATING; held for counsel). Direction pass/warn reuse the v4 start-direction band (R22-01, |az| pass<=7 warn<=9).
TASK_T = dict(carry_err_pct=dict(pass_=5.0, warn=10.0, src="assumption (ours): |carry - target| as % of target"),
              dir_err_deg=dict(pass_=7.0, warn=9.0, src="reuses v4 mine/start_direction band (USGA/R&A R22-01 ~2 SD launch direction)"),
              lateral_err_pct=dict(pass_=7.0, warn=10.0, src="assumption (ours): |final lateral - commanded lateral| as % of target carry"),
              curve_mag_err_m=dict(pass_frac=0.5, src="assumption (ours): |curve - commanded| <= 50% of commanded |curve| (min 2 m)"),
              bend_err_deg=dict(min=2.0, frac=0.5, src="assumption (ours): | |spin axis| - commanded bend | <= max(2 deg, 50% of bend)"),
              straight_curve_m=dict(pass_=5.0, src="assumption (ours): 'straight' passes if |curve| <= 5 m"),
              rate=dict(pass_=0.80, warn=0.60, src="assumption (ours): fraction of contact episodes passing each per-episode test"))

def _band(v, p, w): return "pass" if v <= p else "warn" if v <= w else "fail"

def task_episode(geo, goal):
    tgt_lat = goal["target_carry_m"] * math.tan(math.radians(goal["target_dir_deg"]))
    sgn = draw_sign(goal["handed"]); cmd_curve_y = {"straight": 0.0, "draw": sgn * goal["curve_m"], "fade": -sgn * goal["curve_m"]}[goal["shape"]]
    carry_err = geo["carry_m"] - goal["target_carry_m"]; dir_err = geo["azimuth_deg"] - goal["target_dir_deg"]
    lat_err = geo["lateral_m"] - (tgt_lat + cmd_curve_y); curve_draw = sgn * geo["curve_y_m"]   # + = draw, - = fade (golfer frame)
    bend = goal.get("bend_deg"); ax_g = (sgn * geo["spin_axis_deg"]) if geo.get("spin_axis_deg") is not None else None   # golfer-frame axis, + = draw
    if goal["shape"] == "straight":
        shape_ok = abs(geo["curve_y_m"]) <= TASK_T["straight_curve_m"]["pass_"]; sign_ok = shape_ok
    else:
        sign_ok = (curve_draw > 0) if goal["shape"] == "draw" else (curve_draw < 0)
        if bend is not None:   # Trainer goal: bend = commanded |spin axis| (deg); magnitude graded on the spin axis
            shape_ok = sign_ok and ax_g is not None and abs(abs(ax_g) - bend) <= max(TASK_T["bend_err_deg"]["min"], TASK_T["bend_err_deg"]["frac"] * bend)
        else:
            shape_ok = sign_ok and abs(abs(geo["curve_y_m"]) - goal["curve_m"]) <= max(2.0, TASK_T["curve_mag_err_m"]["pass_frac"] * goal["curve_m"])
    return dict(carry_err_m=carry_err, carry_err_pct=100 * abs(carry_err) / goal["target_carry_m"], dir_err_deg=dir_err, lateral_err_m=lat_err,
                lateral_err_pct=100 * abs(lat_err) / goal["target_carry_m"], curve_draw_m=curve_draw, spin_axis_golfer_deg=ax_g, shape_sign_ok=bool(sign_ok), shape_ok=bool(shape_ok))

def task_accuracy(eps, goal=None, run_args=None):
    """eps: worker episodes (dicts with contact, shot_extra, optional goal). Returns one non-gating row per metric under 'v5/task_*'."""
    rows = {}; per = []
    g0, src = find_goal(eps[0] if eps else None, run_args, goal)
    if g0 is None:
        na = dict(status="n/a", passed=False, gating=False, values=dict(frame=FRAME), why=[NA], tag="info_only")
        return {k: dict(na) for k in ("v5/task_carry_error", "v5/task_direction_error", "v5/task_lateral_error", "v5/task_draw_fade")}, []
    for e in eps:
        g, _ = find_goal(e, run_args, goal)
        geo = shot_geometry(e.get("shot_extra"), (g or {}).get("handed", "left")) if e.get("contact") else None
        if geo is None: per.append(dict(seed=e.get("seed"), contact=bool(e.get("contact")), goal=g)); continue
        per.append(dict(seed=e.get("seed"), contact=True, goal=g, **geo, **task_episode(geo, g)))
    ok = [p for p in per if "carry_err_m" in p]; n = len(per)
    def rate_row(name, key, thr, label):
        if not ok: return dict(status="fail", passed=False, gating=False, values=dict(n=n, n_contact=0), why=[f"{label}: no contact episode with shot geometry"], tag="provisional")
        if key is None: ps = [p["shape_ok"] for p in ok]; med = None
        else:
            vals = sorted(abs(p[key]) for p in ok); med = vals[len(vals) // 2]; ps = [_band(abs(p[key]), thr["pass_"], thr["warn"]) == "pass" for p in ok]
        r = sum(ps) / len(ok); st = "pass" if r >= TASK_T["rate"]["pass_"] else "warn" if r >= TASK_T["rate"]["warn"] else "fail"
        return dict(status=st, passed=st == "pass", gating=False, tag="provisional (held for counsel)", values=dict(n=n, n_contact=len(ok), pass_rate=r, median_abs=med, goal_source=src, frame=FRAME,
                                                                                               shape_frame="golfer (draw = curve toward the trail->lead side: world +y for RH, -y for LH)"),
                    why=[f"{label}: {sum(ps)}/{len(ok)} contact episodes pass ({r:.2f}); NON-GATING, thresholds provisional"], ref=(thr or {}).get("src"))
    rows["v5/task_carry_error"] = rate_row("carry", "carry_err_pct", TASK_T["carry_err_pct"], "carry error <= 5% of target (warn 10%)")
    rows["v5/task_direction_error"] = rate_row("dir", "dir_err_deg", TASK_T["dir_err_deg"], "start-direction error <= 7 deg (warn 9)")
    rows["v5/task_lateral_error"] = rate_row("lat", "lateral_err_pct", TASK_T["lateral_err_pct"], "final lateral error <= 7% of target carry (warn 10%)")
    rows["v5/task_draw_fade"] = rate_row("shape", None, None, "shape: curvature sign matches command and |curve| within 50% (min 2 m) of commanded")
    if ok: rows["v5/task_draw_fade"]["values"]["sign_rate"] = sum(p["shape_sign_ok"] for p in ok) / len(ok)
    return rows, per

# ---------------------------------------------------------------- (b) per-club bands
def load_club_bands(path=BANDS_PATH):
    d = json.loads(Path(path).read_text())
    for c in CLUBS:
        if c not in d["clubs"]: raise ValueError(f"club_bands_v5.json missing {c}")
        cb = d["clubs"][c]
        if cb.get("gating_in_v5") is not False: raise ValueError(f"{c}: v5 club bands must be non-gating")
        if cb.get("status") == "pending counsel":
            if cb.get("bands") or cb.get("tour_average"): raise ValueError(f"{c}: pending-counsel club must carry no numeric bands/centres")
        elif not cb.get("bands"): raise ValueError(f"{c}: bands missing")
    return d

def _grade(v, b):
    if v is None: return "skip"
    if "fail_above" in b:
        return "fail" if v > b["fail_above"] else "warn" if (v > b["warn_above"] or v < b["warn_below"]) else "pass"
    lo, hi = b["pass"]; wl, wh = b["warn"]
    return "pass" if lo <= v <= hi else "warn" if wl <= v <= wh else "fail"

def club_band_rows(medians, club, bands=None):
    """medians: dict smash/launch_deg/spin_rpm/land_angle_deg (median over contact episodes). Non-gating rows 'v5/club_<club>_<metric>'."""
    d = bands or load_club_bands(); cb = d["clubs"][club]; out = {}
    if cb.get("status") == "pending counsel":
        return {f"v5/club_{club}_bands": dict(status="n/a", passed=False, gating=False, values=None, tag="pending counsel",
                                              why=[f"{club}: n/a - bands PENDING COUNSEL (no numbers committed); {cb.get('source_pointer', '')}"])}
    held = "held for counsel" in cb["status"]
    for k, b in cb["bands"].items():
        st = _grade(medians.get(k), b)
        out[f"v5/club_{club}_{k}"] = dict(frame="n/a (scalar launch metrics)", status=st if st != "skip" else "skip", passed=st == "pass", gating=False, values=dict(median=medians.get(k), band=b),
                                          tag=("held for counsel" if held else "sourced (v4 driver band)"), why=[f"{club} {k}: {st}; NON-GATING" + ("; band HELD FOR COUNSEL" if held else "")])
    return out

# ---------------------------------------------------------------- (c) held-out DR test set
# TRAINING DR (final; Trainer a2c1c7a, reference main 3c7119db train/dr_goal.py DR + SEED_MAX). Each dimension = list of [lo, hi] intervals
# (magnitudes for joint/vel/ball; per-joint random sign). Low bands always; high bands from curriculum stage 2 w.p. 0.2.
#   joint |dq| 0-0.03 or 0.05-0.06 rad; vel |dv| 0-0.06 or 0.10-0.12 rad/s; floor mu 0.63-1.07 or 0.45-0.54 / 1.16-1.25;
#   ball offset N(0, 11 mm) per axis capped at +-12 mm; training env seeds < 900000.
#   Extra training dims (heldout-1 does not cover them): slope 0-7% on 50% of episodes, head mass 190-210 g, loft +-1.5 deg,
#   Clauser segment-mass CVs (trunk .04, thigh .08, calf .08, foot .07; clipped at +-2 CV), torque 0.90-1.00 x stock, 20 ms latency on 25%.
TRAINING_DR = dict(source="Trainer a2c1c7a (main 3c7119db) train/dr_goal.py DR", seed_max=900000,
                   joint_rad=[[0.0, 0.03], [0.05, 0.06]], joint_vel=[[0.0, 0.06], [0.10, 0.12]], floor_mu=[[0.63, 1.07], [0.45, 0.54], [1.16, 1.25]], ball_m=[[0.0, 0.012]],
                   slope_grade=[[0.0, 0.07]], torque_scale=[[0.90, 1.00]], latency_steps=[[0, 1]], loft_deg=[[0.0, 1.5]], head_g=[[190.0, 210.0]],
                   # segment mass/inertia factor f = clip(1 + N(0, CV x breadth), 1 +- 2 CV) (Trainer f253d5d answer): trunk CV .04, thigh/calf .08, foot .07
                   seg_trunk=[[0.92, 1.08]], seg_thighcalf=[[0.84, 1.16]], seg_foot=[[0.86, 1.14]])
# Held-out 1 (UNCHANGED since 1a98372). NOTE (2026-10-25): against the final training DR, heldout-1 joint, velocity and friction now sit in the
# GAPS BETWEEN training bands (interpolation gaps, not extrapolation); only the ball offset (13-18 mm vs cap 12 mm) is beyond the training range.
HELDOUT_DR = dict(version="v5-heldout-1", seeds=list(range(910000, 910024)),
                  joint_rad=[0.0325, 0.045], joint_vel=[0.065, 0.09], floor_mu=[[0.55, 0.62], [1.08, 1.15]], ball_m=[0.013, 0.018],
                  note="per-joint |dq| ~ U(shell) with random sign; floor mu uniform over the union of bands; ball dx, dy each |.| ~ U(shell) with random sign. rng: numpy default_rng(seed + 0xD15C).")
# Held-out 2 (OPT-IN, NON-GATING, ranges = ESTIMATES just outside training; one dimension per episode, 4 episodes each, everything else nominal).
HELDOUT2_DR = dict(version="v5-heldout-2", seeds=list(range(920000, 920032)),
                   dims=("slope_grade", "torque_scale", "latency_steps", "loft_deg", "head_g", "seg_trunk", "seg_thighcalf", "seg_foot"),
                   slope_grade=[0.075, 0.10], torque_scale=[0.85, 0.89], latency_steps=[2, 2], loft_deg=[1.6, 2.5], head_g=[[185.0, 189.0], [211.0, 215.0]],
                   # segment mass: training CVs from the Data Agent rows committed in 75a97112 (goalcond_club_shot_shape_dr_refs, single cadaver study); held-out band placement (~2.5-3 SD, just beyond the +-2 CV training clip) is an UNSOURCED engineering estimate; mass and inertia scaled by the same f
                   seg_trunk=[[0.88, 0.90], [1.10, 1.12]], seg_thighcalf=[[0.76, 0.80], [1.20, 1.24]], seg_foot=[[0.79, 0.825], [1.175, 1.21]],
                   info_only_dims=("slope_grade",),
                   info_only_why="slope = modelling gap; partial plumb-address option exists on main (ea0b69da, configure(plumb_addr=True), effective only up to about 1% slope per the Trainer) (Trainer f253d5d: gravity tilt with a floor-perpendicular address pose leans the golfer ~4.6-5.7 deg; no reset bug). Excluded from the heldout-2 aggregate.",
                   note="episode i -> dims[i % 8]; seg_*: body mass and inertia x f on train.dr_goal.SEG bodies (thighcalf = thigh and calf together); slope: gravity tilt at random azimuth; torque: e.tau x scale; latency: actions delayed by k control steps (20 ms each); "
                        "loft: head geom rotated about +y by +-value; head_g: club body mass += (g-200)/1000 kg at the head geom (as DREnv). rng default_rng(seed + 0xD152).")
HARNESS_SEEDS = set(range(4000, 4008)) | set(range(8000, 8008)) | set(range(9000, 9008)) | set(range(7000, 7024))

def _ivs(x): return [list(map(float, v)) for v in x] if isinstance(x[0], (list, tuple)) else [list(map(float, x))]
def _hit(a, b): return not (a[1] < b[0] or a[0] > b[1])   # closed-interval overlap (touching counts as overlap)

def assert_disjoint(train=TRAINING_DR, held=HELDOUT_DR, training_seeds=(), other_sets=()):
    """Raise AssertionError if any held-out interval touches/overlaps any training interval of the same dimension, or a held-out seed is a training
    seed (< seed_max or listed), a harness seed, or in another held-out set."""
    dims = [k for k in ("joint_rad", "joint_vel", "floor_mu", "ball_m", "slope_grade", "torque_scale", "latency_steps", "loft_deg", "head_g", "seg_trunk", "seg_thighcalf", "seg_foot") if k in held and k in train]
    for k in dims:
        for h in _ivs(held[k]):
            for t in _ivs(train[k]): assert not _hit(h, t), f"held-out {k} {h} overlaps training {t}"
    s = set(held["seeds"]); bad = s & (set(training_seeds) | HARNESS_SEEDS)
    for o in other_sets: bad |= s & set(o["seeds"])
    assert not bad, f"held-out seeds overlap training/harness/other held-out seeds: {sorted(bad)[:5]}"
    assert min(s) >= train.get("seed_max", 0), f"held-out seeds must be >= training seed_max {train.get('seed_max')}"
    return True

def gap_kind(train, held, k):
    """'interpolation gap' if every held-out interval lies between training intervals, 'extrapolation' if beyond all of them."""
    T = _ivs(train[k]); lo, hi = min(t[0] for t in T), max(t[1] for t in T)
    return "extrapolation" if all(h[0] > hi or h[1] < lo for h in _ivs(held[k])) else "interpolation gap"

def sample_heldout2(seed, H=HELDOUT2_DR):
    import numpy as np
    i = H["seeds"].index(int(seed)) if int(seed) in H["seeds"] else int(seed); dim = H["dims"][i % len(H["dims"])]
    rg = np.random.default_rng(int(seed) + 0xD152)
    if dim == "head_g" or dim.startswith("seg_"): b = H[dim][int(rg.integers(2))]; val = float(rg.uniform(*b))
    elif dim == "latency_steps": val = int(H["latency_steps"][0])
    elif dim == "loft_deg": val = float(rg.uniform(*H["loft_deg"])) * float(rg.choice([-1.0, 1.0]))
    else: val = float(rg.uniform(*H[dim]))
    return dict(dim=dim, value=val, slope_az_rad=float(rg.uniform(0, 2 * np.pi)))

def heldout2_perturb(n=None):
    H = HELDOUT2_DR; n = len(H["seeds"]) if n is None else int(n)
    return dict(joint_deg=0.0, joint_vel=0.0, ball_tol_m=0.0, friction_rand=False, friction_range=None, seed0=H["seeds"][0], n=n,
                heldout2={k: H[k] for k in ("version", "dims", "slope_grade", "torque_scale", "latency_steps", "loft_deg", "head_g", "seg_trunk", "seg_thighcalf", "seg_foot", "seeds")},
                friction_source=f"held-out DR {H['version']} (new dims, estimates, NON-GATING)")

def heldout_perturb(n=None):
    """perturb= payload for results/overnight/_j_worker_gp_v3.py (optional 'heldout' key; absent = v3/v4 behaviour unchanged)."""
    H = HELDOUT_DR; n = len(H["seeds"]) if n is None else int(n)
    return dict(joint_deg=0.0, joint_vel=0.0, ball_tol_m=0.0, friction_rand=False, friction_range=None, seed0=H["seeds"][0], n=n,
                heldout=dict(joint_rad=H["joint_rad"], joint_vel=H["joint_vel"], floor_mu=H["floor_mu"], ball_m=H["ball_m"], version=H["version"]),
                friction_source=f"held-out DR {H['version']} (disjoint from training; NON-GATING)")

def sample_heldout(seed, nq, H=HELDOUT_DR):
    """Pure-numpy reference sampler (the worker uses exactly this). Returns dq (rad), dv (rad/s), mu, ball (dx, dy) in m."""
    import numpy as np
    rg = np.random.default_rng(int(seed) + 0xD15C)
    sh = lambda lohi, k: rg.uniform(lohi[0], lohi[1], k) * rg.choice([-1.0, 1.0], k)
    dq = sh(H["joint_rad"], nq); dv = sh(H["joint_vel"], nq)
    bands = H["floor_mu"]; w = np.array([b[1] - b[0] for b in bands]); i = int(rg.choice(len(bands), p=w / w.sum())); mu = float(rg.uniform(*bands[i]))
    ball = sh(H["ball_m"], 2)
    return dq, dv, mu, ball

# ---------------------------------------------------------------- D-plane (impact logging; NON-GATING)
# Uses ONLY the Trainer's WORLD-frame impact keys (f253d5d --impact_log, + = left). NEVER the env's face_yaw_deg / club_path_deg / ep face_path (GOLFER frame).
# Sign convention (Trainer-confirmed): + sidespin / + spin axis curves toward +y (left) in the world frame for either hand (LH draw -> -y, LH fade -> +y).
DPLANE_T = dict(face_frac=0.85, start_err_deg=2.0, axis_min_deg=0.5, curve_min_m=0.5,
                src="assumption (ours): start direction ~ 0.85 x face (D-plane rule of thumb, Trainer brief); |start - 0.85 face| <= 2 deg; curvature sign = spin-axis sign when |axis| >= 0.5 deg and |curve| >= 0.5 m")

def _dplane_per(eps):
    per = []
    for e in [e for e in (eps or []) if e.get("contact") and e.get("impact")]:
        im = e["impact"]; g = shot_geometry(e.get("shot_extra")); fw = im["impact_face_world_deg"]; pred = DPLANE_T["face_frac"] * fw
        d = dict(seed=e.get("seed"), face_world_deg=fw, path_world_deg=im.get("impact_path_world_deg"), face_to_path_world_deg=im.get("impact_face_to_path_world_deg"),
                 spin_loft_deg=im.get("impact_spin_loft_deg"), spin_axis_deg=im.get("impact_spin_axis_deg"), start_pred_deg=pred, start_deg=None, start_err_deg=None, start_ok=None, curve_y_m=None, curve_sign_ok=None)
        if g:
            d.update(start_deg=g["azimuth_deg"], start_err_deg=g["azimuth_deg"] - pred, start_ok=abs(g["azimuth_deg"] - pred) <= DPLANE_T["start_err_deg"], curve_y_m=g["curve_y_m"])
            ax = im.get("impact_spin_axis_deg")
            if ax is not None and abs(ax) >= DPLANE_T["axis_min_deg"] and abs(g["curve_y_m"]) >= DPLANE_T["curve_min_m"]: d["curve_sign_ok"] = (ax > 0) == (g["curve_y_m"] > 0)
        per.append(d)
    return per

def _dplane_stats(per):
    S = [d for d in per if d["start_ok"] is not None]; C = [d for d in per if d["curve_sign_ok"] is not None]
    med = lambda k: (sorted(d[k] for d in per if d.get(k) is not None)[len([d for d in per if d.get(k) is not None]) // 2] if any(d.get(k) is not None for d in per) else None)
    err = sorted(d["start_err_deg"] for d in S)
    q = lambda f: err[min(len(err) - 1, int(round(f * (len(err) - 1))))] if err else None
    distinct = len({(round(d["face_world_deg"], 6), None if d["start_deg"] is None else round(d["start_deg"], 6)) for d in per})
    return dict(n=len(per), start_vs_085face_pass_frac=(sum(d["start_ok"] for d in S) / len(S) if S else None), n_start=len(S),
                curve_sign_vs_axis_pass_frac=(sum(d["curve_sign_ok"] for d in C) / len(C) if C else None), n_curve_sign=len(C), distinct_starts=distinct,
                face_world_med_deg=med("face_world_deg"), path_world_med_deg=med("path_world_deg"), start_med_deg=med("start_deg"), start_err_med_deg=med("start_err_deg"),
                start_err_p10_deg=q(0.1), start_err_p90_deg=q(0.9), start_err_min_deg=(err[0] if err else None), start_err_max_deg=(err[-1] if err else None),
                spin_loft_med_deg=med("spin_loft_deg"), spin_axis_med_deg=med("spin_axis_deg"))

def dplane_row(eps, rob_eps=None):
    """v5/dplane (NON-GATING). Graded on the PERTURBED robustness episodes (v4 robustness DR, seeds 7000-7023) when they carry impact keys;
    the deterministic nominal rollouts are identical copies of one swing, so they are reported only as an n=1 'nominal' sub-entry.
    If the graded episodes are all identical (distinct_starts == 1 with n > 1) the row is n/a: 24 copies of one swing are not 24 checks."""
    per_r = _dplane_per(rob_eps); per_n = _dplane_per(eps)
    src = "robustness (perturbed, v4 robustness DR)" if per_r else "nominal (deterministic)"
    per = per_r or per_n
    if not per: return dict(status="n/a", passed=False, gating=False, values=None, tag="info_only", why=["impact logging not available (export lacks DREnv impact_log, or no contact episodes)"])
    v = _dplane_stats(per); v["source"] = src
    nom = None
    if per_n:
        ns = _dplane_stats(per_n); nd = per_n[0]
        nom = dict(n=1, n_rollouts=len(per_n), rollouts_identical=ns["distinct_starts"] == 1, face_world_deg=nd["face_world_deg"], path_world_deg=nd["path_world_deg"], start_deg=nd["start_deg"],
                   start_err_deg=nd["start_err_deg"], start_ok=nd["start_ok"], spin_axis_deg=nd["spin_axis_deg"], spin_loft_deg=nd["spin_loft_deg"], curve_sign_ok=nd["curve_sign_ok"])
    v["nominal"] = nom
    why = ["NON-GATING: D-plane check from WORLD-frame impact keys only (Trainer --impact_log); golfer-frame face_yaw_deg/club_path_deg not used", f"graded episodes: {src}, n={v['n']}, distinct_starts={v['distinct_starts']}"]
    fs, fc = v["start_vs_085face_pass_frac"], v["curve_sign_vs_axis_pass_frac"]
    if v["n"] > 1 and v["distinct_starts"] == 1:
        st = "n/a"; why.append("all graded episodes are identical (one swing repeated); a pass fraction over copies is not evidence, so status n/a")
    else:
        st = "n/a" if fs is None else ("pass" if fs >= TASK_T["rate"]["pass_"] and (fc is None or fc >= TASK_T["rate"]["pass_"]) else "warn" if fs >= TASK_T["rate"]["warn"] else "fail")
    return dict(status=st, passed=st == "pass", gating=False, tag="info_only", frame="world, + = left (+y)", thresholds=DPLANE_T, values=v,
                episodes=per, nominal_episodes=per_n if per_r else None, why=why)

# ---------------------------------------------------------------- assembly
def apply_v5(r_v4, eps=None, goal=None, run_args=None, club=None, heldout_row=None, heldout2_row=None, rob_eps=None):
    """r_v4: output of eval.harness_v4.apply_v4 (verdict untouched). Adds r['v5'] (all rows non-gating)."""
    out = dict(r_v4); v5 = dict(harness="v5", gate="v4 (unchanged; v5 rows are NON-GATING)", rows={})
    t_rows, per = task_accuracy(eps or [], goal, run_args); v5["rows"].update(t_rows); v5["task_episodes"] = per
    g, _ = find_goal((eps or [None])[0], run_args, goal)
    club = club or (g or {}).get("club") or "driver"
    med = (r_v4.get("v5_shot_medians") or {})
    v5["rows"].update(club_band_rows(med, club)); v5["club"] = club
    v5["rows"]["v5/heldout_dr_robustness"] = heldout_row or dict(status="skip", passed=False, gating=False, values=None, why=["held-out DR not run (--heldout-dr 0)"], tag="info_only")
    if heldout2_row is not None:
        if isinstance(heldout2_row, dict) and "slope_info" in heldout2_row: v5["rows"]["v5/heldout2_slope_info"] = heldout2_row.pop("slope_info")
        v5["rows"]["v5/heldout2_dr_robustness"] = heldout2_row
    v5["rows"]["v5/dplane"] = dplane_row(eps, rob_eps)
    v5["goal_obs"] = bool((run_args or {}).get("goal_obs")); v5["frame"] = FRAME
    v5["v4_verdict"] = r_v4.get("verdict"); out["v5"] = v5
    return out
