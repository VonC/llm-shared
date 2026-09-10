"""Versioned immutable no-growth baseline for Markdown findings."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Never, cast

from tools.markdown_check.policy import MANDATORY_RULES, SUPPORTED_RULES

if TYPE_CHECKING:
    from pathlib import Path

    from tools.markdown_check.models import Finding

_SCHEMA_VERSION = 1


class BaselineError(ValueError):
    """The versioned Markdown allowance file is malformed."""


def _fail(message: str) -> Never:
    """Raise one baseline error without embedding construction at call sites."""
    raise BaselineError(message)


def normalize_repository_path(path: str) -> str:
    """Normalize a non-escaping repository-relative path to forward slashes."""
    candidate = path.replace("\\", "/")
    normalized = PurePosixPath(candidate)
    if not candidate or normalized.is_absolute() or ".." in normalized.parts:
        _fail(f"invalid repository-relative path: {path!r}")
    return normalized.as_posix()


@dataclass(frozen=True, order=True, slots=True)
class BaselineAllowance:
    """One positive aggregate allowance for a path and rule."""

    path: str
    rule: str
    count: int


@dataclass(frozen=True, slots=True)
class BaselineComparison:
    """Growth findings and passing debt-reduction advisories."""

    blocked_findings: tuple[Finding, ...]
    advisories: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Baseline:
    """Immutable first-seen allowance map under schema version 1."""

    allowances: tuple[BaselineAllowance, ...]

    def compare(self, findings: tuple[Finding, ...]) -> BaselineComparison:
        """Fail new or growing keys and advise on every shrinking key."""
        return _compare(self.allowances, findings)


def _compare(
    allowances: tuple[BaselineAllowance, ...],
    findings: tuple[Finding, ...],
) -> BaselineComparison:
    """Compare aggregate counts outside the immutable baseline value."""
    allowed = {(item.path, item.rule): item.count for item in allowances}
    actual = Counter((finding.path, finding.rule) for finding in findings)
    growing = {key for key, count in actual.items() if count > allowed.get(key, 0)}
    blocked = tuple(
        finding for finding in findings if (finding.path, finding.rule) in growing
    )
    advisories = tuple(
        f"{item.path}: {item.rule}: debt-reduced: baseline {item.count}, "
        f"actual {actual.get((item.path, item.rule), 0)}"
        for item in allowances
        if actual.get((item.path, item.rule), 0) < item.count
    )
    return BaselineComparison(blocked, advisories)


def _allowance(value: object) -> BaselineAllowance:
    """Validate and normalize one explicit allowance record."""
    if not isinstance(value, dict):
        _fail("baseline allowances require path, rule, and count")
    record = cast("dict[str, object]", value)
    if set(record) != {"path", "rule", "count"}:
        _fail("baseline allowances require path, rule, and count")
    path, rule, count = record["path"], record["rule"], record["count"]
    if not isinstance(path, str) or not isinstance(rule, str):
        _fail("baseline path and rule must be strings")
    if rule not in SUPPORTED_RULES:
        _fail(f"unsupported baseline rule: {rule}")
    if rule in MANDATORY_RULES:
        _fail(f"mandatory rule {rule} cannot be allowed by the baseline")
    if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
        _fail("baseline count must be a positive integer")
    return BaselineAllowance(normalize_repository_path(path), rule, count)


def load_baseline(path: Path) -> Baseline:
    """Load the strict versioned aggregate allowance document."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        message = f"invalid Markdown baseline: {error}"
        raise BaselineError(message) from error
    if not isinstance(payload, dict):
        _fail("baseline requires version and allowances")
    document = cast("dict[str, object]", payload)
    if set(document) != {"version", "allowances"}:
        _fail("baseline requires version and allowances")
    if document["version"] != _SCHEMA_VERSION or not isinstance(
        document["allowances"],
        list,
    ):
        _fail("unsupported baseline version or allowance list")
    values = cast("list[object]", document["allowances"])
    allowances = tuple(_allowance(value) for value in values)
    keys = tuple((item.path, item.rule) for item in allowances)
    if len(set(keys)) != len(keys):
        _fail("baseline allowance keys must be unique")
    return Baseline(tuple(sorted(allowances)))


__all__ = [
    "Baseline",
    "BaselineAllowance",
    "BaselineComparison",
    "BaselineError",
    "load_baseline",
    "normalize_repository_path",
]


# eof
