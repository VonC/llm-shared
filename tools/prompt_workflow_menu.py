"""Thin interactive-menu wrapper around questionary for prompt_workflow (Q12).

This is the only module that touches the terminal UI. It is isolated here so the
rest of the tool stays unit-testable: callers go through ``select`` and tests
monkeypatch it. ``questionary`` is imported lazily inside the function so the
package imports (and the test suite) do not require it to be installed, and this
module is excluded from coverage in ``pyproject.toml`` like ``tools/uv_run.py``.
"""

from __future__ import annotations

# questionary ships no type stubs and is an optional runtime dependency, so the
# strict unknown-type and missing-import checks are disabled for this seam only.
# pyright: reportMissingImports=false, reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false, reportUnknownArgumentType=false
# pyright: reportAttributeAccessIssue=false, reportOptionalMemberAccess=false
# pyright: reportUntypedFunctionDecorator=false, reportUnusedFunction=false


def select[T](message: str, options: list[tuple[str, T]]) -> T | None:
    """Show an arrow-key select menu and return the chosen value or None on ESC.

    Args:
        message: The prompt shown above the choices.
        options: Pairs of (label, value); the label is displayed, the value is
            returned when its row is picked.

    Returns:
        The value of the selected option, or None when the user presses ESC.
    """
    import questionary  # noqa: PLC0415
    from prompt_toolkit.keys import Keys  # noqa: PLC0415

    choices = [questionary.Choice(title=label, value=value) for label, value in options]
    question = questionary.select(message, choices=choices)

    # questionary's select ignores ESC by default; bind it to cancel so ESC
    # exits with None, which the caller treats as "exit without a prompt".
    application = question.application

    @application.key_bindings.add(Keys.Escape, eager=True)
    def _cancel_on_escape(_event: object) -> None:
        application.exit(result=None)

    return question.ask()


# eof
