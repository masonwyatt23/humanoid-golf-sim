"""Load MuJoCo Menagerie Unitree G1, attach a driver-like club on the right wrist and
a soft two-hand grip constraint to the left wrist. Verified to compile + step in MuJoCo 3.x.
Usage: python g1_with_club.py [--menagerie /path/to/menagerie | /path/to/menagerie]   (needs: pip install mujoco numpy)
Menagerie path precedence: --menagerie arg (or first positional arg) > $MENAGERIE_PATH > $MENAGERIE_DIR (legacy) > a menagerie/ checkout next to this repo if it exists."""
import os, sys, numpy as np, mujoco


def resolve_menagerie(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    for i, a in enumerate(argv):
        if a == "--menagerie" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--menagerie="):
            return a.split("=", 1)[1]
    pos = [a for a in argv if not a.startswith("-")]
    if pos:
        return pos[0]
    for k in ("MENAGERIE_PATH", "MENAGERIE_DIR"):
        if os.environ.get(k):
            return os.environ[k]
    _sib = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "menagerie")
    if os.path.isdir(_sib):
        return _sib
    raise SystemExit("MuJoCo Menagerie not found: pass --menagerie PATH or set MENAGERIE_PATH")


MENAG = resolve_menagerie()
CLUB_LEN, GRIP_SEP = 1.15, 0.12        # driver ~45 in; left hand 12 cm below right hand
SHAFT_M, HEAD_M = 0.07, 0.20           # kg (shaft+grip, head) -> total ~0.27-0.30 kg like a real driver

def build():
    spec = mujoco.MjSpec.from_file(f"{MENAG}/unitree_g1/scene.xml")
    rw = spec.body("right_wrist_yaw_link")
    # wrist-yaw-link frame: +x along the hand, z = wrist yaw axis. Shaft along local z, gripped at (0.10,0,0)
    club = rw.add_body(name="club", pos=[0.10, 0, 0])
    club.add_geom(name="shaft", type=mujoco.mjtGeom.mjGEOM_CAPSULE, fromto=[0,0,0.20-CLUB_LEN,0,0,0.20],
                  size=[0.008,0,0], mass=SHAFT_M, contype=0, conaffinity=0, rgba=[.2,.2,.2,1])
    club.add_geom(name="head", type=mujoco.mjtGeom.mjGEOM_BOX, pos=[0.03,0,0.20-CLUB_LEN],
                  size=[0.05,0.05,0.02], mass=HEAD_M, contype=1, conaffinity=1, rgba=[.7,.7,.75,1])
    club.add_site(name="grip_right", pos=[0,0,0])
    club.add_site(name="grip_left", pos=[0,0,-GRIP_SEP])
    club.add_site(name="clubhead", pos=[0.03,0,0.20-CLUB_LEN])
    lw = spec.body("left_wrist_yaw_link")
    lw.add_site(name="lhand", pos=[0.10,0,0])
    # two-hand grip: left palm point glued to the shaft point (soft connect so IK/RL can't blow up)
    eq = spec.add_equality(name="left_grip", type=mujoco.mjtEq.mjEQ_CONNECT,
                           objtype=mujoco.mjtObj.mjOBJ_SITE, name1="lhand", name2="grip_left")
    eq.solref = [0.01, 1]
    return spec.compile()

if __name__ == "__main__":
    m = build(); d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, 0) if m.nkey else None
    for _ in range(500): mujoco.mj_step(m, d)
    sid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "clubhead")
    print("OK nq", m.nq, "nu", m.nu, "mass %.2f" % m.body_mass.sum(), "clubhead pos", d.site_xpos[sid].round(3))
