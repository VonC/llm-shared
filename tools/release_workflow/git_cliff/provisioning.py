"""Give a caller a verified, guarded git-cliff for its pin: reuse it silently, or provision it under the cache lock.

Step 5 of v0.14.0 git-cliff-provisioning (design "Target flow of git-cliff
provisioning", "Reuse check and the use guard", "Provisioning lock,
contention and recovery" and "The provisioning entry point for items 4 and
5"; design decisions Q03, Q07, Q09, Q17 and Q18; requirement clarifications
Q03, Q06, Q08, Q14 and Q15; plan decisions Q06, Q10, Q11, Q12 and Q18).

`provision(tooling_root, pin, budget, *, seams, caller)` runs the target flow
after configuration validation and before any project write; it creates no
project file and takes no project lock:

1. No admitted pin: the configuration stage.
2. The platform check: Windows 10 or Windows Server 2016 and later, x64.
3. The lock-free, write-free reuse check: guard, record, hash, then the
   record-free probe inheriting the guard; a valid entry returns at once and
   prints nothing.
4. Otherwise the version and platform lock, within the caller's own wait W,
   with one waiting line behind a live holder; under it the recheck (another
   caller may have published), the recovery of attempt directories whose
   actors are all `DEAD`, and `installation.install`.
5. The new entry is guarded, the lock is released (an unconfirmed child end
   retained its record), and only then the ready line is printed; an entry
   that cannot be guarded fails once under the extraction stage (plan Q18).
   Since code review round 2 of Step 6 the guard is opened before the
   release, not after it, so another installation, such as an evidence
   candidate of another bundle with its own trust record, cannot replace the
   entry in between.
   Since code review round 1, a ready line that cannot be written releases
   that guard before its failure leaves, so the entry stays replaceable;
   since round 2, that failure, like a waiting or download line that cannot
   be written, is the reporting stage of `ProvisioningError`.

Step 6: the flow runs on an `installation.InstallTarget`. `provision` gives it
`manifest_target(pin)` in the production namespace, unchanged; the evidence
harness runs a candidate through `provision_target` in the evidence
namespace, where the reuse check also compares the entry's archive digest
with the candidate's trust record, read again before each check: the
lock-free one and the recheck under the lock (code review round 1), so a
waiter reuses the entry a concurrent first acquisition published.

Every failure is a `ProvisioningError`; a lock record that cannot be removed
after another failure is added to it as a note. `provisioning_budget` turns a
refused budget value into the budget-setting stage, `configured_pin` reads the
validated `[git-cliff] version`, and `production_seams` binds the Windows
layer. Provisioning never writes to standard output.
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from tools.release_workflow.git_cliff.budget import (
    DOWNLOAD_BUDGET_VARIABLE,
    BudgetSettingError,
    resolve_budget,
)
from tools.release_workflow.git_cliff.cache import CacheLayout, ValidEntry, check_entry
from tools.release_workflow.git_cliff.cache_lock import (
    CacheLock,
    LockSeams,
    LockWaitError,
)
from tools.release_workflow.git_cliff.installation import install, manifest_target
from tools.release_workflow.git_cliff.invocation import (
    GitCliffInvocation,
    probe_request,
)
from tools.release_workflow.git_cliff.messages import (
    ProvisioningError,
    Stage,
    announce,
    permission_failure,
    ready_line,
    waiting_line,
)
from tools.release_workflow.windows_child import (
    ContainmentError,
    PlatformError,
    require_supported_platform,
    run_contained,
)
from tools.release_workflow.windows_guard import open_guard
from tools.release_workflow.windows_process import (
    current_identity,
    process_state,
    transition_mutex,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from contextlib import AbstractContextManager
    from pathlib import Path

    from tools.release_workflow.configuration import Configuration
    from tools.release_workflow.git_cliff.budget import BudgetPolicy
    from tools.release_workflow.git_cliff.cache import Guard
    from tools.release_workflow.git_cliff.cache_lock import LockRecord
    from tools.release_workflow.git_cliff.installation import InstallTarget
    from tools.release_workflow.git_cliff.manifest import AdmittedPin
    from tools.release_workflow.windows_child import ChildOutcome, ChildRequest
    from tools.release_workflow.windows_process import ProcessIdentity, ProcessState


def _local_now() -> datetime:
    """Return the local time with its offset."""
    return datetime.now(UTC).astimezone()


def _stderr_line(line: str) -> None:
    """Write one whole line on standard error."""
    sys.stderr.write(f"{line}\n")
    sys.stderr.flush()


@dataclass(frozen=True, kw_only=True)
class ProvisioningSeams:
    """The injected boundaries of provisioning: the Windows layer, time, standard error and the worker runtime."""

    launch: Callable[[ChildRequest], ChildOutcome]
    open_guard: Callable[[Path], Guard]
    process_state: Callable[[ProcessIdentity], ProcessState]
    current_identity: Callable[[], ProcessIdentity]
    mutex: Callable[[str], AbstractContextManager[None]]
    clock: Callable[[], float]
    sleep: Callable[[float], None]
    stderr: Callable[[str], None]
    runtime: Path
    platform_check: Callable[[], None]
    now: Callable[[], datetime] = _local_now


def production_seams(runtime: Path) -> ProvisioningSeams:
    """Bind the contained launcher, the use guard, the liveness probe, the mutex, the clocks and standard error."""
    return ProvisioningSeams(
        launch=run_contained, open_guard=open_guard, process_state=process_state, current_identity=current_identity,
        mutex=transition_mutex, clock=time.monotonic, sleep=time.sleep, stderr=_stderr_line, runtime=runtime,
        platform_check=require_supported_platform,
    )


def configured_pin(configuration: Configuration) -> str | None:
    """Return the validated `[git-cliff] version`, declared or defaulted, or None when the manifest admits no pin."""
    value = configuration.sections.get("git-cliff", {}).get("version")
    return None if value is None else str(value.value)


def _place(tooling_root: Path, pin: AdmittedPin | None) -> Path:
    """Name the entry directory of a pin, or the cache root before any pin exists."""
    layout = CacheLayout(tooling_root)
    return layout.root if pin is None else layout.entry_dir(pin)


def provisioning_budget(environment: Mapping[str, str], *, tooling_root: Path, pin: AdmittedPin | None) -> BudgetPolicy:
    """Resolve the budget policy once, before any provisioning work, as the budget-setting stage on a refused value."""
    try:
        return resolve_budget(environment)
    except BudgetSettingError as error:
        detail = f"{DOWNLOAD_BUDGET_VARIABLE}={error.value!r} is refused"
        raise ProvisioningError(Stage.BUDGET_SETTING, version=None if pin is None else pin.version,
                                path=_place(tooling_root, pin), detail=detail) from error


def _wait_detail(error: LockWaitError) -> str:
    """Name the last live holder seen and the wait spent, without repeating the remedy."""
    if error.owner is None:
        return f"no live holder seen, not acquired before its deadline after waiting {error.wait:g} s"
    return f"held by process {error.owner.pid} since {error.started} after waiting {error.wait:g} s"


class _Flow:
    """One provisioning call of one caller for one pin."""

    def __init__(self, layout: CacheLayout, target: InstallTarget, budget: BudgetPolicy, seams: ProvisioningSeams, caller: str) -> None:
        """Bind the call to its target's cache place."""
        self._layout = layout
        self._target = target
        self._budget = budget
        self._seams = seams
        self._caller = caller
        self._place = layout.entry_dir(target)

    def _failure(self, stage: Stage, detail: str, path: Path | None = None) -> ProvisioningError:
        """Describe a failed stage at the entry directory or at a given path."""
        return ProvisioningError(stage, version=self._target.version, path=self._place if path is None else path, detail=detail)

    def run(self) -> GitCliffInvocation:
        """Check the platform, reuse a valid entry, or provision one under the lock and guard it."""
        try:
            self._seams.platform_check()
        except PlatformError as error:
            raise self._failure(Stage.PLATFORM, str(error)) from error
        guard = self._reuse()
        if guard is not None:
            return self._invocation(guard)
        guard, installed = self._locked()
        invocation = self._invocation(guard)
        if not installed:
            return invocation
        try:
            announce(self._seams.stderr, ready_line(self._target.version, self._place), version=self._target.version, path=self._place)
        except BaseException:
            # No caller owns the invocation yet: release its guard before the failure leaves.
            invocation.close()
            raise
        return invocation

    def _invocation(self, guard: Guard) -> GitCliffInvocation:
        """Hand the guarded executable to the one object that starts git-cliff."""
        return GitCliffInvocation(guard.path, self._target.version, guard, launch=self._seams.launch)

    def _probe(self, guard: Guard) -> ChildOutcome:
        """Run the record-free version probe, inheriting the entry's guard."""
        return self._seams.launch(probe_request(guard.path, inherited=(guard.handle,), deadline=self._budget.probe))

    def _reuse(self) -> Guard | None:
        """Run the write-free reuse check when the target allows reuse now; a probe that cannot run or end is the containment stage.

        A target's `reuse` function is asked before each check and gives the archive digest the entry must record,
        or None when no entry may be reused now; production has none and compares no archive digest.
        """
        asset: str | None = None
        if self._target.reuse is not None:
            asset = self._target.reuse()
            if asset is None:
                return None
        try:
            found = check_entry(self._layout, self._target, open_guard=self._seams.open_guard, probe=self._probe, asset_sha256=asset)
        except ContainmentError as error:
            raise self._failure(Stage.CONTAINMENT, str(error)) from error
        except OSError as error:
            raise self._failure(Stage.EXTRACTION, f"the entry cannot be read: {error}") from error
        return found.guard if isinstance(found, ValidEntry) else None

    def _lock(self) -> CacheLock:
        """Take the version and platform lock within the caller's own wait, announcing a live holder once."""
        seams = self._seams
        lock = CacheLock(self._layout, self._target, caller=self._caller, seams=LockSeams(
            clock=seams.clock, sleep=seams.sleep, probe=seams.process_state, current=seams.current_identity, mutex=seams.mutex,
            now=seams.now,
        ))
        try:
            return lock.acquire(self._budget.wait, self._announce)
        except LockWaitError as error:
            raise self._failure(Stage.LOCK_WAIT, _wait_detail(error), lock.path) from error
        except PermissionError as error:
            raise permission_failure(self._target.version, error, self._place) from error
        except OSError as error:
            raise self._failure(Stage.LOCK_WAIT, str(error), lock.path) from error

    def _announce(self, holder: LockRecord, wait: float) -> None:
        """Print the waiting line once, for the first live holder."""
        announce(self._seams.stderr, waiting_line(self._target.version, holder.owner.pid, holder.started, wait), version=self._target.version,
                 path=self._place)

    def _guard_published(self) -> Guard:
        """Guard the entry this call just published; one that cannot be guarded fails once under the extraction stage."""
        try:
            return self._seams.open_guard(self._layout.executable(self._target))
        except OSError as error:
            raise self._failure(Stage.EXTRACTION, f"the entry just published cannot be guarded: {error}") from error

    def _locked(self) -> tuple[Guard, bool]:
        """Under the lock: recheck, or recover, install and guard the new entry; release; tell whether this call installed.

        The new entry is guarded before the lock is released (code review round 2 of Step 6), so no other installation
        can replace it between its publication and the guard this call hands out.
        """
        lock = self._lock()
        try:
            guard = self._reuse()
            installed = guard is None
            if guard is None:
                try:
                    lock.recover_attempts()
                except OSError as error:
                    raise permission_failure(self._target.version, error, self._place) from error
                install(self._layout, self._target, self._budget, self._seams, lock)
                guard = self._guard_published()
        except BaseException as failure:
            self._release(lock, failure)
            raise
        try:
            self._release(lock, None)
        except ProvisioningError:
            guard.close()
            raise
        return guard, installed

    def _release(self, lock: CacheLock, failure: BaseException | None) -> None:
        """Release the lock; a record that cannot be removed fails the call, or is noted on the failure already raised."""
        try:
            lock.release()
        except OSError as error:
            problem = self._failure(Stage.LOCK_WAIT, f"the lock record could not be removed: {error}", lock.path)
            if failure is None:
                raise problem from error
            failure.add_note(problem.diagnostic())


def provision(tooling_root: Path, pin: AdmittedPin | None, budget: BudgetPolicy, *, seams: ProvisioningSeams,
              caller: str) -> GitCliffInvocation:
    """Return the invocation object of a verified, guarded git-cliff for this pin.

    Args:
        tooling_root: The executing llm-shared checkout, which holds the cache.
        pin: The admitted pin of the project, or None when the manifest admits none.
        budget: The caller's budget policy, resolved once before this call.
        seams: The Windows layer, time, standard error and worker runtime.
        caller: The caller kind written in the lock record, such as `engine` or `gcliff`.

    Returns:
        The invocation object holding the entry's open use guard.

    Raises:
        ProvisioningError: Any stage failed; the diagnostic names the pin, the path, the stage and the remedy.
    """
    layout = CacheLayout(tooling_root)
    if pin is None:
        raise ProvisioningError(Stage.CONFIGURATION, version=None, path=layout.root,
                                detail="no tested git-cliff pin is admitted, so there is no default pin")
    return provision_target(layout, manifest_target(pin), budget, seams=seams, caller=caller)


def provision_target(layout: CacheLayout, target: InstallTarget, budget: BudgetPolicy, *, seams: ProvisioningSeams,
                     caller: str) -> GitCliffInvocation:
    """Run the provisioning flow for any target in its layout's namespace, such as an evidence candidate.

    Args:
        layout: The cache layout, production or evidence, of the executing checkout.
        target: What to reuse or install: `manifest_target(pin)`, or a candidate's target.
        budget: The caller's budget policy, resolved once before this call.
        seams: The Windows layer, time, standard error and worker runtime.
        caller: The caller kind written in the lock record, such as `engine`, `gcliff` or `harness`.

    Returns:
        The invocation object holding the entry's open use guard.

    Raises:
        ProvisioningError: Any stage failed; the diagnostic names the version, the path, the stage and the remedy.
    """
    return _Flow(layout, target, budget, seams, caller).run()


# eof
