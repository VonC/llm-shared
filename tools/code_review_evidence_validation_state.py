"""Capture and compare validation effects for explicit repository paths.

This split keeps repository enumeration out of retained-manifest evidence and
holds validation cost to the caller-named staged, repair, and artifact paths.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

from tools.code_review_evidence_common import (
    SHA256_RE as _SHA256_RE,
)
from tools.code_review_evidence_common import (
    TREE_OBJECT_RE as _TREE_OBJECT_RE,
)
from tools.code_review_evidence_common import (
    payload_path as _payload_path,
)
from tools.code_review_evidence_common import (
    relative_path as _relative_path,
)
from tools.code_review_evidence_common import (
    repository_root as _repository_root,
)
from tools.code_review_evidence_common import (
    run_git_evidence as _git,
)
from tools.code_review_evidence_common import (
    unique_paths as _unique_paths,
)
from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass(frozen=True)
class FileDigest:
    """Content identity for one repository-relative validation path."""

    path: str
    digest: str | None

    def to_payload(self) -> dict[str, object]:
        """Return the JSON-safe file digest representation."""
        return {"path": self.path, "digest": self.digest}

    @classmethod
    def from_payload(cls, payload: object) -> FileDigest:
        """Build one file digest from strict JSON-safe data."""
        if not isinstance(payload, dict):
            raise ReviewExchangeError("file digest must be an object")
        data = cast("dict[str, object]", payload)
        path = _payload_path(data.get("path"), "file digest path")
        digest = data.get("digest")
        if digest is not None and (
            not isinstance(digest, str) or _SHA256_RE.fullmatch(digest) is None
        ):
            raise ReviewExchangeError("file digest value is invalid")
        return cls(path, digest)


def _file_digest_group(data: dict[str, object], name: str) -> tuple[FileDigest, ...]:
    items = data.get(name)
    if not isinstance(items, list):
        raise ReviewExchangeError(f"validation state {name} is invalid")
    return tuple(FileDigest.from_payload(item) for item in cast("list[object]", items))


@dataclass(frozen=True)
class ValidationState:
    """Index and explicit-path identities around mandatory validation."""

    index_tree: str
    paths: tuple[str, ...]
    tracked_files: tuple[FileDigest, ...]
    ignored_files: tuple[FileDigest, ...]
    untracked_files: tuple[FileDigest, ...]

    def to_payload(self) -> dict[str, object]:
        """Return the JSON-safe validation-state representation."""
        return {
            "index_tree": self.index_tree,
            "paths": list(self.paths),
            "tracked_files": [item.to_payload() for item in self.tracked_files],
            "ignored_files": [item.to_payload() for item in self.ignored_files],
            "untracked_files": [item.to_payload() for item in self.untracked_files],
        }

    @classmethod
    def from_payload(cls, payload: object) -> ValidationState:
        """Build a validation state from strict path-bounded JSON data."""
        if not isinstance(payload, dict):
            raise ReviewExchangeError("validation state must be an object")
        data = cast("dict[str, object]", payload)
        tree = data.get("index_tree")
        if not isinstance(tree, str) or _TREE_OBJECT_RE.fullmatch(tree) is None:
            raise ReviewExchangeError("validation state index tree is invalid")
        raw_paths = data.get("paths")
        if not isinstance(raw_paths, list):
            raise ReviewExchangeError("validation state paths are invalid")
        paths = _unique_paths(cast("list[object]", raw_paths), "validation state path")
        groups = tuple(
            _file_digest_group(data, name)
            for name in ("tracked_files", "ignored_files", "untracked_files")
        )
        evidence_paths = tuple(item.path for group in groups for item in group)
        inconsistent = len(set(evidence_paths)) != len(evidence_paths)
        if inconsistent or not set(evidence_paths) <= set(paths):
            raise ReviewExchangeError("validation state file paths are inconsistent")
        return cls(tree, paths, *groups)


@dataclass(frozen=True)
class ValidationStateComparison:
    """Classified explicit-path differences produced by validation commands."""

    tracked_paths: tuple[str, ...]
    ignored_paths: tuple[str, ...]
    untracked_paths: tuple[str, ...]

    @property
    def acceptable(self) -> bool:
        """Return whether differences are confined to ignored artifacts."""
        return not self.tracked_paths and not self.untracked_paths

    def to_payload(self) -> dict[str, object]:
        """Return the JSON-safe validation comparison representation."""
        return {
            "acceptable": self.acceptable,
            "tracked_paths": list(self.tracked_paths),
            "ignored_paths": list(self.ignored_paths),
            "untracked_paths": list(self.untracked_paths),
        }


def _digest_path(root: Path, relative: str) -> FileDigest:
    path = root / Path(relative)
    digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return FileDigest(relative, digest)


def _listed_path_set(
    root: Path,
    arguments: tuple[str, ...],
    paths: tuple[str, ...],
) -> set[str]:
    pathspecs = tuple(f":(literal){path}" for path in paths)
    output = _git(root, (*arguments, "--", *pathspecs)).stdout
    return {path for path in output.split("\0") if path}


def _selected_digests(
    root: Path,
    paths: tuple[str, ...],
    members: set[str],
) -> tuple[FileDigest, ...]:
    return tuple(_digest_path(root, path) for path in paths if path in members)


def _validation_paths(
    root: Path,
    paths: Iterable[str | Path],
) -> tuple[str, ...]:
    resolved = tuple(_relative_path(root, path) for path in paths)
    selected = tuple(dict.fromkeys(relative for relative, _candidate in resolved))
    if not selected:
        raise ReviewExchangeError("validation state requires explicit paths")
    if any(candidate.is_dir() for _relative, candidate in resolved):
        raise ReviewExchangeError("validation state paths must name files")
    return selected


def capture_validation_paths(
    repository: str | Path,
    paths: Iterable[str | Path],
    index_tree: str,
) -> ValidationState:
    """Capture content identities only for the caller's explicit path scope."""
    root = _repository_root(repository)
    selected = _validation_paths(root, paths)
    tracked = _listed_path_set(root, ("ls-files", "-z"), selected)
    ignored = _listed_path_set(
        root,
        ("ls-files", "--others", "--ignored", "--exclude-standard", "-z"),
        selected,
    )
    untracked = _listed_path_set(
        root,
        ("ls-files", "--others", "--exclude-standard", "-z"),
        selected,
    )
    return ValidationState(
        index_tree,
        selected,
        _selected_digests(root, selected, tracked),
        _selected_digests(root, selected, ignored),
        _selected_digests(root, selected, untracked),
    )


def _changed_paths(
    before: tuple[FileDigest, ...],
    after: tuple[FileDigest, ...],
) -> tuple[str, ...]:
    before_map = {item.path: item.digest for item in before}
    after_map = {item.path: item.digest for item in after}
    ordered_paths = dict.fromkeys((*before_map, *after_map))
    return tuple(
        path
        for path in ordered_paths
        if before_map.get(path) != after_map.get(path)
    )


def compare_validation_state(
    before: ValidationState,
    after: ValidationState,
) -> ValidationStateComparison:
    """Classify side effects without staging, reverting, or relabeling."""
    if before.paths != after.paths:
        raise ReviewExchangeError("validation state paths disagree")
    tracked = list(_changed_paths(before.tracked_files, after.tracked_files))
    if before.index_tree != after.index_tree:
        tracked.append("<index>")
    return ValidationStateComparison(
        tuple(tracked),
        _changed_paths(before.ignored_files, after.ignored_files),
        _changed_paths(before.untracked_files, after.untracked_files),
    )


__all__ = [
    "FileDigest",
    "ValidationState",
    "ValidationStateComparison",
    "capture_validation_paths",
    "compare_validation_state",
]


# eof
