"""Swept-contact test: native MuJoCo contact vs env swept_hit for a head box (v5 size) crossing a ball at 20-110 mph, dt 0.0005/0.001/0.002.
Head driven kinematically (mocap) along +x with random lateral/vertical offsets inside the face, 400 trials per cell."""
import numpy as np, mujoco, json, sys
sys.path.insert(0,'.')
from env.v5_golf_env import swept_hit
HALF=[0.045,0.055,0.032]; R=0.021335
xml=f"""<mujoco><option gravity="0 0 0"/><worldbody>
<body name="h" mocap="true"><geom name="head" type="box" size="{HALF[0]} {HALF[1]} {HALF[2]}" contype="2" conaffinity="2"/></body>
<body name="b" pos="0 0 0"><freejoint/><geom name="ball" type="sphere" size="{R}" mass="0.046" contype="2" conaffinity="2"/></body></worldbody></mujoco>"""
rng=np.random.default_rng(0); out={}
for dt in (0.0005,0.001,0.002):
    for mph in (20,60,90,110):
        v=mph*0.44704; nat=sw=either=0; N=300
        for _ in range(N):
            m=mujoco.MjModel.from_xml_string(xml); m.opt.timestep=dt; d=mujoco.MjData(m)
            oy,oz=rng.uniform(-0.03,0.03,2); ph=rng.uniform(0,dt*v)  # random sub-step phase of arrival
            x=-0.4+ph; hitn=hits=False
            while x<0.4:
                p0=np.array([x,oy,oz]); x+=v*dt; p1=np.array([x,oy,oz])
                d.mocap_pos[0]=p1; d.qpos[:3]=0; d.qvel[:]=0
                I=np.eye(3)
                if swept_hit(p0,I,p1,I,np.zeros(3),HALF,R) is not None: hits=True
                mujoco.mj_step(m,d)
                if d.ncon>0: hitn=True
                if hitn or hits: break
            nat+=hitn; sw+=hits; either+=(hitn or hits)
        out[f"dt{dt}_mph{mph}"]=dict(native=nat/N,swept=sw/N,either=either/N)
        print(dt,mph,out[f"dt{dt}_mph{mph}"],flush=True)
json.dump(out,open('results/v5_tunnel_test.json','w'),indent=1)
