"""Closed stdlib marker grammar and release-version interpreter requirements.

Every branch is parsed and checked, including boolean branches whose value is
already known. Marker text is data and is never evaluated as Python code.
"""

from __future__ import annotations

import operator
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

_VARIABLES = frozenset({
    "sys_platform", "os_name", "platform_system", "platform_machine",
    "implementation_name", "python_version", "python_full_version",
})
_VERSIONS = frozenset({"python_version", "python_full_version"})
_OPERATORS = {
    "==": operator.eq, "!=": operator.ne, "<": operator.lt,
    "<=": operator.le, ">": operator.gt, ">=": operator.ge,
}
_TOKEN = re.compile(
    r"\s*(?:(?P<string>'[^'\r\n]*'|\"[^\"\r\n]*\")|"
    r"(?P<word>[a-zA-Z_][a-zA-Z_0-9]*)|(?P<op>==|!=|<=|>=|<|>)|(?P<paren>[()]))",
)
_RELEASE = re.compile(r"[0-9]+(?:\.[0-9]+)*")
_CLAUSE = re.compile(r"(==|!=|<=|>=|<|>)\s*([0-9]+(?:\.[0-9]+)*)")


def release_tuple(value: str) -> tuple[int, ...]:
    """Accept only numeric release components, without wildcard or suffix."""
    if not _RELEASE.fullmatch(value):
        msg = f"Unsupported release version: {value!r}"
        raise ValueError(msg)
    return tuple(int(part) for part in value.split("."))


def _version_compare(left: str, operation: str, right: str) -> bool:
    lhs, rhs = release_tuple(left), release_tuple(right)
    length = max(len(lhs), len(rhs))
    return _OPERATORS[operation](lhs + (0,) * (length - len(lhs)), rhs + (0,) * (length - len(rhs)))


def satisfies(version: str, specifier: str) -> bool:
    """Check every comma-separated clause using padded release tuples."""
    result = True
    for clause in specifier.split(","):
        match = _CLAUSE.fullmatch(clause.strip())
        if match is None:
            msg = f"Unsupported interpreter specifier: {specifier!r}"
            raise ValueError(msg)
        matched = _version_compare(version, match[1], match[2])
        result = result and matched
    return result


class MarkerParser:
    """Consume a marker once with explicit precedence and checked operands."""

    def __init__(self, text: str, environment: Mapping[str, str]) -> None:
        """Tokenize supported input without accepting an unmatched suffix."""
        self.environment = environment
        self.tokens: list[tuple[str, str]] = []
        self.position = 0
        offset = 0
        while offset < len(text):
            match = _TOKEN.match(text, offset)
            if match is None:
                if text[offset:].isspace():
                    break
                msg = f"Unsupported marker syntax near {text[offset:]!r}"
                raise ValueError(msg)
            self.tokens.append((str(match.lastgroup), match.group().strip()))
            offset = match.end()

    def _peek(self) -> str:
        return self.tokens[self.position][1] if self.position < len(self.tokens) else ""

    def _take(self) -> tuple[str, str]:
        if self.position == len(self.tokens):
            msg = "Incomplete marker expression"
            raise ValueError(msg)
        token = self.tokens[self.position]
        self.position += 1
        return token

    def _operand(self) -> tuple[str, bool]:
        kind, value = self._take()
        if kind == "string":
            return value[1:-1], False
        if kind != "word" or value not in _VARIABLES or value not in self.environment:
            msg = f"Unsupported or unavailable marker variable: {value}"
            raise ValueError(msg)
        return self.environment[value], value in _VERSIONS

    def _comparison(self) -> bool:
        left, left_version = self._operand()
        _, operation = self._take()
        if operation == "not":
            if self._take()[1] != "in":
                msg = "Marker 'not' must be followed by 'in'"
                raise ValueError(msg)
            operation = "not in"
        right, right_version = self._operand()
        if operation in {"in", "not in"}:
            return (left in right) if operation == "in" else (left not in right)
        if operation not in _OPERATORS:
            msg = f"Unsupported marker operator: {operation}"
            raise ValueError(msg)
        if left_version or right_version:
            return _version_compare(left, operation, right)
        return _OPERATORS[operation](left, right)

    def _atom(self) -> bool:
        if self._peek() != "(":
            return self._comparison()
        self._take()
        value = self._or()
        if self._take()[1] != ")":
            msg = "Unclosed marker parentheses"
            raise ValueError(msg)
        return value

    def _and(self) -> bool:
        value = self._atom()
        while self._peek() == "and":
            self._take()
            right = self._atom()
            value = value and right
        return value

    def _or(self) -> bool:
        value = self._and()
        while self._peek() == "or":
            self._take()
            right = self._and()
            value = value or right
        return value

    def parse(self) -> bool:
        """Return the boolean result only after consuming the entire marker."""
        result = self._or()
        if self.position != len(self.tokens):
            msg = f"Unexpected marker token: {self._peek()}"
            raise ValueError(msg)
        return result


def evaluate(text: str, environment: Mapping[str, str]) -> bool:
    """Evaluate the supported marker language, rejecting excessive nesting."""
    try:
        return MarkerParser(text, environment).parse()
    except RecursionError as exc:
        msg = "Marker nesting exceeds supported parser depth"
        raise ValueError(msg) from exc


# eof
