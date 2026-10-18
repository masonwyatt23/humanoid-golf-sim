"""Read-only probe (does not edit env/): runs random-action contacts in HumanoidGolfEnv and prints the club-head geom local axes in world coordinates at first contact.
Run from the project root with env importable: cd /workspace/artifacts/humanoid-golf-scott && /workspace/golfvenv/bin/python /workspace/artifacts/hgs-realism/scripts/toe_sign_probe.py"""
import sys, numpy as np, mujoco
sys.path.insert(0,'.')
from env.humanoid_golf_env import HumanoidGolfEnv
for xml in ["humanoid_golf_v3.xml","humanoid_golf_v4_power.xml"]:
  for hand in ["right","left"]:
    env=HumanoidGolfEnv(model_xml=xml,address_pose="fixed",pin_torso=True,tee_height=0.02,handedness=hand,loft_deg=-27 if False else None)
    rng=np.random.default_rng(0)
    n=0
    for ep in range(60):
        env.reset(seed=ep); done=False
        a=np.zeros(env.model.nu); a[:]=rng.uniform(-1,1,env.model.nu)
        for t in range(120):
            obs,r,te,tr,info=env.step(np.clip(a+0.2*rng.standard_normal(env.model.nu),-1,1))
            if env.true_contact:
                d=env.data;g=env._club_geom;R=d.geom_xmat[g].reshape(3,3)
                print(xml,hand,"contact ep",ep,"t",t,"geom local y in world",R[:,1].round(3),"local x (face)",R[:,0].round(3),"face_off(dy,dz)",env._face_off,"head pos",d.geom_xpos[g].round(3),"ball",d.xpos[env._ball_id].round(3),"torso",d.xpos[env.model.body('torso').id].round(3))
                n+=1; break
            if te or tr: break
        if n>=3: break
    print(xml,hand,"contacts",n)
