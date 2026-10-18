"""Open-loop test of the Stage J joint reference (zero residual): balance, contact, impact speed. Usage: python -m scripts.v5_ref_openloop [--keys file.json] [--tdown 0.27]"""
import argparse, json, sys, numpy as np
from env.v5_golf_env import V5GolfEnv
from env.v5_ref import SwingRef, TUNED_KEYS

def make_env(dt=0.002, gate=0.25, arm=0.6):
    e = V5GolfEnv(club_len=1.15, dt=dt, arm_dist=arm, friction_rand=False); e.strike_gate_nx = gate; e.log_segments = True; return e

def keys_from_vec(x): return {k: float(v) for k, v in zip(TUNED_KEYS, x)}

def run_open_loop(e, ref, res_fn=None, max_t=None):
    e.reset(seed=0); home = e.q_addr.copy(); e.act_scale[:] = 0.0; t = 0.0; zmin = 9.0; tilt = 0.0; xfmax = 0.0; gmax = 0.0; bw = float(np.sum(e.m.body_mass)) * 9.81; info = {}; term = False
    max_t = max_t or ref.t_end + 0.1
    while t < max_t and not term:
        e.q_addr = ref.q(t); _, _, term, tr, info = e.step(np.zeros(len(home))); t += 0.02; zmin = min(zmin, float(e.d.qpos[2]))
        if not e.contact: xfmax = max(xfmax, abs(float(e.log['xfactor_deg'][-1])) if len(e.log['xfactor_deg']) else 0.0)
        if t > 0.2 and not e.contact:
            fl, fr = e.foot_forces(); gmax = max(gmax, (fl if e.lead == 'left' else fr) / bw)
        tilt = max(tilt, float(np.degrees(np.arccos(np.clip(e.d.xmat[e.pel].reshape(3, 3)[2, 2], -1, 1)))))
        if tr: break
    e.q_addr = home
    return dict(contact=bool(e.contact), foul=bool(e.foul), fell=bool(info.get("fell", False)), mph=float(info.get("club_speed_mph", 0.0)), carry=float(info.get("carry_m_noroll", 0.0)),
                launch=float(info.get("launch_deg", 0.0)), min_pelvis_z=zmin, max_tilt_deg=tilt, armed=bool(e.armed), xf_max_deg=xfmax, lead_grf_bw=gmax, t_end=t, min_head_ball=float(e.min_dist), peak_head_mph=None)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--keys", default=None); ap.add_argument("--tdown", type=float, default=0.27); ap.add_argument("--k", type=float, default=1.6); ap.add_argument("--out", default=None)
    a = ap.parse_args(); e = make_env()
    keys = {tuple(k.split("|")): v for k, v in json.load(open(a.keys)).items()} if a.keys else None
    ref = SwingRef(e.names, e.q_addr, e.lead, e.jlo, e.jhi, keys=keys, t_down=a.tdown, k_ease=a.k)
    r = run_open_loop(e, ref); print(json.dumps(r, indent=1))
    if a.out: json.dump(r, open(a.out, "w"), indent=1)
