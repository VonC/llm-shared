"""Read explicit human decisions from Markdown question blocks without writing.

Only decision records inside a question's own ``Answer to Qxx`` section count.
Recommendations, examples in fences, and quoted historical answers do not.
The caller owns explanation progress and its persistent starting position.

Fix: answer extraction, record classification, section lookup, cursor
resolution and report endpoints are separate helpers, so no function exceeds
the project's radon complexity gate; the JSON report is unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SECTION = re.compile(r"^## Open(?:-ended)? questions\b", re.IGNORECASE)
QUESTION = re.compile(r"^### Q(\d+):\s*(\S.*?)\s*$", re.IGNORECASE)
ANSWER = re.compile(r"^#### Answer to Q(\d+)\b", re.IGNORECASE)
BOUNDARY = re.compile(r"^#{1,3}\s")
CONFIRMED = re.compile(
    r"^(?:Confirmed by the user(?: on \d{4}-\d{2}-\d{2})?:\s*|User decision:\s*confirmed\s*[\u2014\u2013:-]\s*)(\S.*)$",
    re.IGNORECASE,
)
PENDING = re.compile(
    r"^(?:Proposed\b|Awaiting user confirmation\b|"
    r"User decision:\s*(?:pending|deferred|undecided|reopened)\b)",
    re.IGNORECASE,
)
DECISION = re.compile(r"^(?:Confirmed by the user\b|User decision:)", re.IGNORECASE)
DIAGNOSTIC_REASONS = frozenset({"conflicting-decision-records", "ambiguous-decision-record"})


@dataclass(frozen=True)
class QuestionDecision:
    """One question's document position and evidence for its decision status."""

    id: str
    position: int
    title: str
    line: int
    status: str
    reason: str
    decision_line: int | None = None


def _question_id(number: str) -> str:
    """Normalize padded IDs while rejecting zero as a question number."""
    value = int(number)
    if value < 1:
        msg = "Question IDs must be positive"
        raise ValueError(msg)
    return f"Q{value:02d}"


def _visible_lines(text: str) -> list[tuple[int, str]]:
    """Keep original line numbers, excluding comments, fences and quotations."""
    text = re.sub(
        r"<!--.*?-->",
        lambda match: "\n" * match[0].count("\n"),
        text,
        flags=re.DOTALL,
    )
    result: list[tuple[int, str]] = []
    fence = ""
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if (
                marker
                and marker[1][0] == fence[0]
                and len(marker[1]) >= len(fence)
                and not marker[2].strip()
            ):
                fence = ""
        elif marker:
            fence = marker[1]
        elif not line.lstrip().startswith(">"):
            result.append((number, line))
    if fence:
        msg = "Unclosed Markdown fence; decision evidence cannot be classified"
        raise ValueError(msg)
    return result


def _answer_body(
    lines: list[tuple[int, str]],
    question_id: str,
) -> list[tuple[int, str]] | None:
    """Return the lines of the question's single answer section, or None without one."""
    starts = [
        (index, match)
        for index, (_, line) in enumerate(lines)
        if (match := ANSWER.match(line))
    ]
    if not starts:
        return None
    if len(starts) != 1 or _question_id(starts[0][1][1]) != question_id:
        msg = f"{question_id}: duplicate or mismatched answer heading"
        raise ValueError(msg)
    body = lines[starts[0][0] + 1 :]
    end = next(
        (offset for offset, (_, line) in enumerate(body) if re.match(r"^#{1,4}\s", line)),
        len(body),
    )
    return body[:end]


def _record_kind(line: str) -> str | None:
    """Name the decision record one answer line holds, or None for plain text."""
    if CONFIRMED.match(line):
        return "confirmed"
    if PENDING.match(line):
        return "pending"
    if DECISION.match(line):
        return "ambiguous"
    return None


def _classify(
    lines: list[tuple[int, str]],
    question_id: str,
) -> tuple[str, str, int | None]:
    """Classify only the active answer, preserving conflicting evidence."""
    answer = _answer_body(lines, question_id)
    if answer is None:
        return "undecided", "missing-answer", None
    records: dict[str, list[int]] = {}
    for number, line in answer:
        kind = _record_kind(line)
        if kind:
            records.setdefault(kind, []).append(number)
    confirmed = records.get("confirmed", [])
    if confirmed and sum(map(len, records.values())) > 1:
        return "undecided", "conflicting-decision-records", None
    if "ambiguous" in records:
        return "undecided", "ambiguous-decision-record", None
    if confirmed:
        return "confirmed", "explicit-user-decision", confirmed[0]
    return (
        "undecided",
        "pending-user-decision" if "pending" in records else "no-explicit-user-decision",
        None,
    )


def _section(lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Return the lines of the single open-questions section, empty without one."""
    sections = [index for index, (_, line) in enumerate(lines) if SECTION.match(line)]
    if len(sections) > 1:
        msg = "Multiple open-questions sections"
        raise ValueError(msg)
    if not sections:
        if any(QUESTION.match(line) for _, line in lines):
            msg = "Question headings exist without an open-questions section"
            raise ValueError(msg)
        return []
    section = lines[sections[0] + 1 :]
    end = next(
        (
            index
            for index, (_, line) in enumerate(section)
            if re.match(r"^#{1,2}\s", line)
        ),
        len(section),
    )
    return section[:end]


def parse_questions(text: str) -> list[QuestionDecision]:
    """Parse one open-questions section, rejecting malformed or duplicate IDs."""
    section = _section(_visible_lines(text))
    result: list[QuestionDecision] = []
    seen: set[str] = set()
    for index, (number, line) in enumerate(section):
        match = QUESTION.match(line)
        if not match:
            if re.match(r"^#{3,}\s+Q\w*\b", line, re.IGNORECASE):
                msg = f"Malformed question heading at line {number}"
                raise ValueError(msg)
            continue
        question_id = _question_id(match[1])
        if question_id in seen:
            msg = f"Duplicate question ID: {question_id}"
            raise ValueError(msg)
        seen.add(question_id)
        following = section[index + 1 :]
        boundary = next(
            (
                offset
                for offset, (_, value) in enumerate(following)
                if BOUNDARY.match(value)
            ),
            len(following),
        )
        status, reason, decision_line = _classify(following[:boundary], question_id)
        result.append(
            QuestionDecision(
                question_id,
                len(result) + 1,
                match[2],
                number,
                status,
                reason,
                decision_line,
            ),
        )
    return result


def _cursor(questions: list[QuestionDecision], after: str | None) -> int:
    """Return the document position of the ``--after`` question, or 0 without one."""
    if after is None:
        return 0
    if not re.fullmatch(r"Q\d+", after, re.IGNORECASE):
        msg = "--after must be a question ID such as Q59"
        raise ValueError(msg)
    cursor_id = _question_id(after[1:])
    cursor = next((item.position for item in questions if item.id == cursor_id), 0)
    if not cursor:
        msg = f"Unknown question cursor: {after}"
        raise ValueError(msg)
    return cursor


def _endpoint(questions: list[QuestionDecision], index: int) -> str | None:
    """Return the ID at one end of an ordered question list, or None when empty."""
    return questions[index].id if questions else None


def decision_report(document: Path, after: str | None = None) -> dict[str, object]:
    """Return ordered decision evidence and the next/last unresolved question."""
    content = document.read_bytes()
    if not content.strip():
        msg = "Document is empty"
        raise ValueError(msg)
    questions = parse_questions(content.decode("utf-8-sig"))
    cursor = _cursor(questions, after)
    undecided = [item for item in questions if item.status == "undecided"]
    following = [item for item in undecided if item.position > cursor]
    return {
        "document": str(document.resolve()),
        "document_sha256": hashlib.sha256(content).hexdigest(),
        "question_count": len(questions),
        "last_question": _endpoint(questions, -1),
        "undecided_count": len(undecided),
        "first_undecided": _endpoint(undecided, 0),
        "next_undecided": _endpoint(following, 0),
        "last_undecided": _endpoint(undecided, -1),
        "questions": [asdict(item) for item in questions],
        "diagnostics": [
            f"{item.id}: {item.reason}"
            for item in undecided
            if item.reason in DIAGNOSTIC_REASONS
        ],
    }


def main(argv: list[str] | None = None) -> int:
    """Print a JSON report; exit 2 on invalid input, including ambiguous records."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "document",
        type=Path,
        help="Exact Markdown path; relative to the current directory",
    )
    parser.add_argument(
        "--after",
        help="Return the next undecided question after this ID",
    )
    args = parser.parse_args(argv)
    try:
        report = decision_report(args.document, args.after)
    except (OSError, ValueError) as error:
        sys.stdout.write(json.dumps({"error": str(error)}, ensure_ascii=True) + "\n")
        return 2
    sys.stdout.write(json.dumps(report, ensure_ascii=True, indent=2) + "\n")
    return 2 if report["diagnostics"] else 0


if __name__ == "__main__":
    raise SystemExit(main())


# eof
