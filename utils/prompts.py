"""LLM prompt templates for the Investment Coach Agent."""

from __future__ import annotations

from services.stock_data import StockMetrics
from utils.formatters import format_market_cap, format_price, format_ratio
from utils.korean_rules import COACH_SYSTEM_BODY

# ollama_client.ask_gpt()가 KOREAN_ONLY_SYSTEM_LAYER를 자동 주입합니다.
SYSTEM_PROMPT: str = COACH_SYSTEM_BODY

INVESTMENT_PROFILE_GUIDE: dict[str, str] = {
    "보수형": (
        "원금 보존과 안정성을 중시합니다. 변동성·하방 리스크·밸류에이션 부담을 "
        "특히 강조하고, 불확실한 상황에서는 보수적 관찰 관점을 제시하세요."
    ),
    "중립형": (
        "성장 가능성과 리스크를 균형 있게 설명합니다. 긍정·위험 요소를 "
        "비슷한 비중으로 다루고, 중립적 관찰 포인트를 제시하세요."
    ),
    "공격형": (
        "성장성·모멘텀·기회 요인을 상대적으로 더 강조합니다. "
        "다만 변동성과 손실 가능성도 반드시 함께 언급하고, 과도한 낙관은 피하세요."
    ),
}

RESPONSE_FORMAT: str = """\
다음 형식으로 답변해 주세요:

## 1. 현재 상황 요약
(현재가, 추세, 최근 이슈를 3~5문장으로 요약)

## 2. 긍정 요소
(재무, 기술적 지표, 뉴스에서 확인되는 긍정적 요인을 bullet로 정리)

## 3. 위험 요소
(변동성, 밸류에이션, 부정적 뉴스, 기술적 약세 등 위험 요인을 bullet로 정리)

## 4. 투자 포인트
(관찰해야 할 가격·지표·이벤트 등 체크포인트를 bullet로 정리)

## 5. 초보 투자자가 주의할 점
(감정적 매매, 분산투자, 손절·분할매수 등 초보자 관점의 주의사항)

## 6. 종합 의견
(긍정·위험 요소를 균형 있게 종합한 코멘트. 매수/매도/투자 권유 없이 관찰 관점으로 서술)
"""


def get_profile_guide(investment_profile: str) -> str:
    """Return coaching guidance text for the given investment profile."""
    return INVESTMENT_PROFILE_GUIDE.get(
        investment_profile,
        INVESTMENT_PROFILE_GUIDE["중립형"],
    )


def build_financial_context(metrics: StockMetrics) -> str:
    """Format market data metrics for the coach prompt."""
    return (
        f"- 종목명: {metrics.name} ({metrics.ticker})\n"
        f"- 현재가: {format_price(metrics.current_price, metrics.currency)}\n"
        f"- 시가총액: {format_market_cap(metrics.market_cap, metrics.currency)}\n"
        f"- PER: {format_ratio(metrics.per)}\n"
        f"- PBR: {format_ratio(metrics.pbr)}\n"
        f"- EPS: {format_price(metrics.eps, metrics.currency)}\n"
        f"- 52주 최고가: {format_price(metrics.fifty_two_week_high, metrics.currency)}\n"
        f"- 52주 최저가: {format_price(metrics.fifty_two_week_low, metrics.currency)}"
    )
