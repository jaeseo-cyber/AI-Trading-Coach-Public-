"""Build interactive stock price charts with Plotly."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from plotly.subplots import make_subplots

from services.stock_data import StockDataError, normalize_ticker
from utils.constants import PRICE_HISTORY_PERIOD

PLOTLY_CHART_CONFIG: dict[str, object] = {
    "scrollZoom": True,
    "displayModeBar": True,
    "modeBarButtonsToAdd": ["zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"],
    "displaylogo": False,
}

# Chart color palette
_CHART_COLORS = {
    "light": {"close": "#2563eb", "volume": "#94a3b8", "paper": "#ffffff", "plot": "#ffffff"},
    "dark": {"close": "#60a5fa", "volume": "#64748b", "paper": "#171717", "plot": "#171717"},
}


def fetch_price_history(
    ticker: str,
    market: str,
    period: str = PRICE_HISTORY_PERIOD,
) -> pd.DataFrame:
    """Fetch historical OHLCV data for charting."""
    symbol = normalize_ticker(ticker, market)

    try:
        return _fetch_history_yfinance(symbol, ticker, period)
    except StockDataError:
        return _fetch_history_fdr(symbol, ticker, market)


def _fetch_history_fdr(symbol: str, ticker: str, market: str) -> pd.DataFrame:
    try:
        from services.fdr_data import fetch_fdr_history

        return fetch_fdr_history(symbol, market)
    except Exception as exc:
        raise StockDataError(
            "차트 데이터 서버에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요."
        ) from exc


def _fetch_history_yfinance(
    symbol: str, ticker: str, period: str = PRICE_HISTORY_PERIOD
) -> pd.DataFrame:
    try:
        history = yf.Ticker(symbol).history(period=period)
    except Exception as exc:
        raise StockDataError(
            "차트 데이터 서버(Yahoo Finance)에 연결하지 못했습니다. "
            "잠시 후 다시 시도해 주세요."
        ) from exc

    if history.empty:
        raise StockDataError(
            f"종목 '{ticker}'의 차트 데이터를 찾을 수 없습니다. "
            "티커와 시장 선택이 올바른지 확인해 주세요."
        )

    return history


def _add_price_traces(fig: go.Figure, df: pd.DataFrame, colors: dict[str, str]) -> None:
    """Add close price and moving average traces to the chart."""
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Close"],
            name="종가",
            line={"color": colors["close"], "width": 2},
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MA20"],
            name="MA20",
            line={"color": "#f59e0b", "width": 1.5, "dash": "dot"},
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MA60"],
            name="MA60",
            line={"color": "#10b981", "width": 1.5, "dash": "dash"},
        ),
        row=1,
        col=1,
    )


def _add_volume_trace(fig: go.Figure, df: pd.DataFrame, colors: dict[str, str]) -> None:
    """Add volume bar trace to the chart."""
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Volume"],
            name="거래량",
            marker={"color": colors["volume"]},
            opacity=0.55,
        ),
        row=2,
        col=1,
    )


def build_price_chart(
    history: pd.DataFrame,
    name: str,
    currency: str,
    *,
    dark_mode: bool = False,
) -> go.Figure:
    """Build a dual-panel price + volume chart with MA20/MA60 overlays."""
    df = history.copy()
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA60"] = df["Close"].rolling(window=60).mean()

    price_title = f"{name} · 최근 1년 주가"
    y_label = "가격 (원)" if currency == "KRW" else f"가격 ({currency})"
    palette = _CHART_COLORS["dark" if dark_mode else "light"]

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.72, 0.28],
        subplot_titles=(price_title, "거래량"),
    )

    _add_price_traces(fig, df, palette)
    _add_volume_trace(fig, df, palette)

    fig.update_layout(
        height=620,
        hovermode="x unified",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.01,
            "xanchor": "left",
            "x": 0,
        },
        margin={"l": 48, "r": 24, "t": 72, "b": 36},
        dragmode="zoom",
        template="plotly_dark" if dark_mode else "plotly_white",
        paper_bgcolor=palette["paper"],
        plot_bgcolor=palette["plot"],
    )
    fig.update_yaxes(title_text=y_label, row=1, col=1)
    fig.update_yaxes(title_text="거래량", row=2, col=1)
    fig.update_xaxes(rangeslider_visible=False, row=1, col=1)
    fig.update_xaxes(rangeslider_visible=False, row=2, col=1)

    return fig
