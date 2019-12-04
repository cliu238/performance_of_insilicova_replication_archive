#!/bin/sh
# $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
export LD_LIBRARY_PATH="$LD_LIBRARY_SAVE"
unset LD_LIBRARY_SAVE

