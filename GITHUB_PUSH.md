# GitHub 푸시 · Streamlit Cloud 배포 (5분)

커밋은 완료되었습니다. 아래 순서대로 진행하세요.

---

## Step 1 — GitHub 저장소 만들기

1. https://github.com/new 접속
2. Repository name: `AI-Trading-Coach` (원하는 이름)
3. **Public** 선택
4. README / .gitignore **추가하지 않음** (이미 있음)
5. **Create repository**

---

## Step 2 — 코드 푸시

GitHub에서 표시되는 URL로 아래 실행 (PowerShell):

```powershell
cd "C:\Users\User\Desktop\SK신입사원 교육_AI\AI_에이전트\AI-Trading-Coach"

git remote add origin https://github.com/본인아이디/AI-Trading-Coach.git
git branch -M main
git push -u origin main
```

> GitHub 로그인 창이 뜨면 인증합니다.

---

## Step 3 — Streamlit Cloud 배포

1. https://share.streamlit.io/ 접속 → GitHub 연동
2. **Create app**
3. 설정:

| 항목 | 값 |
|------|-----|
| Repository | `본인아이디/AI-Trading-Coach` |
| Branch | `main` |
| Main file | `app.py` |

4. **Advanced settings** → Python **3.11**
5. **Secrets** (⚙️) 클릭 후 입력:

```toml
GEMINI_API_KEY = "본인_Gemini_API_키"
GEMINI_MODEL = "gemini-2.5-flash-lite"
```

6. **Deploy!**

---

## Step 4 — 과제 제출

제출물 예시:

```
GitHub: https://github.com/본인아이디/AI-Trading-Coach
실행 URL: https://xxxx.streamlit.app
사용법: 종목 005930 입력 → 분석 시작
```

---

## 확인

- [ ] `.env` 파일이 GitHub에 **없는지** 확인 (API 키 유출 방지)
- [ ] Streamlit URL에서 005930 분석 성공
- [ ] SUBMISSION.md 첨부 또는 README 링크

---

## 문제 해결

| 문제 | 해결 |
|------|------|
| push 거부 | GitHub 저장소 URL 확인, 로그인 |
| AI 실패 | Streamlit Secrets에 GEMINI_API_KEY |
| 429 오류 | gemini-2.5-flash 모델 사용 |
