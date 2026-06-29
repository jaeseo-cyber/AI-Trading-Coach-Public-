"""Korean UI labels and display-name mappings."""

from __future__ import annotations

# ── News source display names ────────────────────────────────────────────────
NEWS_SOURCE_KO: dict[str, str] = {
    "NewsAPI": "뉴스 API",
    "Yahoo Finance": "야후 파이낸스",
    "Google News RSS": "구글 뉴스",
    "Google News": "구글 뉴스",
}

# ── Technical indicator labels ───────────────────────────────────────────────
TECH_LABEL_RSI = "RSI (14)"
TECH_LABEL_MACD = "MACD"
TECH_LABEL_SIGNAL = "시그널"
TECH_LABEL_CLOSE = "종가"
TECH_LABEL_BB_UPPER = "볼린저 상단"
TECH_LABEL_BB_MID = "볼린저 중간"
TECH_LABEL_BB_LOWER = "볼린저 하단"
TECH_LABEL_MA20 = "20일 이동평균"
TECH_LABEL_MA60 = "60일 이동평균"


def localize_news_source(source: str | None) -> str:
    """Return a Korean display name for a news source."""
    if not source:
        return ""
    return NEWS_SOURCE_KO.get(source, source)
