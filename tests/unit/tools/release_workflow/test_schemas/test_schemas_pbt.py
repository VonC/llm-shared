"""Bounded generated ownership conflicts preserve both registration orders."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tools.release_workflow.schemas import (
    DomainSchema,
    SchemaError,
    SchemaRegistry,
    SectionSchema,
)


def _prefix(data: bytes) -> str:
    """Map every byte to the original eight-letter prefix alphabet."""
    return "".join(chr(ord("a") + (value & 7)) for value in data)


def _suffix(data: bytes) -> str:
    """Preserve the full suffix domain without string-constant discovery."""
    return "".join(chr(ord("i") + (value & 7)) for value in data)


@settings(max_examples=25)
@given(prefix=st.binary(min_size=1, max_size=30).map(_prefix),
       suffix=st.binary(min_size=1, max_size=30).map(_suffix), reverse=st.booleans())
def test_prefix_conflicts_are_rejected(prefix: str, suffix: str, *, reverse: bool) -> None:
    """A family cannot overlap a fixed owner for any generated instance name."""
    family = SectionSchema(prefix + ":", (), family=True)
    fixed = SectionSchema(prefix + ":" + suffix, ())
    sections = (fixed, family) if reverse else (family, fixed)
    schema = DomainSchema("sample", sections)
    with pytest.raises(SchemaError, match="ownership"):
        SchemaRegistry((schema,), shipped=(schema,))


# eof
