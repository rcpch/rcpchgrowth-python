FROM python:3.12-bookworm

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
