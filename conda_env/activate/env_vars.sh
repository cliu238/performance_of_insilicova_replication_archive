#!/bin/sh
# $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
CONDA_PREFIX="~/.conda/envs/insilico"
export LD_LIBRARY_SAVE="$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib/R/lib:$CONDA_PREFIX/lib:/usr/lib/jvm/java/jre/lib/amd64/server:$LD_LIBRARY_PATH"

