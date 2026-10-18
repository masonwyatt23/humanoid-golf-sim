#!/bin/bash
# usage: scripts/gate3_scripted.sh <config.json> <name> [override_json] -- 3-seed headline gate of a SCRIPTED config -> results/imit_private
cd /workspace/artifacts/humanoid-golf-scott; mkdir -p results/imit_private
for s in 4000 8000 9000; do GATE_OUT=results/imit_private PYTHONPATH=. OMP_NUM_THREADS=1 /workspace/golfvenv/bin/python -m eval.gate_scripted_cfg $1 $2 100 $s "${3:-{\}}" > logs/gate_$2_$s.log 2>&1; done
