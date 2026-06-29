"""Investment Coach Agent — synthesize agent outputs into coaching analysis."""

from __future__ import annotations

from agents.schemas import (
    AnalysisRequest,
    InvestmentCoachAgentResult,
    MarketDataAgentResult,
    NewsAgentResult,
    TechnicalAnalysisAgentResult,
)
from services.korean_localizer import localize_coach_analysis
from services.ollama_client import OllamaClientError, ask_gpt
from utils.korean_rules import append_korean_user_rules
from utils.prompts import (
    RESPONSE_FORMAT,
    SYSTEM_PROMPT,
    build_financial_context,
    get_profile_guide,
)


class InvestmentCoachAgent:
    """Synthesize multi-agent results into a final coaching report."""

    name = "Investment Coach Agent"

    def run(
        self,
        request: AnalysisRequest,
        market_data: MarketDataAgentResult,
        technical: TechnicalAnalysisAgentResult,
        news: NewsAgentResult,
    ) -> InvestmentCoachAgentResult:
        if market_data.metrics is None:
            return InvestmentCoachAgentResult(
                error=market_data.error or "시장 데이터가 없어 분석을 생성할 수 없습니다.",
            )

        metrics = market_data.metrics
        assert metrics is not None

        question = self._build_question(request, market_data, technical, news)
        extra_names = self._collect_proper_nouns(metrics.name, news)

        try:
            analysis = ask_gpt(question, system_prompt=SYSTEM_PROMPT)
            analysis = localize_coach_analysis(
                analysis,
                ticker=metrics.ticker,
                company_name=metrics.name,
                extra_proper_nouns=extra_names,
            )
        except OllamaClientError as exc:
            return InvestmentCoachAgentResult(error=str(exc))

        return InvestmentCoachAgentResult(analysis=analysis)

    @staticmethod
    def _collect_proper_nouns(company_name: str, news: NewsAgentResult) -> list[str]:
        """Collect proper nouns from company name and news for localization whitelist."""
        names = [company_name]
        if news.success:
            for item in news.items:
                names.append(item.title)
                if item.source:
                    names.append(item.source)
        return names

    def _build_question(
        self,
        request: AnalysisRequest,
        market_data: MarketDataAgentResult,
        technical: TechnicalAnalysisAgentResult,
        news: NewsAgentResult,
    ) -> str:
        """Assemble the user prompt from all agent outputs."""
        metrics = market_data.metrics
        assert metrics is not None

        profile_guide = get_profile_guide(request.investment_profile)
        financial_context = build_financial_context(metrics)

        technical_block = (
            technical.context
            if technical.success
            else (technical.error or "기술적 분석 데이터를 사용할 수 없습니다.")
        )
        news_block = (
            news.summary
            if news.success
            else (news.error or "최근 뉴스 데이터를 사용할 수 없습니다.")
        )

        return append_korean_user_rules(
            f"다음 종목에 대해 투자 코치 관점에서 분석해 주세요.\n\n"
            f"- 종목: {request.ticker}\n"
            f"- 시장: {request.market}\n"
            f"- 분석 유형: {request.analysis_type}\n"
            f"- 투자 성향: {request.investment_profile}\n"
            f"- 성향별 코칭 가이드: {profile_guide}\n\n"
            f"[시장 데이터 — 현재가 및 재무 정보]\n{financial_context}\n\n"
            f"[기술적 분석 — RSI·MACD·이동평균선]\n{technical_block}\n\n"
            f"[최근 뉴스 요약]\n{news_block}\n\n"
            f"{RESPONSE_FORMAT}\n"
            f"분석 유형({request.analysis_type})과 투자 성향({request.investment_profile})에 "
            "맞게 설명의 초점과 강조점을 조절하되, 위 6개 섹션 형식은 반드시 지켜 주세요.\n"
            "- 매수·매도·투자 권유 표현 금지"
        )
