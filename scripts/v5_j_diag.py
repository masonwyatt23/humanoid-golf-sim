import sys, numpy as np, json, pickle
from train.v5_train_j import JEnv
from stable_baselines3 import PPO
RSI=tuple(float(x) for x in sys.argv[2].split(",")) if len(sys.argv)>2 else (1,0,0)
d=sys.argv[1]; A=json.load(open(d.rsplit("/",1)[0]+"/args.json"))
keys={tuple(k.split("|")):v for k,v in json.load(open(A["keys"])).items()}
pol=PPO.load(d+".zip",device="cpu"); vn=pickle.load(open(d+"_vecnorm.pkl","rb"))
print("log_std mean", float(pol.policy.log_std.mean()), "obs_rms var min/max", float(vn.obs_rms.var.min()), float(vn.obs_rms.var.max()), "clip", vn.clip_obs)
def run(det, scale_noise=1.0, n=16, tw=0.0):
    e=JEnv(seed=999,keys=keys,res_scale=A["res_scale"],t_down=A["t_down"]); e.rsi=RSI; e.env.arm_dist=0.6; e.track_w=tw
    res=[]; 
    for s in range(n):
        o,_=e.reset(seed=4000+s); done=False
        while not done:
            x=np.clip((o[None]-vn.obs_rms.mean)/np.sqrt(vn.obs_rms.var+vn.epsilon),-vn.clip_obs,vn.clip_obs)
            a=pol.predict(x,deterministic=det)[0][0]
            o,r,te,tr,info=e.step(a); done=te or tr
        ep=info["ep"]; res.append((ep["contact"],ep["club_mph"],ep["carry"],e.env.min_dist,ep["fell"] or ep["unstable"]))
    c=[r for r in res if r[0]]
    print("det" if det else "stoch", "contact",len(c)/n,"mph",np.mean([r[1] for r in c]) if c else 0,"carry",np.mean([r[2] for r in c]) if c else 0,"min_dist med",np.median([r[3] for r in res]),"fell",np.mean([r[4] for r in res]))
run(True); run(False)
