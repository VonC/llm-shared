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

Fix: add the non-interactive `--from-draft` mode used by the `process-draft`
instruction. It takes an existing draft path, a `--slug`, an optional
`--version` (defaulting to the current `version.txt` version), and a
`--worktree` or `--in-place` layout, then checks the slug, creates the branch,
and relocates the draft to `draft.vX.Y.Z.<slug>.md` inside the chosen tree -
reusing the same slug, collision, worktree, and filename rules as the
interactive flow so the two never drift.
"""

from __future__ import annotations

import argparse
import datetime
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

from tools import find_project_root
from tools.new_draft_git import (
    add_worktree,
    branch_collision,
    create_local_branch,
    git_move,
    path_is_tracked,
    stage_path,
)
from tools.new_draft_models import (
    BUMP_PARTS,
    NewDraftError,
    SemanticVersion,
    compute_worktree_path,
    draft_filename,
    draft_skeleton,
    read_pyproject_version,
    read_version_txt,
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
# Name of the human-facing release file read by the --from-draft default.
VERSION_TXT_NAME = "version.txt"
# Folder under the chosen worktree that holds the draft file.
DOCS_DIRNAME = "docs"


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    """Parse the command line into a namespace.

    Besides `--root`, the `--from-draft` flags drive the non-interactive mode:
    a draft path, a `--slug`, an optional `--version`, and a `--worktree` or
    `--in-place` layout. They default so the interactive flow (no `--from-draft`)
    keeps a `root` of None and a `use_worktree` of None.
    """
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
    parser.add_argument(
        "--from-draft",
        dest="from_draft",
        type=Path,
        default=None,
        help="Process this existing draft non-interactively instead of scaffolding a new one.",
    )
    parser.add_argument(
        "--slug",
        default=None,
        help="Effort slug for the branch and the renamed draft (required with --from-draft).",
    )
    parser.add_argument(
        "--version",
        default=None,
        help="Target version X.Y.Z (with --from-draft; defaults to the version.txt version).",
    )
    layout = parser.add_mutually_exclusive_group()
    layout.add_argument(
        "--worktree",
        dest="use_worktree",
        action="store_true",
        help="Create the branch in a sibling worktree (use with --from-draft).",
    )
    layout.add_argument(
        "--in-place",
        dest="use_worktree",
        action="store_false",
        help="Create the branch in the current working tree (use with --from-draft).",
    )
    parser.set_defaults(use_worktree=None)
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
        (f"{part} -> {current.bumped(part)}", current.bumped(part))
        for part in BUMP_PARTS
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
    LOGGER.info(
        "Created branch '%s' in %s (target version v%s).",
        slug,
        location,
        version,
    )
    LOGGER.info("Wrote draft %s.", draft)


def _resolve_draft_path(raw: Path, root: Path) -> Path:
    """Return the draft path: absolute as given, otherwise under the root."""
    return raw if raw.is_absolute() else root / raw


def _parse_version_arg(raw: str) -> SemanticVersion:
    """Parse a `--version` value, allowing an optional leading `v`."""
    text = raw.strip()
    if text[:1] in {"v", "V"}:
        text = text[1:]
    return SemanticVersion.parse(text)


def _resolve_version_arg(raw: str | None, root: Path) -> SemanticVersion:
    """Return the target version from `--version`, or the version.txt one.

    Args:
        raw: The `--version` value, or None when the flag was not given.
        root: The repository root, used to read `version.txt` for the default.

    Returns:
        The parsed `--version` when present, else the current version read from
        `version.txt` through the shared parser.
    """
    if raw:
        return _parse_version_arg(raw)
    content = (root / VERSION_TXT_NAME).read_text(encoding="utf-8")
    return read_version_txt(content)


def _relocate_draft(
    source: Path,
    target: Path,
    *,
    source_cwd: Path,
    target_cwd: Path,
) -> None:
    """Move the draft from `source` to `target`, following the Q08 rule.

    In the current tree (source and target share a working tree) a tracked draft
    is renamed with `git mv` and an untracked one with a plain rename. For a
    worktree (different trees) the text is written into the target tree and
    staged, then the source is removed and, when it was tracked, its deletion is
    staged in the source tree, so a draft that is not yet committed still moves
    across.

    Args:
        source: The current draft path.
        target: The `draft.vX.Y.Z.<slug>.md` path in the chosen tree.
        source_cwd: The working tree the source lives in.
        target_cwd: The working tree the branch was created in.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    if source_cwd == target_cwd:
        if path_is_tracked(source, cwd=source_cwd):
            git_move(source, target, cwd=source_cwd)
        else:
            source.rename(target)
        return
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    stage_path(target, cwd=target_cwd)
    source_tracked = path_is_tracked(source, cwd=source_cwd)
    source.unlink()
    if source_tracked:
        stage_path(source, cwd=source_cwd)


def _log_from_draft_summary(
    *,
    slug: str,
    version: SemanticVersion,
    source: Path,
    target: Path,
    use_worktree: bool,
) -> None:
    """Log the branch created and the draft move for the --from-draft mode."""
    location = (
        f"worktree {target.parent.parent}" if use_worktree else "the current worktree"
    )
    LOGGER.info(
        "Created branch '%s' in %s (target version v%s).",
        slug,
        location,
        version,
    )
    LOGGER.info("Moved draft %s -> %s.", source, target)


def _run_from_draft(args: argparse.Namespace, root: Path) -> int:
    """Run the non-interactive --from-draft mode and return an exit code.

    Validates the slug (present, well-formed, and free of any branch collision),
    the layout choice, the version, and the draft path, then creates the branch
    and relocates the draft into the chosen tree.

    Args:
        args: The parsed namespace, with `from_draft`, `slug`, `version`, and
            `use_worktree` set by the caller.
        root: The resolved repository root and source working tree.

    Returns:
        0 once the branch is created and the draft is relocated.

    Raises:
        NewDraftError: When the slug is missing or taken, the layout is not
            chosen, or the draft path does not point at a file.
    """
    if not args.slug:
        msg = "Provide a slug with --slug for --from-draft."
        raise NewDraftError(msg)
    slug = validate_slug(args.slug)
    collision = branch_collision(slug, cwd=root)
    if collision is not None:
        msg = f"Branch '{slug}' already exists ({collision}); choose another slug."
        raise NewDraftError(msg)
    if args.use_worktree is None:
        msg = "Choose a layout: pass --worktree or --in-place."
        raise NewDraftError(msg)
    version = _resolve_version_arg(args.version, root)
    source = _resolve_draft_path(args.from_draft, root)
    if not source.is_file():
        msg = f"Draft not found: {source}"
        raise NewDraftError(msg)

    worktree_path = compute_worktree_path(root, slug)
    target_root = _create_branch_and_target(
        slug,
        project_root=root,
        worktree_path=worktree_path,
        use_worktree=args.use_worktree,
    )
    target = target_root / DOCS_DIRNAME / draft_filename(version, slug)
    _relocate_draft(source, target, source_cwd=root, target_cwd=target_root)
    _log_from_draft_summary(
        slug=slug,
        version=version,
        source=source,
        target=target,
        use_worktree=args.use_worktree,
    )
    return 0


def run(argv: Sequence[str] | None) -> int:
    """Run the new_draft workflow and return a process exit code.

    With `--from-draft` the non-interactive mode runs; otherwise the interactive
    flow prompts for the slug, version, and worktree choice.
    """
    _configure_logging()
    args = _parse_args(argv)
    root = _resolve_root(args)

    if args.from_draft is not None:
        return _run_from_draft(args, root)

    slug = _prompt_valid_slug(root)
    if slug is None:
        LOGGER.info("Cancelled: no slug entered.")
        return 1

    current = read_pyproject_version(
        (root / PYPROJECT_NAME).read_text(encoding="utf-8"),
    )
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
