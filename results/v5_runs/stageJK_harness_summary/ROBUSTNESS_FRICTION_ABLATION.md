# Robustness friction ablation (INFO only), 2026-10-19

The default `mine/robustness` gating rule is unchanged (harness ae026ab: friction_rand ON, U(0.5, 1.2)). This file is information only.
Same seeds 7000..7023 and the same perturbations in every variant: joint angles U(+-1.5 deg), joint velocities U(+-0.05 rad/s), ball xy U(+-1 cm).
I checked that the joint-noise draws are identical across variants (episode 0 max 1.406 deg, episode 1 max 1.451 deg).
The friction-range variants draw floor mu in the worker from a separate rng(seed + 0xF41C), set through env var `V3_FRICTION_RANGE`.
Runner: `_run_robust_friction_ablation.py`. Raw JSONs are kept outside git in `<local-path>

**Nominal correction:** the true model floor mu is **1.000** (`env/v5_body.py:86`, `g.friction = [1.0, 0.005, 0.0001]`), and every friction-off episode measured 1.000.
The value 0.978 recorded as `floor_mu_nominal` in the v3 JSONs is wrong. The worker reads it once at construction, before any episode reset; it is most likely one random draw rather than the model value.
So the requested "+-10% of 0.978" range (0.88-1.08) is off-centre. I also ran a true +-10% range (0.90-1.10).

| ckpt | friction | verdict | contact | start-dir pass | foot pass | spin med / p10 / p90 | t/c med / p10 / p90 | contact misses at mu |
|---|---|---|---|---|---|---|---|---|
| K22r5_s51 100k | U(0.5,1.2) [gate] | FAIL | 0.833 | 0.583 | 0.792 | 4028 / 1802 / 4842 | 1.365 / 1.290 / 1.961 | 0.58, 0.63, 0.63, 0.67 |
| K22r5_s51 100k | off (1.000) | FAIL | 1.000 | 0.833 | 0.958 | 3969 / 1286 / 4774 | 1.369 / 1.266 / 3.143 | none |
| K22r5_s51 100k | U(0.880,1.076) | FAIL | 1.000 | 0.833 | 1.000 | 3816 / 1145 / 4618 | 1.373 / 1.276 / 3.143 | none |
| K22r5_s51 100k | U(0.90,1.10) | FAIL | 1.000 | 0.875 | 0.958 | 3748 / 1320 / 4900 | 1.355 / 1.293 / 3.232 | none |
| K19a_s39 400k | U(0.5,1.2) [gate] | FAIL | 0.792 | 0.792 | 0.458 | 3732 / 2468 / 4350 | 1.389 / 1.282 / 1.451 | 0.58, 0.63, 0.63, 0.65, 0.67 |
| K19a_s39 400k | off (1.000) | FAIL | 1.000 | 0.833 | 0.542 | 3310 / 1176 / 4140 | 1.393 / 1.285 / 3.320 | none |
| K19a_s39 400k | U(0.880,1.076) | FAIL | 1.000 | 0.833 | 0.542 | 3460 / 1378 / 4247 | 1.377 / 1.298 / 2.023 | none |
| K19a_s39 400k | U(0.90,1.10) | FAIL | 1.000 | 0.792 | 0.542 | 3373 / 1245 / 4073 | 1.391 / 1.294 / 2.927 | none |

Requirements: contact >= 0.95, start-dir >= 0.90, foot >= 0.90; for each shot metric the median must be inside the PASS/WARN band and p10-p90 inside the WARN band.
Spin WARN band is 1200-4000 (PASS 1800-3000); t/c FAIL is above 1.35 (PASS 1.04-1.25).

**Reading**
- **Friction explains the contact misses only.** All contact misses happen at mu 0.58-0.67; with mu at or near nominal, contact is 24/24.
- **Both still FAIL without wide friction:**
  - The t/c median stays at 1.36-1.39, above the 1.35 limit, in every variant.
  - Start-dir pass stays at 0.79-0.88, below 0.90.
  - Spin p90 stays above 4000 in every variant.
  - K19a foot pass stays at about 0.54.
  - These come from the joint and ball noise, not from friction.
- **t/c p90 gets worse** with friction narrowed (up to 3.1-3.3), because episodes that used to miss now make contact as weak strikes.

**Where the 0.5-1.2 range comes from:** it is a hard-coded training randomization, not a documented turf value.
- **The draw:** `env/v5_golf_env.py:148-149` (Trainer 49de3ef and 1f4aebc), `self.m.geom_friction[self.floor, 0] = self.rng.uniform(0.5, 1.2)  # foot/floor sliding friction randomisation`. It was introduced in Trainer commit 6d3f397, 2026-10-18 00:11 EDT, "v5 Stage A: soft pelvis tether, friction rand, ...".
- **Where it was used:** only the Stage A trainer turns it on, `train/v5_train.py:20` (`V5GolfEnv(..., friction_rand=True, ...)`).
- **The J trainer turns it off:** `train/v5_train_j.py:24` (JEnv init) and `:140` (curriculum eval env) set `friction_rand = False`. So K19a and K22r5 were trained at fixed mu = 1.0, and the 0.5-1.2 range is out-of-distribution for them.
- **No turf source anywhere:** the only documentation is `docs/FROM_SCRATCH_SWING_PLAN.md:68`, "Ground plane friction `1.0 0.005 0.0001` for shoes [guess; typical turf/rubber ~0.6-1.0]", and `:173`, which proposes foot-friction randomization to help balance early in training. No turf source appears in docs/, configs, config.yaml or README.
