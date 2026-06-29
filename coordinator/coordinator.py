"""Coordinator — orchestrates all agents and produces the final analysis."""

from __future__ import annotations

import logging

from agents.investment_coach_agent import InvestmentCoachAgent
from agents.market_data_agent import MarketDataAgent
from agents.news_agent import NewsAgent
from agents.schemas import AnalysisRequest, CoordinatorResult
from agents.technical_analysis_agent import TechnicalAnalysisAgent

logger = logging.getLogger(__name__)


class AnalysisCoordinator:
    """Run the multi-agent pipeline in sequence and return aggregated results."""

    def __init__(
        self,
        market_data_agent: MarketDataAgent | None = None,
        technical_agent: TechnicalAnalysisAgent | None = None,
        news_agent: NewsAgent | None = None,
        coach_agent: InvestmentCoachAgent | None = None,
    ) -> None:
        self.market_data_agent = market_data_agent or MarketDataAgent()
        self.technical_agent = technical_agent or TechnicalAnalysisAgent()
        self.news_agent = news_agent or NewsAgent()
        self.coach_agent = coach_agent or InvestmentCoachAgent()

    def run(self, request: AnalysisRequest) -> CoordinatorResult:
        """
        Execute the full analysis pipeline:
        Market Data → Technical Analysis → News → Investment Coach
        """
        logger.info("Starting analysis for %s (%s)", request.ticker, request.market)

        market_data = self._run_market_data(request)
        technical = self._run_technical(request, market_data)
        news = self._run_news(request, market_data)
        coach = self._run_coach(request, market_data, technical, news)

        return CoordinatorResult(
            request=request,
            market_data=market_data,
            technical=technical,
            news=news,
            coach=coach,
        )

    def _run_market_data(self, request: AnalysisRequest):
        """Stage 1: fetch price and financial metrics."""
        try:
            return self.market_data_agent.run(request)
        except Exception as exc:
            logger.exception("Market Data Agent failed unexpectedly")
            from agents.schemas import MarketDataAgentResult

            return MarketDataAgentResult(error=f"시장 데이터 조회 중 오류: {exc}")

    def _run_technical(self, request: AnalysisRequest, market_data):
        """Stage 2: compute technical indicators."""
        try:
            return self.technical_agent.run(request, market_data.history)
        except Exception as exc:
            logger.exception("Technical Analysis Agent failed unexpectedly")
            from agents.schemas import TechnicalAnalysisAgentResult

            return TechnicalAnalysisAgentResult(
                error=f"기술적 분석 중 오류: {exc}",
            )

    def _run_news(self, request: AnalysisRequest, market_data):
        """Stage 3: collect recent news."""
        company_name = (
            market_data.metrics.name
            if market_data.metrics is not None
            else request.ticker
        )
        try:
            return self.news_agent.run(request, company_name)
        except Exception as exc:
            logger.exception("News Agent failed unexpectedly")
            from agents.schemas import NewsAgentResult

            return NewsAgentResult(error=f"뉴스 수집 중 오류: {exc}")

    def _run_coach(self, request, market_data, technical, news):
        """Stage 4: synthesize AI coaching report."""
        try:
            return self.coach_agent.run(request, market_data, technical, news)
        except Exception as exc:
            logger.exception("Investment Coach Agent failed unexpectedly")
            from agents.schemas import InvestmentCoachAgentResult

            return InvestmentCoachAgentResult(
                error=f"AI 분석 생성 중 오류: {exc}",
            )
