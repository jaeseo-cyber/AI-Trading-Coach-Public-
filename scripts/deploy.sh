#!/bin/bash
# EC2/VPS에서 앱 최초 배포 (프로젝트 루트에서 실행)
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  cp .env.example .env
  echo ".env 파일을 생성했습니다. 필요 시 NEWS_API_KEY 등을 수정하세요."
fi

echo "Docker 이미지 빌드 및 기동..."
docker compose pull ollama 2>/dev/null || true
docker compose build --no-cache app
docker compose up -d

echo ""
echo "모델 다운로드 중 (최초 1회, 수 분 소요)..."
docker compose logs -f ollama &
LOG_PID=$!
sleep 30
kill $LOG_PID 2>/dev/null || true

echo ""
echo "상태 확인:"
docker compose ps
echo ""
echo "접속 URL:"
PUBLIC_IP=$(curl -sf http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || hostname -I | awk '{print $1}')
echo "  Streamlit: http://${PUBLIC_IP}:8501"
echo "  (nginx production) http://${PUBLIC_IP}/  →  make prod"
