REPO_DIR = $(dirname $0)/..

python $REPO_DIR/src/download.py
$REPO_DIR/scripts/map_data.sh
