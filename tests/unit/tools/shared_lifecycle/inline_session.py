"""Run a small pytest project with explicit plugins and isolated environment.

No subprocess or plugin autoload is used; the carrying session keeps measuring
policy execution under its own coverage. Monkeypatch restores all host state.
The child requests plain assertions, including bypassing the host rewrite hook.
Output stays with the carrying session, avoiding redundant console capture setup.
Generated policy projects omit profiled debugger/progress startup work,
unused temporary-directory/legacy-path fixture registration and assertion
plugin setup. Plain Python assertions still execute; their rewriting and
comparison hooks are unnecessary here. The real terminal reporter remains
active for summary assertions.
"""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

import pytest
from _pytest.assertion.rewrite import AssertionRewritingHook

if TYPE_CHECKING:
    from pathlib import Path


def run_inline(root: Path, *arguments: str, plugins: tuple[object, ...] = ()) -> int:
    """Execute one generated project without inherited selection or addopts."""
    with pytest.MonkeyPatch.context() as patch:
        for key in tuple(os.environ):
            if key.startswith("LLM_SHARED_PYTEST_") or key in {"PYTEST_ADDOPTS", "PYTEST_PLUGINS"}:
                patch.delenv(key, raising=False)
        patch.setenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
        patch.setattr(sys, "meta_path", [hook for hook in sys.meta_path if not isinstance(hook, AssertionRewritingHook)])
        patch.setattr(sys, "dont_write_bytecode", True)
        prefix = str(root) + os.sep
        initial_modules = set(sys.modules)
        try:
            return pytest.main([
                str(root), "--rootdir", str(root), "--confcutdir", str(root),
                "-p", "no:cacheprovider", "-p", "no:capture", "--import-mode=importlib",
                "-p", "no:logging", "-p", "no:unittest", "-p", "no:doctest",
                "-p", "no:faulthandler", "-p", "no:junitxml", "-p", "no:pastebin",
                "-p", "no:debugging", "-p", "no:terminalprogress",
                "-p", "no:assertion",
                "-p", "no:tmpdir", "-p", "no:legacypath",
                # Generated cases create no finalizers. Avoid the child plugin's
                # repeated full-process garbage collections during cleanup.
                "-p", "no:unraisableexception",
                "-q", *arguments,
            ], plugins=list(plugins))
        finally:
            # importlib mode retains generated modules between embedded sessions.
            # Remove only this project's modules, leaving the carrying suite intact.
            for name in set(sys.modules).difference(initial_modules):
                module = sys.modules.get(name)
                filename = getattr(module, "__file__", None)
                if isinstance(filename, str) and filename.startswith(prefix):
                    sys.modules.pop(name, None)


# eof
