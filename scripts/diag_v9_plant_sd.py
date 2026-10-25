"""V9 diag: per-episode lead-foot plant (Evaluator SR.lead_foot_plant_metrics / check_lead_foot_plant, same window top=ref.t_dstart -> impact, address = sample 0,
4 ms segment logging like the v3 worker) and start direction (SR.check_start_direction; face angle vs club path at impact) for a checkpoint on 24 noisy address starts
(joints U(+-1.5 deg), vel U(+-0.05), ball +-1 cm, floor mu U(0.7,1.05); own RNG, so episodes are NOT the Evaluator's exact ones). Usage: diag_v9_plant_sd.py out.json ckpt"""
import sys, json, os, re, numpy as np; sys.path.insert(0, '.')
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.v5_train_j import JEnv
sys.path.insert(0, os.environ.get('EVAL_REPO', '../hgs-v4')); from eval import swing_realism as SR
out, ck = sys.argv[1], sys.argv[2]; a = json.load(open(ck.rsplit('/', 1)[0] + '/args.json')); keys = {tuple(k.split('|')): v for k, v in json.load(open(a['keys'])).items()}
EX = re.search(r"^EX = '([^']*)'", open('scripts/strike_log.py').read(), re.M).group(1).split()
def mk():
    e = JEnv(seed=999, keys=keys, res_scale=a['res_scale'], t_down=a['t_down']); e.configure(**{k: a.get(k) for k in EX}); e.configure(res_mult=json.loads(a['res_mult']) if a.get('res_mult') else None, env_v4=a.get('env_v4'), tee_mode=a.get('tee_mode')); return e
vn = VecNormalize.load(ck + '_vecnorm.pkl', DummyVecEnv([mk])); vn.training = False; vn.norm_reward = False; m = PPO.load(ck, device='cpu'); J = vn.venv.envs[0]; J.rsi = (1.0, 0.0, 0.0)
rows = []
for s in range(7000, 7024):
    J.configure(fr_rand=True, fr_lo=0.7, fr_hi=1.05, init_qn=0.026, init_qvn=0.05, ball_tol=0.01); J.env.friction_rand = False
    o, _ = J.reset(seed=s); e = J.env; T, F, G = [], [], []; orig = e._log_seg
    def seg():
        orig(); fl, fr = e.foot_forces(); sid = e.m.site(f"{e.lead}_sole_site").id; P = e.d.site_xpos[sid]; R = e.d.site_xmat[sid].reshape(3, 3); hx = float(e.m.site_size[sid][0])
        T.append(float(e.d.time)); G.append(fl if e.lead == 'left' else fr); F.append([float(P[0]), float(P[1]), float(P[2]), float((P - hx * R[:, 0])[2]), float((P + hx * R[:, 0])[2]), float(np.arctan2(R[1, 0], R[0, 0]))])
    e._log_seg = seg; e.log_segments = True; done = False; info = {}
    while not done:
        act = m.predict(vn.normalize_obs(o[None]), deterministic=True)[0][0]; o, r, te, tr, info = J.step(act); done = te or tr
    e._log_seg = orig
    c = bool(e.contact) and not getattr(e, 'off_face', False); row = dict(seed=s, contact=c)
    if T:
        T_ = np.array(T); imp = int(np.searchsorted(T_, e.t_contact)) if c else len(T_) - 1; itop = int(np.argmin(np.abs(T_[:imp + 1] - J.ref.t_dstart)))
        fm = SR.lead_foot_plant_metrics(T_, F, G, imp, itop); st = SR.check_lead_foot_plant(fm, 1, "logged")[1]['status'] if fm else None
        row.update(foot_status=st, **({k: fm[k] for k in ('slip_m', 'turn_deg', 'airborne_max_ctrl_steps') if k in fm} if fm else {}))
        # timing of max slip: fraction of top->impact window when slip first exceeds 3 cm (warn)
        if fm:
            xy = np.array(F)[itop:imp + 1, :2] - np.array(F)[0, :2]; d = np.hypot(xy[:, 0], xy[:, 1]); k = np.argmax(d > 0.03) if (d > 0.03).any() else None
            row['slip_at_top_cm'] = float(np.hypot(*(np.array(F)[itop, :2] - np.array(F)[0, :2]))) * 100; row['slip_cross_frac'] = (float(k) / max(len(d) - 1, 1)) if k is not None else None
            row['grf_lead_min_bw'] = float(np.min(G[itop:imp + 1])) / (float(np.sum(e.m.body_mass)) * 9.81)
    if c:
        lat = abs(float(info.get('lateral_carry_m', 0.0))) / max(float(info.get('carry_m_noroll', 0.0)), 1e-3) * 100.0; az = float(info.get('azimuth_deg', 0.0))
        row.update(sd_status=SR.check_start_direction(abs(az), lat)[1]['status'], az=az, lat_per100=lat, face=float(info.get('face_yaw_deg', 0.0)), path=float(info.get('club_path_deg', 0.0)),
                   aoa=float(info.get('aoa_deg', 0.0)), dz_mm=e.ball_hit_info['dz'] * 1e3, dy_mm=e.ball_hit_info['dy'] * 1e3)
    rows.append(row)
json.dump(rows, open(out, 'w'), default=float, indent=0)
C = [r for r in rows if r['contact']]; n = len(rows)
print('contact', len(C), '/', n, '| foot pass', sum(r.get('foot_status') == 'pass' for r in rows), 'warn', sum(r.get('foot_status') == 'warn' for r in rows), 'fail', sum(r.get('foot_status') == 'fail' for r in rows))
for k, lim in (('slip_m', 0.03), ('turn_deg', 12.0), ('airborne_max_ctrl_steps', 1.8)):
    v = [r[k] for r in rows if k in r]; print(f'  {k}: median {np.median(v):.3f} p90 {np.percentile(v, 90):.3f}  over-warn {sum(x > lim for x in v)}/{len(v)}')
v = [r['slip_at_top_cm'] for r in rows if 'slip_at_top_cm' in r]; print('  slip already at top (cm): median %.2f p90 %.2f' % (np.median(v), np.percentile(v, 90)), '| cross 3cm at window frac median', np.median([r['slip_cross_frac'] for r in rows if r.get('slip_cross_frac') is not None] or [np.nan]))
print('  min lead GRF in window (BW) median %.2f' % np.median([r['grf_lead_min_bw'] for r in rows if 'grf_lead_min_bw' in r]))
print('SD pass', sum(r.get('sd_status') == 'pass' for r in C), '/', n, '| az median %.1f |az| p90 %.1f | face %.1f path %.1f face-path %.1f (fails: face %.1f path %.1f)' % (np.median([r['az'] for r in C]), np.percentile([abs(r['az']) for r in C], 90), np.median([r['face'] for r in C]), np.median([r['path'] for r in C]), np.median([r['face'] - r['path'] for r in C]),
      np.median([r['face'] for r in C if r['sd_status'] != 'pass'] or [np.nan]), np.median([r['path'] for r in C if r['sd_status'] != 'pass'] or [np.nan])))
print('  sd fail lat_per100 median', np.median([r['lat_per100'] for r in C if r['sd_status'] != 'pass'] or [np.nan]), 'az', [round(r['az'], 1) for r in C if r['sd_status'] != 'pass'])
