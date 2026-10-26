"""Decision scans preserve human authority and never mutate the specification.

Fix: the 58-of-73 scenario builds its document in one helper and splits its
report and cursor checks into two tests, keeping each under the radon gate.
Direct execution of the module file is covered too, as the launcher runs it.
"""

from __future__ import annotations

import json
import runpy
import sys
from typing import TYPE_CHECKING

import pytest

from tools import question_decisions
from tools.question_decisions import decision_report, main, parse_questions

if TYPE_CHECKING:
    from pathlib import Path

SECTION = "## Open questions for the requirement\n\n"
CONFIRMED_COUNT = 58
TOTAL_COUNT = 73
UNDECIDED_COUNT = TOTAL_COUNT - CONFIRMED_COUNT
INVALID_INPUT = 2


def _question(
    number: int,
    answer: str = "Proposed; awaiting user confirmation.",
) -> str:
    """Build realistic question text with a filled proposed answer heading."""
    return (
        f"### Q{number:02d}: Choice {number}\n\n"
        f"#### Recommended option for Q{number:02d}\n\nOption A.\n\n"
        f"#### Answer to Q{number:02d}: option A\n\n{answer}\n\n"
    )


def _fifty_eight_of_seventy_three(tmp_path: Path) -> Path:
    """Write a CRLF document whose Q01-Q58 are confirmed and Q59-Q73 proposed."""
    document = tmp_path / "feature-request.v1.0.0.example.md"
    text = SECTION + "".join(
        _question(number, "Confirmed by the user: Option A.")
        if number <= CONFIRMED_COUNT
        else _question(number)
        for number in range(1, TOTAL_COUNT + 1)
    )
    document.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
    return document


def test_detects_fifteen_proposals_after_fifty_eight_human_decisions(
    tmp_path: Path,
) -> None:
    """Nonempty Answer sections do not turn Q59-Q73 into human decisions."""
    result = decision_report(_fifty_eight_of_seventy_three(tmp_path))
    assert result["question_count"] == TOTAL_COUNT
    assert result["undecided_count"] == UNDECIDED_COUNT
    assert result["first_undecided"] == result["next_undecided"] == "Q59"
    assert result["last_undecided"] == result["last_question"] == "Q73"


def test_cursor_keeps_the_full_count_and_never_writes(tmp_path: Path) -> None:
    """--after moves only next_undecided; the scan leaves the document untouched."""
    document = _fifty_eight_of_seventy_three(tmp_path)
    before = document.read_bytes()
    assert decision_report(document, "Q59")["next_undecided"] == "Q60"
    assert decision_report(document, "Q73")["next_undecided"] is None
    assert decision_report(document, "Q73")["undecided_count"] == UNDECIDED_COUNT
    assert document.read_bytes() == before
    assert list(tmp_path.iterdir()) == [document]


@pytest.mark.parametrize(
    "answer",
    [
        "Option A is recommended and the reviewer agrees.",
        "User decision: pending",
        "User decision: deferred",
        "User decision: reopened",
        "Proposed; awaiting user confirmation.",
    ],
)
def test_proposed_and_deferred_answers_remain_undecided(answer: str) -> None:
    """Only an explicit human choice can complete an answer."""
    assert parse_questions(SECTION + _question(1, answer))[0].status == "undecided"


@pytest.mark.parametrize(
    "answer",
    [
        "Confirmed by the user: Option B with amended conditions.",
        "Confirmed by the user on 2026-10-21: option A, with the clarification and\nexamples above.",
        "User decision: confirmed — Option B, including the clarification.",
        "User decision: confirmed - Inapplicable because the user rejected Q02 A.",
    ],
)
def test_explicit_choices_are_confirmed_with_evidence(answer: str) -> None:
    """Legacy and canonical records carry the exact source line."""
    text = SECTION + _question(1, answer)
    result = parse_questions(text)[0]
    assert result.status == "confirmed"
    assert result.decision_line == text.splitlines().index(answer.splitlines()[0]) + 1


def test_quoted_fenced_and_commented_confirmations_are_not_decisions() -> None:
    """Historical notes and examples cannot impersonate a current choice."""
    answer = (
        "> Confirmed by the user: Option A.\n"
        "```markdown\nConfirmed by the user: Option A.\n```\n"
        "~~~\n### Q99: Example\nUser decision: confirmed — Option A\n~~~\n"
        "<!--\nConfirmed by the user: Option A.\n-->\n"
        "User decision: pending"
    )
    result = parse_questions(SECTION + _question(1, answer))
    assert len(result) == 1
    assert result[0].status == "undecided"


def test_confirmation_in_recommendation_or_other_section_does_not_count() -> None:
    """Decision evidence must belong to this question's own answer section."""
    text = SECTION + _question(1, "Option A.")
    text = text.replace(
        "Option A.\n\n#### Answer",
        "Confirmed by the user: Option A.\n\n#### Answer",
    )
    text += "#### Historical note\nConfirmed by the user: Option A.\n"
    assert parse_questions(text)[0].status == "undecided"


@pytest.mark.parametrize(
    ("answer", "reason"),
    [
        (
            "User decision: confirmed — A\nUser decision: pending",
            "conflicting-decision-records",
        ),
        (
            "Confirmed by the user: A\nConfirmed by the user: B",
            "conflicting-decision-records",
        ),
        ("User decision: maybe A", "ambiguous-decision-record"),
        ("User decision: confirmed", "ambiguous-decision-record"),
        ("Confirmed by the user:", "ambiguous-decision-record"),
    ],
)
def test_ambiguous_records_are_reported_as_errors(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    answer: str,
    reason: str,
) -> None:
    """Ambiguity cannot silently result in an all-decided success."""
    document = tmp_path / "questions.md"
    document.write_text(SECTION + _question(1, answer), encoding="utf-8")
    assert main([str(document)]) == INVALID_INPUT
    report = json.loads(capsys.readouterr().out)
    assert report["undecided_count"] == 1
    assert report["diagnostics"] == [f"Q01: {reason}"]


@pytest.mark.parametrize(
    "body",
    [
        _question(1) + _question(1),
        "### Qzero: Broken\n",
        "#### Q01: Wrong heading level\n",
        "### Q00: Invalid\n",
        _question(1).replace("Answer to Q01", "Answer to Q02"),
        _question(1) + "#### Answer to Q01\nUser decision: pending\n",
        _question(1) + "```\nUnclosed fence",
        _question(1) + SECTION + _question(2),
    ],
)
def test_malformed_questions_fail_instead_of_disappearing(body: str) -> None:
    """Broken structures cannot reduce the apparent undecided count."""
    with pytest.raises(
        ValueError,
        match=r"Duplicate|Malformed|positive|mismatched|Unclosed|Multiple",
    ):
        parse_questions(SECTION + body)


def test_missing_answer_and_open_ended_heading_are_supported() -> None:
    """An unanswered block remains visible under either section spelling."""
    result = parse_questions("## Open-ended questions\n### Q01: Needs a choice\n")
    assert result[0].reason == "missing-answer"


def test_missing_section_with_questions_is_invalid() -> None:
    """A broken section heading cannot hide otherwise valid questions."""
    with pytest.raises(ValueError, match="without an open-questions section"):
        parse_questions(_question(1))


def test_sparse_ids_return_positions_and_distinct_last_values(tmp_path: Path) -> None:
    """Last undecided differs from the final document question; gaps are legal."""
    document = tmp_path / "questions.md"
    document.write_text(
        SECTION
        + _question(3)
        + _question(9)
        + _question(20, "Confirmed by the user: A."),
        encoding="utf-8",
    )
    report = decision_report(document, "q3")
    assert report["next_undecided"] == report["last_undecided"] == "Q09"
    assert report["last_question"] == "Q20"
    questions = parse_questions(document.read_text(encoding="utf-8"))
    assert [question.position for question in questions] == [1, 2, 3]


@pytest.mark.parametrize(
    "body",
    [
        "# Settled document\n",
        SECTION,
        SECTION + _question(1, "Confirmed by the user: A."),
    ],
)
def test_no_undecided_questions_return_null_navigation(
    tmp_path: Path,
    body: str,
) -> None:
    """Empty and completed sets do not invent a next question."""
    document = tmp_path / "questions.md"
    document.write_text(body, encoding="utf-8-sig")
    report = decision_report(document)
    assert report["undecided_count"] == 0
    assert (
        report["first_undecided"]
        is report["next_undecided"]
        is report["last_undecided"]
        is None
    )


@pytest.mark.parametrize("cursor", ["Q99", "59", "Q0"])
def test_invalid_cursor_is_not_an_empty_result(tmp_path: Path, cursor: str) -> None:
    """Cursor mistakes fail rather than falsely claiming end of batch."""
    document = tmp_path / "questions.md"
    document.write_text(SECTION + _question(1), encoding="utf-8")
    with pytest.raises(
        ValueError,
        match=r"Unknown question cursor|--after must|positive",
    ):
        decision_report(document, cursor)


@pytest.mark.parametrize("content", [b"", b"\xff"])
def test_empty_or_non_utf8_input_reports_json_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    content: bytes,
) -> None:
    """Invalid document bytes cannot be classified as settled."""
    document = tmp_path / "questions.md"
    document.write_bytes(content)
    assert main([str(document)]) == INVALID_INPUT
    assert "error" in json.loads(capsys.readouterr().out)


def test_cli_success_and_missing_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """CLI navigation works and a missing file is a bounded JSON failure."""
    document = tmp_path / "questions.md"
    assert main([str(document)]) == INVALID_INPUT
    assert "error" in json.loads(capsys.readouterr().out)
    document.write_text(SECTION + _question(1), encoding="utf-8")
    assert main([str(document), "--after", "Q01"]) == 0
    assert json.loads(capsys.readouterr().out)["next_undecided"] is None


def test_direct_execution_exits_with_the_cli_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Running the module file, as the launcher does, delegates to main."""
    document = tmp_path / "questions.md"
    document.write_text(SECTION + _question(1), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["question_decisions.py", str(document)])
    with pytest.raises(SystemExit) as raised:
        runpy.run_path(question_decisions.__file__, run_name="__main__")
    assert raised.value.code == 0
    assert json.loads(capsys.readouterr().out)["next_undecided"] == "Q01"


# eof
