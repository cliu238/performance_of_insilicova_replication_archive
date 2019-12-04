FROM ubuntu:16.04

MAINTAINER Jonathan Joseph <josephj7@uw.edu>

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
         python3.5-venv \
         python3-tk \
         r-base \
         r-base-dev \
         vim \
         wget \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Zombie reaping...just in case. See https://github.com/krallin/tini/issues/8
RUN TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
    curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
    dpkg -i tini.deb && \
    rm tini.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python SciPy stack
RUN pip3 --no-cache-dir install pip --upgrade && \
  pip3 --no-cache-dir install setuptools --upgrade && \
  pip3 --no-cache-dir install wheel --upgrade && \
  pip3 --no-cache-dir install \
          click==6.6 \
          ipython==6.2.1 \
          jinja2==2.10 \
          jupyter==1.0.0 \
          matplotlib==2.1.2 \
          notebook==5.4.0 \
          numpy==1.14.1 \
          openpyxl==2.5.0 \
          pandas==0.22.0 \
          pytest==3.4.0 \
          pyyaml==3.12 \
          rpy2==2.8.5 \
          scikit-learn==0.19.1 \
          scipy==1.0.0 \
          seaborn==0.8.1 \
          sphinx==1.7.0 \
          statsmodels==0.8.0 \
          xlrd==1.1.0 \
  && rm -rf /root/.cache /usr/local/bin/__pycache__ \
  && find /usr/local/lib/python3.5/dist-packages/ -depth -type d -name __pycache__ -exec rm -rf '{}' \;

## Install Java
RUN echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" \
      | tee /etc/apt/sources.list.d/webupd8team-java.list && \
    echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" \
      | tee -a /etc/apt/sources.list.d/webupd8team-java.list && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EEA14886 && \
    echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" \
        | /usr/bin/debconf-set-selections && \
    apt-get update && \
    apt-get install -y oracle-java8-installer && \
    update-alternatives --display java && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ARG INSILICOVA_VERSION=1.1.4

# Configure R and Java and install the InSilicoVA package.
# R is looking for default-java for it's configuration so symlink java-8-oracle to default-java
RUN ln -s /usr/lib/jvm/java-8-oracle/ /usr/lib/jvm/default-java && \
    R CMD javareconf && \
    echo "/usr/lib/jvm/java-8-oracle/jre/lib/amd64/server/" > /etc/ld.so.conf.d/rJava.conf && \
    /sbin/ldconfig && \
    R -q -e "install.packages(c('rJava', 'coda', 'ggplot2'), repos='http://cran.us.r-project.org')" && \
    wget https://cran.r-project.org/src/contrib/Archive/InSilicoVA/InSilicoVA_$INSILICOVA_VERSION.tar.gz && \
    R CMD INSTALL InSilicoVA_$INSILICOVA_VERSION.tar.gz  && \
    rm InSilicoVA_$INSILICOVA_VERSION.tar.gz && \
    rm -rf /tmp/downloaded_packages/ /tmp/*.rds

VOLUME ["/home"]

RUN \
    # Set the default backend for matplotlib to avoid missing display errors
    sed -i 's/backend      \: TkAgg/backend      \: Agg/' /usr/local/lib/python3.5/dist-packages/matplotlib/mpl-data/matplotlibrc && \

    # Set python3 as the default python for the user
    ln -s /usr/bin/python3 /usr/local/bin/python && \

    # Alias the notebook command. Set the ip so it can be found by a browser outside the docker
    echo "alias notebook=' jupyter notebook --ip 0.0.0.0 --no-browser --allow-root'" >> /etc/bash.bashrc

EXPOSE 8888

WORKDIR /home

ENTRYPOINT [ "/usr/bin/tini", "--" ]

CMD [ "/bin/bash" ]
