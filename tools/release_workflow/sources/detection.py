"""Combine every adapter over the participating roots, register claims and plan edits.

Step 3 of v0.14.0 version-sources. The project root always participates, and
each `[component:<id>]` adds one root, which must be an existing directory.
Every adapter runs over every participating root in tuple order, reading
through one file view, so each file is loaded once per phase. Each located
source claims its physical path and field, and the byte spans holding its
value: a second claim on one pair, a span outside its file or overlapping
spans, even under different fields, fail before any write and name both
claimants. Disjoint fields of one file compose into one new content from one
captured original. Only `versions list` asks for undeclared candidates, from
one Git listing; `check` and `set` never compute them.

Claims are indexed by path and field, and only the handful of spans of one
file is sorted, so the cost stays linear in the located fields.
"""

from __future__ import annotations

from itertools import pairwise
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from tools.release_workflow.sources import ADAPTERS
from tools.release_workflow.sources.model import (
    Claim,
    FileCapture,
    FileEdit,
    Inventory,
    SourceChange,
    SourceError,
    VisibleRecord,
    check_release_only,
    compose,
)
from tools.release_workflow.sources.settings import excluded_directory, read_settings

if TYPE_CHECKING:
    from collections.abc import Container, Mapping, Sequence
    from pathlib import Path

    from tools.release_workflow.sources.model import (
        Adapter,
        FileView,
        LocatedSource,
        Span,
        VersionInputs,
        VersionToken,
    )
    from tools.release_workflow.sources.settings import VersionSettings


def participating_roots(settings: VersionSettings) -> tuple[Path, ...]:
    """Return the project root then each component root, which must be an existing directory."""
    for component, root in settings.components.items():
        if not root.is_dir():
            reason = "is not a directory" if root.exists() else "does not exist"
            msg = f"[component:{component}] root {root} {reason}: create the component directory or correct root"
            raise SourceError(msg)
    return (settings.project_root, *settings.components.values())


def _claimant(source: LocatedSource) -> str:
    """Name a claim by its adapter, field and participating root."""
    return f"{source.adapter} {source.field} at root {source.root}"


def _check_overlaps(path: Path, owned: Sequence[tuple[Span, LocatedSource]]) -> None:
    """Sort one file's spans and reject any that starts before the previous one ends."""
    ordered = sorted(owned, key=lambda item: (item[0].start, item[0].end))
    for (before, first), (span, source) in pairwise(ordered):
        if span.start < before.end:
            msg = (f"{path}: bytes [{span.start}, {span.end}) of {_claimant(source)} overlap "
                   f"bytes [{before.start}, {before.end}) of {_claimant(first)}")
            raise SourceError(msg)


def _claim(sources: Sequence[LocatedSource], view: FileView) -> tuple[Claim, ...]:
    """Register each path and field once, with spans inside the file and disjoint from the others."""
    owners: dict[tuple[Path, str], LocatedSource] = {}
    spans: dict[Path, list[tuple[Span, LocatedSource]]] = {}
    for source in sources:
        key = (source.path, source.field)
        if key in owners:
            msg = f"{source.path} field {source.field} is claimed twice: by {_claimant(owners[key])} and by {_claimant(source)}"
            raise SourceError(msg)
        owners[key] = source
        size = len(view.read(source.path) or b"")
        for span in source.spans:
            if span.end > size:
                msg = f"{source.path}: bytes [{span.start}, {span.end}) of {_claimant(source)} lie outside the {size} bytes of the file"
                raise SourceError(msg)
            spans.setdefault(source.path, []).append((span, source))
    for path, owned in spans.items():
        _check_overlaps(path, owned)
    return tuple(Claim(source.path, source.field, source.adapter, source.spans) for source in sources)


def detect(inputs: VersionInputs, view: FileView, *, adapters: Sequence[Adapter] = ADAPTERS) -> Inventory:
    """Run every adapter over every participating root and register every claim."""
    settings = read_settings(inputs.configuration, adapters)
    roots = participating_roots(settings)
    sources: list[LocatedSource] = []
    visible: list[VisibleRecord] = []
    for adapter in adapters:
        for root in roots:
            found = adapter.detect(root, view, settings)
            sources += found.sources
            visible += found.visible
    claims = _claim(sources, view)
    captures = tuple(FileCapture.of(path, view.read(path)) for path in dict.fromkeys(source.path for source in sources))
    return Inventory(tuple(sources), tuple(visible), claims, captures)


def _edit(capture: FileCapture, fields: Sequence[tuple[LocatedSource, str]], renderers: Mapping[str, Adapter]) -> FileEdit:
    """Compose one file's new content from its captured original and its changed fields."""
    if capture.original is None:
        msg = f"{capture.path} was captured as absent: detect the sources again before planning"
        raise SourceError(msg)
    replacements = [(span, renderers[source.adapter].render(source, expected)) for source, expected in fields for span in source.spans]
    changes = tuple(SourceChange(source.path, source.field, source.adapter, source.value, expected) for source, expected in fields)
    return FileEdit(capture, compose(capture.original, replacements), changes)


def plan_edits(inventory: Inventory, anchor: VersionToken, *, adapters: Sequence[Adapter] = ADAPTERS) -> tuple[FileEdit, ...]:
    """Return one edit per file holding a value that differs from its expected value.

    The release-only guard runs first for every source, so a refusal leaves
    no partial plan.
    """
    renderers = {adapter.name: adapter for adapter in adapters}
    changed: dict[Path, list[tuple[LocatedSource, str]]] = {}
    for source in inventory.sources:
        check_release_only(source, anchor)
        expected = source.form.expected(anchor)
        if source.value != expected:
            changed.setdefault(source.path, []).append((source, expected))
    captures = {capture.path: capture for capture in inventory.captures}
    return tuple(_edit(captures[path], fields, renderers) for path, fields in changed.items())


def _participating_directories(inputs: VersionInputs, inventory: Inventory, manifests: Container[str],
                               adapters: Sequence[Adapter]) -> frozenset[Path]:
    """Return the participating roots and the directories of located manifest files, such as Maven modules."""
    roots = participating_roots(read_settings(inputs.configuration, adapters))
    return frozenset((*roots, *(source.path.parent for source in inventory.sources if source.path.name in manifests)))


def _undeclared_path(root: Path, relative: PurePosixPath, participating: frozenset[Path], home: Path) -> Path | None:
    """Return a listed manifest's path unless it lies under an excluded, participating or artifact directory."""
    if excluded_directory(relative.parent.parts) is not None:
        return None
    path = root.joinpath(*relative.parts)
    return None if path.parent in participating or path.is_relative_to(home) else path


def candidates(inputs: VersionInputs, inventory: Inventory, view: FileView, *, adapters: Sequence[Adapter] = ADAPTERS) -> tuple[VisibleRecord, ...]:
    """List undeclared manifest files with a project version, from one Git listing.

    Names under an excluded directory, a participating directory or the
    artifact home are skipped before any read; every other manifest file is
    read once.
    """
    root = inputs.project.root
    by_manifest = {name: adapter for adapter in adapters for name in adapter.manifest_names}
    participating = _participating_directories(inputs, inventory, by_manifest, adapters)
    records: list[VisibleRecord] = []
    for name in inputs.git.listing(cwd=root):
        relative = PurePosixPath(name)
        adapter = by_manifest.get(relative.name)
        path = None if adapter is None else _undeclared_path(root, relative, participating, inputs.artifacts.home)
        if adapter is None or path is None:
            continue
        content = view.read(path)
        if content is not None and adapter.has_project_version(relative.name, content):
            records.append(VisibleRecord(path, "version", adapter.name, "not-participating undeclared"))
    return tuple(records)


# eof
