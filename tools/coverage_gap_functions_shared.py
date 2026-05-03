"""Shared helpers for coverage gap analysis.

Fix: Split the data model, project-root lookup, and coverage.json parsing out
of `tools.coverage_gap_functions` so the script hub stays below the repo's big
file guard while keeping the same behavior.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, TypeGuard, cast

if TYPE_CHECKING:
    import ast
    from pathlib import Path

ROOT_MARKERS_DIR: tuple[str, ...] = (".git",)
ROOT_MARKERS_FILE: tuple[str, ...] = (
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "tox.ini",
)
POST_COVERAGE_LINES: tuple[str, ...] = (
    "Make sure check.bat is passing, it can be called from anywhere, Python venv is already activated.",
    "Make sure affected tests are passing.",
    "Prefer `pytest --testmon --cov-append --no-header --cov-report term-missing:skip-covered test_file1.py test_file2.py ...`",
    "to run affected test while preserving existing coverage reports.",
)

# ----------------------------
# Exceptions
# ----------------------------


class CoverageGapError(Exception):
    """Base exception for this tool."""


class InvalidRangeError(CoverageGapError, ValueError):
    """Raised when a line range cannot be parsed."""

    def __init__(self, raw: str) -> None:
        """Create an InvalidRangeError for the raw range string provided by the user."""
        msg = f"Invalid range {raw!r} (expected N or N-M)"
        super().__init__(msg)


class InputFileNotFoundError(CoverageGapError, FileNotFoundError):
    """Raised when the target Python file cannot be located."""

    def __init__(self, file_path: Path) -> None:
        """Create an InputFileNotFoundError for a missing target source file."""
        msg = f"File not found: {file_path}"
        super().__init__(msg)


class CoverageJsonNotFoundError(CoverageGapError, FileNotFoundError):
    """Raised when the coverage JSON file cannot be located."""

    def __init__(self, json_path: Path) -> None:
        """Create a CoverageJsonNotFoundError for a missing coverage JSON file."""
        msg = f"Coverage JSON not found: {json_path}"
        super().__init__(msg)


class CoverageJsonFormatError(CoverageGapError):
    """Raised when coverage.json does not match the expected structure."""

    def __init__(self, detail: str) -> None:
        """Create a CoverageJsonFormatError describing the invalid coverage.json structure."""
        msg = f"coverage.json format error: {detail}"
        super().__init__(msg)


class CoverageJsonFileMatchError(CoverageGapError):
    """Raised when matching a file entry in coverage.json fails."""

    def __init__(self, detail: str) -> None:
        """Create a CoverageJsonFileMatchError describing why file matching failed."""
        msg = f"coverage.json file match error: {detail}"
        super().__init__(msg)


# ----------------------------
# Data model
# ----------------------------


@dataclass(frozen=True, order=True)
class LineRange:
    """A 1-based inclusive line range."""

    start: int
    end: int

    @classmethod
    def parse(cls, raw: str) -> LineRange:
        """Parse 'N' or 'N-M' into a LineRange."""
        if re.fullmatch(r"\d+,?", raw):
            # remove , from raw
            raw = raw.rstrip(",")
            n = int(raw)
            return cls(n, n)

        match = re.fullmatch(r"(\d+)-(\d+),?", raw)
        if match is None:
            raise InvalidRangeError(raw)

        raw = raw.rstrip(",")
        a = int(match.group(1))
        b = int(match.group(2))
        if b < a:
            a, b = b, a
        return cls(a, b)

    def covers(self, start: int, end: int) -> bool:
        """Return True if this range fully covers [start, end]."""
        return self.start <= start and self.end >= end


@dataclass(frozen=True)
class FuncInfo:
    """Information about a discovered function/method."""

    qualname: str
    start: int
    end: int
    node: ast.AST
    is_method: bool


@dataclass(frozen=True)
class Detail:
    """Extra detail for a partial uncovered range."""

    kind: Literal["branch", "code"]
    text: str


@dataclass(frozen=True)
class BranchBlock:
    """A block of lines corresponding to a branch-like structure."""

    label: str
    start: int
    end: int

    def contains(self, line: int) -> bool:
        """Return True if 'line' is within this block."""
        return self.start <= line <= self.end

    @property
    def size(self) -> int:
        """Block size in lines (inclusive end not accounted; used for ordering)."""
        return self.end - self.start


# ----------------------------
# Project root detection
# ----------------------------


def find_project_root(start: Path) -> Path:
    """Scan upward for project root markers and return the discovered root path."""
    cur = start.resolve()
    while True:
        for d in ROOT_MARKERS_DIR:
            if (cur / d).is_dir():
                return cur
        for f in ROOT_MARKERS_FILE:
            if (cur / f).is_file():
                return cur
        if cur == cur.parent:
            return start.resolve()
        cur = cur.parent


# ----------------------------
# Coverage JSON helpers
# ----------------------------


def compress_lines_to_ranges(lines: list[int]) -> list[LineRange]:
    """Compress a list of line numbers into consecutive LineRanges."""
    if not lines:
        return list[LineRange]()
    sorted_lines = sorted(set(lines))
    out: list[LineRange] = []

    start = prev = sorted_lines[0]
    for n in sorted_lines[1:]:
        if n == prev + 1:
            prev = n
            continue
        out.append(LineRange(start, prev))
        start = prev = n
    out.append(LineRange(start, prev))
    return out


def _is_obj_dict(obj: object) -> TypeGuard[dict[object, object]]:
    """Narrow an arbitrary object to a plain dict with object keys/values."""
    return isinstance(obj, dict)


def _ensure_dict(obj: object, ctx: str) -> dict[object, object]:
    """Return obj as a dict[object, object], or raise with context."""
    if _is_obj_dict(obj):
        return obj
    msg = f"{ctx} is not a dict"
    raise CoverageJsonFormatError(msg)


def _ensure_str_dict(obj: object, ctx: str) -> dict[str, object]:
    """Return obj as a dict[str, object] after validating all keys are strings."""
    d = _ensure_dict(obj, ctx)
    for k in d:
        if not isinstance(k, str):
            msg = f"{ctx} has a non-string key: {k!r}"
            raise CoverageJsonFormatError(msg)
    return cast("dict[str, object]", d)


def _ensure_str_obj_dict(obj: object, ctx: str) -> dict[str, object]:
    """Return obj as dict[str, object] after validating keys are strings."""
    d = _ensure_dict(obj, ctx)
    for k in d:
        if not isinstance(k, str):
            msg = f"{ctx} has a non-string key: {k!r}"
            raise CoverageJsonFormatError(msg)
    return cast("dict[str, object]", d)


def _is_obj_list(obj: object) -> TypeGuard[list[object]]:
    """Return True if obj is a list (treated as list[object] for typing purposes)."""
    return isinstance(obj, list)


def _read_text_or_raise(path: Path) -> str:
    """Read a UTF-8 text file or raise CoverageJsonNotFoundError."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as err:
        raise CoverageJsonNotFoundError(path) from err


def _parse_json_root_obj(text: str) -> dict[object, object]:
    """Parse JSON text and return the root object as dict[object, object]."""
    try:
        parsed: object = json.loads(text)
    except json.JSONDecodeError as err:
        msg = "invalid JSON"
        raise CoverageJsonFormatError(msg) from err
    return _ensure_dict(parsed, "root")


def _normalize_rel_path(p: str) -> str:
    """Normalize a relative path for suffix matching in coverage.json."""
    return p.replace("\\", "/").lstrip("./")


def _find_matching_file_entries(
    files: dict[str, object],
    target_norm: str,
) -> list[tuple[str, dict[str, object]]]:
    """Return all coverage.json file entries matching the normalized target path."""
    matches: list[tuple[str, dict[str, object]]] = []
    for key, value in files.items():
        key_norm = key.replace("\\", "/")
        if key_norm == target_norm or key_norm.endswith("/" + target_norm):
            matches.append((key, _ensure_str_obj_dict(value, f"root.files[{key!r}]")))
    return matches


def _pick_single_file_entry(
    matches: list[tuple[str, dict[str, object]]],
    *,
    target_rel_file: str,
    coverage_json_path: Path,
) -> dict[str, object]:
    """Pick exactly one match or raise CoverageJsonFileMatchError."""
    if not matches:
        msg = f"no entry for {target_rel_file!r} in {coverage_json_path}"
        raise CoverageJsonFileMatchError(msg)

    if len(matches) > 1:
        keys = "\n".join(f"  - {match[0]}" for match in matches)
        msg = (
            f"ambiguous match for {target_rel_file!r} in {coverage_json_path}:\n{keys}"
        )
        raise CoverageJsonFileMatchError(msg)

    return matches[0][1]


def _extract_missing_lines(file_entry: dict[str, object]) -> list[int]:
    """Extract and validate missing_lines as list[int] from a file entry."""
    missing_obj = file_entry.get("missing_lines", [])
    if not _is_obj_list(missing_obj):
        msg = "missing_lines is not a list"
        raise CoverageJsonFormatError(msg)

    missing_lines: list[int] = []
    for item in missing_obj:
        if not isinstance(item, int):
            msg = "missing_lines contains a non-integer item"
            raise CoverageJsonFormatError(msg)
        missing_lines.append(item)
    return missing_lines


def load_missing_ranges_from_coverage_json(
    coverage_json_path: Path,
    target_rel_file: str,
) -> list[LineRange]:
    """Load missing line ranges for a given file entry in coverage.json."""
    text = _read_text_or_raise(coverage_json_path)
    root_obj = _parse_json_root_obj(text)

    files = _ensure_str_dict(root_obj.get("files"), "root.files")
    target_norm = _normalize_rel_path(target_rel_file)

    matches = _find_matching_file_entries(files, target_norm)
    file_entry = _pick_single_file_entry(
        matches,
        target_rel_file=target_rel_file,
        coverage_json_path=coverage_json_path,
    )

    missing_lines = _extract_missing_lines(file_entry)
    return compress_lines_to_ranges(missing_lines)


__all__ = [
    "POST_COVERAGE_LINES",
    "ROOT_MARKERS_DIR",
    "ROOT_MARKERS_FILE",
    "BranchBlock",
    "CoverageGapError",
    "CoverageJsonFileMatchError",
    "CoverageJsonFormatError",
    "CoverageJsonNotFoundError",
    "Detail",
    "FuncInfo",
    "InputFileNotFoundError",
    "InvalidRangeError",
    "LineRange",
    "_ensure_dict",
    "_ensure_str_dict",
    "_ensure_str_obj_dict",
    "_extract_missing_lines",
    "_find_matching_file_entries",
    "_is_obj_dict",
    "_is_obj_list",
    "_normalize_rel_path",
    "_parse_json_root_obj",
    "_pick_single_file_entry",
    "_read_text_or_raise",
    "compress_lines_to_ranges",
    "find_project_root",
    "load_missing_ranges_from_coverage_json",
]


# eof
