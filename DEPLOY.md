# 배포 가이드 — Streamlit Cloud / Docker / EC2

AI Trading Coach는 **Google Gemini API**를 사용합니다. **Ollama는 필요 없습니다.**

> 과제·공개 URL: **[SUBMISSION.md](./SUBMISSION.md)** (Streamlit Cloud 권장)

---

## 권장 아키텍처 (과제·공개 서비스)

```
[모든 사용자 브라우저] → https://your-app.streamlit.app
                              ↓
                    [Streamlit Cloud 앱]
                              ↓
                    [Google Gemini API (무료 티어)]
```

| 구성요소 | 역할 |
|---------|------|
| **Streamlit Cloud** | 웹 UI 호스팅 (무료) |
| **Gemini API** | AI 분석 (`GEMINI_API_KEY`) |

---

## 서버 Docker 아키텍처 (EC2/VPS)

```
[사용자] → :8501 또는 nginx :80 → [Streamlit] → [Gemini API]
```

---

## (레거시) Ollama 기반 아키텍처

<details>
<summary>이전 Ollama 버전 (현재 프로젝트는 Gemini 사용)</summary>

```
[사용자] → Streamlit → Ollama :11434 (서버 내부)
```

</details>

---

## 이전 문서 (Ollama Docker — 참고용)

<details>
<summary>Ollama + Docker 상세 (구버전)</summary>

# 배포 가이드 — AWS EC2 / VPS (Docker)

AI Trading Coach를 **외부에서 접속 가능한 production 환경**으로 배포하는 방법입니다.

---

## 최종 아키텍처

```
                    ┌─────────────────────────────────────────┐
  인터넷 사용자      │  EC2 / VPS (Ubuntu 22.04+)              │
       │            │                                         │
       ▼            │  ┌─────────┐      ┌──────────────────┐  │
  :80 (권장)  ─────►│  │  nginx  │─────►│  Streamlit :8501 │  │
  또는 :8501        │  │  :80    │      │  (app 컨테이너)   │  │
                    │  └─────────┘      └────────┬─────────┘  │
                    │       production 프로필      │ HTTP       │
                    │                              ▼            │
                    │                    ┌──────────────────┐  │
                    │                    │  Ollama  :11434  │  │
                    │                    │  (ollama 컨테이너)│  │
                    │                    │  llama3.2        │  │
                    │                    └──────────────────┘  │
                    │                         ▲                 │
                    │                    Docker 내부망 only       │
                    │              (11434 외부 노출 ❌ 권장)       │
                    └─────────────────────────────────────────┘
```

| 구성요소 | 포트 | 외부 노출 | 역할 |
|---------|------|----------|------|
| **nginx** | 80 | ✅ (권장) | Reverse proxy, WebSocket |
| **Streamlit** | 8501 | ✅ (또는 nginx 뒤) | 웹 UI |
| **Ollama** | 11434 | ❌ (내부만) | LLM API |

---

## 전체 폴더 구조

```
AI-Trading-Coach/
├── app.py                      # Streamlit 진입점
├── Dockerfile                  # 앱 이미지
├── docker-compose.yml          # ollama + app + nginx(production)
├── Makefile                    # make up / make prod
├── .env.example                # 환경변수 템플릿
├── DEPLOY.md                   # 이 문서
├── docker/
│   ├── entrypoint-app.sh       # Ollama 대기 → Streamlit 0.0.0.0
│   ├── entrypoint-ollama.sh    # ollama serve + 모델 pull
│   └── wait-for-ollama.sh      # Ollama 헬스 대기
├── nginx/
│   └── conf.d/app.conf         # Streamlit reverse proxy
├── scripts/
│   ├── install-docker-ubuntu.sh
│   ├── deploy.sh
│   └── verify_korean.py
├── agents/                     # Multi-Agent
├── coordinator/
├── services/
└── utils/
    └── config.py               # OLLAMA_HOST, STREAMLIT_* env
```

---

## 사전 요구 사항

| 항목 | 권장 |
|------|------|
| OS | Ubuntu 22.04 / 24.04 LTS |
| RAM | **8GB 이상** (llama3.2 + Streamlit) |
| CPU | 2 vCPU 이상 |
| 디스크 | 20GB+ (모델 ~2GB) |
| 소프트웨어 | Docker 24+, Docker Compose v2 |

**AWS EC2 인스턴스 예:** `t3.large` (2 vCPU, 8GB) 또는 `t3.xlarge`

---

## 1. 로컬 Docker 실행

### 준비

```bash
cp .env.example .env
```

### 기본 실행 (app + ollama)

```bash
docker compose up -d
# 또는
make up
```

- Streamlit: http://localhost:8501
- Ollama: http://127.0.0.1:11434 (호스트 로컬만)

### nginx 포함 (production 프로필)

```bash
docker compose --profile production up -d
# 또는
make prod
```

- http://localhost (포트 80)

### 로그 / 상태

```bash
docker compose logs -f app
docker compose ps
make health
```

### 중지

```bash
docker compose down
# 볼륨까지 삭제: make clean
```

> **최초 기동:** Ollama가 `llama3.2` 모델을 pull 하므로 **5~15분** 걸릴 수 있습니다.

---

## 2. AWS EC2 배포 (단계별)

### Step 1 — EC2 인스턴스 생성

1. AWS Console → **EC2** → **Launch instance**
2. 설정:

| 항목 | 값 |
|------|-----|
| AMI | Ubuntu Server 22.04 LTS |
| Instance type | `t3.large` 이상 |
| Key pair | 새로 생성 또는 기존 PEM |
| Storage | 30GB gp3 |

3. **Create security group** (아래 Step 2 참고)
4. **Launch**

### Step 2 — 보안 그룹 (Security Group)

| Type | Port | Source | 용도 |
|------|------|--------|------|
| SSH | 22 | 내 IP | 서버 접속 |
| HTTP | 80 | 0.0.0.0/0 | nginx (production) |
| Custom TCP | 8501 | 0.0.0.0/0 | Streamlit 직접 접속 (nginx 미사용 시) |
| ~~Custom TCP~~ | ~~11434~~ | — | **열지 마세요** (Ollama는 Docker 내부만) |

> 운영 권장: **80만 열고** `make prod`로 nginx 사용. 8501은 제한하거나 닫기.

### Step 3 — SSH 접속

```bash
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>
```

### Step 4 — Docker 설치

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/...)" 
# 또는 저장소 clone 후:
git clone <your-repo-url> AI-Trading-Coach
cd AI-Trading-Coach
sudo bash scripts/install-docker-ubuntu.sh
```

재로그인:

```bash
exit
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>
```

### Step 5 — 앱 배포

```bash
cd AI-Trading-Coach
cp .env.example .env
# 선택: nano .env  (NEWS_API_KEY 등)

bash scripts/deploy.sh
# 또는
docker compose up -d --build
```

### Step 6 — production (nginx)

```bash
make prod
```

### Step 7 — 접속 확인

브라우저에서:

- nginx 사용: `http://<EC2_PUBLIC_IP>`
- Streamlit 직접: `http://<EC2_PUBLIC_IP>:8501`

헬스체크 (서버 내부):

```bash
curl http://localhost:8501/_stcore/health
curl http://localhost/
```

### Step 8 — Elastic IP (선택, 권장)

EC2 → **Elastic IPs** → 할당 → 인스턴스에 연결  
재부팅 후에도 IP가 유지됩니다.

### Step 9 — HTTPS (선택)

1. 도메인을 EC2 Elastic IP에 A 레코드 연결
2. Certbot + nginx SSL 설정 (Let's Encrypt)
3. 보안 그룹에 **443** 추가

---

## 3. 일반 VPS 배포 (DigitalOcean, Linode, Naver Cloud 등)

EC2와 동일한 절차입니다.

```bash
# 1. Ubuntu VPS 생성 (8GB RAM)
# 2. SSH 접속
ssh root@<VPS_IP>

# 3. Docker 설치
apt update && apt install -y git
git clone <your-repo-url> AI-Trading-Coach
cd AI-Trading-Coach
bash scripts/install-docker-ubuntu.sh

# 4. 재로그인 후
cp .env.example .env
docker compose up -d --build

# 5. 방화벽 (ufw)
ufw allow 22
ufw allow 80
ufw allow 8501   # nginx 미사용 시
ufw enable
```

VPS 제공업체 **방화벽/Security**에서도 80, 8501을 허용하세요.

---

## 4. 환경 변수 (.env)

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `OLLAMA_MODEL` | `llama3.2` | 사용할 모델 |
| `OLLAMA_HOST` | (Docker: 자동) | `http://ollama:11434` |
| `STREAMLIT_SERVER_ADDRESS` | `0.0.0.0` | 외부 접속 바인딩 |
| `STREAMLIT_SERVER_PORT` | `8501` | 컨테이너 내부 포트 |
| `STREAMLIT_HOST_PORT` | `8501` | 호스트 매핑 포트 |
| `OLLAMA_HOST_PORT` | `11434` | localhost만 바인딩 |
| `NGINX_HTTP_PORT` | `80` | nginx HTTP |
| `NEWS_API_KEY` | (비움) | NewsAPI (선택) |

---

## 5. 운영 명령

```bash
# 재시작
docker compose restart app

# 로그
docker compose logs -f app ollama

# 모델 수동 pull
docker exec ai-trading-ollama ollama pull llama3.2

# 업데이트 배포
git pull
docker compose build app
docker compose up -d

# 디스크 확인 (모델 볼륨)
docker volume inspect ai-trading-ollama-data
```

---

## 6. 문제 해결

| 증상 | 해결 |
|------|------|
| 8501 접속 불가 | 보안 그룹 8501 허용, `docker compose ps` 확인 |
| AI 분석 실패 | `docker compose logs ollama` — 모델 pull 완료 여부 |
| Ollama 타임아웃 | RAM 8GB 미만이면 인스턴스 업그레이드 |
| nginx 502 | app 헬스 대기: `docker compose logs app` |
| 모델 재다운로드 | `docker volume rm ai-trading-ollama-data` 후 재기동 |

---

## 7. 보안 체크리스트

- [ ] Ollama 포트(11434) **외부 미노출**
- [ ] SSH(22)는 **내 IP만** 허용
- [ ] `.env` Git 커밋 금지
- [ ] production은 **nginx(80)** + HTTPS 권장
- [ ] 정기 `docker compose pull` / `git pull` 업데이트

---

## 8. Streamlit Cloud vs 자체 호스팅

| | Streamlit Cloud | EC2/VPS Docker |
|--|-----------------|----------------|
| Ollama | 별도 공개 URL 필요 | 같은 서버 Docker 내부 |
| 비용 | Cloud 무료 + Ollama 서버 | EC2 월 과금 |
| 제어 | 제한적 | 전체 제어 |
| 권장 | 데모 | **production / 팀 내부 서비스** |

자체 호스팅(Docker)이 Ollama와 Streamlit을 한 서버에서 안정적으로 운영하기에 적합합니다.

</details>
