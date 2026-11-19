"""The download worker runs one archive attempt or metadata lookup and reports one JSON outcome line.

Step 4 of v0.14.0 git-cliff-provisioning (design "Deadline enforcement" and
"Time budgets and retries"; design decision Q06; plan decisions Q10 and Q15).
The parent builds the worker command through the bootstrap with the same
runtime; the arguments round-trip for both modes and anything else is a fatal
outcome. The worker writes exactly one JSON line on its standard output, and
nothing on standard error when it succeeds: the outcome with the received
size and SHA-256 for an archive, or the metadata text, which writes no file.
Its socket timeout is `min(30, remaining)`, and its internal statuses 0, 75
and 65 stand for `ok`, `retryable` and `fatal`; they never reach a caller.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tests.unit.tools.release_workflow.git_cliff_support import Canned, CannedWeb
from tools.release_workflow.git_cliff import download_worker
from tools.release_workflow.git_cliff.download_worker import (
    STATUSES,
    WorkerRequest,
    main,
    parse_request,
    worker_arguments,
    worker_command,
)

_ASSET = "https://github.com/orhun/git-cliff/releases/download/v2.14.2/git-cliff-2.14.2-x86_64-pc-windows-msvc.zip"
_RELEASE = "https://api.github.com/repos/orhun/git-cliff/releases/tags/v2.7.0"
_BODY = bytes(range(256)) * 40
_ARCHIVE = WorkerRequest(mode="archive", url=_ASSET, target=Path("C:/tooling/.staging-1-2-ab/archive.zip"),
                         expected_size=7428304, remaining=299.5)
_METADATA = WorkerRequest(mode="metadata", url=_RELEASE, remaining=60.0)


def _outcome(capsys: pytest.CaptureFixture[str]) -> tuple[dict[str, object], str]:
    """Read the single outcome line and whatever went to standard error."""
    out, err = capsys.readouterr()
    assert out.count("\n") == 1
    assert out.endswith("\n")
    return json.loads(out), err


@pytest.mark.parametrize("request_", [_ARCHIVE, _METADATA])
def test_the_arguments_round_trip_for_both_modes(request_: WorkerRequest) -> None:
    """What the parent passes is exactly what the worker reads back."""
    assert parse_request(worker_arguments(request_)) == request_


def test_the_command_starts_the_bootstrap_with_the_same_runtime() -> None:
    """The worker runs isolated, in UTF-8, through the bootstrap's internal entry kind."""
    runtime, root = Path("C:/llm-shared/venvs/python/Scripts/python.exe"), Path("C:/llm-shared")
    bootstrap = str(root / "tools" / "release_workflow" / "bootstrap.py")
    assert worker_command(runtime, root, _ARCHIVE) == (
        runtime, ["-I", "-X", "utf8", bootstrap, "--entry-kind", "git-cliff-worker", "--", *worker_arguments(_ARCHIVE)])


@pytest.mark.parametrize("arguments", [
    pytest.param([], id="nothing"),
    pytest.param(["--mode", "upload", "--url", _ASSET, "--remaining", "10"], id="unknown-mode"),
    pytest.param(["--mode", "metadata", "--url", "http://api.github.com/x", "--remaining", "10"], id="not-https"),
    pytest.param(["--mode", "archive", "--url", _ASSET, "--remaining", "10"], id="archive-without-target"),
    pytest.param(["--mode", "metadata", "--url", _RELEASE, "--target", "C:/x.zip", "--remaining", "10"], id="metadata-with-target"),
    pytest.param(["--mode", "archive", "--url", _ASSET, "--target", "C:/x.zip", "--expected-size", "-1", "--remaining", "10"],
                 id="negative-size"),
    pytest.param(["--mode", "archive", "--url", _ASSET, "--target", "C:/x.zip", "--expected-size", "1e3", "--remaining", "10"],
                 id="size-not-digits"),
    pytest.param(["--mode", "metadata", "--url", _RELEASE, "--remaining", "0"], id="no-time-left"),
    pytest.param(["--mode", "metadata", "--url", _RELEASE, "--remaining", "inf"], id="unbounded-time"),
    pytest.param(["--mode", "metadata", "--url", _RELEASE, "--remaining", "soon"], id="time-not-a-number"),
    pytest.param(["--mode", "metadata", "--mode", "metadata", "--url", _RELEASE, "--remaining", "10"], id="duplicate"),
    pytest.param(["--mode", "metadata", "--url", _RELEASE, "--remaining", "10", "--retry-after", "2000"], id="unknown-option"),
    pytest.param(["--mode", "metadata", "--url", _RELEASE, "--remaining"], id="missing-value"),
])
def test_invalid_arguments_are_a_fatal_outcome(arguments: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    """A command the parent could not have built is reported, never attempted."""
    web = CannedWeb({})
    assert main(arguments, opener=web.opener()) == STATUSES["fatal"]
    outcome, _ = _outcome(capsys)
    assert outcome["outcome"] == "fatal"
    assert str(outcome["error"]).startswith("invalid worker arguments: ")
    assert web.opened == []


def test_an_archive_attempt_reports_its_size_and_digest(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """One ok line with the received size and SHA-256, the bytes in the target, a socket timeout of the remaining time."""
    web, target = CannedWeb({_ASSET: Canned(body=_BODY)}), tmp_path / "archive.zip"
    request = WorkerRequest(mode="archive", url=_ASSET, target=target, expected_size=len(_BODY), remaining=12.5)
    assert main(worker_arguments(request), opener=web.opener()) == STATUSES["ok"]
    outcome, err = _outcome(capsys)
    assert (outcome, err) == ({"outcome": "ok", "size": len(_BODY), "sha256": hashlib.sha256(_BODY).hexdigest()}, "")
    assert (target.read_bytes(), web.opened) == (_BODY, [(_ASSET, 12.5)])


def test_a_metadata_lookup_writes_no_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                          capsys: pytest.CaptureFixture[str]) -> None:
    """The metadata text is the outcome; the socket timeout is capped at 30 s; nothing is written."""
    monkeypatch.chdir(tmp_path)
    body = '{"tag_name": "v2.7.0", "assets": []}'
    web = CannedWeb({_RELEASE: Canned(body=body.encode())})
    request = WorkerRequest(mode="metadata", url=_RELEASE, remaining=900.0)
    assert main(worker_arguments(request), opener=web.opener()) == STATUSES["ok"]
    assert _outcome(capsys) == ({"outcome": "ok", "metadata": body}, "")
    assert (web.opened, list(tmp_path.iterdir())) == ([(_RELEASE, 30)], [])


@pytest.mark.parametrize(("answer", "outcome"), [
    pytest.param(Canned(status=503), "retryable", id="server-error"),
    pytest.param(Canned(status=404), "fatal", id="not-found"),
    pytest.param(Canned(stall=True), "retryable", id="stalled"),
    pytest.param(Canned(body=_BODY + b"!"), "fatal", id="size-overflow"),
])
def test_failures_report_their_class_and_status(tmp_path: Path, capsys: pytest.CaptureFixture[str], answer: Canned,
                                                outcome: str) -> None:
    """A failed attempt is one line with its class and the error; the status follows the class."""
    web = CannedWeb({_ASSET: answer})
    request = WorkerRequest(mode="archive", url=_ASSET, target=tmp_path / "archive.zip", expected_size=len(_BODY), remaining=30.0)
    assert main(worker_arguments(request), opener=web.opener()) == STATUSES[outcome]
    reported, _ = _outcome(capsys)
    assert (reported["outcome"], sorted(reported)) == (outcome, ["error", "outcome"])


def test_the_internal_statuses_stand_for_the_outcomes() -> None:
    """0, 75 and 65 are private to the parent and worker pair."""
    assert STATUSES == {"ok": 0, "retryable": 75, "fatal": 65}


def test_the_production_opener_is_the_network_one(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                                   capsys: pytest.CaptureFixture[str]) -> None:
    """Without an injected opener the worker builds the standard one."""
    web = CannedWeb({_ASSET: Canned(body=_BODY)})
    monkeypatch.setattr(download_worker.network, "build_opener", web.opener)
    request = WorkerRequest(mode="archive", url=_ASSET, target=tmp_path / "archive.zip", expected_size=len(_BODY), remaining=30.0)
    assert main(worker_arguments(request)) == STATUSES["ok"]
    assert _outcome(capsys)[0]["outcome"] == "ok"


# eof
