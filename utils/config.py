"""Application configuration — .env / Docker / Streamlit Cloud."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


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
                os.environ[key] = str(st.secrets[key]).strip()
    except Exception:
        pass


def get_gemini_api_key() -> str:
    """Return Gemini API key, refreshing Streamlit secrets when available."""
    _apply_streamlit_secrets()
    return os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")


def get_gemini_model() -> str:
    """Return Gemini model id (ASCII only)."""
    _apply_streamlit_secrets()
    model = os.getenv("GEMINI_MODEL", _DEFAULT_GEMINI_MODEL).strip()
    if not model or not model.isascii():
        return _DEFAULT_GEMINI_MODEL
    return model


def validate_gemini_api_key(key: str) -> None:
    """
    Validate API key before HTTP request.

    Non-ASCII keys (e.g. Korean placeholder text in Secrets) crash httpx headers.
    """
    cleaned = key.strip().strip('"').strip("'")
    if not cleaned:
        raise ValueError("missing")

    if not cleaned.isascii():
        raise ValueError("non_ascii")

    if any(ch.isspace() for ch in cleaned) or len(cleaned) < 10:
        raise ValueError("invalid_format")


_apply_streamlit_secrets()

APP_TITLE = "AI 트레이딩 코치"
PAGE_ICON = "📈"
PROJECT_SUBTITLE = "AI 기반 주식 분석 & 트레이딩 코치"

GEMINI_API_KEY = get_gemini_api_key()
GEMINI_MODEL = get_gemini_model()
LLM_MODEL = GEMINI_MODEL
LLM_PROVIDER = "Google Gemini"

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "").strip()
MAX_NEWS_ITEMS = int(os.getenv("MAX_NEWS_ITEMS", "5"))

STREAMLIT_SERVER_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))


def is_llm_configured() -> bool:
    """Return True when a plausible Gemini API key is present."""
    key = get_gemini_api_key()
    if not key:
        return False
    try:
        validate_gemini_api_key(key)
    except ValueError:
        return False
    return True
