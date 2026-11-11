"""The shipped `version` and `versions` commands of the release engine.

Step 9 of v0.14.0 version-sources exposes the version domain through item 1's
dispatcher. Command data goes to stdout, warnings and errors to stderr:

- `version`: the anchor's token, its title (possibly empty), an empty line,
  then the notes unchanged.
- `versions list`: a header, then one tab-separated record per source:
  root-relative path with `/`, field, adapter, form, value and status, `-`
  standing for the form and value of a non-participating file.
- `versions check`: one record per participating source: path, field, form,
  actual and expected values, `ok` or `drift`; any drift is status 1.
- `versions set <token>`: one record per changed source with its old and new
  value, or `unchanged`; the transition's outcome gives the status (0, 1 or 3).
- `versions range [<stable tag>]`: the `target`, `baseline`, `range` and
  `commits` lines of the selected release range.

`validate_versions` accepts `list`, `check`, `set <token>`, `range` and
`range <stable tag>` and rejects anything else right after parsing, before
any Git process or file read (status 2). Every domain error is a `ValueError`
carrying its public status as `exit_code` (2 for a source, version, setting,
configuration or range refusal; an artifact, evidence or transition error
keeps its own); one without it, such as a lock error, is an execution failure
(1). The read commands take no lock and write nothing: they list the artifact
home once and warn about every leftover version-transition evidence directory.

`cli.SHIPPED_HANDLERS` builds the two handlers from `show_version`,
`VersionsCommand` and `validate_versions`, because this module must not import
`cli`, which imports it. `VersionsCommand(ports)` is the explicit fault
injection seam of the transition (plan decision Q07); the shipped value uses
the production ports. Only the standard library and `results` load with this
module: each function imports the domain modules it uses when a command runs,
so importing `cli` stays cheap.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from tools.release_workflow.results import OperationResult

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping, Sequence
    from pathlib import Path

    from tools.release_workflow.invocation import InvocationContext
    from tools.release_workflow.sources.model import FileView, Inventory, VersionInputs
    from tools.release_workflow.version_transition import TransitionPorts

    type ReadOperation = Callable[[VersionInputs, Sequence[str]], OperationResult]

_USAGE = "expected list, check, set <X.Y.Z or X.Y.Z-SNAPSHOT>, range or range <stable tag>"
_HEADER = ("path", "field", "adapter", "form", "value", "status")
_ABSENT = "-"
_REMEDIES = {
    "completed standalone residue": "the next versions set removes it",
    "interrupted": "versions set stops on it: inspect it, restore what is needed and remove it",
    "unreadable": "versions set stops on it: inspect it, restore what is needed and remove it",
    "lifecycle-owned": "it belongs to a release lifecycle; versions set stops on it until that lifecycle ends",
}


def validate_versions(tokens: tuple[str, ...]) -> None:
    """Accept `list`, `check`, `set <token>`, `range` or `range <stable tag>`; raise `ValueError` otherwise."""
    match tokens:
        case ("list" | "check" | "range",):
            return
        case ("set", token):
            from tools.release_workflow.sources import model  # noqa: PLC0415

            model.VersionToken.parse(token)
            return
        case ("range", tag):
            from tools.release_workflow import tags  # noqa: PLC0415

            if isinstance(tags.parse_name(tag), tags.StableName):
                return
            msg = f"versions range {tag!r}: expected a stable release tag name, vX.Y.Z or X.Y.Z"
            raise ValueError(msg)
        case _:
            msg = f"Invalid versions operation {' '.join(tokens) or '(none)'!r}: {_USAGE}"
            raise ValueError(msg)


def _lines(rows: Iterable[Sequence[str]]) -> str:
    """Join each row's fields with tabs, one LF-ended line per row."""
    return "".join("\t".join(row) + "\n" for row in rows)


def _relative(root: Path, path: Path) -> str:
    """Spell a source path relative to the project root with `/`."""
    return path.relative_to(root).as_posix()


def _failed(command: str, exc: ValueError, warnings: tuple[str, ...]) -> OperationResult:
    """Report a refused command with the status its error carries, 1 when it carries none."""
    status: int = getattr(exc, "exit_code", 1)
    return OperationResult(status, diagnostics=(*warnings, f"{command} failed: {exc}"))


def _inputs(context: InvocationContext) -> VersionInputs:
    """Copy the project, configuration, artifacts and Git of the validated invocation."""
    from tools.release_workflow.sources import model  # noqa: PLC0415

    return model.VersionInputs.from_context(context)


def _detect(inputs: VersionInputs) -> tuple[Inventory, FileView]:
    """Detect every participating source through one fresh file view, returned for further reads."""
    from tools.release_workflow.sources import detection, model  # noqa: PLC0415

    view = model.FileView()
    return detection.detect(inputs, view), view


def leftover_warnings(inputs: VersionInputs) -> tuple[str, ...]:
    """Warn about each version-transition evidence directory of the artifact home, listed once."""
    from tools.release_workflow import version_evidence  # noqa: PLC0415

    return tuple(f"warning: leftover {entry.kind} version-transition evidence {entry.path}; {_REMEDIES[entry.kind]}"
                 for entry in version_evidence.find_evidence(inputs.artifacts))


def show_version(context: InvocationContext) -> OperationResult:
    """Print the anchor's token, its title, an empty line and its notes."""
    from tools.release_workflow.sources import anchor, model  # noqa: PLC0415

    inputs = _inputs(context)
    warnings = leftover_warnings(inputs)
    try:
        document = anchor.read_document(inputs.project.root, model.FileView())
    except ValueError as exc:
        return _failed("version", exc, warnings)
    return OperationResult(data=f"{document.token}\n{document.title}\n\n{document.notes}", diagnostics=warnings)


def _list(inputs: VersionInputs, arguments: Sequence[str]) -> OperationResult:
    """List every participating source, then each tool-only file and undeclared candidate, from one Git listing."""
    del arguments
    from tools.release_workflow.sources import detection  # noqa: PLC0415

    root = inputs.project.root
    inventory, view = _detect(inputs)
    rows = [_HEADER]
    rows += [(_relative(root, source.path), source.field, source.adapter, str(source.form), source.value, "participating")
             for source in inventory.sources]
    rows += [(_relative(root, record.path), record.field, record.adapter, _ABSENT, _ABSENT, record.status)
             for record in (*inventory.visible, *detection.candidates(inputs, inventory, view))]
    return OperationResult(data=_lines(rows))


def _check(inputs: VersionInputs, arguments: Sequence[str]) -> OperationResult:
    """Compare each participating source with the value its form expects from the anchor; drift is status 1."""
    del arguments
    from tools.release_workflow.sources import anchor, model  # noqa: PLC0415

    inventory, _ = _detect(inputs)
    anchor_value = next(source.value for source in inventory.sources if source.adapter == anchor.ADAPTER.name)
    token = model.VersionToken.parse(anchor_value)
    rows: list[tuple[str, ...]] = []
    for source in inventory.sources:
        expected = source.form.expected(token)
        state = "ok" if source.value == expected else "drift"
        rows.append((_relative(inputs.project.root, source.path), source.field, str(source.form), source.value, expected, state))
    drifting = sum(row[-1] == "drift" for row in rows)
    if not drifting:
        return OperationResult(data=_lines(rows))
    diagnostic = (f"versions check: {drifting} of {len(rows)} sources drift from the anchor {token}; "
                  "synchronize them with versions set, or correct the anchor")
    return OperationResult(1, _lines(rows), (diagnostic,))


def _range(inputs: VersionInputs, arguments: Sequence[str]) -> OperationResult:
    """Print the release range ending at HEAD or at the stable tag given."""
    from tools.release_workflow import tags  # noqa: PLC0415

    selection = tags.select_range(inputs.git, cwd=inputs.project.root, target=arguments[0] if arguments else None)
    rows = [f"target={selection.target}", f"baseline={selection.baseline or 'none'}",
            f"range={selection.range}", f"commits={selection.commits}"]
    return OperationResult(data="".join(f"{row}\n" for row in rows), diagnostics=selection.warnings)


_READS: Mapping[str, ReadOperation] = {"list": _list, "check": _check, "range": _range}


@dataclass(frozen=True)
class VersionsCommand:
    """The `versions` operations; `set` uses these transition ports, the production ones when `None`."""

    ports: TransitionPorts | None = None

    def __call__(self, context: InvocationContext) -> OperationResult:
        """Run the operation the validator accepted."""
        operation, *arguments = context.operation
        inputs = _inputs(context)
        if operation == "set":
            return self._set(inputs, arguments[0])
        warnings = leftover_warnings(inputs)
        try:
            result = _READS[operation](inputs, arguments)
        except ValueError as exc:
            return _failed(f"versions {operation}", exc, warnings)
        return OperationResult(result.status, result.data, (*warnings, *result.diagnostics))

    def _set(self, inputs: VersionInputs, token: str) -> OperationResult:
        """Run the transition and print each changed field, or `unchanged`."""
        from tools.release_workflow import version_transition  # noqa: PLC0415
        from tools.release_workflow.sources import model  # noqa: PLC0415

        command = f"versions set {token}"
        ports = self.ports or version_transition.DEFAULT_PORTS
        try:
            result = version_transition.set_versions(inputs, model.VersionToken.parse(token), ports=ports)
        except ValueError as exc:
            return _failed(command, exc, ())
        rows = [(_relative(inputs.project.root, change.path), change.field, change.old, change.new) for change in result.changes]
        data = "unchanged\n" if result.outcome is version_transition.TransitionOutcome.UNCHANGED else _lines(rows)
        summary = () if result.status == 0 else (f"{command} failed: {result.outcome}",)
        return OperationResult(result.status, data, (*result.diagnostics, *summary))


# eof
