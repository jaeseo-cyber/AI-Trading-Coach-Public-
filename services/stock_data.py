"""Fetch stock market data via yfinance."""

from __future__ import annotations

from dataclasses import dataclass

import yfinance as yf

from utils.constants import SHORT_HISTORY_PERIOD
from utils.formatters import (
    format_market_cap,
    format_price,
    format_ratio,
    safe_to_float,
)

# Re-export formatters for backward compatibility
__all__ = [
    "StockDataError",
    "StockMetrics",
    "fetch_stock_metrics",
    "format_market_cap",
    "format_price",
    "format_ratio",
    "normalize_ticker",
]


class StockDataError(Exception):
    """Raised when stock data cannot be retrieved."""


@dataclass(frozen=True)
class StockMetrics:
    """Normalized stock metrics for display."""

    ticker: str
    name: str
    currency: str
    current_price: float | None
    market_cap: float | None
    per: float | None
    pbr: float | None
    eps: float | None
    fifty_two_week_high: float | None
    fifty_two_week_low: float | None


def normalize_ticker(ticker: str, market: str) -> str:
    """Convert user input to a yfinance-compatible symbol."""
    symbol = ticker.strip().upper()
    if not symbol:
        raise StockDataError("종목 코드 또는 티커를 입력해 주세요.")

    if market.startswith("한국"):
        if symbol.endswith((".KS", ".KQ")):
            return symbol
        if symbol.isdigit():
            return f"{symbol.zfill(6)}.KS"
        raise StockDataError(
            "한국 주식은 6자리 종목 코드로 입력해 주세요. (예: 005930, 000660)"
        )

    return symbol


def _resolve_current_price(stock: yf.Ticker, info: dict, ticker: str) -> float:
    """Extract the latest price from ticker info or recent history."""
    current_price = safe_to_float(
        info.get("currentPrice")
        or info.get("regularMarketPrice")
        or info.get("previousClose")
    )

    if current_price is not None:
        return current_price

    history = stock.history(period=SHORT_HISTORY_PERIOD)
    if not history.empty:
        fallback = safe_to_float(history["Close"].iloc[-1])
        if fallback is not None:
            return fallback

    raise StockDataError(
        f"종목 '{ticker}'의 시세 정보를 불러올 수 없습니다. "
        "티커를 확인하거나 잠시 후 다시 시도해 주세요."
    )


def fetch_stock_metrics(ticker: str, market: str) -> StockMetrics:
    """Fetch key metrics for a ticker from Yahoo Finance."""
    symbol = normalize_ticker(ticker, market)

    try:
        stock = yf.Ticker(symbol)
        info = stock.info or {}
    except Exception as exc:
        raise StockDataError(
            "네트워크 오류로 종목 데이터를 가져오지 못했습니다. "
            "인터넷 연결을 확인한 뒤 다시 시도해 주세요."
        ) from exc

    if not info or (
        info.get("regularMarketPrice") is None and info.get("currentPrice") is None
    ):
        history = stock.history(period=SHORT_HISTORY_PERIOD)
        if history.empty:
            raise StockDataError(
                f"종목 '{ticker}'의 데이터를 찾을 수 없습니다. "
                "티커와 시장 선택이 올바른지 확인해 주세요."
            )

    current_price = _resolve_current_price(stock, info, ticker)

    return StockMetrics(
        ticker=symbol,
        name=str(info.get("longName") or info.get("shortName") or ticker),
        currency=str(
            info.get("currency") or ("KRW" if market.startswith("한국") else "USD")
        ),
        current_price=current_price,
        market_cap=safe_to_float(info.get("marketCap")),
        per=safe_to_float(info.get("trailingPE") or info.get("forwardPE")),
        pbr=safe_to_float(info.get("priceToBook")),
        eps=safe_to_float(info.get("trailingEps")),
        fifty_two_week_high=safe_to_float(info.get("fiftyTwoWeekHigh")),
        fifty_two_week_low=safe_to_float(info.get("fiftyTwoWeekLow")),
    )
