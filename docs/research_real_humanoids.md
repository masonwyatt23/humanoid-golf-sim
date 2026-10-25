# Real commercial humanoids as a template for the golf humanoid

Researched 2026-10-16 (web search + local MuJoCo checks). **Not committed.**
Legend: ✅ = number appears on a manufacturer page/spec sheet or in the actual model file I loaded; 🟡 = third-party site or press only; ❓ = not published / conflicting / unverified.
Joint-group DoF for most robots is *not* published by the makers; I only list what I could source.

## 1. Spec table (public sources)

| Robot | Height / mass | DoF (what is published) | Peak torque / speed published | Hand | Open sim model |
|---|---|---|---|---|---|
| **Unitree G1** (G1 EDU) | 1.32 m (1.27 m folded-stand figure in another manual), ~35 kg ✅ | 23 base; EDU 23-43. Leg 6, arm 5, waist 1 (+2 optional → waist yaw/roll/pitch), +2 optional wrist (wrist roll/pitch/yaw in 29-DoF model). Waist Z ±155°, X ±45°, Y ±30°; hip P ±154°, R −30…+170°, Y ±158°; wrist P/Y ±92.5° ✅ | Knee 90 N·m (G1) / 120 N·m (EDU) ✅; arm payload ~2-3 kg ✅. Per-motor (from Unitree's RL repo `unitree_rl_mjlab`, g1_constants.py ✅): 5020 (shoulder/elbow/wrist-roll) 25 N·m @ 37 rad/s; 7520-14 (hip pitch/yaw, **waist yaw**) 88 N·m @ 32 rad/s; 7520-22 (hip roll, knee) 139 N·m @ 20 rad/s; 4010 (wrist pitch/yaw) 5 N·m @ 22 rad/s. Speeds are rated no-load limits; the SDK safety default is only 10 rad/s | Dex3-1: 7 DoF (thumb 3, index 2, middle 2) ✅ | **Menagerie `unitree_g1`** (29-DoF + 43-DoF with hands), BSD-3 ✅ |
| **Unitree H1** | ~1.80 m, ~47 kg ✅ | 19 DoF: leg 5 (hip 3, knee, ankle), arm 4 (shoulder 3 + elbow), 1 waist (torso yaw) ✅. **No wrists** | Knee ~360, hip ~220, waist ~220, ankle 45-59, arm joint ~75 N·m ✅ (M107 motor 360 N·m); joint speed ❓ | optional ❓ | **Menagerie `unitree_h1`**, BSD-3 ✅ (menagerie actuators: torso/hip 200, shoulder 40, elbow 18 N·m; those are menagerie's ctrlrange, lower than the 75 N·m spec) |
| **Apptronik Apollo** | 1.72 m (5'8"), 72.6 kg (160 lb), payload 25 kg (55 lb) 🟡 (apptronik.com news pages) | 32 actuated DoF in Menagerie model: torso yaw/roll/pitch, 3-DoF shoulder, elbow, 3-DoF wrist per arm, 6 per leg ✅(model file) | not published by maker ❓. Menagerie file limits (✅ file, provenance ❓): torso yaw 120, torso pitch 315, shoulder 114, elbow 114, wrist roll 10.6, wrist pitch 34.2, hip 120-494, knee 336 N·m. Torso yaw range only ±0.83 rad | ❓ | **Menagerie `apptronik_apollo`**, Apache-2.0 ✅ (no hands in model) |
| **Agility Digit** | 175 cm, 65 kg, payload 16 kg 🟡 | 16 DoF (leg 5, arm 3) per Humanoid Hub 🟡; another site says 20 → **conflict ❓**. Agility's own spec-sheet page returned no data | ❓ | tote-gripper end effector, not a hand | Menagerie has **Cassie** (`agility_cassie`, MIT ✅), the legs-only predecessor with no arms; no Digit model found |
| **Tesla Optimus Gen 2** | 173 cm, 57 kg 🟡 (Tesla announced "10 kg lighter, 30% faster", no full spec sheet; MERA lists 73 kg/22 DoF; Robo2u lists 57 kg/28 DoF → **conflicting**) | 2-DoF neck ✅ (Tesla video list), total ❓ | ❓ | 11 DoF/hand ✅ (Tesla video list) | none official |
| **Tesla Optimus Gen 3 / V3** | not officially published as of search; Gen-2 carry-over numbers only ❓ | ❓ | ❓ | 22-DoF tendon hand reported (25 actuators/hand) 🟡 via patents/press | none |
| **Figure 02** | 5'6" (~168-170 cm), 70 kg, payload 20 kg ✅ (BMW Group page, Figure PR) | whole-body ~39 DoF is an analyst *estimate* (GTJA report) ❓ | ❓ | 16 DoF/hand ✅ (Figure press release) | none |
| **Figure 03** | 5'8" (173 cm), 61 kg, payload 20 kg ✅ (figure.ai spec) | ~30 DoF third-party ❓ | ❓ | not published (20 DoF third-party ❓); fingertip tactile to 3 g ✅ | none |
| **Boston Dynamics Atlas (electric, product)** | 1.9 m, 90 kg ✅ (BD spec sheet Jan 2026) | **56 DoF** ✅, most joints continuous rotation (slip rings) ✅; breakdown ❓ | payload 50 kg instant / 30 sustained / 20 one-hand ✅; reach 2.3 m ✅; joint torque/speed ❓ | ❓ (tactile, gripper variants) | none |
| **1X NEO** | ~1.68 m, ~30 kg 🟡 (1x.tech; lift ~70 kg, carry ~25 kg) | ❓ | ❓ | 22 DoF/hand 🟡 (25 incl. wrist in newer design) | none |
| **Fourier GR-1** | 1.65 m, ~55 kg ✅ | 44 total = 32 body + 6-DoF hands (docs); **waist 3 DoF** ✅ (support.fftai.cn). Early press said 40 DoF / 300 N·m hip → superseded | max joint peak 230 N·m ✅ (docs); speed ❓ | 6 DoF ✅ | Menagerie has **`fourier_n1`** (a smaller, different robot, Apache-2.0 ✅) – not GR-1 |
| **XPeng IRON** | 2024 version 178 cm / 70 kg; Next-Gen 173 cm / 65 kg 🟡 | 82 body DoF (2024/Next-Gen), later production "76 body" ❓ conflicting; "bionic spine" ✅ (Hannover Messe) | ❓ | 22 DoF/hand (older) / 21 (production) 🟡 | none |

Source URLs (all fetched via web search 2026-10-16):
- Unitree G1: https://www.unitree.com/g1/ , https://support.unitree.com/home/en/G1_developer , https://github.com/unitreerobotics/unitree_rl_mjlab/blob/main/src/assets/robots/unitree_g1/g1_constants.py
- Unitree H1: https://www.unitree.com/h1/ , https://support.unitree.com/home/en/H1_developer
- Apptronik Apollo: https://apptronik.com/news-collection/meet-apollo-the-iphone-of-humanoid-robots , https://apptronik.com/news-collection/apptronik-unveils-apollo
- Digit: https://www.humanoidaccessories.com/robots/digit-v4 , https://merarobotics.com/blog/humanoids/agility-digit
- Optimus Gen 2: https://arstechnica.com/information-technology/2023/12/teslas-latest-humanoid-robot-optimus-gen-2-can-handle-eggs-without-cracking-them/ , https://newatlas.com/robotics/tesla-optimus-gen-2-robot/ ; V3 hand: https://www.teslarati.com/tesla-optimus-v3-hand-arm-details-revealed-new-patents/
- Figure 02: https://www.bmwgroup.com/en/news/general/2024/humanoid-robots.html , https://www.prnewswire.com/news-releases/figure-unveils-figure-02-its-second-generation-humanoid-setting-new-standards-in-ai-and-robotics-302214889.html
- Figure 03: https://www.figure.ai/news/introducing-figure-03 , https://roboticaguide.com/figure-03-specs-helix-botq-what-is-undisclosed/
- Atlas: https://bostondynamics.com/wp-content/uploads/2026/01/atlas-spec-sheet.pdf , https://bostondynamics.com/products/atlas/
- 1X NEO: https://www.1x.tech/neo , https://www.humanoidsdaily.com/news/1x-details-neo-human-in-the-loop-strategy-and-hardware-as-pre-orders-go-live
- Fourier GR-1: http://support.fftai.cn/main/en/concepts/mechanical_system/ , http://support.fftai.cn/main/en/concepts/about_gr1/
- XPeng IRON: https://baike.baidu.com/en/item/Iron/3827352 , https://www.hannovermesse.de/en/news/news-articles/china-s-next-top-robot-thanks-to-a-bionic-spine , https://www.prnewswire.com/news-releases/iron-the-worlds-first-advanced-general-purpose-humanoid-robot-walks-off-the-production-lines-as-xpengs-humanoid-robot-manufacturing-facility-is-officially-commissioned-302871836.html

Not found at all / no joint-level specs: Optimus peak torques, Figure, Atlas joint torques, Digit, NEO, IRON. Those robots **cannot be modeled with verified actuator limits**; any numbers for them would be guesses.

## 2. MuJoCo Menagerie status (cloned and checked on this box)

Cloned `https://github.com/google-deepmind/mujoco_menagerie` (no credentials) to **<local-path>/menagerie** (commit `62ab00f`). MuJoCo 3.16.0 installed in venv **<local-path>/mjenv** (system python is PEP-668 locked). Loaded and stepped OK: `unitree_g1/scene.xml`, `unitree_h1/scene.xml`, `apptronik_apollo/scene.xml`.

| Menagerie dir | Robot | Actuators | License |
|---|---|---|---|
| `unitree_g1` | G1 29-DoF (also `g1_with_hands.xml`, 43 act.) | 29 / 43 | BSD-3-Clause |
| `unitree_h1` | H1 (no wrists) | 19 | BSD-3-Clause |
| `apptronik_apollo` | Apollo | 32 | Apache-2.0 |
| `agility_cassie` | Cassie (legs only) | – | MIT |
| `fourier_n1`, `booster_t1`, `berkeley_humanoid`, `pndbotics_adam_lite` | smaller/other humanoids | 23/23/12/25 | Apache-2.0 / Apache-2.0 / BSD-style ("All rights reserved" header, check `LICENSE`) / MIT |
| not in Menagerie | Optimus, Figure, Atlas (electric), Digit, NEO, GR-1, IRON | – | – |

G1 model facts (read from the file): 36 qpos, 29 actuators, total mass 33.3 kg, `actuatorfrcrange` torque limits = the Unitree numbers above (arm 25, wrist pitch/yaw 5, hip pitch/yaw/waist yaw 88, knee 139, waist pitch/roll 50), timestep 0.002, position actuators kp=500. Only rubber-hand meshes in `g1.xml` (no fingers); fingers exist in `g1_with_hands.xml`.

## 3. Which model is the best base?

Requirements: torso/waist yaw, strong hips, two-hand grip, fast arms.

- **Unitree G1 (29-DoF, Menagerie)** — recommended. 3-DoF waist (yaw ±150°), 7-DoF arms (3 shoulder, elbow, 3 wrist), 6-DoF legs, 33 kg (light = fast), fastest published motor speeds (32-37 rad/s), open BSD-3 license, the same robot has a huge RL/mocap-tracking ecosystem (mjlab, whole_body_tracking). Weak points: 25 N·m arms and 5 N·m wrists, 88 N·m hips/waist.
- **H1**: stronger (waist 220, hips 220 N·m) but 4-DoF arms, no wrists, no waist roll/pitch: a two-hand club grip would be a rigid weld. Joint speeds unpublished. Second choice only.
- **Apollo**: best torque and kinematics on paper (torso 3 DoF, 7-DoF arms, 114 N·m shoulders), but mass 81 kg in the model, torso yaw only ±47°, speed limits unknown, no hands, torque numbers' provenance unverified. Good for an "elite hypothetical" comparison, not as the base.
- The others: not available as open models, or no arms.

**Recommendation: G1 29-DoF from Menagerie + a ~0.3 kg, 1.15 m driver, left hand tied to the shaft with a soft `connect` constraint.** Fixed club-to-hand grip is realistic: the Dex3-1 hand is a 3-finger hand and has not been shown gripping a club, so don't promise finger-level grip.

## 4. Can a real robot reach 45-50 m/s club head speed? (my calculation, honest)

Reference: pro tour average ~113 mph = 50 m/s; 350 yd total needs ~58-65 m/s (130-145 mph) — see research_driver_distance.md.

Kinematic ceiling (simple): head speed = ω·r. Waist yaw 32 rad/s × ~0.9 m horizontal reach ≈ 29 m/s; adding shoulder 37 rad/s × ~0.7-1.6 m and wrist ranges, the raw sum of joint *rated* speeds is far above 50 m/s (random-pose Jacobian bound 150-220 m/s, which is meaningless as it assumes every joint at no-load speed at once). So rated joint **speed is not the binding limit; torque (energy delivered during a ~0.25-0.3 s downswing) is.**

Energy check: head at 48 m/s with 0.2 kg is ~230 J, plus shaft/hands/arms/torso kinetic energy, call it 300-450 J total. G1's waist (88 N·m) over ~1.5 rad ≤ 130 J, hips (2×88 N·m, ~1 rad) ≤ 176 J, right arm joints (25 N·m × 2 rad each) ≤ 50 J each, and the real torque falls linearly to zero at rated speed (so roughly half the nominal energy). That is marginal-to-insufficient for 45-50 m/s.

Simulation (scripts/g1_club_speed_feasibility.py, run on this box): G1 with a pelvis yaw hinge (stand-in for planted-feet hip yaw, 176 N·m, 32 rad/s), waist yaw, right-arm 3-shoulder/elbow/3-wrist, a 0.27 kg club, zero gravity, linear torque-speed curve, bang-bang control with random search + hill climbing over joint start/end angles and timing, scoring only speed with the head <0.35 m off the ground and mostly horizontal:

| Actuator scale | Best club head speed found |
|---|---|
| G1 stock limits (×1 torque, ×1 speed) | **34 m/s (~76 mph)** |
| ×2 torque | 40 m/s |
| ×3 torque | 47 m/s |
| ×2 torque, ×1.5 speed | 50 m/s |
| ×3-4 torque, ×1.5 speed | ~57-58 m/s |

Caveats (unverified/approximate): this is a coarse random search (noisy, results are lower bounds on what an optimizer would find, and one ×4 torque/×2 speed run gave an implausible 90 m/s, which I discard as a search/numerical artifact); no ground contact, no balance, no gravity, no ball impact, no motor thermal or gear-compliance limits, club treated as rigid, pelvis hinge range ±1.2 rad, arm motor speeds used as torque-speed corners. Real impact also loses speed to ball mass (smash factor ~1.45-1.5).

**Honest answer:**
- A stock G1 can plausibly reach roughly 30-35 m/s (≈70-78 mph, like a casual golfer) in sim, **not 45-50**. Do not expect 350 yd; ~200-230 yd total would be a realistic G1 ceiling.
- 45-50 m/s needs about **2× torque and 1.5× joint speed on all upper-body/hip joints** (or ~3× torque at stock speed). H1/Apollo-class torque (hips 220-494 N·m, torso 120-315 N·m) gets part of the way, but their speeds are unpublished, so I can't confirm.
- 58-65 m/s (350 yd) needs roughly 3-4× torque *and* 1.5× speed: a hypothetical elite robot, with a heavier-duty arm/wrist chain (wrist 5 N·m → ≥30 N·m is the most glaring G1 gap: Apollo's wrist pitch is 34 N·m in the Menagerie model) and ~30-40 kg·m² of torso inertia rotating at ≥25 rad/s.

## 5. What "elite" hypothetical upgrades to put in the sim

Make these configurable `actuator_scale` knobs on the G1 baseline so the story is honest: "G1 stock → G1+ → Elite":
1. Hip yaw/pitch + waist yaw: 88 → 250 N·m, rated speed 32 → 45 rad/s (H1 hips are 220 N·m, spec-verified).
2. Shoulders/elbow: 25 → 75 N·m (H1 arm joint 75 N·m, spec-verified), speed 37 → 55 rad/s.
3. Wrist pitch/yaw: 5 → 30 N·m (Apollo Menagerie 34 N·m).
4. Keep the 0.3 kg club, 1.15 m, grip tied to both hands; keep human-like waist/hip range (waist ±150° is spec-verified).
5. Label every result with the actuator tier ("stock G1" vs "hypothetical") and never present the elite tier as an existing robot.

## 6. Exact steps: load G1 in MuJoCo and attach a club + two-hand grip

```bash
git clone --depth 1 https://github.com/google-deepmind/mujoco_menagerie <local-path>/menagerie   # already done
python3 -m venv <local-path>/mjenv && <local-path>/mjenv/bin/pip install mujoco numpy               # already done (MuJoCo 3.16.0)
cd <local-path>/artifacts/humanoid-golf-scott
python scripts/g1_with_club.py        # prints: OK nq 36 nu 29 mass 33.61 ...  (verified)
```

`scripts/g1_with_club.py` (verified to compile and step) does:
1. `spec = mujoco.MjSpec.from_file(".../unitree_g1/scene.xml")` (G1 + floor).
2. Adds a `club` body to `right_wrist_yaw_link` at local (0.10, 0, 0) (palm); shaft = capsule along local z, 1.15 m, 0.07 kg; head = 0.20 kg box at the end (total ~0.27 kg); sites `grip_right`, `grip_left` (12 cm down the shaft) and `clubhead`.
3. Adds site `lhand` on `left_wrist_yaw_link` at (0.10, 0, 0), then `add_equality(type=mjEQ_CONNECT, name1="lhand", name2="grip_left", solref=[0.01,1])`: the soft two-hand grip.
4. `spec.compile()` → `MjModel`.

To do next (not done): orient the shaft vs. wrist axes for a correct address posture (set a "stand/address" keyframe, ball at head height), switch G1 actuators from kp=500 position control to torque-limited targets from `actuatorfrcrange`, add `actuator_scale` knobs (§5), add a ball body with contact and ball flight (the Trainer already has this in `env/`), re-use the CMU mocap angles via retargeting (angles are anatomical, not MuJoCo frames), and use `unitree_rl_mjlab`/`whole_body_tracking` motion-tracking rewards for the imitation stage.

Files created: `docs/research_real_humanoids.md` (this), `scripts/g1_with_club.py`, `scripts/g1_club_speed_feasibility.py`. Nothing was committed or pushed.
