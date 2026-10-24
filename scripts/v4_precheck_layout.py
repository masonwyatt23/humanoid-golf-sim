"""Pre-check (Evaluator 2026-10-24): obs/action layout and reference keys of an evalsnap checkpoint vs the scored read-only Trainer export.
Usage: python scripts/v4_precheck_layout.py <ckpt_base> <export_repo> <trainer_clone_for_keys_compare>. Prints one OK/MISMATCH line; exit 1 on mismatch."""
import sys, os, json, hashlib, pickle
ck, repo, clone = sys.argv[1:4]
sys.path.insert(0, repo)
from stable_baselines3 import PPO
from train.v5_train_j import JEnv
A = json.load(open(os.path.join(os.path.dirname(ck), "args.json")))
kp = os.path.join(repo, A["keys"]); kc = os.path.join(clone, A["keys"])
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None
keys = {tuple(k.split("|")): v for k, v in json.load(open(kp)).items()}
e = JEnv(dt=0.002, seed=123, keys=keys, res_scale=A["res_scale"], t_down=A["t_down"])
if A.get("env_v4") and hasattr(e.env, "set_env_v4"): pass
m = PPO.load(ck, device="cpu")
vn = pickle.load(open(ck + "_vecnorm.pkl", "rb"))
o_env, a_env = tuple(e.observation_space.shape), tuple(e.action_space.shape)
o_m, a_m = tuple(m.observation_space.shape), tuple(m.action_space.shape)
o_vn = tuple(vn.obs_rms.mean.shape)
ok = (o_env == o_m == o_vn) and (a_env == a_m) and md5(kp) is not None
print(("LAYOUT_OK" if ok else "LAYOUT_MISMATCH"), dict(obs_env=o_env, obs_model=o_m, obs_vecnorm=o_vn, act_env=a_env, act_model=a_m,
      keys=A["keys"], n_keys=len(keys), keys_md5_export=md5(kp), keys_md5_trainer_head=md5(kc), keys_match_trainer_head=(md5(kp) == md5(kc))))
sys.exit(0 if ok else 1)
