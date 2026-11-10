"""Inspect refusal and reject empty policy sets without executing module bodies."""

from __future__ import annotations

import runpy
import subprocess
from pathlib import Path

import pytest

from tools.lifecycle_compatibility import static_entry

_PREFIX = '''"""Standalone policy."""
import sys
import pytest
if sys.version_info < (3, 12):
    raise pytest.UsageError("policy requires Python 3.12 or later")
LOADER_CONTRACT_VERSION = 1
'''


def test_refusal_boundary_accepts_only_inert_safe_prefix() -> None:
    """Later imports and API work cannot run on unsupported versions."""
    static_entry.check_structure(_PREFIX + "import pathlib\n", "policy")


@pytest.mark.parametrize("source", [
    _PREFIX.replace("import sys", "import os\nimport sys"),
    _PREFIX.replace("import pytest", "import pytest\nx = 1"),
    _PREFIX.replace("raise pytest.UsageError", "print"),
    _PREFIX.replace("(3, 12)", "(3, 10)"),
    _PREFIX.replace("import sys", "import sys as other"),
    _PREFIX.replace("    raise", "    import os\n    raise"),
    "import sys\n",
])
def test_executable_or_incorrect_prefix_is_rejected(source: str) -> None:
    """AST validation rejects extra executable statements and wrong guards."""
    with pytest.raises(ValueError, match="pre-refusal"):
        static_entry.check_structure(source, "policy")


def test_ruff_syntax_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    """Observe the real grammar target and negative-control input, never spawn Ruff."""
    calls: list[list[str]] = []
    def syntax(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        assert kwargs["input"] == "source"
        return subprocess.CompletedProcess(command, 0, "")
    monkeypatch.setattr(static_entry.subprocess, "run", syntax)
    assert static_entry.syntax("source", "policy.py").returncode == 0
    assert calls[0][calls[0].index("--target-version") + 1] == "py310"


@pytest.mark.parametrize("failure", ["", "control", "policy", "os"])
def test_static_main_interprets_all_observations(monkeypatch: pytest.MonkeyPatch, failure: str) -> None:
    """A failed grammar control, policy syntax or transport fails the static gate."""
    def check(source: str, _filename: str) -> subprocess.CompletedProcess[str]:
        if failure == "os":
            raise OSError
        if "dict(x=1)" in source:
            return subprocess.CompletedProcess([], 0 if failure == "control" else 1, "Python 3.12")
        return subprocess.CompletedProcess([], 1 if failure == "policy" else 0, "bad syntax", "")
    monkeypatch.setattr(static_entry, "syntax", check)
    assert static_entry.main() == bool(failure)


def test_empty_policy_set_fails_static_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    """A moved or missing policy directory cannot silently remove every check."""
    def syntax(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess([], 1, "Python 3.12")
    def empty(_path: Path, _pattern: str) -> tuple[Path, ...]:
        return ()
    monkeypatch.setattr(static_entry, "syntax", syntax)
    monkeypatch.setattr(Path, "glob", empty)
    assert static_entry.main() == 1


def test_static_module_entrypoint(monkeypatch: pytest.MonkeyPatch) -> None:
    """The static module executes its gate when launched from check.bat."""
    def syntax(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess([], 0, "")
    monkeypatch.setattr(static_entry.subprocess, "run", syntax)
    with pytest.raises(SystemExit) as caught:
        runpy.run_path(static_entry.__file__, run_name="__main__")
    assert caught.value.code == 1


# eof
