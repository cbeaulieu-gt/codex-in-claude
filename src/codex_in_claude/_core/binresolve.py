"""Resolve `codex` through ordered candidate probes for WSL2/npm shims (#3)."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from codex_in_claude._core import runtime

USR_LOCAL_BIN: Path = Path("/usr/local/bin")


def _is_executable_file(path: Path) -> bool:
    try:
        return path.exists() and path.is_file() and os.access(path, os.X_OK)
    except (OSError, ValueError):
        return False


def resolve_codex_bin() -> str | None:
    """Return the first executable `codex` candidate found, or None."""
    try:
        home = os.environ.get("HOME")
        if home:
            candidate = Path(home) / ".local" / "bin" / "codex"
            if _is_executable_file(candidate):
                return str(candidate)

        candidate = USR_LOCAL_BIN / "codex"
        if _is_executable_file(candidate):
            return str(candidate)

        try:
            run = runtime.run_sync_capture(["npm", "bin", "-g"], timeout_seconds=5)
            npm_bin = run.stdout.strip() if run.exit_code == 0 and not run.binary_missing else ""
            if npm_bin:
                candidate = Path(npm_bin) / "codex"
                if _is_executable_file(candidate):
                    return str(candidate)
        except Exception:
            pass

        try:
            return shutil.which("codex")
        except Exception:
            return None
    except Exception:
        return None
