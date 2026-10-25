"""Evaluate a flat keys file with the V8 objective (V5_ENV_V4=1; V7_NS starts). Usage: python -m scripts.v8_ref_eval keys.json"""
import sys, json, numpy as np
import scripts.v8_ref_fit as F, scripts.v7_ref_fit as V
d = json.load(open(sys.argv[1])); V.KEYS = [tuple(k.split("|")) for k in d]; V.BASE = [float(v) for v in d.values()]
print(json.dumps(F.score(np.zeros(len(V.KEYS))), default=float))
