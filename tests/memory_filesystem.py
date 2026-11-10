"""Route scenario temporary files to memory without patching imports.

Only pytest's scratch tree is simulated. Source files, Python imports and
runner reports keep their normal filesystem. The router is installed in a
measured fixture, and production pathlib, parsing and publication code run
unchanged. No real directories, processes or waits implement scenarios.
Preparation cache publication, shell-transfer scratch, compatibility evidence
and groundhog activation, compatibility preflight, CLI, selection and artifact-contract scenarios use
this same route.
Shared-policy acceptance also routes generated consumer resources here; its
local source adapter lets the real Python loader read those in-memory files.
"""

from __future__ import annotations

# OS-call adapters deliberately keep native signatures and lexical path APIs.
# ruff: noqa: ANN401, PTH109, PTH112, PTH117, PTH118, PTH119
import builtins
import glob
import io
import os
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, cast

import pytest

from tests.scenario_sqlite import install as install_sqlite
from tests.scenario_storage import DESCRIPTOR_BASE, ScenarioStorage
from tests.scenario_streams import ScenarioStreams

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Iterator

_PATH_OPERATIONS = (
    "stat", "lstat", "listdir", "scandir", "mkdir", "rmdir", "unlink",
    "remove", "rename", "replace", "chmod", "utime", "readlink",
)
_DESCRIPTOR_OPERATIONS = ("close", "read", "write", "fstat", "fsync", "lseek")
_PATH_PREDICATES = ("exists", "lexists", "isfile", "isdir", "islink", "isjunction", "realpath", "abspath")

# Only repository scenarios use this boundary. Native filesystem and SQLite
# unit tests keep their own real or explicitly injected storage dependencies.
_SCENARIOS = (
    "tests/unit/test_scenario_storage.py",
    "tests/unit/tools/test_models.py", "tests/unit/tools/test_find_project_root.py",
    "tests/unit/tools/prepare_release/",
    "tests/acceptance/review_resume/", "tests/acceptance/review_status/",
    "tests/acceptance/commit_plan_check/", "tests/acceptance/release_workflow/",
    "tests/unit/tools/release_workflow/", "tests/unit/tools/test_code_review",
    "tests/unit/tools/test_review_", "tests/unit/tools/test_spec_review",
    "tests/unit/tools/test_groundhog_acceptance_levels/",
    "tests/unit/tools/test_groundhog_acceptance_day.py",
    "tests/unit/tools/test_groundhog_acceptance_durations.py",
    "tests/unit/tools/test_codex_plugin_redirects/",
    "tests/unit/tools/test_effort_scope/",
    "tests/unit/tools/test_groundhog_proof/", "tests/unit/tools/test_groundhog_levels",
    "tests/unit/tools/test_groundhog_listings/", "tests/unit/tools/test_groundhog_durations_pbt.py",
    "tests/unit/tools/test_prompt_workflow", "tests/unit/tools/test_scope_capture/",
    "tests/unit/tools/git_history_dashboard/",
    "tests/unit/tools/test_groundhog_acceptance_groups/",
    "tests/unit/tools/test_groundhog_group_coverage/",
    "tests/unit/tools/test_full_suite_levels_acceptance/",
    "tests/acceptance/markdown_check/", "tests/unit/tools/serve_docs/",
    "tests/acceptance/shared_lifecycle/",
    "tests/unit/tools/git_history_diagrams/",
    "tests/unit/tools/test_groundhog_status.py",
    "tests/unit/tools/test_groundhog_snapshot",
    "tests/unit/tools/test_groundhog_commands.py",
    "tests/unit/tools/test_groundhog_cli.py",
    "tests/unit/tools/test_compatibility_preflight/",
    "tests/unit/tools/test_groundhog_selection.py",
    "tests/unit/tools/test_isolate_logos.py",
    "tests/unit/tools/sensitive_history/test_install_hooks.py",
    "tests/unit/tools/sensitive_history/test_history_scan.py",
    "tests/unit/tools/test_group_commit_message_prompt_branches.py",
    "tests/unit/tools/test_git_batch_commit.py",
    "tests/unit/tools/test_groundhog_gate.py",
    "tests/unit/tools/test_groundhog_groups/", "tests/unit/tools/test_groundhog_scope/",
    "tests/unit/tools/test_groundhog_runner.py", "tests/unit/tools/test_groundhog_acceptance.py",
    "tests/unit/tools/test_new_draft_workflow_from_draft.py",
    "tests/unit/tools/test_open_questions_md.py",
    "tests/unit/tools/markdown_check/test_policy/",
    "tests/unit/tools/shared_lifecycle/test_preparation/",
    "tests/unit/tools/shared_lifecycle/test_shell_transport/",
    "tests/unit/tools/shared_lifecycle/test_loader/",
    "tests/unit/tools/shared_lifecycle/test_groundhog_activation/",
    "tests/unit/tools/shared_lifecycle/test_compatibility/",
    "tests/unit/tools/shared_lifecycle/test_gate_contract/test_gate_contract_tdd.py::test_home_spelling_and_containment_are_strict",
    "tests/unit/tools/shared_lifecycle/test_gate_contract/test_gate_contract_tdd.py::test_invalid_declaration_never_falls_back",
)
_active_scenario = False
_COPY_FUNCTION_POSITION = 3


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_protocol(item: pytest.Item, nextitem: pytest.Item | None) -> Generator[None, object, object]:
    """Select scenario storage before any fixture setup, retaining its cost."""
    del nextitem
    global _active_scenario  # noqa: PLW0603 - pytest runs one protocol per worker
    _active_scenario = item.nodeid.startswith(_SCENARIOS)
    try:
        return (yield)
    finally:
        _active_scenario = False


class ScenarioFilesystem:
    """A scoped filesystem boundary backed by explicit file observations."""

    def __init__(self, root: Path) -> None:
        """Create an empty scenario tree and reserve a separate descriptor space.

        Paths handed to tests keep the canonical Windows spelling, with an
        upper-case drive as coverage's ``actual_path`` reports it; only routing
        compares the normcased key. A normcased root gave lower-case scratch
        paths, so coverage data recorded under them never matched the report's
        canonical file names and a covered group walk read 0%.
        """
        drive, rest = os.path.splitdrive(str(root))
        self.root = drive.upper() + rest
        self.root_key = os.path.normcase(self.root)
        self.root_prefix = self.root_key + os.sep
        self.filesystem = ScenarioStorage(os.getcwd())
        self.filesystem.create_dir(root)
        self.os = self.filesystem
        self.io = ScenarioStreams(self.filesystem)
        self.real_getcwd = os.getcwd
        self.virtual_cwd: str | None = None
        self.locks: dict[tuple[int, int], int] = {}
        self.routed_names: dict[str, bool] = {}
        self.resolved_paths: dict[str, Path] = {}
        self.next_scratch_directory = 0

    def contains(self, path: object) -> bool:
        """Recognize scratch paths lexically, without resolving anything on disk."""
        if isinstance(path, str):
            name = path
        elif isinstance(path, Path):
            name = str(path)
        elif isinstance(path, int):
            return path >= DESCRIPTOR_BASE
        elif isinstance(path, (bytes, os.PathLike)):
            name = os.fsdecode(cast("bytes | os.PathLike[str] | os.PathLike[bytes]", path))
        else:
            return False
        # Only absolute spellings enter this cache. Relative names still pass
        # through the current cwd, so chdir cannot reuse a stale routing result.
        known = self.routed_names.get(name)
        if known is not None:
            return known
        if not os.path.isabs(name):
            name = os.path.join(self.getcwd(), name)
        known = self.routed_names.get(name)
        if known is None:
            normalized = os.path.normcase(os.path.normpath(name))
            known = normalized == self.root_key or normalized.startswith(self.root_prefix)
            self.routed_names[name] = known
        return known

    def route(self, real: Callable[..., Any], simulated: Callable[..., Any]) -> Callable[..., Any]:
        """Dispatch a filesystem operation according to its path or descriptor."""
        def operation(path: Any = ".", *args: Any, **kwargs: Any) -> Any:
            if self.contains(path):
                return simulated(path, *args, **kwargs)
            return real(path, *args, **kwargs)
        return operation

    def getcwd(self) -> str:
        """Expose the simulated caller directory without changing the host cwd."""
        return self.virtual_cwd if self.virtual_cwd is not None else self.real_getcwd()

    def install(self, patch: pytest.MonkeyPatch) -> None:
        """Patch only resource calls; never scan or reload application modules."""
        for name in (*_PATH_OPERATIONS, *_DESCRIPTOR_OPERATIONS):
            patch.setattr(os, name, self.route(getattr(os, name), getattr(self.os, name)))
        for name in _PATH_PREDICATES:
            if hasattr(os.path, name):
                patch.setattr(os.path, name, self.route(getattr(os.path, name), getattr(self.os, name)))
        patch.setattr(os, "open", self.route(os.open, self.io.os_open))
        patch.setattr(os, "fdopen", self.route(os.fdopen, self.io.fdopen))
        patch.setattr(builtins, "open", self.route(builtins.open, self.io.open))
        patch.setattr(io, "open", self.route(io.open, self.io.open))
        self._install_resolve(patch)
        self._install_copy(patch)
        self._install_cwd(patch)
        self._install_links(patch)
        # Python 3.13's glob stores these functions at import time.
        globber = getattr(glob, "_StringGlobber", None)
        if globber is not None:
            patch.setattr(globber, "scandir", staticmethod(os.scandir))
            patch.setattr(globber, "lstat", staticmethod(os.lstat))
        if os.name == "nt":
            self._install_windows_locks(patch)
            self._install_junctions(patch)
        install_sqlite(patch, self)

    def _install_resolve(self, patch: pytest.MonkeyPatch) -> None:
        """Reuse immutable Path values after resolving current storage observations."""
        real_resolve = Path.resolve

        def resolve(path: Path, strict: bool = False) -> Path:  # noqa: FBT001, FBT002
            if not self.contains(path):
                return real_resolve(path, strict=strict)
            name = self.filesystem.realpath(path, strict=strict)
            if name not in self.resolved_paths:
                self.resolved_paths[name] = Path(name)
            return self.resolved_paths[name]

        patch.setattr(Path, "resolve", resolve)

    def _install_copy(self, patch: pytest.MonkeyPatch) -> None:
        """Use shutil's stream path for scenario copies, including metadata."""
        real_copy2 = shutil.copy2

        def copy2(source: Any, target: Any, *, follow_symlinks: bool = True) -> Any:
            if not (self.contains(source) or self.contains(target)):
                return real_copy2(source, target, follow_symlinks=follow_symlinks)
            source_path, target_path = os.fsdecode(source), os.fsdecode(target)
            if os.path.isdir(target_path):
                target_path = os.path.join(target_path, os.path.basename(source_path))
            shutil.copyfile(source_path, target_path, follow_symlinks=follow_symlinks)
            shutil.copystat(source_path, target_path, follow_symlinks=follow_symlinks)
            return target_path

        patch.setattr(shutil, "copy2", copy2)
        # copytree captures its default copy_function at definition time.
        real_copytree = shutil.copytree

        def copytree(source: Any, target: Any, *args: Any, **kwargs: Any) -> Any:
            if (self.contains(source) or self.contains(target)) and len(args) < _COPY_FUNCTION_POSITION:
                kwargs.setdefault("copy_function", copy2)
            return real_copytree(source, target, *args, **kwargs)

        patch.setattr(shutil, "copytree", copytree)

    def _install_junctions(self, patch: pytest.MonkeyPatch) -> None:
        """Observe Windows junction creation without calling the kernel."""
        import _winapi  # noqa: PLC0415 - Windows-only boundary

        original = _winapi.CreateJunction

        def junction(source: str, target: str) -> None:
            if self.contains(target):
                self.filesystem.junction(source, target)
            else:
                original(source, target)

        patch.setattr(_winapi, "CreateJunction", junction)

    def _install_cwd(self, patch: pytest.MonkeyPatch) -> None:
        """Retain real cwd operations outside the scenario tree."""
        real_chdir = os.chdir

        def chdir(path: Any) -> None:
            if self.contains(path):
                self.os.chdir(path)
                self.virtual_cwd = self.os.getcwd()
            else:
                real_chdir(path)
                self.virtual_cwd = None

        patch.setattr(os, "chdir", chdir)
        patch.setattr(os, "getcwd", self.getcwd)
        patch.setattr(os, "getcwdb", lambda: os.fsencode(self.getcwd()))

    def _install_links(self, patch: pytest.MonkeyPatch) -> None:
        """Route link creation by its destination, including dangling targets."""
        for name in ("symlink", "link"):
            real, simulated = getattr(os, name), getattr(self.os, name)

            def link(source: Any, target: Any, *args: Any,
                     _real: Callable[..., Any] = real, _simulated: Callable[..., Any] = simulated,
                     **kwargs: Any) -> Any:
                return (_simulated if self.contains(target) else _real)(source, target, *args, **kwargs)

            patch.setattr(os, name, link)

    def _install_windows_locks(self, patch: pytest.MonkeyPatch) -> None:
        """Model byte-range ownership; contention is immediate and deterministic."""
        import errno  # noqa: PLC0415 - Windows-only boundary
        import msvcrt  # noqa: PLC0415 - Windows-only boundary

        real_locking = msvcrt.locking

        def locking(descriptor: int, mode: int, count: int) -> None:
            if not self.contains(descriptor):
                real_locking(descriptor, mode, count)
                return
            stream = self.filesystem.get_open_file(descriptor)
            key = (stream.get_object().st_ino, stream.tell())
            if mode == msvcrt.LK_UNLCK:
                self.locks.pop(key, None)
            elif key in self.locks:
                raise BlockingIOError(errno.EACCES, "simulated lock is held")
            else:
                self.locks[key] = descriptor

        patch.setattr(msvcrt, "locking", locking)


@pytest.fixture(scope="session", autouse=True)
def scenario_filesystem(tmp_path_factory: pytest.TempPathFactory) -> Iterator[ScenarioFilesystem]:
    """Count filesystem construction and patching in the first test's setup."""
    real_getbasetemp = tmp_path_factory.getbasetemp
    # The scratch namespace is wholly virtual. Host-specific parent depth adds
    # repeated path parsing to every domain transition and provides no evidence.
    scenario_base = Path.cwd().anchor
    scenario_root = Path(scenario_base) / f"scenario-{os.getpid()}"
    filesystem = ScenarioFilesystem(scenario_root)
    with pytest.MonkeyPatch.context() as patch:
        # Child processes are forbidden; environment inputs need no host writes.
        patch.setattr(os, "environ", dict(os.environ))
        filesystem.install(patch)
        patch.setattr(tmp_path_factory, "getbasetemp", lambda: scenario_root if _active_scenario else real_getbasetemp())
        yield filesystem


@pytest.fixture(autouse=True)
def scenario_coverage_clock(monkeypatch: pytest.MonkeyPatch, scenario_filesystem: ScenarioFilesystem) -> None:
    """Keep default temporary directories and coverage clocks inside the scenario."""
    if _active_scenario:
        from tools.groundhog import group_coverage  # noqa: PLC0415

        monkeypatch.setattr(group_coverage, "time", SimpleNamespace(time=lambda: 1_700_000_000.0))
        monkeypatch.setattr(tempfile, "tempdir", scenario_filesystem.root)


@pytest.fixture
def tmp_path(request: pytest.FixtureRequest, scenario_filesystem: ScenarioFilesystem) -> Iterator[Path]:
    """Allocate unique virtual scratch trees without native numbered-dir probes."""
    if not _active_scenario:
        # Resolve the overridden pytest fixture for cases outside the frozen
        # scenario boundary, preserving its native allocation and retention.
        yield request.getfixturevalue("tmp_path")
        return
    scenario_filesystem.next_scratch_directory += 1
    path = Path(scenario_filesystem.root) / f"t{scenario_filesystem.next_scratch_directory}"
    scenario_filesystem.filesystem.create_dir(path)
    try:
        yield path
    finally:
        scenario_filesystem.filesystem.discard_tree(path)
        scenario_filesystem.routed_names.clear()
        scenario_filesystem.resolved_paths.clear()


# eof
