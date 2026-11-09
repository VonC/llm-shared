"""Isolate synthetic policy state while the real carrying audit stays attached.

The process dispatcher retains its original hub and still rejects actual starts.
Generated projects explicitly dispatch synthetic events through their separate
hub, including collection events that would belong to a real carrying test.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import llm_shared_process_audit as audit
import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

@pytest.fixture(autouse=True)
def isolated_audit_state(monkeypatch: pytest.MonkeyPatch) -> Generator[None]:
    """Give each policy unit test an empty hub without granting permissions."""
    carrying = audit.get_hub()
    with pytest.MonkeyPatch.context() as patch:
        # A second adapter validates pytest's original method signatures. The
        # carrying hub still enforces all real events through its live protocol.
        for name, original in carrying.originals.items():
            patch.setattr(pytest.FixtureDef, name, original)
        patch.setattr(sys, audit._GUARD, audit.AuditHub())
        try:
            yield
        finally:
            # Tests that replace the guard must restore their changes before
            # this outer isolation restores the real carrying hub.
            monkeypatch.undo()


# eof
