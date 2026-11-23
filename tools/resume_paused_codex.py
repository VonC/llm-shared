"""Codex loaded-image identity and session-file input proof for resume-paused.

Step 1 of v0.15.0 resume-paused implements the two Codex evidence contracts of
the consolidated design. ``CodexImageProver`` runs the query-only loaded-image
sequence on a pane shell's single direct Codex child and accepts only a pinned
release whose layout, manifest, digest and OS build all agree. ``prove_codex_input``
proves the complete latest typed input through exactly one session file (Q14),
and ``refresh_codex_input`` re-proves the same file later (Q15). Every failure
is unsupported evidence with a classified reason; nothing here sends input.

Fix (Step 1 missing work): ``prove_codex_pane`` ties a delivery to its pane
through its unique launch id followed by the profile's ``Working`` signature,
the input proof carries that launch id, and ``DirectorySessionStore`` lists a
real session root completely or reports the enumeration incomplete.

Fix (code review round 1, R7 and R8): the input proof requires a well-typed
session identity and the supported single ``input_text`` message, rejects
repeated JSON keys, and the pane proof matches the pinned submitted-command
and working-line signatures on whole tokens and whole lines.
"""

# ruff: noqa: EM101, TRY301

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Final, Protocol

from tools.resume_paused_profiles import (
    Host,
    ProcessIdentity,
    ReadAccount,
    Reason,
    Verdict,
    as_items,
    as_mapping,
    as_text,
    loads_strict,
)
from tools.resume_paused_windows import GLOBALROOT, direct_children, list_jsonl_files

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from tools.resume_paused_profiles import ProfileRegistry
    from tools.resume_paused_windows import WindowsApi

CODEX_IMAGE: Final = "codex.exe"
MANIFEST_NAME: Final = "codex-package.json"
_RELEASES: Final = "\\packages\\standalone\\releases\\"
_MANIFEST_TEXT_KEYS: Final = ("entrypoint", "execServer", "pathDir", "resourcesDir", "target", "variant", "version")
_MANIFEST_KEYS: Final = frozenset({*_MANIFEST_TEXT_KEYS, "layoutVersion"})
_MANIFEST_PATH_KEYS: Final = ("entrypoint", "execServer", "pathDir", "resourcesDir")
_VERSION_PARTS: Final = 3


class _RejectedError(Exception):
    """One classified reason that ends a proof without input."""


@dataclass(frozen=True)
class ReleaseLayout:
    """Standalone release location parsed from a native image name."""

    release_root: str
    version: str
    target: str
    entrypoint: str


@dataclass(frozen=True)
class CodexImageProof:
    """Identity-checked loaded image of one Codex process generation.

    The process and image handles stay open so each later recheck repeats the
    identity query on the same file object. ``release`` closes them.
    """

    shell_pid: int
    process: ProcessIdentity
    native_name: str
    layout: ReleaseLayout
    sha256: str
    bytes_hashed: int
    manifest_sha256: str
    process_handle: int
    image_handle: int


@dataclass(frozen=True)
class CodexImageDecision:
    """Supported with a proof, or unsupported with classified reasons."""

    verdict: Verdict
    proof: CodexImageProof | None
    reasons: tuple[Reason, ...]


def _escapes(path: str) -> bool:
    """Tell whether a manifest path is absolute or leaves its release."""
    parts = path.replace("\\", "/").split("/")
    return not path or ":" in path or parts[0] == "" or ".." in parts


def parse_release_layout(native_name: str) -> ReleaseLayout | None:
    """Parse ``<root>/packages/standalone/releases/<version>-<target>/<entrypoint>``."""
    root, separator, tail = native_name.partition(_RELEASES)
    directory, _, entrypoint = tail.partition("\\")
    version, _, target = directory.partition("-")
    numbers = version.split(".")
    numeric = len(numbers) == _VERSION_PARTS and all(part.isdecimal() for part in numbers)
    if not (root and separator and numeric and target and not _escapes(entrypoint)):
        return None
    return ReleaseLayout(root + _RELEASES + directory, version, target, entrypoint)


def _manifest_texts(data: bytes) -> dict[str, str] | None:
    """Return the seven text values of an exact eight-key layout-1 manifest."""
    try:
        manifest = as_mapping(loads_strict(data))
    except ValueError:
        return None
    layout_version = manifest.get("layoutVersion")
    if frozenset(manifest) != _MANIFEST_KEYS or type(layout_version) is not int or layout_version != 1:
        return None
    texts = {key: text for key in _MANIFEST_TEXT_KEYS if (text := as_text(manifest[key])) is not None}
    return texts if len(texts) == len(_MANIFEST_TEXT_KEYS) else None


def manifest_agrees(data: bytes, layout: ReleaseLayout) -> bool:
    """Validate the exact eight-key layout-1 manifest against its release."""
    texts = _manifest_texts(data)
    if texts is None or any(_escapes(texts[key]) for key in _MANIFEST_PATH_KEYS):
        return False
    entrypoint = texts["entrypoint"].replace("/", "\\")
    return (texts["version"], texts["target"], entrypoint) == (layout.version, layout.target, layout.entrypoint)


class CodexImageProver:
    """Run the loaded-image identity contract through an injected Windows API."""

    def __init__(self, api: WindowsApi, registry: ProfileRegistry) -> None:
        """Keep the API, the pinned profiles and an invocation-only digest cache."""
        self._api = api
        self._registry = registry
        self._digests: dict[tuple[int, int, str], tuple[str, int]] = {}

    def prove(self, shell_pid: int) -> CodexImageDecision:
        """Prove the pinned release loaded by the shell's single direct Codex child."""
        handles: list[int] = []
        try:
            proof = self._prove(shell_pid, handles)
        except _RejectedError as rejected:
            for handle in handles:
                self._api.close(handle)
            return CodexImageDecision(Verdict.UNSUPPORTED, None, (Reason(str(rejected)),))
        return CodexImageDecision(Verdict.SUPPORTED, proof, ())

    def recheck(self, proof: CodexImageProof) -> tuple[Reason, ...]:
        """Repeat every mutable binding before an input; empty means unchanged."""
        try:
            if self._single_child(proof.shell_pid) != proof.process.pid:
                raise _RejectedError("codex-child-not-single")
            self._bindings(proof.process_handle, proof.process.created_at, proof.native_name)
            self._identity(proof.process_handle, proof.image_handle)
            if self._manifest(proof.layout) != proof.manifest_sha256:
                raise _RejectedError("manifest-changed")
        except _RejectedError as rejected:
            return (Reason(str(rejected)),)
        return ()

    def release(self, proof: CodexImageProof) -> None:
        """Close the handles retained by a proof."""
        self._api.close(proof.image_handle)
        self._api.close(proof.process_handle)

    def _prove(self, shell_pid: int, handles: list[int]) -> CodexImageProof:
        build = self._require(self._api.os_build(), "os-build-unavailable")
        pid = self._single_child(shell_pid)
        process = self._require(self._api.open_process(pid), "process-open-denied")
        handles.append(process)
        created = self._require(self._api.creation_time(process), "process-identity-unavailable")
        native = self._require(self._api.native_image_name(process), "image-name-unavailable")
        self._bindings(process, created, native)
        layout = self._require(parse_release_layout(native), "release-layout-unsupported")
        image = self._require(self._api.open_image(native), "image-open-failed")
        handles.append(image)
        self._identity(process, image)
        key = (pid, created, native)
        if key not in self._digests:
            self._digests[key] = self._require(self._api.sha256(image), "image-hash-failed")
        digest, size = self._digests[key]
        manifest = self._manifest(layout)
        decision = self._registry.select(Host.CODEX, layout.version, build, digest)
        if decision.verdict is not Verdict.SUPPORTED:
            raise _RejectedError(decision.reasons[0].code)
        identity = ProcessIdentity(pid, created)
        return CodexImageProof(shell_pid, identity, native, layout, digest, size, manifest, process, image)

    @staticmethod
    def _require(value: Any, code: str) -> Any:  # noqa: ANN401
        if value is None:
            raise _RejectedError(code)
        return value

    def _single_child(self, shell_pid: int) -> int:
        """Resolve the pane shell's single direct Codex child from a fresh listing."""
        listing = self._require(self._api.processes(), "process-listing-unavailable")
        matches = direct_children(listing, shell_pid, CODEX_IMAGE)
        if len(matches) != 1:
            raise _RejectedError("codex-child-not-single")
        return matches[0].pid

    def _bindings(self, process: int, created: int, native: str) -> None:
        """Require the same generation, native name and one matching image allocation."""
        if self._api.creation_time(process) != created or self._api.native_image_name(process) != native:
            raise _RejectedError("process-binding-changed")
        walk = self._api.image_walk(process)
        if not walk.complete:
            raise _RejectedError("image-walk-incomplete")
        if walk.mapped_names.count(native) != 1:
            raise _RejectedError("image-allocation-not-single")

    def _identity(self, process: int, image: int) -> None:
        if self._api.image_mapping_status(process, image) != 0:
            raise _RejectedError("image-identity-rejected")

    def _manifest(self, layout: ReleaseLayout) -> str:
        path = f"{GLOBALROOT}{layout.release_root}\\{MANIFEST_NAME}"
        data = self._require(self._api.read_file(path), "manifest-unavailable")
        if not manifest_agrees(data, layout):
            raise _RejectedError("manifest-invalid")
        return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class SessionFile:
    """Metadata of one regular session JSONL file from a complete enumeration."""

    path: str
    modified_ns: int
    size: int


class SessionStore(Protocol):
    """Injected session-root access across every date partition."""

    def list_files(self) -> tuple[SessionFile, ...] | None:
        """Return every regular JSONL file, or ``None`` when enumeration is incomplete."""
        ...

    def read(self, path: str) -> bytes | None:
        """Read one file completely while its writer keeps it open."""
        ...


@dataclass(frozen=True)
class CodexInputQuery:
    """The delivered command, its checkout, delivery instant and pre-input version.

    ``resolution_ns`` is the documented filesystem timestamp resolution allowed
    at the lower modification-time boundary.
    """

    text: str
    cwd: str
    delivered_at: datetime
    resolution_ns: int
    cli_version: str
    launch_id: str


@dataclass(frozen=True)
class CodexInputProof:
    """Non-secret identity of the unique session file holding the latest input.

    The delivery's launch id is carried with it, so a later validation can
    re-prove the same file for the same delivery after the pane scrolled.
    """

    path: str
    session_id: str
    cli_version: str
    launch_id: str


@dataclass(frozen=True)
class CodexInputDecision:
    """Supported with a proof, or unsupported, always with bytes accounted."""

    verdict: Verdict
    proof: CodexInputProof | None
    reasons: tuple[Reason, ...]
    account: ReadAccount


def _folded(path: str) -> str:
    return path.replace("\\", "/").rstrip("/").casefold()


def _records(data: bytes) -> list[tuple[dict[str, object], dict[str, object]]]:
    """Parse complete JSONL records into ``(record, payload)`` pairs.

    Raises:
        _RejectedError: The file lacks its final newline, holds a line that is
            not JSON, or holds a record without an object payload.
    """
    if not data.endswith(b"\n"):
        raise _RejectedError("record-incomplete")
    try:
        records = [as_mapping(loads_strict(line)) for line in data.splitlines() if line.strip()]
    except ValueError:
        raise _RejectedError("record-invalid") from None
    pairs = [(record, as_mapping(record.get("payload"))) for record in records]
    if not all(payload for _, payload in pairs):
        raise _RejectedError("record-invalid")
    return pairs


def _typed_at(record: dict[str, object]) -> datetime:
    """Return the timezone-aware instant of one record, or reject the file."""
    try:
        moment = datetime.fromisoformat(str(record.get("timestamp")))
    except ValueError:
        raise _RejectedError("record-invalid") from None
    if moment.tzinfo is None:
        raise _RejectedError("record-invalid")
    return moment


def _session_meta(pairs: list[tuple[dict[str, object], dict[str, object]]]) -> tuple[str, str, str]:
    """Return session id, checkout and version of the single ``session_meta`` record.

    Raises:
        _RejectedError: The file has no or several such records, or one whose
            identity, checkout or version is not a nonempty string.
    """
    metas = [payload for record, payload in pairs if record.get("type") == "session_meta"]
    if len(metas) != 1:
        raise _RejectedError("session-meta-ambiguous")
    session_id, cwd, version = (as_text(metas[0].get(key)) for key in ("id", "cwd", "cli_version"))
    if not (session_id and cwd and version):
        raise _RejectedError("session-meta-invalid")
    return session_id, cwd, version


def _input_text(payload: dict[str, object]) -> str:
    """Return the text of a supported complete user input record.

    Raises:
        _RejectedError: The latest user record is not one ``message`` holding
            exactly one ``input_text`` block with string text.
    """
    content = as_items(payload.get("content"))
    block = as_mapping(content[0]) if len(content) == 1 else {}
    text = as_text(block.get("text"))
    if payload.get("type") != "message" or block.get("type") != "input_text" or text is None:
        raise _RejectedError("input-shape-unsupported")
    return text


def _latest_input_matches(data: bytes, query: CodexInputQuery) -> tuple[str, str] | None:
    """Return session id and version when the latest user input is the delivered command."""
    pairs = _records(data)
    session_id, cwd, version = _session_meta(pairs)
    inputs = [pair for pair in pairs if pair[0].get("type") == "response_item" and pair[1].get("role") == "user"]
    if not inputs:
        return None
    record, payload = inputs[-1]
    exact = _input_text(payload) == query.text
    late = _typed_at(record) >= query.delivered_at
    return (session_id, version) if exact and late and _folded(cwd) == _folded(query.cwd) else None


def _launch_id(query: CodexInputQuery) -> str:
    """Return the delivery's launch id, which the delivered command must carry."""
    if not query.launch_id or query.launch_id not in query.text:
        raise _RejectedError("launch-id-not-in-command")
    return query.launch_id


@dataclass(frozen=True)
class CodexPaneProfile:
    """Pinned screen signatures of one Codex release.

    ``prompt_prefix`` starts the line that shows a submitted command.
    ``working_pattern`` is a regular expression that must match a whole
    captured line while the host works on an accepted turn.
    """

    prompt_prefix: str
    working_pattern: str


def _working_pattern(launch_id: str, profile: CodexPaneProfile) -> re.Pattern[str] | None:
    """Compile the working-line pattern, or ``None`` for an empty or invalid signature."""
    if not (launch_id and profile.prompt_prefix and profile.working_pattern):
        return None
    try:
        return re.compile(profile.working_pattern)
    except re.error:
        return None


def prove_codex_pane(capture: Sequence[str], launch_id: str, profile: CodexPaneProfile) -> tuple[Reason, ...]:
    """Tie the delivery to its pane: one submitted launch id, then the working line.

    Args:
        capture: The pane's captured lines, oldest first.
        launch_id: This delivery's unique launch id.
        profile: The pinned screen signatures of the pane's Codex release.

    Returns:
        No reason when the launch id appears as a whole token on exactly one
        line, that line is a submitted-command line, and a later whole line
        matches the working pattern; otherwise the classified reason. Quoted
        output, prose, a longer id and an empty signature never tie the pane.
    """
    working = _working_pattern(launch_id, profile)
    if working is None:
        return (Reason("pane-signature-unsupported"),)
    token = re.compile(rf"(?<![\w-]){re.escape(launch_id)}(?![\w-])")
    hits = [index for index, line in enumerate(capture) if token.search(line)]
    if len(hits) != 1:
        return (Reason("launch-prefix-repeated" if hits else "launch-prefix-missing"),)
    if not capture[hits[0]].startswith(profile.prompt_prefix):
        return (Reason("launch-prefix-unattributed"),)
    if not any(working.fullmatch(line) for line in capture[hits[0] + 1 :]):
        return (Reason("working-signature-missing"),)
    return ()


class DirectorySessionStore:
    """``SessionStore`` over a real session root, read through shared reads."""

    def __init__(self, root: str, read: Callable[[str], bytes | None]) -> None:
        """Keep the configured session root and the injected whole-file reader."""
        self._root = root
        self._read = read

    def list_files(self) -> tuple[SessionFile, ...] | None:
        """List every regular JSONL file across all date partitions."""
        files = list_jsonl_files(self._root)
        return None if files is None else tuple(SessionFile(file.path, file.modified_ns, file.size) for file in files)

    def read(self, path: str) -> bytes | None:
        """Read one session file completely."""
        return self._read(path)


def prove_codex_input(store: SessionStore, query: CodexInputQuery) -> CodexInputDecision:
    """Prove the delivered command as the latest input of exactly one session file.

    Candidates are files modified since delivery, less the documented timestamp
    resolution. Uniqueness is judged across all of them, and the file's
    ``cli_version`` must equal the independent pre-input version.
    """
    account = ReadAccount()
    listing = store.list_files()
    if listing is None:
        return CodexInputDecision(Verdict.UNSUPPORTED, None, (Reason("enumeration-incomplete"),), account)
    boundary = int(query.delivered_at.timestamp() * 1_000_000_000) - query.resolution_ns
    proofs: list[CodexInputProof] = []
    try:
        launch_id = _launch_id(query)
        for candidate in listing:
            if candidate.modified_ns < boundary:
                continue
            data = store.read(candidate.path)
            if data is None:
                raise _RejectedError("read-failed")
            account = account.plus(len(data))
            match = _latest_input_matches(data, query)
            if match is not None:
                proofs.append(CodexInputProof(candidate.path, *match, launch_id))
        if len(proofs) != 1:
            raise _RejectedError("input-not-found" if not proofs else "input-ambiguous")
        if proofs[0].cli_version != query.cli_version:
            raise _RejectedError("cli-version-mismatch")
    except _RejectedError as rejected:
        return CodexInputDecision(Verdict.UNSUPPORTED, None, (Reason(str(rejected)),), account)
    return CodexInputDecision(Verdict.SUPPORTED, proofs[0], (), account)


def refresh_codex_input(store: SessionStore, query: CodexInputQuery, proof: CodexInputProof) -> CodexInputDecision:
    """Re-prove the same unique file and unchanged latest input after scroll-off."""
    decision = prove_codex_input(store, query)
    if decision.verdict is Verdict.SUPPORTED and decision.proof != proof:
        return CodexInputDecision(Verdict.UNSUPPORTED, None, (Reason("input-identity-changed"),), decision.account)
    return decision


# eof
