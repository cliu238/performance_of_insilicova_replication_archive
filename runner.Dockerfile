# Use the Rocker R base image
FROM rocker/r-ver:4.3.1

# Install Python, R dependencies, and system libraries
RUN apt-get update && \
    apt-get install -y \
    python3 python3-pip python3-venv python3-setuptools \
    libpcre2-dev liblzma-dev libbz2-dev libicu-dev libffi-dev \
    libcurl4-openssl-dev default-jdk \
    r-base r-base-dev libxml2-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Ensure setuptools, pip, and wheel are up-to-date
RUN pip install --upgrade pip setuptools wheel

# Install rpy2 and set up R library paths
RUN pip install rpy2

# Set environment variables for R
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV R_HOME=/usr/lib/R
ENV R_USER=/root
ENV LD_LIBRARY_PATH=/usr/lib/R/lib/:$LD_LIBRARY_PATH
RUN R -e "install.packages('rlang', repos='https://cloud.r-project.org', type='source')"
RUN R -e "install.packages('rJava', repos='https://cloud.r-project.org')"
# Install the R package InSilicoVA and dependencies
RUN R -e "install.packages(c('InSilicoVA', 'methods', 'utils', 'grDevices', 'graphics', 'stats'), repos='http://cran.r-project.org')"

# Set the working directory
WORKDIR /app

# Copy your source code and dependency files
COPY ./src/download.py src/download.py
COPY ./requirements.txt requirements.txt

# Install Python dependencies if the requirements file exists
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Create data directories
RUN mkdir -p /app/data/ghdx

# Set the default command (uncomment and adjust as needed)
# CMD ["pytest", "test/test_insilico.py"]
CMD ["/bin/bash"]