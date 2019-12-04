#! /bin/bash

ANALYSIS=${1:-default}
SYMPTOMS=${2:-insilico}
CAUSES=${3:-insilico}

cd $(dirname $0)/..
REPO_DIR=`pwd`
cd -

INPUT_DIR=$REPO_DIR/data/"$ANALYSIS"_"$CAUSES"_"$SYMPTOMS"
OUT_DIR=$REPO_DIR/data/validate
CLF=insilico

mkdir -p $OUT_DIR

for STATSFILE in accuracy ccc csmf predictions; do
for MODULE in adult child neonate; do
for HCE in w_hce no_hce; do

    FILE_ID="$ANALYSIS"_"$CLF"_"$MODULE"_"$HCE"_"$CAUSES"_"$SYMPTOMS"
    OUT_FILE=$OUT_DIR/"$FILE_ID"_"$STATSFILE".csv
    FILE_PATTERN="$FILE_ID"_splits_*_"$STATSFILE".csv
    
    rm -f $OUT_FILE
    COUNTER=0
    for F in $( find $INPUT_DIR -type f -name $FILE_PATTERN -print ); do
        if [[ $COUNTER = 0 ]]; then
            more $F >> $OUT_FILE
        else
            tail -n +2 $F >> $OUT_FILE
        fi
        COUNTER=$( echo $COUNTER + 1 | bc )
    done
done
done
done
