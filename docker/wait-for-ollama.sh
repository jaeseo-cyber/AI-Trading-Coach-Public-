#!/bin/sh
# Ollama API가 준비될 때까지 대기
set -e

OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"
MAX_WAIT="${OLLAMA_WAIT_SECONDS:-180}"
INTERVAL=5
elapsed=0

echo "[wait-for-ollama] 대상: ${OLLAMA_HOST} (최대 ${MAX_WAIT}초)"

while [ "$elapsed" -lt "$MAX_WAIT" ]; do
  if curl -sf "${OLLAMA_HOST}/" >/dev/null 2>&1; then
    echo "[wait-for-ollama] Ollama 준비 완료"
    exit 0
  fi
  echo "[wait-for-ollama] 대기 중... (${elapsed}s)"
  sleep "$INTERVAL"
  elapsed=$((elapsed + INTERVAL))
done

echo "[wait-for-ollama] 타임아웃 — Ollama에 연결할 수 없습니다." >&2
exit 1
