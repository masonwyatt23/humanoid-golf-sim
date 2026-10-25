"""Strike-height probe: per-episode start elbow/shoulder vs face-local contact dz (and outcome). python -m eval.strike_probe cfg.json eps seed [overrides_json]  -> prints fit"""
import sys,json,numpy as np
from eval.eval_scripted_cfg import base as B0
from eval.env_factory import make_env
cfg=json.load(open(sys.argv[1])); cfg.pop("description",None); cfg.pop("hypothetical",None); kw=dict(B0); kw.update(cfg); kw["script"]=dict(B0["script"],**cfg.get("script",{}))
ov=json.loads(sys.argv[4]) if len(sys.argv)>4 else {}
for k,v in ov.items():
    if k.startswith("script."): kw["script"][k[7:]]=v
    else: kw[k]=v
env=make_env(kw); R=[]
for i in range(int(sys.argv[2])):
    env.reset(seed=int(sys.argv[3])+i); el,sh=env.data.qpos[env._q_el],env.data.qpos[env._q_sp]; hp=env.data.geom_xpos[env._club_geom].copy()-env.data.xpos[env._ball_id]; bx=env.data.qpos[:3].copy(); d=False
    while not d: _,_,te,tr,info=env.step(np.zeros(5,np.float32)); d=te or tr
    fo=env._face_off or (np.nan,np.nan); R.append((el,sh,fo[0],fo[1],np.degrees(info["launch_elevation"]),info["ball_lateral"],info["max_ball_x"],hp[0],hp[1],hp[2],bx[0],bx[1]))
R=np.array(R); ok=~np.isnan(R[:,3])
A=np.c_[np.ones(ok.sum()),R[ok,0],R[ok,1]]; c,*_=np.linalg.lstsq(A,R[ok,3],rcond=None)
print("n contact",ok.sum(),"dz mean %.4f std %.4f"%(R[ok,3].mean(),R[ok,3].std()),"fit dz = %.4f + %.4f*el + %.4f*sh"%tuple(c),"resid std %.4f"%np.std(R[ok,3]-A@c))
for j,n in ((7,"head-ball dx"),(8,"dy"),(9,"dz"),(10,"ball x"),(11,"ball y"),(0,"el"),(1,"sh")): print(n,"corr with strike dz %.2f"%np.corrcoef(R[ok,j],R[ok,3])[0,1],"std %.4f"%R[ok,j].std())
print("launch mean %.1f std %.1f; frac launch<8: %.2f; |y|>8: %d; dist<200: %d"%(R[:,4].mean(),R[:,4].std(),(R[:,4]<8).mean(),(abs(R[:,5])>8).sum(),(R[:,6]<200).sum()))
import os; np.save(os.environ.get("OUT",os.path.join(__import__("tempfile").gettempdir(),"strike_%s.npy"%sys.argv[1].split("/")[-1][:-5])),R)
