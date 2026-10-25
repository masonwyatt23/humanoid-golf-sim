#!/bin/bash
# Paths come from env: HGS_EVAL_REPO, HGS_TRAINER_REPO, HGS_RO_ROOT (dir of read-only exports), HGS_PY (interpreter, default python3).
# usage: scripts/gate3_preset.sh <model> <configs/preset_*.json> -- 3-seed headline gate with an OPT-IN versioned preset (gate_override read from the preset file). Output: results/imit_private/<preset>/
cd ${HGS_TRAINER_REPO:?set HGS_TRAINER_REPO to the Trainer checkout}
P=$2; N=$(${HGS_PY:-python3} -c "import json,sys;print(json.load(open('$P'))['preset'])"); OV=$(${HGS_PY:-python3} -c "import json;print(json.dumps(json.load(open('$P'))['gate_override']))")
D=results/imit_private/$N; mkdir -p $D
for s in 4000 8000 9000; do GATE_OVERRIDE="$OV" GATE_OUT=$D PYTHONPATH=. OMP_NUM_THREADS=1 ${HGS_PY:-python3} -m eval.eval_gate $1 100 $s > logs/gate_$1_${N}_$s.log 2>&1; done
