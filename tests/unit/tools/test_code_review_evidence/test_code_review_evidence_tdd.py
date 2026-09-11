"""Core capture and lifecycle contracts for executable code-review evidence."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from tools import code_review_evidence as evidence
from tools.review_exchange_models import ReviewExchangeError

# ruff: noqa: FBT001, FBT002, S603, S607
# pyright: reportPrivateUsage=false


def _git(root: Path, *arguments: str) -> str:
    """Run one bounded Git command in a temporary repository."""
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return result.stdout.strip()


@pytest.fixture(scope="module")
def staged_repository(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[str, str, str, str]:
    """Build real staged Git evidence outside the measured test call."""
    root = tmp_path_factory.mktemp("code-review-evidence")
    _git(root, "init", "-q")
    tracked = root / "tracked.txt"
    tracked.write_text("staged\n", encoding="utf-8")
    _git(root, "add", "tracked.txt")
    captured = evidence.capture_index_tree(root)
    expected = _git(root, "write-tree")
    tracked.write_text("unstaged\n", encoding="utf-8")
    after_unstaged = evidence.capture_index_tree(root)
    _git(root, "add", "tracked.txt")
    after_staged = evidence.capture_index_tree(root)
    return captured, expected, after_unstaged, after_staged


def test_capture_index_tree_uses_the_index_without_inspecting_worktree(
    staged_repository: tuple[str, str, str, str],
) -> None:
    """Unstaged bytes do not change the captured Git tree object."""
    captured, expected, after_unstaged, after_staged = staged_repository
    assert captured == expected
    assert after_unstaged == captured
    assert after_staged != captured


def test_capture_index_tree_rejects_non_repository_and_malformed_git_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Repository and object-identity failures remain explicit."""
    with pytest.raises(ReviewExchangeError, match="repository is not a directory"):
        evidence.capture_index_tree(tmp_path / "missing")
    # The commonest failure is a caller standing outside the reviewed
    # repository, so the diagnostic must name the directory Git ran in and
    # carry Git's own reason: an exit status alone reads as a damaged
    # repository rather than a misdirected call.
    with pytest.raises(ReviewExchangeError, match=re.escape(str(tmp_path.resolve()))) as outside:
        evidence.capture_index_tree(tmp_path)
    assert "not a git repository" in str(outside.value).casefold()

    completed = subprocess.CompletedProcess(["git", "write-tree"], 0, "not-a-tree\n", "")

    def fake_run(_arguments: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        """Return malformed output through the typed Git seam."""
        return completed

    monkeypatch.setattr(evidence, "run_cross_platform_git_command", fake_run)
    with pytest.raises(ReviewExchangeError, match="malformed tree object"):
        evidence.capture_index_tree(tmp_path)


def test_capture_index_tree_reports_a_failure_that_wrote_no_git_message(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A Git call that never ran still names the directory it would have run in.

    Git writes nothing to standard error when the executable itself cannot be
    started, so the diagnostic falls back to the raised error while keeping the
    directory that tells a misdirected call from a damaged repository.
    """

    def fail_to_start(_arguments: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        """Fail the way a missing Git executable does, with no stderr."""
        message = "git executable not found"
        raise OSError(message)

    monkeypatch.setattr(evidence, "run_cross_platform_git_command", fail_to_start)

    with pytest.raises(ReviewExchangeError, match="git executable not found") as failure:
        evidence.capture_index_tree(tmp_path)

    assert str(tmp_path.resolve()) in str(failure.value)


def test_recorded_blobs_attribute_reviewer_changes_and_protect_writer_deletions(
    tmp_path: Path,
) -> None:
    """Blob baselines distinguish edits, creations, and writer deletions."""
    _git(tmp_path, "init", "-q")
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("writer baseline\n", encoding="utf-8")
    _git(tmp_path, "add", "tracked.txt")

    baseline = evidence.record_pre_repair_blob(tmp_path, "tracked.txt")
    tracked.write_text("reviewer repair\n", encoding="utf-8")
    repair = evidence.attribute_reviewer_patch(tmp_path, baseline)
    assert repair.attributable is True
    assert repair.path == "tracked.txt"
    assert "reviewer repair" in repair.patch

    created = evidence.record_pre_repair_blob(tmp_path, "created.txt")
    (tmp_path / "created.txt").write_text("reviewer created\n", encoding="utf-8")
    creation = evidence.attribute_reviewer_patch(tmp_path, created)
    assert creation.attributable is True
    assert creation.created is True

    tracked.unlink()
    deleted = evidence.record_pre_repair_blob(tmp_path, "tracked.txt")
    deletion = evidence.attribute_reviewer_patch(tmp_path, deleted)
    assert deleted.writer_deleted is True
    assert deletion.attributable is False
    assert "writer-deleted" in deletion.reason


def test_umbrella_digest_and_validation_state_classify_command_artifacts(
    tmp_path: Path,
) -> None:
    """Ignored output is accepted while tracked-file mutation is reported."""
    _git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text(".cache/\n", encoding="utf-8")
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("before\n", encoding="utf-8")
    _git(tmp_path, "add", ".gitignore", "tracked.txt")

    umbrella = evidence.capture_umbrella_digest(tracked)
    assert umbrella.applicable is True
    assert evidence.compare_umbrella_digest(umbrella, tracked).changed is False
    tracked.write_text("after\n", encoding="utf-8")
    assert evidence.compare_umbrella_digest(umbrella, tracked).changed is True
    assert evidence.capture_umbrella_digest(None).applicable is False

    tracked.write_text("before\n", encoding="utf-8")
    validation_paths = (".gitignore", "tracked.txt", ".cache/coverage.json")
    before = evidence.capture_validation_state(tmp_path, validation_paths)
    cache = tmp_path / ".cache"
    cache.mkdir()
    (cache / "coverage.json").write_text("{}\n", encoding="utf-8")
    after_ignored = evidence.capture_validation_state(tmp_path, validation_paths)
    ignored = evidence.compare_validation_state(before, after_ignored)
    assert ignored.acceptable is True
    assert ignored.ignored_paths == (".cache/coverage.json",)

    tracked.write_text("command changed tracked content\n", encoding="utf-8")
    after_tracked = evidence.capture_validation_state(tmp_path, validation_paths)
    tracked_change = evidence.compare_validation_state(after_ignored, after_tracked)
    assert tracked_change.acceptable is False
    assert tracked_change.tracked_paths == ("tracked.txt",)


def test_validation_state_reads_only_explicit_literal_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Snapshot cost and evidence stay bounded to the caller's ordered scope."""
    _git(tmp_path, "init", "-q")
    selected = tmp_path / "selected.txt"
    unrelated = tmp_path / "unrelated.txt"
    selected.write_text("selected\n", encoding="utf-8")
    unrelated.write_text("unrelated\n", encoding="utf-8")
    wildcard = tmp_path / "literal[1].txt"
    wildcard.write_text("literal\n", encoding="utf-8")
    _git(tmp_path, "add", "selected.txt", "unrelated.txt", "literal[1].txt")
    reads: list[Path] = []
    original_read_bytes = Path.read_bytes

    def record_read(path: Path) -> bytes:
        reads.append(path)
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", record_read)
    state = evidence.capture_validation_state(
        tmp_path,
        ("literal[1].txt", "selected.txt", "selected.txt"),
    )

    assert state.paths == ("literal[1].txt", "selected.txt")
    assert tuple(item.path for item in state.tracked_files) == state.paths
    assert unrelated not in reads
    with pytest.raises(ReviewExchangeError, match="explicit paths"):
        evidence.capture_validation_state(tmp_path, ())
    (tmp_path / "directory").mkdir()
    with pytest.raises(ReviewExchangeError, match="must name files"):
        evidence.capture_validation_state(tmp_path, ("directory",))


def test_manifest_round_trip_uses_stable_identity_and_rejects_drift(
    tmp_path: Path,
) -> None:
    """Retained evidence round-trips at one identity-derived ignored path."""
    _git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text("a.*\n", encoding="utf-8")
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("baseline\n", encoding="utf-8")
    _git(tmp_path, "add", ".gitignore", "tracked.txt")
    tree = evidence.capture_index_tree(tmp_path)
    recorded = evidence.record_pre_repair_blob(tmp_path, "tracked.txt")
    state = evidence.capture_validation_state(tmp_path, (".gitignore", "tracked.txt"))
    retained = evidence.CodeReviewEvidence(
        family="code",
        type_token="code",  # noqa: S106 - protocol type token, not a credential
        version="v0.11.0",
        slug="code-reviewer",
        implementation_step="2",
        baseline_index_tree=tree,
        assessed_index_tree=tree,
        recorded_blobs=(recorded,),
        repair_paths=("tracked.txt",),
        validation_before=state,
        validation_after=state,
    )

    path = evidence.write_manifest(tmp_path, retained)
    assert path.name == "a.code-review-evidence.v0.11.0.code-reviewer.step-2.json"
    assert evidence.read_manifest(tmp_path, retained.identity) == retained
    drifted_identity = (*retained.identity[:-1], "3")
    evidence.manifest_path(tmp_path, drifted_identity).write_text(
        path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    with pytest.raises(ReviewExchangeError, match="identity disagrees"):
        evidence.read_manifest(tmp_path, drifted_identity)
    assert evidence.retire_manifest(tmp_path, retained.identity) is True
    assert evidence.retire_manifest(tmp_path, retained.identity) is False


# eof
