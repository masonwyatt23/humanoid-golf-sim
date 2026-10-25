"""Summarise the V19 official grade of V18w_s661 100k (Evaluator 2026-10-25) and compare with the Trainer's LOCAL (not official) JSONs.
Usage: python _summ_V19.py [trainer_clone]"""
import json, os, sys
O = os.path.dirname(os.path.abspath(__file__)); TR = sys.argv[1] if len(sys.argv) > 1 else None; T = "V18w_s661_100k"; TN = "V18w_s661_100000"
ROWS = [("15in_v4", "v4 1.5in MAIN (gating)", "{n}_v3_tee15in_v4h_v4.json"), ("crown16_v4", "v4 crown16 INFO", "{n}_v3_teedefault_v4h_v4.json"),
        ("15in_v3c", "v3c 1.5in", "{n}_v3_tee15in_v4h.json"), ("15in_v3d", "v3d 1.5in", "{n}_v3d_tee15in_v4h.json"),
        ("15in_v41_v4", "v4.1 robustness (re-grounded, info only, non-gating)", None)]
def g(c, k): return (c.get(k) or {}).get("values") or {}
def summ(d):
    c = d["checks"]; st = lambda s: sorted(k for k, v in c.items() if v.get("status") == s); rb = g(c, "mine/robustness"); sh = rb.get("shot", {})
    q = lambda k: {x: sh.get(k, {}).get(x) for x in ("median", "p10", "p90")}
    return dict(P=d.get("checks_passed"), W=d.get("n_warn"), F=d.get("n_fail"), verdict=d.get("verdict"), fails=st("fail"), warns=st("warn"),
                rb=(rb.get("contact_frac"), rb.get("start_direction_pass_frac"), rb.get("lead_foot_plant_pass_frac")), club=q("club_speed_mph"), tc=q("total_over_carry"),
                rspin=q("spin_rpm"), smash=q("smash"), why=(c.get("mine/robustness") or {}).get("why"), nclub=g(c, "shot/club_speed_mph"), nspin=g(c, "shot/spin_rpm"),
                ntc=g(c, "shot/total_over_carry"), dz=g(c, "mine/strike_dz_info"), dy=g(c, "mine/strike_dy_info"), checks={k: v.get("status") for k, v in c.items()})
S = {}
for tt, lab, tp in ROWS:
    p = os.path.join(O, f"realism_v5_{T}_{tt}_gateoff_gp_arm06.json")
    if not os.path.exists(p): print(f"## {lab}: missing"); continue
    s = summ(json.load(open(p))); S[tt] = s
    print(f"## {lab}: {s['verdict']} {s['P']}/{s['W']}/{s['F']}\n fails {s['fails']}\n warns {s['warns']}\n robust {s['rb']} club {s['club']} spin {s['rspin']} t/c {s['tc']} smash {s['smash']}\n why {s['why']}\n nominal club {s['nclub']} spin {s['nspin']} t/c {s['ntc']}\n dz {json.dumps(s['dz'])[:400]}\n dy {json.dumps(s['dy'])[:400]}")
    if TR and tp:
        q = os.path.join(TR, "results/v5_runs/stageJ_harness", tp.format(n=TN)); r = summ(json.load(open(q)))
        diff = {k: (s['checks'].get(k), r['checks'].get(k)) for k in set(s['checks']) | set(r['checks']) if s['checks'].get(k) != r['checks'].get(k)}
        num = [k for k in ("P", "W", "F", "verdict", "rb", "club", "tc", "rspin", "smash", "nclub", "nspin", "ntc", "dz", "dy") if s[k] != r[k]]
        print(f" vs Trainer {os.path.basename(q)} (LOCAL NOT OFFICIAL): {r['verdict']} {r['P']}/{r['W']}/{r['F']}; status diffs (ours, Trainer) {diff}; differing fields {num}")
for tt in ("v5_heldout12", "v5dplane"):
    p = os.path.join(O, f"realism_v5_{T}_15in_{tt}_gateoff_gp_arm06.json")
    if not os.path.exists(p): print(f"## {tt}: missing"); continue
    d = json.load(open(p)); v = d.get("v5") or {}
    print(f"## {tt} (NON-GATING): v4 verdict {v.get('v4_verdict')}")
    for k, r in (v.get("rows") or {}).items():
        if r.get("status") == "n/a": continue
        print(f" {k}: {r.get('status')} {json.dumps(r.get('values'), default=str)[:900]}")
