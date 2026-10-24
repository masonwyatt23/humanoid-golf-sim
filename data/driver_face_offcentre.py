"""Driver face geometry + off-centre (face-edge) adjustment: OPT-IN proposal (Data Agent, 2026-10-24 ET).

Nothing in golfphys/, env/, eval/ or train/ is changed. `face_edge_adjust()` takes a golfphys CENTRE-strike result and a strike
offset and returns provisional smash / spin / launch plus a status flag. Every constant is tagged in
data/references/driver_face_offcentre_refs.json (measured / model / derived). Provisional: low confidence beyond +/-12.7 mm.
"""
import json
from pathlib import Path

REFS = Path(__file__).resolve().parent.parent / "data/references/driver_face_offcentre_refs.json"

FACE_HEIGHT_MM = 53.0        # measured spec: Wishon 919THI (53), R22-07 test driver (53); Wishon 719MW 50
FACE_WIDTH_MM = 105.0        # spec: Wishon 919THI 105, 719MW 106
MEASURED_DZ_MM = 12.7        # Hotstix robot data spans +/-0.5 in
GEAR_V_RPM_PER_MM_AT_148 = 51.3   # derived: Hotstix 3165-1862 rpm over 1.0 in at 100 mph club. 148 mph = TrajectoWare MODEL ball speed (Tutelman), NOT measured
LAUNCH_DEG_PER_MM = 0.20     # derived: Hotstix 4.3->9.4 deg over 1.0 in
SMASH_K_PER_MM2 = 8.6e-5     # LEGACY (superseded by R22-07 table), derived: MyGolfSpy low-face smash -0.7% vs centre, ASSUMING band-mean |dz| ~9 mm (band edge 4.5 mm)


FAIL_DZ_MM = 26.5            # measured spec, single brand (Wishon 919THI 53 mm face), provisional
WARN_DZ_MM = 15.0
SIM_BOX_HALF_MM = 32.0       # sim head is a 64 mm-tall box (info only)


# USGA/R&A R22-07 Figs 1-2: DERIVED FROM DIGITIZED FIGURE, APPROXIMATE (raw digitized points held locally pending review, not in this repo;
# only these derived constants are published). Fig 1: mean of 3 tee positions,
# ball speed / centre-strike ball speed vs dz (mm from face centre; 53 mm face, robot ~115 mph, one driver). n=2 series at -18/-21.
R2207_DZ = [-21, -18, -15, -12, -9, -6, -3, 0, 3, 6, 9, 12, 15, 18, 21]
R2207_RATIO = [0.9368, 0.9422, 0.9495, 0.9631, 0.9773, 0.9882, 0.9953, 1.0, 1.0012, 0.9999, 0.9914, 0.9775, 0.9634, 0.9478, 0.9254]
R2207_LOW_SLOPE_PER_MM = 0.00178   # extrapolation below -21 mm (last measured segment), derived
# R22-07 Fig 2 spin minus centre spin (rpm, at ~167 mph ball): peak +963 at -15 mm then falls (+539 at -21)
R2207_SPIN_DZ = [-21, -18, -15, -12, -9, -6, -3, 0, 3, 6, 9, 12, 15, 18, 21]
R2207_SPIN_DELTA = [539, 864, 963, 852, 679, 600, 299, 0, -280, -564, -817, -1060, -1074, -858, -330]


def r2207_ratio(dz_mm):
    import numpy as np
    if dz_mm < R2207_DZ[0]:
        return R2207_RATIO[0] + R2207_LOW_SLOPE_PER_MM * (dz_mm - R2207_DZ[0])
    if dz_mm > R2207_DZ[-1]:
        return None
    return float(np.interp(dz_mm, R2207_DZ, R2207_RATIO))


def r2207_spin_delta(dz_mm, ball_mph):
    import numpy as np
    if not (R2207_SPIN_DZ[0] <= dz_mm <= R2207_SPIN_DZ[-1]):
        return None
    return float(np.interp(dz_mm, R2207_SPIN_DZ, R2207_SPIN_DELTA)) * ball_mph / 167.0


def status(dz_mm, dx_mm=0.0):
    if abs(dz_mm) > FAIL_DZ_MM or abs(dx_mm) > FACE_WIDTH_MM / 2:
        return "fail"                # off a 53 mm face (measured spec, single brand, provisional): invalid strike
    if abs(dz_mm) > WARN_DZ_MM:
        return "warn"
    if abs(dz_mm) > MEASURED_DZ_MM:
        return "info_outside_measured"
    return "measured_range"


def face_edge_adjust(centre, dz_mm, dx_mm=0.0):
    """SIDE-BY-SIDE scoring model only, never a default. centre: golfphys CENTRE-strike result (must carry centre_dz_mm == 0
    or y_high_m == 0, else ValueError: prevents double-counting golfphys's own gear effect) with smash, spin_rpm, launch_deg,
    ball_speed_mph. dz_mm + = above face centre. Returns capped AND linear spin; a spin check passes only if BOTH pass.
    Levelling-off (cap at +/-12.7 mm) is UNVERIFIED until R22-07 Fig 1/2 is read."""
    cdz = centre.get("centre_dz_mm", None)
    if cdz is None and "y_high_m" in centre:
        cdz = centre["y_high_m"] * 1000.0
    if cdz is None or abs(cdz) > 1e-9:
        raise ValueError("face_edge_adjust needs a golfphys CENTRE-strike result (centre_dz_mm=0 or y_high_m=0)")
    st = status(dz_mm, dx_mm)
    info = dict(status=st, within_sim_box=abs(dz_mm) <= SIM_BOX_HALF_MM, outside_measured=abs(dz_mm) > MEASURED_DZ_MM)
    if st == "fail":
        return dict(info, valid=False, smash=None, spin_rpm_capped=None, spin_rpm_linear=None, launch_deg=None)
    k = GEAR_V_RPM_PER_MM_AT_148 * centre["ball_speed_mph"] / 148.0
    dzs = max(-MEASURED_DZ_MM, min(MEASURED_DZ_MM, dz_mm))
    rr = r2207_ratio(dz_mm); sd = r2207_spin_delta(dz_mm, centre["ball_speed_mph"])
    return dict(info, valid=True, smash=None if rr is None else centre["smash"] * rr,
                smash_legacy_quadratic=centre["smash"] * (1.0 - SMASH_K_PER_MM2 * dz_mm ** 2),
                spin_rpm_r2207=None if sd is None else centre["spin_rpm"] + sd,
                spin_rpm_capped=max(0.0, centre["spin_rpm"] - k * dzs), spin_rpm_linear=max(0.0, centre["spin_rpm"] - k * dz_mm),
                launch_deg=centre["launch_deg"] + LAUNCH_DEG_PER_MM * dz_mm, smash_confidence="MEDIUM within -21..+21 mm (R22-07 digitized, one driver, 115 mph robot); LOW beyond; model-only pass does not count")
