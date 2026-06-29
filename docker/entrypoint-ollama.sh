#!/bin/sh
# Ollama 서버 기동 + 모델 자동 pull
set -e

MODEL="${OLLAMA_MODEL:-llama3.2}"

echo "[ollama] 서버 시작 (0.0.0.0:${OLLAMA_PORT:-11434})"
ollama serve &
SERVE_PID=$!

sleep 5

if ! ollama list 2>/dev/null | grep -q "${MODEL%%:*}"; then
  echo "[ollama] 모델 다운로드: ${MODEL}"
  ollama pull "${MODEL}" || echo "[ollama] pull 실패 — 수동으로 ollama pull ${MODEL} 실행 필요" >&2
else
  echo "[ollama] 모델 이미 존재: ${MODEL}"
fi

echo "[ollama] 준비 완료"
wait "$SERVE_PID"
