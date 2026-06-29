# AI Trading Coach — Streamlit 앱 이미지
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# curl: Ollama 헬스체크 / wait-for-ollama
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY agents/ ./agents/
COPY coordinator/ ./coordinator/
COPY services/ ./services/
COPY utils/ ./utils/
COPY .streamlit/ ./.streamlit/
COPY docker/ ./docker/

RUN chmod +x /app/docker/entrypoint-app.sh /app/docker/wait-for-ollama.sh \
    && sed -i 's/\r$//' /app/docker/*.sh

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -sf "http://127.0.0.1:8501/_stcore/health" || exit 1

ENTRYPOINT ["/app/docker/entrypoint-app.sh"]
