"""MODEL-ONLY, UNCALIBRATED roll / total / AoA add-on (standalone; imports nothing from env/, eval/, train/).
Purpose: let the Trainer report an *estimated* total (carry + roll) for the env, which has no roll, and see how AoA moves launch/spin.
Nothing here is a published model. Structure follows published qualitative facts; the coefficients are chosen by the Data Agent and checked
against published carry/total pairs (see data/references/roll_aoa_addon.json 'validation'). No Instagram-derived or Mason-clip data.
Units: carry/roll/total in YARDS unless a function says metres; angles degrees; spin rpm.
Run: python -m data.roll_aoa_addon  (rebuilds the JSON)"""
import json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/references/roll_aoa_addon.json"
MPH, YD_PER_M = 0.44704, 1.0936133
LABEL = "MODEL-ONLY / UNCALIBRATED: not a published model; do not quote as a measurement"

# Qualitative anchors (sources in docs/ROLL_AOA_ADDON_PROPOSAL.md): normal fairway roll ~8-12% of driver carry (ShotTally, weak/web);
# firm can ~double it, soft nearly eliminate (same); each degree flatter landing adds ~1.5-2 yd roll (Sackett PDF, snippet; ~40 deg reference);
# TrackMan: flatter landing / lower spin -> more roll (help center, snippet).
FIRMNESS = {"soft": 0.35, "normal": 1.0, "firm": 1.6, "very_firm": 2.0}
BASE_ROLL_FRAC = 0.09          # of carry, normal firmness, descent 38 deg, spin 2686 (PGA Tour avg row) -- ASSUMED, in the 8-12% web range
DESC_REF, SPIN_REF = 38.0, 2686.0
DESC_COEF = 0.045              # fractional change in roll per degree flatter than DESC_REF (~1.6 yd/deg at 36 yd roll; Sackett says 1.5-2 yd/deg; ASSUMED)
SPIN_COEF = 0.00012            # fractional change in roll per rpm below SPIN_REF (ASSUMED)

def firmness_factor(firmness="normal"):
    """str in FIRMNESS, or a float multiplier (0.35 soft ... 1.0 normal ... 2.0 very firm)."""
    if isinstance(firmness, str):
        return FIRMNESS[firmness]
    f = float(firmness)
    if not 0.0 <= f <= 3.0:
        raise ValueError("firmness multiplier must be in [0, 3]")
    return f

def estimate_descent_deg(launch_deg, spin_rpm):
    """Crude HEURISTIC landing angle when the env does not give one (anchored on one point: PGA Tour avg 10.9 deg, 2686 rpm -> 38 deg, TrackMan).
    Slopes are assumed: higher launch/spin -> steeper. Prefer a simulated descent angle if you have it. Clipped 25..60."""
    return float(np.clip(38.0 + 1.3 * (launch_deg - 10.9) + 0.004 * (spin_rpm - 2686.0), 25.0, 60.0))

def estimate_roll_yd(carry_yd, launch_deg=None, spin_rpm=None, descent_deg=None, firmness="normal"):
    """-> dict(roll_yd, total_yd, roll_frac, descent_deg_used, label). Give descent_deg if known, else launch+spin.
    roll_frac = BASE * firmness * (1 + DESC_COEF*(38-descent)) * (1 + SPIN_COEF*(2686-spin)), clipped to [0, 0.35]."""
    if carry_yd <= 0:
        raise ValueError("carry_yd must be > 0")
    spin = SPIN_REF if spin_rpm is None else float(spin_rpm)
    if descent_deg is None:
        if launch_deg is None:
            raise ValueError("give descent_deg or launch_deg")
        descent_deg = estimate_descent_deg(launch_deg, spin)
    ff = firmness_factor(firmness)
    frac = BASE_ROLL_FRAC * ff * max(1 + DESC_COEF * (DESC_REF - descent_deg), 0.0) * max(1 + SPIN_COEF * (SPIN_REF - spin), 0.0)
    frac = float(np.clip(frac, 0.0, 0.35))
    roll = carry_yd * frac
    return dict(roll_yd=round(roll, 1), total_yd=round(carry_yd + roll, 1), roll_frac=round(frac, 4), total_over_carry=round(1 + frac, 4),
                descent_deg_used=round(float(descent_deg), 1), firmness=firmness, label=LABEL)

def estimate_total_from_m(carry_m, **kw):
    """Env helper: env carry is in metres. Returns yard values plus metres."""
    r = estimate_roll_yd(carry_m * YD_PER_M, **kw)
    r["roll_m"] = round(r["roll_yd"] / YD_PER_M, 1); r["total_m"] = round(r["total_yd"] / YD_PER_M, 1)
    return r

def tutelman_launch(aoa_deg, spin_loft_deg):
    """Tutelman 3-D launch page (fetched in earlier repo work): launch = AoA + SL*(0.96 - 0.0071*SL)."""
    return aoa_deg + spin_loft_deg * (0.96 - 0.0071 * spin_loft_deg)

def env_spin_rpm(ball_mph, launch_deg, spin_k=130.0):
    """Copy of the env impact_model spin formula as documented in data/loft_env_params_dispersion.py: spin_k*|v|*sin(max(launch+2,0)), v in m/s."""
    return float(np.clip(spin_k * ball_mph * MPH * np.sin(np.radians(max(launch_deg + 2.0, 0.0))), 0, 6000))

def aoa_sensitivity(aoa_list, dynamic_loft_deg=None, spin_loft_deg=None, ball_mph=190.0, spin_k=130.0):
    """Sweep AoA. Either hold dynamic loft fixed (spin loft = DL - AoA: more AoA -> less spin loft, launch rises slowly) or hold spin loft fixed
    (launch moves ~1:1 with AoA). Returns rows with launch (Tutelman) and env-formula spin. MODEL-ONLY."""
    if (dynamic_loft_deg is None) == (spin_loft_deg is None):
        raise ValueError("give exactly one of dynamic_loft_deg / spin_loft_deg")
    rows = []
    for a in aoa_list:
        sl = (dynamic_loft_deg - a) if dynamic_loft_deg is not None else spin_loft_deg
        L = tutelman_launch(a, sl)
        rows.append(dict(aoa_deg=a, spin_loft_deg=round(sl, 2), launch_deg=round(L, 2), env_formula_spin_rpm=round(env_spin_rpm(ball_mph, L, spin_k))))
    return rows

def sensitivity_per_deg(aoa=4.0, dynamic_loft_deg=11.5, ball_mph=190.0, spin_k=130.0):
    a = aoa_sensitivity([aoa - 0.5, aoa + 0.5], dynamic_loft_deg=dynamic_loft_deg, ball_mph=ball_mph, spin_k=spin_k)
    b = aoa_sensitivity([aoa - 0.5, aoa + 0.5], spin_loft_deg=dynamic_loft_deg - aoa, ball_mph=ball_mph, spin_k=spin_k)
    f = lambda r, k: round(r[1][k] - r[0][k], 3)
    return dict(fixed_dynamic_loft=dict(launch_deg_per_aoa_deg=f(a, "launch_deg"), env_spin_rpm_per_aoa_deg=f(a, "env_formula_spin_rpm")),
                fixed_spin_loft=dict(launch_deg_per_aoa_deg=f(b, "launch_deg"), env_spin_rpm_per_aoa_deg=f(b, "env_formula_spin_rpm")))

# Published carry/total pairs used ONLY to check the model (TrackMan Driver Optimizer 2010 chart, fetched; Foresight table, search snippet; R&A, fetched)
PUBLISHED_PAIRS = [
    dict(src="TrackMan carry-optimizer", club_mph=120, aoa=0, launch=9.3, spin=2890, carry=296, total=321),
    dict(src="TrackMan carry-optimizer", club_mph=120, aoa=5, launch=12.6, spin=2343, carry=310, total=350),
    dict(src="TrackMan carry-optimizer", club_mph=110, aoa=5, launch=13.7, spin=2435, carry=279, total=305),
    dict(src="TrackMan total-optimizer", club_mph=120, aoa=0, launch=7.7, spin=2382, carry=290, total=340),
    dict(src="TrackMan total-optimizer", club_mph=120, aoa=5, launch=10.3, spin=1636, carry=300, total=358),
    dict(src="TrackMan total-optimizer", club_mph=110, aoa=5, launch=11.1, spin=1716, carry=268, total=326),
    dict(src="R&A PGA-avg launch sim (Volvik, 'long' orientation)", club_mph=113, aoa=-1.3, launch=10.9, spin=2686, carry=272, total=291),
    dict(src="Foresight optimized table (search snippet; launch/spin = range MIDPOINTS 12 deg, 2100 rpm, not row data) 131 mph low-carry end", club_mph=131, aoa=None, launch=12.0, spin=2100, carry=342, total=378),
    dict(src="Foresight optimized table (search snippet; launch/spin = range midpoints) 131 mph high-carry end", club_mph=131, aoa=None, launch=12.0, spin=2100, carry=372, total=401),
]

def validation():
    rows = []
    for p in PUBLISHED_PAIRS:
        pub = p["total"] / p["carry"]
        r = {k: estimate_roll_yd(p["carry"], launch_deg=p["launch"], spin_rpm=p["spin"], firmness=f)["total_over_carry"] for k, f in (("normal", "normal"), ("firm", "firm"))}
        rows.append(dict(p, published_total_over_carry=round(pub, 3), model_normal=r["normal"], model_firm=r["firm"]))
    return rows

def build():
    cases = []
    for carry_m in (293, 296, 299):
        for fm in ("soft", "normal", "firm", "very_firm"):
            c = estimate_total_from_m(carry_m, launch_deg=10.4, spin_rpm=2400, firmness=fm)
            cases.append(dict(env_carry_m=carry_m, firmness=fm, **{k: c[k] for k in ("roll_yd", "total_yd", "total_m", "roll_frac", "descent_deg_used")}))
    out = dict(label=LABEL, written="2026-10-17 America/New_York", honesty=["Model-only and uncalibrated: the env has no roll and no published roll model was fit.",
        "Coefficients (BASE_ROLL_FRAC, DESC_COEF, SPIN_COEF, FIRMNESS table, descent heuristic) are Data Agent assumptions anchored on web ranges.",
        "No Instagram-derived or Mason-clip data used."],
        constants=dict(BASE_ROLL_FRAC=BASE_ROLL_FRAC, DESC_REF=DESC_REF, SPIN_REF=SPIN_REF, DESC_COEF=DESC_COEF, SPIN_COEF=SPIN_COEF, FIRMNESS=FIRMNESS),
        validation=validation(), sample_350yd_cases=cases,
        aoa_sensitivity_fixed_dynamic_loft_11_5=aoa_sensitivity([0, 2, 4, 5, 6], dynamic_loft_deg=11.5),
        aoa_sensitivity_fixed_spin_loft_7_5=aoa_sensitivity([0, 2, 4, 5, 6], spin_loft_deg=7.5),
        sensitivity_per_deg_at_aoa4_dl11_5=sensitivity_per_deg())
    OUT.write_text(json.dumps(out, indent=1)); return out

if __name__ == "__main__":
    o = build(); print(json.dumps(o["sensitivity_per_deg_at_aoa4_dl11_5"], indent=1))
    for v in o["validation"]: print(v["src"][:40], v["club_mph"], v["published_total_over_carry"], v["model_normal"], v["model_firm"])
    for c in o["sample_350yd_cases"]: print(c)
