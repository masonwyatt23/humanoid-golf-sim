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

def validate_goal(g):
    """Return a normalised goal dict or raise ValueError."""
    if not isinstance(g, dict): raise ValueError("goal must be a dict")
    miss = [k for k in ("target_carry_m",) if g.get(k) is None]
    if miss: raise ValueError(f"goal missing {miss}")
    out = dict(club=g.get("club", "driver"), target_carry_m=float(g["target_carry_m"]), target_dir_deg=float(g.get("target_dir_deg", 0.0)),
               shape=g.get("shape", "straight"), curve_m=abs(float(g.get("curve_m", 0.0) or 0.0)), handed=g.get("handed", "left"))
    if out["club"] not in CLUBS: raise ValueError(f"club {out['club']!r} not in {CLUBS}")
    if out["shape"] not in SHAPES: raise ValueError(f"shape {out['shape']!r} not in {SHAPES}")
    if out["handed"] not in ("left", "right"): raise ValueError("handed must be 'left' or 'right'")
    if out["target_carry_m"] <= 0: raise ValueError("target_carry_m must be > 0")
    return out

def find_goal(ep=None, run_args=None, cli_goal=None):
    for src, g in (("episode", (ep or {}).get("goal")), ("run_args", (run_args or {}).get("goal")), ("cli", cli_goal)):
        if g: return validate_goal(g), src
    return None, None

def draw_sign(handed):
    """World +y = left of the +x target line (MuJoCo right-handed frame, z up). A right-hander's draw curves left (+y), a left-hander's right (-y).
    SIGN CONVENTION TO BE CONFIRMED by the Trainer against the env's lateral_carry_m sign."""
    return 1.0 if handed == "right" else -1.0

def shot_geometry(shot_extra):
    """From the worker's per-episode shot_extra: carry (m), start azimuth (deg), lateral at carry (m), curvature = lateral - carry*tan(azimuth) (m, world y)."""
    s = shot_extra or {}
    c, az, lat = s.get("env_carry_m"), s.get("azimuth_deg"), s.get("env_lateral_m")
    if c is None or az is None or lat is None: return None
    c, az, lat = float(c), float(az), float(lat)
    return dict(carry_m=c, azimuth_deg=az, lateral_m=lat, curve_y_m=lat - c * math.tan(math.radians(az)))

# Thresholds (PROVISIONAL, ours, NON-GATING; held for counsel). Direction pass/warn reuse the v4 start-direction band (R22-01, |az| pass<=7 warn<=9).
TASK_T = dict(carry_err_pct=dict(pass_=5.0, warn=10.0, src="assumption (ours): |carry - target| as % of target"),
              dir_err_deg=dict(pass_=7.0, warn=9.0, src="reuses v4 mine/start_direction band (USGA/R&A R22-01 ~2 SD launch direction)"),
              lateral_err_pct=dict(pass_=7.0, warn=10.0, src="assumption (ours): |final lateral - commanded lateral| as % of target carry"),
              curve_mag_err_m=dict(pass_frac=0.5, src="assumption (ours): |curve - commanded| <= 50% of commanded |curve| (min 2 m)"),
              straight_curve_m=dict(pass_=5.0, src="assumption (ours): 'straight' passes if |curve| <= 5 m"),
              rate=dict(pass_=0.80, warn=0.60, src="assumption (ours): fraction of contact episodes passing each per-episode test"))

def _band(v, p, w): return "pass" if v <= p else "warn" if v <= w else "fail"

def task_episode(geo, goal):
    tgt_lat = goal["target_carry_m"] * math.tan(math.radians(goal["target_dir_deg"]))
    sgn = draw_sign(goal["handed"]); cmd_curve_y = {"straight": 0.0, "draw": sgn * goal["curve_m"], "fade": -sgn * goal["curve_m"]}[goal["shape"]]
    carry_err = geo["carry_m"] - goal["target_carry_m"]; dir_err = geo["azimuth_deg"] - goal["target_dir_deg"]
    lat_err = geo["lateral_m"] - (tgt_lat + cmd_curve_y); curve_draw = sgn * geo["curve_y_m"]   # + = draw, - = fade (golfer frame)
    if goal["shape"] == "straight": shape_ok = abs(geo["curve_y_m"]) <= TASK_T["straight_curve_m"]["pass_"]; sign_ok = shape_ok
    else:
        sign_ok = (curve_draw > 0) if goal["shape"] == "draw" else (curve_draw < 0)
        shape_ok = sign_ok and abs(abs(geo["curve_y_m"]) - goal["curve_m"]) <= max(2.0, TASK_T["curve_mag_err_m"]["pass_frac"] * goal["curve_m"])
    return dict(carry_err_m=carry_err, carry_err_pct=100 * abs(carry_err) / goal["target_carry_m"], dir_err_deg=dir_err, lateral_err_m=lat_err,
                lateral_err_pct=100 * abs(lat_err) / goal["target_carry_m"], curve_draw_m=curve_draw, shape_sign_ok=bool(sign_ok), shape_ok=bool(shape_ok))

def task_accuracy(eps, goal=None, run_args=None):
    """eps: worker episodes (dicts with contact, shot_extra, optional goal). Returns one non-gating row per metric under 'v5/task_*'."""
    rows = {}; per = []
    g0, src = find_goal(eps[0] if eps else None, run_args, goal)
    if g0 is None:
        na = dict(status="n/a", passed=False, gating=False, values=None, why=[NA], tag="info_only")
        return {k: dict(na) for k in ("v5/task_carry_error", "v5/task_direction_error", "v5/task_lateral_error", "v5/task_draw_fade")}, []
    for e in eps:
        g, _ = find_goal(e, run_args, goal)
        geo = shot_geometry(e.get("shot_extra")) if e.get("contact") else None
        if geo is None: per.append(dict(seed=e.get("seed"), contact=bool(e.get("contact")), goal=g)); continue
        per.append(dict(seed=e.get("seed"), contact=True, goal=g, **geo, **task_episode(geo, g)))
    ok = [p for p in per if "carry_err_m" in p]; n = len(per)
    def rate_row(name, key, thr, label):
        if not ok: return dict(status="fail", passed=False, gating=False, values=dict(n=n, n_contact=0), why=[f"{label}: no contact episode with shot geometry"], tag="provisional")
        if key is None: ps = [p["shape_ok"] for p in ok]; med = None
        else:
            vals = sorted(abs(p[key]) for p in ok); med = vals[len(vals) // 2]; ps = [_band(abs(p[key]), thr["pass_"], thr["warn"]) == "pass" for p in ok]
        r = sum(ps) / len(ok); st = "pass" if r >= TASK_T["rate"]["pass_"] else "warn" if r >= TASK_T["rate"]["warn"] else "fail"
        return dict(status=st, passed=st == "pass", gating=False, tag="provisional (held for counsel)", values=dict(n=n, n_contact=len(ok), pass_rate=r, median_abs=med, goal_source=src),
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
        out[f"v5/club_{club}_{k}"] = dict(status=st if st != "skip" else "skip", passed=st == "pass", gating=False, values=dict(median=medians.get(k), band=b),
                                          tag=("held for counsel" if held else "sourced (v4 driver band)"), why=[f"{club} {k}: {st}; NON-GATING" + ("; band HELD FOR COUNSEL" if held else "")])
    return out

# ---------------------------------------------------------------- (c) held-out DR test set
# Training DR as found in the Trainer clone (box HEAD 4c3ad3d, train/v5_train_j.py + results/v5_runs/v11o_cmd.txt / args.json; V9-V11 runs):
#   joint angle noise init_qn U(+-0.03 rad) per actuated joint; joint vel init_qvn U(+-0.06 rad/s); floor mu fr_rand U(0.65, 1.05);
#   ball xy ball_tol U(+-0.012 m) per axis (square). Env-level friction_rand U(0.5, 1.2) is a Stage A option (off in J runs).
# MUST be re-checked against the Trainer's new heavy-DR config before any held-out number is quoted (see spec).
TRAINING_DR = dict(source="Trainer box HEAD 4c3ad3d (V9-V11 J runs); RE-CHECK against the heavy-DR config",
                   joint_rad=[0.0, 0.03], joint_vel=[0.0, 0.06], floor_mu=[[0.65, 1.05]], ball_m=[0.0, 0.012])
# Cross-check vs PureGolf Data Agent DR refs (PENDING, Repo Agent 7b9faa3; cite as pending): Langdown, Bridge & Li (Int J Golf Sci 2(1)) skilled
# within-golfer stance-to-ball SD 11.0 mm (n=1 study) -> training ball +-12 mm ~ 1.1 SD, held-out 13-18 mm ~ 1.2-1.6 SD (plausible, outside training).
# Penner 2002 ball-TURF friction (0.25-0.4) is ball/green, NOT foot/floor mu -> not applicable to floor_mu. Driver DR rows (head mass 190-210 g,
# lie 56-60, loft +-2) are not randomised in training today -> candidate new DR dims once the Trainer's heavy-DR config lands. No range moved.
PENDING_DR_CROSSCHECK = dict(status="pending (Data Agent 7b9faa3)", address_stance_ball_sd_mm=11.0, applies_to="ball_m",
                             not_applicable=["Penner 2002 ball-turf friction (not foot-floor)"], candidates=["driver head mass", "lie", "loft"])
# Held-out: every sampled component lies strictly OUTSIDE its training range (magnitude shells / friction bands beyond both edges).
HELDOUT_DR = dict(version="v5-heldout-1", seeds=list(range(910000, 910024)),
                  joint_rad=[0.0325, 0.045], joint_vel=[0.065, 0.09], floor_mu=[[0.55, 0.62], [1.08, 1.15]], ball_m=[0.013, 0.018],
                  note="per-joint |dq| ~ U(shell) with random sign; floor mu uniform over the union of bands; ball dx, dy each |.| ~ U(shell) with random sign. rng: numpy default_rng(seed + 0xD15C).")
# Seeds used elsewhere by our harness (must stay disjoint from held-out): deterministic rows 4000-4007, 8000-8007, 9000-9007; v3/v4 robustness 7000-7023.
HARNESS_SEEDS = set(range(4000, 4008)) | set(range(8000, 8008)) | set(range(9000, 9008)) | set(range(7000, 7024))

def _overlap(a, b):
    return max(a[0], b[0]) < min(a[1], b[1]) or (a[0] == b[0] and a[1] == b[1])

def assert_disjoint(train=TRAINING_DR, held=HELDOUT_DR, training_seeds=()):
    """Raise AssertionError if any held-out range overlaps its training range, or any held-out seed is a training or harness seed."""
    for k in ("joint_rad", "joint_vel", "ball_m"):
        assert not _overlap(held[k], train[k]) and held[k][0] > train[k][1], f"held-out {k} {held[k]} overlaps training {train[k]}"
    for hb in held["floor_mu"]:
        for tb in train["floor_mu"]: assert not _overlap(hb, tb) and not (tb[0] <= hb[0] <= tb[1] or tb[0] <= hb[1] <= tb[1]), f"held-out floor mu {hb} overlaps training {tb}"
    s = set(held["seeds"]); bad = s & (set(training_seeds) | HARNESS_SEEDS)
    assert not bad, f"held-out seeds overlap training/harness seeds: {sorted(bad)[:5]}"
    return True

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

# ---------------------------------------------------------------- assembly
def apply_v5(r_v4, eps=None, goal=None, run_args=None, club=None, heldout_row=None):
    """r_v4: output of eval.harness_v4.apply_v4 (verdict untouched). Adds r['v5'] (all rows non-gating)."""
    out = dict(r_v4); v5 = dict(harness="v5", gate="v4 (unchanged; v5 rows are NON-GATING)", rows={})
    t_rows, per = task_accuracy(eps or [], goal, run_args); v5["rows"].update(t_rows); v5["task_episodes"] = per
    g, _ = find_goal((eps or [None])[0], run_args, goal)
    club = club or (g or {}).get("club") or "driver"
    med = (r_v4.get("v5_shot_medians") or {})
    v5["rows"].update(club_band_rows(med, club)); v5["club"] = club
    v5["rows"]["v5/heldout_dr_robustness"] = heldout_row or dict(status="skip", passed=False, gating=False, values=None, why=["held-out DR not run (--heldout-dr 0)"], tag="info_only")
    v5["v4_verdict"] = r_v4.get("verdict"); out["v5"] = v5
    return out
