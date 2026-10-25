# Mason's own swings -> real reference data

Real (not synthetic) references built from videos **you filmed or posted yourself** (Instagram
@masonwgolf). Nothing in this repo scrapes or downloads from Instagram; you export your own data
by hand and drop the files into `data/mason_swings/`. Raw videos are git-ignored.

## 0. Read this first: Instagram copies are a worse source than your camera roll

Instagram re-encodes uploads (typically ~30 fps, reduced bitrate, and 240 fps slow-mo is usually
flattened or retimed). Tempo and wrist-release timing need the real capture rate. So:

1. **Best:** the original files in your phone's Photos / camera roll (240 fps slow-mo originals).
2. **OK:** the "Download your information" export with media quality High (your uploaded originals as
   Instagram stored them; still probably 30 fps or lower).
3. **Worst:** screen recordings or saving a reel from the app (extra compression).

If a clip is slow-mo that was exported at 30 fps, pass `--capture-fps 240` (the real camera rate).
If you do not know the real rate, do not guess: the tempo numbers will be wrong.

## 1. Export your own data from Instagram (official tool)

Menu names change often. As of Oct 2026, web sources I checked (stashr.me, redact.dev,
timelinize.com, workshop.monorail.tech; not Instagram's own help page, which I could not load
here) agree on the flow below, but **I am not certain of the exact labels on your app version.**
Meta is renaming "Accounts Center" to "Meta Account" for some users, and the tool used to be called
"Download your information" and is now commonly shown as "Export your information". If a label
differs, look for the closest equivalent or search "export" / "download" in Settings.

On a computer (accountscenter.instagram.com) or in the app (Profile -> menu -> Accounts Center):

1. **Accounts Center -> Your information and permissions -> Export your information**
   (older label: *Download your information*).
2. **Create export** (older: *Request a download*), choose your Instagram profile.
3. **Export to device**, not a cloud transfer.
4. **Customize information**: untick everything except **Posts**, **Reels** (and Stories/Archive
   if your swings are there). You do not need messages or activity data; unticking them keeps the
   file small and avoids exporting private data.
5. **Date range: All time** (it defaults to Last year).
6. **Format: JSON** (HTML is fine too; the videos are the same files). We only need the media.
7. **Media quality: High / Higher** (it defaults to Medium).
8. Start the export. Instagram emails/notifies you when ready (minutes to up to 30 days). Download
   it under *Available downloads* within ~4 days, then unzip.
9. Find the videos in the unzipped folder, usually `media/posts/...` and `media/reels/...`
   (older exports: `content/posts_*`). Copy the swing videos into `data/mason_swings/`.
   The export folder itself (`instagram-<name>-<date>/`) is git-ignored; keep it outside the repo
   anyway because it can contain private data.

### Saving individual posts/reels from the app (alternative)

On your own post or reel: open it -> **... (three dots)** -> **Save to camera roll** / **Download**
(label varies by version and not every post type offers it; I could not verify the current wording).
Then AirDrop / USB / cloud-sync the file to your computer. You can also just use the originals
from Photos, which is better (see section 0).

## 2. Filming protocol (for the real dataset)

- **Frame rate:** 240 fps slow-mo (iPhone: Camera -> Slo-mo -> 1080p at 240 fps). Keep the files
  as-is; do not trim with apps that re-encode at 30 fps. Note the true rate (240).
- **Two views per swing:** down-the-line (DTL, camera behind the ball on the target line, about
  hip height, ~3 m back) and face-on (FO, camera facing your chest, same height and distance).
  Film each swing from both, or alternate views with the same club.
- **Setup:** tripod, camera fixed and level, no zoom or panning, landscape or portrait but
  consistent. Whole body, club head and ball in frame from setup to full finish with margin on
  all sides. Even daylight or bright indoor light, plain background, fitted clothing in a colour
  that contrasts with the background, nobody else in frame.
- **Volume:** 20-50 swings. Suggested: 15 driver + 15 iron + 10 wedge, mixed views, mostly
  full-effort swings. Pause between swings; **one swing per file** (trim to about 3-8 s).
- **Notes:** Tell the sidecar your handedness and club. Record a real-time (30 fps) clip as well if
  you can, to sanity-check capture-rate assumptions.
- **File naming:** `mason_YYYYMMDD_<club>_<view>_<NNN>.mp4`, e.g.
  `mason_20261016_driver_dtl_001.mp4`, `mason_20261016_7iron_fo_003.mp4` (use `iron`, `driver`,
  `wedge`, ... as the club token to be auto-detected; view token `dtl` or `fo`).
  Convert `.mov` as needed; `.mov` also works directly.

## 3. Run the pipeline

```bash
cd <local-path>/artifacts/humanoid-golf-scott
source <local-path>/golfvenv/bin/activate
cp data/mason_swings/metadata.example.csv data/mason_swings/metadata.csv   # edit (optional)
python -m data.ingest_mason_swings --dry-run             # validate only, no pose
python -m data.ingest_mason_swings --capture-fps 240     # if files are slow-mo exports
python -m data.ingest_mason_swings                       # resumable: re-run any time
```

Sidecar keys: `club, view, handedness (right|left), capture_fps`. Precedence: CLI `--capture-fps`
> `<video>.json` > `metadata.csv`/`metadata.json` > filename tokens > defaults (right-handed).
Left-handed swings are mirrored so the right-handed joint model applies.

Output per file: `data/references/mason_<name>.npz` with `joints` (11 columns, degrees, same layout
as the synthetic references), `time`, `dt`, `valid_mask`, `valid_frac`, `landmarks`, and labels
`source="mason_self_filmed"`, `is_synthetic=False`, `style="mason"`, `club`, `view`,
`handedness`, `capture_fps`, `effective_fps`, `detect_frac`. A summary is printed and written to
`data/references/mason_ingest_report.json`; resume state is `data/references/mason_index.json`
(changing a file or any setting re-processes it; `--force` redoes all).

Exit codes: 0 ok, 1 MediaPipe backend failed to start, 2 bad arguments/sidecar, 3 some files failed.

## 4. Error messages and fixes

| code | meaning / fix |
|---|---|
| `bad_extension` | not a video type; use mp4/mov/m4v/mkv/webm/avi |
| `empty_file`, `unreadable` | copy/export failed or odd codec; re-copy, or `ffmpeg -i in.mov -c:v libx264 out.mp4` |
| `low_resolution` | short side < 360 px; film at 1080p |
| `bad_fps`, `low_fps` | `capture_fps` must be the real camera rate and >= the file's fps |
| `too_short`, `too_long` | real duration under 0.8 s or over 20 s; trim to one swing |
| `no_person`, `person_intermittent` | full body in frame, good light, nobody else |
| `insufficient_valid_frames` | key joints (right arm, hips, legs) lost too often; re-film |
| `bad_metadata` | sidecar typo (handedness/view/capture_fps) or invalid JSON |
| `duplicate_name` | two files share a base name (e.g. a.mp4 and a.mov) |

## 5. Caveats

Joint angles are crude single-view MediaPipe proxies (see `docs/WHAM_GVHMR.md` for the upgrade
path); two views are stored as separate references, not fused. Ensure only your own footage
goes in this folder.
