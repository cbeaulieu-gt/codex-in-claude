"""Expose cached `codex_bin()` resolution with an explicit override (#3)."""

from __future__ import annotations

import os
from pathlib import Path

from codex_in_claude import cli_contract
from codex_in_claude._core import binresolve


class BinaryNotFoundError(RuntimeError):
    """The configured/resolved `codex` binary path does not exist on disk."""


_cache: str | None = None


def codex_bin() -> str:
    """Return the configured or resolved `codex` binary path."""
    global _cache  # noqa: PLW0603 — intentional process-level memoization
    if _cache is not None:
        return _cache

    override = os.environ.get("CODEX_IN_CLAUDE_CODEX_BIN", "")
    if override:
        if not Path(override).exists():
            raise BinaryNotFoundError(f"Configured codex binary does not exist: {override}")
        _cache = override
        return _cache

    _cache = binresolve.resolve_codex_bin() or cli_contract.CODEX_BIN
    return _cache


def reset_cache() -> None:
    """Drop the cached binary path (used by tests)."""
    global _cache  # noqa: PLW0603 — resets the intentional module-level cache
    _cache = None
