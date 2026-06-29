#!/usr/bin/env bash
# AI Trading Coach — macOS/Linux 원클릭 실행
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  cp .env.example .env
  echo ".env 파일을 생성했습니다. GEMINI_API_KEY를 설정한 뒤 다시 실행하세요."
  exit 1
fi

if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi

exec .venv/bin/streamlit run app.py \
  --server.address=0.0.0.0 \
  --server.port=8501 \
  --server.headless=true
