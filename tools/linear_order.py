"""Lexicographically order strings in linear input size using UTF-8 radix buckets.

Group membership and exclusion listings need stable order without adding a
comparison sort to the response path. Each trie edge is one byte; branching
visits at most 256 buckets, a constant independent of the number of strings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass
class _Node:
    """One byte-prefix bucket, retaining duplicates at its terminal node."""

    children: dict[int, _Node] = field(default_factory=dict[int, "_Node"])
    values: list[str] = field(default_factory=list[str])


def ordered_strings(values: Iterable[str]) -> tuple[str, ...]:
    """Return strings in Unicode lexical order with a bounded-alphabet trie.

    Args:
        values: Arbitrarily ordered strings; duplicate values are preserved.

    Returns:
        The lexically ordered values, without recursion or a comparison sort.
    """
    root = _Node()
    for value in values:
        node = root
        for byte in value.encode("utf-8", errors="surrogatepass"):
            child = node.children.get(byte)
            if child is None:
                child = _Node()
                node.children[byte] = child
            node = child
        node.values.append(value)
    result: list[str] = []
    pending = [root]
    while pending:
        node = pending.pop()
        result.extend(node.values)
        if len(node.children) < 2:  # noqa: PLR2004
            pending.extend(node.children.values())
        else:
            pending.extend(node.children[byte] for byte in range(255, -1, -1) if byte in node.children)
    return tuple(result)


# eof
