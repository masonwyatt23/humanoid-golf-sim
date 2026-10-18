"""golfphys: standalone ball/club flight model (impact -> aerodynamic flight -> bounce/roll).

Pure Python + numpy, SI units, world frame +x target line, +y LEFT of the line, +z up.
See docs/GOLF_PHYSICS_SIM.md. Parameters live in data/references/golfphys_coefficients.json
(each tagged calibrated / assumption / published, with source and fetched-vs-snippet).
"""
from .params import Params, load_params
from .impact import Delivery, Strike, impact, impact_vec
from .aero import air_density, cd_cl
from .flight import fly, FlightResult
from .bounce import bounce_roll, TURF
from .sim import simulate_shot, ShotResult
from .contact import contact_to_ball, env_contact_to_shot

M_TO_YD = 1.0 / 0.9144
MPH_TO_MS = 0.44704
__all__ = [n for n in dir() if not n.startswith("_")]
