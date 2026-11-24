"""Generated duplicate-key, round-trip and robustness properties of pause artifacts.

Step 2 of v0.15.0 resume-paused: a routing block refuses a repeated key in any
object; generated routing survives its JSON and readable-table renderings
inside a prompt; arbitrary routing text never escapes the routing reading; and
the prompt and receipt parsers fail only with ``ArtifactError`` on arbitrary
input. The finite duplicate-key domain is an exhaustive parametrization;
Unicode text maps integers onto every scalar value, so no category table loads.
"""

from __future__ import annotations

import json
from contextlib import suppress
from typing import cast

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tests.unit.tools.test_resume_paused_artifacts.test_resume_paused_artifacts_tdd import (
    prompt_text,
)
from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    REQUESTOR_PANE,
    REVIEWER_PANE,
    ROOT,
    part,
    routing_mapping,
    slot,
)
from tools.resume_paused_artifacts import (
    ROUTING_FENCE,
    RoutingState,
    parse_prompt,
    parse_receipt,
    parse_routing_json,
    render_routing_section,
)
from tools.resume_paused_models import ArtifactError, CanonicalRoot
from tools.resume_paused_routing import SavedRouting

CANONICAL = CanonicalRoot.from_path(ROOT)
EXAMPLES = 5
ROUND_TRIP_EXAMPLES = 3
SURROGATE_START = 0xD800
SURROGATE_COUNT = 0x800
LAST_SCALAR = 0x10FFFF
C0_END = 0x20
C1_START = 0x7F
C1_END = 0x9F
THIRD_PANE = "5b1c0d2e-3f40-4a5b-8c6d-7e8f90a1b2c3"
SHAPES = ("pair", "reviewer", "unknown requestor", "unknown reviewer", "unknown exchange", "unknown resumed", "single")


def scalar(number: int) -> str:
    """Map an integer onto every Unicode scalar value, skipping the surrogates."""
    return chr(number if number < SURROGATE_START else number + SURROGATE_COUNT)


def single_line(characters: list[str]) -> str:
    """Replace exactly what routing text refuses, then trim, keeping every other scalar."""
    text = "".join(
        "x" if ord(character) < C0_END or C1_START <= ord(character) <= C1_END or character in "\N{LINE SEPARATOR}\N{PARAGRAPH SEPARATOR}" else character
        for character in characters
    ).strip()
    return text or "x"


def object_keys(mapping: dict[str, object], path: tuple[str, ...] = ()) -> list[tuple[str, ...]]:
    """Return the key path of every key of every object in a routing mapping."""
    keys: list[tuple[str, ...]] = []
    for key, value in mapping.items():
        keys.append((*path, key))
        if isinstance(value, dict):
            keys.extend(object_keys(cast("dict[str, object]", value), (*path, key)))
    return keys


def with_duplicate(value: object, path: tuple[str, ...], target: tuple[str, ...], key: str) -> str:
    """Render JSON that repeats ``key`` in the object at ``target``."""
    if not isinstance(value, dict):
        return json.dumps(value)
    mapping = cast("dict[str, object]", value)
    items = [f"{json.dumps(name)}: {with_duplicate(child, (*path, name), target, key)}" for name, child in mapping.items()]
    if path == target:
        items.append(f"{json.dumps(key)}: {json.dumps(mapping[key])}")
    return "{" + ", ".join(items) + "}"


SCALARS = st.integers(0, LAST_SCALAR - SURROGATE_COUNT).map(scalar)
TEXT = st.lists(SCALARS, min_size=1, max_size=6).map(single_line)
KEYS = object_keys(routing_mapping(ROOT))


def test_scalar_mapping_reaches_both_ends_and_skips_surrogates() -> None:
    """The integer encoding covers every scalar value and never yields a surrogate."""
    edges = (0, SURROGATE_START - 1, SURROGATE_START, LAST_SCALAR - SURROGATE_COUNT)
    assert [scalar(number) for number in edges] == ["\x00", chr(0xD7FF), chr(0xE000), "\U0010ffff"]


@pytest.mark.parametrize("case", KEYS, ids="/".join)
def test_duplicate_keys_are_refused_in_every_object(case: tuple[str, ...]) -> None:
    """Two readers could see different values, so a repeated key never parses."""
    with pytest.raises(ArtifactError, match="duplicate JSON key"):
        parse_routing_json(with_duplicate(routing_mapping(ROOT), (), case[:-1], case[-1]))


def fill_target(draw: st.DrawFn, target: dict[str, object], pane: str) -> dict[str, object]:
    """Draw the free text and host of one target, keeping its role and pane."""
    target.update(
        host=draw(st.sampled_from(["claude", "codex"])), label=draw(st.just("") | TEXT),
        agent_session_id=draw(st.none() | TEXT), evidence=draw(TEXT),
        pane_id=draw(st.sampled_from([pane, pane.upper()])),
    )
    return target


@st.composite
def routings(draw: st.DrawFn, shape: str) -> dict[str, object]:
    """Draw one consistent routing object of a supported shape."""
    mapping = routing_mapping(ROOT)
    part(mapping, "observation")["evidence"] = draw(TEXT)
    targets = part(mapping, "targets")
    requestor = fill_target(draw, slot(mapping, "requestor"), REQUESTOR_PANE)
    reviewer = fill_target(draw, slot(mapping, "reviewer"), REVIEWER_PANE)
    other = {**requestor, "role": draw(st.sampled_from(["implementation", "documentation", "other"])), "pane_id": THIRD_PANE}
    unknown = {"unknown": draw(TEXT)}
    resumed = {"reviewer": reviewer, "unknown requestor": other, "unknown resumed": unknown, "single": other}.get(shape, requestor)
    targets["resumed"] = dict(resumed)
    if shape == "unknown requestor":
        targets["requestor"] = unknown
    elif shape == "unknown reviewer":
        targets["reviewer"] = unknown
    elif shape == "unknown exchange":
        mapping["exchange"] = unknown
    elif shape == "single":
        absent = {"not_applicable": draw(TEXT)}
        targets.update(requestor=absent, reviewer=absent)
        mapping["exchange"] = absent
    return mapping


@pytest.mark.parametrize("shape", SHAPES)
@settings(max_examples=ROUND_TRIP_EXAMPLES)
@given(data=st.data())
def test_generated_routing_survives_json_and_table_round_trips(shape: str, data: st.DataObject) -> None:
    """Canonical JSON parses back equal, and a prompt holding JSON and table reads it back."""
    routing = SavedRouting.from_mapping(data.draw(routings(shape)))
    assert SavedRouting.from_mapping(json.loads(json.dumps(routing.to_mapping()))) == routing
    section = "\n".join(render_routing_section(routing)) + "\n"
    reading = parse_prompt(prompt_text(ROOT, section).encode(), CANONICAL)[1]
    expected = RoutingState.UNRESOLVED if routing.unresolved else RoutingState.RESOLVED
    assert (reading.state, reading.routing, reading.reasons) == (expected, routing, routing.unresolved)


@settings(max_examples=EXAMPLES)
@given(st.lists(SCALARS, max_size=60).map("".join))
def test_arbitrary_routing_text_stays_inside_the_reading(text: str) -> None:
    """Whatever a routing block holds, the prompt parses and the routing is classified."""
    prompt = prompt_text(ROOT, f"{ROUTING_FENCE}\n{text}\n```\n").encode()
    assert parse_prompt(prompt, CANONICAL)[1].state in set(RoutingState)


@settings(max_examples=EXAMPLES)
@given(st.binary(max_size=200))
def test_parsers_fail_only_with_artifact_errors(data: bytes) -> None:
    """Arbitrary bytes are a receipt or prompt, or an ``ArtifactError``, never a crash."""
    with suppress(ArtifactError):
        parse_receipt(data)
    with suppress(ArtifactError):
        parse_prompt(data, CANONICAL)


# eof
