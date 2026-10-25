"""Guard: the V12Z tail-pool term in scripts/v12u_ref_fit.py is default off (V12Z_TAIL_N=0 leaves score() unwrapped)."""
from pathlib import Path
SRC = (Path(__file__).resolve().parents[1] / "scripts" / "v12u_ref_fit.py").read_text()

def test_v12z_default_off():
    assert "TN = int(os.environ.get('V12Z_TAIL_N', '0'))" in SRC
    assert "if TN > 0:" in SRC and "os.environ.get('V12Z_TAIL_W', '0')" in SRC
