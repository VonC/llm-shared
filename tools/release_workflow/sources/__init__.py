"""Version source adapters in detection order, and the modules supporting them.

Step 2 of v0.14.0 version-sources registers the `anchor` adapter. Later steps
insert `python`, `npm` and `maven` before `pattern`, which Step 3 appends.
Every other module of this package is a support module and declares no
adapter; the registry test checks that each adapter module appears once.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.release_workflow.sources import anchor

if TYPE_CHECKING:
    from tools.release_workflow.sources.model import Adapter

ADAPTERS: tuple[Adapter, ...] = (anchor.ADAPTER,)
SUPPORT_MODULES = frozenset({"model"})


# eof
