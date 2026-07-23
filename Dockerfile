# Multi-stage Dockerfile for TLF-Research
# Stage 1: build wheels in a builder image
FROM python:3.10-slim AS builder
ENV PYTHONUNBUFFERED=1

# Install build-time deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and build wheels to leverage Docker cache
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    if [ -f /app/requirements.txt ]; then pip wheel --wheel-dir /wheels -r /app/requirements.txt; fi

# Stage 2: runtime image
FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1

# Minimal runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Create a non-root user for running the app
RUN useradd -m -s /bin/bash tlfuser || true

WORKDIR /app

# Copy wheels from builder and install them (if wheels exist)
COPY --from=builder /wheels /wheels
RUN if [ -d /wheels ]; then pip install --no-cache-dir /wheels/*; fi

# Copy repository content
COPY . /app

# Ensure non-root user owns the app directory
RUN chown -R tlfuser:tlfuser /app || true

# Switch to non-root user
USER tlfuser

# Expose a working directory for evaluation outputs
VOLUME ["/app/eval/results"]

# Default command: show help for evaluation script
CMD ["bash", "-lc", "python -m eval.run_eval --help"]
