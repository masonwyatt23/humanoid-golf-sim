"""Swing-realism validation harness: does a policy's rolled-out swing look and behave like a real golf swing?
    taskset -c 0-1 python -m eval.swing_realism [--eps-per-seed 8] [--workers 2] [--models name,...]  ->  results/swing_realism.{json,md}
Rollouts: DETERMINISTIC policy, the policy's own gate env kwargs (results/<name>.json env_kwargs_full, or resid_kw_from_args for older runs; scripted rows = configs/*.json zero residual),
SAME seeds as the gate (4000 / 8000 / 9000), --eps-per-seed episodes each (gate uses 100; this is a rollout-level screen, default 8 -> 24 episodes per model; per-episode seeds = gate seeds + i).
Eight checks, PASS/FAIL each; overall PASS only if ALL pass. Reference values are PUBLISHED (cited below); every pass band built from them is marked DERIVED (mean +/- 2 SD or similar, not a published threshold).
Model facts this harness measures (not assumed): which bodies move, whether feet collide with the ground, actuator caps.  Cosmetic or hypothetical tiers (force_scale 2, power XML, impact gain) are labelled, never relabelled as human.
REFERENCES (published):
 [KS]  Cheetham, Rose, Hinrichs et al. 'Comparison of Kinematic Sequence Parameters between Amateur and Professional Golfers' (peak order pelvis, thorax, arm, club; each peak larger and later; every pro decelerates the pelvis before impact;
       typical driver peaks ~477 / 727 / 980 / 2254 deg/s pelvis / thorax / arm / club); college-male driver study PMC12416643: 515 / 760 / 1138 / 2120 deg/s; pro downswing peaks (PMC6246863 Table 2): upper torso 551.7 +- 47.6, pelvis 415.2 +- 32.9 deg/s.
 [XF]  X-factor at top of backswing, professional driver: 50.82 +- 5.68 deg (Korean pros, MSSE 2011 abstract), 54.9 +- 7.9 deg (elite, DIVA 1242118), peak X-factor mean 56 deg (Stanford 2011 pros). X-factor stretch = increase in separation early in the downswing (Cheetham; McLean).
 [TEMPO] Tour backswing:downswing about 3:1 (TPI measured 3.2:1; Tour Tempo 3:1). Downswing duration, driver: pros 0.31 +- 0.04 s, skilled amateurs 0.31 +- 0.04 s, recreational 0.25 +- 0.02 s (Golf Swing Biomechanics: Systematic Review, PMC9227529, Table 1).
 [GRF] Driver peak vertical GRF about 0.84 BW lead foot and 0.49 BW trail foot (PMC3794489, 24 golfers); trail-to-lead weight transfer through the downswing (Hume & Keogh 2005, Sports Med 35:429); coefficient of friction measured 0.62 (PMC3794489).
 [LM]  Launch-monitor driver tables: data/launch_monitor_98_120.py (TrackMan carry optimizer rows, 100 and 120 mph, AoA -5/+5), data/launch_output.py (smash 1.50 ceiling / 1.49 tour; WARN_LO 1.30 and spin windows are DERIVED there).
No human-attainable-power claim is made anywhere. Pelvis/hip rotation, ground contact and bone/joint torques of a real golfer are not published as pass/fail limits for THIS model; where a check cannot be passed because the model lacks the degree of freedom, that is reported as a structural FAIL with the measured evidence."""
import argparse, json, os, sys, math
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OUT_JSON = ROOT / "results" / "swing_realism.json"; OUT_MD = ROOT / "results" / "swing_realism.md"
DT = 0.005                       # sample period (10 substeps x 0.0005 s)
SEEDS = (4000, 8000, 9000)
MPS2MPH = 2.23694; M2YD = 1.0936
# ---- published numbers + DERIVED bands -----------------------------------------------------------------------------------------------------------------------
XF_PUB = {"korean_pros_top": (50.82, 5.68), "elite_top": (54.9, 7.9), "stanford_pros_peak": (56.0, None)}
XF_BAND = (39.4, 70.7)           # DERIVED: low = 50.82-2*5.68, high = 54.9+2*7.9
XF_STRETCH_MIN = 2.0             # deg, DERIVED (any measurable stretch of separation after the top); no published threshold
TEMPO_RATIO = (2.5, 4.0)         # DERIVED band around the published 3:1 (TPI 3.2:1)
DOWN_S = (0.21, 0.39)            # DERIVED: recreational mean-2SD (0.25-0.04) .. pro mean+2SD (0.31+0.08) from the PMC9227529 table
MU = 0.62                        # published coefficient of friction (PMC3794489)
LEAD_VERT_BW = 0.84; TRAIL_VERT_BW = 0.49   # published peak vertical GRF, driver
NEAR_LIMIT_FRAC = 0.05           # DERIVED: 'near a joint limit' = within 5% of the range
LIMIT_TIME_MAX = 0.10            # DERIVED: pass if no joint spends more than 10% of the swing near a limit
SAT_LEVEL = 0.98; SAT_TIME_MAX = 0.05   # DERIVED: |torque| >= 98% of the actuator cap; pass if <=5% of the downswing
JERK_STEP = 0.5; JERK_TIME_MAX = 0.05   # DERIVED: torque change > 50% of cap within one 5 ms sample = bang-bang step; pass if <=5% of samples
KS_DECEL = 0.95                  # DERIVED: segment speed at impact must be < 95% of its peak (published: pelvis/thorax/arm decelerate before impact)
MOVE_MIN_DPS = 20.0              # DERIVED: a segment whose peak speed is below this 'does not rotate'
CARRY_TOL = 0.0                  # carry must lie inside the TrackMan AoA -5..+5 optimizer band (published rows); beyond 120 mph the band is extrapolated (DERIVED)

def _ref_band(club_mph):
    """TrackMan carry-optimizer carry band (yd) and launch band (deg) at a club speed: linear between the published 100 and 120 mph rows at AoA -5 and +5 (published); outside 100-120 it is extrapolated (DERIVED)."""
    from data.launch_monitor_98_120 import OPT_CARRY
    lerp = lambda x, a, b, p, q: p + (q - p) * (x - a) / (b - a)
    lo = [lerp(club_mph, 100, 120, OPT_CARRY[100][-5][i], OPT_CARRY[120][-5][i]) for i in (3, 1)]
    hi = [lerp(club_mph, 100, 120, OPT_CARRY[100][5][i], OPT_CARRY[120][5][i]) for i in (3, 1)]
    return dict(carry_yd=(min(lo[0], hi[0]), max(lo[0], hi[0])), launch_deg=(min(lo[1], hi[1]), max(lo[1], hi[1])), extrapolated=not (100 <= club_mph <= 120))

# ---- model registry -------------------------------------------------------------------------------------------------------------------------------------------
def registry():
    R = [dict(key="imit20_fs1_q23_dart_s51", kind="policy", tier="stock (force_scale 1)", label="script-distilled policy"),
         dict(key="imit16_fs1_dart_s51", kind="policy", tier="stock (force_scale 1)", label="script-distilled policy"),
         dict(key="imit18_power_dart_s51", kind="policy", tier="hypothetical power tier (impact gain 1.28 inflated)", label="script-distilled policy"),
         dict(key="imit18_power_dart_s51@gain1.2", kind="policy", model="imit18_power_dart_s51", override={"impact_gain": 1.2}, tier="hypothetical power tier (impact gain 1.2, no spin model)", label="script-distilled policy"),
         dict(key="scripted_v3", kind="scripted", cfg="configs/fast_scripted_v3.json", tier="force_scale 2 (hypothetical-strength actuators)", label="SCRIPTED (not learned)"),
         dict(key="scripted_v3_fs1_q23_dz016", kind="scripted", cfg="configs/fast_scripted_v3_fs1_q23_dz016.json", tier="stock (force_scale 1)", label="SCRIPTED (not learned)"),
         dict(key="ppo_v4yaw_s43", kind="policy", tier="force_scale 2 + impact gain (HYPOTHETICAL)", label="residual PPO (yaw-only residual)"),
         dict(key="ppo15_klres_s101", kind="policy", tier="force_scale 2 (hypothetical-strength)", label="= init, not learned"),
         dict(key="ppo20_klres_s111", kind="policy", tier="stock (force_scale 1)", label="= init, not learned"),
         dict(key="ppo_resid_v3_s0", kind="policy", tier="older residual PPO (see its results JSON)", label="residual PPO (older)")]
    return [r for r in R]

def build_kw(spec):
    from eval.env_factory import resid_kw_from_args
    if spec["kind"] == "scripted":
        from eval.eval_scripted_cfg import base
        cfg = json.loads((ROOT / spec["cfg"]).read_text()); kw = dict(base)
        for k, v in cfg.items():
            if k == "script": kw["script"] = {**kw["script"], **v}
            elif k != "description": kw[k] = v
        return kw
    name = spec.get("model", spec["key"]); J = json.loads((ROOT / "results" / f"{name}.json").read_text())
    if "env_kwargs_full" in J:
        kw = dict(J["env_kwargs_full"], _env="residual", track_weight=0.0, track_set=None); kw["residual_scale"] = list(kw["residual_scale"])
    else: kw = resid_kw_from_args(J["args"])
    kw.update(spec.get("override") or {})
    return kw

# ---- rollout ---------------------------------------------------------------------------------------------------------------------------------------------------
def rollout_task(args):
    """One worker task: (spec, seed0, n) -> list of per-episode metric dicts. Heavy imports here (spawned process)."""
    spec, seed0, n = args
    import mujoco
    from eval.env_factory import make_env
    from eval.flight_tracker import FlightTracker
    kw = build_kw(spec); env = make_env(kw); m = env.model
    if spec["kind"] == "scripted":
        z = np.zeros(env.action_space.shape, np.float32); predict = lambda o: z
    else:
        from stable_baselines3 import PPO
        pol = PPO.load(str(ROOT / "models" / spec.get("model", spec["key"]))); predict = lambda o: pol.predict(o, deterministic=True)[0]
    bid = lambda nme: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, nme)
    SEG = {"pelvis": bid("torso"), "thorax": bid("chest"), "arm": bid("right_elbow"), "club": bid("right_wrist")}
    acts = [(mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, a), int(m.actuator_trnid[a][0])) for a in range(m.nu)]
    qadr = [int(m.jnt_qposadr[j]) for _, j in acts]; dadr = [int(m.jnt_dofadr[j]) for _, j in acts]
    jr = np.array([m.jnt_range[j] for _, j in acts]); gear = np.array([m.actuator_gear[a][0] for a in range(m.nu)]); caps = gear * np.array([m.actuator_forcerange[a][1] for a in range(m.nu)])   # joint torque cap N m = gear x force cap
    chest_j = [i for i, (nme, _) in enumerate(acts) if nme == "chest_yaw"][0]
    foot_b = {bid("right_ankle"): "right", bid("left_ankle"): "left"}
    head_g = m.geom("club_head").id
    mass = float(m.body_mass.sum() - m.body_mass[m.body("ball").id] - m.body_mass[m.body("target").id]); BW = mass * 9.81
    # structural facts (measured from the model)
    weld = [(int(m.eq_type[i]), mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, int(m.eq_obj1id[i])), mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, int(m.eq_obj2id[i]))) for i in range(m.neq)]
    foot_geoms = [g for g in range(m.ngeom) if int(m.geom_bodyid[g]) in foot_b]
    foot_collide = [g for g in foot_geoms if int(m.geom_contype[g]) or int(m.geom_conaffinity[g])]
    struct = dict(torso_pinned_by_env=bool(getattr(env, "pin_torso", False)), model_mass_kg=round(mass, 2), equality_constraints=[list(map(str, w)) for w in weld], foot_geoms=len(foot_geoms), foot_geoms_colliding=len(foot_collide),
                  actuator_caps_Nm=[float(c) for c in caps], actuator_names=[a for a, _ in acts], n_free_root_dofs=0)
    rec = {}; cnt = [0]; orig = mujoco.mj_step
    def wrapped(mm, d, *a_, **k_):
        orig(mm, d, *a_, **k_); cnt[0] += 1
        if rec.get("on") and cnt[0] % 10 == 0:
            rec["t"].append(d.time); rec["head"].append(d.geom_xpos[head_g].copy()); rec["ball"].append(d.xpos[env._ball_id].copy())
            rec["w"].append([float(np.linalg.norm(d.cvel[b][:3])) for b in SEG.values()])
            rec["q"].append(d.qpos[qadr].copy()); rec["qd"].append(d.qvel[dadr].copy()); rec["tau"].append(d.actuator_force * gear)
            fz = {"right": 0.0, "left": 0.0}; fs = {"right": 0.0, "left": 0.0}; ft_ = np.zeros(6)
            for ci in range(d.ncon):
                c = d.contact[ci]; g1, g2 = int(c.geom1), int(c.geom2)
                for g_, o_ in ((g1, g2), (g2, g1)):
                    if o_ == 0 and int(m.geom_bodyid[g_]) in foot_b:
                        mujoco.mj_contactForce(mm, d, ci, ft_); R = np.array(c.frame).reshape(3, 3)   # contact frame: row0 = normal; force in contact frame -> world
                        fw = R.T @ ft_[:3]; side = foot_b[int(m.geom_bodyid[g_])]; fz[side] += float(fw[2]); fs[side] += float(np.hypot(fw[0], fw[1]))
            rec["fz"].append([fz["right"], fz["left"]]); rec["fs"].append([fs["right"], fs["left"]])
            rec["foot"].append(np.r_[d.xpos[bid("right_ankle")], d.xpos[bid("left_ankle")]])
    mujoco.mj_step = wrapped
    eps = []
    try:
        for i in range(n):
            ft = FlightTracker(env).install(); seed = seed0 + i
            try:
                obs, _ = env.reset(seed=seed); ft.reset(); cnt[0] = 0
                for k in ("t", "head", "ball", "w", "q", "qd", "tau", "fz", "fs", "foot"): rec[k] = []
                rec["on"] = True; done = False; info = {}
                while not done:
                    obs, _, te, tr, info = env.step(predict(obs)); ft.step(); done = te or tr
                rec["on"] = False; s = ft.summary(info)
            finally:
                ft.close()
            e = analyse({k: np.array(rec[k]) for k in ("t", "head", "ball", "w", "q", "qd", "tau", "fz", "fs", "foot")}, jr, caps, chest_j, BW, s); e["seed"] = seed; eps.append(e)
    finally:
        mujoco.mj_step = orig
    return spec["key"], struct, eps

def analyse(R, jr, caps, chest_j, BW, s):
    """Per-episode metrics from one recorded rollout (arrays sampled every 5 ms). Phases: impact = first ball displacement > 5 mm; top = max club-head height before impact; start = club head moved > 2 cm (DERIVED)."""
    ball = R["ball"]; disp = np.linalg.norm(ball - ball[0], axis=1); imp = int(np.argmax(disp > 0.005)) if (disp > 0.005).any() else len(ball) - 1
    hz = R["head"][:, 2]; top = int(np.argmax(hz[:imp + 1])); hd = np.linalg.norm(R["head"] - R["head"][0], axis=1); st = int(np.argmax(hd > 0.02)) if (hd > 0.02).any() else 0
    e = dict(impact_idx=imp, top_idx=top, start_idx=st, true_contact=bool(s.get("true_contact")))
    bs, ds = max(top - st, 0) * DT, max(imp - top, 0) * DT
    e.update(backswing_s=bs, downswing_s=ds, tempo_ratio=(bs / ds if ds > 0 else None))
    # 1 kinematic sequence (deg/s magnitudes of body angular velocity)
    W = np.degrees(R["w"]); lo, hi = top, min(imp + 10, len(W) - 1); names = ["pelvis", "thorax", "arm", "club"]; ks = {}
    for j, nme in enumerate(names):
        seg = W[lo:hi + 1, j]; pk = int(np.argmax(seg)) + lo
        ks[nme] = dict(peak_dps=float(W[pk, j]), peak_t_ms_rel_impact=float((pk - imp) * DT * 1000), at_impact_dps=float(W[min(imp, len(W) - 1), j]))
    e["ks"] = ks
    # 2 X-factor: chest yaw relative to the (fixed) pelvis, deg, relative to address
    xf = np.abs(np.degrees(R["q"][:, chest_j] - R["q"][0, chest_j])); k_ = min(top + int(0.1 / DT), imp)
    e["xf_peak_deg"] = float(xf[:imp + 1].max()); e["xf_at_top_deg"] = float(xf[top]); e["xf_stretch_deg"] = float(max(xf[top:k_ + 1].max() - xf[top], 0.0))
    # 3 joint limits (samples start..impact+50 ms)
    a, b = st, min(imp + 10, len(R["q"]) - 1); q = R["q"][a:b + 1]; rng = (jr[:, 1] - jr[:, 0]); near = (q < jr[:, 0] + NEAR_LIMIT_FRAC * rng) | (q > jr[:, 1] - NEAR_LIMIT_FRAC * rng)
    e["limit_frac_per_joint"] = near.mean(axis=0).tolist()
    # 4 torque / power (top..impact = downswing)
    tau = R["tau"]; d_ = tau[top:imp + 1] if imp > top else tau[top:top + 1]; capn = np.maximum(caps, 1e-9)
    e["sat_frac_per_act"] = (np.abs(d_) >= SAT_LEVEL * capn).mean(axis=0).tolist()
    dj = np.abs(np.diff(tau[st:imp + 1], axis=0)) > JERK_STEP * capn; e["jerk_frac_per_act"] = (dj.mean(axis=0) if len(dj) else np.zeros(len(caps))).tolist()
    pw = (R["tau"] * R["qd"]).sum(axis=1); e["peak_power_W"] = float(np.abs(pw[st:imp + 1]).max()) if imp >= st else 0.0; e["peak_torque_over_cap"] = (np.abs(d_).max(axis=0) / capn).tolist()
    # 5 ground reaction (right foot = lead for the left-handed setup; left = trail)
    fz, fs = R["fz"], R["fs"]; e["grf_peak_vert_BW"] = [float(fz[:, 0].max() / BW), float(fz[:, 1].max() / BW)]; tot = fz.sum(axis=1)
    e["grf_total_peak_BW"] = float(tot.max() / BW) if len(tot) else 0.0
    e["grf_lead_share_top"] = float(fz[top, 0] / tot[top]) if tot[top] > 1e-6 else None; e["grf_lead_share_impact"] = float(fz[imp, 0] / tot[imp]) if tot[imp] > 1e-6 else None
    ok = fz > 0.1 * BW; ratio = np.where(ok, fs / np.maximum(fz, 1e-9), 0.0); e["grf_shear_over_normal_max"] = float(ratio.max()) if ratio.size else 0.0
    f = R["foot"]; e["foot_slip_m"] = [float(np.linalg.norm(f[imp, 0:2] - f[0, 0:2])), float(np.linalg.norm(f[imp, 3:5] - f[0, 3:5]))]
    e["foot_unloaded_frac"] = [float((fz[st:imp + 1, i] < 0.01 * BW).mean()) for i in (0, 1)]
    # 7/8 ball flight (sim flight tracker, ONE episode)
    club = float(s.get("impact_club_speed", 0.0)) * MPS2MPH; ball_v = float(s.get("peak_ball_speed", s.get("ball_speed_sep", 0.0))) * MPS2MPH   # peak ball speed, the same smash convention as the leaderboard (ratio of means, peak ball / impact club)
    e.update(club_mph=club, ball_mph=ball_v, smash=(ball_v / club if club > 0 else None), launch_deg=float(s.get("launch_elev_deg", float("nan"))), carry_yd=float(s.get("carry", 0.0)) * M2YD)
    return e

# ---- aggregate + checks ---------------------------------------------------------------------------------------------------------------------------------------
def med(xs): xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]; return float(np.median(xs)) if xs else None

def checks(struct, eps):
    C = {}; ok = [e for e in eps if e["true_contact"]] or eps
    # 1 kinematic sequence
    ks = {n: dict(peak_dps=med([e["ks"][n]["peak_dps"] for e in ok]), t_ms=med([e["ks"][n]["peak_t_ms_rel_impact"] for e in ok]), at_impact=med([e["ks"][n]["at_impact_dps"] for e in ok])) for n in ("pelvis", "thorax", "arm", "club")}
    seq = ["pelvis", "thorax", "arm", "club"]; why = []
    moving = [n for n in seq if ks[n]["peak_dps"] is not None and ks[n]["peak_dps"] >= MOVE_MIN_DPS]
    for n in seq:
        if n not in moving: why.append(f"{n} does not rotate (peak {ks[n]['peak_dps']:.1f} deg/s < {MOVE_MIN_DPS:g}): structural" + (" - the env pins the torso/pelvis (pin_torso=True, qpos/qvel reset every physics step)" if n == "pelvis" and struct["torso_pinned_by_env"] else ""))
    order_ok = all(ks[a]["t_ms"] < ks[b]["t_ms"] for a, b in zip(seq, seq[1:])) if len(moving) == 4 else False
    mag_ok = all(ks[a]["peak_dps"] < ks[b]["peak_dps"] for a, b in zip(seq, seq[1:])) if len(moving) == 4 else False
    if len(moving) == 4 and not order_ok: why.append("peak order is not pelvis < thorax < arm < club: " + ", ".join(f"{n} {ks[n]['t_ms']:+.0f} ms" for n in seq))
    if len(moving) == 4 and not mag_ok: why.append("peaks are not increasing proximal-to-distal")
    dec_ok = all(ks[n]["at_impact"] < KS_DECEL * ks[n]["peak_dps"] for n in ("pelvis", "thorax", "arm") if n in moving) and len(moving) >= 3
    if len(moving) == 4 and not dec_ok: why.append("pelvis/thorax/arm do not decelerate before impact")
    C["1_kinematic_sequence"] = dict(passed=bool(len(moving) == 4 and order_ok and mag_ok and dec_ok), values=ks, why=why, ref="[KS] order pelvis,thorax,arm,club; peaks ~477/727/980/2254 deg/s (pros)")
    # 2 X-factor
    xp, xt, xs = med([e["xf_peak_deg"] for e in ok]), med([e["xf_at_top_deg"] for e in ok]), med([e["xf_stretch_deg"] for e in ok]); why = []
    if not (XF_BAND[0] <= xp <= XF_BAND[1]): why.append(f"peak X-factor {xp:.1f} deg outside {XF_BAND[0]}-{XF_BAND[1]} (DERIVED from 50.8+-5.7 / 54.9+-7.9)")
    if xs < XF_STRETCH_MIN: why.append(f"no X-factor stretch in the early downswing ({xs:.1f} deg < {XF_STRETCH_MIN:g}, DERIVED)")
    why.append("the pelvis is pinned by the env (no pelvis rotation), so 'X-factor' here is chest yaw alone vs a fixed pelvis" if struct["torso_pinned_by_env"] else "")
    C["2_x_factor"] = dict(passed=bool(XF_BAND[0] <= xp <= XF_BAND[1] and xs >= XF_STRETCH_MIN and not struct["torso_pinned_by_env"]), values=dict(peak_deg=xp, at_top_deg=xt, stretch_deg=xs), why=[w for w in why if w], ref="[XF] 50.82+-5.68 / 54.9+-7.9 deg at top; stretch after top")
    # 3 joint limits
    lim = np.median(np.array([e["limit_frac_per_joint"] for e in ok]), axis=0); names = struct["actuator_names"]; worst = int(np.argmax(lim))
    C["3_joint_limits"] = dict(passed=bool(lim.max() <= LIMIT_TIME_MAX), values={n: float(x) for n, x in zip(names, lim)}, why=([f"{names[worst]} within {NEAR_LIMIT_FRAC*100:.0f}% of a limit {lim[worst]*100:.0f}% of the swing (> {LIMIT_TIME_MAX*100:.0f}%, DERIVED)"] if lim.max() > LIMIT_TIME_MAX else []), ref="DERIVED: 5% of range, 10% of the swing")
    # 4 torque / power
    sat = np.median(np.array([e["sat_frac_per_act"] for e in ok]), axis=0); jer = np.median(np.array([e["jerk_frac_per_act"] for e in ok]), axis=0); pk = np.median(np.array([e["peak_torque_over_cap"] for e in ok]), axis=0)
    why = []
    if sat.max() > SAT_TIME_MAX: why.append(f"{names[int(np.argmax(sat))]} at its actuator cap {sat.max()*100:.0f}% of the downswing (> {SAT_TIME_MAX*100:.0f}%, DERIVED)")
    if jer.max() > JERK_TIME_MAX: why.append(f"{names[int(np.argmax(jer))]} bang-bang torque steps in {jer.max()*100:.0f}% of samples (> {JERK_TIME_MAX*100:.0f}%, DERIVED)")
    C["4_torque_power"] = dict(passed=bool(sat.max() <= SAT_TIME_MAX and jer.max() <= JERK_TIME_MAX), values=dict(peak_power_W=med([e["peak_power_W"] for e in ok]), max_sat_frac=float(sat.max()), max_jerk_frac=float(jer.max()), peak_torque_over_cap={n: float(x) for n, x in zip(names, pk)}, caps_Nm={n: c for n, c in zip(names, struct["actuator_caps_Nm"])}), why=why, ref="DERIVED saturation/smoothness limits; peak power informational (no published per-joint pass limit used)")
    # 5 ground reaction
    pv = [med([e["grf_peak_vert_BW"][i] for e in ok]) for i in (0, 1)]; ls_t, ls_i = med([e["grf_lead_share_top"] for e in ok]), med([e["grf_lead_share_impact"] for e in ok]); why = []
    if struct["foot_geoms_colliding"] == 0: why.append(f"feet do not collide with the ground in this model (0 of {struct['foot_geoms']} foot geoms have collision enabled): ground reaction = {max(pv):.2f} BW by construction")
    if ls_t is None or ls_i is None: why.append("no weight shift measurable (no foot force)")
    else:
        if not (ls_i - ls_t >= 0.1): why.append(f"no trail-to-lead weight shift ({ls_t:.2f} -> {ls_i:.2f} lead share; need +0.10, DERIVED)")
    gp = bool(struct["foot_geoms_colliding"] > 0 and pv[0] >= 0.5 * LEAD_VERT_BW and ls_t is not None and ls_i is not None and ls_i - ls_t >= 0.1)
    C["5_ground_reaction"] = dict(passed=gp, values=dict(peak_vert_BW_lead=pv[0], peak_vert_BW_trail=pv[1], lead_share_top=ls_t, lead_share_impact=ls_i, shear_over_normal_max=med([e["grf_shear_over_normal_max"] for e in ok]), foot_slip_m=[med([e["foot_slip_m"][i] for e in ok]) for i in (0, 1)], mu_published=MU), why=why, ref="[GRF] driver 0.84 BW lead / 0.49 BW trail peak vertical; weight shift trail->lead; mu 0.62")
    # 6 tempo
    bs, dsw, tr = med([e["backswing_s"] for e in ok]), med([e["downswing_s"] for e in ok]), med([e["tempo_ratio"] for e in ok]); why = []
    if not (TEMPO_RATIO[0] <= tr <= TEMPO_RATIO[1]): why.append(f"backswing:downswing {tr:.2f}:1 outside {TEMPO_RATIO[0]}-{TEMPO_RATIO[1]} (DERIVED around the published 3:1)")
    if not (DOWN_S[0] <= dsw <= DOWN_S[1]): why.append(f"downswing {dsw*1000:.0f} ms outside the human {DOWN_S[0]*1000:.0f}-{DOWN_S[1]*1000:.0f} ms (published pro 310+-40 ms, recreational 250+-20 ms)")
    C["6_tempo"] = dict(passed=bool(TEMPO_RATIO[0] <= tr <= TEMPO_RATIO[1] and DOWN_S[0] <= dsw <= DOWN_S[1]), values=dict(backswing_s=bs, downswing_s=dsw, ratio=tr), why=why, ref="[TEMPO] 3:1 (TPI 3.2:1); downswing driver 0.31+-0.04 s pros")
    # 7 ball flight vs launch-monitor tables
    club, carry, launch, smash = med([e["club_mph"] for e in ok]), med([e["carry_yd"] for e in ok]), med([e["launch_deg"] for e in ok]), med([e["smash"] for e in ok]); band = _ref_band(club); why = []
    if not (band["carry_yd"][0] - CARRY_TOL <= carry <= band["carry_yd"][1] + CARRY_TOL): why.append(f"carry {carry:.0f} yd outside the TrackMan AoA -5..+5 optimizer band {band['carry_yd'][0]:.0f}-{band['carry_yd'][1]:.0f} yd at {club:.0f} mph" + (" (band extrapolated outside 100-120 mph, DERIVED)" if band["extrapolated"] else ""))
    if not (band["launch_deg"][0] <= launch <= band["launch_deg"][1]): why.append(f"launch {launch:.1f} deg outside the same band {band['launch_deg'][0]:.1f}-{band['launch_deg'][1]:.1f} deg")
    C["7_ball_flight_tables"] = dict(passed=not why, values=dict(club_mph=club, carry_yd=carry, launch_deg=launch, smash=smash, ref_band=band), why=why, ref="[LM] TrackMan carry-optimizer rows 100/120 mph (data/launch_monitor_98_120.py)")
    # 8 smash / spin flags (data.launch_output.flags): spin is not simulated, so it can only be 'absent'
    from data.launch_output import flags
    fl = flags(dict(smash=smash, spin_rpm=None, launch_deg=launch)); fl = [f for f in fl if f.startswith("FAIL") or f.startswith("WARN smash")]
    C["8_smash_spin_flags"] = dict(passed=not fl, values=dict(smash=smash, spin_rpm=None, spin_source="absent (no spin model)", flags=fl), why=fl + ["spin is not simulated (hand-set backspin), so no spin check is possible"], ref="data/launch_output.py: FAIL >1.50, WARN >1.49, WARN <1.30 (derived)")
    return C

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--eps-per-seed", type=int, default=8); ap.add_argument("--workers", type=int, default=2); ap.add_argument("--models", default="")
    a = ap.parse_args(); reg = registry()
    if a.models: reg = [r for r in reg if r["key"] in a.models.split(",")]
    import multiprocessing as mp
    ctx = mp.get_context("spawn"); jobs = [(r, s, a.eps_per_seed) for r in reg for s in SEEDS]; res = {}
    with ctx.Pool(min(a.workers, 2)) as pool:
        for key, struct, eps in pool.imap_unordered(rollout_task, jobs):
            res.setdefault(key, dict(struct=struct, eps=[]))["eps"] += eps; print("done", key, len(res[key]["eps"]), flush=True)
    out = dict(protocol=f"deterministic rollouts, gate seeds {list(SEEDS)} x {a.eps_per_seed} episodes (seed+i), gate env kwargs; medians over true-contact episodes", derived_note="every band marked DERIVED is built from published mean+-SD, not a published threshold", models={})
    for r in reg:
        if r["key"] not in res: continue
        x = res[r["key"]]; C = checks(x["struct"], x["eps"]); npass = sum(c["passed"] for c in C.values())
        out["models"][r["key"]] = dict(tier=r["tier"], label=r["label"], kind=r["kind"], n_episodes=len(x["eps"]), true_contact=sum(e["true_contact"] for e in x["eps"]), structure=x["struct"], checks=C, checks_passed=int(npass), verdict="PASS" if npass == len(C) else "FAIL", seeds={str(s): sum(1 for e in x["eps"] if e["seed"] // 1 >= s and e["seed"] < s + a.eps_per_seed) for s in SEEDS})
    OUT_JSON.write_text(json.dumps(out, indent=1, default=float)); OUT_MD.write_text(to_md(out)); print("wrote", OUT_JSON, OUT_MD)

def to_md(out):
    names = list(next(iter(out["models"].values()))["checks"]) if out["models"] else []
    L = ["# Swing realism: does the rolled-out swing look and behave like a real golf swing?", "",
         "**Protocol:** " + out["protocol"] + ". " + out["derived_note"] + ". References are cited in `eval/swing_realism.py` (Cheetham et al. kinematic sequence; Korean-pro / elite / Stanford X-factor; PMC9227529 downswing times; TPI tempo; PMC3794489 GRF and friction; TrackMan optimizer rows).", "",
         "**Overall verdict = PASS only if all 8 checks pass.** No human-attainable-power claim is made; force_scale 2 and the power tier are hypothetical.", "",
         "| model | tier | verdict | passed | " + " | ".join(n.split("_", 1)[1] for n in names) + " |", "|---|---|---|---|" + "---|" * len(names)]
    for k, m in out["models"].items(): L.append(f"| {k} | {m['tier']} | **{m['verdict']}** | {m['checks_passed']}/8 | " + " | ".join("PASS" if m["checks"][n]["passed"] else "FAIL" for n in names) + " |")
    L += ["", "## Why each model fails", ""]
    for k, m in out["models"].items():
        L += [f"### {k} ({m['label']}; {m['tier']}; {m['n_episodes']} episodes)", ""]
        for n in names:
            c = m["checks"][n]
            if not c["passed"]: L.append(f"- **FAIL {n}**: " + "; ".join(c["why"]) if c["why"] else f"- **FAIL {n}**")
        v = m["checks"]
        L += ["", f"Key numbers: downswing {v['6_tempo']['values']['downswing_s']*1000:.0f} ms, backswing:downswing {v['6_tempo']['values']['ratio']:.2f}:1, X-factor peak {v['2_x_factor']['values']['peak_deg']:.1f} deg, club {v['7_ball_flight_tables']['values']['club_mph']:.1f} mph, smash {v['7_ball_flight_tables']['values']['smash']:.2f}, carry {v['7_ball_flight_tables']['values']['carry_yd']:.0f} yd, peak power {v['4_torque_power']['values']['peak_power_W']:.0f} W", ""]
    s0 = next(iter(out["models"].values()))["structure"] if out["models"] else {}
    L += ["## Model structure (measured, same for all rows)", "", f"- Torso/pelvis pinned by the env each physics step (`pin_torso`): {s0.get('torso_pinned_by_env')} (no pelvis translation or rotation, so the kinematic sequence cannot start at the pelvis, and the whole body cannot shift weight); equality constraints (hands grip only): {s0.get('equality_constraints')}",
          f"- Foot geoms: {s0.get('foot_geoms')}, with collision enabled: {s0.get('foot_geoms_colliding')} (no ground reaction force exists)", f"- Model mass {s0.get('model_mass_kg')} kg; only one trunk rotation DOF (chest_yaw), pitch-only hips/knees/ankles."]
    L += ["", "## Check of the 'pelvis = 0 / X-factor = 0' finding (raw-trace audit, 2026-10-17): NOT a recording error", "",
          "Rolled out one scripted v3 (fs1 q23 dz016), one scripted v3 (fs2) and one imit20 swing (seed 4000) and dumped raw MuJoCo state every 5 ms:",
          "- What the harness reads: pelvis = body `torso`, thorax = body `chest`, lead arm = body `right_elbow`, club = body `right_wrist`; speed = |`data.cvel[body][:3]`| (world angular velocity, rad/s) x 180/pi = deg/s. X-factor = joint `chest_yaw` (`qpos[20]`, rad, relative to the pelvis because the pelvis does not turn) x 180/pi = deg.",
          "- `pin_torso` really pins the pelvis: `env.pin_torso` is True (residual env default) and the env resets `qpos[7:14]` and `qvel[6:12]` every physics step; measured torso quaternion deviation 0.0, root qpos deviation 1.2e-5, root qvel max 0.05 (it is reset after each step, so the residual is sub-step noise).",
          "- Raw `chest_yaw`: total range 0.0095 deg (scripted fs1), 0.0138 deg (scripted fs2), 0.0096 deg (imit20); max |qvel| 0.62-0.69 deg/s, against a joint range of +-45 deg. The chest does not rotate in these swings (the scripts have `yaw_ff` 0.0 and the yaw channel is not driven), so X-factor ~ 0 deg and the thorax speed ~ 0.3-0.7 deg/s are real, not units or indexing errors. Even the yaw-residual PPO (ppo_v4yaw_s43) reaches only 0.07 deg and the older ppo_resid_v3_s0 0.37 deg.", ""]
    return "\n".join(L) + "\n"

if __name__ == "__main__": main()
