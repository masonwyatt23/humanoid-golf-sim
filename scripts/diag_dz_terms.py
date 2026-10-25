"""V6 diag (1a): which reward terms favour low strikes? For each real contact on varied-start seeds 7000-7023 (v4 env, tee from args), the golfphys
call is recorded and re-run with the SAME club velocity / face normal / dy but dz forced to each value in DZS (counterfactual, golfphys unchanged).
The contact-outcome reward terms of train/v5_train_j.py are recomputed with the run's args.json weights. Usage: diag_dz_terms.py out.json ckpt..."""
import sys, json, numpy as np, os; sys.path.insert(0, '.')
import env.v5_golf_env as G
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.v5_train_j import JEnv
DZS = [0.005, 0.0, -0.005, -0.010, -0.015, -0.020, -0.025]
rec = []; orig = G.shot_from_contact
def hook(*ar, **kw): rec.append((ar, kw)); return orig(*ar, **kw)
G.shot_from_contact = hook
def terms(e, res, dy, dz, fpth):
    sh = res['shot']; sp = sh.spin_rpm; la = res['launch_deg']; sm = res['smash']; carry = sh.carry_m; tot = sh.total_m; dsc = sh.descent_deg; az = res['azimuth_deg']
    off = float(np.hypot(dy, dz)); T = {}
    T['ctr'] = e.ctr_w * max(0.0, 1 - off / e.hit_tol)
    T['spin_cap'] = -e.spin_w * float(np.clip((sp - e.spin_hi) / e.spin_scale, 0.0, e.spin_cap))
    T['edge'] = -e.edge_w * float(abs(dz) > getattr(e, 'edge_dz', 0.0265)) if getattr(e, 'edge_w', 0) else 0.0
    T['loc'] = -e.loc_w * float(np.clip(abs(dz - e.loc_dz) / 0.01 + abs(dy - e.loc_dy) / 0.015, 0.0, 4.0)) if getattr(e, 'loc_w', 0) else 0.0
    T['smash'] = e.smash_w * float(np.clip((sm - 1.1) / 0.2, 0.0, 1.0))
    T['launch'] = e.launch_w * (float(10.0 <= la <= e.launch_hi) + 0.5 * float(np.clip(1.0 - min(abs(la - 10.0), abs(la - e.launch_hi)) / 4.0, 0.0, 1.0)) * float(not (10.0 <= la <= e.launch_hi)))
    T['desc'] = e.desc_w * float(np.clip((dsc - 12.0) / 22.0, 0.0, 1.0)) * float(carry > 15.0)
    T['spin_lo'] = -e.spin_lo_w * float(np.clip((1800.0 - sp) / 1800.0, 0.0, 1.0))
    T['tc'] = -e.tc_w * float(np.clip((tot / max(carry, 1e-3) - 1.22) / 0.1, 0.0, 3.0)) if carry > 15.0 else 0.0
    T['smash2'] = e.smash2_w * float(np.clip((sm - 0.9) / 0.45, 0.0, 1.0)); T['ctr2'] = -e.ctr2_w * min(off / 0.01, 3.0)
    T['aim_az'] = e.aim_w * 0.5 * float(np.clip(1 - abs(az) / 7.0, 0, 1)) - e.aim_w * float(np.clip((abs(az) - 7.0) / 8.0, 0, 1))
    O = dict(spin=sp, launch=la, smash=sm, carry=carry, tc=tot / max(carry, 1e-3), descent=dsc, az=az, ball_mph=res['ball_speed'] / 0.44704)
    return T, O
OUT = {}
for ck in sys.argv[2:]:
    a = json.load(open(ck.rsplit('/', 1)[0] + '/args.json')); keys = {tuple(k.split('|')): v for k, v in json.load(open(a['keys'])).items()}
    import re as _re; EX = _re.search(r"^EX = '([^']*)'", open('scripts/strike_log.py').read(), _re.M).group(1).split() + (['loc_w', 'loc_dy', 'loc_dz', 'edge_w'] if os.environ.get('LOCW') else [])   # same env config as strike_log (harness-like)
    def mk():
        e = JEnv(seed=999, keys=keys, res_scale=a['res_scale'], t_down=a['t_down'])
        for k in EX:
            try: e.configure(**{k: a[k]})
            except Exception: pass
        e.configure(res_mult=json.loads(a['res_mult']) if a.get('res_mult') else None, env_v4=a.get('env_v4'), tee_mode=a.get('tee_mode')); return e
    vn = VecNormalize.load(ck + '_vecnorm.pkl', DummyVecEnv([mk])); vn.training = False; vn.norm_reward = False; m = PPO.load(ck, device='cpu'); e = vn.venv.envs[0]
    e.rsi = (1.0, 0.0, 0.0)   # full swing from address (harness: e.rsi = (1, 0, 0))
    if not hasattr(e, 'hit_tol') or e.hit_tol is None: e.hit_tol = 0.03
    rows = []
    for s in range(7000, 7024):
        e.configure(fr_rand=True, fr_lo=0.7, fr_hi=1.05, init_qn=0.026, init_qvn=0.05, ball_tol=0.01); e.env.friction_rand = False
        e.env.m.geom_friction[e.env.floor, 0] = 1.0; rec.clear(); o, _ = e.reset(seed=s); done = False
        while not done:
            act, _s = m.predict(vn.normalize_obs(o[None]), deterministic=True); o, r, te, tr, info = e.step(act[0]); done = te or tr
        if not rec or getattr(e.env, 'off_face', False): rows.append(dict(seed=s, contact=False)); continue
        ar, kw = rec[0]; dy, dz = ar[2], ar[3]; fpth = float(info.get('face_yaw_deg', 0.0)) - float(info.get('club_path_deg', 0.0))
        cf = {}
        for z in [dz] + DZS:
            T, O = terms(e, orig(ar[0], ar[1], dy, z, **kw), dy, z, fpth); cf['actual' if z == dz and 'actual' not in cf else '%+.0f' % (z * 1e3)] = dict(T=T, O=O, sum=sum(T.values()))
        rows.append(dict(seed=s, contact=True, dz_mm=dz * 1e3, dy_mm=dy * 1e3, club_mph=float(np.linalg.norm(ar[0])) / 0.44704, cf=cf))
    OUT[ck] = rows
    c = [r for r in rows if r['contact']]
    print('CK', ck, 'contacts', len(c), 'median dz %.1f dy %.1f club %.1f' % tuple(np.median([[r['dz_mm'], r['dy_mm'], r['club_mph']] for r in c], 0)))
    labs = ['%+.0f' % (z * 1e3) for z in DZS]
    for t in list(c[0]['cf']['actual']['T']) + ['SUM']:
        v = [np.mean([(r['cf'][l]['sum'] if t == 'SUM' else r['cf'][l]['T'][t]) for r in c]) for l in labs]; print('  %-9s' % t, ' '.join('%7.2f' % x for x in v), '  (dz mm:', ' '.join(labs), ')')
    for o in c[0]['cf']['actual']['O']:
        print('  O %-8s' % o, ' '.join('%8.2f' % np.mean([r['cf'][l]['O'][o] for r in c]) for l in labs))
json.dump(OUT, open(sys.argv[1], 'w'), default=float)
