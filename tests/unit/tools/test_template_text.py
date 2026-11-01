"""Shipped template text is read through one replaceable function.

Renderers read their template through ``template_text.read_template`` so the
test suite can reuse immutable template text across scenarios, as it already
reuses CLI grammars. These tests pin the function's own contract: exact UTF-8
text for a real template, and the caller-visible error for a missing one.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools import template_text

_TEMPLATES = Path(__file__).resolve().parents[3] / "templates"


def test_read_template_returns_the_exact_utf8_text() -> None:
    """The returned text equals the file's UTF-8 content."""
    path = _TEMPLATES / "review-code-transcript.template.md"

    assert template_text.read_template(path) == path.read_bytes().decode("utf-8")


def test_read_template_raises_for_a_missing_file() -> None:
    """A missing template surfaces as an OS error for the caller to translate."""
    with pytest.raises(FileNotFoundError):
        template_text.read_template(_TEMPLATES / "absent.template.md")


# eof
