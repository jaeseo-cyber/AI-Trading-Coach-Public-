"""KRX stock data via FinanceDataReader (Streamlit Cloud / Yahoo 차단 대비)."""

from __future__ import annotations

import pandas as pd

from utils.formatters import safe_to_float


def _krx_code(ticker: str) -> str:
    """Return 6-digit KRX code from symbol like 005930.KS."""
    code = ticker.strip().upper().split(".")[0]
    return code.zfill(6)


def fetch_krx_history(ticker: str, *, start: str | None = None) -> pd.DataFrame:
    """Fetch OHLCV history from KRX/Naver via FinanceDataReader."""
    import FinanceDataReader as fdr

    code = _krx_code(ticker)
    kwargs: dict = {}
    if start:
        kwargs["start"] = start
    df = fdr.DataReader(code, "KRX", **kwargs)
    if df is None or df.empty:
        raise ValueError(f"KRX 데이터 없음: {code}")
    return df


def fetch_krx_metrics(ticker: str, market: str) -> dict:
    """
    Build metrics dict compatible with StockMetrics from KRX sources.

    Returns keys: name, currency, current_price, market_cap, per, pbr, eps,
    fifty_two_week_high, fifty_two_week_low, symbol
    """
    import FinanceDataReader as fdr

    code = _krx_code(ticker)
    history = fdr.DataReader(code, "KRX")
    if history.empty:
        raise ValueError(f"시세 없음: {code}")

    current_price = float(history["Close"].iloc[-1])
    high_52 = float(history["Close"].tail(252).max()) if len(history) >= 20 else None
    low_52 = float(history["Close"].tail(252).min()) if len(history) >= 20 else None

    name = code
    market_cap = per = pbr = eps = None

    try:
        snap = fdr.SnapReader("KRX")
        row = snap[snap.index.astype(str).str.zfill(6) == code]
        if not row.empty:
            r = row.iloc[0]
            name = str(r.get("Name", r.name if hasattr(r, "name") else code))
            market_cap = safe_to_float(r.get("Marcap"))
            per = safe_to_float(r.get("PER"))
            pbr = safe_to_float(r.get("PBR"))
            eps = safe_to_float(r.get("EPS"))
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
