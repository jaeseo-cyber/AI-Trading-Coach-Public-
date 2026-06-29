"""Fetch company news from NewsAPI, Yahoo Finance, or RSS feeds."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime

import yfinance as yf

from services.stock_data import normalize_ticker
from utils.config import MAX_NEWS_ITEMS, NEWS_API_KEY


class NewsFetchError(Exception):
    """Raised when no news source returns results."""


@dataclass(frozen=True)
class NewsItem:
    title: str
    summary: str
    url: str | None
    source: str | None
    published_at: str | None


def fetch_company_news(
    ticker: str,
    market: str,
    company_name: str,
    *,
    limit: int = MAX_NEWS_ITEMS,
) -> tuple[list[NewsItem], str]:
    """Fetch recent news using NewsAPI, then Yahoo Finance, then RSS."""
    query = _build_search_query(ticker, company_name)
    errors: list[str] = []

    if NEWS_API_KEY:
        try:
            items = _fetch_from_newsapi(query, limit=limit)
            if items:
                return items[:limit], "NewsAPI"
        except Exception as exc:
            errors.append(f"NewsAPI: {exc}")

    try:
        items = _fetch_from_yahoo_finance(ticker, market, limit=limit)
        if items:
            return items[:limit], "Yahoo Finance"
    except Exception as exc:
        errors.append(f"Yahoo Finance: {exc}")

    try:
        items = _fetch_from_google_rss(query, limit=limit)
        if items:
            return items[:limit], "Google News RSS"
    except Exception as exc:
        errors.append(f"RSS: {exc}")

    if NEWS_API_KEY:
        detail = "모든 뉴스 소스에서 결과를 가져오지 못했습니다."
    else:
        detail = (
            "뉴스를 가져오지 못했습니다. "
            "환경 설정에 뉴스 API 키를 등록하면 더 많은 뉴스 소스를 사용할 수 있습니다."
        )

    if errors:
        detail += f" ({'; '.join(errors[:2])})"

    raise NewsFetchError(detail)


def _build_search_query(ticker: str, company_name: str) -> str:
    cleaned_name = company_name.strip()
    if cleaned_name and cleaned_name.upper() != ticker.upper():
        return cleaned_name
    return ticker.strip()


def _fetch_from_newsapi(query: str, *, limit: int) -> list[NewsItem]:
    params = urllib.parse.urlencode(
        {
            "q": query,
            "sortBy": "publishedAt",
            "pageSize": str(limit),
            "apiKey": NEWS_API_KEY,
        }
    )
    url = f"https://newsapi.org/v2/everything?{params}"
    payload = _http_get_json(url)

    if payload.get("status") != "ok":
        message = payload.get("message", "NewsAPI 응답 오류")
        raise NewsFetchError(message)

    items: list[NewsItem] = []
    for article in payload.get("articles", []):
        title = str(article.get("title") or "").strip()
        if not title or title.lower() == "[removed]":
            continue

        summary = str(article.get("description") or article.get("content") or "").strip()
        if not summary:
            summary = "요약 정보가 제공되지 않았습니다."

        source_info = article.get("source") or {}
        items.append(
            NewsItem(
                title=title,
                summary=summary,
                url=article.get("url"),
                source=source_info.get("name"),
                published_at=_format_datetime(article.get("publishedAt")),
            )
        )

    return items


def _fetch_from_yahoo_finance(ticker: str, market: str, *, limit: int) -> list[NewsItem]:
    symbol = normalize_ticker(ticker, market)
    raw_news = yf.Ticker(symbol).news or []

    items: list[NewsItem] = []
    for entry in raw_news:
        content = entry.get("content") or entry
        title = str(content.get("title") or "").strip()
        if not title:
            continue

        summary = str(
            content.get("summary")
            or content.get("description")
            or ""
        ).strip()
        if not summary:
            summary = "요약 정보가 제공되지 않았습니다."

        provider = content.get("provider") or {}
        url = _extract_yahoo_url(content)

        items.append(
            NewsItem(
                title=title,
                summary=summary,
                url=url,
                source=str(provider.get("displayName") or "Yahoo Finance"),
                published_at=_format_datetime(
                    content.get("pubDate") or content.get("displayTime")
                ),
            )
        )

        if len(items) >= limit:
            break

    return items


def _fetch_from_google_rss(query: str, *, limit: int) -> list[NewsItem]:
    encoded_query = urllib.parse.quote(query)
    url = (
        "https://news.google.com/rss/search?"
        f"q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    )
    xml_text = _http_get_text(url)
    root = ET.fromstring(xml_text)

    items: list[NewsItem] = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        if not title:
            continue

        summary = (item.findtext("description") or item.findtext("content") or "").strip()
        summary = _strip_html(summary)
        if not summary:
            summary = "요약 정보가 제공되지 않았습니다."

        items.append(
            NewsItem(
                title=title,
                summary=summary,
                url=item.findtext("link"),
                source=item.findtext("source") or "Google News",
                published_at=_format_datetime(item.findtext("pubDate")),
            )
        )

        if len(items) >= limit:
            break

    return items


def _extract_yahoo_url(content: dict) -> str | None:
    for key in ("clickThroughUrl", "canonicalUrl"):
        link = content.get(key)
        if isinstance(link, dict) and link.get("url"):
            return str(link["url"])
    return content.get("link")


def _http_get_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "AI-Trading-Coach/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise NewsFetchError(f"HTTP {exc.code}: {body[:120]}") from exc
    except urllib.error.URLError as exc:
        raise NewsFetchError("네트워크 연결에 실패했습니다.") from exc


def _http_get_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "AI-Trading-Coach/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise NewsFetchError("RSS 피드를 불러오지 못했습니다.") from exc


def _format_datetime(value: str | None) -> str | None:
    if not value:
        return None

    normalized = value.replace("Z", "+00:00")
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
    ):
        try:
            parsed = datetime.strptime(normalized, fmt)
            return parsed.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            continue

    return value[:16]


def _strip_html(text: str) -> str:
    cleaned = text.replace("<![CDATA[", "").replace("]]>", "")
    while "<" in cleaned and ">" in cleaned:
        start = cleaned.find("<")
        end = cleaned.find(">", start)
        if end == -1:
            break
        cleaned = cleaned[:start] + cleaned[end + 1 :]
    return cleaned.strip()
