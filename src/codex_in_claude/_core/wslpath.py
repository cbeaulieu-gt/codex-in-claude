"""Translate Windows-shaped linked-worktree pointers for WSL git calls."""

from __future__ import annotations

import re
from pathlib import Path

_WINDOWS_DRIVE_PATH_RE = re.compile(r"^(?P<drive>[A-Za-z]):[/\\\\](?P<rest>.*)$")
_MAX_PARENT_LEVELS = 64


def normalize_wsl_drive_path(value: str) -> str:
    """Translate an absolute Windows drive path to its WSL mount path.

    Args:
        value: Candidate path string.

    Returns:
        The translated ``/mnt/<drive>/...`` path when ``value`` starts with an
        ASCII drive letter, colon, and path separator; otherwise ``value``
        unchanged.
    """
    match = _WINDOWS_DRIVE_PATH_RE.match(value)
    if match is None:
        return value
    drive = match.group("drive").lower()
    rest = match.group("rest").replace("\\", "/")
    return f"/mnt/{drive}/{rest}"


def linked_worktree_gitdir(cwd: str) -> str | None:
    """Read a Windows-shaped linked-worktree gitdir pointer.

    Args:
        cwd: Directory whose direct ``.git`` entry should be inspected.

    Returns:
        The translated absolute gitdir path when ``.git`` is a pointer file
        containing a Windows drive path; otherwise ``None``. Read failures are
        treated as no matching pointer.
    """
    git_marker = Path(cwd) / ".git"
    try:
        if not git_marker.is_file():
            return None
        lines = git_marker.read_text().splitlines()
    except (OSError, UnicodeError):
        return None

    first_line = next((line for line in lines if line.strip()), None)
    if first_line is None or not first_line.startswith("gitdir:"):
        return None
    value = first_line.removeprefix("gitdir:").strip()
    if not value:
        return None
    normalized = normalize_wsl_drive_path(value)
    return normalized if normalized != value else None


def git_dir_override(cwd: str) -> dict[str, str]:
    """Build git environment overrides for a Windows-created worktree.

    Starting at ``cwd``, the search walks toward the filesystem root and stops
    at the first directory containing any ``.git`` marker. A bounded level
    count supplements the root check so malformed path behavior cannot make the
    search loop forever.

    Args:
        cwd: Directory from which git repository discovery would begin.

    Returns:
        ``GIT_DIR`` and ``GIT_WORK_TREE`` for a translated pointer, or an empty
        dictionary for every ordinary repository shape.
    """
    current = Path(cwd)
    for _ in range(_MAX_PARENT_LEVELS):
        marker = current / ".git"
        try:
            marker_exists = marker.exists()
        except OSError:
            return {}
        if marker_exists:
            gitdir = linked_worktree_gitdir(str(current))
            if gitdir is None:
                return {}
            return {"GIT_DIR": gitdir, "GIT_WORK_TREE": str(current)}
        parent = current.parent
        if parent == current:
            break
        current = parent
    return {}
