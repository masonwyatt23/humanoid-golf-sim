# Mason feed screen-recordings: swing extraction report

Generated 2026-10-16 from `data/mason_swings/mason_swing_part{1,2,3}.mov` (Mason's own Instagram feed,
phone screen recordings, HEVC 1180x2556 portrait, 60 fps nominal). Raw videos are git-ignored.

## What the recordings actually are
Not one-swing-per-file: each is a scroll through ~10-15 posts (part1 10 clips, part2 15, part3 13), each
a different short clip (2-14 s, many autoplay-looped) wrapped in Instagram UI (status bar, header, like/boost
rows). Different scenes, range/mat/backyard, different camera angles and subject sizes. Duplicate frames:
46% / 61% / 75% of frames (source clips are ~30 / 23 / 15 fps unique, recorded at 60). Timestamps are read
per frame from the container (variable-fps safe; max gap 18 ms, 33 ms once in part3).

## Pipeline (code)
- `data/swing_segmentation.py` - numeric core + tests (`tests/test_swing_segmentation.py`, 14 tests):
  video-tile finder for the dark UI, scroll/cut/duplicate-frame detection, stable spans, pose-jump (loop restart)
  detector, hand-speed swing detector (takeaway/top/impact/finish, tempo), loop de-duplication.
- `data/ingest_feed_recordings.py` - CLI: layout pass -> per-clip tight person crop -> MediaPipe PoseLandmarker
  (heavy `.task`, IMAGE mode) -> swing windows -> `process_video.process_landmarks` -> `<stem>_sNN.npz`.
  `--from-cache` re-segments saved tracks without re-running pose.
- `data/refine_swings.py` - second pass for chosen swings (best-of-3 detections per frame: tight crop, upscaled
  crop, whole tile; torso-consistency check; rolling-median outlier rejection; cut at pose jumps) ->
  `<stem>_sNN_refined.npz`; `--rejoint` recomputes joints from stored landmarks.
- `data/process_video.py` fixes: `key=` validity set (upper body is enough; legs flagged separately) and shoulder
  angle unwrap (smoothing across the +-180 wrap produced +-200 deg artefacts; 0 now = arm hanging).
- Environment: system lacked `libEGL.so.1` (MediaPipe tasks needs it, no root). I extracted `libegl1/libglvnd0/
  libgles2` debs into `<local-path>/golf_scratch/libroot` and set `LD_LIBRARY_PATH`. Model:
  `pose_landmarker_heavy.task` (official storage.googleapis.com/mediapipe-models), in `<local-path>/golf_scratch/`.
  HEVC decoded natively by OpenCV (no transcode needed).

## Swing counts (first pass, `data/references/mason_swing_partN_sNN.npz`, untracked)
| Video | Duration | Clips (spans) | Clips with swings | Swings kept | Rejected candidates |
|---|---|---|---|---|---|
| mason_swing_part1.mov | 70.97 s | 10 | 7 | 7 | 2 |
| mason_swing_part2.mov | 88.4 s | 15 | 5 | 5 | 6 |
| mason_swing_part3.mov | 111.96 s | 13 | 4 | 3 | 5 |
| **Total** | | | | **15** | |

## Per-swing quality (first pass)
`vfr` = frames with all 8 key landmarks >=0.5 vis; `legs` = knees+ankles visible; tempo = backswing:downswing (hand-speed peak as impact proxy).

| File | t in video (s) | tempo | mean vis | upper valid | legs | score | flags |
|---|---|---|---|---|---|---|---|
| mason_swing_part1_s05.npz | 37.29-39.97 | 3.5 | 0.784 | 0.795 | 0.575 | 0.79 | - |
| mason_swing_part2_s02.npz | 19.75-22.47 | 3.22 | 0.8 | 0.779 | 0.543 | 0.78 | - |
| mason_swing_part2_s05.npz | 81.52-83.48 | 2.9 | 0.774 | 0.619 | 0.538 | 0.74 | - |
| mason_swing_part1_s02.npz | 12.89-14.79 | 3.22 | 0.727 | 0.617 | 0.561 | 0.74 | - |
| mason_swing_part2_s01.npz | 14.8-17.67 | 3.0 | 0.767 | 0.74 | 0.188 | 0.73 | - |
| mason_swing_part1_s03.npz | 18.82-20.9 | 2.21 | 0.739 | 0.696 | 0.368 | 0.73 | - |
| mason_swing_part1_s04.npz | 26.32-28.44 | 2.55 | 0.72 | 0.622 | 0.298 | 0.69 | - |
| mason_swing_part1_s06.npz | 56.24-58.08 | 2.9 | 0.719 | 0.709 | 0.323 | 0.67 | little_address_before_takeaway |
| mason_swing_part2_s04.npz | 45.21-47.33 | None | 0.922 | 0.969 | 0.667 | 0.66 | tempo_out_of_range(0.09), little_address_before_takeaway, clipped_follow_through |
| mason_swing_part1_s01.npz | 2.67-4.2 | 1.4 | 0.854 | 0.87 | 0.717 | 0.65 | little_address_before_takeaway |
| mason_swing_part1_s07.npz | 61.72-64.18 | None | 0.829 | 0.905 | 0.405 | 0.60 | tempo_out_of_range(0.73), clipped_follow_through |
| mason_swing_part3_s03.npz | 55.31-56.68 | None | 0.72 | 0.817 | 0.088 | 0.52 | phase_too_short_for_tempo, clipped_follow_through |
| mason_swing_part3_s02.npz | 43.34-44.76 | None | 0.662 | 0.635 | 0.2 | 0.47 | tempo_out_of_range(0.47), clipped_follow_through |
| mason_swing_part3_s01.npz | 23.94-24.99 | None | 0.713 | 0.73 | 0.259 | 0.46 | phase_too_short_for_tempo, little_address_before_takeaway, clipped_follow_through |
| mason_swing_part2_s03.npz | 23.74-24.89 | 5.0 | 0.689 | 0.623 | 0.447 | 0.45 | little_address_before_takeaway, tracking_gaps_in_window |

## Refined swings (`*_refined.npz`, tracked in git)
| File | Frames | Score | Tempo | Mean vis | Upper valid | Legs | Outlier frac | Flags |
|---|---|---|---|---|---|---|---|---|
| mason_swing_part1_s02_refined.npz | 169 | 0.79 | 2.7 | 0.81 | 0.84 | 0.65 | 0.004 | - |
| mason_swing_part1_s03_refined.npz | 187 | 0.78 | 2.21 | 0.79 | 0.88 | 0.62 | 0.005 | - |
| mason_swing_part1_s04_refined.npz | 194 | 0.78 | 3.0 | 0.79 | 0.87 | 0.64 | 0.000 | - |
| mason_swing_part1_s05_refined.npz | 266 | 0.86 | 3.18 | 0.85 | 0.93 | 0.83 | 0.000 | - |
| mason_swing_part1_s06_refined.npz | 187 | 0.78 | 2.55 | 0.81 | 0.89 | 0.70 | 0.003 | little_address_before_takeaway |
| mason_swing_part2_s01_refined.npz | 261 | 0.80 | 3.1 | 0.81 | 0.92 | 0.57 | 0.002 | - |
| mason_swing_part2_s02_refined.npz | 232 | 0.75 | 3.33 | 0.83 | 0.94 | 0.68 | 0.004 | trimmed_at_pose_jump(19.55-22.47s) |
| mason_swing_part2_s05_refined.npz | 177 | 0.77 | 3.1 | 0.80 | 0.86 | 0.62 | 0.001 | - |
| mason_swing_part3_s02_refined.npz | 132 | 0.51 | - | 0.66 | 1.00 | 0.18 | 0.004 | tempo_out_of_range(0.47), clipped_follow_through |
| mason_swing_part3_s03_refined.npz | 154 | 0.61 | - | 0.75 | 1.00 | 0.34 | 0.006 | phase_too_short_for_tempo, clipped_follow_through |
(`Upper valid` in the refined table is measured after the stored landmarks were gap-filled, so it reads a little
higher than the first-pass column. `Legs` = fraction of frames with both knees and ankles visible >= 0.3.)

## Video ranking
| Rank | Video | Why |
|---|---|---|
| 1 | **part1** | Every post is a landscape tile with the full body visible (torso ~15-21% of tile height), tile found in 100% of frames, 7 swings kept (mean score 0.70, best 0.79 first pass / 0.86 refined), highest unique frame rate (~33 fps), no night scenes. Best single swing: `part1_s05` (refined 0.86). |
| 2 | **part2** | Same style of posts but a carousel swipe and several short/odd clips; tile found in 81% of frames, 5 swings kept (mean 0.67), 2 clips had no person detected / person intermittent, one "1/2" carousel overlay. `part2_s01` refined (0.80) is the second-best swing overall. |
| 3 | **part3** | Closest framing (torso 19-29% of tile; legs often cut off -> legs 0.1-0.3), mostly 1-2 s clips, ~15 fps unique frames (75% duplicates), a night/silhouette section where the dark-UI tile finder fails (tile found in only 46% of frames), 3 swings kept, none with a measurable tempo (mean score 0.48). |

## Issues found (be sceptical of the numbers)
- **UI overlays:** status bar, header, like/boost rows are cropped out by the tile finder; remaining overlays inside
  the tile (mute icon, `0:05` timer, `1/2` carousel badge) never overlapped a landmark in the sheets I viewed.
  Carousel swipes show a sliver of the next slide at the tile edge (visible in `part2_s04` end frames).
- **Tile finder is dark-UI based:** night/very dark footage (end of part3, ~92-111 s) is not recognised as a tile, so
  those swings were not processed. Fixing needs a layout model that does not rely on brightness.
- **Loops and edits:** many posts autoplay-loop or are edited; the swing window is cut at pose jumps so some
  windows start mid-backswing (`little_address_before_takeaway`) and the same swing seen twice is de-duplicated by
  trajectory similarity (threshold uncalibrated). Some clips look slow-motion; tempo *ratio* survives that, absolute
  durations do not.
- **Tempo reliability:** from ~30 fps (or 15 fps in part3) screen-recorded source frames, one frame = ~12-25% of a
  downswing, so tempo is +-15% at best; impact is approximated by peak hand speed. Tempo 1.4 (`part1_s01`) and 5.0
  (`part2_s03`) are implausible and should be ignored; `tempo_ratio` is NaN when out of 1-6 or phases < 0.1 s.
  Refined swings with tempo 2.2-3.3 are plausible for an amateur but not measured against ground truth.
- **View angle:** every clip is a single hand-held/tripod view of unknown angle (some look face-on, some DTL,
  some oblique); `view` is `unknown`. Joint angles are 2D-image-plane proxies built from MediaPipe world
  landmarks, so shoulder/wrist angles depend on the camera angle.
- **Handedness:** assumed right-handed (Mason); not verified per clip.
- **Small subject:** torso is 15-21% of tile height; tight-crop/upscale re-detection never beat whole-tile
  detection in the refinement stage (frames chosen: native crop 13-35, upscaled 0, whole tile 16-84 per swing),
  i.e. MediaPipe heavy already handles this size; the refinement gain came from outlier rejection, gap handling and
  choosing the best of three detections, not from upscaling.
- **Rejected candidates:** `no_backswing_before_peak` (loop jumps / partial motion), `hands_not_above_shoulder`
  (chips/waggles/short clips), `low_valid_frames` (< 60% upper-body tracked), and duplicates; see the JSON report.
- **Not verified:** I viewed skeleton overlays for 11 swings (first-pass sheets for 4, refined sheets for 5, none for
  part3); they tracked the golfer well. Hand-speed "impact" is not independently confirmed. No ground truth.

## Retargeting limits (honest)
These are Mason's swings (not Adam Scott), single view, 2D-proxy angles (0 = arm hanging along torso for shoulder
pitch; other joints are interior-angle proxies), no club/ball, no pelvis/thorax rotation, no roll/yaw. They are
suitable for sanity-checking tempo and gross joint ranges (compare against `joint_min/max`), not for direct
imitation of the MuJoCo humanoid without retargeting (WHAM/GVHMR + IK, see docs/WHAM_GVHMR.md). Frames-per-second
of the stored `joints` is 100 Hz after resampling from ~30 fps unique source frames.

## Output paths
- Refined (tracked): `data/references/mason_swing_part{1,2,3}_sNN_refined.npz` (10 files; see docs/REFERENCE_PATHS.md)
- First pass, all 15 swings (untracked): `data/references/mason_swing_partN_sNN.npz`
- Report JSON: `data/references/mason_feed_report.json`
- Scratch (not in git): `<local-path>/golf_scratch/{cache,out2,refined,refined_debug,debug,dbg}` (pose tracks, skeleton sheets)

## Reproduce
```
export LD_LIBRARY_PATH=<local-path>/golf_scratch/libroot/usr/lib/x86_64-linux-gnu   # if libEGL.so.1 is missing
source <local-path>/golfvenv/bin/activate
python -m data.ingest_feed_recordings --model <local-path>/golf_scratch/pose_landmarker_heavy.task \
    --cache-dir <local-path>/golf_scratch/cache --debug-dir <local-path>/golf_scratch/debug      # ~7 min
python -m data.refine_swings --report data/references/mason_feed_report.json \
    --video data/mason_swings/mason_swing_part1.mov --model <local-path>/golf_scratch/pose_landmarker_heavy.task \
    --cache-dir <local-path>/golf_scratch/cache --top 5
```
## Next
Film 20-50 two-view 240 fps swings (docs/MASON_SWINGS.md) or export original files from the phone (not feed
recordings): that fixes fps, view, tempo accuracy, and lets WHAM/GVHMR run properly.


---
# v2 re-mine (2026-10-16): dropped swings, camera view, handedness from the footage

Code: `data/remine_feed_v2.py` (+ `tests/test_remine_feed_v2.py`). Outputs `data/references/mason_v2_*.npz`,
report `data/references/mason_v2_report.json` (per chunk, per swing, every drop reason). Tracks cached in
`<local-path>/golf_scratch/cache_v2/` (scratch, not git).

## What changed vs the first pass
- **Layout-agnostic chunking.** The v1 tile finder is brightness-based and found a tile in only 46% of part3 frames.
  v2 crops a fixed media band (y 9-86% of the frame), splits clips at hard cuts (frame-diff > 15) and runs pose on every
  unique frame of every chunk >= 0.8 s (part1 10 chunks, part2 13, part3 18; 41 chunks). Pose detected in >= 93% of frames
  in every chunk.
- **Relaxed detector** (`peak_speed 3.5` vs 5, hands need only reach the shoulder line, min phase 0.08 s) plus rolling-median
  outlier rejection on the raw tracks, `min_valid_frac 0.5` (swings 0.5-0.6 are written with flag
  `upper_valid_frac_below_0.6` and never `recommended`).
- **Partial swings** (loop restarts / clips that start at the downswing) are kept as `*_partial.npz`: window = 1.2 s before to
  1.0 s after the hand-speed peak, no tempo, quality capped at 0.5, never recommended.
- **Dark section of part3 (~92-112 s):** re-tracked with gamma+CLAHE enhancement (`--enhance`). Pose is found (detect 0.93-0.96) but
  the silhouettes are too poor: all three night swing candidates (99.9-102.2 s, 109.6-111.1 s, partial at 105.3 s) still fail the
  validity gate (34-47% of frames have the upper body at visibility >= 0.3). **Night swings are not recoverable with this model.**
- Result: 28 full swings + 5 partials written (v1: 15 first-pass). 13 of the full swings overlap a v1 swing (same swing, re-cut,
  recorded in `v1_overlap`); the rest are new or previously rejected (`low_valid_frames`, `no_backswing`).

## Camera view per swing (`view`, `view_confidence`, `shoulder_width_ratio`, `stance_ratio`)
Heuristic from the pose at address (0.6 s before takeaway): image distance between the shoulders divided by torso length.
face-on >= 0.8, down-the-line <= 0.35, else `oblique`. Thresholds were set by looking at frames of 6 clips, not fitted to labels.
Counts (33 swing files, excluding the un-mirrored copy): down-the-line 20, oblique 8, face-on 5. The only usable **face-on left-handed** swing is
`mason_v2_p1_s11` (part1 68-70 s). Most of Mason's feed is down-the-line.

## Handedness detected from the footage (`handedness`, `handedness_detected`, `handedness_confidence`, `handedness_verified`)
Two voting cues using the pose model's anatomical left/right labels: (A) the *lead arm* at the top of the backswing is the
straighter one (only when a real backswing exists), (C) at the finish the hands end nearer the *lead* shoulder. A third cue
(face-on hand side at the top) is recorded but not voted: it contradicted the others when the torso turns away from the camera.
Findings:
- **18 clips are verified left-handed** (confidence >= 0.5, no cue in conflict; 11 of them have both cues, the rest only the lead-arm or only the finish cue; e.g. `p1_s03/04/06`, `p2_s01/02/11/13`): the footage independently
  supports left-handed. Right arm straighter at the top (elbow ~125-140 deg vs left ~85-115 deg).
- `handedness_verified=False` where cues conflict or only one cue exists (face-on `p1_s11`, `p2_s10`, night/close-up clips). For those
  `handedness` falls back to the stated value `left`. I checked `p1_s11` by eye: the rear foot (heel up) is on the image right while
  facing the camera, i.e. the target is image-left: left-handed.
- **4 clips read right-handed** and carry no mirror caption: `p2_s05` (pink shirt), `p2_s08` (striped shirt), `p3_s08`
  (gray tee, backyard), `p3_s01_partial`. They are either another golfer on Mason's feed or flipped edits. They are tagged
  `license_class=unknown, commercial_ok=False` (not asserted self-owned) and `recommended=False`.
- **`p3_s09` (87-89 s) reads right-handed with confidence 0.96, and the post carries the on-screen caption "What my swing would
  look like if I was right handed"**: a mirror-flipped edit of a left-handed swing. The detector independently flagged it. I wrote
  `mason_v2_p3_s09_unmirrored.npz` (mirrored back with `data/mirror_references.py`, `mirrored=True`, `handedness=left`,
  `native_footage=False`). Quality 0.83 is the highest of the set (close-up, daylight, DTL) but legs are only 0.19 tracked.
- Limits: a clip that was flipped by the camera app before posting (no caption) would read the opposite hand and cannot be told
  apart by pose alone. I cannot verify the identity of the person in a clip; the feed is Mason's account and the clothes differ across
  years (and some clips may be students/friends). v1 treated everything as Mason.

## Joint-column convention (important for left-handed footage)
`joints` columns are named `right_*` but are computed from the **anatomical** right arm/leg. For a left-handed golfer that is the
**lead** arm (right-handed CMU / MultiSense files: `right_*` = trail arm, by the CMU converter's convention). Every v2 file carries
`joint_convention`. Native-left v2 files need no mirroring to represent a left-handed swing; do not feed them to a loader that
also mirrors them (`mirrored=False` for native, `True` only for `_unmirrored`).

## Selection (`recommended=True`, 11 files, all full swings, quality >= 0.65, valid tempo, upper-valid >= 0.6, no handedness conflict)
| File | Source @ s | View | Tempo | Quality | Legs tracked | Note |
|---|---|---|---|---|---|---|
| `mason_v2_p1_s06.npz` | part1 37.3-40.0 | oblique | 3.5 | 0.76 | 0.57 | = v1 `part1_s05` (best v1 swing) |
| `mason_v2_p1_s11.npz` | part1 68.0-70.4 | **face-on** | 3.6 | 0.76 | 0.69 | new; address then cut to follow-through in the post, handedness unverified (cues conflict) |
| `mason_v2_p2_s02.npz` | part2 19.8-22.5 | DTL | 3.6 | 0.75 | 0.53 | verified left, both cues |
| `mason_v2_p2_s01.npz` | part2 14.8-17.7 | DTL | 2.9 | 0.70 | 0.22 | verified left |
| `mason_v2_p1_s04.npz` | part1 18.8-20.9 | DTL | 2.2 | 0.69 | 0.37 | verified left |
| `mason_v2_p1_s03.npz` | part1 12.9-14.8 | DTL | 3.2 | 0.69 | 0.49 | verified left |
| `mason_v2_p2_s13.npz` | part2 86.6-88.2 | DTL | 3.8 | 0.68 | 0.31 | new, little address |
| `mason_v2_p2_s10.npz` | part2 72.3-74.3 | DTL | 2.9 | 0.68 | 0.26 | new, handedness unverified |
| `mason_v2_p1_s05.npz` | part1 26.3-28.6 | DTL | 2.9 | 0.66 | 0.24 | verified left |
| `mason_v2_p2_s11.npz` | part2 76.6-78.2 | DTL | 2.8 | 0.66 | 0.34 | new, clipped follow-through |
| `mason_v2_p3_s09_unmirrored.npz` | part3 87.1-89.3 | DTL | 2.9 | 0.83 | 0.19 | un-mirrored caption clip; highest quality score |
The scores come from the same 0-1 heuristic as v1 (`refine_swings.quality_score`); the raw (unrefined-by-re-detection) v2 scores are
a little lower than v1 `_refined` for the same swing because v2 does not run the best-of-3 re-detection. Use v1 `_refined` or v2
interchangeably for overlapping swings; do not train on both (double counting).

## Still wrong / not done
- Tempo is still +-15% (30 fps or lower unique source frames); `p1_s01` (4.75) and `p2_s03` (4.88) are implausible.
- No ground truth: view and handedness thresholds were checked by eye on ~10 clips, not on a labelled set.
- Night swings not recoverable; 16 low-validity / duplicate candidates remain dropped (`mason_v2_report.json`).
- Joints are still 2D-proxy angles, not retargeted/IK-fitted.

## Reproduce
```
export LD_LIBRARY_PATH=<local-path>/golf_scratch/libroot/usr/lib/x86_64-linux-gnu; source <local-path>/golfvenv/bin/activate
python -m data.remine_feed_v2 --stage track  --model <local-path>/golf_scratch/pose_landmarker_heavy.task   # ~6 min per all 3 videos
python -m data.remine_feed_v2 --stage track --only part3 --chunks 16,17 --enhance                         # night re-track
python -m data.remine_feed_v2 --stage swings                                                               # seconds, from cache
```

## v3: effective frame rate, slow-motion clips, face-on (2026-10-16)
Question: does any part of the three recordings have a higher effective fps (more unique frames per second, or slowed motion) that
would pin down the downswing better than the ~5 frames of the v2 swings?

### 1. Cadence audit (`python -m data.audit_feed_cadence` -> `data/references/mason_cadence_audit.json`)
Method: decode every frame (media band, 236x394 gray), unique frame = mean abs diff to previous >= 0.1 grey levels (duplicates measure
0.00-0.05, real frames >= 0.5; histogram is cleanly bimodal). Per swing window: unique fps, median unique interval, unique frames in
backswing / downswing.
- All three are 60 fps containers of a **30 fps** player: overall unique-frame fraction 0.57 / 0.52 / 0.52 (the rest is scroll/transition).
  Every swing window is **29-31 fps unique** (strictly alternating unique/duplicate, median interval 33 ms); a few windows read 34-38 fps
  only because a scroll/transition animation (17 ms steps) overlaps the window edge (p2_s03, p1_s07, p1_s10_partial). `p3_s09` (the
  caption-flipped edit) is 15 fps (67 ms interval). **No segment has more than ~30 true unique fps; nothing at 60.** Sliding 1 s windows
  confirm: max 34 unique/s in part1, 40-45 only at scroll animations in parts 2/3.
- v2 normal-speed swings: median **5 unique frames** in the downswing (range 4-9), 14-25 in the backswing. That is all the footage has
  at normal speed.
- Unique-frame rate is NOT a slow-motion signal here (the player always shows 30 fps); slow motion shows up as swing phases lasting 3-8x
  longer in video time.

### 2. Slow-motion clips (`python -m data.remine_slowmo_v3`, tracks from the v2 cache; `data/references/mason_v3_report.json`)
The v2 detector missed them because its hand-speed threshold (3.5 torso/s) is never reached when the swing is slowed. A slow-motion
detector (hand height above shoulders, takeaway = last still frame, impact proxy = peak hand speed after the top, one swing per return
to address) found 34 swings; 10 had backswing >= 1.2 s. I viewed contact sheets for each: **4 are confirmed slow motion** and were written
(`VERIFIED_SLOW` in the script); the other 6 candidates are NOT written because they were either merged normal swings (p3 night clip, finish
bump picked as top), moderately slower normal swings, or had < 50 % valid upper-body frames.

| File | video t (s) | view | backswing / downswing (video s) | unique frames back / down | tempo | est. slowdown k (range) | est. real down (s) | valid | recommended |
|---|---|---|---|---|---|---|---|---|---|
| mason_v3_p1_s01_slowmo | 44.5-48.7 | down-the-line | 3.47 / 0.80 | 106 / 25 | 4.33 | 4.6 (2.7-7.2) | 0.17 | 0.59 | no (valid < 0.6) |
| mason_v3_p2_s02_slowmo | 1.1-5.3 (dusk) | down-the-line | 3.00 / 1.20 | 93 / 38 | 2.50 | 5.3 (3.3-7.2) | 0.23 | 0.49 | no (valid < 0.5) |
| mason_v3_p2_s03_slowmo | 57.8-61.8 | oblique | 3.07 / 0.97 | 93 / 30 | 3.17 | 4.8 (3.2-6.4) | 0.20 | 0.65 | **yes** |
| mason_v3_p2_s04_slowmo | 62.8-65.0 | down-the-line | 1.83 / 0.40 | 56 / 13 | 4.58 | 2.4 (1.3-3.8) | 0.17 | 0.59 | no (handedness unverified: detector said right at conf 0.32) |

All four: `native_footage`, handedness `left` (stated; footage cues agree for s01/s02/s03, s04 inconclusive), license `self_owned`
/ `commercial_ok=True` via `data/provenance.py` (same caveat as v2: confirm no third-party content). Extra keys: `slow_motion`,
`slowdown_factor_est/min/max`, `slowdown_method`, `effective_fps_est`, `unique_fps`, `downswing_unique_frames`,
`backswing_unique_frames`, `time_real_est` (= (time - time[0]) / k; `time` itself stays in VIDEO seconds), `real_backswing_s_est`,
`real_downswing_s_est`, `remine_version='v3'`.

**Slowdown factor, method and honesty.** Uniform time stretch is assumed. k = slow phase duration / normal-speed phase duration, for backswing
and downswing, with two anchors: (A) the median of Mason's 10 normal-speed recommended v2 swings (0.48 s / 0.17 s; these look short for a
real swing, so A over-estimates k); (B) a rule-of-thumb real swing of a fast golfer, backswing 0.7-0.9 s, downswing 0.22-0.30 s (not
measured here, no citation checked). Central k = geometric mean of the four ratios, range = min/max over anchors and anchor ranges. The
two anchors differ by ~1.7x, so **k is only good to about 2x** (e.g. 3-7 for p1_s01); the implied effective capture rate is 30*k = roughly
90-240 fps, not a measurement. What is robust: (a) these clips sample the downswing with **13-38 unique frames instead of ~5**; (b) the
backswing:downswing ratio is scale-free, and the +-1-frame uncertainty on it is only 4-10 % (vs 14-32 % at normal speed). What is still
not pinned down: the event definitions (the impact proxy is the hand-speed peak, which is slightly before impact; "top" is the hand-height
maximum), so the systematic error of the ratio is probably larger than the frame error. The four ratios span 2.5-4.6 (median 3.75, n=4),
which includes the normal-speed v2 median 2.9 and the 3.0 target; the data does not show a different tempo, only that single-swing
tempo is noisy. Do not tighten the tempo band on the strength of these four clips.

### 3. Face-on
No new face-on clips beyond the 5 already in v2 (`p1_s10_partial`, `p1_s11`, `p2_s07_partial`, `p2_s08`, `p3_s08`); none of the
confirmed slow-motion clips is face-on (3 down-the-line, 1 oblique). The only recommended face-on clip stays `mason_v2_p1_s11`
(normal speed, 5 downswing frames).

### Not done / limits
- No clip has more than 30 unique fps; there is no 120/240 fps footage. The slow clips are 30 fps playback of something slowed, so the
  downswing is sampled by 13-38 frames but the underlying capture rate (and the true k) is unknown.
- Candidates not written: p2 c00 swing B (tracking gap before the top), p3 c02/c05/c07/c10 (moderate slowdown or < 50 % valid), p3 c16
  (merged normal + slow swing), p3 c08 (4 downswing frames). A manual per-clip pass could recover one or two more.
- Joints are 2D-proxy angles from MediaPipe, as in v2; slow clips do not add pelvis/thorax turn or club data.
- Tempo from slow clips is not merged into `mason.aggregate` (different detector); it is a separate `mason_slowmo_v3` block in
  `data/references/mason_target_features.json`.
