# CaddieSet integration

Verified 2026-10-15 against the repo, README and `data/CaddieSet.csv` (fetched from GitHub).

## What it is
- Repo: https://github.com/damilab/CaddieSet — **MIT license** (LICENSE file in repo).
- Paper: Jung et al., "CaddieSet: A Golf Swing Dataset with Human Joint Features and Ball Information", CVPR 2025 Workshops (CVSports). Cite it (BibTeX is in the repo README).
- Repo contents: just `LICENSE`, `README.md`, `data/CaddieSet.csv` (~508 KB). **No videos, no raw keypoints, no time series.**
- 1,757 shots (1,757 CSV rows): 924 FACEON + 833 DTL views. **Only 8 golfers ("diverse skill", not pros)**. Clubs: W1 1137, I7 319, I9 101, W3 46, I8 45, I5 41, I4 40, I6 28.

## Fields (CSV columns, 87 total)
- Ball (launch monitor): `View, ClubType, Distance, Carry, LrDistanceOut, DirectionAngle, SpinBack, SpinSide, SpinAxis, BallSpeed, GolferId`.
  Observed ranges: BallSpeed 39.9-69.4 (driver mean 56.3), Carry 107-233, SpinBack 262-7319, DirectionAngle -18..21.
  **Units are not documented in the README.** BallSpeed is most plausibly m/s and Distance/Carry yards (driver mean 56 m/s ~ 126 mph), but this is inferred; confirm with the paper/authors before using absolute values.
- Joint-derived features: columns named `<phase>-<FEATURE>`, phase 0-7 = the 8 swing events detected by a vision model (address -> finish; the exact phase names are in the paper, check there). Features include HIP-ROTATION, HIP-ANGLE, HIP-LINE, HIP-SHIFTED, HEAD-LOC, SHOULDER-ANGLE, SHOULDER-LOC, SPINE-ANGLE, UPPER-TILT, STANCE-RATIO, LEFT/RIGHT-ARM-ANGLE, RIGHT-LEG/LEFT-LEG/LOWER-ANGLE, RIGHT-ARMPIT-ANGLE, RIGHT-DISTANCE, HIP/SHOULDER-HANGING-BACK, WEIGHT-SHIFT, FINISH-ANGLE. 15 expert-defined metrics per the paper; paper says 17 joint coordinates were used to compute them (not released).
- **Sparse by design**: each feature only exists for one view and specific phases (about 40 non-empty columns for FACEON, 33 for DTL), so ~50% NaN per column. Handle NaN explicitly; never `dropna()` the whole row.
- Angles are presumably degrees and `*-LOC/-SHIFTED/-LINE` are normalised ratios (e.g. by stride length); verify against the paper.

## What it can and cannot do for us
Can: ball-flight sanity ranges, joint-feature distributions for amateur-to-intermediate golfers, relationships such as hip rotation vs. ball speed, and regression/validation targets.
Cannot: supply Adam Scott's style (no pros, no per-frame joints, no club/wrist data, no tempo timings), or serve as imitation-learning trajectories. It is a calibration/sanity set, not a motion-capture set.

## Step by step
1. Download: `curl -L https://raw.githubusercontent.com/damilab/CaddieSet/main/data/CaddieSet.csv -o data/external/CaddieSet.csv` (keep out of git or keep the LICENSE alongside; MIT requires preserving the notice if redistributed).
2. Load: `df = pd.read_csv(...)`; split `df[df.View=="FACEON"]` and `DTL`; keep `GolferId` for group-wise CV (8 golfers -> leave-one-golfer-out, otherwise results leak).
3. Phase mapping: read the paper's 8-phase definition and map phase indices to our timeline events (address, takeaway, top, transition, impact, follow-through...). Add this mapping as a dict in the ingest script.
4. Calibrate STYLES (`data/generate_synthetic_scott.py`) loosely:
   - `pelvis_top` / `pelvis_impact`: from `HIP-ROTATION` / `HIP-ANGLE` at the top and impact phases (FACEON). Compare the distribution (mean, p10-p90) of generated `pelvis_rot_deg` at those events to it; check sign/zero convention (relative to address).
   - `sway_back` / `slide_fwd`: from `HIP-SHIFTED` / `HIP-LINE` (normalised, so multiply by stance/stride length in metres).
   - `arm_top`, `wrist_set`: only indirectly via `LEFT/RIGHT-ARM-ANGLE` (elbow angles, not shoulder pitch or wrist hinge).
   - `thorax_top`, `plane_angle`, `tempo_ratio`, `wrist_release_start`: **not available**. Keep the published coaching values.
   Treat CaddieSet only as an amateur envelope: Scott's values should sit at/beyond its high-skill end, not at its mean.
5. Ball-flight sanity check: for the env's simulated shots compare ball speed, launch/direction angle and carry (convert units first) against the CaddieSet per-club distribution (e.g. W1). Flag sim shots outside min-max.
6. Optional model: fit a small interpretable model (ridge/GBM) joint features -> BallSpeed/Carry per club with leave-one-golfer-out; use it as an auxiliary reward-sanity check only.
7. Record the results (per-feature mean/std per club) in `data/external/caddieset_stats.json` so tests can assert calibration ranges.

## Caveats
- Amateurs, 8 people, mostly drivers: statistics are not Tour-representative.
- Joint features came from automatic pose estimation on video (noise, and single-view features depend on camera placement).
- Units/conventions undocumented in the README (see above); verify in the paper before hard-coding.
- No raw coordinates, so this cannot feed `ReferenceDataset` / imitation reward directly.
- MIT covers the dataset repo; it does not grant rights to anyone's underlying videos (not distributed here).

> **Update 2026-10-18:** the data files this document describes (CMU `cmu_64_*.npz`, `multisense_*`, `mason*.npz`, CaddieSet converter/features JSON, `results/imit_private/` gates, as applicable) were untracked at the tip (`git rm --cached`; held locally; `.gitignore`d). They **remain in git history** (no rewrite). Rows citing them are [data/gate held locally].
