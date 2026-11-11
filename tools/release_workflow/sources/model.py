"""Version tokens, forms, the read-once file view and the shared source model.

Step 2 of v0.14.0 version-sources. One token grammar serves the anchor, the
`set` argument, configuration and source values, ordered by the integer triple
of its core. A form maps the anchor token to a source's expected value, and the
release-only guard refuses a release-only value above its target. Adapters read
through a `FileView` that loads each path once per phase, report located
sources and visible records, and never write: the transition composes every
edit of a file from one captured original. The shared input, capture, edit,
inventory and plan types live here for every later step (plan decision Q16).

Step 3 adds `PatternDeclaration` and exposes the declared pattern sources
through `AdapterSettings`: the pattern adapter reads them through the same
`detect` signature as every adapter, which a narrower settings type would
break for the registered tuple.

Step 5 adds the declared component roots and a `participant` lookup to
`AdapterSettings`, with `participant_names`, the index behind it: the python
adapter matches uv workspace members against the component roots, and finds
the participating root a local link reaches in one lookup, so detection stays
linear in the roots.

Step 6 adds the configured form overrides to `AdapterSettings`, which the npm
adapter is the first to apply, and `FileView.derived`, a value computed once
per phase from the view's files: the npm adapter indexes the participating
package names there once, so its `workspace:` check stays linear in the roots.

Step 7 adds `AdapterSettings.authorize`: the Maven adapter authorizes every
POM it discovers with the project's physical path policy before reading it,
and keys modules, sources and claims by the physical path, so a link cannot
make one file look like two.

This module imports only the standard library at run time; foundation types
are imported for type checking only.
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Literal, Protocol, cast

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping, Sequence
    from pathlib import Path

    from tools.release_workflow.artifacts import ArtifactDeclaration
    from tools.release_workflow.configuration import Configuration
    from tools.release_workflow.git import GitExecutionContext
    from tools.release_workflow.invocation import InvocationContext
    from tools.release_workflow.paths import ProjectIdentity

_TOKEN = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-SNAPSHOT)?")
_GRAMMAR = (
    "expected MAJOR.MINOR.PATCH or MAJOR.MINOR.PATCH-SNAPSHOT: decimal numbers without leading zeros, "
    "the uppercase -SNAPSHOT suffix and no 'v' prefix, such as 0.14.0 or 0.14.0-SNAPSHOT"
)
_BOM = b"\xef\xbb\xbf"

Participation = Literal["not-participating tool-only", "not-participating undeclared"]


class VersionError(ValueError):
    """A text that is not a version token: an input failure, status 2."""

    exit_code = 2


class SourceError(ValueError):
    """An unreadable, malformed or unsupported version source: status 2."""

    exit_code = 2


@dataclass(frozen=True)
class VersionToken:
    """`MAJOR.MINOR.PATCH` with an optional `-SNAPSHOT` suffix."""

    major: int
    minor: int
    patch: int
    snapshot: bool = False

    @classmethod
    def parse(cls, text: str) -> VersionToken:
        """Parse the whole text as a token, or fail with the grammar as remedy."""
        match = _TOKEN.fullmatch(text)
        if match is None:
            msg = f"Invalid version {text!r}: {_GRAMMAR}"
            raise VersionError(msg)
        return cls(int(match[1]), int(match[2]), int(match[3]), snapshot=match[4] is not None)

    @property
    def core(self) -> VersionToken:
        """Return the same version without the suffix."""
        return VersionToken(self.major, self.minor, self.patch)

    @property
    def key(self) -> tuple[int, int, int]:
        """Return the integer triple that orders versions; the suffix is not part of it."""
        return (self.major, self.minor, self.patch)

    def __str__(self) -> str:
        """Spell the token as sources and the anchor carry it."""
        return f"{self.major}.{self.minor}.{self.patch}" + ("-SNAPSHOT" if self.snapshot else "")


class Form(StrEnum):
    """How a source's expected value derives from the anchor token."""

    SNAPSHOT = "snapshot"
    CORE = "core"
    RELEASE_ONLY = "release-only"

    @classmethod
    def parse(cls, text: str) -> Form:
        """Read a configured form name, or fail naming the choices."""
        try:
            return cls(text)
        except ValueError as exc:
            msg = f"Unknown version form {text!r}: expected one of snapshot, core, release-only"
            raise SourceError(msg) from exc

    def expected(self, anchor: VersionToken) -> str:
        """Return the anchor token for `snapshot`, its core otherwise."""
        return str(anchor if self is Form.SNAPSHOT else anchor.core)


@dataclass(frozen=True)
class Span:
    """A half-open `[start, end)` range of offsets."""

    start: int
    end: int

    def __post_init__(self) -> None:
        """Reject a negative start or an end before the start."""
        if self.start < 0 or self.end < self.start:
            msg = f"Invalid span [{self.start}, {self.end})"
            raise ValueError(msg)


@dataclass(frozen=True)
class LocatedSource:
    """One owned version field: where it is, how it is read and the bytes holding it."""

    path: Path
    field: str
    adapter: str
    form: Form
    value: str
    spans: tuple[Span, ...]
    root: Path
    manifest: Path | None = None


@dataclass(frozen=True)
class VisibleRecord:
    """A version file shown by `list` that does not participate."""

    path: Path
    field: str
    adapter: str
    status: Participation


@dataclass(frozen=True)
class Detection:
    """What one adapter found at one participating root."""

    sources: tuple[LocatedSource, ...] = ()
    visible: tuple[VisibleRecord, ...] = ()


def check_release_only(source: LocatedSource, anchor: VersionToken) -> None:
    """Refuse a release-only value above the target's core, or one that is not a release token."""
    if source.form is not Form.RELEASE_ONLY:
        return
    malformed = f"{source.path} {source.field}: release-only value {source.value!r} is malformed: it must be a release token such as 0.14.0"
    try:
        current = VersionToken.parse(source.value)
    except VersionError as exc:
        raise SourceError(malformed) from exc
    if current.snapshot:
        raise SourceError(malformed)
    if current.key > anchor.key:
        msg = (f"{source.path} {source.field}: release-only value {current} is higher than the target {anchor.core}; "
               "lower that value or choose a higher target")
        raise SourceError(msg)


def decode_utf8(content: bytes, name: str) -> tuple[str, bytes]:
    """Decode strict UTF-8 after an optional byte-order mark, returned apart and kept."""
    bom = _BOM if content.startswith(_BOM) else b""
    try:
        return content[len(bom):].decode("utf-8"), bom
    except UnicodeDecodeError as exc:
        msg = f"{name} is not valid UTF-8 at byte {exc.start + len(bom)}; save it as UTF-8"
        raise SourceError(msg) from exc


class FileView:
    """Read-only file access that loads each path at most once for one phase.

    A phase that must observe the disk again opens a fresh view. Absence is
    loaded once too and recorded as `None`. Step 6 adds `derived`: a value
    computed from the view's files, such as an index across participating
    roots, is computed once per key for the phase.
    """

    def __init__(self) -> None:
        """Start with nothing loaded or derived."""
        self._contents: dict[Path, bytes | None] = {}
        self._loads: dict[Path, int] = {}
        self._derived: dict[str, object] = {}

    def read(self, path: Path) -> bytes | None:
        """Return the file's bytes, or `None` when it does not exist."""
        if path not in self._contents:
            self._loads[path] = self._loads.get(path, 0) + 1
            try:
                self._contents[path] = path.read_bytes()
            except FileNotFoundError:
                self._contents[path] = None
        return self._contents[path]

    def text(self, path: Path) -> tuple[str, bytes]:
        """Decode the file as strict UTF-8, returning the text and its byte-order mark."""
        content = self.read(path)
        if content is None:
            msg = f"{path} does not exist"
            raise SourceError(msg)
        return decode_utf8(content, str(path))

    def loads(self, path: Path) -> int:
        """Return how many times this view loaded the path."""
        return self._loads.get(path, 0)

    def derived[T](self, key: str, compute: Callable[[], T]) -> T:
        """Return the value derived under `key`, computing it on the first request of this view."""
        if key not in self._derived:
            self._derived[key] = compute()
        return cast("T", self._derived[key])


@dataclass(frozen=True)
class PatternDeclaration:
    """One `[source:<name>]` pattern source: its file, compiled expression and form."""

    name: str
    path: Path
    expression: re.Pattern[str]
    form: Form


class AdapterSettings(Protocol):
    """What an adapter needs to know about the operation's settings."""

    @property
    def project_root(self) -> Path:
        """Return the physical project root, whose root-only sources an adapter emits."""
        ...

    @property
    def patterns(self) -> tuple[PatternDeclaration, ...]:
        """Return the declared pattern sources, in declaration order."""
        ...

    @property
    def components(self) -> Mapping[str, Path]:
        """Return the declared component roots by component id, each a physical directory."""
        ...

    @property
    def forms(self) -> Mapping[str, Form]:
        """Return the configured form of each built-in adapter that `[source:<name>] form` overrides."""
        ...

    def participant(self, path: Path) -> str | None:
        """Name the participating root a physical path is, or return `None`, in one lookup."""
        ...

    def authorize(self, path: Path) -> Path:
        """Return the physical path of a file an adapter discovers, failing when it leaves the project.

        A path outside the physical project root, or entering a nested
        repository, directly or through a link, fails as a `SourceError`.
        """
        ...


class Adapter(Protocol):
    """A version source format: detection over one root and rendering of one value."""

    @property
    def name(self) -> str:
        """Return the adapter name, also its `[source:<name>]` instance."""
        ...

    @property
    def default_form(self) -> Form | None:
        """Return the form used without configuration, `None` when each source declares one."""
        ...

    @property
    def forms(self) -> frozenset[Form]:
        """Return the forms configuration may select."""
        ...

    @property
    def manifest_names(self) -> frozenset[str]:
        """Return the file names an undeclared candidate may carry."""
        ...

    def detect(self, root: Path, view: FileView, settings: AdapterSettings) -> Detection:
        """Locate sources and visible records at one participating root."""
        ...

    def render(self, source: LocatedSource, value: str) -> bytes:
        """Return the replacement bytes of a value in the field's syntax."""
        ...

    def has_project_version(self, name: str, content: bytes) -> bool:
        """Tell whether a candidate file declares its own project version."""
        ...


def participant_names(project_root: Path, components: Mapping[str, Path]) -> dict[str, str]:
    """Index the participating roots by physical path, compared by the filesystem's case rules.

    Built once per settings value, the index answers each `participant` lookup
    in constant time.
    """
    names = {os.path.normcase(str(project_root)): "the project root"}
    names.update({os.path.normcase(str(root)): f"[component:{component}]" for component, root in components.items()})
    return names


def compose(original: bytes, edits: Iterable[tuple[Span, bytes]]) -> bytes:
    """Build one new content from one original and its disjoint byte-span replacements."""
    ordered = sorted(edits, key=lambda edit: edit[0].start)
    parts: list[bytes] = []
    position = 0
    for span, replacement in ordered:
        if span.end > len(original):
            msg = f"Edit span [{span.start}, {span.end}) lies outside {len(original)} bytes"
            raise SourceError(msg)
        if span.start < position:
            msg = f"Edit span [{span.start}, {span.end}) overlaps the previous edit ending at {position}"
            raise SourceError(msg)
        parts += (original[position:span.start], replacement)
        position = span.end
    parts.append(original[position:])
    return b"".join(parts)


def _utf8_length(segment: str) -> int:
    """Measure one text segment in UTF-8 bytes."""
    return len(segment.encode("utf-8"))


def to_byte_spans(text: str, bom_length: int, spans: Sequence[Span]) -> tuple[Span, ...]:
    """Map character spans of decoded text to byte spans of the original file.

    The distinct offsets are sorted once and the text is walked once, encoding
    each segment between consecutive offsets exactly once, so the cost is
    linear in the text whatever the number of fields.
    """
    offsets = sorted({offset for span in spans for offset in (span.start, span.end)})
    if offsets and offsets[-1] > len(text):
        msg = f"Character span ends at {offsets[-1]}, past the {len(text)} characters of the text"
        raise SourceError(msg)
    byte_at: dict[int, int] = {}
    position, total = 0, bom_length
    for offset in offsets:
        total += _utf8_length(text[position:offset])
        byte_at[offset] = total
        position = offset
    return tuple(Span(byte_at[span.start], byte_at[span.end]) for span in spans)


@dataclass(frozen=True)
class VersionInputs:
    """The project, configuration, artifacts and Git a version operation works with."""

    project: ProjectIdentity
    configuration: Configuration
    artifacts: ArtifactDeclaration
    git: GitExecutionContext

    @classmethod
    def from_context(cls, context: InvocationContext) -> VersionInputs:
        """Copy the four inputs from a validated invocation context."""
        return cls(context.project, context.configuration, context.artifacts, context.git)


@dataclass(frozen=True)
class FileCapture:
    """One file as captured for a plan: its bytes, or `None` when absent, with their SHA-256."""

    path: Path
    original: bytes | None
    sha256: str | None

    @classmethod
    def of(cls, path: Path, content: bytes | None) -> FileCapture:
        """Capture content, hashing it when present."""
        return cls(path, content, None if content is None else hashlib.sha256(content).hexdigest())


@dataclass(frozen=True)
class SourceChange:
    """One field changing value inside a file edit."""

    path: Path
    field: str
    adapter: str
    old: str
    new: str


@dataclass(frozen=True)
class FileEdit:
    """The new content of one captured file and the field changes it carries."""

    capture: FileCapture
    new: bytes
    changes: tuple[SourceChange, ...]

    def __post_init__(self) -> None:
        """Refuse an edit that would rewrite a file with its own bytes."""
        if self.new == self.capture.original:
            msg = f"{self.capture.path}: edit leaves the file unchanged"
            raise SourceError(msg)


@dataclass(frozen=True)
class Claim:
    """The ownership of one field and its byte spans by one adapter."""

    path: Path
    field: str
    adapter: str
    spans: tuple[Span, ...]


@dataclass(frozen=True)
class Inventory:
    """Every located source, visible record, claim and file capture of one plan phase."""

    sources: tuple[LocatedSource, ...]
    visible: tuple[VisibleRecord, ...]
    claims: tuple[Claim, ...]
    captures: tuple[FileCapture, ...]


@dataclass(frozen=True)
class Plan:
    """The target, the inventory it was planned from and the file edits it needs."""

    target: VersionToken
    inventory: Inventory
    edits: tuple[FileEdit, ...]


# eof
