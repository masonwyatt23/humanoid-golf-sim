"""Builds data/references/kinematic_sequence_torque_reference_v2.json (published open sources only).

Extends v1 (kseq-reference b78e5eb). Every datapoint carries source id, read tag (fetched-full / abstract / snippet),
population, n, club speed, and value level (measured / secondary / derived / model / extrapolated).
No unpublished or private-clip data. Run: python scripts/gen_kinematic_sequence_torque_reference_v2.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from data import kinematic_sequence_torque_reference as K  # noqa: E402

MPH = 2.23694
OUT = os.path.join(ROOT, "data", "references", "kinematic_sequence_torque_reference_v2.json")

SOURCES = {
    "madrid2020": dict(cite="Madrid, Avalos, Levine, Tuttle, Becker, Kwon. Appl Sci 10(17):5728 (2020), open access (CC BY)",
                       url="https://www.mdpi.com/2076-3417/10/17/5728", tag="fetched-full",
                       note="Tables 1-4 read in full; 66 skilled males (hcp<=3), driver CHS 110.4+-4.8 mph, 500 Hz optical; on-plane (functional swing plane) angular velocities, not 3-axis resultant"),
    "meister2011": dict(cite="Meister et al. J Appl Biomech 27:242-251 (2011)",
                        url="https://waddengolfacademy.com/biomechanics/Rotational%20Biomechanics%20Meister%20Ladd.pdf", tag="fetched-full",
                        note="Full PDF text; 10 pro + 5 amateur males, 5-iron (not driver), easy/medium/hard effort; both feet on ONE force plate"),
    "bourgain2020": dict(cite="Bourgain et al. Proceedings 49:45 (2020), open access",
                         url="https://www.mdpi.com/2504-3900/49/1/45", tag="fetched-full",
                         note="Full text; 28 males, driver, best swing per golfer, Vicon 200 Hz + 2 AMTI plates (artificial turf), TrackMan CHS"),
    "okuda2010": dict(cite="Okuda, Gribble, Armstrong. J Sports Sci Med 9:127-133 (2010), open access",
                      url="https://www.jssm.org/volume09/iss1/cap/jssm-09-127.pdf", tag="fetched-full",
                      note="Full PDF; 13 skilled vs 17 low-skilled, driver, vertical GRF only; CHS not reported"),
    "worsfold2007": dict(cite="Worsfold, Smith, Dyson. golf shoe designs on natural turf, J Sports Sci Med (2007), PMC3794489",
                         url="https://pmc.ncbi.nlm.nih.gov/articles/PMC3794489/", tag="fetched-full",
                         note="PMC full page fetched; 24 golfers, natural-turf force plates; CHS not reported in the numbers used"),
    "worsfold2008": dict(cite="Worsfold, Smith, Dyson. rotational torque at shoe-turf interface, PMC3761900",
                         url="https://pmc.ncbi.nlm.nih.gov/articles/PMC3761900/", tag="fetched-full",
                         note="PMC full page fetched; 24 golfers (8 low/8 mid/8 high hcp), natural turf, 5 shots per club; CHS not reported"),
    "foxworth2013": dict(cite="Foxworth et al. J Orthop Sports Phys Ther 43(9):660-665 (2013)",
                         url="https://www.jospt.org/doi/10.2519/jospt.2013.4417", tag="fetched-full",
                         note="Full article page incl. Table 1-3; torques normalised to % body weight x height; absolute N*m needs assumed anthropometry"),
    "okamoto2006": dict(cite="Okamoto. ISBS proceedings, joint torque contribution to clubhead acceleration (case study)",
                        url="https://commons.nmu.edu/cgi/viewcontent.cgi?article=1254&context=isbs", tag="fetched-full",
                        note="Full paper; 3 professionals (63.3 kg, 1.70 m), 250 Hz Vicon, fastest of 5 drives; club-grip (hand-club) torque and power, not body-joint torque"),
    "sprigings2000": dict(cite="Sprigings & Neal. J Appl Biomech 16:356-366 (2000), simulation",
                          url="https://waddengolfacademy.com/biomechanics/Sprigings%20Neal%202000%20Insight%20into%20the%20important%20of%20wrist%20torque.pdf",
                          tag="fetched-full", note="Scanned PDF (no text layer); pages 3,5,6 read as images. SIMULATION: torque limits are model inputs, torque histories are optimiser outputs read from a figure (+-5 N*m)"),
    "lynn2013": dict(cite="Lynn et al. Int J Golf Sci 2:116-125 (2013), open access",
                     url="https://www.golfsciencejournal.org/article/4979.pdf", tag="fetched-full",
                     note="Full PDF; 5-iron; 15 elite vs 14 recreational; electromagnetic/optical pelvis plate; FlightScope"),
    "callaway2012": dict(cite="Callaway et al. peak pelvis rotation speed and gluteal strength, PMC3362989",
                         url="https://pmc.ncbi.nlm.nih.gov/articles/PMC3362989/", tag="fetched-full",
                         note="PMC page; 56 subjects incl. tour players, 7/8-iron, K-Vest; CHS not reported"),
    "chu2010": dict(cite="Chu, Sell, Lephart. J Sports Sci 28:1251-1259 (2010)",
                    url="https://people.stfx.ca/smackenz/courses/hk396/handouts/Chu%202010%20The%20relationship%20between%20biomechanical%20variables%20and%20driving%20performance.pdf",
                    tag="fetched-full", note="Full PDF (course handout copy); 308 golfers (266 M / 42 F, hcp 8.4+-8.4), driver; values are at swing EVENTS, not peaks; CHS not measured (ball velocity 61.0+-8.7 m/s = 136.5 mph)"),
    "ichikawa2024": dict(cite="Ichikawa et al. J Hum Sport Exerc 19(3):874-881 (2024), open access CC BY-NC-SA",
                         url="https://www.jhse.es/index.php/jhse/article/download/analysis-long-drive-distance-golf-player/36", tag="fetched-full",
                         note="Full PDF; ONE long-drive professional (182.5 cm, 106 kg, 27 y), GEARS 360 fps, GC2 launch monitor, 30 drives; 'kinematic sequence (deg/sec)' values are reported near impact, peak-vs-at-impact not stated"),
    "randa_wld2019": dict(cite="R&A / Nov 2019: Analysis of TrackMan data gathered at World Long Drive events (v1.0)",
                          url="https://assets.randa.org/c42c7bf4-dca7-00ea-4f2e-373223f80f76/550ab9f6-5dd3-45b0-b58c-7563d4256c04/R07%20-%20Analysis%20of%20Trackman%20data%20gathered%20at%20World%20Long%20Drive.pdf",
                          tag="fetched-full", note="Launch-monitor population data only (no biomechanics); defines the >140 mph population that has no joint data"),
    "watson2026": dict(cite="Watson et al. Sports Med 56(5):1191-1212 (2026), systematic review of GRF/CoP in golf, open access",
                       url="https://pmc.ncbi.nlm.nih.gov/articles/PMC13198453/", tag="fetched-full",
                       note="Full HTML; summary tables of primary studies (secondary values for Han 2019, Ball & Best, Williams, Bourgain, Peterson); no N*m or CHS-by-group numbers"),
    "horan2012": dict(cite="Horan & Kavanagh. Sports Biomech 11:165-174 (2012)",
                      url="https://doi.org/10.1080/14763141.2011.638390", tag="abstract",
                      note="Abstract fetched; peak-speed numbers (650/507 deg/s, CHS 50.1 m/s) came from a search-engine summary only"),
    "han2019_ground": dict(cite="Han, Como, Kim, Lee, Kim, Kim, Kwon. Sports Biomech 18:115-134 (2019)",
                           url="https://www.tandfonline.com/doi/full/10.1080/14763141.2019.1586983", tag="abstract",
                           note="Paywalled; abstract only. Correlation values via Watson 2026 (fetched-full secondary). No N*m or BW means retrieved"),
    "han2019_style": dict(cite="Han, Como, Kim, Hung, Hasan, Kwon. Sports Biomech 18:663-685 (2019)",
                          url="https://doi.org/10.1080/14763141.2019.1629617", tag="abstract",
                          note="Paywalled; abstract summary only; phase-time means by swing style taken from Madrid 2020 text (secondary)"),
    "kwon2013": dict(cite="Kwon, Han, Como, Lee, Singhal. Sports Biomech 12:231-246 (2013)",
                     url="https://doi.org/10.1080/14763141.2013.771896", tag="abstract",
                     note="Abstract + docksci first page; 18 skilled males, 5 driver trials; X-factor values via Madrid 2020 (secondary); CHS from a slide-deck snippet"),
    "healy2011": dict(cite="Healy, Moran, Dickson, et al. J Sports Sci 29:1005-1015 (2011)",
                      url="https://eprints.staffs.ac.uk/435/", tag="abstract",
                      note="Repository abstract; 5-iron, 30 males split by ball speed 52.9 vs 39.9 m/s; no body-segment peaks retrieved"),
    "lumbar_loads": dict(cite="Lumbar spinal loads during a golf swing (EMG-assisted model); thesis/paper summaries",
                         url="http://hdl.handle.net/2142/86424", tag="snippet",
                         note="Search-engine summary only (about 6 BW / 4300 N compression near driver impact; AP shear 882 N); attribution between the thesis and a Sports Biomech paper unresolved; forces, not torque"),
    "sonic_arxiv": dict(cite="The Physics behind the Sonic Golf Swing Monitoring Device (arXiv 1001.1137)",
                        url="https://export.arxiv.org/pdf/1001.1137v1.pdf", tag="snippet",
                        note="Search-engine summary only (professionals 258+-8 ms downswing, ~3:1 backswing ratio)"),
    "tpi_timing": dict(cite="TPI article: Measuring Golf Swing Timing from Video",
                       url="https://www.mytpi.com/articles/biomechanics/measuring-the-timing-of-the-golf-swing-from-video", tag="snippet",
                       note="Search-engine summary only (elite database 233-296 ms); not a peer-reviewed table"),
}

DP = []


def dp(id_, cat, quantity, value, unit, source, level, pop, n, chs_mph=None, sd=None, club="driver", note="", conflict=None, **extra):
    tag = SOURCES[source]["tag"] if source in SOURCES else "derived"
    d = dict(id=id_, cat=cat, quantity=quantity, value=value, unit=unit, sd=sd, source=source, tag=tag, level=level,
             population=pop, n=n, chs_mph=chs_mph, chs_ms=None if chs_mph is None else round(chs_mph / MPH, 1), club=club, note=note)
    if conflict:
        d["conflict"] = conflict
    d.update(extra)
    DP.append(d)


# ---------------- (b) kinematic sequence, high-CHS populations ----------------
POP_M = "66 skilled males (touring pros, collegiate, teaching pros; hcp<=3)"
for k, v, sd, r in (("hip_line", 394, 62, 0.447), ("shoulder_line", 711, 63, 0.461), ("upper_lever", 1142, 67, 0.552),
                    ("club", 2364, 115, 0.906), ("wrist_uncocking", 1615, 138, 0.539)):
    dp(f"b_madrid_peak_{k}", "b", f"peak downswing on-plane angular velocity, {k}", v, "deg/s", "madrid2020", "measured", POP_M, 66, 110.4, sd,
       note=f"Pearson/Spearman r with actual CHS = {r}", r_with_chs=r)
for k, v, sd in (("hip_line", 262, 63), ("shoulder_line", 610, 65), ("upper_lever", 725, 84)):
    dp(f"b_madrid_at_BI_{k}", "b", f"angular velocity at ball impact, {k}", v, "deg/s", "madrid2020", "measured", POP_M, 66, 110.4, sd)
for k, v, sd in (("hip_line", -87, 18), ("shoulder_line", -84, 25), ("upper_lever", -73, 6)):
    dp(f"b_madrid_peak_time_{k}", "b", f"time of downswing peak angular velocity before impact, {k}", v, "ms", "madrid2020", "measured", POP_M, 66, 110.4, sd,
       note="peaks of hip line, shoulder line and upper lever fall in a 14 ms window; only the club peak is clearly separated (full proximal-to-distal order holds in the transition phase, not at the downswing peaks)")
dp("b_madrid_peak_decrease_hip", "b", "peak-to-impact hip-line speed loss", -123, "deg/s", "madrid2020", "measured", POP_M, 66, 110.4, 66,
   note="loss correlates with CHS (r=-0.476 actual): faster swingers decelerate the pelvis more")
dp("b_ichikawa_pelvis", "b", "pelvis 'kinematic sequence' angular velocity near impact (straight/draw/fade means)", [325.0, 283.9, 297.7], "deg/s",
   "ichikawa2024", "measured", "ONE long-drive pro (world #13, 428 yd best), 106 kg, 182.5 cm", 1, 137.3, [50.1, 51.5, 71.1],
   note="30 drives, GEARS 360 fps. Definition (peak vs at impact; resultant vs on-plane) not stated. Not higher than the 110 mph skilled values.",
   conflict="C2")
dp("b_ichikawa_torso", "b", "torso angular velocity near impact (straight/draw/fade)", [649.5, 609.9, 621.7], "deg/s", "ichikawa2024", "measured",
   "ONE long-drive pro", 1, 137.3, [63.9, 88.3, 35.4], note="same definition caveat", conflict="C2")
dp("b_ichikawa_arm", "b", "arm angular velocity near impact (straight/draw/fade)", [479.7, 465.6, 460.0], "deg/s", "ichikawa2024", "measured",
   "ONE long-drive pro", 1, 137.3, [28.2, 56.2, 34.0], note="far below Madrid upper-lever 1142 (different segment definition); do not compare directly", conflict="C2")
dp("b_ichikawa_grip_speed", "b", "grip (hand) linear speed", 22.1, "mph", "ichikawa2024", "measured", "ONE long-drive pro", 1, 137.3, 0.7,
   note="grip speed 22.1 mph (9.9 m/s) at 137 mph CHS: club/hand speed ratio about 6.2; unchanged across three shot shapes")
dp("b_ichikawa_chs_ball", "b", "CHS / ball speed / launch / attack angle", dict(chs_mph=137.2, ball_mph=189.3, launch_deg=13.9, attack_deg=7.9, club_loft_static_deg=6.1,
   shaft_in=47.5), "mixed", "ichikawa2024", "measured", "ONE long-drive pro", 1, 137.2, None,
   note="straight shots; ball speed ratio 1.38 (GC2) is below TrackMan smash values of 1.48 for long-drive events")
dp("b_randa_wld_men", "b", "population club speed / ball speed / smash / launch / spin / carry", dict(chs_mph=145, ball_mph=214, smash=1.48, launch_deg=11.2,
   spin_rpm=2789, carry_yd=352), "mixed", "randa_wld2019", "measured", "World Long Drive men, 304 drives (2019 events)", None, 145, None,
   note="TrackMan calculated values. This population has NO published joint/segment speeds; it only defines the target regime.")
dp("b_randa_wld_women", "b", "population club speed / carry (women)", dict(chs_mph=116, ball_mph=171, smash=1.47, launch_deg=13.4, spin_rpm=2813, carry_yd=282),
   "mixed", "randa_wld2019", "measured", "World Long Drive women, 131 drives", None, 116, None, note="no joint data")
dp("b_horan_peak_speeds", "b", "peak speed thorax / pelvis (professionals)", dict(thorax=650, pelvis=507), "deg/s", "horan2012", "secondary",
   "14 male professionals (KPGA/other), driver", 14, 112.1, dict(thorax=60, pelvis=52),
   note="values from search summary only (snippet-level); abstract confirms thorax has the highest upper-body peak speed and thorax-pelvis coupling R2=0.92")
SOURCES["horan2012_numbers"] = dict(cite="Horan & Kavanagh 2012 numeric values via search summary", url="https://doi.org/10.1080/14763141.2011.638390", tag="snippet",
                                    note="numbers 650+-60 and 507+-52 deg/s, CHS 50.1+-2.1 m/s")
DP[-1]["source"] = "horan2012_numbers"
DP[-1]["tag"] = "snippet"
dp("b_lynn_pelvis", "b", "peak pelvic angular velocity (elite vs recreational)", [427.8, 398.8], "deg/s", "lynn2013", "measured",
   "15 elite (hcp 0.3) vs 14 recreational (hcp 20.7), 5-iron", 29, 92.2, [69.9, 69.4],
   note="CHS elite 148.4 km/h = 92.2 mph, recreational 141.1 km/h = 87.7 mph. r(peak pelvic velocity, CHS)=0.017 (n.s.); pelvic ACCELERATION did correlate (r=0.37 with distance). Elite peaks 101.7 ms before impact vs 79.6 ms.",
   conflict="C1")
dp("b_lynn_peak_to_impact", "b", "time from peak pelvic velocity to impact (elite vs recreational)", [101.7, 79.6], "ms", "lynn2013", "measured",
   "elite vs recreational, 5-iron", 29, 92.2, [18.0, 23.0], note="correlates with smash factor r=0.399")
dp("b_callaway_pelvis", "b", "peak pelvis rotation speed (low-handicap vs high-handicap)", [503.2, 380.1], "deg/s", "callaway2012", "measured",
   "56 subjects incl. PGA/LPGA tour, collegiate, recreational; 7/8-iron; K-Vest", 56, None, None, club="7/8-iron",
   note="CHS not reported; includes tour players; sits next to Cheetham pros 477 and Horan pros 507", conflict="C1")
dp("b_chu_event_speeds", "b", "pelvis / upper-torso rotation velocity at the 'acceleration' event (NOT peak)", dict(pelvis=388.1, torso=608.1), "deg/s", "chu2010",
   "measured", "308 golfers (266 M/42 F), hcp 8.4+-8.4", 308, None, dict(pelvis=77.4, torso=117.5),
   note="ball velocity 61.0+-8.7 m/s (136.5 mph); heterogeneous skill, so between-golfer correlations are confounded by skill")
dp("b_kwon_xfactor_secondary", "b", "max X-factor / downswing stretch / total stretch (skilled, driver)", dict(max_xfactor_deg=59, downswing_stretch_deg=1, total_stretch_deg=8), "deg",
   "kwon2013", "secondary", "18 skilled males, hcp -0.6+-2.1", 18, 102.3, None, note="values as quoted in Madrid 2020; X-factor parameters not correlated with CHS (abstract)")
dp("b_han_styles_phase_ms", "b", "phase times by swing style (transition : early downswing : late downswing)", dict(LBS=[109, 117, 119], LDS=[63, 153, 119], LSA=[82, 137, 119]), "ms",
   "han2019_style", "secondary", "74 elite/skilled males (5 styles), driver", 74, None, None, note="as quoted in Madrid 2020 text; downswing (TB to BI) = early + late = 236 (LBS), 272 (LDS), 256 (LSA) ms")
dp("b_healy_5iron_groups", "b", "5-iron CHS of high vs low ball-speed groups", [38.2, 30.7], "m/s", "healy2011", "measured",
   "30 males split by ball speed 52.9+-2.1 vs 39.9+-5.2 m/s", 30, None, [1.7, 2.9], club="5-iron",
   note="CHS values from a search summary (snippet); abstract: higher group had greater hip motion and X-factor angle during the downswing, faster shoulder extension in early downswing")
DP[-1]["tag"] = "snippet"

# ---------------- (a) joint torques ----------------
BWHT_ASSUMED = dict(mass_kg=83.0, height_m=1.80)
BWHT = BWHT_ASSUMED["mass_kg"] * 9.81 * BWHT_ASSUMED["height_m"]
HIP = {"trail_extensor": (10.64, 1.96), "lead_extensor": (5.28, 1.27), "trail_flexor": (6.56, 1.73), "lead_flexor": (6.64, 1.64),
       "trail_abductor": (5.69, 1.21), "lead_abductor": (6.30, 2.23), "trail_adductor": (4.95, 1.88), "lead_adductor": (1.91, 1.14),
       "trail_internal_rotator": (2.70, 1.15), "lead_internal_rotator": (3.21, 0.99), "trail_external_rotator": (2.38, 0.84), "lead_external_rotator": (1.43, 0.49)}
for k, (m, sd) in HIP.items():
    dp(f"a_foxworth_hip_{k}", "a", f"peak internal hip torque, {k.replace('_', ' ')}", m, "% body weight x height", "foxworth2013", "measured",
       "20 male amateurs (10 young 25 y, 10 senior 57 y; hcp 9-11), driver", 20, 91.6, sd,
       note=f"= {m * BWHT / 100:.0f} N*m only for the ASSUMED 83 kg / 1.80 m golfer (derived); group CHS 41.9 / 40.0 m/s (93.7 / 89.5 mph); r with CHS 0.46-0.65 for most components",
       n_m_assumed_83kg_180m=round(m * BWHT / 100, 1))
dp("a_foxworth_hip_bwht_to_Nm", "a", "conversion used for hip torque", dict(BW_Ht_Nm=round(BWHT, 1), **BWHT_ASSUMED), "N*m per 100% BW*Ht", "foxworth2013", "derived",
   "assumption", None, None, note="paper does not give absolute mass/height in the retrieved text; BMI 24.5-27 consistent with the assumed golfer")
dp("a_okamoto_grip_torque", "a", "maximum club-grip (hand-club) torque in the downswing", 40.9, "N*m", "okamoto2006", "measured",
   "3 male professionals (63.3 kg), fastest of 5 drives", 3, 102.4, 2.9,
   note="peak at 87% of downswing, 339.5+-12.2 N grip force; this is torque at the hand-club interface (wrist-level load), not a body joint. Last frames before impact excluded.",
   conflict="C7")
dp("a_okamoto_club_power", "a", "peak total club power / force power / torque power", dict(total_W=2813.4, force_W=2113.4, torque_W=737.9), "W", "okamoto2006", "measured",
   "3 male professionals", 3, 102.4, dict(total=216.9, force=260.7, torque=104.2), note="peaks at 83-86% of downswing; torque share of work about 15% (31.1 of 213.2 J)", conflict="C7")
dp("a_okamoto_work", "a", "mechanical work on club in downswing (total / by force / by torque)", dict(total_J=213.2, force_J=182.1, torque_J=31.1), "J", "okamoto2006", "measured",
   "3 male professionals", 3, 102.4, dict(total=23.3, force=10.6, torque=10.4))
dp("a_sprigings_limits", "a", "model joint torque limits (spine / shoulder / wrist) and max joint speeds", dict(Tmax_Nm=dict(spine=180, shoulder=120, wrist=60), wmax_rad_s=dict(spine=20, shoulder=30, wrist=60)), "N*m; rad/s",
   "sprigings2000", "model", "simulated 80 kg, 1.83 m golfer, 3-segment planar model", None, 98.4, None, note="inputs (from Neal et al. 1999), not measurements; torque-velocity curve shape factor 3.0, activation constant 40 ms")
dp("a_sprigings_trunk_torque", "a", "optimised muscular torque at the spine/trunk generator", dict(early_Nm=75, near_impact_Nm=95), "N*m", "sprigings2000", "model",
   "simulation SIM-1 (wrist torque allowed), CHS 44.0 m/s", None, 98.4, 5, note="75 stated in text; ~95 near impact read from Figure 3 (+-5). Total downswing time 0.380 s (video pro 0.34 s)", conflict="C8")
dp("a_sprigings_shoulder_torque", "a", "optimised muscular torque at the shoulder generator", dict(early_Nm=83, near_impact_Nm=100), "N*m", "sprigings2000", "model",
   "simulation SIM-1", None, 98.4, 5, note="83 stated; ~100 at impact from figure (+-5); onset 0.148 s after the trunk")
dp("a_sprigings_wrist_torque", "a", "optimised wrist torque (active uncocking)", dict(late_Nm=22), "N*m", "sprigings2000", "model",
   "simulation SIM-1", None, 98.4, 5, note="about 20-25 N*m at the end, read from figure; onset 0.138 s after the shoulder (about 94 ms before impact); active wrist torque adds 3.6 m/s (about 9%)")
dp("a_lumbar_compression", "a", "L4/L5 compressive load near driver impact", dict(BW=6.0, N=4300), "BW; N", "lumbar_loads", "measured", "EMG-assisted lumbar model, driver (small sample)", None, None, None,
   note="force, not torque; summary-only; does NOT answer the lumbar N*m gap")
dp("a_none_lumbar_hip_shoulder_Nm", "a", "peak lumbar / shoulder joint torque in N*m, measured, driver", None, "N*m", "madrid2020", "none-found", "n/a", None, None, None,
   note="Not found in any open source: only the Sprigings model torques and Foxworth hip torques (% BW*Ht) exist at joint level; Nesbit gives work (J). Sensors 2020 (PMC7374515) upper-limb kinetics and Nesbit n=84 have values only in figures/club-level")
DP[-1]["tag"] = "n/a"

# ---------------- (c) GRF ----------------
dp("c_bourgain_vgrf", "c", "max vertical GRF per foot, lead / trail (normalised to body weight; mean of per-golfer maxima)",
   dict(pro=[1.181, 0.642], amateur=[1.241, 0.696], overall=[1.222, 0.679]), "BW", "bourgain2020", "measured",
   "9 pros (CHS 48.5 m/s) + 19 amateurs (hcp 15, CHS 40.5 m/s)", 28, 108.5, dict(pro=[0.285, 0.070], amateur=[0.206, 0.136]),
   note="pros did NOT exceed amateurs; best swing per golfer; artificial turf over AMTI plates", conflict="C4")
dp("c_bourgain_hgrf", "c", "max horizontal GRF per foot, lead / trail (to body weight)", dict(pro=[0.158, 0.131], amateur=[0.186, 0.127], overall=[0.177, 0.128]), "BW", "bourgain2020",
   "measured", "same 28 golfers", 28, 108.5, dict(pro=[0.06, 0.04], amateur=[0.08, 0.07]), note="resultant horizontal per foot as defined by the paper; far below the 0.4-0.6 BW AP shear quoted in the v1 review", conflict="C3")
dp("c_bourgain_motor_moment", "c", "correlation of normalised GRF 'motor moment' (about CoM, perpendicular to swing plane) with CHS", 0.83, "r", "bourgain2020", "measured",
   "28 golfers (4 force components each foot)", 28, 108.5, None, note="individual GRF components did NOT correlate strongly with CHS (|r|<0.7); lever arm of horizontal force 0.46 m (trail) / 1.13 m (lead) vs 0.04 / 0.03 m for vertical; best swing CHS 52.5 m/s = 117.4 mph")
dp("c_okuda_max_vgrf", "c", "max vertical GRF lead / trail foot", dict(skilled=[1.09, 0.98], low_skilled=[1.13, 0.89]), "BW", "okuda2010", "measured",
   "13 skilled (hcp 0.8) vs 17 low-skilled (hcp 30.8), driver", 30, None, dict(skilled=[0.32, 0.09], low_skilled=[0.25, 0.12]), note="CHS not reported; weight at address ~50/50", conflict="C4")
dp("c_okuda_downswing_lead", "c", "lead-foot VGRF at early-downswing event (%BW), skilled vs low-skilled", dict(skilled=59, low_skilled=33), "%BW", "okuda2010", "measured",
   "same", 30, None, dict(skilled=28, low_skilled=19), note="skilled golfers transfer load to the lead foot earlier; trail foot 92% BW mid-backswing (skilled)")
dp("c_worsfold_vgrf", "c", "max vertical force per foot, driver, back / front", dict(back=0.49, front=0.84, back_range_metal=0.33, front_range_metal=0.83), "BW", "worsfold2007", "measured",
   "24 golfers (8 low / 8 mid / 8 high hcp), natural turf", 24, None, None, note="3-/7-iron: ~0.82 back / 1.1 front; friction coefficient 0.62 (shear/vertical) at every shoe and club", conflict="C4")
dp("c_worsfold_foot_torque", "c", "rotational torque at shoe-turf interface about vertical axis (Tz max), driver", dict(front_Nm=[17, 19], back_Nm=[6, 7], whole_swing_front_Nm=40,
   low_hcp_back_driver_Nm=18.2), "N*m", "worsfold2008", "measured", "24 golfers on natural turf, 3 shoe types", 24, None, None,
   note="this is foot-ground TORSIONAL torque only (smallest of the three vertical-axis moments per the Kwon group); not the pivoting moment", conflict="C5")
dp("c_meister_free_moment", "c", "peak ground-reaction free moment (about vertical axis through the plate CoP, both feet on one plate) by effort", dict(easy=0.83, medium=1.00, hard=1.19),
   "N*m/kg", "meister2011", "measured", "10 male pros, 5-iron, 3 efforts", 10, None, dict(easy=0.15, medium=0.11, hard=0.08),
   club="5-iron", note="CHS easy/medium/hard = 27.4 / 31.6 / 35.4 m/s (61.3 / 70.7 / 79.2 mph); occurs in EARLY downswing, just after peak X-factor; within-golfer r with CHS median 0.943; hard-effort amateurs 0.92-1.20",
   conflict="C5", chs_by_effort_ms=[27.4, 31.6, 35.4], chs_by_effort_mph=[61.3, 70.7, 79.2])
dp("c_han_corr", "c", "correlation of peak GRF/moment parameters with maximum CHS (driver)", dict(lead_backward_force=0.46, lead_away_force=0.45, combined_backward=0.32,
   trail_forward=0.29, combined_max=0.33), "r", "han2019_ground", "secondary", "63 skilled males (hcp<=3), driver/5-iron/PW", 63, None, None,
   note="from Watson 2026 table; lead-foot GRF moment and trail-foot pivoting moment also correlate (abstract). Maximum angular effort at the instant the lead arm is parallel to the ground (about early downswing). No N*m means retrieved.")
dp("c_misc_corr", "c", "other GRF/CoP correlations with CHS (secondary)", dict(williams_peak_horizontal_GRF=0.69, bourgain2017_summed_force=0.83, ball_best_CoP_range=0.53,
   ball_best_stance_width=0.47, jones_CoP_ML_R2_driver=0.54), "r or R2", "watson2026", "secondary",
   "mixed populations (Williams; Bourgain 6 golfers; Ball & Best 62 males; Jones 104 amateurs)", None, None, None, note="heterogeneous skill samples inflate correlations (Madrid 2020 discussion)")
dp("c_peterson_angular_impulse", "c", "relative net angular impulse by both legs, driver vs 6-iron", dict(driver=0.337, iron6=0.291), "N*m*s/kg", "watson2026", "secondary",
   "11 highly skilled (hcp<5; 5 F, 6 M)", 11, None, None, note="driver > 6-iron, increase via lead-leg horizontal reaction force; CHS not given")
dp("c_chu_vgrf_events", "c", "VGRF lead / trail foot at downswing acceleration event", dict(lead=93.9, trail=46.4), "%BW", "chu2010", "measured", "308 golfers", 308, None,
   dict(lead=28.5, trail=17.3), note="event value, not peak; impact event 74.7 / 35.5 %BW; heterogeneous sample")
dp("c_kwon_group_qualitative", "c", "which GRF mechanism makes the vertical-axis moment", "pivoting moment (F/B components of the two foot GRFs about the combined CoP) is primary; foot contact moment is the smallest; frontal-plane GRF moment largest and peaks near EDA; vertical-axis moments peak near EDA",
   "text", "han2019_ground", "secondary", "skilled males (Kwon lab explainer page)", 63, None, None,
   note="from drkwongolf.info/biom/fgmom.html (public lab page, qualitative; no numbers)")
DP[-1]["tag"] = "snippet"

# ---------------- (d) X-factor ----------------
dp("d_madrid_xfactor", "d", "X-factor at top of backswing / maximum / at impact / range (functional-swing-plane method)", dict(top=61, max=62, impact=9, range=74), "deg", "madrid2020", "measured",
   POP_M, 66, 110.4, dict(top=9, max=8, impact=8, range=9),
   note="stretch (backswing / downswing / total) 5+-3 / 1+-2 / 6+-4 deg; correlation with actual CHS: X at top r=0.265, X at impact 0.249, stretch n.s. (downswing stretch r=-0.258); with height-normalised CHS only X at impact for irons", conflict="C6")
dp("d_meister_xfactor_effort", "d", "peak X-factor and X-factor at impact by effort (5-iron)", dict(peak=[52, 54, 56], at_impact=[24, 28, 33]), "deg", "meister2011", "measured",
   "10 male pros, easy/medium/hard", 10, 79.2, dict(peak=[4, 4, 4], at_impact=[6, 4, 6]), club="5-iron",
   note="CHS 27.4/31.6/35.4 m/s; within-golfer r with CHS median 0.900 (peak) / 0.943 (at impact); peak X-factor precedes peak free moment; pelvic rotation 44-46 deg and upper torso 94-99 deg (pelvis flat vs effort)", conflict="C6")
dp("d_meister_amateurs", "d", "peak X-factor, hard swings, individual amateurs", dict(hcp4=52, hcp15=54, hcp30=48, novice1=46, novice2=46), "deg", "meister2011", "measured",
   "5 amateurs", 5, None, None, club="5-iron", note="amateur peak X-factor within 2 SD of pro 56+-4 for hcp4/15")
dp("d_chu_xfactor", "d", "X-factor at top / at impact (event values; sign convention magnitude)", dict(top=49.0, impact=12.3), "deg", "chu2010", "measured", "308 golfers (heterogeneous)", 308, None,
   dict(top=11.6, impact=9.1), note="regression predictor of ball velocity; confounded by skill")
dp("d_kwon_no_correlation", "d", "X-factor parameter correlation with max CHS in a homogeneous skilled group", "none (raw or height-normalised)", "text", "kwon2013", "measured",
   "18 skilled males", 18, 102.3, None, note="X-factor computation method changes values substantially (conventional method larger than FSP/Cardan); Madrid 2020 reports the same in 66 golfers")
dp("d_parker_regression_v1", "d", "v1 carry-over: Parker top X-factor 54.9+-7.9 deg, beta -0.24 with CHS", 54.9, "deg", "madrid2020", "secondary", "15 elite (v1)", 15, 103, 7.9,
   note="carried from v1 for the delta table (original source Parker 2018 fetched-full in v1)")
DP[-1]["tag"] = "carried-v1"

# ---------------- (e) downswing duration ----------------
dp("e_madrid_downswing", "e", "downswing duration TB to BI", 253, "ms", "madrid2020", "measured", POP_M, 66, 110.4, 26,
   note="backswing 769+-100 ms (ratio 3.0:1); transition 83+-31, early DS 136+-25, late DS 118+-9; r(DS, actual CHS)=-0.481 (R2=0.23), r(DS, height-normalised CHS)=-0.446; late-DS time r=-0.531")
dp("e_bourgain_downswing", "e", "downswing duration (pros vs amateurs)", [260, 280], "ms", "bourgain2020", "measured", "9 pros (108.5 mph) vs 19 amateurs (90.6 mph)", 28, 108.5, [20, 20],
   note="no significant group difference (overall 270+-40 ms at 96.4 mph); definition: downswing from top of backswing")
dp("e_okamoto_downswing", "e", "downswing duration of the three fastest drives", dict(subj1=[47.8, 0.28], subj2=[46.0, 0.26], subj3=[43.7, 0.30], mean=0.28, sd=0.02), "[CHS m/s, s]", "okamoto2006", "measured",
   "3 male professionals", 3, 102.4, 20, note="per-golfer fastest drive: 47.8 m/s at 0.28 s, 46.0 at 0.26 s, 43.7 at 0.30 s (no monotone trend in 3 players)")
dp("e_sprigings_downswing", "e", "simulated downswing time", 380, "ms", "sprigings2000", "model", "simulation (CHS 44.0 m/s)", None, 98.4, None,
   note="video of a tour pro in the same paper: 340 ms for ~49 m/s; model slower than measured pro data", conflict="C8")
dp("e_sonic_downswing", "e", "professional downswing duration", 258, "ms", "sonic_arxiv", "measured", "professionals (study details not retrieved)", None, None, 8, note="summary only")
dp("e_tpi_downswing_range", "e", "elite database downswing duration range", [233, 296], "ms", "tpi_timing", "measured", "TPI elite database (unspecified n)", None, None, None, note="summary only; non-peer-reviewed article")
dp("e_ichikawa_none", "e", "downswing duration for the 137 mph long-drive player", None, "ms", "ichikawa2024", "none-found", "ONE long-drive pro", 1, 137.3, None,
   note="paper reports ball/club/body data but no phase times")
DP[-1]["tag"] = "n/a"

# ---------------- derived: slopes and v1 deltas ----------------
SD_CHS_MS = 2.1
ANCHOR_MS = 49.4
SLOPES = {}
for key, sd, r in (("pelvis_hip_line", 62, 0.447), ("thorax_shoulder_line", 63, 0.461), ("arm_upper_lever", 67, 0.552), ("club", 115, 0.906)):
    SLOPES[key] = round(r * sd / SD_CHS_MS, 2)
DS_SLOPE = round(-0.481 * 26 / SD_CHS_MS, 2)
ANCH = {"pelvis_hip_line": 394, "thorax_shoulder_line": 711, "arm_upper_lever": 1142, "club": 2364}
V1MAP = {"pelvis_hip_line": "pelvis", "thorax_shoulder_line": "thorax", "arm_upper_lever": "lead_arm", "club": "club"}
rows = []
for mph in (110.4, 120.0, 132.0):
    ms = mph / MPH
    row = {"chs_mph": mph, "chs_ms": round(ms, 2), "segments": {}}
    for k in SLOPES:
        madrid = ANCH[k] + SLOPES[k] * (ms - ANCHOR_MS)
        v1 = K.segment_peak_deg_s(V1MAP[k], mph)
        row["segments"][k] = {"madrid_anchor_plus_within_group_slope": round(madrid, 0), "v1_two_group_fit": round(v1, 0),
                              "v1_minus_madrid": round(v1 - madrid, 0)}
    rows.append(row)
ds_rows = []
for mph in (110.4, 120.0, 132.0):
    ms = mph / MPH
    ds_slope_group = -2.5  # ms per m/s between Bourgain pros (260 ms at 48.5) and amateurs (280 at 40.5): 20 ms / 8.0 m/s
    ds_rows.append({"chs_mph": mph, "within_group_madrid_ms": round(253 + DS_SLOPE * (ms - ANCHOR_MS), 0),
                    "between_group_bourgain_ms": round(253 + (-20.0 / 8.0) * (ms - ANCHOR_MS), 0), "v1_fixed_ms": 230})

xs = [27.4, 31.6, 35.4]
ys = [0.83, 1.00, 1.19]
k_prop = sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)
mx, my = sum(xs) / 3, sum(ys) / 3
b_lin = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
a_lin = my - b_lin * mx
fm_rows = []
for mph in (110.4, 120.0, 132.0):
    ms = mph / MPH
    fm_rows.append({"chs_mph": mph, "proportional_Nm_per_kg": round(k_prop * ms, 2), "linear_Nm_per_kg": round(a_lin + b_lin * ms, 2),
                    "Nm_for_83kg_proportional": round(k_prop * ms * 83), "Nm_for_83kg_linear": round((a_lin + b_lin * ms) * 83)})

grip_rows = []
for mph in (100.0, 110.4, 120.0, 132.0):
    ms = mph / MPH
    grip_rows.append({"chs_mph": mph, "v1_linear_fit_Nm": round(K.grip_torque_Nm(mph), 1),
                      "okamoto_anchor_plus_nesbit_slope_Nm": round(40.9 + K.GRIP_TORQUE_SLOPE * (ms - 45.8), 1)})

sprig_rows = []
for mph in (98.4, 110.4, 120.0, 132.0):
    ms = mph / MPH
    sprig_rows.append({"chs_mph": mph, "trunk_Nm_if_prop_to_v": [round(75 * ms / 44.0), round(95 * ms / 44.0)],
                       "trunk_Nm_if_prop_to_v2": [round(75 * (ms / 44.0) ** 2), round(95 * (ms / 44.0) ** 2)]})

xf = {"madrid_between_golfer_slope_deg_per_ms": round(0.265 * 9 / SD_CHS_MS, 2), "meister_within_golfer_slope_deg_per_ms": round((56 - 52) / (35.4 - 27.4), 2)}
xf["x_at_top_at_120_mph"] = [round(61 + xf["meister_within_golfer_slope_deg_per_ms"] * (120 / MPH - ANCHOR_MS)), round(61 + xf["madrid_between_golfer_slope_deg_per_ms"] * (120 / MPH - ANCHOR_MS))]

hip_pair_axial = round((2.70 + 3.21) * BWHT / 100)
CONFLICTS = {
    "C1": "Pelvis peak speed vs CHS: Madrid (driver, n=66) r=0.447 for the hip line, but Lynn (5-iron, n=29) r=0.017 and elite/recreational peaks 428/399 deg/s; tour/skilled group means cluster at 428-507 deg/s (Lynn 428, Parker 475 [v1], Cheetham 477 [v1], Horan 507 snippet, Callaway 503) with no consistent rise from 92 to 112 mph. Treat the v1 pelvis speed extrapolation (519 at 120, 565 at 132) as an UPPER bound.",
    "C2": "The only long-drive datum (one 137 mph player, n=1) shows pelvis 284-325, torso 610-650 and arm 460-480 deg/s near impact: not above 110 mph skilled values (Madrid hip line 394, shoulder line 711). Definition mismatch (peak vs at-impact, GEARS vs Kwon3D) prevents a direct subtraction, but there is no evidence that body-segment speeds keep rising to 132 mph. v1 segment extrapolations (pelvis 565, thorax 886, arm 1226 at 132) are unsupported upper bounds; club speed may come from a longer/lower-loft club, mass (106 kg), lever/grip release.",
    "C3": "Horizontal GRF: Bourgain max 0.13-0.19 BW per foot (resultant, 28 golfers) vs v1 review's 0.4-0.6 BW AP shear (Hume review) and Worsfold AP range 0.31-0.34 BW (irons). Different definitions (per-foot vs summed vs range). No resolution.",
    "C4": "Lead-foot peak vertical GRF: lab plates 1.09-1.24 BW (Okuda 1.09 skilled, Bourgain 1.18 pros/1.24 amateurs; v1 Han snippet 1.12) vs natural turf 0.84 BW (Worsfold, driver). Surface and shoe, not skill, probably explain it.",
    "C5": "Vertical-axis moment: Meister free moment 1.19 N*m/kg (about 99 N*m for 83 kg; 5-iron, hard, both feet on one plate) vs Worsfold foot torsional Tz 17-19 (front) + 6-7 (back) N*m on turf (driver) vs v1's Barrentine 17-26 N*m per foot. They measure different things (free moment about the combined CoP includes the couple of horizontal forces; foot Tz is torsional only). Do not use Worsfold Tz as the pelvis-yaw requirement.",
    "C6": "X-factor at impact: Madrid 9+-8 deg (FSP-based) vs Meister 33+-6 (hard 5-iron pros) vs Kwon: conventional horizontal-plane method gives substantially larger X-factor than FSP/Cardan methods. Top-of-backswing X-factor agrees better (Madrid 61, Meister 56, Parker 54.9, Chu 49 heterogeneous).",
    "C7": "Club-grip torque: Okamoto measured 40.9 N*m at 102.4 mph (n=3) vs the v1 linear fit through Nesbit's four swings (29 N*m at 100 mph, 45 at 120). Club peak power: Okamoto 2813 W at 102.4 mph vs v1 power-law about 2.2-2.4 kW at 100-102 mph. v1 under-predicts grip torque by ~30% and club peak power by ~15-20% at ~102 mph (n=3).",
    "C8": "Downswing duration: Sprigings simulation 380 ms vs measured professional 250-280 ms (Madrid, Bourgain, Okamoto, Sonic 258 ms snippet). Do not use the simulation timing.",
    "C9": f"Hip axial torque: Foxworth peaks (internal rotators 2.70 + 3.21 % BW*Ht, about {hip_pair_axial} N*m for both hips at the assumed 83 kg/1.80 m, amateurs at ~92 mph) vs v1's ~290 N*m 'average hip torque' derived from Nesbit hip WORK (flexion/extension dominated). The v1 number is an energy-equivalent, not an axial pelvis-turning torque.",
    "C10": "X-factor stretch: skilled joint-coordinate/FSP studies 1-6 deg (Madrid, Kwon, Parker) vs Cheetham 2001 sensor method ~19% (v1). Keep stretch as a small additive.",
}

REMAINING = [
    "No peak lumbar/trunk-axial or shoulder torque in N*m measured in a real swing was found in an open source (only Sprigings model torques and Foxworth hips in % BW*Ht).",
    "No joint-level biomechanics (peak speeds by segment, timing, GRF, X-factor) for a population above ~112 mph (n=14, snippet) apart from ONE 137 mph long-drive player's near-impact body speeds (Ichikawa 2024). No GRF at any speed above ~118 mph.",
    "Han 2019 GRF means (BW and N*m for the 63 skilled golfers), Kwon 2013 / Han 2019 style tables, Hellstrom 2009, Ball & Best primary, Wallace/Koenig/Mann, Ae, Lynn GRF, Healy segment peaks, Sasaki, Brown 2011 (female) remain abstract-level or not retrieved (paywalled).",
    "Horan & Kavanagh 2012 peak speeds (thorax 650, pelvis 507, CHS 50.1 m/s) are snippet-level; a full-text read is needed before use.",
    "Madrid on-plane speeds are not the same definition as Cheetham's 3-axis resultant speeds; a common-definition conversion was not found.",
    "Dependence of peak torque/power on CHS above 52 m/s (116 mph) is still extrapolation; torque-vs-CHS scaling exponents are assumptions.",
]

doc = {
    "_meta": {"title": "Kinematic-sequence / torque / GRF / X-factor reference v2 (open published sources only)",
              "version": 2, "extends": "data/references/kinematic_sequence_torque_reference.json (kseq-reference b78e5eb)",
              "contains_instagram_or_mason_derived_data": False, "generated": "2026-10-18",
              "status": "Published-only. Model-only above ~116 mph. Tags: fetched-full = full text/table read; abstract = abstract/landing page only; snippet = search-engine summary only (unverified); n/a = nothing found.",
              "tag_legend": {"fetched-full": "full text/tables read", "abstract": "abstract or landing page only", "snippet": "search-result summary only",
                             "carried-v1": "carried from v1 for comparison", "n/a": "no data found (explicit gap)"},
              "level_legend": ["measured", "secondary (quoted in another fetched paper)", "model (simulation output)", "derived (computed here, assumptions stated)", "none-found"]},
    "sources": SOURCES,
    "datapoints": DP,
    "derived": {
        "madrid_within_group_slopes_deg_s_per_m_s": {"values": SLOPES, "method": "slope = r * SD(variable) / SD(CHS), CHS SD 2.1 m/s, Madrid 2020 Table 4; regression-diluted lower bound; skilled-only range 4.8 mph SD",
                                                     "downswing_time_ms_per_m_s": DS_SLOPE},
        "segment_peak_by_chs": {"rows": rows, "note": "Madrid on-plane anchored at 110.4 mph vs v1 two-group 3-axis fit. Definitions differ; the spread is the uncertainty band. >116 mph extrapolated."},
        "downswing_duration_by_chs": {"rows": ds_rows, "slopes": {"within_group_madrid_ms_per_m_s": DS_SLOPE, "between_group_bourgain_ms_per_m_s": -2.5},
                                      "note": "v1 held 230 ms constant. Measured skilled drivers: 253+-26 (110 mph), 260+-20 (108.5), 280+-20 (102). Extrapolation beyond ~117 mph is unsupported."},
        "free_moment_by_chs": {"rows": fm_rows, "fit": {"proportional_k_Nm_per_kg_per_m_s": round(k_prop, 4), "linear_slope": round(b_lin, 4), "linear_intercept": round(a_lin, 3)},
                               "note": "three points (5-iron, within-pro effort); extrapolated 1.5-2x beyond the 35.4 m/s data; driver and 120+ mph not measured"},
        "grip_torque_by_chs": {"rows": grip_rows, "note": "Okamoto n=3 anchor + Nesbit 4-swing slope 1.83 N*m per m/s; mixed sources, derived"},
        "trunk_torque_model_scaling": {"rows": sprig_rows, "note": "Sprigings model trunk torque 75-95 N*m at 44.0 m/s scaled with v or v^2 (assumption, simulation basis)"},
        "xfactor_by_chs": xf,
        "peak_over_average_power": {"okamoto_club_peak_W": 2813.4, "okamoto_avg_W": round(213.2 / 0.28, 0), "ratio": round(2813.4 / (213.2 / 0.28), 2),
                                    "nesbit_club_ratio_v1": 2.5, "note": "club-level only; v1 used 2.5; measured 3 pros give 3.7"},
        "hip_torque_Nm_assumed_83kg_180m": {k: round(m * BWHT / 100, 1) for k, (m, _sd) in HIP.items()},
    },
    "conflicts": CONFLICTS,
    "remaining_gaps": REMAINING,
}
tags = {}
for d in DP:
    tags[d["tag"]] = tags.get(d["tag"], 0) + 1
doc["_meta"]["datapoint_counts_by_tag"] = tags
doc["_meta"]["datapoint_count_total"] = len(DP)
doc["_meta"]["new_datapoints_excluding_gaps_and_carried"] = sum(v for k, v in tags.items() if k in ("fetched-full", "abstract", "snippet"))

if __name__ == "__main__":
    with open(OUT, "w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    print(OUT, tags, len(DP))
