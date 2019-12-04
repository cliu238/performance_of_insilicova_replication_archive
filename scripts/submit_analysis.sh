#! /bin/bash

ANALYSIS=${1:-default}
SPLITS=${2:-2}
SYMPTOMS=${3:-insilico}
CAUSES=${4:-insilico}
EXTENDED=${5:-0}

shift 5

cd $(dirname $0)/..
REPO_DIR=`pwd`
cd -

LOG_DIR=$REPO_DIR/data/logs

# Working directory in singularity container
WORK_DIR=/home

if [[ "$EXTENDED" == "1" ]]; then
    CLF_PARAM="-p n_sim 12000"
    EXT="_ext"

    if [[  "$ANALYSIS" == "default" ]]; then
        OUT_DIR=$WORK_DIR/data/extended_default_insilico
    else
        OUT_DIR=$WORK_DIR/data/extended_"$CAUSES"_"$SYMPTOMS"
    fi
else
    CLF_PARAM=""
    EXT=""
    OUT_DIR=$WORK_DIR/data/"$ANALYSIS"_"$CAUSES"_"$SYMPTOMS"
fi

CLF=insilico
STEP=1

mkdir -p $LOG_DIR

if [[ "$ANALYSIS" == "default" ]]; then
    ANALYSIS_="no-train"
else
    ANALYSIS_="validate"
fi

for MODULE in adult child neonate; do
for HCE in "" "--no-hce"; do
for START in $(seq 0 $STEP $(echo $SPLITS -1 | bc)); do

    STOP=$(echo $START+$STEP-1 | bc)
    if [[ "$HCE" == "--no-hce" ]]; then HCE_=no_hce; else HCE_=w_hce; fi
    JNAME="$ANALYSIS"_"$CLF"_"$MODULE"_"$HCE_"_"$CAUSES"_"$SYMPTOMS$EXT"
    JNAME="$JNAME"_splits_"$START"-"$STOP"
    LOG=$LOG_DIR/$JNAME
    
    qsub -N $JNAME -P proj_va -o $LOG -e $LOG -pe multi_slot 5 -l mem_free=10g \
         $REPO_DIR/scripts/python_w_singularity.sh $REPO_DIR \
         $WORK_DIR/src/analysis.py -a $ANALYSIS_ -m $MODULE --clf $CLF \
         -c $CAUSES -s $SYMPTOMS $HCE --n-splits $SPLITS --subset $START $STOP \
         -o $OUT_DIR $CLF_PARAM

done
done
done
