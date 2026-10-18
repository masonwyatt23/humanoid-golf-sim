# CMU Graphics Lab Motion Capture golf swings

Real optical-mocap golf swings (Vicon, 120 Hz) converted to our `.npz` reference format by
`data/convert_cmu_mocap.py`. **The subject is not Adam Scott** (an unnamed lab volunteer; CMU
publishes no skill level, handicap, or handedness). Use for a real human kinematic prior and
sequencing, not for Scott's style.

## 1. Licence / terms (read 2026-10-16; quoted verbatim)

Official pages, fetched live:

* Home page, <http://mocap.cs.cmu.edu/>:
  > "This dataset of motions is free for all uses."

  > "This data is free for use in research projects. You may include this data in
  > commercially-sold products, but you may not resell this data directly, even in
  > converted form. If you publish results obtained using this data, we would appreciate it
  > if you would send the citation to your published paper to contact per CMU terms (http://mocap.cs.cmu.edu), and also
  > would add this text to your acknowledgments section: The data used in this project was
  > obtained from mocap.cs.cmu.edu. The database was created with funding from NSF
  > EIA-0196217."
* FAQ, <http://mocap.cs.cmu.edu/faqs.php> ("How can I use this data?"):
  > "The motion capture data may be copied, modified, or redistributed without permission."

  The FAQ also says: "Please don't crawl this database for all motions" (a full zip is offered).
* Mirror we actually downloaded from: `una-dinosauria/cmu-mocap` on GitHub, which republishes
  Bruce Hahne's cgspeed BVH conversion. Its README says "Check `READMEFIRST.txt`"; that file
  (kept at `data/raw_mocap/cmu/READMEFIRST.txt`) says:
  > "CMU places no restrictions on the use of the original dataset, and I (Bruce) place no
  > additional restrictions on the use of this particular BVH conversion."

  (It quotes an older, more permissive wording of the CMU paragraph: "free for use in research
  and commercial projects worldwide".) The GitHub repo itself has no LICENSE file; the cgspeed
  site and this readme are the mirror's terms.

**Assessment (not legal advice): permitted for our use.** Research and commercial products
may use the data; training our own models/policies and shipping derived references/results is
within that. Two obligations:
1. Do **not** resell/distribute the data itself, even converted. The `cmu_*.npz` files are
   converted data: keep them inside the project; do not publish them as a standalone dataset
   or sell them. (The FAQ's "redistributed without permission" conflicts with the home page's
   "may not resell"; we follow the stricter reading.) Raw BVH are gitignored.
2. Add the acknowledgment sentence above in any publication/product credits.

## 2. Which trials are golf swings

From the CMU index (`data/raw_mocap/cmu/cmu-mocap-index-text.txt`, also
<http://mocap.cs.cmu.edu/search.php?subjectnumber=64>):

| Subject | Trials | Description |
|---|---|---|
| 64 (golf) | `64_01`–`64_10` | **Swing** (10 trials) <- converted |
| 64 | `64_11`–`64_15` | Putt |
| 64 | `64_16`–`64_30` | Placing Tee / Placing Ball / Picking up Ball |
| 63 (golf) | `63_01` | Swing, **but** the mirror's `063/63_01.bvh` is byte-identical (md5 `4eb58618…`) to `064/64_01.bvh` — a mirror quirk or duplicate, so it was deleted and not used. |

(docs/research_driver_distance.md said "~10 Swing" for subject 64: confirmed. Only the 10 swing
trials were downloaded; no putts/tee placement.) The CMU site could not be reached directly from
the box (connection timeouts), so the BVH came from the GitHub mirror over HTTPS; the home page,
FAQ and subject-64 index were read through the fetch tool.

Download (what was run):
```
mkdir -p data/raw_mocap/cmu && cd data/raw_mocap/cmu
for i in 01 02 03 04 05 06 07 08 09 10; do
  curl -sO https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/master/data/064/64_$i.bvh; done
```
Source BVH conversion details (READMEFIRST): frame 0 of every BVH is an *added T-pose* (dropped by
our converter); Frame Time was rewritten to 1/120 s; motion data otherwise unmodified from ASF/AMC.
We use the BVH conversion rather than ASF/AMC (the official zip is 100s of MB and the ASF/AMC route
was unreachable from the box); the BVH is permitted by the terms above.

## 3. Output

`python -m data.convert_cmu_mocap` -> `data/references/cmu_64_01.npz … cmu_64_10.npz` plus
`cmu_conversion_report.json`. Keys: `time`, `joints` (deg, `(n,11)`), `joints_rad`, `dt`=0.01,
`events`=[top, impact] s, `takeaway_s`, `finish_s`, `tempo_ratio`, `pelvis_rot_deg`,
`thorax_rot_deg`, `x_factor_deg`, `lateral_sway_m`, `wrist_hinge_deg`, `peak_hand_speed_mps`,
`source="cmu_mocap"`, `is_synthetic=False`, `has_club_head=False`, `style="cmu_subject64"`,
`subject`, `trial`, `trial_id`, `handedness`, `source_file`, `source_fps`=120, `qc_flags`,
`joint_columns`. Same key names/sign conventions as `generate_synthetic_scott.py`
(rotations negative on the backswing; `x_factor = pelvis − thorax`, positive when the thorax is
turned further).

Results (n=10; each trial 227–282 frames = 2.3–2.8 s, trimmed to 0.25 s before takeaway and
0.25 s after finish):

| | min | mean | max |
|---|---|---|---|
| tempo (backswing:downswing) | 1.50 | 1.72 | 1.94 |
| backswing s | 0.80 | 0.89 | 1.01 |
| downswing s | 0.43 | 0.52 | 0.60 |
| pelvis turn at top ° | 38.7 | 51.2 | 60.2 |
| thorax turn at top ° | 73.7 | 85.1 | 95.4 |
| X-factor at top ° | 28.3 | 33.8 | 38.5 |
| peak hand speed m/s | 3.51 | 4.09 | 4.57 |

Trials 64_01, 64_05, 64_06 carry `qc_flags=low_hand_speed` (<4 m/s). Downswing 0.43–0.60 s and
tempo ~1.7:1 are **much slower than a Tour swing** (~0.25 s, ~3:1): this is a slow, lab-paced
swing without a ball, so don't use CMU tempo/speed as a target for distance training.

## 4. Conversion method, units, axes

* Parse BVH, forward kinematics. Joint order from the CHANNELS lines
  (`Zrotation Yrotation Xrotation` => `R = Rz·Ry·Rx`, first listed outermost; root has
  position channels). Frame 0 (added T-pose) dropped.
* Lengths: BVH lengths are ASF units: **metres = value × (1/0.45) × 2.54/100 = ×0.056444**
  (CMU FAQ). Check: thigh = 0.418 m, hand height at address ≈ 0.86 m.
* Axes: world is Y-up (up = +Y), subject at T-pose faces +Z, +X = subject's left. The swing
  direction in the lab is arbitrary, so everything is expressed relative to the subject's own
  address pose.
* Handedness: auto-detected from the finish (hands end nearer the lead shoulder). All 10 trials
  detect **right-handed**. Left-handers would have the trail/lead roles swapped so that the
  "right_*" columns are always the trail arm / trail leg.
* Resample 120 Hz -> `dt = 0.01` s by linear interpolation; 120 Hz angles smoothed first with
  Savitzky–Golay (0.10 s window, order 3). CMU says wrist/hand/toe channels are noisy and
  finger/thumb are fake — we use only `RightHand->RightHandIndex1` as the hand direction.

### Joint mapping to the 11 columns (degrees, from 3-D positions)

Thorax frame: up = hip-centre -> shoulder-centre; lateral = right->left shoulder (orthogonalised);
forward = lateral × up.

| col | name | definition |
|---|---|---|
| 0 | right_shoulder_pitch | −(flexion of trail upper arm vs thorax: 0 hanging, 90 forward, 180 overhead); raising = negative (generator convention) |
| 1 | right_shoulder_roll | abs. abduction of trail upper arm out of the thorax sagittal plane (≥0) |
| 2 | right_elbow | 180 − interior angle(shoulder, elbow, wrist), trail arm |
| 3 | right_wrist | −(180 − interior angle(elbow, wrist, hand-end)); cocked negative. Unsigned: can't go positive on release (generator goes to +60) |
| 4 | left_shoulder_pitch | same as col 0 for the lead arm |
| 5/6/7 | right hip/knee/ankle | hip: 180 − angle(shoulder-centre, hip, knee); knee: 180 − angle(hip, knee, ankle); ankle: angle(knee, ankle, toe) − 90 (trail leg) |
| 8/9/10 | left hip/knee/ankle | same for the lead leg |

Extras: `pelvis_rot_deg`/`thorax_rot_deg` = yaw of the trail→lead hip/shoulder line about vertical,
relative to the quiet-address mean, sign-flipped so the backswing is negative.
`lateral_sway_m` = hip-centre displacement along the address hip line (trail->lead, i.e. toward
the target), + toward target.

**Not the same zero as the env.** The values are anatomical angles *including* the golfer's
address posture (e.g. knee flexion ≈ 25–30° at address, trail hip flexion ≈ 18°), not offsets from
a neutral standing pose, and not the MuJoCo joint frames. The model has no pelvis/torso yaw, so
rotations live in the extra arrays. The retargeting/PD tracking step must handle that. As with
other references, the env's degree/radian handling applies (`joints_rad` provided).

### Events (heuristic, from motion only; no club or ball in CMU data)
Hand midpoint speed/height: *peak* = max hand speed; *top* = highest hand position before the
peak; *takeaway* = last at-rest frame (speed < 5 % of peak) before the backswing; *impact* = the
frame within [peak−0.08 s, peak+0.12 s] where the hands are nearest their address position;
*finish* = first frame after impact with speed < 5 % of peak. Expect ±3–5 frames (±0.03–0.05 s)
error on impact; it was **not** validated against ground truth. Top-of-backswing is robust.

### `club_head`
CMU captured no club, so `club_head` is **not written** (`has_club_head=False`). A shaft
direction isn't derivable from hand/wrist data. Note `HumanoidGolfEnv.load_reference` reads
`data["club_head"]` unconditionally (and `_compute_reward` indexes it), so loading a `cmu_*.npz`
through the env will `KeyError` until the env tolerates a missing club target.
`ReferenceDataset` returns `club_head=None` and loads them fine.

## 5. Caveats
* Subject 64 is an unnamed volunteer; skill/handicap unknown. Pelvis ~51°, thorax ~85°, X-factor
  ~34° and the slow tempo look like a recreational/lab swing, not a Tour pro.
* Wrist hinge from CMU's noisy hand joint is large (−65 to −80° at the top) and unsigned; treat it
  as a rough indicator.
* Hip slide −0.19/−0.23 m trail-ward in the backswing then +0.24–0.25 m toward the target at
  the finish (relative to address) is bigger than Tour norms; includes the follow-through.
* No ball: the capture is of a practice swing, so no contact dynamics.
* 10 trials from one person; it's one body's kinematics, not a distribution of styles.

> **Update 2026-10-18:** the data files this document describes (CMU `cmu_64_*.npz`, `multisense_*`, `mason*.npz`, CaddieSet converter/features JSON, `results/imit_private/` gates, as applicable) were untracked at the tip (`git rm --cached`; held locally; `.gitignore`d). They **remain in git history** (no rewrite). Rows citing them are [data/gate held locally].
