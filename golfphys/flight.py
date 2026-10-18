"""Aerodynamic flight ODE (RK4, pure-python floats for speed). World: +x target, +y left, +z up."""
import math
from dataclasses import dataclass, field
from .params import R_BALL, M_BALL, G, Params
from .aero import cd_cl, air_density, viscosity

A_BALL = math.pi * R_BALL ** 2


@dataclass
class FlightResult:
    carry_m: float; lateral_m: float; apex_m: float; t_apex: float; hang_s: float
    descent_deg: float; land_speed: float; land_pos: tuple; land_vel: tuple; land_spin: tuple
    landing_spin_rpm: float; ground_dist_m: float; traj: list = field(default_factory=list)


def fly(p0, v0, w0, p: Params, rho=None, wind=(0.0, 0.0, 0.0), alt_m=0.0, temp_c=15.0, rh=0.0,
        dt=0.01, t_max=15.0, keep_traj=False, ground_z=0.0) -> FlightResult:
    """Integrate from p0 (m), v0 (m/s), w0 (rad/s, vector) until the ball centre drops to ground_z + R.
    wind = air velocity over the ground (m/s), e.g. (-5,0,0) is a 5 m/s headwind."""
    if rho is None:
        rho = air_density(alt_m, temp_c, rh)
    mu = viscosity(temp_c)
    k = 0.5 * rho * A_BALL / M_BALL
    x, y, z = p0; vx, vy, vz = v0; wx, wy, wz = w0
    wnd = wind; zg = ground_z + R_BALL
    decay = p.spin_decay
    traj = [(0.0, x, y, z)] if keep_traj else []

    def acc(vx, vy, vz, wx, wy, wz):
        rx, ry, rz = vx - wnd[0], vy - wnd[1], vz - wnd[2]
        s = math.sqrt(rx * rx + ry * ry + rz * rz)
        if s < 1e-6:
            return 0.0, 0.0, -G
        wn = math.sqrt(wx * wx + wy * wy + wz * wz)
        # spin component perpendicular to relative velocity drives lift
        cx, cy, cz = wy * rz - wz * ry, wz * rx - wx * rz, wx * ry - wy * rx   # w x r
        cn = math.sqrt(cx * cx + cy * cy + cz * cz)
        S = cn / (s * s) * R_BALL            # = R |w_perp| / s
        cd, cl = cd_cl(s, S, p, rho, mu)
        fd = -k * cd * s
        ax, ay, az = fd * rx, fd * ry, fd * rz - G
        if cn > 1e-9:
            fl = k * cl * s * s / cn
            ax += fl * cx; ay += fl * cy; az += fl * cz
        return ax, ay, az

    t = 0.0; apex = z; t_apex = 0.0
    while t < t_max:
        a1 = acc(vx, vy, vz, wx, wy, wz)
        a2 = acc(vx + .5 * dt * a1[0], vy + .5 * dt * a1[1], vz + .5 * dt * a1[2], wx, wy, wz)
        a3 = acc(vx + .5 * dt * a2[0], vy + .5 * dt * a2[1], vz + .5 * dt * a2[2], wx, wy, wz)
        a4 = acc(vx + dt * a3[0], vy + dt * a3[1], vz + dt * a3[2], wx, wy, wz)
        nvx = vx + dt / 6 * (a1[0] + 2 * a2[0] + 2 * a3[0] + a4[0])
        nvy = vy + dt / 6 * (a1[1] + 2 * a2[1] + 2 * a3[1] + a4[1])
        nvz = vz + dt / 6 * (a1[2] + 2 * a2[2] + 2 * a3[2] + a4[2])
        nx, ny, nz = x + .5 * dt * (vx + nvx), y + .5 * dt * (vy + nvy), z + .5 * dt * (vz + nvz)
        f = math.exp(-decay * dt)
        nwx, nwy, nwz = wx * f, wy * f, wz * f
        if nz <= zg and nvz < 0:
            fr = (z - zg) / max(z - nz, 1e-12)      # linear interpolation to ground crossing
            lx, ly = x + fr * (nx - x), y + fr * (ny - y)
            lvx, lvy, lvz = vx + fr * (nvx - vx), vy + fr * (nvy - vy), vz + fr * (nvz - vz)
            lw = (wx + fr * (nwx - wx), wy + fr * (nwy - wy), wz + fr * (nwz - wz))
            t_l = t + fr * dt
            hs = math.hypot(lvx, lvy)
            sp = math.sqrt(lvx ** 2 + lvy ** 2 + lvz ** 2)
            return FlightResult(
                carry_m=math.hypot(lx - p0[0], ly - p0[1]), lateral_m=ly - p0[1], apex_m=apex - p0[2], t_apex=t_apex,
                hang_s=t_l, descent_deg=math.degrees(math.atan2(-lvz, hs)), land_speed=sp, land_pos=(lx, ly, zg),
                land_vel=(lvx, lvy, lvz), land_spin=lw,
                landing_spin_rpm=math.sqrt(sum(c * c for c in lw)) * 60 / (2 * math.pi),
                ground_dist_m=lx - p0[0], traj=traj)
        x, y, z, vx, vy, vz, wx, wy, wz = nx, ny, nz, nvx, nvy, nvz, nwx, nwy, nwz
        t += dt
        if z > apex:
            apex = z; t_apex = t
        if keep_traj:
            traj.append((t, x, y, z))
    return FlightResult(math.hypot(x - p0[0], y - p0[1]), y - p0[1], apex - p0[2], t_apex, t, 0.0, 0.0, (x, y, z), (vx, vy, vz),
                        (wx, wy, wz), 0.0, x - p0[0], traj)
