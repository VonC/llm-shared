"""Generate isolated real-xdist projects with an observed valid peer barrier."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

NAMES = ("invalid", "exit", "mismatch")
DIAGNOSTICS = {
    "invalid": "requires a non-empty reason string",
    "exit": "validated collection",
    "mismatch": "inconsistent worker collection",
}

_CONFTEST = '''"""Coordinate worker failure only after the controller observes its peer."""
import os
from pathlib import Path
from time import monotonic, sleep
import pytest

ROOT = Path(__file__).parent
SCENARIO = {scenario!r}

def pytest_configure(config):
    if hasattr(config, "workerinput"):
        worker = config.workerinput["workerid"]
        (ROOT / ("worker." + worker + ".pid")).write_text(str(os.getpid()))

@pytest.hookimpl(optionalhook=True, trylast=True)
def pytest_xdist_node_collection_finished(node, ids):
    if node.workerinput["workerid"] == "gw0":
        (ROOT / "announced").write_text("gw0")

def pytest_collection_modifyitems(config, items):
    if getattr(config, "workerinput", {{}}).get("workerid") != "gw1":
        return
    deadline = monotonic() + 15
    while not (ROOT / "announced").exists():
        if monotonic() >= deadline:
            raise pytest.UsageError("valid peer announcement was not observed")
        sleep(0.01)
    if SCENARIO == "invalid":
        items[0].add_marker(pytest.mark.process_allowed(reason=""))
    elif SCENARIO == "exit":
        os._exit(4)
    elif SCENARIO == "mismatch":
        items[0]._nodeid += "-different"
'''

_TEST = '''"""Any scheduled setup or test body leaves persistent evidence."""
from pathlib import Path
import pytest

@pytest.fixture(autouse=True)
def observe_setup():
    Path(__file__).with_name("started").touch()

def test_peer():
    Path(__file__).with_name("started").touch()
'''


def write_project(root: Path, scenario: str) -> None:
    """Write a self-contained project without consuming any parent conftest."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "pytest.ini").write_text(
        "[pytest]\nmarkers =\n    process_allowed(reason): process permission\n", encoding="utf-8",
    )
    (root / "conftest.py").write_text(_CONFTEST.format(scenario=scenario), encoding="utf-8")
    (root / "test_peer.py").write_text(_TEST, encoding="utf-8")


# eof
