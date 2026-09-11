"""Bounded repository readers for review-mode documentation acceptance.

The helpers inspect only paths supplied by a test, ignore external URLs, and
resolve each local target once. Fragment checks compare links with headings in
the resolved target instead of serving or copying the documentation tree. The
final evidence checks select one exact Markdown table row without scanning any
undeclared file.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import unquote

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

_MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
_EXTERNAL_PREFIXES = ("http://", "https://", "mailto:")
_MARKDOWN_SUFFIX = ".md"
_EMOJI_FRAGMENT_PREFIX = "-"
_EXPLANATION = "wiki/explanation/independent-review-mode-and-human-authority.md"
_SELF_REVIEW_EXPLANATION = "wiki/explanation/why-the-llm-reviews-its-own-work.md"
_SELF_REVIEW_HOW_TO = "wiki/how-to/answer-a-review-round.md"
_COVERAGE = "docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md"
_SPEC_TUTORIAL = "wiki/tutorials/09-run-your-first-specification-review.md"
_CODE_TUTORIAL = "wiki/tutorials/10-run-your-first-implementation-code-review.md"
_HOW_TO_GUIDES = (
    "wiki/how-to/enable-independent-review-mode.md",
    "wiki/how-to/run-specification-review.md",
    "wiki/how-to/run-implementation-code-review.md",
    "wiki/how-to/read-independent-review-results-and-continue.md",
    "wiki/how-to/recover-an-independent-review.md",
)
_REFERENCE = "wiki/reference/independent-review-mode-contract.md"
_INVENTORY_CANDIDATES = (
    "wiki/reference/skills-catalog.md",
    "wiki/reference/artifact-files.md",
    "wiki/reference/aliases-and-launchers.md",
    "wiki/reference/templates.md",
    "wiki/reference/automation-and-direct-invocation.md",
    "wiki/reference/repository-layout.md",
)


def assert_contains(markdown: str, values: tuple[str, ...]) -> None:
    """Assert one bounded Markdown value contains every declared token."""
    for value in values:
        assert value in markdown


def repository_root() -> Path:
    """Return the repository root from this fixed test-package location."""
    return Path(__file__).resolve().parents[4]


def read_declared(root: Path, relative_path: str) -> str:
    """Read one declared repository-relative UTF-8 file."""
    path = (root / relative_path).resolve()
    path.relative_to(root.resolve())
    return path.read_text(encoding="utf-8")


def markdown_table_row(markdown: str, key: str) -> str:
    """Return the sole Markdown table row whose first cell matches a key."""
    prefix = f"| {key} |"
    rows = tuple(line for line in markdown.splitlines() if line.startswith(prefix))
    assert len(rows) == 1, f"expected one table row for {key}, found {len(rows)}"
    return rows[0]


def _heading_slug(heading: str) -> str:
    """Return the GitHub-style fragment used by the documentation links."""
    plain = re.sub(r"[^\w\- ]", "", heading.casefold())
    return re.sub(r"[ -]+", "-", plain.strip())


def _local_targets(markdown: str) -> Iterator[str]:
    """Yield local targets while discarding external Markdown URLs."""
    for raw_target in _MARKDOWN_LINK.findall(markdown):
        target = raw_target.split(maxsplit=1)[0].strip("<>")
        if not target.startswith(_EXTERNAL_PREFIXES):
            yield target


def _resolve_target(root: Path, source: Path, target: str) -> tuple[Path, str]:
    """Resolve one local target within the repository and return its fragment."""
    path_part, _separator, fragment = target.partition("#")
    destination = (
        source if not path_part else (source.parent / unquote(path_part)).resolve()
    )
    destination.relative_to(root)
    return destination, fragment


def _assert_fragment(destination: Path, fragment: str, source_name: str) -> None:
    """Assert a Markdown fragment names a heading in the resolved target."""
    if not fragment or destination.suffix.casefold() != _MARKDOWN_SUFFIX:
        return
    headings = {
        _heading_slug(value)
        for value in _HEADING.findall(destination.read_text(encoding="utf-8"))
    }
    headings.update(_EMOJI_FRAGMENT_PREFIX + value for value in tuple(headings) if value)
    assert unquote(fragment).casefold() in headings, (
        f"{source_name}: missing fragment {fragment}"
    )


def assert_local_links(root: Path, relative_paths: Iterable[str]) -> None:
    """Assert every local Markdown link in the declared pages resolves."""
    resolved_root = root.resolve()
    for relative_path in relative_paths:
        source = (resolved_root / relative_path).resolve()
        markdown = source.read_text(encoding="utf-8")
        for target in _local_targets(markdown):
            destination, fragment = _resolve_target(resolved_root, source, target)
            assert destination.exists(), (
                f"{relative_path}: missing link target {target}"
            )
            _assert_fragment(destination, fragment, relative_path)


def assert_named_paths(root: Path, relative_paths: Iterable[str]) -> None:
    """Assert every declared repository-relative path exists."""
    resolved_root = root.resolve()
    for relative_path in relative_paths:
        path = (resolved_root / relative_path).resolve()
        path.relative_to(resolved_root)
        assert path.exists(), f"missing named path: {relative_path}"


@pytest.fixture
def docs_root() -> Path:
    """Provide the repository root to bounded documentation assertions."""
    return repository_root()
