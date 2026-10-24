# Lead-foot vertical GRF: filter spec and peak window (literature notes)

Prepared 2026-10-19 (America/New_York) by the PureGolf Data Agent for the Evaluator. Not committed.
Every number below was read from the fetched page at the URL given. Access: FT = full text read; ABS = abstract only.
Web search was down this session, so sources came from Europe PMC / PMC (open access) only. Paywalled candidates
(Ball & Best 2007/2012, Barrentine 1994, Koenig 1994, Kwon, Nesbit, Lynn & Noffal, Peterson & Wilcox, Utku, Smith & Lewis,
McNally/Queen 2016) were NOT checked and are not cited for any number.

## Table

| # | Citation | URL | Access | GRF filter (type / cutoff / order) | Force-plate rate | Window used for peak | Peak lead vertical GRF | Peak timing |
|---|---|---|---|---|---|---|---|---|
| 1 | Worsfold, Smith & Dyson 2007, JSSM (shoe outsole, natural turf) | https://pmc.ncbi.nlm.nih.gov/articles/PMC3794489/ | FT | **Not stated** (no filter mentioned) | 1000 Hz (Kistler 9851) | Max over swing; also min-to-max range "during the complete swing" | **Driver: 0.84 BW front foot** (back 0.49 BW); 3-/7-iron ~1.1 BW front | "vertical force rising to a maximal in the downswing. After ball impact a rapid decrease in force occurs" |
| 2 | Worsfold et al. 2008, JSSM (low-handicap torque, driver/irons) | https://pmc.ncbi.nlm.nih.gov/articles/PMC3761900/ | FT | Not stated | 1000 Hz | Max over swing | Restates 0.84 BW front (driver) from #1 | — |
| 3 | Worsfold et al. 2009, JSSM (outsole design, driver, hcp 0–19, n=18) | https://pmc.ncbi.nlm.nih.gov/articles/PMC3761538/ | FT | Not stated | 1000 Hz | Fzmax over swing, %BW; note "including baseline of approximately 0.5 BW" | In figure only (not transcribed) | — |
| 4 | Rachnavy et al. 2026 (foot-ground impulse vs clubhead speed) | https://pmc.ncbi.nlm.nih.gov/articles/PMC13111475/ | FT | **4th-order Butterworth, 50 Hz** (kinematics 12 Hz); "follows established methodological standards in golf", checked by residual analysis | 1500 Hz (Kistler 9286BA) | — | not extracted | — |
| 5 | Liu et al. 2026, driver vs 7-iron swing planes | https://pmc.ncbi.nlm.nih.gov/articles/PMC13272296/ | FT | Force plates filtered at **50 Hz** (motion: bidirectional Butterworth 6 Hz; order/direction for GRF not stated) | 1000 Hz (Kistler) | GRFmax "within each swing phase" (phases separated, incl. downswing→follow-through) | not extracted | — |
| 6 | Liu et al. 2025, driver/5-iron/7-iron, college males | https://pmc.ncbi.nlm.nih.gov/articles/PMC12416643/ | FT | GRF filter not stated (motion: bidirectional Butterworth 6 Hz) | 1000 Hz | Time series normalised takeaway→impact | %BW in figures only | "vertical GRF of the left [lead] foot reached its maximum near HD" (a downswing event before impact) |
| 7 | Lin et al. 2023, downswing lower-limb, knee-injury history | https://pmc.ncbi.nlm.nih.gov/articles/PMC10215287/ | FT | 4th-order Butterworth low-pass, **6 Hz** (stated for "selected data"; applies to kinematics+kinetics) | 1000 Hz (AMTI) | Downswing only | — | Max GRF occurs "slightly after" club vertical in downswing (before impact) |
| 8 | Chen et al. 2024, overhead squat & lumbar loads | https://pmc.ncbi.nlm.nih.gov/articles/PMC10893031/ | FT | 4th-order Butterworth low-pass, **14 Hz** (kinematics and GRF) | 1000 Hz (AMTI) | Downswing | — | — |
| 9 | Harada et al. 2023, golf after THA | https://pmc.ncbi.nlm.nih.gov/articles/PMC10227076/ | FT | Butterworth, **12 Hz** for GRF (order not stated) | 1000 Hz (AMTI) | — | — (clinical population) | — |
| 10 | Li et al. 2026, IMU GRF prediction | https://pmc.ncbi.nlm.nih.gov/articles/PMC13023547/ | FT | 4th-order Butterworth low-pass, **6 Hz** for GRF | 2400 Hz (Kistler) | Swing normalised 0–100% | — | — |
| 11 | Queen et al. 2013, J Strength Cond Res (n=28, hcp <9 vs >9) | https://europepmc.org/article/MED/23222089 | ABS | unknown | unknown | Peaks reported **per phase**: address→top, **top→ball contact**, contact→end of follow-through | unknown | Low-handicap golfers had earlier peak vertical force timing |
| 12 | Han et al. 2019, Sports Biomech (n=63, hcp ≤3, driver/5-iron/PW) | https://europepmc.org/article/MED/31042142 | ABS | unknown | unknown | — | unknown | Lead-foot loading is critical "near" lead arm parallel to the ground (downswing, before impact) |

## (a) Filter: no consensus
- Where stated, it is always a Butterworth low-pass. Order 4 when the order is given (#4, #7, #8, #10).
- Cutoffs for GRF vary by ~8×: 6 Hz (#7, #10), 12 Hz (#9), 14 Hz (#8), 50 Hz (#4, #5). Zero-lag/bidirectional is stated only for kinematics (#5, #6), not explicitly for GRF.
- The low cutoffs (6–14 Hz) come from studies feeding inverse dynamics, where GRF is filtered to match the markers. Papers reporting GRF peaks themselves use 50 Hz (#4, #5) or report no filter (#1–3).
- Sampling: 1000 Hz is standard (7 of 10 FT papers); 1500 and 2400 Hz also seen.
- Confidence: high that there is no single standard; medium that 4th-order Butterworth at 50 Hz is the most defensible choice for peak reporting.

## (b) Window and timing
- Every source that gives timing puts the lead-foot vertical peak **in the downswing, before impact** (#1, #6, #7, #12), with a "rapid decrease" after impact (#1). Queen 2013 (#11) reports top→contact as its own phase.
- The Worsfold driver value (0.84 BW, #1) is a max over the whole recorded swing. Because force falls after impact, that max is in practice the downswing value.
- I found **no fetched source for the 1.7 BW upper end** of the current 0.8–1.7 BW band. Only 0.84 BW (driver, turf, #1) and ~1.1 BW (irons, #1) were confirmed. Treat the upper bound as unverified.
- No source gave the peak's offset from impact in ms or as a % of the downswing. Only qualitative events were given (near lead-arm parallel / HD / just after club vertical).
- Confidence: medium-high that the peak falls before impact; low on any numeric offset.

## Recommendation for the harness
1. **Window:** top of backswing → impact, plus a small margin of up to ~20 ms (my choice for event-detection jitter, not from literature). Supported by #1, #6, #7, #11, #12.
2. **Filter:** 4th-order zero-lag (filtfilt) Butterworth low-pass, 50 Hz cutoff, on vertical GRF before taking the peak (follows #4/#5; zero-lag is my choice so the peak isn't shifted in time). Optionally report a 12–14 Hz sensitivity value, because the lower cutoff lowers the peak.
3. **Fallback (≥3 consecutive 2 ms samples above threshold = 6 ms persistence):** no paper uses it. It rejects single-sample spikes the way a ~50 Hz low-pass would (period at 50 Hz is 20 ms, so 6 ms is more permissive). It is consistent in spirit, but it is a harness heuristic, not a literature method. Prefer the filter, and keep the fallback only as a secondary guard.
4. Keep the band's 1.7 BW upper limit labelled PROVISIONAL/unverified until a full-text source is found (Ball & Best, Barrentine, Koenig were not accessible here).
