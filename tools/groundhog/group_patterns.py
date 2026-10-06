"""Compile group globs once and apply ordered inclusion and exclusion rules.

Python's recursive glob translator supplies segment-aware wildcards. A
slash-free pattern matches a name at any depth. Every pattern matching a
directory includes its descendants, including anchored and slashed rules;
later matching rules override earlier ones.
"""

from __future__ import annotations

import glob
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence


@dataclass(frozen=True)
class Pattern:
    """One compiled glob with its inclusion or exclusion decision."""

    expression: re.Pattern[str]
    include: bool


def normalized_patterns(lines: Iterable[str]) -> tuple[str, ...]:
    """Normalize declaration whitespace and path separators, retaining rule order.

    Args:
        lines: One pattern per line, with optional blank and comment lines.

    Returns:
        The effective pattern sequence.
    """
    return tuple(line.strip().replace("\\", "/") for line in lines
                 if line.strip() and not line.lstrip().startswith("#"))


def compile_patterns(lines: Iterable[str]) -> tuple[Pattern, ...]:
    """Compile ordered gitignore-style group rules.

    Args:
        lines: The declaration's pattern lines.

    Returns:
        Precompiled rules to reuse for every candidate path.
    """
    result: list[Pattern] = []
    for line in normalized_patterns(lines):
        include = not line.startswith("!")
        pattern = line if include else line[1:]
        anchored = pattern.startswith("/")
        pattern = pattern.lstrip("/")
        directory = pattern.endswith("/")
        pattern = pattern.rstrip("/")
        basename = "/" not in pattern and not anchored
        if basename:
            pattern = f"**/{pattern}"
        if directory:
            pattern += "/**"
        expression = glob.translate(pattern, recursive=True, include_hidden=True, seps="/")
        if not directory:
            # The translated end anchor is replaced with a descendant suffix:
            # a rule matches a directory as well as a final filename.
            expression = expression[:-2] + r"(?:/.*)?\Z"
        result.append(Pattern(re.compile(expression), include))
    return tuple(result)


def matches(compiled: Sequence[Pattern], relative_posix_path: str) -> bool:
    """Apply the last matching rule to a normalized repository-relative path.

    Args:
        compiled: The precompiled declaration rules.
        relative_posix_path: A path with forward slash separators.

    Returns:
        Whether the path is included after all matching rules.
    """
    included = False
    for rule in compiled:
        if rule.expression.fullmatch(relative_posix_path):
            included = rule.include
    return included


# eof
