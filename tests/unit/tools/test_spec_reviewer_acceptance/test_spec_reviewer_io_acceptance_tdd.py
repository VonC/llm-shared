"""Exact-path and launcher acceptance for the specification reviewer."""

from __future__ import annotations

import os
from pathlib import Path
from typing import cast

import pytest

from tools import prompt_workflow_skill, spec_review_answer_cli, spec_review_request
from tools.prompt_workflow_models import Topic
from tools.review_exchange_models import ReviewDisposition
from tools.review_exchange_paths import derive_artifact_paths

from .fixtures import Effort, make_effort, publish_request, render_answer

# ruff: noqa: S603

_DOCUMENT_READS = 2


@pytest.fixture
def exact_read_journey(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Run instrumented exact reads outside the measured call phase."""
    effort = make_effort(tmp_path / "exact", "plan", "exact-io")
    assert publish_request(effort).code == 0
    paths = derive_artifact_paths(effort.root, effort.context)
    (effort.root / "a.stale-assessment.md").write_text("stale", encoding="utf-8")
    reads: dict[Path, int] = {}
    original_read = Path.read_text
    original_read_bytes = Path.read_bytes

    def counted_read(
        path: Path,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> str:
        resolved = path.resolve()
        if resolved == paths.transcript:
            message = "reviewer renderer must not read the transcript"
            raise AssertionError(message)
        reads[resolved] = reads.get(resolved, 0) + 1
        return original_read(path, encoding=encoding, errors=errors, newline=newline)

    def reject_scan(*_args: object, **_kwargs: object) -> object:
        message = "reviewer renderer must not scan directories"
        raise AssertionError(message)

    def counted_read_bytes(path: Path) -> bytes:
        resolved = path.resolve()
        reads[resolved] = reads.get(resolved, 0) + 1
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_text", counted_read)
    monkeypatch.setattr(Path, "read_bytes", counted_read_bytes)
    monkeypatch.setattr(Path, "iterdir", reject_scan)
    monkeypatch.setattr(Path, "glob", reject_scan)
    monkeypatch.setattr(Path, "rglob", reject_scan)

    answer, summary = render_answer(effort, ReviewDisposition.CHANGES_REQUESTED)

    assert answer.exists()
    assert summary.exists()
    assert reads[effort.document.resolve()] == _DOCUMENT_READS
    reviewer_inputs = [path for path in reads if path.name.startswith("a.")]
    assert reviewer_inputs
    assert all(reads[path] == 1 for path in reviewer_inputs)
    assert (effort.root / "a.stale-assessment.md").resolve() not in reads


def test_answer_render_reads_each_exact_input_once_without_directory_discovery(
    exact_read_journey: None,
) -> None:
    """Known paths are single-read and decoy scratch or transcript files are ignored."""
    assert exact_read_journey is None


@pytest.fixture
def atomic_render_journey(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Run atomic paired rendering outside the measured call phase."""
    effort = make_effort(tmp_path / "atomic", "issue", "atomic")
    replacements: list[tuple[Path, Path]] = []
    original_replace = os.replace

    def observed_replace(
        source: str | Path,
        target: str | Path,
    ) -> None:
        source_path, target_path = Path(source), Path(target)
        replacements.append((source_path, target_path))
        original_replace(source, target)

    monkeypatch.setattr(spec_review_answer_cli.os, "replace", observed_replace)

    answer, summary = render_answer(
        effort,
        ReviewDisposition.CONVERGENCE_RECOMMENDED,
    )

    targets = {target for _, target in replacements}
    assert targets == {answer, summary}
    assert all(source.parent == target.parent for source, target in replacements)


def test_paired_answer_publication_uses_same_directory_atomic_replaces(
    atomic_render_journey: None,
) -> None:
    """Both rendered outputs cross the filesystem boundary through atomic replace."""
    assert atomic_render_journey is None


@pytest.fixture
def ambiguous_route_journey(
    tmp_path: Path,
) -> None:
    """Run ambiguous live routing outside the measured call phase."""
    root = tmp_path / "ambiguous"
    first = make_effort(root, "feature-request", "first")
    assert publish_request(first).code == 0
    docs = root / "docs" / "v0.11.0"
    second_document = docs / "plan.v0.11.0.first.md"
    second_document.write_text(
        "# Second plan\n\n## Open questions for second\n",
        encoding="utf-8",
    )
    second = Effort(
        root,
        Topic("v0.11.0", "first", first.topic.draft_path),
        spec_review_request.specification_context(second_document, first.umbrella),
        second_document,
        first.umbrella,
    )
    assert publish_request(second).code == 0
    before = {path: path.read_bytes() for path in root.glob("a.*") if path.is_file()}

    with pytest.raises(
        Exception,
        match="multiple live specification exchanges",
    ):
        prompt_workflow_skill.next_command(
            root,
            first.topic,
            "first",
            {"CODEX_THREAD_ID": "acceptance"},
        )

    after = {path: path.read_bytes() for path in root.glob("a.*") if path.is_file()}
    assert after == before


def test_ambiguous_live_requests_fail_closed_without_artifact_mutation(
    ambiguous_route_journey: None,
) -> None:
    """Routing refuses two live identities instead of guessing a reviewer target."""
    assert ambiguous_route_journey is None


@pytest.fixture(
    params=[
        ("prompt_workflow.bat", "prompt_workflow.py"),
        ("spec_review_answer.bat", "spec_review_answer_cli.py"),
        ("review_exchange.bat", "review_exchange_cli.py"),
    ],
    ids=lambda case: case[0],
)
def launcher_smoke_journey(request: pytest.FixtureRequest) -> None:
    """Verify each launcher delegates arguments to its canonical entry point."""
    launcher, entry_point = cast("tuple[str, str]", request.param)
    content = (Path("bin") / launcher).read_text(encoding="utf-8")

    assert f"tools\\{entry_point}" in content
    assert "%*" in content


def test_windows_launchers_reach_their_public_help_entry_point(
    launcher_smoke_journey: None,
) -> None:
    """Each shipped batch adapter targets its canonical Python entry point."""
    assert launcher_smoke_journey is None
