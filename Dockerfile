# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install basic system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    if [ -f /app/requirements.txt ]; then pip install --no-cache-dir -r /app/requirements.txt; fi

# Copy the rest of the repository
COPY . /app

# Expose a working directory for evaluation outputs
VOLUME ["/app/eval/results"]

# Default command: show help for evaluation script
CMD ["bash", "-lc", "python -m eval.run_eval --help"]
