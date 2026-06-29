"""Market Data Agent — stock price and financial metrics."""

from __future__ import annotations

from agents.schemas import AnalysisRequest, MarketDataAgentResult
from services.stock_chart import fetch_price_history
from services.stock_data import StockDataError, fetch_stock_metrics


class MarketDataAgent:
    """Fetch current price, financial metrics, and price history."""

    name = "Market Data Agent"

    def run(self, request: AnalysisRequest) -> MarketDataAgentResult:
        """Fetch metrics and price history; partial success if history fails."""
        try:
            metrics = fetch_stock_metrics(request.ticker, request.market)
        except StockDataError as exc:
            return MarketDataAgentResult(error=str(exc))

        try:
            history = fetch_price_history(request.ticker, request.market)
        except StockDataError as exc:
            return MarketDataAgentResult(metrics=metrics, error=str(exc))

        return MarketDataAgentResult(metrics=metrics, history=history)
