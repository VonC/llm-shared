"""Defensive boundary contracts for executable code-review evidence."""

from __future__ import annotations

import subprocess
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools import code_review_evidence as evidence
from tools import code_review_evidence_common as evidence_common
from tools import code_review_evidence_validation_state as validation_state
from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tools.git_command import GitCommandOptions

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


def _retained_payload(tree: str) -> dict[str, object]:
    """Return one minimal valid retained-evidence payload."""
    return {
        "schema_version": 1,
        "identity": {
            "family": "code",
            "type_token": "code",
            "version": "v0.11.0",
            "slug": "code-reviewer",
            "implementation_step": "2",
        },
        "baseline_index_tree": tree,
        "assessed_index_tree": tree,
        "recorded_blobs": [],
        "repair_paths": [],
        "validation_before": None,
        "validation_after": None,
    }


@pytest.fixture(scope="module")
def real_literal_repository(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build one real repository with literal and glob-matching path pairs."""
    root = tmp_path_factory.mktemp("code-review-evidence-literal-paths")
    _git(root, "init", "-q")
    (root / ".gitignore").write_text(".ignored/\n", encoding="utf-8")
    for directory in ("tracked", ".ignored", "untracked"):
        target = root / directory
        target.mkdir()
        (target / "literal[1].txt").write_text("literal\n", encoding="utf-8")
        (target / "literal1.txt").write_text("glob match\n", encoding="utf-8")
    _git(root, "add", ".gitignore", "tracked/literal[1].txt", "tracked/literal1.txt")
    return root


@pytest.fixture(scope="module")
def real_literal_capture(
    real_literal_repository: Path,
) -> tuple[
    evidence.ValidationState,
    tuple[tuple[tuple[str, ...], tuple[str, ...]], ...],
]:
    """Capture the real-Git boundary once outside the measured call phase."""
    observed: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
    original_run = evidence_common.run_cross_platform_git_command

    def record_git_output(
        git_args: Sequence[str],
        *,
        cwd: Path | None = None,
        options: GitCommandOptions | None = None,
    ) -> subprocess.CompletedProcess[str]:
        result = original_run(git_args, cwd=cwd, options=options)
        if git_args and git_args[0] == "ls-files":
            paths = tuple(path for path in result.stdout.split("\0") if path)
            observed.append((tuple(git_args), paths))
        return result

    selected = (
        "tracked/literal[1].txt",
        ".ignored/literal[1].txt",
        "untracked/literal[1].txt",
    )
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            evidence_common,
            "run_cross_platform_git_command",
            record_git_output,
        )
        state = evidence.capture_validation_state(real_literal_repository, selected)
    return state, tuple(observed)


def test_validation_pathspecs_filter_real_git_literally(
    real_literal_capture: tuple[
        evidence.ValidationState,
        tuple[tuple[tuple[str, ...], tuple[str, ...]], ...],
    ],
    real_git_commands: bool,
) -> None:
    """Real Git classifies only literal tracked, ignored, and untracked names."""
    assert real_git_commands is True
    state, observed = real_literal_capture
    selected = (
        "tracked/literal[1].txt",
        ".ignored/literal[1].txt",
        "untracked/literal[1].txt",
    )

    literal_pathspecs = tuple(f":(literal){path}" for path in selected)
    assert tuple(
        arguments[arguments.index("--") + 1 :] for arguments, _paths in observed
    ) == (
        literal_pathspecs,
        literal_pathspecs,
        literal_pathspecs,
    )
    assert tuple(paths for _arguments, paths in observed) == (
        ("tracked/literal[1].txt",),
        (".ignored/literal[1].txt",),
        ("untracked/literal[1].txt",),
    )
    assert tuple(item.path for item in state.tracked_files) == selected[:1]
    assert tuple(item.path for item in state.ignored_files) == selected[1:2]
    assert tuple(item.path for item in state.untracked_files) == selected[2:]


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ("not-an-object", "must be an object"),
        ({"path": "", "object_id": None}, "path is invalid"),
        ({"path": "x", "object_id": "bad"}, "object is invalid"),
        (
            {"path": "x", "object_id": None, "writer_deleted": "yes"},
            "deletion flag is invalid",
        ),
    ],
)
def test_recorded_blob_payload_rejects_malformed_values(
    payload: object,
    message: str,
) -> None:
    """Retained blob fields fail at their typed boundary."""
    with pytest.raises(ReviewExchangeError, match=message):
        evidence.RecordedBlob.from_payload(payload)


def test_evidence_operations_reject_unsafe_and_unattributable_paths(
    tmp_path: Path,
) -> None:
    """Exact-path operations reject escapes, directories, absence, and binary text."""
    _git(tmp_path, "init", "-q")
    with pytest.raises(ReviewExchangeError, match="repository-relative"):
        evidence.record_pre_repair_blob(tmp_path, tmp_path / "absolute.txt")
    with pytest.raises(ReviewExchangeError, match="name a file"):
        evidence.record_pre_repair_blob(tmp_path, ".")
    directory = tmp_path / "directory"
    directory.mkdir()
    with pytest.raises(ReviewExchangeError, match="must be a file"):
        evidence.record_pre_repair_blob(tmp_path, "directory")

    absent = evidence.RecordedBlob("absent.txt", None)
    missing = evidence.attribute_reviewer_patch(tmp_path, absent)
    assert missing.attributable is False
    assert "absent" in missing.reason

    binary = tmp_path / "binary.txt"
    binary.write_bytes(b"\xff")
    with pytest.raises(ReviewExchangeError, match="UTF-8"):
        evidence.attribute_reviewer_patch(
            tmp_path,
            evidence.RecordedBlob("binary.txt", None),
        )


def test_git_evidence_errors_and_malformed_hash_are_explicit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Git launch and object-shape failures never become empty evidence."""
    _git(tmp_path, "init", "-q")
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("content\n", encoding="utf-8")

    def fail_git(*_args: object, **_kwargs: object) -> object:
        message = "git unavailable"
        raise OSError(message)

    monkeypatch.setattr(evidence_common, "run_cross_platform_git_command", fail_git)
    with pytest.raises(ReviewExchangeError, match="Git evidence command failed"):
        evidence.record_pre_repair_blob(tmp_path, "tracked.txt")

    calls = 0

    def malformed_hash(
        _arguments: object,
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        nonlocal calls
        calls += 1
        output = "" if calls == 1 else "not-an-object\n"
        return subprocess.CompletedProcess(["git"], 0, output, "")

    monkeypatch.setattr(evidence_common, "run_cross_platform_git_command", malformed_hash)
    with pytest.raises(ReviewExchangeError, match="malformed pre-repair blob"):
        evidence.record_pre_repair_blob(tmp_path, "tracked.txt")


def test_umbrella_and_validation_payload_failures_are_typed(tmp_path: Path) -> None:
    """Digest and validation snapshots reject malformed and inconsistent inputs."""
    with pytest.raises(ReviewExchangeError, match="umbrella document"):
        evidence.capture_umbrella_digest(tmp_path / "missing.md")
    with pytest.raises(ReviewExchangeError, match="applicability changed"):
        evidence.compare_umbrella_digest(
            evidence.UmbrellaDigest(applicable=False),
            __file__,
        )
    digest = "a" * 64
    assert evidence.UmbrellaDigest.from_payload(
        {"applicable": True, "digest": digest},
    ).digest == digest
    with pytest.raises(ReviewExchangeError, match="applicability"):
        evidence.UmbrellaDigest.from_payload({"applicable": "yes", "digest": None})
    with pytest.raises(ReviewExchangeError, match="value"):
        evidence.UmbrellaDigest.from_payload({"applicable": True, "digest": 3})
    with pytest.raises(ReviewExchangeError, match="value"):
        evidence.UmbrellaDigest.from_payload({"applicable": False, "digest": digest})

    with pytest.raises(ReviewExchangeError, match="file digest value"):
        evidence.FileDigest.from_payload({"path": "x", "digest": 3})
    with pytest.raises(ReviewExchangeError, match="must be an object"):
        evidence.FileDigest.from_payload("bad")
    with pytest.raises(ReviewExchangeError, match="path is invalid"):
        evidence.FileDigest.from_payload({"path": 3, "digest": None})
    with pytest.raises(ReviewExchangeError, match="repository-relative"):
        evidence.FileDigest.from_payload({"path": "../x", "digest": None})
    with pytest.raises(ReviewExchangeError, match="index tree"):
        evidence.ValidationState.from_payload({"index_tree": "bad"})
    with pytest.raises(ReviewExchangeError, match="must be an object"):
        evidence.ValidationState.from_payload("bad")
    with pytest.raises(ReviewExchangeError, match="paths are invalid"):
        evidence.ValidationState.from_payload(
            {
                "index_tree": "0" * 40,
                "paths": "bad",
                "tracked_files": [],
                "ignored_files": [],
                "untracked_files": [],
            },
        )
    with pytest.raises(ReviewExchangeError, match="tracked_files"):
        evidence.ValidationState.from_payload(
            {
                "index_tree": "0" * 40,
                "paths": [],
                "tracked_files": "bad",
                "ignored_files": [],
                "untracked_files": [],
            },
        )
    duplicate_file = {"path": "x", "digest": None}
    with pytest.raises(ReviewExchangeError, match="inconsistent"):
        evidence.ValidationState.from_payload(
            {
                "index_tree": "0" * 40,
                "paths": ["x"],
                "tracked_files": [duplicate_file],
                "ignored_files": [duplicate_file],
                "untracked_files": [],
            },
        )
    with pytest.raises(ReviewExchangeError, match="duplicate paths"):
        evidence.ValidationState.from_payload(
            {
                "index_tree": "0" * 40,
                "paths": ["x", "x"],
                "tracked_files": [],
                "ignored_files": [],
                "untracked_files": [],
            },
        )
    with pytest.raises(ReviewExchangeError, match="paths disagree"):
        evidence.compare_validation_state(
            evidence.ValidationState("0" * 40, ("a",), (), (), ()),
            evidence.ValidationState("0" * 40, ("b",), (), (), ()),
        )

    empty = evidence.ValidationState("0" * 40, (), (), (), ())
    changed = replace(empty, index_tree="1" * 40)
    comparison = evidence.compare_validation_state(empty, changed)
    assert comparison.tracked_paths == ("<index>",)
    assert comparison.to_payload()["acceptable"] is False
    umbrella_comparison = evidence.UmbrellaComparison(
        applicable=True,
        changed=False,
        before="a",
        after="a",
    )
    assert umbrella_comparison.to_payload()["changed"] is False
    repair = evidence.RepairAttribution("x", "patch", attributable=True)
    assert repair.to_payload()["attributable"] is True


def test_manifest_payload_and_io_failures_are_explicit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Manifest schema, identity, ignore, write, and retirement errors are reported."""
    _git(tmp_path, "init", "-q")
    tree = "0" * 40
    payload = _retained_payload(tree)
    invalid_payloads = (
        ({**payload, "schema_version": 2}, "schema"),
        ({**payload, "baseline_index_tree": "bad"}, "tree identity"),
        ({**payload, "recorded_blobs": "bad"}, "repair evidence"),
        ({**payload, "repair_paths": [3]}, "retained repair path is invalid"),
        ({**payload, "repair_paths": ["../outside"]}, "repository-relative"),
        ({**payload, "repair_paths": ["x", "x"]}, "duplicate paths"),
        (
            {
                **payload,
                "recorded_blobs": [
                    {"path": "x", "object_id": None},
                    {"path": "x", "object_id": None},
                ],
            },
            "duplicate paths",
        ),
        (
            {
                **payload,
                "identity": {
                    "family": "code",
                    "type_token": "code",
                    "version": "v0.11.0",
                    "slug": "",
                    "implementation_step": "2",
                },
            },
            "identity is invalid",
        ),
    )
    for malformed, message in invalid_payloads:
        with pytest.raises(ReviewExchangeError, match=message):
            evidence.CodeReviewEvidence.from_payload(malformed)

    retained = evidence.CodeReviewEvidence.from_payload(payload)
    with pytest.raises(ReviewExchangeError, match="unsafe token"):
        evidence.manifest_path(tmp_path, (*retained.identity[:-1], "../2"))
    with pytest.raises(ReviewExchangeError, match="code/code"):
        evidence.manifest_path(tmp_path, ("spec", *retained.identity[1:]))
    prepared = evidence.write_manifest(tmp_path, retained)
    assert prepared.parent == tmp_path / ".reviews"
    assert (prepared.parent / ".gitignore").read_text(encoding="utf-8") == "*\n"
    assert evidence.retire_manifest(tmp_path, retained.identity)

    (prepared.parent / ".gitignore").unlink()
    prepared.parent.rmdir()
    original_git = evidence._git

    def reject_ignore(
        repository: Path,
        args: tuple[str, ...],
        *,
        check: bool = True,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del repository, check, input_text
        return subprocess.CompletedProcess(args, 1, "", "")

    monkeypatch.setattr(evidence, "_git", reject_ignore)
    with pytest.raises(ReviewExchangeError, match="must be ignored"):
        evidence.write_manifest(tmp_path, retained)
    assert not prepared.parent.exists()
    monkeypatch.setattr(evidence, "_git", original_git)

    (tmp_path / ".gitignore").write_text("a.*\n", encoding="utf-8")
    original_write = Path.write_text

    def fail_write(
        self: Path,
        data: str,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> int:
        if self.name.endswith(".tmp"):
            message = "write denied"
            raise OSError(message)
        return original_write(
            self,
            data,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    monkeypatch.setattr(Path, "write_text", fail_write)
    with pytest.raises(ReviewExchangeError, match="cannot write"):
        evidence.write_manifest(tmp_path, retained)
    assert not prepared.parent.exists()
    monkeypatch.setattr(Path, "write_text", original_write)

    path = evidence.write_manifest(tmp_path, retained)
    original_unlink = Path.unlink

    def fail_unlink(
        self: Path,
        missing_ok: bool = False,
    ) -> None:
        if self == path:
            message = "retire denied"
            raise OSError(message)
        original_unlink(self, missing_ok=missing_ok)

    monkeypatch.setattr(Path, "unlink", fail_unlink)
    with pytest.raises(ReviewExchangeError, match="cannot retire"):
        evidence.retire_manifest(tmp_path, retained.identity)


def test_capture_validation_state_rejects_missing_repository(tmp_path: Path) -> None:
    """Validation capture requires one existing exact repository directory."""
    with pytest.raises(ReviewExchangeError, match="repository is not a directory"):
        evidence.capture_validation_state(tmp_path / "missing", ("tracked.txt",))


def test_validation_state_split_rejects_unsafe_scopes_and_git_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The split adapter fails closed at every repository and Git boundary."""
    _git(tmp_path, "init", "-q")
    tree = evidence.capture_index_tree(tmp_path)
    with pytest.raises(ReviewExchangeError, match="repository is not a directory"):
        validation_state.capture_validation_paths(
            tmp_path / "missing",
            ("x",),
            tree,
        )
    with pytest.raises(ReviewExchangeError, match="repository-relative"):
        validation_state.capture_validation_paths(tmp_path, (tmp_path / "x",), tree)
    with pytest.raises(ReviewExchangeError, match="repository-relative"):
        validation_state.capture_validation_paths(tmp_path, ("../x",), tree)
    with pytest.raises(ReviewExchangeError, match="name a file"):
        validation_state.capture_validation_paths(tmp_path, (".",), tree)

    def fail_git(*_args: object, **_kwargs: object) -> object:
        message = "git unavailable"
        raise OSError(message)

    monkeypatch.setattr(
        evidence_common,
        "run_cross_platform_git_command",
        fail_git,
    )
    with pytest.raises(ReviewExchangeError, match="Git evidence command failed"):
        validation_state.capture_validation_paths(tmp_path, ("x",), tree)


# eof
