"""Backward-compatible KRX helpers — delegates to services.fdr_data."""

from __future__ import annotations

import pandas as pd

from services.fdr_data import fetch_fdr_history, fetch_fdr_metrics


def fetch_krx_history(ticker: str, *, start: str | None = None) -> pd.DataFrame:
    """Fetch OHLCV history from Naver/KRX via FinanceDataReader."""
    return fetch_fdr_history(ticker, "한국 (KRX)", start=start, full=True)


def fetch_krx_metrics(ticker: str, market: str) -> dict:
    """Build metrics dict for Korean stocks via FinanceDataReader."""
    return fetch_fdr_metrics(ticker, market)
