# Golf shoe – turf friction (μ) notes  (PureGolf Data Agent, 2026-10-19 ET)
Not committed. Verified public sources only; figures copied from the source text I read.

| # | Source | Access | Surface | Shoe | Quantity | Value | Method |
|---|---|---|---|---|---|---|---|
| 1 | Worsfold, Smith, Dyson 2006, "Modern golf shoe traction properties on grass", J Turfgrass Sports Surf Sci 82:2-12. https://www.researchgate.net/publication/231588836_MODERN_GOLF_SHOE_TRACTION_PROPERTIES_ON_GRASS | ABSTRACT ONLY | natural grass turf adhered to force-plate plate | metal 7-spike (8 mm) | limiting (slip-onset, i.e. peak static) linear traction coeff., forefoot / whole foot | 0.97 / 1.01 | prosthetic leg+foot rig, increasing linear & rotatory force until slip; normal load and speed NOT given in abstract |
| 1 | same | ABSTRACT ONLY | same | alt. 7 moulded spikes | same | 0.91 / 1.01 | same |
| 1 | same | ABSTRACT ONLY | same | flat sole, spikeless, no mouldings | same | 0.66 / 0.88 | same |
| 1 | same | ABSTRACT ONLY | same | metal vs alt spike | rotational limiting torque | metal +31% forefoot rotational, +11% inward / +18% outward whole-foot; absolute Nm not in abstract | same |
| 2 | Worsfold et al. 2007, JSSM 6:484-489. https://pmc.ncbi.nlm.nih.gov/articles/PMC3794489/ | FULL TEXT | natural grass on 2 force plates | metal, alt spike, flat | UTILIZED (required) COF = shear/vertical during real swings, driver/3i/7i, 24 golfers | 0.62 ± 0.03, both feet, all shoes and clubs | in-swing GRF ratio, not a slip limit |
| 3 | Worsfold, Smith, Dyson, "Kinetic Assessment of Golf Shoe Outer Sole Design Features", JSSM (PMC3761538). https://pmc.ncbi.nlm.nih.gov/articles/PMC3761538/ | FULL TEXT | 30 mm natural turf on Kistler 9851 plates; ball off Astroturf mat | metal / alt / flat | utilized COFxy (resultant shear / vertical, Kistler Bioware), driver, 18 golfers, front foot | .634(.097) / .631(.085) / .608(.061); back foot .654/.631/.607 | in-swing; front-foot Tz max ≈ 20 Nm (19.7–20.8) |
| 4 | Doyle (high-school science-fair paper), GCRSEF. https://www.gcrsef.org/wp-content/uploads/formidable/13/Doyle-Dominick-Research-Paper-GCRSEF-compressed-1-1.pdf | FULL TEXT, NOT PEER-REVIEWED | football natural grass vs artificial turf | athletic/running shoes (not golf) | μs / μk | grass 1.249 / 1.148; turf 0.809 / 0.713 | context only, LOW quality |
| 5 | Shorten et al. 2003 ISB abstract. https://media.isbweb.org/images/conf/2003/longAbstracts/SHORTEN_372-405_NB_LONG.pdf | FULL TEXT (long abstract) | natural / synthetic / infill | football cleats | translational traction coeff. range (as quoted in Boise State thesis Table 2) | 0.54–1.45; required in cutting 0.74 ± 0.20 | cleats, not golf |
| 6 | Twomey et al., "The effect of normal load, speed and moisture on footwear traction", Footwear Science 2012. https://doi.org/10.1080/19424280.2011.653992 | ABSTRACT ONLY | natural grass & artificial turf | 3 footwear types | method finding | translational traction rises linearly with load (335–776 N) and speed (50–200 mm/s); rotational constant with speed; moisture large, shoe/surface specific | no μ values in abstract |

Not found / not verified: Slavin & Williams 1995 (ASB proc., static COF of outsoles; cited in #3, no full text found), Williams & Sih 1998, Villwock rotational data (not checked this pass), USGA/STRI or manufacturer golf-shoe μ, any golf shoe on hitting MAT or artificial golf turf.

## Interpretation
- Available (slip-limit) μ for golf shoes on natural grass: ~0.9–1.0 for spiked (forefoot 0.91–0.97, whole foot 1.01); spikeless flat ~0.66–0.88 (source 1, abstract-only, method load/speed unknown).
- Real swings only USE μ ≈ 0.61–0.65 (driver, front foot ≈ 0.63) — full-text, two studies. So μ=1.0 gives ~0.35 margin; slip in the sim at μ≥0.9 means the policy demands more shear/normal than real golfers use.
- Sim μ=1.0, randomization 0.9–1.1: centre matches spiked-shoe limiting values; 1.1 is above any golf-shoe value found; spikeless/mat is not covered.

## Recommendation (derived)
- Nominal μ = 0.95 (spiked, natural grass). Robustness randomization 0.7–1.05 (lower end = spikeless 0.66–0.88 whole/forefoot; upper = spiked whole foot 1.01). Keep 1.1 only as a non-gating stress value.
- Optional gate: utilized foot shear/normal ratio during top→impact should mostly stay ≤ ~0.65–0.75 (real 0.62 ± 0.03, SD up to 0.135 per foot).
- Rotational: no absolute limiting torsional μ verified; only in-swing front-foot torque ≈ 20 Nm (driver, 81 kg men). Use as a sanity scale, not a band.

Confidence: MEDIUM for utilized COF (full text, two studies, same lab); LOW-MEDIUM for limiting μ (single study, abstract only, load/speed not stated); LOW for artificial turf/mats (no golf-specific source).
