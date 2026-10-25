"""D-plane shot-shape relations (label: MODEL, not measured).

Source: D. Tutelman, "3-Dimensional Launch Conditions from Impact Conditions",
https://tutelman.com/golf/ballflight/3dlaunch.php (2007; opened 2026-10-25), building on
Jorgensen's D-plane (The Physics of Golf, 2nd ed. 1999, as cited there).
Sign convention follows TrackMan: face_to_path = face_angle - club_path (deg), positive = face
right of path regardless of dexterity; positive spin axis = curve right. For a left-handed golfer
mirror the lateral axis (negate path, face, axis) -- the relations are symmetric.
Centered strike only: no gear effect (TrackMan "D Plane Tilt" definition), no turf interaction.
"""
from __future__ import annotations

import math

LABEL = "model"


def total_obliqueness_deg(face_to_path_deg: float, spin_loft_deg: float) -> float:
    """cos(Phi) = cos(A) cos(L)  (Tutelman 2007)."""
    a, l = math.radians(face_to_path_deg), math.radians(spin_loft_deg)
    return math.degrees(math.acos(math.cos(a) * math.cos(l)))


def spin_axis_deg(face_to_path_deg: float, spin_loft_deg: float) -> float:
    """tan(spin axis) = tan(A) / tan(L)  (Tutelman 2007). Requires spin_loft > 0."""
    if spin_loft_deg <= 0:
        raise ValueError("spin loft must be > 0")
    return math.degrees(math.atan(math.tan(math.radians(face_to_path_deg)) / math.tan(math.radians(spin_loft_deg))))


def horizontal_launch_deg(face_angle_deg: float, club_path_deg: float, spin_loft_deg: float) -> float:
    """LAx = A (0.96 - 0.0071 Phi) + P, A = F - P (Tutelman 2007 empirical launch fraction)."""
    a = face_angle_deg - club_path_deg
    phi = total_obliqueness_deg(a, spin_loft_deg)
    return a * (0.96 - 0.0071 * phi) + club_path_deg


def face_share_of_start_direction(face_angle_deg: float, club_path_deg: float, spin_loft_deg: float) -> float:
    """Fraction of start direction attributable to face, implied by the model (path weight = 1 - share)."""
    a = face_angle_deg - club_path_deg
    phi = total_obliqueness_deg(a, spin_loft_deg)
    return 0.96 - 0.0071 * phi
