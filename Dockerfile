FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/models/cache

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    "onnx-asr[cpu,hub]==0.12.0" \
    fastapi \
    "uvicorn[standard]" \
    python-multipart

WORKDIR /app

COPY server.py /app/server.py

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]