"""TDD coverage for v0.11.0 review-exchange paths and activation.

Step 1: specify stable derivation for both review families, reversible artifact
identity, archive naming, and one fail-closed effective Git-ignore check.
Generated identity checks reuse configuration and document-directory setup.
"""

from __future__ import annotations

import subprocess
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from tools import review_exchange_paths as paths_module
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import (
    ArchiveKind,
    ExchangeIdentity,
    ReviewContext,
    ReviewExchangeError,
    ReviewFamily,
)

# ruff: noqa: SLF001
from tools.review_exchange_paths import (
    archive_path,
    derive_artifact_paths,
    parse_transcript_identity,
    parse_transient_identity,
    transient_paths_for_ignore,
    validate_activation,
)

if TYPE_CHECKING:
    from pathlib import Path

_VERSION = "v0.11.0"
_SLUG = "review-exchange-core"
_IGNORE_TIMESTAMP = "20000101-000000"
_IGNORE_PROBE_COUNT = 10


def _context(tmp_path: Path, family: ReviewFamily) -> ReviewContext:
    """Create one real reviewed document for a family."""
    if family is ReviewFamily.CODE:
        identity = ExchangeIdentity(family, "code", _VERSION, _SLUG)
        prefix = "plan"
        step = "1"
    else:
        identity = ExchangeIdentity(family, "design-specification", _VERSION, _SLUG)
        prefix = "design"
        step = None
    document = tmp_path / "docs" / "v0.11.0" / f"{prefix}.{_VERSION}.{_SLUG}.md"
    document.parent.mkdir(parents=True)
    document.write_text("# Reviewed document\n", encoding="utf-8")
    return ReviewContext(identity, document, None, step)


def test_specification_paths_use_document_parent_and_project_root(tmp_path: Path) -> None:
    """Specification transcript and transients use their required locations."""
    context = _context(tmp_path, ReviewFamily.SPECIFICATION)

    paths = derive_artifact_paths(tmp_path, context)

    assert paths.transcript == context.document_path.parent / (
        "review.design-specification.v0.11.0.review-exchange-core.md"
    )
    assert paths.request.name == (
        "a.review-requested.design-specification.v0.11.0.review-exchange-core.md"
    )
    assert paths.answer.name == (
        "a.review-answer.design-specification.v0.11.0.review-exchange-core.md"
    )
    assert paths.coordination.name == (
        "a.review-active.specification.design-specification.v0.11.0."
        "review-exchange-core.md"
    )
    assert paths.tombstone.name == (
        "a.review-consumed.specification.design-specification.v0.11.0."
        "review-exchange-core.md"
    )
    assert paths.transition_lock.name == (
        "a.review-lock.specification.design-specification.v0.11.0."
        "review-exchange-core.lock"
    )
    transients = (
        paths.request,
        paths.answer,
        paths.coordination,
        paths.tombstone,
        paths.transition_lock,
    )
    assert all(path.parent == tmp_path / ".reviews" for path in transients)


def test_code_paths_keep_intentional_code_code_names(tmp_path: Path) -> None:
    """The fixed code token remains visible beside the code family token."""
    paths = derive_artifact_paths(tmp_path, _context(tmp_path, ReviewFamily.CODE))

    assert paths.transcript.name == "review.code.v0.11.0.review-exchange-core.md"
    assert paths.request.name == "a.review-requested.code.v0.11.0.review-exchange-core.md"
    assert paths.answer.name == "a.review-answer.code.v0.11.0.review-exchange-core.md"
    assert paths.coordination.name == (
        "a.review-active.code.code.v0.11.0.review-exchange-core.md"
    )
    assert paths.tombstone.name == (
        "a.review-consumed.code.code.v0.11.0.review-exchange-core.md"
    )
    assert paths.transition_lock.name == (
        "a.review-lock.code.code.v0.11.0.review-exchange-core.lock"
    )


def test_archive_path_uses_only_settled_kinds_and_compact_time(tmp_path: Path) -> None:
    """Recovery archives carry identity, compact local time, and fixed kind."""
    paths = derive_artifact_paths(tmp_path, _context(tmp_path, ReviewFamily.CODE))

    archived = archive_path(paths, "20260803-143005", ArchiveKind.ANSWER)

    assert archived.name == (
        "a.review-archive.code.code.v0.11.0.review-exchange-core."
        "20260803-143005.answer.md"
    )
    assert archived.parent == tmp_path / ".reviews"
    with pytest.raises(ReviewExchangeError, match="compact local timestamp"):
        archive_path(paths, "2026-08-03T14:30:05+02:00", ArchiveKind.ANSWER)


@pytest.fixture
def identity_configuration(tmp_path: Path) -> ReviewArtifactConfiguration:
    """Resolve the fixed home once before generated path-identity assertions."""
    (tmp_path / "docs").mkdir()
    return ReviewArtifactConfiguration.load(tmp_path)


@settings(
    max_examples=25,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    family=st.sampled_from(tuple(ReviewFamily)),
    version=st.tuples(
        st.integers(min_value=0, max_value=20),
        st.integers(min_value=0, max_value=20),
        st.integers(min_value=0, max_value=20),
    ).map(lambda value: f"v{value[0]}.{value[1]}.{value[2]}"),
    slug=st.from_regex(r"[a-z0-9][a-z0-9_-]{0,20}", fullmatch=True),
)
def test_paths_parse_back_without_identity_collisions(
    tmp_path: Path,
    identity_configuration: ReviewArtifactConfiguration,
    family: ReviewFamily,
    version: str,
    slug: str,
) -> None:
    """Every generated path set is stable and carries complete identity."""
    type_token = "code" if family is ReviewFamily.CODE else "plan"
    identity = ExchangeIdentity(family, type_token, version, slug)
    document = tmp_path / "docs" / f"plan.{version}.{slug}.md"
    document.write_text("# Document\n", encoding="utf-8")
    context = ReviewContext(
        identity,
        document,
        None,
        "2" if family is ReviewFamily.CODE else None,
    )

    first = derive_artifact_paths(tmp_path, context, configuration=identity_configuration)
    second = derive_artifact_paths(tmp_path, context, configuration=identity_configuration)

    assert first == second
    assert len(set(first.fixed_paths)) == len(first.fixed_paths)
    assert parse_transcript_identity(first.transcript) == identity
    transients = (
        first.request,
        first.answer,
        first.coordination,
        first.tombstone,
        first.transition_lock,
        archive_path(first, _IGNORE_TIMESTAMP, ArchiveKind.REQUEST),
    )
    assert all(parse_transient_identity(path) == identity for path in transients)


def test_activation_checks_all_transients_in_one_ignore_call(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Activation submits one NUL-delimited path set to effective ignore logic."""
    paths = derive_artifact_paths(tmp_path, _context(tmp_path, ReviewFamily.CODE))
    calls: list[tuple[list[str], Path, str | None]] = []

    def fake_run(
        command: list[str],
        *,
        cwd: Path,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        calls.append((command, cwd, input_text))
        if "rev-parse" in command:
            return subprocess.CompletedProcess(command, 0, "true\n", "")
        assert input_text is not None
        return subprocess.CompletedProcess(command, 0, input_text, "")

    monkeypatch.setattr("tools.review_exchange_paths._run_git", fake_run)

    validate_activation(tmp_path, paths)

    ignore_calls = [call for call in calls if "check-ignore" in call[0]]
    assert len(ignore_calls) == 1
    assert "-z" in ignore_calls[0][0]
    submitted = set(filter(None, (ignore_calls[0][2] or "").split("\0")))
    expected = {
        path.relative_to(tmp_path).as_posix()
        for path in (
            tmp_path / ".reviews" / ".gitignore",
            *transient_paths_for_ignore(paths),
        )
    }
    assert submitted == expected
    assert len(expected) == _IGNORE_PROBE_COUNT


def test_activation_fails_outside_git_before_ignore_check(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A project with no verifiable Git root cannot activate review mode."""
    paths = derive_artifact_paths(tmp_path, _context(tmp_path, ReviewFamily.CODE))
    calls: list[list[str]] = []

    def fake_run(
        command: list[str],
        *,
        cwd: Path,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, input_text
        calls.append(command)
        return subprocess.CompletedProcess(command, 128, "", "not a git repository")

    monkeypatch.setattr("tools.review_exchange_paths._run_git", fake_run)

    with pytest.raises(ReviewExchangeError, match="requires a Git repository"):
        validate_activation(tmp_path, paths)
    assert len(calls) == 1


def test_activation_reports_each_path_missing_ignore_coverage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Partial ignore matches fail closed and identify the uncovered path."""
    paths = derive_artifact_paths(tmp_path, _context(tmp_path, ReviewFamily.SPECIFICATION))
    missing = paths.answer.relative_to(tmp_path).as_posix()

    def fake_run(
        command: list[str],
        *,
        cwd: Path,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd
        if "rev-parse" in command:
            return subprocess.CompletedProcess(command, 0, "true\n", "")
        assert input_text is not None
        matched = "\0".join(
            path for path in input_text.split("\0") if path and path != missing
        )
        return subprocess.CompletedProcess(command, 0, f"{matched}\0", "")

    monkeypatch.setattr("tools.review_exchange_paths._run_git", fake_run)

    with pytest.raises(ReviewExchangeError, match="not effectively ignored") as error:
        validate_activation(tmp_path, paths)
    assert missing in str(error.value)


def test_derivation_rejects_document_outside_project_root(tmp_path: Path) -> None:
    """An external reviewed path cannot own project-root transients."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    external = tmp_path / "external" / f"plan.{_VERSION}.{_SLUG}.md"
    external.parent.mkdir()
    external.write_text("# Plan\n", encoding="utf-8")
    context = ReviewContext(
        ExchangeIdentity(ReviewFamily.CODE, "code", _VERSION, _SLUG),
        external,
        None,
        "1",
    )

    with pytest.raises(ReviewExchangeError, match="outside project root"):
        derive_artifact_paths(project_root, context)


def test_identity_parsers_reject_unknown_artifact_names(tmp_path: Path) -> None:
    """Unknown transient and transcript names cannot satisfy exact waiting."""
    with pytest.raises(ReviewExchangeError, match="unrecognized review transient"):
        parse_transient_identity(tmp_path / "a.review-other.md")
    with pytest.raises(ReviewExchangeError, match="unrecognized review transcript"):
        parse_transcript_identity(tmp_path / "review.other.md")


def test_activation_rejects_a_different_project_root(tmp_path: Path) -> None:
    """Activation cannot reuse paths derived for another project root."""
    paths = derive_artifact_paths(tmp_path, _context(tmp_path, ReviewFamily.CODE))
    other = tmp_path / "other"
    other.mkdir()

    with pytest.raises(ReviewExchangeError, match="project root differs"):
        validate_activation(other, paths)


def test_activation_rejects_paths_from_a_different_artifact_home(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Activation cannot mix one configuration with paths from another home."""
    paths = derive_artifact_paths(tmp_path, _context(tmp_path, ReviewFamily.CODE))
    mismatched = replace(paths, request=tmp_path / "other" / paths.request.name)

    def git_repository(
        command: list[str],
        *,
        cwd: Path,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, input_text
        return subprocess.CompletedProcess(command, 0, "true\n", "")

    monkeypatch.setattr(
        "tools.review_exchange_paths._run_git",
        git_repository,
    )

    with pytest.raises(ReviewExchangeError, match="artifact home differs"):
        validate_activation(tmp_path, mismatched)


def test_derivation_rejects_another_repository_artifact_configuration(
    tmp_path: Path,
) -> None:
    """Invocation-bound derivation cannot cross repository boundaries."""
    other = tmp_path / "other"
    other.mkdir()
    artifacts = ReviewArtifactConfiguration.load(other)

    with pytest.raises(ReviewExchangeError, match="another repository"):
        derive_artifact_paths(
            tmp_path,
            _context(tmp_path, ReviewFamily.CODE),
            configuration=artifacts,
        )


def test_standard_git_runner_forwards_bounded_subprocess_arguments(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The standard-library adapter forwards cwd and optional standard input."""
    captured: dict[str, object] = {}

    def fake_subprocess_run(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        captured["command"] = command
        captured.update(kwargs)
        return subprocess.CompletedProcess(command, 0, "ok\n", "")

    monkeypatch.setattr(subprocess, "run", fake_subprocess_run)

    result = paths_module._run_git(
        ["git", "status"],
        cwd=tmp_path,
        input_text="probe\n",
    )

    assert result.stdout == "ok\n"
    assert captured["cwd"] == tmp_path
    assert captured["input"] == "probe\n"


def test_activation_reports_git_ignore_query_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An unverified effective-ignore query fails before protocol writes."""
    paths = derive_artifact_paths(tmp_path, _context(tmp_path, ReviewFamily.CODE))

    def fake_run(
        command: list[str],
        *,
        cwd: Path,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, input_text
        if "rev-parse" in command:
            return subprocess.CompletedProcess(command, 0, "true\n", "")
        return subprocess.CompletedProcess(command, 2, "", "ignore query failed")

    monkeypatch.setattr("tools.review_exchange_paths._run_git", fake_run)

    with pytest.raises(ReviewExchangeError, match="ignore query failed"):
        validate_activation(tmp_path, paths)


# eof
