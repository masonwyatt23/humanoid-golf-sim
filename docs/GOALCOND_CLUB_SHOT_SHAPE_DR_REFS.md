# Goal-conditioned refs: 7-iron/wedge specs, launch, shot shape, domain randomization

Data: `data/references/goalcond_club_shot_shape_dr_refs.{json,csv}` (built by `data/build_goalcond_refs.py`),
model: `data/shot_shape_model.py`, tests: `tests/test_goalcond_refs.py`. Sources opened 2026-10-25 (America/New_York).

Conventions (same as `DRIVER_HEAD_460CC_REFS.md`): every row has `label` (measured / spec / rule / derived / model /
estimate / manufacturer claim / gap), `n` (independent published sources or models), `source_url`, `author_date`, and the
claim. n=1 rows are marked "single published spec (n=1)" (or "(n=1)") and are never shown as population ranges.
Aggregates only. Held locally pending counsel (not tracked): per-model (n=1) manufacturer spec rows, the R&A R04 per-site turf rows, and the TrackMan PGA/LPGA tour-average rows (launch, spin, carry). The schema test for the tour averages is skipped for that reason.

## Key values
| Section | Quantity | Nominal | Range | Label | n |
|---|---|---|---|---|---|
| 1 | 7-iron loft / lie | 32 / 62.0 deg | 31-33 / 62-62 | manufacturer spec (aggregate) | 2 / 2 |
| 1 | PW loft / lie / length / SW | 45 / 64.1 / 35.5 in / D2 | 45-46 / 64.0-64.5 / 35.5-35.75 / D2-D3 | manufacturer spec | 3/3/2/2 |
| 1 | Grooves (W, S, depth, A/pitch, edge r) | 0.9 / >=1.905 / 0.508 mm / 0.0762 / 0.254-0.508 | rule | rule | 1 |
| 2 | SW landing (elite) | 22 m/s, 51 deg, 9060 rpm | n=1 | model (USGA sim) | 1 |
| 3 | Start-direction face share | iron 0.75, driver 0.85 | n=1 | manufacturer claim citing TrackMan | 1 |
| 3 | Spin axis | tan(axis)=tan(F2P)/tan(spin loft) | n=1 | model | 1 |
| 4 | Fairway impact-tester COR | 0.35 | 0.34-0.35 | measured | 3 fairways |
| 4 | Fairway stiffness / resilience / penetration | 4.2 MPa / 0.27 / 11.5 mm | 2.2-8.2 / 0.18-0.34 / 8.9-15.4 | measured | 5 sites |
| 4 | Fairway cross-slope max (bent/Bermuda) | 7% level, 4-5% downhill | n=1 | estimate (architect) | 1 |
| 4 | Stance-to-ball variable error at impact, skilled | 10.23 mm (SD 2.48) | n=1 | measured | 1 study (10 golfers) |
| 4 | Segment-mass CV (Clauser) | trunk 4.1%, thigh 8.0%, head 8.2% ... | n=1 | measured (13 cadavers) | 1 |

## Corrections to the brief
- Face dominance is **lower** for irons (about 75%) than for driver (about 85%) in the source opened (Titleist, citing TrackMan).
  The D-plane model gives the same trend (face share 0.96 - 0.0071*Phi: about 0.78 at Phi 25 deg, 0.87 at Phi 13 deg; derived).

## Gaps (not sourced; do not invent)
Iron/wedge CG location and Ixx; sand/lob wedge head mass and MOI; amateur-by-handicap iron/wedge launch tables and 60-75 mph
iron data; measured curvature (yd per deg face-to-path) for irons/wedges; ball-turf friction coefficient (Biber 2023 Table 3
is image-only); rough lie-slope statistics; elite ball-position (address) variance -- only impact-time stance-to-ball VE found.

Lateral sign convention follows TrackMan (positive = right). For a left-handed golfer, mirror path, face and axis.
