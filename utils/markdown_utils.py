"""Lightweight Markdown → HTML conversion for AI response cards."""

from __future__ import annotations

import html
import re

_CODE_FENCE_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_code_and_html(text: str) -> str:
    """Remove code blocks, inline code markers, and raw HTML from display text."""
    text = _CODE_FENCE_RE.sub("", text)
    text = _INLINE_CODE_RE.sub(r"\1", text)
    text = _HTML_TAG_RE.sub("", text)
    return text


def _format_inline(text: str) -> str:
    """Apply bold formatting and escape HTML for safe rendering."""
    parts = _BOLD_RE.split(text)
    result: list[str] = []
    for index, part in enumerate(parts):
        if index % 2 == 1:
            result.append(f"<strong>{html.escape(part)}</strong>")
        else:
            result.append(html.escape(part))
    return "".join(result)


def markdown_to_html(text: str) -> str:
    """
    Convert Markdown headings, lists, and paragraphs to HTML.

    Code blocks and inline code are stripped so raw code does not appear in the UI.
    """
    text = _strip_code_and_html(text)
    lines = text.split("\n")
    parts: list[str] = []
    in_list = False
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        if stripped.startswith("## "):
            if in_list:
                parts.append("</ul>")
                in_list = False
            heading = stripped[3:].lstrip("#").strip()
            parts.append(f"<h2>{_format_inline(heading)}</h2>")

        elif stripped.startswith(("# ", "### ")):
            continue

        elif stripped.startswith(("- ", "* ")):
            if not in_list:
                parts.append("<ul>")
                in_list = True
            parts.append(f"<li>{_format_inline(stripped[2:])}</li>")

        elif stripped:
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append(f"<p>{_format_inline(stripped)}</p>")

        else:
            if in_list:
                parts.append("</ul>")
                in_list = False

    if in_list:
        parts.append("</ul>")

    return "\n".join(parts)
