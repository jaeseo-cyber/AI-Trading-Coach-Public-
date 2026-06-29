"""HTML builders for Streamlit UI components."""

from __future__ import annotations

import html


def section_header(title: str, subtitle: str = "") -> str:
    """Build a section header block."""
    sub_html = f"<p>{html.escape(subtitle)}</p>" if subtitle else ""
    return (
        f'<div class="section-header">'
        f"<h2>{html.escape(title)}</h2>{sub_html}"
        f"</div>"
    )


def metric_card(label: str, value: str, sub: str = "") -> str:
    """Build a single metric card."""
    sub_html = f'<div class="sub">{html.escape(sub)}</div>' if sub else ""
    return (
        f'<div class="metric-card">'
        f'<div class="label">{html.escape(label)}</div>'
        f'<div class="value">{html.escape(value)}</div>'
        f"{sub_html}"
        f"</div>"
    )


def metric_grid(cards: list[str]) -> str:
    """Wrap metric cards in a responsive grid."""
    return f'<div class="metric-grid">{"".join(cards)}</div>'


def panel_card(title: str, body: str, *, body_class: str = "body-text") -> str:
    """Build a generic panel card with title and body."""
    return (
        f'<div class="panel-card">'
        f"<h3>{html.escape(title)}</h3>"
        f'<p class="{body_class}">{html.escape(body)}</p>'
        f"</div>"
    )


def insight_pill(label: str, css_class: str) -> str:
    """Build a trend/momentum pill badge."""
    return f'<span class="insight-pill {css_class}">{html.escape(label)}</span>'


def news_card(title: str, meta: str, summary: str, url: str | None) -> str:
    """Build a news article card."""
    link_html = (
        f'<a href="{html.escape(url)}" target="_blank">기사 보기 →</a>'
        if url
        else ""
    )
    return (
        f'<div class="news-card">'
        f'<p class="news-title">{html.escape(title)}</p>'
        f'<span class="news-meta">{html.escape(meta)}</span>'
        f'<p class="news-summary">{html.escape(summary)}</p>'
        f"{link_html}"
        f"</div>"
    )


def empty_state(message: str, icon: str = "📊") -> str:
    """Build an empty-state placeholder."""
    return (
        f'<div class="empty-state">'
        f'<div class="icon">{icon}</div>'
        f"{html.escape(message)}"
        f"</div>"
    )
