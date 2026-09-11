"""Bounded in-memory Git subprocess double for repository-oriented tests.

The double returns typed ``CompletedProcess`` values at the same subprocess
seam as Git. Packages keep explicit real-Git boundary cases while orchestration
tests avoid repeated Windows process startup for the finite command vocabulary
they already assert.
"""

from __future__ import annotations

import fnmatch
import hashlib
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


def _file_map() -> dict[str, bytes]:
    """Build one independent index or commit mapping."""
    return {}


def _blob_store() -> dict[str, str]:
    """Build one independent object mapping."""
    return {}


@dataclass
class RepositoryState:
    """Minimal index, commit, and object state for bounded Git commands."""

    staged: dict[str, bytes] = field(default_factory=_file_map)
    committed: dict[str, bytes] = field(default_factory=_file_map)
    blobs: dict[str, str] = field(default_factory=_blob_store)


LazyRepository = Callable[[Path], RepositoryState | None]


class GitTestDouble:
    """Serve a finite Git command set without starting child processes."""

    def __init__(
        self,
        real_run: Callable[..., subprocess.CompletedProcess[str]],
        *,
        lazy_repository: LazyRepository | None = None,
    ) -> None:
        """Retain the real subprocess seam and optional copied-repo loader."""
        self._real_run = real_run
        self._lazy_repository = lazy_repository
        self._repositories: dict[Path, RepositoryState] = {}

    def register(
        self,
        root: Path,
        *,
        staged: Mapping[str, bytes],
        committed: Mapping[str, bytes] | None = None,
    ) -> None:
        """Register one repository snapshot for later bounded commands."""
        self._repositories[root.resolve()] = RepositoryState(
            staged=dict(staged),
            committed=dict(committed or staged),
        )

    def run(
        self,
        argv: Sequence[str],
        *args: Any,
        cwd: str | Path | None = None,
        check: bool = False,
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[str]:
        """Return a real non-Git result or one bounded in-memory Git result."""
        if not argv or argv[0] != "git":
            return self._real_run(argv, *args, cwd=cwd, check=check, **kwargs)
        root = Path(cwd or ".").resolve()
        command = _without_config(tuple(str(value) for value in argv[1:]))
        if command[:1] == ("init",):
            self._repositories[root] = RepositoryState()
            result = _completed(argv)
        else:
            repository = self._repository(root)
            result = (
                _completed(argv, 128, stderr="not a git repository")
                if repository is None
                else _run_repository_command(
                    root,
                    repository,
                    argv,
                    command,
                    input_text=kwargs.get("input"),
                )
            )
        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                result.args,
                output=result.stdout,
                stderr=result.stderr,
            )
        return result

    def _repository(self, root: Path) -> RepositoryState | None:
        """Return registered state or load one copied real repository lazily."""
        repository = self._repositories.get(root)
        if repository is None and self._lazy_repository is not None:
            repository = self._lazy_repository(root)
            if repository is not None:
                self._repositories[root] = repository
        return repository


def _without_config(command: tuple[str, ...]) -> tuple[str, ...]:
    """Drop leading ``-c key=value`` pairs before command dispatch."""
    index = 0
    while index + 1 < len(command) and command[index] == "-c":
        index += 2
    return command[index:]


def _completed(
    argv: Sequence[str],
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
) -> subprocess.CompletedProcess[str]:
    """Build the typed result returned at the subprocess seam."""
    return subprocess.CompletedProcess(list(argv), returncode, stdout, stderr)


def _tree_id(repository: RepositoryState) -> str:
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


def _ignored_paths(root: Path, repository: RepositoryState) -> set[str]:
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
    return {
        relative
        for relative in _worktree_paths(root) - repository.staged.keys()
        if _path_is_ignored(root, relative, root_patterns=patterns)
    }


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


def _run_repository_command(
    root: Path,
    repository: RepositoryState,
    argv: Sequence[str],
    command: tuple[str, ...],
    *,
    input_text: str | None,
) -> subprocess.CompletedProcess[str]:
    """Return one result for a command against initialized fake state."""
    if command == ("check-ignore", "-z", "--stdin"):
        return _run_check_ignore_stdin(root, repository, argv, input_text or "")
    handlers = {
        "add": _run_add,
        "cat-file": _run_cat_file,
        "check-ignore": _run_check_ignore,
        "commit": _run_commit,
        "diff": _run_diff,
        "hash-object": _run_hash_object,
        "ls-files": _run_ls_files,
        "rev-parse": _run_rev_parse,
        "restore": _run_restore,
        "write-tree": _run_write_tree,
    }
    handler = handlers.get(command[0], _run_unsupported)
    return handler(root, repository, argv, command)


def _run_rev_parse(
    _root: Path,
    _repository: RepositoryState,
    argv: Sequence[str],
    command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    """Confirm the bounded repository for activation validation."""
    if command == ("rev-parse", "--is-inside-work-tree"):
        return _completed(argv, stdout="true\n")
    return _run_unsupported(_root, _repository, argv, command)


def _run_add(
    root: Path,
    repository: RepositoryState,
    argv: Sequence[str],
    command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    """Stage current file bytes, expanding bounded directory arguments."""
    for value in command[1:]:
        if value == "--":
            continue
        candidate = root / value
        paths = candidate.rglob("*") if candidate.is_dir() else (candidate,)
        for path in paths:
            if path.is_file() and ".git" not in path.relative_to(root).parts:
                repository.staged[path.relative_to(root).as_posix()] = path.read_bytes()
    return _completed(argv)


def _run_commit(
    _root: Path,
    repository: RepositoryState,
    argv: Sequence[str],
    _command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    """Record the current fake index as the committed baseline."""
    repository.committed = dict(repository.staged)
    return _completed(argv)


def _run_diff(
    _root: Path,
    repository: RepositoryState,
    argv: Sequence[str],
    command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    """List paths whose staged bytes differ from the committed baseline."""
    if command[1:] != ("--cached", "--name-only"):
        return _run_unsupported(_root, repository, argv, command)
    paths = sorted(
        relative
        for relative in repository.staged.keys() | repository.committed.keys()
        if repository.staged.get(relative) != repository.committed.get(relative)
    )
    return _completed(argv, stdout="".join(f"{path}\n" for path in paths))


def _run_restore(
    _root: Path,
    repository: RepositoryState,
    argv: Sequence[str],
    command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    """Restore selected fake index paths from the committed baseline."""
    if command[1:2] != ("--staged",):
        return _run_unsupported(_root, repository, argv, command)
    for relative in command[2:]:
        if relative in repository.committed:
            repository.staged[relative] = repository.committed[relative]
        else:
            repository.staged.pop(relative, None)
    return _completed(argv)


def _run_write_tree(
    _root: Path,
    repository: RepositoryState,
    argv: Sequence[str],
    _command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    """Return the fake index tree identity."""
    return _completed(argv, stdout=f"{_tree_id(repository)}\n")


def _run_hash_object(
    root: Path,
    repository: RepositoryState,
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
    repository: RepositoryState,
    argv: Sequence[str],
    command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    """Return one stored fake blob."""
    return _completed(argv, stdout=repository.blobs[command[2]])


def _run_ls_files(
    root: Path,
    repository: RepositoryState,
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


def _tracked_below(staged: Mapping[str, bytes], relative: str) -> tuple[str, ...]:
    """Return stable tracked paths at or below one portable directory."""
    prefix = relative.rstrip("/")
    return tuple(
        sorted(path for path in staged if path == prefix or path.startswith(f"{prefix}/")),
    )


def _run_check_ignore(
    root: Path,
    _repository: RepositoryState,
    argv: Sequence[str],
    command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    """Check one path against root and home-local ignore files."""
    returncode = 0 if _path_is_ignored(root, command[-1]) else 1
    return _completed(argv, returncode)


def _run_check_ignore_stdin(
    root: Path,
    _repository: RepositoryState,
    argv: Sequence[str],
    input_text: str,
) -> subprocess.CompletedProcess[str]:
    """Return every NUL-delimited stdin path covered by ignore patterns."""
    paths = tuple(path for path in input_text.split("\0") if path)
    matched = tuple(path for path in paths if _path_is_ignored(root, path))
    return _completed(
        argv,
        0 if matched else 1,
        stdout="".join(f"{path}\0" for path in matched),
    )


def _run_unsupported(
    _root: Path,
    _repository: RepositoryState,
    argv: Sequence[str],
    command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    """Reject a Git command outside the bounded test vocabulary."""
    return _completed(argv, 129, stderr=f"unsupported fake Git command: {command}")
