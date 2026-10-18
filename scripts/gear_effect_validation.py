"""Off-centre / gear-effect residuals for golfphys against public measured data (data/references/gear_effect_measured_data.json).
Run: PYTHONPATH=. python scripts/gear_effect_validation.py [--write]   -> data/references/gear_effect_validation.json
Model-only comparison; nothing here changes golfphys. Tests in tests/test_realism_checks.py read the JSON this writes."""
import json, math, sys
from dataclasses import replace
from pathlib import Path
import numpy as np
from scipy.optimize import fsolve, least_squares
from golfphys import load_params, Delivery, Strike, impact
from golfphys.sim import simulate_shot

ROOT = Path(__file__).resolve().parent.parent
D = json.load(open(ROOT / "data/references/gear_effect_measured_data.json"))["datasets"]
MPH = 0.44704; IN = 0.0254; MM = 1e-3
P0 = load_params()


def shot(chs, dl, aoa, x=0.0, y=0.0, p=P0, hand="RH", full=False):
    d = Delivery(club_speed=chs * MPH, dynamic_loft_deg=dl, aoa_deg=aoa, handed=hand)
    im = impact(d, Strike(x_toe_m=x, y_high_m=y), p)
    out = dict(ball_mph=im["ball_speed"] / MPH, smash=im["smash"], launch=im["launch_deg"], backspin=im["backspin_rpm"],
               sidespin=im["sidespin_rpm"], spin=im["spin_rpm"], axis_draw_deg=im["spin_axis_deg"], hla_left_deg=im["azimuth_deg"])
    if full:
        r = simulate_shot(d, Strike(x_toe_m=x, y_high_m=y), p, turf="normal")
        out.update(carry_yd=r.carry_yd, total_yd=r.total_yd)
    return out


# ---------------------------------------------------------------- A. Hot Stix vertical (5 rows)
def hotstix():
    H = D["hotstix_2009"]; rows = H["rows"]; chs = H["club_speed_mph"]
    c = [r for r in rows if r["H_in"] == 0][0]

    def centre_fit(p):
        f = lambda u: [shot(chs, u[0], u[1], p=p)["launch"] - c["launch_deg"], shot(chs, u[0], u[1], p=p)["backspin"] - c["backspin_rpm"]]
        return fsolve(f, [9.0, -3.0])

    def predict(p, u):
        out = []
        for r in rows:
            s = shot(chs, u[0], u[1], y=r["H_in"] * IN, p=p, full=True)
            out.append(s)
        return out

    def table(p, u):
        pr = predict(p, u)
        t0 = [q for q, r in zip(pr, rows) if r["H_in"] == 0][0]
        res = []
        for q, r in zip(pr, rows):
            res.append(dict(H_in=r["H_in"], launch_meas=r["launch_deg"], launch_model=q["launch"], d_launch=q["launch"] - r["launch_deg"],
                            spin_meas=r["backspin_rpm"], spin_model=q["backspin"], d_spin=q["backspin"] - r["backspin_rpm"],
                            ddist_meas=r["distance_yd"] - c["distance_yd"], ddist_model_total=q["total_yd"] - t0["total_yd"],
                            ddist_model_carry=q["carry_yd"] - t0["carry_yd"], ball_mph=q["ball_mph"]))
        return res

    u = centre_fit(P0)
    base = table(P0, u)
    off = [r for r in base if r["H_in"] != 0]
    def rms(key, rr): return float(np.sqrt(np.mean([r[key] ** 2 for r in rr])))
    summary_base = dict(rms_launch=rms("d_launch", off), rms_spin=rms("d_spin", off),
                        rms_ddist_total=float(np.sqrt(np.mean([(r["ddist_model_total"] - r["ddist_meas"]) ** 2 for r in off]))))
    # slopes
    Hs = np.array([r["H_in"] for r in rows])
    sl = lambda key: float(np.polyfit(Hs, [r[key] for r in base], 1)[0])
    meas_launch_slope = float(np.polyfit(Hs, [r["launch_meas"] for r in base], 1)[0])
    meas_spin_slope = float(np.polyfit(Hs, [r["spin_meas"] for r in base], 1)[0])
    slopes = dict(launch_deg_per_in=dict(meas=meas_launch_slope, model=sl("launch_model")),
                  spin_rpm_per_in=dict(meas=meas_spin_slope, model=sl("spin_model")))

    # leave-one-out over the 4 offset rows: fit (roll_radius, gear_v) on 3 rows, predict the 4th; centre row calibrates the delivery.
    def fit_params(train, init=(0.305, 25.0)):
        def resid(z):
            p = replace(P0, roll_radius=z[0], gear_v_rpm_per_mph_in=z[1])
            uu = centre_fit(p)
            out = []
            for r in train:
                s = shot(chs, uu[0], uu[1], y=r["H_in"] * IN, p=p)
                out += [(s["launch"] - r["launch_deg"]) / 0.3, (s["backspin"] - r["backspin_rpm"]) / 100.0]
            return out
        sol = least_squares(resid, init, bounds=([0.12, 5.0], [0.9, 60.0]), x_scale=[0.1, 10.0])
        return sol.x
    loo = []
    offrows = [r for r in rows if r["H_in"] != 0]
    for k, held in enumerate(offrows):
        train = [r for j, r in enumerate(offrows) if j != k]
        z = fit_params(train)
        p = replace(P0, roll_radius=float(z[0]), gear_v_rpm_per_mph_in=float(z[1]))
        uu = centre_fit(p)
        s = shot(chs, uu[0], uu[1], y=held["H_in"] * IN, p=p)
        s0 = shot(chs, u[0], u[1], y=held["H_in"] * IN)
        loo.append(dict(held_H_in=held["H_in"], roll_radius_in=float(z[0] / IN), gear_v=float(z[1]),
                        heldout_d_launch_fit=s["launch"] - held["launch_deg"], heldout_d_spin_fit=s["backspin"] - held["backspin_rpm"],
                        heldout_d_launch_baseline=s0["launch"] - held["launch_deg"], heldout_d_spin_baseline=s0["backspin"] - held["backspin_rpm"]))
    zall = fit_params(offrows)
    pall = replace(P0, roll_radius=float(zall[0]), gear_v_rpm_per_mph_in=float(zall[1]))
    uall = centre_fit(pall)
    fitted = table(pall, uall)
    # Tutelman y-correction variant (CG-depth) for sensitivity: y_eff = H - D*sin(launch) with D = 1.3 in
    var = []
    for r in rows:
        yy = r["H_in"] * IN
        for _ in range(3):
            s = shot(chs, u[0], u[1], y=yy)
            yy = r["H_in"] * IN - 1.3 * IN * math.sin(math.radians(s["launch"]))
        var.append(dict(H_in=r["H_in"], y_eff_in=yy / IN, spin=s["backspin"], launch=s["launch"]))
    return dict(centre_delivery=dict(dyn_loft_deg=float(u[0]), aoa_deg=float(u[1]), note="solved so the centre row launch and spin match exactly (2 eq, 2 unknowns); the 4 offset rows are then genuine predictions of roll + gear terms"),
                baseline_rows=base, baseline_summary=summary_base, slopes=slopes, loo=loo,
                loo_rms=dict(launch_fit=float(np.sqrt(np.mean([r["heldout_d_launch_fit"] ** 2 for r in loo]))), spin_fit=float(np.sqrt(np.mean([r["heldout_d_spin_fit"] ** 2 for r in loo]))),
                             launch_baseline=float(np.sqrt(np.mean([r["heldout_d_launch_baseline"] ** 2 for r in loo]))), spin_baseline=float(np.sqrt(np.mean([r["heldout_d_spin_baseline"] ** 2 for r in loo])))),
                fit_all_offset_rows=dict(roll_radius_in=float(zall[0] / IN), gear_v_rpm_per_mph_in=float(zall[1]), rows=fitted),
                tutelman_y_correction_variant=var)


# ---------------------------------------------------------------- B. MyGolfSpy
def _calib_centre(chs, aoa, launch, p=P0):
    f = lambda dl: shot(chs, float(np.ravel(dl)[0]), aoa, p=p)["launch"] - launch
    return float(fsolve(f, [12.0])[0])


def mgs_vertical(p=P0):
    out = {}
    for g, bins in D["mygolfspy_2016_vertical"]["groups"].items():
        c = bins["center"]; dl = _calib_centre(c["chs"], c["aoa"], c["launch"], p)
        s0 = shot(c["chs"], dl, c["aoa"], p=p)
        g_out = dict(centre_dyn_loft_used=dl, centre_model=dict(ball=s0["ball_mph"], backspin=s0["backspin"], launch=s0["launch"], smash=s0["smash"]),
                     centre_meas=dict(ball=c["ball"], backspin=c["backspin"], launch=c["launch"], smash=c["ball"] / c["chs"]))
        for b in ("high", "low"):
            m = bins[b]
            meas = dict(d_launch=m["launch"] - c["launch"], d_spin=m["backspin"] - c["backspin"], d_smash=m["ball"] / m["chs"] - c["ball"] / c["chs"], d_ball=m["ball"] - c["ball"])
            grid = []
            for mm in range(0, 26):
                y = (1 if b == "high" else -1) * mm * MM
                s = shot(m["chs"], dl, m["aoa"], y=y, p=p)
                grid.append(dict(offset_mm=mm, d_launch=s["launch"] - c["launch"], d_spin=s["backspin"] - s0["backspin"] if m["aoa"] == c["aoa"] else s["backspin"] - s0["backspin"],
                                 d_smash=s["smash"] - s0["smash"]))
            def implied(key):
                tgt = meas[key]; best = min(grid, key=lambda r: abs(r[key] - tgt)); return best["offset_mm"], best[key]
            g_out[b] = dict(meas=meas, implied_offset_mm={k: implied(k)[0] for k in ("d_launch", "d_spin")},
                            model_at_implied={k: implied(k)[1] for k in ("d_launch", "d_spin")},
                            model_at_8mm=[r for r in grid if r["offset_mm"] == 8][0], model_at_12mm=[r for r in grid if r["offset_mm"] == 12][0])
        out[g] = g_out
    return out


def mgs_horizontal(hand="RH", p=P0):
    out = {}
    for g, bins in D["mygolfspy_2016_horizontal"]["groups"].items():
        c = bins["center"]; dl = _calib_centre(c["chs"], c["aoa"], c["launch"], p)
        s0 = shot(c["chs"], dl, c["aoa"], p=p)
        g_out = dict(centre_dyn_loft_used=dl, centre_model=dict(ball=s0["ball_mph"], spin=s0["spin"], launch=s0["launch"], smash=s0["smash"]),
                     centre_meas=dict(ball=c["ball"], spin=c["spin"], launch=c["launch"], smash=c["ball"] / c["chs"], axis=c["axis_tilt"], side=c["side"]))
        for b, sgn in (("toe", 1), ("heel", -1)):
            m = bins[b]
            # measured deltas in golfphys sign convention: draw axis +, HLA left +  (Foresight: axis_tilt negative = draw, side + = right)
            meas = dict(d_axis_draw=-(m["axis_tilt"] - c["axis_tilt"]), d_hla_left=-(m["side"] - c["side"]), d_smash=m["ball"] / m["chs"] - c["ball"] / c["chs"],
                        d_spin=m["spin"] - c["spin"], d_launch=m["launch"] - c["launch"])
            grid = []
            for mm in range(0, 26):
                s = shot(m["chs"], dl, m["aoa"], x=sgn * mm * MM, hand=hand, p=p)
                grid.append(dict(offset_mm=mm, d_axis_draw=s["axis_draw_deg"] - s0["axis_draw_deg"], d_hla_left=s["hla_left_deg"] - s0["hla_left_deg"],
                                 d_smash=s["smash"] - s0["smash"], d_spin=s["spin"] - s0["spin"], d_launch=s["launch"] - s0["launch"]))
            def implied(key):
                best = min(grid, key=lambda r: abs(r[key] - meas[key])); return best["offset_mm"]
            g_out[b] = dict(meas=meas, implied_offset_mm={k: implied(k) for k in ("d_axis_draw", "d_hla_left", "d_smash")},
                            model_at_8mm=[r for r in grid if r["offset_mm"] == 8][0], model_at_12mm=[r for r in grid if r["offset_mm"] == 12][0],
                            sign_axis_ok=bool(np.sign(grid[10]["d_axis_draw"]) == np.sign(meas["d_axis_draw"])),
                            sign_hla_ok=bool(np.sign(grid[10]["d_hla_left"]) == np.sign(meas["d_hla_left"])))
        out[g] = g_out
    return out


# ---------------------------------------------------------------- C. scalar checks
def trackman_geometry():
    p = P0
    toe10 = math.degrees(math.atan(10 * MM / p.bulge_radius)); low10 = math.degrees(math.atan(10 * MM / p.roll_radius))
    return dict(model_toe_10mm_face_open_deg=toe10, published_toe_10mm_deg=2.0, model_low_10mm_loft_deg=low10, published_low_10mm_deg=2.0,
                note="golfphys tilts the local face normal by x/R_bulge and y/R_roll (10 in / 12 in); TrackMan says ~2 deg per 10 mm for standard drivers. Implied radii for exactly 2.0 deg: %.1f in" % (10 * MM / math.tan(math.radians(2.0)) / IN))


def golfdigest(y0_in_list=(0.25, 0.5, 0.75)):
    n = D["golfdigest_robot_2026"]["numbers"]; chs = 95.0
    from scipy.optimize import minimize_scalar
    dl = float(minimize_scalar(lambda d: abs(shot(chs, d, 0.0, full=True)["carry_yd"] - n["mid_center_carry_avg_yd"]), bounds=(6.0, 20.0), method="bounded").x)
    c = shot(chs, dl, 0.0, full=True)
    res = dict(center_dyn_loft_used=dl, center_model=dict(ball_mph=c["ball_mph"], launch=c["launch"], spin=c["spin"], carry=c["carry_yd"]), rows=[])
    for y0 in y0_in_list:
        def carry(xin, yin): return shot(chs, dl, 0.0, x=xin * IN, y=yin * IN, full=True)
        toe = carry(0.75, 0) ; heel = carry(-0.75, 0); lowheel = carry(-0.75, -y0)
        hi = np.mean([carry(x, y0)["carry_yd"] for x in (-0.75, 0, 0.75)]) - c["carry_yd"]
        lo = np.mean([carry(x, -y0)["carry_yd"] for x in (-0.75, 0, 0.75)]) - c["carry_yd"]
        res["rows"].append(dict(vertical_offset_assumed_in=y0, toe_0p75_dcarry=toe["carry_yd"] - c["carry_yd"], heel_0p75_dcarry=heel["carry_yd"] - c["carry_yd"],
                                low_heel_dcarry=lowheel["carry_yd"] - c["carry_yd"], high_face_avg_dcarry=float(hi), low_face_avg_dcarry=float(lo),
                                toe_minus_heel=toe["carry_yd"] - heel["carry_yd"]))
    res["published"] = dict(low_heel_dcarry_field_avg=n["low_heel_carry_avg_yd"] - n["mid_center_carry_avg_yd"], high_face_avg_dcarry=n["high_face_zones_avg_yd"] - n["mid_center_carry_avg_yd"],
                            low_face_avg_dcarry=n["low_face_zones_avg_yd"] - n["mid_center_carry_avg_yd"], heel_dcarry_typical=[-15, -12], toe_dcarry_top10_heads=[-5.1, 0.0], toe_minus_heel=n["toe_vs_heel_same_height_yd"])
    return res


def upshaw():
    u = D["upshaw_via_tutelman"]; ball = u["ball_speed_mph"]; chs = ball / 1.47
    f = lambda dl: shot(chs, float(np.ravel(dl)[0]), 2.0)["launch"] - 12.0
    dl = float(fsolve(f, [14.0])[0])
    hi = shot(chs, dl, 2.0, y=0.75 * IN); lo = shot(chs, dl, 2.0, y=-0.75 * IN)
    return dict(model_spin_diff_1p5in_rpm=lo["backspin"] - hi["backspin"], measured_diff_rpm=u["spin_diff_rpm"], ball_speed_model_mph=(hi["ball_mph"], lo["ball_mph"]),
                note="Upshaw's delivery is unknown; used CHS = 140/1.47, AoA +2, DL for 12 deg launch (assumed). Secondary quote only.")


def trackman_pair():
    # offset (x) needed for smash to drop from 1.500 (centre) to 129/92 = 1.402: model effective-mass drop
    tgt = 129.0 / 92.0; c = 132.0 / 88.0
    best = None
    for mm in range(0, 31):
        s = shot(92, 12.0, 0.0, x=mm * MM)["smash"]; s0 = shot(92, 12.0, 0.0)["smash"]
        ratio = s / s0
        if best is None or abs(ratio - tgt / c) < abs(best[1] - tgt / c): best = (mm, ratio)
    return dict(measured_smash_ratio=tgt / c, implied_offset_mm=best[0], model_ratio_at_implied=best[1],
                note="Only a plausibility figure: the pair differs in club speed too and the offset is not stated.")


def horizontal_gear_scale(hand="RH"):
    """Per heel/toe bin: pick the offset that reproduces the measured start-line (HLA) change with the model bulge radius, then the
    gear-rate multiplier k (x16.4 rpm/mph/in) that reproduces the measured spin-axis change. k near 1 supports bulge+gear as a pair."""
    from scipy.optimize import brentq
    out = []
    for g, bins in D["mygolfspy_2016_horizontal"]["groups"].items():
        c = bins["center"]; dl = _calib_centre(c["chs"], c["aoa"], c["launch"]); s0 = shot(c["chs"], dl, c["aoa"])
        for b, sgn in (("toe", 1), ("heel", -1)):
            m = bins[b]; tgt_h = -(m["side"] - c["side"]); tgt_a = -(m["axis_tilt"] - c["axis_tilt"])
            fh = lambda mm: shot(m["chs"], dl, m["aoa"], x=sgn * mm * MM, hand=hand)["hla_left_deg"] - s0["hla_left_deg"] - tgt_h
            try: mm = brentq(fh, 0.5, 40.0)
            except ValueError: out.append(dict(group=g, bin=b, note="no HLA root")); continue
            def fa(k):
                p = replace(P0, gear_h_rpm_per_mph_in=P0.gear_h_rpm_per_mph_in * k)
                return shot(m["chs"], dl, m["aoa"], x=sgn * mm * MM, hand=hand, p=p)["axis_draw_deg"] - s0["axis_draw_deg"] - tgt_a
            try: k = brentq(fa, 0.0, 4.0)
            except ValueError: k = float("nan")
            out.append(dict(group=g, bin=b, offset_from_HLA_mm=float(mm), gear_scale_k=float(k), d_hla_left_meas=tgt_h, d_axis_draw_meas=tgt_a))
    ks = [r["gear_scale_k"] for r in out if "gear_scale_k" in r and r["gear_scale_k"] == r["gear_scale_k"]]
    return dict(rows=out, k_mean=float(np.mean(ks)), k_min=float(np.min(ks)), k_max=float(np.max(ks)), n=len(ks))


def vertical_param_grid():
    """(roll radius, vertical gear rate) grid scored on (a) Hot Stix 4 offset rows (launch/spin rms, centre-calibrated) and (b) the
    MyGolfSpy field ratio d_spin/d_launch (offset-free), 6 bins. Shows which pairs both datasets accept."""
    H = D["hotstix_2009"]; rows = H["rows"]; chs = H["club_speed_mph"]; c = [r for r in rows if r["H_in"] == 0][0]
    meas_ratio = []
    for g, bins in D["mygolfspy_2016_vertical"]["groups"].items():
        cc = bins["center"]
        for b in ("high", "low"):
            m = bins[b]; meas_ratio.append((m["backspin"] - cc["backspin"]) / (m["launch"] - cc["launch"]))
    grid = []
    for R in (8, 9, 10, 12):
        for gv in (14, 16, 18, 20, 22, 25):
            p = replace(P0, roll_radius=R * IN, gear_v_rpm_per_mph_in=float(gv))
            f = lambda u: [shot(chs, u[0], u[1], p=p)["launch"] - c["launch_deg"], shot(chs, u[0], u[1], p=p)["backspin"] - c["backspin_rpm"]]
            u = fsolve(f, [9.0, -3.0]); dl, aoa = float(u[0]), float(u[1])
            el, es = [], []
            for r in rows:
                if r["H_in"] == 0: continue
                s_ = shot(chs, dl, aoa, y=r["H_in"] * IN, p=p); el.append(s_["launch"] - r["launch_deg"]); es.append(s_["backspin"] - r["backspin_rpm"])
            s1 = shot(chs, dl, aoa, y=0.01 * IN, p=p); s0 = shot(chs, dl, aoa, p=p)
            ratio = (shot(chs, dl, aoa, y=8 * MM, p=p)["backspin"] - s0["backspin"]) / (shot(chs, dl, aoa, y=8 * MM, p=p)["launch"] - s0["launch"])
            grid.append(dict(roll_in=R, gear_v=gv, hotstix_rms_launch=float(np.sqrt(np.mean(np.square(el)))), hotstix_rms_spin=float(np.sqrt(np.mean(np.square(es)))), model_ratio_rpm_per_deg=float(ratio)))
    return dict(mygolfspy_ratio_rpm_per_deg=dict(values=meas_ratio, mean=float(np.mean(meas_ratio)), min=float(np.min(meas_ratio)), max=float(np.max(meas_ratio))),
                hotstix_ratio_rpm_per_deg=float(np.polyfit([r["H_in"] for r in rows], [r["backspin_rpm"] for r in rows], 1)[0] / np.polyfit([r["H_in"] for r in rows], [r["launch_deg"] for r in rows], 1)[0]), grid=grid)


def run():
    _hs = hotstix()
    _pf = replace(P0, roll_radius=_hs["fit_all_offset_rows"]["roll_radius_in"] * IN, gear_v_rpm_per_mph_in=_hs["fit_all_offset_rows"]["gear_v_rpm_per_mph_in"])
    return dict(generated="2026-10-17", mygolfspy_vertical_with_hotstix_fit=mgs_vertical(_pf), model="golfphys@0c2bca2 coefficients (unchanged)", hotstix=_hs, mygolfspy_vertical=mgs_vertical(), mygolfspy_horizontal=mgs_horizontal(), horizontal_gear_scale=horizontal_gear_scale(),
                trackman_geometry=trackman_geometry(), vertical_param_grid=vertical_param_grid(), golfdigest_95mph=golfdigest(), upshaw_secondary=upshaw(), trackman_smash_pair=trackman_pair())


if __name__ == "__main__":
    r = run()
    if "--write" in sys.argv:
        json.dump(r, open(ROOT / "data/references/gear_effect_validation.json", "w"), indent=1)
    print(json.dumps(r, indent=1)[:200000])
