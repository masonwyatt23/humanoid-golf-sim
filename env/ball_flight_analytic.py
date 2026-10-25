# Copied unmodified from <local-path>/sim_proto/ball_flight.py (teammate prototype, see docs/research_sim_realism.md); calibrated to TrackMan PGA driver averages [per that doc].
"""Driver impact model + ball flight (drag, Magnus lift, spin decay, wind) + bounce/roll. Pure numpy.
World: +x target line, +y LEFT of target line (looking down line), +z up. SI units.
"""
import numpy as np
R_BALL, M_BALL, RHO = 0.02135, 0.0459, 1.19
I_BALL = 0.4*M_BALL*R_BALL**2

def impact(v_club, n_face, m_club=0.20, e=0.83, mu=0.22):
    """Two-body impact (center-face hit). v_club: club-head velocity vector at impact; n_face: unit face normal (toward ball)."""
    n = n_face/np.linalg.norm(n_face)
    vn = float(v_club@n); vt = v_club - vn*n
    vt_mag = np.linalg.norm(vt)
    ball_n = (1 + e)*m_club/(m_club + M_BALL)*max(vn, 0.0)           # normal ball speed
    Jn = M_BALL*ball_n
    Jt = min(mu*Jn, M_BALL*vt_mag/3.5)                                # slide vs roll-off limit
    d = vt/vt_mag if vt_mag > 1e-9 else np.zeros(3)
    v_ball = ball_n*n + (Jt/M_BALL)*d
    omega = -(R_BALL*Jt/I_BALL)*np.cross(n, d)                         # contact at -n*R
    return v_ball, omega

def cd_of(v, S=0.085): return max(0.17 + 0.60*S, 0.55 - 0.0085*v)   # Cd rises with spin ratio; point-calibrated to TrackMan PGA-tour avg driver (calib4.py (carry, apex, spin sensitivity))
def cl_of(S): return min(0.45, 0.42*max(S, 1e-6)**0.4)

def simulate(p0, v0, w0, wind=(0, 0, 0), dt=0.001, rho=RHO, t_max=20.0, fairway=True):
    """Returns dict(t, pos, spin, carry, total, apex, lateral_carry, lateral_total, hang, launch angles...)."""
    wind = np.asarray(wind, float)
    p, v, w = np.array(p0, float), np.array(v0, float), np.array(w0, float)
    A = np.pi*R_BALL**2; k = 0.5*rho*A/M_BALL
    ts, ps, ws = [0.0], [p.copy()], [w.copy()]
    t = 0.0; landed = False; carry = None; lat_carry = None; t_land = None; bounces = 0
    def acc(v, w):
        vr = v - wind; s = np.linalg.norm(vr)
        if s < 1e-6: return np.array([0, 0, -9.81])
        S = R_BALL*np.linalg.norm(w)/s
        drag = -k*cd_of(s, S)*s*vr
        wn = np.linalg.norm(w)
        lift = k*cl_of(S)*s*s*(np.cross(w, vr)/(wn*s)) if wn > 1e-6 else 0
        return drag + lift + np.array([0, 0, -9.81])
    while t < t_max:
        a1 = acc(v, w); a2 = acc(v + 0.5*dt*a1, w); a3 = acc(v + 0.5*dt*a2, w); a4 = acc(v + dt*a3, w)
        v_new = v + dt/6*(a1 + 2*a2 + 2*a3 + a4)
        p = p + 0.5*dt*(v + v_new); v = v_new
        w = w*np.exp(-0.03*dt)                                    # ~3 %/s spin decay
        t += dt
        if p[2] <= R_BALL and v[2] < 0:
            p[2] = R_BALL
            if not landed:
                landed = True; carry = p[0] - p0[0]; lat_carry = p[1] - p0[1]; t_land = t; land_speed = np.linalg.norm(v); land_angle = np.degrees(np.arctan2(-v[2], np.hypot(v[0], v[1])))
            vn = -v[2]; en = 0.28 if fairway else 0.20
            vt = np.array([v[0], v[1], 0.0])
            u = vt + np.cross(w, np.array([0, 0, -R_BALL]))           # contact-point slip velocity
            u[2] = 0; um = np.linalg.norm(u)
            Jn = M_BALL*(1 + en)*vn
            Jt = min(0.45*Jn, M_BALL*um/3.5)
            if um > 1e-9:
                d = u/um
                v[0:2] -= (Jt/M_BALL)*d[0:2]
                w = w + (R_BALL/I_BALL)*np.cross(np.array([0, 0, -1.0]), -Jt*d)*(-1)*(-1)
            v[2] = en*vn; bounces += 1
            if vn < 1.0: v[2] = 0.0
        if landed and p[2] <= R_BALL + 1e-6 and abs(v[2]) < 1e-9:
            sp = np.linalg.norm(v[:2])
            if sp < 0.05: break
            v[:2] *= max(0.0, 1 - (0.9*dt)/sp)                         # rolling resistance ~0.9 m/s^2
            w = w*0.98
        ts.append(t); ps.append(p.copy()); ws.append(w.copy())
    ps = np.array(ps); ts = np.array(ts)
    i_apex = int(np.argmax(ps[:, 2]))
    v0n = np.asarray(v0)
    return dict(t=ts, pos=ps, spin=np.array(ws), carry=carry, lat_carry=lat_carry, total=ps[-1, 0] - p0[0], lat_total=ps[-1, 1] - p0[1],
                apex=ps[i_apex, 2] - p0[2], t_apex=ts[i_apex], hang=t_land, land_speed=land_speed if landed else None,
                land_angle=land_angle if landed else None, bounces=bounces,
                ball_speed=float(np.linalg.norm(v0n)), launch=float(np.degrees(np.arctan2(v0n[2], np.hypot(v0n[0], v0n[1])))),
                launch_dir=float(np.degrees(np.arctan2(v0n[1], v0n[0]))), spin_rpm=float(np.linalg.norm(w0)*60/(2*np.pi)),
                backspin_rpm=float(-w0[1]*60/(2*np.pi)), sidespin_rpm=float(w0[2]*60/(2*np.pi)))

if __name__ == '__main__':
    # sanity: tour driver 113 mph club (50.5 m/s), 10.5deg loft, +2 attack, face along path
    for cs in (40, 45, 50.5, 56, 62, 65):
        att = np.radians(2.0); loft = np.radians(12.5)    # dynamic loft at impact
        vc = cs*np.array([np.cos(att), 0, -np.sin(att)*-1*-1*0 + np.sin(att)])
        n = np.array([np.cos(loft), 0, np.sin(loft)])
        vb, w = impact(vc, n)
        r = simulate([0, 0, 0.07], vb, w)
        print('club %.1f m/s (%.0f mph): ball %.1f m/s  smash %.2f  launch %.1f  spin %.0f rpm  carry %.0f m (%.0f yd)  total %.0f m (%.0f yd) apex %.0f m  hang %.1fs' % (
            cs, cs*2.237, r['ball_speed'], r['ball_speed']/cs, r['launch'], r['backspin_rpm'], r['carry'], r['carry']*1.0936, r['total'], r['total']*1.0936, r['apex'], r['hang']))
