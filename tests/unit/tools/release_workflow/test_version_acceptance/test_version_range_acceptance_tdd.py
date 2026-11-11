"""The range acceptance rows AC13 to AC15 through `versions range` and the release-version rule.

Step 9 of v0.14.0 version-sources. Each declared linear history is run through
`cli.main` with the shipped registry: `versions range` prints the selected
target, baseline, range and commit count, keeps the caller's spelling of a tag
target, names the baseline by its `vX.Y.Z` alias, warns about each excluded
unvalidated engine release and fails with status 2 on conflicting tags, an
ambiguous release, or a missing, prerelease or ineligible target, always with
at most four Git calls and no source read. The release-version rule for items
5 and 7 is checked in process on the same kind of histories, and
`versions set` itself does not apply it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.version_support import (
    ENGINE_TRAILER,
    annotation,
    command_project,
    run_command,
    tagged_history,
    version_txt,
)
from tools.release_workflow.tags import RangeError, check_release_version

if TYPE_CHECKING:
    from collections.abc import Mapping

    from tests.unit.tools.release_workflow.acceptance_support import LockFacts
    from tests.unit.tools.release_workflow.git_test_support import GitSandbox

    type Tags = Mapping[str, tuple[int, str | None]]

_INVALID = 2
_MAX_CALLS = 4
_UNVALIDATED = annotation(trailer=True)
_VALIDATED = annotation(trailer=True, valid=True)
_AMBIGUOUS = f"Release notes\n[valid]\n{ENGINE_TRAILER}\n"
_HALO: Tags = {"0.0.22": (1, None), "v0.0.23": (2, annotation()), "v0.0.24": (3, annotation())}
_TWO_ALIASES: Tags = {"v0.12.0": (1, None), "0.13.0": (2, None), "v0.13.0": (2, _UNVALIDATED)}
_HEAD_ALIASES: Tags = {"v0.13.0": (1, None), "0.14.0": (3, None), "v0.14.0": (3, annotation())}


def _range(target: str, baseline: str, revisions: str, commits: int) -> str:
    """Spell the four lines `versions range` prints."""
    return f"target={target}\nbaseline={baseline}\nrange={revisions}\ncommits={commits}\n"


_SELECTED: dict[str, tuple[Tags, list[str], str, str]] = {
    "snapshot-at-head": ({"v0.13.0": (1, None), "v0.14.0-SNAPSHOT": (3, None)}, [], _range("HEAD", "v0.13.0", "v0.13.0..HEAD", 2), ""),
    "unvalidated-engine-release": ({"v0.13.0": (1, annotation()), "v0.14.0": (3, _UNVALIDATED)}, [],
                                   _range("HEAD", "v0.13.0", "v0.13.0..HEAD", 2), "excluded unvalidated engine release v0.14.0 between v0.13.0 and HEAD"),
    "predecessor-of-a-tag": ({"v0.12.0": (1, None), "v0.13.0": (2, None)}, ["v0.13.0"], _range("v0.13.0", "v0.12.0", "v0.12.0..v0.13.0", 1), ""),
    "mixed-prefixes-at-head": (_HALO, [], _range("HEAD", "v0.0.24", "v0.0.24..HEAD", 0), ""),
    "mixed-prefixes-tag": (_HALO, ["v0.0.24"], _range("v0.0.24", "v0.0.23", "v0.0.23..v0.0.24", 1), ""),
    "historical-and-unvalidated-aliases": (_TWO_ALIASES, [], _range("HEAD", "v0.12.0", "v0.12.0..HEAD", 2),
                                           "excluded unvalidated engine release 0.13.0 and v0.13.0 between v0.12.0 and HEAD"),
    "validated-and-unvalidated-aliases": ({"v0.12.0": (1, None), "v0.13.0": (2, _VALIDATED), "0.13.0": (2, _UNVALIDATED)}, [],
                                          _range("HEAD", "v0.12.0", "v0.12.0..HEAD", 2),
                                          "excluded unvalidated engine release 0.13.0 and v0.13.0 between v0.12.0 and HEAD"),
    "two-unvalidated-aliases": ({"v0.12.0": (1, None), "0.13.0": (2, _UNVALIDATED), "v0.13.0": (2, _UNVALIDATED)}, [],
                                _range("HEAD", "v0.12.0", "v0.12.0..HEAD", 2),
                                "excluded unvalidated engine release 0.13.0 and v0.13.0 between v0.12.0 and HEAD"),
    "historical-and-validated-aliases": ({"0.13.0": (1, None), "v0.13.0": (1, _VALIDATED)}, [], _range("HEAD", "v0.13.0", "v0.13.0..HEAD", 2), ""),
    "eligible-aliases-at-head": (_HEAD_ALIASES, [], _range("HEAD", "v0.14.0", "v0.14.0..HEAD", 0), ""),
    "unprefixed-alias-target": (_HEAD_ALIASES, ["0.14.0"], _range("0.14.0", "v0.13.0", "v0.13.0..0.14.0", 2), ""),
    "prefixed-alias-target": (_HEAD_ALIASES, ["v0.14.0"], _range("v0.14.0", "v0.13.0", "v0.13.0..v0.14.0", 2), ""),
    "first-release": ({"v0.1.0-SNAPSHOT": (2, None)}, [], _range("HEAD", "none", "HEAD", 3), ""),
}


@pytest.mark.parametrize("case", list(_SELECTED))
def test_selected_ranges(git_sandbox: GitSandbox, case: str) -> None:
    """AC13 and AC14: the ancestry rule over declared histories, at most four Git calls, no source read."""
    tags, target, expected, warning = _SELECTED[case]
    _, history = tagged_history(git_sandbox, 3, tags)
    run = run_command(git_sandbox, ["versions", "range", *target])
    assert (run.status, run.out) == (0, expected)
    assert run.err == (f"{warning}\n" if warning else "")
    assert len(history.calls) <= _MAX_CALLS


_REFUSED: dict[str, tuple[Tags, list[str], str]] = {
    "same-version-two-commits": ({"0.13.0": (1, None), "v0.13.0": (2, None)}, [], "conflicting tags 0.13.0 and v0.13.0"),
    "alias-on-an-earlier-commit": ({"1.0.0": (1, None), "v1.0.0": (2, None)}, ["v1.0.0"], "conflicting tags 1.0.0 and v1.0.0"),
    "two-versions-one-commit": ({"v1.0.0": (2, None), "v1.1.0": (2, None)}, ["v1.1.0"], "conflicting tags v1.0.0 and v1.1.0"),
    "ambiguous-engine-release": ({"v0.13.0": (1, None), "v0.13.1": (2, _AMBIGUOUS)}, [], "ambiguous release v0.13.1 between v0.13.0 and HEAD"),
    "validated-and-ambiguous-aliases": ({"v0.12.0": (1, None), "v0.13.0": (2, _VALIDATED), "0.13.0": (2, _AMBIGUOUS)}, [],
                                        "ambiguous release 0.13.0 and v0.13.0 between v0.12.0 and HEAD"),
    "two-ambiguous-aliases": ({"v0.12.0": (1, None), "0.13.0": (2, _AMBIGUOUS), "v0.13.0": (2, _AMBIGUOUS)}, [],
                              "ambiguous release 0.13.0 and v0.13.0 between v0.12.0 and HEAD"),
    "unprefixed-target-with-unvalidated-alias": (_TWO_ALIASES, ["0.13.0"],
                                                 "tag 0.13.0 cannot be a range target: its release 0.13.0 and v0.13.0 is not eligible"),
    "prefixed-target-with-unvalidated-alias": (_TWO_ALIASES, ["v0.13.0"],
                                               "tag v0.13.0 cannot be a range target: its release 0.13.0 and v0.13.0 is not eligible"),
    "missing-target": ({"v0.13.0": (1, None)}, ["v0.14.0"], "tag v0.14.0 does not exist"),
    "prerelease-target": ({"v0.14.0-SNAPSHOT": (2, None)}, ["v0.14.0-SNAPSHOT"], "expected a stable release tag name"),
}


@pytest.mark.parametrize("case", list(_REFUSED))
def test_refused_ranges(git_sandbox: GitSandbox, case: str) -> None:
    """AC13 and AC14: conflicting tags, ambiguous releases and unusable targets are status 2, naming the tags."""
    tags, target, message = _REFUSED[case]
    _, history = tagged_history(git_sandbox, 3, tags)
    run = run_command(git_sandbox, ["versions", "range", *target])
    assert (run.status, run.out) == (_INVALID, "")
    assert message in run.err
    assert len(history.calls) <= _MAX_CALLS


@pytest.mark.parametrize(("tags", "version", "message"), [
    ({"v0.13.0": (1, None)}, "0.13.0", "version 0.13.0 is reserved: tag v0.13.0 already names it"),
    ({"0.13.0": (1, None)}, "0.13.0", "version 0.13.0 is reserved: tag 0.13.0 already names it"),
    (_TWO_ALIASES, "0.13.0", "version 0.13.0 is reserved: tag 0.13.0 and v0.13.0 already names it"),
    ({"v0.13.0": (1, None)}, "0.12.9", "version 0.12.9 is not higher than release v0.13.0, reachable from main"),
    ({}, "0.1.0", None),
    (_TWO_ALIASES, "0.12.5", None),
])
def test_release_version_rule(git_sandbox: GitSandbox, tags: Tags, version: str, message: str | None) -> None:
    """AC15: both spellings reserve a version; an ineligible boundary never bounds it; no stable release accepts any."""
    git, history = tagged_history(git_sandbox, 3, tags)
    if message is None:
        check_release_version(git, cwd=git_sandbox.home / "A", version=version)
    else:
        with pytest.raises(RangeError, match=message):
            check_release_version(git, cwd=git_sandbox.home / "A", version=version)
    assert history.calls == [("tag_records",), ("tag_records", "main")]


def test_versions_set_does_not_apply_the_release_version_rule(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """AC15: a target below a reachable release is still written by `versions set`, which makes no Git call."""
    del lock_facts
    root = command_project(git_sandbox, {"version.txt": version_txt("0.13.0")})
    _, history = tagged_history(git_sandbox, 3, {"v0.13.0": (1, None)})
    run = run_command(git_sandbox, ["versions", "set", "0.12.0"])
    assert (run.status, run.out) == (0, "version.txt\tversion\t0.13.0\t0.12.0\n")
    assert (root / "version.txt").read_bytes() == version_txt("0.12.0")
    assert history.calls == []


# eof
