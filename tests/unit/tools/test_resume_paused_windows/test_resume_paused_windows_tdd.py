"""Windows process helpers and the query-only Win32 binding tests.

Step 1 of v0.15.0 resume-paused: the pure helpers resolve direct children and
ancestry from one listing. The ``Win32Api`` tests observe this test process
itself with query-only rights, start no process and send no input: its own
image must pass the class 44 identity query, and invalid handles fail closed.
"""

from __future__ import annotations

import ctypes
import hashlib
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools.resume_paused_windows import (
    GLOBALROOT,
    ProcessRecord,
    Win32Api,
    ancestry_names,
    direct_children,
    filetime_to_datetime,
    list_jsonl_files,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

LISTING = (
    ProcessRecord(1, 0, "explorer.exe"),
    ProcessRecord(10, 1, "cmd.exe"),
    ProcessRecord(20, 10, "Codex.exe"),
    ProcessRecord(21, 10, "conhost.exe"),
    ProcessRecord(30, 20, "powershell.exe"),
)
STATUS_SUCCESS = 0
windows_only = pytest.mark.skipif(sys.platform != "win32", reason="Win32 binding")


def test_filetime_converts_to_utc() -> None:
    """FILETIME ticks count 100 nanoseconds from 1601 in UTC."""
    assert filetime_to_datetime(0) == datetime(1601, 1, 1, tzinfo=UTC)
    assert filetime_to_datetime(116_444_736_000_000_000 + 15) == datetime(1970, 1, 1, 0, 0, 0, 1, tzinfo=UTC)


def test_direct_children_match_the_image_name_without_case() -> None:
    """Only direct children running the named image are returned."""
    assert direct_children(LISTING, 10, "codex.exe") == (LISTING[2],)
    assert direct_children(LISTING, 1, "codex.exe") == ()


def test_ancestry_lists_nearest_ancestor_first() -> None:
    """Ancestor names stop where the listing has no parent."""
    assert ancestry_names(LISTING, 30) == ("Codex.exe", "cmd.exe", "explorer.exe")


def test_ancestry_is_unavailable_for_an_unlisted_process() -> None:
    """A missing process yields no ancestry instead of an empty human proof."""
    assert ancestry_names(LISTING, 99) is None


def test_ancestry_stops_on_a_reused_identifier_cycle() -> None:
    """A parent cycle from identifier reuse ends the walk."""
    cycle = (ProcessRecord(5, 6, "a.exe"), ProcessRecord(6, 5, "b.exe"))

    assert ancestry_names(cycle, 5) == ("b.exe",)


@pytest.fixture
def own_process() -> Iterator[tuple[Win32Api, int, str]]:
    """Open this test process with query rights and name its loaded image."""
    api = Win32Api()
    process = api.open_process(os.getpid())
    assert process is not None
    native = api.native_image_name(process)
    assert native is not None
    yield api, process, native
    api.close(process)


@windows_only
def test_win32_walks_this_process_to_one_image_allocation(own_process: tuple[Win32Api, int, str]) -> None:
    """A complete allocation walk maps the native image name exactly once."""
    api, process, native = own_process

    walk = api.image_walk(process)
    created = api.creation_time(process)

    assert (walk.complete, walk.mapped_names.count(native)) == (True, 1)
    assert walk.regions > 0
    assert (api.os_build() or 0) > 0
    assert filetime_to_datetime(created or 0) < datetime.now(UTC)


@windows_only
def test_win32_identity_query_accepts_the_loaded_image(own_process: tuple[Win32Api, int, str]) -> None:
    """The loaded image file passes class 44 and hashes through the same handle."""
    api, process, native = own_process
    image = api.open_image(native)
    assert image is not None

    status = api.image_mapping_status(process, image)
    digest = api.sha256(image)
    api.close(image)

    assert status == STATUS_SUCCESS
    assert digest == (hashlib.sha256(api.read_file(GLOBALROOT + native) or b"").hexdigest(), len(api.read_file(GLOBALROOT + native) or b""))


@windows_only
def test_win32_lists_this_process_with_its_parent() -> None:
    """The toolhelp listing names this process and its parent identifier."""
    listing = Win32Api().processes()

    assert listing is not None
    own = [record for record in listing if record.pid == os.getpid()]
    assert len(own) == 1
    assert own[0].parent_pid == os.getppid()
    assert own[0].name.casefold().endswith(".exe")


@windows_only
@pytest.mark.parametrize("failing", ["_first", "_next"])
def test_win32_listing_is_unavailable_when_the_walk_fails(failing: str) -> None:
    """A first or later enumeration call failing for another reason yields no partial list."""
    api = Win32Api()

    def denied(_snapshot: int, _entry: object) -> bool:
        ctypes.set_last_error(5)
        return False

    setattr(api, failing, denied)

    assert api.processes() is None


@windows_only
def test_win32_fails_closed_on_invalid_handles_and_paths() -> None:
    """Denied or invalid observations return no evidence, never a guess."""
    api = Win32Api()

    assert api.open_process(0) is None
    assert api.creation_time(0) is None
    assert api.native_image_name(0) is None
    assert not api.image_walk(0).complete
    assert api.open_image("\\Device\\Missing\\absent.exe") is None
    assert api.image_mapping_status(0, 0) != STATUS_SUCCESS
    assert api.sha256(0) is None
    assert api.read_file("Z:\\absent\\missing.jsonl") is None


@windows_only
def test_win32_reads_a_file_completely() -> None:
    """A shared read returns the exact bytes of a real file."""
    path = Path(__file__)

    assert Win32Api().read_file(str(path)) == path.read_bytes()


def test_jsonl_listing_covers_every_sub_directory(tmp_path: Path) -> None:
    """Regular JSONL files are found across nested partitions; other files are ignored."""
    (tmp_path / "2026" / "11" / "14").mkdir(parents=True)
    (tmp_path / "2026" / "11" / "14" / "live.jsonl").write_bytes(b"{}\n")
    (tmp_path / "2026" / "old.jsonl").write_bytes(b"{}\n{}\n")
    (tmp_path / "2026" / "notes.txt").write_bytes(b"ignored")

    files = list_jsonl_files(str(tmp_path))

    assert files is not None
    assert {(Path(file.path).name, file.size) for file in files} == {("live.jsonl", 3), ("old.jsonl", 6)}
    assert all(file.modified_ns > 0 for file in files)


@windows_only
def test_jsonl_listing_is_incomplete_for_a_missing_root_or_a_link(tmp_path: Path) -> None:
    """A listing error or a junction makes the enumeration incomplete, never partial."""
    import _winapi  # noqa: PLC0415 - Windows-only junction creation, no privilege needed

    (tmp_path / "real").mkdir()
    (tmp_path / "real" / "a.jsonl").write_bytes(b"{}\n")
    linked = tmp_path / "linked"
    linked.mkdir()
    _winapi.CreateJunction(str(tmp_path / "real"), str(linked / "alias"))

    assert list_jsonl_files(str(tmp_path / "absent")) is None
    assert list_jsonl_files(str(linked)) is None
    assert list_jsonl_files(str(tmp_path)) is None
    assert list_jsonl_files(str(tmp_path / "real")) is not None


# eof
