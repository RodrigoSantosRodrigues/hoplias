FROM python:3.7

COPY requirements.txt /app/requirements.txt

COPY . /app

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libaec-dev \
    libblosc-dev \
    libzstd-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

RUN pip install watchdog
