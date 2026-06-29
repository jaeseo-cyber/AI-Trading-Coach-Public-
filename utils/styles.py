"""Theme-aware CSS — ChatGPT clarity + Bloomberg terminal aesthetic."""

from __future__ import annotations

LIGHT_VARS = """
    --font-xs: 0.75rem;
    --font-sm: 0.875rem;
    --font-base: 0.9375rem;
    --font-md: 1rem;
    --font-lg: 1.125rem;
    --font-xl: 1.375rem;
    --line-tight: 1.35;
    --line-normal: 1.6;
    --line-relaxed: 1.75;
    --bg-primary: #f7f7f8;
    --bg-secondary: #ffffff;
    --bg-elevated: #ffffff;
    --bg-input: #ffffff;
    --text-primary: #0d0d0d;
    --text-secondary: #565869;
    --text-muted: #8e8ea0;
    --border: #e5e5e5;
    --border-subtle: #ececf1;
    --accent: #f59e0b;
    --accent-soft: rgba(245, 158, 11, 0.12);
    --accent-blue: #2563eb;
    --accent-green: #10a981;
    --accent-red: #ef4444;
    --shadow: 0 1px 3px rgba(0, 0, 0, 0.06), 0 4px 12px rgba(0, 0, 0, 0.04);
    --shadow-lg: 0 4px 24px rgba(0, 0, 0, 0.08);
    --hero-gradient: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
    --chart-bg: #ffffff;
    --sidebar-bg: #ffffff;
"""

DARK_VARS = """
    --font-xs: 0.75rem;
    --font-sm: 0.875rem;
    --font-base: 0.9375rem;
    --font-md: 1rem;
    --font-lg: 1.125rem;
    --font-xl: 1.375rem;
    --line-tight: 1.35;
    --line-normal: 1.6;
    --line-relaxed: 1.75;
    --bg-primary: #0d0d0d;
    --bg-secondary: #171717;
    --bg-elevated: #212121;
    --bg-input: #2f2f2f;
    --text-primary: #ececec;
    --text-secondary: #b4b4b4;
    --text-muted: #8e8e8e;
    --border: #3f3f3f;
    --border-subtle: #2f2f2f;
    --accent: #f59e0b;
    --accent-soft: rgba(245, 158, 11, 0.15);
    --accent-blue: #60a5fa;
    --accent-green: #34d399;
    --accent-red: #f87171;
    --shadow: 0 1px 3px rgba(0, 0, 0, 0.3), 0 4px 12px rgba(0, 0, 0, 0.2);
    --shadow-lg: 0 4px 24px rgba(0, 0, 0, 0.4);
    --hero-gradient: linear-gradient(135deg, #000000 0%, #1a1a1a 50%, #262626 100%);
    --chart-bg: #171717;
    --sidebar-bg: #171717;
"""


def build_app_css(theme: str) -> str:
    vars_block = DARK_VARS if theme == "dark" else LIGHT_VARS
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {{
    {vars_block}
}}

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: var(--font-base);
    line-height: var(--line-normal);
}}

.stApp {{
    background-color: var(--bg-primary) !important;
    color: var(--text-primary);
}}

.block-container {{
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1280px;
}}

/* ── Sidebar ── */
div[data-testid="stSidebar"] {{
    background-color: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border);
}}
div[data-testid="stSidebar"] .stMarkdown,
div[data-testid="stSidebar"] label {{
    color: var(--text-primary) !important;
}}

/* ── Hero ── */
.hero-banner {{
    background: var(--hero-gradient);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-lg);
}}
.hero-banner h1 {{
    color: #ffffff !important;
    font-size: var(--font-xl) !important;
    font-weight: 700 !important;
    margin: 0 0 0.5rem 0 !important;
    letter-spacing: -0.02em;
    line-height: var(--line-tight);
}}
.hero-banner p {{
    color: rgba(255,255,255,0.75) !important;
    font-size: var(--font-sm);
    line-height: var(--line-normal);
    margin: 0;
}}
.hero-badge {{
    display: inline-block;
    background: var(--accent-soft);
    color: var(--accent);
    font-size: var(--font-xs);
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.25rem 0.6rem;
    border-radius: 4px;
    margin-bottom: 0.75rem;
    border: 1px solid rgba(245,158,11,0.3);
}}

/* ── Section header ── */
.section-header {{
    margin: 1.75rem 0 1rem 0;
}}
.section-header h2 {{
    color: var(--text-primary) !important;
    font-size: var(--font-lg) !important;
    font-weight: 600 !important;
    margin: 0 !important;
    letter-spacing: -0.01em;
    line-height: var(--line-tight);
}}
.section-header p {{
    color: var(--text-muted) !important;
    font-size: var(--font-sm);
    line-height: var(--line-normal);
    margin: 0.35rem 0 0 0;
}}

/* ── Panel card ── */
.panel-card {{
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow);
}}
.panel-card h3 {{
    color: var(--text-primary) !important;
    font-size: var(--font-md) !important;
    font-weight: 600 !important;
    margin: 0 0 0.65rem 0 !important;
    line-height: var(--line-tight);
}}
.panel-card .body-text {{
    color: var(--text-secondary);
    font-size: var(--font-sm);
    line-height: var(--line-relaxed);
    margin: 0;
}}
.panel-card .body-text.pre-line {{
    white-space: pre-line;
}}

/* ── Metric grid ── */
.metric-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 0.75rem;
    margin-bottom: 1rem;
}}
.metric-card {{
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.1rem;
    box-shadow: var(--shadow);
    transition: border-color 0.15s ease;
}}
.metric-card:hover {{
    border-color: var(--accent);
}}
.metric-card .label {{
    color: var(--text-muted);
    font-size: var(--font-xs);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.4rem;
    line-height: var(--line-tight);
}}
.metric-card .value {{
    color: var(--text-primary);
    font-size: var(--font-lg);
    font-weight: 600;
    letter-spacing: -0.02em;
    line-height: var(--line-tight);
}}
.metric-card .sub {{
    color: var(--text-secondary);
    font-size: var(--font-xs);
    margin-top: 0.35rem;
    line-height: var(--line-normal);
}}

/* ── Ticker header ── */
.ticker-header {{
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 0.5rem 1rem;
    margin-bottom: 1rem;
}}
.ticker-header .symbol {{
    color: var(--accent);
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: -0.02em;
}}
.ticker-header .name {{
    color: var(--text-secondary);
    font-size: 0.95rem;
}}

/* ── News cards ── */
.news-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 0.75rem;
}}
.news-card {{
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.15rem;
    box-shadow: var(--shadow);
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    transition: border-color 0.15s ease, transform 0.15s ease;
}}
.news-card:hover {{
    border-color: var(--accent-blue);
    transform: translateY(-1px);
}}
.news-card .news-title {{
    color: var(--text-primary);
    font-size: var(--font-sm);
    font-weight: 600;
    line-height: var(--line-normal);
    margin: 0;
}}
.news-card .news-meta {{
    color: var(--text-muted);
    font-size: var(--font-xs);
    line-height: var(--line-tight);
}}
.news-card .news-summary {{
    color: var(--text-secondary);
    font-size: var(--font-sm);
    line-height: var(--line-relaxed);
    margin: 0;
    flex: 1;
}}
.news-card a {{
    color: var(--accent-blue);
    font-size: var(--font-xs);
    font-weight: 500;
    text-decoration: none;
}}
.news-card a:hover {{
    text-decoration: underline;
}}

/* ── AI opinion card (ChatGPT-style) ── */
.ai-card {{
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: var(--shadow-lg);
    margin-top: 0.5rem;
}}
.ai-card-header {{
    background: var(--bg-elevated);
    border-bottom: 1px solid var(--border);
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}}
.ai-avatar {{
    width: 36px;
    height: 36px;
    border-radius: 8px;
    background: var(--hero-gradient);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}}
.ai-card-header .title {{
    color: var(--text-primary);
    font-weight: 600;
    font-size: 0.95rem;
    margin: 0;
}}
.ai-card-header .subtitle {{
    color: var(--text-muted);
    font-size: 0.78rem;
    margin: 0;
}}
.ai-card-body {{
    padding: 1.75rem 1.5rem;
    color: var(--text-primary);
    font-size: var(--font-sm);
    line-height: var(--line-relaxed);
}}
.ai-card-body h2, .ai-card-body h3 {{
    color: var(--text-primary) !important;
    font-size: var(--font-md) !important;
    font-weight: 600 !important;
    margin: 1.5rem 0 0.65rem 0 !important;
    padding-bottom: 0.4rem;
    line-height: var(--line-tight);
    border-bottom: 1px solid var(--border-subtle);
}}
.ai-card-body h2:first-child {{
    margin-top: 0 !important;
}}
.ai-card-body ul {{
    padding-left: 1.35rem;
    color: var(--text-secondary);
    line-height: var(--line-relaxed);
    margin: 0.5rem 0;
}}
.ai-card-body li {{
    margin-bottom: 0.35rem;
}}
.ai-card-body p {{
    color: var(--text-secondary);
    margin: 0.65rem 0;
    line-height: var(--line-relaxed);
}}
.ai-disclaimer {{
    background: var(--accent-soft);
    border-top: 1px solid rgba(245,158,11,0.2);
    padding: 0.85rem 1.5rem;
    color: var(--text-muted);
    font-size: var(--font-xs);
    line-height: var(--line-normal);
}}

/* ── Insight pills ── */
.insight-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 0.75rem 0;
}}
.insight-pill {{
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
    border: 1px solid var(--border);
    background: var(--bg-elevated);
    color: var(--text-secondary);
}}
.insight-pill.bullish {{ border-color: var(--accent-green); color: var(--accent-green); }}
.insight-pill.bearish {{ border-color: var(--accent-red); color: var(--accent-red); }}
.insight-pill.neutral {{ border-color: var(--accent); color: var(--accent); }}

/* ── Chart wrapper ── */
.chart-panel {{
    background: var(--chart-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.75rem 0.5rem 0.5rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
}}
.chart-panel .chart-caption {{
    color: var(--text-muted);
    font-size: 0.75rem;
    padding: 0 0.75rem 0.5rem;
}}

/* ── Hide raw code in AI / markdown areas ── */
.ai-card-body pre,
.ai-card-body code,
.panel-card pre,
.panel-card code {{
    display: none !important;
}}

/* ── Empty state ── */
.empty-state {{
    background: var(--bg-secondary);
    border: 1px dashed var(--border);
    border-radius: 12px;
    padding: 3rem 2rem;
    text-align: center;
    color: var(--text-muted);
    font-size: var(--font-sm);
    line-height: var(--line-relaxed);
}}
.empty-state .icon {{ font-size: 2rem; margin-bottom: 0.75rem; opacity: 0.5; }}

/* ── Streamlit overrides ── */
.stTextInput input {{
    background-color: var(--bg-input) !important;
    color: var(--text-primary) !important;
    border-color: var(--border) !important;
    border-radius: 8px !important;
}}
.stButton > button[kind="primary"] {{
    background: var(--accent) !important;
    color: #0d0d0d !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em;
    transition: opacity 0.15s ease !important;
}}
.stButton > button[kind="primary"]:hover {{
    opacity: 0.88 !important;
    background: var(--accent) !important;
}}
div[data-testid="stMetric"] {{
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    box-shadow: var(--shadow);
}}
div[data-testid="stMetric"] label {{
    color: var(--text-muted) !important;
}}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: var(--text-primary) !important;
}}

/* ── Responsive ── */
@media (max-width: 768px) {{
    .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
    .hero-banner {{ padding: 1.5rem; }}
    .hero-banner h1 {{ font-size: 1.4rem !important; }}
    .metric-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .news-grid {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 480px) {{
    .metric-grid {{ grid-template-columns: 1fr; }}
}}
</style>
"""
