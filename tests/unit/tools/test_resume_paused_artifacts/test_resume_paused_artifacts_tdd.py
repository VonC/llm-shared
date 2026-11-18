"""Read-only pause prompt, usage receipt and routing-block tests.

Step 2 of v0.14.0 resume-paused: a checkout snapshot applies the resume-session
state table to exact prompt and receipt bytes, reads routing only from one
versioned JSON block whose rendered table must agree with it and with the
prompt header, and keeps the grammar the installed ``tuitp`` parses. Every
scenario declares its files in the memory-backed scratch tree and proves that
reading writes nothing. The write guard, read recorder and tree helpers here
also serve the exchange observation tests of the same step.

Fix (code review round 1): an independent recorder of ``Path`` reads checks
that the snapshot's exact reads and bytes include the artifact-home
declaration, whether it is accepted or refused.
"""

from __future__ import annotations

import json
import os
import re
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    REQUESTOR_PANE,
    SNAPSHOT,
    mutated,
    part,
    routing_mapping,
    single_agent,
)
from tools import artifact_home as artifact_home_module
from tools.resume_paused_artifacts import (
    ROUTING_FENCE,
    PromptState,
    RoutingState,
    parse_prompt,
    parse_receipt,
    read_checkout_snapshot,
    render_routing_section,
    render_routing_table,
)
from tools.resume_paused_models import (
    PROMPT_NAME,
    RECEIPT_NAME,
    ArtifactError,
    CanonicalRoot,
    PromptDigest,
)
from tools.resume_paused_routing import SavedRouting
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_artifact_migration import ReviewArtifactMigration
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_status_migration import ReviewStatusMigrationPreflight

if TYPE_CHECKING:
    from collections.abc import Generator

USED_AT = "2026-11-18T07:25:09+01:00"
LAUNCH_ID = "0123456789abcdef0123456789abcdef"
BINDING = "b" * 64
SCHEMAS = (1, 2, 3)
TITLE = "Step 2 tests"
# Copied from senv bin/tuitp_resume.py (HEADING, field), read-only, 2026-11-18:
# the installed launcher's grammar, replayed here without importing senv.
TUITP_HEADING = re.compile(r"# ([a-z0-9-]+): Resume session: (.*)")


def tuitp_field(text: str, name: str) -> str | None:
    """Replay the installed launcher's ``field`` reader."""
    match = re.search(rf"^- {re.escape(name)}: *(.*?) *$", text, re.MULTILINE)
    return match[1] if match else None


def no_tracking(_root: Path, _relative: str) -> bool:
    """Declare that Git tracks nothing below the artifact home."""
    return False


def all_tracked(_root: Path, _relative: str) -> bool:
    """Declare that Git tracks a path below the artifact home."""
    return True


def checkout(tmp_path: Path, home: str = ".reviews") -> Path:
    """Declare one checkout with a prepared catch-all artifact home."""
    root = tmp_path / "checkout"
    (root / home).mkdir(parents=True)
    (root / home / ".gitignore").write_bytes(b"*\n")
    return root


def raw_block(mapping: object) -> str:
    """Render a routing block without validating its content."""
    return f"{ROUTING_FENCE}\n{json.dumps(mapping, indent=2)}\n```\n"


def section(root: Path) -> str:
    """Render the valid routing block and its readable table."""
    return "\n".join(render_routing_section(SavedRouting.from_mapping(routing_mapping(root)))) + "\n"


def prompt_text(root: Path, routing: str = "", *, author: str = "claude", role: str = "requestor", drop: str = "") -> str:
    """Return one pause prompt in the template's shape."""
    header = {
        "Paused by": f"{author} (Claude Code, Opus 5.5)", "Snapshot": SNAPSHOT, "Project root": f"`{root}`",
        "Artifact home": f"`{root / '.reviews'}`", "Session role": role, "Paused at": "after the tests",
    }
    lines = [f"# {author}: Resume session: {TITLE}", "", "Continue the work described below.", ""]
    lines += [f"- {name}: {value}" for name, value in header.items() if name != drop]
    lines += ["", "## Automatic resume routing", "", routing, "## Objective and latest user direction", "", "- Snapshot: later quote", ""]
    return "\n".join(lines)


def receipt_text(schema: int, digest: str, root: Path | str, changes: dict[str, str | None] | None = None) -> str:
    """Return one usage receipt of a schema, with optional field changes or removals."""
    fields = {"Schema": str(schema), "Prompt": PROMPT_NAME, "SHA-256": digest, "Project root": str(root), "Used at": USED_AT, "Forced": "false"}
    if schema > SCHEMAS[0]:
        fields |= {"Paused by": "claude", "Resumed by": "claude", "Agent override": "not needed"}
    if schema > SCHEMAS[1]:
        fields |= {"Launch id": LAUNCH_ID, "Receiving pane": REQUESTOR_PANE, "Assignment binding": BINDING}
    for name, value in (changes or {}).items():
        if value is None:
            fields.pop(name)
        else:
            fields[name] = value
    body = "".join(f"- {name}: {value}\n" for name, value in fields.items())
    return f"# Session resume usage receipt\n\n{body}\n## Reconciliation recorded at resume\n\n- Branch: main\n"


def write(root: Path, name: str, content: str | bytes) -> bytes:
    """Write one artifact into the default home and return its exact bytes."""
    data = content.encode("utf-8") if isinstance(content, str) else content
    (root / ".reviews" / name).write_bytes(data)
    return data


def tree(root: Path) -> dict[str, bytes | None]:
    """Return every path below a checkout with its bytes, or ``None`` for a folder."""
    return {path.relative_to(root).as_posix(): path.read_bytes() if path.is_file() else None for path in root.rglob("*")}


def forbidden(*_args: object, **_kwargs: object) -> None:
    """Fail when a read-only reader reaches a preparing, migrating or writing path."""
    message = "a read-only resume-paused reader reached a writing path"
    raise AssertionError(message)


@contextmanager
def writes_forbidden() -> Generator[None]:
    """Make every home preparation, migration, core construction and mutation fail."""
    with pytest.MonkeyPatch.context() as patch:
        for owner, name in (
            (ReviewArtifactConfiguration, "prepare_home"), (artifact_home_module, "artifact_home"),
            (artifact_home_module, "artifact_path"), (ReviewArtifactMigration, "migrate"),
            (ReviewStatusMigrationPreflight, "run"), (ReviewExchangeCore, "__init__"),
            (os, "mkdir"), (os, "replace"), (os, "rename"), (os, "unlink"), (os, "rmdir"),
        ):
            patch.setattr(owner, name, forbidden)
        yield


@contextmanager
def recorded_reads() -> Generator[list[Path]]:
    """Record every whole-file read made through ``Path`` while the block runs."""
    seen: list[Path] = []
    read_text, read_bytes = Path.read_text, Path.read_bytes

    def text(path: Path, *args: Any, **kwargs: Any) -> str:
        seen.append(path)
        return read_text(path, *args, **kwargs)

    def data(path: Path) -> bytes:
        seen.append(path)
        return read_bytes(path)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(Path, "read_text", text)
        patch.setattr(Path, "read_bytes", data)
        yield seen


def sizes(paths: tuple[Path, ...]) -> int:
    """Return the total size of the files a snapshot reports as read."""
    return sum(path.stat().st_size for path in paths)


def snapshot_of(root: Path) -> tuple[object, ...]:
    """Read one checkout under the write guard and prove its tree is unchanged."""
    before = tree(root)
    with writes_forbidden():
        snapshot = read_checkout_snapshot(root, tracked_directory=no_tracking)
    assert tree(root) == before
    return snapshot.state, snapshot.routing.state if snapshot.routing else None, snapshot.diagnostic


def test_missing_home_reports_no_saved_prompt_and_creates_nothing(tmp_path: Path) -> None:
    """A checkout without its artifact home has no saved task, and stays without one."""
    root = tmp_path / "bare"
    root.mkdir()
    assert snapshot_of(root)[0] is PromptState.NO_PROMPT
    assert not (root / ".reviews").exists()


def test_missing_prompt_leaves_the_receipt_unread(tmp_path: Path) -> None:
    """Only the ignore file is read when no prompt exists, whatever receipt remains."""
    root = checkout(tmp_path)
    write(root, RECEIPT_NAME, "not a receipt")
    snapshot = read_checkout_snapshot(root, tracked_directory=no_tracking)
    assert snapshot.state is PromptState.NO_PROMPT
    assert snapshot.reads == (root / ".reviews" / ".gitignore",)


@pytest.mark.parametrize(
    ("content", "diagnostic"),
    [(b"", "empty"), (b" \r\n\t\n", "empty"), (b"\xff\xfe# claude", "UTF-8")],
)
def test_empty_or_undecodable_prompts_stop_the_checkout(tmp_path: Path, content: bytes, diagnostic: str) -> None:
    """Resume-session reports these prompts and stops, so the snapshot is an error."""
    root = checkout(tmp_path)
    write(root, PROMPT_NAME, content)
    snapshot = read_checkout_snapshot(root, tracked_directory=no_tracking)
    assert snapshot.state is PromptState.ERROR
    assert diagnostic in snapshot.diagnostic


@pytest.mark.parametrize("field", ["Snapshot", "Project root", "Session role"])
def test_incomplete_prompts_stop_the_checkout(tmp_path: Path, field: str) -> None:
    """A prompt without its pause time, root or role is incomplete."""
    root = checkout(tmp_path)
    write(root, PROMPT_NAME, prompt_text(root, drop=field))
    snapshot = read_checkout_snapshot(root, tracked_directory=no_tracking)
    assert (snapshot.state, snapshot.diagnostic) == (PromptState.ERROR, f"resume prompt is incomplete: missing {field}")


@pytest.mark.parametrize(
    ("old", "new", "diagnostic"),
    [
        (f"- Snapshot: {SNAPSHOT}", "- Snapshot: 2026-11-17T17:37:18", "invalid prompt snapshot"),
        (f"- Snapshot: {SNAPSHOT}", f"- Snapshot: {SNAPSHOT}\n- Snapshot: {SNAPSHOT}", "repeats Snapshot"),
        ("checkout`", "elsewhere`", "names another checkout"),
    ],
)
def test_malformed_prompt_metadata_stops_the_checkout(tmp_path: Path, old: str, new: str, diagnostic: str) -> None:
    """A malformed snapshot, a repeated field or another checkout is an error."""
    root = checkout(tmp_path)
    write(root, PROMPT_NAME, prompt_text(root).replace(old, new, 1))
    snapshot = read_checkout_snapshot(root, tracked_directory=no_tracking)
    assert snapshot.state is PromptState.ERROR
    assert diagnostic in snapshot.diagnostic


def test_prompt_directory_and_unreadable_prompt_are_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Existing but unreadable required evidence is never absence."""
    root = checkout(tmp_path)
    (root / ".reviews" / PROMPT_NAME).mkdir()
    assert "not a file" in read_checkout_snapshot(root, tracked_directory=no_tracking).diagnostic
    (root / ".reviews" / PROMPT_NAME).rmdir()
    write(root, PROMPT_NAME, prompt_text(root))
    real = Path.read_bytes

    def refuse(path: Path) -> bytes:
        if path.name == PROMPT_NAME:
            raise PermissionError(13, "denied")
        return real(path)

    monkeypatch.setattr(Path, "read_bytes", refuse)
    snapshot = read_checkout_snapshot(root, tracked_directory=no_tracking)
    assert (snapshot.state, snapshot.diagnostic) == (PromptState.ERROR, "resume prompt is unreadable: denied")


def test_unused_prompt_metadata_keeps_heading_and_exact_digest(tmp_path: Path) -> None:
    """A CRLF prompt with a byte-order mark parses; its digest covers the exact bytes."""
    root = checkout(tmp_path)
    data = write(root, PROMPT_NAME, b"\xef\xbb\xbf" + prompt_text(root).replace("\n", "\r\n").encode())
    snapshot = read_checkout_snapshot(root, tracked_directory=no_tracking)
    prompt = snapshot.prompt
    assert prompt is not None
    assert snapshot.state is PromptState.UNUSED
    assert (prompt.author, prompt.title, prompt.session_role, prompt.snapshot) == ("claude", TITLE, "requestor", SNAPSHOT)
    assert (prompt.digest, prompt.size, prompt.project_root) == (PromptDigest.of(data), len(data), CanonicalRoot.from_path(root))


def test_legacy_heading_has_an_unknown_author(tmp_path: Path) -> None:
    """A prompt saved before agents named themselves keeps its title and no author."""
    root = checkout(tmp_path)
    metadata, routing = parse_prompt(prompt_text(root).replace("# claude: Resume", "# Resume", 1).encode(), CanonicalRoot.from_path(root))
    assert (metadata.author, metadata.title, routing.state) == (None, f"Resume session: {TITLE}", RoutingState.ABSENT)


@pytest.mark.parametrize("schema", SCHEMAS)
def test_matching_receipts_of_every_schema_mark_the_prompt_used(tmp_path: Path, schema: int) -> None:
    """Schema 1, 2 and 3 receipts for these exact bytes and root consume the prompt."""
    root = checkout(tmp_path)
    data = write(root, PROMPT_NAME, prompt_text(root))
    alias = str(root).upper().replace("\\", "/") + "/"
    write(root, RECEIPT_NAME, receipt_text(schema, PromptDigest.of(data).value.upper(), alias))
    snapshot = read_checkout_snapshot(root, tracked_directory=no_tracking)
    assert snapshot.state is PromptState.USED
    assert snapshot.receipt is not None
    assert snapshot.receipt.schema == schema
    home = root / ".reviews"
    assert snapshot.reads == (home / ".gitignore", home / PROMPT_NAME, home / RECEIPT_NAME)
    assert snapshot.account.files == len(snapshot.reads)
    assert snapshot.account.bytes_read == sum(len(path.read_bytes()) for path in snapshot.reads)


def test_schema_three_receipt_keeps_its_binding_fields(tmp_path: Path) -> None:
    """A marked receipt adds the launch id, receiving pane and assignment binding."""
    receipt = parse_receipt(receipt_text(3, "a" * 64, checkout(tmp_path), {"Receiving pane": REQUESTOR_PANE.upper()}).encode())
    assert (receipt.launch_id, receipt.receiving_pane, receipt.assignment_binding) == (LAUNCH_ID, REQUESTOR_PANE, BINDING)
    assert (receipt.paused_by, receipt.resumed_by, receipt.forced, receipt.used_at) == ("claude", "claude", False, USED_AT)


def test_receipt_for_other_bytes_lets_a_replaced_prompt_resume(tmp_path: Path) -> None:
    """A valid receipt of a consumed earlier prompt does not consume its replacement."""
    root = checkout(tmp_path)
    write(root, PROMPT_NAME, prompt_text(root))
    write(root, RECEIPT_NAME, receipt_text(2, "c" * 64, root))
    assert read_checkout_snapshot(root, tracked_directory=no_tracking).state is PromptState.NEW_SINCE_USE


@pytest.mark.parametrize(
    ("schema", "changes", "diagnostic"),
    [
        (4, {}, "unsupported usage receipt schema"),
        (1, {"Forced": None}, "missing Forced"),
        (1, {"Extra": "x"}, "unexpected Extra"),
        (2, {"Paused by": None}, "missing Paused by"),
        (3, {"Launch id": None}, "missing Launch id"),
        (1, {"SHA-256": "a" * 63}, "invalid SHA-256"),
        (1, {"SHA-256": "g" * 64}, "invalid SHA-256"),
        (1, {"Project root": "relative\\root"}, "invalid receipt project root"),
        (1, {"Project root": "C:\\elsewhere"}, "names another checkout"),
        (1, {"Prompt": "a.prompt.txt"}, "names another prompt"),
        (1, {"Used at": "yesterday"}, "invalid receipt use time"),
        (1, {"Forced": "yes"}, "invalid receipt Forced"),
        (2, {"Resumed by": "Claude Code"}, "invalid receipt Resumed by"),
        (2, {"Agent override": ""}, "invalid receipt Agent override"),
        (3, {"Launch id": "XYZ"}, "invalid receipt Launch id"),
        (3, {"Receiving pane": "77e5f39c"}, "invalid receipt Receiving pane"),
        (3, {"Assignment binding": "z"}, "invalid receipt Assignment binding"),
    ],
)
def test_malformed_receipts_stop_the_checkout(tmp_path: Path, schema: int, changes: dict[str, str | None], diagnostic: str) -> None:
    """A malformed receipt, wrong prompt basename or root is never treated as absent."""
    root = checkout(tmp_path)
    data = write(root, PROMPT_NAME, prompt_text(root))
    write(root, RECEIPT_NAME, receipt_text(schema, PromptDigest.of(data).value, root, changes))
    snapshot = read_checkout_snapshot(root, tracked_directory=no_tracking)
    assert snapshot.state is PromptState.ERROR
    assert diagnostic in snapshot.diagnostic
    assert snapshot.prompt is not None


@pytest.mark.parametrize(
    ("content", "diagnostic"),
    [
        (b"- Schema: 1\n", "no receipt title"),
        (b"# Session resume usage receipt\n\nSchema 1\n", "malformed line"),
        (b"# Session resume usage receipt\n\n- Schema: 1\n- Schema: 1\n", "repeats Schema"),
        (b"\xff", "not UTF-8"),
    ],
)
def test_receipt_grammar_is_strict(content: bytes, diagnostic: str) -> None:
    """Only the titled ``- Name: value`` block above the first section is the receipt."""
    with pytest.raises(ArtifactError, match=diagnostic):
        parse_receipt(content)


def test_custom_home_is_read_and_invalid_homes_stop(tmp_path: Path) -> None:
    """A declared home is honored; a bad declaration, ignore file or tracking is an error."""
    root = checkout(tmp_path, ".private/reviews")
    declaration = root / ".review-artifacts.ini"
    declaration.write_text("[review-artifacts]\nhome = .private/reviews\n", encoding="utf-8")
    (root / ".private" / "reviews" / PROMPT_NAME).write_text(prompt_text(root), encoding="utf-8")
    assert snapshot_of(root)[0] is PromptState.UNUSED
    (root / ".private" / "reviews" / ".gitignore").write_bytes(b"*\r\n")
    assert snapshot_of(root)[2] == "artifact home ignore coverage is invalid"
    (root / ".private" / "reviews" / ".gitignore").unlink()
    assert snapshot_of(root)[2] == "artifact home has no ignore file"
    declaration.write_text("[review-artifacts]\nhome = C:\\outside\n", encoding="utf-8")
    assert "unusable" in str(snapshot_of(root)[2])
    tracked = read_checkout_snapshot(checkout(tmp_path / "t"), tracked_directory=all_tracked)
    assert "tracked" in tracked.diagnostic


def test_declared_home_reads_are_accounted_exactly(tmp_path: Path) -> None:
    """The declaration that the configuration load reads joins the exact reads and bytes."""
    root = checkout(tmp_path, ".private/reviews")
    declaration = root / ".review-artifacts.ini"
    declaration.write_text("[review-artifacts]\nhome = .private/reviews\n", encoding="utf-8")
    (root / ".private" / "reviews" / PROMPT_NAME).write_text(prompt_text(root), encoding="utf-8")
    with recorded_reads() as seen:
        snapshot = read_checkout_snapshot(root, tracked_directory=no_tracking)
    home = root / ".private" / "reviews"
    assert snapshot.reads == (declaration, home / ".gitignore", home / PROMPT_NAME) == tuple(seen)
    assert (snapshot.account.files, snapshot.account.bytes_read) == (len(seen), sizes(snapshot.reads))


def test_rejected_declaration_is_still_accounted(tmp_path: Path) -> None:
    """A declaration read and then refused stays in the account of the failed snapshot."""
    root = checkout(tmp_path)
    declaration = root / ".review-artifacts.ini"
    declaration.write_text("[other]\nhome = .reviews\n", encoding="utf-8")
    with recorded_reads() as seen:
        snapshot = read_checkout_snapshot(root, tracked_directory=no_tracking)
    assert snapshot.state is PromptState.ERROR
    assert snapshot.reads == (declaration,) == tuple(seen)
    assert snapshot.account.bytes_read == declaration.stat().st_size


def test_resolved_routing_is_read_without_any_write(tmp_path: Path) -> None:
    """A used prompt with valid JSON and its rendered table reads without side effects."""
    root = checkout(tmp_path)
    data = write(root, PROMPT_NAME, prompt_text(root, section(root)))
    write(root, RECEIPT_NAME, receipt_text(3, PromptDigest.of(data).value, root))
    assert snapshot_of(root)[:2] == (PromptState.USED, RoutingState.RESOLVED)
    snapshot = read_checkout_snapshot(root, tracked_directory=no_tracking)
    assert snapshot.routing is not None
    assert snapshot.routing.routing == SavedRouting.from_mapping(routing_mapping(root))


def test_routing_free_and_table_only_prompts_are_skipped_not_errors() -> None:
    """Legacy and table-only prompts stay manually readable; bulk launch skips them."""
    root = CanonicalRoot.parse("C:\\work\\checkout")
    path = Path(root.display)
    legacy = "| Target | Agent host and intended role | TUIOS session identity |\n| --- | --- | --- |\n"
    rendered = "\n".join(render_routing_table(SavedRouting.from_mapping(routing_mapping(path))))
    quoted = f"````text\n{raw_block(routing_mapping(path))}````\n"
    for routing, state in (("", RoutingState.ABSENT), (legacy, RoutingState.TABLE_ONLY), (rendered, RoutingState.TABLE_ONLY), (quoted, RoutingState.ABSENT)):
        assert parse_prompt(prompt_text(path, routing).encode(), root)[1].state is state


def test_json_without_table_is_resolved_and_table_escapes_pipes(tmp_path: Path) -> None:
    """The JSON block alone is the routing source; its table escapes cell separators."""
    root = checkout(tmp_path)
    reading = parse_prompt(prompt_text(root, raw_block(routing_mapping(root))).encode(), CanonicalRoot.from_path(root))[1]
    assert reading.state is RoutingState.RESOLVED
    assert reading.routing is not None
    assert "requestor \\| pane" in "\n".join(render_routing_table(reading.routing))


def test_rendered_table_describes_unknown_and_absent_parts() -> None:
    """Unknown and not-applicable parts render their reasons in the readable table."""

    def unknown_pane_single_agent(mapping: dict[str, object]) -> None:
        single_agent(mapping)
        part(mapping, "pause").update(pane={"unknown": "shared daemon"})

    routing = SavedRouting.from_mapping(mutated(Path("C:\\work\\checkout"), unknown_pane_single_agent))
    rows = render_routing_table(routing)
    assert "| Pausing pane | unknown: shared daemon |" in rows
    assert "| Requestor | not applicable: single-agent pause |" in rows
    assert "| Review exchange | not applicable: single-agent pause |" in rows
    assert any(row.startswith("| Resumed agent | implementation on claude in TUIOS session ") for row in rows)


@pytest.mark.parametrize(
    ("slot_name", "reasons"),
    [("resumed", ("resumed target unknown: no pane evidence",)), ("reviewer", ("reviewer target unknown: no pane evidence",))],
)
def test_unknown_routing_targets_preserve_the_pause(tmp_path: Path, slot_name: str, reasons: tuple[str, ...]) -> None:
    """An explicit unknown leaves that target unresolved and keeps the prompt usable."""
    root = checkout(tmp_path)
    mapping = mutated(root, lambda m: part(m, "targets").update({slot_name: {"unknown": "no pane evidence"}}))
    data = write(root, PROMPT_NAME, prompt_text(root, raw_block(mapping)))
    snapshot = read_checkout_snapshot(root, tracked_directory=no_tracking)
    assert snapshot.state is PromptState.UNUSED
    assert snapshot.prompt is not None
    assert snapshot.prompt.digest == PromptDigest.of(data)
    assert snapshot.routing is not None
    assert (snapshot.routing.state, snapshot.routing.reasons) == (RoutingState.UNRESOLVED, reasons)


@pytest.mark.parametrize(
    ("routing", "prompt", "diagnostic"),
    [
        ("table", {}, "table contradicts the routing JSON"),
        ("legacy", {}, "not rendered from the routing JSON"),
        ("twice", {}, "more than one routing JSON block"),
        ("tables", {}, "repeats the routing table"),
        ("open", {}, "not closed"),
        ("json", {}, "invalid routing JSON"),
        ("duplicate", {}, "duplicate JSON key"),
        ("pair", {}, "pair contradicts its exchange"),
        ("section", {"author": "chatgpt"}, "author contradicts the prompt heading"),
        ("section", {"role": "reviewer"}, "session role contradicts the prompt"),
        ("snapshot", {}, "snapshot contradicts the prompt snapshot"),
        ("checkout", {}, "checkout contradicts the prompt project root"),
    ],
)
def test_json_table_and_prompt_contradictions_are_errors(tmp_path: Path, routing: str, prompt: dict[str, str], diagnostic: str) -> None:
    """The JSON block, its rendered table and the prompt header must agree exactly."""
    root = checkout(tmp_path)
    valid = section(root)
    block = raw_block(routing_mapping(root))
    late = mutated(root, lambda m: part(m, "pause").update(snapshot="2026-11-17T17:37:19+01:00"))
    elsewhere = routing_mapping(root.parent / "elsewhere")
    text = {
        "table": valid.replace("| Pause author | claude |", "| Pause author | chatgpt |"),
        "legacy": block + "| Target | Agent host and intended role |\n",
        "twice": block + block,
        "tables": valid + "\n" + valid.split("```\n\n", 1)[1],
        "open": f"{ROUTING_FENCE}\n{{}}\n",
        "json": f"{ROUTING_FENCE}\n{{not json\n```\n",
        "duplicate": f'{ROUTING_FENCE}\n{{"schema": 1, "schema": 1}}\n```\n',
        "pair": raw_block(mutated(root, lambda m: m.update(exchange={"not_applicable": "single agent"}))),
        "section": valid,
        "snapshot": raw_block(late),
        "checkout": raw_block(elsewhere),
    }[routing]
    reading = parse_prompt(prompt_text(root, text, **prompt).encode(), CanonicalRoot.from_path(root))[1]
    assert reading.state is RoutingState.ERROR
    assert diagnostic in reading.reasons[0]


def test_prose_session_role_is_not_compared_with_the_routing(tmp_path: Path) -> None:
    """Only a bare role token can contradict the routing's historical role."""
    root = checkout(tmp_path)
    text = prompt_text(root, section(root), role="implementation writer (and code-review requestor)")
    assert parse_prompt(text.encode(), CanonicalRoot.from_path(root))[1].state is RoutingState.RESOLVED


def test_new_prompts_and_schema_three_receipts_keep_the_tuitp_grammar(tmp_path: Path) -> None:
    """The installed launcher reads the same author, title, role and receipt lines."""
    root = checkout(tmp_path)
    text = prompt_text(root, section(root))
    metadata = parse_prompt(text.encode(), CanonicalRoot.from_path(root))[0]
    heading = TUITP_HEADING.fullmatch(text.splitlines()[0].strip())
    assert heading is not None
    assert (heading[1], heading[2], tuitp_field(text, "Session role")) == (metadata.author, metadata.title, metadata.session_role)
    flag = receipt_text(3, metadata.digest.value, root)
    receipt = parse_receipt(flag.encode())
    assert tuitp_field(flag, "Prompt") == PROMPT_NAME
    assert tuitp_field(flag, "SHA-256") == receipt.digest.value
    assert os.path.normcase(tuitp_field(flag, "Project root") or "") == os.path.normcase(receipt.project_root.display)


# eof
