"""Exhaustive and generated strictness properties of the saved-routing schema.

Step 2 of v0.14.0 resume-paused: every key of every routing object is
required, every scalar value refuses a wrong type, and any added key at any
object is refused. The finite key and value domains are exhaustive
parametrizations, so every case runs and fails on its own; added key names
are drawn.
"""

from __future__ import annotations

import string
from typing import cast

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    ROOT,
    part,
    routing_mapping,
)
from tools.resume_paused_models import ArtifactError
from tools.resume_paused_routing import SavedRouting

EXAMPLES = 5
OBJECT_PATHS = (
    (), ("pause",), ("pause", "pane"), ("observation",), ("targets",),
    ("targets", "resumed"), ("targets", "requestor"), ("targets", "reviewer"), ("exchange",),
)


def nested(mapping: dict[str, object], path: tuple[str, ...]) -> dict[str, object]:
    """Return the routing object at one key path."""
    for key in path:
        mapping = part(mapping, key)
    return mapping


def leaf_paths(mapping: dict[str, object], path: tuple[str, ...] = ()) -> list[tuple[str, ...]]:
    """Return the key path of every scalar value in a routing object."""
    paths: list[tuple[str, ...]] = []
    for key, value in mapping.items():
        child = (*path, key)
        paths.extend(leaf_paths(cast("dict[str, object]", value), child) if isinstance(value, dict) else [child])
    return paths


def label_of(case: tuple[str, ...]) -> str:
    """Name one key path for its parametrized case."""
    return "/".join(case) or "routing"


_VALID = routing_mapping(ROOT)
OBJECT_KEYS = [(*path, key) for path in OBJECT_PATHS for key in sorted(nested(_VALID, path))]
LEAVES = leaf_paths(_VALID)


@pytest.mark.parametrize("case", OBJECT_KEYS, ids=label_of)
def test_every_routing_key_is_required(case: tuple[str, ...]) -> None:
    """Removing any key of any routing object is a parse error."""
    mapping = routing_mapping(ROOT)
    del nested(mapping, case[:-1])[case[-1]]
    with pytest.raises(ArtifactError):
        SavedRouting.from_mapping(mapping)


@pytest.mark.parametrize("case", LEAVES, ids=label_of)
def test_every_routing_value_refuses_a_wrong_type(case: tuple[str, ...]) -> None:
    """A list in place of any scalar routing value is a parse error."""
    mapping = routing_mapping(ROOT)
    nested(mapping, case[:-1])[case[-1]] = []
    with pytest.raises(ArtifactError):
        SavedRouting.from_mapping(mapping)


@pytest.mark.parametrize("path", OBJECT_PATHS, ids=label_of)
@settings(max_examples=EXAMPLES)
@given(name=st.text(alphabet=string.ascii_lowercase + "_", min_size=1, max_size=12))
def test_every_routing_object_refuses_unexpected_keys(path: tuple[str, ...], name: str) -> None:
    """Any added key, at any routing object, is a parse error."""
    mapping = routing_mapping(ROOT)
    assume(name not in nested(mapping, path))
    nested(mapping, path)[name] = 1
    with pytest.raises(ArtifactError):
        SavedRouting.from_mapping(mapping)


# eof
