# Research: methods, infrastructure and a 24-hour plan for a powerful, human-looking driver swing

Written 2026-10-16. Research only: nothing committed or pushed, no video downloaded.
Tags: **[V]** verified in a source opened/returned this session; **[C]** computed or measured on this box; **[?]** uncertain, from memory, or inferred.
Companion doc: `docs/research_driver_distance.md` (physics targets, ball aero, club-mass/timestep/one-hand findings). Read its section 0 first; this doc assumes those physics fixes.

## 0. Bottom line
1. **This box has no GPU** (`nvidia-smi: command not found`), 8 CPU cores (Intel Xeon, 1 thread/core), 15 GB RAM, shared by all agents [C]. MJX, MuJoCo Playground, MuJoCo Warp, Isaac Lab and ProtoMotions' fast backends are all GPU-first, so they are **not usable here**. Plan is CPU MuJoCo + SB3 PPO with 8 subprocess envs, and a rented GPU only if we want to scale (section 2.4).
2. **What works for hit-a-ball-hard in the literature is: imitate a motion prior for style, and add a simple task reward for the ball.** Pure PPO with a task reward alone gives inhuman exploits (in SMPLOlympics golf it "kicks" the ball with the pelvis block) [V][S1]. AMP alone can ignore the style reward [V][S1]. PULSE+AMP gave the most golf-like motion [V][S1].
3. **For us the practical equivalent is DeepMimic-style phase-conditioned tracking of a swing reference (Mason's video, CMU mocap, or a scripted swing), plus residual PPO and a ball-speed reward gated on contact.** Full PULSE/MaskedMimic needs the SMPL body, AMASS data and GPU Isaac backends; too heavy for tonight.
4. **Physics before RL** (see companion doc): club mass, timestep, two-handed grip, pelvis/torso yaw. Without them nothing below can reach 110-130 mph.
5. Throughput on this box [C]: about 38-43k raw MuJoCo physics steps/s per core. At a 20 ms control step with dt=0.0005 that is ~1,070 control steps/s/core (~8.5k/s ideal on 8 cores, realistically 2-4k/s with PPO overhead and other agents sharing the CPU [?]). So ~170-350M steps in 24 h at best; plan for ~50-100M.

## 1. State of the art for athletic / sports humanoid skills

| Method | Idea | Relevance to a hard ball strike | Usable here? |
|---|---|---|---|
| DeepMimic (Peng 2018) [V][R1] | PPO to track a reference clip, with phase input and reference-state initialization; optional task goal reward | Best fit: single swing clip + phase, track pose then add ball goal | **Yes**, plain PPO on CPU |
| AMP (Peng 2021) [V][R2] | Discriminator on state transitions gives a style reward from unstructured motion, plus task reward | Style from many clips, no explicit clip choice | Yes but fragile (discriminator tuning, can ignore style [V][S1]); needs custom code |
| ASE (Peng 2022) [V][R3 via R4] | AMP + latent skill embedding, reusable skills | Needs large diverse data, big GPU compute; 64-d latent at 6 Hz [V][R5] | No (overkill) |
| PHC / PHC+ (Luo 2023) [V][R6] | One policy imitates nearly all AMASS, fall recovery; PHC+ reaches 100% AMASS success [V][R5] | Robust tracker, good for noisy video-derived motion | No (SMPL body, GPU) |
| PULSE (Luo 2024) [V][R5] | Distills PHC+ into a latent space for hierarchical RL; retains 99.8% train / 97.1% test success [V][R5]; beats ASE/CALM on coverage [V][R5] | Used for golf in SMPLOlympics with the best human-likeness [V][S1] | No (needs pretrained model, SMPL, GPU) |
| MaskedMimic (Tessler 2024) [V][R7] | One controller inpaints full-body motion from sparse targets (keyframes, text, scene) | Could "specify club path keyframes", but public checkpoint is SMPL / IsaacLab, no text [V][P1] | No for tonight |
| SMPLOlympics / HumanoidOlympics (Luo 2024) [V][S1][S2] | Sports benchmark incl. golf, tennis, table tennis; PPO/AMP/PULSE/PULSE+AMP baselines; SMPL, Unitree H1/G1 | Golf env spec: 1.14 m club, small box head, ball+club+goal reward, plus predicted-landing reward [V][S1] | Reference for reward design; code is IsaacGym |
| ProtoMotions 3 (NVlabs) [V][P2] | Framework implementing Mimic, AMP, MaskedMimic etc.; simulators IsaacGym, IsaacLab, Genesis, Newton, MuJoCo; the MuJoCo backend is CPU-only, one env, debugging only [V][P2] | Reference implementations | Only as reading material |
| Vid2Player3D tennis (Zhang 2023) [V][T1] | Imitation policy + high-level planner; video-derived motion is noisy, so a hybrid controller overrides wrist motion with the high-level policy [V][T1] | **Directly relevant lesson**: noisy video wrist/club motion needs the policy to correct it, not copy it | Idea reusable (residual on wrist/hands) |
| Physics table tennis (Wang 2024) [V][T2] | 18 min of mocap, separate imitation policies per stroke type (drive/push/smash), 120 Hz sim, 30 Hz imitation control; each imitation policy took 2B samples / 12 h on an RTX 4090 [V][T2] | Shows the **cost of the full pipeline** and per-skill policies | Reality check on compute |
| PhysHOI (Wang 2023) [V][T3] | Imitates human-object interaction with a contact-graph reward, no task-specific reward | Contact reward idea: reward the club-ball contact matching the reference | Idea reusable |
| Phase-based speed adaptation, minigolf robot arm (Ewerton 2016) [V][T4] | Non-uniform phase and amplitude parameters of a demonstrated motion, optimized with RL to hit a desired velocity | **Closest result to "club speed at a point"**: change when and how fast, not the whole clip uniformly | Yes (phase-rate action) |

What actually works for a hard hit [V/?]:
- Tracking rewards give human-like kinematics, and a task reward for ball outcome gives power. SMPLOlympics golf reward = ball moves forward + club approaches ball + ball reaches goal + predicted-landing dense reward [V][S1].
- Human-likeness collapses without a motion prior [V][S1].
- Noisy video references must not be tracked exactly; let the policy correct the end-effector (Vid2Player3D) [V][T1].
- Uniformly speeding a reference up is inefficient; real swings change timing non-uniformly (slow backswing, fast downswing) [V][T4].
- Gap in the literature I could find: no peer-reviewed full-humanoid result reporting simulated driver club-head speed in mph [?]. Nothing found with 110+ mph in sim, so we should expect to be pioneering; torque limits and physical realism matter more than algorithm choice [?].

## 2. Training infrastructure

### 2.1 Options
| Stack | Hardware | Throughput evidence | Verdict for this box |
|---|---|---|---|
| MuJoCo CPU + SB3 `SubprocVecEnv` (current repo) | CPU | **[C] 37.7k phys steps/s/core (dt 0.002 model), 42.9k (v3, dt 0.0005, nv=26)** on this box | Use now |
| MJX (JAX) | GPU/TPU | MJX is generally slower than native CPU MuJoCo for a single scene; wins only in large batches [V][M1] | No GPU: skip. MJX on CPU is pointless [V][M1] |
| MuJoCo Playground | GPU (MJX) | Humanoid PPO ~91.9k steps/s on one A100 [V][M2]; 4090 raw MJX humanoid.xml, 8,192 batch: 2.75M phys steps/s (MJWarp, a cut-down XML) [V][M3] | Needs GPU; **a humanoid with a 1-contact-pair model runs much faster than ours will** [?] |
| MuJoCo Warp | NVIDIA GPU (CPU only for debug) [V][M4] | see above | Needs GPU |
| Isaac Lab | RTX-class GPU for Isaac Sim workflows (typically >=RTX 4080 16 GB [V][I1]); Newton/MJWarp physics path can run without Isaac Sim and without RT cores [V][I1][I2] | | Needs GPU |

### 2.2 Expected steps/s on this box [C]/[?]
- Raw: ~1,070 control steps/s/core with the dt=0.0005 v3 model (20 ms control = 40 physics substeps) [C]. The dt=0.002 model: ~3,770 control steps/s/core [C].
- 8 procs on 8 cores: ideal ~8.5k/s (v3), but the box is shared with other agents' training/eval/rendering, SB3 policy inference and the PPO update add overhead, so budget **2-4k steps/s** [?]. Measure with a 2-minute test before committing.
- Budget at 3k/s: ~260M steps per 24 h; real throughput with idle gaps likely 100M. Compare: the physics table-tennis imitation policies used 2B samples each [V][T2], so we are ~20x short of that scale; we must lean on a good reference, a good initialization and narrow tasks rather than brute force.
- Cheap speedups [?]: try dt=0.001 with a stiffer analytic impact model (companion doc 1.4) and only run small dt around impact (variable substeps: coarse until club is within ~0.3 m of ball, fine after). Disable unused contacts (only foot-floor, club-ball, plus hands-to-club via weld). The MJWarp benchmark humanoid is optimized exactly like this (only foot-floor collisions, 8 contacts) [V][M3]. Set `mjData` reuse, avoid Python per-step overhead (batch reward math in numpy). Possible 2-4x [?].

### 2.3 Hardware check commands (run)
`nproc` = 8; `free -g`: 15 GB total (~6 GB available at the time); `nvidia-smi`: not found [C]. Python 3.13.5; system python has no mujoco/SB3 installed (the project's training env lives elsewhere; I benchmarked in a throwaway venv at <local-path>/bench_venv).

### 2.4 If we can get a GPU
Cheapest meaningful upgrade: one rented RTX 4090 or A100. Port the env to MuJoCo Playground/MJX (or MJWarp), 4,096+ envs, Brax/RSL-style PPO; humanoid-class PPO is ~90k steps/s on an A100 [V][M2], i.e. ~25-45x this box. That moves "2B samples" from 8 months to roughly 6-24 h [?]. Do not start the port before the CPU env physics are validated.

## 3. Reward / curriculum recipe for club speed at impact (two-handed grip)

### 3.1 Body and control prerequisites [V from companion doc, ?]
- Two-hand grip: left hand weld/connect to shaft (or a fixed offset grip with a hinge of limited range); torso yaw and pelvis yaw DOFs; spine pitch; wrist hinge (cock/uncock) on both wrists. Real swing power: legs -> pelvis rotation -> torso -> arms -> club, with sequenced peaks (kinematic sequence) [?].
- Actuators with realistic torque limits and `ctrlrange`; do not raise limits to chase speed. Measure peak club speed ~50 m/s (113 mph tour avg) [V companion doc].
- Control: 50 Hz policy, PD position targets (joint target = reference + residual) rather than raw torque; this is how DeepMimic and the sports papers stabilize [V][R1][?].
- Action space: 1 phase-rate scalar `dphi` plus joint residuals (Ewerton: non-uniform timing) [V][T4].

### 3.2 Observation
Joint pos/vel, club head pos/vel (in ball frame), club face normal, ball pos relative to club, **phase phi in [0,1)** as sin/cos, reference pose at phi and phi+lookahead, previous action. Optional: target direction. Keep it ~100 dims [?].

### 3.3 Reward (phase-conditioned, DeepMimic style, with contact gate)
`r = w_t * r_track(phi) + w_c * r_club + w_b * r_ball - w_e * r_effort - w_a * r_alive/smooth`
- `r_track`: exp(-k * pose error) on joint angles, end-effector (hands, club head) positions and velocities vs reference at phase phi (DeepMimic) [V][R1]. Down-weight wrists/club when the reference is noisy video (Vid2Player3D lesson) [V][T1].
- `r_club`: dense shaping toward impact only in the **downswing window** (phi in [phi_impact - w, phi_impact]): reward club-head speed along target direction, `min(v_head_dir / v_target, 1)`, plus clubface square (face normal alignment with target within ±3°) and club path alignment. Use a **velocity** target that is a curriculum variable (below).
- `r_ball` (only at/after contact, **gated**): ball speed along target direction `v_ball_dir/v_target_ball`, launch angle near 10-15°, lateral error small, then carry (from the flight model) after landing. Gate: only counts if first contact was a clean club-face hit (contact normal within face cone) to prevent exploit hits (shaft, heel). Smash factor proxy `v_ball/v_head` reward capped near 1.5 prevents "hit ball with elbow".
- Penalties: joint-limit violations, torque energy (small), ground contact other than feet, losing balance (pelvis height), self-collision, and a big one for ball touched by body.
- Early termination: fall (pelvis < 0.6 m) or phase out of bounds; Reference State Initialization at random phase [V][R1] (also helps credit assignment for the impact window).
- Do **not** reward raw "ball distance" first: SMPLOlympics uses ball-forward + club-approach + goal + predicted landing; our carry reward from the flight model plays the predicted-landing role and is dense [V][S1].
- Known failure from our logs (summarized from the parent thread): contact is a nudge with club ~0.2 m/s. Fix with physics and the `r_club` velocity term before `r_ball`.

### 3.4 Curriculum (target club-head speed, `v_target`)
1. **Contact:** v_target 10 m/s (22 mph), fixed ball, 100% clean contact required to advance.
2. **Speed ladder:** advance v_target by 5 m/s whenever (clean-contact >= 90% and mean head speed >= 90% target) over the last 100 episodes: 15, 20, 25, 30, 35, 40, 45, 50, then 55-58 (125-130 mph).
3. **Variation:** introduce domain randomization (below) only after the first rung that passes at ≥ 30 m/s, so it does not smother learning of the strike.
4. **Direction/launch:** add target direction ±5°, then launch window.
5. **Style:** raise `w_t` back up and add AMP/phase tracking of Mason/CMU references; prune any speed gain that costs > X imitation error [?: choose X from the pose error of the scripted baseline].
Use a ratio rule not wall-clock; log the ladder level in `results/`.

### 3.5 Phase-conditioned policy
- Feed phase, and let the policy output a phase-rate, so timing is learned (Ewerton non-uniform phase [V][T4]). Clamp dphi so a full swing takes >= ~0.8 s (tour downswing ~0.25 s [?]).
- Alternative that is faster to get working: **scripted / IK swing + residual PPO**: a hand-built swing trajectory (from a reference or a bezier on joint targets), PPO learns residual offsets and timing. This is what `env/residual_golf_env.py` appears to start [?, file exists in repo]. Strongly recommended as the first thing to get a real hit.

### 3.6 Domain randomization (after the strike works)
Ball position ±2 cm / ±5 cm along line; ball mass, club mass ±5%, club length ±2 cm, grip friction, joint damping/torque ±10%, ground friction, action delay 0-1 steps, observation noise, initial pose noise; **no** randomization of impact physics until contact is reliable. Randomization is mostly for robustness and to make dispersion numbers honest, not for sim-to-real here [?]. Note: HumanoidOlympics ran H1/G1 sports with no domain randomization at 200 Hz sim / 50 Hz control [V][S2], so DR is optional for a sim-only goal.

### 3.7 Making it look human
- Pose-tracking term against Mason/CMU references; CMU swings are slow (tempo ~1.7:1) so use for sequencing, not speed [companion; from Data Agent report].
- Limit joint velocities and use torque penalties; hide root-height tricks.
- Kinematic sequence reward [?]: peak angular velocity order pelvis -> torso -> arm -> club; rewards ordering of peak times, cheap to compute and well-known in golf biomechanics [?].
- Add AMP-style discriminator only if tracking is not enough; it is the least stable component [V][S1].

## 4. Recommended architecture and 24-hour experiment plan (this box: 8 CPU, no GPU)

### 4.1 Architecture
- **Env:** MuJoCo, `humanoid_golf_v3`-like model with: club 0.3 kg total (head 0.2, shaft 0.1; v3 already uses 0.10/0.20 [C from xml]), 1.14 m length, two-hand grip, pelvis and torso yaw, wrist hinges, dt 0.0005 with variable-dt or analytic impact [companion], control 50 Hz.
- **Flight tracker:** calibrated drag+Magnus model from the companion doc (Cd 0.26, Cl=min(1.7S,0.30)) [C companion] used to compute carry; log club speed, ball speed, smash, launch, spin, lateral.
- **Policy:** SB3 PPO, MLP 2x512 (tanh) policy and value, VecNormalize, n_envs=8 (SubprocVecEnv), n_steps 512, batch 4096, lr 3e-4 linear decay, gamma 0.99, GAE 0.95, clip 0.2, entropy 0.0-0.005, 10 epochs [?: sensible defaults, tune]. Policy outputs: joint target residuals around the reference/scripted pose + phase-rate.
- **Reference:** scripted swing first, then Mason-best-video reference, CMU as sequencing prior.
- **Eval:** deterministic and stochastic, 50-100 episodes, seeds fixed, metrics: contact%, club speed at impact (mph), ball speed, smash, carry, lateral std, pose error to reference.

### 4.2 Ordered experiments (budget ~24 h; times assume ~2-3k steps/s)
| # | Time | Experiment | Success gate | If fails |
|---|---|---|---|---|
| E0 | 0-1 h | Measure real env throughput (2 min, 8 procs). Check v3 timestep and impact: apply a prescribed club velocity of 50 m/s into the ball, verify ball leaves at ~1.4-1.5x with no tunnelling and no ball at 0 speed | Ball speed 70-77 m/s; consistent over 100 trials | Reduce dt or switch to analytic impact |
| E1 | 1-3 h | **Prescribed swing (no learning)**: generate a joint trajectory with IK / scripted keyframes so club reaches ~30 m/s at ball; check torque saturation | Club >= 30 m/s with realistic torques, 100% contact | Add DOFs, raise gear within believable limits, relax grip |
| E2 | 3-6 h | **Residual PPO on the scripted swing**, `v_target` ladder 10 -> 30 m/s, 5M-10M steps | Clean contact ≥ 90%, club ≥ 25 m/s | Increase reference weight, tune `r_club` |
| E3 | 6-12 h | Continue ladder to 45 m/s with phase-rate action; add kinematic-sequence term; 20M-40M steps | Club ≥ 40 m/s (90 mph), carry from flight model | Check torque saturation: if saturated, it's a body limit not an RL limit |
| E4 | 12-16 h | Swap/blend reference to Mason best video + CMU sequencing prior; weight pose tracking; small DR | Pose error ≤ baseline +20%, club speed drop ≤ 10% | Reduce `w_t` or only track torso/pelvis, let hands/club free |
| E5 | 16-20 h | Direction/launch/dispersion: lateral and launch reward, dispersion eval (50 ep) | Lateral std < 8 m at 40 m/s, launch 10-15° | Add face-angle reward |
| E6 | 20-24 h | Push speed 50-58 m/s, longest run from best checkpoint; render showcase video; write results/leaderboard | Club ≥ 50 m/s (113 mph) stretch; record honestly | Report body-limit analysis |
Parallelism: 8 cores only; run **one** training job at a time with 6-7 envs and keep 1-2 cores for eval/render by other agents [?]. If training stalls twice at a ladder rung, stop and re-check physics (E0/E1), not hyper-parameters.

### 4.3 Decision rule for a GPU rental
If E3 gates pass (so physics is validated) but throughput is the limiter, port to MJX/Playground on a rented 4090/A100 [V][M2][M3]; do not port before.

### 4.4 Risks / unknowns
- No source found reporting a simulated humanoid driver at 110+ mph [?]; goal might be limited by actuator realism rather than learning.
- Mason's video references: monocular pose gives noisy wrists/club (Vid2Player3D lesson [V][T1]); use as a style prior.
- Speed claims such as "club ≥ 50 m/s in sim with realistic torque" are unproven here [?].
- ProtoMotions MuJoCo backend is debugging-only [V][P2]; do not plan on it for training.
- Licensing: CMU data: commercial products OK but no resale even converted; retagged counsel_required 2026-10 (Data Agent report); SMPL body models have their own non-commercial license [?: check before depending on SMPL].

## Sources
- [S1] SMPLOlympics: https://arxiv.org/html/2407.00187 ; GitHub https://github.com/SMPLOlympics/SMPLOlympics
- [S2] HumanoidOlympics: https://humanoidolympics.github.io/
- [R1] DeepMimic: https://arxiv.org/abs/1804.02717
- [R2] AMP: https://arxiv.org/abs/2104.02180
- [R3] ASE (arXiv ID 2205.01906 is from memory [?]; ACM DOI 10.1145/3528223.3530110 cited in [T2])
- [R4] ASE citation as listed in https://doi.org/10.1145/3641519.3657437
- [R5] PULSE: https://arxiv.org/html/2310.04582 ; https://www.zhengyiluo.com/PULSE-Site/
- [R6] PHC: https://github.com/ZhengyiLuo/PHC/blob/master/README.MD
- [R7] MaskedMimic: https://arxiv.org/abs/2409.14393
- [P1] MaskedMimic model card: https://github.com/NVlabs/ProtoMotions/blob/main/data/pretrained_models/masked_mimic/smpl/MODEL_CARD.md
- [P2] ProtoMotions installation/simulators: https://nvlabs.github.io/ProtoMotions/getting_started/installation.html ; https://nvlabs.github.io/ProtoMotions/user_guide/experiments.html
- [T1] Vid2Player3D tennis: https://doi.org/10.1145/3592408 ; https://xbpeng.github.io/projects/Vid2Player3D/Vid2Player3D_2023.pdf
- [T2] Table tennis: https://doi.org/10.1145/3641519.3657437 ; appendix https://jiashunwang.github.io/PhysicsPingPong/static/mat/physpingpong_appendix.pdf
- [T3] PhysHOI: https://wyhuai.github.io/physhoi-page/
- [T4] Movement Primitives with Multiple Phase Parameters: https://www.ias.informatik.tu-darmstadt.de/uploads/Team/MarcoEwerton/ewerton_icra_2016_stockholm.pdf
- [M1] MJX docs: https://github.com/google-deepmind/mujoco/blob/main/doc/mjx.rst
- [M2] MuJoCo Playground: https://arxiv.org/abs/2502.08844 ; https://playground.mujoco.org/assets/playground_technical_report.pdf
- [M3] MJWarp benchmark: https://github.com/nvlukasz/mjx_warp
- [M4] MuJoCo Warp: https://github.com/google-deepmind/mujoco_warp/
- [I1] Isaac Lab installation / physics backends: https://isaac-sim.github.io/IsaacLab/develop/source/setup/installation/index.html ; https://isaac-sim.github.io/IsaacLab/develop/source/concepts/physics_backends.html
- [I2] Newton RT-core discussion: https://github.com/newton-physics/newton/discussions/150
- Local measurements [C]: `nproc`, `free -g`, `lscpu`, `nvidia-smi`, and a 20k-step mj_step timing in <local-path>/bench_venv on `env/models/humanoid_golf.xml` and `humanoid_golf_v3.xml`.
