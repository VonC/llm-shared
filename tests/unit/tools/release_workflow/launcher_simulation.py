"""Drive real bootstrap and dispatch with simulated interpreter and Git ports.

The input is an argument vector and an entry kind, never shell source. Runtime
records, parsing, preflight, payload reads, handlers and rendering stay real.
No checkout copy, virtualenv, executable, console or shell is started.
"""

from __future__ import annotations

import io
import json
import subprocess
import sys
from dataclasses import dataclass, replace
from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.test_support import (
    ENV,
    metadata,
    prepared_runtime,
)
from tools.release_workflow import bootstrap, cli
from tools.release_workflow.git import GitExecutionContext
from tools.release_workflow.results import OperationResult
from tools.release_workflow.runtime_identity import RuntimeIdentity

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from pathlib import Path

    from tests.unit.tools.release_workflow.repository_simulation import GitSandbox
    from tools.release_workflow.git_environment import ConfigEntry
    from tools.release_workflow.invocation import InvocationContext


def probe(context: InvocationContext) -> OperationResult:
    """Expose the actual context that reached production dispatch."""
    return OperationResult(data=json.dumps({
        "root": str(context.project.root), "cwd": str(context.original_cwd),
        "tooling": str(context.runtime.root), "payload": context.payload,
        "entry": context.entry_kind, "non_interactive": context.non_interactive,
        "name": context.project_name, "version": str(context.version_file),
        "runtime_public": isinstance(context.runtime, RuntimeIdentity),  # pyright: ignore[reportUnnecessaryIsInstance] - runtime class identity is the regression
        "runtime_equal": context.runtime == RuntimeIdentity(context.runtime.root, context.runtime.environment),
        "dont_write_bytecode": sys.dont_write_bytecode,
    }, ensure_ascii=False) + "\n")


def failure(_context: InvocationContext) -> OperationResult:
    """Return a domain failure for the real status/diagnostic normalizer."""
    return OperationResult(23, diagnostics=("original child failure",))


def interrupt(_context: InvocationContext) -> OperationResult:
    """Deliver cancellation at the handler boundary without an OS signal."""
    raise KeyboardInterrupt


HANDLERS = {"probe": cli.Handler(probe), "required": cli.Handler(probe, requires_input=True),
            "fail": cli.Handler(failure), "wait": cli.Handler(interrupt)}


def _patch_git(patch: pytest.MonkeyPatch, sandbox: GitSandbox) -> None:
    """Supply typed repository facts to the selected runtime's Git context."""
    def observations(context: GitExecutionContext) -> GitExecutionContext:
        return replace(sandbox.verified_git, executable=context.executable,
                       environment=context.environment, original_cwd=context.original_cwd)

    def read_version(_context: GitExecutionContext, *, cwd: Path) -> tuple[int, int, int]:  # noqa: ARG001 - native boundary signature
        return sandbox.verified_git.version

    def effective_config(context: GitExecutionContext, *, cwd: Path) -> tuple[ConfigEntry, ...]:
        return observations(context).effective_config(cwd=cwd)

    def project_metadata(context: GitExecutionContext, *, cwd: Path) -> tuple[Path, Path, Path]:
        return observations(context).metadata(cwd=cwd)

    def index(context: GitExecutionContext, *, cwd: Path, directory: str | None = None) -> tuple[str, ...]:
        return observations(context).index(cwd=cwd, directory=directory)

    patch.setattr(GitExecutionContext, "read_version", read_version)
    patch.setattr(GitExecutionContext, "effective_config", effective_config)
    patch.setattr(GitExecutionContext, "metadata", project_metadata)
    patch.setattr(GitExecutionContext, "index", index)


@dataclass(frozen=True)
class ToolingSimulation:
    """One independently selected tooling identity, with data-only metadata."""

    root: Path
    identity: RuntimeIdentity

    def run(self, arguments: Sequence[str], *, sandbox: GitSandbox, cwd: Path,  # noqa: PLR0913 - explicit boundary inputs
            environment: Mapping[str, str] | None = None, entry: str = "explicit-native",
            payload: bytes = b"", console: bool = False,
            handlers: Mapping[str, cli.Handler] | None = HANDLERS) -> subprocess.CompletedProcess[bytes]:
        """Execute production bootstrap with scoped interpreter facts and streams."""
        # Load genuine standalone helper classes before substituting the selected
        # checkout path. In particular the private identity remains a distinct
        # class, so dispatch must normalize it without rereading the record.
        bytecode = sys.dont_write_bytecode
        private = {key: value for key, value in sys.modules.items() if key.startswith("_release_bootstrap_")}
        output, errors = io.BytesIO(), io.BytesIO()
        stdout, stderr = io.TextIOWrapper(output, encoding="utf-8"), io.TextIOWrapper(errors, encoding="utf-8")
        stdin = io.TextIOWrapper(io.BytesIO(payload), encoding="utf-8", newline="")
        source = dict(sandbox.environment if environment is None else environment)
        search_path = list(sys.path)

        def dispatch(args: list[str], *, entry_kind: str, original_cwd: Path,
                     tooling_root: Path, runtime: bootstrap.Identity) -> int:
            return cli.main(args, entry_kind=entry_kind, original_cwd=original_cwd,
                            tooling_root=tooling_root, runtime=runtime, environment=source, handlers=handlers)

        original_import = bootstrap.importlib.import_module

        def import_engine(name: str) -> object:
            """Declare engine availability without substituting a successful import for absence."""
            if name != "tools.release_workflow.cli":
                return original_import(name)
            if not (self.root / "tools/release_workflow/cli.py").is_file():
                message = "selected release engine is unavailable"
                raise ModuleNotFoundError(message)
            return SimpleNamespace(main=dispatch)

        try:
            helpers = {name: bootstrap.helper(name) for name in ("runtime_identity", "markers", "readiness")}
            with pytest.MonkeyPatch.context() as patch:
                patch.chdir(cwd)
                patch.setattr(sys, "executable", str(self.identity.executable))
                patch.setattr(sys, "prefix", str(self.identity.prefix))
                patch.setattr(sys, "stdin", stdin)
                patch.setattr(sys, "stdout", stdout)
                patch.setattr(sys, "stderr", stderr)
                patch.setattr(bootstrap, "__file__", str(self.root / "tools/release_workflow/bootstrap.py"))
                patch.setattr(bootstrap, "helper", helpers.__getitem__)
                patch.setattr(bootstrap, "environment", lambda: dict(ENV))
                patch.setattr(bootstrap.importlib, "import_module", import_engine)
                _patch_git(patch, sandbox)
                patch.setattr(cli, "stdin_is_console", lambda: console)
                code = bootstrap.main(["--entry-kind", entry, "--", *arguments])
            stdout.flush()
            stderr.flush()
            return subprocess.CompletedProcess(list(arguments), code, output.getvalue(), errors.getvalue())
        finally:
            sys.path[:] = search_path
            sys.dont_write_bytecode = bytecode
            for key in list(sys.modules):
                if key.startswith("_release_bootstrap_"):
                    del sys.modules[key]
            sys.modules.update(private)
            stdout.close()
            stderr.close()
            stdin.close()


def tooling(root: Path) -> ToolingSimulation:
    """Prepare only record/readiness data; no production source tree is copied."""
    prepared_runtime(root)
    metadata(root)
    engine = root / "tools/release_workflow/cli.py"
    engine.parent.mkdir(parents=True)
    engine.write_text("# Engine availability fixture; dispatch uses production Python.\n", encoding="utf-8")
    identity = RuntimeIdentity(root.resolve(), "venvs/prepared")
    (root / "venvs/release-runtime.v1.txt").write_text(identity.serialize(), encoding="utf-8", newline="\n")
    return ToolingSimulation(root.resolve(), identity)


def decoded(result: subprocess.CompletedProcess[bytes]) -> dict[str, object]:
    """Check actual stream encoding and line endings before reading context."""
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert b"\r" not in result.stdout
    return json.loads(result.stdout.decode("utf-8"))


# eof
