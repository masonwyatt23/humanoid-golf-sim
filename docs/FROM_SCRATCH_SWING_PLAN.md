# Plan: a real golf swing learned from scratch (v5 body, left-handed, stock torque limits)

Status: **PLAN ONLY. No training launched, nothing pushed.** Written 2026-10-17 (America/New_York). Author: Scott/Trainer agent.
Labels used throughout: **[measured]** = measured on this box in this repo; **[read]** = read from a file/doc in this repo;
**[published]** = from a cited source, not re-verified by me; **[guess]** = my assumption, must be validated; **[hypothetical]** = not a stock/real robot.
No Mason/Instagram-derived number appears in this file. Mason reference data is private and may only be used locally as a soft reward (section 7).

## 0. Summary (read this first)
1. Every learned/"swing" result so far (gate-passing 100.7 mph / ~140 m carry on stock, 288-298 m on the hypothetical tier) comes from a **planar, script-copied or script-parameter-searched swing** on a **simplified body**. That is not a golf swing. This plan replaces it.
2. The current body (v3/v4) **cannot** express a real swing: one yaw joint in the torso, **no pelvis yaw/pitch/roll**, 2-DoF shoulders, no lead-arm actuation of consequence, 1-DoF wrist, the lead hand is a soft equality connect (not a grip), ground contact is disabled for all body geoms, no ground-reaction sensing, handedness is a sign flip only (**section 2**).
3. Proposed **v5**: a ~34-actuated-DoF, left-handed, full-body humanoid on a pelvis with a floating base or pelvis-pinned-by-friction feet, 3-DoF waist, 3-DoF shoulders, elbows, 2-DoF wrists (+ forearm roll), a rigid club welded into both hands via two grip welds, foot-ground contact with friction, and force sensors for GRF (**section 4**). Two tiers: **stock** (G1-class torque/speed, from Unitree/Menagerie numbers) and **hypothetical** (scaled).
4. **Stock torque limits almost certainly cap club speed near ~100 mph with this body family** (measured 98-101 mph in the current env [measured/read]); the earlier G1 feasibility sim gave ~76 mph [read, docs/research_real_humanoids.md]. A learned from-scratch policy should be expected to land **at or below ~100 mph on stock**, not above. Higher requires roughly 2x torque and 1.5x joint speed (or 3x torque at stock speed) [read, same doc; coarse random-search lower bound] (**section 9**).
5. Honest expected outcome: contact at address-to-impact with a **shrinking ball tolerance** is likely achievable (stage A). A *learned from scratch* swing that also passes the existing 3-seed gate (contact >= 0.99, lateral <= ~2.7 m, ~100 mph, ~140 m carry) is **uncertain (my estimate 25-40 %)** within the compute budget; a swing with a correct kinematic sequence is **less likely (15-25 %)**; matching 120 mph on stock is **not expected (<5 %)** (**section 10**).
6. Compute: ~1000-2400 env steps/s/core measured under heavy shared load [measured]; 8 cores and ~9 GB available, so **<= 3 jobs with 2 workers each**, ~10-20 M steps per stage, ~35-45 core-hours total (**section 8**).

## 1. Honest scope of what exists today [read/measured]
- `env/humanoid_golf_env.py` (584 lines; Gymnasium; torso with a free joint, 25 qpos / 23 qvel / **11 actuators** in v3 [measured]; timestep 0.002 in the default model [measured]; control dt 20 ms; `max_steps=200`).
- `env/models/humanoid_golf_v3.xml`, `v4_power.xml` (only the right wrist force range differs: 3 -> 6, i.e. wrist 60 -> 120 N*m), `v2`, `h12wrist`, `humanoid_golf.xml`.
- `env/g1_golf_env.py`: Unitree G1 29-DoF (Menagerie, BSD-3) with pelvis as a yaw hinge, **legs held rigid by PD, cannot fall**, soft-tied lead hand, actuator tiers `stock`/`elite(hypothetical)`, torque falling linearly to 0 at rated speed, dt 0.0005, 20 ms control. Closest existing thing to the target spec, but not full-body in the learning sense.
- All gate-passing results: planar scripted swing, script-distilled policies, CMA-ES scripted parameter searches. All 8+ PPO "residual" attempts selected their initial (script-copied) weights [from the parent log].

## 2. Audit of v3/v4 body vs the spec
| Requirement | v3 / v4 today | Gap |
|---|---|---|
| Pelvis yaw / pitch / roll | Pelvis does not exist; `torso` carries the free joint. Hips are pitch-only (+-60 deg), no hip roll/yaw | **Missing.** No pelvis rotation, so no pelvis->thorax sequencing or X-factor. |
| Spine / torso DOFs | One hinge `chest_yaw` (+-45 deg, damping 1, armature 0.5), 120 N*m cap (gear 60 x force 2). No lateral bend, no flexion, no separate pelvis | **Missing** waist pitch/roll; yaw range +-45 deg < real X-factor needs; no pelvis vs thorax. |
| Lead/trail shoulder 3-DoF | Trail (named `right_*`): pitch + roll only. Lead (`left_*`): pitch + roll, only `left_shoulder_pitch` is actuated, roll/elbow are passive (damping 0.5) | **Missing** shoulder yaw (internal/external rotation) on both; lead arm largely unpowered. |
| Elbows | `right_elbow` 0-150 actuated; `left_elbow` -10..150 **passive** | Lead elbow unactuated. |
| Wrist 2-DoF | `right_wrist` 1 hinge (+-120 deg) actuated; lead hand has none | **Missing** radial/ulnar deviation + forearm pronation/supination, lead wrist. |
| Grip on rigid club | Club is geoms on the trail wrist body; lead hand is `connect` with solref 0.03 (soft) | **Not a grip.** Needs two hand frames both rigidly attached (weld / site-to-site with hard solref), grip separation ~0.1 m, club mass/MOI/length realistic. |
| Feet / ground friction | All non-ball/club geoms `contype=0 conaffinity=0`; legs are hip/knee/ankle pitch only, no foot geoms in contact | **Missing.** No foot-ground contact, so no friction cone, no GRF, no balance requirement; hence `pin_torso` option. |
| Ground-reaction sensing | None | Add 2 foot force/torque sensors + foot-contact flags; compute COP and lead/trail vertical-force share. |
| Handedness | Sign flip of yaw/roll targets and ball y (`docs/HANDEDNESS.md`); XML is not mirrored; naming `right_*` = trail | **Not real left-handedness.** v5 builds a physically mirrored model: lead = physical right limbs, ball and target direction mirrored. |
| Actuator realism | `motor` with `forcerange` x `gear`; **derived joint torques** (my arithmetic from the XML, not re-measured): trail shoulder pitch 250, shoulder roll 150, elbow 120, wrist 60 (v3)/120 (v4), lead shoulder pitch 150, hip 250, knee 200, ankle 80, chest yaw 120 N*m. **No torque-speed curve.** Action x `torque_scale`(10) is clipped by forcerange | These are **not G1 stock** (G1: arm 25, wrist pitch/yaw 5, waist yaw 88). "Stock" in the current gates means "no gain boost on this custom body", not G1 stock. Must be re-labelled. |
| Observation | qpos, qvel, ball relative terms, phase (a clock) | No contact/GRF, no club kinematics (angular velocity, face angle), no segment speeds. |

Consequence: the current "stock 100.7 mph" figure belongs to a custom body with up to 250 N*m shoulder torque and no speed limit. It is **not evidence** about what G1-class actuators can do (G1-class feasibility: ~76 mph [read]).

## 3. Torque / speed limits (per joint, N*m) with sources
Two tiers. **Stock tier** uses published robot numbers; **human reference** is for comparison only; the **hypothetical tier** is a guess.

Source for stock: Unitree G1 motor classes, from `unitree_rl_mjlab` g1_constants.py as recorded in `docs/research_real_humanoids.md` [read; original not re-fetched by me today] and the Menagerie `unitree_g1/g1.xml` `actuatorfrcrange` [read in that doc]. Torque falls linearly to 0 at rated no-load speed (as in `g1_golf_env.py`) [read]. H1 numbers (hip/waist ~220, arm ~75) from the same doc [published].

| Joint (v5) | Stock tier (G1 motor, N*m @ rad/s) | Hypothetical tier (guess) | Human peak, order of magnitude [guess from memory, not sourced, do not cite] |
|---|---|---|---|
| Hip pitch / yaw (per leg) | 88 @ 32 (7520-14) | 220-250 @ 45 (H1 hip 220 is published) | 150-300 |
| Hip roll (per leg) | 139 @ 20 (7520-22) | 250 @ 30 [guess] | 150-250 |
| Knee | 139 @ 20 | 300 @ 30 [guess] | 150-250 |
| Ankle pitch/roll | G1 ankle ~50 [read: 'waist pitch/roll 50' pattern; ankle number not re-read] -> treat as **[guess] 50** | 80 [guess] | 60-120 |
| Waist yaw | 88 @ 32 | 250 @ 45 [guess, H1 waist ~220 published] | 100-200 (trunk rotation) |
| Waist pitch / roll | 50 @ 20 (read) | 150 [guess] | 100-250 |
| Shoulder pitch/roll/yaw (3-DoF) | 25 @ 37 (5020) | 75 @ 55 (H1 arm 75 published; speed guess) | 50-100 |
| Elbow | 25 @ 37 | 75 @ 55 | 50-80 |
| Forearm roll / wrist roll | 25 @ 37 | 30 @ 55 | 10-20 |
| Wrist pitch / yaw (radial-ulnar) | **5 @ 22 (4010)** | 30 @ 55 (Apollo Menagerie 34, provenance unverified) | 10-25 |

Flags:
- The **5 N*m wrist** is the single most limiting stock number for club release; a real wrist/forearm chain delivers ~2-5x that [guess].
- Human column is order-of-magnitude recall and **must be replaced by cited values** (Data Agent task) before being used anywhere beyond context.
- The SDK safe speed default is 10 rad/s [read]; rated speeds are used here and are optimistic.
- Add per-joint velocity limits via the torque-speed curve, not hard clamps. Add action-rate and torque-squared penalties.
- All hypothetical numbers are **[hypothetical/guess]**; every result must carry the tier label.

## 4. v5 body XML spec (proposal)
Build via `mujoco.MjSpec` from Menagerie `unitree_g1/g1.xml` (as `g1_golf_env.py` does) **but keep all body joints free, feet colliding**. Options: (a) G1-based (recommended: real mass/inertia, 33 kg, 1.32 m [read]), (b) custom 1.75-1.85 m human-scale body (needed if the club should be a full-length driver at address; G1 is short, so the 1.15 m club from `g1_golf_env.py` is a scaling compromise, flagged **[guess]**). Decision gate G0: use G1-based unless the address pose with a 1.15 m club is infeasible.

Kinematics (all hinges; axes in the golfer frame; names use trail/lead roles; physical sides for a **left-hander**: lead = physical right, trail = physical left):
- Base: free joint on pelvis (no pinning). Ground plane friction `1.0 0.005 0.0001` for shoes [guess; typical turf/rubber ~0.6-1.0], condim 6 on feet.
- Legs (x2): hip pitch/roll/yaw, knee, ankle pitch/roll = 6 each. Foot box geoms (heel/toe) contype=1 with the floor; spikes not modelled.
- Waist: yaw (+-90 deg), roll (+-30), pitch (+-40) = 3. Pelvis yaw is implicit via hip yaw of planted feet.
- Arms (x2): shoulder pitch/roll/yaw (3), elbow (1), forearm roll (1), wrist pitch (1), wrist yaw/deviation (1) = 7 per arm.
- Neck/head: fixed (rigid), head orientation reward-free.
- Total actuated DoF ~ 12 (legs) + 3 (waist) + 14 (arms) = **29**, same as G1-29 minus the roll-only wrist replacement; add no fingers.
- Club: rigid body, length 1.15 m scaled (or 1.12 m real driver on a human-scale body), mass 0.30 kg, head 0.20 kg, shaft MOI from a capsule; **two grip welds**: lead hand at grip top, trail hand 0.10-0.12 m below (`equality weld`, `solref 0.005 1`, `solimp 0.95 0.99 0.001`), hands as sites 3 cm from the wrist frames. Club-head face loft and lie modelled from the existing analytic face/impact model in `humanoid_golf_env.py` so ball-flight physics stay comparable [read].
- Ball: unchanged (r 0.021 m, 46 g), on a held tee until first contact (as `g1_golf_env.py`).
- Sensors: foot force + torque sensors (2), `framelinvel`/`frameangvel` on pelvis, thorax, lead upper arm, club head; joint `jointpos/jointvel/actuatorfrc`.
- Timestep 0.0005 (as g1 env); control 20 ms; episode <= 2.0 s from address (including backswing; no phase clock in obs, use a time-since-start scalar only as an optional input and test removing it).

Handedness: mirror the Menagerie arm/leg assignments (lead = physical right). Target direction and ball offset mirrored in the env, **no sign flips** in rewards. Add a unit test that a mirrored (right-handed) copy gives the same flight for a mirrored action.

## 5. Env / reward spec
Observation (~120 dims): joint pos/vel (29x2), pelvis orientation (6D), pelvis/thorax angular velocity, club-head pos/vel in pelvis frame, club-shaft direction, ball position relative to club head, foot contact flags + normal-force fractions, previous action, time since start (optional). Domain randomization: ball position +-d (curriculum, below), mass +-5 %, friction +-20 %, small action delay.

Actions: normalized joint torque targets (or PD target offsets with the torque-speed clamp); start with PD targets around the address pose for learning stability, **but the address pose is a fixed keyframe, not a swing script**. 

Reward = sum of (scales are untuned **[guess]**; stage weights in section 6):
1. **Ball-flight physics (terminal, after ball lands or 3 s)**, using the existing flight tracker: carry (target-conditioned, saturating), launch window (9-13 deg for driver, tier-labelled), backspin window (2000-3000 rpm; note the Data Agent found env spin ~900 rpm below the TrackMan chart, so use the **opt-in corrected spin model** from Stage 29 when available, and say which one a result used), smash window (1.40-1.50), lateral |y| <= 2.7 m soft penalty growing quadratically past 1.5 m, and a contact-quality term (face offset, strike from the face geom).
2. **Contact shaping (dense, early)**: negative club-head-to-ball distance at the time of closest approach, gated so a swing that passes through address-height with the face open to the ball gets a bonus; large penalty for hitting the ground before the ball by > 3 cm (fat) or topping.
3. **Kinematic sequence (from `docs/SPEED_GAP_100_120_SPEC.md` on branch `speed-gap-public` @ a2bcaec, Data Agent; unverified extrapolations)**:
   - Peak speeds (deg/s, ~100 mph interpolated): pelvis yaw 442, thorax 665, lead arm 886, club 2054; ~120 mph extrapolated 519 / 803 / 1097 / 2500. Use the **100 mph** targets on stock, with peak term `w=0.5`, 15 % scale, overshoot at 0.25x, clip [-4, 0] (their spec).
   - Order/timing: pelvis peak ~87 ms (SD 19) before impact, thorax ~68 ms (SD 14), lead arm ~65 ms (SD 8), club at impact; sequence bonus 1/3 per ordered adjacent pair with >= 5 ms gap, +0.5 if the pelvis decelerates before impact. All soft, only active after Stage B passes.
   - Segment mapping: pelvis = `pelvis_yaw` (or pelvis angular z), thorax = pelvis + waist yaw rates, lead arm = norm of 3 lead shoulder rates, club = angular speed (outcome).
4. **X-factor**: reward a peak pelvis-thorax yaw separation near the top of the backswing in a **window**, **[guess]** 35-55 deg (real values vary; Chu 2010 only says more X-factor correlates with ball speed [read, spec doc]; no sourced number). Weight small; cap so it cannot be farmed by twisting at standstill (require it to be followed by an increase of thorax speed).
5. **Weight shift / GRF**: reward the **lead-foot share of vertical GRF rising across the downswing** (e.g. trail-dominant at top, lead-dominant near impact), COP moving toward the lead foot; no numeric published targets are asserted here **[guess: ~60-80 % lead at impact]**; verify in a Data Agent follow-up. Also a termination/penalty for feet slipping, center of mass outside the support polygon, or falling (balance is a hard requirement, in contrast to the pinned-torso v3).
6. **Regularisers**: torque^2 (energy), action rate, joint-limit proximity, self-collision (club vs body), jerk.
7. **Motion priors (SOFT only)**: see section 7.

No term may refer to a scripted trajectory or copy joint targets from one. The imitation weight is capped at 20 % of the total reward and is annealed to <= 5 % in later stages; a run with a prior weight of 0 must still reach Stage A (**ablation required**).

## 6. Curriculum and stages (go / no-go)
Common eval gate: the existing `scripts/gate3.sh`-style **3-seed gate** (seeds 5000/5001/5002 equivalents), contact >= 0.99, lateral <= 2.73 m (existing limit), numbers labelled stock / boosted / hypothetical and **learned (from scratch)**. Anything started from a script is labelled script-copied and does not count.

**Stage 0 - build and verify body (no learning). ~1-2 days of work, ~2 core-hours.**
Go if: model loads; standing for 2 s under a PD hold with no fall; both grip welds hold the club under a hand-driven swing (club-hand drift < 5 mm); mirrored model unit test passes; GRF sums to body weight +-5 % at rest; steps/s >= 600 on one idle core with ball (current G1-based env ~1050 raw ctrl steps/s [measured under load]).
No-go: balance impossible with stock limits -> fall back to a hypothetical-tier ankle/hip or a pelvis tether (labelled).

**Stage A - Contact (ball tolerance shrinking). ~10 M steps, ~8 core-hours, 2 seeds.**
Ball start offset tolerance (club-head vs ball at address) shrinks 8 cm -> 4 -> 2 -> 1 cm; reward: contact + contact quality + small forward distance; sequence/X-factor weights 0. Advance a rung when contact >= 0.9 over 256 eval episodes.
Go: contact >= 0.99 over 3 seeds at 1 cm tolerance **without a prior**, no falls >= 98 %.
No-go: < 0.5 contact at 2 cm after 10 M steps -> add (a) a staged soft prior of CMU golf kinematics at 10-20 %, (b) a PD-target action space, (c) a lower-DoF curriculum (freeze legs/waist then release).

**Stage B - Distance and ball flight. ~15 M steps, ~12 core-hours.**
Ramp ball-flight weight 0 -> 1 (as the existing `curriculum_weights`), carry target 100 -> 120 -> 140 m, launch/spin/lateral windows on. Go: gate passes with carry >= 120 m, lateral <= 2.73 m, **learned from scratch**. Stretch: >= 140 m (matches the script-copied number, would be a real result).
No-go: lateral > 4 m or carry < 100 m after budget -> keep the best, report honestly, stop adding terms.

**Stage C - Sequence and biomechanics. ~10 M steps, ~8 core-hours.**
Add peak-speed, ordering, X-factor, GRF terms at their weights, annealing prior from <= 20 % to <= 5 %. Go: pelvis -> thorax -> lead arm -> club order correct in >= 80 % of gate swings **and** gate still passes (carry within 5 % of Stage B). Report measured segment peaks vs the 100 mph spec (+-20 % considered "similar" given spec uncertainty).
No-go: sequence is wrong but ball flight passes -> report both honestly; the ball-flight result stands, the "biomechanically correct" claim does not.

**Stage D (optional, hypothetical tier) - speed push toward 110-120 mph.**
Ramp the speed-gap penalty (100 -> 110 -> 120). Only on the hypothetical tier or with torque x2-x3 / speed x1.5. Go: 3-seed pass at >= 110 mph. Labelled **hypothetical**.

## 7. Motion priors (soft rewards only)
- **CMU golf** (public, free for use; `docs/CMU_MOCAP_GOLF.md`; subject not Adam Scott [read]): retarget joint *angles* (anatomical, needs frame mapping) to compute a **phase-free** reward `exp(-d(DTW(q_agent, q_ref)))` on pelvis/thorax/arm angle trajectories, and sequence timing. Weight <= 0.2 (annealed). Right-handed data must be mirrored for the left-hander.
- **Data Agent targets**: the published segment peak speeds/timing in section 5.3 (public only).
- **Mason refs (private)**: local-only soft reward on left-shoulder/elbow/wrist rate medians; **the files and any numbers derived from them must not be committed, logged to committed docs, or sent to other agents**; the extracted rates are noted as weak (2D, unknown frame rate) by the Data Agent. Optional, weight <= 0.1, and Stage A/B must pass without it.
- Priors may shape but never gate: a run without priors is the control for every claim of "from scratch".

## 8. Compute plan (8-core box, ~15 GB RAM; ~9 GB available at write time [measured])
Measured today (shared box, load average ~7 from other agents' jobs, so these are pessimistic) [measured]:
- `HumanoidGolfEnv` (v3, 11 actuators, dt 0.002): **~2400 env steps/s on one core** (random actions, with reset).
- G1-based `g1_golf_env` model (37 qpos, 30 actuators, dt 0.0005): **~42 k raw `mj_step`/s, i.e. ~1050 control steps/s at 40 substeps/step** on one core. The full env with ball + flight + reward will be slower (est. 600-900 steps/s [guess]).
- Python processes of existing jobs use ~300 MB each; the box showed ~0 GB free but ~9 GB available. Memory is therefore **tight**; the orchestrator's limit is <= 3 jobs.
Plan: SubprocVecEnv (or `gymnasium.vector.AsyncVectorEnv`) with **6 workers per job** only when other jobs are idle; with 3 concurrent jobs use 2 workers each. Expected throughput ~1500-3500 steps/s per job (idle box) -> 10 M steps ~ 1-2 h per job idle, **realistically 3-6 h when sharing**.
Budget: Stage 0 ~2 core-h; A ~8; B ~12; C ~8; D ~8 optional; plus 3-seed gates and ablations (~6) = **~35-45 core-hours**, ~1-1.5 days wall clock at 3 jobs. Use `float32`, short rollouts (n_steps 2048 x workers), PPO with `target_kl`, **no residual-on-script**. Reduce cost: (i) run the 20 ms control with 10 ms physics substeps for Stage A (dt 0.002, as the current env) and validate Stage B/C at dt 0.0005; (ii) freeze the ball until the club head is within 0.3 m (skip flight simulation for non-contact episodes); (iii) cache the analytic flight model [read: `env/ball_flight_analytic.py`] instead of integrating in MuJoCo for training, and use the full tracker only in the gate. MJX/GPU is not planned (no GPU on this box [guess, not checked today]).
Checkpoint and commit notes after each stage; learned model files (small) are committed locally, never pushed without a human OK.

## 9. Torque caps and what higher club speed would need
**Flag: stock torque limits likely cap club speed near ~100 mph (160 km/h, ~45 m/s) with this body family.** Evidence:
- Measured 98-101 mph on the current v3 stock config [measured/gate results from the parent log] - and that body has **larger** torque than G1 (e.g. 250 N*m shoulder, 60 N*m wrist, no torque-speed curve) [read from XML, my arithmetic].
- G1 stock limits (arms 25, wrist pitch/yaw 5, waist yaw 88, hips 88, rated speed 32-37 rad/s) gave only ~34 m/s (**~76 mph**) in the coarse feasibility search (zero gravity, no ground, no ball, random search, lower bound) [read, docs/research_real_humanoids.md; scripts/g1_club_speed_feasibility.py].
- Expect a learned v5 stock policy to land **between ~70 and ~100 mph**; a result >100 mph on G1-class torque would be surprising and should be checked for non-physical exploits (self-collision, ground contact exploits, joint limit slips).
What a higher speed needs [read; same feasibility table, a coarse lower bound]:
| Target | Needed | Label |
|---|---|---|
| ~45 m/s (~100 mph) | ~2x torque with 1x speed, or ~3x torque at stock speed (on G1 body) | [read] |
| ~50 m/s (~112 mph) | ~2x torque and 1.5x speed | [read] |
| 120 mph (~54 m/s) | ~3x torque and 1.5x speed; wrist 5 -> >= 30 N*m | [read/guess] |
| 350 yd | 3-4x torque and 1.5x speed *and* correct launch/spin; and 350 total is a roll-model estimate (coin flip at 296 m carry) | [read, Data Agent validation docs, model-only] |
Other levers: heavier/longer lever arms (human scale 1.8 m body vs G1 1.32 m), stronger wrists, a more flexible shaft model (store-and-release energy; not modelled today), a lighter club head and a longer shaft (driver at the 1.17 m limit). Each is **hypothetical** until a real actuator spec supports it.

## 10. Honest expected outcomes
| Outcome | Probability (my estimate, guess) | Comment |
|---|---|---|
| v5 model builds, balances, welds the club, mirrored left-hander verified | ~85 % | engineering risk, mostly time |
| Stage A learned contact from scratch with no script, >= 0.99 at 1 cm | 55-70 % | small ball tolerance is the hard part; PD-target actions help |
| Stage B passes the 3-seed gate at >= 100 m carry (stock, learned) | 30-45 % | lateral dispersion from a full-body free-base swing is the risk |
| Stage B matches ~140 m carry / ~100 mph | 15-25 % | stock-limits and from-scratch both bind |
| Stage C correct kinematic sequence + gate pass | 15-25 % | priors needed; soft-only |
| Club speed > 105 mph on stock (G1-class) torque | < 5 % | see section 9 |
| 120 mph on hypothetical tier (3x torque, 1.5x speed) | 20-30 % | needs Stage D budget |
| 350 yd carry | ~0 % | the model maximum is ~333 yd per the Data Agent; 350 total is only a roll estimate |
Prior attempts (8+ PPO runs on script-copied starts) all retained their initial weights, so **no evidence yet that PPO improves a swing**; Stage A is the first real test of learning, which is why the plan starts with contact only.

## 11. Immediate next steps (when allowed to start; none started now)
1. Stage 0: write `env/models/humanoid_golf_v5_g1_lh.xml` builder (`scripts/make_v5_model.py`), tests (balance, grip drift, mirror) - no training.
2. Re-label current "stock" in all docs as "custom-body, no gain boost" and add the G1 tier as the true stock tier.
3. Ask the Data Agent for (a) cited human joint torque/speed values, (b) cited pro GRF/weight-shift and X-factor ranges, and (c) the spin-formula check (they already reported ~900 rpm gap).
4. Implement stages A-C reward in one env file with unit tests (reward terms on recorded rollouts, no learning).
5. Stage A launch decision at a go/no-go review: <= 3 jobs, <= 2 workers each.

## 12. Risks
- Balance and slipping dominate early learning on a free-base body; mitigate with a curriculum (pelvis tether -> free) and a foot-friction randomization.
- Reward hacking (club-ground pushes, flailing arms to farm "speed" terms, farming X-factor by twisting): mitigate via gates on ball-flight outcome and caps.
- Spec numbers are partly interpolated/extrapolated and unverified; do not cite as ground truth.
- Memory pressure with other agents' jobs; stay within 3 jobs, 2 workers each, and checkpoint often.
