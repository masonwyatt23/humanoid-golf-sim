"""Builds data/references/golfphys_coefficients.json from the validation run (data/references/golfphys_validation.json)."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
v = json.load(open(ROOT / "data/references/golfphys_validation.json"))
P = v["_params"]; T = v["_turf"]
CAL, ASM, PUB = "calibrated", "assumption", "published"
src = {
    "m_head": (ASM, "typical 195-205 g driver head", "n/a"),
    "e0": (CAL, "fit to 30 TrackMan 2010 carry-optimizer rows (smash/launch/spin); effective value absorbs head mass/COR (exceeds 0.83 legal COR because m_head is nominal)", "fetched chart (wishongolf PDF)"),
    "e_slope": (ASM, "fitted slope was ~0 (-1e-4/(m/s)); fixed at 0", "fetched chart"),
    "e_ref_speed": (ASM, "reference normal speed", "n/a"),
    "s_t": (CAL, "tangential-impulse efficiency vs full rolling contact (uniform sphere M*vt/3.5); fit to the same rows", "fetched chart; mechanism Cochran & Stobbs / Tutelman (snippet)"),
    "s_t_slope": (ASM, "fitted slope ~ -0.002/deg, not significant on held-out rows; fixed at 0", "fetched chart"),
    "I_head_h": (PUB, "Tutelman gear-effect 3: Ih 4000-5900 g cm^2", "fetched tutelman.com/golf/ballflight/gearEffect3.php"),
    "I_head_v": (PUB, "Iv = 1/2 - 2/3 of Ih (Tutelman GE3)", "fetched tutelman.com/golf/ballflight/gearEffect3.php"),
    "gear_h_rpm_per_mph_in": (PUB, "16.4 rpm per mph ball speed per inch of horizontal offset", "fetched Tutelman GE3"),
    "gear_v_rpm_per_mph_in": (PUB, "25 rpm per mph per inch vertical offset", "fetched Tutelman GE3"),
    "gear_mode": (ASM, "'tutelman' empirical add-on; not validated against launch-monitor off-centre data (none collected)", "n/a"),
    "bulge_radius": (ASM, "10 in standard driver bulge (common spec, not verified in this session)", "unverified"),
    "roll_radius": (ASM, "12 in standard roll (common spec, not verified)", "unverified"),
    "aero_model": (ASM, "Cl form 0.54 S^0.4 (curve-fit to Bearman & Harvey 1976 Fig. 9 as quoted; snippet) with scale calibration", "snippet (Bearman 1976 scribd/COMSOL blog)"),
    "cd_scale": (CAL, "fit: TM carry-opt carry + 3 landing-angle anchors; scales no-spin and spin Cd", "fetched chart + snippet anchors"),
    "cl_scale": (CAL, "same fit", "fetched chart + snippet anchors"),
    "cd_spin_slope": (CAL, "dCd/dS (induced-drag term) fit jointly; a 2-parameter fit could not match carry and 38 deg descent together", "fetched chart + snippet anchors"),
    "cd_plateau": (ASM, "no-spin Cd after drag crisis (B&H qualitative)", "snippet"),
    "cd_re_slope": (ASM, "slow Cd rise with Re after crisis (B&H qualitative)", "snippet"),
    "re_crit": (ASM, "drag-crisis Re 4-6e4 for dimpled ball", "snippet (IJIMT 2013 citing B&H)"),
    "cd_sub": (ASM, "subcritical Cd", "unverified"),
    "cl_cap": (ASM, "Cl saturation cap (never binds at driver S<0.15 after scaling)", "unverified"),
    "spin_decay": (PUB, "3.3-4 %/s spin loss (Tutelman spin-decay page); 0.04 used. Constant-rate; Smits&Smith have velocity dependence", "snippet (Tutelman)"),
}
params = {}
for k, val in P.items():
    if k in ("turf",):
        continue
    st, note, s = src.get(k, (ASM, "", ""))
    params[k] = dict(value=val, status=st, note=note, source=s)
out = dict(
    label="golfphys coefficients. status: calibrated = fitted to cited published rows (see golfphys_validation.json for fit vs held-out); assumption = my choice; published = value quoted from a source (fetched/snippet in 'source').",
    written="2026-10-17", no_personal_clip_data=True,
    params=params,
    turf={k: dict(v, status=("calibrated (absolute: carry-opt+Foresight totals)" if k == "normal" else "calibrated ONLY on one relative statistic: Broadie/ShotLink soft -5.31 / firm +4.49 yd of total vs medium (fetched USGA PDF); changes a_roll only"),
                  source="data/references/roll_aoa_validation.json (TrackMan/Foresight rows), USGA 'Golf Course Effects on Hitting Distance' (fetched)") for k, v in T.items()},
)
json.dump(out, open(ROOT / "data/references/golfphys_coefficients.json", "w"), indent=1)
print("ok", len(params))
