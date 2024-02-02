FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip

COPY requirements/development-requirements.txt .

RUN pip install -r development-requirements.txt

COPY . .
