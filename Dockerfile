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
         libffi-dev \
         build-essential \
         libfreetype6-dev \
         pkg-config \
         libpng-dev \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# # Zombie reaping...just in case. See https://github.com/krallin/tini/issues/8
# RUN TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
#     curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
#     dpkg -i tini.deb && \
#     rm tini.deb && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel
RUN pip3 --no-cache-dir install pip==20.3.4 --upgrade
RUN pip3 --no-cache-dir install setuptools --upgrade
RUN pip3 --no-cache-dir install wheel --upgrade

# Install individual Python packages
RUN pip3 --no-cache-dir install click==6.6
RUN pip3 --no-cache-dir install ipython==6.2.1
RUN pip3 --no-cache-dir install jinja2==2.10
RUN pip3 --no-cache-dir install jupyter==1.0.0
RUN pip3 --no-cache-dir install matplotlib==2.1.2
RUN pip3 --no-cache-dir install notebook==5.4.0
RUN pip3 --no-cache-dir install numpy==1.14.1
RUN pip3 --no-cache-dir install openpyxl==2.5.0
RUN pip3 --no-cache-dir install pandas==0.22.0
RUN pip3 --no-cache-dir install pytest==3.4.0
RUN pip3 --no-cache-dir install pyyaml==3.12
RUN pip3 --no-cache-dir install rpy2==2.8.5
RUN pip3 --no-cache-dir install scipy==1.0.0
RUN pip3 --no-cache-dir install scikit-learn==0.19.1
RUN pip3 --no-cache-dir install seaborn==0.8.1
RUN pip3 --no-cache-dir install sphinx==1.7.0
RUN pip3 --no-cache-dir install statsmodels==0.8.0
RUN pip3 --no-cache-dir install xlrd==1.1.0

# Cleanup cache to reduce image size
RUN rm -rf /root/.cache /usr/local/bin/__pycache__
RUN find /usr/local/lib/python3.5/dist-packages/ -depth -type d -name __pycache__ -exec rm -rf '{}' \;

# 手动下载安装 Oracle JDK 8
RUN mkdir -p /usr/lib/jvm && \
    wget --no-check-certificate --header "Cookie: oraclelicense=accept-securebackup-cookie" \
    "https://download.oracle.com/otn-pub/java/jdk/8u171-b11/jdk-8u171-linux-x64.tar.gz" -O /tmp/jdk8.tar.gz && \
    tar -xzf /tmp/jdk8.tar.gz -C /usr/lib/jvm && \
    rm /tmp/jdk8.tar.gz

# 配置 alternatives 使系统默认使用 Oracle JDK 8
RUN update-alternatives --install /usr/bin/java java /usr/lib/jvm/jdk1.8.0_171/bin/java 1 && \
    update-alternatives --install /usr/bin/javac javac /usr/lib/jvm/jdk1.8.0_171/bin/javac 1

# 设置 JAVA_HOME 环境变量
ENV JAVA_HOME=/usr/lib/jvm/jdk1.8.0_171

# 建立默认 Java 的符号链接，供 R 或其他程序查找
RUN ln -sf $JAVA_HOME /usr/lib/jvm/default-java

# 重新配置 R 的 Java 设置（如果需要使用 rJava）
RUN R CMD javareconf

# 后续你可以继续安装 R 包、配置 rJava 等，比如：
RUN R -q -e "Sys.setenv(JAVA_HOME='$JAVA_HOME'); install.packages(c('rJava', 'coda', 'ggplot2'), repos='http://cran.us.r-project.org', type='source')"

# 测试加载 rJava
RUN R -q -e "library(rJava)"

# 清理 apt 缓存，减小镜像体积
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
ARG INSILICOVA_VERSION=1.1.4

# # Configure R and Java and install the InSilicoVA package.
# # R is looking for default-java for it's configuration so symlink java-8-oracle to default-java
# RUN ln -s /usr/lib/jvm/java-8-oracle/ /usr/lib/jvm/default-java && \
#     R CMD javareconf && \
#     echo "/usr/lib/jvm/java-8-oracle/jre/lib/amd64/server/" > /etc/ld.so.conf.d/rJava.conf && \
#     /sbin/ldconfig && \
#     R -q -e "install.packages(c('rJava', 'coda', 'ggplot2'), repos='http://cran.us.r-project.org')" && \
#     wget https://cran.r-project.org/src/contrib/Archive/InSilicoVA/InSilicoVA_$INSILICOVA_VERSION.tar.gz && \
#     R CMD INSTALL InSilicoVA_$INSILICOVA_VERSION.tar.gz  && \
#     rm InSilicoVA_$INSILICOVA_VERSION.tar.gz && \
#     rm -rf /tmp/downloaded_packages/ /tmp/*.rds

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

# CMD [ "/bin/bash" ]
