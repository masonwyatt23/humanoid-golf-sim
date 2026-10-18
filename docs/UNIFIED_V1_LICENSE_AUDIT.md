# `unified_v1` licence-tag audit

Engineering diligence, **not legal advice**. Compares the licence tags in the unified training reference set with the licence research committed in `data/references/mocap_dataset_licenses.json` and `docs/research_mocap_datasets_licenses.md` (commit `eb8d1db`). Items marked **[unverified]** were not confirmed from a primary source in this audit.

Inputs read: `data/reference_sets/unified_v1.json` (50 entries), `data/reference_sets/unified_v1_sampling.json`, `data/unified_refset.py`, the `.npz` provenance tags of the referenced files, `results/imit*.json`, `train/train_imitate.py`.

## 1. What feeds `unified_v1`

Exactly three sources. CaddieSet, GolfDB, AMASS, synthetic styles and the pro-profile data are **not** in the manifest (checked: the `source` field takes only `mason`, `multisense`, `cmu`).

| Source | Entries (train / val) | Sampling mass (`source_weights`, train split) | Share of entries | What it is |
|---|---|---|---|---|
| `mason` | 12 (9 / 3) | 0.60 | 24% | Mason's swings, pose estimated from phone screen recordings of Instagram playback (~30 fps); one flipped-edit clip un-mirrored; one slow-mo clip at weight 0 |
| `multisense` | 28 (22 / 6) | 0.20 | 56% | MultiSenseGolf IMU joint kinematics, participants P19, P20, P22, mirrored to left-handed (`*_mirrored.npz`) |
| `cmu` | 10 (8 / 2) | 0.20 | 20% | CMU mocap subject 64 trials 01-10 (right-handed originals, mirrored on load) |

Within a source, per-file weight is `quality**1.0` normalised to the source mass. Val-split entries have training weight 0 and are used only by `eval/unified_style.py`. The weights are a stated prior, "not tuned" (sampling config rationale). The manifest and all referenced `.npz` files are tracked in the public repo.

## 2. Tag comparison

| Source | Tag in manifest | Finding in licence research | Conflict / gap |
|---|---|---|---|
| `mason` | `license_class: self_owned`, `commercial_ok: true` | **Not covered** by the research (it only reviews third-party datasets). Per-file note: "Instagram-recorded footage of Mason's own swings; confirm no third-party content/music in the source video." Research only mentions that OpenCap's hosted service must not be used for these swings | The tag is an owner's assertion, never verified. Instagram platform terms, and third-party content in the source recordings, were not reviewed. README says right-handed clips on the feed can be other golfers; see handedness gaps below |
| `multisense` | `cc0`, `commercial_ok: true`, citation in `ack` | `commercial_ok: needs_counsel`, recommended tag `cc0`, `counsel_needed: true`, verification `secondary_search_snippet`. CC0 is inferred from the Dataverse default waiver, not read from the dataset record. Concern: identifiable participants, consent scope, privacy law for commercial training | **Conflict:** the manifest says commercially OK; the research says to gate commercial release on counsel sign-off. The CC0 text itself is **[unverified]** (not read from the record). The `.npz` has `acknowledgment_required: False` while the manifest still carries a citation string (consistent with "citation courtesy"). Project joint-position data only, no video |
| `cmu` | `cmu_permissive`, `commercial_ok: true`, acknowledgment text in `ack` | `commercial_ok: yes`, tag `cmu_permissive`, verification `primary_fetched`. Home page: free for all uses, may be included in commercial products, **may not resell the data directly, even in converted form**; acknowledgment text requested. The FAQ page words it differently (copy, modify, redistribute) and the research says to follow the stricter home page | Tags **agree**. Open point: the converted CMU `.npz` files (and a mirror-on-load pipeline) sit in a public repo. Free redistribution is not "resale", but the "even in converted form" clause is a counsel item. The required acknowledgment is in the manifest and `.npz` tags but, as far as this audit checked, **not yet in the README or a model card** |

Tag fields missing from the manifest compared with what the research proposes: `license_url`, `counsel_required`, a `verification` level, and `acknowledgment_text` at manifest level (only inside `.npz` and as `ack`). The research's proposed new classes (`cc_by`, `commercial_license_required`, `needs_counsel`) are not used; MultiSense would map to `needs_counsel` or stay `cc0` with `counsel_required`. Nothing in `unified_refset.py` blocks entries with `commercial_ok: true` and a counsel flag, because no such flag exists.

### Mason handedness / third-party gaps (from the `.npz` tags)

`handedness_verified` is false for three Mason entries:
- `mason_v2_p1_s11` (val split): `handedness_detected: right` (confidence 0.12), stated left, cues disagree (lead arm left, hands side left, finish right). The manifest records it as native left, `commercial_ok` true. README says right-handed clips are other golfers flagged not commercial-safe, so this clip may be mislabelled **or** may not be Mason. **[unverified]**
- `mason_v2_p2_s10` (train, mass 0.072 of 0.6): detected left, stated left, unverified, lead-arm cue says right. **[unverified]**
- `mason_v3_p2_s03_slowmo`: weight 0 in default sampling.

## 3. Which models depend on which sources

`train_imitate.py` hard-codes `track_set="unified_v1"` with `track_weight` 2.0 (recorded in `results/imit*.json` `args`/`env_kwargs_full`). The behaviour-cloning teacher is the scripted config, not the references, so the references enter through the PPO tracking term only (train split). The policies are reported to track the script closely (README, Stage 10), so how much the references shaped the final behaviour is **[unverified]**; the licence exposure exists regardless.

| Model / runs | Depends on `unified_v1` (Mason 0.6 / MultiSense 0.2 / CMU 0.2) | Note |
|---|---|---|
| `imit3_w075_s51/s52/s53`, `imit3_w050_s51/s52` (Stage 10; 4 pass auto_loop) | **Yes**, `track_set: unified_v1` recorded | `imit3_w050_*` record `init_model: None`, so they may or may not descend from the w075 weights **[unverified]**. Both lineages depend on `unified_v1` either way |
| `imit2_w075_s51/s52/s53` | **Yes** | all FAIL on auto_loop |
| `imit_w075_s51/s52/s53` (marked INVALID) | `track_weight` 2.0 recorded, `track_set` **not recorded** | train code on main uses `unified_v1`; not verified at their commit |
| `ppo_v3tiny_*`, `ppo_v3flt_*`, `ppo_v4yaw_*` | No: `style_ref` null, `style_weight` 0 | See `docs/PROVENANCE_AUDIT.md`. Hand-tuned script config origin **[unverified]** |
| `ppo_resid_v3_left_an*`, `left_fast*` | Not in `unified_v1`; Mason-only style terms (see `docs/CHECKPOINT_RELEASE.md`) | Out of scope here |

Consequence: the earlier statements "no recorded run uses CMU or MultiSense" are wrong for Stage 10. README and `docs/CHECKPOINT_RELEASE.md` were updated accordingly. Any release of an `imit*` checkpoint reaches all three sources.

## 4. Needs counsel / needs Mason sign-off

**Needs counsel**
1. MultiSenseGolf: CC0 label vs identifiable participants and consent scope for commercial model training. Also confirm the CC0 text from the record itself (research used a secondary snippet).
2. CMU: whether public redistribution of converted/mirrored CMU `.npz` files in the repo is within "no resale, even in converted form". Reconcile the home-page and FAQ wording.
3. Instagram-derived Mason data: platform terms for using screen recordings of one's own posts, and any third-party content or music in them.
4. Whether publishing checkpoints trained with these references creates any obligations beyond attribution (model cards, derived-data wording). **[unverified]**

**Needs Mason sign-off**
1. Confirm the screen recordings contain only Mason (no other golfers, no coaches or bystanders), especially `mason_v2_p1_s11` and `mason_v2_p2_s10`; confirm handedness, or remove them from `unified_v1`.
2. Agree that derived motion from his swings may be public (repo is already public) and may be encoded in released weights.
3. Approve exclusion or inclusion of val-split entries from any release.

**Engineering follow-ups (no change made)**
- Add the CMU acknowledgment and the MultiSense citation to the README and a future model card.
- Add `counsel_required` and `license_url` to manifest entries; consider a default-deny for entries with unverified handedness or `needs_counsel` sources.
- Record a hash of the manifest and sampling config in each training result (see `docs/PROVENANCE_AUDIT.md`).


## Update: manifest changes (sync2)

- **MultiSense tag:** all 28 `multisense_*_mirrored.npz` entries in `data/reference_sets/unified_v1.json` changed from `license_class: cc0`, `commercial_ok: true` to `license_class: needs_counsel`, `commercial_ok: false`, with new fields `license_class_as_published: "cc0"`, `counsel_required: true` and a `license_note` citing `docs/research_mocap_datasets_licenses.md` and this audit. Set in `data/unified_refset.py` (`MS_LICENSE`). The `.npz` file tags, `data/provenance.py` preset and converter still say `cc0`/`commercial_ok=True`; they were not rewritten. Nothing in sampling reads `commercial_ok`, so training weights and splits are identical (checked: path, split, weight and quality fields are unchanged).
- **LOUD NOTE, unverified Mason clips:** `mason_v2_p1_s11` (val split; detected right-handed, confidence 0.12, may not be Mason) and `mason_v2_p2_s10` (train split, mass 0.072) now carry `handedness_unverified: true` and `exclude_pending_verification: true`. **Sampling does not honor the flags**: dropping them would silently change val scoring (`results/unified_val_style.*`) and train weights behind the recorded imit2/imit3 runs. Decide to exclude or re-verify, then rebuild and rerun. **[unverified]**


## Update: retag, licence annotations and unified_v2 (2026-10-17)

Related docs from the Data Agent (kept as separate files): [`P1_S11_HANDEDNESS_CHECK.md`](P1_S11_HANDEDNESS_CHECK.md) (re-check was inconclusive; needs Mason's confirmation), [`IMPACT_FACE_PATH_AVAILABILITY.md`](IMPACT_FACE_PATH_AVAILABILITY.md) (face angle / club path are not available from current references; proxies in `data/references/mason_impact_face_path_proxies.json` are unverified) and [`TRACKING_REWARD_REFERENCE_GAPS.md`](TRACKING_REWARD_REFERENCE_GAPS.md).

- **Manifest annotations (engineering follow-up above is now done):** `unified_v1.json` entries carry `counsel_required`, `license_url`, `verification`, `no_standalone_resale` / `acknowledgment_required` for CMU, and Mason entries carry `handedness_verified`, `needs_mason_confirmation` and `third_party_content_unreviewed: true`. `commercial_cleared(entry)` = `commercial_ok and not counsel_required`; CMU stays cleared but has an open counsel question on public redistribution of converted files. v1 sampling, splits and weights are unchanged.
- **The `.npz` tags now match the manifest.** The earlier statement that the per-file tags, preset and converter still say `cc0`/`commercial_ok=True` is superseded: `scripts/retag_multisense.py` rewrote all 56 `multisense_*.npz` files (28 raw + 28 mirrored) to `needs_counsel`, `commercial_ok=False`, `license_class_as_published=cc0`, `counsel_required=True`; arrays are asserted identical. Consequence: `ReferenceDataset(commercial_only=True)` and `include_commercial_only` now exclude MultiSense. No recorded run used that filter.
- **Flags honored in a new set:** `unified_v2` excludes the two unverified Mason clips from train and val; `unified_v1` still samples them, so imit2/imit3 remain reproducible. Existing results were not re-evaluated.

> **Update (2026-10, CMU tag audit):** the `cmu` row above describes the manifest tag at audit time (`cmu_permissive`, `commercial_ok: true`). It has since been retagged to `needs_counsel` / `commercial_ok: false` / `counsel_required: true`, in `data/provenance.py`, in all 10 `cmu_64_*.npz` embedded keys and in `unified_v1.json`. Not legal advice.

> **Update 2026-10-18:** the data files this document describes (CMU `cmu_64_*.npz`, `multisense_*`, `mason*.npz`, CaddieSet converter/features JSON, `results/imit_private/` gates, as applicable) were untracked at the tip (`git rm --cached`; held locally; `.gitignore`d). They **remain in git history** (no rewrite). Rows citing them are [data/gate held locally].
