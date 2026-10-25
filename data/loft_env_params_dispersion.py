"""Build data/references/loft_env_params_dispersion.json (model rows part). PUBLIC SOURCES ONLY; no Instagram/Mason-clip data.
Reuses run() from data.targets_130mph_350yd (read-only import of env/ball_flight_analytic.py). ~3 min.
Run: python -m data.loft_env_params_dispersion"""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data.targets_130mph_350yd import run, tut_launch
OUT_ROWS = ROOT / "data/references/_loft_model_rows.json"
MPH = 0.44704

def env_spin(ball_mph, launch, spin_k=130.0):
    """env/humanoid_golf_env.py impact_model: rpm = spin_k * |v_ball| * sin(radians(max(elev+2,0))), clipped 0..6000 (m/s)."""
    return float(np.clip(spin_k * ball_mph * MPH * np.sin(np.radians(max(launch + 2.0, 0.0))), 0, 6000))

# (label, AoA, dynamic loft)  -- dynamic loft = static head loft + shaft/wrist/face-roll offset (offset itself is NOT sourced)
CFG = [("A baseline power tier (AoA +5, DL 14.5)", 5, 14.5), ("B lower DL only (AoA +5, DL 12.5)", 5, 12.5), ("C lower DL more (AoA +5, DL 11.0)", 5, 11.0),
       ("D AoA +3, DL 10.5", 3, 10.5), ("E AoA 0, DL 9.0", 0, 9.0), ("F AoA +2, DL 9.5", 2, 9.5), ("G AoA +4, DL 9.0", 4, 9.0)]
def sweep():
    rows = []
    for mph in (100, 120, 130):
        for lab, a, dl in CFG:
            for K in (4.0, 5.6):
                r = run(mph, a, dl, K=K); r["config"] = lab; r["env_impact_model_spin_k130_rpm"] = round(env_spin(r["ball_mph"], r["launch_deg"]))
                rows.append(r); print(mph, lab, K, r["launch_deg"], r["spin_rpm"], r["carry_yd"], r["total_yd"], flush=True)
    json.dump(rows, open(OUT_ROWS, "w"), indent=1)

# ---------------- dispersion model + JSON assembly ----------------
C_CURVE = 9.0 / 275.0   # yd of curve per deg face-to-path per yd carry: TrackMan PGA driver 275 yd carry: F2P 2 deg ~19 yd, 5 deg ~44 yd (=9.5, 8.8 yd/deg); mean 9.0
START_F, START_P = 0.76, 0.24   # PING/Wood et al. 2018: horizontal launch ratio toward face angle, driver 76 +-8 % (n=89, filtered)

def lateral_sigma_yd(D, s_face, s_path):
    """1-sigma lateral miss (yd) at carry D, face and path independent, zero-mean, small angles; start = .76 f + .24 p, curve = C*D*(f-p). MODEL (not a source)."""
    kf = D * (np.pi / 180) * START_F + C_CURVE * D; kp = D * (np.pi / 180) * START_P - C_CURVE * D
    return float(np.hypot(kf * s_face, kp * s_path))

def calibrate_s(D, sigma_alpha_deg):
    """face=path sigma (deg) so lateral sigma = D*tan(sigma_alpha) (Broadie direction sigma, which includes start line + curve + roll)."""
    return float(D * np.tan(np.radians(sigma_alpha_deg)) / lateral_sigma_yd(D, 1.0, 1.0))

def main():
    rows = json.load(open(OUT_ROWS))
    carry = {m: next(r["carry_yd"] for r in rows if r["club_mph"] == m and r["config"].startswith("F") and r["K"] == 4.0) for m in (100, 120, 130)}
    disp = []
    for lab, sa in (("PGA Tour pro (Broadie 'Pro', long tee shots)", 4.0), ("low-handicap amateur (Broadie 'Am1', scoring avg 70-83; closest published to a +3)", 5.4)):
        sref = calibrate_s(297.0, sa)
        for m in (100, 120, 130):
            D = carry[m]
            disp.append(dict(group=lab, club_mph=m, carry_yd_model=D, sigma_alpha_deg_published=sa, face_sigma_deg_calibrated=round(sref, 2), path_sigma_deg_calibrated=round(sref, 2),
                             start_line_sigma_deg=round(float(np.hypot(START_F * sref, START_P * sref)), 2), lateral_sigma_yd_1sigma=round(lateral_sigma_yd(D, sref, sref), 1),
                             lateral_width_68pct_yd=round(2 * lateral_sigma_yd(D, sref, sref), 0), lateral_width_95pct_yd=round(4 * lateral_sigma_yd(D, sref, sref), 0), basis="model, calibrated to Broadie sigma(alpha) at 297 yd; face=path sigma assumed equal and independent (no published split) -> UNVERIFIED split"))
    d = json.load(open(ROOT / "data/references/targets_130mph_350yd_and_loft.json"))
    out = dict(schema_version=1, name="loft_env_params_dispersion", built_for="Trainer: env loft params + stock lateral scatter; written 2026-10-17 America/New_York",
        honesty=["No Instagram-derived or Mason-clip data, no video. Mason's 120+ mph is self-reported and unverified.",
                 "Ball rows are the repo analytic model (env/ball_flight_analytic.py, read-only import): MODEL, NOT a source. Dynamic loft = static loft_deg + unknown shaft/wrist offset (no published conversion).",
                 "No MuJoCo contact sweep was run: how loft_deg and AoA map to env launch needs a policy rollout (Trainer)."],
        env_params=[
          dict(param="loft_deg", where="HumanoidGolfEnv.__init__ (env/humanoid_golf_env.py ~L117): head box geom_quat about y; None keeps the XML euler (3 deg in v2/v3/v4_power xml)", effect="static face tilt; launch ~ +0.85 deg per deg of dynamic loft at fixed AoA (model slope B->A rows)", suggested="reduce by ~5-6 deg from the loft that gave 12.6 deg launch to hit ~8 deg launch (model); verify by rollout", basis="model"),
          dict(param="attack angle (no direct param)", where="set by scripted swing (shoulder pitch q_fin/timing, wrist release) and ball_x / ball_x_noise", effect="launch ~ AoA + 0.85-0.9*SL; spin falls with AoA at fixed dyn loft", suggested="AoA +2..+4 for 130 mph; arc geometry: ball_x shift dx moves AoA by ~dx/R rad, R = pivot-to-head ~1.6-1.8 m ASSUMED (0.05 m ~ 1.7 deg; ball_x_noise 0.03 m ~ +-1 deg)", basis="derived geometry, R unverified"),
          dict(param="ball_dz / tee_height", where="env/humanoid_golf_env.py L376/L400: ball z = 0.021 + tee_height + ball_dz", effect="where on the face/arc the strike lands (impact_model dz0 -0.019 centres the face-strike height term); raising the ball relative to the arc lowers spin, raises launch for a given face", suggested="keep strike within +-0.02 m of dz0; do not use ball_dz as a loft knob", basis="code reading"),
          dict(param="impact_model.spin_k / gain / k_off / dz0 / k_side", where="env post-contact (humanoid_golf_env.py ~L475-485)", effect="launch direction comes from MuJoCo contact (NOT overwritten); gain scales ball speed; spin rpm = spin_k*|v_ball|*sin(radians(max(launch_elev+2,0))), clipped 0-6000; sidespin = k_side*dy", suggested="spin_k 130 (v4yaw) gives rows in env_impact_model_spin_k130_rpm; at 8-9 deg launch spin_k=130 gives ~1500-2000 rpm at 100-130 mph (rows); to hold ~2200-2500 use spin_k ~150-165 (arithmetic scaling, e.g. 130*2300/1991); lower launch lowers env spin automatically, so re-check the 1800-3000 gate band", basis="code reading + arithmetic"),
          dict(param="elev_target_deg / elev_weight", where="ResidualGolfEnv (env/residual_golf_env.py L30, L336, L373)", effect="reward centres launch at elev_target_deg=12.5 default (and fallback rpm 1500+70*elev); a policy is pulled to 12.5-12.6 by this term", suggested="set elev_target_deg ~8-9 (model carry optimum at 130 mph is ~10-11 deg, see table) to move launch toward 7.8; THIS is the most likely reason power tier sits at 12.6", basis="code reading"),
          dict(param="wrist command lead (style_lead / wr_lead ~0.06 s)", where="ResidualGolfEnv L65, L127-130", effect="PD lag shifts effective wrist w at contact; more cocked (w>0) = hands ahead = less loft; re-measure dynamic loft after the lead fix", suggested="aim w in the w_contact band 0.173-0.564*elbow_rad +-0.1 (earlier repo analysis, not re-derived); do not force forward lean (driver needs +AoA)", basis="repo analysis + published qualitative (unverified)"),
          dict(param="face angle", where="no explicit param; head box yaw from club path/wrist/forearm rotation", effect="start line ~76% face / 24% path; lateral via k_side*dy only", suggested="log face angle and path at contact to use the dispersion section", basis="published (PING 2018)"),
          dict(param="K (tangential divisor) and e", where="analytic ball model / data.targets_130mph_350yd.impact_k; env/ball_flight_analytic.impact default mu=0.22, e=0.83 (repo docs use e=0.845, K 4.0 or 5.6)", effect="K 5.6 lowers spin ~30% (2121->1515 rpm at 130 mph, AoA+3 DL10.5) and adds 3-6 yd carry; e caps smash (<=1.50)", suggested="K=5.6 for TrackMan-like spin (repo impact doc); e=0.845", basis="model; calibration per repo docs")],
        launch_options_table=rows, carry_vs_launch_note="Carry change vs baseline A (AoA +5, DL 14.5, launch 12.9), model K=4.0 / K=5.6. 130 mph: launch 10-11 (B,C) +6.7/+7.5 | +1.5/-2.6; launch 9.2 (D) +2.8 | -4.4; launch 8.2 (F, G) +0.1/-0.1 | -8.3/-15.5; launch 7.5 (E) -5.7 | -11.4. 120 mph: B +2.6, C -0.3, D -3.3, F -7.2, E -11.5, G -11.9 (K=4.0); K=5.6 is 5-14 yd worse. 100 mph: every lower-launch row loses 6-32 yd (K=4.0). So 7.8-8.2 deg launch is carry-neutral only at ~130 mph with K=4.0 and AoA +2..+4 / DL 9-9.5; at K=5.6 or lower speed it costs 8-40 yd. The model carry optimum is ~10-11 deg at 130 mph. Tutelman: optimal launch falls with ball speed (190 mph ball -> ~7 deg at AoA 0).",
        dispersion=dict(
          sources_numbers=[
            dict(id="broadie_golfmetrics", metric="sigma of direction (angle between start-end line and start-target line) on long tee shots: Pro 4.0 deg (d0.75 297 yd), Am1 (scoring avg 70-83) 5.4, Am2 6.4, Am3 8.1; 4 deg = 14 yd @200, 21 yd @300; fit sigma = -0.0315*d0.75 + 13.223", url="https://business.columbia.edu/sites/default/files-efs/pubfiles/2851/broadie_wscg_v_200802.pdf", verification="fetched (pdf)", unverified=False, caveat="all long tee shots (not only driver), ShotLink-era data, includes curve+roll, c. 2008"),
            dict(id="trackman_face_to_path", metric="PGA Tour driver 275 yd carry: F2P -2 deg ~ 19 yd left curve, +5 deg ~ 44 yd right; 1 deg F2P ~ 12 yd at 300 yd; elite player should keep F2P within ~1 deg (1.5 deg forces aiming off the fairway)", url="https://www.trackman.com/blog/face-to-path", verification="search snippet", unverified=True, caveat="vendor blog; curvature in yards at carry"),
            dict(id="wood_ping_2018", metric="Driver horizontal launch toward face angle 76% +-8% (95% CI, n=89 filtered shots, F2P >=1.5 deg); 7-iron 69%+-3; wedge 61%+-7; vertical launch toward dynamic loft: driver 83%+-8%; robot 63%+-4 horizontal (7-iron); 731 driver shots/157 golfers (via Pebble summary: PING, Vicon + Foresight)", url="https://www.mdpi.com/2504-3900/2/6/249", verification="search snippet (MDPI proceedings text)", unverified=True, caveat="peer-reviewed proceedings; I read excerpts not the full PDF"),
            dict(id="bliss_langdown_2026", metric="1 deg of target-line/calibration error ~ 4 yd side dispersion over 250 yd carry; driver club path TrackMan -3.75 vs Mevo+ -2.25 deg (one golfer); driver path/plane absolute agreement poor", url="https://oro.open.ac.uk/107777/", verification="abstract fetched; the 4 yd and -3.75/-2.25 figures via Pebble summary", unverified=True, caveat="single-golfer indoor"),
            dict(id="foresight_gcquad_single_digit_test", metric="3, 5 and 7 handicappers, GCQuad, stock drives: ~70 yd side-to-side (about +-35 yd) after discarding outliers", url="https://www.australiangolfdigest.com.au/what-this-fascinating-consistency-test-revealed-about-single-digit-handicaps/", verification="search snippet", unverified=True, caveat="3 golfers; width not sigma"),
            dict(id="practical_golf_decade", metric="one ~scratch golfer, 20 driver shots on a mat: 68.6 yd left-right; author cites Scott Fawcett (DECADE) 65-70 yd typical for scratch or better", url="https://practical-golf.com/golf-ball-control", verification="search snippet", unverified=True, caveat="n=20, blog, secondhand DECADE figure"),
            dict(id="t5golf_blog", metric="tour 18-22 yd, scratch 25-30 yd 'lateral spread' (95% ellipse claimed)", url="https://t5golf.com/what-is-a-good-driver-dispersion/", verification="search snippet", unverified=True, caveat="LOW CONFIDENCE: no data source, conflicts with the 65-70 yd width above; do not use"),
            dict(id="arccos_report", metric="no lateral yards; men 0-4.9 hcp: 249.9-250 yd avg, 49.3% fairways hit, 12.0% wayward (4.4% penalty + 7.6% recovery)", url="https://golfweek.usatoday.com/story/sports/golf/equipment/2025/05/10/arccos-driving-distance-report-no-change-in-yards-for-club-golfers/83534228007/", verification="search snippet", unverified=True, caveat="fairway rates only"),
            dict(id="trackman_tour_averages", metric="TrackMan publishes no driver lateral dispersion, face-angle sigma or path sigma for tour or scratch players", url="https://www.trackman.com/blog/introducing-updated-tour-averages", verification="search snippet", unverified=True, caveat="absence of evidence in snippets only"),
            dict(id="kjss_2017", metric="TrackMan 15 tour pros vs 15 semi-pros: tour pros had lower CV in club path, dynamic loft, launch angle (no degree values)", url="https://doi.org/10.35159/kjss.2017.12.26.6.1347", verification="abstract (search)", unverified=True, caveat="no sigma in degrees")],
          model_assumptions=dict(start_line="0.76*face + 0.24*path (PING)", curve_yd_per_deg_face_to_path_per_yd_carry=round(C_CURVE, 4), face_path_independent=True, note="Real face and path are positively correlated, which shrinks F2P variance; calibrating to Broadie's total direction sigma with independent equal sigmas therefore UNDERSTATES real face/path sigmas. No published face-angle or path sigma for 100-120 mph players was found."),
          stock_scatter_push=disp),
        bc_prior_options=d["bc_prior_options"], bc_note="Reused unchanged from data/references/targets_130mph_350yd_and_loft.json (CMU, MultiSense, BONES-SEED = counsel_required; AMASS/GolfDB/HumanML3D EXCLUDED; LAFAN1 noncommercial). Nothing new found this round. Repo flag stands: data/provenance.py tags cmu_mocap commercial_ok=True.",
        unverified_items=["All model rows (not a source); dynamic-loft offset from loft_deg; AoA vs ball_x geometry (R assumed); spin_k suggestion (arithmetic).", "Face/path sigma split (assumed equal, independent), calibrated from Broadie direction sigma; no published split.", "TrackMan F2P yard figures, PING 76/83%, Bliss-Langdown 4 yd/deg, GCQuad 70 yd, DECADE 65-70 yd (snippets/secondhand).", "Broadie sigma applies to long tee shots incl. roll c. 2008, not 100-120 mph driver carry specifically.", "Mapping of Mason (+3) to Broadie Am1 is a judgement; his 120+ mph is self-reported."])
    json.dump(out, open(ROOT / "data/references/loft_env_params_dispersion.json", "w"), indent=1)
    OUT_ROWS.unlink()
    for x in disp: print(x["group"][:12], x["club_mph"], x["carry_yd_model"], x["face_sigma_deg_calibrated"], x["lateral_sigma_yd_1sigma"], x["lateral_width_95pct_yd"])

if __name__ == "__main__":
    if "--assemble" in sys.argv:
        main()          # needs the sweep rows file
    else:
        sweep()         # ~3 min; then run again with --assemble
