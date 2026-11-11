"""Properties of annotation classification and linear-chain range selection.

Step 8 of v0.14.0 version-sources: for generated annotation line sequences,
drawn from notes, trailers, `[valid]`, blank lines and near misses, the
classifier agrees with a reference predicate written another way (drop one
final `[valid]`, then look at what remains). For generated linear chains of at
most fifteen commits, each commit carrying no tag, an eligible release, an
unvalidated engine release or a historical plain-spelled release, the baseline
of HEAD is the nearest eligible tagged ancestor, the commit count is its
distance to HEAD (the whole chain without one), and every unvalidated release
after it is warned about. Each generated selection also makes exactly the
call table's Git calls in order: records and count without a candidate,
records, tags between and count for one, and the independent tips before the
tags between for several (code review round 1). Each example draws one bit
field decoded by the test, so each property stays inside the lifecycle limit.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from hypothesis import given, settings
from hypothesis import strategies as st

from tests.unit.tools.release_workflow.repository_simulation import RepositoryFacts
from tests.unit.tools.release_workflow.version_support import (
    ENGINE_TRAILER,
    annotation,
    chain,
)
from tools.release_workflow import tags
from tools.release_workflow.tags import Eligibility

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox

_LINES = ("Release notes", ENGINE_TRAILER, "[valid]", "", "Release tooling:", "[valid] ", f"see {ENGINE_TRAILER}", "Release tooling: ")
_LINE_BITS = 3
_MAX_LINES = 6
_MAX_CHAIN = 15
_CHOICE_BITS = 2
_PREFIX = "Release tooling: "


def _is_trailer(line: str) -> bool:
    """Tell whether a line is a trailer: the exact prefix and a value that is not blank."""
    return line.startswith(_PREFIX) and bool(line[len(_PREFIX):].strip())


def _closing(content: list[str], trailers: list[str]) -> Eligibility:
    """Drop one final `[valid]`; the one trailer must then close the remaining lines, with no `[valid]` among them."""
    validated = content[-1] == "[valid]"
    rest = content[:-1] if validated else content
    if len(trailers) > 1 or rest[-1] != trailers[0] or "[valid]" in rest:
        return Eligibility.AMBIGUOUS
    return Eligibility.VALIDATED if validated else Eligibility.UNVALIDATED


def _reference(lines: list[str]) -> Eligibility:
    """Classify another way than production: no trailer is historical, otherwise see how the trailer closes."""
    content = [line for line in lines if line.strip()]
    trailers = [line for line in content if _is_trailer(line)]
    return _closing(content, trailers) if trailers else Eligibility.HISTORICAL


@settings(max_examples=25)
@given(layout=st.integers(min_value=0, max_value=(1 << (_LINE_BITS * _MAX_LINES + _LINE_BITS)) - 1))
def test_classification_matches_the_reference_predicate(layout: int) -> None:
    """Whole-line classification agrees with the reference on every generated annotation."""
    count = layout & ((1 << _LINE_BITS) - 1)
    lines = [_LINES[(layout >> (_LINE_BITS * (index + 1))) & ((1 << _LINE_BITS) - 1)] for index in range(min(count, _MAX_LINES))]
    assert tags.eligibility("\n".join(lines) + "\n") is _reference(lines)


def test_linear_chains_select_the_nearest_eligible_ancestor(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """The baseline is the nearest eligible tagged ancestor of HEAD and the count its distance."""
    base = git_sandbox.context()

    @settings(max_examples=25)
    @given(length=st.integers(min_value=1, max_value=_MAX_CHAIN), layout=st.integers(min_value=0, max_value=(1 << (_CHOICE_BITS * _MAX_CHAIN)) - 1))
    def check(length: int, layout: int) -> None:
        git = replace(base, facts=RepositoryFacts())
        history = git.facts.history
        commits = chain(history, length)
        eligible: list[tuple[int, str]] = []
        warned: list[tuple[int, str]] = []
        for position, commit in enumerate(commits, 1):
            choice = (layout >> (_CHOICE_BITS * (position - 1))) & ((1 << _CHOICE_BITS) - 1)
            if choice:
                name = f"{'' if choice == 3 else 'v'}0.0.{position}"  # noqa: PLR2004 - choice 3 is a plain historical name
                history.tag(name, commit, annotation(trailer=choice == 2))  # noqa: PLR2004 - choice 2 is unvalidated
                (warned if choice == 2 else eligible).append((position, name))  # noqa: PLR2004
        selection = tags.select_range(git, cwd=tmp_path)
        if not eligible:
            assert (selection.baseline, selection.commits) == (None, length)
            assert history.calls == [("tag_records", "HEAD"), ("commit_count", "HEAD")]
            return
        position, name = eligible[-1]
        assert (selection.baseline, selection.range, selection.commits) == (name, f"{name}..HEAD", length - position)
        assert [warning.split()[4] for warning in selection.warnings] == [tag for at, tag in warned if at > position]
        tips = [("independent_commits", *(f"c{at}" for at, _tag in eligible))] if len(eligible) > 1 else []
        start = f"refs/tags/{name}"
        assert history.calls == [("tag_records", "HEAD"), *tips, ("tag_names", "HEAD", start), ("commit_count", f"{start}..HEAD")]

    check()


# eof
