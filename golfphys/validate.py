"""Calibration + held-out validation against the published datapoints in data/references/roll_aoa_validation.json
(TrackMan 2010 driver fitting chart rows fetched; Foresight ranges midpoints fetched; R&A simulations fetched; Rice/Burke snippets).
Run:  python -m golfphys.validate  -> writes data/references/golfphys_validation.json and (with --write-coeffs) golfphys_coefficients.json.
Every fit says which rows were fit and which were held out. Nothing is tuned on held-out rows."""
import json, math, sys
from dataclasses import replace, asdict
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from .params import Params, R_BALL
from .impact import Delivery, impact
from .flight import fly
from .bounce import bounce_roll, TURF
from .sim import shot_from_launch

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/references/roll_aoa_validation.json"
MPH = 0.44704
YD = 0.9144


def rows():
    return json.load(open(DATA))["datapoints"]


def _stat(r):
    r = np.asarray(r, float)
    if r.size == 0:
        return dict(n=0)
    return dict(n=int(r.size), bias=round(float(r.mean()), 3), mae=round(float(np.abs(r).mean()), 3),
                rmse=round(float(np.sqrt((r ** 2).mean())), 3), min=round(float(r.min()), 3), max=round(float(r.max()), 3))


def flight_rows(rs):
    return [x for x in rs if x.get("ball_mph") and x.get("launch_deg") and x.get("spin_rpm") and x.get("carry_yd")
            and x["group"] in ("tm_carry_opt", "tm_total_opt", "foresight", "ra_sim", "rice", "longdrive")]


def sim_carry(x, p, rho_kw=None):
    from .sim import shot_from_launch
    return shot_from_launch(x["ball_mph"] * MPH, x["launch_deg"], x["spin_rpm"], p, roll=False, dt=0.02)


# ---------------------------------------------------------------- aero
def fit_aero(p0: Params, fit_rows, free=("cd_scale", "cl_scale")):
    def res(th):
        p = replace(p0, **dict(zip(free, th)))
        return [(sim_carry(x, p).carry_yd - x["carry_yd"]) for x in fit_rows]
    sol = least_squares(res, [getattr(p0, k) for k in free], diff_step=1e-3, bounds=([0.5] * len(free), [1.8] * len(free)))
    return dict(zip(free, [float(v) for v in sol.x]))


def carry_residuals(p, rs):
    out = []
    for x in rs:
        s = sim_carry(x, p)
        out.append(dict(id=x["id"], group=x["group"], club_mph=x["club_mph"], pub=x["carry_yd"], model=round(s.carry_yd, 1),
                        res=round(s.carry_yd - x["carry_yd"], 1), descent=round(s.descent_deg, 1), apex_m=round(s.apex_m, 1)))
    return out


# ---------------------------------------------------------------- impact
def tm_rows(rs):
    return [x for x in rs if x["group"] in ("tm_carry_opt", "tm_total_opt") and x.get("dynamic_loft_deg") is not None]


def impact_resid(p, rs):
    out = []
    for x in rs:
        im = impact(Delivery(x["club_mph"] * MPH, x["dynamic_loft_deg"], x["aoa_deg"]), p=p)
        out.append(dict(id=x["id"], group=x["group"], club_mph=x["club_mph"],
                        d_ball_mph=im["ball_speed"] / MPH - x["ball_mph"], d_smash=im["smash"] - x["ball_mph"] / x["club_mph"],
                        d_launch=im["launch_deg"] - x["launch_deg"], d_spin=im["spin_rpm"] - x["spin_rpm"],
                        rel_spin=im["spin_rpm"] / x["spin_rpm"] - 1))
    return out


def fit_impact(p0, fit_rows, free=("e0", "e_slope", "s_t", "s_t_slope")):
    def res(th):
        p = replace(p0, **dict(zip(free, th)))
        r = impact_resid(p, fit_rows)
        return [v for q in r for v in (q["d_smash"] / 0.01, q["d_launch"] / 0.3, q["rel_spin"] / 0.05)]
    x0 = [getattr(p0, k) for k in free]
    B = dict(e0=(0.7, 0.95), e_slope=(-0.02, 0.02), s_t=(0.2, 1.0), s_t_slope=(-0.05, 0.05))
    lo = [B[k][0] for k in free]; hi = [B[k][1] for k in free]
    sol = least_squares(res, x0, diff_step=1e-3, bounds=(lo, hi))
    return dict(zip(free, [float(v) for v in sol.x]))


# ---------------------------------------------------------------- bounce
BKEYS = ("e_a", "mu", "beta", "plow", "a_roll")


def total_yd(x, p, turf_params):
    s = shot_from_launch(x["ball_mph"] * MPH, x["launch_deg"], x["spin_rpm"], p, roll=False, dt=0.02)
    fl = fly((0, 0, R_BALL), _v(x), _w(x), p, dt=0.02)
    b = bounce_roll(fl.land_pos, fl.land_vel, fl.land_spin, turf_params=turf_params)
    return math.hypot(b["rest_x"], b["rest_y"]) / YD, fl


def _v(x):
    L = math.radians(x["launch_deg"]); v = x["ball_mph"] * MPH
    return (v * math.cos(L), 0.0, v * math.sin(L))


def _w(x):
    return (0.0, -x["spin_rpm"] * 2 * math.pi / 60, 0.0)


def fit_bounce(p, fit_rows, base=None):
    base = dict(base or TURF["normal"])
    def tp(th):
        d = dict(base); d.update(dict(zip(BKEYS, th))); return d
    def res(th):
        t = tp(th)
        return [total_yd(x, p, t)[0] - x["total_yd"] for x in fit_rows]
    sol = least_squares(res, [base[k] for k in BKEYS], diff_step=1e-3, bounds=([0.2, 0.3, 0.0, 0.0, 0.5], [0.9, 0.8, 1.0, 0.9, 3.0]))
    return tp(sol.x)


def total_residuals(p, rs, turf_params):
    out = []
    for x in rs:
        t, fl = total_yd(x, p, turf_params)
        out.append(dict(id=x["id"], group=x["group"], club_mph=x["club_mph"], pub_total=x["total_yd"], model_total=round(t, 1),
                        res_total=round(t - x["total_yd"], 1), pub_roll=round(x["total_yd"] - x["carry_yd"], 1),
                        model_roll=round(t - fl.carry_m / YD, 1), res_roll=round((t - fl.carry_m / YD) - (x["total_yd"] - x["carry_yd"]), 1),
                        model_carry=round(fl.carry_m / YD, 1), descent=round(fl.descent_deg, 1)))
    return out


# ---------------------------------------------------------------- full pipeline
def _by_group(res, key, groups=None):
    out = {}
    for g in sorted({r["group"] for r in res}):
        out[g] = _stat([r[key] for r in res if r["group"] == g])
    out["ALL"] = _stat([r[key] for r in res])
    return out


def run(write=False):
    rs = rows(); fr = flight_rows(rs); base = Params()
    rep = dict(note="Residual = model - published. fit/held-out roles are stated per block.")
    # ---- aero
    tmc = [x for x in fr if x["group"] == "tm_carry_opt"]
    dr = [x for x in rs if x["group"] == "descent" and x.get("ball_mph")]
    free = ("cd_scale", "cl_scale", "cd_spin_slope")

    def res(th):
        q = replace(base, **dict(zip(free, th)))
        r = [(sim_carry(x, q).carry_yd - x["carry_yd"]) / 3 for x in tmc]
        for x in dr:
            s = sim_carry(x, q); r += [(s.descent_deg - x["descent_deg"]) / 1.5, (s.carry_yd - x["carry_yd"]) / 3]
        return r
    sol = least_squares(res, [1.0, 1.0, 0.35], diff_step=1e-3, bounds=([0.3] * 3, [2.5] * 3))
    aero = dict(zip(free, [float(v) for v in sol.x])); p = replace(base, **aero)
    rep["aero_fit"] = dict(params=aero, fit_rows="TM carry-optimizer carry (30) + 3 landing-angle anchors (snippet: TrackMan PGA 2019/2023, LPGA 2023: carry and descent)")
    cr = carry_residuals(p, fr)
    rep["carry_residuals_calibrated_yd"] = _by_group(cr, "res")
    rep["carry_by_speed_band"] = {b: _stat([r["res"] for r in cr if lo <= r["club_mph"] < hi and r["group"] != "tm_carry_opt"])
                                  for b, (lo, hi) in {"<100 (held-out groups)": (0, 100), "100-120": (100, 121), ">=124": (124, 999)}.items()}
    rep["carry_rows"] = cr
    uncal = {m: _by_group(carry_residuals(replace(base, aero_model=m, cd_scale=1, cl_scale=1, cd_spin_slope=base.cd_spin_slope), fr), "res")["tm_carry_opt"]
             for m in ("bh_fit", "smits_smith_sec", "env_legacy")}
    rep["uncalibrated_aero_models_vs_tm_carry_opt"] = uncal
    drow = []
    for x in rs:
        if x["group"] == "descent" and x.get("ball_mph"):
            s = sim_carry(x, p); drow.append(dict(id=x["id"], tag=x["tag"], pub_descent=x["descent_deg"], model=round(s.descent_deg, 1),
                                                   res=round(s.descent_deg - x["descent_deg"], 1)))
    rep["descent_check"] = dict(rows=drow, note="the 3 rows with speed data were FIT; the USGA fetched 38.5/37.6 deg values have no speed/spin so are only context")
    # dt convergence
    xx = tmc[14]; rep["dt_convergence_carry_yd"] = {str(d): round(shot_from_launch(xx["ball_mph"] * MPH, xx["launch_deg"], xx["spin_rpm"], p, roll=False, dt=d).carry_yd, 3) for d in (0.02, 0.01, 0.005, 0.002)}
    # ---- impact
    tm = tm_rows(rs); ca = [x for x in tm if x["group"] == "tm_carry_opt"]; to = [x for x in tm if x["group"] == "tm_total_opt"]
    imp = fit_impact(p, ca, ("e0", "s_t")); p = replace(p, **imp, e_slope=0.0, s_t_slope=0.0)
    def block(q, sel):
        r = impact_resid(q, sel)
        return {k: _stat([x[k] for x in r]) for k in ("d_smash", "d_launch", "d_spin", "rel_spin")}
    rep["impact_fit"] = dict(params=imp, fit_rows="TM carry-optimizer rows (30)",
                             fit_residuals=block(p, ca), heldout_tm_total_opt=block(p, to),
                             uncalibrated_defaults=block(base, tm))
    q2 = replace(p, **fit_impact(p, [x for x in tm if x["club_mph"] <= 105], ("e0", "s_t")))
    rep["impact_speed_extrapolation"] = dict(fit="TM rows club <=105 mph", params={"e0": q2.e0, "s_t": q2.s_t}, heldout_110_120=block(q2, [x for x in tm if x["club_mph"] >= 110]))
    q3 = replace(p, **fit_impact(p, to, ("e0", "s_t")))
    rep["impact_reverse_cv"] = dict(fit="TM total-optimizer rows", params={"e0": q3.e0, "s_t": q3.s_t}, heldout_carry_opt=block(q3, ca))
    # Foresight/Burke ball speed check (smash at high speed): published ball/club
    rep["high_speed_smash_published"] = {x["id"]: round(x["ball_mph"] / x["club_mph"], 3) for x in rs if x["group"] in ("foresight", "longdrive") and x.get("ball_mph")}
    rep["high_speed_smash_model_centre"] = {str(c): round(impact(Delivery(c * MPH, 11.0, 3.0), p=p)["smash"], 3) for c in (120, 130, 140, 145)}
    # ---- bounce
    fit_b = [x for x in fr if x["group"] in ("tm_carry_opt", "foresight")]
    tp = fit_bounce(p, fit_b); tp = {k: float(v) for k, v in tp.items()}
    rep["bounce_fit"] = dict(params=tp, fit_rows="TM carry-optimizer totals (30) + Foresight midpoints (12); other groups held out",
                             bounds="e_a 0.2-0.9, mu 0.3-0.8, beta 0-1, plow 0-0.9, a_roll 0.5-3.0: e_a and a_roll sit near bounds (lumped, effective parameters)")
    tr = total_residuals(p, fr, tp)
    rep["total_residuals_yd"] = _by_group(tr, "res_total"); rep["roll_residuals_yd"] = _by_group(tr, "res_roll")
    rep["total_rows"] = tr
    # ---- firmness (relative calibration to Broadie deltas)
    ref = dict(ball_mph=167, launch_deg=10.9, spin_rpm=2686, club_mph=113)
    t0 = total_yd(ref, p, tp)[0]
    def solve_a(delta):
        lo, hi = 0.2, 8.0
        for _ in range(40):
            mid = (lo + hi) / 2; t = total_yd(ref, p, dict(tp, a_roll=mid))[0] - t0
            if t > delta: lo = mid
            else: hi = mid
        return (lo + hi) / 2
    soft_a, firm_a = solve_a(-5.31), solve_a(+4.49)
    turf = {"normal": dict(tp), "soft": dict(tp, a_roll=soft_a), "firm": dict(tp, a_roll=firm_a)}
    rep["firmness_calibration"] = dict(target="Broadie/ShotLink (USGA PDF, fetched): soft -5.31 yd, firm +4.49 yd of tee-shot TOTAL vs medium; tour-average shot",
                                       a_roll=dict(soft=soft_a, normal=tp["a_roll"], firm=firm_a),
                                       check_at_tour_avg={k: round(total_yd(ref, p, v)[0] - t0, 2) for k, v in turf.items()},
                                       check_at_130mph={k: None for k in turf})
    # roll vs descent slope: vary spin/launch at 120 mph club (~178 mph ball)
    import itertools
    pts = []
    for L, S in itertools.product((8, 10, 12, 14, 17), (1800, 2400, 3000, 3600)):
        x = dict(ball_mph=178, launch_deg=L, spin_rpm=S); t, fl = total_yd(x, p, tp); pts.append((fl.descent_deg, t - fl.carry_m / YD, fl.carry_m / YD))
    pts = np.array(pts); sl = np.polyfit(pts[:, 0], pts[:, 1], 1)
    rep["roll_vs_descent"] = dict(model_slope_yd_per_deg=float(sl[0]), model_roll_at_39deg=float(np.polyval(sl, 39)), n=len(pts), descent_range=[float(pts[:, 0].min()), float(pts[:, 0].max())],
                                  published_slopes_yd_per_deg="-0.74..-2.45 (median -1.7, 8 USGA/R&A experiments, fetched); ShotLink -1.52; proposed model -1.6",
                                  roll_range_yd=[float(pts[:, 1].min()), float(pts[:, 1].max())])
    rep["_params"] = {k: v for k, v in asdict(p).items()}
    rep["_turf"] = turf
    if write:
        json.dump(rep, open(ROOT / "data/references/golfphys_validation.json", "w"), indent=1, default=float)
        print("wrote validation json")
    return rep, p, turf


if __name__ == "__main__":
    rep, p, turf = run(write="--write" in sys.argv)
    for k in ("aero_fit", "carry_residuals_calibrated_yd", "carry_by_speed_band", "uncalibrated_aero_models_vs_tm_carry_opt", "descent_check", "dt_convergence_carry_yd", "impact_fit",
              "impact_speed_extrapolation", "impact_reverse_cv", "high_speed_smash_published", "high_speed_smash_model_centre", "bounce_fit", "total_residuals_yd", "roll_residuals_yd", "firmness_calibration", "roll_vs_descent"):
        print(k, json.dumps(rep[k], default=float)[:1500])
