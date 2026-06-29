"""Verify AI coach output contains no foreign prose."""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running as: python scripts/verify_korean.py
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agents.schemas import AnalysisRequest
from coordinator import AnalysisCoordinator
from services.korean_localizer import (
    apply_deterministic_patch,
    build_allowed_terms,
    contains_foreign_prose,
    find_foreign_issues,
    localize_coach_analysis,
)


def verify_sample_patch() -> bool:
    """Test deterministic patch on known bad sample."""
    sample = (
        "SK hynix Inc. (000660.KS) 현재는 2,628,000원으로 재무가 좋고, "
        "시가총액 1,865.5조 원이며 PER 6.06입니다. "
        "종목의 52주 최고가와 최저가는分别 2,987,000원과 245,000원입니다. "
        "최근 뉴스에서는 SK hynix와 Samsung이 jointly $518.58 billion를 "
        "투자할 예정이며, DRAM 공급량을 doubling 할計画도 있습니다."
    )
    allowed = build_allowed_terms("000660.KS", "SK hynix Inc.", extra_proper_nouns=["Samsung"])
    patched = apply_deterministic_patch(sample)
    issues = find_foreign_issues(patched, allowed)
    print("--- Deterministic patch ---")
    print(patched[:200], "...")
    print("Issues:", issues)
    return not contains_foreign_prose(patched, allowed)


def verify_full_pipeline(ticker: str = "000660", market: str = "한국 (KRX)") -> bool:
    """Run full coordinator and verify coach output."""
    request = AnalysisRequest(
        ticker=ticker,
        market=market,
        analysis_type="종합 분석",
        investment_profile="중립형",
    )
    print(f"\n--- Full pipeline: {ticker} ---")
    result = AnalysisCoordinator().run(request)

    if not result.coach.success:
        print("Coach failed:", result.coach.error)
        return False

    analysis = result.coach.analysis
    metrics = result.market_data.metrics
    assert metrics is not None

    allowed = build_allowed_terms(
        metrics.ticker,
        metrics.name,
        extra_proper_nouns=[metrics.name, "Samsung", "Micron"],
    )

    issues = find_foreign_issues(analysis, allowed)
    print("Analysis length:", len(analysis))
    print("Foreign issues:", issues if issues else "NONE")
    if issues:
        print("\nSample (first 500 chars):\n", analysis[:500])
    return not issues


def verify_localize_on_sample() -> bool:
    """Test full localize_coach_analysis on bad sample (requires Ollama)."""
    sample = (
        "SK hynix Inc. (000660.KS) 현재는 2,628,000원. "
        "52주 최고가와 최저가는分别 2,987,000원과 245,000원. "
        "Samsung과 jointly $518.58 billion 투자, doubling 할計划."
    )
    print("\n--- Ollama localize ---")
    try:
        result = localize_coach_analysis(
            sample,
            ticker="000660.KS",
            company_name="SK hynix Inc.",
            extra_proper_nouns=["Samsung"],
        )
    except Exception as exc:
        print("Ollama error:", exc)
        return False

    allowed = build_allowed_terms("000660.KS", "SK hynix Inc.", extra_proper_nouns=["Samsung"])
    issues = find_foreign_issues(result, allowed)
    print("Result:", result[:300], "...")
    print("Issues:", issues if issues else "NONE")
    return not issues


if __name__ == "__main__":
    ok = verify_sample_patch()
    print("Deterministic:", "PASS" if ok else "FAIL")

    if "--full" in sys.argv:
        ok = verify_localize_on_sample() and ok
        print("Ollama localize:", "PASS" if ok else "FAIL")
        ok = verify_full_pipeline() and ok
        print("Full pipeline:", "PASS" if ok else "FAIL")

    sys.exit(0 if ok else 1)
