# Provenance audit: training args recorded in committed results

Engineering diligence, generated from the committed `results/*.json` by `scripts/audit_provenance.py` (read-only). **Missing values are reported as missing and were not guessed.** Scope: `ppo_v3tiny_*`, `ppo_v3flt_*`, `ppo_v4yaw_*` and `imit`/`imit2`/`imit3` runs (20 run files). Older `ppo_resid_v3_*` runs are out of scope here (see `docs/CHECKPOINT_RELEASE.md`).

## What each run JSON records

- `results/<run>.json` has an `args` block (CLI arguments as parsed) and a short `git_head`. Seeds, `force_scale`, `res_scale`, `carry_cap`, reward weights and `style_ref`/`style_weight` (PPO runs) are recorded there. Runs from `train_imitate` (`imit2`, `imit3`) also record `env_kwargs_full`, which includes `track_set`, `track_weight`, `force_scale`, `tempo_scale`, `model_xml` and the script config.
- `results/gate_<run>.json` records the evaluation environment (`env_kwargs`), episodes and seed (4000), not the training args and not a git commit. For the `imit*` gate files `env_kwargs.track_set` is `null`: evaluation does not use the tracking term, so the reference set is **not** recorded there.
- Nothing records a hash of the reference manifest (`data/reference_sets/unified_v1.json`) or of the checkpoint `.zip`. The checkpoints are gitignored and not committed, so a result JSON cannot be tied to a specific weights file.

## Completeness criteria

A run has **complete provenance** only if it has: an args block, a seed, a git commit that resolves to a commit on main, a recorded reference field (`style_ref`/`track_set`, or an explicit none), the env flags (`force_scale`, `tempo_scale`) and a gate JSON. Under that definition **no run is fully complete**, for the shared reasons below, plus per-run gaps in the table.

## Findings

1. **`git_head` is not an ancestor of main for any of the 20 runs.** All hashes exist in the local object store, but they come from the pre-reconciliation working clone (history later re-applied onto origin/main as new commits). So `git checkout <git_head>` on a fresh clone of main will not work. Matching them to main commits would be a guess by commit subject; it was not done. Whether the working tree was dirty when each run started is not recorded.
2. **No reference-manifest hash.** `imit2`/`imit3` record `track_set: unified_v1` by name only. On current main `data/reference_sets/unified_v1.json` has a single commit (`c4a3b05`), but because each run's `git_head` is not on main (finding 1) it cannot be shown that the manifest the run read equals the current one. The sampling config and weights come from `unified_v1_sampling.json`, also not hashed.
3. **No checkpoint hash.** The `models/*.zip` files are gitignored; no md5/sha is recorded anywhere in `results/`.
4. **`imit_w075_s51/52/53` (marked INVALID in the notes)** have only an `args` block (no `env_kwargs_full`), so `track_set` is not recorded. `train/train_imitate.py` on main hard-codes `track_set="unified_v1"`, but whether it did at their `git_head` was not checked, so this is not asserted for them. They are excluded from pass counts anyway.
5. **`ppo_v3tiny_s21/22/23` do not record `tempo_scale`**; the key is absent from their args (not evidence of 0.0, so not filled in). They also differ from v3flt/v4: `analytic_ball` true, `lat_angular` true, `carry_cap` 160.
6. **`imit3_w050_s51/52` record `init_model: None`**, so the chain from the w075 stage (the stage-advance step of `auto_loop.py`) is not captured in the args file. Lineage would have to come from the loop log or commit messages.
7. **Only the latest attempt of a run name is stored.** `results/` holds one JSON per run name, while `TRAINING_NOTES.md` lists repeated attempts of `imit*` runs with different results (for example two attempts each of `imit2`). The attempt a given `git_head` and args belong to cannot be told from the JSON alone.
8. **Stage 9 `ppo_v4yaw_*`** args record `contact_damp` 0.3 and an `impact_model` (gain 1.28, dz0 -0.019, k_off 0.4, spin_k 130, k_side 3500) and `t_down` 0.065. These are the hypothetical 128 mph tier (see README); the recorded values match the label.
9. **No real-motion references in `ppo_v3tiny`, `ppo_v3flt`, `ppo_v4yaw`.** `style_ref` is null and `style_weight` 0 in every args block. That supports "no reference data in the training objective" for these runs. It does not show that the scripted base config (`configs/fast_scripted_v3.json`, hand-tuned) was never tuned using data from the repo's references. Origin of that tuning is **unverified**.

## Per-run table

| Run | Seed | `git_head` (not on main) | force_scale | tempo_scale | Reference data in training | Gate JSON (gate_pass) | Missing / not recorded |
|---|---|---|---|---|---|---|---|
| `imit2_w075_s51` | 51 | `eaf8b62` | 2.0 | 0.0 | track_set=`unified_v1` (name only), track_weight 2.0 | yes (true) | git_head not an ancestor of main; manifest hash; checkpoint hash |
| `imit2_w075_s52` | 52 | `1700f6a` | 2.0 | 0.0 | track_set=`unified_v1` (name only), track_weight 2.0 | yes (false) | git_head not an ancestor of main; manifest hash; checkpoint hash |
| `imit2_w075_s53` | 53 | `c2676bd` | 2.0 | 0.0 | track_set=`unified_v1` (name only), track_weight 2.0 | yes (false) | git_head not an ancestor of main; manifest hash; checkpoint hash |
| `imit3_w050_s51` | 51 | `281a3ed` | 2.0 | 0.0 | track_set=`unified_v1` (name only), track_weight 2.0 | yes (true) | git_head not an ancestor of main; manifest hash; checkpoint hash; init_model None (lineage from w075 stage not recorded) |
| `imit3_w050_s52` | 52 | `34bdeb9` | 2.0 | 0.0 | track_set=`unified_v1` (name only), track_weight 2.0 | yes (true) | git_head not an ancestor of main; manifest hash; checkpoint hash; init_model None (lineage from w075 stage not recorded) |
| `imit3_w075_s51` | 51 | `1892aa8` | 2.0 | 0.0 | track_set=`unified_v1` (name only), track_weight 2.0 | yes (true) | git_head not an ancestor of main; manifest hash; checkpoint hash |
| `imit3_w075_s52` | 52 | `1892aa8` | 2.0 | 0.0 | track_set=`unified_v1` (name only), track_weight 2.0 | yes (true) | git_head not an ancestor of main; manifest hash; checkpoint hash |
| `imit3_w075_s53` | 53 | `faeb127` | 2.0 | 0.0 | track_set=`unified_v1` (name only), track_weight 2.0 | yes (false) | git_head not an ancestor of main; manifest hash; checkpoint hash |
| `imit_w075_s51` | 51 | `1288344` | None | not recorded | track_weight 2.0 in args; **track_set not recorded** (no `env_kwargs_full`) | yes (false) | track_set; tempo_scale; git_head not an ancestor of main; manifest hash; checkpoint hash |
| `imit_w075_s52` | 52 | `845d2af` | None | not recorded | track_weight 2.0 in args; **track_set not recorded** (no `env_kwargs_full`) | yes (false) | track_set; tempo_scale; git_head not an ancestor of main; manifest hash; checkpoint hash |
| `imit_w075_s53` | 53 | `1288344` | None | not recorded | track_weight 2.0 in args; **track_set not recorded** (no `env_kwargs_full`) | yes (false) | track_set; tempo_scale; git_head not an ancestor of main; manifest hash; checkpoint hash |
| `ppo_v3flt_all_s33` | 33 | `a56eb96` | 2.0 | 0.02 | none (`style_ref` null, `style_weight` 0) | yes (false) | git_head not an ancestor of main; manifest hash; checkpoint hash |
| `ppo_v3flt_yaw_s31` | 31 | `a56eb96` | 2.0 | 0.0 | none (`style_ref` null, `style_weight` 0) | yes (true) | git_head not an ancestor of main; manifest hash; checkpoint hash |
| `ppo_v3flt_yaw_s32` | 32 | `a56eb96` | 2.0 | 0.0 | none (`style_ref` null, `style_weight` 0) | yes (true) | git_head not an ancestor of main; manifest hash; checkpoint hash |
| `ppo_v3tiny_s21` | 21 | `fc1f106` | 2.0 | not recorded | none (`style_ref` null, `style_weight` 0) | yes (false) | tempo_scale; git_head not an ancestor of main; manifest hash; checkpoint hash |
| `ppo_v3tiny_s22` | 22 | `fc1f106` | 2.0 | not recorded | none (`style_ref` null, `style_weight` 0) | yes (false) | tempo_scale; git_head not an ancestor of main; manifest hash; checkpoint hash |
| `ppo_v3tiny_s23` | 23 | `fc1f106` | 2.0 | not recorded | none (`style_ref` null, `style_weight` 0) | yes (false) | tempo_scale; git_head not an ancestor of main; manifest hash; checkpoint hash |
| `ppo_v4yaw_s41` | 41 | `f06e61d` | 2.0 | 0.0 | none (`style_ref` null, `style_weight` 0) | yes (true) | git_head not an ancestor of main; manifest hash; checkpoint hash |
| `ppo_v4yaw_s42` | 42 | `f06e61d` | 2.0 | 0.0 | none (`style_ref` null, `style_weight` 0) | yes (true) | git_head not an ancestor of main; manifest hash; checkpoint hash |
| `ppo_v4yaw_s43` | 43 | `f06e61d` | 2.0 | 0.0 | none (`style_ref` null, `style_weight` 0) | yes (true) | git_head not an ancestor of main; manifest hash; checkpoint hash |

`manifest hash` and `checkpoint hash` are missing for every run; they are listed per row for completeness.

## Recommendations (no code change made)

- Have `train_residual.py` / `train_imitate.py` write the full `git describe --dirty`, the sha256 of the reference manifest and sampling config, and the sha256 of the saved checkpoint into the result JSON.
- Have `auto_loop.py` record the attempt number and the `init_model` path for each stage.
- Make `eval_gate.py` copy the training run's `git_head`/args reference into the gate JSON.
- Regenerate this table with `python scripts/audit_provenance.py --json`.

> **Update 2026-10-18:** the data files this document describes (CMU `cmu_64_*.npz`, `multisense_*`, `mason*.npz`, CaddieSet converter/features JSON, `results/imit_private/` gates, as applicable) were untracked at the tip (`git rm --cached`; held locally; `.gitignore`d). They **remain in git history** (no rewrite). Rows citing them are [data/gate held locally].
