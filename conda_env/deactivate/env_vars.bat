:: $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh

:: Reset variable to previous value from before activating
@set CONDA_PREFIX=%CONDA_PREFIX_SAVE%
@set RHOME=%RHOME_SAVE%
@set R_LIBS_USER=%R_LIBS_USER_SAVE%
@set JAVA_HOME=%JAVA_HOME_SAVE%

:: Clear our save variables
@set CONDA_PREFIX_SAVE=
@set RHOME_SAVE=
@set R_LIBS_USER_SAVE=
@set JAVA_HOME_SAVE=