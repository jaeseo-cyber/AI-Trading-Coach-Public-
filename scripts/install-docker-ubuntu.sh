#!/bin/bash
# Ubuntu 22.04/24.04 EC2·VPS — Docker + Compose 설치
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "sudo로 실행하세요: sudo bash scripts/install-docker-ubuntu.sh"
  exit 1
fi

apt-get update
apt-get install -y ca-certificates curl gnupg

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

systemctl enable docker
systemctl start docker

# ubuntu 사용자(또는 ec2-user)를 docker 그룹에 추가
DEPLOY_USER="${SUDO_USER:-ubuntu}"
usermod -aG docker "$DEPLOY_USER" || true

echo ""
echo "Docker 설치 완료. 재로그인 후 docker compose 사용 가능."
echo "  docker --version"
echo "  docker compose version"
