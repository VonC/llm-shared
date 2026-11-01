"""Generate Unicode text without Hypothesis's Unicode category tables.

``scalar_text`` draws integers and maps them onto every Unicode scalar value
(every code point except the surrogate block), minus any declared characters
below that block. This is the domain of ``characters`` excluding category
``Cs`` and those characters. It avoids the per-process category-table load
that otherwise lands, as cold CPU and garbage collection, on whichever test
first draws default-alphabet text. A low-range branch keeps ASCII-heavy values
common, as ``characters`` does; length bounds are passed through unchanged.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from hypothesis import strategies as st

if TYPE_CHECKING:
    from hypothesis.strategies import SearchStrategy

SURROGATE_FIRST = 0xD800
SURROGATE_COUNT = 0xE000 - SURROGATE_FIRST
LAST_SCALAR = 0x10FFFF
_ASCII_LAST = 0x7F


def last_index(skipped: tuple[int, ...] = ()) -> int:
    """Return the highest index ``scalar_character`` accepts for ``skipped``."""
    return LAST_SCALAR - SURROGATE_COUNT - len(skipped)


def scalar_character(index: int, skipped: tuple[int, ...] = ()) -> str:
    """Map an index onto the allowed scalar values, in code point order.

    Args:
        index: A rank from 0 to ``last_index(skipped)``.
        skipped: Ascending code points below the surrogate block to omit.

    Returns:
        The allowed character holding that rank.
    """
    code = index
    for skip in skipped:
        if code >= skip:
            code += 1
    if code >= SURROGATE_FIRST:
        code += SURROGATE_COUNT
    return chr(code)


def scalar_text(*, min_size: int = 0, max_size: int | None = None, exclude: str = "") -> SearchStrategy[str]:
    """Draw text over every scalar value except ``exclude``.

    Args:
        min_size: The minimum number of characters.
        max_size: The maximum number of characters, unbounded when ``None``.
        exclude: Characters below the surrogate block to omit from the domain.

    Returns:
        A strategy with the same domain as ``text(characters(...))``.

    Raises:
        ValueError: When an excluded character is not below the surrogate block.
    """
    skipped = tuple(sorted({ord(character) for character in exclude}))
    if any(code >= SURROGATE_FIRST for code in skipped):
        message = "excluded characters must lie below the surrogate block"
        raise ValueError(message)
    ascii_last = _ASCII_LAST - sum(code <= _ASCII_LAST for code in skipped)

    def character(index: int) -> str:
        return scalar_character(index, skipped)

    indexes = st.one_of(st.integers(0, ascii_last), st.integers(0, last_index(skipped)))
    return st.lists(indexes.map(character), min_size=min_size, max_size=max_size).map("".join)


# eof
