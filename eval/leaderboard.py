"""
Leaderboard over every checkpoint in models/.   python -m eval.leaderboard [--episodes 50] [--seed 4000] [--force]

* Identical files (same md5) are evaluated once; all names are listed.
* Each model uses its own training config: results/train_<name>.json (any alias of that md5),
  else KNOWN_CONFIGS below (models with no JSON; config taken from the training command line).
* Caching: results/leaderboard_cache.json keyed by md5 + env fingerprint (md5 of
  env/humanoid_golf_env.py + env/models/*.xml). Evaluated md5s are skipped unless the env changed or --force.
* results/leaderboard_history.json keeps every evaluation ever made (incl. seeded pre-v2-physics results).
* Contact regression: a (checkpoint, mode) whose contact rate is lower than the best contact rate of
  any EARLIER-trained checkpoint (by model file mtime / history order) in the same mode is flagged.
* DTW: mean joint-trajectory DTW (rad) vs every data/references/*_swing.npz (incl. mason_swing.npz if present).
  Non-Scott reference columns are pure reference-style distances.
"""
import argparse, hashlib, json, math, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
ENV_KEYS = ["curriculum", "pin_torso", "address_pose", "torque_scale", "randomize_reset", "forward_reward",
            "carry_reward", "ball_damping", "action_smoothing", "shoulder_range_deg"]
# no results/train_*.json exist for these; configs from the launch command lines seen in `ps` / logs
KNOWN_CONFIGS = {
    "ppo_scott_baseline": dict(steps=30000, env={}, source="launch cmd `--timesteps 30000 --tag _baseline` (default env); no train JSON"),
    "ppo_scott_curr": dict(steps=30000, env=dict(curriculum=True, pin_torso=True, address_pose="fixed", torque_scale=3.0),
                           source="launch cmd `--curriculum --pin_torso --address_pose fixed --torque_scale 3 --tag _curr`; no train JSON"),
}
# earlier evaluations (my own runs, seeds 3000-3049, 50 eps) under the PRE-v2 physics env
SEED_HISTORY = [
    dict(md5="79f83863b227a1267fbdcab08642473f", names=["ppo_scott(30k, old)", "ppo_scott_prev_backup"], steps=30000, order=1,
         env_fingerprint="pre-v2-physics", modes={"deterministic": {"contact_rate": 1.0, "mean_distance": 1.92}, "stochastic": {"contact_rate": 0.18, "mean_distance": 2.65}}),
    dict(md5="90b069adbd3d5c4693692032d49806a3", names=["ppo_scott_final2", "ppo_scott(60k)"], steps=60000, order=2,
         env_fingerprint="pre-v2-physics", modes={"deterministic": {"contact_rate": 0.98, "mean_distance": 2.71}, "stochastic": {"contact_rate": 0.52, "mean_distance": 2.74}}),
]


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def env_fingerprint():
    h = hashlib.md5()
    for p in [ROOT / "env/humanoid_golf_env.py", ROOT / "env/residual_golf_env.py", ROOT / "env/ball_flight_analytic.py", *sorted((ROOT / "env/models").glob("*.xml"))]:
        if not p.exists(): continue
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def discover():
    groups = {}
    for z in sorted((ROOT / "models").glob("*.zip"), key=lambda p: p.stat().st_mtime):
        g = groups.setdefault(md5(z), {"names": [], "mtime": z.stat().st_mtime})
        g["names"].append(z.stem)
    j = RES / f"{SCRIPTED_SRC}.json"
    if j.exists():
        groups["scripted-" + SCRIPTED_SRC] = {"names": [SCRIPTED], "mtime": j.stat().st_mtime - 1, "scripted": True}
    if (RES / "ppo_resid_v3_left_an10_s8.json").exists():   # trainer's scripted config (TRAINING_NOTES: ball_x 0.422, noise 0.005, loft 7, left; eval/eval_scripted_cfg.py base)
        groups["scripted-bx0422"] = {"names": [SCRIPTED_BX], "mtime": j.stat().st_mtime - 0.5, "scripted": True, "scripted_cfg": "bx0422"}
    if (ROOT / "configs/fast_scripted_v2_lofted.json").exists():   # trainer's lofted scripted swing (commit ffc6271), zero residual
        groups["scripted-lofted"] = {"names": [SCRIPTED_LOFT], "mtime": j.stat().st_mtime - 0.25, "scripted": True, "scripted_cfg": "lofted"}
    if (ROOT / "configs/fast_scripted_v3.json").exists():   # stock-motor (force_scale 1) version of the same scripted swing (TRAINING_NOTES Stage 18 actuator baseline)
        groups["scripted-fs1"] = {"names": [SCRIPTED_FS1], "mtime": j.stat().st_mtime - 0.15, "scripted": True, "scripted_cfg": "fs1"}
    if (ROOT / "configs/fast_scripted_v3.json").exists():   # trainer Stage 6 scripted config (commit 9ffa35b), zero residual
        groups["scripted-v3"] = {"names": [SCRIPTED_V3], "mtime": j.stat().st_mtime - 0.2, "scripted": True, "scripted_cfg": "v3"}
    return groups


# results/TRAINING_NOTES.md CORRECTION: eval.eval_gate rebuilt these from train_residual-style args and dropped the v3 address/script settings -> rows are INVALID (superseded by imit2/imit3, which store env_kwargs_full)
NOISE_PASS_CARRY_FRAC = 0.80   # noise PASS (QUICK) = contact stays 100% AND mean carry >= 80% of the clean full-N deterministic mean carry, at that sigma (N=NOISE_EPS det episodes)
NOISE_SIGMAS, NOISE_EPS = (0.005, 0.01), 10   # QUICK noise-robustness columns (small N, labelled)
GATE_ONLY = set()   # v4power rows now supported by main's env (flight_steps/impact_model/power XML); kept as an escape hatch
INVALID_CONFIG = {"imit_w075_s51", "imit_w075_s52", "imit_w075_s53"}
SCRIPTED_V3 = "scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01]"
SCRIPTED_FS1 = "scripted (not learned) [STOCK motors force_scale 1: fast v3 swing, default elbow]"
SCRIPTED_LOFT = "scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01]"
SCRIPTED = "scripted_baseline[ladder cfg: right, loft 6, default ball_x]"   # pseudo-checkpoint: ResidualGolfEnv with the LADDER run's exact config and a ZERO residual action
SCRIPTED_SRC = "ppo_resid_v3_ladder_s0"
SCRIPTED_BX = "scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm]"


def config_for(names):
    for n in names:                       # residual-PPO models: exact env flags from results/<name>.json "args"
        j = RES / f"{n}.json"
        if j.exists() and ("res_scale" in json.loads(j.read_text()).get("args", {}) or "env_kwargs_full" in json.loads(j.read_text())):   # any residual-PPO run with a results JSON is auto-scored (new checkpoints need no code change)
            from eval.env_factory import resid_kw_from_args
            J = json.loads(j.read_text()); args = J["args"]
            assert args.get("name", n) == n, f"{j} args.name mismatch"
            if "env_kwargs_full" in J:   # v5 imitation runs: exact env kwargs incl. script_weight/learn_scale/address (rebuilding from args silently drops them - see TRAINING_NOTES CORRECTION)
                kw = dict(J["env_kwargs_full"], _env="residual", track_weight=0.0, track_set=None); kw["residual_scale"] = list(kw["residual_scale"])
                return args.get("timesteps", args.get("ppo_steps", 0)), kw, f"results/{j.name} env_kwargs_full (script_weight={kw.get('script_weight')}, learn_scale={kw.get('learn_scale')})"
            note = f"results/{j.name} args" + ("" if "ball_dz" in args else "; ball_dz ABSENT in args (flag predates run) -> env default 0.0 used, true training value UNKNOWN")
            return args.get("timesteps", 0), resid_kw_from_args(args), note
    for n in names:                       # prefer a JSON that exists for any alias
        j = RES / f"train_{n.replace('ppo_', '', 1)}.json"
        if j.exists():
            d = json.loads(j.read_text())
            return d["timesteps"], {k: d[k] for k in ENV_KEYS if k in d}, f"results/{j.name}"
    for n in names:
        if n in KNOWN_CONFIGS:
            k = KNOWN_CONFIGS[n]
            return k["steps"], k["env"], k["source"]
    return None, None, "UNKNOWN"


def track_score_run(name, kw, episodes, seed):
    """Mean final info['track_score'] (trainer definition) over `episodes` deterministic episodes; plus mean per-signal parts."""
    import numpy as np
    from stable_baselines3 import PPO
    from eval.env_factory import make_env
    env = make_env(kw); model = PPO.load(str(ROOT / "models" / name), device="cpu"); vals, parts = [], {}
    for ep in range(episodes):
        obs, _ = env.reset(seed=seed + ep); done = False; info = {}; last = None
        while not done:
            obs, _, te, tr, info = env.step(model.predict(obs, deterministic=True)[0]); done = te or tr
            if "track_score" in info: last = (info["track_score"], info.get("track_parts", {}))
        if last: vals.append(last[0]); [parts.setdefault(k, []).append(v) for k, v in last[1].items()]
    return {"defined": bool(vals), "mean": float(np.mean(vals)) if vals else None, "min": float(np.min(vals)) if vals else None, "parts": {k: float(np.mean(v)) for k, v in parts.items()}, "episodes": episodes, "n_with_score": len(vals)}


def load(p, default):
    return json.loads(p.read_text()) if p.exists() else default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=50); ap.add_argument("--seed", type=int, default=4000)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--workers", type=int, default=0, help="parallel episode workers per evaluation (0 = auto: min(4, cores - 1min load average), at least 1)")
    ap.add_argument("--quick", action="store_true", help="QUICK GATE: --quick-episodes episodes (default 10) per mode; labelled provisional, cached separately, writes only results/leaderboard_quick.md and NEVER touches leaderboard.md/json/history (not ranked until a full-gate run)")
    ap.add_argument("--quick-episodes", type=int, default=10); a = ap.parse_args()
    if a.quick: a.episodes = a.quick_episodes
    import os
    if a.workers <= 0:
        a.workers = max(1, min(2, (os.cpu_count() or 2) - int(os.getloadavg()[0])))
    a.workers = min(a.workers, 2)   # shared-box policy: never more than 2 eval workers
    print(f"[leaderboard] mode={'QUICK (provisional)' if a.quick else 'FULL'} episodes={a.episodes} workers={a.workers}", flush=True)
    import eval.dispersion_report as dr
    refs = sorted(p.name[:-len("_swing.npz")] for p in (ROOT / "data/references").glob("*_swing.npz"))
    dr.REFS = refs
    fp = env_fingerprint()
    cache = load(RES / "leaderboard_cache.json", {})
    hist = load(RES / "leaderboard_history.json", {"entries": SEED_HISTORY})
    groups = discover()
    for h, g in groups.items():
        key = f"{h}:{fp}:{a.episodes}:{a.seed}:s12"
        cfg_hash_cached = cache.get(key, {}).get("config_hash")
        if g.get("scripted_cfg") in ("lofted", "v3", "fs1"):
            import eval.eval_scripted_cfg as esc
            cf = "fast_scripted_v3.json" if g["scripted_cfg"] in ("v3", "fs1") else "fast_scripted_v2_lofted.json"
            cfg = {k: v for k, v in json.loads((ROOT / "configs" / cf).read_text()).items() if k != "description"}
            if g["scripted_cfg"] == "fs1": cfg["force_scale"] = 1.0   # stock motors
            steps, kw, src = 0, dict(esc.base, **cfg), f"zero-residual; configs/{cf} (trainer) applied over eval/eval_scripted_cfg.py base (as the trainer's eval_scripted_cfg usage)"
        elif g.get("scripted_cfg") == "bx0422":
            import eval.eval_scripted_cfg as esc
            steps, kw, src = 0, dict(esc.base, ball_x=0.422, ball_x_noise=0.005, loft_deg=7.0), "zero-residual action; trainer config from TRAINING_NOTES / eval/eval_scripted_cfg.py base + ball_x 0.422, ball_x_noise 0.005, loft 7, left"
        elif g.get("scripted"):
            from eval.env_factory import resid_kw_from_args
            steps, kw, src = 0, resid_kw_from_args(json.loads((RES / f"{SCRIPTED_SRC}.json").read_text())["args"]), f"zero-residual action with results/{SCRIPTED_SRC}.json args"
        else:
            steps, kw, src = config_for(g["names"])
        chash = hashlib.md5(json.dumps(kw, sort_keys=True, default=str).encode()).hexdigest()[:12] if kw is not None else None
        if key in cache and not a.force and cache[key].get("config_hash") == chash:   # hit = same checkpoint md5 + env fingerprint + episodes/seed + env-config hash
            print("skip (cached)", g["names"]); continue
        if kw is None:
            cache[key] = {"md5": h, "names": g["names"], "config_source": "UNKNOWN", "error": "training config unknown; not evaluated"}
            continue
        print("evaluating", g["names"], kw, flush=True); t0 = time.time()
        modes = {}
        for det in (True, False):
            try:
                d, _ = dr.run(g["names"][0], kw, a.episodes, a.seed, det, scripted=bool(g.get("scripted")), workers=a.workers)
            except Exception as e:
                d = {"error": f"{type(e).__name__}: {e}"}
            modes["deterministic" if det else "stochastic"] = d
        if any("error" in v for v in modes.values()):
            print("ERROR (not cached):", g["names"], {m: v.get("error") for m, v in modes.items()}); continue
        cache[key] = {"md5": h, "names": g["names"], "steps": steps, "env_kwargs": kw, "config_source": src,
                      "env_fingerprint": fp, "config_hash": chash, "quick": bool(a.quick), "eval_seconds": round(time.time() - t0, 1), "workers": a.workers, "episodes": a.episodes, "seed_base": a.seed, "mtime": g["mtime"], "modes": modes, "scripted": bool(g.get("scripted")),
                      "evaluated_at": time.strftime("%Y-%m-%d %H:%M:%S")}
        (RES / "leaderboard_cache.json").write_text(json.dumps(cache, indent=1))
        if not g.get("scripted") and not any(e["md5"] == h and e.get("env_fingerprint") == fp for e in hist["entries"]):
            hist["entries"].append({"md5": h, "names": g["names"], "steps": steps, "order": g["mtime"], "env_fingerprint": fp,
                                    "modes": {m: {"contact_rate": v.get("contact_rate"), "mean_distance": v.get("mean_distance")} for m, v in modes.items()}})
    (RES / "leaderboard_cache.json").write_text(json.dumps(cache, indent=1))
    if a.quick:
        rows = [c for k, c in cache.items() if k.split(":")[1] == fp and k.split(":")[2:] == [str(a.episodes), str(a.seed), "s12"] and "modes" in c]
        Lq = ["# QUICK GATE (provisional) - NOT a leaderboard", "", f"{a.episodes} episodes per mode, seeds {a.seed}+, env fingerprint `{fp}`. Small N: lateral std / miss rates are noisy. Models here are NOT ranked and NOT promoted; run `python -m eval.leaderboard` (full N) for rank/qualification.", "",
              "| model | kind | det contact | det carry m | det lat std | det launch | stoch contact | stoch carry m | eval s | provisional pass (contact 100% both, det carry>=30, lat std<=2.73) |", "|---|---|---|---|---|---|---|---|---|---|"]
        for c in sorted(rows, key=lambda c: c.get("mtime", 0)):
            d, st = c["modes"].get("deterministic", {}), c["modes"].get("stochastic", {})
            if "contact_rate" not in d or "contact_rate" not in st: continue
            ok = d["contact_rate"] >= 1 and st["contact_rate"] >= 1 and d["mean_carry"] >= 30 and d["lateral_std"] <= 2.73 and not d.get("launch_flat_flag")
            Lq.append(f"| {'/'.join(c['names'])[:70]} | {'SCRIPTED (not learned)' if c.get('scripted') else ('SCRIPT-DISTILLED' if any(x.startswith('imit') for x in c['names']) else 'LEARNED')} | {d['contact_rate']*100:.0f}% | {d['mean_carry']:.1f} | {d['lateral_std']:.2f} | {d['launch_elev_mean_deg']:.1f} | {st['contact_rate']*100:.0f}% | {st['mean_carry']:.1f} | {c.get('eval_seconds','-')} | {'PROVISIONAL YES' if ok else 'no'} |")
        (RES / "leaderboard_quick.md").write_text("\n".join(Lq) + "\n"); print("\n".join(Lq)); return
    (RES / "leaderboard_history.json").write_text(json.dumps(hist, indent=1))

    cur = sorted([c for k, c in cache.items() if k.split(":")[1] == fp and k.split(":")[2:] == [str(a.episodes), str(a.seed), "s12"]
                  and "modes" in c and not any(n in INVALID_CONFIG or n in GATE_ONLY for n in c["names"])],
                 key=lambda c: c.get("mtime", 0))
    # noise robustness (QUICK, N=NOISE_EPS det episodes, seeds a.seed+): Gaussian noise sigma on every obs AND action; only for models that pass a quick contact/carry screen; cached per entry
    for c in cur:
        d0 = c.get("modes", {}).get("deterministic", {})
        if c.get("env_kwargs") is None or d0.get("contact_rate", 0) < 1 or d0.get("mean_carry", 0) < 30 or c.get("scripted") and "v3 Stage 6" not in c["names"][0]: continue
        nr = c.setdefault("noise_robust", {})
        for sg in NOISE_SIGMAS:
            if str(sg) in nr and not a.force: continue
            try:
                dn, _ = dr.run(c["names"][0], c["env_kwargs"], NOISE_EPS, a.seed, True, scripted=bool(c.get("scripted")), workers=a.workers, noise=sg)
                nr[str(sg)] = {k: dn[k] for k in ("contact_rate", "mean_carry", "lateral_std", "launch_elev_mean_deg") if k in dn}; nr[str(sg)]["episodes"] = NOISE_EPS
            except Exception as e:
                nr[str(sg)] = {"error": f"{type(e).__name__}: {e}"}
        (RES / "leaderboard_cache.json").write_text(json.dumps(cache, indent=1))
    # per-run track_score: the TRAINER's definition, env.ResidualGolfEnv._track_score: mean over tracked signals (shoulder pitch, chest yaw, wrist hinge) of exp(-mean((time-normalised swing shape - Mason/unified-refset reference shape)^2)/0.15); info["track_score"].
    # It is DEFINED only when the run's env had track_set + track_weight>0 (imit* runs: unified_v1, weight 2); for other runs it is undefined (n/a), not 0. Reward-only quantity; evaluated here with the run's own track config, det policy, N=NOISE_EPS, seeds a.seed+.
    for c in cur:
        if c.get("scripted") or "track_score" in c and not a.force: continue
        jj = RES / f"{c['names'][0]}.json"
        ek = json.loads(jj.read_text()).get("env_kwargs_full") if jj.exists() else None
        if not ek or not ek.get("track_set") or not (ek.get("track_weight") or 0) > 0:
            c["track_score"] = {"defined": False}; continue
        try:
            c["track_score"] = track_score_run(c["names"][0], dict(c["env_kwargs"], track_set=ek["track_set"], track_weight=float(ek["track_weight"])), NOISE_EPS, a.seed)
        except Exception as e:
            c["track_score"] = {"defined": False, "error": f"{type(e).__name__}: {e}"}
        (RES / "leaderboard_cache.json").write_text(json.dumps(cache, indent=1))
    # contact regressions vs best EARLIER-trained checkpoint (any env fingerprint, from history)
    flags = []
    for c in cur:
        if c.get("scripted"): continue
        for m, v in c.get("modes", {}).items():
            if "contact_rate" not in v: continue
            prev = [(e["modes"][m]["contact_rate"], e["names"][0]) for e in hist["entries"]
                    if e["md5"] != c["md5"] and e["order"] < c["mtime"] and e["modes"].get(m, {}).get("contact_rate") is not None]
            if prev:
                best, who = max(prev)
                v["best_prev_contact"], v["best_prev_model"] = best, who
                if v["contact_rate"] < best - 1e-9:
                    flags.append(f"{'/'.join(c['names'])} [{m}]: contact {v['contact_rate']*100:.0f}% < best previous {best*100:.0f}% ({who})")
    def v2m(v):
        a = [v['dtw_mason_v2'][r]['all11']['mean'] for r in v['dtw_mason_v2']]; u = [v['dtw_mason_v2'][r]['upper5']['mean'] for r in v['dtw_mason_v2']]
        return f"{sum(a)/len(a):.3f} / {sum(u)/len(u):.3f}"

    def score(c):
        ms = [v for v in c.get("modes", {}).values() if "contact_rate" in v]
        if not ms: return (-1, -1)
        return (sum(v["contact_rate"] for v in ms) / len(ms), sum(v["mean_carry"] for v in ms) / len(ms))
    # --- smash gate (launch_report thresholds: fail >1.50, warn >1.49 or <1.30). smash = det mean ball mph / det mean impact club mph (ratio of means; NOT smash_factor_mean) ---
    SM_FAIL, SM_WARN_HI, SM_WARN_LO = 1.50, 1.49, 1.30
    def smash_ratio(c):
        v = c.get("modes", {}).get("deterministic", {}); b, k = v.get("mean_peak_ball_speed"), v.get("impact_club_speed_mean")
        try: r = float(b) / float(k)
        except Exception: return None
        return r if math.isfinite(r) else None
    def smash_flag(c):
        r = smash_ratio(c)
        if r is None: return "n/m smash (no ball/impact speed)"
        if r > SM_FAIL: return "FAIL smash>1.50"
        if r > SM_WARN_HI: return "WARN smash>1.49"
        if r < SM_WARN_LO: return "WARN smash<1.30"
        return None
    def demote_reason(c):
        """HYPOTHETICAL demotion: boosted-impact (impact gain > 1.05) rows whose residual is yaw-only (res_scale[:3] == 0, yaw cap <= 0.05) are effectively the SCRIPTED swing under a power impact model, not a stock-motor policy."""
        ek = c.get("env_kwargs") or {}; g = ek.get("impact_gain") or (ek.get("impact_model") or {}).get("gain"); rs = ek.get("residual_scale")
        if c.get("scripted") or not (g and g > 1.05 and rs and all(abs(x) < 1e-9 for x in rs[:3])): return None
        return "HYPOTHETICAL, effectively scripted: force_scale %g + impact gain %g (inflated), yaw-only residual (res_scale %s); not a stock-motor policy" % (ek.get("force_scale") or 1, g, rs)
    def verdict(c):
        """'= init, not learned' when the run's results JSON says the selected checkpoint is the init (PPO fine-tune never beat it) and the policy-vs-script diff is unchanged."""
        for n in c["names"]:
            j = RES / f"{n}.json"
            if not j.exists(): continue
            try: J = json.loads(j.read_text())
            except Exception: continue
            if J.get("selected") == "init" and J.get("diff_before") == J.get("diff_after"):
                return f"= init, not learned (PPO fine-tune from {J.get('init')}: selected checkpoint = init, policy-vs-script diff unchanged)"
            if J.get("selected") not in (None, "init"):
                dj = RES / f"{n}_departure.json"
                try: D = json.loads(dj.read_text()) if dj.exists() else None
                except Exception: D = None
                if D and "klres_vs_init_rms_rad" in D:
                    a = (J.get("diff_before") or {}).get("rms_rad_all"); b = (J.get("diff_after") or {}).get("rms_rad_all")
                    return (f"weakly changed from init, no demonstrated gain (PPO soft-selection from {J.get('init')}: selected checkpoint {J.get('selected')} != init, but RMS departure from init is only {D['klres_vs_init_rms_rad']:.2g} rad; "
                            f"policy-vs-script RMS {a:.3g} -> {b:.3g} rad, i.e. moved TOWARD the script, not away from it)")
        return None
    for c in cur:
        if "modes" in c:
            c["verdict"] = verdict(c)
            c["smash_ratio_det"] = smash_ratio(c); c["smash_flag"] = smash_flag(c); c["hypo_demoted"] = demote_reason(c)
    # swing-realism harness verdict (results/swing_realism.json, written by eval/swing_realism.py): rows not evaluated are NOT verified, hence not eligible
    try: _SR = json.loads((ROOT / "results" / "swing_realism.json").read_text()).get("models", {})
    except Exception: _SR = {}
    for c in cur:
        if "modes" not in c: continue
        k_ = next((n for n in c["names"] if n in _SR), None)
        if k_ is None and c.get("scripted"): k_ = next((kk for kk in ("scripted_v3",) if kk in _SR), None)   # scripted rows: harness scripted_v3 (same structural limits)
        r_ = _SR.get(k_) if k_ else None
        c["realism"] = (dict(verdict=r_["verdict"], checks_passed=r_["checks_passed"], failed=[n for n, ck in r_["checks"].items() if not ck["passed"]], harness_row=k_) if r_ else dict(verdict="NOT EVALUATED", checks_passed=None, failed=[], harness_row=None))
    sm_ok = lambda c: c.get("smash_flag") is None and "smash_flag" in c and not c.get("hypo_demoted") and (c.get("realism") or {}).get("verdict") == "PASS"   # eligible = smash 1.30-1.49 AND not demoted AND swing-realism harness PASS (unevaluated = unverified = not eligible)
    ranked_all = sorted(cur, key=score, reverse=True)           # incl. scripted baseline
    ranked = [c for c in ranked_all if not c.get("scripted")]   # trained checkpoints only
    ranked_ok_all = [c for c in ranked_all if sm_ok(c)]; ranked_ok = [c for c in ranked if sm_ok(c)]   # rows with smash inside 1.30-1.49: only these can be top/best/showcase
    def _fs(c):
        ek = c.get("env_kwargs", {}) or {}
        return 3.0 if "power" in str(ek.get("model_xml", "")) else float(ek.get("force_scale", 1.0) or 1.0)
    def _motor(c):
        ek = c.get("env_kwargs", {}) or {}
        if "power" in str(ek.get("model_xml", "")): return "power tier (hypothetical: fs 2 + wrist 120 N m + chest +-60; distances INFLATED: impact gain " + str((ek.get("impact_model") or {}).get("gain", "?")) + ", smash ~1.6)"
        f = float(ek.get("force_scale", 1.0) or 1.0)
        return "stock (force_scale 1)" if f <= 1.0 else f"{f:g}x (force_scale {f:g}, hypothetical-strength actuators)"
    def _rtag(c):
        r = c.get("realism") or {}; return "" if not r else (f"[REALISM {r['verdict']}" + (f" {r['checks_passed']}/8" if r.get("checks_passed") is not None else "") + "] ")
    def _label(c): return _rtag(c) + _label0(c)
    def _label0(c):
        if c.get("scripted"): return "SCRIPTED (not learned)"
        if c.get("verdict"): return c["verdict"] + " | " + ("SCRIPT-FREE IMITATION INIT" if False else "init policy's label applies")
        if c.get("hypo_demoted"): return "HYPOTHETICAL: effectively scripted (yaw-only residual under fs2 + impact gain %g); not a stock-motor policy" % ((c.get("env_kwargs") or {}).get("impact_gain") or ((c.get("env_kwargs") or {}).get("impact_model") or {}).get("gain", 0))
        ek = c.get("env_kwargs", {}) or {}; sw = ek.get("script_weight")
        if sw == 0 and any(x.startswith("imit") for x in c["names"]): return "SCRIPT-DISTILLED policy (script-free imitation of the scripted swing, script_weight 0)"
        if sw not in (None, 1.0): return f"SCRIPT-DISTILLED BLEND {round((1 - sw) * 100)}% policy / {round(sw * 100)}% scripted (imitation of the script)" if any(x.startswith("imit") for x in c["names"]) else f"BLEND {round((1 - sw) * 100)}/{round(sw * 100)}"
        return "LEARNED residual on scripted swing"
    stock_tr = [c for c in ranked if _fs(c) <= 1.0]; stock_sc = [c for c in ranked_all if c.get("scripted") and _fs(c) <= 1.0]
    hyp_tr = [c for c in ranked_ok if _fs(c) > 1.0]
    best_line = "@@STOCK@@"
    if hyp_tr: best_line += "**Best under HYPOTHETICAL-strength actuators (force_scale>1 / power tier; NOT a realistic-motor result): " + " / ".join(hyp_tr[0]["names"]) + f"** ({hyp_tr[0]['steps']} steps; {_motor(hyp_tr[0])}) - mean true contact over det+stoch {score(hyp_tr[0])[0]*100:.0f}%, mean carry {score(hyp_tr[0])[1]:.3f} m."
    if not ranked_ok: best_line = "No evaluated models with smash inside 1.30-1.49."
    left = [c for c in ranked_ok if c.get("env_kwargs", {}).get("handedness") == "left"]
    Q_CARRY, Q_LAT, Q_ELEV = 30.0, 2.73, 5.0
    def qual(c):
        v = c.get("modes", {}).get("deterministic", {})
        if "contact_rate" not in v: return None
        checks = {"contact==100% (det and stoch)": all(m.get("contact_rate", 0) >= 1.0 for m in c["modes"].values()),
                  f"mean carry >= {Q_CARRY:g} m (det)": v["mean_carry"] >= Q_CARRY,
                  f"lateral std <= {Q_LAT:g} m (det)": v["lateral_std"] <= Q_LAT,
                  f"mean launch elev >= {Q_ELEV:g} deg, not flat (det)": not v["launch_flat_flag"],
                  "eligible: smash within 1.30-1.49 (ball mph / impact club mph, det) and not hypothetical-demoted (yaw-only residual under boosted impact)": sm_ok(c)}
        return checks
    qrows = [(c, qual(c)) for c in ranked if qual(c)]
    qualifying = [c for c, q in qrows if all(q.values())]
    qualifying.sort(key=score, reverse=True)
    out = {"env_fingerprint": fp, "episodes": a.episodes, "seed_base": a.seed, "references": refs,
           "lateral_threshold_m": 0.5, "models": cur, "contact_regressions": flags, "best_model": (ranked_ok[0]["names"] if ranked_ok else None), "best_overall": (ranked_ok_all[0]["names"] if ranked_ok_all else None), "smash_gate": {"fail_above": SM_FAIL, "warn_above": SM_WARN_HI, "warn_below": SM_WARN_LO, "definition": "det mean ball mph / det mean impact club mph (not smash_factor_mean); rows outside 1.30-1.49 are flagged and cannot be best/top/showcase"}, "verdicts": ["/".join(c["names"]) + ": " + c["verdict"] for c in cur if c.get("verdict")], "hypo_demoted": ["/".join(c["names"]) + ": " + c["hypo_demoted"] for c in cur if c.get("hypo_demoted")], "smash_flagged": ["/".join(c["names"]) + ": " + c["smash_flag"] for c in cur if c.get("smash_flag")], "ranking_unflagged": ["/".join(c["names"]) for c in ranked_ok], "best_left": (left[0]["names"] if left else None), "qualifying": [c["names"] for c in qualifying], "best_qualifying": (qualifying[0]["names"] if qualifying else None),
           "qualify_criterion": {"carry_m_min": Q_CARRY, "lateral_std_m_max": Q_LAT, "launch_elev_deg_min": Q_ELEV, "contact": "100% in both modes", "mode": "deterministic for carry/lateral/launch"},
           "ranking": ["/".join(c["names"]) for c in ranked], "ranking_incl_scripted": ["/".join(c["names"]) for c in ranked_all],
           "track_score_caveat": "VOID/UNVERIFIED: every models[].track_score (mean/min/parts sh,yaw,wr) was computed with the lead/trail arm mapping the Trainer found wrong (trail key scores 0.02). Do not read track_score or any 'Mason-shaped wrist' claim as valid; only the yaw part is unaffected. See the noise/track_score section of leaderboard.md.",
           "history": hist["entries"]}
    (RES / "leaderboard.json").write_text(json.dumps(out, indent=1))
    if ranked_ok:
        bv = [v for v in ranked_ok[0]["modes"].values() if "peak_club_speed_max" in v]
        if bv:
            mx = max(v["peak_club_speed_max"] for v in bv)
            best_line += (f" Peak club-head speed (best single swing over det+stoch): {mx:.2f} m/s = {mx*2.23694:.1f} mph = {mx/53.64*100:.1f}% of the 120 mph (53.64 m/s) target.")
    if left:
        best_line += f" **Best left-handed model: {' / '.join(left[0]['names'])} [{_motor(left[0])}]** (mean contact {score(left[0])[0]*100:.0f}%, mean carry {score(left[0])[1]:.2f} m, physics protocol)."
    _sb = ""
    stock_q = [c for c in stock_tr if any(c["names"][0] in q_["names"] for q_ in qualifying)]
    if stock_q: _sb += "**Stock-motor (force_scale 1) best QUALIFYING trained model: " + " / ".join(stock_q[0]["names"]) + f"** - mean contact {score(stock_q[0])[0]*100:.0f}%, mean carry {score(stock_q[0])[1]:.1f} m. "
    else:
        _sb += "**NO trained model on STOCK motors (force_scale 1) meets the showcase criterion.**" + (f" (Best stock-motor trained row, not qualifying: {' / '.join(stock_tr[0]['names'])}, mean carry {score(stock_tr[0])[1]:.1f} m.)" if stock_tr else "") + " "
        if stock_sc: _sb += f"Stock-motor scripted (not learned) reference: det carry {stock_sc[0]['modes']['deterministic']['mean_carry']:.1f} m, {stock_sc[0]['modes']['deterministic']['peak_club_mph_mean']:.1f} mph. "
    best_line = best_line.replace("@@STOCK@@", _sb)
    best_line += (f" **Best model meeting the showcase criterion (hypothetical-strength actuators if force_scale>1; real carry AND tight lateral AND not-flat launch AND 100% contact; see below): {' / '.join(qualifying[0]['names'])} [{_motor(qualifying[0])}].**"
                  if qualifying else " **NO model meets the showcase criterion (hypothetical-strength actuators if force_scale>1; carry >= %g m, lateral std <= %g m, launch elev >= %g deg, contact 100%%); see qualification table.**" % (Q_CARRY, Q_LAT, Q_ELEV))
    rank_txt = ("Ranking criterion: (1) true club-ball contact rate averaged over deterministic and stochastic modes, higher first; "
                "(2) ties broken by mean carry (m, averaged over both modes, mean over all episodes). Distance is not used.")
    rk = " > ".join("/".join(c["names"][:1]) for c in ranked_all)
    if ranked_ok_all and ranked_ok_all[0].get("scripted"):
        best_line += f" **Best overall (incl. scripted, no-learning baseline): {SCRIPTED}** - mean contact {score(ranked_ok_all[0])[0]*100:.0f}%, mean carry {score(ranked_ok_all[0])[1]:.3f} m (no trained checkpoint beats it)."
    elif ranked_ok_all:
        best_line += f" Best overall incl. scripted baseline: {' / '.join(ranked_ok_all[0]['names'])} [{_motor(ranked_ok_all[0])}]."
    best_line += " **SMASH GATE (launch_report thresholds, smash = det ball mph / impact club mph): rows outside 1.30-1.49 are flagged (FAIL >1.50, WARN >1.49 or <1.30) and cannot be a best/top/showcase row; %d of %d evaluated rows are flagged, %d are not (see 'Smash flag' section).**" % (sum(1 for c in cur if c.get("smash_flag")), sum(1 for c in cur if "smash_flag" in c), sum(1 for c in cur if "smash_flag" in c and not c["smash_flag"]))
    boosted = [("/".join(c["names"][:1]), c["env_kwargs"]["force_scale"]) for c in qualifying if c.get("env_kwargs", {}).get("force_scale", 1.0) > 1.0]
    best_line += (" **HYPOTHETICAL-STRENGTH ACTUATORS: " + ", ".join(f"{n} (force_scale {fs:g}, hypothetical-strength actuators)" for n, fs in boosted) + " run with boosted actuator force caps (force_scale > 1 = more force than the default model); speeds/carries are not evidence of human- or robot-attainable performance.**") if boosted else ""
    best_line += " Rows `imit_w075_s51/52/53` are excluded: INVALID config (eval rebuilt the env from args and dropped v3 settings; see TRAINING_NOTES CORRECTION; superseded by imit2/imit3). Rows with script_weight<1 are BLENDS (executed command = script_weight x scripted + rest learned), shown in the per-row summary."
    def _by(nm): return next((c for c in cur if nm in c["names"] and "modes" in c), None)
    def _noise(c):
        nr = {k: v for k, v in (c.get("noise_robust") or {}).items() if v and "mean_carry" in v}; cl = c["modes"]["deterministic"]["mean_carry"]
        return ", ".join(f"sigma {k}: {v['mean_carry']:.0f} m ({v['mean_carry']/cl*100:.0f}%)" for k, v in sorted(nr.items())) or "noise not measured"
    pair = []
    for nm, why in (("imit9_w000_s51", "best lateral spread (script-free imitation of the scripted v3 swing; passes the 3-seed headline gate for s51/s52/s53) but NOISE-FRAGILE"),
                    ("imit3_w050_s51", "best under observation/action noise (50% script-distilled policy / 50% scripted blend)")):
        c = _by(nm)
        if c: d_ = c["modes"]["deterministic"]; pair.append(f"{nm}: {why}: det carry {d_['mean_carry']:.1f} m / lat std {d_['lateral_std']:.2f} m; quick noise {_noise(c)} (10 eps, vs clean {d_['mean_carry']:.0f} m)")
    if pair:
        best_line += " **Shown side by side, neither promoted as 'learned from Mason' (both imitate the scripted swing; force_scale 2 hypothetical-strength actuators): " + " | ".join(pair) + ".**"
    mt = ["", "## Motor strength x label (read this before any carry number)", "", "| model | motor strength | label | det carry m (yd) | det lat std m | det club mph | smash (ball/impact club, det) | smash flag | landed (det) | qualifies (carry>=30 m, lat<=2.73, 100% contact, smash 1.30-1.49) |", "|---|---|---|---|---|---|---|---|---|---|"]
    mt += ["", "**imit19_masonmapped_dart_s51 caution (SLOW-SWING / LOW-SPEED ARTIFACT, not better accuracy):** trainer gate JSONs (3 seeds x 100 eps, force_scale 2, results/imit_private/gate_imit19_*) show det club 87.6 mph, carry 58.2-58.4 m, launch 13.9-14.0 deg and lateral std only 0.04-0.11 m (stoch 0.04-0.26), against imit15_dart_s53 at 120 mph, 110-113 m, 0.5-2.1 m. It hits ~27% slower, carries about half as far and its lateral spread is 10-30x smaller (0.1-0.2% of carry vs 0.5-1.9% for imit15), so the tiny spread follows from low club speed and a short, tame swing (script t_down 0.08, wrist_cock -0.6, wr_end -0.09), not from precision at a comparable drive. Do not rank it on lateral std. Its wrist/arm style claims are also covered by the lead/trail arm VOID.", ""]
    import subprocess as _sp
    _trk = all(_sp.run(["git", "ls-files", "--error-unmatch", f"results/imit_private/gate_imit19_masonmapped_dart_s51{x}.json"], cwd=ROOT, capture_output=True).returncode == 0 for x in ("", "_seed8000", "_seed9000"))
    mt = [_x.replace("results/imit_private/gate_imit19_*", "results/imit_private/gate_imit19_* [" + ("in repo" if _trk else "held locally (not in repo)") + "]") for _x in mt]
    for c in sorted(cur, key=lambda c: (_fs(c), c.get("scripted", False), -score(c)[1])):
        d_ = c.get("modes", {}).get("deterministic", {})
        if "mean_carry" not in d_: continue
        mt.append(f"| {'/'.join(c['names'][:2])[:60]} | {_motor(c)} | {_label(c)} | {d_['mean_carry']:.1f} ({d_['mean_carry']*1.09361:.0f}) | {d_['lateral_std']:.2f} | {d_['peak_club_mph_mean']:.1f} | {('%.3f' % c['smash_ratio_det']) if c.get('smash_ratio_det') else 'n/m'} | {c.get('smash_flag') or 'ok'} | {d_['landed_fraction']*100:.0f}% | {'yes' if c in qualifying else 'no'} |")
    # --- sim carry vs launch-monitor-model carry (model-based; existing sim numbers are NOT changed) ---
    try:
        from sim.golf_simulator import shot_from_launch
        _sp = load(RES / "ball_spin_measured.json", {})
        mt += ["", "## Sim carry vs launch-monitor-model carry (MODEL-BASED; the MuJoCo carry columns elsewhere are unchanged)", "",
               "MuJoCo carry = ball flown in MuJoCo with the env's own aero (Cd 0.26, Cl=min(1.7 S, 0.3)) and whatever spin the contact produced. 'Model carry' = `sim/golf_simulator.shot_from_launch` (analytic drag + Magnus, validated vs TrackMan within its stated tolerance) at the sim's own mean ball speed and launch with an ASSUMED tour backspin of 2700 rpm. 'Model carry @ smash 1.48' keeps the policy's club speed and launch but sets ball speed = 1.48 x club speed (a legal-driver smash), same 2700 rpm. Measured env backspin (6 det episodes, `results/ball_spin_measured.json`) is shown where available. Real-world reading: only the last column answers 'what would a 1.48-smash driver do at this club speed'; sim smash ~1.0 rows (v3 envs) are far SHORT of real distance, sim smash >1.5 rows (power tier, `impact_model` gain 1.28) are at/above the legal-driver limit.", "",
               "| model | motor strength | club mph (peak) | sim ball mph | sim smash (impact) | launch deg | measured backspin rpm | MuJoCo carry m | model carry m (sim ball spd/launch, 2700 rpm) | model carry m @ smash 1.48 | MuJoCo / model |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for c in sorted(cur, key=lambda c: (_fs(c), c.get("scripted", False), -score(c)[1])):
            d_ = c.get("modes", {}).get("deterministic", {})
            if not all(k in d_ for k in ("mean_peak_ball_speed", "peak_club_speed_mean", "launch_elev_mean_deg", "mean_carry")): continue
            bm, cm, la = d_["mean_peak_ball_speed"] * 2.23694, d_["peak_club_speed_mean"] * 2.23694, d_["launch_elev_mean_deg"]
            if bm < 20 or cm < 20 or not (0 < la < 40): continue
            try: a1 = shot_from_launch(bm, la, 2700).carry_yd * 0.9144; a2 = shot_from_launch(1.48 * cm, la, 2700).carry_yd * 0.9144
            except Exception: continue
            imp = d_.get("impact_club_speed_mean") or 0; sm = f"{bm / (imp * 2.23694):.2f}" if imp > 0.05 else "n/a"
            ms = next((v for k, v in _sp.items() if k in c["names"]), None); mspin = f"{ms['backspin_rpm']:.0f}" if ms else "n/m"
            mt.append(f"| {'/'.join(c['names'][:2])[:60]} | {_motor(c)} | {cm:.0f} | {bm:.0f} | {sm} | {la:.1f} | {mspin} | {d_['mean_carry']:.0f} | {a1:.0f} | {a2:.0f} | {d_['mean_carry'] / a1:.2f} |")
        mt += ["", "n/m = not measured. Spin for non-power rows is the contact-friction spin MuJoCo produced (tens to ~900 rpm in the v3 envs, far below a real driver's ~2700), which is why their MuJoCo carry is much shorter than the model carry at the same ball speed: low spin means little lift. Power-tier rows get ~3080 rpm from the hand-set `impact_model` (spin_k 130), and a ball speed 1.28x the contact result. The hypothetical club speed (132 mph, `t_down` 0.06 s) and smash ~1.55-1.59 are what make 300+ m, not a unit error: at the same inputs the analytic model gives ~307 m and a 1.48 smash would give ~295 m."]
    except Exception as e:
        mt += ["", f"(launch-monitor-model carry table unavailable: {type(e).__name__}: {e})"]
    L = ["# Leaderboard", "", best_line, "", rank_txt, "", f"Full ranking (scripted baseline included): {rk}", ""] + mt + [""] + [
         "Peak club speed = max club_head linear speed over every physics substep of the swing, measured per episode (mean / max over episodes); mph = m/s x 2.23694; % of target = peak / 53.64 m/s (120 mph). "
         "Impact club speed = club_head linear speed at first club-ball contact; smash factor = peak ball speed / impact club speed (contact shots with club speed > 0.05 m/s, averaged).", "",
         f"Current env fingerprint `{fp}` (env + XML hash). {a.episodes} episodes, seeds {a.seed}..{a.seed+a.episodes-1}. "
         "+y = left, miss = |final y| > 0.5 m. Distance = final ball x (total); carry = x at landing after flight, 0 if never landed (mean over all episodes). "
         "**CAVEAT (arm mapping): arm columns 0-3 of every DTW below compare the env's right_* chain (the TRAIL/club arm for a lefty, env/residual_golf_env.py ~l.153-157, 228) with reference cols 0-3. For native mason_v2 refs those cols are Mason's anatomical right = LEAD arm, so the arm part of dtw_mason_v2 (all11 and upper5; eval/style_match.py UPPER_COLS=slice(0,5), dispersion_report.py l.72-74) is VOID: lead/trail arm bug, see Trainer. Leg columns are not affected by the arm issue. dtw_to_reference_style_rad vs scott/rory/scheffler/average uses the same column indices (dispersion_report.py l.71); synthetic/v1 refs are stored in trail/lead roles so they are probably unaffected, UNVERIFIED.** DTW = mean joint-trajectory DTW (rad) to each reference; non-Scott columns are pure reference-style distances.", "",
         "| Model(s) | Steps | Mode | Contact | Mean dist (m) | Max dist (m) | Mean carry (m) | Landed | Lateral std (m) | Left | Right | Peak ball spd (m/s) | Impact club spd (m/s) | Smash | Peak club spd mean/max (m/s) | Peak club mph mean/max | % of 120 mph mean/max | Launch elev mean deg (std) [flat?] | DTW native Mason v2, mean of 11 refs (11j / upper5) | " + " | ".join(f"DTW {r}" for r in refs) + " |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|" + "---|" * len(refs)]
    for c in cur:
        for m, v in c.get("modes", {}).items():
            nm = "<br>".join(c["names"])
            if "error" in v:
                L.append(f"| {nm} | {c['steps']} | {m} | ERROR: {v['error']} |"); continue
            L.append(f"| {nm} | {c['steps']} | {m[:5]} | {v['contact_rate']*100:.0f}% | {v['mean_distance']:.2f} | {v['max_distance']:.2f} | {v['mean_carry']:.3f} | {v['landed_fraction']*100:.0f}% | {v['lateral_std']:.3f} | {v['left_miss_rate']*100:.0f}% | {v['right_miss_rate']*100:.0f}% | {v['mean_peak_ball_speed']:.2f} | {v['impact_club_speed_mean']:.2f} | {v['smash_factor_mean']:.2f} (n={v['smash_factor_n']}) | {'n/a' if v['peak_club_speed_mean'] != v['peak_club_speed_mean'] else format(v['peak_club_speed_mean'],'.2f') + ' / ' + format(v['peak_club_speed_max'],'.2f')} | {'n/a' if v['peak_club_mph_mean'] != v['peak_club_mph_mean'] else format(v['peak_club_mph_mean'],'.1f') + ' / ' + format(v['peak_club_mph_max'],'.1f')} | {'n/a' if v['peak_club_pct_target_mean'] != v['peak_club_pct_target_mean'] else format(v['peak_club_pct_target_mean'],'.1f') + '% / ' + format(v['peak_club_pct_target_max'],'.1f') + '%'}{' (' + str(v['peak_club_unstable_episodes']) + ' sim-unstable eps excluded; raw max ' + format(v['peak_club_raw_max_unstable'],'.3g') + ' m/s)' if v['peak_club_unstable_episodes'] else ''} | {v['launch_elev_mean_deg']:.1f} ({v['launch_elev_std_deg']:.1f}){' FLAT' if v['launch_flat_flag'] else ''} | {v2m(v)} | "
                     + " | ".join(f"{v['dtw_to_reference_style_rad'][r]['mean']:.3f}" for r in refs) + " |")

    # ---- per-row summary: learned fraction (from JSON args), DTW (native mason_v2 set), sequencing (proxy) vs Mason
    def learned_note(c):
        if c.get("scripted"): return "0% (scripted, zero residual)"
        for n in c["names"]:
            j = RES / f"{n}.json"
            if j.exists():
                JJ = json.loads(j.read_text()); ar = JJ.get("args", {}); ek = JJ.get("env_kwargs_full") or c.get("env_kwargs", {})
                if "script_weight" in ek and ek["script_weight"] is not None and ek["script_weight"] != 1.0:   # imitation-distilled blend: script_weight = share of the scripted command in the executed action
                    sw = float(ek["script_weight"]); return (("SCRIPT-FREE IMITATION of the scripted v3 swing: " if sw == 0 else "IMITATION OF THE SCRIPT, %d%% script: " % round(sw * 100)) if any(x.startswith("imit") for x in c["names"]) else "") + f"BLEND: executed command = {sw*100:.0f}% scripted + {(1-sw)*100:.0f}% {"script-distilled policy" if any(x.startswith("imit") for x in c["names"]) else "learned"} (script_weight={sw}, learn_scale={ek.get('learn_scale')}); residual cap +-{ar.get('res_scale')} rad" + (" ; HYPOTHETICAL ACTUATORS force_scale %g" % ek["force_scale"] if ek.get("force_scale", 1) > 1 else "")
                if "res_scale" in ar:
                    ts = ar.get("tempo_scale", "0.3 (env default)")
                    return f"residual on scripted swing: cap +-{ar['res_scale']} rad (shoulder, elbow, wrist, yaw) + tempo_scale {ts}; % of control from policy = not defined/unknown"
        if c.get("env_kwargs", {}).get("_env") != "residual": return "direct policy control (HumanoidGolfEnv; no scripted base)"
        return "unknown (args not recorded)"
    mf = ROOT / "data/references/mason_target_features.json"
    mj = json.loads(mf.read_text())["mason"]["aggregate"] if mf.exists() else {}
    mval = lambda k: mj.get("sequencing." + k, {}).get("median")
    sh_t, el_t, wr_t = mval("arm_shoulder_pitch_R_peak_vel_t"), mval("elbow_R_peak_vel_t"), mval("wrist_R_peak_vel_t")
    L += ["", "## Per-row summary: learned fraction, style distance, sequencing (proxy)", "",
          "Learned fraction = what the JSON args record (residual caps / env type), never guessed. DTW = native mason_v2 recommended set, mean over refs (all 11 joints, rad; arm columns VOID: lead/trail arm bug, see Trainer). Sequencing = time of peak |angular velocity| per segment relative to first true contact (ms; negative = before impact), measured every 5 ms of simulated time within [impact-0.30 s, impact+0.05 s]; proximal-to-distal = hips -> chest yaw -> shoulder -> elbow -> wrist -> club-head speed peaks non-decreasing (5 ms ties count as in order). PROXY: single-joint angular speeds, the sim has no pelvis yaw joint, club speed is the head geom speed.", "",
          "| Model(s) | Mode | Learned fraction (from JSON args) | DTW all11 mean | Peak t rel. impact ms: hips / chest yaw / shoulder / elbow / wrist / club | Prox-to-distal | wrist-shoulder lag s | elbow-shoulder lag s |", "|---|---|---|---|---|---|---|---|"]
    for c in cur:
        for m, v in c.get("modes", {}).items():
            if "error" in v: continue
            dt = [v["dtw_mason_v2"][r]["all11"]["mean"] for r in v.get("dtw_mason_v2", {})]
            q = v.get("sequencing_proxy", {})
            pk = " / ".join(f"{x:.0f}" for x in q["peak_rel_impact_ms_median"]) if q.get("n") else "n/a"
            L.append(f"| {'<br>'.join(c['names'])} | {m[:5]} | {learned_note(c)} | {(sum(dt)/len(dt)) if dt else float('nan'):.3f} | {pk} | {q.get('frac_proximal_to_distal', float('nan'))*100:.0f}% (n={q.get('n', 0)}) | {q.get('wrist_minus_shoulder_s_median', float('nan')):.3f} | {q.get('elbow_minus_shoulder_s_median', float('nan')):.3f} |")
    if sh_t is not None:
        L += ["", f"**Mason reference (proxy, `data/references/mason_target_features.json`, file mtime {time.strftime('%Y-%m-%d %H:%M', time.localtime(mf.stat().st_mtime))}; schema {json.loads(mf.read_text()).get('schema')}; self-filmed ~30 fps 2D MediaPipe angles, {mj.get('n_swings', '?') if isinstance(mj, dict) else '?'}-swing set, events +-1 frame, tempo +-15%):** arm-only sequencing, times in seconds from takeoff within [top, impact+0.15 s]: shoulder_R peak {sh_t:.2f}, elbow_R {el_t:.2f}, wrist_R {wr_t:.2f}; wrist-minus-shoulder lag median {mval('wrist_minus_shoulder_peak_lag_s')} s; elbow-minus-shoulder (from medians) {el_t - sh_t:.2f} s. Pelvis/thorax sequencing is UNAVAILABLE for Mason (reported 'unavailable'), so hips/torso rows cannot be compared. The Data Agent's regenerated (0.4 s timing fix) version is used only if the file in this tree is that version (check the mtime above); no sequencing number is taken from anywhere else. Sim lags and Mason lags are different windows/definitions: indicative only."]
    L += ["", "## Distance in yards (1 m = 1.09361 yd) - det / stoch separate", "",
          "Total = carry + roll = final ball x minus start x along the target line at episode end (450-step horizon; ball may still be rolling; analytic-ball runs end early). Carry = first-landing distance (0 if never landed). Means over all episodes.", "",
          "| Model(s) | Mode | Carry m | Carry yd | Total m | Total yd | Roll m (landed shots) | Max total yd |", "|---|---|---|---|---|---|---|---|"]
    for c in cur:
        for m, v in c.get("modes", {}).items():
            if "error" in v or "mean_total_yd" not in v: continue
            L.append(f"| {'<br>'.join(c['names'])} | {m[:5]} | {v['mean_carry']:.1f} | {v['mean_carry_yd']:.1f} | {v['mean_total_m']:.1f} | {v['mean_total_yd']:.1f} | {v['mean_roll_m']:.1f} | {v['max_total_yd']:.0f} |")
    L += ["", "## Configs used (each model evaluated with its own)", ""]
    for c in cur:
        L.append(f"- **{'/'.join(c['names'])}** ({c['steps']} steps): {c['config_source']}; env = `{json.dumps(c['env_kwargs'])}`")
    for k, c in cache.items():
        if k.split(":")[1] == fp and c.get("config_source") == "UNKNOWN": L.append(f"- {c['names']}: training config UNKNOWN, not evaluated.")
    Qs = ["", "## Showcase qualification criterion", "",
          f"A model qualifies only if ALL hold (deterministic mode unless stated, physics protocol, 50 eps): true contact 100% in both modes; mean carry >= {Q_CARRY:g} m (documented threshold; the scripted baseline carries ~38 m on this protocol); lateral std <= {Q_LAT:g} m (the trainer's gate baseline); mean launch elevation >= {Q_ELEV:g} deg (ball velocity at the end of club-ball contact; rules out the flat/negative-launch exploit). Among qualifiers: highest mean carry over det+stoch.", "",
          "| Model | " + " | ".join(next(iter([q for _, q in qrows])).keys()) + " | Qualifies |", "|---|" + "---|" * (len(next(iter([q for _, q in qrows])))+1)]
    for c, q in qrows:
        Qs.append(f"| {'/'.join(c['names'])} | " + " | ".join('yes' if x else 'NO' for x in q.values()) + f" | {'**YES**' if all(q.values()) else 'no'} |")
    Qs += ["", "## Smash flag", "", "Smash = det mean ball mph / det mean impact club mph (ratio of means; NOT smash_factor_mean). Thresholds from eval/launch_report.py (derived, not published): FAIL >1.50, WARN >1.49 or <1.30. Flagged rows cannot be the best/top/showcase row. DEMOTED rows (ppo_v4yaw_*: force_scale 2 + impact gain 1.28 with a yaw-only residual, so effectively the scripted swing under an inflated power impact model) are labelled HYPOTHETICAL and are also ineligible. Boosted v3 policies sit at ~0.9-1.0 (ball barely faster than the club: not a real-contact smash) and the v4/power impact-model rows at 1.44-1.60.", "",
           "| model | smash | flag | demotion |", "|---|---|---|---|"]
    for c in sorted([c for c in cur if "smash_flag" in c and not c.get("scripted")], key=lambda c: -(c.get("smash_ratio_det") or 0)):
        Qs.append(f"| {'/'.join(c['names'][:1])} | {('%.3f' % c['smash_ratio_det']) if c.get('smash_ratio_det') else 'n/m'} | {c['smash_flag'] or 'ok (1.30-1.49)'} | {c.get('hypo_demoted') or '-'} |")
    Qs += ["", "## Swing realism (results/swing_realism.md; eval/swing_realism.py)", "", "A row is eligible for best/top/showcase/qualifying only if the harness PASSES all 8 checks. NOT EVALUATED = unverified = not eligible.", ""] + [f"- **{'/'.join(c['names'])[:90]}**: {c['realism']['verdict']}" + (f" ({c['realism']['checks_passed']}/8); failed: {', '.join(x.split('_', 1)[1] for x in c['realism']['failed'])}" if c['realism']['failed'] else "") for c in cur if c.get("realism") and c["realism"]["verdict"] != "NOT EVALUATED"] + [f"- {sum(1 for c in cur if c.get('realism', {}).get('verdict') == 'NOT EVALUATED')} other rows: NOT EVALUATED."]
    Qs += ["", "## Verdicts (from each run's results JSON)", ""] + [f"- **{'/'.join(c['names'])}**: {c['verdict']}" for c in cur if c.get("verdict")] + [""]
    Qs += ["", ("Qualifying: " + ", ".join('/'.join(c['names']) for c in qualifying)) if qualifying else "**None qualifies.**"]
    flat = [c for c in cur if any(v.get("launch_flat_flag") for v in c.get("modes", {}).values())]
    Qs += ["", "Flat/negative-launch flag (mean elevation < %g deg or >= 50%% of shots below it): " % Q_ELEV + (", ".join('/'.join(c['names']) + " [" + ", ".join(f"{m[:3]} {v['launch_elev_mean_deg']:.1f} deg" for m, v in c['modes'].items() if v.get('launch_flat_flag')) + "]" for c in flat) or "none")]
    L += Qs
    # trainer gate numbers next to verified ones (left-handed models)
    G = ["", "## Left-handed models: trainer gate JSON vs verified (this leaderboard, same protocol: MuJoCo physics, flight tracker, 450-step horizon, deterministic, 50 eps, seeds 4000+)", "",
         "Verified = this run. Trainer gate = `results/gate_<name>.json` (`eval.eval_gate`; gate: carry > 11.98 m AND lateral std < 2.73 m AND contact >= 99%). Trainer 'analytic' = `results/<name>.json` policy block (100 eps, analytic flight from the MuJoCo launch vector with ASSUMED backspin, episode ends 3 steps after contact) - NOT re-verified here, different protocol.", "",
         "| Model | Source | Contact | Landed | Mean carry (m) | Lateral std (m) | Peak club mph mean | Gate pass |", "|---|---|---|---|---|---|---|---|"]
    for c in cur:
        if c.get("env_kwargs", {}).get("handedness") != "left" or c.get("scripted"): continue
        nm = c["names"][0]; v = c["modes"].get("deterministic", {})
        if "contact_rate" in v:
            ok = v["mean_carry"] > 11.98 and v["lateral_std"] < 2.73 and v["contact_rate"] >= 0.99
            G.append(f"| {nm} | verified (this run, det) | {v['contact_rate']*100:.0f}% | {v['landed_fraction']*100:.0f}% | {v['mean_carry']:.2f} | {v['lateral_std']:.2f} | {v['peak_club_mph_mean']:.1f} | {'PASS' if ok else 'FAIL'} |")
        gj = RES / f"gate_{nm}.json"
        if gj.exists():
            g = json.loads(gj.read_text()).get("policy_det", {})
            G.append(f"| {nm} | trainer gate JSON (det) | {g['contact_rate']*100:.0f}% | {g['landed_fraction']*100:.0f}% | {g['mean_carry']:.2f} | {g['lateral_std']:.2f} | {g['peak_club_mph_mean']:.1f} | {'PASS' if json.loads(gj.read_text()).get('gate_pass') else 'FAIL'} |")
        tj = RES / f"{nm}.json"
        if tj.exists():
            t = json.loads(tj.read_text()).get("policy", {})
            if t: G.append(f"| {nm} | trainer analytic (100 eps) | {t['true_contact_rate']*100:.0f}% | {t['landed_fraction']*100:.0f}% | {t['mean_carry']:.2f} | {t['lateral_std']:.2f} | {t['impact_club_speed_mean_mph']:.1f} (impact) | n/a |")
    L += G
    # native Mason v2 refs
    V = ["", "## DTW vs NATIVE Mason v2 references [arm columns VOID: lead/trail arm bug, see Trainer] (recommended, non-partial, license self_owned/commercial_ok; mean DTW rad: all 11 joints / upper-body 5)", "",
         "**DTW provenance:** scored against `data/references/mason_v2_*.npz` (npz mtimes unchanged, 2026-10-16 03:39); these do NOT read `mason_target_features.json` or `mason_impact_geometry_targets.json`, so the Data Agent regeneration (0.4 s timing fix) does not alter any DTW number here, and no DTW value used pre-fix target values. `mason_impact_geometry_targets.json` was not present in this working tree when this was generated.  "
         "**CAVEATS: 2D-proxy joint angles from single-view MediaPipe, screen-recorded ~30 fps (tempo +-15%), not retargeted to the MuJoCo humanoid, no club data, leg joints weak; native left-handed footage, `right_*` columns = anatomical right = LEAD arm of a left-hander, whereas the env's `right_*` joints are the swinging arm of its own model (mapping/sign conventions NOT calibrated). Indicative only. MultiSense (right-handed, CC0, different protocol) deliberately NOT scored here.**", "",
         "Refs: " + ", ".join(f"`{r.replace('mason_v2_','')}` (q={dr.MASON_V2_INFO[r]['quality']}, {dr.MASON_V2_INFO[r]['view']}, mirrored={dr.MASON_V2_INFO[r]['mirrored']})" for r in dr.MASON_V2_REFS), "",
         "| Model(s) | Mode | " + " | ".join(r.replace("mason_v2_", "") for r in dr.MASON_V2_REFS) + " | mean over refs |", "|---|---|" + "---|" * (len(dr.MASON_V2_REFS) + 1)]
    for c in cur:
        for m, v in c.get("modes", {}).items():
            if "dtw_mason_v2" not in v: continue
            a11 = [v["dtw_mason_v2"][r]["all11"]["mean"] for r in dr.MASON_V2_REFS]; u5 = [v["dtw_mason_v2"][r]["upper5"]["mean"] for r in dr.MASON_V2_REFS]
            V.append("| " + "<br>".join(c["names"]) + " | " + m[:5] + " | " + " | ".join(f"{x:.3f} / {y:.3f}" for x, y in zip(a11, u5)) + f" | {sum(a11)/len(a11):.3f} / {sum(u5)/len(u5):.3f} |")
    L += V
    L += ["", "## Contact regressions (vs best earlier-trained checkpoint, same mode)", ""] + ([f"- {f}" for f in flags] or ["- none"])
    L += ["", "## History (all evaluated checkpoints)", "", "| Checkpoint(s) | Steps | Env | Det contact | Stoch contact |", "|---|---|---|---|---|"]
    for e in sorted(hist["entries"], key=lambda e: e["order"]):
        f = lambda m: "n/a" if e["modes"].get(m, {}).get("contact_rate") is None else f"{e['modes'][m]['contact_rate']*100:.0f}%"
        L.append(f"| {', '.join(e['names'])} | {e['steps']} | {e['env_fingerprint']} | {f('deterministic')} | {f('stochastic')} |")
    # dispersion detail for the ladder model and the scripted baseline
    det_rows = [c for c in cur if c.get("scripted") or "ppo_resid_v3_ladder_s0" in c["names"] or c.get("env_kwargs", {}).get("handedness") == "left"]
    D = ["# Dispersion detail: scripted baseline, ladder model and all left-handed models", "",
         f"{a.episodes} episodes/mode, seeds {a.seed}..{a.seed+a.episodes-1}; flight_tracker definitions (+y left, miss |y|>0.5 m; distance = final ball x at episode end (episode ends on landing/stop); max_ball_x = furthest x reached; carry = x at first landing after flight, mean over all episodes, 'landed' = fraction that landed). Peak club speed validated (>100 m/s or non-finite excluded and counted).", "",
         "| Model | Mode | Contact | Mean final x (m) | Std | Max | Mean max ball x (m) | Mean carry (m) | Landed | Lateral std (m) | Mean y | Left miss | Right miss | Peak club mean/max (m/s) | Peak club mph mean/max | % of 120 mph (max) | unstable eps | Launch elev mean deg (std) | flat? |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in det_rows:
        for m, v in c["modes"].items():
            D.append(f"| {'/'.join(c['names'])} | {m} | {v['contact_rate']*100:.0f}% | {v['mean_distance']:.2f} | {v['std_distance']:.2f} | {v['max_distance']:.2f} | {v['mean_max_ball_x']:.2f} | {v['mean_carry']:.3f} | {v['landed_fraction']*100:.0f}% | {v['lateral_std']:.3f} | {v['mean_y']:+.3f} | {v['left_miss_rate']*100:.0f}% | {v['right_miss_rate']*100:.0f}% | {v['peak_club_speed_mean']:.2f} / {v['peak_club_speed_max']:.2f} | {v['peak_club_mph_mean']:.1f} / {v['peak_club_mph_max']:.1f} | {v['peak_club_pct_target_max']:.1f}% | {v['peak_club_unstable_episodes']} | {v['launch_elev_mean_deg']:.1f} ({v['launch_elev_std_deg']:.1f}) | {'FLAT' if v['launch_flat_flag'] else 'no'} |")
    D += ["", "DTW to native Mason v2 recommended refs (mean rad, all11 / upper5; see leaderboard.md for caveats): mean over the 11 refs", "", "| Model | Mode | mean of 11 refs |", "|---|---|---|"]
    for c in det_rows:
        for m, v in c["modes"].items():
            D.append(f"| {'/'.join(c['names'])} | {m} | {v2m(v)} |")
    (RES / "dispersion_ladder_scripted.md").write_text("\n".join(D) + "\n")
    (RES / "dispersion_ladder_scripted.json").write_text(json.dumps([{k: c[k] for k in ("names", "steps", "config_source", "env_kwargs", "modes")} for c in det_rows], indent=1))
    L += ["", f"## Noise robustness + track_score (QUICK GATE: {NOISE_EPS} deterministic episodes, seeds {a.seed}+, small N so noisy; screened models only)", "",
          f"Gaussian noise of the given sigma is added to EVERY observation and EVERY action (action clipped to [-1,1]). **Noise PASS (QUICK) = contact stays 100% AND mean carry >= {NOISE_PASS_CARRY_FRAC*100:.0f}% of the clean full-N deterministic mean carry at that sigma** (threshold is my choice, not the trainer's; lateral spread is shown but not part of the pass). Provisional: not used for ranking or qualification.",
          "**VOID for the shoulder/wrist parts and any 'Mason-shaped wrist' claim: lead/trail arm bug reported by the Trainer (trail key scores 0.02); `env/residual_golf_env.py` `_load_keyframes` (right_shoulder_pitch/right_wrist columns) and `_track_score` col map {sh:1, yaw:2, wr:3} used that arm mapping. Treat track_score as UNVERIFIED until the Trainer fixes it; only the yaw part is not affected by the arm mix-up.** "
          "track_score = trainer definition (`ResidualGolfEnv._track_score`: mean over shoulder-pitch / chest-yaw / wrist-hinge of exp(-MSE(time-normalised swing shape vs unified-refset reference shape)/0.15), 1 = identical shape); **defined only for runs trained with track_set + track_weight>0 (imit* runs); n/a for every other row (undefined, not zero)**. The trainer logs it in `info` but had not reported it per run; here: run's own track config, deterministic, N=%d." % NOISE_EPS, "",
          "| model | kind | clean carry m / lat std | sigma 0.005: contact, carry m (% of clean), lat std | noise pass 0.005 | sigma 0.01: contact, carry m (% of clean), lat std | noise pass 0.01 | track_score (mean / min) |", "|---|---|---|---|---|---|---|---|"]
    for c in cur:
        nr = c.get("noise_robust"); ts = c.get("track_score")
        if not nr and not (ts and ts.get("defined")): continue
        d0 = c["modes"]["deterministic"]; cl = d0["mean_carry"]
        def f(v):
            if not v or "error" in v: return "-", "-"
            ok = v["contact_rate"] >= 1.0 and v["mean_carry"] >= NOISE_PASS_CARRY_FRAC * cl
            return f"{v['contact_rate']*100:.0f}%, {v['mean_carry']:.1f} ({v['mean_carry']/cl*100:.0f}%), {v['lateral_std']:.2f}", ("PASS" if ok else "FAIL")
        (f5, p5), (f10, p10) = f((nr or {}).get("0.005")), f((nr or {}).get("0.01"))
        tstr = f"{ts['mean']:.3f} / {ts['min']:.3f}" if ts and ts.get("defined") else "n/a (undefined: no track config)"
        L.append(f"| {'/'.join(c['names'][:1])} | {'SCRIPTED (not learned)' if c.get('scripted') else learned_note(c)[:60]} | {cl:.1f} / {d0['lateral_std']:.2f} | {f5} | {p5} | {f10} | {p10} | {tstr} |")
    from eval.hypo_tier import md as hypo_md
    L += [""] + hypo_md()   # separate hypothetical tier (force_scale>1 / effectively scripted), from per-seed gate JSONs
    (RES / "leaderboard.md").write_text("\n".join(L) + "\n"); print("\n".join(L))
    from eval.compare_styles import from_leaderboard
    from_leaderboard()

if __name__ == "__main__":
    main()
