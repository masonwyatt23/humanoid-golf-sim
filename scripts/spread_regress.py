"""V18 spread diag regression (LOCAL): per-episode strike dy/dz vs perturbation groups. Fit ridge on seeds 8000-8047 (non-gating), test R2 on GATING seeds 7000-7023; also LOO R2 on pooled 72.
Usage: spread_regress.py <run> ..."""
import csv, json, sys, numpy as np
G = dict(legs=list(range(0, 12)), trunk=[12, 13, 14], arms=[15, 16, 17, 18, 22, 23, 24, 25], wrists=[19, 20, 21, 26, 27, 28])
def load(f):
    R = [r for r in csv.DictReader(open(f)) if r['case'] == 'perturbed' and r['contact'] == 'True' and r['dy_mm'] != '']
    X = {}; dq = np.array([json.loads(r['dq_json']) for r in R]); dqd = np.array([json.loads(r['dqd_json']) for r in R])
    for g, ix in G.items(): X['q_' + g] = dq[:, ix]
    X['qd_all'] = dqd; X['ball_x'] = np.array([[float(r['ball_dx_mm'])] for r in R]); X['ball_y'] = np.array([[float(r['ball_dy_mm'])] for r in R]); X['mu'] = np.array([[float(r['floor_mu'])] for r in R])
    X['q_all'] = dq; X['ALL'] = np.hstack([dq, dqd, X['ball_x'], X['ball_y'], X['mu']])
    return X, np.array([float(r['dy_mm']) for r in R]), np.array([float(r['y_high_mm']) for r in R])
def fit(A, y, lam):
    m, s = A.mean(0), A.std(0) + 1e-12; Z = (A - m) / s; w = np.linalg.solve(Z.T @ Z + lam * np.eye(Z.shape[1]), Z.T @ (y - y.mean())); return lambda B: ((B - m) / s) @ w + y.mean()
def r2(y, p): return 1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum()
def loo(A, y, lam):
    p = np.array([fit(np.delete(A, i, 0), np.delete(y, i), lam)(A[i:i + 1])[0] for i in range(len(y))]); return r2(y, p)
for run in sys.argv[1:]:
    Xt, yt, zt = load(f'results/v10_diag/spread_{run}_8000-8047.csv'); Xg, yg, zg = load(f'results/v10_diag/spread_{run}_7000-7023.csv')
    print(f'\n{run}: n fit(8000-8047)={len(yt)} n gating={len(yg)}; dy sd {np.concatenate([yt,yg]).std():.1f} mm, dz sd {np.concatenate([zt,zg]).std():.1f} mm, heel(<-8) {(np.concatenate([yt,yg])<-8).mean():.2f} toe(>+8) {(np.concatenate([yt,yg])>8).mean():.2f}')
    print(f"{'group':8s} {'k':>3s} | dy: LOO72  heldout-gating | dz: LOO72  heldout-gating")
    for g in Xt:
        k = Xt[g].shape[1]; lam = 1.0 if k < 4 else 5.0; A = np.vstack([Xt[g], Xg[g]])
        print(f"{g:8s} {k:3d} | {loo(A, np.concatenate([yt, yg]), lam):6.2f} {r2(yg, fit(Xt[g], yt, lam)(Xg[g])):8.2f}      | {loo(A, np.concatenate([zt, zg]), lam):6.2f} {r2(zg, fit(Xt[g], zt, lam)(Xg[g])):8.2f}")
    A = np.vstack([Xt['q_all'], Xg['q_all']]); y = np.concatenate([yt, yg]); Z = (A - A.mean(0)) / A.std(0); c = [np.corrcoef(Z[:, j], y)[0, 1] for j in range(29)]
    names = 'Lhp Lhr Lhy Lkn Lap Lar Rhp Rhr Rhy Rkn Rap Rar Wy Wr Wp Lsp Lsr Lsy Lel Lwr Lwp Lwy Rsp Rsr Rsy Rel Rwr Rwp Rwy'.split()
    print('top single-joint qpos corr with dy:', ', '.join(f'{names[j]} {c[j]:+.2f}' for j in np.argsort(-np.abs(c))[:6]))
