"""Stage J joint-space swing reference for the v5 G1 LEFT-handed golfer (lead arm = physical RIGHT; see lead_trail).
REFERENCE-GUIDED RESIDUAL RL scaffolding, NOT pure from-scratch. Public-only sources: data/references/public_joint_trajectories_110plus.json (550e64e),
g1_joint_mapping_public_refs.json / planar_swing_decomposition_public_refs.json (e517409; mapping notes embedded below). No Instagram/Mason data.

Clock: t=0 start; hold T_WAIT, smooth backswing to the top over T_BACK, hold at top T_HOLD, downswing T_DOWN (impact at t_imp), follow-through to the finish over T_FOLLOW.
q_ref(t) = q_addr + delta(t); delta(t) interpolates keyframe deltas (rad, relative to the address pose) ADDR(0) -> TOP -> IMPACT -> FINISH.
Public-derived keyframes (PUBLIC_KEYS): waist_yaw from the X-factor curve (+61 deg at top -> +14 at impact, LH sign verified in Stage I; the downswing follows the
public phase curve exactly), lead/trail shoulder pitch = -(elevation-5deg) (lead top 90 -> -85, impact 35 -> -30; trail top 43, impact 23), elbows q=(80-flex)/55
(lead top 58 -> 0.40, impact 34 -> 0.84; trail top 130 -> -0.91, impact 40 -> 0.73), wrist/pelvis/roll/yaw/hip: no public absolute channel -> 0 (address hold) in the
PURE reference; TUNED_KEYS are additional free keyframe deltas fitted open-loop in the sim (scripts/v5_ref_fit.py), still no private data.
"""
import json, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
_REF = json.load(open(os.path.join(HERE, "..", "data", "references", "public_joint_trajectories_110plus.json")))["channels"]["x_factor"]["speed_class_curves"]["110"]
_PH = np.array(_REF["phase_grid"]["phase"]); _XF = -np.array(_REF["phase_grid"]["angle_deg"])      # LH mirror -> +61 at top, +14 at impact
_tt = np.array(_REF["t_s"]); _aa = -np.array(_REF["angle_deg"]); _T110 = float(_REF["downswing_duration_s"])

T_WAIT, T_BACK, T_HOLD, T_FOLLOW = 0.10, 0.85, 0.05, 0.40
JOINTS = ["hip_yaw", "hip_roll", "hip_pitch", "knee", "ankle_pitch", "waist_yaw", "waist_roll", "waist_pitch", "sh_pitch", "sh_roll", "sh_yaw", "elbow", "wr_roll", "wr_pitch", "wr_yaw"]
# keys: (group, role, stage) role in lead/trail/both ; value rad delta from address
PUBLIC_KEYS = {
    ("waist_yaw", "both", "top"): np.radians(61.0), ("waist_yaw", "both", "imp"): np.radians(14.0), ("waist_yaw", "both", "fin"): np.radians(-30.0),
    ("sh_pitch", "lead", "top"): -1.44, ("sh_pitch", "lead", "imp"): -0.48, ("sh_pitch", "lead", "fin"): -1.3,
    ("sh_pitch", "trail", "top"): -0.46, ("sh_pitch", "trail", "imp"): -0.11, ("sh_pitch", "trail", "fin"): -0.9,
    ("elbow", "lead", "top"): 0.47, ("elbow", "lead", "imp"): 0.91, ("elbow", "lead", "fin"): 0.3,
    ("elbow", "trail", "top"): -1.44, ("elbow", "trail", "imp"): 0.20, ("elbow", "trail", "fin"): -0.5,
}
STAGES = ["top", "imp", "fin"]
# tunable free keyframes (rad deltas, in addition to / replacing the public ones)
TUNED_GROUPS = [("hip_yaw", "both"), ("hip_roll", "lead"), ("hip_roll", "trail"), ("knee", "lead"), ("knee", "trail"), ("waist_roll", "both"), ("waist_pitch", "both"),
                ("sh_pitch", "lead"), ("sh_pitch", "trail"), ("sh_roll", "lead"), ("sh_roll", "trail"), ("sh_yaw", "lead"), ("sh_yaw", "trail"), ("elbow", "lead"), ("elbow", "trail"),
                ("wr_pitch", "lead"), ("wr_pitch", "trail"), ("wr_yaw", "lead"), ("wr_yaw", "trail"), ("wr_roll", "lead"), ("wr_roll", "trail"), ("waist_yaw", "both"), ("ankle_pitch", "both")]
TUNED_KEYS = [(g, r, s) for (g, r) in TUNED_GROUPS for s in STAGES]


def _ease_down(x, k=1.6): return np.clip(x, 0, 1) ** k


class SwingRef:
    def __init__(self, names, q_addr, lead, jlo, jhi, keys=None, t_down=0.27, k_ease=1.6):
        """keys: dict (group, role, stage) -> rad delta added on top of PUBLIC_KEYS (tuned residual keyframes) or full override if keys has key 'replace'."""
        self.names, self.q_addr, self.jlo, self.jhi = list(names), np.asarray(q_addr, float), jlo, jhi
        self.t_down = t_down; self.k_ease = k_ease; self.lead = lead; trail = "left" if lead == "right" else "right"
        self.t_top = T_WAIT + T_BACK; self.t_imp = self.t_top + T_HOLD + t_down; self.t_end = self.t_imp + T_FOLLOW
        self.t_dstart = self.t_top + T_HOLD
        self.K = np.zeros((3, len(names)))      # top, imp, fin deltas
        self.xf_idx = None
        tab = dict(PUBLIC_KEYS); self.k_grp = {}; self.sh_grp = {}; self.pc_grp = {}; self.il = {}
        if keys:   # K8: ("ease", <kind>, "k") entries set a per-joint-kind downswing ease exponent (e.g. wrist lag/release timing), not keyframe deltas
            keys = dict(keys)
            for k in [k for k in keys if k[0] == "ease"]: self.k_grp[k[1]] = float(keys.pop(k))
            for k in [k for k in keys if k[0] == "phase"]: self.sh_grp[k[1]] = float(keys.pop(k))
            for k in [k for k in keys if k[0] == "il"]: self.il[k[1]] = float(keys.pop(k))   # K26: impact-lean bump (rad) on a named joint (lead wrist/shoulder shaft lean), gaussian about impact, sd IL_W
            for k in [k for k in keys if k[0] == "pc"]: self.pc_grp.setdefault(k[1], {})[k[2]] = float(keys.pop(k))   # K22: explicit bell-velocity downswing curve per kind: c = peak time before impact (s), w = width (s)   # K10: per-kind downswing start delay (s), e.g. hip/waist
        if keys: 
            for k, v in keys.items(): tab[k] = tab.get(k, 0.0) + v if not isinstance(v, tuple) else v[0]
        for (g, role, st), v in tab.items():
            for j, n in enumerate(self.names):
                side = n.split("_")[0] if n.startswith(("left", "right")) else None
                kind = n.replace("left_", "").replace("right_", "").replace("_joint", "")
                gk = {"hip_yaw": "hip_yaw", "hip_roll": "hip_roll", "hip_pitch": "hip_pitch", "knee": "knee", "ankle_pitch": "ankle_pitch", "waist_yaw": "waist_yaw", "waist_roll": "waist_roll", "waist_pitch": "waist_pitch",
                      "sh_pitch": "shoulder_pitch", "sh_roll": "shoulder_roll", "sh_yaw": "shoulder_yaw", "elbow": "elbow", "wr_roll": "wrist_roll", "wr_pitch": "wrist_pitch", "wr_yaw": "wrist_yaw"}[g]
                if kind != gk: continue
                r_ = "lead" if side == lead else "trail" if side == trail else "both"
                if side is None or role == "both" or role == r_:
                    sgn = 1.0
                    self.K[STAGES.index(st), j] += sgn * v
            self.xf_idx = [j for j, n in enumerate(self.names) if n.startswith("waist_yaw")][0]
        kinds = [n.replace("left_", "").replace("right_", "").replace("_joint", "") for n in self.names]
        self.sh_vec = np.array([self.sh_grp.get(kd, self.sh_grp.get(kd.split("_")[0], 0.0)) for kd in kinds]); self.sh_xf = self.sh_grp.get("waist_yaw", self.sh_grp.get("waist", 0.0))
        self.il_idx = [(self.names.index(n), v) for n, v in self.il.items() if n in self.names]
        self.pc_idx = []
        for g_, pr in self.pc_grp.items():
            js = [j for j, kd in enumerate(kinds) if kd == g_ or kd.startswith(g_ + "_") or (g_ == "shoulder" and kd.startswith("shoulder"))]
            self.pc_idx.append((np.array(js, int), float(pr.get("c", 0.08)), max(float(pr.get("w", 0.04)), 0.01), float(pr.get("a", 1.0))))
        self.k_vec = np.array([self.k_grp.get(kd, self.k_grp.get(kd.split("_")[0], k_ease)) for kd in kinds])
        self.wy_pub = (PUBLIC_KEYS[("waist_yaw", "both", "top")], PUBLIC_KEYS[("waist_yaw", "both", "imp")])
        self.wy_extra = [self.K[i, self.xf_idx] - (PUBLIC_KEYS[("waist_yaw", "both", s)]) for i, s in enumerate(STAGES)]

    def delta(self, t):
        tb0, tb1 = T_WAIT, T_WAIT + T_BACK
        if t <= tb0: return np.zeros(len(self.names))
        if t <= self.t_top + T_HOLD and t > tb1: return self.K[0].copy()
        if t <= tb1:
            x = (t - tb0) / T_BACK; s = 3 * x * x - 2 * x ** 3; return self.K[0] * s
        if t <= self.t_imp:                                    # downswing top -> impact
            ph = (t - self.t_dstart) / self.t_down; phj = np.clip((t - self.t_dstart - self.sh_vec) / np.maximum(self.t_down - self.sh_vec, 0.05), 0, 1); g = _ease_down(phj, self.k_vec)
            ph = float(np.clip((t - self.t_dstart - self.sh_xf) / max(self.t_down - self.sh_xf, 0.05), 0, 1)); gx = _ease_down(ph, self.k_ease)
            d = self.K[0] + (self.K[1] - self.K[0]) * g
            # waist yaw: public X-factor phase curve (110 mph class, LH-mirrored) + the extra tuned offset
            xf = np.interp(ph, _PH, np.radians(_XF)); extra = self.wy_extra[0] + (self.wy_extra[1] - self.wy_extra[0]) * gx
            d[self.xf_idx] = xf + extra
            if self.pc_idx:   # K22: bell-shaped velocity (erf position profile) peaking pc_c before impact; overrides ease/phase for those joints
                from math import erf
                for js, c_, w_, a_ in self.pc_idx:
                    tc = self.t_imp - c_; F = lambda tt: erf((tt - tc) / w_)
                    f0, f1 = F(self.t_dstart), F(self.t_imp); gg = (F(t) - f0) / max(f1 - f0, 1e-6)
                    d[js] = (1.0 - a_) * d[js] + a_ * (self.K[0][js] + (self.K[1][js] - self.K[0][js]) * gg)   # a = blend toward the explicit curve (K22e gentle arm)
            return d
        x = np.clip((t - self.t_imp) / T_FOLLOW, 0, 1); s = 3 * x * x - 2 * x ** 3
        return self.K[1] + (self.K[2] - self.K[1]) * s

    def q(self, t):
        d = self.delta(t)
        if getattr(self, 'il_idx', None):
            b = float(np.exp(-0.5 * ((t - self.t_imp) / 0.035) ** 2)); d = d.copy()
            for j, v in self.il_idx: d[j] += v * b
        return np.clip(self.q_addr + d, self.jlo + 1e-3, self.jhi - 1e-3)
    def downswing_phase(self, t): return float(np.clip((t - self.t_dstart) / self.t_down, 0.0, 1.0)) if t >= self.t_dstart else 0.0
    def u(self, t): return float(np.clip(t / self.t_end, 0.0, 1.0))
