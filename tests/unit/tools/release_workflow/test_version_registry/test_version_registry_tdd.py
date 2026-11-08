"""The explicit adapter tuple lists every adapter module exactly once.

Step 2 of v0.14.0 version-sources: the modules of `tools.release_workflow.sources`,
minus the declared support modules, each contribute one entry to `ADAPTERS`,
named after the module; a synthetic listing with an unregistered or a
duplicated adapter breaks the check. The current order is `("anchor",)`.
"""

from __future__ import annotations

import importlib
import pkgutil
from collections import Counter
from typing import TYPE_CHECKING

import pytest

from tools.release_workflow import sources
from tools.release_workflow.sources import anchor

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from tools.release_workflow.sources.model import Adapter


def _registry_problems(modules: Iterable[str], support: frozenset[str], adapters: Sequence[Adapter]) -> list[str]:
    """List adapter modules missing from the tuple, duplicated or without a module."""
    expected = set(modules) - support
    counts = Counter(adapter.name for adapter in adapters)
    problems = [f"missing from ADAPTERS: {name}" for name in sorted(expected - set(counts))]
    problems += [f"listed {count} times: {name}" for name, count in sorted(counts.items()) if count > 1]
    problems += [f"no adapter module: {name}" for name in sorted(set(counts) - expected)]
    return problems


def _modules() -> list[str]:
    """Name the modules of the sources package."""
    return [info.name for info in pkgutil.iter_modules(sources.__path__)]


def test_every_adapter_module_is_registered_once() -> None:
    """The real package and tuple agree, and each entry is its module's `ADAPTER`."""
    modules = _modules()
    assert _registry_problems(modules, sources.SUPPORT_MODULES, sources.ADAPTERS) == []
    for name in sorted(set(modules) - sources.SUPPORT_MODULES):
        module = importlib.import_module(f"tools.release_workflow.sources.{name}")
        assert module.ADAPTER in sources.ADAPTERS


def test_detection_order() -> None:
    """The anchor comes first; later steps insert adapters before `pattern`."""
    assert tuple(adapter.name for adapter in sources.ADAPTERS) == ("anchor",)


@pytest.mark.parametrize(("modules", "adapters", "problem"), [
    (["anchor", "model", "extra"], (anchor.ADAPTER,), "missing from ADAPTERS: extra"),
    (["anchor", "model"], (anchor.ADAPTER, anchor.ADAPTER), "listed 2 times: anchor"),
    (["model"], (anchor.ADAPTER,), "no adapter module: anchor"),
])
def test_synthetic_listing_breaks_the_check(modules: list[str], adapters: tuple[Adapter, ...], problem: str) -> None:
    """An unregistered module, a duplicate entry or an entry without a module is reported."""
    assert _registry_problems(modules, sources.SUPPORT_MODULES, adapters) == [problem]


# eof
