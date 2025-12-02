FROM python:3.8

WORKDIR /app

# Install system dependencies with explicit runtime dependencies first
# Allow apt-get update to continue even if bookworm-updates repository fails
# Use --fix-missing to allow partial installation if some packages fail to download
# Removed libgif7 (runtime) - libgif-dev is sufficient for compilation
# libsz2 will be installed automatically as dependency of libaec-dev if available
RUN apt-get update || true && \
    apt-get install -y --no-install-recommends --fix-missing \
        libsnappy1v5 \
        libgif-dev \
        libaec-dev \
        libblosc-dev \
        libzstd-dev \
    || true && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements first for better Docker layer caching
COPY requirements.txt /app/requirements.txt
COPY config.yml /app/config.yml

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir uvicorn watchdog

# Copy application code last
COPY . /app
