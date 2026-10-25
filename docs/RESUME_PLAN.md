# Resume plan (project paused Oct 25, 2026)

Development is paused per Mason (6:16 PM ET, Oct 25, 2026). This file is the Evaluator's state-at-pause and resume checklist, copied from the team's local plan. Nothing here is a result; official numbers live in `results/overnight/V19_GRADE.md`.

## Evaluator — paused 2026-10-25 6:17 PM ET (Mason pause order via Orchestrator)

**State at pause:** no grade running and nothing ungraded or uncommitted. Hourly watch routine "Hourly Trainer checkpoint watch" is PAUSED. Resume only when the Orchestrator says so.

**Harness commit:** branch scott-e at `aeed7260` (worktree hgs-scott-lb).
- Harness code was last changed in `22fde15e` (v4.1 --reground info row) and `cb2d3683` (stance_obs forwarding).
- Ported to main: `aeed7260` (V19 grade) is handed to the Repo Agent; earlier commits through `9a95d884` are on main as `13b08820`.

**Best official grade:** V18w_s661 100k (V19_GRADE.md). v4 1.5in 13/5/1 FAIL, robustness only, .958/.958/.875 (plant 21/24). Robustness t/c and spin tails also fail.

**Gate settings (official, unchanged):**
- harness v4, env_v4 head, 1.5in tee main row
- worker: arm 0.6, club 1.15, 24 episodes, gate off, golfphys
- robustness seeds 7000-7023; gate contact ≥.95, start ≥.90, plant ≥.90
- RO export from the Trainer's box HEAD; V12X keys (md5 verified, not published)

**Info rows (non-gating):** crown 1.6in, v3c, v3d (+1 strike_height vs Trainer), v4.1 --reground, v5 (heldout-1 seeds 910000-910023, heldout-2 --heldout2-dr 32, D-plane on perturbed episodes).

**Pass rule:** a full pass is v4 1.5in, robustness included. It is not a pass if it comes only from crown, v3d, or v4.1. Render the 1080p cinematic only after a full pass.

**CPU on resume:** follow whatever budget the Orchestrator sets then. The last rule was 1 core shared with the Repo Agent: taskset -c 1, nice -n 10, --procs 1, threads 1, one at a time.

**Queued candidates (ungraded):**
1. V19a_s700 100k/150k/200k: not yet checked; only 50k was checked locally, at .917/.875/.833.
2. stageG2_s205_875000: goal-trained; grade the v5 task rows.
3. Any snapshot the Trainer produces later that could beat .958/.958/.875.

V18w 25k-75k, V18x and V18q-V18v all failed locally, are no better, and are not queued.

**Data Agent (not on main):** the peer-reviewed speed refs (WIP, 86 rows) stay on branch peer-reviewed-speed-refs, to be reviewed after the pause; the abstract-only Betzler/Worobets rows will be decided then.
