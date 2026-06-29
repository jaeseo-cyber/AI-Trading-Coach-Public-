"""Google Gemini API client (Ollama 대체)."""

from __future__ import annotations

import re
import time

from google import genai
from google.genai import types

from utils.config import (
    get_gemini_api_key,
    get_gemini_model,
    get_gemini_model_candidates,
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
            "Streamlit Secrets(또는 .env)에 한글·설명 문구가 아닌 "
            "Google AI Studio에서 발급한 영문 API 키만 입력했는지 확인하세요.\n"
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


def _is_quota_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return (
        "429" in message
        or "resource_exhausted" in message
        or "quota exceeded" in message
    )


def _is_transient_error(exc: Exception) -> bool:
    """503/5xx — server overload; retry or switch model."""
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


def _retry_delay_seconds(exc: Exception, attempt: int, *, default: float = 3.0) -> float:
    match = _QUOTA_RE.search(str(exc))
    if match:
        return float(match.group(1)) + 0.5
    return min(default * (2**attempt), 12.0)


def _quota_error_message(model: str) -> LLMClientError:
    return LLMClientError(
        "Gemini API 무료 사용 한도(429)에 도달했습니다.\n\n"
        f"• 사용 모델: {model}\n"
        "• 무료 티어는 하루 요청 수(RPD)가 적습니다.\n\n"
        "**해결 방법**\n"
        "1) 10~30분 후 다시 시도 (일일 한도는 태평양 자정에 초기화)\n"
        "2) Secrets에서 `GEMINI_MODEL = \"gemini-2.5-flash-lite\"` 로 변경\n"
        "3) 사용량 확인: https://ai.dev/rate-limit"
    )


def _transient_error_message(model: str) -> LLMClientError:
    return LLMClientError(
        "Gemini 서버가 일시적으로 과부하 상태입니다 (503).\n\n"
        f"• 마지막 시도 모델: {model}\n"
        "• 다른 모델로 자동 재시도했으나 모두 실패했습니다.\n\n"
        "**해결 방법**\n"
        "1) **1~3분 후** 다시 '분석 시작' 클릭 (일시적 트래픽 급증)\n"
        "2) Streamlit Secrets에서 모델 변경:\n"
        '   `GEMINI_MODEL = "gemini-2.5-flash-lite"`\n'
        "3) 그래도 실패하면 `gemini-2.0-flash-lite` 시도"
    )


def _generate_once(
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

    try:
        client = _get_client()
    except LLMClientError:
        raise
    except Exception as exc:
        raise LLMClientError(f"Gemini API 호출 오류: {exc}") from exc

    for model_name in candidates:
        last_model = model_name
        for attempt in range(_MAX_RETRIES_PER_MODEL):
            try:
                return _generate_once(
                    client,
                    model_name=model_name,
                    user_content=user_content,
                    config=config,
                )
            except LLMClientError:
                raise
            except UnicodeEncodeError as exc:
                raise LLMClientError(
                    "Gemini API 요청 인코딩 오류입니다. "
                    "GEMINI_API_KEY에 한글이 섞여 있지 않은지 확인해 주세요."
                ) from exc
            except Exception as exc:
                message = str(exc)
                if "ascii" in message.lower() and "encode" in message.lower():
                    raise LLMClientError(
                        "Gemini API 요청 인코딩 오류입니다. "
                        "GEMINI_API_KEY에 한글 placeholder가 들어가 있지 않은지 확인해 주세요."
                    ) from exc
                if _should_fallback_model(exc):
                    last_retryable_exc = exc
                    # 404: model deprecated — skip retries, try next model immediately
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
                "지정한 Gemini 모델을 찾을 수 없습니다 (404).\n\n"
                f"• 마지막 시도: {last_model}\n"
                "• Streamlit Secrets의 `GEMINI_MODEL`을 아래 중 하나로 설정하세요:\n"
                '  `gemini-2.5-flash-lite` (권장) 또는 `gemini-2.0-flash`'
            ) from last_retryable_exc

    raise LLMClientError("Gemini API 호출에 실패했습니다. 잠시 후 다시 시도해 주세요.")
