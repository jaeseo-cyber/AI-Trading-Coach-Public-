"""User-facing LLM configuration status messages."""

from __future__ import annotations

from utils.config import get_llm_config_error


def render_llm_config_error() -> str:
    """Return a Korean error message for the current LLM config state."""
    code = get_llm_config_error()
    if code is None:
        return ""

    if code == "missing_groq":
        return (
            "**GROQ_API_KEY가 설정되지 않았습니다.**\n\n"
            "1. https://console.groq.com/keys 에서 무료 API 키 발급\n"
            "2. Streamlit Secrets에 추가:\n\n"
            "```toml\n"
            'LLM_PROVIDER = "groq"\n'
            'GROQ_API_KEY = "gsk_..."\n'
            'GROQ_MODEL = "llama-3.1-8b-instant"\n'
            "```"
        )

    if code == "missing":
        return (
            "**AI API 키가 설정되지 않았습니다.**\n\n"
            "**옵션 A — Google Gemini (기본)**\n"
            "```toml\n"
            'GEMINI_API_KEY = "AIzaSy..."\n'
            'GEMINI_MODEL = "gemini-2.5-flash-lite"\n'
            "```\n"
            "발급: https://aistudio.google.com/apikey\n\n"
            "**옵션 B — Groq (Gemini 한도 대안, 권장 백업)**\n"
            "```toml\n"
            'GROQ_API_KEY = "gsk_..."\n'
            'GROQ_MODEL = "llama-3.1-8b-instant"\n'
            "```\n"
            "발급: https://console.groq.com/keys\n\n"
            "**옵션 C — 둘 다 설정 (Gemini 실패 시 Groq 자동 전환)**\n"
            "위 두 키를 모두 Secrets에 넣으면 한도·과부하 시 자동으로 Groq를 사용합니다."
        )

    if code == "placeholder":
        return (
            "**API 키가 예시 문구 그대로입니다.**\n\n"
            "placeholder가 아닌 실제 발급 키를 입력해 주세요."
        )

    if code == "non_ascii":
        return "**API 키에 한글이 포함되어 있습니다.** 영문 키만 입력하세요."

    if code == "invalid_format":
        return "**API 키 형식이 올바르지 않습니다.** 공백 없이 한 줄로 입력하세요."

    return f"**AI API 설정 오류** ({code}) — Secrets 확인 후 Reboot 해 주세요."
