"""Generated ownership conflicts fail independently of registration order."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from tools.release_workflow.schemas import (
    DomainSchema,
    SchemaError,
    SchemaRegistry,
    SectionSchema,
)


@given(prefix=st.text(alphabet="abcdefgh", min_size=1, max_size=30), suffix=st.text(alphabet="ijklmnop", min_size=1, max_size=30), reverse=st.booleans())
def test_prefix_conflicts_are_rejected(prefix: str, suffix: str, *, reverse: bool) -> None:
    """A family cannot overlap a fixed owner for any generated instance name."""
    family = SectionSchema(prefix + ":", (), family=True)
    fixed = SectionSchema(prefix + ":" + suffix, ())
    sections = (fixed, family) if reverse else (family, fixed)
    schema = DomainSchema("sample", sections)
    with pytest.raises(SchemaError, match="ownership"):
        SchemaRegistry((schema,), shipped=(schema,))


# eof
