"""Worker tee_geometry() crown must follow the Trainer's _crown_tee_dz() (2026-10-24 fix): box = face-centre site + 0.5*H*up_z
(H = face_h if set, else head-box height); realistic = env _head_geo['crown_z'] (sole clearance + sourced 62 mm crown); shell max corner kept as info.
Reference values (Trainer env, single-env probe): box 21.464 mm, box face_h 0.053 16.056 mm, realistic 4.135 mm."""
import re, types
from pathlib import Path
import numpy as np
import pytest

_W = Path(__file__).resolve().parents[1] / "results/overnight/_j_worker_gp_v3.py"
if not _W.exists(): pytest.skip("v3 worker is untracked (held); tee_geometry checked in the Evaluator repo", allow_module_level=True)
SRC = _W.read_text()
NS = dict(np=np); exec(re.search(r"def tee_geometry\(env_\):.*?\n    return G_\n", SRC, re.S).group(0), NS)
tee_geometry = NS["tee_geometry"]

class _M:
    def __init__(s, sizes): s.geom_size = sizes
    def geom(s, name): return types.SimpleNamespace(id=2)

def _env(head="box", face_h=None):
    sizes = np.array([[0.045, 0.055, 0.032], [0.021335, 0, 0], [0.03, 0.05, 0.031]])
    d = types.SimpleNamespace(geom_xmat=np.tile(np.eye(3).ravel(), (3, 1)), geom_xpos=np.array([[0, 0, 0.049], [0, 0, 0.05987], [0, 0, 0.033]]),
                              site_xpos=np.array([[0, 0, 0.049]]))
    e = types.SimpleNamespace(d=d, m=_M(sizes), head_geom=0, ball_geom=1, head_site=0, tee=np.array([0, 0, 0.05987]), head=head, face_h=face_h)
    if head == "realistic":
        e._head_geo = dict(crown_z=0.064); e.face_limits = lambda: (0.027, 0.0525)
    return e

def test_box_crown_uses_face_h_like_trainer():
    g = tee_geometry(_env()); assert abs(g["crown_z_m"] - (0.049 + 0.032)) < 1e-12
    g = tee_geometry(_env(face_h=0.053)); assert abs(g["crown_z_m"] - (0.049 + 0.0265)) < 1e-12 and abs(g["crown_boxtop_z_m"] - 0.081) < 1e-12

def test_realistic_crown_is_env_crown_z_shell_kept_as_info():
    g = tee_geometry(_env("realistic"))
    assert abs(g["crown_z_m"] - 0.064) < 1e-12 and abs((g["crown_z_m"] - g["ball_centre_z_m"]) * 1e3 - 4.13) < 0.5
    assert abs(g["crown_shell_maxcorner_z_m"] - 0.064) < 1e-12 and "crown_source" in g
    assert abs(g["crown_above_sole_m"] - (g["crown_shell_maxcorner_z_m"] - g["sole_min_z_m"])) < 1e-12   # Data Agent check still shell geometry
