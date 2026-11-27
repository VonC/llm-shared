"""Stage two sender faults inside one guarded guest step using the production command and a real pane."""

from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from functools import partial
from typing import TYPE_CHECKING

from tools import resume_paused
from tools.resume_paused_marker import marker_in_command
from tools.resume_paused_profiles import CommandResult
from tools.resume_paused_transport import enter_arguments, resolve_selector

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from pathlib import Path

    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_profiles import CommandRunner


@dataclass
class Fault:
    """Intercept only the exact confirmed send in this launch. Pass all observations through."""

    case: str
    pane: PaneRecord
    operations: list[str] = field(default_factory=list[str])

    def send(self, runner: CommandRunner, args: Sequence[str]) -> CommandResult:
        """Withhold one ask or leave its real text unsubmitted, then count the production recovery Enter."""
        if args[1] == "send-keys":
            assert self.case == "recovery"
            assert self.operations == ["paste"]
            assert tuple(args) == enter_arguments(self.pane.session, self.pane.pane_id)
            self.operations.append("enter")
        if args[1] != "ask-agent":
            return runner.run(args)
        return self._confirmed(runner, args)

    def _confirmed(self, runner: CommandRunner, args: Sequence[str]) -> CommandResult:
        assert not self.operations
        assert "--confirm" in args
        assert args[args.index("--select") + 1] == resolve_selector([self.pane], self.pane).selector
        command = args[-1]
        assert args[-2] == "--"
        assert marker_in_command(command).pane_id == self.pane.pane_id
        if self.case == "stall":
            self.operations.append("drop")
        else:
            assert self.case == "recovery"
            self.operations.append("paste")
            result = runner.run(("tuios", "send-text", "-s", self.pane.session, "-w", self.pane.pane_id, command))
            assert result.exit_code == 0, "TUIOS did not paste the command into the selected guest pane"
        return CommandResult(1, "")


@dataclass
class _Runner:
    fault: Fault
    delegate: CommandRunner

    def run(self, arguments: Sequence[str]) -> CommandResult:
        return self.fault.send(self.delegate, arguments)


def _runner(fault: Fault, factory: Callable[[float], CommandRunner], seconds: float) -> CommandRunner:
    return _Runner(fault, factory(seconds))


def run_fault(folder: Path, case: str, pane: PaneRecord) -> tuple[int, str]:
    """Run the shipping CLI with one process-local transport substitution after the guest guard."""
    fault = Fault(case, pane)
    runtime = resume_paused.default_runtime(os.environ)
    bounded = partial(_runner, fault, runtime.runner_for)
    injected = replace(runtime, runner_for=bounded)
    output = folder / "launch-1.stdout"
    with output.open("x", encoding="utf-8") as stdout, (folder / "launch-1.stderr").open("x", encoding="utf-8") as stderr:
        try:
            code = resume_paused.main([], runtime=lambda: injected, stdout=stdout, stderr=stderr)
        finally:
            (folder / "transport.txt").write_text("\n".join(fault.operations), encoding="utf-8")
    (folder / "launch-1.exit.json").write_text(str(code), encoding="utf-8")
    assert fault.operations == (["drop"] if case == "stall" else ["paste", "enter"]), "Expected fault sequence did not occur"
    return code, output.read_text(encoding="utf-8")


# eof
