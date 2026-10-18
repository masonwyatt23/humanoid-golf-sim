"""Build docs/dashboard.html: static, self-contained (inline CSS, no JS/network). python -m sim.dashboard
Reads results/leaderboard.json, results/golf_simulator_validation.json, results/course_estimates.json."""
import json, os, html, math, datetime

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
J = lambda p: json.load(open(os.path.join(ROOT, p)))
e = html.escape


def f(v, nd=1, suf=""):
    return "-" if v is None or (isinstance(v, float) and not math.isfinite(v)) else f"{v:.{nd}f}{suf}"


def power_presets_html():
    """imit18 power-tier gate rows at impact gain 1.20 (headline) by loft + stock 3-seed gates (imit20, imit16, scripted dz016); smash = ball mph / impact club mph; flags per launch_report thresholds."""
    import sys; sys.path.insert(0, ROOT)
    from eval.hypo_tier import gain_rows, stock_gate_rows
    def fl(sm): return "FAIL smash>1.50" if sm > 1.50 else "WARN smash>1.49" if sm > 1.49 else "WARN smash<1.30" if sm < 1.30 else "ok"
    pr = []
    for r in gain_rows():
        if abs(r["gain"] - 1.2) > 1e-9: continue
        f_ = fl(r["smash"]); pr.append(f"<tr><td>{e(r['model'])} (hypothetical power tier, gain 1.20, no spin model)</td><td>{r['loft']}</td><td>{r['seed']}</td><td>{r['club']:.1f}</td><td>{r['ball_mph']:.0f}</td><td>{r['smash']:.3f}</td><td class=\"{'ok' if f_ == 'ok' else 'bad'}\">{f_}</td><td>{r['launch']:.1f}</td><td>{r['carry']*1.09361:.0f} yd ({r['carry']:.0f} m)</td><td>{r['lat']:.2f}</td><td>{'PASS' if r['pass'] else 'FAIL'}</td></tr>")
    for r in stock_gate_rows():
        if r.get("missing"): pr.append(f"<tr><td>{e(r['name'])}</td><td colspan=10>MISSING: no gate JSON found</td></tr>"); continue
        f_ = fl(r["smash"]); pr.append(f"<tr><td>STOCK force_scale 1: {e(r['name'])}</td><td>{r['loft']}</td><td>{r['seed']}</td><td>{r['club']:.1f}</td><td>{r['ball']:.0f}</td><td>{r['smash']:.3f}</td><td class=\"{'ok' if f_ == 'ok' else 'bad'}\">{f_}</td><td>{r['launch']:.1f}</td><td>{r['carry']*1.09361:.0f} yd ({r['carry']:.0f} m)</td><td>{r['lat']:.2f}</td><td>{'PASS' if r['pas'] else 'FAIL'}</td></tr>")
    return "".join(pr)


def hypo_html():
    import sys; sys.path.insert(0, ROOT)
    from eval.hypo_tier import tier, noise_cell
    rows = []
    for r in tier():
        lab = '<span class="b hy">EFFECTIVELY SCRIPTED, force_scale 2 (hypothetical-strength actuators)</span>' if r["effectively_scripted"] else '<span class="b ln">policy differs from script</span> <span class="b hy">force_scale 2 (hypothetical-strength actuators)</span>'
        for sd, d in sorted(r["seeds"].items()):
            p, st = d["policy_det"], d["policy_stoch"]
            rows.append(f"<tr><td>{e(r['name'])}<br>{lab}</td><td>{sd}</td><td>{p['mean_carry']*1.09361:.0f} yd ({p['mean_carry']:.1f} m)</td><td>{p['lateral_std']:.2f} / {st['lateral_std']:.2f}</td><td>{p['landed_fraction']*100:.0f}%</td><td>{p['peak_club_mph_mean']:.1f}</td><td>{e(noise_cell(r['name']))}</td><td class=\"{'ok' if d['gate_pass'] else 'bad'}\">{'PASS' if d['gate_pass'] else 'FAIL'}</td></tr>")
    return "".join(rows)


def side_by_side(lb):
    out = []
    for nm, why in (("imit9_w000_s51", "best lateral spread (script-free imitation of the scripted v3 swing; passes 3-seed gate; noise-fragile)"), ("imit3_w050_s51", "best under noise (50% learned / 50% scripted)")):
        m = next((m for m in lb["models"] if nm in m["names"] and "modes" in m), None)
        if not m: continue
        d = m["modes"]["deterministic"]; nr = {k: v for k, v in (m.get("noise_robust") or {}).items() if v and "mean_carry" in v}
        out.append(f"<b>{nm}</b>: {why}; det carry {d['mean_carry_yd']:.0f} yd, lateral std {d['lateral_std']:.2f} m; quick noise carry " + (", ".join(f"{v['mean_carry']/d['mean_carry']*100:.0f}% at sigma {k}" for k, v in sorted(nr.items())) or "n/a") + ".")
    return " ".join(out)


def stock_note(lb):
    st = next((m for m in lb["models"] if m.get("scripted") and any("STOCK motors" in n for n in m["names"]) and "modes" in m), None)
    q = [m for m in lb["models"] if (m.get("env_kwargs") or {}).get("force_scale", 1.0) in (None, 1.0) and not m.get("scripted") and m["names"] in lb.get("qualifying", [])]
    t = "<b>Motor strength.</b> " + ("A trained stock-motor (force_scale 1) model qualifies: " + e(q[0]["names"][0]) + ". " if q else "<b>No trained model on stock motors (force_scale 1) qualifies.</b> ")
    if st: d = st["modes"]["deterministic"]; t += f"Stock-motor scripted (not learned) reference: {d['mean_carry_yd']:.0f} yd carry, {d['peak_club_mph_mean']:.0f} mph. "
    return t + "Every row below tagged force_scale 2 or power tier is hypothetical-strength: not a realistic-motor result." + " <b>imit19_masonmapped_dart_s51</b>: its tiny lateral std (0.04-0.11 m) is a SLOW-SWING / low-speed artifact (87.6 mph, 58 m carry vs 120 mph, 112 m for imit15), not better accuracy; arm-based DTW/track_score style columns are VOID (lead/trail arm bug, see Trainer). <b>Power-tier distances are INFLATED</b> (impact gain 1.28) until the gain is fixed. <b>Distance caveat:</b> MuJoCo carries are not launch-monitor numbers. Power-tier rows (club 132 mph, smash 1.55-1.60, ~3080 rpm set by the env impact model) are hypothetical and ~6% above the model carry at a 1.48 smash; v3 rows have smash ~1.0 and almost no spin, so they are far SHORTER than a real driver at the same club speed (see results/ball_flight_audit.md and the leaderboard table sim carry vs launch-monitor-model carry)."


def build():
    lb, val, crs = J("results/leaderboard.json"), J("results/golf_simulator_validation.json"), J("results/course_estimates.json")
    rows = []
    for m in lb["models"]:
        d, s = m["modes"]["deterministic"], m["modes"]["stochastic"]
        name = m["names"][0] if not m["scripted"] else m["names"][0]
        scripted = bool(m["scripted"]); fs = m["env_kwargs"].get("force_scale")
        cr = (d["contact_rate"] + s["contact_rate"]) / 2
        carry = d.get("mean_carry_yd"); carry = 0.0 if carry is None or not math.isfinite(carry) else carry
        rows.append((cr, carry, m, d, s, name, scripted, fs))
    rows.sort(key=lambda r: (-r[0], -r[1]))
    best = lb["best_qualifying"] or []
    tr = []
    for i, (cr, carry, m, d, s, name, scripted, fs) in enumerate(rows, 1):
        tag = '<span class="b sc">SCRIPTED (not learned)</span>' if scripted else ('<span class="b ln">script-distilled</span>' if any(x.startswith('imit') for x in m['names']) else '<span class="b ln">learned</span>')
        hyp = '<span class="b hy">force_scale %g (hypothetical-strength actuators)</span>' % fs if fs and fs > 1 else ("" if fs else '<span class="b">default env</span>')
        if m.get("verdict"): tag = tag + ' <span class="b sc">' + e(m["verdict"]) + '</span>'
        _r = m.get("realism") or {}
        if _r: tag = tag + ' <span class="b ' + ('ln' if _r.get('verdict') == 'PASS' else 'hy') + '">realism: ' + e(str(_r.get('verdict'))) + (' %s/8' % _r['checks_passed'] if _r.get('checks_passed') is not None else '') + '</span>'
        if m.get("hypo_demoted"): tag = '<span class="b hy">HYPOTHETICAL: effectively scripted (yaw-only residual, fs2 + impact gain 1.28); not a stock-motor policy</span>'
        star = " &#9733;" if (not scripted and m["names"][:1] == best[:1] and (len(best) < 2 or best[1] in m["names"])) else ""
        tr.append(f"<tr><td>{i}</td><td>{e(' / '.join(m['names']))[:110]}{star}<br>{tag} {hyp}</td><td>{f(d['contact_rate']*100,0,'%')} / {f(s['contact_rate']*100,0,'%')}</td>"
                  f"<td>{f(d.get('mean_carry_yd'),0)}</td><td>{f(d.get('mean_total_yd'),0)}</td><td>{f(d.get('lateral_std'),2)}</td><td>{f(d.get('launch_elev_mean_deg'),1)}</td>"
                  f"<td>{f(d.get('peak_club_mph_mean'),0)}</td><td>{f(m.get('smash_ratio_det'),2)}</td><td class=\"{'bad' if m.get('smash_flag') else 'ok'}\">{e(m.get('smash_flag') or 'ok')}</td></tr>")
    vt = []
    for blk, title in (("flight_from_published_launch", "Flight model from published launch conditions"), ("impact_model", "Impact model (club speed to ball)")):
        for c in val[blk]["checks"]:
            err = f"{c['error']*100:+.1f}%" if c["error_kind"].startswith("%") else f"{c['error']:+.1f}"
            vt.append(f"<tr><td>{title}</td><td>{c['metric']}</td><td>{c['model']:.2f}</td><td>{c['published']:.2f}</td><td>{err}</td><td class=\"{'ok' if c['passed'] else 'bad'}\">{'PASS' if c['passed'] else 'FAIL'}</td></tr>")
    ct = "".join(f"<tr><td>{e(r['profile'])}</td><td>{r['mean_score']:.1f}</td><td>{r['mean_vs_par']:+.1f}</td><td>{r['p10']:.0f}-{r['p90']:.0f}</td><td>{r['fairways_hit_pct']:.0f}%</td><td>{r['gir_pct']:.0f}%</td></tr>" for r in crs["results"])
    book = "".join(f"<tr><td>{h['n']}</td><td>{h['par']}</td><td>{h['yards']}</td><td>{h['fw_halfwidth_yd']*2:g}</td></tr>" for h in crs["holes"])
    sc = val["flight_from_published_launch"]["shot"]
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Humanoid golf dashboard</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><style>
body{{font:15px/1.45 system-ui,sans-serif;max-width:1100px;margin:24px auto;padding:0 14px;color:#1a2a1a;background:#f6f8f4}}
h1{{margin:.2em 0}} h2{{border-bottom:2px solid #6a9a5a;padding-bottom:3px;margin-top:1.6em}}
table{{border-collapse:collapse;width:100%;background:#fff;font-size:13px}} th,td{{border:1px solid #ccd6c6;padding:4px 7px;text-align:left;vertical-align:top}} th{{background:#e4eddf}}
.b{{display:inline-block;font-size:11px;padding:1px 6px;border-radius:9px;background:#ddd;margin:1px 2px}} .sc{{background:#ffd9a8}} .ln{{background:#bfe5b5}} .hy{{background:#f5b7b1}}
.ok{{color:#176b17;font-weight:700}} .bad{{color:#b00020;font-weight:700}} .note{{background:#fff7d6;border-left:4px solid #e0b000;padding:8px 12px;margin:10px 0}}
</style></head><body>
<h1>Humanoid golf: evaluation dashboard</h1>
<p>Generated {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} (America/New_York) from <code>results/leaderboard.json</code>, <code>results/golf_simulator_validation.json</code>, <code>results/course_estimates.json</code>. Regenerate: <code>python -m sim.dashboard</code>.</p>
<div class="note"><b>Honest labels.</b> Every leaderboard row uses boosted actuators (force_scale &gt; 1) unless marked otherwise: <b>force_scale 2 (hypothetical-strength actuators)</b>, not a real robot. Rows tagged SCRIPTED are a hand-written swing, not learned. Leaderboard yards use the MuJoCo-physics ball (smash about 1.0, a known artifact). Launch-monitor and course numbers are <b>model-based</b> (analytic ball model / Monte Carlo), not measured.</div>
<div class="note">{stock_note(lb)}</div>
<div class="note"><b>Two models shown side by side, neither promoted as &quot;learned from Mason&quot;.</b> {side_by_side(lb)} Both imitate the scripted swing and run force_scale 2 (hypothetical-strength actuators).</div>
<h2>Leaderboard (ranked by true contact, then mean carry; star = best qualifying model)</h2>
<div class="note"><b>Smash flag.</b> Rows with smash (det mean ball mph / impact club mph) outside 1.30-1.49 are flagged (FAIL &gt;1.50, WARN &gt;1.49 or &lt;1.30; thresholds derived, not published) and cannot be the star/best/showcase row. Boosted v3 policies at ~0.9-1.0 are flagged.</div>
<table><tr><th>#</th><th>Model</th><th>Contact det / stoch</th><th>Carry yd (det)</th><th>Total yd (det)</th><th>Lateral std m</th><th>Launch deg</th><th>Peak club mph</th><th>Smash (ball/impact club)</th><th>Smash flag (ok = 1.30-1.49)</th></tr>{''.join(tr)}</table>
<p>Episodes per row: {lb['episodes']}, seed base {lb['seed_base']}. Total equals carry when the episode ends at first landing (no roll). Qualification: {e(json.dumps(lb['qualify_criterion']))}.</p>
<h2>Hypothetical tier (force_scale &gt; 1): 3-seed headline gate, separate from learned vs scripted</h2>
<p>force_scale 2 (hypothetical-strength actuators). Per seed, 100 episodes, flight_steps 900; PASS needs contact, lateral std &le; 2.73 m, launch 5-20 deg, landed &ge; 90% in det AND stoch. A model passes only if all of seeds 4000/8000/9000 pass; &quot;effectively scripted&quot; = matches the zero-residual script (not a learned drive).</p>
<table><tr><th>Model</th><th>Seed</th><th>Carry (det)</th><th>Lateral std m det / stoch</th><th>Landed</th><th>Club mph</th><th>Noise quick (carry, % clean; 0.005 / 0.01)</th><th>Headline</th></tr>{hypo_html()}</table>
<h2>Gate presets: power tier (gain 1.20, by loft) and stock-motor gates</h2>
<p>Per-seed 100-episode eval_gate rows. Smash = mean ball mph / mean impact club mph; flagged outside 1.30-1.49 (derived thresholds). Stock rows have smash ~1.0 (WARN &lt;1.30): ball barely faster than the club, carry far short of real driver distance. Some backing files are held locally by the Trainer and are not in the repo. Gain-1.28 power rows (smash ~1.6) are inflated and omitted here.</p>
<table><tr><th>Model</th><th>Loft</th><th>Seed</th><th>Club mph</th><th>Ball mph</th><th>Smash</th><th>Smash flag</th><th>Launch deg</th><th>Carry (det)</th><th>Lat std m</th><th>Headline gate</th></tr>{power_presets_html()}</table>
<h2>Launch-monitor validation (analytic ball model vs TrackMan PGA Tour driver average)</h2>
<p>Benchmark: 113 mph club, 167 mph ball, smash 1.48, 10.9&deg; launch, 2686 rpm, 32 yd apex, 38&deg; landing, <b>275 yd carry</b> (TrackMan published PGA Tour averages; USGA Equipment Specifications Research, Table&nbsp;2). Model from those launch conditions: carry {sc['carry_yd']:.0f} yd, total {sc['total_yd']:.0f} yd, apex {sc['apex_yd']:.0f} yd.</p>
<table><tr><th>Check</th><th>Metric</th><th>Model</th><th>Published</th><th>Error</th><th>Result</th></tr>{''.join(vt)}</table>
<p>The simple impact model over-predicts backspin (FAIL rows above are reported, not hidden). One benchmark row only; spot check, not a full calibration.</p>
<h2>Course-mode estimates ({e(crs['label'])})</h2>
<p>Synthetic example course (invented), par {crs['par']}, {crs['total_yards']} yd. Dispersion from the simulator's leaderboard data; putting, chipping, rough and hazard effects are assumed constants. Profile B is a what-if (sim spread scaled to tour-average carry), not an achieved result.</p>
<table><tr><th>Profile</th><th>Mean score</th><th>vs par</th><th>p10-p90</th><th>Fairways</th><th>GIR</th></tr>{ct}</table>
<details><summary>Yardage book (synthetic example course)</summary><table><tr><th>Hole</th><th>Par</th><th>Yards</th><th>Fairway width yd</th></tr>{book}</table></details>
</body></html>"""
    out = os.path.join(ROOT, "docs", "dashboard.html")
    open(out, "w").write(page)
    return out


if __name__ == "__main__":
    print(build())
