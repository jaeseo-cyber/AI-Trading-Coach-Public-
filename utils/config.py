"""Application configuration — .env / Docker / Streamlit Cloud."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def _apply_streamlit_secrets() -> None:
    """Load Streamlit Cloud secrets into environment variables."""
    try:
        import streamlit as st

        for key in (
            "GEMINI_API_KEY",
            "GEMINI_MODEL",
            "NEWS_API_KEY",
            "STREAMLIT_SERVER_ADDRESS",
            "STREAMLIT_SERVER_PORT",
        ):
            if key in st.secrets:
                os.environ[key] = str(st.secrets[key])
    except Exception:
        pass


_apply_streamlit_secrets()

APP_TITLE = "AI 트레이딩 코치"
PAGE_ICON = "📈"
PROJECT_SUBTITLE = "AI 기반 주식 분석 & 트레이딩 코치"

# Google Gemini (무료 티어) — https://aistudio.google.com/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
LLM_MODEL = GEMINI_MODEL
LLM_PROVIDER = "Google Gemini"

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "").strip()
MAX_NEWS_ITEMS = int(os.getenv("MAX_NEWS_ITEMS", "5"))

STREAMLIT_SERVER_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))


def is_llm_configured() -> bool:
    """Return True when Gemini API key is present."""
    return bool(GEMINI_API_KEY)
