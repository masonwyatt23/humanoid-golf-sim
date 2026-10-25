"""Convert MultiSenseGolf (Harvard Dataverse doi:10.7910/DVN/LCCLLW, CC0 1.0) inertial-mocap golf swings to
the project's reference .npz format, reusing the CMU converter's joint / event logic.

Only the `pns-joint-root-relative-position` stream of each `P??_Swing??_stream_data.hdf5` is used (21-joint
Perception Neuron Studio skeleton, cm, Y-up, +X = subject's left, +Z = facing). No video is read.

    python -m data.convert_multisense_golf --raw-dir <local-path>/multisense \
        --participants P19 P20 P22 --top-n 10 --min-club-mph 85

Output: data/references/multisense_<Pxx>_s<NN>.npz  (license-tagged `multisensegolf_needs_counsel`: published CC0, needs_counsel, commercial_ok=False).
Missing vs CMU: no finger/toe joints -> wrist-hinge (col 3) and ankle (cols 7, 10) are not measured and are
written as 0 with qc flag `wrist_ankle_not_measured`. Launch-monitor club/ball speed and carry are stored as
metadata (not club-head trajectories). All 24 participants swing right-handed (Participant Metadata.csv).
"""
from __future__ import annotations

import os
import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data import convert_cmu_mocap as cm  # noqa: E402
from data import provenance as prov  # noqa: E402

JOINTS = ["Hips", "RightUpLeg", "RightLeg", "RightFoot", "LeftUpLeg", "LeftLeg", "LeftFoot", "Spine", "Spine1",
          "Spine2", "Neck", "Neck1", "Head", "RightShoulder", "RightArm", "RightForeArm", "RightHand",
          "LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand"]
MPS_TO_MPH = 2.23694
DOI = "10.7910/DVN/LCCLLW"


def load_positions(h5path: Path):
    import h5py
    with h5py.File(h5path, "r") as h:
        g = h["pns-joint-root-relative-position/cm-values"]
        P = g["data"][:].astype(float).reshape(-1, 21, 3) / 100.0           # metres
        t = g["time_s"][:, 0].astype(float)
    t = t - t[0]
    keep = np.concatenate([[True], np.diff(t) > 1e-4])          # some files have repeated / out-of-order stamps
    keep &= np.maximum.accumulate(t) == t
    return t[keep], P[keep]


def to_named(P: np.ndarray) -> Dict[str, np.ndarray]:
    d = {n: P[:, i] for i, n in enumerate(JOINTS)}
    d["Head_end"] = d["Head"]
    # finger / toe proxies so cm.compute_joints runs; the columns that depend on them are zeroed later
    for s in ("Right", "Left"):
        d[f"{s}HandIndex1"] = d[f"{s}Hand"] + (d[f"{s}Hand"] - d[f"{s}ForeArm"]) * 0.3
        d[f"{s}ToeBase"] = d[f"{s}Foot"] + np.array([0.0, 0.0, 0.1])
    return d


def convert_swing(h5path: Path, meta: Dict, hand: str = "right", fs: float = 100.0) -> Dict:
    t, P = load_positions(h5path)
    if np.any(np.diff(t) <= 0):
        raise cm.CmuConvertError("non-monotonic timestamps")
    tu = np.arange(0, t[-1], 1.0 / fs)
    Pu = np.stack([np.column_stack([np.interp(tu, t, P[:, j, k]) for k in range(3)]) for j in range(21)], axis=1)
    N = to_named(Pu)
    c = cm.compute_joints(N, fs, hand)
    ev = cm.detect_events(c["hands"], fs)
    n = len(tu)
    i0 = max(0, ev["takeaway"] - int(0.25 * fs)); i1 = min(n - 1, ev["finish"] + int(0.25 * fs))
    sl = slice(i0, i1 + 1)
    addr_i = slice(i0, max(ev["takeaway"], i0 + 3))
    pel = cm._yaw(c["pel_line"]); pel = pel - pel[addr_i].mean()
    pel = pel if pel[ev["top"]] < 0 else -pel
    tho = cm._yaw(c["tho_line"]); tho = tho - tho[addr_i].mean()
    tho = tho if tho[ev["top"]] < 0 else -tho
    tgt = c["pel_line"][addr_i].mean(axis=0); tgt[1] = 0; tgt = tgt / (np.linalg.norm(tgt) + 1e-12)
    sway = np.sum((c["hip_c"] - c["hip_c"][addr_i].mean(axis=0)) * tgt, -1)
    joints = c["joints"].copy()
    joints[:, [3, 7, 10]] = 0.0                                   # wrist/ankle not measured
    dt = 0.01
    t_src = np.arange(i1 - i0 + 1) / fs
    cut = lambda x: np.asarray(x)[sl]
    ts = np.arange(0, t_src[-1] + 1e-9, dt)
    rs = lambda x: np.interp(ts, t_src, x) if np.ndim(x) == 1 else np.column_stack([np.interp(ts, t_src, x[:, k]) for k in range(x.shape[1])])
    ev_s = np.array([(ev["top"] - i0) / fs, (ev["impact"] - i0) / fs]); take_s = (ev["takeaway"] - i0) / fs
    bs, ds = ev_s[0] - take_s, ev_s[1] - ev_s[0]
    tempo = bs / ds if ds > 0 else float("nan")
    flags = ["wrist_ankle_not_measured"]
    if not (1.5 <= tempo <= 5.5): flags.append(f"tempo_out_of_range:{tempo:.2f}")
    if not (0.12 <= ds <= 0.6): flags.append(f"downswing_s_out_of_range:{ds:.2f}")
    if ev["peak_hand_speed"] < 4.0: flags.append(f"low_hand_speed:{ev['peak_hand_speed']:.1f}")
    pn = meta["participant"]
    out = {
        "time": ts, "joints": rs(cut(joints)), "joints_rad": np.deg2rad(rs(cut(joints))),
        "pelvis_rot_deg": rs(cut(pel)), "thorax_rot_deg": rs(cut(tho)), "x_factor_deg": rs(cut(pel - tho)),
        "lateral_sway_m": rs(cut(sway)), "wrist_hinge_deg": np.zeros_like(ts),
        "events": ev_s, "takeaway_s": np.array(take_s), "finish_s": np.array((ev["finish"] - i0) / fs),
        "tempo_ratio": np.array(tempo), "peak_hand_speed_mps": np.array(ev["peak_hand_speed"]),
        "dt": np.array(dt), "source_fps": np.array(1.0 / np.mean(np.diff(t))),
        "source": np.array("multisensegolf"), "is_synthetic": np.array(False), "has_club_head": np.array(False),
        "style": np.array(f"multisense_{pn}"), "subject": np.array(pn), "trial": np.array(meta["swing"]),
        "trial_id": np.array(f"{pn}_{meta['swing']:02d}"), "handedness": np.array(hand),
        "source_file": np.array(h5path.name), "qc_flags": np.array(flags, dtype="U64"),
        "joint_columns": np.array(cm.JOINT_COLUMNS), "capture": np.array("inertial_mocap_perception_neuron_studio"),
        "view": np.array("3d"), "skill_self_report_1to7": np.array(meta["skill"]),
        "club_speed_mph_launch_monitor": np.array(meta["club_mph"]), "ball_speed_mps": np.array(meta["ball_mps"]),
        "carry_m": np.array(meta["carry_m"]), "launch_monitor_note": np.array(
            "Optical launch monitor club speed at impact; the club head is not tracked in this .npz"),
        "mirrored": np.array(False),
    }
    prov.tag(out, "multisensegolf_needs_counsel", overwrite=True)
    return out


def read_meta(raw: Path):
    ann = list(csv.DictReader(open(raw / "Annotation Data.csv", encoding="utf-8-sig")))
    part = {r["Participant Number"]: r for r in csv.DictReader(open(raw / "Participant Metadata.csv", encoding="utf-8-sig"))}
    return ann, part


def fnum(x):
    try:
        return float(x)
    except Exception:
        return float("nan")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", type=Path, default=None, help="raw MultiSense dir (default: $GOLF_SCRATCH_DIR/multisense)")
    ap.add_argument("--out", type=Path, default=Path(__file__).parent / "references")
    ap.add_argument("--participants", nargs="+", default=["P19", "P20", "P22"])
    ap.add_argument("--top-n", type=int, default=10, help="keep this many highest club-speed swings per participant")
    ap.add_argument("--min-club-mph", type=float, default=85.0)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if a.raw_dir is None:
        a.raw_dir = Path((os.environ.get("GOLF_SCRATCH_DIR") or sys.exit("set GOLF_SCRATCH_DIR (local scratch dir with the raw/cached data) or pass the path explicitly"))) / "multisense"
    ann, part = read_meta(a.raw_dir)
    rep: List[Dict] = []
    for p in a.participants:
        num = int(p[1:])
        rows = [r for r in ann if int(r["Participant Number"]) == num]
        hdfs = {int(f.stem.split("Swing")[1].split("_")[0]): f for f in (a.raw_dir / p).glob("Swing*/*.hdf5")}
        cand = []
        for r in rows:
            s = int(r["Swing Number"])
            if s in hdfs and np.isfinite(fnum(r["Club Speed (m/s)"])):
                cand.append((fnum(r["Club Speed (m/s)"]) * MPS_TO_MPH, s, r))
        cand = [c for c in sorted(cand, key=lambda c: -c[0]) if c[0] >= a.min_club_mph][: a.top_n]
        for mph, s, r in sorted(cand, key=lambda c: c[1]):
            meta = dict(participant=p, swing=s, skill=int(part[p]["Self-Reported Expertise Level (7-Likert)"]),
                        club_mph=mph, ball_mps=fnum(r["Ball Speed (m/s)"]), carry_m=fnum(r["Carry Distance (m)"]))
            try:
                d = convert_swing(hdfs[s], meta, hand=part[p]["Swing Handedness"].strip().lower())
            except Exception as e:
                rep.append({"file": f"multisense_{p}_s{s:02d}.npz", "error": str(e)}); continue
            name = f"multisense_{p}_s{s:02d}.npz"
            if not a.dry_run:
                np.savez(a.out / name, **d)
            rep.append({"file": name, "club_mph": round(mph, 1), "carry_m": meta["carry_m"], "tempo": round(float(d["tempo_ratio"]), 2),
                        "peak_hand_mps": round(float(d["peak_hand_speed_mps"]), 1), "frames": int(len(d["time"])),
                        "flags": [str(f) for f in d["qc_flags"]]})
    if not a.dry_run:
        (a.out / "multisense_conversion_report.json").write_text(json.dumps(rep, indent=1))
    for r in rep: print(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
