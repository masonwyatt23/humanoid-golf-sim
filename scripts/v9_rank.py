"""Table of harness v4 (local 915348c) 1.5in rows for run prefixes; strike numbers from the harness gate (mine/strike_dz_info / strike_dy_info).
Usage: v9_rank.py V9a V9b ...  -> prints table, then BEST (real nominal contact; min fails, then robustness min-rate, then t/c p90)."""
import json, glob, sys
H = 'results/v5_runs/stageJ_harness'; rows = []
for p in sys.argv[1:]:
    for f in glob.glob(f'{H}/{p}_s*_*_v3_tee15in_v4h_v4.json'):
        n = f.split('/')[-1].split('_v3_')[0]; d = json.load(open(f)); c = d['checks']; r = c['mine/robustness']['values']; s = r.get('shot', {})
        g = lambda k, q: (s.get(k) or {}).get(q); z = c.get('mine/strike_dz_info', {}).get('values') or {}; y = c.get('mine/strike_dy_info', {}).get('values') or {}
        rows.append(dict(n=n, step=int(n.split('_')[-1]), p=d['checks_passed'], w=d['n_warn'], f=d['n_fail'], nom=d.get('true_contact', 0) > 0, C=r['contact_frac'], SD=r['start_direction_pass_frac'], F=r['lead_foot_plant_pass_frac'],
                         sp=g('spin_rpm', 'p90'), tc=g('total_over_carry', 'p90'), ndz=(z.get('deterministic') or {}).get('median'), rdz=(z.get('robustness') or {}).get('median'), rdy=(y.get('robustness') or {}).get('median'), rn=(z.get('robustness') or {}).get('n'),
                         fails=','.join(k.split('/')[-1] for k, v in c.items() if v['status'] == 'fail')))
rows.sort(key=lambda r: (r['n'].split('_')[0], r['step']))
fm = lambda v, k=1: '-' if v is None else f'{v:.{k}f}'
for r in rows: print(f"{r['n']:18s} {r['p']}/{r['w']}/{r['f']} nom={'Y' if r['nom'] else 'N'} {r['C']:.2f}/{r['SD']:.2f}/{r['F']:.2f} sp90 {fm(r['sp'],0)} tc90 {fm(r['tc'],2)} ndz {fm(r['ndz'])} rdz/dy {fm(r['rdz'])}/{fm(r['rdy'])} (n {r['rn']}) F: {r['fails']}")
ok = [r for r in rows if r['nom']]
if ok:
    b = min(ok, key=lambda r: (r['f'], -min(r['C'] / .95, r['SD'] / .9, r['F'] / .9), r['tc'] or 9)); print('BEST', b['n'], f"{b['p']}/{b['w']}/{b['f']}", f"{b['C']:.2f}/{b['SD']:.2f}/{b['F']:.2f}", 'tc90', fm(b['tc'], 2))
