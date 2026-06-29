"""Shared schemas for multi-agent analysis pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from services.news import NewsItem
from services.stock_data import StockMetrics
from services.technical_analysis import TechnicalAnalysisResult


@dataclass(frozen=True)
class AnalysisRequest:
    ticker: str
    market: str
    analysis_type: str
    investment_profile: str


@dataclass
class MarketDataAgentResult:
    metrics: StockMetrics | None = None
    history: pd.DataFrame | None = None
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.metrics is not None and self.error is None


@dataclass
class TechnicalAnalysisAgentResult:
    result: TechnicalAnalysisResult | None = None
    ma20: float | None = None
    ma60: float | None = None
    ma_analysis: str = ""
    context: str = ""
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.result is not None and self.error is None


@dataclass
class NewsAgentResult:
    items: list[NewsItem] = field(default_factory=list)
    source: str | None = None
    summary: str = ""
    error: str | None = None

    @property
    def success(self) -> bool:
        return bool(self.items) and self.error is None


@dataclass
class InvestmentCoachAgentResult:
    analysis: str = ""
    error: str | None = None

    @property
    def success(self) -> bool:
        return bool(self.analysis) and self.error is None


@dataclass
class CoordinatorResult:
    request: AnalysisRequest
    market_data: MarketDataAgentResult
    technical: TechnicalAnalysisAgentResult
    news: NewsAgentResult
    coach: InvestmentCoachAgentResult
