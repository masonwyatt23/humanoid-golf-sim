"""Phone screen-recordings of a social feed (Instagram etc.) -> per-swing reference .npz files.

    LD_LIBRARY_PATH=<dir with libEGL.so.1 if the system lacks it> \
    python -m data.ingest_feed_recordings --model /path/pose_landmarker_heavy.task \
        [--videos data/mason_swings] [--out data/references] [--debug-dir <local-path>]

Why a separate tool: a feed recording is ~15-25 *different* short clips (different scenes,
people-sizes, camera angles) separated by scrolling, wrapped in app UI.  `ingest_mason_swings`
assumes one swing per file filmed full-frame, so here we:

 1. Layout pass (cheap, 118x256 thumbnails): locate the video tile in every frame, mark
    scrolling / UI-only frames (dropped), hard cuts and duplicate frames (a 30 fps clip
    recorded at 60 fps shows every frame twice), and group frames into *stable spans* = one
    continuous clip each.  Timestamps come from the container per frame (variable fps safe).
 2. Pose pass per span: crop the tile at full resolution, find the golfer's bounding box with
    a few samples, re-crop tightly (small golfers), run the MediaPipe PoseLandmarker (.task
    model) on every unique frame.  Image-space landmarks (for detection) and world
    landmarks (for joint angles) are cached per span.
 3. `swing_segmentation.detect_swings` splits each span into address->finish windows from
    hand speed; windows run through `process_video.process_landmarks` -> joints; loop
    repeats are de-duplicated.  Output: data/references/<video stem>_sNN.npz.

Output keys = process_landmarks keys + source="mason_self_filmed", is_synthetic=False,
capture="screen_recording_of_social_feed", and per-swing quality / timing fields.
Nothing here touches the network.  Raw videos are git-ignored.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
try:
    from data import provenance as _prov
except ImportError:  # run as a script
    import provenance as _prov

try:
    from data import process_video as pv
    from data import swing_segmentation as ss
except Exception:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from data import process_video as pv
    from data import swing_segmentation as ss

SOURCE_LABEL = "mason_self_filmed"
CAPTURE_LABEL = "screen_recording_of_social_feed"
THUMB_W, THUMB_H = 118, 256
UPPER = [pv.R_SH, pv.R_EL, pv.R_WR, pv.R_HIP, pv.L_SH, pv.L_HIP]  # validity needs only these
KEY = [pv.R_SH, pv.R_EL, pv.R_WR, pv.R_HIP, pv.R_KNEE, pv.R_ANK, pv.L_SH, pv.L_HIP]
SKELETON = [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16), (11, 23), (12, 24), (23, 24),
            (23, 25), (25, 27), (24, 26), (26, 28), (27, 31), (28, 32)]


# ------------------------------------------------------------------------------ pass 1
def scan_layout(video: Path, max_frames: Optional[int] = None) -> Dict:
    """Decode once at low-res; return timestamps, tile rows, dup/cut flags, spans."""
    import cv2
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise IOError(f"cannot open {video}: HEVC needs an OpenCV/ffmpeg build with HEVC support; "
                      "else transcode: ffmpeg -i in.mov -c:v libx264 -crf 14 out.mp4 "
                      "(timestamps are preserved with -vsync passthrough)")
    ts: List[float] = []
    rows: List[Optional[Tuple[int, int]]] = []
    grays: List[np.ndarray] = []
    size = None
    try:
        while True:
            ok, f = cap.read()
            if not ok or (max_frames and len(ts) >= max_frames):
                break
            size = f.shape[:2]
            ts.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
            th = cv2.resize(f, (THUMB_W, THUMB_H), interpolation=cv2.INTER_AREA)
            r = ss.find_video_rows(th)
            rows.append(r)
            g = cv2.cvtColor(th, cv2.COLOR_BGR2GRAY)
            if r is not None:
                m = np.zeros_like(g)
                m[r[0]:r[1] + 1] = g[r[0]:r[1] + 1]
                g = m
            else:
                g = np.zeros_like(g)
            grays.append(g)
    finally:
        cap.release()
    if not ts:
        raise IOError(f"no frames decoded from {video}")
    t = np.asarray(ts)
    # POS_MSEC can repeat on some builds; fall back to a constant-rate clock if it does
    if np.any(np.diff(t) <= 0):
        t = np.arange(len(t)) / 60.0
    dup, cut = ss.frame_changes(np.stack(grays))
    spans = ss.stable_spans(rows, t, cut_flags=cut)
    return {"t": t, "rows": rows, "dup": dup, "cut": cut, "spans": spans, "size": size}


# ------------------------------------------------------------------------------ pose
class Landmarker:
    """MediaPipe tasks PoseLandmarker in IMAGE mode (re-detects every frame: robust to the
    motion blur of a downswing, at the cost of per-frame jitter that we smooth later)."""

    def __init__(self, model_path: str):
        import mediapipe as mp
        from mediapipe.tasks import python as mpt
        from mediapipe.tasks.python import vision
        if not Path(model_path).exists():
            raise RuntimeError(f"pose model not found: {model_path} (download pose_landmarker_heavy.task "
                               "from storage.googleapis.com/mediapipe-models/pose_landmarker/")
        self._mp = mp
        self._lm = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
            base_options=mpt.BaseOptions(model_asset_path=str(model_path)),
            running_mode=vision.RunningMode.IMAGE, num_poses=1))

    def __call__(self, bgr: np.ndarray) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        import cv2
        rgb = np.ascontiguousarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        res = self._lm.detect(self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb))
        if not res.pose_landmarks:
            return None
        img = np.array([[l.x, l.y, l.z, l.visibility] for l in res.pose_landmarks[0]])
        wld = np.array([[l.x, l.y, l.z, l.visibility] for l in res.pose_world_landmarks[0]])
        return img, wld

    def close(self):
        try:
            self._lm.close()
        except Exception:
            pass


def person_bbox(img_lm_px: List[np.ndarray], min_vis: float = 0.5, pad: float = 0.2,
                tile_wh: Tuple[int, int] = (1, 1), min_side: int = 256
                ) -> Optional[Tuple[int, int, int, int]]:
    """Union of confident landmarks (tile pixels) over sample frames -> padded (x0,y0,x1,y1).
    Falls back to None when nothing was seen."""
    pts = [a[a[:, 3] >= min_vis, :2] for a in img_lm_px if a is not None]
    pts = [p for p in pts if len(p)]
    if not pts:
        return None
    P = np.concatenate(pts)
    x0, y0 = P.min(0)
    x1, y1 = P.max(0)
    w, h = max(x1 - x0, 1), max(y1 - y0, 1)
    x0, x1 = x0 - pad * w, x1 + pad * w
    y0, y1 = y0 - pad * h, y1 + pad * h
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = max(x1 - x0, min_side), max(y1 - y0, min_side)
    W, H = tile_wh
    x0, x1 = max(0, cx - w / 2), min(W, cx + w / 2)
    y0, y1 = max(0, cy - h / 2), min(H, cy + h / 2)
    return int(x0), int(y0), int(x1), int(y1)


def track_span(frames_bgr: List[np.ndarray], lander, n_probe: int = 10) -> Dict:
    """Pose for every (unique) frame of one clip.  Returns arrays in *tile pixel* coords:
    img (n,33,4) [x_px, y_px, z, vis], world (n,33,4), bbox, tile_wh, detect_frac."""
    n = len(frames_bgr)
    H, W = frames_bgr[0].shape[:2]
    probe = np.linspace(0, n - 1, min(n_probe, n)).astype(int)
    seen = []
    for i in probe:
        r = lander(frames_bgr[i])
        if r is not None:
            seen.append(r[0] * np.array([W, H, 1, 1]))
    bbox = person_bbox(seen, tile_wh=(W, H))
    img = np.full((n, 33, 4), np.nan)
    wld = np.full((n, 33, 4), np.nan)
    if bbox is None:
        return {"img": img, "world": wld, "bbox": None, "tile_wh": (W, H), "detect_frac": 0.0}
    x0, y0, x1, y1 = bbox
    for i, f in enumerate(frames_bgr):
        r = lander(f[y0:y1, x0:x1])
        if r is None:
            continue
        a, w = r
        img[i] = np.column_stack([a[:, 0] * (x1 - x0) + x0, a[:, 1] * (y1 - y0) + y0, a[:, 2], a[:, 3]])
        wld[i] = w
    det = float(np.isfinite(img[:, pv.R_SH, 0]).mean())
    return {"img": img, "world": wld, "bbox": bbox, "tile_wh": (W, H), "detect_frac": det}


# ------------------------------------------------------------------------------ pass 2
def hand_track(img: np.ndarray, min_vis: float = 0.4):
    """Hands (mean of visible wrists), shoulder-mid y, hip-mid xy, median torso length (px)."""
    wr = img[:, [pv.L_WR, pv.R_WR]]
    ok = wr[..., 3] >= min_vis
    xy = wr[..., :2].copy()
    xy[~ok] = np.nan
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        hands = np.nanmean(xy, axis=1)
    sh = img[:, [pv.L_SH, pv.R_SH], :2].mean(1)
    hip = img[:, [pv.L_HIP, pv.R_HIP], :2].mean(1)
    torso = np.linalg.norm(sh - hip, axis=1)
    tl = float(np.nanmedian(torso)) if np.isfinite(torso).any() else float("nan")
    return hands, sh[:, 1], hip, tl


def resample_world(t: np.ndarray, lm: np.ndarray, fs: float, t0: float, t1: float
                   ) -> np.ndarray:
    """(n,33,4) irregular-time landmarks -> uniform grid at fs; NaN rows stay NaN where the
    nearest observation is further than 0.2 s."""
    tg = np.arange(t0, t1, 1.0 / fs)
    out = np.full((len(tg), 33, 4), np.nan)
    ok = np.isfinite(lm[:, pv.R_SH, 0])
    if ok.sum() < 2:
        return out
    tt = t[ok]
    near = np.abs(tg[:, None] - tt[None, :]).min(1) <= 0.2
    flat = lm[ok].reshape(ok.sum(), -1)
    for c in range(flat.shape[1]):
        col = flat[:, c]
        good = np.isfinite(col)
        if good.sum() >= 2:
            out.reshape(len(tg), -1)[:, c] = np.interp(tg, tt[good], col[good])
    out[~near] = np.nan
    return out


def _quality(img: np.ndarray, sl: slice, bbox, tile_wh) -> Dict:
    seg = img[sl]
    vis = seg[:, KEY, 3]
    good = np.isfinite(seg[:, KEY, 0]).all(1) & (np.nan_to_num(vis, nan=0) >= 0.5).all(1)
    H = tile_wh[1]
    bh = (bbox[3] - bbox[1]) if bbox else 0
    return {"valid_frame_ratio": round(float(good.mean()), 3),
            "mean_visibility": round(float(np.nanmean(vis)), 3) if np.isfinite(vis).any() else 0.0,
            "n_unique_frames": int(len(seg))}


def segment_span(track: Dict, t: np.ndarray, params: Optional[ss.SwingParams] = None,
                 min_clip_s: float = 1.0):
    """t: unique-frame timestamps (seconds) matching track arrays.  The clip is first split
    at pose jumps (autoplay-loop restarts / edits), then swings are detected per piece."""
    hands, sh_y, hip, tl = hand_track(track["img"])
    cuts = ss.pose_jump_cuts(track["img"][:, KEY, :2], tl)
    edges = [0, *[int(c) for c in cuts], len(t)]
    swings: List[ss.Swing] = []
    rejected: List[Dict] = []
    for a, b in zip(edges[:-1], edges[1:]):
        if t[b - 1] - t[a] < min_clip_s:
            continue
        sw, rj = ss.detect_swings(t[a:b], hands[a:b], sh_y[a:b], tl, params)
        swings += sw
        rejected += rj
    return swings, rejected, (hands, sh_y, hip, tl), [float(t[c]) for c in cuts]


def build_swing_npz(video_name: str, idx: int, sw: ss.Swing, track: Dict, t: np.ndarray,
                    aux, span_info: Dict, args) -> Tuple[Optional[Dict], Optional[str]]:
    sl = slice(int(np.searchsorted(t, sw.start_t)), int(np.searchsorted(t, sw.end_t, side="right")))
    lm = resample_world(t[sl], track["world"][sl], 60.0, sw.start_t, sw.end_t)
    try:
        data = pv.process_landmarks(lm, 60.0, min_visibility=args.min_visibility, max_gap=5,
                                    min_valid_frac=args.min_valid_frac, out_dt=args.out_dt, key=UPPER)
    except ValueError as e:
        return None, f"low_valid_frames: {e}"
    q = _quality(track["img"], sl, track["bbox"], track["tile_wh"])
    legs = track["img"][sl][:, [pv.L_KNEE, pv.R_KNEE, pv.L_ANK, pv.R_ANK], 3]
    leg_ratio = float((np.nan_to_num(legs, nan=0) >= args.min_visibility).all(1).mean())
    hands, sh_y, hip, tl = aux
    tile_h = track["tile_wh"][1]
    data.update(
        source=np.array(SOURCE_LABEL), style=np.array("mason"), is_synthetic=np.array(False),
        capture=np.array(CAPTURE_LABEL), source_file=np.array(video_name),
        swing_index=np.array(idx), view=np.array("unknown"), handedness=np.array(args.handedness),
        club=np.array("unknown"), leg_valid_frame_ratio=np.array(leg_ratio),
        legs_note=np.array("leg joints (cols 5-10) are interpolated/zero-filled where leg_valid_frame_ratio is low"), capture_fps=np.array(0.0),
        t_start_in_video=np.array(sw.start_t), t_end_in_video=np.array(sw.end_t),
        t_takeaway=np.array(sw.takeaway_t), t_top=np.array(sw.top_t), t_impact=np.array(sw.impact_t),
        tempo_ratio=np.array(sw.tempo), backswing_s=np.array(sw.backswing_s),
        downswing_s=np.array(sw.downswing_s), peak_hand_speed_torso_per_s=np.array(sw.peak_speed),
        valid_frame_ratio=np.array(q["valid_frame_ratio"]), mean_visibility=np.array(q["mean_visibility"]),
        torso_px=np.array(tl), torso_frac_of_tile_h=np.array(tl / tile_h),
        quality_flags=np.array(sw.flags, dtype=str),
        hands_px=np.column_stack([t[sl], hands[sl]]).astype(np.float32))
    return data, None


def process_video(video: Path, out_dir: Path, lander, args, debug_dir: Optional[Path] = None) -> Dict:
    import cv2
    t0 = time.time()
    lay = scan_layout(video, args.max_frames)
    t, spans, dup = lay["t"], lay["spans"], lay["dup"]
    H, W = lay["size"]
    rep: Dict = {"video": video.name, "frames": int(len(t)), "duration_s": round(float(t[-1]), 2),
                 "fps_mean": round(float((len(t) - 1) / (t[-1] - t[0])), 2),
                 "duplicate_frame_frac": round(float(dup.mean()), 3),
                 "frame_gap_max_s": round(float(np.diff(t).max()), 4),
                 "tile_frames_frac": round(float(np.mean([r is not None for r in lay["rows"]])), 3),
                 "spans": [], "swings": [], "rejected": [], "issues": []}
    cap = None if args.from_cache else cv2.VideoCapture(str(video))
    # spans are sorted; stream frames and buffer one span at a time (JPEG q95 keeps RAM small)
    buffers: Dict[int, List[Tuple[int, bytes]]] = {k: [] for k in range(len(spans))}
    bounds = [(s.start, s.end) for s in spans]
    k_of = np.full(len(t), -1)
    for k, (a, b) in enumerate(bounds):
        k_of[a:b + 1] = k
    swing_no = 0
    sigs: List[Tuple[str, np.ndarray]] = []
    cur = 0
    def flush(k: int):
        s = spans[k]
        items = buffers.pop(k)
        if len(items) < 8:
            return
        frames = [cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR) for _, b in items]
        fidx = np.array([i for i, _ in items])
        tt = t[fidx]
        track = track_span(frames, lander)
        info = {"span": k, "t0": round(float(t[s.start]), 2), "t1": round(float(t[s.end]), 2),
                "tile_rows_thumb": [s.top, s.bottom], "unique_frames": int(len(frames)),
                "detect_frac": round(track["detect_frac"], 3), "bbox": track["bbox"],
                "tile_wh": track["tile_wh"]}
        if args.cache_dir:
            Path(args.cache_dir).mkdir(parents=True, exist_ok=True)
            np.savez_compressed(Path(args.cache_dir) / f"{video.stem}_span{k:02d}.npz", t=tt,
                                img=track["img"].astype(np.float32), world=track["world"].astype(np.float32),
                                bbox=np.array(track["bbox"] or [0, 0, 0, 0]), tile_wh=np.array(track["tile_wh"]))
        analyse(k, tt, track, info, frames)

    def analyse(k, tt, track, info, frames):
        nonlocal swing_no
        if track["bbox"] is None or track["detect_frac"] < 0.4:
            info["status"] = "no_person_detected" if track["bbox"] is None else "person_intermittent"
            rep["spans"].append(info)
            return
        bh = (track["bbox"][3] - track["bbox"][1]) / track["tile_wh"][1]
        info["person_bbox_frac_of_tile_h"] = round(float(bh), 2)
        swings, rej, aux, jumps = segment_span(track, tt)
        info["pose_jump_cuts_at"] = [round(j, 2) for j in jumps]
        info["n_swings_detected"] = len(swings)
        info["status"] = "ok" if swings else "no_swing_found"
        info["torso_frac_of_tile_h"] = round(float(aux[3] / track["tile_wh"][1]), 3)
        for r in rej:
            rep["rejected"].append({"span": k, "t_in_video": round(float(r["t"]), 2), "reason": r["reason"]})
        for sw in swings:
            data, err = build_swing_npz(video.name, swing_no + 1, sw, track, tt, aux, info, args)
            if data is None:
                rep["rejected"].append({"span": k, "t_in_video": round(float(sw.impact_t), 2), "reason": err})
                continue
            sig = ss.trajectory_signature(aux[0][(tt >= sw.start_t) & (tt <= sw.end_t)],
                                          aux[2][(tt >= sw.start_t) & (tt <= sw.end_t)], aux[3])
            dup_of = next((nm for nm, sg in sigs if ss.is_duplicate(sig, sg)), None)
            if dup_of:
                rep["rejected"].append({"span": k, "t_in_video": round(float(sw.impact_t), 2),
                                        "reason": f"duplicate_of {dup_of} (autoplay loop / re-shown clip)"})
                continue
            swing_no += 1
            data["swing_index"] = np.array(swing_no)
            name = f"{video.stem}_s{swing_no:02d}"
            sigs.append((name, sig))
            if not args.dry_run:
                out = out_dir / f"{name}.npz"
                _prov.tag(data, "mason_self_filmed")
                tmp = out.with_name(out.stem + ".tmp.npz")
                np.savez(tmp, **data)
                tmp.replace(out)
            rep["swings"].append({
                "file": f"{name}.npz", "span": k, "t_start": round(sw.start_t, 2), "t_top": round(sw.top_t, 2),
                "t_impact": round(sw.impact_t, 2), "t_end": round(sw.end_t, 2),
                "tempo_ratio": None if not np.isfinite(sw.tempo) else round(float(sw.tempo), 2),
                "backswing_s": round(float(sw.backswing_s), 2), "downswing_s": round(float(sw.downswing_s), 2),
                "valid_frame_ratio": float(data["valid_frame_ratio"]), "process_valid_frac": round(float(data["valid_frac"]), 3),
                "mean_visibility": float(data["mean_visibility"]), "torso_frac_of_tile_h": round(float(data["torso_frac_of_tile_h"]), 3),
                "peak_hand_speed_torso_per_s": round(float(sw.peak_speed), 1), "flags": sw.flags,
                "leg_valid_frame_ratio": round(float(data["leg_valid_frame_ratio"]), 3), "output_frames_at_0.01s": int(len(data["time"]))})
            if debug_dir and frames is not None:
                _debug_sheet(debug_dir / f"{name}.jpg", frames, tt, track, sw)
        rep["spans"].append(info)

    if args.from_cache:
        for k, fn in enumerate(sorted(Path(args.from_cache).glob(f"{video.stem}_span*.npz"))):
            d = np.load(fn)
            track = {"img": d["img"].astype(float), "world": d["world"].astype(float),
                     "bbox": tuple(int(v) for v in d["bbox"]) if d["bbox"].any() else None,
                     "tile_wh": tuple(int(v) for v in d["tile_wh"]), "detect_frac": 0.0}
            track["detect_frac"] = float(np.isfinite(track["img"][:, pv.R_SH, 0]).mean())
            kk = int(fn.stem.rsplit("span", 1)[1])
            sp_ = spans[kk]
            info = {"span": kk, "t0": round(float(t[sp_.start]), 2), "t1": round(float(t[sp_.end]), 2),
                    "tile_rows_thumb": [sp_.top, sp_.bottom], "unique_frames": int(len(d["t"])),
                    "detect_frac": round(track["detect_frac"], 3), "bbox": track["bbox"], "tile_wh": track["tile_wh"]}
            analyse(kk, d["t"], track, info, None)
    try:
        i = 0
        while not args.from_cache and i < len(t):
            ok, f = cap.read()
            if not ok:
                rep["issues"].append(f"decoder stopped at frame {i}/{len(t)}")
                break
            k = int(k_of[i])
            if k >= 0 and not dup[i]:
                s = spans[k]
                y0 = int(round(s.top * H / THUMB_H))
                y1 = int(round((s.bottom + 1) * H / THUMB_H))
                ok2, jb = cv2.imencode(".jpg", f[y0:y1], [cv2.IMWRITE_JPEG_QUALITY, 95])
                buffers[k].append((i, jb.tobytes()))
            if k >= 0 and i == spans[k].end:
                flush(k)
            i += 1
    finally:
        if cap is not None:
            cap.release()
    rep["n_swings"] = len(rep["swings"])
    rep["elapsed_s"] = round(time.time() - t0, 1)
    return rep


def _debug_sheet(path: Path, frames, tt, track, sw: ss.Swing):
    import cv2
    path.parent.mkdir(parents=True, exist_ok=True)
    tiles = []
    for label, tm in (("start", sw.start_t), ("top", sw.top_t), ("impact", sw.impact_t), ("end", sw.end_t)):
        i = int(np.argmin(np.abs(tt - tm)))
        f = frames[i].copy()
        lm = track["img"][i]
        for a, b in SKELETON:
            if lm[a, 3] > 0.3 and lm[b, 3] > 0.3 and np.isfinite(lm[[a, b], :2]).all():
                cv2.line(f, tuple(int(v) for v in lm[a, :2]), tuple(int(v) for v in lm[b, :2]), (0, 255, 0), 3)
        if track["bbox"]:
            x0, y0, x1, y1 = track["bbox"]
            cv2.rectangle(f, (x0, y0), (x1, y1), (0, 128, 255), 2)
        f = cv2.resize(f, (360, int(360 * f.shape[0] / f.shape[1])))
        cv2.putText(f, f"{label} {tm:.2f}s", (6, 22), 0, 0.6, (0, 255, 255), 2)
        tiles.append(f)
    h = min(t.shape[0] for t in tiles)
    cv2.imwrite(str(path), np.hstack([t[:h] for t in tiles]))


# ------------------------------------------------------------------------------ CLI
def build_parser() -> argparse.ArgumentParser:
    root = Path(__file__).parent
    ap = argparse.ArgumentParser(description="feed screen-recording -> per-swing reference npz")
    ap.add_argument("--videos", type=Path, default=root / "mason_swings")
    ap.add_argument("--glob", default="*.mov")
    ap.add_argument("--out", type=Path, default=root / "references")
    ap.add_argument("--model", default=None, help="pose_landmarker_*.task")
    ap.add_argument("--cache-dir", type=Path, help="save raw pose tracks per span (scratch, not git)")
    ap.add_argument("--debug-dir", type=Path, help="write per-swing skeleton contact sheets")
    ap.add_argument("--report", type=Path, help="JSON report (default: <out>/mason_feed_report.json)")
    ap.add_argument("--handedness", default="right", choices=["right", "left"])
    ap.add_argument("--min-visibility", type=float, default=0.3,
                    help="MediaPipe leg/foot visibility is often 0.3-0.6 even when clearly visible")
    ap.add_argument("--min-valid-frac", type=float, default=0.6)
    ap.add_argument("--out-dt", type=float, default=0.01)
    ap.add_argument("--max-frames", type=int, help="debug: only first N frames")
    ap.add_argument("--from-cache", type=Path, help="skip pose: re-segment cached span tracks (layout is re-scanned)")
    ap.add_argument("--dry-run", action="store_true", help="analyse, write report only")
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    vids = sorted(args.videos.glob(args.glob)) if args.videos.exists() else []
    if not vids:
        print(f"No videos matching {args.glob} in {args.videos}")
        return 0
    args.out.mkdir(parents=True, exist_ok=True)
    try:
        lander = None if args.from_cache else Landmarker(str(args.model))
    except Exception as e:
        print(f"ERROR: cannot start MediaPipe PoseLandmarker: {e}\n"
              "  If it mentions libEGL.so.1: install libegl1 (or extract it from the .deb and set "
              "LD_LIBRARY_PATH).")
        return 1
    reports, failed = [], 0
    try:
        for v in vids:
            print(f"== {v.name}", flush=True)
            try:
                rep = process_video(v, args.out, lander, args, args.debug_dir)
                print(f"   swings={rep['n_swings']} spans={len(rep['spans'])} {rep['elapsed_s']}s", flush=True)
            except Exception as e:
                failed += 1
                rep = {"video": v.name, "error": f"{type(e).__name__}: {e}"}
                print(f"   FAILED: {e}", flush=True)
            reports.append(rep)
    finally:
        if lander:
            lander.close()
    rp = args.report or (args.out / "mason_feed_report.json")
    rp.write_text(json.dumps({"total_swings": sum(r.get("n_swings", 0) for r in reports),
                              "videos": reports}, indent=1, default=str))
    print(f"report: {rp}  total_swings={sum(r.get('n_swings', 0) for r in reports)}")
    return 0 if failed == 0 else 3


if __name__ == "__main__":
    sys.exit(main())
