"""Codex loaded-image identity and session-file input proof tests.

Step 1 of v0.15.0 resume-paused: the image contract accepts only a pinned
release whose process linkage, allocation walk, class 44 identity, digest,
manifest and OS build agree, and rechecks them before input. The input proof
needs exactly one session file whose latest typed input is the delivered
command, with the pre-input version; every other outcome is unsupported.

Fix (design Q28=A follow-up): the real-updater experiment stays deferred, so
the module is unchanged and every recheck stays mandatory. A clean recheck is
never reused: each change of the process, image, path or manifest is still
reported by the next recheck after a clean one.
"""

# ruff: noqa: RUF001

from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from tests.unit.tools.resume_paused_test_support import (
    CHECKOUT,
    CODEX_DIGEST,
    CODEX_NATIVE,
    CODEX_TARGET,
    CODEX_VERSION,
    CREATED,
    HOST_PID,
    MANIFEST_PATH,
    RELEASE_ROOT,
    SESSION_ID,
    SHELL_PID,
    FakeSessionStore,
    FakeWindowsApi,
    at,
    codex_manifest,
    codex_registry,
    codex_session,
    jsonl,
)
from tools.resume_paused_codex import (
    CodexImageProver,
    CodexInputProof,
    CodexInputQuery,
    CodexPaneProfile,
    DirectorySessionStore,
    ReleaseLayout,
    manifest_agrees,
    parse_release_layout,
    prove_codex_input,
    prove_codex_pane,
    refresh_codex_input,
)
from tools.resume_paused_profiles import (
    SUPPORTED_PROFILES,
    ProcessIdentity,
    ReadAccount,
    Reason,
    Verdict,
)
from tools.resume_paused_windows import ImageWalk, ProcessRecord

LAYOUT = ReleaseLayout(RELEASE_ROOT, CODEX_VERSION, CODEX_TARGET, "codex.exe")
COMMAND = "$llm-shared:resume-session rp1:launch-1"
QUERY = CodexInputQuery(text=COMMAND, cwd="C:\\Work\\Checkout\\", delivered_at=at(30), resolution_ns=1_000_000, cli_version=CODEX_VERSION, launch_id="launch-1")
SECOND_CHILD = (ProcessRecord(SHELL_PID, 1, "cmd.exe"), ProcessRecord(HOST_PID, SHELL_PID, "codex.exe"), ProcessRecord(21, SHELL_PID, "codex.exe"))
PARTIAL_WALK = ImageWalk(complete=False, regions=1, mapped_names=(CODEX_NATIVE,))
DOUBLE_WALK = ImageWalk(complete=True, regions=2, mapped_names=(CODEX_NATIVE, CODEX_NATIVE))
RECHECK_CHANGES: list[tuple[dict[str, Any], str]] = [
    ({"listing": (ProcessRecord(SHELL_PID, 1, "cmd.exe"), ProcessRecord(22, SHELL_PID, "codex.exe"))}, "codex-child-not-single"),
    ({"listing": SECOND_CHILD}, "codex-child-not-single"),
    ({"listing": None}, "process-listing-unavailable"),
    ({"created": CREATED + 1}, "process-binding-changed"),
    ({"native": "\\Device\\Volume3\\renamed\\codex.exe"}, "process-binding-changed"),
    ({"walk": PARTIAL_WALK}, "image-walk-incomplete"),
    ({"walk": DOUBLE_WALK}, "image-allocation-not-single"),
    ({"status": 0xC0000001}, "image-identity-rejected"),
    ({"files": {MANIFEST_PATH: codex_manifest(variant="other")}}, "manifest-changed"),
    ({"files": {}}, "manifest-unavailable"),
]


def test_release_layout_is_parsed_from_the_native_image_name() -> None:
    """The standalone release path yields root, version, target and entrypoint."""
    assert parse_release_layout(CODEX_NATIVE) == LAYOUT


@pytest.mark.parametrize(
    "native",
    [
        "\\Device\\Volume3\\npm\\node_modules\\codex\\codex.exe",
        "\\packages\\standalone\\releases\\0.167.2-x86\\codex.exe",
        "\\Device\\V\\packages\\standalone\\releases\\current\\codex.exe",
        "\\Device\\V\\packages\\standalone\\releases\\0.167-x86\\codex.exe",
        "\\Device\\V\\packages\\standalone\\releases\\0.167.2\\codex.exe",
        "\\Device\\V\\packages\\standalone\\releases\\0.167.2-x86",
        "\\Device\\V\\packages\\standalone\\releases\\0.167.2-x86\\..\\codex.exe",
    ],
)
def test_unknown_release_layouts_are_rejected(native: str) -> None:
    """Other layouts, unversioned junctions and escaping paths are unsupported."""
    assert parse_release_layout(native) is None


def test_observed_manifest_agrees_with_its_release() -> None:
    """The exact eight-key layout-1 manifest matches version, target and entrypoint."""
    assert manifest_agrees(codex_manifest(), LAYOUT)
    assert manifest_agrees(codex_manifest(entrypoint="bin/codex.exe"), replace(LAYOUT, entrypoint="bin\\codex.exe"))


@pytest.mark.parametrize(
    "data",
    [
        b"{not json",
        b"[]",
        codex_manifest(extra="key"),
        codex_manifest(layoutVersion=2),
        codex_manifest(layoutVersion=True),
        codex_manifest(variant=3),
        codex_manifest(pathDir="..\\outside"),
        codex_manifest(resourcesDir="C:/elsewhere"),
        codex_manifest(execServer="/rooted"),
        codex_manifest(pathDir=""),
        codex_manifest(version="0.168.0"),
        codex_manifest(target="aarch64-pc-windows-msvc"),
        codex_manifest(entrypoint="other.exe"),
    ],
)
def test_manifest_disagreement_is_rejected(data: bytes) -> None:
    """Unknown schema, wrong types, escaping paths and disagreement fail closed."""
    assert not manifest_agrees(data, LAYOUT)


def test_pinned_release_is_proved_and_handles_are_retained() -> None:
    """A pinned release yields the identity-checked proof and keeps both handles."""
    api = FakeWindowsApi()

    decision = CodexImageProver(api, codex_registry()).prove(SHELL_PID)

    assert decision.verdict is Verdict.SUPPORTED
    assert decision.reasons == ()
    proof = decision.proof
    assert proof is not None
    assert (proof.shell_pid, proof.process, proof.native_name) == (SHELL_PID, ProcessIdentity(HOST_PID, CREATED), CODEX_NATIVE)
    assert (proof.layout, proof.sha256, proof.bytes_hashed) == (LAYOUT, CODEX_DIGEST, 4096)
    assert (proof.process_handle, proof.image_handle) == (1020, 7)
    assert api.closed == []


def test_shipped_registry_keeps_the_observed_release_unsupported() -> None:
    """Without a validated pin the full contract still ends unsupported."""
    api = FakeWindowsApi()

    decision = CodexImageProver(api, SUPPORTED_PROFILES).prove(SHELL_PID)

    assert decision.verdict is Verdict.UNSUPPORTED
    assert decision.proof is None
    assert decision.reasons == (Reason("profile-version-unpinned"),)
    assert api.closed == [1020, 7]


@pytest.mark.parametrize(
    ("change", "reason", "closed"),
    [
        ({"build": None}, "os-build-unavailable", []),
        ({"build": 22631}, "os-build-unpinned", [1020, 7]),
        ({"listing": None}, "process-listing-unavailable", []),
        ({"listing": SECOND_CHILD}, "codex-child-not-single", []),
        ({"listing": ()}, "codex-child-not-single", []),
        ({"process_handle": None}, "process-open-denied", []),
        ({"created": None}, "process-identity-unavailable", [1020]),
        ({"native": None}, "image-name-unavailable", [1020]),
        ({"walk": PARTIAL_WALK}, "image-walk-incomplete", [1020]),
        ({"walk": DOUBLE_WALK}, "image-allocation-not-single", [1020]),
        ({"walk": ImageWalk(complete=True, regions=1, mapped_names=())}, "image-allocation-not-single", [1020]),
        ({"native": "\\Device\\V\\bin\\codex.exe", "walk": ImageWalk(complete=True, regions=1, mapped_names=("\\Device\\V\\bin\\codex.exe",))}, "release-layout-unsupported", [1020]),
        ({"image_handle": None}, "image-open-failed", [1020]),
        ({"status": 0xC0000001}, "image-identity-rejected", [1020, 7]),
        ({"status": 0xC0000022}, "image-identity-rejected", [1020, 7]),
        ({"digest": None}, "image-hash-failed", [1020, 7]),
        ({"digest": ("b" * 64, 4096)}, "image-digest-mismatch", [1020, 7]),
        ({"files": {}}, "manifest-unavailable", [1020, 7]),
        ({"files": {MANIFEST_PATH: codex_manifest(version="9.9.9")}}, "manifest-invalid", [1020, 7]),
    ],
)
def test_each_failed_observation_is_unsupported_and_releases_handles(change: dict[str, Any], reason: str, closed: list[int]) -> None:
    """Every missing, denied, ambiguous or contradictory observation fails closed."""
    api = FakeWindowsApi(**change)

    decision = CodexImageProver(api, codex_registry()).prove(SHELL_PID)

    assert decision.verdict is Verdict.UNSUPPORTED
    assert decision.proof is None
    assert decision.reasons == (Reason(reason),)
    assert api.closed == closed


def test_digest_is_hashed_once_per_image_within_an_invocation() -> None:
    """A second proof of the same generation reuses the invocation digest."""
    api = FakeWindowsApi()
    prover = CodexImageProver(api, codex_registry())

    first = prover.prove(SHELL_PID)
    second = prover.prove(SHELL_PID)

    assert first.proof == second.proof
    assert api.hashed == 1


def test_recheck_passes_while_every_binding_is_unchanged() -> None:
    """Before input the same generation, image and manifest recheck clean."""
    api = FakeWindowsApi()
    prover = CodexImageProver(api, codex_registry())
    proof = prover.prove(SHELL_PID).proof
    assert proof is not None

    assert prover.recheck(proof) == ()
    prover.release(proof)

    assert api.closed == [7, 1020]


@pytest.mark.parametrize(("change", "reason"), RECHECK_CHANGES)
def test_recheck_reports_each_changed_binding(change: dict[str, Any], reason: str) -> None:
    """A replaced child, restarted process, renamed image or new manifest stops input."""
    api = FakeWindowsApi()
    prover = CodexImageProver(api, codex_registry())
    proof = prover.prove(SHELL_PID).proof
    assert proof is not None
    for name, value in change.items():
        setattr(api, name, value)

    assert prover.recheck(proof) == (Reason(reason),)


@pytest.mark.parametrize(("change", "reason"), RECHECK_CHANGES)
def test_clean_recheck_is_never_reused(change: dict[str, Any], reason: str) -> None:
    """With the real-updater experiment deferred (Q28=A), a change after a clean recheck is still reported."""
    api = FakeWindowsApi()
    prover = CodexImageProver(api, codex_registry())
    proof = prover.prove(SHELL_PID).proof
    assert proof is not None
    assert prover.recheck(proof) == ()
    for name, value in change.items():
        setattr(api, name, value)

    assert prover.recheck(proof) == (Reason(reason),)


def test_unique_latest_input_is_proved_with_bytes_accounted() -> None:
    """One file modified since delivery holds the command as its latest input."""
    live = codex_session([("earlier", at(20)), (COMMAND, at(31))])
    old = codex_session([(COMMAND, at(31))])
    store = FakeSessionStore({"2026/11/13/old.jsonl": old, "2026/11/14/live.jsonl": live}, {"2026/11/13/old.jsonl": at(10)})

    decision = prove_codex_input(store, QUERY)

    assert decision.verdict is Verdict.SUPPORTED
    assert decision.proof == CodexInputProof("2026/11/14/live.jsonl", SESSION_ID, CODEX_VERSION, "launch-1")
    assert decision.account == ReadAccount(files=1, bytes_read=len(live))


def test_older_partition_file_still_written_after_delivery_is_a_candidate() -> None:
    """An older date partition counts when its file changed since delivery."""
    live = codex_session([(COMMAND, at(31))])
    store = FakeSessionStore({"2026/11/01/long-running.jsonl": live}, {"2026/11/01/long-running.jsonl": at(31)})

    assert prove_codex_input(store, QUERY).proof == CodexInputProof("2026/11/01/long-running.jsonl", SESSION_ID, CODEX_VERSION, "launch-1")


def test_modification_boundary_allows_only_the_documented_resolution() -> None:
    """A file modified within the resolution before delivery is still read."""
    data = codex_session([(COMMAND, at(30))])
    inside = FakeSessionStore({"a.jsonl": data}, {"a.jsonl": at(30) - timedelta(microseconds=500)})
    outside = FakeSessionStore({"a.jsonl": data}, {"a.jsonl": at(30) - timedelta(milliseconds=2)})

    assert prove_codex_input(inside, QUERY).verdict is Verdict.SUPPORTED
    assert prove_codex_input(outside, QUERY).reasons == (Reason("input-not-found"),)
    assert prove_codex_input(outside, QUERY).account == ReadAccount()


@pytest.mark.parametrize(
    ("files", "reason"),
    [
        ({"a.jsonl": codex_session([(COMMAND, at(31))]), "b.jsonl": codex_session([(COMMAND, at(32))])}, "input-ambiguous"),
        ({"a.jsonl": codex_session([(COMMAND, at(31)), ("later input", at(40))])}, "input-not-found"),
        ({"a.jsonl": codex_session([(COMMAND + " extra", at(31))])}, "input-not-found"),
        ({"a.jsonl": codex_session([(COMMAND, at(29))])}, "input-not-found"),
        ({"a.jsonl": codex_session([(COMMAND, at(31).replace(tzinfo=None))])}, "record-invalid"),
        ({"a.jsonl": codex_session([(COMMAND, at(31))], cwd="C:/work/other")}, "input-not-found"),
        ({"a.jsonl": codex_session([])}, "input-not-found"),
        ({"a.jsonl": codex_session([(COMMAND, at(31))], version="0.168.0")}, "cli-version-mismatch"),
        ({"a.jsonl": None}, "read-failed"),
        ({"a.jsonl": codex_session([(COMMAND, at(31))])[:-1]}, "record-incomplete"),
        ({"a.jsonl": b"{broken\n"}, "record-invalid"),
        ({"a.jsonl": b'{"type": "session_meta", "payload": 3}\n'}, "record-invalid"),
        ({"a.jsonl": b'{"type": "response_item", "payload": {"role": "user"}}\n'}, "session-meta-ambiguous"),
        ({"a.jsonl": codex_session([(COMMAND, at(31))]) + b'{"type": "response_item", "timestamp": "never", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "later"}]}}\n'}, "record-invalid"),
    ],
)
def test_unproved_input_is_unsupported(files: dict[str, bytes | None], reason: str) -> None:
    """Duplicates, later input, wrong text, time, checkout, version or damage fail closed."""
    decision = prove_codex_input(FakeSessionStore(files), QUERY)

    assert decision.verdict is Verdict.UNSUPPORTED
    assert decision.proof is None
    assert decision.reasons == (Reason(reason),)


def test_incomplete_enumeration_is_unsupported() -> None:
    """A session root that cannot be listed completely proves nothing."""
    decision = prove_codex_input(FakeSessionStore({}, complete=False), QUERY)

    assert decision.reasons == (Reason("enumeration-incomplete"),)
    assert decision.account == ReadAccount()


def test_refresh_reproves_the_same_file_after_scroll_off() -> None:
    """A later validation accepts only the carried session identity."""
    store = FakeSessionStore({"a.jsonl": codex_session([(COMMAND, at(31))])})
    proof = prove_codex_input(store, QUERY).proof
    assert proof is not None

    assert refresh_codex_input(store, QUERY, proof).proof == proof
    changed = refresh_codex_input(store, QUERY, replace(proof, path="b.jsonl"))
    store.files["a.jsonl"] = codex_session([(COMMAND, at(31)), ("new input", at(50))])
    lost = refresh_codex_input(store, QUERY, proof)

    assert changed.reasons == (Reason("input-identity-changed"),)
    assert changed.proof is None
    assert lost.reasons == (Reason("input-not-found"),)


def test_checkout_comparison_ignores_separators_case_and_trailing_slash() -> None:
    """The recorded checkout matches across separator and case differences."""
    store = FakeSessionStore({"a.jsonl": codex_session([(COMMAND, at(31))], cwd=CHECKOUT.upper() + "/")})

    assert prove_codex_input(store, QUERY).verdict is Verdict.SUPPORTED


@pytest.mark.parametrize("launch_id", ["", "launch-2"])
def test_command_must_carry_the_delivery_launch_id(launch_id: str) -> None:
    """A missing launch id, or one the delivered command lacks, proves nothing."""
    store = FakeSessionStore({"a.jsonl": codex_session([(COMMAND, at(31))])})

    decision = prove_codex_input(store, replace(QUERY, launch_id=launch_id))

    assert decision.reasons == (Reason("launch-id-not-in-command"),)
    assert decision.account == ReadAccount()


def test_refresh_rejects_a_proof_carried_from_another_delivery() -> None:
    """The carried launch id must be the one of the proved delivery."""
    store = FakeSessionStore({"a.jsonl": codex_session([(COMMAND, at(31))])})
    proof = prove_codex_input(store, QUERY).proof
    assert proof is not None

    assert proof.launch_id == "launch-1"
    assert refresh_codex_input(store, QUERY, replace(proof, launch_id="launch-0")).reasons == (Reason("input-identity-changed"),)


PANE = CodexPaneProfile(prompt_prefix="› ", working_pattern=r"• Working \(\d+s .*\)")
SUBMITTED = "› $llm-shared:resume-session rp1:launch-1"
WORKING = "• Working (3s • esc to interrupt)"


def test_pane_shows_one_submitted_launch_followed_by_the_working_line() -> None:
    """The delivery is tied to its pane by its submitted launch id, then the working line."""
    assert prove_codex_pane(["› earlier prompt", SUBMITTED, "", WORKING], "launch-1", PANE) == ()


@pytest.mark.parametrize(
    ("capture", "launch_id", "reason"),
    [
        (["› other command", WORKING], "launch-1", "launch-prefix-missing"),
        ([SUBMITTED + "0", WORKING], "launch-1", "launch-prefix-missing"),
        (["› rp1:xlaunch-1", WORKING], "launch-1", "launch-prefix-missing"),
        ([SUBMITTED, WORKING, SUBMITTED], "launch-1", "launch-prefix-repeated"),
        ([SUBMITTED, WORKING, "tool output quoting launch-1"], "launch-1", "launch-prefix-repeated"),
        (["quoted launch-1", WORKING], "launch-1", "launch-prefix-unattributed"),
        (["  › indented rp1:launch-1", WORKING], "launch-1", "launch-prefix-unattributed"),
        ([WORKING, SUBMITTED], "launch-1", "working-signature-missing"),
        ([SUBMITTED, "documentation about Working"], "launch-1", "working-signature-missing"),
        ([SUBMITTED, "› Ask Codex to do anything"], "launch-1", "working-signature-missing"),
        ([SUBMITTED, WORKING + " trailing"], "launch-1", "working-signature-missing"),
    ],
)
def test_pane_without_a_unique_accepted_launch_is_rejected(capture: list[str], launch_id: str, reason: str) -> None:
    """Quoted output, prose, placeholders, longer ids and unfollowed prompts do not tie the pane."""
    assert prove_codex_pane(capture, launch_id, PANE) == (Reason(reason),)


@pytest.mark.parametrize(
    ("launch_id", "profile"),
    [
        ("", PANE),
        ("launch-1", CodexPaneProfile(prompt_prefix="", working_pattern="Working")),
        ("launch-1", CodexPaneProfile(prompt_prefix="› ", working_pattern="")),
        ("launch-1", CodexPaneProfile(prompt_prefix="› ", working_pattern="Working (")),
    ],
)
def test_empty_or_invalid_pane_signature_is_unsupported(launch_id: str, profile: CodexPaneProfile) -> None:
    """An empty launch id, prefix or pattern, or an invalid pattern, accepts nothing."""
    assert prove_codex_pane([SUBMITTED, WORKING], launch_id, profile) == (Reason("pane-signature-unsupported"),)


def session_records(meta: dict[str, Any], payload: dict[str, Any]) -> bytes:
    """Render one session file from a declared metadata payload and latest user payload."""
    return jsonl([
        {"type": "session_meta", "payload": meta},
        {"type": "response_item", "timestamp": at(31).isoformat(), "payload": payload},
    ])


META: dict[str, Any] = {"id": SESSION_ID, "cwd": CHECKOUT, "cli_version": CODEX_VERSION}
MESSAGE: dict[str, Any] = {"type": "message", "role": "user", "content": [{"type": "input_text", "text": COMMAND}]}


def test_well_formed_declared_records_are_proved() -> None:
    """The declared metadata and message shapes are the supported ones."""
    assert prove_codex_input(FakeSessionStore({"a.jsonl": session_records(META, MESSAGE)}), QUERY).verdict is Verdict.SUPPORTED


@pytest.mark.parametrize(
    ("meta", "payload", "reason"),
    [
        ({key: value for key, value in META.items() if key != "id"}, MESSAGE, "session-meta-invalid"),
        ({**META, "id": None}, MESSAGE, "session-meta-invalid"),
        ({**META, "id": 7}, MESSAGE, "session-meta-invalid"),
        ({**META, "id": ""}, MESSAGE, "session-meta-invalid"),
        ({**META, "cwd": None}, MESSAGE, "session-meta-invalid"),
        ({**META, "cli_version": 167}, MESSAGE, "session-meta-invalid"),
        (META, {**MESSAGE, "type": "reasoning"}, "input-shape-unsupported"),
        (META, {key: value for key, value in MESSAGE.items() if key != "type"}, "input-shape-unsupported"),
        (META, {**MESSAGE, "content": [{"type": "text", "text": COMMAND}]}, "input-shape-unsupported"),
        (META, {**MESSAGE, "content": [{"type": "input_text", "text": 3}]}, "input-shape-unsupported"),
        (META, {**MESSAGE, "content": [*MESSAGE["content"], {"type": "input_text", "text": "more"}]}, "input-shape-unsupported"),
        (META, {**MESSAGE, "content": COMMAND}, "input-shape-unsupported"),
    ],
)
def test_malformed_session_identity_or_input_shape_is_unsupported(meta: dict[str, Any], payload: dict[str, Any], reason: str) -> None:
    """A missing or mistyped session identity and an unsupported input shape prove nothing."""
    decision = prove_codex_input(FakeSessionStore({"a.jsonl": session_records(meta, payload)}), QUERY)

    assert decision.proof is None
    assert decision.reasons == (Reason(reason),)


def test_repeated_json_key_or_second_metadata_record_is_invalid_evidence() -> None:
    """A record that repeats a key, or a second metadata record, is rejected."""
    session = codex_session([(COMMAND, at(31))])
    repeated = session + b'{"type": "response_item", "type": "event_msg", "payload": {"role": "user"}}\n'

    assert prove_codex_input(FakeSessionStore({"a.jsonl": repeated}), QUERY).reasons == (Reason("record-invalid"),)
    assert prove_codex_input(FakeSessionStore({"a.jsonl": session * 2}), QUERY).reasons == (Reason("session-meta-ambiguous"),)


def test_directory_store_lists_every_partition_and_reads_through_the_reader(tmp_path: Path) -> None:
    """A real session root is listed across date partitions and proved like a declared one."""
    live = tmp_path / "2026" / "11" / "14" / "live.jsonl"
    live.parent.mkdir(parents=True)
    live.write_bytes(codex_session([(COMMAND, at(31))]))
    store = DirectorySessionStore(str(tmp_path), lambda path: Path(path).read_bytes())

    listing = store.list_files()
    decision = prove_codex_input(store, replace(QUERY, delivered_at=at(0).replace(year=1971)))

    assert listing is not None
    assert [(Path(file.path).name, file.size) for file in listing] == [("live.jsonl", len(live.read_bytes()))]
    assert decision.proof == CodexInputProof(str(live), SESSION_ID, CODEX_VERSION, "launch-1")
    assert decision.account == ReadAccount(files=1, bytes_read=len(live.read_bytes()))
    assert DirectorySessionStore(str(tmp_path / "absent"), lambda _path: None).list_files() is None


# eof
