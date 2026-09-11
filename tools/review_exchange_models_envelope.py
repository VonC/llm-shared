"""Review-content envelope handling for the v0.11.0 exchange core.

Step 2 keeps strict request and answer metadata compatible with legacy content
while every new rendering carries a two-role LLM-nature snapshot.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, cast

from tools.review_exchange_models import (
    ExchangeIdentity,
    ReviewContext,
    ReviewDisposition,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
    enum_value,
    mapping_value,
    optional_path_value,
    optional_string,
    path_value,
    positive_integer,
    strict_fields,
    validate_local_timestamp,
)
from tools.review_role_nature import RoleNatureSnapshot

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path
    from typing import Any


_H1_RE = re.compile(r"\A# [^\r\n]+\r?\n")
_JSON_SECTION_RE = re.compile(r"\A\r?\n## JSON\r?\n\r?\n```json\r?\n")


@dataclass(frozen=True)
class Envelope:
    """Strict machine-readable metadata for request and answer Markdown."""

    identity: ExchangeIdentity
    umbrella_path: Path | None
    document_path: Path
    implementation_step: str | None
    role: ReviewRole
    round_number: int
    created_at: str
    disposition: ReviewDisposition | None = None
    role_natures: RoleNatureSnapshot = field(default_factory=RoleNatureSnapshot)

    def __post_init__(self) -> None:
        """Validate role, round, timestamp, and family context fields."""
        object.__setattr__(self, "document_path", self.document_path.resolve())
        if self.umbrella_path is not None:
            object.__setattr__(self, "umbrella_path", self.umbrella_path.resolve())
        positive_integer(self.round_number, "envelope round")
        validate_local_timestamp(self.created_at)
        if self.role is ReviewRole.REVIEWER and self.disposition is None:
            raise ReviewExchangeError("reviewer envelope requires a disposition")
        if self.role is not ReviewRole.REVIEWER and self.disposition is not None:
            raise ReviewExchangeError(
                f"{self.role.value} envelope cannot declare a disposition",
            )
        if self.identity.family is ReviewFamily.CODE:
            if not self.implementation_step:
                raise ReviewExchangeError("code envelope requires an implementation step")
        elif self.implementation_step is not None:
            raise ReviewExchangeError(
                "implementation step is only valid for code review",
            )

    def to_dict(self) -> dict[str, Any]:
        """Return strict JSON-compatible envelope data."""
        return {
            "identity": self.identity.to_dict(),
            "umbrella_path": (
                self.umbrella_path.as_posix() if self.umbrella_path is not None else None
            ),
            "document_path": self.document_path.as_posix(),
            "implementation_step": self.implementation_step,
            "role": self.role.value,
            "round_number": self.round_number,
            "created_at": self.created_at,
            "disposition": self.disposition.value if self.disposition is not None else None,
            "role_natures": self.role_natures.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Envelope:
        """Construct an envelope from strict JSON-compatible data."""
        expected = {
            "identity", "umbrella_path", "document_path", "implementation_step",
            "role", "round_number", "created_at", "disposition",
        }
        legacy = "role_natures" not in data
        if not legacy:
            expected.add("role_natures")
        strict_fields(data, expected, "envelope")
        identity_data = mapping_value(data["identity"], "envelope identity")
        disposition_value = data["disposition"]
        disposition = (
            None
            if disposition_value is None
            else enum_value(
                ReviewDisposition,
                disposition_value,
                "review disposition",
            )
        )
        created_at = data["created_at"]
        if not isinstance(created_at, str):
            raise ReviewExchangeError("invalid envelope creation timestamp")
        return cls(
            identity=ExchangeIdentity.from_dict(identity_data),
            umbrella_path=optional_path_value(data["umbrella_path"], "umbrella path"),
            document_path=path_value(data["document_path"], "document path"),
            implementation_step=optional_string(
                data["implementation_step"],
                "implementation step",
            ),
            role=enum_value(ReviewRole, data["role"], "review role"),
            round_number=positive_integer(data["round_number"], "envelope round"),
            created_at=created_at,
            disposition=disposition,
            role_natures=RoleNatureSnapshot.from_optional_dict(
                None
                if legacy
                else mapping_value(data["role_natures"], "envelope role natures"),
            ),
        )


def render_json_markdown(title: str, data: Mapping[str, Any], content: str) -> str:
    """Render titled Markdown with JSON as its first section."""
    if not title.strip() or "\n" in title or "\r" in title:
        raise ReviewExchangeError("Markdown title must be one non-empty line")
    metadata = json.dumps(data, indent=2, sort_keys=True)
    prefix = f"# {title}\n\n## JSON\n\n```json\n{metadata}\n```\n"
    return prefix if not content else f"{prefix}\n{content}"


def parse_json_markdown(markdown: str) -> tuple[Mapping[str, Any], str]:
    """Parse the first JSON section from one titled Markdown document."""
    title = _H1_RE.match(markdown)
    if title is None:
        raise ReviewExchangeError("review Markdown must start with an H1 title")
    remainder = markdown[title.end() :]
    opener = _JSON_SECTION_RE.match(remainder)
    if opener is None:
        raise ReviewExchangeError("first Markdown section must be ## JSON")
    payload_start = title.end() + opener.end()
    closer = re.search(r"(?m)^```[ \t]*(?:\r?\n|$)", markdown[payload_start:])
    if closer is None:
        raise ReviewExchangeError("JSON metadata fence is not closed")
    payload_end = payload_start + closer.start()
    content_start = payload_start + closer.end()
    content = markdown[content_start:]
    if content.startswith("\r\n"):
        content = content[2:]
    elif content.startswith("\n"):
        content = content[1:]
    try:
        data = json.loads(markdown[payload_start:payload_end])
    except json.JSONDecodeError as error:
        raise ReviewExchangeError(f"invalid envelope JSON: {error.msg}") from error
    return mapping_value(data, "JSON section"), content


def render_envelope_markdown(envelope: Envelope, content: str) -> str:
    """Render one titled request or answer with JSON as its first section."""
    artifact = "request" if envelope.role is ReviewRole.REQUESTOR else "answer"
    title = f"Review {artifact} for {envelope.identity.key}"
    return render_json_markdown(title, envelope.to_dict(), content)


def parse_envelope_markdown(markdown: str) -> tuple[Envelope, str]:
    """Parse the first JSON section and return later Markdown unchanged."""
    data, content = parse_json_markdown(markdown)
    first_authored_heading = re.search(r"(?m)^(#{1,6}) ", content)
    if first_authored_heading is not None and first_authored_heading.group(1) != "##":
        raise ReviewExchangeError("authored Markdown sections must start at H2")
    return Envelope.from_dict(data), content


def _summary_value(summary: str, label: str) -> str:
    """Read exactly one human-readable identity field from a summary."""
    prefix = f"{label}: "
    values = [line[len(prefix) :] for line in summary.splitlines() if line.startswith(prefix)]
    if len(values) != 1:
        raise ReviewExchangeError(f"summary identity mismatch: expected one {label} field")
    return values[0]


def validate_summary_identity(
    summary: str,
    context: ReviewContext,
    round_number: int,
) -> None:
    """Fail when human-readable request identity differs from machine context."""
    positive_integer(round_number, "review round")
    umbrella = (
        context.umbrella_path.as_posix()
        if context.umbrella_path is not None
        else "none"
    )
    expected = {"Umbrella draft": umbrella, "Review round": str(round_number)}
    if context.identity.family is ReviewFamily.SPECIFICATION:
        expected["Reviewed specification"] = context.document_path.as_posix()
    else:
        expected["Implementation plan"] = context.document_path.as_posix()
        step = cast("str", context.implementation_step)
        expected["Implementation step"] = step
    mismatches = [
        label
        for label, value in expected.items()
        if _summary_value(summary, label) != value
    ]
    if mismatches:
        raise ReviewExchangeError(
            "summary identity mismatch: " + ", ".join(mismatches),
        )


# eof
