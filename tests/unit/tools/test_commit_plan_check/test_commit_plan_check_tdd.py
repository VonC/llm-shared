"""Tests for typed, read-only commit-plan readiness evidence.

Step 2 exposes the same parser, staged inventory, and validator through a
side-effect-free service, a platform-neutral CLI, and a root batch launcher.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import commit_plan_check
from tools.git_batch_commit_models import (
    CommitBlock,
    CommitMessageError,
    CommitPlanGroup,
    CommitPlanSubjectRequirement,
    CommitPlanValidation,
)

# Test doubles intentionally replace typed command boundaries with small lambdas.
# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false

READY_BLOCK = CommitBlock(
    git_adds=["git add -- docs/example.md"],
    commit_message="feat(check): expose evidence\n\nWhy:\n- Needed.\n\nWhat:\n- Added.",
    commit_title="feat(check): expose evidence",
)
READY_GROUP = CommitPlanGroup(
    position=1,
    subject="feat(check): expose evidence",
    paths=("docs/example.md",),
)
OPERATIONAL_STATUS = 2
NON_READY_STATUS = 3


def _repository(tmp_path: Path, content: str | None = "plan") -> Path:
    """Create the minimum repository markers and optional root plan."""
    (tmp_path / ".git").mkdir()
    if content is not None:
        (tmp_path / "a.commit").write_text(content, encoding="utf-8")
    return tmp_path


def _install_ready_collaborators(
    monkeypatch: pytest.MonkeyPatch,
) -> list[tuple[object, ...]]:
    """Install recording parser, inventory, and validator collaborators."""
    calls: list[tuple[object, ...]] = []

    def parse(content: str, *, interactive: bool = True) -> list[CommitBlock]:
        calls.append(("parse", content, interactive))
        return [READY_BLOCK]

    def inventory(root: Path) -> tuple[str, ...]:
        calls.append(("inventory", root))
        return ("docs/example.md",)

    def validate(
        blocks: list[CommitBlock],
        paths: tuple[str, ...],
        requirements: tuple[CommitPlanSubjectRequirement, ...],
    ) -> CommitPlanValidation:
        calls.append(("validate", blocks, paths, requirements))
        return CommitPlanValidation((READY_GROUP,), ())

    monkeypatch.setattr(commit_plan_check, "parse_clipboard_content", parse)
    monkeypatch.setattr(commit_plan_check, "staged_paths", inventory)
    monkeypatch.setattr(
        commit_plan_check,
        "completed_validation_subject_requirements",
        lambda root, paths: calls.append(("requirements", root, paths)) or (),
    )
    monkeypatch.setattr(commit_plan_check, "validate_commit_plan", validate)
    return calls


def test_ready_service_uses_each_public_boundary_once(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A ready result preserves exact ordered inputs from all shared APIs."""
    root = _repository(tmp_path, "commit plan\n")
    calls = _install_ready_collaborators(monkeypatch)

    result = commit_plan_check.check_commit_plan(root)

    assert result.state is commit_plan_check.CommitPlanCheckState.VALID
    assert result.ready is True
    assert result.groups == (READY_GROUP,)
    assert result.staged_paths == ("docs/example.md",)
    assert result.diagnostics == ()
    assert calls == [
        ("parse", "commit plan\n", False),
        ("inventory", root),
        ("requirements", root, ("docs/example.md",)),
        ("validate", [READY_BLOCK], ("docs/example.md",), ()),
    ]


@pytest.mark.parametrize(
    ("content", "expected_state"),
    [
        (None, commit_plan_check.CommitPlanCheckState.MISSING_PLAN),
        ("", commit_plan_check.CommitPlanCheckState.EMPTY_PLAN),
        (" \n\t", commit_plan_check.CommitPlanCheckState.EMPTY_PLAN),
    ],
)
def test_missing_and_empty_plans_fail_closed_before_collaborators(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    content: str | None,
    expected_state: commit_plan_check.CommitPlanCheckState,
) -> None:
    """Absent or blank input has a distinct non-ready typed result."""
    root = _repository(tmp_path, content)
    monkeypatch.setattr(
        commit_plan_check,
        "parse_clipboard_content",
        lambda *_args, **_kwargs: pytest.fail("parser called"),
    )
    monkeypatch.setattr(
        commit_plan_check,
        "staged_paths",
        lambda _root: pytest.fail("inventory called"),
    )

    result = commit_plan_check.check_commit_plan(root)

    assert result.state is expected_state
    assert result.ready is False
    assert result.groups == ()
    assert result.staged_paths == ()
    assert len(result.diagnostics) == 1


def test_nonempty_content_without_blocks_is_an_empty_plan(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A parser result without commit blocks cannot be ready."""
    root = _repository(tmp_path)
    monkeypatch.setattr(
        commit_plan_check,
        "parse_clipboard_content",
        lambda _content, *, interactive: []
        if interactive is False
        else pytest.fail("interactive parse"),
    )
    monkeypatch.setattr(
        commit_plan_check,
        "staged_paths",
        lambda _root: pytest.fail("inventory called"),
    )

    result = commit_plan_check.check_commit_plan(root)

    assert result.state is commit_plan_check.CommitPlanCheckState.EMPTY_PLAN
    assert result.diagnostics == ("a.commit contains no commit groups",)


@pytest.mark.parametrize(
    ("paths", "validation", "expected_state"),
    [
        (
            (),
            CommitPlanValidation(
                (READY_GROUP,),
                ("planned path is not staged: docs/example.md",),
            ),
            commit_plan_check.CommitPlanCheckState.EMPTY_STAGED_SET,
        ),
        (
            ("other.md",),
            CommitPlanValidation(
                (READY_GROUP,),
                (
                    "planned path is not staged: docs/example.md",
                    "staged path is missing from the plan: other.md",
                ),
            ),
            commit_plan_check.CommitPlanCheckState.INVALID_PLAN,
        ),
    ],
)
def test_nonready_validation_preserves_groups_paths_and_all_diagnostics(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    paths: tuple[str, ...],
    validation: CommitPlanValidation,
    expected_state: commit_plan_check.CommitPlanCheckState,
) -> None:
    """Empty inventory and validator failure remain distinguishable."""
    root = _repository(tmp_path)
    monkeypatch.setattr(
        commit_plan_check,
        "parse_clipboard_content",
        lambda _content, *, interactive: [READY_BLOCK]
        if interactive is False
        else pytest.fail("interactive parse"),
    )
    monkeypatch.setattr(commit_plan_check, "staged_paths", lambda _root: paths)
    calls: list[tuple[list[CommitBlock], tuple[str, ...]]] = []

    def validate(
        blocks: list[CommitBlock],
        staged: tuple[str, ...],
        requirements: tuple[CommitPlanSubjectRequirement, ...],
    ) -> CommitPlanValidation:
        assert requirements == ()
        calls.append((blocks, staged))
        return validation

    monkeypatch.setattr(commit_plan_check, "validate_commit_plan", validate)
    monkeypatch.setattr(
        commit_plan_check,
        "completed_validation_subject_requirements",
        lambda _root, _paths: (),
    )

    result = commit_plan_check.check_commit_plan(root)

    assert result.state is expected_state
    assert result.groups == (READY_GROUP,)
    assert result.staged_paths == paths
    assert result.diagnostics == validation.diagnostics
    assert calls == [([READY_BLOCK], paths)]


def test_malformed_plan_is_expected_invalidity(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A public parser diagnostic becomes quotable non-ready evidence."""
    root = _repository(tmp_path)

    def malformed(_content: str, *, interactive: bool) -> list[CommitBlock]:
        assert interactive is False
        message = "missing What section"
        raise CommitMessageError(message, [])

    monkeypatch.setattr(commit_plan_check, "parse_clipboard_content", malformed)

    result = commit_plan_check.check_commit_plan(root)

    assert result.state is commit_plan_check.CommitPlanCheckState.INVALID_PLAN
    assert result.diagnostics == ("cannot parse a.commit: missing What section",)


@pytest.mark.parametrize(
    ("boundary", "message"),
    [
        ("read", "access denied"),
        ("inventory", "git failed"),
    ],
)
def test_operational_failures_return_stable_typed_diagnostics(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    boundary: str,
    message: str,
) -> None:
    """I/O and Git failures cannot claim that the plan itself is invalid."""
    root = _repository(tmp_path)
    if boundary == "read":
        monkeypatch.setattr(
            commit_plan_check,
            "_read_plan",
            lambda _path: (_ for _ in ()).throw(OSError(message)),
        )
    else:
        monkeypatch.setattr(
            commit_plan_check,
            "parse_clipboard_content",
            lambda _content, *, interactive: [READY_BLOCK]
            if interactive is False
            else pytest.fail("interactive parse"),
        )
        monkeypatch.setattr(
            commit_plan_check,
            "staged_paths",
            lambda _root: (_ for _ in ()).throw(OSError(message)),
        )

    result = commit_plan_check.check_commit_plan(root)

    assert result.state is commit_plan_check.CommitPlanCheckState.OPERATIONAL_FAILURE
    assert result.ready is False
    assert result.diagnostics == (f"cannot {boundary} commit plan: {message}",)


def test_structured_payload_has_the_exact_stable_schema() -> None:
    """JSON evidence preserves declared key order and typed group ordering."""
    result = commit_plan_check.CommitPlanCheckResult(
        state=commit_plan_check.CommitPlanCheckState.INVALID_PLAN,
        groups=(READY_GROUP,),
        diagnostics=("first", "second"),
        staged_paths=("docs/example.md", "other.md"),
    )

    payload = result.structured_payload()

    assert list(payload) == [
        "schema_version",
        "state",
        "ready",
        "staged_paths",
        "groups",
        "diagnostics",
    ]
    assert payload == {
        "schema_version": 1,
        "state": "invalid-plan",
        "ready": False,
        "staged_paths": ["docs/example.md", "other.md"],
        "groups": [
            {
                "position": 1,
                "subject": "feat(check): expose evidence",
                "paths": ["docs/example.md"],
            },
        ],
        "diagnostics": ["first", "second"],
    }


def test_human_and_json_renderers_are_deterministic_and_equivalent() -> None:
    """Both projections contain the same state, groups, paths, and diagnostics."""
    result = commit_plan_check.CommitPlanCheckResult(
        state=commit_plan_check.CommitPlanCheckState.INVALID_PLAN,
        groups=(READY_GROUP,),
        diagnostics=("first", "second"),
        staged_paths=("docs/example.md", "other.md"),
    )

    assert commit_plan_check.render_human(result) == (
        "state: invalid-plan\n"
        "ready: false\n"
        "group 1: feat(check): expose evidence\n"
        "group 1 path: docs/example.md\n"
        "staged path: docs/example.md\n"
        "staged path: other.md\n"
        "diagnostic: first\n"
        "diagnostic: second"
    )
    assert json.loads(commit_plan_check.render_json(result)) == result.structured_payload()


@pytest.mark.parametrize(
    ("state", "diagnostics", "expected_status", "expected_stream"),
    [
        (commit_plan_check.CommitPlanCheckState.VALID, (), 0, "out"),
        (
            commit_plan_check.CommitPlanCheckState.MISSING_PLAN,
            ("evidence",),
            3,
            "out",
        ),
        (
            commit_plan_check.CommitPlanCheckState.OPERATIONAL_FAILURE,
            ("evidence",),
            2,
            "err",
        ),
    ],
)
def test_main_maps_states_to_status_and_stream(  # noqa: PLR0913
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    state: commit_plan_check.CommitPlanCheckState,
    diagnostics: tuple[str, ...],
    expected_status: int,
    expected_stream: str,
) -> None:
    """The adapter reserves stderr and status two for operational failure."""
    root = _repository(tmp_path)
    result = commit_plan_check.CommitPlanCheckResult(
        state=state,
        diagnostics=diagnostics,
    )
    monkeypatch.setattr(commit_plan_check, "check_commit_plan", lambda _root: result)

    status = commit_plan_check.main(["--root", str(root), "--format", "json"])

    captured = capsys.readouterr()
    assert status == expected_status
    rendered = commit_plan_check.render_json(result)
    if expected_stream == "out":
        assert captured.out == f"{rendered}\n"
        assert captured.err == ""
    else:
        assert captured.out == ""
        assert captured.err == "commit-plan-check: evidence\n"


def test_main_defaults_to_human_and_discovers_root_upward(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """No root or format arguments select discovery and human output."""
    root = _repository(tmp_path)
    nested = root / "nested"
    nested.mkdir()
    starts: list[Path] = []
    result = commit_plan_check.CommitPlanCheckResult(
        state=commit_plan_check.CommitPlanCheckState.VALID,
    )
    monkeypatch.setattr(Path, "cwd", classmethod(lambda _cls: nested))
    monkeypatch.setattr(
        commit_plan_check,
        "find_project_root",
        lambda start: starts.append(start) or root,
    )
    monkeypatch.setattr(commit_plan_check, "check_commit_plan", lambda _root: result)

    assert commit_plan_check.main([]) == 0
    assert capsys.readouterr().out == "state: valid\nready: true\n"
    assert starts == [nested]


@pytest.mark.parametrize(
    "arguments",
    [
        ["--format", "xml"],
        ["--root"],
    ],
)
def test_invalid_arguments_return_two_without_running_service(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    arguments: list[str],
) -> None:
    """Invalid invocation has stable stderr without an argparse process exit."""
    monkeypatch.setattr(
        commit_plan_check,
        "check_commit_plan",
        lambda _root: pytest.fail("service called"),
    )

    assert commit_plan_check.main(arguments) == OPERATIONAL_STATUS
    assert "commit-plan-check:" in capsys.readouterr().err


def test_invalid_explicit_root_and_unexpected_error_return_two(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Root validation and unexpected service errors share operational status."""
    assert commit_plan_check.main(["--root", str(tmp_path)]) == OPERATIONAL_STATUS
    assert "not a Git repository root" in capsys.readouterr().err

    root = _repository(tmp_path)
    monkeypatch.setattr(
        commit_plan_check,
        "check_commit_plan",
        lambda _root: (_ for _ in ()).throw(RuntimeError("surprise")),
    )
    assert commit_plan_check.main(["--root", str(root)]) == OPERATIONAL_STATUS
    assert "unexpected failure: surprise" in capsys.readouterr().err


# eof
