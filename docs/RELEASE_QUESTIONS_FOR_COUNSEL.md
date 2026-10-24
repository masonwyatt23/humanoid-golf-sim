# Release questions for counsel (for Mason's 11 AM summary)

Not legal advice and not a legal conclusion; a list of questions and the current facts so counsel can answer them. Nothing has been released or published.

## 1. MultiSenseGolf and CMU (status: `needs_counsel` in the manifest)
- MultiSenseGolf (28 swings, P19/P20/P22) is published CC0 1.0 (Harvard Dataverse), but participants are identifiable. Project tag: `needs_counsel`, `commercial_ok=false`, `counsel_required=true`; the 28 mirrored files are used as 20% of default training weight.
  - Q: Does CC0 on the record cover commercial model training/redistribution given identifiable participants and unknown consent text?
  - Q: Is the derived joint-angle data (no video, no images) still personal data? Are we allowed to ship trained weights?
- CMU Mocap subject 64: free for all uses incl. commercial; no standalone resale/distribution of the converted data; acknowledgment text required.
  - Q: Does shipping converted `.npz` files in an open repo count as standalone distribution? Is the acknowledgment sufficient in a README/model card?
- Fallback if counsel says no: drop both from commercial training; Mason-only plus synthetic.

## 2. Instagram-derived Mason data
- Source: screen recordings of Mason's own Instagram feed posts (`third_party_content_unreviewed=true`). Tagged self_owned, but:
  - Q: Does Instagram/platform terms allow recording the feed and deriving a dataset (even from your own posts)?
  - Q: Third-party content in the recordings (music, other people's faces, captions, reposts, brand footage): were any non-Mason swings or people included? The pipeline keeps landmarks and joint angles; raw video is not in git.
  - Q: Do other golfers or bystanders appearing in feed clips need consent or removal? Two clips have unverified handedness and may not be Mason (`p1_s11`, `p2_s10`, excluded).
  - Q: Can the derived angles/landmarks be published (open source) or only used internally?
- Cleaner path: Mason's own 240 fps capture with a signed consent/release (`docs/FILMING_PROTOCOL.md`).

## 3. Mocap and pose-data licenses (`docs/research_mocap_datasets_licenses.md`)
- Blocked for commercial training per our reading: AMASS, SMPL/SMPL-X, BEDLAM (commercial model training banned), Human3.6M, SportsPose, GolfDB (CC BY-NC, YouTube-sourced), Ubisoft LAFAN1 (non-commercial); HumanML3D and Motion-X inherit AMASS terms.
- Q: Confirm none are used anywhere in a commercial pipeline (our MediaPipe pipeline avoids SMPL).
- Q: Counsel review needed for: CC0-with-identifiable-participants (MultiSense), CaddieSet (MIT repo, unknown participant consent), GolfPose (no published terms).
- Q: Is MediaPipe's own license/model-card compatible with commercial use of its outputs?

## 4. Player names / likeness in profile files
- `docs/research_pro_swing_profiles.md` and JSON name six real professional golfers (names omitted here). Content is published summary stats from cited sources, framed as "style profiles"; no player video, no claims of simulating real persons.
- Q: Is naming players acceptable in a public repo, product copy, or model names (right of publicity, trademark, endorsement implication)? Should the files use anonymised labels (e.g., "long-hitter style A")?
- Q: Does reuse of third-party published numbers (articles, vendor data) need attribution or permission?

## 5. BONES-SEED
- 142k motions retargeted to Unitree G1; commercial use allowed only for startups under $1M revenue, cannot be committed to GitHub, not golf-specific.
- Q: Does the company qualify (revenue, affiliates, future growth threshold)? Is use limited to internal training with no redistribution of derived data? Not downloaded or used so far.

## 6. Open-source release implications
- Q: Which repo content can be public: Mason npz files (Instagram-derived, identifiable movement), CMU-derived npz (acknowledgment, no standalone resale), MultiSense-derived npz (needs_counsel), profile files (names), trained weights?
- Q: License choice for code/data separately; do dataset-level terms (CMU resale clause) force the data to stay out of the repo?
- Q: Does a model trained on mixed licenses (Mason, CMU, MultiSense) inherit restrictions?
- Q: Mason's launch-monitor/self-reported numbers (120+ mph, 300+ yd) are personal data/claims: publishing them needs his consent and a "self-reported" label.
- Current stance: nothing released; `commercial_cleared(entry) = commercial_ok and not counsel_required`.

## 7. TrackMan Driver Fitting Chart 2010 rows (TM2010)
- 48 rows transcribed from the TrackMan Driver Fitting Chart 2010 (18 in the 70-85 mph launch set, 30 in the slow-speed total/carry set) plus the two notes files that quote chart values. They are optimizer/model output from a vendor chart, not measurements. **Held locally; not in the public repo.**
  - Q: Can the raw transcribed values (and notes quoting them) be published in this repo under MIT, with attribution? If not, is a citation-only reference acceptable?

## 8. R&A/USGA report "The effect of impact position on driving distance" (R22-07)
- Raw points digitized from Figs 1-2 (ball speed and spin vs impact height). Date is uncertain: the report is about 2022 by its R22-07 number and publication, but its header says 2006. **The raw digitized points are held locally; not in the public repo.** Only derived constants are published, labelled "derived from digitized figure, approximate" (commit 4c1b9d92, `data/driver_face_offcentre.py`).
  - Q: Can the raw digitized values be published under MIT, with attribution? Are the published derived constants (a small interpolation table and slopes) acceptable as-is?
