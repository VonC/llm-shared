#!/usr/bin/env python3
"""Non-interactive command adapter for executable code-review evidence."""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

# bin\code_review_evidence.bat runs this file by path, so sys.path[0] is the
# tools directory and the `tools.` package below is not importable from it.
# Bootstrap the repository root the way new_draft.py does, or the launcher
# fails with "No module named 'tools'" from every project.
if __name__ == "__main__":  # pragma: no cover - thin launcher boundary
    with contextlib.suppress(Exception):
        _project_root = Path(__file__).parent.parent.resolve()
        sys.path.insert(0, str(_project_root))

from tools.code_review_evidence import (
    CodeReviewEvidence,
    RecordedBlob,
    UmbrellaDigest,
    ValidationState,
    attribute_reviewer_patch,
    capture_index_tree,
    capture_umbrella_digest,
    capture_validation_state,
    compare_umbrella_digest,
    compare_validation_state,
    read_manifest,
    record_pre_repair_blob,
    retire_manifest,
    write_manifest,
)
from tools.review_exchange_models import ReviewExchangeError

_FATAL_EXIT = 2

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


class _ArgumentParser(argparse.ArgumentParser):
    """Raise parser failures through the stable evidence error boundary."""

    def error(self, message: str) -> NoReturn:
        raise ReviewExchangeError(message)


def _identity_arguments(parser: argparse.ArgumentParser) -> None:
    for name in ("family", "type-token", "version", "slug", "implementation-step"):
        parser.add_argument(f"--{name}", required=True)


def _identity(args: argparse.Namespace) -> tuple[str, str, str, str, str]:
    """Return the exact retained-evidence identity from parsed arguments."""
    return (args.family, args.type_token, args.version, args.slug, args.implementation_step)


def _repository_file(root: Path, value: str | Path, label: str) -> Path:
    """Resolve one caller-named file without escaping the selected repository."""
    supplied = Path(value)
    if supplied.is_absolute():
        raise ReviewExchangeError(f"{label} must be repository-relative")
    candidate = (root / supplied).resolve()
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise ReviewExchangeError(f"{label} must be repository-relative") from error
    if not relative.parts:
        raise ReviewExchangeError(f"{label} must name a file")
    return candidate


def _read_json(root: Path, path: str | Path) -> object:
    """Read one repository-contained UTF-8 JSON input by explicit path."""
    source = _repository_file(root, path, "evidence JSON path")
    try:
        return json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ReviewExchangeError(f"cannot read evidence JSON: {error}") from error


class CodeReviewEvidenceCli:
    """Typed dispatcher with no prompt, path escape, or implicit selection."""

    def __init__(self) -> None:
        """Build the complete non-interactive parser once."""
        self.parser = self._parser()

    @staticmethod
    def _parser() -> _ArgumentParser:
        parser = _ArgumentParser(prog="code-review-evidence")
        parser.add_argument("--repository", default=".")
        commands = parser.add_subparsers(dest="operation", required=True)
        commands.add_parser("capture-index-tree")
        blob = commands.add_parser("record-pre-repair-blob")
        blob.add_argument("path")
        patch = commands.add_parser("attribute-reviewer-patch")
        patch.add_argument("baseline_json")
        umbrella = commands.add_parser("umbrella-digest")
        umbrella_commands = umbrella.add_subparsers(dest="umbrella_operation", required=True)
        umbrella_capture = umbrella_commands.add_parser("capture")
        umbrella_capture.add_argument("path", nargs="?")
        umbrella_compare = umbrella_commands.add_parser("compare")
        umbrella_compare.add_argument("baseline_json")
        umbrella_compare.add_argument("path", nargs="?")
        validation = commands.add_parser("validation-state")
        validation_commands = validation.add_subparsers(dest="validation_operation", required=True)
        validation_capture = validation_commands.add_parser("capture")
        validation_capture.add_argument("paths", nargs="+")
        validation_compare = validation_commands.add_parser("compare")
        validation_compare.add_argument("before_json")
        validation_compare.add_argument("after_json")
        manifest_write = commands.add_parser("write-manifest")
        manifest_write.add_argument("evidence_json")
        for name in ("read-manifest", "retire-manifest"):
            command = commands.add_parser(name)
            _identity_arguments(command)
        return parser

    def dispatch(self, args: argparse.Namespace) -> object:
        """Dispatch one parsed operation through its typed evidence helper."""
        root = Path(args.repository).expanduser().resolve()
        handlers: dict[str, Callable[[Path, argparse.Namespace], object]] = {
            "capture-index-tree": self._capture_index,
            "record-pre-repair-blob": self._record_blob,
            "attribute-reviewer-patch": self._attribute_patch,
            "umbrella-digest": self._umbrella_digest,
            "validation-state": self._validation_state,
            "write-manifest": self._write_manifest,
            "read-manifest": self._read_manifest,
            "retire-manifest": self._retire_manifest,
        }
        handler = handlers.get(args.operation)
        if handler is None:
            raise ReviewExchangeError("unsupported evidence operation")
        return handler(root, args)

    @staticmethod
    def _capture_index(root: Path, _args: argparse.Namespace) -> object:
        return {"index_tree": capture_index_tree(root)}

    @staticmethod
    def _record_blob(root: Path, args: argparse.Namespace) -> object:
        return record_pre_repair_blob(root, args.path).to_payload()

    @staticmethod
    def _attribute_patch(root: Path, args: argparse.Namespace) -> object:
        baseline = RecordedBlob.from_payload(_read_json(root, args.baseline_json))
        return attribute_reviewer_patch(root, baseline).to_payload()

    @staticmethod
    def _umbrella_digest(root: Path, args: argparse.Namespace) -> object:
        path = (
            None
            if args.path is None
            else _repository_file(root, args.path, "umbrella path")
        )
        if args.umbrella_operation == "capture":
            return capture_umbrella_digest(path).to_payload()
        baseline = UmbrellaDigest.from_payload(_read_json(root, args.baseline_json))
        return compare_umbrella_digest(baseline, path).to_payload()

    @staticmethod
    def _validation_state(root: Path, args: argparse.Namespace) -> object:
        if args.validation_operation == "capture":
            return capture_validation_state(root, args.paths).to_payload()
        before = ValidationState.from_payload(_read_json(root, args.before_json))
        after = ValidationState.from_payload(_read_json(root, args.after_json))
        return compare_validation_state(before, after).to_payload()

    @staticmethod
    def _write_manifest(root: Path, args: argparse.Namespace) -> object:
        retained = CodeReviewEvidence.from_payload(_read_json(root, args.evidence_json))
        return {"manifest": write_manifest(root, retained).as_posix()}

    @staticmethod
    def _read_manifest(root: Path, args: argparse.Namespace) -> object:
        return read_manifest(root, _identity(args)).to_payload()

    @staticmethod
    def _retire_manifest(root: Path, args: argparse.Namespace) -> object:
        return {"retired": retire_manifest(root, _identity(args))}

    def run(self, arguments: Sequence[str] | None = None) -> int:
        """Parse, dispatch, and emit one canonical JSON result."""
        args = self.parser.parse_args(arguments)
        payload = self.dispatch(args)
        sys.stdout.write(json.dumps(payload, sort_keys=True) + "\n")
        return 0


def main(arguments: Sequence[str] | None = None) -> int:
    """Run the evidence adapter and report one stable fatal exit on failure."""
    try:
        return CodeReviewEvidenceCli().run(arguments)
    except ReviewExchangeError as error:
        sys.stderr.write(f"ERROR: {error}\n")
        return _FATAL_EXIT


if __name__ == "__main__":  # pragma: no cover - direct launcher path
    raise SystemExit(main())


# eof
