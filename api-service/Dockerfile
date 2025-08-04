FROM python:3.9

COPY requirements.txt /app/requirements.txt

COPY . /app

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential python3-dev libffi-dev

RUN pip install --upgrade setuptools importlib-metadata pip

RUN pip install --upgrade pip setuptools wheel

RUN pip install -r requirements.txt uvicorn watchdog
