"""Fast Git boundary for code-review evidence unit contracts.

The production API still receives Git-shaped completed processes for the exact
commands under test. A separate module-scoped fixture keeps one real repository
check outside measured test calls, while these contracts avoid repeated Windows
process startup for tree, blob, ignore, and path-classification operations.
"""

from __future__ import annotations

import fnmatch
import hashlib
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from collections.abc import Sequence


def _staged_files() -> dict[str, bytes]:
    return {}


def _blob_store() -> dict[str, str]:
    return {}


@dataclass
class _Repository:
    """Minimal staged and object state used by the evidence tests."""

    staged: dict[str, bytes] = field(default_factory=_staged_files)
    blobs: dict[str, str] = field(default_factory=_blob_store)


def _tree_id(repository: _Repository) -> str:
    """Return a stable Git-shaped identity for the staged snapshot."""
    digest = hashlib.sha1()  # noqa: S324 - Git-compatible test object shape
    for relative, content in sorted(repository.staged.items()):
        digest.update(relative.encode())
        digest.update(content)
    return digest.hexdigest()


def _worktree_paths(root: Path) -> set[str]:
    """List repository files without synthetic Git metadata."""
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(root).parts
    }


def _ignored_paths(root: Path, repository: _Repository) -> set[str]:
    """Classify the bounded ignore-pattern vocabulary used by these tests."""
    ignore_file = root / ".gitignore"
    patterns = (
        tuple(
            line.strip()
            for line in ignore_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        )
        if ignore_file.is_file()
        else ()
    )
    ignored: set[str] = set()
    for relative in _worktree_paths(root) - repository.staged.keys():
        if _path_is_ignored(root, relative, root_patterns=patterns):
            ignored.add(relative)
    return ignored


def _matches_ignore_pattern(relative: str, patterns: tuple[str, ...]) -> bool:
    """Return whether one path matches the test repository ignore rules."""
    return any(
        (pattern.endswith("/") and relative.startswith(pattern))
        or fnmatch.fnmatch(relative, pattern)
        for pattern in patterns
    )


def _path_is_ignored(
    root: Path,
    relative: str,
    *,
    root_patterns: tuple[str, ...] | None = None,
) -> bool:
    """Apply root and nearest home-local ignore rules to one portable path."""
    patterns = root_patterns
    if patterns is None:
        ignore_file = root / ".gitignore"
        patterns = (
            tuple(ignore_file.read_text(encoding="utf-8").splitlines())
            if ignore_file.is_file()
            else ()
        )
    if _matches_ignore_pattern(relative, patterns):
        return True
    candidate = root / relative
    local_ignore = candidate.parent / ".gitignore"
    if not local_ignore.is_file():
        return False
    local_patterns = tuple(local_ignore.read_text(encoding="utf-8").splitlines())
    return _matches_ignore_pattern(candidate.name, local_patterns)


def _completed(
    argv: Sequence[str],
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
) -> subprocess.CompletedProcess[str]:
    """Build the typed result returned at the subprocess seam."""
    return subprocess.CompletedProcess(list(argv), returncode, stdout, stderr)


@pytest.fixture
def real_git_commands() -> bool:
    """Select real Git subprocesses for one explicit boundary contract."""
    return True


@pytest.fixture(autouse=True)
def fast_git_commands(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Serve evidence Git commands in memory instead of spawning processes."""
    if "real_git_commands" in request.fixturenames:
        return
    repositories: dict[Path, _Repository] = {}
    real_run = subprocess.run

    def fake_run(
        argv: Sequence[str],
        *args: Any,
        cwd: str | Path | None = None,
        check: bool = False,
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[str]:
        """Implement the bounded Git command set exercised by this package."""
        if not argv or argv[0] != "git":
            return real_run(argv, *args, cwd=cwd, check=check, **kwargs)
        root = Path(cwd or ".").resolve()
        command = tuple(str(value) for value in argv[1:])
        if command[:1] == ("init",):
            repositories[root] = _Repository()
            result = _completed(argv)
        elif root not in repositories:
            result = _completed(argv, 128, stderr="not a git repository")
        else:
            repository = repositories[root]
            result = _run_repository_command(root, repository, argv, command)
        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                result.args,
                output=result.stdout,
                stderr=result.stderr,
            )
        return result

    monkeypatch.setattr(subprocess, "run", fake_run)


def _run_repository_command(
    root: Path,
    repository: _Repository,
    argv: Sequence[str],
    command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    """Return one result for a command against an initialized fake repository."""
    handlers = {
        "add": _run_add,
        "write-tree": _run_write_tree,
        "hash-object": _run_hash_object,
        "cat-file": _run_cat_file,
        "ls-files": _run_ls_files,
        "check-ignore": _run_check_ignore,
    }
    handler = handlers.get(command[0], _run_unsupported)
    return handler(root, repository, argv, command)


def _run_add(
    root: Path,
    repository: _Repository,
    argv: Sequence[str],
    command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    """Stage current file bytes in the fake index."""
    for relative in command[1:]:
        repository.staged[relative] = (root / relative).read_bytes()
    return _completed(argv)


def _run_write_tree(
    _root: Path,
    repository: _Repository,
    argv: Sequence[str],
    _command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    """Return the fake index tree identity."""
    return _completed(argv, stdout=f"{_tree_id(repository)}\n")


def _run_hash_object(
    root: Path,
    repository: _Repository,
    argv: Sequence[str],
    command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    """Store and identify one worktree blob."""
    relative = command[-1]
    content = (root / relative).read_text(encoding="utf-8")
    object_id = hashlib.sha1(content.encode()).hexdigest()  # noqa: S324
    repository.blobs[object_id] = content
    return _completed(argv, stdout=f"{object_id}\n")


def _run_cat_file(
    _root: Path,
    repository: _Repository,
    argv: Sequence[str],
    command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    """Return one stored fake blob."""
    return _completed(argv, stdout=repository.blobs[command[2]])


def _run_ls_files(
    root: Path,
    repository: _Repository,
    argv: Sequence[str],
    command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    """Return tracked, ignored, or other paths for one ls-files query."""
    if command[1] == "--error-unmatch":
        relative = command[-1]
        returncode = 0 if relative in repository.staged else 1
        return _completed(argv, returncode, stdout=f"{relative}\n")
    if command[1] == "--":
        paths = _tracked_below(repository.staged, command[-1])
        return _completed(argv, stdout="".join(f"{path}\n" for path in paths))
    if command[1] == "-z":
        paths = repository.staged.keys()
    else:
        ignored = _ignored_paths(root, repository)
        others = _worktree_paths(root) - repository.staged.keys()
        paths = ignored if "--ignored" in command else others - ignored
    return _completed(argv, stdout="".join(f"{path}\0" for path in sorted(paths)))


def _tracked_below(staged: dict[str, bytes], relative: str) -> tuple[str, ...]:
    """Return stable tracked paths at or below one portable directory."""
    prefix = relative.rstrip("/")
    return tuple(
        sorted(path for path in staged if path == prefix or path.startswith(f"{prefix}/")),
    )


def _run_check_ignore(
    root: Path,
    _repository: _Repository,
    argv: Sequence[str],
    command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    """Check one path against root and home-local ignore files."""
    returncode = 0 if _path_is_ignored(root, command[-1]) else 1
    return _completed(argv, returncode)


def _run_unsupported(
    _root: Path,
    _repository: _Repository,
    argv: Sequence[str],
    command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    """Reject a Git command outside the bounded evidence vocabulary."""
    return _completed(argv, 129, stderr=f"unsupported fake Git command: {command}")


# eof
