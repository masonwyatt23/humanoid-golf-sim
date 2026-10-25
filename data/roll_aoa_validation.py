"""MODEL-ONLY validation of data/roll_aoa_addon.py against MORE published data (standalone; imports nothing from env/, eval/, train/).
Datapoints live in data/references/roll_aoa_validation.json (rebuilt by build_datapoints()). Every datapoint carries url + tag:
  fetched = page/PDF opened in full this session (text read);  snippet = search-result excerpt/synthesis only (not opened).
Residual = model - published. Nothing here changes the add-on defaults. No Instagram-derived or Mason-clip data.
Run: python -m data.roll_aoa_validation   (rebuilds the JSON and prints stats)"""
import json
from pathlib import Path
import numpy as np
from data import roll_aoa_addon as A

ROOT = Path(__file__).resolve().parent.parent
JSON = ROOT / "data/references/roll_aoa_validation.json"
LABEL = "MODEL-ONLY / UNCALIBRATED validation: residuals of a Data-Agent heuristic vs published numbers; not a calibration"
U_TM = "https://wishongolf.com/wp-content/uploads/2012/07/TrackMan-Driver-Optimization_2010.pdf"
U_FS = "https://help.foresightsports.com/hc/en-us/articles/47208228295187-Ball-Launch-Data-Performance-Reference-Tables"
U_RA = "https://assets.randa.org/c42c7bf4-dca7-00ea-4f2e-373223f80f76/550ab9f6-5dd3-45b0-b58c-7563d4256c04/R07%20-%20Analysis%20of%20Trackman%20data%20gathered%20at%20World%20Long%20Drive.pdf"
U_BM = "https://assets-us-01.kc-usercontent.com/c42c7bf4-dca7-00ea-4f2e-373223f80f76/250b3e34-9172-4ad1-991f-9d5560cbf832/Proposed%20Bounce%20Model%20for%20Use%20in%20Evaluating%20Optimum%20Overall%20Distance.pdf"
U_USGA = "https://www.usga.org/content/dam/usga/pdf/2023/Golf-Course-Distance-Effects-Final.pdf"
U_RICE = "https://www.andrewricegolf.com/andrew-rice-golf/2012/11/optimal-driver-numbers"
U_GD = "https://www.golfdigest.com/story/fade-with-driver-draw-with-three-wood-distance-test-mythbusters"
U_BURKE = "https://golf.com/instruction/driving/long-drive-champ-golfer-trackman-numbers/"
U_TM23 = "https://smashfactorlab.com/trackman-tour-averages/"
U_TMPGA = "https://support.trackmangolf.com/hc/en-us/article_attachments/7349802113051/PGA_Tour_average.pdf"
U_TMTOT = "https://support.trackmangolf.com/hc/en-us/articles/39727276786843-Parameters-Total-Tee-to-Green"

# TrackMan Driver Fitting Charts 2010 (fetched via curl+pdftotext). rows: (AoA, ball_mph, launch, spin, carry, total, dynamic_loft); club speed 75..120 step 5, 3 AoA (-5,0,5) each.
TM_CARRY = [(-5,104,14.6,3722,143,166,18.2),(0,107,16.3,3121,154,178,19.2),(5,108,19.2,2720,164,187,21.8),(-5,113,12.9,3652,160,176,16.2),(0,115,15.5,3179,171,187,18.3),(5,116,18.0,2648,181,197,20.3),
 (-5,121,11.9,3669,175,199,15.0),(0,123,14.5,3164,187,211,17.1),(5,124,17.0,2596,197,223,19.1),(-5,129,11.1,3689,191,215,14.0),(0,131,13.4,3093,203,228,15.8),(5,132,16.4,2633,214,239,18.5),
 (-5,137,9.9,3626,207,243,12.6),(0,138,12.7,3114,219,244,15.0),(5,140,15.7,2595,231,256,17.6),(-5,144,9.6,3722,222,244,12.2),(0,146,12.1,3118,235,272,14.3),(5,148,14.9,2538,247,272,16.7),
 (-5,152,8.7,3675,237,260,11.1),(0,154,11.2,3038,251,275,13.2),(5,155,14.5,2563,263,288,16.2),(-5,160,7.7,3570,252,275,9.9),(0,162,10.5,2970,266,291,12.3),(5,163,13.7,2435,279,305,15.2),
 (-5,168,7.0,3548,266,290,9.2),(0,170,9.8,2919,281,306,11.6),(5,171,13.0,2358,295,321,14.4),(-5,176,6.1,3433,281,305,8.1),(0,178,9.3,2890,296,321,11.0),(5,179,12.6,2343,310,350,14.0)]
TM_TOTAL = [(-5,107,11.8,3214,140,182,14.9),(0,109,13.0,2506,147,195,15.3),(5,111,15.3,1976,156,206,17.1),(-5,115,10.1,3078,154,188,12.8),(0,117,12.1,2494,163,199,14.3),(5,118,14.8,2005,174,209,16.5),
 (-5,123,9.3,3110,169,215,11.9),(0,125,11.7,2568,180,228,13.8),(5,126,14.0,1964,189,241,15.6),(-5,131,8.5,3122,185,231,11.0),(0,132,10.8,2517,196,245,12.8),(5,134,13.8,2021,207,259,15.3),
 (-5,138,7.9,3144,201,247,10.2),(0,140,10.5,2565,213,262,12.3),(5,141,13.0,1948,223,276,14.4),(-5,146,7.2,3118,216,262,9.3),(0,148,10.0,2570,230,278,11.7),(5,149,12.4,1887,239,293,13.7),
 (-5,154,6.4,3071,231,278,8.4),(0,156,9.1,2461,243,294,10.7),(5,157,11.7,1810,254,309,12.9),(-5,162,5.6,3005,245,293,7.5),(0,163,8.7,2471,260,310,10.2),(5,165,11.1,1716,268,326,12.2),
 (-5,170,5.3,3030,261,307,7.1),(0,171,8.0,2396,274,325,9.5),(5,172,10.7,1681,285,342,11.7),(-5,178,4.5,2929,273,322,6.2),(0,179,7.7,2382,290,340,9.0),(5,180,10.3,1636,300,358,11.3)]
# Foresight optimized driver table (fetched): club, ball, carry_lo, carry_hi, total_lo, total_hi, spin_hi(at 10 deg), spin_lo(at 14 deg); launch range 10-14 in every row.
FS = [(69,100,130,142,159,169,3500,2500),(76,110,157,170,181,194,3400,2400),(83,120,183,197,204,221,3300,2300),(90,130,207,223,227,246,3200,2200),(97,140,231,249,250,272,3100,2110),
 (103,150,254,275,273,299,3000,2000),(110,160,276,301,295,325,2900,1900),(117,170,298,325,318,349,2800,1800),(124,180,320,349,340,386,2700,1700),(131,190,342,372,378,401,2600,1600),
 (138,200,360,389,381,418,2500,1500),(145,210,383,408,405,438,2400,1400)]
# Andrew Rice / TrackMan chart (snippet): club, ball, launch, carry, total; text says +5 deg AoA, spin 1900-2200 rpm, normal ground (spin assumed 2050 = midpoint).
RICE = [(65,96,16.5,136,182),(75,111,15.6,157,208),(85,126,14.6,193,242),(90,133,14.2,209,256),(95,140,13.7,225,271),(100,148,13.2,242,286),(105,156,12.6,259,303)]

def _dp(id, source, url, tag, **kw):
    d = dict(id=id, source=source, url=url, tag=tag, club_mph=None, ball_mph=None, aoa_deg=None, launch_deg=None, spin_rpm=None, dynamic_loft_deg=None, carry_yd=None, total_yd=None,
             descent_deg=None, firmness_label="unspecified", flags=[], notes="")
    d.update(kw); return d

def build_datapoints():
    out = []
    for name, tab in (("carry", TM_CARRY), ("total", TM_TOTAL)):
        for i, (aoa, ball, la, sp, c, t, dl) in enumerate(tab):
            out.append(_dp(f"tm_{name}_{75+5*(i//3)}_{aoa:+d}", f"TrackMan Driver Fitting Chart 2010, {name.upper()} optimizer", U_TM, "fetched", group=f"tm_{name}_opt",
                           club_mph=75 + 5 * (i // 3), ball_mph=ball, aoa_deg=aoa, launch_deg=la, spin_rpm=sp, dynamic_loft_deg=dl, carry_yd=c, total_yd=t, firmness_label="normal (TrackMan: calculated total, flat, 'normal' hardness)",
                           notes="TrackMan total is a CALCULATED value (U_TMTOT), not a measured roll."))
    for club, ball, c0, c1, t0, t1, s0, s1 in FS:
        out.append(_dp(f"fs_{club}", "Foresight Optimized Driver Launch Data (ranges; midpoints used)", U_FS, "fetched", group="foresight", club_mph=club, ball_mph=ball, launch_deg=12.0, spin_rpm=(s0 + s1) / 2,
                       carry_yd=(c0 + c1) / 2, total_yd=(t0 + t1) / 2, notes=f"carry {c0}-{c1}, total {t0}-{t1}, launch 10-14, spin {s1}-{s0}; midpoints, not row data. Turf firmness not stated."))
    out.append(_dp("ra_pga_113", "R&A WLD report Table 4: PGA-Tour-average launch simulated for a Volvik ball, 'long' orientation", U_RA, "fetched", group="ra_sim", club_mph=113, ball_mph=167, launch_deg=10.9, spin_rpm=2686, carry_yd=272, total_yd=291,
                   notes="Simulation (USGA/R&A bounce model of the time), not a measurement."))
    out.append(_dp("ra_lpga_94", "R&A WLD report Table 4: LPGA-average launch simulated, 'long' orientation", U_RA, "fetched", group="ra_sim", club_mph=94, ball_mph=140, launch_deg=13.2, spin_rpm=2611, carry_yd=223, total_yd=244, notes="Simulation."))
    for club, ball, la, c, t in RICE:
        out.append(_dp(f"rice_{club}", "Andrew Rice Golf 'Optimal Driver Numbers' chart (made with TrackMan)", U_RICE, "snippet", group="rice", club_mph=club, ball_mph=ball, aoa_deg=5, launch_deg=la, spin_rpm=2050, carry_yd=c, total_yd=t,
                       firmness_label="normal (page: 'normal ground conditions')", notes="spin is an ASSUMED midpoint of the stated 1900-2200 rpm; AoA +5 and flat terrain stated on page."))
    out.append(_dp("burke_141", "Tim Burke 409 yd practice drive, TrackMan (GOLF.com; carry/total from search synthesis, not in fetched page text)", U_BURKE, "snippet", group="longdrive", club_mph=141.3, ball_mph=211.9, aoa_deg=8, launch_deg=None, spin_rpm=1850,
                   carry_yd=380.6, total_yd=409.5, flags=["carry_total_unverified_in_fetched_text", "launch_unknown"], notes="Fetched page text confirms 141.3 mph, ~1.5 smash, AoA almost 8, 1850 rpm, '409-yard'; carry 380.6 / total 409.5 only from a search synthesis. Launch not given (11.0 assumed for model input)."))
    out.append(_dp("golfdigest_test", "Golf Digest driver test (search synthesis)", U_GD, "snippet", group="other", carry_yd=220.6, total_yd=241.2, flags=["no_launch_spin_speed"], notes="No club speed/launch/spin; used only as a ratio sanity check, excluded from model residuals."))
    # descent-angle datapoints (for estimate_descent_deg)
    out += [
        _dp("desc_pga_old", "TrackMan PGA Tour averages (older table)", U_TMPGA, "snippet", group="descent", club_mph=113, ball_mph=167, aoa_deg=-1.3, launch_deg=10.9, spin_rpm=2686, carry_yd=275, descent_deg=38, notes="Anchor of the add-on heuristic; R&A report (fetched) has the same speed/launch/spin/carry 275 but no landing angle."),
        _dp("desc_pga_2023", "TrackMan 2023 PGA Tour driver average (third-party transcription)", U_TM23, "snippet", group="descent", club_mph=115, ball_mph=171, aoa_deg=-0.9, launch_deg=10.4, spin_rpm=2545, carry_yd=282, descent_deg=39, notes="Transcribed by eye from TrackMan graphics by the site (its own words)."),
        _dp("desc_lpga_2023", "TrackMan 2023 LPGA Tour driver average (third-party transcription)", U_TM23, "snippet", group="descent", club_mph=96, ball_mph=143, aoa_deg=2.8, launch_deg=12.6, spin_rpm=2506, carry_yd=223, descent_deg=36),
        _dp("desc_usga_pga", "USGA Golf Course Effects report: typical PGA Tour drive inbound angle 38-39 deg", U_USGA, "fetched", group="descent", club_mph=None, descent_deg=38.5, notes="range 38-39, midpoint"),
        _dp("desc_usga_ods", "USGA/R&A bounce-model report: mean terminal angle of 94 ODS-tested balls = 37.6 deg (range 35 to >40)", U_BM, "fetched", group="descent", club_mph=109, descent_deg=37.6, notes="ODS driver launch conditions ~109 mph per the report text on bounce model calibration")]
    return out

# ---- roll-vs-descent-angle and firmness evidence (fetched, U_BM / U_USGA) ----
BOUNCE_TABLE1 = [dict(site="USGA Range 2003", slope=-1.56, intercept=90.7, d39=30), dict(site="Philadelphia CC 2011 (17th)", slope=-1.91, intercept=110.8, d39=23), dict(site="Philadelphia CC 2011 (18th)", slope=-2.01, intercept=100.8, d39=37),
    dict(site="Rutgers turf farm 2014 (creeping)", slope=-0.74, intercept=54.6, d39=19), dict(site="Rutgers turf farm 2014 (colonial)", slope=-1.43, intercept=74.7, d39=26), dict(site="Lehigh CC 2018 (pre-irrigation)", slope=-2.45, intercept=120.3, d39=25),
    dict(site="Lehigh CC 2018 (post-irrigation)", slope=-0.98, intercept=58.2, d39=15), dict(site="USGA Range 2019 (low speed)", slope=-1.79, intercept=88.3, d39=18)]
BOUNCE_TOUR = dict(shotlink_2016_18_slope=-1.52, shotlink_2016_18_intercept=81, shotlink_2016_18_d39_mean_text=22, shotlink_2016_18_d39_mean_fig1_caption=26.5, quintavalla_2007_slope=-1.24, quintavalla_2007_d39_mean=30, quintavalla_2007_d39_range=(17.9, 41.6),
                   proposed_model="d = 79.1 - 1.6*alpha (yards, alpha deg)", proposed_slope=-1.6, proposed_intercept=79.1)
FIRMNESS_DATA = dict(broadie_shotlink_vs_firm_yd=dict(medium=-4.49, soft=-9.80, unknown=-4.09), lehigh_pre_post_irrigation_d39=(25, 15), usga_2018_moisture_plus5_8pct_reduction_yd=dict(range=(2, 15), average=(5, 10)), johnson_2008_venue_range_yd=(5, 30))

def model_row(dp, firmness="normal"):
    launch = dp["launch_deg"] if dp["launch_deg"] is not None else 11.0
    return A.estimate_roll_yd(dp["carry_yd"], launch_deg=launch, spin_rpm=dp["spin_rpm"], firmness=firmness)

def usable(dp):
    return dp["carry_yd"] and dp["total_yd"] and dp["spin_rpm"] is not None and "no_launch_spin_speed" not in dp["flags"]

def flag_tm_outliers(dps, thresh=8.0):
    """Flag TrackMan rows whose published roll deviates > thresh yd from the median roll of the same optimizer & AoA across club speeds (deterministic, data-internal)."""
    for g in ("tm_carry_opt", "tm_total_opt"):
        rows = [d for d in dps if d.get("group") == g]
        for aoa in (-5, 0, 5):
            sel = [d for d in rows if d["aoa_deg"] == aoa]; med = float(np.median([d["total_yd"] - d["carry_yd"] for d in sel]))
            for d in sel:
                if abs(d["total_yd"] - d["carry_yd"] - med) > thresh and "roll_outlier_within_chart" not in d["flags"]: d["flags"].append("roll_outlier_within_chart")
    return dps

def residuals(dps, firmness="normal", params=None):
    rows = []
    for d in dps:
        if not usable(d) or d.get("group") == "descent": continue
        m = model_row(d, firmness) if params is None else params(d)
        pub_roll = d["total_yd"] - d["carry_yd"]
        rows.append(dict(id=d["id"], group=d["group"], tag=d["tag"], club_mph=d["club_mph"], aoa=d["aoa_deg"], flags=d["flags"], pub_roll=pub_roll, model_roll=m["roll_yd"], res_roll=m["roll_yd"] - pub_roll,
                         pub_ratio=d["total_yd"] / d["carry_yd"], model_ratio=m["total_over_carry"], res_ratio=m["total_over_carry"] - d["total_yd"] / d["carry_yd"], res_total=m["total_yd"] - d["total_yd"]))
    return rows

def stats(rows, key="res_roll"):
    x = np.array([r[key] for r in rows], float)
    if not len(x): return dict(n=0)
    return dict(n=int(len(x)), bias=round(float(x.mean()), 3), mae=round(float(np.abs(x).mean()), 3), rmse=round(float(np.sqrt((x ** 2).mean())), 3), min=round(float(x.min()), 3), max=round(float(x.max()), 3))

def band(c):
    return "<=95" if c <= 95 else ("100-110" if c <= 110 else ("115-120" if c <= 120 else ">=124"))

def group_stats(rows):
    out = {}
    def add(k, rs):
        out[k] = dict(roll_yd=stats(rs, "res_roll"), ratio=stats(rs, "res_ratio"), total_yd=stats(rs, "res_total"))
    add("ALL", rows)
    add("ALL_without_tm_outliers", [r for r in rows if "roll_outlier_within_chart" not in r["flags"]])
    for g in sorted({r["group"] for r in rows}): add("group:" + g, [r for r in rows if r["group"] == g])
    for b in ("<=95", "100-110", "115-120", ">=124"): add("club_mph:" + b, [r for r in rows if r["club_mph"] and band(r["club_mph"]) == b and "roll_outlier_within_chart" not in r["flags"]])
    for a in (-5, 0, 5): add(f"tm_aoa:{a:+d}", [r for r in rows if r["group"].startswith("tm_") and r["aoa"] == a and "roll_outlier_within_chart" not in r["flags"]])
    return out

def descent_residuals(dps):
    rows = []
    for d in dps:
        if d.get("group") != "descent" or d["launch_deg"] is None: continue
        est = A.estimate_descent_deg(d["launch_deg"], d["spin_rpm"])
        rows.append(dict(id=d["id"], pub=d["descent_deg"], model=round(est, 2), res=round(est - d["descent_deg"], 2), tag=d["tag"]))
    return rows

def roll_vs_descent_check(carries=(250, 275, 300, 325), spin=2686.0):
    """Model d(roll)/d(descent) in yd/deg and absolute roll at 39 deg vs the USGA/R&A experiments (fetched): slopes -0.74..-2.45 (median of Table 1 = -1.7), ShotLink -1.52, Quintavalla -1.24; roll@39deg 15-37 (tests), 22-30 (tour)."""
    rows = []
    for c in carries:
        r1 = A.estimate_roll_yd(c, descent_deg=38.5, spin_rpm=spin)["roll_yd"]; r2 = A.estimate_roll_yd(c, descent_deg=39.5, spin_rpm=spin)["roll_yd"]
        r39 = A.estimate_roll_yd(c, descent_deg=39.0, spin_rpm=spin)["roll_yd"]
        rows.append(dict(carry_yd=c, model_slope_yd_per_deg=round(r2 - r1, 2), model_roll_at_39deg=r39, proposed_usga_model_roll_at_39=round(79.1 - 1.6 * 39, 1)))
    sl = [t["slope"] for t in BOUNCE_TABLE1]
    return dict(rows=rows, published_slope_median=float(np.median(sl)), published_slope_range=(min(sl), max(sl)), published_d39_range=(min(t["d39"] for t in BOUNCE_TABLE1), max(t["d39"] for t in BOUNCE_TABLE1)))

def firmness_check(carry=296.0, launch=10.4, spin=2400.0):
    """Model firmness multipliers vs data-implied ones. Model roll at normal for the given shot; tour data say medium->soft = -5.3 yd total and firm vs medium = +4.5 yd (Broadie, fetched); Lehigh pre/post irrigation roll ratio 15/25 = 0.6 (fetched, one fairway)."""
    base = A.estimate_roll_yd(carry, launch_deg=launch, spin_rpm=spin, firmness="normal")["roll_yd"]
    rows = {}
    for f in ("soft", "normal", "firm", "very_firm"):
        r = A.estimate_roll_yd(carry, launch_deg=launch, spin_rpm=spin, firmness=f)["roll_yd"]; rows[f] = dict(model_roll_yd=r, model_minus_normal_yd=round(r - base, 1), multiplier=A.FIRMNESS[f])
    d = FIRMNESS_DATA["broadie_shotlink_vs_firm_yd"]
    rows["data_tour_total_distance_deltas_vs_medium"] = dict(soft=round(d["soft"] - d["medium"], 2), firm=round(-d["medium"], 2), unit="yd of TOTAL distance (ShotLink, ~285 yd avg drives; includes any carry effect)")
    rows["data_implied_multiplier_given_base_roll"] = dict(soft=round(max(0.0, (base + (d["soft"] - d["medium"])) / base), 2), firm=round((base + (-d["medium"])) / base, 2), lehigh_post_over_pre=round(15 / 25, 2))
    return rows

def refit_on_tm(dps):
    """Least-squares refit of (BASE, DESC_COEF, SPIN_COEF) on TrackMan-chart rows (non-outlier) with the add-on's descent heuristic fixed. Reported, NOT applied. It fits TrackMan's calculated totals, not measured roll."""
    from scipy.optimize import least_squares
    tm = [d for d in dps if d.get("group", "").startswith("tm_") and "roll_outlier_within_chart" not in d["flags"]]
    def pred(p, d):
        base, dc, sc = p; desc = A.estimate_descent_deg(d["launch_deg"], d["spin_rpm"])
        frac = np.clip(base * max(1 + dc * (A.DESC_REF - desc), 0) * max(1 + sc * (A.SPIN_REF - d["spin_rpm"]), 0), 0, 0.35); return d["carry_yd"] * frac
    f = lambda p: [pred(p, d) - (d["total_yd"] - d["carry_yd"]) for d in tm]
    sol = least_squares(f, [A.BASE_ROLL_FRAC, A.DESC_COEF, A.SPIN_COEF], bounds=([0.01, 0.0, 0.0], [0.3, 0.5, 0.005]))
    base, dc, sc = [float(x) for x in sol.x]
    def params(d):
        r = pred(sol.x, d); return dict(roll_yd=r, total_yd=d["carry_yd"] + r, total_over_carry=(d["carry_yd"] + r) / d["carry_yd"])
    held = [d for d in dps if not d.get("group", "").startswith("tm_") and d.get("group") not in ("descent",) and usable(d) and "burke" not in d["id"]]
    return dict(fit=dict(BASE_ROLL_FRAC=round(base, 4), DESC_COEF=round(dc, 4), SPIN_COEF=round(sc, 6)), n_fit=len(tm), in_sample=stats(residuals(tm, params=params)),
                held_out_other_sources=stats(residuals(held, params=params)), held_out_default_model=stats(residuals(held)), in_sample_default_model=stats(residuals(tm)),
                held_out_by_group={g: dict(fit=stats([r for r in residuals(held, params=params) if r["group"] == g]), default=stats([r for r in residuals(held) if r["group"] == g])) for g in sorted({d["group"] for d in held})})

def aoa_checks(dps):
    """Tutelman launch (SL = DL - AoA) vs the TrackMan chart (dynamic loft listed per row, fetched); env-formula spin vs chart spin; empirical sensitivities."""
    tm = [d for d in dps if d.get("group", "").startswith("tm_")]
    L, S = [], []
    for d in tm:
        sl = d["dynamic_loft_deg"] - d["aoa_deg"]
        L.append(dict(id=d["id"], group=d["group"], res=A.tutelman_launch(d["aoa_deg"], sl) - d["launch_deg"]))
        S.append(dict(id=d["id"], group=d["group"], res=A.env_spin_rpm(d["ball_mph"], d["launch_deg"]) - d["spin_rpm"], sl=sl, ball=d["ball_mph"], spin=d["spin_rpm"]))
    st = lambda rows: stats(rows, "res")
    X = np.array([[1, d["aoa_deg"], d["dynamic_loft_deg"]] for d in tm]); y = np.array([d["launch_deg"] for d in tm]); coef = np.linalg.lstsq(X, y, rcond=None)[0]
    # chart-implied spin model: spin = k * ball_mph * spin_loft  (through origin)
    xs = np.array([s["ball"] * s["sl"] for s in S]); ys = np.array([s["spin"] for s in S]); k = float((xs @ ys) / (xs @ xs)); sres = ys - k * xs
    # tutelman-implied launch slopes vs empirical sensitivity at fixed club speed across AoA -5/0/+5
    emp = {}
    for g in ("tm_carry_opt", "tm_total_opt"):
        rows = [d for d in tm if d["group"] == g]; dl, ds, dd = [], [], []
        for c in sorted({d["club_mph"] for d in rows}):
            r = sorted([d for d in rows if d["club_mph"] == c], key=lambda d: d["aoa_deg"]); dl.append((r[2]["launch_deg"] - r[0]["launch_deg"]) / 10); ds.append((r[2]["spin_rpm"] - r[0]["spin_rpm"]) / 10); dd.append((r[2]["dynamic_loft_deg"] - r[0]["dynamic_loft_deg"]) / 10)
        emp[g] = dict(launch_deg_per_aoa_deg=round(float(np.mean(dl)), 3), spin_rpm_per_aoa_deg=round(float(np.mean(ds)), 1), dynamic_loft_deg_per_aoa_deg=round(float(np.mean(dd)), 3))
    return dict(tutelman_launch_residual_all=st(L), tutelman_launch_residual_by_group={g: st([r for r in L if r["group"] == g]) for g in ("tm_carry_opt", "tm_total_opt")},
                env_formula_spin_residual_all=st(S), env_formula_spin_residual_by_group={g: st([r for r in S if r["group"] == g]) for g in ("tm_carry_opt", "tm_total_opt")},
                chart_ols_launch_eq=dict(intercept=round(float(coef[0]), 3), per_aoa_deg_at_fixed_dynamic_loft=round(float(coef[1]), 3), per_dynamic_loft_deg_at_fixed_aoa=round(float(coef[2]), 3), note="OLS over 60 chart rows; optimizer rows are not a controlled experiment"),
                model_sensitivity_per_deg=A.sensitivity_per_deg(), chart_empirical_sensitivity_per_aoa_deg=emp,
                chart_implied_spin_model=dict(k_rpm_per_mph_per_deg_spin_loft=round(k, 3), rmse_rpm=round(float(np.sqrt((sres ** 2).mean())), 1), form="spin = k * ball_mph * (dynamic_loft - AoA)"),
                chart_note="At fixed club speed the chart spin falls ~100-250 rpm per +1 deg AoA because the optimizer also changes dynamic loft; add-on's fixed-dynamic-loft case (+28 rpm) and fixed-spin-loft case (+188 rpm) both have the WRONG sign vs the chart for spin")

def case_350(params=None):
    out = {}
    for fm in ("soft", "normal", "firm"):
        out[fm] = {m: A.estimate_total_from_m(m, launch_deg=10.4, spin_rpm=2400, firmness=fm)["total_yd"] for m in (293, 296, 299)}
    return out

def absolute_roll_alternative(dps):
    """Alternative framing from the fetched USGA/R&A data: bounce-and-roll is ~constant YARDS set by terminal angle (slope ~-1.6 yd/deg), not a fraction of carry. Roll at 36-39 deg => 18-31 yd. 
    Compare total at carry 324 yd (296 m) for: add-on fraction model vs USGA proposed linear model (79.1 - 1.6*alpha) vs ShotLink mean (+22..30 yd at 39 deg)."""
    rows = []
    for alpha in (32, 35, 38, 40):
        rows.append(dict(descent_deg=alpha, usga_proposed_roll_yd=round(79.1 - 1.6 * alpha, 1), addon_roll_yd_carry324=A.estimate_roll_yd(324, descent_deg=alpha, spin_rpm=2400)["roll_yd"]))
    return rows


def roll_vs_carry_slopes(dps):
    """Published roll (total-carry, yd) regressed on carry per source group: slope ~0 means roll is ~constant yards, i.e. NOT proportional to carry as the add-on assumes (add-on slope = BASE*factors ~0.09-0.12)."""
    out = {}
    for g in sorted({d["group"] for d in dps if usable(d) and d["group"] not in ("descent", "other")}):
        rows = [d for d in dps if d["group"] == g and usable(d) and "roll_outlier_within_chart" not in d["flags"]]
        if len(rows) < 4: continue
        x = np.array([d["carry_yd"] for d in rows]); y = np.array([d["total_yd"] - d["carry_yd"] for d in rows]); b, a = np.polyfit(x, y, 1)
        out[g] = dict(n=len(rows), slope_yd_roll_per_yd_carry=round(float(b), 3), intercept_yd=round(float(a), 1), roll_min=float(y.min()), roll_max=float(y.max()), roll_median=float(np.median(y)))
    return out

def high_speed_evidence(dps, carry_yd=296 * A.YD_PER_M):
    """Roll evidence at the operating point (env carry 293-299 m = 320-327 yd, ~130 mph club speed) and the roll needed for a 350 yd TOTAL."""
    need = lambda c: round(350 - c, 1)
    fs = [d for d in dps if d["group"] == "foresight" and d["club_mph"] >= 124]
    ev = {"foresight_124_145mph_roll_yd(fetched, midpoints)": [d["total_yd"] - d["carry_yd"] for d in fs],
          "burke_141mph_roll_yd(snippet, weak)": [dps_get(dps, "burke_141")["total_yd"] - dps_get(dps, "burke_141")["carry_yd"]],
          "usga_proposed_linear_model_descent_33_35_38_40deg(fetched)": [round(79.1 - 1.6 * a, 1) for a in (33, 35, 38, 40)],
          "shotlink_tour_mean_at_39deg(fetched; text 22, Fig.1 caption 26.5, Quintavalla 2007 30)": [22, 26.5, 30],
          "tm_total_optimizer_120mph_spin<=2400(fetched; TrackMan-calculated)": [dps_get(dps, f"tm_total_120_{a:+d}")["total_yd"] - dps_get(dps, f"tm_total_120_{a:+d}")["carry_yd"] for a in (0, 5)],
          "addon_normal_roll_yd(launch 10.4, spin 2400; model)": [A.estimate_roll_yd(carry_yd + dm, launch_deg=10.4, spin_rpm=2400)["roll_yd"] for dm in (-3 * A.YD_PER_M, 0, 3 * A.YD_PER_M)]}
    return dict(carry_m_cases={293: round(293 * A.YD_PER_M, 1), 296: round(296 * A.YD_PER_M, 1), 299: round(299 * A.YD_PER_M, 1)},
                roll_needed_for_350_total_yd={m: need(293 * A.YD_PER_M if m == 293 else (296 * A.YD_PER_M if m == 296 else 299 * A.YD_PER_M)) for m in (293, 296, 299)}, evidence=ev)

def dps_get(dps, id):
    return next(d for d in dps if d["id"] == id)

def build():
    dps = flag_tm_outliers(build_datapoints())
    res = residuals(dps)
    out = dict(label=LABEL, written="2026-10-17 America/New_York", addon_defaults_unchanged=True, datapoints=dps,
               counts=dict(total=len(dps), fetched=sum(d["tag"] == "fetched" for d in dps), snippet=sum(d["tag"] == "snippet" for d in dps), used_in_residuals=len(res),
                           tm_rows=sum(d.get("group", "").startswith("tm_") for d in dps), tm_outliers=sum("roll_outlier_within_chart" in d["flags"] for d in dps)),
               bounce_table1_usga_experiments=BOUNCE_TABLE1, bounce_tour=BOUNCE_TOUR, firmness_data=FIRMNESS_DATA,
               residuals_normal=res, stats_normal=group_stats(res),
               residuals_firm_for_reference=group_stats(residuals(dps, "firm")), descent_heuristic_residuals=descent_residuals(dps), roll_vs_descent=roll_vs_descent_check(),
               firmness_check=firmness_check(), absolute_roll_alternative=absolute_roll_alternative(dps), refit_on_trackman_not_applied=refit_on_tm(dps), roll_vs_carry_slopes=roll_vs_carry_slopes(dps), high_speed_evidence=high_speed_evidence(dps), aoa_checks=aoa_checks(dps), sample_350_cases_unchanged=case_350())
    JSON.write_text(json.dumps(out, indent=1, default=lambda o: list(o) if isinstance(o, tuple) else str(o))); return out

if __name__ == "__main__":
    o = build(); print(json.dumps(o["counts"])); s = o["stats_normal"]
    for k, v in s.items(): print(k, v["roll_yd"], v["ratio"]["bias"])
    print(json.dumps({k: o[k] for k in ("descent_heuristic_residuals", "roll_vs_descent", "firmness_check", "absolute_roll_alternative", "refit_on_trackman_not_applied", "aoa_checks")}, indent=1, default=str))
