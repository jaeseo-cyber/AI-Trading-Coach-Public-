"""Application-wide constants for markets, analysis, and UI options."""

from __future__ import annotations

# ── Market & analysis options (sidebar) ──────────────────────────────────────
MARKET_OPTIONS: tuple[str, ...] = ("한국 (KRX)", "미국 (NYSE/NASDAQ)")
ANALYSIS_TYPE_OPTIONS: tuple[str, ...] = ("종합 분석", "기술적 분석", "펀더멘털 분석")
INVESTMENT_PROFILE_OPTIONS: tuple[str, ...] = ("보수형", "중립형", "공격형")
DEFAULT_INVESTMENT_PROFILE_INDEX: int = 1

# ── Data fetching ────────────────────────────────────────────────────────────
PRICE_HISTORY_PERIOD: str = "1y"
SHORT_HISTORY_PERIOD: str = "5d"
MIN_TRADING_DAYS_FOR_TECH: int = 60

# ── UI layout ────────────────────────────────────────────────────────────────
CHART_COLUMN_RATIO: float = 1.65
TECH_COLUMN_RATIO: float = 1.0
