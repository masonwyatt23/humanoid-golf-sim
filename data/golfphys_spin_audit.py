"""Golfphys spin/launch audit vs MEASURED TrackMan aggregate rows (Data Agent, 2026-10-24 ET).

DEFERRED (Evaluator review 2026-10-24; not adopted). Opt-in proposal only: golfphys defaults are NOT changed. `proposed_params()` returns a Params copy with the
calibrated tangential-impulse terms (s_t, s_t_slope); callers must opt in explicitly.
Fit uses ONLY measured rows in data/references/golfphys_spin_audit_rows.csv (split by SOURCE, pre-declared):
  train    = TrackMan Combine MALE driver averages (5) + TrackMan PGA/LPGA Tour driver averages (2)
  held_out = TrackMan Combine FEMALE driver averages (4; 79-90 mph, closest to the 74 mph question)
No policy/training results are used anywhere in this file.
Optional: --held PATH adds counsel_pending TrackMan-2010-chart rows (kept OUTSIDE the repo) as an extra analysis-only check.
"""
import csv, json, math, sys
from dataclasses import replace
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from golfphys.params import load_params
from golfphys.impact import impact, Delivery, Strike, MPH

ROOT = Path(__file__).resolve().parent.parent
ROWS = ROOT / "data/references/golfphys_spin_audit_rows.csv"
OUT = ROOT / "data/references/golfphys_spin_audit.json"
# fitted below by main(); stored here after the audit run so proposed_params() is reproducible without refitting
PROPOSED = {"s_t": None, "s_t_slope": None}


def load_rows(path=ROWS):
    with open(path) as f:
        return [r for r in csv.DictReader(f)]


def predict(r, p, mode="spin_loft"):
    """mode 'spin_loft': DL = AoA + published spin loft (matches the spin driver); 'dyn_loft': DL as published."""
    aoa = float(r["aoa_deg"]); dl = aoa + float(r["spin_loft_deg"]) if mode == "spin_loft" else float(r["dynamic_loft_deg"])
    o = impact(Delivery(float(r["club_mph"]) * MPH, dl, aoa), Strike(), p=p)
    return dict(spin=o["spin_rpm"], launch=o["launch_deg"], ball_mph=o["ball_speed"] / MPH, spin_loft=o["spin_loft_deg"])


def stats(rows, p, mode="spin_loft"):
    out = []
    for r in rows:
        q = predict(r, p, mode); m = float(r["spin_rpm"])
        out.append(dict(id=r["id"], club_mph=float(r["club_mph"]), spin_loft=float(r["spin_loft_deg"]), meas_spin=m,
                        pred_spin=round(q["spin"]), err_rpm=round(q["spin"] - m), err_pct=round(100 * (q["spin"] / m - 1), 1),
                        meas_launch=float(r["launch_deg"]), pred_launch=round(q["launch"], 2), err_launch=round(q["launch"] - float(r["launch_deg"]), 2),
                        meas_ball=float(r["ball_mph"]), pred_ball=round(q["ball_mph"], 1)))
    e = np.array([x["err_rpm"] for x in out], float); el = np.array([x["err_launch"] for x in out], float)
    return dict(n=len(out), bias_rpm=round(float(e.mean()), 0), rmse_rpm=round(float(np.sqrt((e ** 2).mean())), 0),
                launch_bias=round(float(el.mean()), 2), launch_rmse=round(float(np.sqrt((el ** 2).mean())), 2), rows=out)


def fit(train, base):
    def res(x):
        p = replace(base, s_t=x[0], s_t_slope=x[1])
        return [(predict(r, p)["spin"] - float(r["spin_rpm"])) / 100.0 for r in train]
    s = least_squares(res, [base.s_t, 0.0], bounds=([0.2, -0.1], [1.5, 0.1]))
    return float(s.x[0]), float(s.x[1])


def proposed_params(base=None):
    base = base or load_params()
    if PROPOSED["s_t"] is None:
        PROPOSED.update(json.load(open(OUT))["proposal"]["params"])
    return replace(base, s_t=PROPOSED["s_t"], s_t_slope=PROPOSED["s_t_slope"])


def probe(p):
    o = {}
    for v, sl in [(74, 16), (74, 17), (74, 18)]:
        q = impact(Delivery(v * MPH, sl + 1.0, 1.0), Strike(), p=p)
        o[f"{v}mph_sl{sl}_aoa+1"] = dict(spin=round(q["spin_rpm"]), launch=round(q["launch_deg"], 2), ball_mph=round(q["ball_speed"] / MPH, 1))
    # K30 sanity case (Trainer-reported MODEL inputs, not data): DL 17.3, AoA +1.0, LH; centre strike + low-strike sweep
    k = {}
    for y in (0.0, -0.01, -0.02, -0.022, -0.025):
        q = impact(Delivery(74 * MPH, 17.3, 1.0, handed="LH"), Strike(0.0, y), p=p)
        k[f"y_high_{y*1000:+.0f}mm"] = dict(spin=round(q["spin_rpm"]), launch=round(q["launch_deg"], 2), smash=round(q["smash"], 3))
    o["K30_inputs_74mph_dl17.3_aoa+1_LH"] = k
    return o


def main(held_path=None):
    rows = load_rows(); base = load_params()
    train = [r for r in rows if r["split"] == "train"]; held = [r for r in rows if r["split"] == "held_out"]
    st, sl = fit(train, base); cal = replace(base, s_t=st, s_t_slope=sl)
    rep = dict(generated="2026-10-24 (America/New_York)", baseline_params=dict(s_t=base.s_t, s_t_slope=base.s_t_slope),
               split="by source: train = TM Combine male + TM Tour; held_out = TM Combine female (pre-declared before fitting)",
               before=dict(train=stats(train, base), held_out=stats(held, base), held_out_dynloft_inputs=stats(held, base, "dyn_loft"),
                           train_dynloft_inputs=stats(train, base, "dyn_loft")),
               after=dict(train=stats(train, cal), held_out=stats(held, cal)),
               proposal=dict(params=dict(s_t=round(st, 4), s_t_slope=round(sl, 5)), form="s_t_eff = s_t + s_t_slope*(spin_loft-12) (existing golfphys form)", opt_in=True),
               probe_before=probe(base), probe_after=probe(cal))
    if held_path:
        hr = [dict(r, spin_loft_deg=str(float(r["dyn_loft"]) - float(r["aoa"])), aoa_deg=r["aoa"], dynamic_loft_deg=r["dyn_loft"]) for r in csv.DictReader(open(held_path))]
        rep["counsel_pending_tm2010_check"] = dict(before=stats(hr, base), after=stats(hr, cal), note="TrackMan 2010 optimizer MODEL rows, counsel_pending; analysis only, not fit")
    OUT.write_text(json.dumps(rep, indent=1)); return rep


if __name__ == "__main__":
    r = main(sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--held" else None)
    for k in ("before", "after"):
        for s in ("train", "held_out"):
            x = r[k][s]; print(k, s, "n", x["n"], "bias", x["bias_rpm"], "rmse", x["rmse_rpm"], "launch bias", x["launch_bias"], "rmse", x["launch_rmse"])
    print(json.dumps(r["proposal"])); print(json.dumps(r["probe_before"])); print(json.dumps(r["probe_after"]))
    if "counsel_pending_tm2010_check" in r:
        c = r["counsel_pending_tm2010_check"]; print("tm2010", c["before"]["bias_rpm"], c["before"]["rmse_rpm"], "->", c["after"]["bias_rpm"], c["after"]["rmse_rpm"])
