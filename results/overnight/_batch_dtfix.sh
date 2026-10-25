#!/bin/bash
# Paths come from env: HGS_EVAL_REPO, HGS_TRAINER_REPO, HGS_RO_ROOT (dir of read-only exports), HGS_PY (interpreter, default python3).
# dt-fix re-score (gate off, golfphys, arm 0.6, club 1.15, 3 seeds x 8 det eps); new files *_dtfix_gateoff_gp_arm06.*; refuses to overwrite
cd ${HGS_EVAL_REPO:?set HGS_EVAL_REPO to the evaluator checkout}
O=results/overnight
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
while read t name; do
  J=$O/realism_v5_${name}_dtfix_gateoff_gp_arm06.json; T=${J%.json}.txt
  if [ -s $J ] || [ -s $T ]; then echo "SKIP exists $J"; continue; fi
  [[ $t = /* ]] || t=$O/$t
  echo "START $name $(date +%H:%M:%S)"; taskset -c 0-1 ${HGS_PY:-python3} $O/_run_j_gateoff_gp.py $t --json $J > $T 2>$O/_batch_dtfix_${name}.err; echo "END $name rc=$? $(date +%H:%M:%S)"
done < $O/_dtfix.list
echo ALLDONE
