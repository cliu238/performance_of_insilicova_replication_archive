FROM rpy2/base-ubuntu:vRELEASE_3_5_6-22.04

# Install required system libraries including Java
RUN apt-get update && \
    apt-get install -y \
    python3 python3-pip python3-venv python3-setuptools \
    libpcre2-dev liblzma-dev libbz2-dev libicu-dev libffi-dev \
    libcurl4-openssl-dev default-jdk libxml2-dev \
    libgsl-dev libjpeg-dev libtiff-dev libpng-dev libssl-dev \
    openjdk-11-jdk && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set Java environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"
ENV R_USER=/root

# Debug: Verify Java version
RUN java -version && R -e "system('java -version')"

# Install rJava with correct Java settings
RUN R -e "Sys.setenv(JAVA_HOME='/usr/lib/jvm/java-11-openjdk-amd64'); install.packages('rJava', repos='https://cloud.r-project.org')"

# Install InSilicoVA
RUN R -e "install.packages('InSilicoVA', repos='https://cloud.r-project.org')"

# Set the working directory
WORKDIR /app

# Copy your source code and dependencies
COPY ./src/download.py src/download.py
COPY ./requirements.txt requirements.txt

# Install Python dependencies
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Create data directories
RUN mkdir -p /app/data/ghdx

# Set default command
CMD ["/bin/bash"]