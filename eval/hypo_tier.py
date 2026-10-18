"""HYPOTHETICAL TIER (force_scale > 1) 3-seed headline-gate table, built from results/gate_<name>_seed<seed>.json (seed 4000 file = ..._seed4000.json).
Kept SEPARATE from the learned-vs-scripted leaderboard.  'Effectively scripted' = on every recorded seed the policy's det carry is within 1% and lateral std within 15%
(or 0.3 m) of the zero-residual script recorded in the same gate file.  Nothing is guessed: every cell is read from the JSON.

REPRODUCIBILITY: this reads results/imit_private/gate_*.json. Those gate JSONs are HELD LOCALLY by the Trainer and are NOT in the
public repo (some are untracked or never committed), so the table CANNOT be rebuilt from main alone: running it on a fresh clone omits the held runs
(e.g. the gain 1.20 / 1.02 / 1.28 imit18 power-tier rows are 'Trainer-reported, file held')."""
import glob, json, os, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
TOL_CARRY, TOL_LAT_REL, TOL_LAT_ABS = 0.01, 0.15, 0.3


def tier():
    by = {}
    fs = sorted(glob.glob(str(ROOT / "results/gate_*_seed*.json")) + glob.glob(str(ROOT / "results/imit_private/gate_*.json")) + glob.glob(str(ROOT / "results/power48_private/gate_*.json")))   # *_private = Trainer's GATE_OUT dirs; seed-4000 file there has no _seed suffix
    for f in fs:
        d = json.loads(Path(f).read_text()); kw = d.get("env_kwargs", {})
        if not (kw.get("force_scale", 1.0) or 1.0) > 1.0 or "policy_det" not in d: continue
        by.setdefault(d["name"], {})[d["seed"]] = d
    rows = []
    for n, S in sorted(by.items()):
        eff = all(abs(d["policy_det"]["mean_carry"] - d["scripted_zero_residual"]["mean_carry"]) <= TOL_CARRY * d["scripted_zero_residual"]["mean_carry"]
                  and abs(d["policy_det"]["lateral_std"] - d["scripted_zero_residual"]["lateral_std"]) <= max(TOL_LAT_ABS, TOL_LAT_REL * d["scripted_zero_residual"]["lateral_std"])
                  for d in S.values() if "scripted_zero_residual" in d)
        res = (json.loads((ROOT / f"results/{n}.json").read_text()).get("args", {}).get("res_scale") if (ROOT / f"results/{n}.json").exists() else None)
        kw = next(iter(S.values()))["env_kwargs"]
        rows.append(dict(name=n, seeds=S, effectively_scripted=eff, res_scale=res, force_scale=kw.get("force_scale"), flight_steps=kw.get("flight_steps"),
                         all3=all(s in S and S[s]["gate_pass"] for s in (4000, 8000, 9000))))
    return rows


def noise_cell(name):
    """Quick noise screen (N=10 det eps, Gaussian sigma on every obs+action) from results/leaderboard.json; 'not measured' if absent."""
    try: L = json.loads((ROOT / "results/leaderboard.json").read_text())
    except Exception: return "not measured"
    for m in L["models"]:
        if name in m["names"] and m.get("noise_robust"):
            cl = m["modes"]["deterministic"]["mean_carry"]; nr = m["noise_robust"]
            return " / ".join(f"{nr[k]['mean_carry']:.0f} ({nr[k]['mean_carry']/cl*100:.0f}%)" if nr.get(k) and "mean_carry" in nr[k] else "-" for k in ("0.005", "0.01")) + " " + ("PASS" if all(nr.get(k) and nr[k]["contact_rate"] >= 1 and nr[k]["mean_carry"] >= 0.8 * cl for k in ("0.005", "0.01")) else "FAIL")
    return "not measured"


def _held(f):
    import subprocess
    try: return subprocess.run(["git", "ls-files", "--error-unmatch", str(f)], cwd=ROOT, capture_output=True).returncode != 0
    except Exception: return False


def gain_rows():
    """imit18 power-tier gates under overridden impact_gain / loft (Trainer; any results/imit_private/<dir>/gate_imit18_power_dart_s5*[_seedN].json whose env has impact_gain, plus the
    default gain-1.28 gates for comparison). Dedupes identical (model, gain, loft, seed). Smash = mean ball mph / mean impact club mph (ratio of means). Absent files => no rows."""
    rows, seen = [], set()
    files = sorted(glob.glob(str(ROOT / "results/imit_private/gate_imit18_power_dart_s5*.json"))) + sorted(glob.glob(str(ROOT / "results/imit_private/*/gate_imit18_power_dart_s5*.json")))
    for f in files:
        try: j = json.load(open(f))
        except Exception: continue
        ek = j.get("env_kwargs", {}); p, st = j["policy_det"], j["policy_stoch"]
        gain = float(ek.get("impact_gain") or (ek.get("impact_model") or {}).get("gain", 0)); loft = ek.get("loft_deg")
        m = re.search(r"dart_(s5\d)", f).group(1); key = (m, gain, loft, j["seed"])
        if key in seen: continue
        seen.add(key)
        sm = p["mean_peak_ball_speed"] / p["impact_club_speed_mean"]
        rows.append(dict(model="imit18_power_dart_" + m, gain=gain, loft=loft, seed=j["seed"], club=p["peak_club_mph_mean"], ball_mph=p["mean_peak_ball_speed"] * 2.23694, smash=sm, launch=p["launch_elev_mean_deg"],
                         carry=p["mean_carry"], lat=p["lateral_std"], lat_s=st["lateral_std"], landed=p["landed_fraction"], **{"pass": bool(j["gate_pass"])}, held=_held(f), src="/".join(Path(f).parts[-2:])))
    return sorted(rows, key=lambda r: (r["model"], -r["gain"], r["loft"] or 0, r["seed"]))


def stock_gate_rows():
    """STOCK (force_scale 1) 3-seed headline gates: Stage 25/26 scripted q23 dz016 + imit16 (+ imit20 if a gate file exists). Smash = mean ball mph / mean impact club mph."""
    rows = []
    for name, pats in (("stock scripted q_back 2.3 dz 0.016 (SCRIPTED, not learned)", ["results/imit_private/gate_stock_fs1_q23_dz016_scripted%s.json"]),
                       ("imit16_fs1_dart_s51 (script-distilled)", ["results/gate_imit16_fs1_dart_s51_seed4000.json", "results/gate_imit16_fs1_dart_s51_seed%s.json"]),
                       ("imit20_fs1_q23_dart_s51 (script-distilled)", ["results/gate_imit20_fs1_q23_dart_s51_seed4000.json", "results/gate_imit20_fs1_q23_dart_s51_seed%s.json", "results/imit_private/gate_imit20_fs1_q23_dart_s51%s.json"])):
        got = False
        for sd, sfx in ((4000, ""), (8000, "_seed8000"), (9000, "_seed9000")):
            cands = []
            for pt in pats:
                if "%s" in pt: cands.append(pt % (sfx if "imit_private" in pt else str(sd)))
                else: cands.append(pt) if sd == 4000 else None
            f = next((ROOT / c for c in cands if (ROOT / c).exists()), None)
            if f is None: continue
            j = json.load(open(f)); p = j["policy_det"]; st = j["policy_stoch"]; got = True
            rows.append(dict(name=name, seed=j["seed"], club=p["peak_club_mph_mean"], ball=p["mean_peak_ball_speed"] * 2.23694, smash=p["mean_peak_ball_speed"] / p["impact_club_speed_mean"], launch=p["launch_elev_mean_deg"],
                             carry=p["mean_carry"], lat=p["lateral_std"], lat_s=st["lateral_std"], loft=j["env_kwargs"].get("loft_deg"), pas=bool(j["gate_pass"]), held=_held(f), src="/".join(Path(f).parts[-2:])))
        if not got: rows.append(dict(name=name, missing=True))
    return rows


def md():
    R = tier()
    L = ["## HYPOTHETICAL TIER (force_scale > 1): 3-seed headline gate, kept separate from learned vs scripted", "",
         "**DISTANCES INFLATED for power-tier rows** (env impact_model gain 1.28 gives smash ~1.55-1.60 > the ~1.48 legal limit; see results/ball_flight_audit.md); do not quote them as real-world distance. "
         "**force_scale 2 (hypothetical-strength actuators)**: boosted actuator force caps; not human- or robot-attainable. Source: `results/gate_<name>_seed<seed>.json` (eval_gate, headline tier: det AND stoch contact>=99%, lateral std<=2.73 m, launch 5-20 deg, carry>=min_carry, landed>=90%). "
         "'Effectively scripted' = policy det carry within 1% and lateral std within 15% (or 0.3 m) of the zero-residual script in the same file on every seed; such rows are NOT learned drives. A model counts as passing only if ALL of seeds 4000/8000/9000 pass.", "",
         "| model | label | force_scale | flight_steps | residual cap (res_scale) | seed | episodes | det carry m / yd | det lat std m | stoch lat std m | landed (det) | launch deg | club mph | script lat std m | noise quick (carry m, % of clean; sigma 0.005 / 0.01) | headline |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in R:
        sw = next(iter(r["seeds"].values()))["env_kwargs"].get("script_weight")
        lab = "SCRIPT-FREE IMITATION OF THE SCRIPT (script-distilled policy = 100% of joint targets, imitating the v3 script; force_scale 2, hypothetical-strength actuators)" if (sw == 0 and r["name"].startswith("imit")) and not r["effectively_scripted"] else "EFFECTIVELY SCRIPTED (force_scale 2, hypothetical-strength actuators)" if r["effectively_scripted"] else "POLICY DIFFERS FROM SCRIPT (hypothetical actuators; learned fraction: see leaderboard row)"
        for s, d in sorted(r["seeds"].items()):
            p, st, z = d["policy_det"], d["policy_stoch"], d.get("scripted_zero_residual", {})
            L.append(f"| {r['name']} | {lab} | {r['force_scale']:g} | {r['flight_steps']} | {r['res_scale']} | {s} | {d['episodes']} | {p['mean_carry']:.1f} / {p['mean_carry']*1.09361:.0f} | {p['lateral_std']:.2f} | {st['lateral_std']:.2f} | {p['landed_fraction']*100:.0f}% | {p['launch_elev_mean_deg']:.1f} | {p['peak_club_mph_mean']:.1f} | {z.get('lateral_std', float('nan')):.2f} | {noise_cell(r['name'])} | {'PASS' if d['gate_pass'] else 'FAIL'} (min_carry {d['min_carry']}) |")
    G = gain_rows()
    if not G:
        L += ["", "### imit18 power tier: impact-gain / loft re-gates", "", "Gain re-gate files (results/imit_private/, Trainer) are not present in this checkout: table omitted (held locally, not an error)."]
    else:
        L += ["", "### imit18 power tier (hypothetical, no spin model): HEADLINE gain-1.20 re-gates vs the inflated gain-1.28 default", "",
              "Trainer gates (100 eps x seeds 4000/8000/9000), env `impact_gain` overridden. **Use the gain 1.20 rows as the headline power tier**; gain 1.28 (313.8 m class, smash ~1.6) is INFLATED. Smash = mean ball mph / mean impact club mph; flags use the launch_report thresholds (fail >1.50, warn >1.49 or <1.30; derived, not published). A flagged row is not eligible as a showcase/top row. Gain 1.0 exactly was not gated. Rows marked `held` have no backing file in the repo (Trainer-reported, file held on the box).", "",
              "| model | gain | loft deg | seed | club mph | ball mph | smash | smash flag | launch deg | det carry m / yd | det lat std m | stoch lat std m | landed | headline | backing |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in G:
            fl = "FAIL smash>1.50" if r["smash"] > 1.50 else "WARN smash>1.49" if r["smash"] > 1.49 else "WARN smash<1.30" if r["smash"] < 1.30 else "ok"
            L.append(f"| {r['model']} | {r['gain']:g} | {r['loft']} | {r['seed']} | {r['club']:.1f} | {r['ball_mph']:.0f} | {r['smash']:.3f} | {fl} | {r['launch']:.1f} | {r['carry']:.1f} / {r['carry']*1.09361:.0f} | {r['lat']:.2f} | {r['lat_s']:.2f} | {r['landed']*100:.0f}% | {'PASS' if r['pass'] else 'FAIL'} | {'held locally (not in repo)' if r['held'] else 'in repo'} `{r['src']}` |")
        miss = [f"{m} loft -27 seed 9000 (and loft -27 for s52 entirely)" for m in ("imit18_power_dart_s51",) if not any(r["model"] == m and r["loft"] == -27 and r["seed"] == 9000 for r in G)]
        if miss: L += ["", "Missing (not in the Trainer files found): " + "; ".join(miss) + "."]
    SG = stock_gate_rows()
    if SG:
        L += ["", "### STOCK motors (force_scale 1): 3-seed headline gates, Stage 25/26 (Trainer)", "",
              "Gate = eval_gate headline protocol (100 eps x seeds 4000/8000/9000). Smash = mean ball mph / mean impact club mph: ~1.0 means the ball leaves barely faster than the club (not a real-contact smash; flagged WARN <1.30 by the smash gate), so these carries are far SHORT of real driver distance. Rows marked held have no backing file in the repo.", "",
              "| model | seed | loft | club mph | ball mph | smash | smash flag | launch deg | det carry m / yd | det lat std m | stoch lat std m | headline | backing |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in SG:
            if r.get("missing"): L.append(f"| {r['name']} | - | - | - | - | - | - | - | - | - | - | MISSING: no gate JSON found (only a result JSON/model, if any); not evaluated here | - |"); continue
            fl = "FAIL smash>1.50" if r["smash"] > 1.50 else "WARN smash>1.49" if r["smash"] > 1.49 else "WARN smash<1.30" if r["smash"] < 1.30 else "ok"
            L.append(f"| {r['name']} | {r['seed']} | {r['loft']} | {r['club']:.1f} | {r['ball']:.0f} | {r['smash']:.3f} | {fl} | {r['launch']:.1f} | {r['carry']:.1f} / {r['carry']*1.09361:.0f} | {r['lat']:.2f} | {r['lat_s']:.2f} | {'PASS' if r['pas'] else 'FAIL'} | {'held locally (not in repo)' if r['held'] else 'in repo'} `{r['src']}` |")
        L += ["", "**imit15_dart_s52 note:** the lateral std 4.37 m (with a ~190 m outlier) comes from a seed-5000 TRAIN-env run (`results/imit_private/gate_imit15_dart_s52_seed5000.json`, headline FAIL). Seed 5000 is NOT a gate seed; it is not a gate result. The authoritative 3-seed gates (4000/8000/9000) pass with lateral std 1.46/0.54/2.14 m (Trainer files) and 1.5/0.91/2.11 m (repo `results/gate_imit15_dart_s52_seed*.json`). Both sets are listed; the 3-seed gates decide."]
    L += ["", "3/3-seed pass: " + (", ".join(f"{r['name']}: {'YES' if r['all3'] else 'NO'}" for r in R) or "no rows"), ""]
    return L


if __name__ == "__main__":
    import sys
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print((__doc__ or "").strip()); sys.exit(0)
    print("\n".join(md()))
