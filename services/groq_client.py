"""Groq API client — Gemini 대안 (무료 티어 RPM 넉넉)."""

from __future__ import annotations

import time

from utils.config import get_groq_api_key, get_groq_model
from utils.korean_rules import merge_korean_system_prompt


class GroqClientError(Exception):
    """Raised when Groq API call fails."""


def _is_retryable(exc: Exception) -> bool:
    message = str(exc).lower()
    return (
        "429" in message
        or "503" in message
        or "502" in message
        or "500" in message
        or "rate limit" in message
        or "overloaded" in message
    )


def ask_groq(
    question: str,
    *,
    system_prompt: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
    korean_only: bool = True,
) -> str:
    """Send a question to Groq (OpenAI-compatible chat API)."""
    api_key = get_groq_api_key().strip()
    if not api_key:
        raise GroqClientError(
            "GROQ_API_KEY가 설정되지 않았습니다.\n"
            "1) https://console.groq.com/keys 에서 무료 API 키 발급\n"
            "2) Streamlit Secrets에 GROQ_API_KEY=your_key 추가"
        )

    effective_system = (
        merge_korean_system_prompt(system_prompt)
        if korean_only
        else system_prompt
    )

    messages: list[dict[str, str]] = []
    if effective_system:
        messages.append({"role": "system", "content": effective_system})
    messages.append({"role": "user", "content": question})

    model_name = (model or get_groq_model()).strip()
    kwargs: dict = {"model": model_name, "messages": messages}
    if temperature is not None:
        kwargs["temperature"] = temperature

    try:
        from groq import Groq
    except ImportError as exc:
        raise GroqClientError(
            "groq 패키지가 설치되지 않았습니다. requirements.txt를 확인하세요."
        ) from exc

    client = Groq(api_key=api_key)
    last_exc: Exception | None = None

    for attempt in range(3):
        try:
            response = client.chat.completions.create(**kwargs)
            text = (response.choices[0].message.content or "").strip()
            if not text:
                raise GroqClientError("Groq가 빈 응답을 반환했습니다.")
            return text
        except GroqClientError:
            raise
        except Exception as exc:
            last_exc = exc
            if _is_retryable(exc) and attempt < 2:
                time.sleep(2.0 * (attempt + 1))
                continue
            break

    message = str(last_exc) if last_exc else "unknown"
    if "429" in message or "rate limit" in message.lower():
        raise GroqClientError(
            "Groq API 사용 한도(429)에 도달했습니다.\n\n"
            "1) 1~2분 후 다시 시도\n"
            "2) GROQ_MODEL을 `llama-3.1-8b-instant` 로 변경\n"
            "3) 한도 확인: https://console.groq.com/settings/limits"
        ) from last_exc
    raise GroqClientError(f"Groq API 호출 오류: {message}") from last_exc
