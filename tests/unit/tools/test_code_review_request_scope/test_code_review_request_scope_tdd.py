"""Scope evidence reuses validated identity, declared commands and proof validity.

The round-trip test caches real resolutions of its stable, symlink-free paths
to avoid repeatedly paying Windows filesystem lookup cost at every boundary.
Transcript commands preserve HTML-like text, dunder paths and backtick runs.
"""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime
from functools import cache
from pathlib import Path

import pytest

from tests.unit.tools.groundhog_acceptance_support import make_deps
from tests.unit.tools.groundhog_group_support import CoverageSpawns, group_project
from tests.unit.tools.review_exchange_test_support import (
    common_arguments,
    review_artifact,
    review_policy,
)
from tests.unit.tools.test_code_review_request.test_code_review_request_tdd import (
    _always_ignored,
    _captured_tree,
    _checked_plan,
    _cli_args,
    _cli_files,
    _round_input,
)
from tools import code_review_request as renderer
from tools import code_review_request_scope as scopes
from tools import code_review_validation as validation
from tools import effort_scope
from tools import review_exchange_cli as exchange_cli
from tools.groundhog import cli, exclusions, floor, snapshot
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    ExchangeIdentity,
    ReviewConfiguration,
    ReviewDisposition,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_envelope import parse_envelope_markdown
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore
from tools.scope_capture import WHOLE_SCOPE, validate_capture

_FATAL_EXIT = 2


@pytest.mark.parametrize(("command", "span"), [
    ("ghog affected --scope-file=<paths.scope>", "`ghog affected --scope-file=<paths.scope>`"),
    ("rg __init__.py tools", "`rg __init__.py tools`"),
    ("echo `literal` value", "``echo `literal` value``"),
    ("echo ``literal`` value", "```echo ``literal`` value```"),
    ("`script` argument", "`` `script` argument ``"),
    ("echo `literal`", "`` echo `literal` ``"),
])
def test_transcript_validation_commands_stay_literal(
    tmp_path: Path, command: str, span: str,
) -> None:
    """Publication cannot turn command punctuation into transcript Markdown."""
    source = replace(
        _round_input(tmp_path),
        resolved_validation_set=validation.resolve_code_review_validation((command,)),
    )

    rendered = renderer.render_code_review_request(source)
    _, authored = parse_envelope_markdown(rendered.request_content)
    evidence = json.loads(authored.split("```json\n", 1)[1].split("\n```", 1)[0])

    assert f"- {span} (sources: project)" in rendered.transcript_summary
    assert evidence["resolved_validation_set"]["commands"] == [
        {"command": command, "sources": ["project"]},
    ]


def test_default_scope_and_declared_commands(tmp_path: Path) -> None:
    """Only the built-in policy receives a selector; additions stay literal."""
    default = validation.load_project_validation(tmp_path)
    assert not default.declared
    assert validation.complete_project_default(default, "--group=sentinel") == (
        "ghog day --full=speed --group=sentinel",
    )
    (tmp_path / ".review-validation").write_text("ghog day\nproject-check\n", encoding="utf-8")
    declared = validation.load_project_validation(tmp_path)
    assert declared.declared
    assert validation.complete_project_default(declared, "--whole-suite") == declared.commands
    resolved = validation.resolve_code_review_validation(
        declared.commands, ("plan-check",), ("request-check",),
    )
    assert resolved.command_lines == ("ghog day", "project-check", "plan-check", "request-check")
    notice = validation.migration_notice(declared)
    assert all(value in notice for value in ("GHOG_FULL", "saved proof", "another declared command"))
    assert validation.migration_notice(default) == ""


@pytest.mark.parametrize(("command", "claims"), [
    ("ghog day --full=speed --group=sentinel", True),
    ("ghog day --full=cov --group=sentinel", False),
    ("ghog day --full=speed --group=other", False),
    ("ghog full --full=speed --group=sentinel", False),
    ("echo ghog day --full=speed --group=sentinel", False),
    ("ghog day --full=speed --full=cov --group=sentinel", False),
    ("ghog day --full=speed --group=sentinel --group=other", False),
    ("ghog day --full=speed --group=sentinel --whole-suite", False),
    ("ghog day --full=speed --group=sentinel --scope-file=file", False),
])
def test_declared_group_statement(command: str, *, claims: bool) -> None:
    """A declaration only claims speed for its exact explicitly named walk."""
    policy = validation.ProjectValidation((command,), declared=True)
    statement = validation.group_claim_statement(policy, "sentinel")
    assert ("no speed proof" not in statement) is claims
    assert "sentinel" in statement


def test_requirement_scope_and_current_proof(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Validated identity selects the requirement and proof uses the shared rule."""
    plan = tmp_path / "docs/plan.v0.13.0.topic.md"
    plan.parent.mkdir()
    plan.write_text("# Plan\n", encoding="utf-8")
    requirement = plan.with_name("feature-request.v0.13.0.topic.md")
    requirement.write_text("# Requirement\n", encoding="utf-8")
    identity = ExchangeIdentity(ReviewFamily.CODE, "code", "v0.13.0", "topic")
    resolved = scopes.resolve_request_scope(tmp_path, plan, identity)
    assert resolved.scope == WHOLE_SCOPE
    assert resolved.source_path == requirement
    seen: list[tuple[Path, str, str]] = []

    def proof(root: Path, key: str, fingerprint: str) -> snapshot.EffectiveProof:
        seen.append((root, key, fingerprint))
        return snapshot.EffectiveProof("digest", None)

    monkeypatch.setattr(snapshot, "effective_proof", proof)
    evidence = scopes.scope_evidence(tmp_path, resolved)
    assert evidence == {
        "scope": "whole", "group": None, "fingerprint": WHOLE_SCOPE.fingerprint,
        "requirement": requirement.relative_to(tmp_path).as_posix(), "proof": "missing",
    }
    assert seen == [(tmp_path, "whole", WHOLE_SCOPE.fingerprint)]


def test_invalid_effort_is_not_silently_whole(tmp_path: Path) -> None:
    """Invalid requirement groups retain their source and cause."""
    plan = tmp_path / "docs/plan.v0.13.0.topic.md"
    plan.parent.mkdir()
    plan.with_name("feature-request.v0.13.0.topic.md").write_text(
        "# Requirement\n\n- Test group: missing\n", encoding="utf-8",
    )
    identity = ExchangeIdentity(ReviewFamily.CODE, "code", "v0.13.0", "topic")
    with pytest.raises(effort_scope.EffortScopeError, match=r"feature-request.*ghog-groups"):
        scopes.resolve_request_scope(tmp_path, plan, identity)


def test_scope_change_requires_reason() -> None:
    """A changed fingerprint requires an explicit nonempty explanation."""
    previous = {"scope": "group:old", "fingerprint": "old"}
    current = {"scope": "whole", "fingerprint": WHOLE_SCOPE.fingerprint}
    with pytest.raises(ValueError, match=r"group:old.*whole"):
        scopes.scope_change_block(previous, current, None)
    block = scopes.scope_change_block(previous, current, "Broaden validation.")
    assert all(text in block for text in ("Scope change", "group:old", "whole", "Broaden validation."))
    assert scopes.scope_change_block(current, current, None) == ""
    assert scopes.scope_change_block(None, current, None) == ""


def _render(root: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, dict[str, Path], list[str]]:
    """Build renderer inputs with only Git and commit readiness substituted."""
    plan = root / "docs/plan.v0.13.0.topic.md"
    plan.parent.mkdir(exist_ok=True)
    plan.write_text("# Plan\n", encoding="utf-8")
    files = _cli_files(root)
    arguments = _cli_args(plan, files)
    monkeypatch.setattr(renderer.files, "is_effectively_ignored", _always_ignored)
    monkeypatch.setattr(renderer, "check_commit_plan", _checked_plan)
    monkeypatch.setattr(renderer, "capture_index_tree", _captured_tree)
    return plan, files, arguments


def _assert_proof(root: Path, files: dict[str, Path], arguments: list[str], proof: str) -> str:
    """Check the rendered proof against its validated capture and return the prose."""
    assert renderer.main(arguments, project_root=root) == 0
    envelope, authored = parse_envelope_markdown(files["content"].read_text(encoding="utf-8"))
    assert envelope.test_scope is not None
    assert envelope.test_scope["proof"] == proof
    capture = validate_capture(root, files["summary"].with_name("a.scope.json").read_text(encoding="utf-8"))
    assert capture.fingerprint == envelope.test_scope["fingerprint"]
    return authored


@pytest.mark.parametrize("selector", ["--whole-suite", "--group=sentinel"])
@pytest.mark.parametrize("change", ["floor", "exclusions"])
def test_rendered_proof_downgrades_and_recovers(  # noqa: PLR0913
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
    selector: str, change: str,
) -> None:
    """Real walks and rendering share timing invalidation for both scope kinds."""
    group_project(tmp_path)
    plan, files, arguments = _render(tmp_path, monkeypatch)
    requirement = plan.with_name("feature-request.v0.13.0.topic.md")
    requirement.write_text("# Requirement\n" + ("- Test group: sentinel\n" if "group" in selector else ""), encoding="utf-8")
    spawns = CoverageSpawns(tmp_path)
    spawns._lines.extend(["=== slowest durations ===", "0.10s call tests/sentinel/test_core.py::test_ok"])
    walk = ["day", "--full=speed", selector, "--root", str(tmp_path)]
    assert cli.main(walk, make_deps(spawns)) == 0
    _assert_proof(tmp_path, files, arguments, "speed")
    if change == "floor":
        floor.write_floor(tmp_path, 99, 2.0)
    else:
        exclusions.write_exclusions(tmp_path, {"tests/other/test_core.py::test_ok": 5.0})
    _assert_proof(tmp_path, files, arguments, "cov")
    assert cli.main(walk, make_deps(spawns)) == 0
    authored = _assert_proof(tmp_path, files, arguments, "speed")
    assert f"ghog day --full=speed {selector}" in authored
    capsys.readouterr()


def test_cli_requires_capture_and_rejects_invalid_effort(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """Required capture and invalid group errors happen before paired outputs."""
    plan, files, arguments = _render(tmp_path, monkeypatch)
    assert renderer.main(arguments[:-2], project_root=tmp_path) == _FATAL_EXIT
    assert "--scope-capture-output" in capsys.readouterr().err
    plan.with_name("feature-request.v0.13.0.topic.md").write_text("- Test group: unknown\n", encoding="utf-8")
    assert renderer.main(arguments, project_root=tmp_path) == _FATAL_EXIT
    assert "ghog-groups" in capsys.readouterr().err
    assert not files["content"].exists()


def test_cli_rejects_unsupported_plan_layout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """Workflow lookup failures become stable renderer errors before output."""
    plan, files, arguments = _render(tmp_path, monkeypatch)
    unsupported = tmp_path / plan.name
    plan.rename(unsupported)
    arguments[arguments.index("--plan") + 1] = str(unsupported)

    assert renderer.main(arguments, project_root=tmp_path) == _FATAL_EXIT
    assert "Unrecognized canonical parent" in capsys.readouterr().err
    assert not files["content"].exists()


def test_request_without_requirement_reports_whole_scope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A supported plan without a requirement explicitly reports the fallback."""
    _plan, files, arguments = _render(tmp_path, monkeypatch)

    _assert_proof(tmp_path, files, arguments, "missing")

    envelope, _ = parse_envelope_markdown(files["content"].read_text(encoding="utf-8"))
    assert envelope.test_scope is not None
    assert envelope.test_scope["scope"] == "whole"
    assert envelope.test_scope["requirement"] is None


def _exchange_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[
    exchange_cli.Runtime, ReviewExchangeCore, dict[str, Path], list[str],
]:
    """Use the real exchange with only process, activation and Git seams replaced."""
    group_project(tmp_path)
    plan, files, arguments = _render(tmp_path, monkeypatch)
    arguments[arguments.index("--round-number") + 1] = "1"
    requirement = plan.with_name("feature-request.v0.13.0.topic.md")
    requirement.write_text("# Requirement\n- Test group: sentinel\n", encoding="utf-8")
    context = renderer.code_review_context(plan, "1")
    paths = derive_artifact_paths(tmp_path, context)
    store = ReviewExchangeStore(paths)
    configuration = ReviewConfiguration(enabled=True)
    core = ReviewExchangeCore(store, context, review_policy(context), configuration,
                              wall_clock=lambda: datetime(2026, 10, 4, 12, tzinfo=UTC))
    runtime = exchange_cli.Runtime(tmp_path, context, paths, configuration, core)
    def root_for(_path: Path) -> Path:
        return tmp_path

    def runtime_for(*_args: object) -> exchange_cli.Runtime:
        return runtime

    def activated(_runtime: exchange_cli.Runtime) -> None:
        return None

    monkeypatch.setattr(exchange_cli, "find_project_root", root_for)
    monkeypatch.setattr(exchange_cli, "_build_runtime", runtime_for)
    monkeypatch.setattr(exchange_cli, "_require_activation", activated)
    monkeypatch.setattr(exchange_cli, "_is_effectively_ignored", _always_ignored)
    core.start()
    return runtime, core, files, arguments


def _owned_cli(core: ReviewExchangeCore, arguments: list[str]) -> int:
    """Present the current in-memory capability through the actual CLI boundary."""
    capability = core.ownership_capability
    assert capability is not None
    return exchange_cli.main([*arguments, "--ownership-generation", str(capability.generation),
                              "--ownership-token", capability.token])


@pytest.fixture
def cached_round_trip_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reuse actual path resolutions only where no symlink or rename changes them."""
    monkeypatch.setattr(Path, "resolve", cache(Path.resolve))


@pytest.mark.usefixtures("cached_round_trip_paths")
def test_render_publish_status_affected_and_replacement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """The reviewer consumes frozen files, and changed replacements demand disclosure."""
    runtime, core, files, arguments = _exchange_fixture(tmp_path, monkeypatch)
    context, paths = runtime.context, runtime.paths
    assert renderer.main(arguments, project_root=tmp_path) == 0
    publication = ["publish-request", *common_arguments(context),
                   "--content-file", str(files["content"]), "--summary-file", str(files["summary"]),
                   "--scope-capture-file", str(files["summary"].with_name("a.scope.json"))]
    assert _owned_cli(core, publication) == 0
    capsys.readouterr()
    assert _owned_cli(core, ["status", *common_arguments(context)]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["bound_scope"]["scope"] == "group:sentinel"
    bound = paths.scope.read_bytes()
    # An unrelated definition edit must not change the reviewer's collection.
    declaration = tmp_path / ".ghog-groups"
    declaration.write_text(declaration.read_text(encoding="utf-8").replace("tests/sentinel/**", "tests/**/*.py"), encoding="utf-8")
    _assert_frozen_affected(tmp_path, status["paths"]["scope"])
    capsys.readouterr()
    reason = _assert_scope_change(tmp_path, files, arguments, capsys)
    assert paths.scope.read_bytes() == bound
    core.publish_answer(review_artifact(context, ReviewRole.REVIEWER, 1,
                        disposition=ReviewDisposition.CHANGES_REQUESTED), "Changes needed.")
    core.consume_answer(reviewed_work_changed=True)
    core.continue_round()
    arguments[arguments.index("--round-number") + 1] = "2"
    assert renderer.main([*arguments, "--scope-change-file", str(reason)], project_root=tmp_path) == 0
    assert _owned_cli(core, publication) == 0
    capsys.readouterr()
    assert paths.scope.read_bytes() != bound


def _assert_scope_change(
    tmp_path: Path, files: dict[str, Path], arguments: list[str], capsys: pytest.CaptureFixture[str],
) -> Path:
    """A replacement discloses its reason and cannot silently change scope."""
    assert renderer.main(arguments, project_root=tmp_path) == _FATAL_EXIT
    assert "--scope-change-file" in capsys.readouterr().err
    reason = files["summary"].with_name("a.scope-change.md")
    reason.write_text("Cover the expanded membership.", encoding="utf-8")
    authored = _assert_proof(tmp_path, files, [*arguments, "--scope-change-file", str(reason)], "missing")
    assert "Scope change:" in authored
    assert "Cover the expanded membership." in authored
    return reason


def _assert_frozen_affected(root: Path, capture: str) -> None:
    """The published capture determines collection even after a declaration edit."""
    spawns = CoverageSpawns(root)
    assert cli.main(["affected", "--no-cov", f"--scope-file={capture}",
                     "--root", str(root)], make_deps(spawns, {"GHOG_GROUP": "other"})) == 0
    assert spawns.commands[-1][-1] == "tests/sentinel/test_core.py"
    assert "tests/other/test_core.py" not in spawns.commands[-1]


def test_legacy_replacement_clears_scope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """A legacy replacement cannot inherit scope evidence from the preceding round."""
    runtime, core, files, arguments = _exchange_fixture(tmp_path, monkeypatch)
    _assert_proof(tmp_path, files, arguments, "missing")
    core.publish_request(files["content"].read_text(encoding="utf-8"),
                         files["summary"].read_text(encoding="utf-8"),
                         files["summary"].with_name("a.scope.json").read_text(encoding="utf-8"))
    core.publish_answer(review_artifact(runtime.context, ReviewRole.REVIEWER, 1,
                        disposition=ReviewDisposition.CHANGES_REQUESTED), "Legacy next.")
    core.consume_answer(reviewed_work_changed=True)
    core.continue_round()
    core.publish_request(review_artifact(runtime.context, ReviewRole.REQUESTOR, 2), "Legacy report.")
    assert exchange_cli.main(["status", *common_arguments(runtime.context)]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["bound_scope"] == "missing"
    assert "scope" not in status["paths"]
    assert not runtime.paths.scope.exists()


def test_definition_edit_invalidates_previously_saved_proof(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An unchanged source digest cannot preserve proof for a changed declaration."""
    group_project(tmp_path)
    plan, files, arguments = _render(tmp_path, monkeypatch)
    plan.with_name("feature-request.v0.13.0.topic.md").write_text(
        "- Test group: sentinel\n", encoding="utf-8",
    )
    assert cli.main(["day", "--full=cov", "--group=sentinel", "--root", str(tmp_path)],
                    make_deps(CoverageSpawns(tmp_path))) == 0
    assert renderer.main(arguments, project_root=tmp_path) == 0
    envelope, _ = parse_envelope_markdown(files["content"].read_text(encoding="utf-8"))
    assert envelope.test_scope is not None
    assert envelope.test_scope["proof"] == "cov"
    declaration = tmp_path / ".ghog-groups"
    declaration.write_text(declaration.read_text(encoding="utf-8").replace(
        "src/sentinel/**", "src/sentinel/*.py",
    ), encoding="utf-8")
    assert renderer.main(arguments, project_root=tmp_path) == 0
    envelope, _ = parse_envelope_markdown(files["content"].read_text(encoding="utf-8"))
    assert envelope.test_scope is not None
    assert envelope.test_scope["proof"] == "missing"
