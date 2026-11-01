"""Bounded generated values retain the full literal alphabet and strict parsing.

Literal values come from ``tests.scalar_text``: every Unicode scalar value
except CR and LF, the same domain as ``characters`` excluding category ``Cs``
and those two characters, without loading Hypothesis's Unicode category tables
on first use. Length bounds, example budget and the explicit example are
unchanged.
"""

from __future__ import annotations

from functools import partial
from pathlib import Path

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from tests.scalar_text import scalar_text
from tools.release_workflow.configuration import ConfigurationError, load_configuration
from tools.release_workflow.paths import ProjectIdentity
from tools.release_workflow.schemas import (
    TOOLING_SCHEMA,
    DomainSchema,
    SchemaRegistry,
    SectionSchema,
    ValueRule,
)

_LITERAL_TEXT = scalar_text(max_size=12, exclude="\r\n")


def read_text(text: str, **_kwargs: object) -> str:
    """Supply generated content without repeated fixture filesystem writes."""
    return text


@pytest.mark.parametrize("_batch", range(5))
@settings(max_examples=5)
@given(value=_LITERAL_TEXT)
@example(value="% ! ^ & = # ; \\ é \U0010ffff" * 5)
def test_literal_data_reaches_owner_unchanged(_batch: int, value: str) -> None:
    """Bound the value with ordinary characters so INI edge whitespace is data."""
    raw = "x" + value + "x"
    root = Path.cwd()
    identity = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    schema = DomainSchema("sample", (SectionSchema("sample", (ValueRule("pattern"),)),))
    shipped = (TOOLING_SCHEMA, schema)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(Path, "read_text", staticmethod(partial(read_text, "[sample]\npattern=" + raw + "\n")))
        result = load_configuration(identity, SchemaRegistry(shipped, shipped=shipped))
    assert result.sections["sample"]["pattern"].value == raw


@pytest.mark.parametrize("_batch", range(5))
@settings(max_examples=5)
@given(key=st.text(alphabet="abcdefgh", min_size=1, max_size=20))
def test_unknown_and_duplicate_keys_always_fail(_batch: int, key: str) -> None:
    """Generated unowned keys and duplicate declarations cannot be ignored."""
    root = Path.cwd()
    identity = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    for text in (f"[tooling]\n{key}=literal\n", f"[tooling]\n{key}=one\n{key}=two\n"):
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(Path, "read_text", staticmethod(partial(read_text, text)))
            with pytest.raises(ConfigurationError):
                load_configuration(identity)


# eof
