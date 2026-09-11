"""TDD contracts for the non-interactive code-review evidence CLI."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

import pytest

from tools import code_review_evidence_cli as cli

if TYPE_CHECKING:
    from pathlib import Path

# ruff: noqa: S603, S607

_FATAL_EXIT = 2


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


def test_cli_captures_index_blob_and_umbrella_evidence(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Typed capture commands return JSON without an input prompt."""
    _git(tmp_path, "init", "-q")
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("content\n", encoding="utf-8")
    _git(tmp_path, "add", "tracked.txt")

    assert cli.main(["--repository", str(tmp_path), "capture-index-tree"]) == 0
    captured = json.loads(capsys.readouterr().out)
    assert captured["index_tree"] == _git(tmp_path, "write-tree")

    assert cli.main(
        ["--repository", str(tmp_path), "record-pre-repair-blob", "tracked.txt"],
    ) == 0
    blob = json.loads(capsys.readouterr().out)
    assert blob["path"] == "tracked.txt"
    assert blob["object_id"]

    assert cli.main(
        ["--repository", str(tmp_path), "umbrella-digest", "capture", "tracked.txt"],
    ) == 0
    digest = json.loads(capsys.readouterr().out)
    assert digest["applicable"] is True


def test_cli_rejects_unsafe_paths_and_malformed_retained_evidence(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Exact-path and retained-model failures return the stable fatal exit."""
    _git(tmp_path, "init", "-q")
    assert cli.main(
        ["--repository", str(tmp_path), "record-pre-repair-blob", "../outside.txt"],
    ) == _FATAL_EXIT
    assert "repository-relative" in capsys.readouterr().err

    home = tmp_path / ".reviews"
    home.mkdir()
    (home / ".gitignore").write_bytes(b"*\n")
    manifest = home / "a.code-review-evidence.v0.11.0.code-reviewer.step-2.json"
    manifest.write_text("{malformed", encoding="utf-8")
    assert cli.main(
        [
            "--repository",
            str(tmp_path),
            "read-manifest",
            "--family",
            "code",
            "--type-token",
            "code",
            "--version",
            "v0.11.0",
            "--slug",
            "code-reviewer",
            "--implementation-step",
            "2",
        ],
    ) == _FATAL_EXIT
    assert "manifest" in capsys.readouterr().err


def test_cli_rejects_repository_path_escapes(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Every caller-owned file operand remains inside the selected repository."""
    _git(tmp_path, "init", "-q")
    assert cli.main(
        ["--repository", str(tmp_path), "umbrella-digest", "capture", "../outside.md"],
    ) == _FATAL_EXIT
    assert "repository-relative" in capsys.readouterr().err
    assert cli.main(
        [
            "--repository",
            str(tmp_path),
            "attribute-reviewer-patch",
            str(tmp_path / "absolute.json"),
        ],
    ) == _FATAL_EXIT
    assert "repository-relative" in capsys.readouterr().err
    assert cli.main(
        ["--repository", str(tmp_path), "attribute-reviewer-patch", "."],
    ) == _FATAL_EXIT
    assert "must name a file" in capsys.readouterr().err


def test_cli_rejects_manifest_identity_mixture(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A retained manifest cannot be read under a different step identity."""
    _git(tmp_path, "init", "-q")
    home = tmp_path / ".reviews"
    home.mkdir()
    (home / ".gitignore").write_bytes(b"*\n")
    manifest = home / "a.code-review-evidence.v0.11.0.code-reviewer.step-3.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "identity": {
                    "family": "code",
                    "type_token": "code",
                    "version": "v0.11.0",
                    "slug": "code-reviewer",
                    "implementation_step": "2",
                },
                "baseline_index_tree": "0" * 40,
                "assessed_index_tree": "0" * 40,
                "recorded_blobs": [],
                "repair_paths": [],
                "validation_before": None,
                "validation_after": None,
            },
        ),
        encoding="utf-8",
    )
    assert cli.main(
        [
            "--repository",
            str(tmp_path),
            "read-manifest",
            "--family",
            "code",
            "--type-token",
            "code",
            "--version",
            "v0.11.0",
            "--slug",
            "code-reviewer",
            "--implementation-step",
            "3",
        ],
    ) == _FATAL_EXIT
    assert "identity disagrees" in capsys.readouterr().err


def _identity_args(step: str = "2") -> list[str]:
    """Return the exact manifest identity command arguments."""
    return [
        "--family",
        "code",
        "--type-token",
        "code",
        "--version",
        "v0.11.0",
        "--slug",
        "code-reviewer",
        "--implementation-step",
        step,
    ]


def test_cli_executes_patch_and_umbrella_comparison(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Patch and umbrella operations remain callable through one CLI model."""
    _git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text("a.*\n", encoding="utf-8")
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("before\n", encoding="utf-8")
    _git(tmp_path, "add", ".gitignore", "tracked.txt")

    assert cli.main(
        ["--repository", str(tmp_path), "record-pre-repair-blob", "tracked.txt"],
    ) == 0
    baseline_path = tmp_path / "a.baseline.json"
    baseline_path.write_text(capsys.readouterr().out, encoding="utf-8")
    tracked.write_text("after\n", encoding="utf-8")
    assert cli.main(
        [
            "--repository",
            str(tmp_path),
            "attribute-reviewer-patch",
            baseline_path.name,
        ],
    ) == 0
    assert json.loads(capsys.readouterr().out)["attributable"] is True

    assert cli.main(
        ["--repository", str(tmp_path), "umbrella-digest", "capture", "tracked.txt"],
    ) == 0
    digest_path = tmp_path / "a.digest.json"
    digest_path.write_text(capsys.readouterr().out, encoding="utf-8")
    assert cli.main(
        [
            "--repository",
            str(tmp_path),
            "umbrella-digest",
            "compare",
            digest_path.name,
            "tracked.txt",
        ],
    ) == 0
    assert json.loads(capsys.readouterr().out)["changed"] is False


def test_cli_executes_validation_and_manifest_lifecycle(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Validation snapshots and retained manifests share the same CLI model."""
    _git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text("a.*\n", encoding="utf-8")
    (tmp_path / "tracked.txt").write_text("before\n", encoding="utf-8")
    _git(tmp_path, "add", ".gitignore", "tracked.txt")

    assert cli.main(
        [
            "--repository",
            str(tmp_path),
            "validation-state",
            "capture",
            ".gitignore",
            "tracked.txt",
        ],
    ) == 0
    before_path = tmp_path / "a.before.json"
    before_path.write_text(capsys.readouterr().out, encoding="utf-8")
    after_path = tmp_path / "a.after.json"
    after_path.write_text(before_path.read_text(encoding="utf-8"), encoding="utf-8")
    assert cli.main(
        [
            "--repository",
            str(tmp_path),
            "validation-state",
            "compare",
            before_path.name,
            after_path.name,
        ],
    ) == 0
    assert json.loads(capsys.readouterr().out)["acceptable"] is True

    state = json.loads(before_path.read_text(encoding="utf-8"))
    manifest_input = tmp_path / "a.manifest-input.json"
    manifest_input.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "identity": {
                    "family": "code",
                    "type_token": "code",
                    "version": "v0.11.0",
                    "slug": "code-reviewer",
                    "implementation_step": "2",
                },
                "baseline_index_tree": state["index_tree"],
                "assessed_index_tree": state["index_tree"],
                "recorded_blobs": [],
                "repair_paths": [],
                "validation_before": state,
                "validation_after": state,
            },
        ),
        encoding="utf-8",
    )
    assert cli.main(
        ["--repository", str(tmp_path), "write-manifest", manifest_input.name],
    ) == 0
    capsys.readouterr()
    mixed = json.loads(manifest_input.read_text(encoding="utf-8"))
    mixed["identity"]["family"] = "spec"
    manifest_input.write_text(json.dumps(mixed), encoding="utf-8")
    assert cli.main(
        ["--repository", str(tmp_path), "write-manifest", manifest_input.name],
    ) == _FATAL_EXIT
    assert "code/code" in capsys.readouterr().err
    assert cli.main(
        ["--repository", str(tmp_path), "retire-manifest", *_identity_args()],
    ) == 0
    assert json.loads(capsys.readouterr().out)["retired"] is True


def test_cli_reports_parser_json_and_dispatch_failures(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Parser, explicit JSON input, and unknown dispatch failures use exit 2."""
    _git(tmp_path, "init", "-q")
    assert cli.main(["--repository", str(tmp_path)]) == _FATAL_EXIT
    assert "required" in capsys.readouterr().err
    assert cli.main(
        [
            "--repository",
            str(tmp_path),
            "attribute-reviewer-patch",
            "missing.json",
        ],
    ) == _FATAL_EXIT
    assert "cannot read evidence JSON" in capsys.readouterr().err

    namespace = cli.argparse.Namespace(repository=str(tmp_path), operation="unknown")
    with pytest.raises(cli.ReviewExchangeError, match="unsupported"):
        cli.CodeReviewEvidenceCli().dispatch(namespace)


# eof
