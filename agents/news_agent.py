"""News Agent — collect, translate, and summarize recent company news."""

from __future__ import annotations

from agents.schemas import AnalysisRequest, NewsAgentResult
from services.news import NewsFetchError, NewsItem, fetch_company_news
from services.translator import translate_news_items


class NewsAgent:
    """Fetch recent news, translate to Korean, and produce a digest summary."""

    name = "News Agent"

    def run(
        self,
        request: AnalysisRequest,
        company_name: str,
    ) -> NewsAgentResult:
        try:
            items, source = fetch_company_news(
                request.ticker,
                request.market,
                company_name,
            )
        except NewsFetchError as exc:
            return NewsAgentResult(error=str(exc))

        items = translate_news_items(items)

        return NewsAgentResult(
            items=items,
            source=source,
            summary=build_news_summary(items),
        )


def build_news_summary(news_items: list[NewsItem]) -> str:
    """Create a concise digest from collected headlines."""
    if not news_items:
        return "수집된 뉴스가 없습니다."

    lines = ["최근 뉴스 요약:"]
    for index, item in enumerate(news_items, start=1):
        lines.append(f"{index}. {item.title}")
        if item.summary and item.summary != "요약 정보가 제공되지 않았습니다.":
            lines.append(f"   - {item.summary}")

    return "\n".join(lines)
