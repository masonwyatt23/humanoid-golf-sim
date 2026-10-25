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
ck=sys.argv[1]
a = json.load(open(ck.rsplit('/', 1)[0] + '/args.json')); keys = {tuple(k.split('|')): v for k, v in json.load(open(a['keys'])).items()}
import re as _re; EX = _re.search(r"^EX = '([^']*)'", open('scripts/strike_log.py').read(), _re.M).group(1).split()
def mk():
    e = JEnv(seed=999, keys=keys, res_scale=a['res_scale'], t_down=a['t_down'])
    for k in EX:
        try: e.configure(**{k: a[k]})
        except Exception: pass
    e.configure(res_mult=json.loads(a['res_mult']), env_v4=a.get('env_v4'), tee_mode=a.get('tee_mode'), dz_lin_w=45, dz_tgt=0.0015); return e
vn = VecNormalize.load(ck + '_vecnorm.pkl', DummyVecEnv([mk])); vn.training = False; m = PPO.load(ck, device='cpu'); e = vn.venv.envs[0]; e.rsi=(1.0,0.0,0.0)
for s in range(7000,7006):
    rec.clear(); o,_=e.reset(seed=s); done=False; dzs=[]
    while not done:
        act,_=m.predict(vn.normalize_obs(o[None]),deterministic=True); o,r,te,tr,info=e.step(act[0]); done=te or tr
        if 'dz' in info and info['dz'] is not None: dzs.append(round(float(info['dz'])*1000,2))
    print(s,'golfphys dz mm', rec and round(rec[0][0][3]*1000,2), 'info dz seq', sorted(set(dzs))[:4])
