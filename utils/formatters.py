"""Shared numeric and display formatters."""

from __future__ import annotations


def safe_to_float(value: object) -> float | None:
    """Convert a value to float, returning None for invalid or NaN inputs."""
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number:  # NaN check
        return None
    return number


def format_price(value: float | None, currency: str) -> str:
    """Format a price for display."""
    if value is None:
        return "—"
    if currency == "KRW":
        return f"{value:,.0f}원"
    return f"{currency} {value:,.2f}"


def format_market_cap(value: float | None, currency: str) -> str:
    """Format market capitalization with locale-appropriate units."""
    if value is None:
        return "—"

    if currency == "KRW":
        if value >= 1_000_000_000_000:
            return f"{value / 1_000_000_000_000:,.1f}조원"
        if value >= 100_000_000:
            return f"{value / 100_000_000:,.0f}억원"
        return f"{value:,.0f}원"

    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:,.2f}T"
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.2f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"
    return f"${value:,.0f}"


def format_ratio(value: float | None, suffix: str = "") -> str:
    """Format a financial ratio."""
    if value is None:
        return "—"
    return f"{value:,.2f}{suffix}"


def format_indicator(value: float | None, digits: int = 2) -> str:
    """Format a technical indicator value."""
    if value is None:
        return "—"
    return f"{value:,.{digits}f}"
