"""Multi-agent modules for AI Trading Coach."""

from agents.investment_coach_agent import InvestmentCoachAgent
from agents.market_data_agent import MarketDataAgent
from agents.news_agent import NewsAgent
from agents.schemas import (
    AnalysisRequest,
    CoordinatorResult,
    InvestmentCoachAgentResult,
    MarketDataAgentResult,
    NewsAgentResult,
    TechnicalAnalysisAgentResult,
)
from agents.technical_analysis_agent import TechnicalAnalysisAgent

__all__ = [
    "AnalysisRequest",
    "CoordinatorResult",
    "InvestmentCoachAgent",
    "InvestmentCoachAgentResult",
    "MarketDataAgent",
    "MarketDataAgentResult",
    "NewsAgent",
    "NewsAgentResult",
    "TechnicalAnalysisAgent",
    "TechnicalAnalysisAgentResult",
]
