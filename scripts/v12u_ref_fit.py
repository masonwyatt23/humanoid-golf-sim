"""V12U refit: V10 objective + harness-style start direction on noisy starts.
- h_sd2 = on_face & |az|<=7 & lateral per 100 yd <= 13.5 (golfphys lateral_carry_m / carry_m_noroll from env info, same formula as the harness)
- heel = on_face & dy < -10 mm (V13h 50k start-dir non-passes: heel strikes dy -14..-41 mm)
Env weights: V12U_SD2_W (penalty per 0.05 below 0.92), V12U_HEEL_W (penalty per 0.05 heel rate), V12U_LAT_W (per yd/100 of median lateral above 9).
Draws: v8's score loops pid 0..NS-1 and ignores V7_PID0; here pid -> pid + V12U_PID0 so fit and holdout draws are disjoint.
Holdout: python -m scripts.v12u_ref_fit --holdout KEYS.json (uses V12U_PID0 for the held-out set, prints summary JSON).
V12Z (default off: V12Z_TAIL_N=0 leaves the objective unchanged): + V12Z_TAIL_N harness-v4-style starts on stance-shift TAIL seeds from V12Z_TAIL_POOL
(default results/v10_diag/tail/tail_pool_20000_99999.npy; non-gating) taken at pool[V12Z_TAIL_OFF : OFF+N] (fit and held-out use disjoint offsets).
Noise as the v4 worker: joints radians(1.5)*U(-1,1), vel .05*U(-1,1) from rng(s+0x5EED), floor mu U(.7,1.05) from rng(s+0xF41C); ball offset +-1 cm from rng(s) (approximation of the worker's env-rng draw).
Penalty V12Z_TAIL_W x [mean over tail starts of clip((turn-11)/1,0,3) + 3*airborne(>=2 ctrl steps) + 3*no-contact] (zero-residual reference rollouts; proxies, not harness grades)."""
import os, sys, json, numpy as np
import scripts.v10_ref_fit as T
V = T.V; F = T.F
P0 = int(os.environ.get('V12U_PID0', '0')); _R = []
_one10 = V.one
def one(e, ref, pid):
    S = {}; st = e.step
    def step(a):
        o = st(a); i = o[4]
        if 'face_yaw_deg' in i and 'fy' not in S: S['fy'] = float(i['face_yaw_deg']) * (1.0 if str(getattr(e, 'handed', 'R')).upper().startswith('R') else -1.0)   # world face (+ left), = Evaluator impact_face_world_deg (calibrated 13:55 vs official V16y/V17f/V18d); S['az'] = float(i.get('azimuth_deg', 0.0) or 0.0)
        if 'lateral_carry_m' in i and 'lat' not in S and float(i.get('carry_m_noroll', 0) or 0) > 1.0: S['lat'] = 100.0 * abs(float(i['lateral_carry_m'])) / float(i['carry_m_noroll'])
        return o
    e.step = step
    try: r = _one10(e, ref, None if pid is None else pid + P0)
    finally: e.__dict__.pop('step', None)
    r['lat100'] = S.get('lat'); r['fy'] = S.get('fy'); _R.append(r); return r
V.one = one
_s10 = V.score
def score(x):
    _R.clear(); s, d = _s10(x); R = _R[1:]
    if not R: return s, d
    on = [r for r in R if r.get('on_face')]
    d['h_sd2'] = float(np.mean([bool(r.get('on_face')) and abs(r.get('az') or 99) <= 7.0 and (r.get('lat100') if r.get('lat100') is not None else 99) <= 13.5 for r in R]))
    d['heel'] = float(np.mean([bool(r.get('on_face')) and (r.get('dy') or 0) / 0.001 < -10.0 for r in R]))
    d['lat_med'] = float(np.median([r['lat100'] for r in on if r.get('lat100') is not None])) if on else None
    d['lat_nom'] = _R[0].get('lat100')
    d['dy2'] = float(np.mean([bool(r.get('on_face')) and abs((r.get('dy') or 0) / 0.001) <= 8.0 for r in R]))   # V12V: two-sided |dy| <= 8 mm rate
    d['nom_dy_abs'] = abs((_R[0].get('dy') or 0.05) / 0.001)
    dp = [abs(r['az'] - 0.85 * r['fy']) for r in on if r.get('fy') is not None and r.get('az') is not None]
    d['dplane'] = float(np.mean([x <= 2.0 for x in dp])) if dp else 0.0; d['dplane_med'] = float(np.median(dp)) if dp else None   # V12V: D-plane proxy |az - 0.85 face| <= 2 deg
    d['nom_dz_mm'] = (_R[0].get('dz') or -0.05) / 0.001; wz = float(os.environ.get('V12U_DZ_W', '0'))   # V12X: nominal strike-height term (target 0..+3 mm)
    s -= wz * min(max(-d['nom_dz_mm'], d['nom_dz_mm'] - 3.0, 0.0) / 2.0, 6)
    n0 = _R[0]; d['dplane_nom'] = abs(n0['az'] - 0.85 * n0['fy']) if n0.get('fy') is not None and n0.get('az') is not None else None   # Evaluator v5/dplane = nominal shot only (official episodes seeds 4000-4023 are identical, std 0): |start - .85*face_world| <= 2
    d['heel8'] = float(np.mean([bool(r.get('on_face')) and (r.get('dy') or 0) / 0.001 < -8.0 for r in R]))   # V12Y: heel tail (D-plane pulls are heel strikes, dy <= -15 mm; passes >= -8.4)
    wh8 = float(os.environ.get('V12U_HEEL8_W', '0')); wdr = float(os.environ.get('V12U_DPLR_W', '0'))
    s -= wh8 * d['heel8'] / 0.05 + wdr * max(0.85 - d['dplane'], 0) / 0.05   # V12Y: noisy-start D-plane pass rate (world face, |az - .85 fw| <= 2)
    w4 = float(os.environ.get('V12U_DY2_W', '0')); w5 = float(os.environ.get('V12U_DPL_W', '0'))
    s -= w4 * (max(0.85 - d['dy2'], 0) / 0.05 + min(max(d['nom_dy_abs'] - 8.0, 0) / 2.0, 6)) + w5 * min(max((d['dplane_nom'] if d['dplane_nom'] is not None else 9.0) - 1.5, 0) / 0.5, 6)
    w1 = float(os.environ.get('V12U_SD2_W', '0')); w2 = float(os.environ.get('V12U_HEEL_W', '0')); w3 = float(os.environ.get('V12U_LAT_W', '0'))
    s -= w1 * max(0.92 - d['h_sd2'], 0) / 0.05 + w2 * d['heel'] / 0.05 + w3 * max((d['lat_med'] or 20) - 9.0, 0)
    return s, d
TN = int(os.environ.get('V12Z_TAIL_N', '0'))
def tail_eval(x):
    import mujoco
    from env.v5_ref import SwingRef
    pool = np.load(os.environ.get('V12Z_TAIL_POOL', 'results/v10_diag/tail/tail_pool_20000_99999.npy')); off = int(os.environ.get('V12Z_TAIL_OFF', '0'))
    e = V._E; ref = SwingRef(e.names, e.q_addr, e.lead, e.jlo, e.jhi, keys=V.build(x), t_down=V.TD); out = []
    for sd in pool[off:off + TN]:
        sd = int(sd); r0 = e.reset; st = e.step; A = dict(run=0, mx=0)
        def reset(*a, **kw):
            o = r0(*a, **kw); n = len(e.qa); g = np.random.default_rng(sd + 0x5EED)
            e.d.qpos[e.qa] += np.radians(1.5) * g.uniform(-1, 1, n); e.d.qvel[e.da] += 0.05 * g.uniform(-1, 1, n)
            e.m.geom_friction[e.floor, 0] = np.random.default_rng(sd + 0xF41C).uniform(0.7, 1.05); e.tee[:2] += np.random.default_rng(sd).uniform(-0.01, 0.01, 2); mujoco.mj_forward(e.m, e.d); return o
        def step(a):
            o = st(a)
            if e.d.time >= ref.t_dstart and not e.contact:
                fl, fr = e.foot_forces(); g_ = fl if e.lead == 'left' else fr; A['run'] = A['run'] + 1 if g_ <= 1.0 else 0; A['mx'] = max(A['mx'], A['run'])
            return o
        e.reset = reset; e.step = step
        try: r = V.one(e, ref, None)
        except Exception as ex: r = dict(on_face=False, err=str(ex)[:60])
        finally: e.__dict__.pop('reset', None); e.__dict__.pop('step', None); e.m.geom_friction[e.floor, 0] = 1.0
        r['air'] = A['mx']; out.append(r)
    on = [r.get('on_face', False) for r in out]; tn = np.array([r.get('h_turn', 30.0) for r in out]); sl = np.array([r.get('h_slip', 0.1) for r in out]); air = np.array([r['air'] for r in out])
    d = dict(tail_n=len(out), tail_contact=float(np.mean(on)), tail_turn_ok=float(np.mean(tn <= 12.0)), tail_turn_med=float(np.median(tn)), tail_air_ok=float(np.mean(air < 2)), tail_slip_ok=float(np.mean(sl <= 0.03)),
             tail_plant_pass=float(np.mean([o and t <= 12.0 and a < 2 and s_ <= 0.03 for o, t, a, s_ in zip(on, tn, air, sl)])),
             tail_heel8=float(np.mean([bool(r.get('on_face')) and (r.get('dy') or 0) / 0.001 < -8.0 for r in out])))
    pen = float(np.mean(np.clip(tn - 11.0, 0, 3))) + 3.0 * float(np.mean(air >= 2)) + 3.0 * (1.0 - d['tail_contact'])
    return pen, d
if TN > 0:
    _s12 = score
    def score(x):
        s, d = _s12(x)
        if d.get('err'): return s, d
        pen, dt = tail_eval(x); d.update(dt); d['tail_pen'] = pen
        return s - float(os.environ.get('V12Z_TAIL_W', '0')) * pen, d
F.score = score; V.score = score
if __name__ == '__main__':
    if '--holdout' in sys.argv:
        k = sys.argv[sys.argv.index('--holdout') + 1]; d = json.load(open(k))
        V.KEYS = [tuple(q.split('|')) for q in d]; V.BASE = [float(v) for v in d.values()]
        sc, summ = score(np.zeros(len(V.KEYS)))
        print(json.dumps(dict(keys=k, pid0=P0, ns=V.NS, score=sc, summary=summ)))
    else:
        import runpy; runpy.run_module('scripts.v7_ref_fit', run_name='__main__', alter_sys=False)
