"""Prove the strict record rules every lock and record kind shares.

Step 1 of v0.14.0 git-cliff-provisioning moves the decoding helpers of the
operation lock into `lock_records` (plan decision Q02). Each rule names the
caller's label, so the operation lock keeps `Duplicate owner field: pid`; the
decoded object keeps the exact key set of the document, which lets each record
kind compare it with the keys it expects.
"""

from __future__ import annotations

import json

import pytest

from tools.release_workflow.lock_records import decode_object, positive_integer, text

_LARGE = 2**40


@pytest.mark.parametrize("label", ["owner", "cache lock"])
def test_duplicate_keys_are_refused_with_the_caller_label(label: str) -> None:
    """A repeated key is ambiguous, at the top level and in a nested object."""
    with pytest.raises(ValueError, match=rf"^Duplicate {label} field: pid$"):
        decode_object(b'{"pid": 1, "pid": 2}', label=label)
    with pytest.raises(ValueError, match=rf"^Duplicate {label} field: name$"):
        decode_object(b'{"child": {"name": "a", "name": "b"}}', label=label)


@pytest.mark.parametrize("content", [b"[]", b"1", b'"owner"', b"null", b"true"])
def test_a_document_that_is_not_an_object_is_refused(content: bytes) -> None:
    """Arrays, numbers, strings and constants never become records."""
    with pytest.raises(TypeError, match=r"^Owner record is not an object$"):
        decode_object(content, label="owner")
    with pytest.raises(TypeError, match=r"^Entry record is not an object$"):
        decode_object(content, label="entry")


@pytest.mark.parametrize("content", [b"{", b"", b"\xff", b'{"pid": 1} trailing'])
def test_malformed_documents_are_refused(content: bytes) -> None:
    """Truncated JSON, invalid UTF-8 and trailing data fail as value errors."""
    with pytest.raises((json.JSONDecodeError, UnicodeDecodeError)) as caught:
        decode_object(content, label="owner")
    assert isinstance(caught.value, ValueError)


def test_the_decoded_object_keeps_the_exact_document_keys() -> None:
    """No key is dropped, added or reordered, so a record compares its own key set."""
    record = decode_object(b'{"version": 1, "pid": 42, "operation": "x", "extra": null}', label="owner")
    assert list(record) == ["version", "pid", "operation", "extra"]
    assert record.keys() != {"version", "pid", "operation"}
    assert record["extra"] is None


@pytest.mark.parametrize("value", [1, 42, _LARGE])
def test_positive_integers_are_accepted(value: int) -> None:
    """Every integer above zero is returned unchanged."""
    assert positive_integer({"pid": value}, "pid", label="owner") == value


@pytest.mark.parametrize("value", [0, -1, True, False, "42", 42.0, None, [42]])
def test_other_integer_values_are_refused(value: object) -> None:
    """Zero, negatives, booleans, numeric strings, floats and other values are refused."""
    with pytest.raises(ValueError, match=r"^Invalid owner pid$"):
        positive_integer({"pid": value}, "pid", label="owner")


def test_a_missing_integer_is_refused_with_the_label() -> None:
    """An absent key is invalid rather than defaulted."""
    with pytest.raises(ValueError, match=r"^Invalid entry size$"):
        positive_integer({}, "size", label="entry")


@pytest.mark.parametrize("value", ["", "x", "with space"])
def test_present_strings_are_accepted(value: str) -> None:
    """An explicitly present string is returned, even when it is empty."""
    assert text({"handoff": value}, "handoff", label="owner") == value


@pytest.mark.parametrize("record", [{}, {"handoff": None}, {"handoff": 1}, {"handoff": True}, {"handoff": ["x"]}])
def test_missing_or_non_string_text_is_refused(record: dict[str, object]) -> None:
    """Absence, null and every non-string value are refused with the label."""
    with pytest.raises(TypeError, match=r"^Invalid owner handoff$"):
        text(record, "handoff", label="owner")


# eof
