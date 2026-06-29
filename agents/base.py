"""Base agent protocol for the multi-agent pipeline."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Agent(Protocol):
    """Minimal interface shared by all agents."""

    name: str
