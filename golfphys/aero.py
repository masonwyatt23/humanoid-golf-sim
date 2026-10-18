"""Air density and Cd/Cl(Re, S) for a dimpled golf ball.

Models
 'bh_fit'          Cl = cl_scale * min(cap, 0.54 S^0.4) (Bearman & Harvey 1976 Fig.9 curve fit as quoted in the literature;
                   snippet-level source, valid Re > 1.26e5), Cd = no-spin Cd(Re) + k S (shape from B&H qualitative description).
 'smits_smith_sec' Cl = 1.99 S - 3.25 S^2 (secondary implementation; UNVERIFIED), same Cd.
 'env_legacy'      the env's cd_of/cl_of (env/ball_flight_analytic.py) for comparison.
S = R w / V (spin ratio). Re = rho V D / mu.
"""
import math

MU_AIR = 1.81e-5
D_BALL = 0.0427


def air_density(alt_m=0.0, temp_c=15.0, rh=0.0, pressure_pa=None):
    """Moist-air density (kg/m3). Barometric (ISA) pressure if not given; Magnus-Tetens vapour pressure."""
    if pressure_pa is None:
        pressure_pa = 101325.0 * (1 - 2.25577e-5 * alt_m) ** 5.25588
    T = temp_c + 273.15
    es = 610.94 * math.exp(17.625 * temp_c / (temp_c + 243.04))
    pv = max(0.0, min(1.0, rh)) * es
    return (pressure_pa - pv) / (287.058 * T) + pv / (461.495 * T)


def viscosity(temp_c=15.0):
    T = temp_c + 273.15
    return 1.716e-5 * (T / 273.15) ** 1.5 * (273.15 + 110.4) / (T + 110.4)   # Sutherland


def cd_cl(V, S, p, rho=1.19, mu=MU_AIR):
    """Return (Cd, Cl) at airspeed V (m/s) and spin ratio S, using Params p."""
    if p.aero_model == "env_legacy":
        return max(0.17 + 0.60 * S, 0.55 - 0.0085 * V), min(0.45, 0.42 * max(S, 1e-6) ** 0.4)
    Re = rho * V * D_BALL / mu
    # no-spin Cd: smooth drag crisis at re_crit, then slow linear rise
    cris = 1.0 / (1.0 + math.exp((Re - p.re_crit) / (0.12 * p.re_crit)))
    cd0 = p.cd_plateau + p.cd_re_slope * max(0.0, (Re - 1.5e5) / 1e5)
    cd0 = cd0 + (p.cd_sub - p.cd_plateau) * cris
    cd = p.cd_scale * (cd0 + p.cd_spin_slope * S)
    if p.aero_model == "smits_smith_sec":
        cl = 1.99 * S - 3.25 * S * S
        cl = max(cl, 0.0) if S < 0.306 else 0.0
    else:
        cl = 0.54 * max(S, 1e-9) ** 0.4
    return cd, p.cl_scale * min(p.cl_cap, cl)
