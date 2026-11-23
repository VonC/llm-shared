"""Build the snapshot-tag fixture history from one deterministic `git fast-import` stream, and check its hashes.

Step 6 of v0.14.0 git-cliff-provisioning (design "Frozen inputs and the
coverage matrix"; design decision Q14; requirement clarification Q13; plan
decision Q09). llm-shared's own history has no `-SNAPSHOT` tag, so the
evidence harness builds this fixture beside it and compares both git-cliff
versions on it too.

- `stream()` writes the whole history as one fast-import stream that fixes
  every object-producing input: each commit replaces its whole tree
  (`deleteall`, then every file inline), names its parents in order, its
  message, its author and committer with dates and time zones; each annotated
  tag names its target, tagger, date, zone and message. The messages cover the
  commit parsers and skip rules of the dev_workflow `cliff.toml` (every group,
  the release, dependency and work-in-progress skips, a breaking change, a
  security body matched with a fix, a revert, an unconventional commit and a
  merge), and the tags are stable and `-SNAPSHOT` (`TAGS`).
- `environment(source, global_config)` is the Git environment of the
  evidence run: every inherited `GIT_*` dropped, `GIT_CONFIG_GLOBAL` naming an
  empty file and `GIT_CONFIG_NOSYSTEM=1`, so only command-line configuration
  applies.
- `build(git, directory)` runs `init --template= --object-format=sha1`, then
  `fast-import --done` fed the stream as input bytes, then one `for-each-ref`,
  each with `CONFIG` (no line-ending conversion, no signing); no hook can run,
  since the repository has none and no configuration names one. It returns
  the branch and tag object hashes.
- `verify(recorded, built)` fails on the first ref whose regenerated hash
  differs from the bundle's, comparing the branch and every tag of either
  side in order (code review round 1).

Pure except for `build`, which only calls Git; nothing here reads the clock.
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from tools.release_workflow.git import GitExecutionContext

CONFIG = ("-c", "core.autocrlf=false", "-c", "core.safecrlf=false", "-c", "core.eol=lf", "-c", "commit.gpgSign=false",
          "-c", "tag.gpgSign=false", "-c", "gc.auto=0")
BRANCH = "refs/heads/main"
_TAGS_PREFIX = "refs/tags/"
_OBJECT = re.compile(r"[0-9a-f]{40}")
_AUTHOR = "Ada Author <ada@example.invalid>"
_COMMITTER = "Cy Committer <cy@example.invalid>"
_TAGGER = "Tia Tagger <tia@example.invalid>"
_EPOCH = 1_700_000_000
_HOUR = 3600
_ZONES = ("+0100", "-0500")


class FixtureError(ValueError):
    """The fixture repository does not hold the history the stream describes."""

    exit_code = 2


@dataclass(frozen=True)
class FixtureHashes:
    """The object hashes of the built fixture: the branch's head commit and each annotated tag object, in `TAGS` order."""

    head: str
    tags: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class _Commit:
    """One commit: its mark, its parents in order, its message and the one file it adds or changes, if any."""

    mark: int
    parents: tuple[int, ...]
    message: str
    change: tuple[str, str] | None = None


@dataclass(frozen=True)
class _Tag:
    """One annotated tag of a commit mark."""

    name: str
    target: int


_HISTORY: tuple[_Commit | _Tag, ...] = (
    _Commit(1, (), "chore: start the fixture history\n", ("README.md", "# Fixture\n")),
    _Commit(2, (1,), "feat: add the parser\n", ("src/parser.txt", "parse\n")),
    _Commit(3, (2,), "fix(core): handle empty input\n", ("src/parser.txt", "parse empty input\n")),
    _Tag("v0.1.0", 3),
    _Commit(4, (3,), "docs: describe the snapshot flow\n", ("docs/snapshot.md", "# Snapshot\n")),
    _Commit(5, (4,), "chore(release): prepare for v0.2.0\n", ("version.txt", "0.2.0-SNAPSHOT\n")),
    _Tag("v0.2.0-SNAPSHOT", 5),
    _Commit(6, (5,), "feat!: change the output format\n\nBREAKING CHANGE: one line per entry.\n", ("src/output.txt", "one line\n")),
    _Commit(7, (6,), "wip: half done\n", ("src/draft.txt", "draft\n")),
    _Commit(8, (7,), "chore(deps): bump the tool\n", ("deps.txt", "tool 2\n")),
    _Commit(9, (8,), "fix: guard the reader\n\nCloses a security issue in the reader.\n", ("src/reader.txt", "guarded\n")),
    _Commit(10, (9,), "perf: scan faster\n", ("src/scan.txt", "fast\n")),
    _Commit(11, (9, 10), "Merge branch 'topic'\n"),
    _Tag("v0.2.0", 11),
    _Commit(12, (11,), "refactor: split the module\n", ("src/split.txt", "split\n")),
    _Commit(13, (12,), "revert: undo the split\n", ("src/split.txt", "joined\n")),
    _Commit(14, (13,), "style: format the sources\n", ("src/style.txt", "styled\n")),
    _Commit(15, (14,), "test: cover the reader\n", ("tests/reader.txt", "covered\n")),
    _Commit(16, (15,), "ci: run the checks\n", (".ci.txt", "checks\n")),
    _Commit(17, (16,), "chore(release): set new version\n", ("version.txt", "0.3.0-SNAPSHOT\n")),
    _Commit(18, (17,), "this commit is not conventional\n", ("notes.txt", "free text\n")),
    _Commit(19, (18,), "chore: tidy the notes\n", ("notes.txt", "tidy\n")),
    _Tag("v0.3.0-SNAPSHOT", 19),
    _Commit(20, (19,), "feat(api): expose the reader\n", ("src/api.txt", "api\n")),
)
TAGS = tuple(step.name for step in _HISTORY if isinstance(step, _Tag))


def _data(text: str) -> bytes:
    """Write one exact-length `data` block and its closing line feed."""
    payload = text.encode("utf-8")
    return b"data %d\n%s\n" % (len(payload), payload)


def _stamp(mark: int, offset: int) -> str:
    """Give a mark's fixed date, `offset` seconds past its hour, with its fixed zone."""
    return f"{_EPOCH + mark * _HOUR + offset} {_ZONES[mark % len(_ZONES)]}"


def _commit(commit: _Commit, tree: dict[str, str]) -> bytes:
    """Write one commit replacing its whole tree."""
    header = [f"commit {BRANCH}", f"mark :{commit.mark}", f"author {_AUTHOR} {_stamp(commit.mark, 0)}",
              f"committer {_COMMITTER} {_stamp(commit.mark, 60)}"]
    links = [f"from :{commit.parents[0]}", *(f"merge :{parent}" for parent in commit.parents[1:])] if commit.parents else []
    files = b"".join(f"M 100644 inline {path}\n".encode() + _data(content) for path, content in sorted(tree.items()))
    return "\n".join(header).encode() + b"\n" + _data(commit.message) + "".join(f"{line}\n" for line in links).encode() + b"deleteall\n" + files


def _tag(tag: _Tag) -> bytes:
    """Write one annotated tag of its target mark."""
    header = f"tag {tag.name}\nfrom :{tag.target}\ntagger {_TAGGER} {_stamp(tag.target, 120)}\n"
    return header.encode() + _data(f"Release {tag.name}\n")


def stream() -> bytes:
    """Write the whole fixture history as one fast-import stream, ending with `done`."""
    trees: dict[int, dict[str, str]] = {}
    parts: list[bytes] = []
    for step in _HISTORY:
        if isinstance(step, _Tag):
            parts.append(_tag(step))
            continue
        tree: dict[str, str] = {}
        for parent in reversed(step.parents):
            tree.update(trees[parent])
        if step.change is not None:
            tree[step.change[0]] = step.change[1]
        trees[step.mark] = tree
        parts.append(_commit(step, tree))
    return b"".join(parts) + b"done\n"


def environment(source: Mapping[str, str], global_config: Path) -> dict[str, str]:
    """Give the evidence Git environment: no inherited `GIT_*`, an empty global file and no system file."""
    kept = {name: value for name, value in source.items() if not name.upper().startswith("GIT_")}
    return {**kept, "GIT_CONFIG_GLOBAL": str(global_config), "GIT_CONFIG_NOSYSTEM": "1"}


def _refs(listing: str) -> dict[str, str]:
    """Read `refname NUL objectname` lines."""
    refs: dict[str, str] = {}
    for line in listing.splitlines():
        name, separator, sha = line.partition("\0")
        if not separator or _OBJECT.fullmatch(sha) is None:
            msg = f"unexpected fixture ref listing line {line!r}"
            raise FixtureError(msg)
        refs[name] = sha
    return refs


def _hashes(listing: str) -> FixtureHashes:
    """Keep the branch head and exactly the stream's tags."""
    refs = _refs(listing)
    head = refs.pop(BRANCH, None)
    if head is None:
        msg = f"the fixture repository has no {BRANCH}"
        raise FixtureError(msg)
    tags = {name.removeprefix(_TAGS_PREFIX): sha for name, sha in refs.items()}
    if set(tags) != set(TAGS) or any(not name.startswith(_TAGS_PREFIX) for name in refs):
        msg = f"the fixture repository holds the tags {sorted(refs)}, expected {list(TAGS)}"
        raise FixtureError(msg)
    return FixtureHashes(head, tuple((name, tags[name]) for name in TAGS))


def build(git: GitExecutionContext, directory: Path) -> FixtureHashes:
    """Create the fixture repository in a new directory and return its branch and tag object hashes.

    Args:
        git: The evidence Git, over `environment(...)`.
        directory: A directory that does not exist yet, outside any repository.

    Returns:
        The head commit of `refs/heads/main` and each tag object, in `TAGS` order.

    Raises:
        FixtureError: Git lists another branch or other tags than the stream's.
    """
    directory.mkdir(parents=True)
    git.run([*CONFIG, "init", "--quiet", "--template=", "--object-format=sha1", "--initial-branch=main"], cwd=directory)
    git.run([*CONFIG, "fast-import", "--quiet", "--done"], cwd=directory, input=stream())
    listing = git.run([*CONFIG, "for-each-ref", "--format=%(refname)%00%(objectname)", BRANCH, "refs/tags"], cwd=directory).stdout
    return _hashes(listing)


def verify(recorded: FixtureHashes, built: FixtureHashes) -> None:
    """Require the regenerated hashes to equal the recorded ones exactly, naming the first ref that differs.

    Since code review round 1, every tag of either side is compared in order, so a tag the bundle does not record
    fails as surely as a changed one.
    """
    if built.head != recorded.head:
        msg = f"the regenerated fixture's {BRANCH} is {built.head}, the bundle records {recorded.head}"
        raise FixtureError(msg)
    for expected, regenerated in itertools.zip_longest(recorded.tags, built.tags):
        if regenerated != expected:
            name = (expected or regenerated or ("", ""))[0]
            records = None if expected is None else expected[1]
            found = None if regenerated is None else regenerated[1]
            msg = f"the regenerated fixture's {_TAGS_PREFIX}{name} is {found}, the bundle records {records}"
            raise FixtureError(msg)


# eof
