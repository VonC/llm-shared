"""Every provisioning failure names its pin, path, stage and remedy; the three standard-error lines follow the design.

Step 5 of v0.14.0 git-cliff-provisioning (design "Messages, statuses and the
failure contract"; design decisions Q05 and Q18; requirement clarification
Q08). The download line gives the asset size in MiB with one decimal; the
ready and waiting lines name the pin, and the waiting line shows the holder's
start as a local time with its offset and the caller's own wait W. A
`ProvisioningError` is a status 2 setup failure for engine callers whose
diagnostic names the pin, the internal path, the stage and its remedy; no
remedy asks to install git-cliff or change PATH, and the probe and extraction
remedies never suggest the budget variable. A permission failure names the
nearest existing directory above the refused path, also for a write another
process reported (code review round 1). A line that standard error cannot
take is a twelfth stage, `reporting`, with its error as cause (round 2).
"""

from __future__ import annotations

import errno
from pathlib import Path

import pytest

from tests.unit.tools.release_workflow.git_cliff_support import synthetic_pin
from tools.release_workflow.git_cliff.budget import DOWNLOAD_BUDGET_VARIABLE
from tools.release_workflow.git_cliff.cache_lock import LOCK_WAIT_REMEDY
from tools.release_workflow.git_cliff.manifest import AdmittedPin
from tools.release_workflow.git_cliff.messages import (
    REMEDIES,
    ProvisioningError,
    Stage,
    announce,
    denied_write,
    downloading_line,
    permission_failure,
    ready_line,
    waiting_line,
)

ENTRY = Path("C:/llm-shared/.tools/git-cliff/2.14.2/x86_64-pc-windows-msvc")
REAL_ASSET = AdmittedPin(
    version="2.14.2", default=True, triple="x86_64-pc-windows-msvc", asset="git-cliff-2.14.2-x86_64-pc-windows-msvc.zip",
    size=7_428_304, sha256="6ece2112b3f4af462190ecbea4aeb1315fff6af415629b597f84319073c31131",
    member="git-cliff-2.14.2/git-cliff.exe", evidence="tools/release_workflow/git_cliff/bundles/2.14.2",
)


def test_the_download_line_gives_the_asset_and_its_size_in_mebibytes() -> None:
    """7,428,304 bytes read 7.1 MiB, as in the design table."""
    assert downloading_line(REAL_ASSET) == (
        "git-cliff 2.14.2: downloading git-cliff-2.14.2-x86_64-pc-windows-msvc.zip (7.1 MiB) from GitHub"
    )


def test_the_ready_line_names_the_entry() -> None:
    """The published entry is announced with its path."""
    assert ready_line("2.14.2", ENTRY) == f"git-cliff 2.14.2: ready at {ENTRY}"


@pytest.mark.parametrize(("started", "wait", "shown"), [
    ("2026-11-18T14:02:31+01:00", 360, "since 14:02:31+01:00 (up to 360 s)"),
    ("2026-07-01T08:00:00-04:00", 3660, "since 08:00:00-04:00 (up to 3660 s)"),
    ("2026-11-18T14:02:31.250000+01:00", 960.0, "since 14:02:31+01:00 (up to 960 s)"),
])
def test_the_waiting_line_shows_the_holder_its_local_start_and_the_callers_wait(started: str, wait: float, shown: str) -> None:
    """The holder's PID, its start as local time with offset, and the caller's own W."""
    assert waiting_line("2.14.2", 4812, started, wait) == f"git-cliff 2.14.2: waiting for provisioning by process 4812 {shown}"


@pytest.mark.parametrize("stage", list(Stage))
def test_every_stage_diagnostic_names_the_pin_the_path_the_stage_and_its_remedy(stage: Stage) -> None:
    """The diagnostic is the error text; it carries status 2 and every field it was built with."""
    error = ProvisioningError(stage, version="2.14.2", path=ENTRY, detail="what happened.")
    text = error.diagnostic()
    assert str(error) == text
    assert text == f"git-cliff 2.14.2 unavailable at {ENTRY} ({stage.value} stage): what happened. {REMEDIES[stage]}"
    assert (error.exit_code, error.stage, error.version, error.path, error.detail) == (2, stage, "2.14.2", ENTRY, "what happened.")
    assert isinstance(error, ValueError)


def test_a_diagnostic_without_an_admitted_pin_says_so() -> None:
    """The configuration stage can fail before any pin exists."""
    error = ProvisioningError(Stage.CONFIGURATION, version=None, path=ENTRY.parent.parent, detail="no default")
    assert error.diagnostic().startswith(f"git-cliff (no admitted pin) unavailable at {ENTRY.parent.parent} (configuration stage): no default. ")


def test_the_stage_names_and_remedies_follow_the_design() -> None:
    """The design's eleven stages and the reporting stage, each with its remedy; the lock wait reuses the lock's own remedy."""
    assert [stage.value for stage in Stage] == [
        "platform", "containment", "budget-setting", "configuration", "permission", "lock-wait", "download", "verification",
        "extraction", "probe", "in-use", "reporting",
    ]
    assert set(REMEDIES) == set(Stage)
    assert REMEDIES[Stage.LOCK_WAIT] == LOCK_WAIT_REMEDY
    assert "Windows 10 or Windows Server 2016" in REMEDIES[Stage.PLATFORM]
    assert "github.com and release-assets.githubusercontent.com" in REMEDIES[Stage.DOWNLOAD]
    assert "300 through 3600" in REMEDIES[Stage.BUDGET_SETTING]
    assert REMEDIES[Stage.EXTRACTION] == REMEDIES[Stage.PROBE] == "Delete the named staging or entry directory, then retry"


@pytest.mark.parametrize("stage", list(Stage))
def test_no_remedy_asks_to_install_git_cliff_or_change_path(stage: Stage) -> None:
    """Provisioning owns git-cliff: no remedy points at a global install."""
    remedy = REMEDIES[stage].lower()
    assert "install" not in remedy
    assert "path" not in remedy.replace("named", "")


@pytest.mark.parametrize("stage", [Stage.PROBE, Stage.EXTRACTION, Stage.VERIFICATION, Stage.IN_USE])
def test_the_probe_and_metadata_remedies_never_mention_the_budget_variable(stage: Stage) -> None:
    """The override raises only the download and wait budgets."""
    assert DOWNLOAD_BUDGET_VARIABLE not in REMEDIES[stage]


def test_a_permission_failure_names_the_nearest_existing_directory_above_the_refused_path(tmp_path: Path) -> None:
    """A refused mkdir deep below a missing folder names the directory that needs write access."""
    tooling = tmp_path / "tooling"
    tooling.mkdir()
    refused = PermissionError(errno.EACCES, "denied", str(tooling / ".tools" / "git-cliff" / "2.14.2"))
    error = permission_failure("2.14.2", refused, ENTRY)
    assert (error.stage, error.path, error.version) == (Stage.PERMISSION, tooling, "2.14.2")
    assert error.detail == f"cannot write below {tooling}: {refused}"


def test_a_refused_file_write_names_its_directory(tmp_path: Path) -> None:
    """A refused write of an existing file names the folder holding it."""
    (tmp_path / "owner.json").write_bytes(b"{}")
    error = permission_failure("2.14.2", PermissionError(errno.EACCES, "denied", str(tmp_path / "owner.json")), ENTRY)
    assert error.path == tmp_path


def test_a_permission_failure_without_a_file_name_names_the_fallback() -> None:
    """An error that names no path falls back to the cache place given."""
    assert permission_failure("2.14.2", PermissionError(errno.EACCES, "denied"), ENTRY).path == ENTRY


def test_a_write_refused_elsewhere_names_its_directory_and_the_reported_reason(tmp_path: Path) -> None:
    """A download worker's report gives the path and the reason; the nearest existing directory is named."""
    error = denied_write("2.14.2", str(tmp_path / "gone" / "archive.zip"), "the download worker reported PermissionError: denied", ENTRY)
    assert (error.stage, error.path) == (Stage.PERMISSION, tmp_path)
    assert error.detail == f"cannot write below {tmp_path}: the download worker reported PermissionError: denied"


def test_a_line_is_announced_on_the_given_writer() -> None:
    """The writer receives the whole line."""
    lines: list[str] = []
    announce(lines.append, "git-cliff 2.14.2: ready at here", version="2.14.2", path=ENTRY)
    assert lines == ["git-cliff 2.14.2: ready at here"]


@pytest.mark.parametrize("failure", [OSError(errno.EPIPE, "Broken pipe"), ValueError("I/O operation on closed file.")])
def test_a_line_the_stream_cannot_take_is_the_reporting_stage(failure: Exception) -> None:
    """A broken or closed standard error is a typed provisioning failure, status 2, with its error as cause."""

    def broken(line: str) -> None:
        del line
        raise failure

    with pytest.raises(ProvisioningError) as raised:
        announce(broken, "git-cliff 2.14.2: ready at here", version="2.14.2", path=ENTRY)
    assert (raised.value.stage, raised.value.exit_code, raised.value.path, raised.value.__cause__) == (Stage.REPORTING, 2, ENTRY, failure)
    assert "'git-cliff 2.14.2: ready at here' could not be written to standard error" in raised.value.detail


def test_the_synthetic_pin_reads_in_bytes_below_one_mebibyte() -> None:
    """A small asset still prints one decimal."""
    pin = synthetic_pin()
    assert downloading_line(pin).endswith(f"({pin.size / (1 << 20):.1f} MiB) from GitHub")


# eof
