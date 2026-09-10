"""Render one validated code-review answer and transcript summary pair."""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import argparse
import contextlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

# bin\code_review_answer.bat runs this file by path, so sys.path[0] is the
# tools directory and the `tools.` package below is not importable from it.
# Bootstrap the repository root the way new_draft.py does, or the launcher
# fails with "No module named 'tools'" from every project.
if __name__ == "__main__":  # pragma: no cover - thin launcher boundary
    with contextlib.suppress(Exception):
        _project_root = Path(__file__).parent.parent.resolve()
        sys.path.insert(0, str(_project_root))

from tools.code_review_answer import (
    EarlyRejectionAssessment,
    ImplementationAssessment,
    render_code_review_answer,
)
from tools.code_review_evidence import (
    capture_index_tree,
    manifest_path,
    read_manifest,
)
from tools.code_review_request import code_review_context
from tools.review_artifact_configuration import caller_file_parents
from tools.review_exchange_models import (
    ReviewContext,
    ReviewDisposition,
    ReviewExchangeError,
    format_local_timestamp,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

_FATAL_EXIT = 2
_ASSESSMENT_KEYS = (
    "implementation_check",
    "validation_plan_effects",
    "pre_repair_validation",
    "resolved_validation_set",
    "resolver_drift",
    "repository_state_comparison",
    "repairs",
    "staged_paths",
    "commit_plan_assessment",
    "unresolved_findings",
    "boundary_crossing_work",
    "decision_rationale",
    "retained_manifest",
)
_INPUT_LABELS = {
    "disagreement": "disagreement file",
    "implementation_check": "implementation check file",
    "validation_plan_effects": "validation plan effects file",
    "pre_repair_validation": "pre-repair validation file",
    "resolved_validation_set": "resolved validation set file",
    "resolver_drift": "resolver drift file",
    "repository_state_comparison": "repository state comparison file",
    "repairs": "repairs file",
    "staged_paths": "staged paths file",
    "commit_plan_assessment": "commit plan assessment file",
    "unresolved_findings": "unresolved findings file",
    "boundary_crossing_work": "boundary-crossing work file",
    "writer_instructions": "writer instructions file",
    "decision_rationale": "decision rationale file",
    "guidance": "guidance file",
    "guidance_response": "guidance response file",
    "retained_manifest": "retained manifest file",
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
    """Map the reviewer-facing decision names onto protocol dispositions."""
    choices = {
        "changes-requested": ReviewDisposition.CHANGES_REQUESTED,
        "commit-ready": ReviewDisposition.CONVERGENCE_RECOMMENDED,
    }
    try:
        return choices[value]
    except KeyError as error:
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


def _root_path(
    root: Path,
    value: str | Path,
    label: str,
    *,
    source: bool,
    parents: frozenset[Path] | None = None,
) -> Path:
    """Validate one regular, ignored ``a.*`` path in an accepted directory."""
    path = Path(value).expanduser().resolve()
    accepted = caller_file_parents(root) if parents is None else parents
    if path.parent not in accepted:
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
    """Read one exact caller-authored input once as strict UTF-8."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ReviewExchangeError(f"{label} is not valid UTF-8") from error
    except OSError as error:
        raise ReviewExchangeError(f"cannot read {label}: {error}") from error


def _parser() -> _ArgumentParser:
    """Build the explicit answer-variant command contract."""
    parser = _ArgumentParser(description=__doc__)
    parser.add_argument("--document", required=True)
    parser.add_argument("--umbrella")
    parser.add_argument("--implementation-step", required=True)
    parser.add_argument("--round-number", required=True, type=_positive_int)
    parser.add_argument("--exchange-occurrence", required=True, type=_positive_int)
    parser.add_argument(
        "--answer-kind", required=True, choices=("early-rejection", "assessment"),
    )
    parser.add_argument("--disposition", required=True, type=_disposition)
    for flag in (
        "disagreement",
        "implementation-check",
        "validation-plan-effects",
        "pre-repair-validation",
        "resolved-validation-set",
        "resolver-drift",
        "repository-state-comparison",
        "repairs",
        "staged-paths",
        "commit-plan-assessment",
        "unresolved-findings",
        "boundary-crossing-work",
        "writer-instructions",
        "decision-rationale",
        "guidance",
        "guidance-response",
        "retained-manifest",
    ):
        parser.add_argument(f"--{flag}-file")
    parser.add_argument("--substantive-repair", action="store_true")
    parser.add_argument("--readiness-floor-incomplete", action="store_true")
    parser.add_argument("--answer-content-output", required=True)
    parser.add_argument("--transcript-summary-output", required=True)
    return parser


def _temp_output(path: Path, content: str) -> Path:
    """Write and flush one same-directory temporary UTF-8 output."""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            delete=False,
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
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


def _validate_early_variant(args: argparse.Namespace) -> None:
    """Require the narrow early-rejection evidence shape."""
    if args.disagreement_file is None:
        raise ReviewExchangeError("disagreement file is required")
    if any(getattr(args, f"{key}_file") is not None for key in _ASSESSMENT_KEYS):
        raise ReviewExchangeError("early-rejection cannot carry assessment evidence")
    if args.substantive_repair or args.readiness_floor_incomplete:
        raise ReviewExchangeError("early-rejection cannot carry assessment flags")


def _validate_assessment_variant(args: argparse.Namespace) -> None:
    """Require the complete implementation-assessment evidence shape."""
    if args.disagreement_file is not None:
        raise ReviewExchangeError("assessment cannot carry disagreement evidence")
    for key in _ASSESSMENT_KEYS:
        if getattr(args, f"{key}_file") is None:
            raise ReviewExchangeError(f"{_INPUT_LABELS[key]} is required")


def _validate_variant(args: argparse.Namespace) -> None:
    """Require one exact evidence shape before resolving or reading files."""
    if args.writer_instructions_file is None:
        raise ReviewExchangeError("writer instructions file is required")
    if (args.guidance_file is None) != (args.guidance_response_file is None):
        raise ReviewExchangeError("guidance and guidance response files must be paired")
    if args.answer_kind == "early-rejection":
        _validate_early_variant(args)
    else:
        _validate_assessment_variant(args)


def _validated_paths(
    args: argparse.Namespace,
    root: Path,
) -> tuple[dict[str, Path], Path, Path]:
    """Resolve exact caller paths and reject collisions before any read."""
    parents = caller_file_parents(root)
    inputs = {
        key: _root_path(root, value, _INPUT_LABELS[key], source=True, parents=parents)
        for key in _INPUT_LABELS
        if (value := getattr(args, f"{key}_file")) is not None
    }
    answer = _root_path(
        root,
        args.answer_content_output,
        "answer content output",
        source=False,
        parents=parents,
    )
    summary = _root_path(
        root,
        args.transcript_summary_output,
        "transcript summary output",
        source=False,
        parents=parents,
    )
    all_paths = [*inputs.values(), answer, summary]
    if len(set(all_paths)) != len(all_paths):
        raise ReviewExchangeError("caller paths must be distinct")
    return inputs, answer, summary


def _authored_inputs(inputs: dict[str, Path]) -> dict[str, str]:
    """Read every authored evidence file once, excluding the typed manifest."""
    return {
        key: _read_utf8(path, _INPUT_LABELS[key])
        for key, path in inputs.items()
        if key != "retained_manifest"
    }


def _inventory(content: str) -> tuple[str, ...]:
    """Parse one line-oriented authored inventory, including an explicit none."""
    items = tuple(line.strip() for line in content.splitlines() if line.strip())
    if len(items) == 1 and items[0].casefold() in {"none", "none."}:
        return ()
    return items


def _assessment_source(
    args: argparse.Namespace,
    root: Path,
    context: ReviewContext,
    inputs: dict[str, Path],
    authored: dict[str, str],
) -> ImplementationAssessment:
    """Verify live retained evidence and build one full assessment."""
    step = context.implementation_step
    if step is None:
        raise ReviewExchangeError("implementation step must be present")
    identity = (
        "code",
        "code",
        context.identity.version,
        context.identity.slug,
        step,
    )
    expected_manifest = manifest_path(root, identity).resolve()
    if inputs["retained_manifest"] != expected_manifest:
        raise ReviewExchangeError("retained manifest file must be the exact live evidence manifest")
    retained = read_manifest(root, identity)
    if capture_index_tree(root) != retained.assessed_index_tree:
        raise ReviewExchangeError("assessed index tree differs from live index")
    return ImplementationAssessment(
        context=context,
        project_root=root,
        round_number=args.round_number,
        exchange_occurrence=args.exchange_occurrence,
        created_at=format_local_timestamp(),
        disposition=args.disposition,
        baseline_index_tree=retained.baseline_index_tree,
        assessed_index_tree=retained.assessed_index_tree,
        implementation_check=authored["implementation_check"],
        validation_plan_effects=authored["validation_plan_effects"],
        pre_repair_validation=authored["pre_repair_validation"],
        resolved_validation_set=authored["resolved_validation_set"],
        resolver_drift=authored["resolver_drift"],
        repository_state_comparison=authored["repository_state_comparison"],
        repairs=_inventory(authored["repairs"]),
        staged_paths=_inventory(authored["staged_paths"]),
        commit_plan_assessment=authored["commit_plan_assessment"],
        unresolved_findings=_inventory(authored["unresolved_findings"]),
        boundary_crossing_work=_inventory(authored["boundary_crossing_work"]),
        writer_instructions=authored["writer_instructions"],
        decision_rationale=authored["decision_rationale"],
        substantive_repair=args.substantive_repair,
        readiness_floor_complete=not args.readiness_floor_incomplete,
        human_guidance=authored.get("guidance"),
        guidance_response=authored.get("guidance_response"),
    )


def _render(args: argparse.Namespace, project_root: Path) -> None:
    """Validate, render once, and publish only the ignored output pair."""
    root = project_root.expanduser().resolve()
    if not root.is_dir():
        raise ReviewExchangeError(f"project root is not a directory: {root}")
    _validate_variant(args)
    context = code_review_context(args.document, args.implementation_step, args.umbrella)
    inputs, answer, summary = _validated_paths(args, root)
    authored = _authored_inputs(inputs)
    if args.answer_kind == "early-rejection":
        source = EarlyRejectionAssessment(
            context=context,
            project_root=root,
            round_number=args.round_number,
            exchange_occurrence=args.exchange_occurrence,
            created_at=format_local_timestamp(),
            disposition=args.disposition,
            disagreement=authored["disagreement"],
            writer_instructions=authored["writer_instructions"],
            human_guidance=authored.get("guidance"),
            guidance_response=authored.get("guidance_response"),
        )
    else:
        source = _assessment_source(args, root, context, inputs, authored)
    rendered = render_code_review_answer(source)
    _write_pair(answer, rendered.answer_content, summary, rendered.transcript_summary)


def main(argv: Sequence[str] | None = None, *, project_root: Path | None = None) -> int:
    """Run the renderer with one stable validation-error exit code."""
    try:
        args = _parser().parse_args(argv)
        _render(args, Path.cwd() if project_root is None else project_root)
    except ReviewExchangeError as error:
        sys.stderr.write(f"code_review_answer: {error}\n")
        return _FATAL_EXIT
    return 0


if __name__ == "__main__":  # pragma: no cover - thin launcher boundary
    raise SystemExit(main())


__all__ = ["main"]


# eof
