"""Byte builders for version sources and helpers for read-once file views.

Step 2 of v0.14.0 version-sources starts this module with `version.txt`
documents in LF, CRLF and byte-order-mark variants, settings naming the
project root and a load-count helper; later steps add the ecosystem files.
Step 3 adds pattern declarations to those settings, `.env`-style line files,
`.release.ini` and nested-file writers, a `VersionInputs` builder over a
`git_sandbox` project and a synthetic adapter that locates one fixed span
and logs each root it visits, standing in for adapters later steps add.
Nothing here starts a process or interprets a version.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from tools.release_workflow.artifacts import resolve_artifacts
from tools.release_workflow.configuration import load_configuration
from tools.release_workflow.paths import ProjectIdentity
from tools.release_workflow.sources.model import (
    Detection,
    Form,
    LocatedSource,
    PatternDeclaration,
    Span,
    VersionInputs,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.sources.model import AdapterSettings, FileView

BOM = b"\xef\xbb\xbf"
UMBRELLA_PATTERN = r"^APP_SERVICE_VERSION=(.+)$"
_FIRST_SIX = Span(0, 6)


@dataclass(frozen=True)
class RootSettings:
    """Adapter settings naming the project root and its declared pattern sources."""

    project_root: Path
    patterns: tuple[PatternDeclaration, ...] = ()


def version_txt(first_line: str = "0.14.0", notes: str = "", *, newline: str = "\n", bom: bool = False) -> bytes:
    """Build a `version.txt` document; `notes` uses LF, converted to `newline`."""
    text = first_line + newline + notes.replace("\n", newline)
    return (BOM if bom else b"") + text.encode("utf-8")


def write_version_txt(root: Path, content: bytes) -> Path:
    """Write the anchor document at a project root and return its path."""
    root.mkdir(parents=True, exist_ok=True)
    path = root / "version.txt"
    path.write_bytes(content)
    return path


def load_counts(view: FileView, *paths: Path) -> tuple[int, ...]:
    """Return how many times the view loaded each path."""
    return tuple(view.loads(path) for path in paths)


def lines_file(lines: Sequence[str], *, newline: str = "\n", bom: bool = False) -> bytes:
    """Build a line-oriented file such as `.env`, each line ended by `newline`."""
    return (BOM if bom else b"") + "".join(line + newline for line in lines).encode("utf-8")


def write_file(root: Path, relative: str, content: bytes) -> Path:
    """Write a file below a root, creating its directories, and return its path."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def write_release_ini(root: Path, text: str) -> Path:
    """Write the project's `.release.ini` as UTF-8."""
    return write_file(root, ".release.ini", text.encode("utf-8"))


def declare_pattern(root: Path, name: str = "cicd-env", file: str = ".env", pattern: str = UMBRELLA_PATTERN,
                    form: Form = Form.SNAPSHOT) -> PatternDeclaration:
    """Declare a pattern source as `read_settings` would, compiled with `re.MULTILINE`."""
    return PatternDeclaration(name, root / file, re.compile(pattern, re.MULTILINE), form)


def project_identity(root: Path) -> ProjectIdentity:
    """Supply a validated identity for a root without reproving Git discovery."""
    return ProjectIdentity(root, root / ".git", root / ".git", str(root))


def version_inputs(sandbox: GitSandbox, root: Path) -> VersionInputs:
    """Load the root's configuration and artifact declaration over the sandbox's Git port."""
    project = project_identity(root)
    git = sandbox.context()
    return VersionInputs(project, load_configuration(project), resolve_artifacts(project, git), git)


@dataclass(frozen=True)
class SyntheticAdapter:
    """A test adapter locating one fixed character span of one file at each root.

    It logs `(name, root)` for every detection call, reports a candidate when
    the content holds `version`, and renders a value as its UTF-8 bytes.
    """

    name: str
    forms: frozenset[Form] = frozenset()
    manifest_names: frozenset[str] = frozenset()
    file: str = "manifest.txt"
    key: str = "version"
    span: Span = _FIRST_SIX
    form: Form = Form.CORE
    log: list[tuple[str, Path]] = field(default_factory=list[tuple[str, "Path"]])

    @property
    def default_form(self) -> Form | None:
        """Return the form the synthetic source is located with."""
        return self.form

    def detect(self, root: Path, view: FileView, settings: AdapterSettings) -> Detection:
        """Log the call and locate the span when the file exists at this root."""
        del settings
        self.log.append((self.name, root))
        path = root / self.file
        content = view.read(path)
        if content is None:
            return Detection()
        value = content[self.span.start:self.span.end].decode("utf-8")
        return Detection((LocatedSource(path, self.key, self.name, self.form, value, (self.span,), root),))

    def render(self, source: LocatedSource, value: str) -> bytes:
        """Return the value's UTF-8 bytes."""
        del source
        return value.encode("utf-8")

    def has_project_version(self, name: str, content: bytes) -> bool:
        """Report a candidate when the content mentions `version`."""
        del name
        return b"version" in content


# eof
