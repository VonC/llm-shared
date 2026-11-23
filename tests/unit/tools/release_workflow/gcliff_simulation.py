"""One `gcliff` scenario: the provisioning world inside a simulated tooling checkout, the sandbox projects and a fake console.

Step 8 of v0.14.0 git-cliff-provisioning (plan "Shared test architecture").
`gcliff_scenario` builds, for one test, the `ProvisionWorld` whose cache lives
in the tooling checkout the launcher simulation selects, with the shipped
2.14.2 pin as the world's pin, and a `FakeKernel` for the console filter.
`GcliffScenario.run` starts the `gcliff-batch` entry through the production
bootstrap and launcher with those seams. Each launch is kept with the console
handler calls made before it, so a test sees that the filter surrounds the
git-cliff run only. A scenario can also select from another pin table, such as
a synthetic 2.14.2 whose archive the fake worker can deliver, since no test
downloads the published asset. No process, socket, console handler or real
wait.
"""

from __future__ import annotations

import dataclasses
import functools
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from tests.unit.tools.release_workflow.git_cliff_children_fake import ProvisionWorld
from tests.unit.tools.release_workflow.git_cliff_support import VERSION
from tests.unit.tools.release_workflow.launcher_simulation import tooling
from tests.unit.tools.release_workflow.native_kernel_fake import FakeKernel
from tools.release_workflow.git_cliff.launcher import LauncherSeams
from tools.release_workflow.git_cliff.manifest import ADMITTED_PINS, admitted
from tools.release_workflow.windows_child import ignore_console_interrupts

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path
    from subprocess import CompletedProcess

    import pytest

    from tests.unit.tools.release_workflow.git_cliff_children_fake import Launched
    from tests.unit.tools.release_workflow.launcher_simulation import ToolingSimulation
    from tests.unit.tools.release_workflow.repository_simulation import GitSandbox
    from tools.release_workflow.git_cliff.manifest import AdmittedPin
    from tools.release_workflow.windows_child import ChildOutcome, ChildRequest


@dataclass
class GcliffScenario:
    """The world, tooling simulation, sandbox, console kernel and pin table of one `gcliff` test."""

    world: ProvisionWorld
    simulation: ToolingSimulation
    sandbox: GitSandbox
    kernel: FakeKernel = field(default_factory=FakeKernel)
    pins: tuple[AdmittedPin, ...] = ADMITTED_PINS
    consoles: list[tuple[tuple[str, ...], tuple[tuple[object, int], ...]]] = field(
        default_factory=list[tuple[tuple[str, ...], tuple[tuple[object, int], ...]]])

    def _launch(self, request: ChildRequest) -> ChildOutcome:
        """Keep the console handler calls made before this launch, then play the child."""
        self.consoles.append((request.arguments, tuple(self.kernel.handlers)))
        return self.world.children(request)

    def seams(self) -> LauncherSeams:
        """Bind the launcher to this world, its console kernel and its pin table."""
        return LauncherSeams(provisioning=dataclasses.replace(self.world.seams(), launch=self._launch),
                             console=functools.partial(ignore_console_interrupts, api=self.kernel), pins=self.pins)

    def run(self, *arguments: str, cwd: Path, environment: Mapping[str, str] | None = None) -> CompletedProcess[bytes]:
        """Run `gcliff` with these git-cliff arguments from a directory, through the bootstrap's `gcliff-batch` entry."""
        return self.simulation.run(list(arguments), sandbox=self.sandbox, cwd=cwd, environment=environment, entry="gcliff-batch",
                                   launcher=self.seams())

    @property
    def runs(self) -> list[Launched]:
        """Return the git-cliff runs started, in order."""
        return self.world.children.of("run")


def gcliff_scenario(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, sandbox: GitSandbox) -> GcliffScenario:
    """Build the world in a tooling checkout below `tmp_path`, whose pin is the shipped 2.14.2."""
    world = ProvisionWorld.build(tmp_path.resolve(), monkeypatch)
    world.pin = admitted(VERSION, ADMITTED_PINS)
    return GcliffScenario(world, tooling(world.layout.tooling_root), sandbox)


# eof
