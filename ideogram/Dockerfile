FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# Allow apt-get update to continue even if trixie repository fails
# Use --fix-missing to allow partial installation if some packages fail to download
RUN apt-get update || true && \
    apt-get install -y --no-install-recommends --fix-missing \
        libgif-dev \
        libaec-dev \
        libblosc-dev \
        libzstd-dev \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxrender1 \
        libxext6 \
        build-essential \
        g++ \
        gfortran \
        libblas-dev \
        liblapack-dev \
    || true && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt /app/requirements.txt
COPY config.yml /app/config.yml

# Install Cython first (if needed for compilation)
RUN pip install --no-cache-dir Cython>=0.29.0

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir uvicorn watchdog

# Copy application code last
COPY . /app
