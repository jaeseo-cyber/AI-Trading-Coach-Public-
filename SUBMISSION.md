# 과제 제출 · 공개 배포 가이드

교수님·동료·다른 PC 사용자가 **동일하게 실행**할 수 있도록 정리한 문서입니다.

---

## 제출물 체크리스트

| 항목 | 내용 |
|------|------|
| GitHub 저장소 URL | 소스 코드 |
| **공개 앱 URL** (권장) | Streamlit Cloud 배포 주소 |
| README.md | 설치·실행 방법 |
| `.env.example` | 환경 변수 템플릿 (API 키는 **커밋 금지**) |
| `requirements.txt` | Python 의존성 |

---

## 방법 1 — Streamlit Cloud (권장: 누구나 URL로 접속)

**제출자(본인)가 1회 배포** → 심사자·동료는 **브라우저만** 있으면 사용 가능.

### 배포 단계

1. GitHub에 프로젝트 푸시 (`.env`는 올리지 않음)
2. [share.streamlit.io](https://share.streamlit.io/) → **New app**
3. 설정: Main file = `app.py`, Python **3.11**
4. **Secrets** 입력:

```toml
GEMINI_API_KEY = "본인_발급_키"
GEMINI_MODEL = "gemini-2.5-flash"
# NEWS_API_KEY = "선택"
```

5. **Deploy** → 생성된 URL 예: `https://your-app.streamlit.app`

### API 키 발급 (무료)

https://aistudio.google.com/apikey

### 제출 예시 문구

> 공개 URL: https://xxxx.streamlit.app  
> 종목 코드(예: 005930) 입력 후 「분석 시작」 클릭

---

## 방법 2 — 로컬 실행 (Windows / Mac / Linux)

다른 사용자가 **자신의 PC**에서 실행할 때:

```bash
git clone <저장소URL>
cd AI-Trading-Coach
cp .env.example .env    # Windows: copy .env.example .env
```

`.env` 편집:

```env
GEMINI_API_KEY=본인_발급_키
GEMINI_MODEL=gemini-2.5-flash
```

실행:

```bash
# Windows
scripts\run.bat

# Mac / Linux
chmod +x scripts/run.sh
./scripts/run.sh
```

또는:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

→ http://localhost:8501

---

## 방법 3 — Docker (서버 / EC2 / VPS)

```bash
cp .env.example .env
# .env에 GEMINI_API_KEY 설정
docker compose up -d --build
```

→ http://서버IP:8501

nginx 포함:

```bash
docker compose --profile production up -d --build
```

→ http://서버IP

---

## 환경별 요구 사항

| 환경 | Python | API 키 | Ollama |
|------|--------|--------|--------|
| Streamlit Cloud | (호스팅) | Secrets에 설정 | **불필요** |
| 로컬 | 3.11+ | `.env` | **불필요** |
| Docker | (이미지 내장) | `.env` | **불필요** |

---

## 사용 방법 (공통)

1. 사이드바: 시장 · 분석 유형 · 투자 성향 선택
2. 종목 코드 입력 (한국: `005930`, 미국: `AAPL`)
3. **분석 시작** 클릭 (1~2분 소요)
4. 차트 · 기술 지표 · 뉴스 · AI 코치 리포트 확인

---

## 문제 해결

| 증상 | 해결 |
|------|------|
| AI 분석 실패 | `GEMINI_API_KEY` 확인, 모델을 `gemini-2.5-flash`로 변경 |
| 429 할당량 초과 | 잠시 후 재시도 또는 Google AI Studio 할당량 확인 |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| Cloud에서만 실패 | Secrets에 `GEMINI_API_KEY` 재확인 |

---

## 면책

본 앱은 투자 **권유가 아닌** 학습·정보 제공 목적입니다.
