FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/ml_service

COPY requirements.txt ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git curl \
    && pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY . .

ENV MODEL_DIR=./data/checkpoints
ENV OUTPUT_DIR=./data/outputs

CMD ["python", "-m", "app.train"]
