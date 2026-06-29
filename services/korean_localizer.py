"""Detect and localize foreign-language text to Korean."""

from __future__ import annotations

import re

from services.ollama_client import OllamaClientError, ask_gpt

# ── Detection ──────────────────────────────────────────────────────────────────
_KOREAN_RE = re.compile(r"[가-힣]")
# Chinese / Japanese Han (not Korean Hangul)
_CJK_HAN_RE = re.compile(r"[\u4e00-\u9fff]")
_CJK_JP_RE = re.compile(r"[\u3040-\u30ff]")
_ENGLISH_WORD_RE = re.compile(r"[A-Za-z]{2,}")
_VIETNAMESE_LATIN_RE = re.compile(
    r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]",
    re.IGNORECASE,
)
_HYPHEN_ENGLISH_RE = re.compile(r"-[a-zA-Z][a-zA-Z\s]*")
_DOLLAR_AMOUNT_RE = re.compile(
    r"\$\s*([\d,]+(?:\.\d+)?)\s*(billion|million|trillion)?",
    re.IGNORECASE,
)
_ENGLISH_BEFORE_HANGUL_RE = re.compile(r"[A-Za-z]{2,}(?=[가-힣])")

_MAX_REWRITE_ATTEMPTS = 6

_BASE_ALLOWED: frozenset[str] = frozenset({
    "AI", "BB", "CEO", "CFO", "DRAM", "EPS", "ETF", "HBM", "INC", "IPO",
    "KRX", "KRW", "KS", "KQ", "LTD", "MACD", "MA", "MA20", "MA60",
    "NASDAQ", "NYSE", "PBR", "PER", "RSI", "SK", "USD", "US", "UK", "EU",
    "Samsung", "SAMSUNG", "Apple", "APPLE", "Google", "GOOG", "GOOGL",
    "hynix", "Hynix", "HYNIX", "Micron", "MICRON",
    "HBM", "HBM3", "HBM4", "HBM4E", "AI",
})

# Chinese/Japanese characters → Korean (deterministic)
_CJK_REPLACEMENTS: dict[str, str] = {
    "分别": "각각",
    "计划": "계획",
    "計划": "계획",
    "以及": "및",
    "与": "와",
    "为": "를",
    "将": "할",
    "预计": "예상",
    "增长": "성장",
    "投资": "투자",
    "公司": "회사",
    "市场": "시장",
    "风险": "위험",
    "机会": "기회",
    "分析": "분석",
    "总结": "요약",
    "目前": "현재",
    "同时": "동시에",
    "可能": "가능",
    "进行": "진행",
    "提高": "향상",
    "下降": "하락",
    "上升": "상승",
}

_ENGLISH_PHRASE_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (r"Moving Average", "이동평균"),
    (r"moving average", "이동평균"),
    (r"Memory Type", "메모리 유형"),
    (r"memory type", "메모리 유형"),
    (r"signal line", "시그널 선"),
    (r"Signal line", "시그널 선"),
    (r"MACD Signal", "MACD 시그널"),
    (r"MACD signal", "MACD 시그널"),
    (r"risk management", "리스크 관리"),
    (r"Risk management", "리스크 관리"),
    (r"balancing act", "균형 유지"),
    (r"Balancing act", "균형 유지"),
    (r"growth potential", "성장 가능성"),
    (r"Growth potential", "성장 가능성"),
    (r"diversify your portfolio", "포트폴리오를 분산"),
    (r"strategies to", "전략으로"),
    (r"strategysto", "전략으로"),
    (r"AI oriented", "AI 중심"),
    (r"next generation", "차세대"),
)

# English → Korean (longer phrases first when applied via sorted keys)
_ENGLISH_REPLACEMENTS: dict[str, str] = {
    "jointly": "공동으로",
    "respectively": "각각",
    "doubling": "두 배로 확대",
    "doubled": "두 배로 늘린",
    "double": "두 배",
    "however": "다만",
    "therefore": "따라서",
    "shortage": "부족",
    "SHORTAGE": "공급 부족",
    "balanced": "균형 잡힌",
    "balancing": "균형",
    "potential": "가능성",
    "growth": "성장",
    "recommend": "권장",
    "recommended": "권장",
    "investment": "투자",
    "invest": "투자",
    "expected": "예상",
    "forecast": "전망",
    "supply": "공급",
    "demand": "수요",
    "increase": "증가",
    "decrease": "감소",
    "currently": "현재",
    "recent": "최근",
    "news": "뉴스",
    "plan": "계획",
    "planned": "계획",
    "planning": "계획",
    "together": "함께",
    "tăng": "증가",
    "Tăng": "증가",
    "biến": "변",
    "bullish": "강세",
    "bearish": "약세",
    "overbought": "과매수",
    "oversold": "과매도",
    "risk": "위험",
    "act": "조치",
    "moving": "이동",
    "average": "평균",
    "Moving": "이동",
    "Average": "평균",
    "below": "이하",
    "above": "이상",
    "signal": "시그널",
    "Signal": "시그널",
    "line": "선",
    "days": "일",
    "day": "일",
    "situation": "상황",
    "momentum": "모멘텀",
    "trend": "추세",
    "price": "가격",
    "market": "시장",
    "stock": "주식",
    "volatility": "변동성",
    "valuation": "밸류에이션",
    "event": "이벤트",
    "events": "이벤트",
    "indicator": "지표",
    "indicators": "지표",
    "financial": "재무",
    "technical": "기술적",
    "competition": "경쟁",
    "competitive": "경쟁",
    "instability": "불안정",
    "billion": "억",
    "million": "백만",
    "trillion": "조",
    "Memory": "메모리",
    "memory": "메모리",
    "Type": "유형",
    "type": "유형",
    "glitch": "결함",
    "glich": "결함",
    "performance": "성능",
    "delivery": "출하",
    "export": "수출",
    "development": "개발",
    "competition": "경쟁",
    "share": "점유",
    "cost": "비용",
    "profit": "이익",
    "loss": "손실",
    "Korea": "한국",
    "Korean": "한국의",
    "based": "기반",
    "chip": "칩",
    "chips": "칩",
    "customer": "고객",
    "customers": "고객",
    "sample": "샘플",
    "samples": "샘플",
    "milestone": "이정표",
    "warning": "경고",
    "warnings": "경고",
    "investor": "투자자",
    "investors": "투자자",
    "market": "시장",
    "markets": "시장",
    "sector": "섹터",
    "industry": "산업",
    "product": "제품",
    "products": "제품",
    "semiconductor": "반도체",
    "semiconductors": "반도체",
    "management": "관리",
    "Management": "관리",
    "gain": "수익",
    "gains": "수익",
    "new": "새로운",
    "diversify": "분산",
    "portfolio": "포트폴리오",
    "your": "",
    "consider": "고려",
    "consideration": "고려",
    "strategy": "전략",
    "strategies": "전략",
    "strategysto": "전략으로",
    "oriented": "중심",
    "next": "차세대",
    "shipments": "출하",
    "shipment": "출하",
    "major": "주요",
    "competitor": "경쟁사",
    "competitors": "경쟁사",
    "fluctuation": "변동",
    "impact": "영향",
    "carefully": "신중히",
    "so": "",
    "complete": "완료",
    "decision": "판단",
    "long": "장기",
    "focusing": "집중",
    "diversification": "분산",
    "according": "에 따라",
    "company": "회사",
    "strong": "강한",
    "ilio": "",
}

_TOKEN_GLUED_REPLACEMENTS: dict[str, str] = {
    "SHORTAGE가": "공급 부족이",
    "SHORTAGE": "공급 부족",
    "shortage": "부족",
    "tăng할": "증가할",
    "tăng": "증가",
    "biến동성": "변동성",
    "biến": "변",
    "Korea를": "한국을",
    "Korea을": "한국을",
    "jointly": "공동으로",
    "doubling 할": "두 배로 확대할",
    "doubling할": "두 배로 늘리는",
    "doubling": "두 배로 확대",
    "分别": "각각",
    "할計划도": "할 계획도",
    "할計划": "할 계획",
    "計划도": "계획도",
    "计划도": "계획도",
    "計划": "계획",
    "计划": "계획",
}

_REWRITE_SYSTEM = """\
당신은 한국어 금융 콘텐츠 교정 전문가입니다.
입력된 투자 분석 글을 한국어로만 다시 작성합니다.

★ 절대 규칙 (위반 금지) ★
1. 모든 문장은 한국어(한글)로만 작성합니다.
2. 영어 단어를 문장에 넣지 마세요.
   금지: jointly, doubling, billion, plan, risk, growth, expected 등
   허용: SK hynix, Samsung, 000660.KS, PER, PBR, EPS, RSI, MACD, DRAM, HBM
3. 중국어·일본어 한자를 절대 사용하지 마세요.
   금지: 分别, 计划, 計划, 以及 등 → 각각, 계획, 및 등 한글로
4. 달러 금액은 한국어로: "$518.58 billion" → "약 5185억 달러"
5. 섹션 제목 6개(## 1. ~ ## 6.) 형식과 bullet(-) 구조 유지
6. 매수·매도·투자 권유 금지
7. 분석 본문만 출력 (다른 설명 없음)
"""

_FINAL_SYSTEM = """\
아래 텍스트에서 영어 단어와 중국어·일본어 한자를 모두 제거하고
의미를 유지한 채 100% 한글 문장으로만 다시 작성하세요.
회사명(SK hynix, Samsung)·티커·PER/PBR/EPS/RSI/MACD/DRAM/HBM만 라틴 문자 허용.
"""


def build_allowed_terms(
    ticker: str,
    company_name: str,
    *,
    extra_proper_nouns: list[str] | None = None,
) -> set[str]:
    """Build Latin tokens allowed to remain in output."""
    allowed = set(_BASE_ALLOWED)
    allowed.add(ticker.strip().upper())

    for name in [company_name, *(extra_proper_nouns or [])]:
        for token in _ENGLISH_WORD_RE.findall(name):
            allowed.add(token)
            allowed.add(token.upper())
            allowed.add(token.lower())

    return allowed


def korean_ratio(text: str) -> float:
    letters = re.findall(r"[a-zA-Z가-힣\u4e00-\u9fff\u3040-\u30ff]", text)
    if not letters:
        return 1.0
    return len(_KOREAN_RE.findall(text)) / len(letters)


def find_foreign_issues(text: str, allowed: set[str] | None = None) -> list[str]:
    """Return a list of foreign fragments detected in text."""
    allowed = allowed or set(_BASE_ALLOWED)
    allowed_lower = {t.lower() for t in allowed}
    issues: list[str] = []

    for match in _CJK_HAN_RE.finditer(text):
        issues.append(f"한자:{match.group()}")
    for match in _CJK_JP_RE.finditer(text):
        issues.append(f"일본어:{match.group()}")

    if _VIETNAMESE_LATIN_RE.search(text):
        issues.append("베트남어")

    for word in _ENGLISH_WORD_RE.findall(text):
        upper, lower = word.upper(), word.lower()
        if upper in allowed or lower in allowed_lower or word in allowed:
            continue
        issues.append(f"영어:{word}")

    return issues


def contains_foreign_prose(text: str, allowed: set[str] | None = None) -> bool:
    return bool(find_foreign_issues(text, allowed))


def _replace_dollar_amounts(text: str) -> str:
    """Convert $X billion/million patterns to Korean."""

    def _convert(match: re.Match[str]) -> str:
        raw_num = match.group(1).replace(",", "")
        unit = (match.group(2) or "").lower()
        try:
            value = float(raw_num)
        except ValueError:
            return match.group(0)

        if unit == "billion":
            eok = value * 10
            return f"약 {eok:,.1f}억 달러"
        if unit == "trillion":
            return f"약 {value:,.1f}조 달러"
        if unit == "million":
            return f"약 {value:,.1f}백만 달러"
        return f"약 {raw_num}달러"

    return _DOLLAR_AMOUNT_RE.sub(_convert, text)


def apply_deterministic_patch(text: str) -> str:
    """Apply dictionary-based CJK/English replacements without LLM."""
    result = _replace_dollar_amounts(text)

    for src, dst in sorted(_TOKEN_GLUED_REPLACEMENTS.items(), key=lambda x: -len(x[0])):
        result = result.replace(src, dst)

    for src, dst in sorted(_CJK_REPLACEMENTS.items(), key=lambda x: -len(x[0])):
        result = result.replace(src, dst)

    for pattern, replacement in _ENGLISH_PHRASE_REPLACEMENTS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    for src, dst in sorted(_ENGLISH_REPLACEMENTS.items(), key=lambda x: -len(x[0])):
        result = re.sub(rf"\b{re.escape(src)}\b", dst, result, flags=re.IGNORECASE)

    # English glued directly before Hangul: "doubling할" → already in glued dict;
    # generic fallback for remaining patterns
    def _replace_glued(match: re.Match[str]) -> str:
        word = match.group(0)
        lower = word.lower()
        if lower in _ENGLISH_REPLACEMENTS:
            return _ENGLISH_REPLACEMENTS[lower]
        return word

    result = _ENGLISH_BEFORE_HANGUL_RE.sub(_replace_glued, result)
    result = _HYPHEN_ENGLISH_RE.sub(" ", result)
    result = re.sub(r"\s{2,}", " ", result)

    # Remove any remaining CJK Han characters (Chinese/Japanese)
    if _CJK_HAN_RE.search(result):
        for src, dst in sorted(_CJK_REPLACEMENTS.items(), key=lambda x: -len(x[0])):
            result = result.replace(src, dst)
        result = _CJK_HAN_RE.sub("", result)

    return result.strip()


def _scrub_remaining_foreign(text: str, allowed: set[str]) -> str:
    """Apply dictionary replacements; do not delete unknown words (avoids broken sentences)."""
    result = apply_deterministic_patch(text)

    for pattern, replacement in _ENGLISH_PHRASE_REPLACEMENTS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    for src, dst in sorted(_ENGLISH_REPLACEMENTS.items(), key=lambda x: -len(x[0])):
        result = re.sub(rf"\b{re.escape(src)}\b", dst, result, flags=re.IGNORECASE)

    # Strip Chinese / Japanese Han only (never Korean Hangul)
    for src, dst in sorted(_CJK_REPLACEMENTS.items(), key=lambda x: -len(x[0])):
        result = result.replace(src, dst)
    result = _CJK_HAN_RE.sub("", result)
    result = _CJK_JP_RE.sub("", result)

    # Vietnamese diacritics → remove accent letters only when not part of allowed token
    result = result.replace("biến", "변").replace("tăng", "증가")

    result = re.sub(r"\s{2,}", " ", result)
    return result.strip()


def localize_coach_analysis(
    text: str,
    *,
    ticker: str,
    company_name: str,
    extra_proper_nouns: list[str] | None = None,
) -> str:
    """
    Ensure coach analysis is pure Korean prose.

    Applies deterministic patches, then Ollama rewrites until clean or max attempts.
    """
    if not text.strip():
        return text

    allowed = build_allowed_terms(
        ticker, company_name, extra_proper_nouns=extra_proper_nouns
    )
    current = apply_deterministic_patch(text)

    try:
        for attempt in range(_MAX_REWRITE_ATTEMPTS):
            current = _scrub_remaining_foreign(current, allowed)
            if not contains_foreign_prose(current, allowed):
                return current

            current = _rewrite_via_ollama(
                current,
                ticker=ticker,
                company_name=company_name,
                strict=attempt > 0,
            )

        current = _scrub_remaining_foreign(current, allowed)
        if contains_foreign_prose(current, allowed):
            current = _final_korean_pass(
                current, ticker=ticker, company_name=company_name
            )
            current = _scrub_remaining_foreign(current, allowed)

        for _ in range(3):
            if not contains_foreign_prose(current, allowed):
                break
            current = _rewrite_via_ollama(
                current,
                ticker=ticker,
                company_name=company_name,
                strict=True,
            )
            current = _scrub_remaining_foreign(current, allowed)

        return current
    except OllamaClientError:
        return _scrub_remaining_foreign(
            apply_deterministic_patch(text), allowed
        )


def _rewrite_via_ollama(
    text: str,
    *,
    ticker: str,
    company_name: str,
    strict: bool = False,
) -> str:
    issues = find_foreign_issues(text)
    issue_note = ""
    if issues:
        issue_note = (
            f"\n\n★ 반드시 제거할 외국어: {', '.join(issues[:12])}"
            + (" ..." if len(issues) > 12 else "")
        )

    strict_note = (
        "\n\n⚠ 이전 출력에 영어·한자가 남아 있었습니다. "
        "이번에는 한글만 사용하세요. 分别→각각, 計划→계획, jointly→공동으로, doubling→두 배."
        if strict
        else ""
    )

    prompt = (
        "다음 투자 코치 분석을 자연스러운 한국어(한글)로 전면 재작성하세요.\n"
        "영어 단어와 중국어·일본어 한자를 모두 한글로 바꾸세요.\n\n"
        f"- 종목: {company_name} ({ticker})\n"
        f"- 허용 라틴: 회사명, 티커, PER, PBR, EPS, RSI, MACD, DRAM, HBM, Samsung\n"
        f"{issue_note}{strict_note}\n\n"
        f"--- 초안 ---\n{text}\n--- 초안 끝 ---"
    )

    result = ask_gpt(
        prompt,
        system_prompt=_REWRITE_SYSTEM,
        temperature=0.1,
    ).strip()
    return result if result else text


def _final_korean_pass(text: str, *, ticker: str, company_name: str) -> str:
    """Last-resort pass: Korean-only rewrite."""
    prompt = (
        f"종목: {company_name} ({ticker})\n\n"
        f"다음 텍스트를 한글만 사용해 다시 작성하세요:\n\n{text}"
    )
    result = ask_gpt(
        prompt,
        system_prompt=_FINAL_SYSTEM,
        temperature=0.1,
    ).strip()
    return result if result else text


def ensure_korean_text(
    text: str,
    *,
    ticker: str = "",
    company_name: str = "",
    extra_proper_nouns: list[str] | None = None,
    use_llm: bool = True,
    max_attempts: int = 3,
) -> str:
    """
    모든 에이전트 출력을 한국어 단일 언어로 정규화.

    1) 사전 기반 치환 (deterministic)
    2) 외국어 잔존 시 Ollama 재작성 (선택)
    3) 최종 검증 및 스크럽
    """
    if not text.strip():
        return text

    if ticker or company_name:
        allowed = build_allowed_terms(
            ticker, company_name, extra_proper_nouns=extra_proper_nouns
        )
    else:
        allowed = build_allowed_terms("", "", extra_proper_nouns=extra_proper_nouns)

    current = apply_deterministic_patch(text)
    if not contains_foreign_prose(current, allowed):
        return current

    if not use_llm:
        return _scrub_remaining_foreign(current, allowed)

    try:
        for attempt in range(max_attempts):
            current = _scrub_remaining_foreign(current, allowed)
            if not contains_foreign_prose(current, allowed):
                return current

            label = company_name or ticker or "텍스트"
            current = _rewrite_via_ollama(
                current,
                ticker=ticker or "N/A",
                company_name=label,
                strict=attempt > 0,
            )

        current = _scrub_remaining_foreign(current, allowed)
        if contains_foreign_prose(current, allowed):
            current = _final_korean_pass(
                current,
                ticker=ticker or "N/A",
                company_name=company_name or "텍스트",
            )
            current = _scrub_remaining_foreign(current, allowed)

        return current
    except OllamaClientError:
        return _scrub_remaining_foreign(apply_deterministic_patch(text), allowed)
