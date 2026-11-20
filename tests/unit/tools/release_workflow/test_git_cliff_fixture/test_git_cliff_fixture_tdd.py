"""The snapshot-tag fixture history is one deterministic `git fast-import` stream built under a controlled Git.

Step 6 of v0.14.0 git-cliff-provisioning (design "Frozen inputs and the
coverage matrix"; design decision Q14; requirement clarification Q13; plan
decision Q09). No process: Git is a recording `subprocess.run` behind a real
`GitExecutionContext`.

- The stream is byte-identical across two builds and well formed: every
  `data` count is exact, it holds no carriage return and ends with `done`.
- It fixes every object-producing input: each commit replaces its whole tree
  (`deleteall`), names its author and committer with dates and zones and its
  parent order, one commit is a merge; the commit messages cover the parser
  and skip-rule matrix of the dev_workflow `cliff.toml`; the annotated tags,
  stable and `-SNAPSHOT`, name their tagger with a date and zone.
- The Git calls use `--object-format=sha1`, configuration on the command line
  only (an empty `GIT_CONFIG_GLOBAL` file and `GIT_CONFIG_NOSYSTEM=1`, every
  inherited `GIT_*` dropped), no hooks (`--template=`), no signing and no
  line-ending conversion; the stream reaches `fast-import` as input bytes.
- The built hashes are read in one `for-each-ref` call; a listing without the
  branch or with other tags fails, and recorded hashes that differ from the
  regenerated ones fail naming the first differing ref; since code review
  round 1, a tag missing from either side fails too.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_cliff_harness_fake import (
    FakeGit,
    GitCall,
    git_context,
    refs_listing,
)
from tools.release_workflow.git_cliff.fixture_history import (
    CONFIG,
    TAGS,
    FixtureError,
    FixtureHashes,
    build,
    environment,
    stream,
    verify,
)

if TYPE_CHECKING:
    from pathlib import Path

_MINIMUM_COMMITS = 10
_IDENTITY = re.compile(rb"^(author|committer|tagger) [^<>\n]+ <[^<>\n]+> \d+ [+-]\d{4}$")
_HASHES = FixtureHashes(head="a" * 40, tags=tuple((name, f"{index:x}" * 40) for index, name in enumerate(TAGS, start=1)))
_MESSAGES = (
    b"feat:", b"fix(", b"docs:", b"perf:", b"refactor:", b"style:", b"test:", b"ci:", b"chore:", b"revert:", b"feat!:",
    b"chore(release): prepare for", b"chore(deps", b"wip:", b"security", b"Merge branch",
)


def _commands(content: bytes) -> list[tuple[bytes, list[bytes], list[bytes]]]:
    """Read the stream as fast-import does: each command with its header lines and the exact bytes of each `data`."""
    commands: list[tuple[bytes, list[bytes], list[bytes]]] = []
    position = 0
    while position < len(content):
        end = content.index(b"\n", position)
        line, position = content[position:end], end + 1
        if line.startswith(b"data "):
            size = int(line.removeprefix(b"data "))
            commands[-1][2].append(content[position:position + size])
            position += size
            if content[position:position + 1] == b"\n":
                position += 1
        elif line.startswith((b"commit ", b"tag ", b"done")):
            commands.append((line, [], []))
        else:
            commands[-1][1].append(line)
    return commands


def test_the_stream_is_byte_identical_across_two_builds_and_well_formed() -> None:
    """Two builds give the same bytes; every data count is exact; no carriage return; the stream ends with `done`."""
    first, second = stream(), stream()
    assert first == second
    commands = _commands(first)
    assert commands[-1][0] == b"done"
    assert b"\r" not in first
    assert first.endswith(b"done\n")


def _commits() -> list[tuple[bytes, list[bytes], list[bytes]]]:
    """Return the commit commands of the stream."""
    return [command for command in _commands(stream()) if command[0] == b"commit refs/heads/main"]


def test_every_commit_fixes_its_tree_identities_and_dates_with_zones() -> None:
    """Each commit replaces its whole tree and names its author, then its committer, each with a date and zone."""
    commits = _commits()
    assert len(commits) >= _MINIMUM_COMMITS
    for _head, lines, _data in commits:
        assert b"deleteall" in lines
        identities = [line for line in lines if line.startswith((b"author ", b"committer "))]
        assert [line.split(b" ")[0] for line in identities] == [b"author", b"committer"]
        assert all(_IDENTITY.match(line) for line in identities)
    assert {line.split(b" ")[-1] for _head, lines, _data in commits for line in lines if line.startswith(b"committer ")} >= {b"+0100", b"-0500"}


def test_one_commit_is_a_merge_naming_its_first_parent_first() -> None:
    """The parent order is fixed: `from` the first parent, then `merge` the second."""
    merges = [lines for _head, lines, _data in _commits() if any(line.startswith(b"merge :") for line in lines)]
    assert len(merges) == 1
    assert next(line for line in merges[0] if line.startswith((b"from ", b"merge "))).startswith(b"from :")


def test_the_messages_cover_the_parser_and_skip_rule_matrix() -> None:
    """Every group, skip rule, the breaking marker, the security body and an unconventional merge appear."""
    messages = b"\n".join(data[0] for head, _lines, data in _commands(stream()) if head.startswith(b"commit "))
    missing = [prefix for prefix in _MESSAGES if prefix not in messages]
    assert missing == []


def test_the_annotated_tags_are_stable_and_snapshot_with_their_tagger_date_and_zone() -> None:
    """The tags are the declared stable and `-SNAPSHOT` names, each with a tagger line and a message."""
    tags = [(head, lines, data) for head, lines, data in _commands(stream()) if head.startswith(b"tag ")]
    assert [head.removeprefix(b"tag ").decode() for head, _lines, _data in tags] == list(TAGS)
    assert any(name.endswith("-SNAPSHOT") for name in TAGS)
    assert any(not name.endswith("-SNAPSHOT") for name in TAGS)
    for _head, lines, data in tags:
        assert lines[0].startswith(b"from :")
        assert _IDENTITY.match(lines[1])
        assert data[0].strip()


def test_environment_drops_inherited_git_variables_and_selects_an_empty_global_file(tmp_path: Path) -> None:
    """No system configuration, the empty global file, and no inherited `GIT_*` of any case."""
    config = tmp_path / "empty.gitconfig"
    chosen = environment({"PATH": "C:/bin", "GIT_AUTHOR_DATE": "1 +0000", "git_config_system": "C:/x", "GIT_DIR": "C:/repo"}, config)
    assert chosen == {"PATH": "C:/bin", "GIT_CONFIG_GLOBAL": str(config), "GIT_CONFIG_NOSYSTEM": "1"}


def _built(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, listing: bytes | None = None) -> tuple[FakeGit, FixtureHashes]:
    """Build the fixture through a recording Git whose `for-each-ref` reports a listing, the expected one by default."""
    config = tmp_path / "empty.gitconfig"
    config.write_bytes(b"")
    fake = FakeGit({"for-each-ref": refs_listing(_HASHES) if listing is None else listing})
    git = git_context(tmp_path, monkeypatch, fake, environment({"GIT_TRACE": "1"}, config))
    return fake, build(git, tmp_path / "fixture")


def _config_pairs(call: GitCall) -> list[str]:
    """Return the values of the `-c` options of a call."""
    return [call.arguments[index + 1] for index, argument in enumerate(call.arguments) if argument == "-c"]


def test_build_inits_a_sha1_repository_without_hooks_and_imports_the_stream_as_input(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`init`, then `fast-import` fed the stream bytes, then one `for-each-ref`, all in the fixture directory."""
    fake, hashes = _built(tmp_path, monkeypatch)
    directory = tmp_path / "fixture"
    assert [call.command for call in fake.calls] == ["init", "fast-import", "for-each-ref"]
    init, imported, listed = fake.calls
    assert {"--quiet", "--template=", "--object-format=sha1", "--initial-branch=main"} <= set(init.arguments)
    assert (imported.input, imported.stdin) == (stream(), "absent")
    assert imported.arguments[-2:] == ["--quiet", "--done"]
    assert listed.arguments[-3:] == ["--format=%(refname)%00%(objectname)", "refs/heads/main", "refs/tags"]
    assert {call.cwd for call in fake.calls} == {directory}
    assert hashes == _HASHES


def test_every_git_call_has_command_line_configuration_only_no_signing_and_no_line_ending_conversion(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Each call carries the fixed `-c` pairs, an empty global file, no system file and no inherited `GIT_*`."""
    fake, _hashes = _built(tmp_path, monkeypatch)
    for call in fake.calls:
        assert {"core.autocrlf=false", "core.safecrlf=false", "commit.gpgSign=false", "tag.gpgSign=false"} <= set(_config_pairs(call))
        assert call.environment["GIT_CONFIG_GLOBAL"] == str(tmp_path / "empty.gitconfig")
        assert call.environment["GIT_CONFIG_NOSYSTEM"] == "1"
        assert "GIT_TRACE" not in call.environment
    assert (tmp_path / "empty.gitconfig").read_bytes() == b""
    assert list(CONFIG[::2]) == ["-c"] * (len(CONFIG) // 2)


@pytest.mark.parametrize(("listing", "reason"), [
    pytest.param(b"refs/tags/v0.1.0\0" + b"1" * 40 + b"\n", "refs/heads/main", id="no-branch"),
    pytest.param(refs_listing(FixtureHashes("a" * 40, (("v9.9.9", "9" * 40),))), "tags", id="other-tags"),
    pytest.param(b"refs/heads/main " + b"a" * 40 + b"\n", "listing", id="malformed"),
])
def test_a_listing_without_the_branch_or_with_other_tags_fails(listing: bytes, reason: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The built repository must hold the branch and exactly the stream's tags."""
    with pytest.raises(FixtureError, match=reason):
        _built(tmp_path, monkeypatch, listing)


def test_verify_accepts_the_same_hashes() -> None:
    """A regeneration reproducing the recorded hashes passes."""
    verify(_HASHES, FixtureHashes(_HASHES.head, _HASHES.tags))


@pytest.mark.parametrize(("built", "named"), [
    pytest.param(FixtureHashes("f" * 40, _HASHES.tags), "refs/heads/main", id="head"),
    pytest.param(FixtureHashes(_HASHES.head, (*_HASHES.tags[:-1], (TAGS[-1], "f" * 40))), f"refs/tags/{TAGS[-1]}", id="tag"),
])
def test_recorded_hashes_that_differ_from_the_regenerated_ones_fail(built: FixtureHashes, named: str) -> None:
    """The first differing ref is named with both hashes."""
    with pytest.raises(FixtureError, match=named) as raised:
        verify(_HASHES, built)
    assert "f" * 40 in str(raised.value)


@pytest.mark.parametrize(("built", "named"), [
    pytest.param(FixtureHashes(_HASHES.head, _HASHES.tags[:-1]), f"refs/tags/{TAGS[-1]} is None", id="missing-tag"),
    pytest.param(FixtureHashes(_HASHES.head, (*_HASHES.tags, ("v9.9.9", "9" * 40))), "refs/tags/v9.9.9 is 9", id="extra-tag"),
])
def test_a_tag_missing_from_either_side_fails(built: FixtureHashes, named: str) -> None:
    """Code review round 1: every tag of either side is compared, not only the recorded ones."""
    with pytest.raises(FixtureError, match=named):
        verify(_HASHES, built)


# eof
