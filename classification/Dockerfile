FROM python:3.8

COPY requirements.txt /app/requirements.txt
COPY config.yml /app/config.yml

COPY . /app

WORKDIR /app

RUN apt-get update && pip install --upgrade pip && apt-get install -y \
    libgif-dev \
    libaec-dev \
    libblosc-dev \
    libzstd-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt && pip install uvicorn

RUN pip install watchdog
