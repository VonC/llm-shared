"""Terminal text-input seam for the `new_draft` tool.

Like `prompt_workflow_menu`, this is the only new_draft module that touches the
terminal, so it is kept tiny and excluded from coverage (it needs a TTY to
exercise). `questionary` is imported lazily so importing the package, and the
test suite, never requires it. Arrow-key selections reuse
`prompt_workflow_menu.select`; this module only adds the free-text prompt used
for the slug.
"""

from __future__ import annotations

# questionary ships no type stubs and is an optional runtime dependency, so the
# strict unknown-type and missing-import checks are disabled for this seam only.
# pyright: reportMissingImports=false, reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false, reportUnknownArgumentType=false
# pyright: reportAttributeAccessIssue=false, reportOptionalMemberAccess=false


def ask_text(message: str, *, default: str = "") -> str | None:
    """Prompt for a single line of text and return it, or None on cancel.

    Args:
        message: The prompt shown to the user.
        default: The pre-filled value.

    Returns:
        The entered text (stripped), or None when the user cancels (Ctrl-C).
    """
    import questionary  # noqa: PLC0415

    answer = questionary.text(message, default=default).ask()
    if answer is None:
        return None
    return str(answer).strip()


# eof
