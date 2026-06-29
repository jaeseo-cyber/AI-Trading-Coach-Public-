"""FinanceDataReader fallback when Yahoo Finance is blocked (Streamlit Cloud)."""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

from utils.formatters import safe_to_float

_FDR_CHART_DAYS = 370


def _history_start() -> str:
    return (datetime.now() - timedelta(days=_FDR_CHART_DAYS)).strftime("%Y-%m-%d")


def _fdr_code(symbol: str, market: str) -> str:
    """Return FinanceDataReader symbol (6-digit KRX code or US ticker)."""
    base = symbol.strip().upper().split(".")[0]
    if market.startswith("한국"):
        return base.zfill(6)
    return base


def fetch_fdr_history(
    symbol: str,
    market: str,
    *,
    start: str | None = None,
    full: bool = False,
) -> pd.DataFrame:
    """Fetch OHLCV history via FinanceDataReader (Naver/KRX/Stooq/Yahoo)."""
    import FinanceDataReader as fdr

    code = _fdr_code(symbol, market)
    if start:
        df = fdr.DataReader(code, start)
    elif full:
        df = fdr.DataReader(code)
    else:
        df = fdr.DataReader(code, _history_start())

    if df is None or df.empty:
        raise ValueError(f"FinanceDataReader 데이터 없음: {code}")
    return df


def _fetch_krx_listing_row(code: str) -> pd.Series | None:
    import FinanceDataReader as fdr

    listing = fdr.StockListing("KRX")
    rows = listing[listing["Code"].astype(str).str.zfill(6) == code]
    if rows.empty:
        return None
    return rows.iloc[0]


def _fetch_us_listing_row(ticker: str) -> pd.Series | None:
    import FinanceDataReader as fdr

    for market in ("NASDAQ", "NYSE"):
        try:
            listing = fdr.StockListing(market)
            rows = listing[listing["Symbol"].astype(str).str.upper() == ticker.upper()]
            if not rows.empty:
                return rows.iloc[0]
        except Exception:
            continue
    return None


def fetch_fdr_metrics(symbol: str, market: str) -> dict:
    """
    Build metrics dict compatible with StockMetrics from FinanceDataReader.

    Returns keys: symbol, name, currency, current_price, market_cap, per, pbr, eps,
    fifty_two_week_high, fifty_two_week_low
    """
    code = _fdr_code(symbol, market)
    is_korea = market.startswith("한국")
    history = fetch_fdr_history(symbol, market, full=True)
    current_price = float(history["Close"].iloc[-1])
    high_52 = float(history["Close"].tail(252).max()) if len(history) >= 20 else None
    low_52 = float(history["Close"].tail(252).min()) if len(history) >= 20 else None

    name = code
    market_cap = per = pbr = eps = None
    currency = "KRW" if is_korea else "USD"
    out_symbol = f"{code}.KS" if is_korea else code

    try:
        if is_korea:
            row = _fetch_krx_listing_row(code)
            if row is not None:
                name = str(row.get("Name", code))
                market_cap = safe_to_float(row.get("Marcap"))
                listing_close = safe_to_float(row.get("Close"))
                if listing_close is not None:
                    current_price = listing_close
        else:
            row = _fetch_us_listing_row(code)
            if row is not None:
                name = str(row.get("Name", code))
    except Exception:
        pass

    return {
        "symbol": out_symbol,
        "name": name,
        "currency": currency,
        "current_price": current_price,
        "market_cap": market_cap,
        "per": per,
        "pbr": pbr,
        "eps": eps,
        "fifty_two_week_high": high_52,
        "fifty_two_week_low": low_52,
    }
