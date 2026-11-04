FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY frontend/requirements.txt ./requirements.txt

RUN uv pip install --no-cache --system -r requirements.txt

COPY frontend ./frontend

EXPOSE 8501
