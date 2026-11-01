"""Property checks preserve arbitrary native and UTF-8 payloads without shell parsing.

Payloads come from ``tests.scalar_text``: every Unicode scalar value except NUL,
the same domain as ``characters`` excluding category ``Cs`` and NUL, without
loading Hypothesis's Unicode category tables on first use. Unbounded length and
example budgets are unchanged.
"""

from __future__ import annotations

import io
from unittest.mock import patch

import pytest
from hypothesis import given, settings

from tests.scalar_text import scalar_text
from tools.release_workflow import cli
from tools.release_workflow.inputs import read_payload
from tools.release_workflow.invocation import validate_arguments

_TEXT = scalar_text(exclude="\0")


@pytest.mark.parametrize("_batch", range(20))
@settings(max_examples=5)
@given(_TEXT)
def test_native_values_remain_data(_batch: int, value: str) -> None:
    """The equals spelling disambiguates free text that starts with an option."""
    arguments = ["probe", f"--text={value}"]
    validate_arguments("explicit-native", tuple(arguments))
    _, request = cli._parse(arguments)
    assert read_payload(None, use_stdin=False, text=request.text, source="native", required=True, non_interactive=True) == value


@pytest.mark.parametrize("_batch", range(20))
@settings(max_examples=5)
@given(_TEXT)
def test_utf8_stdin_remains_data(_batch: int, value: str) -> None:
    """Unicode and newline values survive strict byte decoding independently of locale."""
    stream = io.TextIOWrapper(io.BytesIO(value.encode("utf-8")), encoding="ascii")
    with patch("sys.stdin", stream):
        assert read_payload(None, use_stdin=True, text=None, source="stdin", required=True, non_interactive=True) == value

# eof
