# Amateur launch by handicap + wedge CG/mass/MOI refs

Built by `data/build_amateur_launch_wedge_cg_refs.py` -> `data/references/amateur_launch_wedge_cg_refs.{json,csv}` (131 rows committed of 161 built by the Data Agent, schema = goalcond refs). Test: `tests/test_amateur_launch_wedge_cg_refs.py`.

## What is committed
* **Rules-body aggregate:** R&A/USGA R22-01 (May 2019), Tables 5-7, text tables (no chart digitizing). Group means and SDs for male/female, driver and 6-iron, CONGU categories 1-4 only (clubhead speed 52.6-100.5 mph; professional group held, see below). Each row is n=1 (one collated report); the shot count is in `range`. The report found no consistent link between handicap and launch angle or spin.
* **Patent claims:** wedge CG height (claimed ranges 16-20 mm and >=21.335 mm), x-axis MOI >120 kg*mm^2, impact height 10-20 mm.
* No peer-reviewed rows in this file. Betzler 2012/2014 and PMC10877370 were not opened in full.

## Held (not in git)
`<local-path>/held_research_bands/goalcond/amateur_vendor_wedge_HELD.json`: TrackMan amateur averages, per-model wedge MOI/CG, wedge head-mass tables.

## Gaps
Wedge (PW/GW/SW/LW) launch/spin by handicap; 7-iron by handicap (use 6-iron); wedge CG depth; per-loft wedge MOI; wedge head mass in a committable source.

## Held at port (Repo Agent, 2026-10-25)
* R22-01 professional-group rows (26 rows: male/female driver and 6-iron, group 0). The report states the professional male driver group is PGA Tour radar data, i.e. tour averages, which the repo does not carry. Amateur CONGU category 1-4 rows (aggregates with shot counts and attribution, like the committed R22-07 derived rows) are committed.
* The single patent test example (one 54-degree wedge shot, n=1).
* Both held locally at <local-path>/held_research_bands/amateur/ pending counsel; counsel section 11 is held locally too (not in git).
* Three claims from one clubmaker's own technical page (conventional-wedge CG height aggregate, sand-wedge Izz average, toe height) are HELD as vendor-specific pending counsel (<local-path>/held_research_bands/amateur/held_from_8edf73cc_cutter_manufacturer_rows.csv). The four wedge head-mass GAP rows now cite the patent source instead.
