FROM python:3.11-slim 

COPY requirements.txt /app/requirements.txt
COPY config.yml /app/config.yml

COPY . /app

WORKDIR /app

RUN apt-get update && pip install --upgrade pip && apt-get install -y --no-install-recommends \
    libgif-dev \
    libaec-dev \
    libblosc-dev \
    libzstd-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt && pip install uvicorn

RUN pip install watchdog
