# AI 트레이딩 코치 (AI Trading Coach)

Multi-Agent 기반 주식 분석 Streamlit 웹 앱입니다.  
**Google Gemini API(무료 티어)** 를 사용하며, **Ollama 설치 없이** Windows / Mac / Linux / Streamlit Cloud / Docker 어디서든 실행할 수 있습니다.

> **과제 제출용 가이드:** [SUBMISSION.md](./SUBMISSION.md)  
> **서버 배포 상세:** [DEPLOY.md](./DEPLOY.md)

---

## 주요 기능

- **시장 데이터**: 현재가, 시가총액, PER/PBR/EPS, 52주 고저
- **주가 차트**: 1년 종가 · MA20/60 · 거래량 (Plotly)
- **기술적 분석**: RSI, MACD, 볼린저 밴드, 이동평균선
- **최신 뉴스**: Yahoo Finance · Google News RSS (NewsAPI 선택)
- **AI 투자 코치**: Gemini 기반 종합 코칭 리포트 (**100% 한국어**)

---

## 빠른 시작 (로컬)

### 1. 사전 요구

- Python **3.11+**
- [Gemini API 키 (무료)](https://aistudio.google.com/apikey)

### 2. 설치 및 실행

```bash
git clone <your-repository-url>
cd AI-Trading-Coach
cp .env.example .env          # Windows: copy .env.example .env
```

`.env` 파일:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

```bash
pip install -r requirements.txt
streamlit run app.py
```

**Windows 원클릭:** `scripts\run.bat`  
**Mac/Linux:** `chmod +x scripts/run.sh && ./scripts/run.sh`

→ http://localhost:8501

---

## 공개 URL 배포 (모든 사용자 접속 — 과제 제출 권장)

### Streamlit Cloud (무료)

1. GitHub에 코드 푸시 (`.env` **커밋 금지**)
2. [share.streamlit.io](https://share.streamlit.io/) → New app → `app.py`
3. **Secrets:**

```toml
GEMINI_API_KEY = "your_api_key"
GEMINI_MODEL = "gemini-2.5-flash"
```

4. Deploy → `https://your-app.streamlit.app` URL을 과제에 제출

---

## Docker 실행

```bash
cp .env.example .env
# GEMINI_API_KEY 설정
docker compose up -d --build
```

→ http://localhost:8501 (또는 서버 IP)

---

## 환경 변수

| 변수 | 필수 | 설명 |
|------|------|------|
| `GEMINI_API_KEY` | **필수** | Google AI Studio API 키 |
| `GEMINI_MODEL` | 권장 | 기본 `gemini-2.5-flash` |
| `NEWS_API_KEY` | 선택 | NewsAPI 키 |

---

## 사용 방법

1. 사이드바에서 **시장**, **분석 유형**, **투자 성향** 선택
2. 종목 코드 입력 (예: `005930`, `AAPL`)
3. **분석 시작** 클릭
4. 대시보드에서 차트 · 지표 · 뉴스 · AI 코치 확인

---

## 프로젝트 구조

```
AI-Trading-Coach/
├── app.py                    # Streamlit 진입점
├── requirements.txt
├── docker-compose.yml        # Gemini + Streamlit (+ nginx)
├── SUBMISSION.md             # 과제 제출 가이드
├── scripts/run.bat | run.sh  # 원클릭 실행
├── agents/                   # Multi-Agent
├── coordinator/
├── services/ollama_client.py # Gemini API 클라이언트
└── utils/
```

---

## 문제 해결

| 증상 | 해결 |
|------|------|
| AI 분석 실패 | `.env` 또는 Cloud Secrets에 `GEMINI_API_KEY` 설정 |
| 429 할당량 | `gemini-2.5-flash` 사용, 잠시 후 재시도 |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |

---

## 면책

본 앱은 **투자 자문이 아닌** 정보 제공·학습 목적의 도구입니다.
