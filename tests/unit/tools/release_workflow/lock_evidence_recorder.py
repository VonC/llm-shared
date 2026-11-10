"""Record uv lock compatibility evidence with the real tool, outside pytest.

Step 5 of v0.14.0 version-sources (plan decisions Q03, Q04 and Q06). Started
by hand and never imported by a test, from the project root:

    python -m tests.unit.tools.release_workflow.lock_evidence_recorder --uv <uv.exe>
        --python <project python.exe> --output <test_version_lock_evidence/lock_evidence.v1.json>

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
before and after it.

Every `UV_*` variable is removed from the environment of each run, so user
configuration cannot change the result. The JSON is written with sorted keys
and LF endings; the tool and interpreter paths become `<uv>` and `<python>`,
and the recorder refuses to write a file that still holds a host path. Step 6
adds the npm records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from tests.unit.tools.release_workflow.version_support import (
    pyproject_toml,
    python_pair_edit,
)
from tools.release_workflow.sources.model import VersionToken

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

_BEFORE = "0.13.0"
_WRITTEN_REVISION = 5
_TARGET = VersionToken.parse("0.14.0")
_FILES = ("pyproject.toml", "uv.lock")
_GENERATE = ("lock", "--offline", "--no-config", "--python")
_LOCKED = ("lock", "--locked", "--offline", "--no-config", "--python")
_HOST_PATH = re.compile(r"[A-Za-z]:[\\/]|[\\/](?:Users|home)[\\/]")
_ABOUT = ("uv lock compatibility evidence of the python adapter (v0.14.0 version-sources, Step 5), written by "
          "tests/unit/tools/release_workflow/lock_evidence_recorder.py. The 'before' pair is a pyproject.toml and its "
          "uv.lock both at before_version; the edited pair is the same files after the adapter's version-only edit to "
          "target_version; the manifest-only control edits the manifest alone. A run accepts a pair when it exits 0 "
          "and changes neither file.")


@dataclass(frozen=True)
class Scenario:
    """One recorded combination of root layout, lock revision and line endings."""

    layout: str
    revision: int
    line_endings: str = "lf"

    def identifier(self, tool_version: str) -> str:
        """Name the record, such as `uv-0.13.4-v1r3-virtual-crlf`."""
        suffix = "-crlf" if self.line_endings == "crlf" else ""
        return f"uv-{tool_version}-v1r{self.revision}-{self.layout}{suffix}"


_SCENARIOS = (
    Scenario("virtual", 5), Scenario("editable", 5), Scenario("virtual", 3), Scenario("editable", 3), Scenario("virtual", 3, "crlf"),
)


@dataclass(frozen=True)
class Tools:
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


def _digests(project: Path) -> dict[str, str]:
    """Hash both files of the pair as they are on disk."""
    return {name: hashlib.sha256((project / name).read_bytes()).hexdigest() for name in _FILES}


def _write(project: Path, contents: Mapping[str, bytes]) -> None:
    """Write both files of a pair."""
    for name in _FILES:
        (project / name).write_bytes(contents[name])


def _run(tools: Tools, project: Path, pair: str, contents: Mapping[str, bytes]) -> dict[str, object]:
    """Write a pair, run the locked command on it and record the outcome and both files' hashes."""
    _write(project, contents)
    before = _digests(project)
    completed = tools.run(project, _LOCKED)
    errors = [tools.sanitized(line.strip(), project) for line in completed.stderr.splitlines() if line.strip().startswith("error:")]
    return {"pair": pair, "exit_code": completed.returncode, "errors": errors, "sha256_before": before, "sha256_after": _digests(project)}


def _relabel(lock: bytes, revision: int) -> bytes:
    """Set the revision line of a uv-written lock, which must hold exactly one."""
    line = f"\nrevision = {_WRITTEN_REVISION}\n".encode()
    if lock.count(line) != 1:
        msg = f"the generated uv.lock does not hold exactly one 'revision = {_WRITTEN_REVISION}' line"
        raise SystemExit(msg)
    return lock.replace(line, f"\nrevision = {revision}\n".encode())


def _before_pair(tools: Tools, project: Path, scenario: Scenario) -> tuple[dict[str, bytes], str]:
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
        manifest, lock = manifest.replace(b"\n", b"\r\n"), lock.replace(b"\n", b"\r\n")
        provenance += "; both files then converted from LF to CRLF"
    return {"pyproject.toml": manifest, "uv.lock": lock}, provenance


def record(tools: Tools, scenario: Scenario, build: str) -> dict[str, object]:
    """Record one scenario in a new temporary directory outside the repository."""
    tool_version = build.split()[1]
    with tempfile.TemporaryDirectory(prefix="uv-lock-evidence-") as scratch:
        project = Path(scratch)
        before, provenance = _before_pair(tools, project, scenario)
        runs = [_run(tools, project, "before", before)]
        _write(project, before)
        edited = python_pair_edit(project, _TARGET)
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


def main(argv: Sequence[str] | None = None) -> int:
    """Record every scenario and write the evidence file."""
    parser = argparse.ArgumentParser(description="Record uv lock compatibility evidence for the python adapter.")
    parser.add_argument("--uv", type=Path, required=True, help="uv executable, such as the project venv's uv.exe")
    parser.add_argument("--python", type=Path, required=True, help="the project interpreter the locks target")
    parser.add_argument("--output", type=Path, required=True, help="the lock_evidence.v1.json file to write")
    arguments = parser.parse_args(argv)
    tools = Tools(Path(arguments.uv).resolve(), Path(arguments.python).resolve())
    build = tools.build()
    data = {"format": 1, "about": _ABOUT, "records": [record(tools, scenario, build) for scenario in _SCENARIOS]}
    text = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if _HOST_PATH.search(text) is not None:
        msg = "the evidence still holds a host path; nothing was written"
        raise SystemExit(msg)
    output = Path(arguments.output)
    output.write_bytes(text.encode("utf-8"))
    sys.stdout.write(f"{len(_SCENARIOS)} uv records written to {output}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# eof
