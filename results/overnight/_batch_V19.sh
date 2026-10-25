#!/bin/bash
# Paths come from env: HGS_EVAL_REPO, HGS_TRAINER_REPO, HGS_RO_ROOT (dir of read-only exports), HGS_PY (interpreter, default python3).
# V19 official grading (Evaluator 2026-10-25 ET): V18w_s661 100k (--stance_obs, V12X keys; Trainer cmd b869788b). RO export 7f5445e0 (Trainer box HEAD, contains b869788b). Worker forwards stance_obs from args.json. Snapshot and keys md5s verified, not published.
# Rows as _batch_V18.sh: v4 MAIN 1.5in (gating), v4 crown INFO, v3c and v3d at 1.5in, v5 heldout and D-plane NON-GATING; plus v4.1 --reground INFO row (NON-GATING, as _batch_V41.sh).
# One job at a time, taskset -c 0-1, 2 workers, BLAS threads 2. Layout pre-check per checkpoint; a v4 address mismatch stops the checkpoint.
cd ${HGS_EVAL_REPO:?set HGS_EVAL_REPO to the evaluator checkout}; O=results/overnight; PY=${HGS_PY:-python3}; X4=${HGS_RO_ROOT:?set HGS_RO_ROOT to the dir holding _ro_trainer_<hash> exports}/_ro_trainer_7f5445e0
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2; unset V3_FRICTION_RANGE V3_FACE_H
run() { # tag ck harness teeenv teetag
  J=$O/realism_v5_${1}_${5}_${3}_gateoff_gp_arm06.json; [ -s $J ] && { echo "SKIP $1 $3 $5"; return 0; }
  H="--harness $3"; [ $3 = v3c ] && H=""
  echo "START $1 $3 $5 $(date +%T)"; V3_HEAD=v4 V3_TEE=$4 taskset -c 0-1 $PY $O/_run_j_gateoff_gp_v3.py $O/_evalsnap/$1/$2 --v5-repo $X4 $H --json $J.tmp > ${J%.json}.txt 2>$O/_batch_V19_${1}_${3}_$5.err; rc=$?
  if [ $rc -eq 0 ] && [ -s $J.tmp ]; then mv $J.tmp $J; else echo "FAILED $1 $3 $5 rc=$rc: $(grep -h 'mismatch\|Error\|SystemExit' $O/_batch_V19_${1}_${3}_$5.err | tail -1)"; fi; echo "END $1 $3 $5 rc=$rc $(date +%T)"; return $rc
}
for p in "V18w_s661_100k ckpt_100000 full"; do set -- $p
  PC=$(taskset -c 0-1 $PY $O/_precheck_layout.py $O/_evalsnap/$1/$2 $X4 ${HGS_TRAINER_REPO:?set HGS_TRAINER_REPO to the Trainer checkout} 2>/dev/null | tail -1); echo "PRECHECK $1 $PC"
  case "$PC" in LAYOUT_OK*) ;; *) echo "BLOCKER $1: layout pre-check not OK, checkpoint stopped"; exit 2;; esac
  run $1 $2 v4 1.5in 15in || { echo "BLOCKER $1: v4 main failed, checkpoint stopped"; exit 3; }
  run $1 $2 v4 crown crown16
  [ $3 = full ] && { run $1 $2 v3c 1.5in 15in; run $1 $2 v3d 1.5in 15in; }
done; echo ALLDONE $(date +%T)
# v5 held-out DR, NON-GATING (as V14)
J=$O/realism_v5_V18w_s661_100k_15in_v5_heldout12_gateoff_gp_arm06.json
[ -s $J ] || { echo "START heldout $(date +%T)"; V3_HEAD=v4 V3_TEE=1.5in taskset -c 0-1 $PY $O/_run_j_gateoff_gp_v3.py $O/_evalsnap/V18w_s661_100k/ckpt_100000 --v5-repo $X4 --harness v5 --heldout-dr 24 --heldout2-dr 32 --json $J.tmp > ${J%.json}.txt 2>$O/_batch_V19_V18w_s661_v5_heldout12.err && mv $J.tmp $J; echo "END heldout rc=$? $(date +%T)"; }
echo HELDOUT_DONE $(date +%T)
# v5 D-plane on perturbed robustness episodes (as V16b, harness b9e38999), NON-GATING
J=$O/realism_v5_V18w_s661_100k_15in_v5dplane_gateoff_gp_arm06.json
[ -s $J ] || { echo "START dplane $(date +%T)"; V3_HEAD=v4 V3_TEE=1.5in taskset -c 0-1 $PY $O/_run_j_gateoff_gp_v3.py $O/_evalsnap/V18w_s661_100k/ckpt_100000 --v5-repo $X4 --harness v5 --heldout-dr 0 --json $J.tmp > ${J%.json}.txt 2>$O/_batch_V19b_V18w_s661_100k.err && mv $J.tmp $J; echo "END dplane rc=$? $(date +%T)"; }
echo DPLANE_DONE $(date +%T)
# v4.1 robustness (re-grounded, info only, non-gating), as _batch_V41.sh
J=$O/realism_v5_V18w_s661_100k_15in_v41_v4_gateoff_gp_arm06.json
[ -s $J ] || { echo "START v41 $(date +%T)"; V3_HEAD=v4 V3_TEE=1.5in taskset -c 0-1 $PY $O/_run_j_gateoff_gp_v3.py $O/_evalsnap/V18w_s661_100k/ckpt_100000 --v5-repo $X4 --harness v4 --reground --json $J.tmp > ${J%.json}.txt 2>$O/_batch_V19_V18w_s661_100k_15in_v41.err && mv $J.tmp $J; echo "END v41 rc=$? $(date +%T)"; }
echo V41_DONE $(date +%T)
