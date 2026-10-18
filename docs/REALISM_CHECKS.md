# Realism checks (swing + shot) and toe_sign finding

Package `realism/` (not under eval/). Thresholds: `data/references/realism_thresholds.json`
(rebuild with `python scripts/build_realism_thresholds.py`). Every threshold carries a source tag:
`published` / `derived` / `assumption` / `extrapolated` / `model`. Extrapolated reference rows are flagged
in the output (`extrapolated: true`) and can only warn, never hard-fail, unless noted in the JSON.

## Usage (Evaluator)
```python
from realism import check_swing_realism, check_shot_realism, shot_from_gate_block
sw = check_swing_realism(joint_traces, dt=0.02, tier="g1_stock")   # -> {"overall","checks":[{name,status,value,expected,reason,tag}]}
sh = check_shot_realism(dict(ball_speed_mph=.., club_speed_mph=.., launch_deg=.., spin_rpm=.., carry_yd=.., total_yd=.., descent_deg=..))
# gate JSON blocks (club_speed_ms, ball_speed_ms, launch_deg, carry_yd, total_yd):
sh = check_shot_realism(shot_from_gate_block(gate["policy_det"]))
```
Status values: pass / warn / fail / skip (skip = input not supplied; never silently pass).

## Swing checks
sequence order (pelvis -> torso -> arm -> club) and timing lead bounds; at dt = 0.02 s one sample is the
resolution, so published mean lags (~3 ms apart) are unresolvable and give warn, not fail; peak speeds in
90-120 mph club-speed band (extrapolated rows flagged); X-factor; torque and power feasibility vs actuator limits
(G1 stock / elite tiers, feasibility ratio); GRF / torque budget.

## Shot checks
smash <= 1.5 (fail above; warn near upper edge); spin 1800-3000 rpm; launch / carry / total plausibility vs
golfphys at the same ball speed, launch, spin (`carry_vs_golfphys_yd`, skipped if spin absent);
total/carry in [0.99, 1.45] (fail outside; env has no roll so ratio ~1.00 warns); `carry_positive` (carry <= 0 fails);
descent angle band.

Demo (read-only on hgs-kseq/results/gate_imit15_dart_s52.json): `policy_det` -> overall warn (smash 0.994 warn,
club speed 120.4 mph pass, launch 12.3 pass, total/carry 0.997 warn; spin/descent skipped). `scripted_zero_residual`
-> fail (smash 7.46, carry 0). Gate blocks carry no spin, so they cannot reach pass.

## toe_sign finding (read-only on env/)
`golfphys.env_contact_to_shot(handed, toe_sign)`: RH toe = -y, LH toe = +y by default convention.

**Simple MuJoCo env (humanoid_golf_v3/v4_power/h12wrist.xml line 72, v2 line 42; env/humanoid_golf_env.py `_contact_face_off`):**
`<geom name="club_head" type="box" size="0.04 0.05 0.03" pos="0 0 -1.12" euler="0 3 0">` is mirror-symmetric in
local y and the body/arms are centred at y = 0 (torso pos 0 0 1.0; ball at 0.3 0 0.05), with the shot along +x.
There is NO toe/heel in the XML. Local +y ~ world +y at contact (only a 3 deg pitch about y). The golfer-to-ball
vector is +x = the shot direction, so there is no stance that defines "away from the body". Toe/heel in this
env is a reporting convention, not a physical fact: it cannot be measured by any rollout.
Recommendation: keep the documented convention that +y is the toe and use `handed="LH", toe_sign=+1`
(equivalently `handed="RH", toe_sign=-1`). Confidence: low-moderate (anatomical inference, shoulders at +/-0.15 x).
Handedness in the env only flips reporting signs (`hand_sign`, docs/HANDEDNESS.md).

**G1 env (env/g1_golf_env.py lines ~61-72):** head geom at pos [0.03, 0, 0.20-CLUB_LEN], size [0.04,0.05,0.03], also
symmetric. But the geometry places the golfer: with the swing at the address and impact keyposes,
mj_forward gives head local x -> world +y (face normal; the ball is at +y of the head: head y = -0.100 / -0.065, ball y = 0),
head local y -> world -x, pelvis at x = 0, ball at x = +0.5. The target direction is +y with the ball in front of
the golfer on +x: the target is to the golfer's left = right-hander setup. Toe is away from the body = world +x =
local -y, so local +y = HEEL. For the G1 env: `handed="RH", toe_sign=-1` (local +y = heel).
Confidence: moderate (pose geometry, deterministic). Caveat: the default `G1Swing("stock"/"elite").run()` produced
no head-ball contact, so launch direction was not observed.
Trainer rollout if confirmation is wanted: log, at first head-ball contact, the head-geom xmat columns,
ball velocity direction (vy sign = shot direction) and contact dy (`_contact_face_off`), then confirm the face
normal maps to the ball velocity and that +dy lies toward the golfer. `scripts/toe_sign_probe.py` is the read-only probe.

## Gear effect
See docs/GEAR_EFFECT_VALIDATION.md.
