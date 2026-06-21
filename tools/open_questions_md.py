"""Manage the ``## Open questions`` section of a design/requirement document.

This tool operates on a ``<type>.vX.Y.Z.<topic>.md`` document (for example
``design.v1.2.3.cdc-gap.md``) and its companion scratch file
``a.<base>.open.questions.md`` kept at the project root, where ``<base>`` is the
document name without its ``.md`` suffix. The companion of
``design.v1.2.3.cdc-gap.md`` is therefore
``a.design.v1.2.3.cdc-gap.open.questions.md``.

The project root is located with the shared ``find_project_root`` helper, so the
tool honors ``PRJ_DIR`` and otherwise walks up to the first ``.git`` directory,
exactly like the other tools in this package. The document itself is looked up
under ``<root>/docs/<name>`` first, then ``<root>/docs/<vX.Y.Z>/<name>`` when a
version token is present in the name. The document must exist and be non-empty;
otherwise the tool fails early with a fatal error.

Exactly one of three mutually exclusive modes must be selected:

- ``--create``: create the companion file at the project root, truncating it
  back to empty when it already exists.
- ``--strip``: remove from the document the first line matching
  ``^## Open questions.*$`` and every line after it (truncate at the marker),
  then collapse any trailing blank lines so the document ends with a single
  newline rather than a run of blank lines that would trip the
  MD012/no-multiple-blanks markdown rule. When no such line is found the
  document is left untouched.
- ``--append``: append the companion's ``## Open questions`` section (the first
  line matching ``^## Open questions.*$`` and every line after it) to the
  document, keeping exactly one empty line between the document's last
  non-empty line and the section.

Exit codes: ``0`` on success, ``EXIT_FATAL`` (2) for any fatal error.
"""

from __future__ import annotations

import argparse
import contextlib
import logging
import re
import sys
from pathlib import Path
from typing import NoReturn

if __name__ == "__main__":
    with contextlib.suppress(Exception):
        _project_root = Path(__file__).parent.parent.resolve()
        sys.path.insert(0, str(_project_root))

from tools import find_project_root

# Name of the documentation folder, relative to the project root.
DOCS_DIR_NAME = "docs"
# Suffix of the documents this tool operates on.
MD_SUFFIX = ".md"
# Companion file name = COMPANION_PREFIX + <base> + COMPANION_SUFFIX.
COMPANION_PREFIX = "a."
COMPANION_SUFFIX = ".open.questions.md"
# A line that opens the open-questions section: "## Open questions" + anything.
MARKER_PATTERN = re.compile(r"^## Open questions.*$")
# A version token inside a document name, such as "v1.2.3" or "v8.11".
VERSION_PATTERN = re.compile(r"v\d+(?:\.\d+)+")
# Separator inserted before an appended section so exactly one empty line sits
# between the document's last non-empty line and the section.
SECTION_SEPARATOR = "\n\n"
# Exit code used by the script entry point for fatal errors.
EXIT_FATAL = 2

LOGGER = logging.getLogger("open_questions_md")


class OpenQuestionsError(Exception):
    """Base exception raised by the open-questions tool."""


def _configure_logging() -> None:
    """Configure a single stdout handler at INFO level for the tool."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


def _extract_version(name: str) -> str | None:
    """Return the version token of a document name, or None when absent.

    Args:
        name: The document file name, such as ``design.v1.2.3.cdc-gap.md``.

    Returns:
        The first version token found (for example ``v1.2.3``), or ``None``
        when the name carries no ``vX.Y...`` token.
    """
    match = VERSION_PATTERN.search(name)
    return match.group(0) if match else None


def _companion_name(base: str) -> str:
    """Build the companion file name for a document base name.

    Args:
        base: The document name without its ``.md`` suffix.

    Returns:
        The companion file name, ``a.<base>.open.questions.md``.
    """
    return f"{COMPANION_PREFIX}{base}{COMPANION_SUFFIX}"


def _resolve_doc(root: Path, name: str) -> Path:
    """Locate a non-empty document under the docs folder.

    The lookup tries ``<root>/docs/<name>`` first, then
    ``<root>/docs/<version>/<name>`` when ``name`` carries a version token. The
    first candidate that exists and is non-empty is returned.

    Args:
        root: The resolved project root directory.
        name: The document file name to locate.

    Returns:
        The absolute path to the existing, non-empty document.

    Raises:
        OpenQuestionsError: When no candidate exists, or every candidate that
            does exist is empty.
    """
    docs_dir = root / DOCS_DIR_NAME
    version = _extract_version(name)
    candidates = [docs_dir / name]
    if version:
        candidates.append(docs_dir / version / name)

    empty_hits: list[Path] = []
    for candidate in candidates:
        if not candidate.is_file():
            continue
        if candidate.read_text(encoding="utf-8").strip():
            return candidate
        empty_hits.append(candidate)

    if empty_hits:
        joined = ", ".join(str(path) for path in empty_hits)
        msg = f"Document '{name}' exists but is empty: {joined}"
        raise OpenQuestionsError(msg)

    searched = ", ".join(str(candidate) for candidate in candidates)
    msg = f"Document '{name}' not found under: {searched}"
    raise OpenQuestionsError(msg)


def _strip_open_questions(text: str) -> tuple[str, bool]:
    """Remove the open-questions section from a document body.

    The text kept before the marker is right-trimmed of trailing blank or
    whitespace-only lines and closed with a single newline, so a marker
    preceded by one or more blank lines never strips down to a document ending
    in a run of blank lines (which would trip the MD012/no-multiple-blanks
    markdown rule).

    Args:
        text: The full document text.

    Returns:
        A tuple ``(new_text, changed)``. When a marker line is found,
        ``new_text`` holds every line before it, right-trimmed to a single
        trailing newline (or the empty string when nothing precedes the
        marker), and ``changed`` is ``True``. Otherwise the original text is
        returned with ``changed`` set to ``False``.
    """
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if MARKER_PATTERN.match(line.rstrip("\r\n")):
            body = "".join(lines[:index]).rstrip()
            return (f"{body}\n" if body else ""), True
    return text, False


def _extract_section(text: str) -> str | None:
    """Return the open-questions section of a companion file.

    Args:
        text: The full companion file text.

    Returns:
        The marker line and every line after it, or ``None`` when no marker
        line is present.
    """
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if MARKER_PATTERN.match(line.rstrip("\r\n")):
            return "".join(lines[index:])
    return None


def _append_section(doc_text: str, section: str) -> str:
    """Append a section to a document with one empty line before it.

    Trailing blank or whitespace-only lines of the document are dropped so the
    result keeps exactly one empty line between the document's last non-empty
    line and the appended section.

    Args:
        doc_text: The current document text.
        section: The open-questions section to append.

    Returns:
        The document text ending with the last non-empty line, one empty line,
        the appended section, and a single trailing newline.
    """
    body = doc_text.rstrip()
    combined = body + SECTION_SEPARATOR + section
    if not combined.endswith("\n"):
        combined += "\n"
    return combined


def _mode_create(companion_path: Path) -> int:
    """Create the companion file, truncating it back to empty when it exists.

    Args:
        companion_path: The companion file path at the project root.

    Returns:
        ``0`` on success.
    """
    existed = companion_path.exists()
    companion_path.write_text("", encoding="utf-8")
    if existed:
        LOGGER.info("Reset companion to empty: %s", companion_path)
    else:
        LOGGER.info("Created empty companion: %s", companion_path)
    return 0


def _mode_strip(doc_path: Path) -> int:
    """Truncate the document at the open-questions marker line.

    Args:
        doc_path: The resolved document path.

    Returns:
        ``0`` on success (including the no-op case where no marker is found).
    """
    text = doc_path.read_text(encoding="utf-8")
    new_text, changed = _strip_open_questions(text)
    if not changed:
        LOGGER.info(
            "No '## Open questions' section found in %s; nothing to strip",
            doc_path,
        )
        return 0

    doc_path.write_text(new_text, encoding="utf-8")
    LOGGER.info("Stripped '## Open questions' section from %s", doc_path)
    return 0


def _mode_append(doc_path: Path, companion_path: Path) -> int:
    """Append the companion's open-questions section to the document.

    Args:
        doc_path: The resolved document path.
        companion_path: The companion file path at the project root.

    Returns:
        ``0`` on success.

    Raises:
        OpenQuestionsError: When the companion is missing or carries no
            open-questions section.
    """
    if not companion_path.is_file():
        msg = f"Companion file not found: {companion_path}"
        raise OpenQuestionsError(msg)

    section = _extract_section(companion_path.read_text(encoding="utf-8"))
    if section is None:
        msg = f"No '## Open questions' section found in companion: {companion_path}"
        raise OpenQuestionsError(msg)

    doc_text = doc_path.read_text(encoding="utf-8")
    new_text = _append_section(doc_text, section)
    doc_path.write_text(new_text, encoding="utf-8")
    LOGGER.info(
        "Appended '## Open questions' section from %s into %s",
        companion_path,
        doc_path,
    )
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    """Parse command-line arguments for the open-questions tool.

    Args:
        argv: The argument vector without the program name, or ``None`` to read
            from ``sys.argv``.

    Returns:
        The parsed argparse namespace with ``docfile`` and exactly one of the
        ``create`` / ``strip`` / ``append`` flags set.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Manage the '## Open questions' section of a docs/<type>.vX.Y.Z."
            "<topic>.md document and its a.<base>.open.questions.md companion."
        ),
    )
    parser.add_argument(
        "docfile",
        help=(
            "Document file name (for example design.v1.2.3.cdc-gap.md), "
            "looked up under <root>/docs or <root>/docs/<vX.Y.Z>."
        ),
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-c",
        "--create",
        action="store_true",
        help="Create an empty a.<base>.open.questions.md companion at the root.",
    )
    group.add_argument(
        "-s",
        "--strip",
        action="store_true",
        help="Remove the '## Open questions' line and everything after it.",
    )
    group.add_argument(
        "-a",
        "--append",
        action="store_true",
        help=(
            "Append the companion's '## Open questions' section to the "
            "document, after two empty lines."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: create, strip, or append the open-questions section.

    Args:
        argv: The argument vector without the program name. When ``None``,
            ``argparse`` reads from ``sys.argv``.

    Returns:
        ``0`` on success.

    Raises:
        OpenQuestionsError: For any fatal precondition or mode failure.
    """
    _configure_logging()
    args = _parse_args(argv)
    root = find_project_root(Path.cwd())

    name = Path(args.docfile).name
    if not name.endswith(MD_SUFFIX):
        msg = f"Expected a '{MD_SUFFIX}' document name, got: {args.docfile!r}"
        raise OpenQuestionsError(msg)
    base = name[: -len(MD_SUFFIX)]

    # Precondition shared by all modes: the document must exist and be non-empty.
    doc_path = _resolve_doc(root, name)
    LOGGER.info("Document: %s", doc_path)

    companion_path = root / _companion_name(base)

    if args.create:
        return _mode_create(companion_path)
    if args.strip:
        return _mode_strip(doc_path)
    return _mode_append(doc_path, companion_path)


def _log_fatal(err: Exception) -> NoReturn:
    """Log a fatal error and exit with ``EXIT_FATAL``."""
    LOGGER.error("ERROR: %s", err)
    raise SystemExit(EXIT_FATAL) from err


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OpenQuestionsError, OSError) as err:
        _log_fatal(err)


# eof
