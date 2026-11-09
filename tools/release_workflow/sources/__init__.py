"""Version source adapters in detection order, and the modules supporting them.

Step 2 of v0.14.0 version-sources registers the `anchor` adapter. Step 3
appends `pattern` and adds the `settings` and `detection` support modules;
later steps insert `python`, `npm` and `maven` before `pattern`. Every other
module of this package is a support module and declares no adapter; the
registry test checks that each adapter module appears once.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.release_workflow.sources import anchor, pattern

if TYPE_CHECKING:
    from tools.release_workflow.sources.model import Adapter

ADAPTERS: tuple[Adapter, ...] = (anchor.ADAPTER, pattern.ADAPTER)
SUPPORT_MODULES = frozenset({"model", "settings", "detection"})


# eof
