"""Harness v4 (2026-10-24, Orchestrator-approved single v4 re-baseline). Starts from v3d (eval/harness_v3d.py) bands and rules UNCHANGED:
spin 2000-3700 at 70-85 mph (derived), pelvis floor 250 deg/s, thorax/arm tie or inversion <= 30 ms, arm->club >= 20 ms, robustness club p10 >= 0.93x median
(low confidence), strike_height FAIL edge = env face_limits() vertical half-height. What v4 adds:
  * the run must use the v4 env (tee_info.head.mode == 'v4', cross-checked against V4_SPEC by the worker), else the verdict is 'not v4 (head/address not v4)';
  * MAIN row = the 1.5 in tee (tee_info.mode == '1.5in'); the 1.6 in crown tee is an INFO row only, labelled V4_CROWN_LABEL;
    a pass at the crown tee alone is not a pass; spin-band-only and face-edge-model-only flags as v3d.
Sources: Data Agent driver-face-centre-height @ 857e373; Evaluator review scott-e ebb6e4a; US 12,649,090 B2 Tables 3-4; USGA TPX3004 Rev 2.0 sec 2.1b. See docs/HARNESS_V4_NOTES.md."""
import copy   # eval.harness_v3d imported lazily so the worker can load V4_SPEC/check_v4 from a scored repo's sys.path

IN = 0.0254; R_BALL = 0.021335
# Expected v4 address spec (SI). Worker cross-check (results/overnight/_j_worker_gp_v3.py, V3_HEAD=v4) stops on any mismatch.
V4_SPEC = dict(
    face_centre_z_ground_m=dict(value=0.029, tol=5e-4, src="derived, Data Agent 857e373 (US 12,649,090 Zup-CGZ; corrected route B), Evaluator ebb6e4a: likely 27-31 mm"),
    cfz_m=dict(value=0.039, tol=5e-4, src="US 12,649,090 Tables 3-4 CFZ 35-45 mm aggregated across examples (narrowest 38-40), manufacturer patent claim"),
    lie_deg=dict(value=58.5, tol=0.1, src="Data Agent JSON lie (Wishon 58, PING G440 MAX 58.5, PROCEED 59)"),
    izz_gcm2=dict(value=5600.0, tol_rel=0.01, src="single published manufacturer claim (n=1, one head; Tour Edge 2023 press release), attributed, not measured or an aggregate; US 12,649,090 claim 1 Izz 560-700 kg mm2; rule cap 5900+100"),
    tee_15in_ball_centre_m=dict(value=1.5 * IN + R_BALL, tol=5e-4, src="MyGolfSpy tee test: 1.5 in measured from ground level; 38.1 + 21.335 = 59.435 mm"),
    tee_16in_ball_centre_m=dict(value=1.6 * IN + R_BALL, tol=5e-4, src="1.6 in tee: 40.64 + 21.335 = 61.975 mm (~ equator at a 62 mm crown; Golf Digest 'at least half the ball above the crown')"),
    face_half_h_m=dict(value=0.027, tol=5e-4, src="Data Agent JSON face height 54 mm / 2"),
    face_half_w_m=dict(value=0.0525, tol=5e-4, src="Data Agent JSON face width 105 mm / 2"),
)
V4_CROWN_LABEL = "v4 head, 1.6 in crown tee (equator at sourced crown)"
STATUS_PENDING = "pending Trainer flag"

def check_v4(measured):
    """measured: dict of V4_SPEC keys -> value (SI / deg / g cm2). Returns {key: (got, expected, tol)} for every mismatch or missing key."""
    bad = {}
    for k, s in V4_SPEC.items():
        g = measured.get(k); tol = s.get("tol", abs(s["value"]) * s.get("tol_rel", 0.0))
        if g is None or abs(float(g) - s["value"]) > tol: bad[k] = (g, s["value"], tol)
    return bad

def _is_v4(r): return (((r or {}).get("tee_info") or {}).get("head") or {}).get("mode") == "v4"
def _tee(r): return ((r or {}).get("tee_info") or {}).get("mode")

def crown_info_row(r_crown):
    if r_crown is None: return None
    from eval import harness_v3d as H3
    c = H3.apply_v3d_flagged(r_crown)
    return dict(status="info", passed=False, tag="info_only", gating=False, label=V4_CROWN_LABEL,
                values=dict(verdict=c["verdict"], n_pass=c["checks_passed"], n_warn=c["n_warn"], n_fail=c["n_fail"], tee_mode=_tee(r_crown),
                            fails=sorted(k for k, v in c["checks"].items() if v.get("status") == "fail")),
                why=[f"INFO only: {V4_CROWN_LABEL}; a pass here alone is NOT a pass (main row = 1.5 in tee)"])

def apply_v4(r_main, r_crown=None):
    """r_main: v3c result at the 1.5 in tee on the v4 env; r_crown (optional): same checkpoint at the 1.6 in crown tee (info only)."""
    from eval import harness_v3d as H3
    out = H3.apply_v3d_flagged(r_main)   # v3d bands, face-edge FAIL from env face_limits (face_edge_for handles mode v4), spin-band/face-edge-model flags
    out["harness_v3"] = dict(out.get("harness_v3") or {}, harness="v4", base_run="v3c", bands="v3d")
    if r_crown is not None: out["checks"]["mine/v4_crown_tee_info"] = crown_info_row(r_crown)
    out["v4_crown_tee_only"] = False
    if not _is_v4(r_main): out["verdict"] = "not v4 (head/address not v4)"
    elif _tee(r_main) != "1.5in": out["verdict"] = "not v4 (main row must be the 1.5 in tee)"
    elif out["verdict"] != "PASS" and r_crown is not None and out["checks"]["mine/v4_crown_tee_info"]["values"]["verdict"] == "PASS":
        out["v4_crown_tee_only"] = True; out["v4_note"] = "not a pass (crown-tee-only)"
    return out
