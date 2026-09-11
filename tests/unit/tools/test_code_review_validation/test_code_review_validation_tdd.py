"""TDD contracts for immutable mandatory validation resolution."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import TYPE_CHECKING, cast

import pytest

from tools.code_review_validation import (
    DEFAULT_PROJECT_VALIDATION_COMMANDS,
    PROJECT_VALIDATION_FILE,
    ResolvedValidationCommand,
    ResolvedValidationSet,
    ValidationSource,
    load_project_validation_commands,
    resolve_code_review_validation,
)
from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from pathlib import Path


def test_resolver_preserves_defaults_adds_checks_and_merges_sources() -> None:
    """First appearance orders commands and every contributing source is retained."""
    resolved = resolve_code_review_validation(
        ("ghog day", "project lint"),
        ("focused tests", "project lint"),
        ("request audit", "focused tests"),
    )

    assert resolved.command_lines == (
        "ghog day",
        "project lint",
        "focused tests",
        "request audit",
    )
    assert [entry.sources for entry in resolved.commands] == [
        ("project",),
        ("project", "plan"),
        ("plan", "request"),
        ("request",),
    ]
    with pytest.raises(FrozenInstanceError):
        setattr(resolved, "commands", ())


def test_resolver_is_deterministic_and_exposes_drift_inputs() -> None:
    """Equal inputs are stable while later additions produce a comparable value."""
    before = resolve_code_review_validation(("ghog day",), ("focused tests",))
    repeated = resolve_code_review_validation(("ghog day",), ("focused tests",))
    after = resolve_code_review_validation(
        ("ghog day",),
        ("focused tests",),
        ("security audit",),
    )

    assert before == repeated
    assert before != after
    assert after.command_lines == (*before.command_lines, "security audit")


@pytest.mark.parametrize(
    ("project", "plan", "request_commands", "message"),
    [
        ((), (), (), "project validation defaults must be non-empty"),
        ((" ",), (), (), "validation command must be non-empty"),
        (("ghog day",), ("",), (), "validation command must be non-empty"),
        (("ghog day",), (), ("\n",), "validation command must be non-empty"),
    ],
)
def test_resolver_rejects_missing_defaults_and_empty_additions(
    project: tuple[str, ...],
    plan: tuple[str, ...],
    request_commands: tuple[str, ...],
    message: str,
) -> None:
    """The additive API cannot erase defaults or publish empty commands."""
    with pytest.raises(ReviewExchangeError, match=message):
        resolve_code_review_validation(project, plan, request_commands)


def test_typed_validation_values_reject_invalid_direct_construction() -> None:
    """Callers cannot bypass resolver invariants through public constructors."""
    with pytest.raises(ReviewExchangeError, match="validation command must be non-empty"):
        ResolvedValidationCommand(" ", ("project",))
    with pytest.raises(ReviewExchangeError, match="sources must be non-empty and unique"):
        ResolvedValidationCommand("ghog day", ())
    with pytest.raises(ReviewExchangeError, match="source is unsupported"):
        ResolvedValidationCommand("ghog day", (cast("ValidationSource", "writer"),))
    with pytest.raises(ReviewExchangeError, match="set must be non-empty"):
        ResolvedValidationSet(())

    command = ResolvedValidationCommand("ghog day", ("project",))
    with pytest.raises(ReviewExchangeError, match="commands must be unique"):
        ResolvedValidationSet((command, command))


def test_project_declaration_absent_keeps_the_built_in_default(tmp_path: Path) -> None:
    """A project that declares nothing inherits the built-in mandatory floor."""
    assert load_project_validation_commands(tmp_path) == DEFAULT_PROJECT_VALIDATION_COMMANDS


def test_project_declaration_replaces_the_default_and_stays_mandatory(
    tmp_path: Path,
) -> None:
    """A declared floor is what the project must prove, and it is still `project`.

    The point of the declaration is that a repository without a Python suite can
    state a floor it can actually satisfy. It must remain a floor: the commands
    are labelled `project`, and the resolver still offers no way to subtract one.
    """
    (tmp_path / PROJECT_VALIDATION_FILE).write_text(
        "# this repository is Bash, not Python\n"
        "\n"
        "shellcheck src/install.sh\n"
        "bash verify.sh --step 2\n",
        encoding="utf-8",
    )

    declared = load_project_validation_commands(tmp_path)
    assert declared == ("shellcheck src/install.sh", "bash verify.sh --step 2")
    assert "ghog day" not in declared

    resolved = resolve_code_review_validation(declared, ("plan check",), ())
    assert resolved.command_lines == (
        "shellcheck src/install.sh",
        "bash verify.sh --step 2",
        "plan check",
    )
    assert resolved.commands[0].sources == ("project",)


def test_empty_declaration_is_refused_rather_than_read_as_no_floor(
    tmp_path: Path,
) -> None:
    """A file declaring nothing is an error; omitting the file is the way to opt out."""
    (tmp_path / PROJECT_VALIDATION_FILE).write_text(
        "# every line a comment\n\n",
        encoding="utf-8",
    )

    with pytest.raises(ReviewExchangeError, match="declares no command"):
        load_project_validation_commands(tmp_path)


def test_declaration_must_be_a_file(tmp_path: Path) -> None:
    """A directory of that name is a malformed declaration, not an absent one."""
    (tmp_path / PROJECT_VALIDATION_FILE).mkdir()

    with pytest.raises(ReviewExchangeError, match="is not a file"):
        load_project_validation_commands(tmp_path)


def test_unreadable_project_declaration_is_reported(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Filesystem read failures retain their cause and declaration context."""
    declaration = tmp_path / PROJECT_VALIDATION_FILE
    declaration.write_text("ghog day\n", encoding="utf-8")

    def denied_read(*_args: object, **_kwargs: object) -> str:
        raise OSError

    monkeypatch.setattr("pathlib.Path.read_text", denied_read)

    with pytest.raises(ReviewExchangeError, match=r"invalid \.review-validation"):
        load_project_validation_commands(tmp_path)
