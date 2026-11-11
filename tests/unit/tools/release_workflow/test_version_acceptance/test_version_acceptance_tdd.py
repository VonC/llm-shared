"""The version-sources acceptance rows AC1 to AC12 through `cli.main`, plus launcher cases.

Step 9 of v0.14.0 version-sources (plan decision Q09). Each row runs one or
more commands through parsing, preflight, dispatch and rendering with the
shipped registry, and compares whole-tree snapshots of the sandbox, ignored
files and the artifact home included: a read command or a refused `set`
leaves every byte as it was, and a transition changes only its sources and
the prepared home. Rows that need an injected failure, a declared lock owner
or a recording lock use the shipped registry whose `versions` command carries
explicit transition ports (plan decision Q07). The lifecycle row calls the
in-process primitive, the only way a lifecycle caller reaches it. The
recorded uv and npm evidence is replayed through `versions set`. One launcher
case per command and per public status (0 to 3) runs production bootstrap,
readiness and rendering.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from tests.unit.tools.release_workflow.acceptance_support import hold, snapshot
from tests.unit.tools.release_workflow.version_support import (
    DEMO_GROUP,
    EVIDENCE_NAME,
    FIXED_NOW,
    PATTERN_INI,
    RESTORATION_FIXTURES,
    TARGET,
    Faults,
    ViewLog,
    annotation,
    command_project,
    crlf,
    declare_evidence,
    gav,
    lines_file,
    package_json,
    package_lock,
    pom_xml,
    pyproject_toml,
    run_command,
    source_bytes,
    tagged_history,
    uv_lock,
    version_inputs,
    version_registry,
    version_txt,
)
from tools.release_workflow.operation_lock import OperationLock
from tools.release_workflow.version_evidence import (
    STANDALONE,
    EvidenceManifest,
    EvidenceState,
)
from tools.release_workflow.version_transition import (
    LifecycleOwnership,
    TransitionError,
    set_versions,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from tests.unit.tools.release_workflow.acceptance_support import LockFacts
    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tests.unit.tools.release_workflow.launcher_simulation import ToolingSimulation
    from tools.release_workflow import cli
    from tools.release_workflow.artifacts import PreparedArtifacts
    from tools.release_workflow.version_transition import TransitionLock
    from tools.release_workflow.windows_process import ProcessIdentity, ProcessState

_INVALID = 2
_FAILED = 1
_INCOMPLETE = 3
_SNAPSHOT = "0.13.0-SNAPSHOT"
_ROOT_POM = gav(DEMO_GROUP, "demo-root", _SNAPSHOT)
_PARENT = f"<parent>{_ROOT_POM}</parent>"
_SET = ["versions", "set", "0.14.0"]
_COMMANDS = (["version"], ["versions", "list"], ["versions", "check"], _SET)
_EVIDENCE = Path(__file__).parents[1] / "test_version_lock_evidence" / "lock_evidence.v1.json"
_RECORDS: list[dict[str, Any]] = json.loads(_EVIDENCE.read_text(encoding="utf-8"))["records"]


def _manifest(state: EvidenceState) -> bytes:
    """Encode a standalone manifest with no file, as a stopped transition left it."""
    return EvidenceManifest(STANDALONE, "0.14.0", state, FIXED_NOW.isoformat(), ()).encode()


def _added(before: Mapping[str, bytes | None], after: Mapping[str, bytes | None]) -> dict[str, bytes | None]:
    """Return the paths of `after` that differ from `before`, new ones included."""
    return {path: content for path, content in after.items() if path not in before or before[path] != content}


@pytest.mark.parametrize("anchor", ["v0.14.0", "0.14.0-snapshot", "0.014.0"])
@pytest.mark.parametrize("command", _COMMANDS)
def test_malformed_anchor_fails_every_command_and_creates_nothing(git_sandbox: GitSandbox, lock_facts: LockFacts,
                                                                  anchor: str, command: list[str]) -> None:
    """AC1: status 2 with the token grammar as remedy; no file, artifact home or lock record appears."""
    del lock_facts
    command_project(git_sandbox, {"version.txt": version_txt(anchor, "Notes\n")})
    before = snapshot(git_sandbox.home)
    run = run_command(git_sandbox, command)
    assert (run.status, run.out) == (_INVALID, "")
    assert f"Invalid version {anchor!r}: expected MAJOR.MINOR.PATCH" in run.err
    assert snapshot(git_sandbox.home) == before


def test_crlf_anchor_keeps_title_notes_and_line_endings(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """AC1 and AC2: `version` reads the document; `set` replaces only the token bytes."""
    del lock_facts
    root = command_project(git_sandbox, {"version.txt": version_txt("0.13.0-SNAPSHOT -- Title", "Notes\n\nMore\n", newline="\r\n", bom=True)})
    shown = run_command(git_sandbox, ["version"])
    assert (shown.status, shown.out) == (0, "0.13.0-SNAPSHOT\nTitle\n\nNotes\n\nMore\n")
    assert run_command(git_sandbox, _SET).status == 0
    assert (root / "version.txt").read_bytes() == version_txt("0.14.0 -- Title", "Notes\n\nMore\n", newline="\r\n", bom=True)


def _root_pairs(version: str) -> dict[str, bytes]:
    """A CRLF project whose root holds a uv editable pair and an npm pair beside the anchor."""
    return {
        "version.txt": version_txt(f"{version} -- Title", "Notes\n", newline="\r\n"),
        "pyproject.toml": pyproject_toml(version, layout="editable", newline="\r\n"),
        "uv.lock": crlf(uv_lock(version, layout="editable")),
        "package.json": crlf(package_json(version, private=True)),
        "package-lock.json": crlf(package_lock(version)),
    }


def _every_adapter(version: str) -> dict[str, bytes]:
    """A CRLF project during the snapshot of `version`, with every adapter: anchor, Python, npm, Maven and a pattern source.

    The pattern source owns a POM property the Maven adapter does not, so two
    adapters' disjoint fields of `pom.xml` compose into one new content.
    """
    snapshot_version = f"{version}-SNAPSHOT"
    pom = pom_xml(gav(DEMO_GROUP, "demo-root", snapshot_version), f"<properties><app.version>{snapshot_version}</app.version></properties>")
    return {
        "version.txt": version_txt(f"{snapshot_version} -- Title", "Notes\n", newline="\r\n"),
        "pyproject.toml": pyproject_toml(version, newline="\r\n"),
        "package.json": crlf(package_json(version, private=True)),
        "pom.xml": crlf(pom),
    }


_PROPERTY_INI = "[source:app-property]\nfile = pom.xml\npattern = <app.version>(.+)</app.version>\nform = snapshot\n"


@pytest.mark.parametrize(("files", "ini", "target"), [
    (_root_pairs, "", "0.14.0"),
    (_every_adapter, _PROPERTY_INI, "0.14.0-SNAPSHOT"),
], ids=["root-python-and-npm-pairs", "every-adapter"])
def test_crlf_project_changes_every_source_in_one_set(git_sandbox: GitSandbox, lock_facts: LockFacts,
                                                      files: Callable[[str], dict[str, bytes]], ini: str, target: str) -> None:
    """AC4, AC5, AC7 and AC8: the four root files, or every adapter's source, follow; only owned bytes change.

    Each source is compared with its builder at the new version, byte for
    byte, and the artifact home keeps only its ignore file: no lock record
    or evidence remains. The other acceptance rows compare whole trees.
    """
    del lock_facts
    root = command_project(git_sandbox, files("0.13.0"), ini)
    run = run_command(git_sandbox, ["versions", "set", target])
    assert (run.status, run.err) == (0, "")
    old = target.replace("0.14.0", "0.13.0")
    assert run.out.splitlines()[-1] == f"version.txt\tversion\t{old}\t{target}"
    expected = files("0.14.0")
    assert source_bytes(root, list(expected)) == expected
    assert [path.name for path in (root / ".reviews").iterdir()] == [".gitignore"]


def test_combined_crlf_project_at_the_new_version_checks_ok(git_sandbox: GitSandbox) -> None:
    """AC7 and AC10: after that transition, every participating source holds its expected value."""
    command_project(git_sandbox, _every_adapter("0.14.0"), _PROPERTY_INI)
    check = run_command(git_sandbox, ["versions", "check"])
    assert (check.status, check.err) == (0, "")
    rows = [line.split("\t") for line in check.out.splitlines()]
    assert {row[0] for row in rows} == set(_every_adapter("0.14.0"))
    assert all(row[-1] == "ok" for row in rows)


def test_tool_only_pair_and_undeclared_candidate_never_participate(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """AC4, AC5 and AC10: both are listed as not participating; `check` and `set` ignore them."""
    del lock_facts
    tool_only = {"pyproject.toml": b"[tool.ruff]\nline-length = 100\n", "uv.lock": uv_lock()}
    candidate = {"frontend/package.json": package_json("9.9.9", name="frontend")}
    root = command_project(git_sandbox, {"version.txt": version_txt("0.14.0"), **tool_only, **candidate})
    listed = run_command(git_sandbox, ["versions", "list"])
    assert listed.out.splitlines()[1:] == [
        "version.txt\tversion\tanchor\tsnapshot\t0.14.0\tparticipating",
        "pyproject.toml\tproject.version\tpython\t-\t-\tnot-participating tool-only",
        "uv.lock\tpackage.version\tpython\t-\t-\tnot-participating tool-only",
        "frontend/package.json\tversion\tnpm\t-\t-\tnot-participating undeclared",
    ]
    check = run_command(git_sandbox, ["versions", "check"])
    assert (check.status, check.out) == (0, "version.txt\tversion\tsnapshot\t0.14.0\t0.14.0\tok\n")
    changed = run_command(git_sandbox, ["versions", "set", "0.15.0"])
    assert (changed.status, changed.out) == (0, "version.txt\tversion\t0.14.0\t0.15.0\n")
    assert source_bytes(root, [*tool_only, *candidate]) == {**tool_only, **candidate}


_REFUSED: dict[str, tuple[dict[str, bytes], str, str]] = {
    "component-is-reactor-module": ({
        "version.txt": version_txt(_SNAPSHOT), "pom.xml": pom_xml(_ROOT_POM, "<modules><module>frontend</module></modules>"),
        "frontend/pom.xml": pom_xml(_PARENT, gav(None, "frontend", _SNAPSHOT)),
    }, "[component:frontend]\nroot = frontend\n", "pom.xml field project/version is claimed twice"),
    "dynamic-version": ({"version.txt": version_txt("0.13.0"), "pyproject.toml": b'[project]\nname = "demo-app"\ndynamic = ["version"]\n'},
                        "", "[project] lists version in dynamic"),
    "pattern-twice": ({"version.txt": version_txt(_SNAPSHOT), "cicd/config/.env": lines_file([f"APP_SERVICE_VERSION={_SNAPSHOT}"] * 2)},
                      PATTERN_INI, "matches more than once"),
    "pattern-none": ({"version.txt": version_txt(_SNAPSHOT), "cicd/config/.env": lines_file(["OTHER=1"])}, PATTERN_INI, "matches nothing"),
    "pattern-empty-group": ({"version.txt": version_txt(_SNAPSHOT), "cicd/config/.env": lines_file(["APP_SERVICE_VERSION="])},
                            PATTERN_INI.replace("(.+)$", "(.+)?$"), "captures an empty value"),
    "maven-property-dependency": ({
        "version.txt": version_txt(_SNAPSHOT),
        "pom.xml": pom_xml(_ROOT_POM, "<packaging>pom</packaging>", "<modules><module>core</module><module>app</module></modules>"),
        "core/pom.xml": pom_xml(_PARENT, gav(None, "core")),
        "app/pom.xml": pom_xml(_PARENT, gav(None, "app"), f"<dependencies><dependency>{gav(DEMO_GROUP, 'core', '${revision}')}</dependency></dependencies>"),
    }, "", "version: '${revision}' is a Maven property expression"),
    "external-parent-without-version": ({
        "version.txt": version_txt(_SNAPSHOT),
        "pom.xml": pom_xml(f"<parent>{gav('org.springframework.boot', 'spring-boot-starter-parent', '3.3.4')}</parent>", gav(DEMO_GROUP, "demo-root")),
    }, "", "has no version of its own"),
    "npm-workspaces": ({"version.txt": version_txt("0.13.0"), "package.json": package_json(workspaces=["packages/*"])},
                       "", "npm workspaces are unsupported"),
    "npm-lock-format-1": ({"version.txt": version_txt("0.13.0"), "package.json": package_json(), "package-lock.json": package_lock(lockfile=1)},
                          "", "lockfileVersion 1 is unsupported"),
    "uv-unregistered-schema": ({"version.txt": version_txt("0.13.0"), "pyproject.toml": pyproject_toml(), "uv.lock": uv_lock(revision=99)},
                               "", "unsupported uv lock schema"),
    "uv-workspace-without-lock": ({"version.txt": version_txt("0.13.0"),
                                   "pyproject.toml": pyproject_toml(extra='\n[tool.uv.workspace]\nmembers = ["packages/*"]\n')},
                                  "", "uv workspaces are unsupported"),
    "python-component-link": ({
        "version.txt": version_txt("0.13.0"), "web/pyproject.toml": pyproject_toml(name="web"),
        "api/pyproject.toml": b'[project]\nname = "api"\nversion = "0.13.0"\ndependencies = ["web @ file:../web"]\n',
    }, "[component:api]\nroot = api\n[component:web]\nroot = web\n", "links [component:api] to [component:web]"),
    "tool-only-workspace-member": ({
        "version.txt": version_txt("0.13.0"), "pyproject.toml": b'[tool.uv.workspace]\nmembers = ["*"]\n',
        "api/pyproject.toml": pyproject_toml(name="api"),
    }, "[component:api]\nroot = api\n", "[tool.uv.workspace] members include [component:api]"),
    "pattern-overlaps-pyproject": ({"version.txt": version_txt("0.13.0"), "pyproject.toml": pyproject_toml()},
                                   '[source:pyver]\nfile = pyproject.toml\npattern = ^version = "(.+)"$\nform = core\n', "overlap"),
    "two-patterns-same-bytes": ({"version.txt": version_txt(_SNAPSHOT), "cicd/config/.env": lines_file([f"APP_SERVICE_VERSION={_SNAPSHOT}"])},
                                PATTERN_INI + PATTERN_INI.replace("cicd-env", "copy"), "overlap"),
}


@pytest.mark.parametrize("case", list(_REFUSED))
@pytest.mark.parametrize("command", [["versions", "list"], ["versions", "check"], _SET])
def test_refused_arrangements_fail_before_any_write(git_sandbox: GitSandbox, lock_facts: LockFacts, case: str, command: list[str]) -> None:
    """AC4, AC5, AC6, AC8 and AC9: status 2 naming the source and the limitation; every byte stays."""
    del lock_facts
    files, ini, message = _REFUSED[case]
    command_project(git_sandbox, files, ini)
    before = snapshot(git_sandbox.home)
    run = run_command(git_sandbox, command)
    assert (run.status, run.out) == (_INVALID, "")
    assert message in run.err
    assert snapshot(git_sandbox.home) == before


def test_internal_project_version_stays_while_reactor_versions_follow(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """AC9: root, inherited modules' parents and dependency management change; `${project.version}` stays."""
    del lock_facts
    fixture = RESTORATION_FIXTURES["maven-inherited"]
    root = command_project(git_sandbox, fixture.files)
    run = run_command(git_sandbox, ["versions", "set", "0.14.0-SNAPSHOT"])
    assert (run.status, len(run.out.splitlines())) == (0, 5)
    expected = {name: content.replace(b"0.13.0-SNAPSHOT", b"0.14.0-SNAPSHOT") for name, content in fixture.files.items()}
    assert source_bytes(root, list(expected)) == expected
    assert b"${project.version}" in expected["app/pom.xml"]


def test_forms_follow_the_anchor_and_release_only_never_goes_down(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """AC7: npm keeps the core, Maven the suffix; a lower target is refused before any write; `check` shows drift."""
    del lock_facts
    root = command_project(git_sandbox, {"version.txt": version_txt("0.0.24"), "package.json": package_json("0.0.24"),
                                         "pom.xml": pom_xml(gav(DEMO_GROUP, "demo-root", "0.0.24"))})
    assert run_command(git_sandbox, ["versions", "set", "0.0.25-SNAPSHOT"]).status == 0
    assert source_bytes(root, ["package.json", "pom.xml"]) == {
        "package.json": package_json("0.0.25"), "pom.xml": pom_xml(gav(DEMO_GROUP, "demo-root", "0.0.25-SNAPSHOT"))}
    before = snapshot(git_sandbox.home)
    refused = run_command(git_sandbox, ["versions", "set", "0.0.24"])
    assert refused.status == _INVALID
    assert "package.json version: release-only value 0.0.25 is higher than the target 0.0.24" in refused.err
    assert snapshot(git_sandbox.home) == before
    (root / "version.txt").write_bytes(version_txt("0.0.24"))
    check = run_command(git_sandbox, ["versions", "check"])
    assert check.status == _FAILED
    assert "package.json\tversion\trelease-only\t0.0.25\t0.0.24\tdrift\n" in check.out


@pytest.mark.parametrize("record", _RECORDS, ids=[record["id"] for record in _RECORDS])
def test_recorded_lock_evidence_replays_through_versions_set(git_sandbox: GitSandbox, lock_facts: LockFacts, record: dict[str, Any]) -> None:
    """AC8: from each recorded "before" pair, `versions set` writes exactly the recorded edited pair."""
    del lock_facts
    files = {name: pair["before"].encode("utf-8") for name, pair in record["files"].items()}
    root = command_project(git_sandbox, {"version.txt": version_txt(str(record["before_version"])), **files})
    run = run_command(git_sandbox, ["versions", "set", str(record["target_version"])])
    assert (run.status, run.err) == (0, "")
    edited = {name: pair["edited"].encode("utf-8") for name, pair in record["files"].items()}
    assert source_bytes(root, list(edited)) == edited


def test_injected_failure_at_the_third_of_five_writes_restores_the_first_two(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """AC11: both replaced files are restored and verified, the evidence is deleted, status 1."""
    fixture = RESTORATION_FIXTURES["combined"]
    root = command_project(git_sandbox, fixture.files, fixture.ini)
    before = snapshot(git_sandbox.home)
    faults = Faults(root / ".reviews", fail_write=2)
    run = run_command(git_sandbox, _SET, handlers=version_registry(faults.ports(lock_facts.probe)))
    assert (run.status, run.out) == (_FAILED, "")
    assert [path.name for path in faults.sources] == [".env", "package.json", "pom.xml", "package.json", ".env"]
    assert "every replaced source was restored and verified (2 files)" in run.err
    assert run.err.endswith("versions set 0.14.0 failed: restored\n")
    assert _added(before, snapshot(git_sandbox.home)) == {"A/.reviews": None, "A/.reviews/.gitignore": b"*\n"}


def test_failed_restoration_names_each_source_and_its_retained_copy(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """AC11: status 3; each unrestored source keeps the new bytes, its original stays in the evidence."""
    fixture = RESTORATION_FIXTURES["combined"]
    root = command_project(git_sandbox, fixture.files, fixture.ini)
    originals = {root / name: content for name, content in fixture.files.items()}

    def fails(path: Path, content: bytes) -> bool:
        return originals.get(path) == content

    faults = Faults(root / ".reviews", fail_write=2, fail_when=fails)
    run = run_command(git_sandbox, _SET, handlers=version_registry(faults.ports(lock_facts.probe)))
    assert (run.status, run.out) == (_INCOMPLETE, "")
    retained = dict(re.findall(r"^(.+) was not restored; its original is retained at (.+)$", run.err, re.MULTILINE))
    assert sorted(retained) == sorted(str(path) for path in faults.sources[:2])
    assert {source: Path(copy).read_bytes() for source, copy in retained.items()} == {source: originals[Path(source)] for source in retained}
    manifest = EvidenceManifest.decode((root / ".reviews" / EVIDENCE_NAME / "manifest.json").read_bytes())
    assert manifest.state is EvidenceState.RESTORATION_INCOMPLETE


@dataclass
class _RecordingLocks:
    """A lock factory recording each acquisition and release of the production lock."""

    events: list[str] = field(default_factory=list[str])

    def __call__(self, artifacts: PreparedArtifacts, *, probe: Callable[[ProcessIdentity], ProcessState]) -> TransitionLock:
        """Wrap a production lock for these artifacts."""
        return _RecordedLock(OperationLock(artifacts, probe=probe), self.events)


@dataclass
class _RecordedLock:
    """One production lock whose acquisition and release are recorded."""

    lock: OperationLock
    events: list[str]

    def acquire(self) -> TransitionLock:
        """Acquire, then record."""
        self.lock.acquire()
        self.events.append("acquire")
        return self

    def release(self) -> None:
        """Release, then record."""
        self.lock.release()
        self.events.append("release")


def test_same_target_takes_and_releases_the_lock_and_writes_nothing(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """AC11: `unchanged`, no source write, no lock record or evidence left behind."""
    root = command_project(git_sandbox, {"version.txt": version_txt("0.14.0"), "package.json": package_json("0.14.0")})
    before = snapshot(git_sandbox.home)
    faults, locks = Faults(root / ".reviews"), _RecordingLocks()
    ports = replace(faults.ports(lock_facts.probe), lock_factory=locks)
    run = run_command(git_sandbox, _SET, handlers=version_registry(ports))
    assert (run.status, run.out, run.err) == (0, "unchanged\n", "")
    assert (locks.events, faults.sources, faults.evidence) == (["acquire", "release"], [], [])
    assert _added(before, snapshot(git_sandbox.home)) == {"A/.reviews": None, "A/.reviews/.gitignore": b"*\n"}


def test_held_lock_fails_naming_its_owner(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """AC11: another live operation keeps the project; status 1, nothing written."""
    root = command_project(git_sandbox, {"version.txt": version_txt("0.13.0"), "package.json": package_json()})
    hold(root, lock_facts, 77)
    before = snapshot(git_sandbox.home)
    run = run_command(git_sandbox, _SET, handlers=version_registry(Faults(root / ".reviews").ports(lock_facts.probe)))
    assert (run.status, run.out) == (_FAILED, "")
    assert "another operation holds this project" in run.err
    assert "pid=77" in run.err
    assert snapshot(git_sandbox.home) == before


@pytest.mark.parametrize("version", ["0.13.0", "0.14.0"])
def test_leftover_writing_evidence_stops_set_and_check_warns(git_sandbox: GitSandbox, lock_facts: LockFacts, version: str) -> None:
    """AC11: killed before or after its last replacement, a `set` leaves evidence that stops the next one, never `unchanged`."""
    del lock_facts
    root = command_project(git_sandbox, {"version.txt": version_txt(version), "package.json": package_json(version)})
    evidence = declare_evidence(root / ".reviews", EVIDENCE_NAME, _manifest(EvidenceState.WRITING))
    before = snapshot(git_sandbox.home)
    stopped = run_command(git_sandbox, _SET)
    assert (stopped.status, stopped.out) == (_INVALID, "")
    assert f"{evidence}: interrupted version-transition evidence" in stopped.err
    check = run_command(git_sandbox, ["versions", "check"])
    assert check.err.startswith(f"warning: leftover interrupted version-transition evidence {evidence}")
    assert snapshot(git_sandbox.home) == before


def test_cleanup_failure_keeps_the_new_versions_and_the_next_set_removes_the_residue(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """AC11: status 1 states the versions are applied and names the residue; the next `set` removes it."""
    root = command_project(git_sandbox, {"version.txt": version_txt("0.13.0"), "package.json": package_json()})
    faults = Faults(root / ".reviews", fail_remove="original.1")
    run = run_command(git_sandbox, _SET, handlers=version_registry(faults.ports(lock_facts.probe)))
    assert (run.status, run.out) == (_FAILED, "package.json\tversion\t0.13.0\t0.14.0\nversion.txt\tversion\t0.13.0\t0.14.0\n")
    assert "the new versions are applied" in run.err
    assert source_bytes(root, ["version.txt", "package.json"]) == {"version.txt": version_txt("0.14.0"), "package.json": package_json("0.14.0")}
    rerun = run_command(git_sandbox, _SET)
    assert (rerun.status, rerun.out) == (0, "unchanged\n")
    assert f"removed completed standalone residue {root / '.reviews' / EVIDENCE_NAME}" in rerun.err
    assert not (root / ".reviews" / EVIDENCE_NAME).exists()


def test_lifecycle_lock_of_another_project_fails_before_any_read(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """AC11: item 5's in-process call with a lock taken for project B cannot run in project A."""
    root = command_project(git_sandbox, {"version.txt": version_txt("0.13.0")})
    inputs = version_inputs(git_sandbox, root)
    other = hold(git_sandbox.home / "B", lock_facts, lock_facts.pid)
    before, views = snapshot(root), ViewLog()
    ports = replace(Faults(inputs.artifacts.home).ports(lock_facts.probe), view=views)
    with pytest.raises(TransitionError, match="the lifecycle lock cannot be used for this project") as caught:
        set_versions(inputs, TARGET, lifecycle=LifecycleOwnership(other, "release-1"), ports=ports)
    assert (caught.value.exit_code, views.views) == (_FAILED, [])
    assert snapshot(root) == before


@pytest.mark.parametrize("ini", ["[source:python]\nform = snapshot\n", "[source:npm]\nunknown = 1\n"])
@pytest.mark.parametrize("command", [*_COMMANDS, ["versions", "range"]])
def test_configuration_failures_stop_every_command(git_sandbox: GitSandbox, ini: str, command: list[str]) -> None:
    """AC12: an invalid form or an unknown key fails preflight, even for `version`; nothing is written."""
    command_project(git_sandbox, {"version.txt": version_txt("0.14.0")}, ini)
    tagged_history(git_sandbox, 1, {})
    before = snapshot(git_sandbox.home)
    run = run_command(git_sandbox, command)
    assert (run.status, run.out) == (_INVALID, "")
    assert run.err.startswith("Release preflight failed: ")
    assert snapshot(git_sandbox.home) == before


_LAUNCHER_PROJECT = {"version.txt": version_txt("0.13.0 -- Title", "Notes\n"), "package.json": package_json("0.12.0")}
_LAUNCHER_CASES = [
    (["version"], False, 0, b"0.13.0\nTitle\n\nNotes\n", ""),
    (["versions", "list"], False, 0, b"path\tfield\tadapter\tform\tvalue\tstatus\n"
     b"version.txt\tversion\tanchor\tsnapshot\t0.13.0\tparticipating\npackage.json\tversion\tnpm\trelease-only\t0.12.0\tparticipating\n", ""),
    (["versions", "check"], False, _FAILED, b"version.txt\tversion\tsnapshot\t0.13.0\t0.13.0\tok\n"
     b"package.json\tversion\trelease-only\t0.12.0\t0.13.0\tdrift\n", "versions check: 1 of 2 sources drift"),
    (_SET, False, 0, b"package.json\tversion\t0.12.0\t0.14.0\nversion.txt\tversion\t0.13.0\t0.14.0\n", ""),
    (_SET, True, _INCOMPLETE, b"", "versions set 0.14.0 failed: restoration incomplete"),
    (["versions", "range"], False, 0, b"target=HEAD\nbaseline=v0.12.0\nrange=v0.12.0..HEAD\ncommits=1\n", ""),
    (["versions", "range", "v9.9.9"], False, _INVALID, b"", "tag v9.9.9 does not exist"),
]


@pytest.mark.parametrize(("command", "faulty", "status", "stdout", "stderr"), _LAUNCHER_CASES)
def test_each_command_and_status_through_the_launcher(*, git_sandbox: GitSandbox, lock_facts: LockFacts,  # noqa: PLR0913 - case table
                                                      launcher_tooling: ToolingSimulation,
                                                      command: list[str], faulty: bool, status: int, stdout: bytes, stderr: str) -> None:
    """Production bootstrap, readiness and rendering carry each command's stdout and each public status (Q09)."""
    root = command_project(git_sandbox, _LAUNCHER_PROJECT)
    tagged_history(git_sandbox, 2, {"v0.12.0": (1, annotation())})
    registry: dict[str, cli.Handler] | None = None
    if faulty:
        original = _LAUNCHER_PROJECT["package.json"]
        faults = Faults(root / ".reviews", fail_write=1, fail_when=lambda path, content: path.name == "package.json" and content == original)
        registry = version_registry(faults.ports(lock_facts.probe))
    result = launcher_tooling.run([*command, "--project-root", str(root)], sandbox=git_sandbox, cwd=git_sandbox.home, handlers=registry)
    assert (result.returncode, result.stdout) == (status, stdout)
    assert stderr in result.stderr.decode("utf-8")
    assert b"\r" not in result.stdout + result.stderr


# eof
