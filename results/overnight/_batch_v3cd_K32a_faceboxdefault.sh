#!/bin/bash
# Paths come from env: HGS_EVAL_REPO, HGS_TRAINER_REPO, HGS_RO_ROOT (dir of read-only exports), HGS_PY (interpreter, default python3).
# K32a_s72 100k/200k re-run with V3_FACE_H=none (64 mm head box, default face; args face_h 0.053 NOT applied): v3c tee 0 and live v3d crown tee. RO export 13f0d2b.
cd ${HGS_EVAL_REPO:?set HGS_EVAL_REPO to the evaluator checkout}; O=results/overnight; PY=${HGS_PY:-python3}
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 V3_FACE_H=none; unset V3_FRICTION_RANGE
for p in "K32a_s72_100k ckpt_100000" "K32a_s72_200k ckpt_200000"; do set -- $p
 for R in "v3c 0 tee0box" "v3d crown teecrownbox"; do set -- $1 $2 $R
  J=$O/realism_v5_${1}_${5}_${3}_gateoff_gp_arm06.json; X=""; [ $3 = v3d ] && X="--harness v3d"
  echo "START $1 $5 $(date +%T)"; V3_TEE=$4 taskset -c 0-1 $PY $O/_run_j_gateoff_gp_v3.py $O/_evalsnap/$1/$2 --v5-repo ${HGS_RO_ROOT:?set HGS_RO_ROOT to the dir holding _ro_trainer_<hash> exports}/_ro_trainer_13f0d2b $X --json $J.tmp > ${J%.json}.txt 2>$O/_batch_v3cd_K32a_${1}_$5.err; rc=$?
  [ $rc -eq 0 ] && [ -s $J.tmp ] && mv $J.tmp $J; echo "END $1 $5 rc=$rc $(date +%T)"
 done
done; echo ALLDONE
