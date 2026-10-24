"""Generated literal values survive strict INI parsing without interpolation."""

from __future__ import annotations

from functools import partial
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from tools.release_workflow.configuration import ConfigurationError, load_configuration
from tools.release_workflow.paths import ProjectIdentity
from tools.release_workflow.schemas import (
    TOOLING_SCHEMA,
    DomainSchema,
    SchemaRegistry,
    SectionSchema,
    ValueRule,
)


def read_text(text: str, **_kwargs: object) -> str:
    """Supply generated content without repeated fixture filesystem writes."""
    return text


@given(value=st.text(alphabet=st.characters(exclude_categories=("Cs",), exclude_characters="\r\n"), max_size=100))
def test_literal_data_reaches_owner_unchanged(value: str) -> None:
    """Bound the value with ordinary characters so INI edge whitespace is data."""
    raw = "x" + value + "x"
    root = Path.cwd()
    identity = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    schema = DomainSchema("sample", (SectionSchema("sample", (ValueRule("pattern"),)),))
    shipped = (TOOLING_SCHEMA, schema)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(Path, "read_text", partial(read_text, "[sample]\npattern=" + raw + "\n"))
        result = load_configuration(identity, SchemaRegistry(shipped, shipped=shipped))
    assert result.sections["sample"]["pattern"].value == raw


@given(key=st.text(alphabet="abcdefgh", min_size=1, max_size=20))
def test_unknown_and_duplicate_keys_always_fail(key: str) -> None:
    """Generated unowned keys and duplicate declarations cannot be ignored."""
    root = Path.cwd()
    identity = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    for text in (f"[tooling]\n{key}=literal\n", f"[tooling]\n{key}=one\n{key}=two\n"):
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(Path, "read_text", partial(read_text, text))
            with pytest.raises(ConfigurationError):
                load_configuration(identity)


# eof
