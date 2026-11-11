"""Classify release tags, select release ranges and check release versions.

Step 8 of v0.14.0 version-sources. Range readers used an unfiltered last-tag
query that cannot tell stable, snapshot, engine and validated tags apart, and
split its output; this module is the one classifier, range
selector and release-version rule every reader shares (umbrella decisions 33
and 34).

- Names: `vX.Y.Z` and `X.Y.Z` are stable releases; `-SNAPSHOT` in any case
  marks a development marker; every other name is ignored.
- Eligibility, by whole annotation lines: a lightweight tag, or an annotation
  without a `Release tooling: <value>` trailer line, is historical; a trailer
  as the last nonempty line is an unvalidated engine release, and followed
  only by `[valid]` a validated one; a trailer elsewhere, several trailers or
  `[valid]` before the trailer are ambiguous (design decision Q01).
- Boundaries: stable tags of one version on one commit are one release, its
  aliases; one version on two commits, or two versions on one commit,
  conflict and fail. A boundary takes the most restrictive class of its
  aliases, ambiguous then not eligible then eligible (design decision Q18),
  and is named by its `vX.Y.Z` alias when it has one, otherwise by its
  `X.Y.Z` alias (Q19).
- `select_range` applies the design's seven-step ancestry rule with at most
  four Git calls: the tag records reachable from the target, the independent
  tips of several candidates, the tag names between the baseline and the
  target, and the commit count. Git revisions are `HEAD` or
  `refs/tags/<name>`; the printed range uses plain names. Without a
  candidate, the range is the full history through the target, and its
  boundaries are still checked as those after a baseline are.
- `check_release_version` exposes umbrella decision 33 with two calls: every
  tag record, and the records reachable from `main`. A version any stable tag
  already names is reserved; otherwise it must be higher, numerically, than
  every eligible boundary on `main`.

Grouping and checks use dictionaries and sets keyed by version, commit and
name: each selection is linear in the reachable tags.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from tools.release_workflow.git import GitRevisionNotFoundError
from tools.release_workflow.sources.model import VersionToken

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from pathlib import Path

    from tools.release_workflow.git import GitExecutionContext, TagRecord

_NAME = re.compile(r"(v?)(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-(?i:snapshot))?")
_TRAILER = "Release tooling: "
_VALID = "[valid]"
_HEAD = "HEAD"
_MAIN = "main"
_TAG_REF = "refs/tags/"


class RangeError(ValueError):
    """A target, history or release version the selector refuses: status 2."""

    exit_code = 2


@dataclass(frozen=True)
class StableName:
    """A stable release tag name: its spelling, its token and whether it carries `v`."""

    name: str
    token: VersionToken
    prefixed: bool


@dataclass(frozen=True)
class SnapshotName:
    """A development marker name: never a baseline, target or recovery target."""

    name: str
    token: VersionToken
    prefixed: bool


def parse_name(name: str) -> StableName | SnapshotName | None:
    """Read a tag name as a stable release, a snapshot marker, or nothing."""
    match = _NAME.fullmatch(name)
    if match is None:
        return None
    token = VersionToken(int(match[2]), int(match[3]), int(match[4]))
    return (SnapshotName if match[5] else StableName)(name, token, bool(match[1]))


class Eligibility(StrEnum):
    """The class of one stable tag, read from its annotation."""

    HISTORICAL = "historical"
    VALIDATED = "validated"
    UNVALIDATED = "unvalidated"
    AMBIGUOUS = "ambiguous"


def _trailer(line: str) -> bool:
    """Tell whether a line is a tooling trailer: the exact prefix and a nonempty value."""
    return line.startswith(_TRAILER) and bool(line[len(_TRAILER):].strip())


def _engine(lines: Sequence[str], trailers: Sequence[int]) -> Eligibility:
    """Classify nonblank lines holding trailers: one trailer, no `[valid]` before it, then nothing or `[valid]`."""
    position = trailers[0]
    if len(trailers) > 1 or _VALID in lines[:position]:
        return Eligibility.AMBIGUOUS
    after = lines[position + 1:]
    if not after:
        return Eligibility.UNVALIDATED
    return Eligibility.VALIDATED if after == [_VALID] else Eligibility.AMBIGUOUS


def eligibility(annotation: str | None) -> Eligibility:
    """Classify an annotation by whole lines; a lightweight tag (`None`) is historical."""
    if annotation is None:
        return Eligibility.HISTORICAL
    lines = [line for line in annotation.splitlines() if line.strip()]
    trailers = [index for index, line in enumerate(lines) if _trailer(line)]
    return _engine(lines, trailers) if trailers else Eligibility.HISTORICAL


@dataclass(frozen=True)
class ClassifiedTag:
    """A stable tag record with its parsed name and its class."""

    record: TagRecord
    name: StableName
    eligibility: Eligibility


def classify(record: TagRecord) -> ClassifiedTag | None:
    """Classify a stable tag record; a snapshot marker or any other name gives `None`."""
    name = parse_name(record.name)
    if not isinstance(name, StableName):
        return None
    return ClassifiedTag(record, name, eligibility(record.annotation))


class BoundaryClass(StrEnum):
    """The class of one release boundary, the most restrictive of its aliases."""

    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    AMBIGUOUS = "ambiguous"


def _spell(names: Iterable[str]) -> str:
    """Join names in sorted order for a diagnostic."""
    return " and ".join(sorted(names))


@dataclass(frozen=True)
class Boundary:
    """The stable tags of one version on one commit: one release and its aliases."""

    version: VersionToken
    commit: str
    aliases: tuple[ClassifiedTag, ...]

    @property
    def names(self) -> frozenset[str]:
        """Return the alias tag names."""
        return frozenset(alias.record.name for alias in self.aliases)

    @property
    def status(self) -> BoundaryClass:
        """Ambiguous when any alias is, otherwise not eligible when any alias is unvalidated, otherwise eligible."""
        classes = {alias.eligibility for alias in self.aliases}
        if Eligibility.AMBIGUOUS in classes:
            return BoundaryClass.AMBIGUOUS
        return BoundaryClass.INELIGIBLE if Eligibility.UNVALIDATED in classes else BoundaryClass.ELIGIBLE

    @property
    def name(self) -> str:
        """Return the `vX.Y.Z` alias when there is one, otherwise the `X.Y.Z` alias."""
        return next((alias.record.name for alias in self.aliases if alias.name.prefixed), self.aliases[0].record.name)

    @property
    def spelled(self) -> str:
        """Name every alias, for diagnostics."""
        return _spell(self.names)


def _one_commit_per_version(by_version: Mapping[tuple[int, int, int], Sequence[ClassifiedTag]]) -> None:
    """Fail when one version is tagged on several commits, naming the tags."""
    for key, group in by_version.items():
        commits = sorted({tag.record.commit for tag in group})
        if len(commits) > 1:
            msg = (f"conflicting tags {_spell(tag.record.name for tag in group)}: version {VersionToken(*key)} is tagged on commits "
                   f"{' and '.join(commits)}; keep one release commit per version")
            raise RangeError(msg)


def _one_version_per_commit(by_commit: Mapping[str, Sequence[ClassifiedTag]]) -> None:
    """Fail when one commit carries several versions, naming the tags."""
    for commit, group in by_commit.items():
        versions = sorted({tag.name.token.key for tag in group})
        if len(versions) > 1:
            msg = (f"conflicting tags {_spell(tag.record.name for tag in group)}: commit {commit} carries versions "
                   f"{' and '.join(str(VersionToken(*key)) for key in versions)}; keep one version per release commit")
            raise RangeError(msg)


def boundaries(tags: Iterable[ClassifiedTag]) -> tuple[Boundary, ...]:
    """Group stable tags by version and commit, in first-appearance order; conflicting tags fail."""
    by_version: dict[tuple[int, int, int], list[ClassifiedTag]] = {}
    by_commit: dict[str, list[ClassifiedTag]] = {}
    for tag in tags:
        by_version.setdefault(tag.name.token.key, []).append(tag)
        by_commit.setdefault(tag.record.commit, []).append(tag)
    _one_commit_per_version(by_version)
    _one_version_per_commit(by_commit)
    return tuple(Boundary(VersionToken(*key), group[0].record.commit, tuple(group)) for key, group in by_version.items())


@dataclass(frozen=True)
class RangeSelection:
    """The target, the baseline release (or `None`), the printed range, its commit count and any warnings."""

    target: str
    baseline: str | None
    range: str
    commits: int
    warnings: tuple[str, ...] = ()


def _target(target: str | None) -> tuple[str, str]:
    """Return the Git revision and the printed name of the target; only a stable name is a tag target."""
    if target is None:
        return _HEAD, _HEAD
    if not isinstance(parse_name(target), StableName):
        msg = (f"{target!r} is not a stable release tag name: expected vX.Y.Z or X.Y.Z; snapshot and other prerelease tags "
               "are never range targets")
        raise RangeError(msg)
    return f"{_TAG_REF}{target}", target


def _boundaries(git: GitExecutionContext, cwd: Path, revision: str, shown: str) -> tuple[Boundary, ...]:
    """Read and group the stable tags reachable from the target, in one call; a missing tag target is status 2."""
    try:
        records = git.tag_records(cwd=cwd, merged=revision)
    except GitRevisionNotFoundError as exc:
        msg = f"tag {shown} does not exist; name an existing stable release tag"
        raise RangeError(msg) from exc
    return boundaries(_stable(records))


def _without_target(found: Sequence[Boundary], target: str | None) -> list[Boundary]:
    """Remove a tag target's whole boundary, which must be eligible; HEAD keeps every boundary."""
    if target is None:
        return list(found)
    own = next(boundary for boundary in found if target in boundary.names)
    if own.status is not BoundaryClass.ELIGIBLE:
        state = "ambiguous" if own.status is BoundaryClass.AMBIGUOUS else "not eligible (an unvalidated engine release)"
        msg = f"tag {target} cannot be a range target: its release {own.spelled} is {state}"
        raise RangeError(msg)
    return [boundary for boundary in found if boundary is not own]


def _baseline(git: GitExecutionContext, cwd: Path, candidates: Sequence[Boundary]) -> Boundary:
    """Return the one candidate no other candidate descends from; parallel tips or an inversion fail."""
    if len(candidates) == 1:
        return candidates[0]
    tips = frozenset(git.independent_commits([boundary.commit for boundary in candidates], cwd=cwd))
    independent = [boundary for boundary in candidates if boundary.commit in tips]
    if len(independent) != 1:
        msg = (f"several independent eligible releases: {_spell(boundary.name for boundary in independent)}; versions range "
               "cannot choose a baseline from merged parallel histories")
        raise RangeError(msg)
    baseline = independent[0]
    higher = next((boundary for boundary in candidates if boundary.version.key > baseline.version.key), None)
    if higher is not None:
        msg = f"version inversion: baseline {baseline.name} is lower than the earlier release {higher.name}; correct the release tags"
        raise RangeError(msg)
    return baseline


def _checked(remaining: Sequence[Boundary], between: frozenset[str] | None, where: str) -> tuple[str, ...]:
    """Fail on an ambiguous boundary in the range and warn about each unvalidated one; `None` means every boundary."""
    warnings: list[str] = []
    for boundary in remaining:
        if between is not None and not boundary.names & between:
            continue
        if boundary.status is BoundaryClass.AMBIGUOUS:
            msg = f"ambiguous release {boundary.spelled} {where}; correct its annotation"
            raise RangeError(msg)
        if boundary.status is BoundaryClass.INELIGIBLE:
            warnings.append(f"excluded unvalidated engine release {boundary.spelled} {where}")
    return tuple(warnings)


def select_range(git: GitExecutionContext, *, cwd: Path, target: str | None = None) -> RangeSelection:
    """Select the release range ending at HEAD or at a stable tag, by the design's ancestry rule."""
    revision, shown = _target(target)
    remaining = _without_target(_boundaries(git, cwd, revision, shown), target)
    candidates = [boundary for boundary in remaining if boundary.status is BoundaryClass.ELIGIBLE]
    if not candidates:
        warnings = _checked(remaining, None, f"before {shown}")
        return RangeSelection(shown, None, shown, git.commit_count(revision, cwd=cwd), warnings)
    baseline = _baseline(git, cwd, candidates)
    start = f"{_TAG_REF}{baseline.name}"
    between = frozenset(git.tag_names(cwd=cwd, merged=revision, not_merged=start))
    warnings = _checked(remaining, between, f"between {baseline.name} and {shown}")
    return RangeSelection(shown, baseline.name, f"{baseline.name}..{shown}", git.commit_count(f"{start}..{revision}", cwd=cwd), warnings)


def _stable(records: Iterable[TagRecord]) -> list[ClassifiedTag]:
    """Classify the stable tags among records, dropping every other name."""
    return [tag for record in records if (tag := classify(record)) is not None]


def _highest_eligible(found: Iterable[Boundary]) -> Boundary | None:
    """Return the eligible boundary of the highest version, or `None`."""
    eligible = [boundary for boundary in found if boundary.status is BoundaryClass.ELIGIBLE]
    return max(eligible, key=lambda boundary: boundary.version.key, default=None)


def check_release_version(git: GitExecutionContext, *, cwd: Path, version: str) -> None:
    """Refuse a release version a stable tag already names, or one not above every eligible release on `main`."""
    token = VersionToken.parse(version)
    if token.snapshot:
        msg = f"{version} is not a release version: a release carries no -SNAPSHOT suffix"
        raise RangeError(msg)
    every = _stable(git.tag_records(cwd=cwd))
    highest = _highest_eligible(boundaries(_stable(git.tag_records(cwd=cwd, merged=_MAIN))))
    reserved = [tag.record.name for tag in every if tag.name.token.key == token.key]
    if reserved:
        msg = f"version {token} is reserved: tag {_spell(reserved)} already names it; choose another version"
        raise RangeError(msg)
    if highest is not None and token.key <= highest.version.key:
        msg = f"version {token} is not higher than release {highest.name}, reachable from main; choose a higher version"
        raise RangeError(msg)


# eof
