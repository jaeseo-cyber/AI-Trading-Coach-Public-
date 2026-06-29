"""Google Gemini API client (Ollama 대체)."""

from __future__ import annotations

from google import genai
from google.genai import types

from utils.config import GEMINI_API_KEY, GEMINI_MODEL
from utils.korean_rules import merge_korean_system_prompt


class LLMClientError(Exception):
    """Raised when an LLM API call fails."""


OllamaClientError = LLMClientError


def _get_client() -> genai.Client:
    if not GEMINI_API_KEY:
        raise LLMClientError(
            "GEMINI_API_KEY가 설정되지 않았습니다.\n"
            "1) https://aistudio.google.com/apikey 에서 무료 API 키 발급\n"
            "2) .env 파일에 GEMINI_API_KEY=your_key 추가"
        )
    return genai.Client(api_key=GEMINI_API_KEY)


def ask_gpt(
    question: str,
    *,
    system_prompt: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
    korean_only: bool = True,
) -> str:
    """Send a question to Google Gemini and return the assistant response."""
    effective_system = (
        merge_korean_system_prompt(system_prompt)
        if korean_only
        else system_prompt
    )

    config_kwargs: dict = {}
    if effective_system:
        config_kwargs["system_instruction"] = effective_system
    if temperature is not None:
        config_kwargs["temperature"] = temperature

    config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=model or GEMINI_MODEL,
            contents=question,
            config=config,
        )
        text = (response.text or "").strip()
        if not text:
            raise LLMClientError("Gemini가 빈 응답을 반환했습니다.")
        return text
    except LLMClientError:
        raise
    except Exception as exc:
        raise LLMClientError(f"Gemini API 호출 오류: {exc}") from exc
