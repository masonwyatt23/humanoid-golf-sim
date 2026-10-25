"""V18 tail diag (LOCAL, read-only use of the v4 noise recipe): per seed, the harness-v4 perturbation (joint offsets dq = radians(1.5)*U(-1,1) and vel 0.05*U(-1,1) from rng(seed+0x5EED),
floor mu, ball offset via env reset(seed) with ball_tol .01) and its effect on the stance: lead/trail sole shift right after mj_forward and after 5 control steps of zero residual (PD to the reference address).
Usage: pert_tail_scan.py out.npz seeds_spec(e.g. 10000-19999,8000-8047,7000-7023)"""
import sys, json, numpy as np, mujoco; sys.path.insert(0, '.')
from train.v5_train_j import JEnv
K = {tuple(k.split('|')): v for k, v in json.load(open('results/v5_runs/stageV12X_ref_s1/tuned_keys_flat.json')).items()}
e = JEnv(dt=0.002, seed=999, keys=K, res_scale=0.3, t_down=0.2723206007952667); e.configure(env_v4=True, tee_mode='1.5in', fast_env=True, rsi=(1.0, 0.0, 0.0), ball_tol=0.01)
def soles():
    E = e.env; out = []
    for s in (E.lead, 'left' if E.lead == 'right' else 'right'):
        i = E.m.site(f"{s}_sole_site").id; R = E.d.site_xmat[i].reshape(3, 3); out += list(E.d.site_xpos[i]) + [np.degrees(np.arctan2(R[1, 0], R[0, 0]))]
    return np.array(out)
e.configure(ball_tol=0.0); e.reset(seed=0); S0 = soles(); B0 = e.env.d.qpos[e.env.ball_q:e.env.ball_q + 2].copy()
for _ in range(5): e.step(np.zeros(e.action_space.shape))
S0b = soles(); e.configure(ball_tol=0.01)
seeds = [s for p in sys.argv[2].split(',') for s in range(int(p.split('-')[0]), int(p.split('-')[1]) + 1)]
DQ, DV, MU, BALL, SH0, SH5 = [], [], [], [], [], []
for sd in seeds:
    e.reset(seed=sd); E = e.env; BALL.append(E.d.qpos[E.ball_q:E.ball_q + 2] - B0)
    mu = np.random.default_rng(sd + 0xF41C).uniform(0.7, 1.05); E.m.geom_friction[E.floor, 0] = mu; rg = np.random.default_rng(sd + 0x5EED); n = len(E.qa)
    dq = np.radians(1.5) * rg.uniform(-1, 1, n); dv = 0.05 * rg.uniform(-1, 1, n); E.d.qpos[E.qa] += dq; E.d.qvel[E.da] += dv; mujoco.mj_forward(E.m, E.d)
    SH0.append(soles() - S0)
    for _ in range(5): e.step(np.zeros(e.action_space.shape))
    SH5.append(soles() - S0b); DQ.append(dq); DV.append(dv); MU.append(mu)
np.savez(sys.argv[1], seeds=np.array(seeds), dq=np.array(DQ), dv=np.array(DV), mu=np.array(MU), ball=np.array(BALL), sh0=np.array(SH0), sh5=np.array(SH5), names=np.array(e.env.names), lead=e.env.lead)
print('done', len(seeds))
