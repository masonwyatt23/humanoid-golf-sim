#!/bin/bash
# Paths come from env: HGS_EVAL_REPO, HGS_TRAINER_REPO, HGS_RO_ROOT (dir of read-only exports), HGS_PY (interpreter, default python3).
# K33a-d / K34a-b at 50k-300k on BOTH heads (Evaluator 2026-10-24 ET). Main table: V3_TEE=0 (default tee), V3_HEAD=box and realistic, v3c and v3d (4 runs/ckpt);
# INFO: v3d crown tee per head (box = 'compensates for the oversized sim head'; realistic = 'realistic head, crown tee (equator at sourced crown)').
# V3_FACE_H=none everywhere (K33a/b args face_h 0.053 is sensitivity only; main table = standard head geometry).
# Code: box rows on each run's own Trainer commit (K33a/b 9c7d437 --tee_mode crown; K33c/d 9cc20e9 --tee_anneal; K34a/b a9d917e --head realistic);
# realistic rows on a9d917e (first commit with --head realistic; default head bit-identical per its message). One job at a time, taskset -c 0-1, 2 workers, BLAS 2.
cd ${HGS_EVAL_REPO:?set HGS_EVAL_REPO to the evaluator checkout}; O=results/overnight; PY=${HGS_PY:-python3}; S=${HGS_TRAINER_REPO:?set HGS_TRAINER_REPO to the Trainer checkout}/results/v5_runs/_snap; R=${HGS_RO_ROOT:?set HGS_RO_ROOT to the dir holding _ro_trainer_<hash> exports}/_ro_trainer_
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2; unset V3_FRICTION_RANGE; export V3_FACE_H=none
while ! grep -q '^ALLDONE' $O/_batch_V4rebase.log 2>/dev/null; do sleep 30; done   # serial after Part A
echo "BEGIN $(date '+%F %T %Z')"
L=$O/_evalsnap_md5_K33K34.txt
for r in "K34a_s78 a9d917e" "K34b_s79 a9d917e" "K33a_s74 9c7d437" "K33b_s75 9c7d437" "K33c_s76 9cc20e9" "K33d_s77 9cc20e9"; do set -- $r; run=$1; BX=$R$2; RX=${R}a9d917e
 for n in 300000 250000 200000 150000 100000 50000; do tag=${run}_$((n/1000))k; d=$S/${run}_$n; mkdir -p $O/_evalsnap/$tag
  for f in ckpt_$n.zip ckpt_${n}_vecnorm.pkl args.json; do [ -s $O/_evalsnap/$tag/$f ] || cp -p $d/$f $O/_evalsnap/$tag/; a=$(md5sum < $d/$f | cut -c1-32); b=$(md5sum < $O/_evalsnap/$tag/$f | cut -c1-32); echo "$tag $f trainer_snap=$a evalsnap=$b $([ $a = $b ] && echo MATCH || echo MISMATCH)" >> $L; done
  grep -q "^$tag .*MISMATCH" $L && { echo "BLOCKER $tag md5 mismatch, skipped"; continue; }
  echo "PRECHECK $tag $(taskset -c 0-1 $PY $O/_precheck_layout.py $O/_evalsnap/$tag/ckpt_$n $BX ${HGS_TRAINER_REPO:?set HGS_TRAINER_REPO to the Trainer checkout} 2>/dev/null | tail -1)"
  for q in "box v3c 0 tee0box" "box v3d 0 tee0box" "realistic v3c 0 tee0real" "realistic v3d 0 tee0real" "box v3d crown crownbox" "realistic v3d crown crownreal"; do set -- $q
   X=$BX; [ $1 = realistic ] && X=$RX; H=""; [ $2 = v3d ] && H="--harness v3d"
   J=$O/realism_v5_${tag}_${4}_${2}_gateoff_gp_arm06.json; [ -s $J ] && { echo "SKIP $tag $2 $4"; continue; }
   echo "START $tag $2 $4 $(basename $X) $(date +%T)"; V3_HEAD=$1 V3_TEE=$3 taskset -c 0-1 $PY $O/_run_j_gateoff_gp_v3.py $O/_evalsnap/$tag/ckpt_$n --v5-repo $X $H --json $J.tmp > ${J%.json}.txt 2>$O/_batch_K33K34_${tag}_${2}_$4.err; rc=$?
   if [ $rc -eq 0 ] && [ -s $J.tmp ]; then mv $J.tmp $J; else echo "FAILED $tag $2 $4 rc=$rc: $(grep -h 'mismatch\|Error\|SystemExit' $O/_batch_K33K34_${tag}_${2}_$4.err | tail -1)"; fi; echo "END $tag $2 $4 rc=$rc $(date +%T)"
  done
 done
done; echo "ALLDONE $(date '+%F %T %Z')"
