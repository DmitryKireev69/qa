FROM python:3.13.7-bookworm

LABEL authors="kireev"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /var/qa

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

