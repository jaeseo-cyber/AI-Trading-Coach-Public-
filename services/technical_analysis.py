"""Technical indicator calculations and trend interpretation."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from utils.constants import MIN_TRADING_DAYS_FOR_TECH
from utils.formatters import format_indicator
from utils.series_utils import latest_from_series

# Re-export for backward compatibility
__all__ = [
    "TechnicalAnalysisError",
    "TechnicalIndicators",
    "TechnicalAnalysisResult",
    "build_technical_context",
    "compute_technical_analysis",
    "format_indicator",
]


class TechnicalAnalysisError(Exception):
    """Raised when technical indicators cannot be computed."""


@dataclass(frozen=True)
class TechnicalIndicators:
    """Latest values of computed technical indicators."""

    rsi: float | None
    macd: float | None
    signal: float | None
    bb_upper: float | None
    bb_middle: float | None
    bb_lower: float | None
    close: float | None


@dataclass(frozen=True)
class TechnicalAnalysisResult:
    """Interpreted technical analysis output."""

    indicators: TechnicalIndicators
    trend_label: str
    momentum_label: str
    trend_explanation: str
    momentum_explanation: str
    summary: str


# ── Indicator calculations ───────────────────────────────────────────────────


def _calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Compute Relative Strength Index."""
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))


def _calculate_macd(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal_period: int = 9,
) -> tuple[pd.Series, pd.Series]:
    """Compute MACD line and signal line."""
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    return macd, signal


def _calculate_bollinger(
    close: pd.Series,
    period: int = 20,
    std_dev: float = 2.0,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Compute Bollinger Band upper, middle, and lower lines."""
    middle = close.rolling(window=period, min_periods=period).mean()
    std = close.rolling(window=period, min_periods=period).std()
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    return upper, middle, lower


# ── Trend / momentum interpretation ─────────────────────────────────────────


def _interpret_trend(
    close: float,
    ma20: float | None,
    ma60: float | None,
    macd: float | None,
    signal: float | None,
) -> tuple[str, str]:
    """Determine trend direction from moving averages and MACD."""
    bullish_points: list[str] = []
    bearish_points: list[str] = []

    if ma20 is not None and ma60 is not None:
        if close > ma20 > ma60:
            bullish_points.append(
                "종가가 20일·60일 이동평균선 위에 있어 단기·중기 상승 구조입니다."
            )
        elif close < ma20 < ma60:
            bearish_points.append(
                "종가가 20일·60일 이동평균선 아래에 있어 단기·중기 하락 구조입니다."
            )
        elif close > ma20:
            bullish_points.append("종가가 20일 이동평균선 위에 있습니다.")
        elif close < ma20:
            bearish_points.append("종가가 20일 이동평균선 아래에 있습니다.")

    if macd is not None and signal is not None:
        if macd > signal:
            bullish_points.append("MACD가 시그널 선 위에 있어 매수 모멘텀이 우세합니다.")
        elif macd < signal:
            bearish_points.append("MACD가 시그널 선 아래에 있어 매도 모멘텀이 우세합니다.")

    if len(bullish_points) > len(bearish_points):
        label = "상승추세"
        explanation = " ".join(bullish_points)
        if bearish_points:
            explanation += f" 다만 {bearish_points[0]}"
        return label, explanation

    if len(bearish_points) > len(bullish_points):
        label = "하락추세"
        explanation = " ".join(bearish_points)
        if bullish_points:
            explanation += f" 다만 {bullish_points[0]}"
        return label, explanation

    return (
        "횡보",
        "이동평균선과 MACD 기준으로 뚜렷한 방향성이 나타나지 않습니다. "
        "추세 전환 여부를 추가로 확인하는 것이 좋습니다.",
    )


def _interpret_momentum(
    rsi: float | None,
    close: float,
    bb_upper: float | None,
    bb_lower: float | None,
    macd: float | None,
    signal: float | None,
) -> tuple[str, str]:
    """Determine overbought/oversold momentum from RSI and Bollinger Bands."""
    overbought_points: list[str] = []
    oversold_points: list[str] = []

    if rsi is not None:
        if rsi >= 70:
            overbought_points.append(
                f"RSI가 {rsi:.1f}로 70 이상 구간에 있어 과매수 가능성이 있습니다."
            )
        elif rsi <= 30:
            oversold_points.append(
                f"RSI가 {rsi:.1f}로 30 이하 구간에 있어 과매도 가능성이 있습니다."
            )

    if bb_upper is not None and close >= bb_upper:
        overbought_points.append(
            "종가가 볼린저 밴드 상단에 닿거나 돌파해 단기 과열 신호가 보입니다."
        )
    if bb_lower is not None and close <= bb_lower:
        oversold_points.append(
            "종가가 볼린저 밴드 하단에 닿거나 이탈해 단기 과매도 신호가 보입니다."
        )

    if (
        macd is not None
        and signal is not None
        and macd > signal
        and rsi is not None
        and rsi >= 60
    ):
        overbought_points.append(
            "MACD 상승과 RSI 상승이 겹치며 단기 과열이 강화될 수 있습니다."
        )
    if (
        macd is not None
        and signal is not None
        and macd < signal
        and rsi is not None
        and rsi <= 40
    ):
        oversold_points.append(
            "MACD 하락과 RSI 약세가 겹치며 반등 전까지 조정이 이어질 수 있습니다."
        )

    if overbought_points and not oversold_points:
        return "과매수", " ".join(overbought_points)
    if oversold_points and not overbought_points:
        return "과매도", " ".join(oversold_points)
    if overbought_points and oversold_points:
        return "혼조", " ".join(overbought_points + oversold_points)

    return (
        "중립",
        "RSI와 볼린저 밴드 기준으로 과매수·과매도 구간에 해당하지 않습니다. "
        "추세 지표와 함께 종합적으로 판단해 주세요.",
    )


# ── Public API ───────────────────────────────────────────────────────────────


def compute_technical_analysis(history: pd.DataFrame) -> TechnicalAnalysisResult:
    """Compute RSI, MACD, Signal, Bollinger Bands and interpret the trend."""
    if history.empty or "Close" not in history.columns:
        raise TechnicalAnalysisError(
            "차트 데이터가 부족해 기술적 분석을 수행할 수 없습니다."
        )

    if len(history) < MIN_TRADING_DAYS_FOR_TECH:
        raise TechnicalAnalysisError(
            f"기술적 분석을 위해 최소 {MIN_TRADING_DAYS_FOR_TECH}거래일 이상의 "
            "데이터가 필요합니다. 다른 종목을 선택하거나 잠시 후 다시 시도해 주세요."
        )

    close = history["Close"]
    ma20 = close.rolling(window=20, min_periods=20).mean()
    ma60 = close.rolling(window=60, min_periods=60).mean()

    rsi_series = _calculate_rsi(close)
    macd_series, signal_series = _calculate_macd(close)
    bb_upper, bb_middle, bb_lower = _calculate_bollinger(close)

    indicators = TechnicalIndicators(
        rsi=latest_from_series(rsi_series),
        macd=latest_from_series(macd_series),
        signal=latest_from_series(signal_series),
        bb_upper=latest_from_series(bb_upper),
        bb_middle=latest_from_series(bb_middle),
        bb_lower=latest_from_series(bb_lower),
        close=latest_from_series(close),
    )

    if indicators.close is None:
        raise TechnicalAnalysisError(
            "종가 데이터를 확인할 수 없어 기술적 분석을 수행할 수 없습니다."
        )

    trend_label, trend_explanation = _interpret_trend(
        close=indicators.close,
        ma20=latest_from_series(ma20),
        ma60=latest_from_series(ma60),
        macd=indicators.macd,
        signal=indicators.signal,
    )
    momentum_label, momentum_explanation = _interpret_momentum(
        rsi=indicators.rsi,
        close=indicators.close,
        bb_upper=indicators.bb_upper,
        bb_lower=indicators.bb_lower,
        macd=indicators.macd,
        signal=indicators.signal,
    )

    summary = (
        f"**추세 판단: {trend_label}**\n\n{trend_explanation}\n\n"
        f"**모멘텀 판단: {momentum_label}**\n\n{momentum_explanation}"
    )

    return TechnicalAnalysisResult(
        indicators=indicators,
        trend_label=trend_label,
        momentum_label=momentum_label,
        trend_explanation=trend_explanation,
        momentum_explanation=momentum_explanation,
        summary=summary,
    )


def build_technical_context(result: TechnicalAnalysisResult) -> str:
    """Format technical analysis for AI prompt context."""
    indicators = result.indicators
    return (
        f"- RSI: {format_indicator(indicators.rsi)}\n"
        f"- MACD: {format_indicator(indicators.macd)}\n"
        f"- 시그널: {format_indicator(indicators.signal)}\n"
        f"- 볼린저 상단: {format_indicator(indicators.bb_upper)}\n"
        f"- 볼린저 중간: {format_indicator(indicators.bb_middle)}\n"
        f"- 볼린저 하단: {format_indicator(indicators.bb_lower)}\n"
        f"- 추세 판단: {result.trend_label}\n"
        f"- 모멘텀 판단: {result.momentum_label}\n"
        f"- 추세 설명: {result.trend_explanation}\n"
        f"- 모멘텀 설명: {result.momentum_explanation}"
    )
