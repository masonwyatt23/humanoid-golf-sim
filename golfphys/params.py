"""Parameter set + loader. Values default from data/references/golfphys_coefficients.json when present."""
from dataclasses import dataclass, field, asdict, replace
import json
from pathlib import Path

JSON = Path(__file__).resolve().parent.parent / "data/references/golfphys_coefficients.json"

R_BALL = 0.02135          # m  (USGA/R&A min diameter 42.67 mm)
M_BALL = 0.0459           # kg (max 45.93 g)
I_BALL = 0.4 * M_BALL * R_BALL ** 2   # uniform-sphere approximation (ASSUMPTION; real balls ~0.4-0.45 m R^2)
G = 9.80665


@dataclass
class Params:
    # --- impact ---
    m_head: float = 0.200          # kg driver head (typical 195-205 g)
    e0: float = 0.845              # centre-hit effective COR at e_ref_speed  (CALIBRATED, see JSON)
    e_slope: float = 0.0           # d e / d (normal speed m/s)  (CALIBRATED if nonzero)
    e_ref_speed: float = 50.0
    s_t: float = 0.62              # tangential impulse efficiency vs full-roll (CALIBRATED)
    s_t_slope: float = 0.0         # per degree of spin loft (CALIBRATED if nonzero)
    I_head_h: float = 5.0e-4       # kg m^2 about horizontal axis (Tutelman GE3 4000-5900 g cm^2, fetched)
    I_head_v: float = 3.0e-4       # kg m^2 about vertical axis (1/2-2/3 of Ih)
    gear_h_rpm_per_mph_in: float = 16.4   # Tutelman GE3 (fetched) - used only when gear_mode='tutelman'
    gear_v_rpm_per_mph_in: float = 25.0
    gear_mode: str = "tutelman"    # 'tutelman' (published empirical) | 'none'
    bulge_radius: float = 0.254    # m (10 in standard driver bulge; UNVERIFIED here)
    roll_radius: float = 0.305     # m (12 in standard roll; UNVERIFIED here)
    # --- aero ---
    aero_model: str = "bh_fit"     # 'bh_fit' | 'smits_smith_sec' | 'env_legacy'
    cd_scale: float = 1.0          # (CALIBRATED)
    cl_scale: float = 1.0          # (CALIBRATED)
    cd_plateau: float = 0.235      # no-spin Cd just past the drag crisis (ASSUMPTION, B&H qualitative)
    cd_re_slope: float = 0.012     # per 1e5 Re above 1.5e5 (ASSUMPTION; B&H: slow rise after crisis)
    cd_spin_slope: float = 0.35    # induced-drag term dCd/dS (ASSUMPTION)
    re_crit: float = 6.0e4         # drag crisis centre for dimpled ball (IJIMT/B&H snippet 4-6e4)
    cd_sub: float = 0.45           # subcritical Cd (ASSUMPTION)
    cl_cap: float = 0.32
    spin_decay: float = 0.040      # 1/s exponential (Tutelman 3.3-4 %/s, snippet)
    # --- bounce / roll ---
    turf: str = "normal"
    # turf table lives in bounce.TURF (overridden from JSON)


def load_params(path=JSON, **over) -> Params:
    p = Params()
    try:
        d = json.load(open(path))
        for k, v in d.get("params", {}).items():
            if hasattr(p, k):
                setattr(p, k, v["value"] if isinstance(v, dict) else v)
    except FileNotFoundError:
        pass
    return replace(p, **over) if over else p
