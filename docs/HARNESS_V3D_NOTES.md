# Harness v3d (opt-in `--harness v3d`; v3c stays the default until reviewed)

Orchestrator-approved for implementation 2026-10-24. Source: the Trainer band check (a Trainer band-check note held locally, not in this repo, copied verbatim below).
v3d re-grades the SAME v3c episodes (`eval/harness_v3d.py`, a pure function of the recorded values), so a v3c JSON can be re-graded without re-simulating.

| # | rule | v3c | v3d | label |
|---|---|---|---|---|
| 1 | shot spin (deterministic row and robustness median/p10/p90) | PASS 1800-3000, WARN 1200-4000 | PASS 2000-3700 rpm when club speed is 70-85 mph (else v3c band); WARN 1200-4000 unchanged | DERIVED: envelope of TrackMan 2010 optimizer rows 75-85 mph (1964-3722); USGA/R&A R22-01 measured means 2671-3202 inside |
| 2 | pelvis peak angular velocity | 403 x [0.7,1.3] (extrapolated, WARN-capped) | PASS >= 250 deg/s, WARN below; info target ~340 | DERIVED: Cheetham 2008 amateur 395 +- 68 (mean - 2 SD = 259 at 88 mph), lowered for ~74 mph; Lynn 2013 within-group r ~ 0.02 |
| 3 | kinematic sequence order + timing | strict order; each peak 15-110 ms before club | pelvis first and >= 15 ms before club (design choice); thorax/arm tie or inversion up to 30 ms allowed; REQUIRE arm >= 20 ms before club (else WARN, which blocks a PASS verdict); peaks <= 150 ms | DERIVED: Cheetham 2008 amateur arm 64 +- 23 ms (64 - 2x23 = 18); pros thorax 68 / arm 65 ms; amateurs pelvis 78 +- 38 |
| 4 | lead-foot slip / rotation | PROVISIONAL | unchanged, PROVISIONAL (no sourced numbers) | - |
| 5 | robustness gate | contact / start-dir / foot / shot bands | + FAIL if club speed p10 < 0.93 x median | LOW CONFIDENCE: Shaw et al. 2023 JSCR abstract (CV <= 5.8% within session, doi 10.1519/jsc.0000000000004554); elite SD 0.5-2.1 mph from a search snippet only |

Info flag: if the v3d verdict is PASS but the same row re-graded with the v3c spin band is not, the verdict is `not a pass (spin-band-only)`.

Regression: `tests/test_harness_v3d.py` checks that the v3c spin fallback reproduces every recorded v3c spin status (deterministic and robustness percentiles) on the local v3c JSONs.

## Source notes (Trainer band check, verbatim)

# Trainer v3 realism band check (2026-10-24, America/New_York; not committed)
Sources read this pass: Cheetham et al. 2008 FULL TEXT (Table 1) https://waddengolfacademy.com/biomechanics/Cheetham%20Rose%20Neal%20Comparison_of_Kinematic_Sequence.pdf ;
repo kseq-v2 (origin/main data/references/kinematic_sequence_torque_reference_v2.json — file is NOT in the local working tree, read via git show); driver_70_85mph_launch_rows.csv; dispersion_and_lead_foot_NOTES.md.
realism/ directory not present in the working tree (not checked). Policy values (4062 rpm, 254 deg/s, p10 59.6 mph) taken from the brief, not verified.

## 1. Spin 1800–3000 rpm at ~74 mph — VERDICT: upper bound too tight; 4062 still out of band
Measured means (USGA/R&A R22-01, TrackMan, range sessions, means incl. mishits): 68.4 mph 2671; 77.0 mph 2784; 85.8 mph 3202 rpm (measured, full text, URLs in driver_70_85mph_launch_rows.csv).
Model/optimizer: TrackMan 2010 fitting chart AoA −5…+5: 75 mph 1976–3722; 80 mph 2005–3652; 85 mph 1964–3669. Foresight optimized table: 69 mph 2500–3500, 76 mph 2400–3400, 83 mph 2300–3300 (model/reference).
- 3000 cap excludes a measured mean (3202 @ 85.8) and the TrackMan carry-optimal AoA −5 rows (~3650–3720).
- PROPOSED speed-matched band 70–85 mph: 2000–3700 rpm (envelope of TrackMan optimizer rows; measured means inside). DERIVED from cited rows, not a published band. Optional soft target 2400–3300.
- 4062 is ~10% above every sourced value at this speed → keep failing. No per-shot spin SD found for 70–85 mph players, so no sourced tolerance beyond the envelope.

## 2. Pelvis peak angular velocity at 70–85 mph (policy 254 deg/s) — VERDICT: low; borderline vs amateur −2 SD
Measured (full text unless noted):
- Cheetham 2008: amateurs (CHS 88±5 mph, n=19) 395±68 deg/s; pros (109±3 mph) 477±53. Pelvis = superior-inferior axis component, Polhemus 240 Hz, unfiltered. (PMC3362989 misquotes amateur SD as 53; table says 68.)
- Lynn 2013 (5-iron): recreational (87.7 mph) 398.8±69.4; elite (92.2 mph) 427.8±69.9; within-sample r(peak pelvis, CHS)=0.017 (n.s.). https://www.golfsciencejournal.org/article/4979.pdf
- Callaway 2012 (7/8-iron, K-Vest, CHS n/r): high-hcp 380.1, low-hcp 503.2. https://pmc.ncbi.nlm.nih.gov/articles/PMC3362989/
- Madrid 2020 hip-line ON-PLANE 394±62 @110.4 mph (different definition; not comparable directly).
Scaling (DERIVED): Cheetham between-group slope (477−395)/(109−88) ≈ 3.9 deg/s per mph → ~340 deg/s at 74 mph; within-group correlation is ~0 (Lynn), so speed is a weak predictor. No source has pelvis speeds for golfers below ~85 mph.
- Proposal: soft target ~340 (derived); gate floor 250 deg/s (Cheetham amateur mean −2 SD = 259 at 88 mph, lowered for 74 mph — derived). 254 sits at the floor: pass-but-flag, not fail.

## 3. Kinematic-sequence timing band 15–110 ms between peaks — VERDICT: 15 ms minimum is NOT supported for thorax→arm; club-with-arm is unrealistic
Cheetham 2008 time of peak before impact (ms): pros pelvis 87±19, thorax 68±14, arm 65±8; amateurs pelvis 78±38, thorax 59±29, arm 64±23 (amateur mean order pelvis, ARM, thorax). Club peak ≈ impact by their definition (discussion text).
Madrid 2020: hip 87±18, shoulder 84±25, upper lever 73±6 ms; "hip, shoulder and upper-lever peaks fall in a 14 ms window" (kseq-v2 note).
Implied gaps (DERIVED from means): pelvis→thorax 19 ms (pro), 3 ms (Madrid); thorax→arm 3 ms (pro), −5 ms (amateur), 11 ms (Madrid); arm→club ≈ 65 ms (pro), 64 ms (amateur), 73 ms (Madrid).
- Thorax and arm peaking together is NORMAL (even pros). Drop the 15 ms floor for pelvis→thorax and thorax→arm; allow 0 ms and, for amateur-realism, thorax/arm inversion up to ~30 ms (amateur SDs 23–29).
- Club peaking with the arm is NOT realistic: arm→club ≥ ~20 ms (amateur mean 64 − 2×23 = 18, derived), typical 50–80. Require pelvis peak ≥ ~15 ms before club and club peak within ~10 ms of impact (design choice, not sourced).
- 110 ms upper bound: fine for arm→club (pro 65±8); pelvis peak up to ~150 ms before impact occurs in amateurs (78±38).

## 4. Lead-foot slip / rotation on turf top→impact — VERDICT: NO SOURCED NUMBERS
Searched again this pass; still no published measurement of lead-foot linear slip (mm) or foot rotation (deg) top→impact. Related only: Worsfold 2008 shoe–turf vertical-axis torque front foot 17–19 N·m driver (https://pmc.ncbi.nlm.nih.gov/articles/PMC3761900/); Meister 2011 free moment 0.83–1.19 N·m/kg (5-iron). Any slip band stays PROVISIONAL / sim-tuned.

## 5. Club-speed variability within a golfer (p10 59.6 mph) — VERDICT: sourced human variability is small (~1–3%)
- Elite golfers, repeated driver trials: individual CHS SD 0.24–0.96 m/s = 0.5–2.1 mph ("Driving Performance Variability Among Elite Golfers", Science & Golf proceedings, https://doi.org/10.1007/978-2-287-99054-0_46 — read via search snippet of chapter text only; DOI fetch 404'd; treat as snippet-level).
- Shaw et al. 2023 JSCR (abstract): within-session driver CHS CV ≤ 5.8% (upper bound across variables incl. CI), talented golfers, 3 shots. https://doi.org/10.1519/jsc.0000000000004554
- Implication (DERIVED, assumes policy mean ≈ 74 mph): p10 59.6 implies SD ≈ 11 mph (CV ≈ 15%), 5–20× human within-golfer SD. A sourced robustness target: p10 ≥ mean − 1.28×(0.03×mean) ≈ 0.96×mean (≈71 mph at 74). Amateur data are scarcer; 5.8% CV gives ≈ 0.93×mean as a lenient floor.

## Strike offset rows (added 2026-10-24, Orchestrator-approved)

Approval: the Humanoid Golf Orchestrator approved option (a) of the spin-audit review on Oct 24, 2026: strike dy/dz info rows plus a
provisional strike-height row (WARN beyond 15 mm, FAIL at the face edge).

* The v3 worker (`results/overnight/_j_worker_gp_v3.py`) records `strike = {dy_m, dz_m}` per episode (deterministic and robustness) from the
  env's impact record (`v5_golf_env._do_contact`: offset of the contact point from the `clubhead` site, i.e. the face centre; dy toward the toe,
  dz up the face). Same values the env returns as `info['dy']` / `info['dz']`.
* **INFO rows, all v3 harnesses (v3b/v3c/v3d):** `mine/strike_dy_info`, `mine/strike_dz_info` — median / p10 / p90 in mm, deterministic and
  robustness episodes, plus deterministic median |dz|. Not gating; P/W/F counts and v3c verdicts are unchanged. Absent when the run predates the field.
* **v3d only, GATING, PROVISIONAL:** `mine/strike_height` on the deterministic median |dz|:
  PASS ≤ 15 mm, WARN > 15 mm, FAIL ≥ 32 mm.
  * **15 mm is a design choice, not sourced.**
  * **32 mm face edge = sim geometry, not a real-driver source:** `env/models/humanoid_golf_v5_g1_lh.xml` and `..._rh.xml`, line 271,
    `<geom name="head" size="0.045 0.055 0.032" type="box">` → half-height 0.032 m (half-width toward toe 0.055 m). The `clubhead` site
    (line 274) sits at the head-box face centre (verified: in the head-geom frame it is at (+0.0450, 0.0000, 0.0000) m).
* Evidence: the golfphys spin-audit review (Oct 24) — at seed 4000, K30a 300k struck 25 mm low (4455 rpm vs ~2631 centred) and K30b 400k
  31 mm low (4660 rpm vs ~2449 centred); K25b 400k 8 mm low. Strikes this far down sit at the edge of the sim face, where the vendored
  golfphys model barely loses ball speed (so the spin penalty's size is itself uncertain).
* The face-edge threshold lives in ONE constant, `eval/harness_v3d.py: STRIKE_FACE_EDGE_MM` (default 32.0 = sim head-box half-height).
  The Data Agent's sourced 53 mm face height (→ 26.5 mm half-height) is UNDER REVIEW and NOT adopted; switching would change only that constant.

## Face-edge extension (Orchestrator-approved 2026-10-24, v3d only; v3c verdicts unchanged)

* `STRIKE_FACE_EDGE_MM = 26.5` (= 53/2): **measured spec, single brand (Wishon 919THI 53x105 mm), provisional** (replaces the 32 mm sim-geometry
  default). `mine/strike_height`: FAIL on deterministic median |dz| ≥ 26.5 mm, WARN > 15 mm (design choice, not sourced).
* INFO rows: `mine/strike_within_sim_box_info` (|dz| ≤ 32 mm sim head-box half-height; sim geometry) and `mine/strike_outside_measured_info`
  (|dz| > 12.7 mm, outside measured Hotstix data).
* Side-by-side ball model (never the default): Data Agent commit ec675dd (branch golfphys-face-edge-refs) cherry-picked here as bf85b8b —
  `data/driver_face_offcentre.py:face_edge_adjust()`, `docs/DRIVER_FACE_OFFCENTRE_REFS.md`, `data/references/driver_face_offcentre_refs.*`.
  Per episode the v3 worker re-runs the env's own golfphys `shot_from_contact` with the same club velocity, face normal and dy but **dz = 0**
  (centre strike; recorded as `strike.centre`, `dz_used_m = 0`), then `eval/harness_v3d.face_edge_eval` applies `face_edge_adjust` with the real dz.
  Guard: `face_edge_eval` raises ValueError unless the input is a centre strike (`dz_used_m == 0`), so the off-centre effect is never counted twice.
  Two variants: CAPPED (±12.7 mm saturation, as written) and LINEAR (extrapolated). INFO rows `mine/spin_face_edge_capped_info` /
  `mine/spin_face_edge_linear_info` carry spin, launch, smash, ball speed, carry and total/carry (golfphys_total re-flight), deterministic + robustness.
* Verdict rule: under the model, spin passes only if BOTH capped and linear pass (`face_edge_model` in the v3d JSON). A result that would PASS
  only under the model is reported as **'not a pass (face-edge-model-only)'** (`face_edge_model_only = true`), like the spin-band-only flag.
* Labels: 148 mph is a MODEL value (TrajectoWare); smash LOW confidence; leveling off beyond 12.7 mm is UNVERIFIED until R22-07 Fig 1 is read;
  51.3 rpm/mm and 0.201°/mm are DERIVED from measured Hotstix data (secondary source).
* Check: K30a 300k seed 4000 — real strike dz −25.4 mm → env spin 4455 rpm; centre re-run (dz = 0) → 2688 rpm.
