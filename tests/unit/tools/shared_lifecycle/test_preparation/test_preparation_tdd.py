"""Check atomic preparation and drive-root callers without importing policies."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools import pytest_plugin_environment as env


@pytest.fixture
def layout(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Declare complete live sources without importing their executable bodies."""
    project, shared, cache = (tmp_path / name for name in ("project", "shared", "cache"))
    project.mkdir()
    policy = shared / "tools" / "pytest_plugins"
    policy.mkdir(parents=True)
    for name in (env.LOADER, *env.POLICIES.values()):
        (policy / f"{name}.py").write_text("LOADER_CONTRACT_VERSION = 1\nraise RuntimeError('never import in preparation')\n", encoding="utf-8")
    return project, shared, cache


def test_drive_root_preserves_user_cache(layout: tuple[Path, Path, Path]) -> None:
    """A drive root is a valid caller even when user storage is on that drive."""
    project, shared, cache = layout
    drive = Path(project.anchor)
    result = env.prepare_environment(drive, shared, {env.SELECTION: "lifecycle"}, cache_root=cache)
    assert result[env.ROOT] == str(drive.resolve())
    assert Path(result["PYTHONPATH"].split(os.pathsep)[0]).parent == cache


def test_preparation_preserves_inputs_and_publishes_only_loader(layout: tuple[Path, Path, Path]) -> None:
    """Selection changes only owned entries and does not execute source bodies."""
    project, shared, cache = layout
    original = {env.SELECTION: " process, lifecycle,process ", "OTHER": "kept", "PYTHONPATH": "consumer", "PYTEST_ADDOPTS": '-q -k "one or two"'}
    before = original.copy()
    result = env.prepare_environment(project, shared, original, cache_root=cache)
    assert original == before
    assert result[env.SELECTION] == "lifecycle,process"
    assert result[env.ROOT] == str(project.resolve())
    policy = shared / "tools" / "pytest_plugins"
    source = (policy / f"{env.LOADER}.py").read_bytes()
    entry = cache / hashlib.sha256(source).hexdigest()
    assert result["PYTHONPATH"].split(os.pathsep) == [str(entry), str(policy), "consumer"]
    assert result["PYTEST_ADDOPTS"] == f'-p {env.LOADER} -q -k "one or two"'
    assert result["OTHER"] == "kept"
    assert [p.name for p in entry.iterdir()] == [f"{env.LOADER}.py"]
    assert not (project / ".reviews").exists()
    assert env.prepare_environment(project, shared, result, cache_root=cache) == result


def test_deselection_removes_old_owned_entries_only(layout: tuple[Path, Path, Path]) -> None:
    """Deselection preserves unrelated entries and removes fully owned variables."""
    project, shared, cache = layout
    original = {env.SELECTION: "lifecycle", "PYTHONPATH": "consumer", "PYTEST_ADDOPTS": "-q"}
    prepared = env.prepare_environment(project, shared, original, cache_root=cache)
    prepared[env.SELECTION] = ""
    result = env.prepare_environment(project, shared, prepared, cache_root=cache)
    assert result == {"PYTHONPATH": "consumer", "PYTEST_ADDOPTS": "-q"}
    assert env.prepare_environment(project, shared, {}, cache_root=cache) == {}
    owned_only = env.prepare_environment(project, shared, {env.SELECTION: "lifecycle"}, cache_root=cache)
    owned_only[env.SELECTION] = ""
    assert env.prepare_environment(project, shared, owned_only, cache_root=cache) == {}


@pytest.mark.parametrize("raw", ["bad", "lifecycle,,process", ",", "PROCESS", "life cycle"])
def test_invalid_selection_never_publishes(layout: tuple[Path, Path, Path], raw: str) -> None:
    """Only named tokens and an entirely empty declaration are accepted."""
    project, shared, cache = layout
    original = {env.SELECTION: raw}
    with pytest.raises(env.PreparationError, match=env.SELECTION):
        env.prepare_environment(project, shared, original, cache_root=cache)
    assert original == {env.SELECTION: raw}
    assert not cache.exists()


@pytest.mark.parametrize("change", ["missing", "syntax", "missing_contract", "mismatch", "computed", "duplicate"])
def test_policy_source_failures_publish_nothing(layout: tuple[Path, Path, Path], change: str) -> None:
    """Source presence and a single literal contract are checked before cache IO."""
    project, shared, cache = layout
    path = shared / "tools/pytest_plugins/llm_shared_process_audit.py"
    sources = {"syntax": "def ?", "missing_contract": "x = 1", "mismatch": "LOADER_CONTRACT_VERSION = 2", "computed": "LOADER_CONTRACT_VERSION = int('1')", "duplicate": "LOADER_CONTRACT_VERSION = 1\nLOADER_CONTRACT_VERSION = 1"}
    if change == "missing":
        path.unlink()
    else:
        path.write_text(sources[change], encoding="utf-8")
    with pytest.raises(env.PreparationError, match="llm_shared_process_audit"):
        env.prepare_environment(project, shared, {env.SELECTION: "lifecycle,process"}, cache_root=cache)
    assert not cache.exists()


def test_cache_corruption_is_rejected_without_repair(layout: tuple[Path, Path, Path]) -> None:
    """An immutable entry is never silently rewritten, even if its file vanished."""
    project, shared, cache = layout
    original = {env.SELECTION: "lifecycle"}
    prepared = env.prepare_environment(project, shared, original, cache_root=cache)
    entry = Path(prepared["PYTHONPATH"].split(os.pathsep)[0])
    source = entry / f"{env.LOADER}.py"
    source.write_text("corrupt", encoding="utf-8")
    with pytest.raises(env.PreparationError, match="explicitly remove"):
        env.prepare_environment(project, shared, original, cache_root=cache)
    assert source.read_text(encoding="utf-8") == "corrupt"
    source.unlink()
    with pytest.raises(env.PreparationError, match="explicitly remove"):
        env.prepare_environment(project, shared, original, cache_root=cache)


def test_racing_publication_verifies_winner(layout: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    """A concurrently published complete entry is reused without replacement."""
    project, shared, cache = layout
    rename = Path.rename
    def race(source: Path, target: Path) -> Path:
        target.mkdir()
        (target / f"{env.LOADER}.py").write_bytes((source / f"{env.LOADER}.py").read_bytes())
        raise FileExistsError
    monkeypatch.setattr(Path, "rename", race)
    result = env.prepare_environment(project, shared, {env.SELECTION: "process"}, cache_root=cache)
    assert Path(result["PYTHONPATH"].split(os.pathsep)[0]).is_dir()
    assert len(list(cache.iterdir())) == 1
    monkeypatch.setattr(Path, "rename", rename)


def test_interrupted_publication_cleans_only_temporary_entry(layout: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    """Failure leaves no activation and no incomplete published directory."""
    project, shared, cache = layout
    def fail(_source: Path, _target: Path) -> Path:
        message = "publication interrupted"
        raise OSError(message)
    monkeypatch.setattr(Path, "rename", fail)
    with pytest.raises(env.PreparationError, match="publication interrupted"):
        env.prepare_environment(project, shared, {env.SELECTION: "process"}, cache_root=cache)
    assert list(cache.iterdir()) == []


def test_independent_bindings_and_source_edits(layout: tuple[Path, Path, Path], tmp_path: Path) -> None:
    """Loader hashes follow source changes; existing shells keep their binding."""
    project, shared, cache = layout
    first = env.prepare_environment(project, shared, {env.SELECTION: "lifecycle"}, cache_root=cache)
    other = tmp_path / "second-shared/tools/pytest_plugins"
    other.mkdir(parents=True)
    for source in (shared / "tools/pytest_plugins").iterdir():
        (other / source.name).write_bytes(source.read_bytes() + b"# changed\n")
    second = env.prepare_environment(project, other.parent.parent, first, cache_root=cache)
    assert first[env.POLICY_DIR] != second[env.POLICY_DIR]
    assert first["PYTHONPATH"].split(os.pathsep)[0] != second["PYTHONPATH"].split(os.pathsep)[0]
    assert first[env.POLICY_DIR] not in second["PYTHONPATH"].split(os.pathsep)
    assert set(cache.iterdir()) == {Path(first["PYTHONPATH"].split(os.pathsep)[0]), Path(second["PYTHONPATH"].split(os.pathsep)[0])}


@pytest.mark.parametrize("location", ["project", "shared"])
def test_cache_must_live_outside_both_checkouts(layout: tuple[Path, Path, Path], location: str) -> None:
    """Preparing a transient consumer cannot write cache files in either tree."""
    project, shared, _cache = layout
    with pytest.raises(env.PreparationError, match="outside"):
        env.prepare_environment(project, shared, {env.SELECTION: "process"}, cache_root=(project if location == "project" else shared) / "cache")


@pytest.mark.parametrize("options", ["  -q  ", '-k "-p llm_shared_pytest_loader"', "", "-p other -x"])
def test_unselected_environment_preserves_option_text(layout: tuple[Path, Path, Path], options: str) -> None:
    """Empty selections leave unrelated text and originally empty keys intact."""
    project, shared, cache = layout
    original = {"PYTEST_ADDOPTS": options, "PYTHONPATH": "", "OTHER": "value"}
    assert env.prepare_environment(project, shared, original, cache_root=cache) == original
    selected = dict(original, **{env.SELECTION: "lifecycle"})
    prepared = env.prepare_environment(project, shared, selected, cache_root=cache)
    assert "" not in prepared["PYTHONPATH"].split(os.pathsep)
    assert env.prepare_environment(project, shared, prepared, cache_root=cache) == prepared


@pytest.mark.parametrize("option", ["-p llm_shared_pytest_loader", "-pll m", "-pll m -p=llm_shared_pytest_loader", "-pll m -pllm_shared_pytest_loader"])
def test_option_cleanup_preserves_other_plugins(option: str) -> None:
    """Joined and separated loader options are removed at token boundaries."""
    assert env.clean_options(option) == ("-pll m " if option.startswith("-pll m -p") else "-pll m" if option == "-pll m" else "")


def test_cache_location_uses_only_user_storage(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Both platform cache defaults stay independent of checkout bindings."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert env.default_cache_root({}) == tmp_path / ".cache/llm-shared/pytest-loader"
    assert env.default_cache_root({"LOCALAPPDATA": str(tmp_path)}) == tmp_path / "llm-shared/pytest-loader"


def test_annotated_contract_and_default_cache(layout: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    """A literal annotated contract is valid without executing its body."""
    project, shared, cache = layout
    (shared / "tools/pytest_plugins/llm_shared_process_audit.py").write_text("LOADER_CONTRACT_VERSION: int = 1\n", encoding="utf-8")
    def default_cache(_environment: object) -> Path:
        return cache
    monkeypatch.setattr(env, "default_cache_root", default_cache)
    prepared = env.prepare_environment(project, shared, {env.SELECTION: "process"})
    assert prepared[env.POLICY_DIR] == str(shared / "tools/pytest_plugins")


def test_preparation_reads_each_required_source_once(layout: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    """Fresh and repeated preparation perform bounded source/cache IO only."""
    project, shared, cache = layout
    read_bytes = Path.read_bytes
    reads: list[Path] = []
    def counted(path: Path) -> bytes:
        reads.append(path)
        return read_bytes(path)
    monkeypatch.setattr(Path, "read_bytes", counted)
    original = {env.SELECTION: "lifecycle,process"}
    prepared = env.prepare_environment(project, shared, original, cache_root=cache)
    policy = shared / "tools/pytest_plugins"
    expected = [policy / f"{name}.py" for name in (env.LOADER, *env.POLICIES.values())]
    expected.append(Path(prepared["PYTHONPATH"].split(os.pathsep)[0]) / f"{env.LOADER}.py")
    assert reads == expected
    reads.clear()
    assert env.prepare_environment(project, shared, prepared, cache_root=cache) == prepared
    assert reads == expected
