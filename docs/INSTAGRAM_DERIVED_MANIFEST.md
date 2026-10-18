# Instagram-derived data manifest (DRAFT for Mason's release decision)

> Consent note: the clips come from Mason's own screen-recorded social-media feed video; consent for release has not been given; this repo is public.

> **Held back:** the machine-readable `data/references/instagram_derived_manifest.json` is NOT in the repo (it holds per-clip timestamps/frame counts from the recordings). Regenerate locally with `python -m data.instagram_derived_manifest`; the test skips if absent. Counts below were re-verified against `git ls-files` on main @ `45bcd41` (132 / 73 npz / 26 / 33 / 39 mentioning).


Not legal advice. Nothing was moved, deleted or published. Generated from `origin/main` @ `d18a82f` by `python -m data.instagram_derived_manifest --local-repo <checkout>`; machine-readable list: `data/references/instagram_derived_manifest.json` (per-file path, size, short sha256, derivation, content type, recommendation). Classification is path-pattern based (heuristic); the npz facts (source video, swing index, frame counts, array dtypes) were read from each file.

## 0. Headline facts
- **The GitHub repo `masonwyatt23/humanoid-golf-sim (renamed 2026-10-18 from humanoid-golf-scott)` is PUBLIC** (checked with `gh repo view`: `visibility: PUBLIC`, `isPrivate: false`; an unauthenticated HTTP GET of the repo page returned 200). So everything below that is tracked on `main` is already publicly readable, and is in git history (202 commits) even if later removed.
- **132 tracked files** are Instagram-derived or built from those clips: **73 pose `.npz`** (needs counsel), **26** aggregate/report JSON + docs (release aggregates only), **33** code/tests/index files (safe). 39 further tracked files only *mention* these artifacts (see the JSON list `other_tracked_files_mentioning_mason_artifacts`; e.g. leaderboard/results docs quoting Mason numbers, `env/`, `eval/`, `train/` code reading the files).
- **Raw video/images: none tracked, none in history** (searched all history for `.mov/.mp4/.m4v/.png/.jpg/.jpeg`: no additions). None of the 73 npz holds an image-like (uint8) array; they hold MediaPipe 33x4 landmarks (x, y, z, visibility) and 11 joint-angle columns. `.gitignore` blocks `data/mason_swings/*` (videos), `*.mov/*.mp4`, `instagram-*/`. Pose time series of an identifiable person are still personal-ish data, not "no data".
- **Third-party content: UNREVIEWED for every item.** The source is screen recordings of the feed (parts 1-3, `mason_swing_part{1,2,3}.mov`), which may contain other people's posts/likeness/music. Every npz carries `provenance_note: confirm no third-party content/music in the source`; unified manifests carry `third_party_content_unreviewed: true`. Nobody has checked that every swing is Mason's (two clips, `p1_s11`, `p2_s10`, have unverified handedness and are excluded from training weight).
- Mason's Instagram handle and name appear in tracked docs/metadata (`docs/MASON_SWINGS.md`, `docs/MASON_SWING_PIPELINE.md`, `docs/MASON_VIDEO_REPORT.md`). Commit author metadata in history includes a personal email address of the repo owner (not repeated here); a history rewrite would be needed to remove that too.

## 1. Inventory (tracked on origin/main)
| Group | Files | Derivation | Content | Images? | Recommendation |
|---|---|---|---|---|---|
| `data/references/mason_swing_part{1,2,3}_sNN_mirrored.npz` | 15 | v1 first pass, mirrored copies (unmirrored originals are git-ignored, local only) | landmarks+angles | none | needs counsel |
| `data/references/mason_swing_part*_refined[_mirrored].npz` | 20 | v1 refined | landmarks+angles | none | needs counsel |
| `data/references/mason_v2_p{1,2,3}_sNN[_partial|_unmirrored].npz` | 34 | v2 re-mine of parts 1-3 | landmarks+angles+QC flags | none | needs counsel |
| `data/references/mason_v3_p*_slowmo.npz` | 4 | v3 slow-motion segments (parts 1-2) | landmarks+angles | none | needs counsel |
| `mason_v2_report.json`, `mason_v3_report.json`, `mason_feed_report.json`, `mason_cadence_audit.json` | 4 | per-clip QC/timestamps of the recordings | metadata, timestamps in video | none | aggregates only (timestamps locate clips in the source) |
| `mason_target_features`, `mason_impact_geometry_targets`, `mason_impact_face_path_proxies`, `mason_keyframe_targets`, `mason_keyframe_targets_extra`, `mason_elbow_address_stats`, `mason_elbow_camera_bias`, `mason_vs_profiles` (.json) | 8 | computed from v2/v3 npz | joint-angle stats; several have per-clip entries | none | aggregates only (strip per-clip tables first) |
| `wrist_elbow_event_targets.json`, `wrist_sign_mapping.json` | 2 | **do use Mason data**: per-clip v2 angles plus CMU comparison (checked: `mason_clips`/`clips` keys; mapping constants fitted to Mason best clip and CMU) | per-clip angles, constants | none | aggregates only; CMU part is needs-counsel by its own audit |
| `data/reference_sets/unified_v{1,2}[_sampling].json` | 4 | index; 12 of 50 entries are Mason (all on main) | paths/weights/flags | none | safe (but entries point at the npz) |
| `docs/MASON_*.md`, `WRIST_*` docs, `UNIFIED_V1_LICENSE_AUDIT.md` | 12 | quote Mason numbers/process | docs | none | aggregates only; check per-clip tables |
| scripts (`data/*mason*`, ingest/remine/refine/audit, unified_refset, wrist_*) | 17 | code | code | none | safe |
| tests touching Mason files | 9 | tests | code | none | safe |
| `data/mason_swings/{README.md,metadata.example.csv,.gitkeep}` | 3 | placeholders | docs | none | safe |

Files that merely quote numbers (not counted above, listed in the JSON): `results/leaderboard.*`, `results/TRAINING_NOTES.md`, `results/ppo_resid_v3_left_*.json` (config/args naming Mason refs), `results/unified_val_style.*`, `README.md`, `CHANGELOG.md`, `docs/TRACKING_REWARD_REFERENCE_GAPS.md`, `docs/REFERENCE_PATHS.md`, `docs/CHECKPOINT_RELEASE.md`, etc. Low risk (aggregate numbers), but a "remove Mason data" policy must sweep them too. `env/`, `eval/`, `train/` code only reads the files.

## 2. Local only (not in git)
From the local checkout status: 3 raw screen recordings `data/mason_swings/mason_swing_part{1,2,3}.mov` (git-ignored), 15 unmirrored v1 `mason_swing_part*_sNN.npz` (git-ignored), `data/references/mason_ingest_report.json` (git-ignored by rule), and 5 untracked `logs/*mason*` training logs (not reviewed for content). Keep all of these out of git. (The `data/raw_mocap/cmu` BVHs are ignored too but are not Instagram data.)

## 3. Recommended mechanism (easy first)
1. **Decide first: visibility.** The repo is public. If Mason wants these private, the fastest reversible step is making the repo private (a GitHub setting; Mason's call). That does not undo copies others may already have cloned.
2. **Provenance tag.** Add `provenance_source=instagram_derived` (npz field and manifest/unified entries; `provenance_source` already exists as `mason_self_filmed`) so any release script can filter on it. Cheap and non-destructive.
3. **Private location.** Move the raw-pose files to a git-ignored `private/` (or a separate private repo / release asset) and keep only aggregate JSON public; update `unified_*.json` paths and tests accordingly. Not done here (instruction: no moves).
4. **If the repo stays public and the pose files must go:** `git rm` removes them from the tip only; they remain in history. Removal from history needs `git filter-repo` (rewrites all 202 commit hashes, force-push, every clone/fork must re-clone; also commit-hash references in docs break) and GitHub support to purge cached views/forks. Treat as heavy; only do it if counsel says the data cannot be public.
5. **Release gate:** a small script that fails if any file with `instagram_derived` is staged for a public release (the JSON manifest can drive it).

## 4. Questions for Mason (decisions needed)
1. Make the repo private now, or keep it public? (It is public today and the pose files are in it.)
2. Are the 73 pose `.npz` files OK to keep public, or private-only? If private-only, do you want history rewritten (heavy), or accept that history copies exist?
3. May aggregates (angles at address/top/impact, tempo, elbow stats) be published? Per-clip tables or only pooled stats?
4. Do you confirm every swing in the feed recordings is you, and that none shows other people/music/brand content? Who reviews this (needs someone to watch the three recordings)? Until then everything stays `third_party_content_unreviewed`.
5. Does Instagram's terms of use allow recording your feed and deriving data from it, even your own posts? (counsel question, also in `docs/RELEASE_QUESTIONS_FOR_COUNSEL.md`)
6. Is it acceptable that your name/handle and the owner's email appear in public docs and commit metadata?
7. Should trained checkpoints that used Mason references (style/tracking terms) be released? (`docs/CHECKPOINT_RELEASE.md`)
8. Would you rather replace this data with a fresh 240 fps capture under a signed release (`docs/FILMING_PROTOCOL.md`) and retire the feed-derived data?

## 5. Caveats
Classification is by path pattern plus read-in npz metadata; the sha256 values are the first 16 hex chars. Whether any frame contains someone else is unknown. Recommendations are engineering suggestions, not legal conclusions.

> **Update 2026-10-18:** the data files this document describes (CMU `cmu_64_*.npz`, `multisense_*`, `mason*.npz`, CaddieSet converter/features JSON, `results/imit_private/` gates, as applicable) were untracked at the tip (`git rm --cached`; held locally; `.gitignore`d). They **remain in git history** (no rewrite). Rows citing them are [data/gate held locally].
