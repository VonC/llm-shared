"""CLI adapter for migration-aware schema-2 repository review status."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import NoReturn

from tools.review_status import collect_review_status
from tools.review_status_models import ReviewStatusOutcome
from tools.review_status_render import render_human, render_json

_OPERATIONAL_STATUS = 2


class _InvocationError(Exception):
    """Raised when arguments do not satisfy the public command contract."""


class _ArgumentParser(argparse.ArgumentParser):
    """Turn argparse termination into the command's status-two boundary."""

    def error(self, message: str) -> NoReturn:
        raise _InvocationError(message)


def _parser() -> argparse.ArgumentParser:
    """Build the stable public argument parser."""
    parser = _ArgumentParser(
        description="Report active reviews after bounded migration preflight.",
    )
    parser.add_argument("--root", type=Path, help="explicit Git repository root")
    parser.add_argument(
        "--format",
        choices=("human", "json"),
        default="human",
        help="status rendering format",
    )
    return parser


def _git_marker(root: Path) -> bool:
    """Return whether a directory carries a normal or worktree Git marker."""
    return (root / ".git").exists()


def _resolve_root(explicit_root: Path | None) -> Path:
    """Resolve an explicit Git root or discover one upward from the caller."""
    if explicit_root is not None:
        root = explicit_root.resolve(strict=True)
        if not root.is_dir() or not _git_marker(root):
            message = f"not a Git repository root: {root}"
            raise FileNotFoundError(message)
        return root

    # Do not use find_project_root here: its PRJ_DIR override could redirect a
    # caller-root status query to an unrelated repository.
    current = Path.cwd().resolve(strict=True)
    for candidate in (current, *current.parents):
        if _git_marker(candidate):
            return candidate
    message = f"no Git repository found from caller directory: {current}"
    raise FileNotFoundError(message)


def _wall_clock() -> datetime:
    """Return one timezone-aware evaluation time for the collection service."""
    return datetime.now().astimezone()


def main(argv: list[str] | None = None) -> int:
    """Collect once, render once, and return the result's typed process status."""
    try:
        arguments = _parser().parse_args(argv)
        root = _resolve_root(arguments.root)
        result = collect_review_status(root, _wall_clock)
    except _InvocationError as error:
        sys.stderr.write(f"rvw_status: {error}\n")
        return _OPERATIONAL_STATUS
    except (OSError, UnicodeError, ValueError) as error:
        sys.stderr.write(f"rvw_status: {error}\n")
        return _OPERATIONAL_STATUS
    except Exception as error:  # noqa: BLE001  # pragma: no cover
        sys.stderr.write(f"rvw_status: unexpected failure: {error}\n")
        return _OPERATIONAL_STATUS

    renderer = render_json if arguments.format == "json" else render_human
    rendered = f"{renderer(result)}\n"
    if result.outcome is ReviewStatusOutcome.OPERATIONAL_FAILURE:
        sys.stderr.write(rendered)
    else:
        sys.stdout.write(rendered)
    return result.process_status


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["main"]


# eof
