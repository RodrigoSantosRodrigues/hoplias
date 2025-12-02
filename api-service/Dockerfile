FROM python:3.11-slim

WORKDIR /app

# Install system dependencies with error handling
RUN apt-get update || true && \
    apt-get install -y --no-install-recommends --fix-missing \
        gcc \
        make \
        python3-dev \
        libffi-dev \
    || true && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir uvicorn watchdog

# Copy application code last
COPY . /app
