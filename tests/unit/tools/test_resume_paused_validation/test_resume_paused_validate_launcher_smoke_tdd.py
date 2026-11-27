r"""Launcher wiring and public entry point of the receiver validator.

Step 4 of v0.15.0 resume-paused ships ``bin\resume_paused_validate.bat`` as
the agent-callable read-only validator, separate from the human-only bulk
command. Following the review launcher smoke-test convention, the launcher's
source is checked for self-location, Python selection and argument forwarding,
and ``main`` is called in process: it forwards the command, host, checkout and
carried identity, prints exactly one ASCII-safe UTF-8 JSON object, and exits
0 when valid, 3 when refused and 2 on invalid input or an unexpected failure.
No process starts and no host file is read.
"""

from __future__ import annotations

import io
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from tools import resume_paused_validation as module
from tools.resume_paused_input import CarriedIdentity
from tools.resume_paused_marker import Marker
from tools.resume_paused_models import SessionRole
from tools.resume_paused_profiles import Host, ReadAccount
from tools.resume_paused_validation import (
    ReceiverValidator,
    ValidationRequest,
    ValidationResult,
    default_validator,
    main,
)

LAUNCHER = Path(__file__).resolve().parents[4] / "bin" / "resume_paused_validate.bat"
LAUNCH = "0123456789abcdef0123456789abcdef"
MARKER = Marker(LAUNCH, "77e5f39c-0536-4cbb-a057-f4a1f5c715b0", SessionRole.REQUESTOR, "a" * 64)
REFUSED = 3
INVALID = 2


class RecordingValidator:
    """Declared validation outcome, recording the forwarded request."""

    def __init__(self, result: ValidationResult | Exception) -> None:
        """Keep the result or the failure to raise."""
        self.result = result
        self.requests: list[ValidationRequest] = []

    def validate(self, request: ValidationRequest) -> ValidationResult:
        """Record the request and return the declared result."""
        self.requests.append(request)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def outcome(*, valid: bool) -> ValidationResult:
    """Return one declared validation result."""
    reasons = () if valid else ("pane-absent",)
    return ValidationResult(valid, reasons, Host.CODEX, MARKER, consumed=False, live=None, carried_session="s" if valid else None, account=ReadAccount())


def run(argv: list[str], validator: RecordingValidator) -> tuple[int, dict[str, object], str]:
    """Run ``main`` in process and return its exit code, JSON object and raw output."""
    out = io.StringIO()
    code = main(argv, stdout=out, factory=lambda: validator)
    text = out.getvalue()
    return code, json.loads(text), text


def test_launcher_self_locates_and_forwards_every_argument() -> None:
    """The launcher runs the validator module with the llm-shared Python and all arguments."""
    source = LAUNCHER.read_text(encoding="utf-8")
    assert r'"%LLM_SHARED_DIR%\tools\resume_paused_validation.py" %*' in source
    assert 'if not defined LLM_SHARED_DIR set "LLM_SHARED_DIR=%~dp0.."' in source
    assert "exit /b %ERRORLEVEL%" in source
    assert "resume_paused.bat" not in source


def test_valid_receiver_prints_one_json_object_and_exits_zero() -> None:
    """Arguments reach the validator unchanged; the JSON is one ASCII line."""
    validator = RecordingValidator(outcome(valid=True))
    code, data, text = run(
        ["--command", "/resume-session --resume-paused x", "--host", "codex", "--project-root", "C:/work/checkout",
         "--carried-session", "s", "--carried-launch-id", LAUNCH],
        validator,
    )
    assert (code, data["valid"], data["carried"]) == (0, True, {"session_id": "s", "launch_id": LAUNCH})
    assert text.count("\n") == 1
    assert text.isascii()
    request = validator.requests[0]
    assert (request.command, request.host, request.carried) == ("/resume-session --resume-paused x", Host.CODEX, CarriedIdentity("s", LAUNCH))
    assert request.project_root == Path("C:/work/checkout").absolute()


def test_refused_receiver_exits_three_with_the_compact_failure_line() -> None:
    """A refusal is an expected stop that still names its reason and result line."""
    validator = RecordingValidator(outcome(valid=False))
    code, data, _text = run(["--command", "c", "--host", "claude"], validator)
    assert (code, data["reasons"], data["result"]) == (REFUSED, ["pane-absent"], f"resume-paused {LAUNCH} failed")
    assert validator.requests[0].carried is None


@pytest.mark.parametrize(
    ("argv", "result"),
    [
        (["--host", "codex"], outcome(valid=True)),
        (["--command", "c", "--host", "gemini"], outcome(valid=True)),
        (["--command", "c", "--host", "codex"], RuntimeError("unexpected")),
    ],
    ids=["missing command", "unknown host", "unexpected failure"],
)
def test_invalid_input_and_failures_exit_two_with_one_json_object(argv: list[str], result: ValidationResult | Exception) -> None:
    """Invalid arguments and unexpected failures still print one JSON object."""
    code, data, _text = run(argv, RecordingValidator(result))
    assert (code, data["valid"], data["reasons"]) == (INVALID, False, ["invalid-input"])


def test_default_composition_binds_the_receiving_terminal() -> None:
    """Both receivers validate against the same shared dispatch."""
    environ = {"TUIOS_PANE_ID": MARKER.pane_id}
    composed = default_validator(environ, lambda: datetime(2026, 11, 19, tzinfo=UTC))
    assert isinstance(composed, ReceiverValidator)
    assert composed.environ is environ
    assert composed.provers == {}


def test_clock_is_timezone_aware() -> None:
    """The launcher's clock returns an aware instant."""
    assert module._now().tzinfo is not None  # noqa: SLF001 - the launcher's injected clock


def test_main_without_a_factory_composes_the_default_validator(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without an injected factory, ``main`` builds the default composition."""
    built: list[object] = []

    def compose(environ: object, clock: object) -> RecordingValidator:
        """Record the composition and return a declared validator."""
        built.append((environ, clock))
        return RecordingValidator(outcome(valid=False))

    monkeypatch.setattr(module, "default_validator", compose)
    out = io.StringIO()
    assert main(["--command", "c", "--host", "codex"], stdout=out) == REFUSED
    assert len(built) == 1


# eof
