"""Backward-compatible wrapper for the Investment Coach Agent."""

from __future__ import annotations

from agents.investment_coach_agent import InvestmentCoachAgent
from agents.news_agent import build_news_summary
from agents.schemas import AnalysisRequest, MarketDataAgentResult, NewsAgentResult, TechnicalAnalysisAgentResult
from services.news import NewsItem
from services.stock_data import StockMetrics


def analyze_stock(
    ticker: str,
    market: str,
    analysis_type: str,
    investment_profile: str,
    *,
    metrics: StockMetrics,
    technical_context: str | None = None,
    news_items: list[NewsItem] | None = None,
) -> str:
    """Legacy entry point — delegates to InvestmentCoachAgent."""
    request = AnalysisRequest(
        ticker=ticker,
        market=market,
        analysis_type=analysis_type,
        investment_profile=investment_profile,
    )

    technical = TechnicalAnalysisAgentResult(
        context=technical_context or "기술적 분석 데이터를 사용할 수 없습니다.",
    )
    news = NewsAgentResult(
        items=news_items or [],
        summary=build_news_summary(news_items or []),
        error=None if news_items else "최근 뉴스 데이터를 사용할 수 없습니다.",
    )

    result = InvestmentCoachAgent().run(
        request,
        MarketDataAgentResult(metrics=metrics),
        technical,
        news,
    )

    if not result.success:
        from services.ollama_client import OllamaClientError

        raise OllamaClientError(result.error or "AI 분석 생성에 실패했습니다.")

    return result.analysis
