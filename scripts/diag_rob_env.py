"""V6 diag (1b): varied-start robustness of a policy (or the open-loop reference with --openloop) across env variants, seeds 7000-7023,
friction U(0.7,1.05), init_qn 0.026 / init_qvn 0.05, ball +-1 cm, full swing from address (rsi 1,0,0). Start direction = Evaluator SR.check_start_direction
(|az|, lateral/100); foot = PROXY of SR.check_lead_foot_plant on whole-episode JEnv foot stats (pass = slip < 0.6*25% sole, turn < 12 deg, airborne < 1.8 ctrl steps).
Usage: diag_rob_env.py out.json ckpt [--openloop] [--keys path]"""
import sys, json, os, numpy as np; sys.path.insert(0, '.')
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.v5_train_j import JEnv
sys.path.insert(0, os.environ.get('EVAL_REPO', '../hgs-v4')); from eval import swing_realism as SR
out, ck = sys.argv[1], sys.argv[2]; OL = '--openloop' in sys.argv; KP = sys.argv[sys.argv.index('--keys') + 1] if '--keys' in sys.argv else None
a = json.load(open(ck.rsplit('/', 1)[0] + '/args.json')); kp = KP or a['keys']; keys = {tuple(k.split('|')): v for k, v in json.load(open(kp)).items()}
import re; EX = re.search(r"^EX = '([^']*)'", open('scripts/strike_log.py').read(), re.M).group(1).split()
VARS = dict(box={}, box_face54=dict(face_h=0.054), v5_realistic=dict(head='realistic'), v4=dict(env_v4=True))
SLIP = 0.6 * SR.FOOT_SLIP_FAIL_FRAC * SR.FOOT_LENGTH_M; TURN = SR.FOOT_WARN_FRAC * SR.FOOT_TURN_FAIL_DEG; AIR = SR.FOOT_WARN_FRAC * SR.FOOT_AIR_CTRL_STEPS
R = {}
for vn_, cfg in VARS.items():
    def mk():
        e = JEnv(seed=999, keys=keys, res_scale=a['res_scale'], t_down=a['t_down']); e.configure(**{k: a.get(k) for k in EX})
        e.configure(res_mult=json.loads(a['res_mult']) if a.get('res_mult') else None); e.configure(**cfg); return e
    vn = VecNormalize.load(ck + '_vecnorm.pkl', DummyVecEnv([mk])); vn.training = False; vn.norm_reward = False; m = PPO.load(ck, device='cpu'); e = vn.venv.envs[0]; e.rsi = (1.0, 0.0, 0.0)
    rows = []
    for s in range(7000, 7024):
        e.configure(fr_rand=True, fr_lo=0.7, fr_hi=1.05, init_qn=0.026, init_qvn=0.05, ball_tol=0.01); e.env.friction_rand = False
        o, _ = e.reset(seed=s); done = False; zero = np.zeros(e.action_space.shape)
        while not done:
            act = zero if OL else m.predict(vn.normalize_obs(o[None]), deterministic=True)[0][0]
            o, r, te, tr, info = e.step(act); done = te or tr
        ep = info.get('ep', {}); c = bool(ep.get('contact')) and not getattr(e.env, 'off_face', False)
        sd = None
        if c and float(info.get('carry_m_noroll', 0) or 0) > 0:
            lat = abs(float(info.get('lateral_carry_m', 0.0))) / float(info['carry_m_noroll']) * 100.0; sd = SR.check_start_direction(abs(float(info.get('azimuth_deg', 0.0))), lat)[1]['status']
        foot = (ep.get('foot_slip', 9) < SLIP and ep.get('foot_turn', 99) < TURN and ep.get('foot_air', 99) < AIR)
        rows.append(dict(seed=s, contact=c, sd=sd, foot=bool(foot), slip_cm=100 * ep.get('foot_slip', np.nan), turn=ep.get('foot_turn'), air=ep.get('foot_air'),
                         dz=(e.env.ball_hit_info or {}).get('dz') if c else None, club_mph=ep.get('club_mph')))
    n = len(rows); R[vn_] = dict(contact=sum(r['contact'] for r in rows) / n, sd=sum(r['sd'] == 'pass' for r in rows) / n, foot=sum(r['foot'] and r['contact'] for r in rows) / n,
                                foot_any=sum(r['foot'] for r in rows) / n, slip_cm_med=float(np.nanmedian([r['slip_cm'] for r in rows])), turn_med=float(np.nanmedian([r['turn'] for r in rows])),
                                air_med=float(np.nanmedian([r['air'] for r in rows])), dz_med_mm=(float(np.median([r['dz'] for r in rows if r['dz'] is not None])) * 1e3 if any(r['dz'] is not None for r in rows) else None), rows=rows)
    print(('OPENLOOP ' if OL else '') + ck.split('/')[-2], vn_, ' '.join(f'{k} {v:.2f}' if isinstance(v, float) else f'{k} {v}' for k, v in R[vn_].items() if k != 'rows'), flush=True)
json.dump(dict(ck=ck, openloop=OL, keys=kp, thresholds=dict(slip_m=SLIP, turn_deg=TURN, air_steps=AIR), variants=R), open(out, 'w'), default=float)
