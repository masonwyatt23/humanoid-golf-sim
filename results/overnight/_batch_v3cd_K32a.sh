#!/bin/bash
# Paths come from env: HGS_EVAL_REPO, HGS_TRAINER_REPO, HGS_RO_ROOT (dir of read-only exports), HGS_PY (interpreter, default python3).
# Regression (K30a 100k det-only, args tee) + K32a_s72 100k/200k: v3c at V3_TEE=0 (old tee), v3d LIVE at V3_TEE=crown (derived), plus INFO v3d at the checkpoint's own args tee (0.020). RO export 13f0d2b.
cd ${HGS_EVAL_REPO:?set HGS_EVAL_REPO to the evaluator checkout}; O=results/overnight; PY=${HGS_PY:-python3}
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2; unset V3_FRICTION_RANGE V3_FACE_H
J=$O/realism_v5_K30a_s66_100k_regress_teeargs_det_v3c.json; echo "START regress $(date +%T)"
V3_TEE=args taskset -c 0-1 $PY $O/_run_j_gateoff_gp_v3.py $O/_evalsnap/K30a_s66_100k/ckpt_100000 --v5-repo ${HGS_RO_ROOT:?set HGS_RO_ROOT to the dir holding _ro_trainer_<hash> exports}/_ro_trainer_4a955d8 --robustness 0 --json $J > ${J%.json}.txt 2>$O/_batch_v3cd_K32a_regress.err; echo "END regress rc=$? $(date +%T)"
for p in "K32a_s72_100k ckpt_100000" "K32a_s72_200k ckpt_200000"; do set -- $p
 for R in "v3c 0 tee0" "v3d crown teecrown" "v3d args teeargs"; do set -- $1 $2 $R
  J=$O/realism_v5_${1}_${5}_${3}_gateoff_gp_arm06.json; [ -s $J ] && { echo SKIP $1 $5; continue; }
  X=""; [ $3 = v3d ] && X="--harness v3d"
  echo "START $1 $3 $5 $(date +%T)"; V3_TEE=$4 taskset -c 0-1 $PY $O/_run_j_gateoff_gp_v3.py $O/_evalsnap/$1/$2 --v5-repo ${HGS_RO_ROOT:?set HGS_RO_ROOT to the dir holding _ro_trainer_<hash> exports}/_ro_trainer_13f0d2b $X --json $J.tmp > ${J%.json}.txt 2>$O/_batch_v3cd_K32a_${1}_${3}_$5.err; rc=$?
  if [ $rc -eq 0 ] && [ -s $J.tmp ]; then mv $J.tmp $J; else echo "FAILED $1 $3 $5 rc=$rc"; fi; echo "END $1 $3 $5 rc=$rc $(date +%T)"
 done
done; echo ALLDONE
