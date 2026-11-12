"""Observe narrow compatibility errors and fresh dispatch without children."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.groundhog_acceptance_support import (
    QueueSpawns,
    make_deps,
    passing_transcript,
)
from tests.unit.tools.test_groundhog_acceptance_levels.support import save
from tools.groundhog import cli, compatibility_preflight
from tools.groundhog.levels import FullLevel
from tools.groundhog.models import EXIT_SETUP_ERROR

if TYPE_CHECKING:
    from pathlib import Path

_FULL_CHILDREN = 2


def declare(root: Path, text: str = "enabled = true") -> Path:
    """Declare applicability and the fixed checkout-owned entrypoint."""
    (root / "pyproject.toml").write_text("[tool.llm-shared.lifecycle-compatibility]\n" + text, encoding="utf-8")
    entry = root / "bin" / "lifecycle_compatibility.bat"
    entry.parent.mkdir(exist_ok=True)
    entry.touch()
    return entry


@pytest.mark.parametrize("text", ["", "[tool.other]\nx = 1", "[tool.llm-shared.lifecycle-compatibility]\n", "[tool.llm-shared.lifecycle-compatibility]\nenabled = false"])
def test_absent_or_false_never_spawns(tmp_path: Path, text: str) -> None:
    """Ordinary consumers acquire no independent interpreter prerequisite."""
    (tmp_path / "pyproject.toml").write_text(text, encoding="utf-8")
    spawns = QueueSpawns([])
    compatibility_preflight.run(tmp_path, make_deps(spawns))
    assert not spawns.commands


@pytest.mark.parametrize("text", ['enabled = "true"', "enabled = 1", "enabled = []", "enabled = {}"])
def test_malformed_declaration_stops_before_spawn(tmp_path: Path, text: str) -> None:
    """Literal booleans are mandatory in an explicitly declared table."""
    declare(tmp_path, text)
    with pytest.raises(compatibility_preflight.CompatibilityError, match="lifecycle-compatibility"):
        compatibility_preflight.run(tmp_path, make_deps(QueueSpawns([])))


@pytest.mark.parametrize("text", ["tool = 1", "[tool]\nllm-shared = false", "[tool.llm-shared]\nlifecycle-compatibility = true", "[broken"])
def test_invalid_parent_shapes_fail_closed(tmp_path: Path, text: str) -> None:
    """Malformed tracked declarations cannot become disabled by coercion."""
    (tmp_path / "pyproject.toml").write_text(text, encoding="utf-8")
    with pytest.raises(compatibility_preflight.CompatibilityError, match="lifecycle-compatibility"):
        compatibility_preflight.entrypoint(tmp_path)


def test_missing_declaration_file_is_disabled(tmp_path: Path) -> None:
    """Projects without pyproject remain unaffected."""
    assert compatibility_preflight.entrypoint(tmp_path) is None


def test_missing_entrypoint_is_identified(tmp_path: Path) -> None:
    """An enabled checkout must ship its fixed entrypoint."""
    entry = declare(tmp_path)
    entry.unlink()
    with pytest.raises(compatibility_preflight.CompatibilityError, match=r"bin.*lifecycle_compatibility\.bat"):
        compatibility_preflight.entrypoint(tmp_path)


@pytest.mark.parametrize("subcommand", ["day", "full"])
def test_malformed_setup_prevents_children(tmp_path: Path, subcommand: str) -> None:
    """Invalid applicability fails before day detaches or direct full starts."""
    declare(tmp_path, 'enabled = "true"')
    spawns = QueueSpawns([])
    detach = ["--detach"] if subcommand == "day" else []
    assert cli.main([subcommand, *detach, "--root", str(tmp_path), "--llm"], make_deps(spawns)) == EXIT_SETUP_ERROR
    assert not spawns.commands


def test_failed_harness_stops_validation(tmp_path: Path) -> None:
    """A harness failure earns no test or compatibility success."""
    declare(tmp_path)
    spawns = QueueSpawns([(["compatibility failed"], 1)])
    assert cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(spawns)) == EXIT_SETUP_ERROR
    assert len(spawns.commands) == 1


@pytest.mark.parametrize("level", [None, "pass", "cov", "speed"])
def test_day_obtains_fresh_evidence_even_on_saved_noop(tmp_path: Path, level: str | None) -> None:
    """Each invocation preflights exactly once, including the proof no-op."""
    entry = declare(tmp_path)
    save(tmp_path, FullLevel.NONE if level is None else FullLevel[level.upper()])
    args = ["day", "--root", str(tmp_path), "--llm"] + ([] if level is None else ["--full=" + level])
    fresh = QueueSpawns([(["new evidence"], 0)])
    assert cli.main(args, make_deps(fresh)) == 0
    assert fresh.commands == [["cmd.exe", "/d", "/c", str(entry)]]


def test_direct_full_preflights_once(tmp_path: Path) -> None:
    """Direct full uses the target checkout rather than the groundhog source."""
    declare(tmp_path)
    spawns = QueueSpawns([(["fresh"], 0), (passing_transcript(1, "TOTAL    100    0   100%"), 0)])
    assert cli.main(["full", "--full=pass", "--root", str(tmp_path), "--llm"], make_deps(spawns)) == 0
    assert len(spawns.commands) == _FULL_CHILDREN


def test_foreign_binding_precedes_harness(tmp_path: Path) -> None:
    """Binding rejection occurs before any executable compatibility work."""
    declare(tmp_path)
    spawns = QueueSpawns([])
    deps = replace(make_deps(spawns), environ={"LLM_SHARED_PYTEST_ROOT": str(tmp_path / "other")}.get)
    assert cli.main(["day", "--root", str(tmp_path), "--llm"], deps) == EXIT_SETUP_ERROR
    assert not spawns.commands


@pytest.mark.parametrize("forced", [False, True])
def test_upgrades_and_forced_walks_obtain_fresh_evidence(tmp_path: Path, *, forced: bool) -> None:
    """A saved default proof cannot replace the next invocation's preflight."""
    declare(tmp_path)
    save(tmp_path, FullLevel.NONE)
    args = ["day", "--root", str(tmp_path), "--llm"]
    children = [(["fresh again"], 0)]
    children.extend([(passing_transcript(1, None), 0)] if forced else [])
    children.append((passing_transcript(1, "TOTAL    100    0   100%"), 0))
    fresh = QueueSpawns(children)
    assert cli.main([*args, "--full=cov", *(["--force"] if forced else [])], make_deps(fresh)) == 0
    assert len(fresh.commands) == len(children)


def test_full_failure_prevents_pytest(tmp_path: Path) -> None:
    """Direct full also stops before the audited suite on preflight failure."""
    declare(tmp_path)
    spawns = QueueSpawns([(["failed"], 1)])
    assert cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns)) == EXIT_SETUP_ERROR
    assert len(spawns.commands) == 1


# eof
