"""AI Trading Coach - Streamlit application entry point."""

import streamlit as st

from agents.schemas import AnalysisRequest
from coordinator import AnalysisCoordinator
from utils.config import APP_TITLE, GEMINI_MODEL, LLM_PROVIDER, PAGE_ICON, is_llm_configured
from utils.constants import (
    ANALYSIS_TYPE_OPTIONS,
    DEFAULT_INVESTMENT_PROFILE_INDEX,
    INVESTMENT_PROFILE_OPTIONS,
    MARKET_OPTIONS,
)
from utils.ui_components import (
    inject_theme,
    render_coordinator_result,
    render_empty_state,
    render_hero,
    render_search_panel,
    render_section_header,
)


def _init_session_state() -> None:
    """Ensure required session state keys exist."""
    if "show_result" not in st.session_state:
        st.session_state.show_result = False
    if "last_ticker" not in st.session_state:
        st.session_state.last_ticker = ""


def render_sidebar() -> tuple[str, str, str, bool]:
    """Render sidebar settings and return user selections."""
    with st.sidebar:
        st.markdown("## 설정")
        st.divider()

        dark_mode = st.toggle(
            "🌙 다크 모드",
            value=st.session_state.get("dark_mode", False),
            key="dark_mode_toggle",
        )
        st.session_state.dark_mode = dark_mode

        st.divider()
        st.markdown("**시장**")
        market = st.selectbox(
            "시장",
            options=list(MARKET_OPTIONS),
            label_visibility="collapsed",
        )

        st.markdown("**분석 유형**")
        analysis_type = st.radio(
            "분석 유형",
            options=list(ANALYSIS_TYPE_OPTIONS),
            label_visibility="collapsed",
        )

        st.markdown("**투자 성향**")
        investment_profile = st.radio(
            "투자 성향",
            options=list(INVESTMENT_PROFILE_OPTIONS),
            index=DEFAULT_INVESTMENT_PROFILE_INDEX,
            label_visibility="collapsed",
        )

        st.divider()
        st.markdown("##### AI 연결")
        st.caption(f"제공: {LLM_PROVIDER}")
        st.caption(f"모델: {GEMINI_MODEL}")
        if not is_llm_configured():
            st.warning("GEMINI_API_KEY가 없습니다. .env에 키를 설정하세요.")

        st.divider()
        st.markdown("##### 분석 에이전트")
        st.caption("시장 데이터 · 기술 분석 · 뉴스 · 투자 코치")

        st.divider()
        st.caption("AI 트레이딩 코치 v1.0 · Gemini")

    return market, analysis_type, investment_profile, dark_mode


def render_result_section(
    ticker: str,
    show_result: bool,
    market: str,
    analysis_type: str,
    investment_profile: str,
    dark_mode: bool,
) -> None:
    """Run analysis pipeline and render results."""
    render_section_header("분석 대시보드")

    if not show_result:
        render_empty_state()
        return

    if not ticker:
        st.warning("종목 코드 또는 티커를 입력해 주세요.")
        return

    if not is_llm_configured():
        st.error(
            "GEMINI_API_KEY가 설정되지 않았습니다.\n\n"
            "로컬: `.env` 파일에 키 추가\n"
            "Streamlit Cloud: Secrets에 `GEMINI_API_KEY` 설정\n\n"
            "무료 발급: https://aistudio.google.com/apikey"
        )
        return

    request = AnalysisRequest(
        ticker=ticker,
        market=market,
        analysis_type=analysis_type,
        investment_profile=investment_profile,
    )

    with st.spinner(f"{ticker} · 멀티 에이전트 분석 실행 중..."):
        result = AnalysisCoordinator().run(request)

    render_coordinator_result(result, dark_mode=dark_mode)


def main() -> None:
    """Application entry point."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _init_session_state()

    market, analysis_type, investment_profile, dark_mode = render_sidebar()
    theme = "dark" if dark_mode else "light"
    inject_theme(theme)

    render_hero()
    ticker, analyze_clicked = render_search_panel()

    if analyze_clicked:
        st.session_state.show_result = True
        st.session_state.last_ticker = ticker

    render_result_section(
        ticker=st.session_state.last_ticker,
        show_result=st.session_state.show_result,
        market=market,
        analysis_type=analysis_type,
        investment_profile=investment_profile,
        dark_mode=dark_mode,
    )


if __name__ == "__main__":
    main()
