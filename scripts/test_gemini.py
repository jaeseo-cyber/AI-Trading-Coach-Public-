#!/usr/bin/env python3
"""Gemini API 연결 테스트."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")

from utils.config import GEMINI_API_KEY, GEMINI_MODEL, is_llm_configured


def main() -> int:
    print(f"모델: {GEMINI_MODEL}")
    print(f"API 키 설정: {is_llm_configured()}")

    if not is_llm_configured():
        print("\n[FAIL] GEMINI_API_KEY가 없습니다.")
        print("  https://aistudio.google.com/apikey 에서 무료 키 발급 후")
        print("  .env 파일에 GEMINI_API_KEY=... 추가")
        return 1

    from services.ollama_client import ask_gpt

    print("\nGemini 호출 중...")
    reply = ask_gpt(
        '한국어로 "Gemini 연결 테스트 성공" 한 문장만 출력하세요.',
        temperature=0.1,
    )
    print(f"\n[OK] 응답:\n{reply}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
