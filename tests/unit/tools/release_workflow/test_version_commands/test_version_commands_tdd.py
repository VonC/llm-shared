"""The five version command contracts through `cli.main` and the shipped registry.

Step 9 of v0.14.0 version-sources. `version` prints the anchor's token, title,
an empty line and the notes; `versions list` a header and tab-separated
records with `/` paths and `-` for a non-participating form and value;
`versions check` its records, with status 1 on drift; `versions set` each old
and new value, or `unchanged`; `versions range` four `key=value` lines. A
missing, extra or malformed token fails with status 2 before any identity
load or Git context. Each read command warns about every leftover
version-transition evidence directory, names its remedy and writes nothing;
only `list` and `range` call Git. Errors keep their status: 2 for a refused
source or range target, 1 for evidence that cannot be written, and 3 for an
incomplete restoration, which reaches the caller.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.acceptance_support import snapshot
from tests.unit.tools.release_workflow.version_support import (
    FIXED_NOW,
    Faults,
    annotation,
    command_project,
    declare_evidence,
    package_json,
    package_lock,
    pyproject_toml,
    run_command,
    tagged_history,
    uv_lock,
    version_registry,
    version_txt,
)
from tools.release_workflow import cli, versions
from tools.release_workflow.git import GitExecutionContext
from tools.release_workflow.version_evidence import (
    STANDALONE,
    EvidenceManifest,
    EvidenceState,
)

if TYPE_CHECKING:
    from pathlib import Path
    from typing import NoReturn

    from tests.unit.tools.release_workflow.acceptance_support import LockFacts
    from tests.unit.tools.release_workflow.git_test_support import GitSandbox

_INVALID = 2
_FAILED = 1
_INCOMPLETE = 3
_EVIDENCE = "a.version-transition.20261108T090000+0100-7"
_LIST_HEADER = "path\tfield\tadapter\tform\tvalue\tstatus\n"


def _manifest(owner: str, state: EvidenceState) -> bytes:
    """Encode a manifest with no file, as a stopped transition left it."""
    return EvidenceManifest(owner, "0.14.0", state, FIXED_NOW.isoformat(), ()).encode()


def test_shipped_registry_builds_both_commands_from_the_versions_module() -> None:
    """`version` takes no token; `versions` validates its tokens and uses the production transition ports."""
    assert dict(cli.SHIPPED_HANDLERS) == {
        "version": cli.Handler(versions.show_version),
        "versions": cli.Handler(versions.VersionsCommand(), validate_arguments=versions.validate_versions),
    }


@pytest.mark.parametrize(("content", "expected"), [
    (version_txt("0.14.0-SNAPSHOT -- Title", "Line 1\n\nLine 3\n"), "0.14.0-SNAPSHOT\nTitle\n\nLine 1\n\nLine 3\n"),
    (version_txt("0.14.0"), "0.14.0\n\n\n"),
    (version_txt("0.14.0 --", "Notes é", newline="\r\n", bom=True), "0.14.0\n\n\nNotes é"),
])
def test_version_prints_token_title_empty_line_and_notes(git_sandbox: GitSandbox, content: bytes, expected: str) -> None:
    """Empty titles and notes are accepted; the output is LF; nothing is written and Git is not called."""
    command_project(git_sandbox, {"version.txt": content})
    before = snapshot(git_sandbox.home)
    run = run_command(git_sandbox, ["version"])
    assert (run.status, run.out, run.err) == (0, expected, "")
    assert snapshot(git_sandbox.home) == before
    assert git_sandbox.verified_git.facts.history.calls == []


@pytest.mark.parametrize(("tokens", "message"), [
    (["version", "extra"], "'version' takes no arguments: extra"),
    (["versions"], "Invalid versions operation '(none)'"),
    (["versions", "bogus"], "Invalid versions operation 'bogus'"),
    (["versions", "list", "extra"], "Invalid versions operation 'list extra'"),
    (["versions", "check", "now"], "Invalid versions operation 'check now'"),
    (["versions", "set"], "Invalid versions operation 'set'"),
    (["versions", "set", "v0.14.0"], "Invalid version 'v0.14.0'"),
    (["versions", "set", "0.14.0", "0.15.0"], "Invalid versions operation 'set 0.14.0 0.15.0'"),
    (["versions", "range", "v0.14.0-SNAPSHOT"], "versions range 'v0.14.0-SNAPSHOT': expected a stable release tag name"),
    (["versions", "range", "v0.13.0", "HEAD"], "Invalid versions operation 'range v0.13.0 HEAD'"),
])
def test_bad_tokens_fail_before_identity_and_git(tokens: list[str], message: str, tmp_path: Path,
                                                 monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """A missing, extra or malformed token is status 2 with the expected form, before any identity load or Git."""
    def refused(*_arguments: object, **_options: object) -> NoReturn:
        msg = "token validation must come first"
        raise AssertionError(msg)

    monkeypatch.setattr(GitExecutionContext, "create", refused)
    monkeypatch.setattr(cli.RuntimeIdentity, "load", refused)
    assert cli.main(tokens, entry_kind="explicit-native", original_cwd=tmp_path) == _INVALID
    err = capsys.readouterr().err
    assert err.startswith("Release preflight failed: ")
    assert message in err


def test_list_prints_header_and_one_record_per_source(git_sandbox: GitSandbox) -> None:
    """Participating sources, then tool-only files, then undeclared candidates, from one Git listing."""
    command_project(git_sandbox, {
        "version.txt": version_txt("0.14.0-SNAPSHOT"),
        "pyproject.toml": b"[tool.ruff]\nline-length = 100\n", "uv.lock": uv_lock(),
        "api/package.json": package_json("0.14.0"), "api/package-lock.json": package_lock("0.14.0"),
        "frontend/package.json": package_json("2.0.0", name="frontend"),
    }, "[component:api]\nroot = api\n")
    before = snapshot(git_sandbox.home)
    run = run_command(git_sandbox, ["versions", "list"])
    assert (run.status, run.err) == (0, "")
    assert run.out == _LIST_HEADER + (
        "version.txt\tversion\tanchor\tsnapshot\t0.14.0-SNAPSHOT\tparticipating\n"
        "api/package.json\tversion\tnpm\trelease-only\t0.14.0\tparticipating\n"
        "api/package-lock.json\tversion\tnpm\trelease-only\t0.14.0\tparticipating\n"
        'api/package-lock.json\tpackages[""].version\tnpm\trelease-only\t0.14.0\tparticipating\n'
        "pyproject.toml\tproject.version\tpython\t-\t-\tnot-participating tool-only\n"
        "uv.lock\tpackage.version\tpython\t-\t-\tnot-participating tool-only\n"
        "frontend/package.json\tversion\tnpm\t-\t-\tnot-participating undeclared\n"
    )
    assert snapshot(git_sandbox.home) == before
    assert git_sandbox.verified_git.facts.history.calls == [("listing",)]


@pytest.mark.parametrize(("value", "status", "state", "diagnostic"), [
    ("0.14.0", 0, "ok", ""),
    ("0.13.0", _FAILED, "drift",
     "versions check: 1 of 2 sources drift from the anchor 0.14.0-SNAPSHOT; synchronize them with versions set, or correct the anchor\n"),
])
def test_check_prints_actual_and_expected_values(git_sandbox: GitSandbox, value: str, status: int, state: str, diagnostic: str) -> None:
    """Each participating source is `ok` or `drift`; drift is status 1; no Git call, no write."""
    command_project(git_sandbox, {"version.txt": version_txt("0.14.0-SNAPSHOT"), "package.json": package_json(value)})
    before = snapshot(git_sandbox.home)
    run = run_command(git_sandbox, ["versions", "check"])
    assert (run.status, run.err) == (status, diagnostic)
    assert run.out == ("version.txt\tversion\tsnapshot\t0.14.0-SNAPSHOT\t0.14.0-SNAPSHOT\tok\n"
                       f"package.json\tversion\trelease-only\t{value}\t0.14.0\t{state}\n")
    assert snapshot(git_sandbox.home) == before
    assert git_sandbox.verified_git.facts.history.calls == []


def test_set_prints_each_change_then_unchanged(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """The first run prints old and new values, `version.txt` last; the second prints `unchanged`; no Git call."""
    del lock_facts
    root = command_project(git_sandbox, {"version.txt": version_txt("0.13.0"), "pyproject.toml": pyproject_toml(), "uv.lock": uv_lock()})
    first = run_command(git_sandbox, ["versions", "set", "0.14.0"])
    assert (first.status, first.err) == (0, "")
    assert first.out == ("pyproject.toml\tproject.version\t0.13.0\t0.14.0\n"
                         "uv.lock\tpackage.version\t0.13.0\t0.14.0\n"
                         "version.txt\tversion\t0.13.0\t0.14.0\n")
    assert (root / "pyproject.toml").read_bytes() == pyproject_toml("0.14.0")
    second = run_command(git_sandbox, ["versions", "set", "0.14.0"])
    assert (second.status, second.out, second.err) == (0, "unchanged\n", "")
    assert sorted(path.name for path in (root / ".reviews").iterdir()) == [".gitignore"]
    assert git_sandbox.verified_git.facts.history.calls == []


def test_range_prints_four_key_value_lines(git_sandbox: GitSandbox) -> None:
    """Target, baseline, range and commit count, from the selector's Git calls only; no source is read."""
    _, history = tagged_history(git_sandbox, 3, {"v0.13.0": (1, annotation())})
    run = run_command(git_sandbox, ["versions", "range"])
    assert (run.status, run.out, run.err) == (0, "target=HEAD\nbaseline=v0.13.0\nrange=v0.13.0..HEAD\ncommits=2\n", "")
    assert history.calls == [("tag_records", "HEAD"), ("tag_names", "HEAD", "refs/tags/v0.13.0"),
                             ("commit_count", "refs/tags/v0.13.0..HEAD")]


@pytest.mark.parametrize("command", [["version"], ["versions", "list"], ["versions", "check"], ["versions", "range"]])
def test_read_commands_warn_about_leftover_evidence_and_write_nothing(git_sandbox: GitSandbox, command: list[str]) -> None:
    """Interrupted evidence is named on stderr with its remedy; the command still succeeds."""
    root = command_project(git_sandbox, {"version.txt": version_txt("0.14.0")})
    tagged_history(git_sandbox, 1, {})
    evidence = declare_evidence(root / ".reviews", _EVIDENCE, _manifest(STANDALONE, EvidenceState.WRITING))
    before = snapshot(git_sandbox.home)
    run = run_command(git_sandbox, command)
    assert run.status == 0
    assert run.err.startswith(f"warning: leftover interrupted version-transition evidence {evidence}; versions set stops on it")
    assert snapshot(git_sandbox.home) == before


@pytest.mark.parametrize(("manifest", "kind", "remedy"), [
    (_manifest(STANDALONE, EvidenceState.COMPLETE), "completed standalone residue", "the next versions set removes it"),
    (_manifest("release-9", EvidenceState.COMPLETE), "lifecycle-owned", "it belongs to a release lifecycle"),
    (b"{not json", "unreadable", "versions set stops on it: inspect it, restore what is needed and remove it"),
])
def test_each_evidence_kind_has_its_remedy(git_sandbox: GitSandbox, manifest: bytes, kind: str, remedy: str) -> None:
    """Completed residue, a lifecycle's evidence and an unreadable manifest each get their own advice."""
    root = command_project(git_sandbox, {"version.txt": version_txt("0.14.0")})
    evidence = declare_evidence(root / ".reviews", _EVIDENCE, manifest)
    run = run_command(git_sandbox, ["version"])
    assert (run.status, run.out) == (0, "0.14.0\n\n\n")
    assert run.err.startswith(f"warning: leftover {kind} version-transition evidence {evidence}; {remedy}")
    assert run.err.count("\n") == 1


@pytest.mark.parametrize(("command", "message"), [
    (["version"], "version failed: "),
    (["versions", "check"], "versions check failed: "),
    (["versions", "range", "v9.9.9"], "versions range failed: tag v9.9.9 does not exist"),
    (["versions", "set", "0.14.0"], "versions set 0.14.0 failed: "),
])
def test_refusals_keep_status_2(git_sandbox: GitSandbox, lock_facts: LockFacts, command: list[str], message: str) -> None:
    """A missing anchor or an unknown range target is status 2 and writes nothing."""
    del lock_facts
    tagged_history(git_sandbox, 1, {})
    before = snapshot(git_sandbox.home)
    run = run_command(git_sandbox, command)
    assert (run.status, run.out) == (_INVALID, "")
    assert message in run.err
    assert snapshot(git_sandbox.home) == before


def test_evidence_that_cannot_be_written_is_status_1(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """No source is written when the recovery evidence fails; the evidence error keeps its status."""
    root = command_project(git_sandbox, {"version.txt": version_txt("0.13.0"), "package.json": package_json()})
    faults = Faults(root / ".reviews", fail_when=lambda path, _content: path.name == "manifest.json")
    run = run_command(git_sandbox, ["versions", "set", "0.14.0"], handlers=version_registry(faults.ports(lock_facts.probe)))
    assert (run.status, run.out) == (_FAILED, "")
    assert "versions set 0.14.0 failed: cannot write evidence" in run.err
    assert faults.sources == []
    assert (root / "version.txt").read_bytes() == version_txt("0.13.0")


def test_incomplete_restoration_reaches_the_caller_as_status_3(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """The unrestored source and its retained copy are named; the summary states the outcome."""
    original = package_json()
    root = command_project(git_sandbox, {"version.txt": version_txt("0.13.0"), "package.json": original, "pyproject.toml": pyproject_toml()})

    def fails(path: Path, content: bytes) -> bool:
        return path.name == "package.json" and content == original

    faults = Faults(root / ".reviews", fail_write=1, fail_when=fails)
    run = run_command(git_sandbox, ["versions", "set", "0.14.0"], handlers=version_registry(faults.ports(lock_facts.probe)))
    assert (run.status, run.out) == (_INCOMPLETE, "")
    assert f"{root / 'package.json'} was not restored; its original is retained at " in run.err
    assert run.err.endswith("versions set 0.14.0 failed: restoration incomplete\n")
    assert (root / "package.json").read_bytes() == package_json("0.14.0")


# eof
