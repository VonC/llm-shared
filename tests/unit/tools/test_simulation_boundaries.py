"""Regressions for test isolation and unexecuted launcher wiring.

Profiled guard cases provide synthetic source at the read boundary while
retaining real parsing, execution and import-path restoration.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from types import ModuleType

import pytest

from tests import script_entry


@pytest.mark.parametrize("event", ["_winapi.CreateProcess", "os.startfile", "os.exec"])
def test_process_audit_blocks_native_events(event: str) -> None:
    """The real audit hook rejects bypasses without creating a process."""
    with pytest.raises(AssertionError, match="attempted " + event):
        sys.audit(event)


@pytest.mark.parametrize("ending", ["pass", "raise SystemExit(2)", "raise RuntimeError('failure')"])
def test_script_guard_restores_import_path(
    monkeypatch: pytest.MonkeyPatch, ending: str,
) -> None:
    """Success and exceptional exits undo path changes made by the guard."""
    source = "if __name__ == '__main__':\n    sys.path.insert(0, 'guard-only')\n    " + ending + "\n"
    # All three profiled cases supply only the synthetic source read. The real
    # guard parser, compiler, execution and finally restoration still run.
    path = Path(__file__).with_name(f"guard_{ending.partition('(')[0].replace(' ', '_')}.py")
    original_read = Path.read_text

    def read_source(candidate: Path, encoding: str | None = None,
                    errors: str | None = None, newline: str | None = None) -> str:
        if candidate == path:
            return source
        return original_read(candidate, encoding=encoding, errors=errors, newline=newline)

    monkeypatch.setattr(Path, "read_text", read_source)
    module = ModuleType("guard_fixture")
    module.__file__ = str(path)
    vars(module)["sys"] = sys
    before = sys.path[:]
    if ending == "pass":
        script_entry.run_main(module)
    else:
        error = SystemExit if "SystemExit" in ending else RuntimeError
        with pytest.raises(error):
            script_entry.run_main(module)
    assert sys.path == before


def test_missing_script_guard_is_explicit(tmp_path: Path) -> None:
    """A missing guard is an error even with Python assertions disabled."""
    path = tmp_path / "no_entry.py"
    path.write_text("VALUE = 1\n", encoding="utf-8")
    module = ModuleType("no_entry")
    module.__file__ = str(path)
    with pytest.raises(ValueError, match="Expected script guards"):
        script_entry.run_main(module)


def _main_guard(tree: ast.Module) -> ast.If:
    """Locate the first script bootstrap in the module's execution order."""
    return next(node for node in tree.body if isinstance(node, ast.If)
                and ast.unparse(node.test) == "__name__ == '__main__'")


@pytest.mark.parametrize("name", ["code_review_request", "code_review_evidence_cli", "code_review_answer_cli"])
def test_code_review_path_bootstrap_contract(name: str) -> None:
    """Path execution exposes the checkout before the first tools import."""
    root = Path(__file__).resolve().parents[3]
    tree = ast.parse((root / "tools" / f"{name}.py").read_text(encoding="utf-8"))
    guard = _main_guard(tree)
    first_import = next(node for node in tree.body if isinstance(node, ast.ImportFrom)
                        and node.module and node.module.split(".")[0] == "tools")
    assert guard.lineno < first_import.lineno
    source = ast.unparse(guard)
    assert "_project_root = Path(__file__).parent.parent.resolve()" in source
    assert "sys.path.insert(0, str(_project_root))" in source


# eof
