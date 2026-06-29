"""Reusable UI components — metric cards, charts, news, AI opinion."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from agents.schemas import CoordinatorResult
from services.news import NewsItem
from services.stock_chart import PLOTLY_CHART_CONFIG, build_price_chart
from services.stock_data import StockMetrics
from services.technical_analysis import TechnicalAnalysisResult
from utils.config import APP_TITLE, GEMINI_MODEL, LLM_PROVIDER, PAGE_ICON, PROJECT_SUBTITLE, is_llm_configured
from utils.constants import CHART_COLUMN_RATIO, TECH_COLUMN_RATIO
from utils.formatters import format_indicator, format_market_cap, format_price, format_ratio
from utils.html_builder import (
    empty_state,
    metric_card,
    metric_grid,
    news_card,
    panel_card,
    section_header,
)
from utils.labels import (
    TECH_LABEL_BB_LOWER,
    TECH_LABEL_BB_MID,
    TECH_LABEL_BB_UPPER,
    TECH_LABEL_CLOSE,
    TECH_LABEL_MACD,
    TECH_LABEL_MA20,
    TECH_LABEL_MA60,
    TECH_LABEL_RSI,
    TECH_LABEL_SIGNAL,
    localize_news_source,
)
from utils.markdown_utils import markdown_to_html


def inject_theme(theme: str) -> None:
    """Inject theme-aware CSS into the Streamlit page."""
    from utils.styles import build_app_css

    st.markdown(build_app_css(theme), unsafe_allow_html=True)


def render_hero() -> None:
    """Render the top hero banner."""
    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-badge">멀티 에이전트 · 프로페셔널 대시보드</div>
            <h1>{PAGE_ICON} {APP_TITLE}</h1>
            <p>{PROJECT_SUBTITLE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, subtitle: str = "") -> None:
    """Render a section title with optional subtitle."""
    st.markdown(section_header(title, subtitle), unsafe_allow_html=True)


def render_search_panel() -> tuple[str, bool]:
    """Render ticker search input and analyze button."""
    render_section_header("종목 검색", "티커를 입력하고 분석하기를 실행하세요")

    with st.container(border=True):
        col_input, col_btn = st.columns([5, 1], gap="small")
        with col_input:
            ticker = st.text_input(
                "종목 입력",
                placeholder="005930 · AAPL · TSLA",
                label_visibility="collapsed",
                key="ticker_input",
            )
        with col_btn:
            st.markdown("<div style='margin-top:0.25rem'></div>", unsafe_allow_html=True)
            clicked = st.button("분석하기", type="primary", use_container_width=True)

    return ticker.strip(), clicked


def render_metric_cards(metrics: StockMetrics) -> None:
    """Render market data metric cards."""
    render_section_header("시장 데이터", f"{metrics.name} · {metrics.ticker}")
    st.markdown(
        f"""
        <div class="ticker-header">
            <span class="symbol">{html.escape(metrics.ticker)}</span>
            <span class="name">{html.escape(metrics.name)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    card_defs: list[tuple[str, str, str]] = [
        ("현재가", format_price(metrics.current_price, metrics.currency), "최근 종가"),
        ("시가총액", format_market_cap(metrics.market_cap, metrics.currency), "시장 규모"),
        ("PER", format_ratio(metrics.per), "주가수익비율"),
        ("PBR", format_ratio(metrics.pbr), "주가순자산비율"),
        ("EPS", format_price(metrics.eps, metrics.currency), "주당순이익"),
        ("52주 최고", format_price(metrics.fifty_two_week_high, metrics.currency), "52주"),
        ("52주 최저", format_price(metrics.fifty_two_week_low, metrics.currency), "52주"),
    ]
    cards = [metric_card(label, value, sub) for label, value, sub in card_defs]
    st.markdown(metric_grid(cards), unsafe_allow_html=True)


def render_chart_panel(
    history: pd.DataFrame,
    metrics: StockMetrics,
    *,
    dark_mode: bool = False,
) -> None:
    """Render the interactive price chart."""
    render_section_header("주가 차트", "최근 1년 · 종가 · 20·60일 이동평균 · 거래량")
    st.markdown(
        """
        <div class="chart-panel">
            <div class="chart-caption">
                드래그 확대 · 더블클릭 초기화 · 스크롤 줌
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    fig = build_price_chart(history, metrics.name, metrics.currency, dark_mode=dark_mode)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CHART_CONFIG)


def _pill_class(label: str) -> str:
    """Map trend/momentum labels to CSS pill classes."""
    if label in ("상승추세", "과매도"):
        return "bullish" if label == "상승추세" else "bearish"
    if label in ("하락추세", "과매수"):
        return "bearish" if label == "하락추세" else "bullish"
    return "neutral"


def render_technical_panel(
    result: TechnicalAnalysisResult,
    *,
    ma20: float | None = None,
    ma60: float | None = None,
    ma_analysis: str = "",
) -> None:
    """Render technical analysis indicators and interpretation."""
    indicators = result.indicators
    render_section_header("기술적 분석", "RSI · MACD · 볼린저 밴드 · 이동평균선")

    pills = [
        (result.trend_label, _pill_class(result.trend_label)),
        (result.momentum_label, _pill_class(result.momentum_label)),
    ]
    pill_html = '<div class="insight-row">' + "".join(
        f'<span class="insight-pill {cls}">{html.escape(lbl)}</span>'
        for lbl, cls in pills
    ) + "</div>"
    st.markdown(pill_html, unsafe_allow_html=True)

    tech_cards: list[tuple[str, str]] = [
        (TECH_LABEL_RSI, format_indicator(indicators.rsi)),
        (TECH_LABEL_MACD, format_indicator(indicators.macd)),
        (TECH_LABEL_SIGNAL, format_indicator(indicators.signal)),
        (TECH_LABEL_CLOSE, format_indicator(indicators.close)),
        (TECH_LABEL_BB_UPPER, format_indicator(indicators.bb_upper)),
        (TECH_LABEL_BB_MID, format_indicator(indicators.bb_middle)),
        (TECH_LABEL_BB_LOWER, format_indicator(indicators.bb_lower)),
    ]
    if ma20 is not None:
        tech_cards.append((TECH_LABEL_MA20, format_indicator(ma20)))
    if ma60 is not None:
        tech_cards.append((TECH_LABEL_MA60, format_indicator(ma60)))

    cards = [metric_card(label, value) for label, value in tech_cards]
    st.markdown(metric_grid(cards), unsafe_allow_html=True)

    st.markdown(panel_card("추세 해석", result.trend_explanation), unsafe_allow_html=True)
    if ma_analysis:
        st.markdown(panel_card("이동평균선", ma_analysis), unsafe_allow_html=True)


def render_news_cards(
    news_items: list[NewsItem] | None,
    source: str | None = None,
    summary: str | None = None,
) -> None:
    """Render news digest and article cards."""
    render_section_header("최신 뉴스", "최근 기업 관련 뉴스 · 최대 5건")

    if not news_items:
        st.markdown(
            empty_state("관련 뉴스를 불러오지 못했습니다.", icon="📰"),
            unsafe_allow_html=True,
        )
        return

    if source:
        st.caption(f"출처: {localize_news_source(source)}")

    if summary:
        st.markdown(
            panel_card("뉴스 요약", summary, body_class="body-text pre-line"),
            unsafe_allow_html=True,
        )

    cards = []
    for item in news_items:
        meta = " · ".join(
            p for p in (localize_news_source(item.source), item.published_at) if p
        )
        cards.append(news_card(item.title, meta, item.summary, item.url))

    st.markdown(f'<div class="news-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_ai_opinion_card(result: CoordinatorResult) -> None:
    """Render the AI Investment Coach analysis card."""
    coach = result.coach
    req = result.request

    if not coach.success:
        st.error(coach.error or "AI 분석을 생성하지 못했습니다.")
        return

    render_section_header(
        "AI 투자 코치",
        f"모델: {GEMINI_MODEL} · 멀티 에이전트 종합 분석",
    )

    body_html = markdown_to_html(coach.analysis)
    meta = (
        f"{html.escape(req.ticker)} · {html.escape(req.market)} · "
        f"{html.escape(req.analysis_type)} · {html.escape(req.investment_profile)}"
    )

    st.markdown(
        f"""
        <div class="ai-card">
            <div class="ai-card-header">
                <div class="ai-avatar">🤖</div>
                <div>
                    <p class="title">투자 코치 AI</p>
                    <p class="subtitle">{meta}</p>
                </div>
            </div>
            <div class="ai-card-body">{body_html}</div>
            <div class="ai-disclaimer">
                ⚠ 본 내용은 투자 권유가 아닌 정보 제공 목적이며,
                최종 투자 판단과 책임은 사용자에게 있습니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state() -> None:
    """Render placeholder when no analysis has been run."""
    st.markdown(
        """
        <div class="empty-state">
            <div class="icon">📊</div>
            <strong>분석 결과가 여기에 표시됩니다</strong><br>
            종목 코드를 입력하고 분석하기를 실행하세요.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_coordinator_result(
    result: CoordinatorResult,
    *,
    dark_mode: bool = False,
) -> None:
    """Render the full analysis dashboard from coordinator output."""
    market_data = result.market_data
    technical = result.technical
    news = result.news

    if not market_data.success or market_data.metrics is None:
        st.error(market_data.error or "종목 데이터를 불러오지 못했습니다.")
        return

    metrics = market_data.metrics
    render_metric_cards(metrics)

    col_chart, col_tech = st.columns([CHART_COLUMN_RATIO, TECH_COLUMN_RATIO], gap="medium")

    with col_chart:
        if market_data.history is not None and not market_data.history.empty:
            render_chart_panel(market_data.history, metrics, dark_mode=dark_mode)
        elif market_data.error:
            st.warning(market_data.error)

    with col_tech:
        if technical.success and technical.result is not None:
            render_technical_panel(
                technical.result,
                ma20=technical.ma20,
                ma60=technical.ma60,
                ma_analysis=technical.ma_analysis,
            )
        elif technical.error:
            st.warning(technical.error)

    render_news_cards(
        news.items,
        news.source,
        news.summary if news.success else None,
    )
    render_ai_opinion_card(result)
