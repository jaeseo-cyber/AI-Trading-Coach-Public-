"""Translate foreign-language news to Korean (minimal Gemini usage)."""

from __future__ import annotations

import json
import re

from services.korean_localizer import apply_deterministic_patch, korean_ratio
from services.news import NewsItem
from services.ollama_client import OllamaClientError, ask_gpt

_TRANSLATE_SYSTEM = """\
당신은 금융·주식 뉴스 전문 번역가입니다.
입력된 뉴스 제목과 요약을 자연스럽고 정확한 한국어로 번역합니다.

규칙:
- 반드시 한국어로만 출력합니다.
- JSON 배열만 출력하고 다른 설명·코드·주석은 포함하지 않습니다.
- 고유명사(회사명, 티커)는 음역 또는 원문 유지 중 더 자연스러운 쪽을 선택합니다.
- 번역 결과 형식: [{"title": "...", "summary": "..."}, ...]
"""


def needs_translation(text: str, threshold: float = 0.35) -> bool:
    """Return True if the text is mostly non-Korean and should be translated."""
    stripped = text.strip()
    if not stripped:
        return False
    return korean_ratio(stripped) < threshold


def translate_news_items(items: list[NewsItem]) -> list[NewsItem]:
    """
    Translate foreign news titles/summaries to Korean.

    Uses a single Gemini call for the whole batch. On quota errors, returns
    originals (coach still summarizes news in Korean).
    """
    if not items:
        return items

    translate_indices = [
        index
        for index, item in enumerate(items)
        if needs_translation(item.title) or needs_translation(item.summary)
    ]
    if not translate_indices:
        return items

    batch = [items[index] for index in translate_indices]
    try:
        translated = _translate_batch(batch)
    except (OllamaClientError, ValueError, json.JSONDecodeError):
        return items

    result = list(items)
    for index, new_item in zip(translate_indices, translated):
        result[index] = new_item
    return result


def _translate_batch(items: list[NewsItem]) -> list[NewsItem]:
    """Translate a batch of news items in a single Gemini call."""
    lines: list[str] = []
    for index, item in enumerate(items, start=1):
        lines.append(f"{index}. 제목: {item.title}")
        lines.append(f"   요약: {item.summary}")

    prompt = (
        "다음 뉴스 항목을 한국어로 번역해 주세요.\n"
        "입력 순서와 개수를 유지하고 JSON 배열만 반환하세요.\n\n"
        + "\n".join(lines)
    )

    raw = ask_gpt(prompt, system_prompt=_TRANSLATE_SYSTEM)
    parsed = _parse_translation_json(raw, expected_count=len(items))

    translated: list[NewsItem] = []
    for original, entry in zip(items, parsed):
        title = apply_deterministic_patch(
            str(entry.get("title") or original.title).strip()
        )
        summary = apply_deterministic_patch(
            str(entry.get("summary") or original.summary).strip()
        )
        translated.append(
            NewsItem(
                title=title or original.title,
                summary=summary or original.summary,
                url=original.url,
                source=original.source,
                published_at=original.published_at,
            )
        )
    return translated


def _parse_translation_json(raw: str, expected_count: int) -> list[dict]:
    """Extract and parse a JSON array from the model response."""
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("JSON array not found in translation response")

    data = json.loads(cleaned[start : end + 1])
    if not isinstance(data, list) or len(data) != expected_count:
        raise ValueError("Unexpected translation result shape")
    return data
