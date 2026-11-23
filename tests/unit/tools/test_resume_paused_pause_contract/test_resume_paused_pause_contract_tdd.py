"""Pause routing capture and manual artifact reader contract tests.

Step 3 of v0.15.0 resume-paused: the canonical pause instruction and template
write the saved routing as one ``resume-paused-routing`` JSON block followed by
the readable table rendered from it. The instruction's worked example is the
Step 2 rendering of its own JSON, its row grammar accepts every cell the Step 2
renderer writes, and a prompt filled from the template parses under the Step 2
reader with its routing resolved. The capture rules name the full pane UUID
and the TUIOS session string, the exact exchange or an explicit not-applicable,
keep historical authorship apart from intended roles, record missing evidence
as explicit unknowns, ask no routing question and never contact the
counterpart or launch ``resume_paused``. The pause replacement guard follows
requirement Q29=A. The receipt template keeps the manual schema 2 lines and
adds the marked schema 3 lines; the status and list readers accept receipt
schemas 1 to 3. The installed ``tuitp`` grammar (prompt heading,
``Session role``, receipt ``Prompt``, ``SHA-256`` and ``Project root``) is
replayed from local fixtures without importing senv, and the provider adapters
stay canonical redirects.

Fix (code review round 1): pause's own check of the existing prompt's receipt
accepts schemas 1 to 3 instead of only the schema 1/2 resume state table. The
guard rules pin that reader, a marked schema 3 receipt classifies the old
prompt as used or new by its digest, and a receipt whose lines do not match its
schema is malformed.
"""

from __future__ import annotations

import re
from functools import cache
from itertools import takewhile
from typing import TYPE_CHECKING, cast

import pytest

from tests.unit.tools.test_resume_paused_artifacts.test_resume_paused_artifacts_tdd import (
    TUITP_HEADING,
    tuitp_field,
)
from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    part,
    single_agent,
)
from tools.prompt_workflow_steps import llm_shared_dir
from tools.resume_paused_artifacts import (
    ROUTING_FENCE,
    ROUTING_TABLE_HEADER,
    PromptState,
    RoutingState,
    classify_usage,
    parse_prompt,
    parse_receipt,
    parse_routing_json,
    render_routing_section,
    render_routing_table,
)
from tools.resume_paused_models import PROMPT_NAME, ArtifactError, CanonicalRoot
from tools.resume_paused_routing import RoutingTarget, SavedExchange, SavedRouting
from tools.review_exchange_models import ReviewFamily

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

ROOT = llm_shared_dir()
PAUSE = "instructions/pause-session.md"
PAUSE_TEMPLATE = "templates/pause-session.template.md"
RECEIPT_TEMPLATE = "templates/resume-session.template.md"
STATUS = "instructions/status-session.md"
STATUS_TEMPLATE = "templates/status-session.template.md"
LIST = "instructions/list-session.md"
LIST_TEMPLATE = "templates/list-session.template.md"
GUARD = "Name the agent that writes the prompt"
CAPTURE = "Record automatic resume routing in the handoff"
PUBLISH = "Publish the latest prompt and finish pausing"
ROUTING = "Automatic resume routing"
EXAMPLE_FENCE = "````markdown"
GRAMMAR_HEADER = "| Row | Cell rendered from the JSON |"
CHECKOUT = "C:\\work\\example"
TITLE = "Step 3 contract"
LEGACY_ROLE = "implementation (code-review requestor inside implement-step)"
LEGACY_TABLE = (
    "| Target | Agent host and intended role | TUIOS session identity | Pane id and name | Resolved checkout | Identity and assignment evidence |",
    "| --- | --- | --- | --- | --- | --- |",
    "| Resumed agent | Claude, requestor | example | 5f0e6c1a, Claude impl | C:\\work\\example | own pane |",
)
HEADER = {
    "Paused by": "claude (Claude Code, model Opus 5.5)",
    "Snapshot": "2026-11-19T00:31:00+01:00",
    "Project root": f"`{CHECKOUT}`",
    "Artifact home": f"`{CHECKOUT}\\.reviews`",
    "Session role": "requestor",
    "Topic and step": "v1.2.0 example, step 3",
    "Paused at": "after the round 2 answer",
}
AGENT_FIELDS = ("Paused by", "Resumed by", "Agent override")
MARKED = ("Launch id", "Receiving pane", "Assignment binding")
MARKED_SCHEMA = 3
DROPPED_BY_SCHEMA: dict[int, frozenset[str]] = {
    1: frozenset({*AGENT_FIELDS, *MARKED}),
    2: frozenset(MARKED),
    MARKED_SCHEMA: frozenset(),
}
PANE_UUID_LENGTH = 36
RECEIPT_VALUES = {
    "Prompt": PROMPT_NAME,
    "Project root": CHECKOUT,
    "Used at": "2026-11-19T08:30:00+01:00",
    "Forced": "false",
    "Paused by": "claude",
    "Resumed by": "claude",
    "Agent override": "not needed",
    "Launch id": "0123456789abcdef0123456789abcdef",
    "Receiving pane": "5f0e6c1a-2b3d-4e5f-8a9b-0c1d2e3f4a5b",
    "Assignment binding": "b" * 64,
}
FIELD = re.compile(r"- (?P<name>[A-Za-z][A-Za-z0-9 -]*?): (?P<value>.*)")
SESSION_ADAPTERS = (
    ".agent/workflows/{name}.md",
    ".agents/llm-shared/instructions/{name}.md",
    ".agents/llm-shared/skills/{name}/SKILL.md",
    ".claude/skills/{name}/SKILL.md",
    ".github/skills/{name}/SKILL.md",
    ".grok/commands/{name}.md",
)
ADAPTER_LINE_LIMIT = 7


@cache
def shipped(relative: str) -> str:
    """Return one shipped instruction or template; its text cannot change during a session."""
    return (ROOT / relative).read_text(encoding="utf-8")


def folded(text: str) -> str:
    """Fold line breaks and repeated spaces into single spaces."""
    return " ".join(text.split())


def section(relative: str, heading: str) -> str:
    """Return the text of one level-two section, below its heading line."""
    return shipped(relative).split(f"\n## {heading}\n", 1)[1].split("\n## ", 1)[0]


def fenced(text: str, opening: str) -> list[str]:
    """Return the lines of the one fence opened by the exact line ``opening``."""
    lines = text.splitlines()
    starts = [index for index, line in enumerate(lines) if line == opening]
    assert len(starts) == 1, f"expected one {opening!r} fence"
    closing = opening[: len(opening) - len(opening.lstrip("`"))]
    start = starts[0] + 1
    return lines[start : lines.index(closing, start)]


def cells(line: str) -> list[str]:
    """Split one table row into its name and its cell; the name holds no separator."""
    return [part.strip() for part in line.strip().strip("|").split("|", 1)]


def keys(value: object) -> set[str]:
    """Return every key of a nested JSON value."""
    if not isinstance(value, dict):
        return set()
    mapping = cast("dict[str, object]", value)
    return {name for key, item in mapping.items() for name in (key, *keys(item))}


def example() -> tuple[str, ...]:
    """Return the pause instruction's worked routing example."""
    return tuple(fenced(section(PAUSE, CAPTURE), EXAMPLE_FENCE))


def example_routing() -> SavedRouting:
    """Parse the worked example's JSON block with the Step 2 reader."""
    return parse_routing_json("\n".join(fenced("\n".join(example()), ROUTING_FENCE)))


def variant(change: Callable[[dict[str, object]], None]) -> SavedRouting:
    """Return the worked example's routing after one change to its JSON object."""
    mapping = example_routing().to_mapping()
    change(mapping)
    return SavedRouting.from_mapping(mapping)


def single(mapping: dict[str, object]) -> None:
    """Turn the pause into a single implementation pause, saved role included."""
    single_agent(mapping)
    part(mapping, "pause")["session_role"] = "implementation"


def unknowns(mapping: dict[str, object]) -> None:
    """Record the pausing pane, the reviewer and the exchange as unknown."""
    part(mapping, "pause")["pane"] = {"unknown": "shared daemon pane variables"}
    part(mapping, "targets")["reviewer"] = {"unknown": "no pane shows the reviewer role"}
    mapping["exchange"] = {"unknown": "exchange evidence unreadable"}


def bare(mapping: dict[str, object]) -> None:
    """Drop optional labels, agent session ids and the round; add an umbrella and a separator."""
    for name in ("resumed", "requestor"):
        part(part(mapping, "targets"), name).update(label="", agent_session_id=None, evidence="screen | log")
    part(mapping, "exchange").update(round=None, umbrella="docs/v1.2.0/draft.v1.2.0.umbrella.md")


def specification(mapping: dict[str, object]) -> None:
    """Turn the exchange into a specification review, which has no implementation step."""
    mapping["exchange"] = {
        "family": "specification", "document": "docs/v1.2.0/design.v1.2.0.example.md",
        "implementation_step": None, "umbrella": None, "occurrence": 2, "round": 1,
    }


VARIANTS: dict[str, Callable[[dict[str, object]], None]] = {
    "paired": lambda _mapping: None,
    "single agent": single,
    "unknowns": unknowns,
    "bare values": bare,
    "specification": specification,
}


def documented_cells() -> dict[str, list[re.Pattern[str]]]:
    """Return the accepted cell forms of each row of the instruction's rendering table."""
    lines = section(PAUSE, CAPTURE).splitlines()
    rows = takewhile(lambda line: line.startswith("|"), lines[lines.index(GRAMMAR_HEADER) + 2 :])
    forms: dict[str, list[re.Pattern[str]]] = {}
    for line in rows:
        name, cell = cells(line)
        spans = re.findall(r"`([^`]+)`", cell)
        forms[name] = [
            re.compile("".join(".+" if piece.startswith("<") else re.escape(piece) for piece in re.split(r"(<[^>]+>)", span)))
            for span in spans
        ]
    return forms


def filled_prompt(routing: Sequence[str], changes: dict[str, str] | None = None) -> bytes:
    """Fill the pause template's heading and header fields; ``routing`` replaces its routing section body."""
    values = HEADER | (changes or {})
    head, rest = shipped(PAUSE_TEMPLATE).split(f"\n## {ROUTING}\n", 1)
    tail = rest.split("\n## ", 1)[1]
    lines = head.splitlines()
    assert [match["name"] for line in lines if (match := FIELD.fullmatch(line))] == list(HEADER)
    filled = [f"# claude: Resume session: {TITLE}"]
    for line in lines[1:]:
        match = FIELD.fullmatch(line)
        filled.append(line if match is None else f"- {match['name']}: {values[match['name']]}")
    return "\n".join([*filled, "", f"## {ROUTING}", "", *routing, "", f"## {tail}"]).encode("utf-8")


def receipt_header() -> list[str]:
    """Return the receipt template's lines above its first section."""
    return list(takewhile(lambda line: not line.startswith("## "), shipped(RECEIPT_TEMPLATE).splitlines()))


def filled_receipt(schema: int, digest: str) -> bytes:
    """Fill the receipt template's header for one schema, dropping the lines that schema lacks."""
    dropped = DROPPED_BY_SCHEMA[schema]
    values = RECEIPT_VALUES | {"Schema": str(schema), "SHA-256": digest}
    header = receipt_header()
    filled: list[str] = []
    for line in header:
        match = FIELD.fullmatch(line)
        if match is None:
            filled.append(line)
        elif match["name"] not in dropped:
            filled.append(f"- {match['name']}: {values[match['name']]}")
    return "\n".join([*filled, *shipped(RECEIPT_TEMPLATE).splitlines()[len(header) :]]).encode("utf-8")


def test_instruction_example_is_the_rendering_of_its_own_json() -> None:
    """The worked example is exactly what the Step 2 renderer writes for its JSON."""
    assert example() == render_routing_section(example_routing())


def test_instruction_example_records_a_resolved_pair_with_full_identities() -> None:
    """The example names full pane UUIDs, session strings and the exact exchange."""
    routing = example_routing()
    resumed, reviewer, exchange = routing.resumed, routing.reviewer, routing.exchange
    assert isinstance(resumed, RoutingTarget)
    assert isinstance(reviewer, RoutingTarget)
    assert isinstance(exchange, SavedExchange)
    assert resumed == routing.requestor
    assert routing.unresolved == ()
    assert all(len(target.pane_id) == PANE_UUID_LENGTH and target.session for target in (resumed, reviewer))
    assert (exchange.family, exchange.implementation_step, exchange.occurrence) == (ReviewFamily.CODE, "3", 1)


@pytest.mark.parametrize("name", list(VARIANTS))
def test_documented_cells_accept_every_rendered_cell(name: str) -> None:
    """Each rendered row matches one documented form of the same row, in the same order."""
    forms = documented_cells()
    rendered = render_routing_table(variant(VARIANTS[name]))
    assert rendered[:2] == (ROUTING_TABLE_HEADER, "| --- | --- |")
    rows = [cells(line) for line in rendered[2:]]
    assert [row_name for row_name, _ in rows] == list(forms)
    for row_name, value in rows:
        assert any(form.fullmatch(value) for form in forms[row_name]), (row_name, value)


def test_template_writes_the_json_skeleton_then_the_rendered_table() -> None:
    """The template's block names every schema key and its table lists the rendered rows."""
    text = section(PAUSE_TEMPLATE, ROUTING)
    skeleton = fenced(text, ROUTING_FENCE)
    assert set(re.findall(r'"([a-z_]+)":', "\n".join(skeleton))) == keys(example_routing().to_mapping())
    assert {'  "schema": "resume-paused-routing",', '  "version": 1,'} <= set(skeleton)
    lines = text.splitlines()
    table = list(takewhile(lambda line: line.startswith("|"), lines[lines.index(ROUTING_TABLE_HEADER) :]))
    rendered = render_routing_table(example_routing())
    assert [cells(line)[0] for line in table] == [cells(line)[0] for line in rendered]
    assert table[2] == rendered[2]
    assert not any(line.startswith(LEGACY_TABLE[0][:40]) for line in shipped(PAUSE_TEMPLATE).splitlines())


@pytest.mark.parametrize(
    ("name", "role", "state", "reasons"),
    [
        ("paired", "requestor", RoutingState.RESOLVED, ()),
        ("single agent", "implementation", RoutingState.RESOLVED, ()),
        ("unknowns", "requestor", RoutingState.UNRESOLVED, ("reviewer target unknown: no pane shows the reviewer role", "review exchange unknown: exchange evidence unreadable")),
    ],
)
def test_prompt_filled_from_the_template_parses_under_step_two(name: str, role: str, state: RoutingState, reasons: tuple[str, ...]) -> None:
    """A new pause parses with its routing classified; unknowns stay explicit reasons."""
    routing = variant(VARIANTS[name])
    data = filled_prompt(render_routing_section(routing), {"Session role": role})
    metadata, reading = parse_prompt(data, CanonicalRoot.parse(CHECKOUT))
    assert (metadata.author, metadata.title, metadata.session_role, metadata.snapshot) == ("claude", TITLE, role, routing.pause.snapshot)
    assert (reading.state, reading.routing, reading.reasons) == (state, routing, reasons)


def test_session_role_line_must_hold_the_routing_role_token() -> None:
    """A header role token other than the routing's saved role makes the routing an error."""
    data = filled_prompt(render_routing_section(example_routing()), {"Session role": "implementation"})
    _, reading = parse_prompt(data, CanonicalRoot.parse(CHECKOUT))
    assert (reading.state, reading.reasons) == (RoutingState.ERROR, ("routing session role contradicts the prompt",))


def test_prompt_with_routing_keeps_the_launcher_grammar() -> None:
    """The installed launcher still reads the heading and Session role of a routing prompt."""
    text = filled_prompt(render_routing_section(example_routing())).decode("utf-8")
    heading = TUITP_HEADING.fullmatch(text.splitlines()[0].strip())
    assert heading is not None
    assert (heading[1], heading[2], tuitp_field(text, "Session role")) == ("claude", TITLE, "requestor")


@pytest.mark.parametrize(("routing", "state"), [(LEGACY_TABLE, RoutingState.TABLE_ONLY), ((), RoutingState.ABSENT)], ids=["prose table", "no routing"])
def test_legacy_prompts_stay_readable_and_skip_bulk_routing(routing: tuple[str, ...], state: RoutingState) -> None:
    """A prompt without a routing block keeps its manual and launcher readability."""
    data = filled_prompt(routing, {"Session role": LEGACY_ROLE})
    metadata, reading = parse_prompt(data, CanonicalRoot.parse(CHECKOUT))
    assert (metadata.session_role, reading.state, reading.routing) == (LEGACY_ROLE, state, None)
    text = data.decode("utf-8")
    assert (TUITP_HEADING.fullmatch(text.splitlines()[0]) is not None, tuitp_field(text, "Session role")) == (True, LEGACY_ROLE)


def test_receipt_template_adds_the_marked_lines_after_the_schema_two_lines() -> None:
    """The marked schema 3 lines follow every schema 2 line, and a manual resume omits them."""
    fields = [(match["name"], match["value"]) for line in receipt_header() if (match := FIELD.fullmatch(line))]
    assert [name for name, _ in fields] == ["Schema", "Prompt", "SHA-256", "Project root", "Used at", "Forced", *AGENT_FIELDS, *MARKED]
    placeholders = dict(fields)
    assert placeholders["Prompt"] == PROMPT_NAME
    assert placeholders["Schema"] == "{2 for a manual resume; 3 for a marked resume}"
    assert all(placeholders[name].startswith("{marked resume only, omit this line on a manual resume: ") for name in MARKED)
    meaning = folded(section(RECEIPT_TEMPLATE, "Meaning of this usage flag"))
    assert "Schema 3 keeps every schema 2 line and only adds marked-resume bindings, which hold no token or capability." in meaning


@pytest.mark.parametrize("schema", [1, 2, 3])
def test_receipts_filled_from_the_template_parse_and_keep_the_launcher_lines(schema: int) -> None:
    """Each receipt schema parses, consumes the prompt it names, and keeps the three launcher lines."""
    metadata, _ = parse_prompt(filled_prompt(render_routing_section(example_routing())), CanonicalRoot.parse(CHECKOUT))
    data = filled_receipt(schema, metadata.digest.value)
    receipt = parse_receipt(data)
    assert (receipt.schema, receipt.paused_by is not None, receipt.launch_id is not None) == (schema, schema > 1, schema == MARKED_SCHEMA)
    assert classify_usage(metadata, receipt, metadata.project_root) is PromptState.USED
    text = data.decode("utf-8")
    assert [tuitp_field(text, name) for name in ("Prompt", "SHA-256", "Project root")] == [PROMPT_NAME, metadata.digest.value, CHECKOUT]


@pytest.mark.parametrize(("matching", "state"), [(True, PromptState.USED), (False, PromptState.NEW_SINCE_USE)], ids=["same bytes", "other bytes"])
def test_schema_three_receipt_classifies_the_existing_prompt_for_pause(matching: bool, state: PromptState) -> None:  # noqa: FBT001
    """Before replacing a prompt, pause reads a marked receipt as used or new by its digest alone."""
    metadata, _ = parse_prompt(filled_prompt(render_routing_section(example_routing())), CanonicalRoot.parse(CHECKOUT))
    digest = metadata.digest.value if matching else "c" * 64
    receipt = parse_receipt(filled_receipt(MARKED_SCHEMA, digest))
    assert classify_usage(metadata, receipt, metadata.project_root) is state


MALFORMED_RECEIPTS: dict[str, Callable[[str], str]] = {
    "schema 3 without its launch id": lambda text: "\n".join(line for line in text.splitlines() if not line.startswith("- Launch id:")),
    "schema 2 with the marked lines": lambda text: text.replace("- Schema: 3", "- Schema: 2"),
    "unknown schema 4": lambda text: text.replace("- Schema: 3", "- Schema: 4"),
}


@pytest.mark.parametrize("name", list(MALFORMED_RECEIPTS))
def test_malformed_receipts_stop_the_pause_guard(name: str) -> None:
    """A receipt whose lines do not match its schema is malformed rather than unused or used."""
    text = MALFORMED_RECEIPTS[name](filled_receipt(MARKED_SCHEMA, "c" * 64).decode("utf-8"))
    with pytest.raises(ArtifactError, match="usage receipt"):
        parse_receipt(text.encode("utf-8"))


CAPTURE_RULES = (
    "never launch `resume_paused` or contact the counterpart to obtain it",
    "A pane's full UUID is its record's `window_id`, 36 characters long; the table view prints only its first 8 characters.",
    "Its TUIOS session identity is the record's `session` string, the session name the selector uses, not a numeric id.",
    "historical authorship never implies an intended requestor role",
    "Preserve the user's latest explicit role-switch direction and its source",
    "Do not ask a routing selection question or invent an identifier just to complete the pause.",
    "Record identity and evidence only, never review ownership capabilities, tokens or credentials.",
    "whose opening line is exactly `` ```json resume-paused-routing `` and which holds one JSON object",
    'replace the pausing pane, a target or the exchange with `{"unknown": "<reason>"}`',
    'are each `{"not_applicable": "<reason>"}`, all three or none. The resumed target is never not applicable.',
    "When the resumed target is one of them, write the identical object in both places.",
    "one pane UUID never appears in two different target objects",
    "its `round` records the round at pause only; a resume selects the current round from live protocol state",
    "Write `none` for an empty label and for a `null` agent session id, umbrella or round, and `not applicable` for a `null` implementation step.",
    "makes a bulk resume refuse this routing as an error; ordinary `resume-session` still reads the prompt",
)
GUARD_RULES = (
    "| Its agent id differs from yours or is missing | Ask |",
    "| Its pausing pane differs from this pause's pausing pane, even with the same agent id | Ask |",
    "| Its saved session role differs from this pause's saved role, even with the same agent id | Ask |",
    "| Same agent id, and every pane or role known on both sides is equal | Replace without asking |",
    "Read the existing prompt's pausing pane from its routing block's `pause.pane` and its saved role from that block's `pause.session_role`.",
    "Compare panes by full pane UUID and TUIOS session string, never by label.",
    "is not by itself a difference; compare the remaining recorded fields",
    "A legacy prompt without pane or role fields therefore keeps the agent-id comparison.",
    "Compare historical pausing identities, not intended future role assignments or a recorded role switch.",
    "Name the existing checkpoint's agent, pausing pane and saved role, marking unavailable values as unknown",
    "If the user declines, preserve the existing prompt and stop without writing a new one.",
    "This guard applies at pause time only; it adds no confirmation to bulk resume.",
    "Accept a receipt of schema 1, 2 or 3 as [status-session](status-session.md#determine-whether-the-latest-prompt-is-unprocessed) does",
    "classify it by its `Prompt`, `SHA-256` and `Project root` lines, never by its schema",
    "A valid receipt for the prompt's exact bytes makes the prompt used, and one for other bytes makes it new since previous use.",
    "Another schema, or a receipt that misses a line of its schema or carries another one, is malformed: report the diagnostic and stop without replacing the prompt.",
)
READER_RULES = (
    (PAUSE, PUBLISH, "Write the `- Session role:` line as the routing's `pause.session_role` token alone"),
    (PAUSE, PUBLISH, "check that the routing block parses as one strict JSON object and that each table cell equals its rendering from the JSON"),
    (STATUS, "Determine whether the latest prompt is unprocessed", "Accept a usage receipt of schema 1, 2 or 3."),
    (STATUS, "Determine whether the latest prompt is unprocessed", "schema 3, written only by a marked resume, keeps every schema 2 line and adds `Launch id`, `Receiving pane` and `Assignment binding`"),
    (STATUS, "Determine whether the latest prompt is unprocessed", "the schema 3 lines are non-secret bindings that never change the classification"),
    (STATUS, "Determine whether the latest prompt is unprocessed", "Any other schema, or a receipt missing a line of its schema, is an invalid receipt."),
    (STATUS, "Determine whether the latest prompt is unprocessed", "read only from its `resume-paused-routing` JSON block"),
    (STATUS, "Determine whether the latest prompt is unprocessed", "it never derives routing from a table and never checks the targets against live panes"),
    (STATUS_TEMPLATE, "Opening when an unprocessed prompt exists", "saved routing {resolved, unresolved: reasons, error: diagnostic, table only, or none}"),
    (STATUS_TEMPLATE, "Opening when no unprocessed prompt exists", "through a marked resume in pane `{receiving pane}` for a schema 3 receipt"),
    (LIST, "Check listed sessions against disk", "Accept receipt schemas 1, 2 and 3 as [status-session](status-session.md#determine-whether-the-latest-prompt-is-unprocessed) does"),
    (LIST, "Check listed sessions against disk", "a receipt matches on its `Prompt`, `SHA-256` and `Project root` lines whatever its schema"),
    (LIST, "Check listed sessions against disk", "`through a marked resume in pane {Receiving pane}` for a schema 3 receipt"),
    (LIST_TEMPLATE, "Sessions waiting to be resumed", "{disk check result, naming the receiving pane of a schema 3 receipt}"),
)


@pytest.mark.parametrize("rule", CAPTURE_RULES)
def test_capture_rules_keep_routing_read_only_and_explicit(rule: str) -> None:
    """Capture reads its own evidence, writes explicit unknowns and asks no routing question."""
    assert rule in folded(section(PAUSE, CAPTURE))


@pytest.mark.parametrize("rule", GUARD_RULES)
def test_replacement_guard_follows_requirement_q29(rule: str) -> None:
    """A different known pane or role guards replacement; unknowns alone do not."""
    assert rule in folded(section(PAUSE, GUARD))


@pytest.mark.parametrize(("relative", "heading", "rule"), READER_RULES)
def test_manual_readers_accept_schema_three_and_json_routing(relative: str, heading: str, rule: str) -> None:
    """Pause, status and list describe the schema 3 receipt and the JSON routing source."""
    assert rule in folded(section(relative, heading))


@pytest.mark.parametrize("name", ["pause-session", "status-session", "list-session", "resume-session"])
def test_session_adapters_stay_canonical_redirects(name: str) -> None:
    """Provider adapters point at the canonical instruction and copy none of its body."""
    for pattern in SESSION_ADAPTERS:
        text = shipped(pattern.format(name=name))
        assert f"instructions/{name}.md" in text
        assert len(text.splitlines()) <= ADAPTER_LINE_LIMIT
        assert "resume-paused-routing" not in text


# eof
