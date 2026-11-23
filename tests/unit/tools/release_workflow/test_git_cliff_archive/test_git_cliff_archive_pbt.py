"""Whatever other members an archive holds, extraction leaves only `git-cliff.exe` in staging.

Step 4 of v0.14.0 git-cliff-provisioning (design "Single-member extraction";
plan "Shared test architecture": property tests for archive member
selection). Generated member names, traversal, absolute and drive-letter
forms among them, sit beside the manifest member; staging then holds only
`git-cliff.exe` with the member's bytes, and nothing appears beside staging.
"""

from __future__ import annotations

import io
import tempfile
import zipfile
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from tests.unit.tools.release_workflow.git_cliff_support import (
    STAND_IN_EXECUTABLE,
    synthetic_pin,
)
from tools.release_workflow.git_cliff.archive import extract_member

PIN = synthetic_pin()
_HOSTILE = st.sampled_from([
    "../escape.exe", "../../up/evil.exe", "/absolute.exe", "C:/drive.exe", "C:relative.exe", "..\\back.exe",
    "git-cliff-2.14.2/git-cliff-completions.exe", "git-cliff.exe", "nested/dir/file.txt",
])
_NAMES = st.lists(st.one_of(_HOSTILE, st.text(alphabet="abcdefgh./", min_size=1, max_size=12)), max_size=4, unique=True)


@settings(max_examples=10)
@given(names=_NAMES, first=st.booleans())
def test_only_git_cliff_exe_appears_in_staging(names: list[str], *, first: bool) -> None:
    """The manifest member, before or after the others, is the only thing written."""
    others = {name: b"other" for name in names if name != PIN.member}
    members = {PIN.member: STAND_IN_EXECUTABLE, **others} if first else {**others, PIN.member: STAND_IN_EXECUTABLE}
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in members.items():
            archive.writestr(name, content)
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        staged, staging = root / "archive.zip", root / "staging"
        staged.write_bytes(buffer.getvalue())
        staging.mkdir()
        extract_member(staged, PIN, staging)
        assert [path.name for path in staging.iterdir()] == ["git-cliff.exe"]
        assert (staging / "git-cliff.exe").read_bytes() == STAND_IN_EXECUTABLE
        assert sorted(path.name for path in root.iterdir()) == ["archive.zip", "staging"]


# eof
