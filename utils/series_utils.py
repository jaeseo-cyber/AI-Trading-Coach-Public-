"""Pandas Series helpers shared across analysis modules."""

from __future__ import annotations

import pandas as pd


def latest_from_series(series: pd.Series) -> float | None:
    """Return the last valid float from a pandas Series."""
    if series.empty:
        return None

    value = series.iloc[-1]
    if pd.isna(value):
        return None

    return float(value)


def analyze_moving_averages(
    close: float | None,
    ma20: float | None,
    ma60: float | None,
) -> str:
    """Interpret price position relative to 20/60-day moving averages."""
    if close is None or ma20 is None or ma60 is None:
        return "이동평균선 데이터가 부족합니다."

    if close > ma20 > ma60:
        return "종가가 20일·60일 이동평균선 위에 있어 단기·중기 상승 추세로 해석됩니다."

    if close < ma20 < ma60:
        return "종가가 20일·60일 이동평균선 아래에 있어 단기·중기 하락 추세로 해석됩니다."

    if close > ma20:
        return "종가가 20일 이동평균선 위에 있으나 60일선과의 관계는 혼조입니다."

    if close < ma20:
        return "종가가 20일 이동평균선 아래에 있으나 60일선과의 관계는 혼조입니다."

    return "이동평균선 기준 뚜렷한 방향성이 나타나지 않습니다."
