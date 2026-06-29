"""Application configuration — .env / Docker / Streamlit Cloud."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-lite"
# 429/503 시 자동 폴백 (부하가 적은 lite 모델 우선)
_GEMINI_MODEL_FALLBACKS: tuple[str, ...] = (
    "gemini-2.5-flash-lite",
    "gemini-1.5-flash-8b",
    "gemini-2.0-flash",
    "gemini-2.5-flash",
)
_PLACEHOLDER_KEYS = frozenset(
    {
        "your_gemini_api_key",
        "your_api_key",
        "your_api_key_here",
        "본인_gemini_api_키",
        "본인_발급_키",
        "paste_your_key_here",
    }
)


def _clean_secret(value: object) -> str:
    return str(value).strip().strip('"').strip("'")


def _read_streamlit_secret(key: str) -> str | None:
    """Read a secret from st.secrets (flat key or nested TOML section)."""
    try:
        import streamlit as st

        if key in st.secrets:
            cleaned = _clean_secret(st.secrets[key])
            if cleaned:
                return cleaned

        for section in st.secrets:
            try:
                block = st.secrets[section]
                if key in block:
                    cleaned = _clean_secret(block[key])
                    if cleaned:
                        return cleaned
            except Exception:
                continue
    except Exception:
        pass
    return None


def _apply_streamlit_secrets() -> None:
    """Copy Streamlit Cloud secrets into os.environ (when runtime is active)."""
    for key in (
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_MODEL",
        "NEWS_API_KEY",
        "STREAMLIT_SERVER_ADDRESS",
        "STREAMLIT_SERVER_PORT",
    ):
        value = _read_streamlit_secret(key)
        if value:
            os.environ[key] = value


def bootstrap_secrets() -> None:
    """Call from app.main() after st.set_page_config — secrets need active runtime."""
    _apply_streamlit_secrets()
    key = get_gemini_api_key()
    if key:
        os.environ["GEMINI_API_KEY"] = key
    model = get_gemini_model()
    if model:
        os.environ["GEMINI_MODEL"] = model


def get_gemini_api_key() -> str:
    """Return Gemini API key (.env → Streamlit Secrets, refreshed each call)."""
    for env_key in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        env_val = os.getenv(env_key, "").strip()
        if env_val:
            return _clean_secret(env_val)

    for secret_key in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        secret_val = _read_streamlit_secret(secret_key)
        if secret_val:
            os.environ["GEMINI_API_KEY"] = secret_val
            return secret_val

    return ""


def get_gemini_model() -> str:
    """Return Gemini model id (ASCII only)."""
    model = os.getenv("GEMINI_MODEL", "").strip()
    if not model:
        model = _read_streamlit_secret("GEMINI_MODEL") or ""
    if not model or not model.isascii():
        return _DEFAULT_GEMINI_MODEL
    return model


def get_gemini_model_candidates(preferred: str | None = None) -> tuple[str, ...]:
    """Ordered model list for primary call + 429 quota fallback."""
    primary = (preferred or get_gemini_model()).strip()
    if not primary.isascii():
        primary = _DEFAULT_GEMINI_MODEL

    seen: set[str] = set()
    ordered: list[str] = []
    for name in (primary, *_GEMINI_MODEL_FALLBACKS):
        if name not in seen:
            seen.add(name)
            ordered.append(name)
    return tuple(ordered)


def validate_gemini_api_key(key: str) -> None:
    """
    Validate API key before HTTP request.

    Non-ASCII keys (e.g. Korean placeholder text in Secrets) crash httpx headers.
    """
    cleaned = _clean_secret(key)
    if not cleaned:
        raise ValueError("missing")

    if cleaned.lower() in _PLACEHOLDER_KEYS:
        raise ValueError("placeholder")

    if not cleaned.isascii():
        raise ValueError("non_ascii")

    if any(ch.isspace() for ch in cleaned) or len(cleaned) < 10:
        raise ValueError("invalid_format")


def get_llm_config_error() -> str | None:
    """Return error code when LLM is not ready, else None."""
    key = get_gemini_api_key()
    if not key:
        return "missing"
    try:
        validate_gemini_api_key(key)
    except ValueError as exc:
        return str(exc.args[0]) if exc.args else "invalid"
    return None


APP_TITLE = "AI 트레이딩 코치"
PAGE_ICON = "📈"
PROJECT_SUBTITLE = "AI 기반 주식 분석 & 트레이딩 코치"

GEMINI_API_KEY = ""
GEMINI_MODEL = _DEFAULT_GEMINI_MODEL
LLM_MODEL = GEMINI_MODEL
LLM_PROVIDER = "Google Gemini"

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "").strip()
MAX_NEWS_ITEMS = int(os.getenv("MAX_NEWS_ITEMS", "5"))

STREAMLIT_SERVER_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))


def is_llm_configured() -> bool:
    """Return True when a plausible Gemini API key is present."""
    return get_llm_config_error() is None
