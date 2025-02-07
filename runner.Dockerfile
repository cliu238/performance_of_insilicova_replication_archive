# Use the latest Python image
FROM python:3.13.1

# Set the working directory inside the container
WORKDIR /app

# Copy the source script
COPY ./src/download.py src/download.py

# Copy dependencies if available
COPY ./requirements.txt requirements.txt

# Install dependencies only if `requirements.txt` exists
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Ensure required directories exist before running
RUN mkdir -p /app/data/ghdx

# Set environment variable to avoid Python buffer issues
ENV PYTHONUNBUFFERED=1

# Run the script when the container starts
CMD ["python", "src/map_insilico.py"]
