"""Slow-motion / effective-fps audit of Mason's feed recordings + `mason_v3_*` references.

What it does (all from the stage-1 pose tracks cached by data/remine_feed_v2.py, so no new pose run):
 1. Cadence: the recordings are 60 fps screen captures of a ~30 fps feed player.  `unique frames` are the frames
    that differ from the previous one (pixel diff); this is already how the tracks were built.  The audit of the
    raw video (data/audit_feed_cadence.py) shows every swing window is 30 fps unique (one 15 fps), none is 60.
 2. Swing finder tuned for slow motion (long backswing, low hand speed): per pose-continuous segment, top = peak
    of smoothed hand height above the shoulders, takeaway = last time the hands were still within 0.15 torso of
    their address height, impact proxy = peak hand speed after top.  Normal-speed swings found by the SAME
    detector give the reference durations.
 3. Slowdown factor k = slow-clip phase duration / normal-speed phase duration, for backswing and downswing, with
    TWO anchors (the absolute scale is NOT measurable from the footage; k is only an order-of-magnitude estimate):
      A. feed anchor: median of Mason's 11 recommended normal-speed v2 swings (same kind of detector). These
         durations (0.48 s / 0.17 s) are shorter than typical real swings, so anchor A over-estimates k.
      B. physical anchor: typical real-time swing of a fast golfer, backswing 0.7-0.9 s, downswing 0.22-0.30 s
         (coaching/biomechanics rule of thumb; NOT measured here, no citation checked).
    Central k = geometric mean over {backswing, downswing} x {A, B}; range = min/max of those four numbers.
    What IS well determined is the backswing:downswing ratio (scale-invariant) and the unique-frame counts.
    Only clips whose slow motion was confirmed by eye (contact sheets) are written (VERIFIED_SLOW); other
    detections are listed in the report as unverified candidates (a few were merged normal swings).
 4. Writes `data/references/mason_v3_*.npz` for slow-motion swings that have enough downswing frames, and
    `data/references/mason_v3_report.json` (deterministic).

    python -m data.remine_slowmo_v3            # needs <local-path>/cache_v2 ($GOLF_SCRATCH_DIR/cache_v2) from remine_feed_v2 --stage track
"""
from __future__ import annotations

import os
import argparse
import json
import sys
import types
from pathlib import Path
from typing import Dict, List

import numpy as np
from scipy.signal import savgol_filter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data import ingest_feed_recordings as fr  # noqa: E402
from data import process_video as pv  # noqa: E402
from data import provenance as prov  # noqa: E402
from data import refine_swings as rs  # noqa: E402
from data import remine_feed_v2 as v2  # noqa: E402
from data import swing_segmentation as ss  # noqa: E402

SLOW_BACKSWING_S = 1.2     # normal feed swings: backswing 0.45-0.7 s
MIN_DOWN_FRAMES = 10       # unique frames between top and impact needed for a "timing" reference
HY_TOP_MIN = 0.15          # hands this many torso lengths above the shoulder line at the top
ADDRESS_TOL = 0.15
# (part, chunk, approx takeaway second in video) confirmed slow motion by viewing frames: smooth multi-second backswing
VERIFIED_SLOW = {(1, "06", 44), (2, "09", 58), (2, "09", 63), (2, "00", 1)}
ANCHOR_B = dict(backswing_s=(0.7, 0.9), downswing_s=(0.22, 0.30))


def signals(img: np.ndarray, t: np.ndarray):
    hands, sh_y, hip, tl = fr.hand_track(img)
    hy = (sh_y - hands[:, 1]) / tl
    v = np.gradient(hands, t, axis=0)
    sp = np.hypot(v[:, 0], v[:, 1]) / tl
    ok = np.isfinite(sp)
    sp = np.where(ok, sp, 0.0)
    n = len(t)
    w = 9 if n >= 9 else (n // 2) * 2 - 1
    if w >= 5:
        sp = savgol_filter(sp, w, 2)
        hy_f = np.where(np.isfinite(hy), hy, np.nan)
        s = hy_f.copy()
        good = np.isfinite(s)
        if good.sum() > w:
            s[good] = savgol_filter(s[good], w, 2)
        hy = s
    return hands, hy, sp, tl


def find_swings(t, hy, sp, min_gap_s=1.5):
    """Return list of dicts(takeaway, top, impact, peak_speed). One swing per prominent hand-height maximum."""
    out = []
    ok = np.isfinite(hy)
    if ok.sum() < 10:
        return out
    cand = [i for i in range(1, len(t) - 1) if ok[i] and ok[i - 1] and ok[i + 1] and hy[i] >= HY_TOP_MIN
            and hy[i] >= hy[i - 1] and hy[i] > hy[i + 1]]
    # keep the highest maximum within each min_gap window
    cand.sort(key=lambda i: -hy[i])
    kept: List[int] = []
    for i in cand:
        if all(abs(t[i] - t[j]) >= min_gap_s for j in kept):
            kept.append(i)
    last_impact = -1.0
    for i in sorted(kept):
        pre = np.flatnonzero(ok[:i])
        if len(pre) < 5:
            continue
        # contiguous tracked stretch before top
        base = np.nanmin(hy[max(0, i - int(12 * 30)):i + 1])
        if hy[i] - base < 0.8:
            continue
        below = np.flatnonzero(ok[:i] & (hy[:i] <= base + ADDRESS_TOL))
        if not len(below):
            continue
        a = int(below[-1])
        # a real swing starts from address: the hands must have been still near the address height for >= 0.4 s
        # before takeaway, and (if a swing was already accepted) must have returned to address since its impact
        # -> rejects finish-phase bumps and loop restarts that begin mid-swing
        still = ok[:a + 1] & (hy[:a + 1] <= base + ADDRESS_TOL) & (t[:a + 1] >= t[a] - 0.4)
        if t[a] - t[0] < 0.4 or still.sum() < 4 or t[a] <= last_impact + 0.2:
            continue
        # impact: peak speed after the top, within the descent
        post_end = i + 1
        while post_end < len(t) and t[post_end] - t[i] < 3.0 and (not ok[post_end] or hy[post_end] > base + 0.2):
            post_end += 1
        if post_end - i < 3:
            continue
        j = i + int(np.argmax(sp[i:post_end]))
        last_impact = float(t[j])
        out.append(dict(takeaway=float(t[a]), top=float(t[i]), impact=float(t[j]), peak_speed=float(sp[j]),
                        base_hy=float(base), top_hy=float(hy[i])))
    return out


def segments(img, t, tl):
    cuts = ss.pose_jump_cuts(img[:, fr.KEY, :2], tl)
    edges = [0, *[int(c) for c in cuts], len(t)]
    return [(a, b) for a, b in zip(edges[:-1], edges[1:]) if t[b - 1] - t[a] >= 0.8]


def run(args):
    cache = Path(args.cache_dir)
    out_dir = Path(__file__).parent / "references"
    rows: List[Dict] = []
    store = {}
    for part in (1, 2, 3):
        vname = f"mason_swing_part{part}.mov"
        for fn in sorted(cache.glob(f"mason_swing_part{part}_c*.npz")):
            d = np.load(fn)
            t = d["t"].astype(float)
            img = d["img"].astype(float)
            wld = d["world"].astype(float)
            if len(t) < 20 or np.isfinite(img[:, pv.R_SH, 0]).mean() < 0.4:
                continue
            _, _, _, tl0 = fr.hand_track(img)
            img_c, wld_c, drop = rs.reject_outliers(img, wld, tl0)
            track = {"img": img_c, "world": wld_c, "bbox": tuple(int(v) for v in d["bbox"]),
                     "tile_wh": tuple(int(v) for v in d["tile_wh"]), "detect_frac": 1.0}
            for a, b in segments(img_c, t, tl0):
                tt = t[a:b]
                hands, hy, sp, tl = signals(img_c[a:b], tt)
                for sw in find_swings(tt, hy, sp):
                    m = (tt >= sw["takeaway"]) & (tt <= sw["impact"])
                    md = (tt >= sw["top"]) & (tt <= sw["impact"])
                    iv = np.diff(tt[m])
                    rows.append(dict(part=part, video=vname, chunk=fn.stem.split("_c")[-1], seg=(float(tt[0]), float(tt[-1])),
                                     takeaway=sw["takeaway"], top=sw["top"], impact=sw["impact"],
                                     backswing_s=sw["top"] - sw["takeaway"], downswing_s=sw["impact"] - sw["top"],
                                     n_back_frames=int(((tt >= sw["takeaway"]) & (tt <= sw["top"])).sum()),
                                     n_down_frames=int(md.sum()),
                                     unique_fps=float(1.0 / np.median(iv)) if len(iv) else float("nan"),
                                     peak_speed=sw["peak_speed"], _key=(fn.name, a, b), _drop=drop))
                    store[len(rows) - 1] = (track, t, wld_c, img_c, a, b, tl)
    # anchor A: Mason's recommended normal-speed v2 swings
    va = []
    for f in sorted(out_dir.glob("mason_v2_p*_s*.npz")):
        if "unmirrored" in f.name:
            continue
        with np.load(f, allow_pickle=True) as z:
            if bool(z["recommended"]) and bool(z["native_footage"]) and not bool(z["partial"]):
                va.append((float(z["backswing_s"]), float(z["downswing_s"])))
    ref = dict(feed_backswing_s=float(np.median([x[0] for x in va])), feed_downswing_s=float(np.median([x[1] for x in va])),
               n_feed=len(va), anchor_B=ANCHOR_B)
    slow = []
    for r in rows:
        r["verified_slow"] = (r["part"], r["chunk"], int(round(r["takeaway"]))) in VERIFIED_SLOW
        r["slow_motion"] = r["verified_slow"]
        r["slow_candidate"] = r["backswing_s"] >= SLOW_BACKSWING_S
        if r["slow_motion"]:
            slow.append(r)
            ests = {"backswing_A": r["backswing_s"] / ref["feed_backswing_s"], "downswing_A": r["downswing_s"] / ref["feed_downswing_s"],
                    "backswing_B": r["backswing_s"] / float(np.mean(ANCHOR_B["backswing_s"])),
                    "downswing_B": r["downswing_s"] / float(np.mean(ANCHOR_B["downswing_s"]))}
            lo_hi = [r["backswing_s"] / ANCHOR_B["backswing_s"][1], r["backswing_s"] / ref["feed_backswing_s"],
                     r["downswing_s"] / ANCHOR_B["downswing_s"][1], r["downswing_s"] / ref["feed_downswing_s"],
                     r["backswing_s"] / ANCHOR_B["backswing_s"][0], r["downswing_s"] / ANCHOR_B["downswing_s"][0]]
            r["slowdown_estimates"] = ests
            r["slowdown_median"] = float(np.exp(np.mean(np.log(list(ests.values())))))
            r["slowdown_range"] = [min(lo_hi), max(lo_hi)]
            r["effective_fps_est"] = 30.0 * r["slowdown_median"]
    report = dict(reference_normal=ref, n_swings_found=len(rows), n_slow=len(slow), n_slow_candidates_unverified=sum(1 for r in rows if r['slow_candidate'] and not r['slow_motion']), swings=[], written=[])
    k_sw = 0
    namespace = types.SimpleNamespace(min_visibility=0.3, min_valid_frac=0.45, out_dt=0.01, handedness="left")
    for idx, r in sorted(enumerate(rows), key=lambda x: (x[1]["part"], x[1]["takeaway"])):
        entry = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if not k.startswith("_")}
        entry["seg"] = [round(x, 2) for x in r["seg"]]
        if "slowdown_estimates" in r:
            entry["slowdown_estimates"] = {k: round(v, 2) for k, v in r["slowdown_estimates"].items()}
            entry["slowdown_range"] = [round(x, 2) for x in r["slowdown_range"]]
        report["swings"].append(entry)
        if not r["slow_motion"]:
            if r["slow_candidate"]:
                entry["note"] = "unverified slow-motion candidate (not confirmed by eye; some are merged normal swings); not written"
            continue
        track, t, wld_c, img_c, a, b, tl = store[idx]
        if r["n_down_frames"] < MIN_DOWN_FRAMES:
            entry["dropped"] = f"downswing_only_{r['n_down_frames']}_unique_frames"
            continue
        s0 = max(float(t[a]), r["takeaway"] - 0.8 * r["slowdown_median"])
        s0 = max(s0, r["takeaway"] - 1.5)
        s1 = min(float(t[b - 1]), r["impact"] + 0.5 * r["slowdown_median"])
        s1 = min(s1, r["impact"] + 1.5)
        sw = ss.Swing(s0, s1, r["takeaway"], r["top"], r["impact"], r["peak_speed"], r["backswing_s"],
                      r["downswing_s"], r["backswing_s"] / r["downswing_s"], [])
        aux = (fr.hand_track(track["img"]))
        data, err = fr.build_swing_npz(r["video"], 0, sw, track, t, aux, {}, namespace)
        if data is None:
            entry["dropped"] = err[:80]
            continue
        view = v2.classify_view(img_c, t, sw.takeaway_t)
        hd = v2.classify_handedness(img_c, wld_c, t, sw.top_t, sw.impact_t, sw.takeaway_t, view["view"], tempo_valid=True)
        detected, conf = hd["handedness"], hd["confidence"]
        final = detected if (detected != "unknown" and conf >= 0.5) else "left"
        conflict = final != "left"
        sl = (t >= s0) & (t <= s1)
        legs = img_c[sl][:, [pv.L_KNEE, pv.R_KNEE, pv.L_ANK, pv.R_ANK], 3]
        leg_ratio = float((np.nan_to_num(legs, nan=0) >= 0.3).all(1).mean())
        meta = {"mean_visibility": float(data["mean_visibility"]), "process_valid_frac": float(data["valid_frac"]),
                "leg_valid_frame_ratio": leg_ratio, "tempo_ratio": float(sw.tempo),
                "torso_frac_of_tile_h": float(data["torso_frac_of_tile_h"]), "flags": []}
        flags = ["slow_motion_clip"]
        if float(data["valid_frac"]) < 0.5:
            flags.append("valid_frac_below_0.5")
        if conflict:
            flags.append("detected_right_handed_possible_mirrored_edit_or_other_person")
        if float(data["valid_frac"]) < 0.6:
            flags.append("upper_valid_frac_below_0.6")
        q = rs.quality_score(meta)
        k_sw += 1
        name = f"mason_v3_p{r['part']}_s{k_sw:02d}_slowmo"
        t_real = (data["time"] - data["time"][0]) / r["slowdown_median"]
        verified = bool(detected == final and conf >= 0.5 and hd.get("cues_agree", False))
        data.update(
            source=np.array("mason_self_filmed"), style=np.array("mason"), is_synthetic=np.array(False),
            capture=np.array("screen_recording_of_social_feed_v3_slowmo"), source_file=np.array(r["video"]),
            swing_index=np.array(k_sw), view=np.array(view["view"]), view_confidence=np.array(view["confidence"]),
            shoulder_width_ratio=np.array(view["shoulder_width_ratio"]), stance_ratio=np.array(view["stance_ratio"]),
            handedness=np.array(final), handedness_detected=np.array(detected), handedness_confidence=np.array(conf),
            handedness_stated=np.array("left"), handedness_verified=np.array(verified),
            source_clip_note=np.array(""), handedness_cue_lead_arm=np.array(str(hd["cue_lead_arm"])),
            handedness_cue_hands_side=np.array(str(hd["cue_hands_side"])), handedness_cue_finish=np.array(str(hd["cue_finish"])),
            finish_ratio=np.array(hd["finish_ratio"]), elbow_L_top_deg=np.array(hd["elbow_L_top"]),
            elbow_R_top_deg=np.array(hd["elbow_R_top"]), mirrored=np.array(False), native_footage=np.array(True),
            partial=np.array(False),
            joint_convention=np.array("anatomical: right_* cols are the golfer's anatomical RIGHT arm/leg "
                                      "(= LEAD arm for a left-handed golfer, TRAIL arm for right-handed)"),
            club=np.array("unknown"), capture_fps=np.array(float(r["unique_fps"])),
            t_start_in_video=np.array(s0), t_end_in_video=np.array(s1),
            t_takeaway=np.array(sw.takeaway_t), t_top=np.array(sw.top_t), t_impact=np.array(sw.impact_t),
            tempo_ratio=np.array(sw.tempo), backswing_s=np.array(sw.backswing_s), downswing_s=np.array(sw.downswing_s),
            leg_valid_frame_ratio=np.array(leg_ratio), outlier_landmark_frac=np.array(0.0),
            quality_score=np.array(q), quality_flags=np.array(flags, dtype=str),
            recommended=np.array(bool(q >= 0.6 and not conflict and float(data["valid_frac"]) >= 0.6)),
            v1_overlap=np.array(""), remine_version=np.array("v3"),
            slow_motion=np.array(True), slowdown_factor_est=np.array(r["slowdown_median"]),
            slowdown_factor_min=np.array(r["slowdown_range"][0]), slowdown_factor_max=np.array(r["slowdown_range"][1]),
            slowdown_method=np.array("durations and hand speed vs normal-speed feed swings (same detector); +-30% or worse"),
            effective_fps_est=np.array(r["effective_fps_est"]),
            unique_fps=np.array(float(r["unique_fps"])), downswing_unique_frames=np.array(r["n_down_frames"]),
            backswing_unique_frames=np.array(r["n_back_frames"]),
            time_real_est=np.array(t_real),
            time_real_note=np.array("time_real_est = (time - time[0]) / slowdown_factor_est; 'time' stays in video seconds"),
            real_backswing_s_est=np.array(sw.backswing_s / r["slowdown_median"]),
            real_downswing_s_est=np.array(sw.downswing_s / r["slowdown_median"]))
        prov.tag(data, "mason_self_filmed", overwrite=True,
                 **({"license_class": "unknown", "commercial_ok": False, "provenance_source": "mason_feed_unverified_person",
                     "provenance_note": "Detected right-handed in a slow-motion feed clip: possibly another golfer or a flipped edit."}
                    if conflict else {}))
        prov.save_npz_atomic(out_dir / f"{name}.npz", data)
        entry["file"] = f"{name}.npz"
        entry["written_view"] = view["view"]
        entry["handedness"] = final
        entry["quality_score"] = round(float(q), 3)
        entry["recommended"] = bool(q >= 0.6 and not conflict and float(data["valid_frac"]) >= 0.6)
        report["written"].append(f"{name}.npz")
    (out_dir / "mason_v3_report.json").write_text(json.dumps(report, indent=1, sort_keys=True, default=float) + "\n")
    print(json.dumps({k: report[k] for k in ("reference_normal", "n_swings_found", "n_slow", "n_slow_candidates_unverified", "written")}, indent=1))
    for e in report["swings"]:
        if e.get("slow_motion"):
            print(e["part"], e["chunk"], e["takeaway"], e["top"], e["impact"], "back", e["backswing_s"], "down", e["downswing_s"],
                  "nd", e["n_down_frames"], "k", e.get("slowdown_estimates"), e.get("dropped", e.get("file")))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", default=None, help="default: $GOLF_SCRATCH_DIR/cache_v2")
    a = ap.parse_args()
    if a.cache_dir is None:
        a.cache_dir = str(Path((os.environ.get("GOLF_SCRATCH_DIR") or sys.exit("set GOLF_SCRATCH_DIR (local scratch dir with the raw/cached data) or pass the path explicitly"))) / "cache_v2")
    run(a)
