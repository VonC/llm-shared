"""Small isolated efforts with real workflow behavior and process-free Git seams.

Only unrelated Git readiness, activation and branch discovery are substituted.
Scope matching, proof, captures, persistence and coverage data stay real. Path
resolution caching is local to each symlink-free fixture and undone afterward.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from tests.unit.tools.groundhog_group_support import CoverageSpawns, group_project
from tests.unit.tools.prepare_release.prepare_release_plan_test_support import (
    SyntheticGitRepository,
)
from tests.unit.tools.review_exchange_test_support import (
    common_arguments,
    configured_home,
    review_policy,
)
from tools import code_review_request as renderer
from tools import prompt_workflow_git as workflow_git
from tools import prompt_workflow_progress as progress
from tools import review_exchange_cli as exchange_cli
from tools.commit_plan_check import CommitPlanCheckResult, CommitPlanCheckState
from tools.groundhog import cli
from tools.groundhog.context import Deps
from tools.prepare_release import prepare_release_plan_workflow as release_workflow
from tools.prompt_workflow_progress_review import ReviewReport
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import ReviewConfiguration
from tools.review_exchange_models_envelope import Envelope, parse_envelope_markdown
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

if TYPE_CHECKING:
    from collections.abc import Mapping

    from tools.review_exchange_models import ArtifactPaths, ReviewContext

# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false


@dataclass
class Effort:
    """Drive public entry points on one tiny effort without launching Git."""

    root: Path
    home: Path
    plan: Path
    requirement: Path
    context: ReviewContext
    paths: ArtifactPaths
    files: dict[str, Path]
    core: ReviewExchangeCore

    def set_group(self, group: str | None) -> None:
        """Change only the authoritative requirement's current selection."""
        declaration = "" if group is None else f"- Test group: {group}\n"
        self.requirement.write_text(f"# Requirement\n\n{declaration}", encoding="utf-8")

    def render(self) -> int:
        """Render the actual scope, validation policy, proof and paired artifacts."""
        arguments = ["--plan", str(self.plan), "--implementation-step", "8", "--round-number", "1"]
        for key in ("assessment", "implementation-report", "change-summary", "writer-response"):
            arguments.extend((f"--{key}-file", str(self.files[key])))
        for key, option in (("content", "request-content"), ("summary", "transcript-summary"),
                            ("capture", "scope-capture")):
            arguments.extend((f"--{option}-output", str(self.files[key])))
        return renderer.main(arguments, project_root=self.root)

    def request(self) -> tuple[Envelope, str, dict[str, Any]]:
        """Read authored commands and proof from the actual renderer output."""
        envelope, authored = parse_envelope_markdown(self.files["content"].read_text(encoding="utf-8"))
        evidence = json.loads(authored.split("```json\n", 1)[1].split("\n```", 1)[0])
        return envelope, authored, evidence

    def publish(self) -> int:
        """Present session ownership through the real exchange publication CLI."""
        capability = self.core.ownership_capability
        assert capability is not None
        return exchange_cli.main([
            "publish-request", *common_arguments(self.context),
            "--content-file", str(self.files["content"]), "--summary-file", str(self.files["summary"]),
            "--scope-capture-file", str(self.files["capture"]),
            "--ownership-generation", str(capability.generation), "--ownership-token", capability.token,
        ])

    def walk(self, *arguments: str, environment: Mapping[str, str] | None = None,
             seconds: float = 0.1) -> tuple[int, CoverageSpawns]:
        """Fake only the pytest child, including its measured duration evidence."""
        spawns = CoverageSpawns(self.root, extra_lines=(
            "=== slowest durations ===", f"{seconds:.2f}s call tests/old/test_core.py::test_ok",
        ))
        deps = Deps(popen_factory=spawns, environ=dict(environment or {}).get)
        return cli.main([*arguments, "--root", str(self.root)], deps), spawns


def _ignored(_root: Path, _path: Path) -> bool:
    """Substitute the Git ignore query, which these journeys do not assert."""
    return True


def _checked_plan(_root: Path) -> CommitPlanCheckResult:
    """Supply readiness without exercising commit-plan parsing again."""
    return CommitPlanCheckResult(CommitPlanCheckState.VALID)


def _captured_tree(_root: Path) -> str:
    """Supply the unrelated staged-tree identity at the renderer's Git seam."""
    return "1" * 40


@pytest.fixture
def effort(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Effort:
    """Initialize files and unrelated Git seams before each measured journey."""
    monkeypatch.setattr(Path, "resolve", cache(Path.resolve))
    root = group_project(tmp_path)
    old_test = root / "tests/old/test_core.py"
    old_test.parent.mkdir()
    sentinel_test = root / "tests/sentinel/test_core.py"
    old_test.write_bytes(sentinel_test.read_bytes())
    sentinel_test.unlink()
    new_test = root / "tests/new/test_core.py"
    new_test.parent.mkdir()
    new_test.write_text("def test_new():\n    assert True\n", encoding="utf-8")
    groups = root / ".ghog-groups"
    groups.write_text(groups.read_text(encoding="utf-8").replace("tests/sentinel/**", "tests/old/**"), encoding="utf-8")
    home = configured_home(root)
    docs = root / "docs/v9.9.0"
    docs.mkdir(parents=True)
    for kind, body in (("draft", "# Draft\n\n- Test group: sentinel\n"),
                       ("design", "# Design\n"),
                       ("plan", "# Plan\n\n### Step 8. Acceptance\n\n## Implementation decisions\n\n| Q01 | Settled |\n"),
                       ("plan-validation", "## Step 8. Acceptance\n\n### Analysis of Step 8\n\nNo\n")):
        name = "plan.v9.9.0.topic.validation.md" if kind == "plan-validation" else f"{kind}.v9.9.0.topic.md"
        (docs / name).write_text(body, encoding="utf-8")
    plan = docs / "plan.v9.9.0.topic.md"
    context = renderer.code_review_context(plan, "8")
    files = {key: home / f"a.{key}.md" for key in
             ("assessment", "implementation-report", "change-summary", "writer-response", "content", "summary")}
    files["capture"] = home / "a.scope.json"
    for key in ("assessment", "implementation-report", "change-summary", "writer-response"):
        files[key].write_text("Acceptance evidence for this round.\n", encoding="utf-8")
    paths = derive_artifact_paths(root, context)
    configuration = ReviewConfiguration(enabled=True)
    core = ReviewExchangeCore(ReviewExchangeStore(paths), context, review_policy(context), configuration)
    runtime = exchange_cli.Runtime(root, context, paths, configuration, core)
    monkeypatch.setattr(renderer.files, "is_effectively_ignored", _ignored)
    monkeypatch.setattr(renderer, "check_commit_plan", _checked_plan)
    monkeypatch.setattr(renderer, "capture_index_tree", _captured_tree)
    monkeypatch.setattr(exchange_cli, "find_project_root", lambda _path: root)
    monkeypatch.setattr(exchange_cli, "_build_runtime", lambda *_args: runtime)
    monkeypatch.setattr(exchange_cli, "_require_activation", lambda _runtime: None)
    monkeypatch.setattr(exchange_cli, "_is_effectively_ignored", _ignored)
    monkeypatch.setattr(workflow_git, "current_branch", lambda _root: "topic")
    monkeypatch.setattr(workflow_git, "working_tree_changed_files", lambda _root: [])
    monkeypatch.setattr(workflow_git, "fork_point", lambda _root: None)
    monkeypatch.setattr(workflow_git, "has_step_commit", lambda *_args: False)
    monkeypatch.setattr(progress.progress_review, "review_report", lambda *_args: ReviewReport((), None))
    monkeypatch.setattr(progress.review_history, "last_requestor_nature", lambda *_args: None)
    monkeypatch.setattr(progress, "next_line", lambda *_args: "next command")
    monkeypatch.chdir(root)
    monkeypatch.setenv("PRJ_DIR", str(root))
    result = Effort(root, home, plan, docs / "feature-request.v9.9.0.topic.md", context, paths, files, core)
    result.set_group("sentinel")
    core.start()
    return result


@pytest.fixture
def release_base(effort: Effort, monkeypatch: pytest.MonkeyPatch) -> str:
    """Initialize a divergent release graph with the existing in-memory Git protocol."""
    repository = SyntheticGitRepository(effort.root)
    base = repository.add_commit("chore: seed", frozenset({"seed.txt"}))
    repository.refs.update(develop=base, topic=base)
    repository.current = "develop"
    repository.add_commit("feat: integration work", frozenset({"integration.txt"}))
    repository.current = "topic"
    repository.add_commit("feat: effort", frozenset({"effort.txt"}))
    repository.current = "main"
    repository.add_commit("fix: independent main work", frozenset({"main.txt"}))
    monkeypatch.setattr(release_workflow, "GitRepository", lambda _root: repository)
    return base
