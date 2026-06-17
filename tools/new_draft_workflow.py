"""Interactive workflow for the `new_draft` effort-scaffolding tool.

Flow: ask for a slug (re-prompting until it is valid and free of any local or
remote branch), read the current version from `pyproject.toml` and let the user
pick a patch/minor/major bump, offer a sibling worktree, then create the branch
(in place or in the worktree) and write the `docs/draft.vX.Y.Z.<slug>.md`
skeleton in the chosen worktree. The chosen version only labels the draft and
its filename; `pyproject.toml` is read but never rewritten.

The terminal seams (`ask_text`, `select`) and the Git calls are imported as
module attributes so tests monkeypatch them and drive every branch without a TTY
or a real repository.
"""

from __future__ import annotations

import argparse
import datetime
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

from tools import find_project_root
from tools.new_draft_git import add_worktree, branch_collision, create_local_branch
from tools.new_draft_models import (
    BUMP_PARTS,
    NewDraftError,
    SemanticVersion,
    compute_worktree_path,
    draft_filename,
    draft_skeleton,
    read_pyproject_version,
    validate_slug,
)
from tools.new_draft_prompts import ask_text
from tools.prompt_workflow_menu import select

if TYPE_CHECKING:
    from collections.abc import Sequence

LOGGER = logging.getLogger("new_draft")

# Exit code used for fatal errors, matching the other tool hubs.
EXIT_FATAL = 2
# Name of the file whose version line is bumped on the new branch.
PYPROJECT_NAME = "pyproject.toml"
# Folder under the chosen worktree that holds the draft file.
DOCS_DIRNAME = "docs"


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    """Parse the command line into a namespace with an optional `--root`."""
    parser = argparse.ArgumentParser(
        prog="new_draft",
        description="Scaffold a new development effort: branch, optional worktree, draft.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root to act on (default: discovered from the current directory).",
    )
    return parser.parse_args(argv)


def _resolve_root(args: argparse.Namespace) -> Path:
    """Return the repository root from `--root` or by discovery."""
    if args.root is not None:
        return args.root.resolve()
    return find_project_root(Path.cwd())


def _prompt_valid_slug(cwd: Path) -> str | None:
    """Prompt for a slug until it is valid and free, or None when cancelled.

    Args:
        cwd: The repository root used for the branch-collision check.

    Returns:
        A validated slug with no branch collision, or None when the user
        cancels the text prompt.
    """
    while True:
        raw = ask_text("Slug name for the new effort:")
        if raw is None:
            return None
        try:
            slug = validate_slug(raw)
        except NewDraftError as err:
            LOGGER.info("%s", err)
            continue
        collision = branch_collision(slug, cwd=cwd)
        if collision is not None:
            LOGGER.info(
                "Branch '%s' already exists (%s); pick another slug.",
                slug,
                collision,
            )
            continue
        return slug


def _prompt_version(current: SemanticVersion) -> SemanticVersion | None:
    """Offer patch/minor/major bumps of `current` and return the chosen one."""
    options = [
        (f"{part} -> {current.bumped(part)}", current.bumped(part)) for part in BUMP_PARTS
    ]
    return select(f"Target version (current v{current}):", options)


def _prompt_worktree(worktree_path: Path) -> bool | None:
    """Ask whether to create a sibling worktree; None when cancelled."""
    options = [
        (f"Yes, create worktree at {worktree_path}", True),
        ("No, work in the current worktree", False),
    ]
    return select("Isolate this effort in a separate worktree?", options)


def _create_branch_and_target(
    slug: str,
    *,
    project_root: Path,
    worktree_path: Path,
    use_worktree: bool,
) -> Path:
    """Create the branch (in place or in a worktree) and return its root path."""
    if use_worktree:
        add_worktree(worktree_path, slug, cwd=project_root)
        return worktree_path
    create_local_branch(slug, cwd=project_root)
    return project_root


def _write_draft(
    target_root: Path,
    *,
    version: SemanticVersion,
    slug: str,
    today: datetime.date,
) -> Path:
    """Write the draft skeleton under `target_root/docs` and return its path."""
    docs_dir = target_root / DOCS_DIRNAME
    docs_dir.mkdir(parents=True, exist_ok=True)
    draft = docs_dir / draft_filename(version, slug)
    draft.write_text(
        draft_skeleton(version=version, slug=slug, branch=slug, today=today),
        encoding="utf-8",
    )
    return draft


def _today() -> datetime.date:
    """Return today's date (UTC) for the draft metadata."""
    return datetime.datetime.now(datetime.UTC).date()


def _log_summary(
    *,
    slug: str,
    version: SemanticVersion,
    target_root: Path,
    draft: Path,
    use_worktree: bool,
) -> None:
    """Log what was created and the next step for the user."""
    location = f"worktree {target_root}" if use_worktree else "the current worktree"
    LOGGER.info("Created branch '%s' in %s (target version v%s).", slug, location, version)
    LOGGER.info("Wrote draft %s.", draft)


def run(argv: Sequence[str] | None) -> int:
    """Run the interactive new_draft workflow and return a process exit code."""
    _configure_logging()
    root = _resolve_root(_parse_args(argv))

    slug = _prompt_valid_slug(root)
    if slug is None:
        LOGGER.info("Cancelled: no slug entered.")
        return 1

    current = read_pyproject_version((root / PYPROJECT_NAME).read_text(encoding="utf-8"))
    version = _prompt_version(current)
    if version is None:
        LOGGER.info("Cancelled: no version selected.")
        return 1

    worktree_path = compute_worktree_path(root, slug)
    use_worktree = _prompt_worktree(worktree_path)
    if use_worktree is None:
        LOGGER.info("Cancelled: no worktree choice made.")
        return 1

    target_root = _create_branch_and_target(
        slug,
        project_root=root,
        worktree_path=worktree_path,
        use_worktree=use_worktree,
    )
    draft = _write_draft(target_root, version=version, slug=slug, today=_today())
    _log_summary(
        slug=slug,
        version=version,
        target_root=target_root,
        draft=draft,
        use_worktree=use_worktree,
    )
    return 0


def _configure_logging() -> None:
    """Configure stdout logging with message-only formatting."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


def _log_fatal(err: Exception) -> NoReturn:
    """Log a fatal error and exit with `EXIT_FATAL`."""
    _configure_logging()
    LOGGER.exception("ERROR: %s", err)
    raise SystemExit(EXIT_FATAL) from err


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point: run the workflow, turning expected errors into exit 2."""
    try:
        return run(argv)
    except (NewDraftError, OSError) as err:
        _log_fatal(err)


# eof
