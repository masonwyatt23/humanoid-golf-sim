"""
Polished showcase video from results/leaderboard.json:  results/videos/showcase_polished.mp4  (+ showcase_polished.json)

    python -m eval.render_polished [--pick best_qualifying] [--swings 12] [--seed 5000] [--K 6]

Slides: title card -> leaderboard (deterministic) -> leaderboard (stochastic) -> segment per model (side-on | down-the-line,
slow motion, live overlay of measured club mph / carry / lateral / launch) -> end card with caveats.

* Trained model: --pick best_qualifying. If NO trained model meets the leaderboard criterion, a clearly labeled FALLBACK PREVIEW of the
  best trained model is rendered (red banner 'DOES NOT YET QUALIFY' + the failing criteria computed from the data). Never a 'good drive'.
* Scripted segments ('SCRIPTED (not learned)'): the zero-residual scripted row with the highest det carry among those satisfying the criterion (all scripted rows still appear on the leaderboard slides); if none does, the
  trainer-config 0.422 scripted baseline is shown, labeled as not qualifying when it fails.
* Qualification is recomputed here from leaderboard.json with the leaderboard's own criterion (qualify_criterion): 100% contact in both
  modes, det mean carry >= carry_m_min, det lateral std <= lateral_std_m_max, det mean launch >= launch_elev_deg_min.
* Every number on slides/banners is read from results/leaderboard.json (all-episode stats, 50 eps) or measured live on the rendered swing.
* Swing selection: tracker pass over N deterministic seeds, lower median by carry among true-contact+landed swings; that seed is rendered and
  the overlay shows what was measured on the RENDERED swing (strikes of learned policies are not bit-reproducible once rendering/instrumentation
  is attached, so the rendered swing can differ from the selection pass; both numbers are in showcase_polished.json).
"""
import argparse, datetime, json, subprocess, sys, os, shutil
from pathlib import Path
import numpy as np
from eval import render_showcase as rs

ROOT, FPS, W, H = rs.ROOT, rs.FPS, 1280, 480


def ensure_gl():
    if os.environ.get("_RS_GL"): return
    r = subprocess.run([sys.executable, "-c", "import mujoco;from env.humanoid_golf_env import HumanoidGolfEnv as E;e=E();mujoco.Renderer(e.model,64,64)"],
                       cwd=ROOT, env={**os.environ, "MUJOCO_GL": "egl"}, capture_output=True)
    if r.returncode == 0:
        os.environ["MUJOCO_GL"] = "egl"; os.environ["_RS_GL"] = "egl"; return
    env = {**os.environ, "MUJOCO_GL": "glfw", "_RS_GL": "glfw"}
    os.execvpe("xvfb-run", ["xvfb-run", "-a", "-s", "-screen 0 1280x720x24", sys.executable, "-m", "eval.render_polished", *sys.argv[1:]], env)


def qualification(m, crit):
    d, s = m["modes"].get("deterministic", {}), m["modes"].get("stochastic", {})
    if not d or not s or "error" in d or "error" in s:
        return False, ["evaluation error"]
    fails = []
    if not (d["contact_rate"] >= 1.0 and s["contact_rate"] >= 1.0): fails.append(f"contact det/stoch {d['contact_rate']*100:.0f}%/{s['contact_rate']*100:.0f}% (need 100% both)")
    if d["mean_carry"] < crit["carry_m_min"]: fails.append(f"det carry {d['mean_carry']:.1f} m < {crit['carry_m_min']:.0f}")
    if d["lateral_std"] > crit["lateral_std_m_max"]: fails.append(f"det lateral std {d['lateral_std']:.2f} m > {crit['lateral_std_m_max']}")
    if not d["launch_elev_mean_deg"] >= crit["launch_elev_deg_min"]: fails.append(f"det launch {d['launch_elev_mean_deg']:.1f} deg < {crit['launch_elev_deg_min']:.0f}")
    return not fails, fails


SKY_TOP, SKY_HOR = np.array([70, 120, 200], np.float32), np.array([200, 225, 245], np.float32)


def style_scene(env):
    """Cleaner scene: brighter headlight, light fairway-green ground, haze/fog toward a sky-gradient horizon (sky painted over pure-black background pixels)."""
    import mujoco
    m = env.model
    m.vis.headlight.ambient[:] = [0.55, 0.55, 0.55]; m.vis.headlight.diffuse[:] = [0.85, 0.85, 0.85]; m.vis.headlight.specular[:] = [0.2, 0.2, 0.2]
    m.vis.rgba.fog[:] = [SKY_HOR[0] / 255, SKY_HOR[1] / 255, SKY_HOR[2] / 255, 1]; m.vis.rgba.haze[:] = m.vis.rgba.fog
    m.vis.map.fogstart, m.vis.map.fogend = 4.0, 60.0
    m.geom_rgba[m.geom("ground").id] = [0.45, 0.78, 0.45, 1]
    gid = m.geom("ground").id
    if m.geom_type[gid] == mujoco.mjtGeom.mjGEOM_PLANE: m.geom_size[gid, :2] = 0.0   # 0 = infinite plane: no visible ground edge in tracking / chase cams (was a 20 m square)


def paint_sky(img):
    h = img.shape[0]
    mask = (img.sum(axis=2) == 0)
    if not mask.any(): return img
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]   # top -> bottom
    sky = (SKY_TOP[None, None, :] * (1 - t) + SKY_HOR[None, None, :] * t).astype(np.uint8)
    sky = np.broadcast_to(sky, img.shape)
    out = img.copy(); out[mask] = sky[mask]
    return out


def actuator_tags(kw):
    """Honest hardware flags read from the env config (never hard-coded per model)."""
    tags = []
    fs, ts = kw.get("force_scale", 1.0), kw.get("torque_scale", None)
    if fs and fs > 1.0: tags.append(f"force_scale {fs:g} (hypothetical-strength actuators)")
    if ts and ts > 1.0: tags.append(f"torque_scale {ts:g} (boosted)")
    if (kw.get("impact_model") or {}).get("spin_k"): tags.append("no spin model: backspin hand-set by impact model (spin_k), not from contact")
    g = kw.get("impact_gain") or (kw.get("impact_model") or {}).get("gain", 1.0)
    if g and g > 1.25: tags.append(f"impact gain {g:g}: ball speed/smash INFLATED (smash ~1.6), distances inflated")
    elif g and g > 1.05: tags.append(f"impact gain {g:g}: hypothetical power tier, smash set by this gain (gate-measured, see banner), distances model-based")
    td = (kw.get("script") or {}).get("t_down")
    if td is not None and td < 0.08: tags.append(f"t_down {td:g} s (65-80 ms downswing: not a human tempo)")
    return tags


class PRec:
    """Polished recorder: tracking side cam + DTL->ball-chase cam, impact-centred slow-motion ramp, live overlay (mph, yards, launch, lateral)."""
    def __init__(self, env, writer, banner, banner_color, ft, kind, tags):
        import mujoco, cv2
        self.mj, self.cv2, self.env, self.w, self.ft, self.kind, self.tags = mujoco, cv2, env, writer, ft, kind, tags
        self.banner, self.banner_color = banner, banner_color
        self.r = mujoco.Renderer(env.model, 480, 640)
        self.cams = [self._cam(90), self._cam(0)]
        self.trail, self.acc, self.last_k = [], 0, 12
        self.peak_club, self.t_contact, self.impact_frame, self.start_x = 0.0, None, None, None
        self.frames0 = writer.frames

    def _cam(self, az):
        c = self.mj.MjvCamera(); c.type = self.mj.mjtCamera.mjCAMERA_FREE; c.azimuth = az; c.elevation = -8; c.distance = 3.0; c.lookat[:] = (0.9, 0, 0.5); return c

    def Kf(self):
        e = self.env; t = float(e.data.time)
        if e.true_contact:
            if self.t_contact is None: self.t_contact = t
            ts = t - self.t_contact
            return 2 if ts < 0.10 else 6 if ts < 0.40 else 24
        head = e.data.geom_xpos[e._club_geom]; ball = e.data.xpos[e._ball_id]
        d = float(np.linalg.norm(head - ball)); v = e._club_speed()
        return 3 if (d < 0.7 and v > 15) else 14

    def install(self):
        self.orig = self.mj.mj_step
        def wrapped(m, d, *a, **k):
            self.orig(m, d, *a, **k)
            v = self.env._club_speed()
            if v == v and v <= 100.0: self.peak_club = max(self.peak_club, v)
            self.acc += 1
            kk = self.Kf(); self.last_k = kk
            if self.acc >= kk:
                self.acc = 0; self.frame(v)
        self.mj.mj_step = wrapped

    def uninstall(self): self.mj.mj_step = self.orig

    def frame(self, v=None, hold=1):
        e, cv2 = self.env, self.cv2
        bp = e.data.xpos[e._ball_id].copy(); hp = e.data.geom_xpos[e._club_geom].copy()
        if self.start_x is None: self.start_x = float(bp[0])
        if e.true_contact and bp[2] > 0.03 and (not self.trail or abs(bp - self.trail[-1]).max() > 0.02): self.trail.append(bp)
        airborne = e.true_contact and bp[0] - self.start_x > 1.5
        if e.true_contact and self.impact_frame is None: self.impact_frame = self.w.frames
        panels = []
        for i, cam in enumerate(self.cams):
            if i == 0:   # TRACKING side-on: follows the club head, then the ball
                tgt = bp if airborne else hp
                cam.lookat[:] = (0.9 + 0.8 * (tgt[0] - 0.9), 0.0, 0.8 + 0.3 * (tgt[2] - 0.8)); cam.distance = 3.0 if not airborne else min(3.0 + 0.35 * (bp[0] - self.start_x), 40)
                name = "SIDE-ON (tracking)"
            else:        # DOWN-THE-LINE, then BALL CHASE from behind once airborne
                if airborne:
                    cam.lookat[:] = bp; cam.distance = min(6.0 + 0.30 * (bp[0] - self.start_x), 45); cam.elevation = -4; name = "BALL CHASE"
                else:
                    cam.lookat[:] = (0.9, 0.0, 0.8); cam.distance = 3.6; cam.elevation = -6; name = "DOWN-THE-LINE"
            self.r.update_scene(e.data, camera=cam); sc = self.r.scene
            chase = (i == 1 and airborne)
            rad = max(0.02, 0.006 * cam.distance)   # keep markers visible but small as the camera pulls back
            pts = [bp] if chase else self.trail
            for p in pts:
                if sc.ngeom >= sc.maxgeom: break
                g = sc.geoms[sc.ngeom]
                self.mj.mjv_initGeom(g, self.mj.mjtGeom.mjGEOM_SPHERE, [(0.02 + 0.01 * cam.distance) if chase else rad, 0, 0], p, [1, 0, 0, 0, 1, 0, 0, 0, 1], [1, 0.85, 0, 1]); sc.ngeom += 1
            img = paint_sky(self.r.render().copy())
            cv2.putText(img, name, (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            panels.append(img)
        img = np.concatenate(panels, axis=1)
        cs = e._club_speed() if v is None else v
        bs = float(np.linalg.norm(e._ball_lin_vel())) if e.true_contact else None
        le = self.ft.launch_elev_deg() if e.true_contact else float("nan")
        carry = float(e.carry) if e._landed else 0.0
        x = float(bp[0]) - self.start_x
        slow = (1.0 / FPS) / (self.last_k * e.model.opt.timestep)
        f = lambda val, fmt: "n/a" if val is None or val != val else format(val, fmt)
        lines = [f"Club speed now: {cs * 2.23694:.0f} mph   peak so far: {self.peak_club * 2.23694:.1f} mph ({self.peak_club / 53.64 * 100:.0f}% of 120)   Ball speed: {f(None if bs is None else bs * 2.23694, '.0f')} mph ({f(bs, '.1f')} m/s)",
                 f"Launch: {f(le, '.1f')} deg   Carry: {'n/a' if carry <= 0 else format(carry, '.1f') + ' m / ' + format(carry * 1.09361, '.0f') + ' yd'}   Ball dist. so far: {x:.1f} m / {x * 1.09361:.0f} yd   Lateral y (+left): {float(bp[1]):+.2f} m",
                 f"Slow-mo {slow:.1f}x (ramps around impact)   {self.kind}   left-handed   measured in simulation, this swing only"]
        if self.tags: lines += [("ACTUATORS: " if i == 0 else "   ") + t for i, t in enumerate(self.tags)]   # one tag per line (no clipping)
        ov = img.copy(); cv2.rectangle(ov, (0, 480 - 22 * len(lines) - 10), (1280, 480), (0, 0, 0), -1); img = cv2.addWeighted(ov, 0.6, img, 0.4, 0)
        for i, t in enumerate(lines): cv2.putText(img, t, (10, 480 - 22 * len(lines) + 22 * i + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 120) if i == 3 else (255, 255, 255), 1, cv2.LINE_AA)
        if self.banner:
            ov = img.copy(); cv2.rectangle(ov, (0, 30), (1280, 30 + 24 * len(self.banner) + 6), (0, 0, 0), -1); img = cv2.addWeighted(ov, 0.65, img, 0.35, 0)
            for i, t in enumerate(self.banner): cv2.putText(img, t, (10, 50 + 24 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.banner_color if i == 0 else (255, 255, 255), 2 if i == 0 else 1, cv2.LINE_AA)
        for _ in range(hold): self.w.write(img)


def noise_caveat(m):
    """Quick noise-fragility line from leaderboard.json noise_robust (N=10, sigma on every obs+action); '' if not measured."""
    nr = m.get("noise_robust") or {}; cl = m["modes"]["deterministic"]["mean_carry"]
    if not nr: return ""
    bits = [f"sigma {k}: carry {v['mean_carry']:.0f} m ({v['mean_carry']/cl*100:.0f}% of clean {cl:.0f} m), contact {v['contact_rate']*100:.0f}%" for k, v in sorted(nr.items()) if v and "mean_carry" in v]
    return "Noise robustness (quick, 10 eps): " + "; ".join(bits)


def pose_slide(sim_deg, sim_impact, mason_path, kind, label):
    """Joint-angle traces: Mason reference (2D-proxy MediaPipe angles) vs sim, time normalised takeaway->impact. PROXY: conventions/signs not guaranteed identical."""
    import cv2
    d = np.load(mason_path, allow_pickle=True); vm = d["valid_mask"].astype(bool); t = d["time"]; j = d["joints"].astype(float)
    t0, ti = float(d["t_takeaway"] - d["t_start_in_video"]), float(d["t_impact"] - d["t_start_in_video"])
    sel = vm & (t >= t0) & (t <= ti)
    mt, mj = (t[sel] - t0) / max(ti - t0, 1e-6), j[sel]
    st = np.linspace(0, 1, sim_impact + 1); sj = sim_deg[: sim_impact + 1]
    img = np.zeros((H, W, 3), np.uint8); img[:] = (12, 16, 24)
    cv2.putText(img, f"Joint-angle traces: Mason reference vs sim ({kind})  -  PROXY", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 220, 255), 2, cv2.LINE_AA)
    cols = [(0, "right_shoulder_pitch"), (2, "right_elbow"), (3, "right_wrist"), (4, "left_shoulder_pitch")]
    for k, (ci, nm) in enumerate(cols):
        x0, y0, w_, h_ = 20 + k * 310, 60, 290, 280
        cv2.rectangle(img, (x0, y0), (x0 + w_, y0 + h_), (80, 80, 80), 1)
        allv = np.concatenate([mj[:, ci], sj[:, ci]]); lo, hi = float(allv.min()), float(allv.max()); hi = hi if hi - lo > 1 else lo + 1
        pts = lambda xs, ys: np.array([[x0 + int(x * w_), y0 + h_ - int((y - lo) / (hi - lo) * (h_ - 10)) - 5] for x, y in zip(xs, ys)], np.int32)
        cv2.polylines(img, [pts(mt, mj[:, ci])], False, (60, 200, 255), 2, cv2.LINE_AA); cv2.polylines(img, [pts(st, sj[:, ci])], False, (120, 255, 120), 2, cv2.LINE_AA)
        cv2.putText(img, nm, (x0 + 6, y0 + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img, f"{lo:.0f}..{hi:.0f} deg", (x0 + 6, y0 + h_ - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1, cv2.LINE_AA)
    cv2.putText(img, "blue = Mason (" + Path(mason_path).stem + ", native left, 2D-proxy MediaPipe angles, ~30 fps, valid frames only)", (20, 372), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (60, 200, 255), 1, cv2.LINE_AA)
    cv2.putText(img, f"green = sim {label}: joint angles from this swing, takeaway -> impact", (20, 394), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 255, 120), 1, cv2.LINE_AA)
    cv2.putText(img, "x = time normalised takeaway->impact (Mason backswing 0.58 s vs sim script tempo differ). Mason angles are not retargeted to this humanoid; sign/zero conventions may differ. Indicative only.", (20, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 120), 1, cv2.LINE_AA)
    return img


def card(lines, colors=None, size=0.8):
    import cv2
    img = np.zeros((H, W, 3), np.uint8); img[:] = (12, 16, 24)
    y = 60
    for i, t in enumerate(lines):
        sz, th = (size * 1.6, 3) if i == 0 else (size, 1)
        col = (colors or {}).get(i, (255, 255, 255) if i else (0, 220, 255))
        cv2.putText(img, t, (40, y), cv2.FONT_HERSHEY_SIMPLEX, sz, col, th, cv2.LINE_AA)
        y += int(46 * sz / 0.8) if i else 70
    return img


def fit_text(t, maxw, scale=0.45):
    """Shrink font (down to 0.32) then ellipsise so the label never runs into the next column."""
    import cv2
    for sc in (0.45, 0.40, 0.36, 0.32):
        if cv2.getTextSize(t, cv2.FONT_HERSHEY_SIMPLEX, sc, 1)[0][0] <= maxw: return (t, sc)
    while len(t) > 4 and cv2.getTextSize(t + "...", cv2.FONT_HERSHEY_SIMPLEX, 0.32, 1)[0][0] > maxw: t = t[:-1]
    return (t + "...", 0.32)


def table_slide(title, rows, mode, crit, note):
    import cv2
    img = np.zeros((H, W, 3), np.uint8); img[:] = (12, 16, 24)
    cv2.putText(img, title, (20, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 220, 255), 2, cv2.LINE_AA)
    cols = [("model", 20), ("kind", 440), ("contact", 500), ("carry m", 590), ("landed", 680), ("lat std m", 760), ("miss L/R", 860), ("launch deg", 960), ("peak mph", 1070), ("qual.", 1150), ("smash (! = flagged)", 1200)]
    for c, x in cols: cv2.putText(img, c, (x, 66), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1, cv2.LINE_AA)
    y = 94
    for name, kind, m, q in rows:
        d = m["modes"][mode]
        disp = (name[name.index("[") + 1:].rstrip("]") if "[" in name else name); ek_ = m.get("env_kwargs") or {}
        mt_ = "[POWER hypo] " if "power" in str(ek_.get("model_xml", "")) else "[fs%g HYPO] " % ek_.get("force_scale") if (ek_.get("force_scale") or 1) > 1 else "[stock] "
        sm_ = m.get("smash_ratio_det"); vals = [fit_text(mt_ + disp, 410), kind, f"{d['contact_rate']*100:.0f}%", f"{d['mean_carry']:.1f}", f"{d['landed_fraction']*100:.0f}%", f"{d['lateral_std']:.2f}",
                f"{d['left_miss_rate']*100:.0f}/{d['right_miss_rate']*100:.0f}%", f"{d['launch_elev_mean_deg']:.1f}" + (" FLAT" if d.get("launch_flat_flag") else ""), f"{d['peak_club_mph_mean']:.1f}", "YES" if q else "no", ("smash %.2f" % sm_ + ("!" if m.get("smash_flag") else "")) if sm_ else "smash n/m"]
        col = (120, 255, 120) if q else (255, 255, 255)
        for (c, x), v in zip(cols, vals):
            fs = 0.45
            if isinstance(v, tuple): v, fs = v
            cv2.putText(img, v, (x, y), cv2.FONT_HERSHEY_SIMPLEX, fs, col if c in ("model", "qual.") else (230, 230, 230), 1, cv2.LINE_AA)
        y += 29
    for i, t in enumerate(note): cv2.putText(img, t, (20, H - 54 + 20 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 120), 1, cv2.LINE_AA)
    return img


def wrap(t, n=105):
    out, cur = [], ""
    for w in t.split():
        if len(cur) + len(w) + 1 > n: out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    return out + [cur]



def profiles_slides(path):
    """Optional --profiles segment: summarise docs/MASON_VS_PROFILES.md as generic 'style profile' slides (no individual names, no coaching claims). Returns list of (image, seconds)."""
    import re
    txt = Path(path).read_text(); src = f"source: {Path(path).name} (auto-generated by data.compare_mason_to_profile; internal reference)"
    inputs = re.findall(r"^\| (tempo_ratio|backswing_s|downswing_s|club_head_speed_mph) \| ([\d.]+) \| \+-([\d.]+) \| ([\d.]+) \|", txt, re.M)
    prio = re.findall(r"^\d+\. `(\w+)` - mean priority ([\d.]+) over (\d+) profiles", txt, re.M)
    n_prof = len(re.findall(r"^## vs ", txt, re.M))
    unit = {"tempo_ratio": "", "backswing_s": " s", "downswing_s": " s", "club_head_speed_mph": " mph"}
    A = ["Mason vs STYLE PROFILES (summary)", f"{n_prof} style profiles built from published summary stats (some unverified) - NOT simulations of real persons; internal reference", "",
         "Mason inputs (from ~30 fps video; trust 0-1):"]
    cols = {1: (255, 200, 90), 3: (200, 200, 200)}
    for k, v, u, tr in inputs:
        note = " SELF-REPORTED, not measured" if k == "club_head_speed_mph" else (" loose band only" if k == "tempo_ratio" else " suspect: 4-6 frame downswing / feed clips")
        A.append(f"  {k}: {float(v):.3g}{unit[k]} (+-{float(u):.2g}, trust {tr}){note}")
    A += ["", "Honest read: these are gaps to a published-stat style profile. Joint-angle proxies are not compared. Nothing here is a sim result", src]
    B = ["Where Mason differs most from the style profiles", "(priority = gap size vs measurement noise AND trust; mean over the profiles that include the feature)", ""]
    for k, pr, n in prio: B.append(f"  {k}: mean priority {pr} over {n} profile(s)")
    B += ["", "Read first:", "  - tempo/duration from 30 fps video: loose (+-~27%); absolute seconds from feed clips may be sped up; re-measure at 240 fps",
          "  - club speed is self-reported (120+ mph), unverified by launch monitor; band position is NOT a population percentile",
          "  - not a coaching prescription; consult a coach/fitter. Internal reference only; legal review before external use", src]
    return [(card(A, cols, 0.55), 9), (card(B, {1: (255, 200, 90)}, 0.55), 9)]


def extras(video, meta, lb):
    """20-30 s social cut (title, impact windows of each segment, leaderboard-det slide, end card) + README hero GIF (<5 MB, docs/hero_swing.gif)."""
    vd = video.parent; fps = FPS; segs = meta["segments"]
    parts = [(0, 3.0), (int(3.0 * fps) + 0, 0)]   # placeholder replaced below
    parts = [(0.0, 3.0)]
    for s_ in segs:
        imp = s_["frames"]["impact"]
        if imp: parts.append((max(0.0, imp / fps - 2.0), 7.0))
    parts.append((meta["duration_s"] - meta.get("end_card_s", 8.0), 3.0))   # end card start (show first 3 s)
    # leaderboard det slide sits right after the 4 s title card (held 7 s)
    parts.insert(1, (4.0, 3.5))
    tot = sum(d for _, d in parts)
    fl = "".join(f"[0:v]trim=start={st:.3f}:duration={du:.3f},setpts=PTS-STARTPTS[v{i}];" for i, (st, du) in enumerate(parts))
    fl += "".join(f"[v{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=0[o]"
    out = vd / "showcase_social.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-filter_complex", fl, "-map", "[o]", "-an", "-vcodec", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", str(out)], check=True)
    meta["social_cut"] = dict(path=str(out.relative_to(ROOT)), duration_s=tot, parts_s=parts)
    # hero gif: first segment impact window
    imp = next((s_["frames"]["impact"] for s_ in segs if s_["frames"]["impact"]), None)
    if imp:
        gif = ROOT / "docs" / "hero_swing.gif"; gif.parent.mkdir(exist_ok=True)
        st = max(0.0, imp / fps - 1.0)
        for wpx, gfps in ((800, 12), (720, 10), (640, 10), (560, 8)):
            pal = vd / "_pal.png"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{st:.3f}", "-t", "6", "-i", str(video), "-vf", f"fps={gfps},scale={wpx}:-1:flags=lanczos,palettegen=max_colors=96", str(pal)], check=True)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{st:.3f}", "-t", "6", "-i", str(video), "-i", str(pal), "-lavfi", f"fps={gfps},scale={wpx}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4", str(gif)], check=True)
            if gif.stat().st_size < 4.8e6: break
        meta["hero_gif"] = dict(path=str(gif.relative_to(ROOT)), bytes=gif.stat().st_size, width=wpx, fps=gfps, from_segment=segs[0]["kind"] + " " + segs[0]["model"])
    (video.with_suffix(".json")).write_text(json.dumps(meta, indent=1, default=float))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pick", default="best_qualifying", choices=["best_qualifying", "best", "best_left"])
    ap.add_argument("--model", default=None, help="render this checkpoint name (as in the leaderboard, e.g. imit3_w050_s51) instead of the --pick choice")
    ap.add_argument("--swings", type=int, default=12); ap.add_argument("--seed", type=int, default=5000); ap.add_argument("--K", type=int, default=6)
    ap.add_argument("--env-override", default=None, help="JSON dict merged into the chosen model's env kwargs (e.g. '{\"impact_gain\": 1.2}'); use with --override-stats")
    ap.add_argument("--override-stats", default=None, help="gate JSON (eval_gate output run with the same override): its policy_det/policy_stoch replace the leaderboard stats shown on screen; noise caveat is dropped (it was measured without the override)")
    ap.add_argument("--out", default="results/videos/showcase_polished.mp4"); ap.add_argument("--no-pose", dest="pose", action="store_false"); ap.add_argument("--no-extras", action="store_true", help="skip social cut + hero gif")
    ap.add_argument("--profiles", nargs="?", const="docs/MASON_VS_PROFILES.md", default=None, help="optional style-profile summary slides from this doc (default docs/MASON_VS_PROFILES.md)")
    a = ap.parse_args(); ensure_gl()
    from stable_baselines3 import PPO
    from eval.env_factory import make_env
    from eval.flight_tracker import FlightTracker
    import cv2
    lb = json.loads((ROOT / "results/leaderboard.json").read_text()); crit = lb["qualify_criterion"]; models = lb["models"]
    by = {m["names"][0]: m for m in models}; label = lambda m: "/".join(m["names"])
    q = {m["names"][0]: qualification(m, crit) for m in models}
    trained = [m for m in models if not m.get("scripted")]; scripted = [m for m in models if m.get("scripted")]
    # --- trained model pick
    pk = {"best_qualifying": lb.get("best_qualifying"), "best": lb.get("best_model"), "best_left": lb.get("best_left")}[a.pick]
    fallback = pk is None
    if a.model: pk, fallback = next(m["names"] for m in models if a.model in m["names"]), False
    if fallback: pk = lb["best_model"]
    lm = by[pk[0]]; ok_l, fail_l = q[pk[0]]
    if lm.get("smash_flag") or lm.get("hypo_demoted"):   # smash gate / hypothetical demotion (leaderboard.json): not eligible as a qualifying showcase
        ok_l = False; fail_l = list(fail_l) + ([f"smash {lm['smash_ratio_det']:.2f} outside 1.30-1.49 ({lm['smash_flag']})"] if lm.get("smash_flag") else []) + ([lm["hypo_demoted"]] if lm.get("hypo_demoted") else [])
    if a.env_override:
        lm = dict(lm); lm["env_kwargs"] = dict(lm["env_kwargs"], **json.loads(a.env_override)); lm["noise_robust"] = None
        if a.override_stats:
            gj = json.loads((ROOT / a.override_stats).read_text()); lm["modes"] = dict(lm["modes"], deterministic=gj["policy_det"], stochastic=gj["policy_stoch"])
            ok_l, fail_l = qualification(lm, crit)
        by[pk[0]] = lm
    # --- scripted segments: those that qualify; else the 0.422 trainer-cfg baseline (labeled)
    sq = [m for m in scripted if q[m["names"][0]][0]]
    seg_s = [max(sq, key=lambda m: m["modes"]["deterministic"]["mean_carry"])] if sq else [m for m in scripted if "ball_x 0.422" in m["names"][0]][:1]
    when = datetime.date.today().isoformat()
    w = rs.Writer(ROOT / a.out); hold = lambda img, s: [w.write(img) for _ in range(int(s * FPS))]
    meta = dict(date=when, pick=a.pick, fallback_preview=fallback, learned=label(lm), learned_qualifies=ok_l, learned_failed_criteria=fail_l,
                scripted_segments=[label(m) for m in seg_s], scripted_qualify={label(m): q[m["names"][0]] for m in scripted}, criterion=crit,
                leaderboard_env_fingerprint=lb.get("env_fingerprint"), segments=[])
    # title card
    _ek = lm.get("env_kwargs") or {}; _sw = _ek.get("script_weight"); _pw = "power" in str(_ek.get("model_xml", "")); _boost = (_ek.get("force_scale") or 1) > 1 or _pw
    _kind = "SCRIPT-DISTILLED POLICY" if (_sw == 0.0 and lm["names"][0].startswith("imit")) else "SCRIPT-DISTILLED BLEND" if (_sw not in (None, 1.0) and lm["names"][0].startswith("imit")) else "residual-PPO policy"
    _g = _ek.get("impact_gain") or (_ek.get("impact_model") or {}).get("gain")
    if _pw: _tier = [f"HYPOTHETICAL POWER TIER (force_scale 2 + power XML{', impact gain %g' % _g if _g else ''}); no spin model", "(not a real robot or human; backspin hand-set by the impact model)"]
    elif _boost: _tier = ["BOOSTED ACTUATORS: force_scale 2 = hypothetical-strength actuators", "(not a real robot or human)"]
    else: _tier = ["STOCK MOTORS (force_scale 1) for the policy segment; the scripted segment and some leaderboard rows use boosted", "actuators (force_scale 2 = hypothetical-strength, not a real robot or human); each is tagged on screen."]
    t = [f"Humanoid Golf - {_kind} vs scripted swing", "Left-handed setup (v3 humanoid, MuJoCo) - SIMULATION", *([f"{_kind}, {'stock motors (force_scale 1)' if not _boost else 'hypothetical tier'}: " + lm["names"][0]] ), *_tier, f"Rendered {when}   |   data: results/leaderboard.json ({lb['episodes']} episodes/mode, seeds {lb['seed_base']}+)"]
    cols = {}
    if fallback:
        t += ["FALLBACK PREVIEW: no trained model meets the showcase criterion", "Learned segment = best trained model, shown for transparency - NOT a good drive"]; cols = {6: (255, 70, 70), 7: (255, 70, 70)}
        cols = dict(cols); cols[2] = (120, 255, 120); cols[3] = (255, 170, 80); cols[4] = (255, 170, 80)
    hold(card(t, cols, 0.6), 4)
    # leaderboard slides
    rank = [r.split("/")[0] for r in (lb.get("ranking_unflagged") or lb["ranking"])][:4]   # smash-flagged rows (outside 1.30-1.49) are not eligible as top rows
    kd = lambda m: "LEARNED" if (m.get("env_kwargs") or {}).get("script_weight") in (None, 1.0) else "DISTILLED" if (m.get("env_kwargs") or {}).get("script_weight") == 0.0 else f"BLEND {round((1 - m['env_kwargs']['script_weight']) * 100)}/{round(m['env_kwargs']['script_weight'] * 100)}"
    rows = [(label(by[n]), kd(by[n]), by[n], q[n][0]) for n in rank if n in by]
    rows += [(label(m), "SCRIPTED", m, q[m["names"][0]][0]) for m in scripted]
    if lm["names"][0] not in rank: rows.insert(0, (label(lm), kd(lm), lm, ok_l))
    crit_txt = f"Criterion: contact 100% both modes, det carry >= {crit['carry_m_min']:.0f} m, det lateral std <= {crit['lateral_std_m_max']} m, launch >= {crit['launch_elev_deg_min']:.0f} deg. Ranking = contact then carry (not distance)."
    n1 = [crit_txt, "Top trained models by leaderboard ranking + all zero-residual SCRIPTED rows (not learned). All-episode means; carry/launch from flight tracker."]
    hold(table_slide(f"Leaderboard - DETERMINISTIC policy ({lb['episodes']} eps)", rows, "deterministic", crit, n1), 7)
    hold(table_slide(f"Leaderboard - STOCHASTIC policy ({lb['episodes']} eps)", rows, "stochastic", crit, n1 + ["Scripted rows are zero-residual (no sampling), so det = stoch."]), 7)
    # segments
    segs = [("LEARNED", lm, ok_l, fail_l)] + [("SCRIPTED (not learned)", m, *q[m["names"][0]]) for m in seg_s]
    for kind, m, okq, fails in segs:
        name = m["names"][0]; d = m["modes"]["deterministic"]; sc = m.get("scripted", False)
        swt = (m.get("env_kwargs") or {}).get("script_weight")
        blend = ("script-free imitation of the scripted v3 swing" if swt == 0.0 else f"{round((1 - swt) * 100)}% script-distilled policy / {round(swt * 100)}% scripted") if (kind == "LEARNED" and swt is not None and swt < 1.0) else ""   # from the run's env kwargs (verified in results JSON), never guessed
        dk = "SCRIPT-DISTILLED POLICY" if (kind == "LEARNED" and swt == 0.0) else "SCRIPT-DISTILLED BLEND" if (kind == "LEARNED" and swt is not None and 0.0 < swt < 1.0 and name.startswith("imit")) else kind   # display name: a script-free imitation is not a swing learned independently
        _ek = m.get("env_kwargs") or {}; _fs = _ek.get("force_scale") or 1.0; _g = _ek.get("impact_gain") or (_ek.get("impact_model") or {}).get("gain", 1.0) or 1.0
        mot = (", power tier hypothetical (impact gain %g)" % _g if _g > 1.05 else f", force_scale {_fs:g} hypothetical-strength" if _fs > 1.0 else ", stock motors (force_scale 1)") if dk != kind or kind == "LEARNED" else ""
        title = (f"{dk} ({label(m)}){mot}" if kind == "LEARNED" else f"{kind}") + (f" - {blend}" if blend and dk == kind else "")   # distilled rows: the blend is already named in the overlay line, keeps the banner inside the frame
        kind_txt = dk + (f" [{blend}]" if blend else "")
        hold(card([title, f"model: {label(m)}", f"Deterministic, {lb['episodes']} eps: carry {d['mean_carry']:.1f} m mean | lateral std {d['lateral_std']:.2f} m | miss L/R {d['left_miss_rate']*100:.0f}%/{d['right_miss_rate']*100:.0f}%",
                   f"launch {d['launch_elev_mean_deg']:.1f} deg | peak club {d['peak_club_mph_mean']:.1f} mph | landed {d['landed_fraction']*100:.0f}%" + ("   (FLAT launch)" if d.get("launch_flat_flag") else ""),
                   ("QUALIFIES under the criterion" if okq else "DOES NOT YET QUALIFY: " + "; ".join(fails))] + [x for x in wrap("Swing shown: ONE deterministic swing, lower median by carry of %d (seeds %d..); live overlay = that swing's own measurement." % (a.swings, a.seed), 100)],
                  {4: (120, 255, 120) if okq else (255, 70, 70)}, 0.6), 4.5)
        env = make_env(m["env_kwargs"]); pol = rs.ZeroPolicy(env) if sc else PPO.load(str(ROOT / "models" / m["names"][0]))
        res = []
        for i in range(a.swings):
            ft = FlightTracker(env).install()
            try:
                obs, _ = env.reset(seed=a.seed + i); ft.reset(); done = False; info = {}
                while not done:
                    obs, _, te, tr, info = env.step(pol.predict(obs)[0]); ft.step(); done = te or tr
            finally:
                ft.close()
            res.append((a.seed + i, ft.summary(info)))
        good = sorted([r for r in res if r[1]["true_contact"] and r[1]["carry"] > 0], key=lambda r: r[1]["carry"])
        seed, sh = good[(len(good) - 1) // 2]
        ban = [f"{title}" + ("" if okq else "  -  DOES NOT YET QUALIFY") , f"All-episode (det): carry {d['mean_carry']:.1f} m | lat std {d['lateral_std']:.2f} m | L/R miss {d['left_miss_rate']*100:.0f}/{d['right_miss_rate']*100:.0f}% | launch {d['launch_elev_mean_deg']:.1f} deg | {d['peak_club_mph_mean']:.1f} mph",
               f"This swing: seed {seed}, median-by-carry of {a.swings} (overlay below = this swing only)"]
        if kind == "LEARNED" and not a.env_override and m.get("smash_flag"):
            _g = []
            for _sd in (4000, 8000, 9000):
                _f = next((c_ for c_ in (ROOT / "results" / f"gate_{m['names'][0]}_seed{_sd}.json", ROOT / "results/imit_private" / f"gate_{m['names'][0]}{'' if _sd == 4000 else '_seed%d' % _sd}.json") if c_.exists()), ROOT / "results" / "_none.json")
                if _f.exists(): _j = json.loads(_f.read_text()); _g.append((_sd, _j["gate_pass"], _j["policy_det"]["lateral_std"]))
            ban.insert(2, "Smash %.2f (%s): ball barely faster than club (short of real distance)" % (m["smash_ratio_det"], m["smash_flag"]) + ((" | 3-seed gate: %s, lat std %s m" % ("PASS %d/3" % sum(1 for x in _g if x[1]), "/".join("%.2f" % x[2] for x in _g))) if len(_g) == 3 else " | no 3-seed gate JSON in results/"))
        if kind == "LEARNED" and a.env_override and a.override_stats:
            _p = json.loads((ROOT / a.override_stats).read_text())["policy_det"]
            ban.insert(2, "Launch monitor (gate mean, det): club %.1f mph | ball %.0f mph | smash %.2f | launch %.1f deg | carry %.0f yd (%.0f m) | backspin hand-set, no spin model" % (_p["peak_club_mph_mean"], _p["mean_peak_ball_speed"] * 2.23694, _p["mean_peak_ball_speed"] / _p["impact_club_speed_mean"], _p["launch_elev_mean_deg"], _p["mean_carry"] * 1.09361, _p["mean_carry"]))
        if kind == "LEARNED" and a.env_override and a.override_stats: ban.insert(1 + 1, "Stats: eval_gate %s eps, seed %s, with override %s (not the 50-ep leaderboard row)" % (json.loads((ROOT / a.override_stats).read_text()).get("episodes"), json.loads((ROOT / a.override_stats).read_text()).get("seed"), a.env_override))
        if not okq: ban.insert(2, "Fails: " + "; ".join(fails))
        nc = noise_caveat(m) if kind == "LEARNED" else ""
        if nc:
            nr_ = {k: v for k, v in (m.get("noise_robust") or {}).items() if v and "mean_carry" in v}
            frag = any(v["mean_carry"] < 0.8 * d["mean_carry"] for v in nr_.values())
            ban.append("Noise (quick, 10 eps) vs clean %.0f m: " % d["mean_carry"] + ", ".join("sigma %s -> %.0f m (%.0f%%)" % (k, v["mean_carry"], v["mean_carry"] / d["mean_carry"] * 100) for k, v in sorted(nr_.items())) + ("  NOISE-FRAGILE" if frag else ""))
        style_scene(env)
        from eval.env_factory import joint_qpos_idx
        qi = joint_qpos_idx(env); tags = actuator_tags(m["env_kwargs"])
        ft = FlightTracker(env).install(); jt = []
        try:
            col = (120, 255, 120) if okq else (255, 70, 70)
            if kind != "LEARNED": col = (0, 220, 255) if okq else (255, 170, 60)
            rec = PRec(env, w, ban, col, ft, kind_txt, tags)
            rec.install()
            try:
                obs, _ = env.reset(seed=seed); ft.reset(); done = False; info = {}; jt = [np.degrees(env.data.qpos[qi])]; imp_step = None
                while not done:
                    obs, _, te, tr, info = env.step(pol.predict(obs)[0]); ft.step(); jt.append(np.degrees(env.data.qpos[qi])); done = te or tr
                    if imp_step is None and env.true_contact: imp_step = len(jt) - 1
            finally:
                rec.uninstall()
            rec.frame(hold=int(3 * FPS)); rec.r.close()
        finally:
            ft.close()
        sw = ft.summary(info)
        seg_frames = (rec.frames0, w.frames, rec.impact_frame)
        if a.pose and imp_step:
            hold(pose_slide(np.array(jt), imp_step, ROOT / "data/references/mason_v2_p1_s06.npz", kind_txt, label(m)), 5)
        meta["segments"].append(dict(kind=dk, blend=blend or None, script_weight=swt, model=label(m), qualifies=okq, failed=fails, seed=seed, selection_pass_carry=sh["carry"], actuator_tags=tags,
                                     frames=dict(start=seg_frames[0], end=seg_frames[1], impact=seg_frames[2]),
                                     rendered=dict(carry=sw["carry"], carry_yd=sw["carry_yd"], total_yd=sw["total_yd"], lateral_y=sw["final_y"], launch_deg=sw["launch_elev_deg"], peak_club_mph=rec.peak_club * 2.23694, impact_club_mps=sw["impact_club_speed"]),
                                     all_swings=[dict(seed=s_, carry=x["carry"], y=x["final_y"], launch=x["launch_elev_deg"]) for s_, x in res]))
    # end card
    e = ["Caveats", "- ACTUATORS: force_scale 2 rows = HYPOTHETICAL-strength actuators (boosted force caps), not real hardware; power tier = hypothetical, no spin model (backspin hand-set), impact gain 1.28 INFLATED (gain 1.20 smash ~1.46-1.48). Stock = force_scale 1.", f"- {lb['episodes']} episodes per mode, seeds {lb['seed_base']}+; flight tracker = MuJoCo ball only (no spin / sidespin model), so lateral spread is optimistic.",
         "- Carry is the first-landing distance; launch = ball velocity at club-ball separation; club speed = peak club-head geom speed (validated < 100 m/s).",
         "- 'BLEND a/b' = executed command is a% script-distilled policy / b% scripted (script_weight from the run's env kwargs). 'LEARNED' = trained policy (PPO residual on a scripted swing, or behaviour-cloned imitation: see segment label). 'SCRIPTED (not learned)' = zero residual, no learning. Scripted rows never count as learned.",
         "- Learned strikes are regime-sensitive: one swing is not the average; see the leaderboard slides for all-episode stats. Address-noise outliers exist.",
         "- DTW style scores (leaderboard.md) are 2D-proxy, tempo +-15% indicative only; Mason v3 slow-mo refs are loose-tempo extras."]
    if noise_caveat(lm) and (lm.get("env_kwargs") or {}).get("script_weight") == 0.0: e.insert(1, "- " + noise_caveat(lm) + ". NOISE-FRAGILE: the distilled policy loses much of its carry under small observation/action noise (quick screen, my 80%-of-clean threshold).")
    if (lm.get("env_kwargs") or {}).get("script_weight") == 0.0: e = [x.replace("'LEARNED' = trained policy (PPO residual on a scripted swing, or behaviour-cloned imitation: see segment label)", "'SCRIPT-DISTILLED POLICY' = behaviour-cloned imitation of the scripted swing (not learned from Mason)") for x in e]
    if (lm.get("env_kwargs") or {}).get("script_weight") == 0.0: e.insert(1, "- SCRIPT-DISTILLED row = script-free imitation of the scripted v3 swing (behaviour cloning, 100% of joint targets from the policy); it reproduces the script, it does not discover a new swing.")
    if a.env_override: e.insert(1, "- ENV OVERRIDE %s applied to the learned segment only. The leaderboard slides above show the unmodified leaderboard row (impact gain 1.28 for the power tier = inflated distances); the swing segment and its banner use the override and the gate numbers named in the banner. Hypothetical power tier, no spin model (backspin hand-set)." % a.env_override)
    if fallback: e.insert(1, "THIS IS A FALLBACK PREVIEW: no trained model qualifies - the learned segment is not a good drive.")
    if a.profiles:
        for img_, sec_ in profiles_slides(ROOT / a.profiles): hold(img_, sec_)
        meta['profiles_segment'] = a.profiles
    ls_ = sum([wrap(x, 108) for x in e[1:]], []); pages = [ls_[i:i + 11] for i in range(0, len(ls_), 11)]   # paginate: a card holds ~11 wrapped lines at this size
    for pi, pg in enumerate(pages):
        hold(card([f"Caveats ({pi + 1}/{len(pages)})"] + pg, {1: (255, 70, 70)} if (fallback and pi == 0) else {}, 0.55), 6)
    meta["end_card_s"] = 6 * len(pages)
    w.close(); meta["frames"] = w.frames; meta["duration_s"] = w.frames / FPS; meta["slowdown"] = "ramped: 3-14 physics steps/frame pre-impact, 2 at impact (+0.1 s), 6 then 24 after; factor shown live"
    (ROOT / a.out).with_suffix(".json").write_text(json.dumps(meta, indent=1, default=float)); print(json.dumps({k: v for k, v in meta.items() if k != "segments"}, indent=1, default=float))
    if not a.no_extras: extras(ROOT / a.out, meta, lb)
    for s_ in meta["segments"]: print(s_["kind"], s_["model"], s_["qualifies"], s_["seed"], {k: round(v, 2) for k, v in s_["rendered"].items()})


if __name__ == "__main__":
    main()
