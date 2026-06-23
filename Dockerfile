FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY recruitiq/ ./recruitiq/
COPY scripts/ ./scripts/
COPY configs/ ./configs/
COPY validate_submission.py .

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "scripts/rank.py"]
CMD ["--candidates", "/data/raw/candidates.jsonl", "--out", "/data/outputs/submission.csv"]
