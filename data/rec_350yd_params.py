"""Build data/references/recommended_350yd_params.json. PUBLIC/SCRIPTED data only; no Instagram-derived or Mason-clip data, no imit_private files.
Reads (copied numbers, not imported): results/power_loft_scan1_s25.json (scripted zero-residual power tier, gain 1.20, n=40; measured in env).
Model rows: data.targets_130mph_350yd.run (repo analytic model, read-only). Run: python -m data.rec_350yd_params"""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data.targets_130mph_350yd import run
from data.loft_env_params_dispersion import env_spin, lateral_sigma_yd, calibrate_s
YD_PER_M = 1.0936133
# MEASURED in env (Trainer scan, scripted zero residual, impact gain 1.20, n=40, club 132.4 mph). distance/carry in METRES (env code comments; reward 'metres').
SCAN = {-31: (12.58, 298.84, 2.05), -29: (11.15, 299.09, 2.05), -27: (9.72, 292.70, 1.87), -25: (8.30, 274.41, 1.52), -23: (10.02, 235.24, 2.52)}  # loft: (launch deg, carry m, lat std m)
SCAN_LAUNCH_STD_AT_M23 = 13.69

def main():
    L = np.array([-31, -29, -27, -25]); la = np.array([SCAN[k][0] for k in L])
    slope, icpt = np.polyfit(L, la, 1)
    scan = [dict(loft_deg=k, launch_deg=v[0], carry_m=v[1], carry_yd=round(v[1] * YD_PER_M, 1), lateral_std_m=v[2], basis="measured (env, scripted, gain 1.20, n=40)") for k, v in SCAN.items()]
    scan[-1]["note"] = "cliff: launch std 13.7 deg = mixed mishits; carry 235 m; do not use"
    target = {l: round(float(slope * l + icpt), 2) for l in (-24, -25, -26, -27, -28, -29)}
    rec = dict(loft_deg=-28, impact_gain=1.20, elev_target_deg=10.0, elev_weight=1.0, spin_k=130, ball_x=0.396, ball_x_noise=0.003, ball_dz=-0.008, tee_height=0.04,
               fallback_measured="loft_deg=-27 (launch 9.72 deg, carry 292.7 m measured)", predicted_env_launch_deg_interpolated=target[-28], predicted_env_carry_m_interpolated=round((299.09 + 292.70) / 2, 1))
    model = []
    for mph in (130, 132):
        for K in (4.0, 5.6):
            for lab, a, dl in (("rec AoA +4 DL 11.5", 4, 11.5), ("alt AoA +4 DL 11.0", 4, 11.0)):
                r = run(mph, a, dl, K=K); r = {k: (float(v) if isinstance(v, (np.floating,)) else v) for k, v in r.items()}
                r["config"] = lab; r["env_formula_spin_rpm_k130"] = round(env_spin(r["ball_mph"], r["launch_deg"], 130.0)); model.append(r)
    # shaping: scale to carry reward (carry_cap 120 => ~24/shot at gate=1)
    s_pro = calibrate_s(297.0, 4.0); s_am = calibrate_s(297.0, 5.4)
    terms = [
      dict(term="start_line", def_="eps_s = ball start azimuth - target azimuth (deg), from first 5 ms of ball velocity", form="-w*min((eps_s/sigma)^2, 9)", sigma_deg=1.0, w=1.5, anchor="PING 2018: start = 0.76 face + 0.24 path (snippet-verified, unverified full text); model start-line sigma 1.03 deg for pro (face=path=1.29) and 1.39 for Broadie Am1; start sigma 1.0 = pro-level goal; +3 stock ~1.4", basis="derived"),
      dict(term="face_angle_at_impact", def_="f = club-face yaw (face normal projected on ground) minus target line at first contact (deg)", form="-w*min((f/sigma)^2, 9)", sigma_deg=1.5, w=1.0, anchor="stock +3 face sigma ~1.5 deg (between model rows 1.29 pro / 1.75 Am1; no published face sigma exists); curriculum: start sigma 3.0 anneal to 1.5", basis="derived, UNVERIFIED sigma"),
      dict(term="club_path", def_="p = club-head velocity azimuth at contact minus target line (deg)", form="-w*min((p/sigma)^2, 9)", sigma_deg=1.5, w=0.5, anchor="same as face; path matters 24% for start line but sets curve via face-to-path", basis="derived, UNVERIFIED sigma"),
      dict(term="face_to_path", def_="d = f - p (deg)", form="-w*min((d/sigma)^2, 9)", sigma_deg=2.0, w=0.5, anchor="TrackMan: 2 deg F2P ~19 yd curve, 5 deg ~44 yd at 275 yd carry (snippet, unverified); elite keep within ~1 deg", basis="published-ish (snippet) + derived"),
      dict(term="lateral_miss_yards", def_="existing env term: lat_weight*_lat_pen with lat_angular=True (percent of carry, cap 30) so short shots cannot hide a miss; report in yards = metres*1.0936", form="-lat_weight * min(|lat|/max(carry,30),0.3)*100", lat_weight=1.0, lat_angular=True, anchor="Broadie pro direction sigma 4.0 deg = 7% of carry = ~21 yd at 300 yd; 1 deg ~1.75% ; with carry reward ~24/shot, 1 pro-sigma miss costs ~7", basis="derived; uses existing env knob (no code change)"),
      dict(term="launch_elev", def_="existing elev_target_deg/elev_weight (elev_weight is 0.0 in the loft-27 gate config, so the 12.5 deg default target was NOT active there)", form="-elev_weight*|launch - target|/10", elev_target_deg=10.0, elev_weight=1.0, anchor="model carry optimum 10-11 deg at 130 mph; env scan carry peak at 11.2-12.6 deg", basis="measured env scan + model")]
    out = dict(schema_version=1, name="recommended_350yd_params", written="2026-10-17 America/New_York (Saturday)",
        honesty=["No Instagram-derived or Mason-clip data, no video, no imit_private files read for this table. Env numbers come only from the scripted zero-residual scan results/power_loft_scan1_s25.json.",
                 "Env distance/carry are in METRES (env reward/penalty code and TrackMan 251 m comparison); yards = m*1.0936. Env has no roll: distance == carry.",
                 "Model rows are repo analytic model (NOT a source). Mason's 120+ mph is self-reported, unverified. Nothing here was rolled out in MuJoCo for the recommended loft_deg -28 (interpolated)."],
        measured_loft_scan=scan, scan_fit=dict(launch_deg_per_loft_deg=round(float(slope), 3), intercept=round(float(icpt), 2), fit_over=[-31, -29, -27, -25], interpolated_launch_by_loft=target, basis="linear fit of measured points (4 pts); -23 excluded (cliff)"),
        verdict=dict(target_launch_deg="9.7-10.4 (not 7.8)", reasons=["7.8 deg would be loft_deg ~-24.3 (fit), beyond the measured -25 (8.30 deg, carry 274 m = -25 m / -8% vs peak) and next to the -23 failure (launch std 13.7 deg, carry 235 m).", "Model: 7.5-8.2 deg costs 0..8 yd at best (K=4.0) and 8-16 yd at K=5.6 at 130 mph; model optimum 10-11 deg.", "-27 (9.72 deg) measured costs 6.4 m (2%) vs the -29 peak; -28 interpolates ~10.4 deg for ~3 m.", "Env spin formula 130*v*sin(launch+2) gives ~2340 rpm at 9.7 deg (a gate JSON backspin of ~2359 was reported by the Trainer, consistent), inside the 1800-3000 gate."]),
        recommended=rec, model_prediction_130_132=model,
        three_fifty_note="350 yd TOTAL = 320 m. Measured env carry at 132.4 mph is 293-299 m = 320-327 yd carry (no roll). Model total (carry + roll) at 130-132 mph AoA+4 DL 11-12 is 349-361 yd (K=4.0: 349-356, K=5.6: 355-361). 350 yd CARRY (320 m) is ~21-27 m above the best measured env carry and not reached by the model (max ~333 yd): stretch/unverified.",
        shaping_terms=terms, shaping_scale_note="All per-shot terminal terms, summed with the existing carry reward (~24 at carry_cap 120). Weights and sigmas are derived starting points to be tuned, not published values. Cap each squared term at 9 (3 sigma).",
        dispersion_anchors=dict(face_path_sigma_deg_pro_model=round(s_pro, 2), face_path_sigma_deg_am1_model=round(s_am, 2), stock_plus3_face_path_sigma_deg=1.5, broadie_pro_direction_sigma_deg=4.0, broadie_am1_direction_sigma_deg=5.4,
              lateral_1sigma_yd_at_320yd_carry={"pro": round(lateral_sigma_yd(320, s_pro, s_pro), 1), "+3 (face=path 1.5)": round(lateral_sigma_yd(320, 1.5, 1.5), 1)},
              env_scripted_lateral_std_m="1.5-2.5 m (0.3-0.5 deg at 293 m) in the scan: the scripted swing is ~10x tighter than any human reference, so the goal for a learned policy is to stay near it, not to match human scatter",
              source="docs/LOFT_ENV_PARAMS_AND_DISPERSION.md (Broadie fetched; PING, TrackMan snippets unverified; face/path sigma not published)"),
        logging_needed="Env does not log face yaw, club path, or dynamic loft at contact; add them (read face normal and club-head velocity at first contact) before using face/path terms. env/ is read-only for the Data Agent.",
        bc_prior_options=[dict(source="CMU subject 64 (10 swings)", license_tag="counsel_required", note="reference tracking/RSI prior; provenance.py now tags CMU needs_counsel / commercial_ok=False (retagged 2026-10); open item for Mason/counsel: whether to keep or untrack the tracked cmu_64_*.npz"),
                          dict(source="MultiSenseGolf (28 swings)", license_tag="counsel_required", note="no wrist data; low weight"),
                          dict(source="BONES-SEED", license_tag="counsel_required", note="not in repo; general humanoid prior; never commit"),
                          dict(source="100STYLE", license_tag="cc_by", note="locomotion only"),
                          dict(source="AMASS / GolfDB / HumanML3D / Motion-X", license_tag="EXCLUDED_commercial", note="do not use"),
                          dict(source="LAFAN1", license_tag="noncommercial", note="do not use"),
                          dict(source="scripted zero-residual swing + residual policy (own code)", license_tag="none", note="recommended base: measured scatter 2 m; learn residual with shaping terms above")],
        recommended_bc="Use scripted swing as the behaviour prior (own code, no license issue): DAgger/BC-regularise the residual toward zero (small residual_scale) and add the shaping terms; use CMU/MultiSense only as tagged counsel_required tracking references.",
        unverified_items=["loft_deg -28 outcome (interpolated)", "all model rows", "face/path sigmas 1.5/1.29 (not published; calibrated or assumed)", "shaping weights and scales (derived)", "TrackMan F2P yards and PING 76% (snippets)", "step from scripted to learned-policy scatter", "env units = metres (code reading; confirm with Trainer)"],
        sources=["https://business.columbia.edu/sites/default/files-efs/pubfiles/2851/broadie_wscg_v_200802.pdf", "https://www.mdpi.com/2504-3900/2/6/249", "https://www.trackman.com/blog/face-to-path"])
    json.dump(out, open(ROOT / "data/references/recommended_350yd_params.json", "w"), indent=1, default=float)
if __name__ == "__main__": main()
