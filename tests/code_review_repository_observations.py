"""Declared evidence inputs for code-review scenarios.

Only tests change these facts. The dependency port reads them without staging,
committing, storing objects, interpreting shell text or executing a fallback.
Tree/blob identifiers are opaque fixture tokens, not simulated Git objects.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from tests.review_repository_observations import ReviewRepositories

if TYPE_CHECKING:
    from collections.abc import Sequence

    import pytest

    from tools.git_command import GitCommandOptions


@dataclass
class EvidenceFacts:
    """Explicit baseline, index, ignore and blob observations for one scenario."""

    baseline: dict[str, bytes] = field(default_factory=dict[str, bytes])
    index: dict[str, bytes] = field(default_factory=dict[str, bytes])
    ignored_paths: set[str] = field(default_factory=set[str])
    blob_ids: dict[str, str] = field(default_factory=dict[str, str])
    blobs: dict[str, str] = field(default_factory=dict[str, str])
    identities: dict[tuple[tuple[str, bytes], ...], str] = field(default_factory=dict[tuple[tuple[str, bytes], ...], str])

    def tree(self) -> str:
        """Return an opaque stable token for explicitly declared index bytes."""
        key = tuple(sorted(self.index.items()))
        return self.identities.setdefault(key, f"{len(self.identities) + 1:040x}")

    def changed_paths(self) -> tuple[str, ...]:
        """Return fixture differences independently of the working files."""
        return tuple(sorted(name for name in self.index.keys() | self.baseline.keys()
                            if self.index.get(name) != self.baseline.get(name)))


REPOSITORIES = ReviewRepositories()
EVIDENCE: dict[Path, EvidenceFacts] = {}


def declare_repository(root: Path, baseline: dict[str, bytes] | None = None) -> EvidenceFacts:
    """Register inert metadata and independent data maps for one scenario."""
    initial = dict(baseline or {})
    REPOSITORIES.register(root, initial)
    facts = EvidenceFacts(baseline=initial, index=dict(initial))
    EVIDENCE[root.resolve()] = facts
    return facts


def declare_index(root: Path, *paths: str) -> None:
    """Supply exact index bytes/deletions without processing Git commands."""
    facts = EVIDENCE[root.resolve()]
    for name in paths:
        path = root / name
        if path.is_file():
            facts.index[name] = path.read_bytes()
        else:
            facts.index.pop(name, None)
    REPOSITORIES.repositories[root.resolve()].tracked = dict(facts.index)


def declare_blob(root: Path, name: str) -> None:
    """Supply the object id and original text expected from the evidence port."""
    facts = EVIDENCE[root.resolve()]
    token = f"{len(facts.blobs) + 1:040x}"
    facts.blob_ids[name] = token
    facts.blobs[token] = (root / name).read_text(encoding="utf-8")


def read_evidence(arguments: Sequence[str], *, cwd: Path | None = None,
                  options: GitCommandOptions | None = None) -> subprocess.CompletedProcess[str]:
    """Return declared external observations to the real evidence implementation."""
    root = Path(cwd or Path.cwd()).resolve()
    command = tuple(arguments)
    facts = EVIDENCE.get(root)
    if facts is None:
        raise subprocess.CalledProcessError(128, command, stderr="not a git repository")

    if command[:1] in {("check-ignore",), ("rev-parse",)} or command[:2] == ("ls-files", "--"):
        return REPOSITORIES.run(["git", *arguments], cwd=root, check=options.check if options else True)
    output, code = _evidence_output(command, facts, root)
    if code and (options is None or options.check):
        raise subprocess.CalledProcessError(code, command, output, "")
    return subprocess.CompletedProcess(list(arguments), code, output, "")


def _evidence_output(command: tuple[str, ...], facts: EvidenceFacts, root: Path) -> tuple[str, int]:
    """Resolve evidence reads without implementing repository mutations."""
    match command:
        case ("write-tree",):
            return facts.tree() + "\n", 0
        case ("ls-files", "--error-unmatch", "--", name):
            return (name + "\n", 0) if name in facts.index else ("", 1)
        case ("hash-object", "-w", "--", name):
            return facts.blob_ids[name] + "\n", 0
        case ("cat-file", "blob", token):
            return facts.blobs[token], 0
        case ("ls-files", *_) if "-z" in command:
            return _literal_inventory(command, facts, root), 0
        case _:
            message = f"undeclared evidence observation: {command!r}"
            raise AssertionError(message)


def _literal_inventory(command: tuple[str, ...], facts: EvidenceFacts, root: Path) -> str:
    """Filter explicitly requested literal paths against declared fixture sets."""
    separator = command.index("--")
    pathspecs = command[separator + 1:]
    assert all(name.startswith(":(literal)") for name in pathspecs), command
    selected = tuple(name.removeprefix(":(literal)") for name in pathspecs)
    names = _inventory_names(command[1:separator], facts, root, selected)
    return "".join(name + "\0" for name in selected if name in names)


def _inventory_names(options: tuple[str, ...], facts: EvidenceFacts,
                     root: Path, selected: tuple[str, ...]) -> set[str]:
    """Supply one declared inventory category."""
    tracked = set(facts.index)
    match options:
        case ("-z",):
            return tracked
        case ("--others", "--ignored", "--exclude-standard", "-z"):
            return facts.ignored_paths - tracked
        case ("--others", "--exclude-standard", "-z"):
            return {name for name in selected if (root / name).is_file()} - tracked - facts.ignored_paths
        case _:
            message = f"undeclared inventory options: {options!r}"
            raise AssertionError(message)


def install_observations(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bind evidence reads and review repository probes to declared inputs."""
    from tools import code_review_evidence, code_review_evidence_common  # noqa: PLC0415

    EVIDENCE.clear()
    REPOSITORIES.repositories.clear()
    monkeypatch.setattr(code_review_evidence, "run_cross_platform_git_command", read_evidence)
    monkeypatch.setattr(code_review_evidence_common, "run_cross_platform_git_command", read_evidence)
    monkeypatch.setattr(subprocess, "run", REPOSITORIES.run)
    monkeypatch.setattr(shutil, "which", REPOSITORIES.which)


# eof
