"""Strict supported-catalog policy loading for markdown-check."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Never, cast

if TYPE_CHECKING:
    from pathlib import Path

SUPPORTED_RULES = frozenset(
    {
        "MD001",
        "MD009",
        "MD012",
        "MD013",
        "MD024",
        "MD025",
        "MD032",
        "MD033",
        "MD034",
        "MD038",
        "MD040",
        "MD050",
        "LS001",
        "LS002",
        "LS003",
    },
)
MANDATORY_RULES = frozenset({"MD012", "MD024", "MD025"})
_DEFAULT_ENABLED = SUPPORTED_RULES - {"MD013"}


class PolicyError(ValueError):
    """The repository Markdown policy is malformed or unsupported."""


def _fail(message: str) -> Never:
    """Raise one policy error without embedding construction at call sites."""
    raise PolicyError(message)


@dataclass(frozen=True, slots=True)
class MarkdownPolicy:
    """Validated effective catalog and rule-specific options."""

    enabled_rules: frozenset[str]
    allowed_html: frozenset[str]


def _allowed_elements(value: object) -> frozenset[str]:
    """Validate the one supported MD033 option shape."""
    if not isinstance(value, dict):
        _fail("MD033 options must be an object")
    options = cast("dict[str, object]", value)
    if set(options) != {"allowed_elements"}:
        _fail("MD033 options must contain only allowed_elements")
    elements = options["allowed_elements"]
    if not isinstance(elements, list):
        _fail("MD033 allowed_elements must be a list of names")
    candidates = cast("list[object]", elements)
    if any(not isinstance(element, str) or not element for element in candidates):
        _fail("MD033 allowed_elements must be a list of names")
    normalized = tuple(
        cast("str", element).casefold() for element in candidates
    )
    if len(set(normalized)) != len(normalized):
        _fail("MD033 allowed_elements must be unique")
    return frozenset(normalized)


def _apply_setting(
    rule: str,
    value: object,
    enabled: set[str],
) -> frozenset[str] | None:
    """Apply one validated catalog setting and return MD033 options if any."""
    if not isinstance(value, bool):
        if rule == "MD033":
            enabled.add(rule)
            return _allowed_elements(value)
        _fail(f"{rule} accepts only a boolean value")
    if rule in MANDATORY_RULES and not value:
        _fail(f"mandatory rule {rule} cannot be disabled")
    if rule == "MD013" and value:
        _fail("MD013 is catalogued but must remain disabled")
    if value:
        enabled.add(rule)
    else:
        enabled.discard(rule)
    return None


def load_policy(path: Path) -> MarkdownPolicy:
    """Load and validate `.markdownlint.json` before inventory evaluation."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        message = f"invalid Markdown policy: {error}"
        raise PolicyError(message) from error
    if not isinstance(payload, dict):
        _fail("Markdown policy must be a JSON object")
    settings = cast("dict[str, object]", payload)
    unknown = set(settings) - SUPPORTED_RULES
    if unknown:
        _fail(f"unsupported Markdown rules: {sorted(unknown)!r}")
    enabled = set(_DEFAULT_ENABLED)
    allowed_html: frozenset[str] = frozenset()
    for rule, value in settings.items():
        configured_html = _apply_setting(rule, value, enabled)
        if configured_html is not None:
            allowed_html = configured_html
    return MarkdownPolicy(frozenset(enabled), allowed_html)


__all__ = [
    "MANDATORY_RULES",
    "SUPPORTED_RULES",
    "MarkdownPolicy",
    "PolicyError",
    "load_policy",
]


# eof
