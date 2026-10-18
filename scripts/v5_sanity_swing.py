"""Stage 0 PIPELINE-ONLY scripted motion for the v5 env: a rigid trunk (waist-yaw) wind-up and sweep that carries the club head on a horizontal arc through
the ball, to exercise contact detection, golfphys shot computation, segment logging and reward terms. NOT a golf swing (arms/wrists/legs do not move), NOT a
teacher, never used for training, distillation or reward shaping. Use with env tether=True or False (the unpinned variant is reported separately)."""
import numpy as np

def waist_offset(t, wy=0.6, t_back=0.8, t_hold=0.05, t_down=0.25, fw=0.8):
    """Waist-yaw offset (rad) from address: smooth backswing to +wy (away from the target for an LH golfer), hold, linear sweep to -fw*wy."""
    t1 = t_back; t2 = t1 + t_hold; t3 = t2 + t_down
    if t < t1:
        u = t / t1; return wy * u * u * (3 - 2 * u)
    if t < t2: return wy
    if t < t3:
        u = (t - t2) / t_down; return wy * (1 - u * (1 + fw))
    return -fw * wy

def action_at(env, t, **kw):
    a = np.zeros(len(env.names)); i = env.names.index("waist_yaw_joint")
    sgn = 1.0 if env.handed == "LH" else -1.0          # mirrored for a right-hander (yaw sign flips)
    a[i] = np.clip(sgn * waist_offset(t, **kw) / env.act_scale[i], -1, 1)
    return a

def run_swing(env, seed=0, max_s=2.0, **kw):
    env.reset(seed=seed); info = {}
    while True:
        t = env.d.time
        o, r, term, trunc, info = env.step(action_at(env, t, **kw))
        if term or trunc or t > max_s: break
    return info
