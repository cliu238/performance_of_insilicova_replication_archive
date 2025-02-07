InSilicoVA
==========
### Purpose:
This repo holds code used to validate the result in [Probabilistic
Cause-of-death Assignment using Verbal Autopsies](http://amstat.tandfonline.com/
doi/full/10.1080/01621459.2016.1152191) by Tyler H. McCormick, Zehang Richard
Li, Clara Calvert, Amelia C. Crampin, Kathleen Kahn & Samuel J. Clark.

### Setup:
This analysis is conducted using Python 2.7. The InSilicoVA algorithm is
publicly available as a R package. The package makes calls to Java (using rJava)
to perform heavy computation. I strongly recommended running this code in a
conda environment. The `./conda_env/` directory of this repo has resources for
configuring an Anaconda environment with the software and packages required to
run this analysis.

###### Docker for Setup

Docker images for smartva and insilico are now in the private IHME
docker repo. You can [log in with your IHME credentials here](https://reg.ihme.uw.edu/harbor/sign-in?redirect_url=%2Fharbor%2Fprojects). Then from the command line:

```
docker login reg.ihme.uw.edu
docker pull reg.ihme.uw.edu/va/insilico:1.0.0
```

###### Setup a Conda Environment
To setup a conda environment, `cd` into the root directory of this git repo and
run one of the following commands (depending on your operating system--sorry OSX
users, I don't have a mac and everyone thinks you're pretentious anyways):

```
conda env create -n insilico -f conda_env/windows_environment.yml

conda env create -n insilico -f conda_env/linux_environment.yml
```

If that fails, it is likely that a specific version of a package is not
available on your system or conflict in some way. In this case, it should
probably suffice to just specify the minimal required packages and let conda
resolve the package version dependencies. After all it is a package manager. In
this case, run:

```
conda env create -n insilico -f environment.yml
```

Assuming that went well, you should now have a conda environment named
`insilico` with Python 2.7, R 3.3.2, and Java 1.8 installed in it. You should
also have suitable Python packages to consider your environment a working SciPy
environment. Also rJava should be installed.

###### Set environment variables
The following environment variables may be important (depending on your system):
*  `RHOME` - pointing at `.../R/bin`
* `JAVA_HOME` - pointing at `.../jre/`
* `LD_LIBRARY_PATH` - `.../R/lib` and `.../jre/lib` should be prepended to
  whatever was initially there.

Environment variables can be set through conda environments by placing
`env_vars.sh` (or `env_vars.bat` on Windows OS) in the
`{CONDA_PREFIX}/etc/conda/activate.d/` and
`{CONDA_PREFIX}/etc/conda/deacative.d/`
directories of the conda environment subdirectory. `CONDA_PREFIX` is something
like `~/.conda/envs/insilico` or
`C:\Users\{username}\AppData\Local\Continuum\Anaconda3\envs\insilico`.
`{CONDA_PREFIX}/etc/` should exist but you will need to create the rest of the
directory tree. Versions of `env_vars` files which worked for me are in the
`./conda_env/` directory of this repo.

Once the `env_vars` files are in the correct place activate the environment
using `source activate insilico` (or `activate insilico` on Windows). You can
verify that the shell is pointing at the correct versions of Python and R by
running `which python` and `which R` if you're lucky enough to NOT be working
on Windows OS. If you're stuck on Windows OS, you can run some convoluted
silliness like: `python -c "import sys;print(sys.executable)"` and
`R -q -e "R.home()"` to verify the default installations.

At this point `rJava` should successfully run. The command
`R -q -e "library('rJava')""` should run without throwing any errors. If it
doesn't (which is likely) here are a list of things to try fiddling with:

* Set `JAVA_HOME`. Try setting it to `.../jre` or `.../jdk` or
  `.../something/bin` or unset it. Results may vary depending on your system.
* Try reinstalling java or using default system version. It's important that the
  version of java matches the version of R (32-bit or 64-bit) or else everything
  fails.
* On Linux, try running `R CMD javareconf` and then reinstalling `rJava`
* Uninstall `rJava` through conda with `conda uninstall r-rJava` and reinstall
  it through R with
  `R -q -e "install.packages('rJava', repos='http://cran.us.r-project.org')`

###### Install InSilicoVA
The InSilicoVA package should be installed through R. It may be useful to
confirm that the location of the R library is consistent between the R
installations and the R instance running in Python through rpy2. To do this
run the following two commands:

```
R -q -e ".libPaths()[1]"
python -c "import rpy2.robjects;print(list(rpy2.robjects.r('.libPaths()'))[0])"
```

These should be pointing to the same directory. If not, set `R_LIBS_USER` in the
activate and deactivate `env_vars` files as shown in `env_vars.bat`. Deactivate
the environment and re-activate it and verify that the paths align. If the paths
align, install the package with the following command:
```
R -q -e "install.packages('InSilicoVA', repos='http://cran.us.r-project.org')"
```

###### Verify the environment works
To test the environment, navigate to the root directory of the repo and run:

```
py.test test/test_environment.py
```

It should have a happy green line and declare one test passed in less than 30
seconds. If it says it failed, well, something went wrong... Good luck.

### Data:
This replication study uses the PHMRC dataset which is publicly available on
the [Global Health Data Exchange (GHDx)](http://ghdx.healthdata.org/record/
population-health-metrics-research-consortium-gold-standard-verbal-autopsy-data-
2005-2011)
