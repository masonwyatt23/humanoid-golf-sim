"""v5 --head realistic (K34, training on it) must stay byte-identical after the v4 port; v4 takes its sourced values from env.v5_body.V4 only."""
import hashlib, json
import numpy as np, pytest
pytest.importorskip("mujoco")
from env import v5_body as B

SPEC = json.loads('{"cg_depth": 0.04, "cg_h": 0.031, "cg_shaft": 0.035, "crown_h": 0.062, "depth": 0.112, "face_h": 0.054, "face_w": 0.105, "fc_h": 0.03, "fc_shaft": 0.035, "fp": 0.02, "heel_toe": 0.12, "iv": 0.0003, "izz": 0.00045, "lie": 58.5, "loft": 10.5, "mass": 0.2}')
GEOM_SHA = "609f042e06060f4eb4cc47cc7634f76b59f1828fc6f1fb4b42b7772cee547862"   # computed on main 58510f07 (pre-v4) at club_len 0.87 and 1.15
KEYS = ('fc_w', 'cg_w', 'plate_half', 'plate_c_w', 'Rw', 'shell_half', 'shell_c_w', 'mass_half')

def _sha(g):
    h = hashlib.sha256()
    for k in KEYS: h.update(np.round(np.asarray(g[k], float), 9).tobytes())
    return h.hexdigest()

def test_v5_realistic_spec_unchanged():
    s, est = B.realistic_head_spec()
    assert {k: round(v, 9) for k, v in s.items()} == SPEC
    assert set(B.K34_PINNED) <= set(est)   # pinned K34 values stay labelled as estimates

@pytest.mark.parametrize("L", [0.87, 1.15])
def test_v5_realistic_geometry_unchanged(L):
    g = B.realistic_head_geometry(B.club_geometry("LH", L))
    assert _sha(g) == GEOM_SHA and abs(g["crown_z"] - 0.064) < 1e-12 and g["sole_clear"] == B.SOLE_CLEAR == 0.002

def test_v4_uses_v4_dict_not_pinned_fallback():
    g = B.realistic_head_geometry(B.club_geometry("LH", 1.15, B.V4_LIE_DEG), v4=True); s = g["spec"]
    assert g["sole_clear"] == B.V4["sole_clear"] == 0.0
    assert abs(s["fc_h"] - 0.029) < 1e-12 and s["fc_shaft"] == B.V4["fc_shaft"] == 0.039 and s["izz"] == B.V4["izz"] == 5600e-7
    assert B.V4_LIE_DEG == 58.5 and not (set(B.K34_PINNED) & set(g["estimates"]))
