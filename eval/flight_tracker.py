"""
flight_tracker (MINIMAL EQUIVALENT, written by the evaluator; no pre-existing
flight_tracker.py was found anywhere on the box).

Records the ball trajectory (world frame) every env step and summarizes dispersion.

Conventions (MuJoCo world frame, golfer facing +x, z up, right-handed axes):
  x = down-the-line (forward), +y = LEFT of the target line, -y = RIGHT, z = up.
  Target line = the x axis through the ball's start y (=0).
Lateral miss: final |y| > LATERAL_THRESHOLD_M (default 0.5 m).
  left miss  : final y > +threshold ;  right miss : final y < -threshold.
Impact club speed = |linear velocity| of club_head geom at the first club-ball contact step (env info).
Peak club speed = max over every physics substep (club speed = world-frame linear part v[3:] of mj_objectVelocity for the club_head geom; samples >100 m/s or non-finite are NON-PHYSICAL: such episodes are flagged and excluded from peak stats, never clipped) of the whole episode of club_head linear speed (m/s; x2.23694 = mph); target 120 mph = 53.64 m/s.
Smash factor = peak ball speed (m/s over the episode) / impact club speed, per contact shot with club speed > MIN_CLUB_SPEED, then averaged.
Distance = final ball x (total/rolled), carry from env info (0 if never landed after flight).
"""
from typing import Dict, Sequence
import warnings
import numpy as np

M_TO_YD = 1.09361   # 1 m = 1.09361 yd
LATERAL_THRESHOLD_M = 0.5
MPS_TO_MPH = 2.23694
TARGET_MPH = 120.0
TARGET_MS = 53.64     # 120 mph
MAX_PLAUSIBLE_CLUB_SPEED = 100.0  # m/s; above this the MuJoCo sim blew up (unstable QACC), not a real speed
FLAT_LAUNCH_DEG = 5.0   # launch elevation below this = flat/negative (flagged): mean < 5 deg or >= 50% of shots < 5 deg
LAND_Z = 0.03          # m; ball centre height counted as touchdown (matches env carry rule)
LAND_MIN_APEX = 0.5    # m; ball must have flown above this before touchdown counts
MIN_CLUB_SPEED = 0.05  # m/s; smash factor undefined below this


class FlightTracker:
    def __init__(self, env):
        self.env, self.traj = env, []

    def install(self, track_landing=False):
        """Patch mujoco.mj_step to sample club_head speed after EVERY physics substep (peak over whole swing)."""
        import mujoco
        self._mj, self._orig, self.peak_club = mujoco, mujoco.mj_step, 0.0
        self.n_nonphysical, self.raw_max, self.first_bad_t = 0, 0.0, None
        self._sep, self._last_v, self.v_sep = False, None, None
        self._hist, self.club_pre = [], float('nan')
        self._seq_init()
        self.track_landing = bool(track_landing); self._land_reset()
        def wrapped(m, d, *a, **k):
            self._orig(m, d, *a, **k)
            v = self.env._club_speed()
            self._hist.append(v)
            self._seq_n += 1
            if self._seq_n % 10 == 0:   # every 10th substep (5 ms): |joint angular velocity| of the sequencing segments + club speed
                self._seq_t.append(float(d.time)); self._seq_v.append([abs(d.qvel[i]) if i is not None else np.nan for i in self._seq_dofs] + [v])
            if self.track_landing and self.land_v is None:   # opt-in: ball velocity at first descent through z<LAND_Z after it has flown above LAND_MIN_APEX
                bz = float(self.env.data.xpos[self.env._ball_id][2]); self._land_apex = max(self._land_apex, bz)
                if self._land_apex > LAND_MIN_APEX and bz < LAND_Z:
                    self.land_v = np.array(self.env._ball_lin_vel(), float)
            if self.env.true_contact and self.t_impact is None: self.t_impact = float(d.time)
            if self.env.true_contact and self.club_pre != self.club_pre and len(self._hist) >= 3: self.club_pre = self._hist[-3]
            if not np.isfinite(v) or v > MAX_PLAUSIBLE_CLUB_SPEED:   # validate; never silently clip
                self.n_nonphysical += 1
                self.raw_max = max(self.raw_max, v) if np.isfinite(v) else float("inf")
                if self.first_bad_t is None: self.first_bad_t = float(d.time)
            else:
                self.peak_club = max(self.peak_club, v)
            # launch vector = ball velocity at the end of club-ball contact (first substep without contact after first true contact)
            if self.env.true_contact and not self._sep:
                bv = self.env._ball_lin_vel(); self._last_v = bv
                if not self.env._check_contact():
                    self._sep, self.v_sep = True, bv
        mujoco.mj_step = wrapped
        return self

    def close(self):
        if getattr(self, "_orig", None) is not None:
            self._mj.mj_step = self._orig; self._orig = None

    def _land_reset(self):
        self.land_v, self._land_apex = None, 0.0

    def reset(self):
        self._land_reset()
        self.peak_club, self.n_nonphysical, self.raw_max, self.first_bad_t = 0.0, 0, 0.0, None
        self._sep, self._last_v, self.v_sep = False, None, None
        self._hist, self.club_pre = [], float("nan")
        self._seq_init()
        self.traj = [self.env.data.xpos[self.env._ball_id].copy()]

    def step(self):
        self.traj.append(self.env.data.xpos[self.env._ball_id].copy())

    SEQ_SEGMENTS = [("hips", ("right_hip_pitch", "left_hip_pitch")), ("torso(chest_yaw)", ("chest_yaw",)), ("shoulder_R", ("right_shoulder_pitch",)),
                    ("elbow_R", ("right_elbow",)), ("wrist_R", ("right_wrist",)), ("club_head_speed", None)]
    SEQ_WINDOW = (-0.30, 0.05)   # s relative to first true contact

    def _seq_init(self):
        import mujoco
        self._seq_n, self._seq_t, self._seq_v, self.t_impact = 0, [], [], None
        if not hasattr(self, "_seq_dofs"):
            m, dofs = self.env.model, []
            for _, names in self.SEQ_SEGMENTS:
                for n in (names or ()):
                    try: dofs.append(int(m.jnt_dofadr[m.joint(n).id]))
                    except Exception: dofs.append(None)
            self._seq_dofs = dofs

    def seq_summary(self):
        """Time of peak |angular velocity| of each segment (hips, chest yaw, shoulder, elbow, wrist; club-head speed) relative to impact (ms), within
        [impact-0.30 s, impact+0.05 s]. Proximal-to-distal = peak times non-decreasing in the listed order (5 ms resolution; ties count as in order). NaN if no contact."""
        out = {"seq_ok": False}
        if self.t_impact is None or not self._seq_t: return out
        t = np.asarray(self._seq_t); V = np.asarray(self._seq_v); lo, hi = self.t_impact + self.SEQ_WINDOW[0], self.t_impact + self.SEQ_WINDOW[1]
        w = (t >= lo) & (t <= hi)
        if w.sum() < 5: return out
        cols, k = [], 0
        for name, names in self.SEQ_SEGMENTS:
            if names is None: cols.append(V[:, -1]); continue
            idx = list(range(k, k + len(names))); k += len(names)
            cols.append(np.nanmean(V[:, idx], axis=1) if not np.all(np.isnan(V[:, idx])) else np.full(len(t), np.nan))
        peaks = []
        for c in cols:
            peaks.append(float((t[w][int(np.nanargmax(c[w]))] - self.t_impact) * 1000.0) if not np.all(np.isnan(c[w])) else float("nan"))
        out.update(seq_ok=True, peaks_ms=peaks, names=[n for n, _ in self.SEQ_SEGMENTS])
        pk = np.array(peaks); okp = pk[~np.isnan(pk)]
        out["prox_to_distal"] = bool(len(okp) == len(pk) and np.all(np.diff(pk) >= 0))
        names = out["names"]; g = lambda n: pk[names.index(n)]
        out["wrist_minus_shoulder_s"] = float((g("wrist_R") - g("shoulder_R")) / 1000.0)
        out["elbow_minus_shoulder_s"] = float((g("elbow_R") - g("shoulder_R")) / 1000.0)
        out["torso_minus_hips_s"] = float((g("torso(chest_yaw)") - g("hips")) / 1000.0)
        return out

    def launch_elev_deg(self) -> float:
        """Elevation (deg) of the ball velocity right after contact (separation velocity); NaN if no contact."""
        v = self.v_sep if self.v_sep is not None else self._last_v
        if v is None:
            return float("nan")
        return float(np.degrees(np.arctan2(v[2], np.hypot(v[0], v[1]) + 1e-9)))

    def summary(self, info: Dict) -> Dict[str, float]:
        t = np.asarray(self.traj)
        return {"final_x": float(t[-1, 0]), "final_y": float(t[-1, 1]), "final_z": float(t[-1, 2]),
                "max_height": float(t[:, 2].max()), "max_abs_y": float(np.abs(t[:, 1]).max()),
                "carry": float(info.get("carry", 0.0)), "true_contact": bool(info.get("true_contact", False)),
                "peak_ball_speed": float(info.get("peak_ball_speed", float("nan"))),
                "impact_club_speed": float(info.get("impact_club_speed", float("nan"))),
                "sep_rpm": float(info.get("sep_rpm", float("nan"))),
                "start_x": float(t[0, 0]), "total_dist": float(t[-1, 0] - t[0, 0]),   # total = carry + roll: final ball x minus start x along the target line (+x)
                "carry_yd": float(info.get("carry", 0.0)) * M_TO_YD, "total_yd": float((t[-1, 0] - t[0, 0]) * M_TO_YD),
                "club_speed_pre_contact": getattr(self, "club_pre", float("nan")),   # club speed at the substep BEFORE the first contact substep
                "ball_speed_sep": float(np.linalg.norm(self.v_sep)) if getattr(self, "v_sep", None) is not None else float("nan"),
                "seq": self.seq_summary(),
                "launch_elev_deg": self.launch_elev_deg(),
                "launch_elev_env_peakspeed_deg": float(np.degrees(info.get("launch_elevation", float("nan")))),
                "peak_club_speed": float(getattr(self, "peak_club", float("nan"))),
                "nonphysical_substeps": int(getattr(self, "n_nonphysical", 0)),
                "raw_max_club_speed": float(getattr(self, "raw_max", 0.0)),
                "first_nonphysical_sim_time": getattr(self, "first_bad_t", None)} | self.landing_summary()

    def landing_summary(self) -> Dict[str, float]:
        """Opt-in (install(track_landing=True)); {} otherwise so default output is unchanged. descent_angle_deg = angle below horizontal of the ball
        velocity at first touchdown (z<LAND_Z m); landing_speed_mps = |v| there. NaN if the ball never landed. Env flight model, no roll."""
        if not getattr(self, "track_landing", False): return {}
        v = self.land_v
        if v is None: return {"descent_angle_deg": float("nan"), "landing_speed_mps": float("nan")}
        return {"descent_angle_deg": float(np.degrees(np.arctan2(-v[2], np.hypot(v[0], v[1]) + 1e-9))), "landing_speed_mps": float(np.linalg.norm(v))}


def seq_aggregate(shots):
    ss = [s["seq"] for s in shots if s.get("seq", {}).get("seq_ok")]
    if not ss: return {"n": 0}
    names = ss[0]["names"]; P = np.array([x["peaks_ms"] for x in ss], float)
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        med = np.nanmedian(P, axis=0)
        fin = lambda k: [x[k] for x in ss if x[k] == x[k]]
        return {"n": len(ss), "segments": names, "peak_rel_impact_ms_median": [float(v) for v in med], "peak_rel_impact_ms_iqr": [[float(np.nanpercentile(P[:, i], 25)), float(np.nanpercentile(P[:, i], 75))] for i in range(P.shape[1])],
                "frac_proximal_to_distal": float(np.mean([x["prox_to_distal"] for x in ss])),
                "wrist_minus_shoulder_s_median": float(np.median(fin("wrist_minus_shoulder_s"))) if fin("wrist_minus_shoulder_s") else float("nan"),
                "elbow_minus_shoulder_s_median": float(np.median(fin("elbow_minus_shoulder_s"))) if fin("elbow_minus_shoulder_s") else float("nan"),
                "torso_minus_hips_s_median": float(np.median(fin("torso_minus_hips_s"))) if fin("torso_minus_hips_s") else float("nan")}


def dispersion(shots: Sequence[Dict], thr: float = LATERAL_THRESHOLD_M) -> Dict[str, float]:
    x = np.array([s["final_x"] for s in shots]); y = np.array([s["final_y"] for s in shots])
    tc = np.array([s["true_contact"] for s in shots], bool)
    def rates(m):
        return (float((y[m] > thr).mean()), float((y[m] < -thr).mean())) if m.any() else (float("nan"),) * 2
    l, r = rates(np.ones(len(y), bool)); lc, rc = rates(tc)
    cs = np.array([s.get("impact_club_speed", np.nan) for s in shots]); bs = np.array([s["peak_ball_speed"] for s in shots])
    ok = tc & (cs > MIN_CLUB_SPEED)           # contact shots with a measurable club speed
    smash = bs[ok] / cs[ok]
    pk = np.array([s.get("peak_club_speed", np.nan) for s in shots])
    bad = np.array([s.get("nonphysical_substeps", 0) > 0 for s in shots])
    n_unstable = int(bad.sum())
    raw = np.array([s.get("raw_max_club_speed", 0.0) for s in shots])
    pk = np.where(bad, np.nan, pk)    # episodes with any non-physical substep are EXCLUDED from peak stats (and counted/reported), not clipped
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pkm, pkx = np.nanmean(pk), (np.nanmax(pk) if (~np.isnan(pk)).any() else float("nan"))
    le = np.array([s.get("launch_elev_deg", np.nan) for s in shots])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        lem, les = (float(np.nanmean(le)), float(np.nanstd(le))) if (~np.isnan(le)).any() else (float("nan"),) * 2
        leflat = float(np.mean(le[~np.isnan(le)] < FLAT_LAUNCH_DEG)) if (~np.isnan(le)).any() else float("nan")
    return {"launch_elev_mean_deg": lem, "launch_elev_std_deg": les, "launch_flat_frac": leflat,
            "launch_flat_flag": bool(lem == lem and (lem < FLAT_LAUNCH_DEG or leflat >= 0.5)),
            "peak_club_unstable_episodes": n_unstable, "peak_club_raw_max_unstable": float(raw.max()) if bad.any() else None, "peak_club_speed_mean": float(pkm), "peak_club_speed_max": float(pkx),
            "peak_club_mph_mean": float(pkm * MPS_TO_MPH), "peak_club_mph_max": float(pkx * MPS_TO_MPH),
            "peak_club_pct_target_mean": float(pkm / TARGET_MS * 100), "peak_club_pct_target_max": float(pkx / TARGET_MS * 100),
            "impact_club_speed_mean": float(np.nanmean(cs[tc])) if tc.any() else float("nan"),
            "impact_club_speed_max": float(np.nanmax(cs[tc])) if tc.any() else float("nan"),
            "smash_factor_mean": float(smash.mean()) if ok.any() else float("nan"),
            "smash_factor_median": float(np.median(smash)) if ok.any() else float("nan"),
            "backspin_rpm_mean": (float(np.nanmean([sh.get("sep_rpm", np.nan) for sh in np.asarray(shots, dtype=object)[tc]])) if tc.any() and np.isfinite([sh.get("sep_rpm", np.nan) for sh in np.asarray(shots, dtype=object)[tc]]).any() else float("nan")),
            "smash_factor_n": int(ok.sum()), "episodes": int(len(x)), "contact_rate": float(tc.mean()),
            "mean_distance": float(x.mean()), "std_distance": float(x.std()), "median_distance": float(np.median(x)),
            "max_distance": float(x.max()), "mean_y": float(y.mean()), "lateral_std": float(y.std()),
            "mean_abs_y": float(np.abs(y).mean()), "max_abs_y": float(np.abs(y).max()),
            "left_miss_rate": l, "right_miss_rate": r, "in_corridor_rate": 1 - l - r,
            "left_miss_rate_contact_only": lc, "right_miss_rate_contact_only": rc,
            "sequencing_proxy": seq_aggregate(shots),
            "mean_carry": float(np.mean([s["carry"] for s in shots])),
            "mean_carry_yd": float(np.mean([s["carry"] for s in shots]) * M_TO_YD),
            "mean_total_m": float(np.mean([s.get("total_dist", np.nan) for s in shots])), "median_total_m": float(np.median([s.get("total_dist", np.nan) for s in shots])),
            "mean_total_yd": float(np.mean([s.get("total_dist", np.nan) for s in shots]) * M_TO_YD), "max_total_yd": float(np.max([s.get("total_dist", np.nan) for s in shots]) * M_TO_YD),
            "mean_roll_m": float(np.mean([s["final_x"] - s["carry"] if s["carry"] > 0 else np.nan for s in shots])) if any(s["carry"] > 0 for s in shots) else float("nan"),   # roll = final x minus landing x (both absolute x)
            "landed_fraction": float(np.mean([s["carry"] > 0 for s in shots])),
            "mean_peak_ball_speed": float(np.nanmean([s["peak_ball_speed"] for s in shots])),
            "lateral_threshold_m": thr}
