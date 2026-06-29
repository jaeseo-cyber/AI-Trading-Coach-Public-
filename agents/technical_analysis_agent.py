"""Technical Analysis Agent — RSI, MACD, and moving averages."""

from __future__ import annotations

import pandas as pd

from agents.schemas import AnalysisRequest, TechnicalAnalysisAgentResult
from services.technical_analysis import (
    TechnicalAnalysisError,
    build_technical_context,
    compute_technical_analysis,
)
from utils.formatters import format_indicator
from utils.series_utils import analyze_moving_averages, latest_from_series


class TechnicalAnalysisAgent:
    """Compute and interpret technical indicators."""

    name = "Technical Analysis Agent"

    def run(
        self,
        request: AnalysisRequest,
        history: pd.DataFrame | None,
    ) -> TechnicalAnalysisAgentResult:
        if history is None or history.empty:
            return TechnicalAnalysisAgentResult(
                error="주가 이력이 없어 기술적 분석을 수행할 수 없습니다.",
            )

        try:
            result = compute_technical_analysis(history)
        except TechnicalAnalysisError as exc:
            return TechnicalAnalysisAgentResult(error=str(exc))

        close = history["Close"]
        ma20 = latest_from_series(close.rolling(window=20, min_periods=20).mean())
        ma60 = latest_from_series(close.rolling(window=60, min_periods=60).mean())
        ma_analysis = analyze_moving_averages(
            close=latest_from_series(close),
            ma20=ma20,
            ma60=ma60,
        )

        context = (
            f"{build_technical_context(result)}\n"
            f"- MA20: {format_indicator(ma20)}\n"
            f"- MA60: {format_indicator(ma60)}\n"
            f"- 이동평균선 해석: {ma_analysis}"
        )

        return TechnicalAnalysisAgentResult(
            result=result,
            ma20=ma20,
            ma60=ma60,
            ma_analysis=ma_analysis,
            context=context,
        )
