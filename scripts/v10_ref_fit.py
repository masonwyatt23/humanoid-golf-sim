"""V10 refit: V8 objective + harness-style lead-foot plant on every start: address-referenced lead-sole slip and turn over ref.t_dstart -> impact
(Evaluator pass: slip <= 3 cm, turn <= 12 deg), penalised per start and on the noisy median. Warm start from V8 keys. V5_ENV_V4=1."""
import sys, numpy as np
import scripts.v8_ref_fit as F, scripts.v7_ref_fit as V
_one = V.one
def one(e, ref, pid):
    st = e.step; S = {}
    def step(a):
        o = st(a)
        sid = e.m.site(f"{e.lead}_sole_site").id; P = e.d.site_xpos[sid]; R = e.d.site_xmat[sid].reshape(3, 3); yw = float(np.arctan2(R[1, 0], R[0, 0]))
        if 'a' not in S: S['a'] = (float(P[0]), float(P[1]), yw); S['sl'] = 0.0; S['tn'] = 0.0
        if e.d.time >= ref.t_dstart and not e.contact:
            S['sl'] = max(S['sl'], float(np.hypot(P[0] - S['a'][0], P[1] - S['a'][1]))); S['tn'] = max(S['tn'], abs(float((np.degrees(yw - S['a'][2]) + 180) % 360 - 180)))
        return o
    e.step = step
    try: r = _one(e, ref, pid)
    finally: e.__dict__.pop('step', None)
    r['h_slip'] = S.get('sl', 0.1); r['h_turn'] = S.get('tn', 30.0); return r
V.one = one
_t8 = F.term
def term(r, cap=85.0):
    s = _t8(r, cap); return s - float(__import__("os").environ.get("V10_SLIP_W","20")) * min(max(r.get("h_slip", 0.1) - 0.025, 0) / 0.01, 5) - 8.0 * min(max(r.get('h_turn', 30) - 10.0, 0) / 3.0, 4)
F.term = term; V.term = term
_s8 = F.score
W_SPD = float(__import__('os').environ.get('V10_SPD_W', '0')); W_PEL = float(__import__('os').environ.get('V10_PEL_W', '0'))
def score(x):
    s, d = _s8(x)
    if W_SPD or W_PEL:
        r = d.get('mph_p10', 0) / max(d.get('mph_med_all', 1), 1)
        s -= W_SPD * min(max(0.95 - r, 0) / 0.05, 6) + W_PEL * min(max(255.0 - (d.get('pel_med') or 0), 0) / 25.0, 6)
    return s, d
F.score = score; V.score = score
if __name__ == "__main__":
    import runpy; runpy.run_module("scripts.v7_ref_fit", run_name="__main__", alter_sys=False)
