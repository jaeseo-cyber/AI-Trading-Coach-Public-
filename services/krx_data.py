"""KRX stock data via FinanceDataReader (Streamlit Cloud / Yahoo 차단 대비)."""

from __future__ import annotations

import pandas as pd

from utils.formatters import safe_to_float


def _krx_code(ticker: str) -> str:
    """Return 6-digit KRX code from symbol like 005930.KS."""
    code = ticker.strip().upper().split(".")[0]
    return code.zfill(6)


def fetch_krx_history(ticker: str, *, start: str | None = None) -> pd.DataFrame:
    """Fetch OHLCV history from Naver/KRX via FinanceDataReader."""
    import FinanceDataReader as fdr

    code = _krx_code(ticker)
    # FDR v0.9+: DataReader('005930') — 'KRX' 두 번째 인자는 start 날짜로 해석됨 (버그 원인)
    if start:
        df = fdr.DataReader(code, start)
    else:
        df = fdr.DataReader(code)
    if df is None or df.empty:
        raise ValueError(f"KRX 데이터 없음: {code}")
    return df


def _fetch_listing_row(code: str) -> pd.Series | None:
    """Return KRX listing row for a single code."""
    import FinanceDataReader as fdr

    listing = fdr.StockListing("KRX")
    rows = listing[listing["Code"].astype(str).str.zfill(6) == code]
    if rows.empty:
        return None
    return rows.iloc[0]


def fetch_krx_metrics(ticker: str, market: str) -> dict:
    """
    Build metrics dict compatible with StockMetrics from KRX sources.

    Returns keys: name, currency, current_price, market_cap, per, pbr, eps,
    fifty_two_week_high, fifty_two_week_low, symbol
    """
    code = _krx_code(ticker)
    history = fetch_krx_history(ticker)
    current_price = float(history["Close"].iloc[-1])
    high_52 = float(history["Close"].tail(252).max()) if len(history) >= 20 else None
    low_52 = float(history["Close"].tail(252).min()) if len(history) >= 20 else None

    name = code
    market_cap = per = pbr = eps = None

    try:
        row = _fetch_listing_row(code)
        if row is not None:
            name = str(row.get("Name", code))
            market_cap = safe_to_float(row.get("Marcap"))
            listing_close = safe_to_float(row.get("Close"))
            if listing_close is not None:
                current_price = listing_close
    except Exception:
        pass

    return {
        "symbol": f"{code}.KS",
        "name": name,
        "currency": "KRW",
        "current_price": current_price,
        "market_cap": market_cap,
        "per": per,
        "pbr": pbr,
        "eps": eps,
        "fifty_two_week_high": high_52,
        "fifty_two_week_low": low_52,
    }
