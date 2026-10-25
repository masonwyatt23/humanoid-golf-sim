# Research v2: openly licensed, commercially usable golf swing / mocap data

Prepared 2026-10-16 (ET). Engineering diligence, **not legal advice**; get counsel's sign-off before shipping. Extends
docs/research_data_sources.md (read that first for GolfDB, AMASS, BEDLAM, Motion-X, HuMMan, KIT, CaddieSet, GolfPose; not repeated
here except where status changed). "[primary]" = read on the source's own page/API today; "[secondary]" = search-result summary or a
copy of the terms on a third-party page.

## Result in one line
**One new GO: MultiSenseGolf (Harvard Dataverse, CC0 1.0): 24 golfers, 1,557 full-body inertial-mocap swings with launch-monitor
club speed up to 102.7 mph.** Downloaded and converted (28 swings of the three fastest golfers). Everything else new is NO-GO or
irrelevant. CMU stays the only optical-mocap source (10 swings, already converted).

## Go / no-go table
| Source | Golf content | License evidence | Verdict |
|---|---|---|---|
| **MultiSenseGolf** (Oh et al., doi:10.7910/DVN/LCCLLW, Harvard Dataverse, released 2026-02-03, v4 2026-10-05) | 1,557 swings, 24 participants (beginner to pro), 17-IMU full-body mocap (Perception Neuron Studio), insole pressure, FPV + RGB-D video, launch-monitor club/ball speed and carry | Dataverse API `latestVersion.license`: `{"name": "CC0 1.0", "uri": "http://creativecommons.org/publicdomain/zero/1.0", "rightsIdentifier": "CC0-1.0"}`; no `termsOfUse`/`restrictions` text set [primary]. `Participant Metadata.csv`: "Whether to Consent to Data Disclosure?" = "Agree" for all 24 rows [primary] | **GO (downloaded)** |
| **CMU Mocap**, subject 64 (10 swings) | optical mocap, 120 Hz | Home page: "This dataset of motions is free for all uses." and "You may include this data in commercially-sold products, but you may not resell this data directly, even in converted form." [primary, re-read today at mocap.cs.cmu.edu]; details/obligations in docs/CMU_MOCAP_GOLF.md (held locally) | **GO (done earlier)**, keep converted files private, add acknowledgment |
| CMU subject 63 (`63_01`) | 1 "Swing" listed | same terms. The GitHub mirror's `063/63_01.bvh` is byte-identical to `64_01.bvh` (docs/CMU_MOCAP_GOLF.md (held locally)) | Skip (duplicate) |
| **Mixamo** (Adobe) | golf-swing animations exist, keyframed/generic | Adobe-staff FAQ text reposted on community.adobe.com: "The only research application Mixamo content can't be used in is training machine-learning models." and "really the only thing you can't do is distribute the raw character and animation files" [secondary: a community-forum copy; helpx FAQ says "royalty free for personal, commercial, and non-profit projects" [primary snippet]] | **NO-GO** (ML training prohibited; not real swings either) |
| **MoCapAct** (Microsoft) | RL experts + rollouts on CMU clips for the dm_control humanoid; no golf-specific selection found | README: "The code is licensed under the MIT License. The dataset is licensed under the CDLA Permissive v2 License." [secondary, from search snippet of the GitHub README]; underlying motion is CMU data under CMU's terms | **NO-GO / not needed** (humanoid policy data, not swing references; CMU terms still apply) |
| OpenCap datasets (SimTK) | squats, sit-to-stand, drop jumps, walking: no golf | license terms not shown in the pages I could read | **No-go** (irrelevant) |
| Zenodo "Golf Dataset" (doi:10.5281/zenodo.6406122, D. Haluza) | one 88 kB `.sav` (SPSS file) from a survey-type study | "License: Creative Commons Attribution 4.0 International" [primary] | **N/A** (not motion data) |
| Univ. Edinburgh DataShare, wrist IMU/EMG in golf (doi:10.7488/ds/3823) | wrist angular velocity, forearm IMU, EMG, clubhead kinematics; not full-body | page lists "End-user Licence" without terms I could read [primary page, terms not shown] | **No-go** (license unread, partial body) |
| GolfDB, AMASS, BEDLAM, Motion-X, HuMMan, Human3.6M, Kaggle Golf-Pose | see docs/research_data_sources.md | non-commercial / no license | unchanged: NO-GO |
| KIT whole-body DB ("play golf"), GolfPose (3D golf, email authors), CaddieSet | see docs/research_data_sources.md | no commercial grant / no license / 2D features | unchanged: ask in writing (KIT, GolfPose) |

I did not find another openly licensed (CC0 / CC-BY / similar) full-body golf mocap beyond CMU and MultiSenseGolf. The searches covered
Zenodo/Figshare/Dryad/Dataverse golf kinematics, MoCapAct, Mixamo, OpenCap. Not exhaustively searched: SFU mocap, 100STYLE, Bandai
Namco, LAFAN1 (none are golf; licenses not read).

## MultiSenseGolf in detail
- **Where:** https://doi.org/10.7910/DVN/LCCLLW . Files: `Documentation.zip` (3 CSVs), `P01.zip` ... `P24_3.zip` (1-2 GB each, one participant
  per zip, some split `_1/_2/_3`, each swing folder has FPV video, front RGB-D frames, timestamps and a `.hdf5` of streams). API used:
  `https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/LCCLLW` and
  `/api/access/datafile/<id>` (no login needed; `fileAccessRequest: true` but files were not restricted and downloaded directly).
- **What I downloaded:** `Documentation.zip`; `P19_1/_2`, `P20_1/_2`, `P22_1/_2`, `P23_1/_2` zips (~12 GB), of which **only the
  `*_stream_data.hdf5` files were extracted (about 390 MB)**; the zips were deleted. No participant video or depth frames were kept,
  so no faces are stored. P23 produced no swing >= 88 mph so none of its swings were converted. Scratch: `<local-path>/golf_scratch/multisense/`.
- **Format:** `pns-joint-root-relative-position/cm-values/data` (n, 63) = 21 joints x xyz in cm, root-relative, Y-up, +X = subject's left, +Z =
  facing; ~94 Hz irregular timestamps. Joint order inferred from the geometry (Hips, R/L UpLeg, Leg, Foot, Spine, Spine1, Spine2, Neck, Neck1,
  Head, R/L Shoulder, Arm, ForeArm, Hand); the dataset's documentation ZIP has only CSVs, so this order is my inference. Checked
  by bone lengths (parent-relative offsets: thigh ~44 cm, forearm ~27.5 cm, upper arm ~28 cm).
- **Annotation CSV:** per swing launch-monitor club speed (m/s), ball speed, carry, launch angle, spin. Best club speeds by participant
  (mph): P10 105, P19 103, P20 101, P14 96, P22 93, P9 94... Participants holding a professional license per the metadata: P17-P24.
  Self-reported skill (1-7): P19 = 7, P20 = 7, P22 = 6.
- **Converted:** `data/convert_multisense_golf.py` (held locally) -> `data/references/multisense_P{19,20,22}_sNN.npz`, 28 files with club speed
  88.8-102.7 mph, carry 123-163 m, tempo 2.1-3.6, hand peak 7.4-10.5 m/s. Reuses the CMU converter's joint maths and event
  detection (3D hand path). Tagged `license_class=cc0`, `commercial_ok=True`, `provenance_source=multisensegolf_harvard_dataverse`;
  `acknowledgment_required=False` but a citation string is stored (courtesy). Report: `data/references/multisense_conversion_report.json`.
- **Limits (be sceptical):** (1) IMU mocap, not optical: drift and soft-tissue artefacts, no ground truth in this repo;
  (2) no finger/toe joints, so wrist hinge and ankle columns are zeros (flagged); (3) no club-head trajectory, only launch-monitor
  speed per swing; (4) all 24 participants are right-handed (metadata: Swing Handedness = Right for all), so for Mason (left) these
  need mirroring; (5) a few swings are only 100 mph at the launch monitor, nowhere near Mason's 120+ mph target, so they are
  sequencing/tempo references, not speed targets; (6) the CC0 waiver covers the dataset record; I did not read the paper's data statement
  or the IRB text, only the metadata "Agree" for disclosure. Counsel should confirm that CC0 plus that consent covers commercial ML use
  of motion derived from identifiable people (we use joint positions only, no video).
- **More available:** other participants (e.g. P17, P18, P21, P24, and P10/P14 with high launch-monitor speeds) were not downloaded or converted; P10 and P14 are self-rated intermediate.
  Say if you want more, the script takes `--participants`, `--top-n`, `--min-club-mph`.

## Recommendation
1. Use MultiSenseGolf for commercially clean full-body sequencing/tempo (fast, trained golfers) and CMU for optical-quality swings, both mirrored for Mason.
2. Treat as non-commercial and keep out: GolfDB, AMASS-derived, Motion-X, Mixamo (ML clause).
3. Ask in writing: KIT H2T (golf mocap) and the GolfPose authors, as before.
4. Mason's own clips remain the only left-handed data; native-left v2 files need no mirroring.
