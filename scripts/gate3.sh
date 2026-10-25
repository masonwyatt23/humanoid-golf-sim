#!/bin/bash
# Paths come from env: HGS_EVAL_REPO, HGS_TRAINER_REPO, HGS_RO_ROOT (dir of read-only exports), HGS_PY (interpreter, default python3).
# usage: scripts/gate3.sh <model> -- 3-seed gate into private dir; nohup-safe
cd ${HGS_TRAINER_REPO:?set HGS_TRAINER_REPO to the Trainer checkout}; mkdir -p results/imit_private
for s in 4000 8000 9000; do GATE_OUT=results/imit_private PYTHONPATH=. OMP_NUM_THREADS=1 ${HGS_PY:-python3} -m eval.eval_gate $1 100 $s > logs/gate_$1_$s.log 2>&1; done
