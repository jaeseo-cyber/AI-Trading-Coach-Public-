#!/bin/sh
# Streamlit 앱 기동 (Gemini API — Ollama 불필요)
set -e

export STREAMLIT_SERVER_ADDRESS="${STREAMLIT_SERVER_ADDRESS:-0.0.0.0}"
export STREAMLIT_SERVER_PORT="${STREAMLIT_SERVER_PORT:-8501}"

if [ -z "$GEMINI_API_KEY" ]; then
  echo "[app] 경고: GEMINI_API_KEY가 없습니다. AI 분석이 동작하지 않습니다." >&2
fi

echo "[app] Streamlit 시작 — ${STREAMLIT_SERVER_ADDRESS}:${STREAMLIT_SERVER_PORT}"
echo "[app] LLM: Google Gemini (${GEMINI_MODEL:-gemini-2.0-flash})"

exec streamlit run app.py \
  --server.address="${STREAMLIT_SERVER_ADDRESS}" \
  --server.port="${STREAMLIT_SERVER_PORT}" \
  --server.headless=true \
  --browser.gatherUsageStats=false
