"""LLM API client — Google Gemini + Groq (자동 폴백)."""

from __future__ import annotations

import re
import time

from google import genai
from google.genai import types

from services.groq_client import GroqClientError, ask_groq
from utils.config import (
    get_gemini_api_key,
    get_gemini_model,
    get_gemini_model_candidates,
    get_groq_api_key,
    get_llm_provider,
    validate_gemini_api_key,
)
from utils.korean_rules import merge_korean_system_prompt


class LLMClientError(Exception):
    """Raised when an LLM API call fails."""


OllamaClientError = LLMClientError

_QUOTA_RE = re.compile(r"retry in (\d+(?:\.\d+)?)s", re.IGNORECASE)
_MAX_RETRIES_PER_MODEL = 3


def _api_key_error(exc: ValueError) -> LLMClientError:
    if exc.args and exc.args[0] == "non_ascii":
        return LLMClientError(
            "GEMINI_API_KEY 값이 올바르지 않습니다.\n"
            "Streamlit Secrets에 Google AI Studio에서 발급한 영문 API 키만 입력했는지 확인하세요.\n"
            "발급: https://aistudio.google.com/apikey"
        )
    if exc.args and exc.args[0] == "invalid_format":
        return LLMClientError(
            "GEMINI_API_KEY 형식이 올바르지 않습니다.\n"
            "발급: https://aistudio.google.com/apikey"
        )
    return LLMClientError(
        "AI API 키가 설정되지 않았습니다.\n"
        "Gemini: https://aistudio.google.com/apikey\n"
        "Groq(대안): https://console.groq.com/keys"
    )


def _get_gemini_client() -> genai.Client:
    api_key = get_gemini_api_key()
    try:
        validate_gemini_api_key(api_key)
    except ValueError as exc:
        raise _api_key_error(exc) from exc
    return genai.Client(api_key=api_key)


def _is_quota_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return (
        "429" in message
        or "resource_exhausted" in message
        or "quota exceeded" in message
    )


def _is_transient_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return (
        "503" in message
        or "502" in message
        or "500" in message
        or "504" in message
        or "unavailable" in message
        or "high demand" in message
        or "overloaded" in message
        or "try again later" in message
    )


def _is_model_not_found(exc: Exception) -> bool:
    message = str(exc).lower()
    return "404" in message or "not found" in message or "not supported for generatecontent" in message


def _should_fallback_model(exc: Exception) -> bool:
    return _is_quota_error(exc) or _is_transient_error(exc) or _is_model_not_found(exc)


def _should_fallback_provider(exc: LLMClientError) -> bool:
    message = str(exc).lower()
    return (
        "429" in message
        or "503" in message
        or "404" in message
        or "quota" in message
        or "과부하" in message
        or "한도" in message
        or "not found" in message
        or "unavailable" in message
    )


def _retry_delay_seconds(exc: Exception, attempt: int, *, default: float = 3.0) -> float:
    match = _QUOTA_RE.search(str(exc))
    if match:
        return float(match.group(1)) + 0.5
    return min(default * (2**attempt), 12.0)


def _quota_error_message(model: str) -> LLMClientError:
    groq_hint = ""
    if get_groq_api_key():
        groq_hint = "\n• Groq 키가 설정되어 있어 자동 전환을 시도했으나 실패했습니다."
    else:
        groq_hint = (
            "\n• **대안:** Groq 무료 키 발급 후 Secrets에 추가\n"
            "  `GROQ_API_KEY = \"gsk_...\"`  (https://console.groq.com/keys)"
        )
    return LLMClientError(
        "Gemini API 무료 사용 한도(429)에 도달했습니다.\n\n"
        f"• 사용 모델: {model}\n"
        f"{groq_hint}\n\n"
        "1) 10~30분 후 다시 시도\n"
        "2) `GEMINI_MODEL = \"gemini-2.5-flash-lite\"` 또는 Groq 사용\n"
        "3) 사용량: https://ai.dev/rate-limit"
    )


def _transient_error_message(model: str) -> LLMClientError:
    return LLMClientError(
        "Gemini 서버가 일시적으로 과부하 상태입니다 (503).\n\n"
        f"• 마지막 시도 모델: {model}\n"
        "1~3분 후 다시 시도하거나 Groq API 키를 Secrets에 추가해 주세요."
    )


def _generate_gemini_once(
    client: genai.Client,
    *,
    model_name: str,
    user_content: types.Content,
    config: types.GenerateContentConfig | None,
) -> str:
    response = client.models.generate_content(
        model=model_name,
        contents=[user_content],
        config=config,
    )
    text = (response.text or "").strip()
    if not text:
        raise LLMClientError("Gemini가 빈 응답을 반환했습니다.")
    return text


def _ask_gemini(
    question: str,
    *,
    system_prompt: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
    korean_only: bool = True,
) -> str:
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

    preferred = (model or get_gemini_model()).strip()
    if not preferred.isascii():
        preferred = get_gemini_model()

    candidates = get_gemini_model_candidates(preferred)
    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=question)],
    )

    last_retryable_exc: Exception | None = None
    last_model = preferred

    client = _get_gemini_client()

    for model_name in candidates:
        last_model = model_name
        for attempt in range(_MAX_RETRIES_PER_MODEL):
            try:
                return _generate_gemini_once(
                    client,
                    model_name=model_name,
                    user_content=user_content,
                    config=config,
                )
            except LLMClientError:
                raise
            except UnicodeEncodeError as exc:
                raise LLMClientError(
                    "Gemini API 요청 인코딩 오류입니다. GEMINI_API_KEY를 확인해 주세요."
                ) from exc
            except Exception as exc:
                message = str(exc)
                if "ascii" in message.lower() and "encode" in message.lower():
                    raise LLMClientError(
                        "Gemini API 인코딩 오류입니다. GEMINI_API_KEY에 한글이 섞여 있지 않은지 확인하세요."
                    ) from exc
                if _should_fallback_model(exc):
                    last_retryable_exc = exc
                    if _is_model_not_found(exc):
                        break
                    if attempt < _MAX_RETRIES_PER_MODEL - 1:
                        time.sleep(_retry_delay_seconds(exc, attempt))
                        continue
                    break
                raise LLMClientError(f"Gemini API 호출 오류: {exc}") from exc

    if last_retryable_exc is not None:
        if _is_quota_error(last_retryable_exc):
            raise _quota_error_message(last_model) from last_retryable_exc
        if _is_transient_error(last_retryable_exc):
            raise _transient_error_message(last_model) from last_retryable_exc
        if _is_model_not_found(last_retryable_exc):
            raise LLMClientError(
                f"Gemini 모델을 찾을 수 없습니다 (404): {last_model}\n"
                'Secrets에서 GEMINI_MODEL = "gemini-2.5-flash-lite" 로 설정하세요.'
            ) from last_retryable_exc

    raise LLMClientError("Gemini API 호출에 실패했습니다.")


def ask_gpt(
    question: str,
    *,
    system_prompt: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
    korean_only: bool = True,
) -> str:
    """
    LLM 호출 — provider 설정에 따라 Gemini 또는 Groq 사용.

    LLM_PROVIDER=gemini (기본): Gemini → 실패 시 Groq 자동 폴백 (GROQ_API_KEY 있을 때)
    LLM_PROVIDER=groq: Groq만 사용
    """
    provider = get_llm_provider()
    groq_kwargs = {
        "system_prompt": system_prompt,
        "temperature": temperature,
        "korean_only": korean_only,
    }

    if provider == "groq":
        try:
            return ask_groq(question, model=model, **groq_kwargs)
        except GroqClientError as exc:
            raise LLMClientError(str(exc)) from exc

    # Gemini primary (default)
    if not get_gemini_api_key():
        if get_groq_api_key():
            try:
                return ask_groq(question, model=model, **groq_kwargs)
            except GroqClientError as exc:
                raise LLMClientError(str(exc)) from exc
        raise _api_key_error(ValueError("missing"))

    try:
        return _ask_gemini(
            question,
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
            korean_only=korean_only,
        )
    except LLMClientError as exc:
        if get_groq_api_key() and _should_fallback_provider(exc):
            try:
                return ask_groq(question, model=model, **groq_kwargs)
            except GroqClientError as groq_exc:
                raise LLMClientError(
                    f"{exc}\n\nGroq 대체 호출도 실패: {groq_exc}"
                ) from groq_exc
        raise
