"""Executable structure checks for the reviewer assessment instruction mode."""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
_INSTRUCTION = _ROOT / "instructions" / "implementation-check.md"
_LAUNCHER = "<LLM_SHARED_DIR>\\bin\\code_review_evidence.bat"
_MINIMUM_NONE_REFERENCES = 3


def _instruction() -> str:
    """Return the canonical implementation-check instruction once per assertion."""
    return _INSTRUCTION.read_text(encoding="utf-8")


def _section(content: str, heading: str, next_heading: str) -> str:
    """Return one exact instruction section bounded by unique headings."""
    return content.split(heading, maxsplit=1)[1].split(next_heading, maxsplit=1)[0]


def test_reviewer_mode_uses_executable_baselines_and_manifest_lifecycle() -> None:
    """Reviewer setup delegates snapshots, baselines, and retention to Step 2."""
    content = _instruction()
    setup = _section(
        content,
        "### Reviewer evidence setup before applying criteria",
        "### Reviewer evidence boundary after a Yes result",
    )

    assert "Outside reviewer assessment mode" in content
    assert _LAUNCHER in setup
    assert "umbrella-digest\n   capture" in setup
    assert "validation-state\n   capture" in setup
    assert "record-pre-repair-blob" in setup
    assert "write-manifest" in setup
    assert "read-manifest" in setup
    assert "never completes an umbrella row" in content


def test_yes_and_no_paths_apply_the_same_executable_comparisons() -> None:
    """Both criteria outcomes compare umbrella and validation state before return."""
    content = _instruction()
    yes_path = _section(
        content,
        "### Reviewer evidence boundary after a Yes result",
        "### Reviewer evidence boundary after a No result",
    )
    no_path = _section(
        content,
        "### Reviewer evidence boundary after a No result",
        "## Document-level status line",
    )

    for result_path in (yes_path, no_path):
        assert _LAUNCHER in result_path
        assert "umbrella-digest\n   compare" in result_path
        assert "validation-state\n   capture" in result_path
        assert "validation-state\n   compare" in result_path
        assert "same ordered `validation_path_set`" in result_path


def test_validation_scope_covers_staged_and_known_artifact_paths() -> None:
    """The captured scope cannot hide a tracked change outside command outputs."""
    content = _instruction()
    normalized = " ".join(content.split())

    assert "every staged path that belongs to the reviewed step" in content
    assert "every known validation-artifact path" in content
    assert "the exact validation plan" in normalized
    assert "first-seen ordered union in O(n)" in content


def test_reviewer_permissions_fail_closed_and_keep_detected_changes() -> None:
    """Only reviewed rows are writable and every other tracked change survives."""
    content = _instruction()

    assert "only the exact validation-plan rows for the reviewed" in content
    assert "suppress the final-step umbrella completion section" in content
    assert "Leave the changed umbrella file in place" in content
    assert "stays unstaged and unreverted" in content
    assert "attribute-reviewer-patch" in content
    assert "retire-manifest" in content
    assert "`changes-requested`" in content


def test_missing_umbrella_records_not_applicable_evidence() -> None:
    """An absent umbrella omits the operand and retains typed not-applicable proof."""
    content = _instruction()

    assert content.count("`Umbrella draft: none`") >= _MINIMUM_NONE_REFERENCES
    assert "omit the path operand" in content
    assert '"applicable": false' in content


# eof
