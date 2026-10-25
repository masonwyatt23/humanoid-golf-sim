"""STEP2 stageDR trainer: train/v5_train_j.py main block UNCHANGED (exec'd from its source, so every J flag/default/guard is the same) with
JEnv -> train.dr_goal.DREnv for the TRAINING envs only (det_eval stays nominal JEnv), plus (b) the auto-advancing DR curriculum and the external early-stop hook.
Extra flags (default off): --dr, --dr_stage0, --goal_obs, --goal_w, --curr_window. Every extra flag is FLAG-GUARDED on the live env.
Usage: python -m train.v5_train_dr <all v5_train_j flags> --dr [--goal_obs]"""
import json, os, sys, time, numpy as np
import train.v5_train_j as J
from train.dr_goal import DREnv, STAGES, DR, HELDOUT

def _dr_args():
    import argparse
    p = argparse.ArgumentParser(add_help=False); p.add_argument("--dr", action="store_true"); p.add_argument("--dr_stage0", type=int, default=0); p.add_argument("--goal_obs", action="store_true")
    p.add_argument("--goal_w", type=float, default=0.0); p.add_argument("--curr_window", type=int, default=300)
    a, rest = p.parse_known_args(); return a, rest
DA, REST = _dr_args() if __name__ == "__main__" else (None, None)

def make(rank, seed, dt, keys, rs, td, extra=None, dr_extra=None):
    def f():
        e_ = DREnv(dt=dt, seed=seed * 100 + rank + 191, keys=keys, res_scale=rs, t_down=td); e_.configure(**(extra or {})); e_.configure(**(dr_extra or {}))
        allx = dict(extra or {}, **(dr_extra or {}))
        bad = {k: (v, getattr(e_, k, '<missing>')) for k, v in allx.items() if v is not None and not (getattr(e_, k, '<missing>') is v or (isinstance(v, (int, float, str, bool, tuple)) and getattr(e_, k, '<missing>') == v) or (isinstance(v, (dict, list)) and getattr(e_, k, '<missing>') == v))}
        if bad: raise SystemExit(f"FLAG GUARD: configured flags not live in DREnv (abort): {bad}")
        return e_
    return f

class CurrDR(J.CurrJ):
    """(b) stage promotion on training-episode stats under the CURRENT DR (address starts only), harness-matched thresholds
    (mine/robustness: contact>=0.95, start direction |az|<=3 deg (sd_w gate), plant pass = Evaluator lead-foot slip<=3 cm & turn<=12 deg & air<=1 ctrl step, over the whole episode (stricter than the harness window)).
    address->contact: contact>=0.80 & fell<=0.05 ; contact->speed: contact>=0.95 & plant>=0.80 ; speed->shaping: contact>=0.95 & start>=0.80 & plant>=0.90 & club mph med >= 0.95*T.
    Each promotion row (with the window stats) is appended to curriculum_dr.jsonl. External early stop: file EARLY_STOP in the run dir (written by an external watcher, not in this repo)."""
    def _on_step(self):
        if not hasattr(self, "_win"):
            self._win = []; self.stage = getattr(self, "stage", 0); self.training_env.env_method("__setattr__", "dr_stage", self.stage)
        for inf in self.locals.get("infos", []):
            ep = inf.get("ep") if isinstance(inf, dict) else None
            if ep is not None and ep.get("rsi_mode", ep.get("mode", 0)) == 0: self._win.append(ep)
        W = self.curr_window
        if len(self._win) >= W and self.stage < 3:
            w = self._win[-W:]; c = [x for x in w if x.get("contact")]
            st = dict(contact=len(c) / W, fell=float(np.mean([bool(x.get("fell") or x.get("unstable")) for x in w])),
                      start=float(np.mean([abs(x.get("az", 99)) <= 3.0 for x in c])) if c else 0.0,
                      plant=float(np.mean([x.get("foot_slip", 1) <= 0.03 and x.get("foot_turn", 0) <= 12 and x.get("foot_air", 0) <= 1 for x in w])),
                      mph=float(np.median([x["club_mph"] for x in c])) if c else 0.0, T=float(self.T))
            crit = [(st["contact"] >= 0.80 and st["fell"] <= 0.05), (st["contact"] >= 0.95 and st["plant"] >= 0.80), (st["contact"] >= 0.95 and st["start"] >= 0.80 and st["plant"] >= 0.90 and st["mph"] >= 0.95 * self.T)][self.stage]
            if self.n_calls % 2000 == 0 or crit:
                row = dict(step=self.num_timesteps, stage=STAGES[self.stage], window=W, stats=st, promote=bool(crit), t=time.strftime("%Y-%m-%d %H:%M:%S %Z"))
                if crit: self.stage += 1; row["to"] = STAGES[self.stage]; self.training_env.env_method("__setattr__", "dr_stage", self.stage); self._win = []
                open(os.path.join(self.out, "curriculum_dr.jsonl"), "a").write(json.dumps(row) + "\n")
        if len(self._win) > 4 * W: self._win = self._win[-W:]
        if os.path.exists(os.path.join(self.out, "EARLY_STOP")): print("EARLY_STOP file found -> stopping", flush=True); return False
        return super()._on_step()

if __name__ == "__main__":
    sys.argv = [sys.argv[0]] + REST
    src = open(J.__file__).read(); main = src[src.index('if __name__ == "__main__":'):]
    dr_extra = dict(dr=(True if DA.dr else None), dr_stage=(DA.dr_stage0 if DA.dr else None), goal_obs=(True if DA.goal_obs else None), goal_w=(DA.goal_w or None))
    main = main.replace("make(i, a.seed, a.dt, keys, a.res_scale, a.t_down, extra)", "make(i, a.seed, a.dt, keys, a.res_scale, a.t_down, extra, DR_EXTRA)")
    main = main.replace("cb = CurrJ(", "cb = CurrDR(").replace('json.dump(vars(a), open(os.path.join(out, "args.json"), "w"))', 'json.dump(dict(vars(a), **DR_ARGS), open(os.path.join(out, "args.json"), "w"))')
    main = main.replace("cb.h_last = step0", "cb.h_last = step0; cb.curr_window = DR_ARGS['curr_window']; cb.stage = DR_ARGS['dr_stage0']")
    assert main.count("DR_EXTRA") == 1 and main.count("CurrDR(") == 1 and main.count("DR_ARGS") == 3, "v5_train_j main block changed; refusing to patch"
    G = dict(vars(J)); G.update(__name__="__main__", make=make, CurrDR=CurrDR, DR_EXTRA=dr_extra, DR_ARGS=dict(vars(DA), dr_ranges=DR, heldout_excluded=HELDOUT, trainer="train/v5_train_dr.py"))
    exec(compile(main, J.__file__ + ":__main__", "exec"), G)
