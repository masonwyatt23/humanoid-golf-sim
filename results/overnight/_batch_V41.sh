#!/bin/bash
# Paths come from env: HGS_EVAL_REPO, HGS_RO_ROOT (dir of read-only exports), HGS_PY (interpreter, default python3).
# Harness v4.1 INFO row (NON-GATING, Orchestrator 2026-10-25): --reground on v4 1.5in, RO export b663c9f6 (as _batch_V18.sh). v4 stays the official gate.
# First: regression with the patched worker/harness and the option OFF: V18i_s560 150k v4 1.5in must be byte-identical to the V17 official JSON.
# One job at a time, taskset -c 0-1, 2 workers, BLAS threads 2.
cd ${HGS_EVAL_REPO:?set HGS_EVAL_REPO}; O=results/overnight; PY=${HGS_PY:-python3}; X4=${HGS_RO_ROOT:?set HGS_RO_ROOT}/_ro_trainer_b663c9f6
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2; unset V3_FRICTION_RANGE V3_FACE_H
run() { # tag ck teetag extra...
  t=$1; c=$2; tt=$3; shift 3; J=$O/realism_v5_${t}_${tt}_v4_gateoff_gp_arm06.json; [ -s $J ] && { echo "SKIP $t $tt"; return 0; }
  echo "START $t $tt $(date +%T)"; V3_HEAD=v4 V3_TEE=1.5in taskset -c 0-1 $PY $O/_run_j_gateoff_gp_v3.py $O/_evalsnap/$t/$c --v5-repo $X4 --harness v4 "$@" --json $J.tmp > ${J%.json}.txt 2>$O/_batch_V41_${t}_${tt}.err; rc=$?
  [ $rc -eq 0 ] && [ -s $J.tmp ] && mv $J.tmp $J; echo "END $t $tt rc=$rc $(date +%T)"
}
run V18i_s560_150k ckpt_150000 15in_regV41
run V18l_s590_50k ckpt_50000 15in_v41 --reground
run V18i_s560_150k ckpt_150000 15in_v41 --reground
run V18f_s530_50k ckpt_50000 15in_v41 --reground
echo ALLDONE $(date +%T)
