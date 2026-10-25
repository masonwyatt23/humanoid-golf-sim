"""Re-mine Mason's feed screen-recordings (v2): layout-agnostic chunking + relaxed swing detection +
view / handedness classification + `mason_v2_*` references.

Stage 1 (`--stage track`): decode each video, crop the media band (y 9%-86% of frame, works for dark/night
posts where the brightness-based tile finder of ingest_feed_recordings fails), split into clips at hard cuts
(scroll / next post), run MediaPipe PoseLandmarker per unique frame, cache tracks (scratch, not git).
Stage 2 (`--stage swings`): from cached tracks, segment swings with relaxed params, classify camera view
and handedness from the pose, outlier-reject, write `data/references/mason_v2_*.npz` (+ report JSON).

    export LD_LIBRARY_PATH=<local-path>/libroot/usr/lib/x86_64-linux-gnu
    python -m data.remine_feed_v2 --stage track  --model <local-path>/pose_landmarker_heavy.task
    python -m data.remine_feed_v2 --stage swings
"""
from __future__ import annotations

import os
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data import ingest_feed_recordings as fr  # noqa: E402
from data import process_video as pv  # noqa: E402
from data import provenance as prov  # noqa: E402
from data import swing_segmentation as ss  # noqa: E402

Y0_FRAC, Y1_FRAC = 0.09, 0.86
CUT_THR = 15.0


# ------------------------------------------------------------------ view / handedness (pure numpy)
def _nm(x):
    with np.errstate(all="ignore"):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            return np.nanmedian(x)


def classify_view(img: np.ndarray, t: np.ndarray, takeaway_t: float) -> Dict:
    """Camera view from the pose at address (frames just before takeaway).
    face-on: shoulder line is ~perpendicular to the optical axis -> wide shoulder separation in the image
    (relative to torso length) and wide stance; down-the-line: shoulders/hips overlap -> narrow.
    Returns {view, shoulder_width_ratio, hip_width_ratio, stance_ratio, confidence}."""
    sel = (t >= takeaway_t - 0.6) & (t <= takeaway_t + 0.05)
    if sel.sum() < 3:
        sel = np.arange(len(t)) < max(4, len(t) // 5)
    a = img[sel]
    ok = lambda i: a[:, i, 3] >= 0.4
    sh = np.linalg.norm(a[:, pv.L_SH, :2] - a[:, pv.R_SH, :2], axis=1)
    hip = np.linalg.norm(a[:, pv.L_HIP, :2] - a[:, pv.R_HIP, :2], axis=1)
    tor = np.linalg.norm(a[:, [pv.L_SH, pv.R_SH], :2].mean(1) - a[:, [pv.L_HIP, pv.R_HIP], :2].mean(1), axis=1)
    sw = _nm(sh / tor)
    hw = _nm(hip / tor)
    stance = _nm(np.abs(a[:, pv.L_ANK, 0] - a[:, pv.R_ANK, 0]) / tor)
    # shoulder_width/torso ~1.0-1.3 face-on, ~0.2-0.5 DTL (calibrated on the clips, see report)
    if not np.isfinite(sw):
        return dict(view="unknown", shoulder_width_ratio=float("nan"), hip_width_ratio=float("nan"),
                    stance_ratio=float("nan"), confidence=0.0)
    if sw >= 0.8:
        v, c = "face_on", min(1.0, (sw - 0.8) / 0.3 + 0.5)
    elif sw <= 0.35:
        v, c = "down_the_line", min(1.0, (0.35 - sw) / 0.2 + 0.5)
    else:
        v, c = "oblique", 0.5
    return dict(view=v, shoulder_width_ratio=float(sw), hip_width_ratio=float(hw), stance_ratio=float(stance),
                confidence=float(c))


def _elbow_angle(w: np.ndarray, sh, el, wr) -> np.ndarray:
    a, b, c = w[:, sh, :3], w[:, el, :3], w[:, wr, :3]
    u, v = a - b, c - b
    cos = (u * v).sum(1) / (np.linalg.norm(u, axis=1) * np.linalg.norm(v, axis=1) + 1e-9)
    return np.degrees(np.arccos(np.clip(cos, -1, 1)))


def classify_handedness(img: np.ndarray, world: np.ndarray, t: np.ndarray, top_t: float, impact_t: float,
                        takeaway_t: float, view: str, tempo_valid: bool = True) -> Dict:
    """Handedness from the footage using the pose model's anatomical L/R labels.  Two voting cues:
    A) lead arm at the top of the backswing = the straighter arm (lead elbow ~150-180 deg, trail folded
       ~80-120 deg).  Lead arm anatomical-left -> right-handed.  Only used when a real backswing exists
       (tempo_valid), otherwise 'top' is meaningless (edited / looped clips).
    C) finish: hands end up over the LEAD shoulder (horizontal/image distance to each shoulder, averaged over
       frames >=0.35 s after impact).  Nearer to anatomical-left shoulder -> right-handed.  Needs >=4 good frames.
    B) (recorded, NOT voted) face-on hands-side at top: unreliable when the torso turns away from the camera.
    A clip mirror-flipped by the poster/camera app reads as the opposite handedness (undetectable from pose)."""
    out: Dict = dict(handedness="unknown", cue_lead_arm=None, cue_hands_side=None, cue_finish=None, confidence=0.0,
                     elbow_L_top=float("nan"), elbow_R_top=float("nan"), finish_ratio=float("nan"))
    votes = []
    i = int(np.argmin(np.abs(t - top_t)))
    lo, hi = max(0, i - 2), min(len(t), i + 3)
    w = world[lo:hi]
    eL = _nm(_elbow_angle(w, pv.L_SH, pv.L_EL, pv.L_WR))
    eR = _nm(_elbow_angle(w, pv.R_SH, pv.R_EL, pv.R_WR))
    out.update(elbow_L_top=float(eL), elbow_R_top=float(eR))
    if tempo_valid and np.isfinite(eL) and np.isfinite(eR) and abs(eL - eR) >= 15:
        lead = "left" if eL > eR else "right"
        out["cue_lead_arm"] = lead
        votes.append(("right" if lead == "left" else "left", min(1.0, abs(eL - eR) / 60.0)))
    # finish cue
    sel = (t >= impact_t + 0.35)
    a = img[sel]
    if len(a) >= 4:
        ok = (a[:, [pv.L_SH, pv.R_SH, pv.L_WR, pv.R_WR], 3] >= 0.5).all(1)
        a = a[ok]
        if len(a) >= 4:
            hands = a[:, [pv.L_WR, pv.R_WR], :2].mean(1)
            dL = np.linalg.norm(hands - a[:, pv.L_SH, :2], axis=1)
            dR = np.linalg.norm(hands - a[:, pv.R_SH, :2], axis=1)
            tor = np.linalg.norm(a[:, [pv.L_SH, pv.R_SH], :2].mean(1) - a[:, [pv.L_HIP, pv.R_HIP], :2].mean(1), axis=1)
            r = float(np.median((dR - dL) / np.maximum(tor, 1e-6)))        # >0: hands nearer the LEFT shoulder
            out["finish_ratio"] = r
            if abs(r) >= 0.08:
                lead = "left" if r > 0 else "right"
                out["cue_finish"] = lead
                votes.append(("right" if lead == "left" else "left", min(1.0, abs(r) / 0.4)))
    if view in ("face_on", "oblique") and np.isfinite(i):
        a = img[lo:hi]
        hands = np.nanmean(a[:, [pv.L_WR, pv.R_WR], :2], axis=1).mean(0)
        shm = a[:, [pv.L_SH, pv.R_SH], :2].mean(1).mean(0)
        sdir = (a[:, pv.R_SH, 0] - a[:, pv.L_SH, 0]).mean()
        tor = np.linalg.norm(shm - a[:, [pv.L_HIP, pv.R_HIP], :2].mean(1).mean(0))
        out["hands_side_ratio"] = float((hands[0] - shm[0]) * np.sign(sdir) / max(tor, 1e-6))
        out["cue_hands_side"] = "right" if out["hands_side_ratio"] > 0 else "left"
    if votes:
        sc = sum((1 if h == "right" else -1) * wgt for h, wgt in votes)
        out["handedness"] = "right" if sc > 0 else "left" if sc < 0 else "unknown"
        out["confidence"] = float(min(1.0, abs(sc) / max(1.0, len(votes))))
        out["cues_agree"] = len({h for h, _ in votes}) == 1
        out["n_votes"] = len(votes)
    return out


# ------------------------------------------------------------------ stage 1
def scan_chunks(video: Path):
    import cv2
    cap = cv2.VideoCapture(str(video))
    ts, grays = [], []
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    y0, y1 = int(Y0_FRAC * H), int(Y1_FRAC * H)
    while True:
        ok, f = cap.read()
        if not ok:
            break
        ts.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
        grays.append(cv2.cvtColor(cv2.resize(f[y0:y1], (118, 197), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY))
    cap.release()
    t = np.asarray(ts)
    if np.any(np.diff(t) <= 0):
        t = np.arange(len(t)) / 60.0
    dup, cut = ss.frame_changes(np.stack(grays))
    cut = np.abs(np.diff(np.stack(grays).astype(np.int16), axis=0, prepend=grays[0][None].astype(np.int16))).mean(axis=(1, 2)) > CUT_THR
    starts = [0, *np.flatnonzero(cut).tolist()]
    chunks = []
    for a, b in zip(starts, [*starts[1:], len(t)]):
        idx = [i for i in range(a, b) if not dup[i] or i == a]
        if len(idx) >= 8 and t[b - 1] - t[a] >= 0.8:
            chunks.append((a, b, idx))
    return t, chunks, (y0, y1)


def enhance_dark(bgr):
    """Night / silhouette footage: gamma lift + CLAHE on luminance so the pose model sees limbs."""
    import cv2
    lut = (255.0 * (np.arange(256) / 255.0) ** 0.5).astype(np.uint8)
    f = cv2.LUT(bgr, lut)
    lab = cv2.cvtColor(f, cv2.COLOR_BGR2LAB)
    lab[..., 0] = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(lab[..., 0])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def stage_track(args):
    import cv2
    lander = fr.Landmarker(args.model)
    cache = Path(args.cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    try:
        for v in sorted(Path(args.videos).glob("mason_swing_part*.mov")):
            if args.only and args.only not in v.name:
                continue
            t0 = time.time()
            t, chunks, (y0, y1) = scan_chunks(v)
            print(f"{v.name}: {len(t)} frames, {len(chunks)} chunks ({time.time()-t0:.0f}s scan)", flush=True)
            cap = cv2.VideoCapture(str(v))
            want = {}
            sel = None if not args.chunks else {int(c) for c in args.chunks.split(",")}
            for k, (a, b, idx) in enumerate(chunks):
                if sel is not None and k not in sel:
                    continue
                for i in idx:
                    want[i] = k
            bufs: Dict[int, list] = {k: [] for k in range(len(chunks)) if sel is None or k in sel}
            chunks_sel = [(kk, c) for kk, c in enumerate(chunks) if sel is None or kk in sel]
            for i in range(len(t)):
                ok, f = cap.read()
                if not ok:
                    break
                k = want.get(i)
                if k is not None:
                    bufs[k].append((i, cv2.imencode(".jpg", f[y0:y1], [cv2.IMWRITE_JPEG_QUALITY, 95])[1].tobytes()))
                if k is None and False:
                    pass
                # flush finished chunks
                for kk in [kk for kk, (a, b, idx) in chunks_sel if idx[-1] == i and kk in bufs]:
                    items = bufs.pop(kk)
                    out = cache / f"{v.stem}_c{kk:02d}.npz"
                    frames = [cv2.imdecode(np.frombuffer(bb, np.uint8), cv2.IMREAD_COLOR) for _, bb in items]
                    if args.enhance:
                        frames = [enhance_dark(f_) for f_ in frames]
                    tr = fr.track_span(frames, lander)
                    tt = t[[ii for ii, _ in items]]
                    np.savez_compressed(out, t=tt, img=tr["img"].astype(np.float32), world=tr["world"].astype(np.float32),
                                        bbox=np.array(tr["bbox"] or [0, 0, 0, 0]), tile_wh=np.array(tr["tile_wh"]),
                                        y_off=np.array(y0))
                    print(f"  c{kk:02d} {tt[0]:.1f}-{tt[-1]:.1f}s n={len(tt)} det={tr['detect_frac']:.2f} ({time.time()-t0:.0f}s)", flush=True)
            cap.release()
    finally:
        lander.close()



# ------------------------------------------------------------------ stage 2
# manual observations from viewing the footage (time windows in the source video, seconds)
KNOWN_NOTES = {("mason_swing_part3.mov", 84.0, 90.5): "On-screen caption 'What my swing would look like if I was right "
                                                     "handed': this clip is a mirror-flipped edit of a left-handed swing"}
RELAXED = dict(peak_speed=3.5, top_above_shoulder=0.0, min_phase_s=0.08, min_peak_gap_s=0.8)


def _overlap(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0)) / max(1e-6, min(a1 - a0, b1 - b0))


def _build(video_name, name, sw, track, tt, aux, args, partial=False):
    import types
    ns = types.SimpleNamespace(min_visibility=0.3, min_valid_frac=0.5, out_dt=0.01, handedness="left")
    data, err = fr.build_swing_npz(video_name, 0, sw, track, tt, aux, {}, ns)
    return data, err


def stage_swings(args):
    import types
    from data import refine_swings as rs
    cache = Path(args.cache_dir)
    v1 = json.loads((Path(__file__).parent / "references" / "mason_feed_report.json").read_text())
    v1_sw = {v["video"]: v["swings"] for v in v1["videos"]}
    out_dir = Path(__file__).parent / "references"
    report = {"videos": [], "n_full": 0, "n_partial": 0, "clips": []}
    sigs: List[Tuple[str, np.ndarray]] = []
    params = ss.SwingParams(**RELAXED)
    for part in (1, 2, 3):
        stem = f"mason_swing_part{part}"
        vname = stem + ".mov"
        files = sorted(cache.glob(f"{stem}_c*.npz"))
        k_sw = 0
        vrep = {"video": vname, "chunks": [], "swings": []}
        for fn in files:
            d = np.load(fn)
            t = d["t"]; img = d["img"].astype(float); wld = d["world"].astype(float)
            ck = {"chunk": fn.stem.split("_c")[-1], "t0": round(float(t[0]), 2), "t1": round(float(t[-1]), 2),
                  "n_unique": int(len(t))}
            det = float(np.isfinite(img[:, pv.R_SH, 0]).mean())
            ck["detect_frac"] = round(det, 3)
            if det < 0.4:
                ck["status"] = "person_intermittent_or_absent"; vrep["chunks"].append(ck); continue
            _, _, _, tl0 = fr.hand_track(img)
            img_c, wld_c, drop = rs.reject_outliers(img, wld, tl0)
            track = {"img": img_c, "world": wld_c, "bbox": tuple(int(v) for v in d["bbox"]),
                     "tile_wh": tuple(int(v) for v in d["tile_wh"]), "detect_frac": det}
            swings, rej, aux, jumps = fr.segment_span(track, t, params, min_clip_s=0.8)
            ck.update(n_swings=len(swings), n_rejected=len(rej), outlier_frac=round(drop, 4),
                      pose_jump_cuts=[round(j, 2) for j in jumps],
                      torso_frac_of_tile_h=round(float(aux[3] / track["tile_wh"][1]), 3),
                      rejected=[{"t": round(r["t"], 2), "reason": r["reason"].split(" ")[0]} for r in rej])
            ck["status"] = "swing" if swings else "no_swing"
            vrep["chunks"].append(ck)
            cands = [("full", sw, None) for sw in swings]
            for r in rej:
                if r["reason"].startswith("no_backswing"):
                    tp = r["t"]
                    cands.append(("partial", ss.Swing(max(t[0], tp - 1.2), min(t[-1], tp + 1.0), tp - 1.0, tp - 0.5, tp, 5.0, 0.5, 0.5, float("nan"), ["partial_no_backswing"]), r))
            for kind, sw, _r in sorted(cands, key=lambda c: c[1].start_t):
                if sw.end_t - sw.start_t < 1.0:
                    continue
                data, err = _build(vname, "", sw, track, t, aux, args, partial=(kind == "partial"))
                if data is None:
                    vrep["swings"].append({"kind": kind, "t": [round(sw.start_t, 2), round(sw.end_t, 2)], "dropped": err[:60]}); continue
                m = (t >= sw.start_t) & (t <= sw.end_t)
                sig = ss.trajectory_signature(aux[0][m], aux[2][m], aux[3])
                dup = next((nm for nm, sg in sigs if ss.is_duplicate(sig, sg)), None)
                if dup:
                    vrep["swings"].append({"kind": kind, "t": [round(sw.start_t, 2), round(sw.end_t, 2)], "dropped": f"duplicate_of {dup}"}); continue
                view = classify_view(img_c, t, sw.takeaway_t)
                hd = classify_handedness(img_c, wld_c, t, sw.top_t, sw.impact_t, sw.takeaway_t, view["view"], tempo_valid=bool(np.isfinite(sw.tempo) and kind == "full"))
                legs = img_c[m][:, [pv.L_KNEE, pv.R_KNEE, pv.L_ANK, pv.R_ANK], 3]
                leg_ratio = float((np.nan_to_num(legs, nan=0) >= 0.3).all(1).mean())
                flags = list(sw.flags) + (["partial_no_backswing"] if kind == "partial" and "partial_no_backswing" not in sw.flags else [])
                meta = {"mean_visibility": float(data["mean_visibility"]), "process_valid_frac": float(data["valid_frac"]),
                        "leg_valid_frame_ratio": leg_ratio, "tempo_ratio": None if not np.isfinite(sw.tempo) else float(sw.tempo),
                        "torso_frac_of_tile_h": float(data["torso_frac_of_tile_h"]), "flags": flags}
                if float(data["valid_frac"]) < 0.6:
                    flags.append("upper_valid_frac_below_0.6")
                q = rs.quality_score(meta)
                if kind == "partial":
                    q = min(q, 0.5)
                stated = "left"
                detected = hd["handedness"]
                conf = hd["confidence"]
                final = detected if (detected != "unknown" and conf >= 0.5) else stated
                conflict = final != stated
                if conflict:
                    flags.append("detected_right_handed_possible_mirrored_edit_or_other_person")
                note = next((n for (vn, a0, a1), n in KNOWN_NOTES.items() if vn == vname and a0 <= sw.start_t <= a1), "")
                if note:
                    flags.append("mirrored_edit_caption_in_video")
                verified = bool(detected == final and conf >= 0.5 and hd.get("cues_agree", False) and not note) or bool(note and detected == "right")
                recommended = (kind == "full" and q >= 0.65 and not conflict and float(data["valid_frac"]) >= 0.6 and np.isfinite(sw.tempo) and view["view"] != "unknown")
                k_sw += 1
                name = f"mason_v2_p{part}_s{k_sw:02d}" + ("_partial" if kind == "partial" else "")
                ov = [s_["file"] for s_ in v1_sw.get(vname, []) if _overlap(sw.start_t, sw.end_t, s_["t_start"], s_["t_end"]) > 0.5]
                data.update(
                    source=np.array("mason_self_filmed"), style=np.array("mason"), is_synthetic=np.array(False),
                    capture=np.array("screen_recording_of_social_feed_v2"), source_file=np.array(vname),
                    swing_index=np.array(k_sw), view=np.array(view["view"]), view_confidence=np.array(view["confidence"]),
                    shoulder_width_ratio=np.array(view["shoulder_width_ratio"]), stance_ratio=np.array(view["stance_ratio"]),
                    handedness=np.array(final), handedness_detected=np.array(detected), handedness_confidence=np.array(conf),
                    handedness_stated=np.array(stated), handedness_verified=np.array(verified), source_clip_note=np.array(note), handedness_cue_lead_arm=np.array(str(hd["cue_lead_arm"])),
                    handedness_cue_hands_side=np.array(str(hd["cue_hands_side"])), handedness_cue_finish=np.array(str(hd["cue_finish"])), finish_ratio=np.array(hd["finish_ratio"]),
                    elbow_L_top_deg=np.array(hd["elbow_L_top"]), elbow_R_top_deg=np.array(hd["elbow_R_top"]),
                    mirrored=np.array(False), native_footage=np.array(True), partial=np.array(kind == "partial"),
                    joint_convention=np.array("anatomical: right_* cols are the golfer's anatomical RIGHT arm/leg "
                                              "(= LEAD arm for a left-handed golfer, TRAIL arm for right-handed)"),
                    club=np.array("unknown"), capture_fps=np.array(0.0),
                    t_start_in_video=np.array(sw.start_t), t_end_in_video=np.array(sw.end_t),
                    t_takeaway=np.array(sw.takeaway_t), t_top=np.array(sw.top_t), t_impact=np.array(sw.impact_t),
                    tempo_ratio=np.array(sw.tempo), backswing_s=np.array(sw.backswing_s), downswing_s=np.array(sw.downswing_s),
                    leg_valid_frame_ratio=np.array(leg_ratio), outlier_landmark_frac=np.array(drop),
                    quality_score=np.array(q), quality_flags=np.array(flags, dtype=str), recommended=np.array(bool(recommended)),
                    v1_overlap=np.array(",".join(ov)), remine_version=np.array("v2"))
                if conflict and not note:
                    # detected right-handed, no caption: possibly another golfer or a flipped edit -> not asserted self-owned
                    prov.tag(data, "unknown", overwrite=True, provenance_source="mason_feed_unverified_person",
                             provenance_note="Clip from Mason's feed that reads right-handed with no mirror caption: may be another "
                                             "person or a flipped edit; identity/consent not established, so not commercial-safe.")
                else:
                    prov.tag(data, "mason_self_filmed", overwrite=True)
                if not args.dry_run:
                    np.savez(out_dir / f"{name}.npz", **data)
                sigs.append((name, sig))
                vrep["swings"].append({"file": f"{name}.npz", "kind": kind, "t": [round(sw.start_t, 2), round(sw.end_t, 2)],
                                       "view": view["view"], "shoulder_w": round(view["shoulder_width_ratio"], 2),
                                       "handedness": final, "detected": detected, "hconf": round(conf, 2),
                                       "cues(lead_arm,finish)": [hd["cue_lead_arm"], hd["cue_finish"]], "finish_r": round(hd["finish_ratio"], 2) if np.isfinite(hd["finish_ratio"]) else None, "elbL/R_top": [round(hd["elbow_L_top"]), round(hd["elbow_R_top"])],
                                       "tempo": None if not np.isfinite(sw.tempo) else round(float(sw.tempo), 2), "quality": round(q, 3),
                                       "recommended": bool(recommended), "flags": flags, "v1_overlap": ov,
                                       "legs": round(leg_ratio, 2), "frames": int(len(data["time"]))})
                report["n_partial" if kind == "partial" else "n_full"] += 1
        report["videos"].append(vrep)
    # un-mirror clips whose caption says they are flipped edits: write a native-left version
    from data import mirror_references as mr
    for v in report["videos"]:
        for s_ in v["swings"]:
            if "mirrored_edit_caption_in_video" in s_.get("flags", []) and "file" in s_ and not args.dry_run:
                src = out_dir / s_["file"]
                d0 = {k: x for k, x in np.load(src, allow_pickle=False).items()}
                d1 = mr.mirror_dict(d0, src.name)
                d1.update(handedness=np.array("left"), handedness_detected=np.array("left"), mirrored=np.array(True),
                          native_footage=np.array(False), handedness_verified=np.array(True),
                          recommended=np.array(bool(s_["quality"] >= 0.65 and np.isfinite(float(d0["tempo_ratio"])))),
                          provenance_note=np.array(str(d0["provenance_note"]) + " Un-mirrored from a caption-flagged right-handed edit of Mason's left-handed swing."))
                dst = out_dir / (src.stem + "_unmirrored.npz")
                np.savez(dst, **d1)
                s_["unmirrored_file"] = dst.name
    (out_dir / "mason_v2_report.json").write_text(json.dumps(report, indent=1, default=str)) if not args.dry_run else None
    for v in report["videos"]:
        print(v["video"])
        for s_ in v["swings"]:
            print("  ", s_)
    print("full", report["n_full"], "partial", report["n_partial"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["track", "swings"], required=True)
    ap.add_argument("--videos", default=str(Path(__file__).parent / "mason_swings"))
    ap.add_argument("--model", default=None, help="default: $GOLF_SCRATCH_DIR/pose_landmarker_heavy.task")
    ap.add_argument("--cache-dir", default=None, help="default: $GOLF_SCRATCH_DIR/cache_v2")
    ap.add_argument("--only")
    ap.add_argument("--chunks", help="comma list of chunk indices to (re)track")
    ap.add_argument("--enhance", action="store_true", help="gamma+CLAHE dark-footage enhancement before pose")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.model is None or a.cache_dir is None:
        _s = (os.environ.get("GOLF_SCRATCH_DIR") or sys.exit("set GOLF_SCRATCH_DIR (local scratch dir with the raw/cached data) or pass the path explicitly"))
        a.model = a.model or str(Path(_s) / "pose_landmarker_heavy.task"); a.cache_dir = a.cache_dir or str(Path(_s) / "cache_v2")
    if a.stage == "track":
        stage_track(a)
    else:
        stage_swings(a)
