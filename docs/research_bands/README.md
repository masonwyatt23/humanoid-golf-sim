# Research bands (public sources only)

Launch-monitor rows and realism-gate bands collected for the realism harness. Every CSV row carries a source `url` and a `measurement_type` label (MEASURED / model or optimizer output / DERIVED or computed). Labels such as PROVISIONAL and the confidence notes are kept as written.

| File | Contents |
|---|---|
| `data/references/research_bands/slow_speed_driver_total_carry.csv` | 23 driver rows (numeric club speeds 62.6–100.5 mph; total/carry); 30 TrackMan 2010 chart rows held back (below). Evaluator verification of the full 53-row set: 52/53 verified, 1 partial. |
| `data/references/research_bands/driver_70_85mph_launch_rows.csv` | 12 rows reused from the slow-speed set with an `in_70_85_window` flag; 18 TrackMan 2010 chart rows held back. No new rows. |
| `docs/research_bands/turf_friction_NOTES.md` | Golf-shoe / turf friction sources for the robustness gate. |
| `docs/research_bands/grf_filter_window_NOTES.md` | Filtering and window for peak lead vertical GRF. |
| `data/references/research_bands/driver_dispersion_bands.csv` | Launch direction and lateral landing dispersion (PROVISIONAL gate band). |
| `data/references/research_bands/lead_foot_plant_bands.csv` | Lead-foot plant evidence (mostly kinetic, not displacement; PROVISIONAL band). |
| `docs/research_bands/dispersion_and_lead_foot_NOTES.md` | Notes for the two CSVs above. |

## Attribution and licensing
- The numbers are cited facts from the listed public sources, each linked per row. Rights in the source documents stay with their owners.
- The project's MIT license covers only this project's own text, code and computed columns, not the source documents.
- **TrackMan Driver Fitting Chart 2010 rows are held back, pending review.** The MIT/provenance audit flagged rows transcribed from that chart as an open counsel question, so they are not in these CSVs (18 rows from `driver_70_85mph_launch_rows.csv`, 30 from `slow_speed_driver_total_carry.csv`). The two notes files for these CSVs (`slow_speed_driver_total_carry_NOTES.md`, `driver_70_85mph_launch_rows_NOTES.md`) quote chart values throughout, so they are held back too. Both the rows and the notes are kept locally and will be added only after review.
- No Instagram-derived, private, CMU or MultiSense data is included.
