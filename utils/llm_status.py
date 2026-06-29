"""User-facing LLM configuration status messages."""

from __future__ import annotations

from utils.config import get_llm_config_error


def render_llm_config_error() -> str:
    """Return a Korean error message for the current LLM config state."""
    code = get_llm_config_error()
    if code is None:
        return ""

    if code == "missing":
        return (
            "**GEMINI_API_KEY가 설정되지 않았습니다.**\n\n"
            "**Streamlit Cloud (배포 URL 사용 시)**\n"
            "1. https://share.streamlit.io/ → 해당 앱 선택\n"
            "2. 우측 **⋮** → **Settings** → **Secrets**\n"
            "3. 아래 내용 붙여넣기 (따옴표·키 값만 본인 것으로 교체):\n\n"
            "```toml\n"
            'GEMINI_API_KEY = "AIzaSy..."\n'
            'GEMINI_MODEL = "gemini-2.5-flash"\n'
            "```\n"
            "4. **Save** → **Reboot app** (또는 1~2분 대기)\n\n"
            "**로컬 실행 시:** 프로젝트 폴더 `.env` 파일에\n"
            "`GEMINI_API_KEY=AIzaSy...` 추가\n\n"
            "무료 키 발급: https://aistudio.google.com/apikey"
        )

    if code == "placeholder":
        return (
            "**GEMINI_API_KEY가 예시 문구 그대로입니다.**\n\n"
            "Secrets에 `your_gemini_api_key` 또는 `본인_Gemini_API_키` 같은 "
            "placeholder가 아닌, Google AI Studio에서 발급한 **실제 API 키**를 넣어 주세요.\n\n"
            "발급: https://aistudio.google.com/apikey"
        )

    if code == "non_ascii":
        return (
            "**GEMINI_API_KEY에 한글이 포함되어 있습니다.**\n\n"
            "Secrets 값에는 한글 설명 없이 **영문 API 키만** 입력하세요."
        )

    if code == "invalid_format":
        return (
            "**GEMINI_API_KEY 형식이 올바르지 않습니다.**\n\n"
            "공백·줄바꿈 없이 키 전체를 한 줄로 입력했는지 확인하세요."
        )

    return (
        f"**GEMINI_API_KEY 설정 오류** ({code})\n\n"
        "Streamlit Secrets를 확인한 뒤 앱을 Reboot 해 주세요."
    )
