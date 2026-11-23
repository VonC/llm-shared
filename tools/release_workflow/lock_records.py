"""Decode strict JSON records shared by every lock, owner, entry and trust kind.

Step 1 of v0.14.0 git-cliff-provisioning moves these rules out of
`operation_lock.py` (plan decision Q02): a repeated key is ambiguous and
refused instead of trusting the last one, a record is always a JSON object,
counters and identities are positive integers (booleans and numeric strings
refused), and text fields must be present strings. Each rule names the
caller's label, so the operation lock keeps its `owner` messages while the
git-cliff cache lock record, owner file, entry record and trust record use
their own. The decoded object keeps the exact keys of the document, so each
record kind compares them with the key set it expects.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Callable


def _unique_fields(label: str) -> Callable[[list[tuple[str, object]]], dict[str, object]]:
    """Build a pairs hook that refuses duplicate keys at every object level."""
    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                msg = f"Duplicate {label} field: {key}"
                raise ValueError(msg)
            result[key] = value
        return result
    return unique


def decode_object(content: bytes, *, label: str) -> dict[str, object]:
    """Decode one JSON object without accepting arbitrary JSON values as records.

    Args:
        content: The complete record bytes, UTF-8 JSON.
        label: The record kind named in every message, such as `owner`.

    Returns:
        The decoded object, with the keys of the document in document order.
    """
    value: object = json.loads(content, object_pairs_hook=_unique_fields(label))
    if not isinstance(value, dict):
        msg = f"{label[:1].upper()}{label[1:]} record is not an object"
        raise TypeError(msg)
    return cast("dict[str, object]", value)


def positive_integer(record: dict[str, object], key: str, *, label: str) -> int:
    """Accept positive integers, rejecting booleans, numeric strings and absence."""
    value = record.get(key)
    if type(value) is not int or value <= 0:
        msg = f"Invalid {label} {key}"
        raise ValueError(msg)
    return value


def text(record: dict[str, object], key: str, *, label: str) -> str:
    """Require an explicitly present string even when an empty value is allowed."""
    value = record.get(key)
    if not isinstance(value, str):
        msg = f"Invalid {label} {key}"
        raise TypeError(msg)
    return value


# eof
