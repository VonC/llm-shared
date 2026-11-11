"""Record uv and npm lock compatibility evidence with the real tools, outside pytest.

Step 5 of v0.14.0 version-sources (plan decisions Q03, Q04 and Q06). Started
by hand and never imported by a test, from the project root:

    python -m tests.unit.tools.release_workflow.lock_evidence_recorder --uv <uv.exe>
        --python <project python.exe> --npm <npm.cmd> --node-dir <Node 22.9.0 directory>
        --output <test_version_lock_evidence/lock_evidence.v1.json>

Each scenario runs in a new temporary directory outside the repository, which
is deleted when it ends. The recorder writes a virtual or editable
`pyproject.toml` at `0.13.0` and lets uv write the revision 5 lock with
`uv lock --offline --no-config --python <python>`. The revision 3 lock is that
lock with its revision line set to 3, as the record's provenance says (plan
decision Q04); the CRLF variant converts both files of the virtual revision 3
pair. The locked command `uv lock --locked --offline --no-config --python
<python>` then runs on the "before" pair (both files at `0.13.0`), on the
edited pair the production adapter plans for `0.14.0`, and on the
manifest-only control (the manifest edited, the lock left at `0.13.0`). Each
run records its exit code, its `error:` lines and the SHA-256 of both files
before and after it. Every `UV_*` variable is removed from the environment of
each run, so user configuration cannot change the result.

Step 6 adds the npm records (plan decisions Q05 and Q06). The recorder writes
a `private: true` root `package.json` at `0.0.24` and lets npm write its lock
with `npm install --package-lock-only --offline --lockfile-version <2|3>
--ignore-scripts --no-audit --no-fund`; the CRLF variant converts both files
of the format 3 pair. The frozen command `npm ci --offline --ignore-scripts
--no-audit --no-fund` runs on the "before" pair and on the edited pair the
production adapter plans for `0.0.25`; the lock-only check `npm install
--package-lock-only --offline --ignore-scripts --no-audit --no-fund` runs on
both pairs and on the manifest-only control, and records the lock's format
and root versions after it. `node_modules` is removed before each run. The
Node directory is prepended to the child `PATH` only, every `npm_config_*`
variable is removed, and npm's cache and user configuration point into the
scratch directory.

The JSON is written with sorted keys and LF endings; tool, interpreter and
scratch paths become placeholders, and the recorder refuses to write a file
that still holds a host path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from tests.unit.tools.release_workflow.version_support import (
    crlf,
    package_json,
    pair_edit,
    pyproject_toml,
)
from tools.release_workflow.sources import npm, python
from tools.release_workflow.sources.model import VersionToken

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

_BEFORE = "0.13.0"
_WRITTEN_REVISION = 5
_TARGET = VersionToken.parse("0.14.0")
_FILES = ("pyproject.toml", "uv.lock")
_GENERATE = ("lock", "--offline", "--no-config", "--python")
_LOCKED = ("lock", "--locked", "--offline", "--no-config", "--python")
_NPM_BEFORE = "0.0.24"
_NPM_TARGET = VersionToken.parse("0.0.25")
_NPM_FILES = ("package.json", "package-lock.json")
_NPM_FLAGS = ("--offline", "--ignore-scripts", "--no-audit", "--no-fund")
_FROZEN = ("ci", *_NPM_FLAGS)
_LOCK_ONLY = ("install", "--package-lock-only", *_NPM_FLAGS)
_NPM_RUNS = (("before", "frozen"), ("before", "lock-only"), ("edited", "frozen"), ("edited", "lock-only"), ("manifest-only", "lock-only"))
_NPM_NOTE = ("npm ci does not compare the root version, so it also accepts a manifest-only edit (planning probe of 2026-11-07); "
             "the frozen runs prove npm accepts both pairs, and the lock-only check is the run that notices a missed lock field "
             "(plan decision Q05)")
_HOST_PATH = re.compile(r"[A-Za-z]:[\\/]|[\\/](?:Users|home)[\\/]")
_ABOUT = ("Lock compatibility evidence of the python adapter with uv (v0.14.0 version-sources, Step 5) and of the npm adapter "
          "with npm (Step 6), written by tests/unit/tools/release_workflow/lock_evidence_recorder.py. The 'before' pair is a "
          "manifest and its lock both at before_version; the edited pair is the same files after the adapter's version-only edit "
          "to target_version; the manifest-only control edits the manifest alone. A run accepts a pair when it exits 0 and "
          "changes neither file. npm records add the lock-only check (plan decision Q05), whose rewrite of the control's lock "
          "shows npm notices a missed lock field.")


@dataclass(frozen=True)
class UvScenario:
    """One recorded combination of root layout, lock revision and line endings."""

    layout: str
    revision: int
    line_endings: str = "lf"

    def identifier(self, tool_version: str) -> str:
        """Name the record, such as `uv-0.13.4-v1r3-virtual-crlf`."""
        suffix = "-crlf" if self.line_endings == "crlf" else ""
        return f"uv-{tool_version}-v1r{self.revision}-{self.layout}{suffix}"


_SCENARIOS = (
    UvScenario("virtual", 5), UvScenario("editable", 5), UvScenario("virtual", 3), UvScenario("editable", 3),
    UvScenario("virtual", 3, "crlf"),
)


@dataclass(frozen=True)
class NpmScenario:
    """One recorded combination of lock format and line endings for a root package."""

    lock_format: int
    line_endings: str = "lf"

    def identifier(self, tool_version: str) -> str:
        """Name the record, such as `npm-10.8.3-lock3-root-crlf`."""
        suffix = "-crlf" if self.line_endings == "crlf" else ""
        return f"npm-{tool_version}-lock{self.lock_format}-root{suffix}"


_NPM_SCENARIOS = (NpmScenario(2), NpmScenario(3), NpmScenario(3, "crlf"))


@dataclass(frozen=True)
class UvTools:
    """The uv executable and the interpreter its lock commands target."""

    uv: Path
    python: Path

    def run(self, project: Path, arguments: Sequence[str]) -> subprocess.CompletedProcess[str]:
        """Run uv in the project with the interpreter as last argument."""
        return self._uv(project, [*arguments, str(self.python)])

    def build(self) -> str:
        """Return uv's version line, such as `uv 0.13.4 (... x86_64-pc-windows-msvc)`."""
        return self._uv(Path.cwd(), ["--version"]).stdout.strip()

    def _uv(self, cwd: Path, arguments: Sequence[str]) -> subprocess.CompletedProcess[str]:
        """Start uv without any `UV_*` variable and capture its output."""
        environment = {name: value for name, value in os.environ.items() if not name.upper().startswith("UV_")}
        return subprocess.run([str(self.uv), *arguments], cwd=cwd, env=environment, capture_output=True, text=True,  # noqa: S603
                              encoding="utf-8", errors="replace", check=False)

    def sanitized(self, text: str, project: Path) -> str:
        """Replace the scratch directory and tool paths with placeholders."""
        for path, placeholder in ((project, "<project>"), (self.python, "<python>"), (self.uv, "<uv>")):
            text = text.replace(str(path), placeholder)
        return text


@dataclass(frozen=True)
class NpmTools:
    """The npm launcher and the Node directory prepended to each run's `PATH`."""

    npm: Path
    node_dir: Path

    def run(self, scratch: Path, arguments: Sequence[str]) -> subprocess.CompletedProcess[str]:
        """Run npm in the scratch project, without `node_modules`, user configuration or a shared cache."""
        project = scratch / "project"
        shutil.rmtree(project / "node_modules", ignore_errors=True)
        environment = {name: value for name, value in os.environ.items() if not name.lower().startswith("npm_config_")}
        environment.update({"PATH": f"{self.node_dir}{os.pathsep}{os.environ.get('PATH', '')}",
                            "npm_config_cache": str(scratch / "npm-cache"), "npm_config_userconfig": str(scratch / "npmrc")})
        return subprocess.run([str(self.npm), *arguments], cwd=project, env=environment, capture_output=True, text=True,  # noqa: S603
                              encoding="utf-8", errors="replace", check=False)

    def build(self, scratch: Path) -> str:
        """Return npm's and Node's versions, such as `npm 10.8.3 on Node v22.9.0`."""
        node = subprocess.run([str(self.node_dir / "node.exe"), "--version"], capture_output=True, text=True, check=False)  # noqa: S603
        return f"npm {self.run(scratch, ['--version']).stdout.strip()} on Node {node.stdout.strip()}"

    def sanitized(self, text: str, scratch: Path) -> str:
        """Replace the scratch directory and tool paths with placeholders."""
        for path, placeholder in ((scratch, "<scratch>"), (self.npm, "<npm>"), (self.node_dir, "<node-dir>")):
            text = text.replace(str(path), placeholder)
        return text


def _digests(project: Path, names: Sequence[str]) -> dict[str, str]:
    """Hash the files of the pair as they are on disk."""
    return {name: hashlib.sha256((project / name).read_bytes()).hexdigest() for name in names}


def _write(project: Path, contents: Mapping[str, bytes]) -> None:
    """Write the files of a pair."""
    for name, content in contents.items():
        (project / name).write_bytes(content)


def _run(tools: UvTools, project: Path, pair: str, contents: Mapping[str, bytes]) -> dict[str, object]:
    """Write a pair, run the locked command on it and record the outcome and both files' hashes."""
    _write(project, contents)
    before = _digests(project, _FILES)
    completed = tools.run(project, _LOCKED)
    errors = [tools.sanitized(line.strip(), project) for line in completed.stderr.splitlines() if line.strip().startswith("error:")]
    return {"pair": pair, "exit_code": completed.returncode, "errors": errors, "sha256_before": before, "sha256_after": _digests(project, _FILES)}


def _relabel(lock: bytes, revision: int) -> bytes:
    """Set the revision line of a uv-written lock, which must hold exactly one."""
    line = f"\nrevision = {_WRITTEN_REVISION}\n".encode()
    if lock.count(line) != 1:
        msg = f"the generated uv.lock does not hold exactly one 'revision = {_WRITTEN_REVISION}' line"
        raise SystemExit(msg)
    return lock.replace(line, f"\nrevision = {revision}\n".encode())


def _before_pair(tools: UvTools, project: Path, scenario: UvScenario) -> tuple[dict[str, bytes], str]:
    """Write the manifest, let uv write its lock, derive the scenario's pair and state its provenance."""
    manifest = pyproject_toml(_BEFORE, layout=scenario.layout)
    (project / "pyproject.toml").write_bytes(manifest)
    generated = tools.run(project, _GENERATE)
    if generated.returncode != 0:
        msg = f"uv lock failed for the {scenario.layout} root: {tools.sanitized(generated.stderr, project)}"
        raise SystemExit(msg)
    lock = (project / "uv.lock").read_bytes()
    provenance = "pyproject.toml written by the recorder; uv.lock written by <uv> lock --offline --no-config --python <python>"
    if scenario.revision != _WRITTEN_REVISION:
        lock = _relabel(lock, scenario.revision)
        provenance += f"; its revision line then set to {scenario.revision} (plan decision Q04)"
    if scenario.line_endings == "crlf":
        manifest, lock = crlf(manifest), crlf(lock)
        provenance += "; both files then converted from LF to CRLF"
    return {"pyproject.toml": manifest, "uv.lock": lock}, provenance


def record(tools: UvTools, scenario: UvScenario, build: str) -> dict[str, object]:
    """Record one uv scenario in a new temporary directory outside the repository."""
    tool_version = build.split()[1]
    with tempfile.TemporaryDirectory(prefix="uv-lock-evidence-") as scratch:
        project = Path(scratch)
        before, provenance = _before_pair(tools, project, scenario)
        runs = [_run(tools, project, "before", before)]
        _write(project, before)
        edited = pair_edit(python.ADAPTER, project, _TARGET)
        runs.append(_run(tools, project, "edited", edited))
        runs.append(_run(tools, project, "manifest-only", {"pyproject.toml": edited["pyproject.toml"], "uv.lock": before["uv.lock"]}))
    schema = tomllib.loads(before["uv.lock"].decode("utf-8"))
    return {
        "id": scenario.identifier(tool_version), "tool": "uv", "tool_version": tool_version, "tool_build": build,
        "lock_schema": {"version": schema["version"], "revision": schema["revision"]},
        "layout": scenario.layout, "line_endings": scenario.line_endings, "provenance": provenance,
        "generated_by": ["<uv>", *_GENERATE, "<python>"], "command": ["<uv>", *_LOCKED, "<python>"],
        "before_version": _BEFORE, "target_version": str(_TARGET),
        "files": {name: {"before": before[name].decode("utf-8"), "edited": edited[name].decode("utf-8")} for name in _FILES},
        "runs": runs,
    }


def _npm_run(tools: NpmTools, scratch: Path, pair: tuple[str, str], contents: Mapping[str, bytes]) -> dict[str, object]:
    """Write a pair, run the frozen command or the lock-only check, and record the outcome, hashes and lock root fields."""
    project = scratch / "project"
    _write(project, contents)
    before = _digests(project, _NPM_FILES)
    completed = tools.run(scratch, _FROZEN if pair[1] == "frozen" else _LOCK_ONLY)
    errors = [tools.sanitized(line.strip(), scratch) for line in completed.stderr.splitlines() if line.startswith(("npm error", "npm ERR!"))]
    lock = json.loads((project / "package-lock.json").read_bytes())
    lock_after = {"lockfileVersion": lock.get("lockfileVersion"), "version": lock.get("version"),
                  "packages_root_version": lock.get("packages", {}).get("", {}).get("version")}
    return {"pair": pair[0], "check": pair[1], "exit_code": completed.returncode, "errors": errors, "sha256_before": before,
            "sha256_after": _digests(project, _NPM_FILES), "lock_after": lock_after}


def _npm_before_pair(tools: NpmTools, scratch: Path, scenario: NpmScenario) -> tuple[dict[str, bytes], list[str], str]:
    """Write the manifest, let npm write its lock in the scenario's format, and state the pair's provenance."""
    project = scratch / "project"
    project.mkdir()
    manifest = package_json(_NPM_BEFORE, private=True)
    (project / "package.json").write_bytes(manifest)
    command = ["install", "--package-lock-only", "--offline", "--lockfile-version", str(scenario.lock_format), *_NPM_FLAGS[1:]]
    generated = tools.run(scratch, command)
    if generated.returncode != 0:
        msg = f"npm could not write the format {scenario.lock_format} lock: {tools.sanitized(generated.stderr, scratch)}"
        raise SystemExit(msg)
    lock = (project / "package-lock.json").read_bytes()
    provenance = "package.json written by the recorder; package-lock.json written by <npm> " + " ".join(command)
    if scenario.line_endings == "crlf":
        manifest, lock = crlf(manifest), crlf(lock)
        provenance += "; both files then converted from LF to CRLF"
    return {"package.json": manifest, "package-lock.json": lock}, ["<npm>", *command], provenance


def record_npm(tools: NpmTools, scenario: NpmScenario) -> dict[str, object]:
    """Record one npm scenario in a new temporary directory outside the repository."""
    with tempfile.TemporaryDirectory(prefix="npm-lock-evidence-") as directory:
        scratch = Path(directory).resolve()
        before, generated_by, provenance = _npm_before_pair(tools, scratch, scenario)
        build = tools.build(scratch)
        _write(scratch / "project", before)
        edited = pair_edit(npm.ADAPTER, scratch / "project", _NPM_TARGET)
        pairs = {"before": before, "edited": edited,
                 "manifest-only": {"package.json": edited["package.json"], "package-lock.json": before["package-lock.json"]}}
        runs = [_npm_run(tools, scratch, run, pairs[run[0]]) for run in _NPM_RUNS]
    tool_version = build.split()[1]
    return {
        "id": scenario.identifier(tool_version), "tool": "npm", "tool_version": tool_version, "tool_build": build,
        "lock_format": scenario.lock_format, "layout": "root", "line_endings": scenario.line_endings, "provenance": provenance,
        "note": _NPM_NOTE,
        "generated_by": generated_by, "command": ["<npm>", *_FROZEN], "lock_only_command": ["<npm>", *_LOCK_ONLY],
        "before_version": _NPM_BEFORE, "target_version": str(_NPM_TARGET),
        "files": {name: {"before": before[name].decode("utf-8"), "edited": edited[name].decode("utf-8")} for name in _NPM_FILES},
        "runs": runs,
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Record every scenario and write the evidence file."""
    parser = argparse.ArgumentParser(description="Record uv and npm lock compatibility evidence for the python and npm adapters.")
    parser.add_argument("--uv", type=Path, required=True, help="uv executable, such as the project venv's uv.exe")
    parser.add_argument("--python", type=Path, required=True, help="the project interpreter the locks target")
    parser.add_argument("--npm", type=Path, required=True, help="npm launcher, such as npm.cmd of the Node 22.9.0 directory")
    parser.add_argument("--node-dir", type=Path, required=True, help="the Node 22.9.0 directory prepended to each npm run's PATH")
    parser.add_argument("--output", type=Path, required=True, help="the lock_evidence.v1.json file to write")
    arguments = parser.parse_args(argv)
    tools = UvTools(Path(arguments.uv).resolve(), Path(arguments.python).resolve())
    npm_tools = NpmTools(Path(arguments.npm).resolve(), Path(arguments.node_dir).resolve())
    build = tools.build()
    records = [record(tools, scenario, build) for scenario in _SCENARIOS]
    records += [record_npm(npm_tools, scenario) for scenario in _NPM_SCENARIOS]
    text = json.dumps({"format": 1, "about": _ABOUT, "records": records}, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if _HOST_PATH.search(text) is not None:
        msg = "the evidence still holds a host path; nothing was written"
        raise SystemExit(msg)
    output = Path(arguments.output)
    output.write_bytes(text.encode("utf-8"))
    sys.stdout.write(f"{len(_SCENARIOS)} uv and {len(_NPM_SCENARIOS)} npm records written to {output}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# eof
