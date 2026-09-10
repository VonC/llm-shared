"""Fixed-path CLI for the pure paired specification answer renderer."""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, NoReturn, cast

# bin\spec_review_answer.bat runs this file by path, so sys.path[0] is the
# tools directory and the `tools.` package below is not importable from it.
# Bootstrap the repository root the way new_draft.py does, or the launcher
# fails with "No module named 'tools'" from every project.
if __name__ == "__main__":  # pragma: no cover - thin launcher boundary
    with contextlib.suppress(Exception):
        _project_root = Path(__file__).parent.parent.resolve()
        sys.path.insert(0, str(_project_root))

from tools.review_artifact_configuration import caller_file_parents
from tools.review_exchange_models import (
    ReviewDisposition,
    ReviewExchangeError,
    format_local_timestamp,
    positive_integer,
)
from tools.spec_review_answer import (
    SpecificationAssessment,
    render_specification_answer,
)
from tools.spec_review_request import specification_context

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from tools.review_exchange_models import ReviewContext

_FATAL_EXIT = 2
_SHA256_LENGTH = 64
_INPUT_LABELS = {
    "assessment": "assessment file",
    "question_verdicts": "question verdicts file",
    "writer_instructions": "writer instructions file",
    "requested_changes": "requested changes file",
    "covered_wording": "covered wording file",
    "convergence_rationale": "convergence rationale file",
    "guidance": "guidance file",
    "guidance_response": "guidance response file",
    "retained_manifest": "retained manifest file",
}
_MANIFEST_FIELDS = {
    "document_sha256",
    "identity",
    "original_round_number",
    "assessment_input_paths",
}


class _ArgumentParser(argparse.ArgumentParser):
    """Raise validation errors instead of terminating the host process."""

    def error(self, message: str) -> NoReturn:
        raise ReviewExchangeError(message)


def _positive_int(value: str) -> int:
    """Parse one positive command-line integer."""
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("value must be positive") from error
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def _disposition(value: str) -> ReviewDisposition:
    """Parse exactly one supported machine disposition."""
    try:
        return ReviewDisposition(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("invalid disposition") from error


def _is_effectively_ignored(project_root: Path, path: Path) -> bool:
    """Return whether Git excludes one exact root scratch path."""
    git = shutil.which("git")
    if git is None:
        raise ReviewExchangeError("git was not found for ignored-file validation")
    try:
        result = subprocess.run(  # noqa: S603 - fixed Git executable and arguments
            [git, "-C", str(project_root), "check-ignore", "--quiet", "--", str(path)],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise ReviewExchangeError(f"cannot validate ignored file: {error}") from error
    return result.returncode == 0


def _root_path(root: Path, value: str | Path, label: str, *, source: bool) -> Path:
    """Validate one regular, ignored home-local ``a.*`` path."""
    path = Path(value).expanduser().resolve()
    if path.parent not in caller_file_parents(root):
        raise ReviewExchangeError(f"{label} must be in the review artifact home")
    if not path.name.startswith("a."):
        raise ReviewExchangeError(f"{label} must use an a.* file name")
    if source and not path.is_file():
        raise ReviewExchangeError(f"{label} does not exist or is not a regular file")
    if not source and path.exists() and not path.is_file():
        raise ReviewExchangeError(f"{label} is not a regular file")
    if not _is_effectively_ignored(root, path):
        raise ReviewExchangeError(f"{label} is not effectively ignored")
    return path


def _read_utf8(path: Path, label: str) -> str:
    """Read one exact caller input once as strict UTF-8."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ReviewExchangeError(f"{label} is not valid UTF-8") from error
    except OSError as error:
        raise ReviewExchangeError(f"cannot read {label}: {error}") from error


def _document_sha256(document: Path) -> str:
    """Read current reviewed bytes once, require UTF-8, and return SHA-256."""
    try:
        content = document.read_bytes()
        content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ReviewExchangeError("reviewed document is not valid UTF-8") from error
    except OSError as error:
        raise ReviewExchangeError(f"cannot read reviewed document: {error}") from error
    return hashlib.sha256(content).hexdigest()


def _validate_manifest(
    content: str,
    *,
    digest: str,
    identity: Mapping[str, object],
    round_number: int,
    input_paths: list[Path],
) -> None:
    """Validate one exact single-use retained assessment manifest."""
    try:
        decoded: Any = json.loads(content)
    except json.JSONDecodeError as error:
        raise ReviewExchangeError(f"invalid retained manifest JSON: {error.msg}") from error
    if not isinstance(decoded, dict):
        raise ReviewExchangeError("retained manifest must be a JSON object")
    manifest = cast("dict[str, object]", decoded)
    if set(manifest) != _MANIFEST_FIELDS:
        raise ReviewExchangeError("retained manifest has invalid fields")
    original_round = positive_integer(
        manifest["original_round_number"],
        "retained manifest original round",
    )
    if original_round > round_number:
        raise ReviewExchangeError("retained manifest has invalid original round")
    expected_paths = [path.as_posix() for path in input_paths]
    if (
        manifest["document_sha256"] != digest
        or manifest["identity"] != identity
        or manifest["assessment_input_paths"] != expected_paths
    ):
        raise ReviewExchangeError("retained manifest differs from current context")


def _parser() -> _ArgumentParser:
    """Build the narrow explicit-file command contract."""
    parser = _ArgumentParser(description=__doc__)
    parser.add_argument("--document", required=True)
    parser.add_argument("--umbrella")
    parser.add_argument("--round-number", required=True, type=_positive_int)
    parser.add_argument("--disposition", required=True, type=_disposition)
    parser.add_argument("--expected-document-sha256", required=True)
    for flag in ("assessment", "question-verdicts", "writer-instructions"):
        parser.add_argument(f"--{flag}-file", required=True)
    for flag in (
        "requested-changes", "covered-wording", "convergence-rationale",
        "guidance", "guidance-response", "retained-manifest",
    ):
        parser.add_argument(f"--{flag}-file")
    parser.add_argument("--answer-content-output", required=True)
    parser.add_argument("--transcript-summary-output", required=True)
    return parser


def _temp_output(path: Path, content: str) -> Path:
    """Write and flush one same-directory temporary UTF-8 output."""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", delete=False,
            dir=path.parent, prefix=f".{path.name}.", suffix=".tmp",
        ) as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            return Path(stream.name)
    except OSError as error:
        raise ReviewExchangeError(f"cannot prepare paired outputs: {error}") from error


def _write_pair(first: Path, first_content: str, second: Path, second_content: str) -> None:
    """Publish both renderer outputs or restore their exact prior state."""
    originals = {path: path.read_bytes() if path.exists() else None for path in (first, second)}
    temporary = [_temp_output(first, first_content), _temp_output(second, second_content)]
    try:
        os.replace(temporary[0], first)  # noqa: PTH105 - atomic replace seam
        os.replace(temporary[1], second)  # noqa: PTH105 - atomic replace seam
    except OSError as error:
        for path, content in originals.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content)
        raise ReviewExchangeError(f"cannot write paired outputs: {error}") from error
    finally:
        for path in temporary:
            path.unlink(missing_ok=True)


def _validated_context(
    args: argparse.Namespace,
    project_root: Path,
) -> tuple[Path, ReviewContext, str]:
    """Validate the root, exact context, and assessed document digest."""
    root = project_root.expanduser().resolve()
    if not root.is_dir():
        raise ReviewExchangeError(f"project root is not a directory: {root}")
    context = specification_context(args.document, args.umbrella)
    digest = _document_sha256(context.document_path)
    expected_digest = args.expected_document_sha256.lower()
    if len(expected_digest) != _SHA256_LENGTH or any(
        char not in "0123456789abcdef" for char in expected_digest
    ):
        raise ReviewExchangeError("expected document SHA-256 is invalid")
    if digest != expected_digest:
        raise ReviewExchangeError("reviewed document content drifted since assessment")
    return root, context, digest


def _validated_paths(
    args: argparse.Namespace,
    root: Path,
) -> tuple[dict[str, Path], Path, Path]:
    """Resolve exact caller paths and reject every collision before reads."""
    inputs = {
        key: _root_path(root, getattr(args, f"{key}_file"), label, source=True)
        for key, label in _INPUT_LABELS.items()
        if getattr(args, f"{key}_file") is not None
    }
    answer = _root_path(root, args.answer_content_output, "answer content output", source=False)
    summary = _root_path(
        root, args.transcript_summary_output, "transcript summary output", source=False,
    )
    all_paths = [*inputs.values(), answer, summary]
    if len(set(all_paths)) != len(all_paths):
        raise ReviewExchangeError("caller paths must be distinct")
    return inputs, answer, summary


def _authored_inputs(
    inputs: dict[str, Path],
    *,
    digest: str,
    context: ReviewContext,
    round_number: int,
) -> dict[str, str]:
    """Read every exact input once and validate optional retained evidence."""
    authored = {
        key: _read_utf8(path, _INPUT_LABELS[key]) for key, path in inputs.items()
    }
    manifest = authored.pop("retained_manifest", None)
    assessment_paths = [path for key, path in inputs.items() if key != "retained_manifest"]
    if manifest is not None:
        _validate_manifest(
            manifest, digest=digest, identity=context.identity.to_dict(),
            round_number=round_number, input_paths=assessment_paths,
        )
    return authored


def _render(args: argparse.Namespace, project_root: Path) -> None:
    """Validate exact inputs, render once, and publish only the ignored pair."""
    root, context, digest = _validated_context(args, project_root)
    inputs, answer, summary = _validated_paths(args, root)
    authored = _authored_inputs(
        inputs,
        digest=digest,
        context=context,
        round_number=args.round_number,
    )
    rendered = render_specification_answer(
        SpecificationAssessment(
            context=context, project_root=root, round_number=args.round_number,
            created_at=format_local_timestamp(), disposition=args.disposition,
            assessment=authored["assessment"],
            question_verdicts=authored["question_verdicts"],
            writer_instructions=authored["writer_instructions"],
            requested_changes=authored.get("requested_changes"),
            covered_wording=authored.get("covered_wording"),
            convergence_rationale=authored.get("convergence_rationale"),
            human_guidance=authored.get("guidance"),
            guidance_response=authored.get("guidance_response"),
        ),
    )
    _write_pair(answer, rendered.answer_content, summary, rendered.transcript_summary)


def main(argv: Sequence[str] | None = None, *, project_root: Path | None = None) -> int:
    """Run the answer renderer with one stable validation-error exit code."""
    try:
        args = _parser().parse_args(argv)
        _render(args, Path.cwd() if project_root is None else project_root)
    except ReviewExchangeError as error:
        sys.stderr.write(f"spec_review_answer: {error}\n")
        return _FATAL_EXIT
    return 0


if __name__ == "__main__":  # pragma: no cover - thin launcher boundary
    raise SystemExit(main())


# eof
