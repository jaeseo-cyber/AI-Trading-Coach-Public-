@echo off
REM AI Trading Coach — Windows 원클릭 실행
cd /d "%~dp0.."
if not exist .env (
  copy .env.example .env
  echo .env 파일을 생성했습니다. GEMINI_API_KEY를 설정한 뒤 다시 실행하세요.
  notepad .env
  exit /b 1
)
if not exist .venv (
  python -m venv .venv
  call .venv\Scripts\pip install -r requirements.txt
)
call .venv\Scripts\streamlit.exe run app.py --server.address=0.0.0.0 --server.port=8501
pause
