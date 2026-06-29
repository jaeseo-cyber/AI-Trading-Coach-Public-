"""Google Gemini API client (Ollama 대체)."""

from __future__ import annotations

from google import genai
from google.genai import types

from utils.config import get_gemini_api_key, get_gemini_model, validate_gemini_api_key
from utils.korean_rules import merge_korean_system_prompt


class LLMClientError(Exception):
    """Raised when an LLM API call fails."""


OllamaClientError = LLMClientError


def _api_key_error(exc: ValueError) -> LLMClientError:
    if exc.args and exc.args[0] == "non_ascii":
        return LLMClientError(
            "GEMINI_API_KEY 값이 올바르지 않습니다.\n"
            "Streamlit Secrets(또는 .env)에 한글·설명 문구가 아닌 "
            "Google AI Studio에서 발급한 영문 API 키(AIza...로 시작)만 입력했는지 확인하세요.\n"
            "발급: https://aistudio.google.com/apikey"
        )
    if exc.args and exc.args[0] == "invalid_format":
        return LLMClientError(
            "GEMINI_API_KEY 형식이 올바르지 않습니다.\n"
            "공백 없이 Google AI Studio에서 발급한 API 키 전체를 입력했는지 확인하세요.\n"
            "발급: https://aistudio.google.com/apikey"
        )
    return LLMClientError(
        "GEMINI_API_KEY가 설정되지 않았습니다.\n"
        "1) https://aistudio.google.com/apikey 에서 무료 API 키 발급\n"
        "2) .env 또는 Streamlit Secrets에 GEMINI_API_KEY=your_key 추가"
    )


def _get_client() -> genai.Client:
    api_key = get_gemini_api_key()
    try:
        validate_gemini_api_key(api_key)
    except ValueError as exc:
        raise _api_key_error(exc) from exc

    return genai.Client(api_key=api_key)


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
    model_name = (model or get_gemini_model()).strip()
    if not model_name.isascii():
        model_name = get_gemini_model()

    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=question)],
    )

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=model_name,
            contents=[user_content],
            config=config,
        )
        text = (response.text or "").strip()
        if not text:
            raise LLMClientError("Gemini가 빈 응답을 반환했습니다.")
        return text
    except LLMClientError:
        raise
    except UnicodeEncodeError as exc:
        raise LLMClientError(
            "Gemini API 요청 인코딩 오류입니다. "
            "GEMINI_API_KEY에 한글이나 특수문자가 섞여 있지 않은지 "
            "Streamlit Secrets 설정을 확인해 주세요."
        ) from exc
    except Exception as exc:
        message = str(exc)
        if "ascii" in message.lower() and "encode" in message.lower():
            raise LLMClientError(
                "Gemini API 요청 인코딩 오류입니다. "
                "GEMINI_API_KEY에 한글 placeholder(예: '여기에 키 입력')가 "
                "들어가 있지 않은지 Streamlit Secrets를 확인해 주세요."
            ) from exc
        raise LLMClientError(f"Gemini API 호출 오류: {exc}") from exc
