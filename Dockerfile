FROM ubuntu:18.04

MAINTAINER Jonathan Joseph <josephj7@uw.edu>
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq && apt-get install -y \
         curl \
         dpkg \
         dos2unix \
         git \
         graphviz \
         make \
         pandoc \
         pandoc-citeproc \
         python3 \
         python3-pip \
         python3-venv \
         python3-tk \
         r-base \
         r-base-dev \
         vim \
         wget \
         libfreetype6-dev \
         pkg-config \
         wget tar curl  \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# # Zombie reaping...just in case. See https://github.com/krallin/tini/issues/8
# RUN TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
#     curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
#     dpkg -i tini.deb && \
#     rm tini.deb && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

# Update package lists
RUN apt-get update -qq

# Install Python pip
RUN apt-get install -y python3-pip libffi-dev gcc

# Upgrade pip
RUN python3 -m pip --no-cache-dir install --upgrade pip==19.3.1

# Upgrade setuptools and wheel
RUN python3 -m pip --no-cache-dir install --upgrade setuptools

RUN python3 -m pip --no-cache-dir install --upgrade wheel
# Install ipywidgets with a version that does not require comm
RUN python3 -m pip install --no-cache-dir ipywidgets==7.5.1
# Install Jupyter and notebook
RUN python3 -m pip --no-cache-dir install jupyter==1.0.0

RUN python3 -m pip --no-cache-dir install notebook==5.4.0

# Install core scientific libraries
RUN python3 -m pip --no-cache-dir install numpy==1.14.1

RUN python3 -m pip --no-cache-dir install scipy==1.5.4

RUN python3 -m pip --no-cache-dir install pandas==1.1.5

#RUN python3 -m pip --no-cache-dir install pandas==0.22.0

RUN python3 -m pip --no-cache-dir install statsmodels==0.8.0

# Install visualization libraries
RUN python3 -m pip --no-cache-dir install matplotlib==2.1.2

RUN python3 -m pip --no-cache-dir install seaborn==0.8.1

# Install scikit-learn
RUN python3 -m pip --no-cache-dir install scikit-learn==0.19.1

# Install YAML and Excel file handling libraries
RUN python3 -m pip --no-cache-dir install pyyaml==3.12

RUN python3 -m pip --no-cache-dir install openpyxl==2.5.0

RUN python3 -m pip --no-cache-dir install xlrd==1.1.0

# Install additional utilities
RUN python3 -m pip --no-cache-dir install click==6.6

RUN python3 -m pip --no-cache-dir install ipython==6.2.1

RUN python3 -m pip --no-cache-dir install jinja2==2.10

# Install testing and documentation tools
RUN python3 -m pip --no-cache-dir install pytest==3.4.0

RUN python3 -m pip --no-cache-dir install sphinx==1.7.0

# Install R-Python interface
RUN python3 -m pip --no-cache-dir install rpy2==2.8.5

# # Clean up cache
# RUN rm -rf /root/.cache /usr/local/bin/__pycache__

# # Remove Python __pycache__ directories
# RUN find /usr/local/lib/python3.5/dist-packages/ -depth -type d -name __pycache__ -exec rm -rf '{}' \;
## Install Java
# Copy the Oracle JDK 8 tarball into the Docker image
COPY ./jdk-8u202-linux-arm64-vfp-hflt.tar.gz /tmp/jdk8.tar.gz

# Create the JDK directory and extract the tarball
RUN mkdir -p /usr/lib/jvm && \
    tar -xzf /tmp/jdk8.tar.gz -C /usr/lib/jvm && \
    rm /tmp/jdk8.tar.gz

# Set Java environment variables
ENV JAVA_HOME=/usr/lib/jvm/jdk1.8.0_202
ENV PATH="$JAVA_HOME/bin:$PATH"

# Verify Java installation
RUN java -version

# Clean up unnecessary files
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

ARG INSILICOVA_VERSION=1.1.4

# Configure R and Java and install the InSilicoVA package.
# R is looking for default-java for it's configuration so symlink java-8-oracle to default-java
# Symlink Java 8 to default-java for R configuration
RUN ln -s /usr/lib/jvm/jdk1.8.0_202/ /usr/lib/jvm/default-java

# Reconfigure Java for R
RUN R CMD javareconf

# Configure Java for RJava package
RUN echo "/usr/lib/jvm/jdk1.8.0_202/jre/lib/amd64/server/" > /etc/ld.so.conf.d/rJava.conf

# Update dynamic linker run-time bindings
RUN /sbin/ldconfig

R -q -e "install.packages('devtools', repos='http://cran.us.r-project.org')"
R -q -e "devtools::install_version('ggplot2', version='3.1.1', repos='http://cran.us.r-project.org')"

# # Install required R packages
# RUN R -q -e "install.packages(c('rJava', 'coda', 'ggplot2'), repos='http://cran.us.r-project.org')"

# # Install required R packages explicitly in the default library path
# RUN R -q -e "install.packages(c('rJava', 'coda', 'ggplot2'), repos='http://cran.us.r-project.org', lib='/usr/local/lib/R/site-library')"

# # Verify that the dependencies are installed correctly
# RUN R -q -e "installed.packages()[, c('Package', 'Version')]"

# # Download the InSilicoVA package
# RUN wget https://cran.r-project.org/src/contrib/Archive/InSilicoVA/InSilicoVA_1.1.4.tar.gz

# # # Install the InSilicoVA package
# RUN R CMD INSTALL InSilicoVA_1.1.4.tar.gz

# # Clean up downloaded files
# RUN rm InSilicoVA_$INSILICOVA_VERSION.tar.gz && rm -rf /tmp/downloaded_packages/ /tmp/*.rds



# VOLUME ["/home"]

# RUN \
#     # Set the default backend for matplotlib to avoid missing display errors
#     sed -i 's/backend      \: TkAgg/backend      \: Agg/' /usr/local/lib/python3.5/dist-packages/matplotlib/mpl-data/matplotlibrc && \

#     # Set python3 as the default python for the user
#     ln -s /usr/bin/python3 /usr/local/bin/python && \

#     # Alias the notebook command. Set the ip so it can be found by a browser outside the docker
#     echo "alias notebook=' jupyter notebook --ip 0.0.0.0 --no-browser --allow-root'" >> /etc/bash.bashrc

# EXPOSE 8888

# WORKDIR /home

# ENTRYPOINT [ "/usr/bin/tini", "--" ]

CMD [ "/bin/bash" ]