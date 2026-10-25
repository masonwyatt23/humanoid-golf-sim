# Wrist PD lag: why achieved ~-0.33 rad vs commanded ~-0.09 rad

> Consent note: the clips come from Mason's own screen-recorded social-media feed video; consent for release has not been given; this repo is public.


Method: read `env/residual_golf_env.py`, `env/models/humanoid_golf_v3.xml`, `humanoid_golf_v4_power.xml`, `eval/wrist_replay.py` (read-only), then ran `python -m data.wrist_pd_lag_probe` in `<local-path>/golfvenv` (MuJoCo 3.16; other joints held by the env's own PD; left-hander; `grip=False`, the env default, so the passive left arm is NOT coupled). Output: `data/references/wrist_pd_lag_probe.json`. Sim only, UNVERIFIED against hardware, and I did not reproduce the exact -0.33/-0.09 pair (I did not have the Trainer's run/seed/clip).

## 1. Actuator model facts (as read)
- Action is a **target position** for a PD loop evaluated every physics substep (0.5 ms; control dt 20 ms, ZOH on the target only). `ctrl = (kp*(tgt-q) - kd*qd)/gear`, MuJoCo `motor` (gain 1), `force = clip(ctrl, forcerange)`, `torque = gear*force`.
- right_wrist: `gear=20`; forcerange +-3 (v3) -> **60 N·m** stock, +-6 (v4_power) -> **120 N·m** stock; configs use `force_scale` (mostly 2.0, one 1.0) which multiplies `actuator_forcerange`, so v3 fs2 = 120 N·m, v4_power fs2 = 240 N·m. Joint: hinge axis y, range +-120 deg, `armature=0.2`; joint damping **2.0 in v3, 0.5 in v4_power** (v4_power sets `damping="0.5"` on the wrist; confirmed in the probe JSON). v4_power therefore lags somewhat less (results below are within ~0.01 rad of v3 in the ramp tests). Gains in configs: `kp=700`, `kd=700/30=23.33` (class default kd=40). Club (shaft 0.10 kg, head 0.20 kg at 1.12 m) hangs off the wrist.
- Command timing: `targets(self.clock)` is evaluated at the clock **before** it advances, so the applied target is one control step (20 ms) behind the post-step `env.clock`. `eval/wrist_replay.py` logs `cmd = tg(env.clock)` **after** `env.step`, i.e. the target for the *next* step, 20 ms ahead of what produced the logged angle.

## 2. Probe results (v3 fs2; v3 fs1 and v4_power fs1/fs2 within a few mrad, see JSON)
- **Steady state is exact**: steps to -0.09 and -0.33 rad end at -0.087 / -0.329 rad. So there is **no sign, offset, or ctrl-scale error** and no gravity/club-load droop in this PD (gravity torque ~2 N·m vs kp 700: ~3 mrad).
- **It is a dynamic lag**: a step to -0.09 takes ~0.18 s to reach 90%; -0.33 takes ~0.10 s.
- Settled at -0.5 (top), ramp to -0.09 over the 0.095 s downswing used by the scripts: at the ramp end the applied command is -0.155 (-0.09 one step later) but achieved is **-0.28 (v3 fs1/fs2) / -0.27 (v4_power)**, i.e. 0.12-0.13 rad behind; with a 0.2 s ramp the lag is 0.05 rad. A ramp 0 -> -0.977 in 0.095 s lags by 0.30-0.48 rad (fs1 v3 is torque-saturated 7% of steps; fs2 and v4_power are not).
- Reading the achieved angle a step early (post-step vs applied-target mismatch above) adds another ~0.05-0.1 rad of apparent gap, which together can reach the reported ~0.2-0.3 gap. This is arithmetic from the probe, not a reproduction.

## 3. Root-cause hypotheses (ranked)
1. **Plain PD tracking lag (time constant) vs a very fast downswing** (most likely, measured). Velocity-proportional error ~ (kd+joint damping)/kp ~ 0.06 s times the ramp rate (~4.3 rad/s) ~ 0.12-0.25 rad. Not a bug; the wrist cannot follow a command that moves 0.4 rad in 95 ms.
2. **Logging/stale-command phase**: the replay diagnostic compares an angle with a target that is 20 ms ahead of the applied one (and `style_lead` only applies with `style_prior`). Inflates the gap, does not cause the real lag.
3. **Torque saturation**: only in v3 at stock force (fs1, 60 N·m): 5-7% of steps saturated in ramps and the large 0.977 ramp. Not the cause at fs2/v4_power in these cases, but would add lag for larger commands.
4. **Sign/offset error**: ruled out for the PD itself (steady state exact). A *mapping* offset remains a separate issue (`docs/WRIST_SIGN_MAPPING.md`).
5. **Gravity/club inertia**: small steady effect; the club inertia is what sets the time constant (part of #1). Grip constraint: not active in these runs; if `grip=True` it may add coupling (untested).
6. Ctrl-mapping scale: ruled out (gear/forcerange as above; steady-state exact).

## 4. Recommended fix / diagnostic (do not edit env/ from here)
- Diagnostic: rerun `eval/wrist_replay.py` logging the *applied* target (`env._tgt[2]`) and `qpos` at the same step; expect lag ~0.12 rad at impact.
- Fix: **lead the wrist command by ~0.06 s** (read the target at `t+0.06`; same idea as `style_lead`, applied to the scripted/keyframe wrist). Probe (v3 fs2, ramp -0.5 -> -0.09 in 0.095 s), achieved minus intended at impact: lead 0 -> -0.11; lead 0.04 -> -0.015; lead 0.06 -> +0.003; lead 0.08 -> +0.01. Doubling kp to 1400 with kd 23.3 gives -0.025 without lead (but stiffer gains change the whole swing; untested elsewhere); kd 40 is slower (-0.076).
- Also compare sensible timing: a 0.095 s downswing is itself shorter than published downswing times (see the filming/timing docs); a longer downswing reduces lag ~linearly.

## 5. Files
`data/wrist_pd_lag_probe.py`, `data/references/wrist_pd_lag_probe.json` (regenerate with `python -m data.wrist_pd_lag_probe`; ~4 s, no training).
