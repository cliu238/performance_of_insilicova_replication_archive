:: $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh

:: Save the current environment variables
@set CONDA_PREFIX_SAVE = %CONDA_PREFIX%
@set RHOME_SAVE = %RHOME%
@set R_LIBS_USER_SAVE = %R_LIBS_USER%
@set JAVA_HOME_SAVE = %JAVA_HOME%

:: Set them to the conda environment
@set CONDA_PREFIX=my/path/to/../envs/insilico
@set RHOME=%CONDA_PREFIX%/R/bin
@set R_LIBS_USER=%CONDA_PREFIX%/R/library
@set JAVA_HOME=%CONDA_PREFIX%/Library/jre