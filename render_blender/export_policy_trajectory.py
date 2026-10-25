"""Export a TRAINED-POLICY rollout (not the scripted swing) for build_and_render.py (same npz format as export_trajectory.py).
    python -m render_blender.export_policy_trajectory --model imit20_fs1_q23_dart_s51 --out <local-path>/policy_stock.npz [--seeds 4000 8]
    ... --model imit18_power_dart_s51 --override '{"impact_gain": 1.2}' --gate-json results/imit_private/gain120/gate_imit18_power_dart_s51.json --out ...
Env kwargs = the gate's: env_kwargs_full from results/<model>.json (+ _env residual, track_weight 0, track_set None) + optional --override (same as GATE_OVERRIDE).
Rollout: DETERMINISTIC policy, N consecutive seeds starting at --seed0; the clip shows the MEDIAN-carry swing among true-contact episodes (not best-of-N). The seed and every candidate's carry are written to the json.
The numbers in the json (club mph, carry, launch) are from that ONE rolled-out episode; the gate means (from --gate-json) are stored separately under 'gate_means' and shown as a caption.
The policy is behaviour-cloned from the scripted v3 swing ('script-distilled'); this is not a swing learned independently and not learned from any person."""
import argparse, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--seed0", type=int, default=4000); ap.add_argument("--n", type=int, default=8, help="candidate seeds seed0..seed0+n-1")
    ap.add_argument("--override", default="", help="JSON env-kwarg override (as GATE_OVERRIDE)"); ap.add_argument("--gate-json", default="", help="gate JSON whose policy_det means are stored as gate_means (same override)")
    a = ap.parse_args()
    import mujoco
    from stable_baselines3 import PPO
    from eval.env_factory import make_env
    from eval.flight_tracker import FlightTracker
    J = json.loads((ROOT / "results" / f"{a.model}.json").read_text())
    kw = dict(J["env_kwargs_full"], _env="residual", track_weight=0.0, track_set=None); kw["residual_scale"] = list(kw["residual_scale"])
    if a.override: kw.update(json.loads(a.override))
    env = make_env(kw); pol = PPO.load(str(ROOT / "models" / a.model))
    m = env.model; rec = {}; n = [0]; orig = mujoco.mj_step
    def wrapped(mm, d, *args, **k):
        orig(mm, d, *args, **k); n[0] += 1
        if n[0] % 10 == 0 and rec.get("on"):
            rec["t"].append(d.time); rec["xpos"].append(d.xpos.copy()); rec["xquat"].append(d.xquat.copy()); rec["ball"].append(d.xpos[env._ball_id].copy())
    mujoco.mj_step = wrapped
    cands = []
    def rollout(seed, record):
        ft = FlightTracker(env).install()
        rec.update(t=[], xpos=[], xquat=[], ball=[], on=record)
        try:
            obs, _ = env.reset(seed=seed); ft.reset(); n[0] = 0; rec.update(t=[], xpos=[], xquat=[], ball=[]); done = False; info = {}
            while not done:
                obs, _, te, tr, info = env.step(pol.predict(obs, deterministic=True)[0]); ft.step(); done = te or tr
            s = ft.summary(info); sepv = ft.v_sep if ft.v_sep is not None else ft._last_v
        finally:
            ft.close()
        return s, sepv
    try:
        for i in range(a.n):
            s, _ = rollout(a.seed0 + i, False); cands.append((a.seed0 + i, float(s["carry"]), bool(s["true_contact"])))
            print("cand seed", a.seed0 + i, "carry %.1f" % s["carry"], "contact", s["true_contact"], flush=True)
        good = sorted([c for c in cands if c[2] and c[1] > 0], key=lambda c: c[1]); seed = good[(len(good) - 1) // 2][0]
        s, sepv = rollout(seed, True)   # deterministic env => identical to the candidate run; recorded now
    finally:
        mujoco.mj_step = orig
    names = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, i) for i in range(m.nbody)]
    t = np.array(rec["t"]); ball = np.array(rec["ball"])
    disp = np.linalg.norm(ball - ball[0], axis=1); ii = int(np.argmax(disp > 0.005)) if (disp > 0.005).any() else -1
    out = dict(t=t, xpos=np.array(rec["xpos"]), xquat=np.array(rec["xquat"]), ball=ball, body_names=np.array(names), impact_idx=ii)
    gid = m.geom("club_head").id
    out["club_head_geom_offset"] = m.geom_pos[gid]; out["club_head_body"] = names[m.geom_bodyid[gid]]; out["club_shaft_fromto"] = np.array([0, 0, 0, 0, 0, -1.1])
    out["v_sep"] = np.array(sepv if sepv is not None else [np.nan] * 3)
    np.savez(a.out, **out)
    ex = {k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in s.items() if isinstance(v, (int, float, bool, np.floating))}
    gm = None
    if a.gate_json:
        g = json.loads(Path(a.gate_json).read_text())["policy_det"]
        gm = {k: g.get(k) for k in ("mean_carry", "mean_carry_yd", "peak_club_mph_mean", "launch_elev_mean_deg", "lateral_std", "contact_rate")}; gm["gate_seeds_note"] = "mean over 100 episodes of " + Path(a.gate_json).name + " (seed in file)"
    Path(a.out).with_suffix(".json").write_text(json.dumps(dict(model=a.model, rollout_seed=seed, candidate_seeds=cands, selection="median carry among true-contact deterministic rollouts of seeds %d..%d" % (a.seed0, a.seed0 + a.n - 1),
        override=a.override or None, env_force_scale=kw.get("force_scale"), env_impact_gain=kw.get("impact_gain") or (kw.get("impact_model") or {}).get("gain"), summary=ex, samples=len(t), impact_idx=ii, gate_means=gm, v_sep=out["v_sep"].tolist()), indent=1, default=float))
    print("saved", a.out, len(t), "samples; impact idx", ii, "seed", seed, {k: ex.get(k) for k in ("impact_club_speed", "peak_ball_speed", "carry", "carry_yd", "launch_elev_deg", "true_contact")})
main()
