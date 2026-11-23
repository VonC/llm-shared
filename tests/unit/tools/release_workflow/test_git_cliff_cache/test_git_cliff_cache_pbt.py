"""Generated attempt names and entry records round-trip through their encodings.

Step 3 of v0.14.0 git-cliff-provisioning (plan "Shared test architecture":
property tests where the input domain is large and the function pure): any
positive PID and creation time with any lowercase hexadecimal token builds a
staging or retired directory name that parses back to the same owner, and an
entry record with any digests and positive size decodes to itself.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from tests.unit.tools.release_workflow.git_cliff_support import (
    entry_record,
    synthetic_pin,
)
from tools.release_workflow.git_cliff.cache import Attempt, CacheLayout, EntryRecord
from tools.release_workflow.windows_process import ProcessIdentity

PIN = synthetic_pin()
_LAYOUT = CacheLayout(Path("C:/tooling"))
_POSITIVE = st.integers(min_value=1, max_value=2**63 - 1)
_TOKENS = st.text(alphabet="0123456789abcdef", min_size=1, max_size=32)
_DIGESTS = st.binary(min_size=32, max_size=32).map(bytes.hex)


@settings(max_examples=25)
@given(kind=st.sampled_from(["staging", "retired"]), pid=_POSITIVE, created=_POSITIVE, token=_TOKENS)
def test_attempt_names_round_trip(kind: str, pid: int, created: int, token: str) -> None:
    """The name of an attempt directory gives back its kind, its owner and its token."""
    owner = ProcessIdentity(pid, created)
    name = _LAYOUT.attempt_dir(PIN, kind, owner, token).name
    assert CacheLayout.parse_attempt(name) == Attempt(kind, owner, token)


@settings(max_examples=25)
@given(asset=_DIGESTS, executable=_DIGESTS, size=_POSITIVE)
def test_entry_records_round_trip(asset: str, executable: str, size: int) -> None:
    """Any digests and positive size encode to a record that decodes to itself."""
    record = replace(entry_record(PIN), asset_sha256=asset, executable_sha256=executable, executable_size=size)
    assert EntryRecord.decode(record.encode()) == record


# eof
