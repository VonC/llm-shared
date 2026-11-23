"""Install one pin while holding its cache lock: staging, recorded children, verification, extraction, retirement, publication.

Step 5 of v0.14.0 git-cliff-provisioning (design "Target flow of git-cliff
provisioning", "Download, verification and extraction", "Publication",
"Child process lifecycle" and "Time budgets and retries"; design decisions
Q01, Q06, Q07 and Q17; requirement clarification Q14; plan decisions Q10 and
Q18 and the plan risk pass).

`install` runs under a held `CacheLock`, in this order:

1. Create `<pin>/.staging-<pid>-<created>-<token>/` and its `owner.json`.
2. Run at most two download worker attempts inside the download budget D,
   whose deadline is fixed before the first one; the 5 s retry delay is drawn
   from D and a retry needs time left after it. Only a retryable outcome is
   retried. Each worker is recorded in the lock record, then in the owner
   file, before it resumes; one that outlives its deadline was ended and
   reaped by the launcher before the stage fails.
3. Recompute the staged archive's size and SHA-256 (never retried), extract
   the single manifest member as `git-cliff.exe`, delete the archive.
4. Run the staging probe within its 15 s, recorded like a worker.
5. Write `entry.json`, then remove `owner.json` once every recorded child has
   ended, so the published entry holds only `git-cliff.exe` and `entry.json`.
6. `retire_entry`, then publish staging by one directory rename.

A failure whose children have all ended removes staging and propagates; the
caller then releases the lock. An unconfirmed end of a worker or the staging
probe retains the lock record (`retain_record()`), keeps staging and fails
with the containment stage: a later caller recovers both only once the owner
and every recorded child are `DEAD`. Every failure is a `ProvisioningError`
naming the entry directory, or the directory a refused write needed.

Code review round 1 of Step 5: a staging directory this call could not
create, a name collision included, is never removed; D is one absolute
deadline (a spent budget fails the download stage before any worker, and the
launcher counts a worker's creation and recording against its remainder);
and a staging file the worker could not write is the permission stage naming
its directory, not a network failure. Round 2: each worker request carries
D's absolute expiry itself (`ChildRequest.expires`), so no duration sampled
before the launch can restart it, and a worker recorded past it never runs;
a download line that cannot be written is the reporting stage.

`retire_entry` moves an existing entry aside from the state it finds: it
renames `git-cliff.exe` to `.retired-<pid>-<created>-<token>.exe` inside the
entry (refused while any use guard is open), then the directory to
`<pin>/.retired-<pid>-<created>-<token>/` (refused by any other open handle
inside); either refusal is the in-use stage. An entry already without its
executable skips the first rename, so an interrupted retirement resumes at
the directory. The retired directory is recovered once its name owner is
`DEAD`.

Step 6 installs an `InstallTarget` instead of an admitted pin: the asset to
fetch, its URL and member, an `accept` check that verifies the staged archive
and returns the SHA-256 the entry records (a `VerificationError` is the
verification stage), and a `before_publish` hook run once the entry is
complete in staging, before retirement and publication. `manifest_target`
keeps the production behavior exactly: verify against the manifest digest,
nothing before publication. An evidence candidate accepts against its trust
record or its release listing and writes its trust record in that hook.
`reuse` tells the provisioning flow whether an existing entry of the target
may be reused and which archive digest it must record; since code review
round 1 it is a function, called again under the lock, so a candidate whose
trust record another caller wrote meanwhile reuses that caller's entry
instead of replacing it.
"""

from __future__ import annotations

import functools
import secrets
import shutil
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from tools.release_workflow.git_cliff.archive import (
    ExtractionError,
    VerificationError,
    extract_member,
    verify_archive,
)
from tools.release_workflow.git_cliff.cache import (
    ENTRY_RECORD,
    EXECUTABLE,
    OWNER_FILE,
    Attempt,
    CacheLayout,
    CachePin,
    EntryRecord,
    OwnerFile,
    probe_problem,
)
from tools.release_workflow.git_cliff.download_worker import (
    WorkerRequest,
    outcome_fields,
    worker_command,
)
from tools.release_workflow.git_cliff.invocation import probe_request
from tools.release_workflow.git_cliff.manifest import download_url
from tools.release_workflow.git_cliff.messages import (
    ProvisioningError,
    Stage,
    announce,
    denied_write,
    downloading_line,
    permission_failure,
)
from tools.release_workflow.windows_child import (
    ChildRequest,
    ContainmentError,
    UnconfirmedEndError,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import datetime
    from pathlib import Path

    from tools.release_workflow.git_cliff.budget import BudgetPolicy
    from tools.release_workflow.git_cliff.cache_lock import CacheLock
    from tools.release_workflow.git_cliff.manifest import AdmittedPin
    from tools.release_workflow.windows_child import ChildOutcome
    from tools.release_workflow.windows_process import ProcessIdentity

_ATTEMPTS = 2
_OUTCOMES = frozenset({"ok", "retryable", "fatal"})


class InstallSeams(Protocol):
    """The provisioning seams an installation uses: `provisioning.ProvisioningSeams`, or the test world's."""

    @property
    def launch(self) -> Callable[[ChildRequest], ChildOutcome]:
        """Return the contained child launcher."""
        ...

    @property
    def current_identity(self) -> Callable[[], ProcessIdentity]:
        """Return the identity of this process, owner of the staging directory."""
        ...

    @property
    def clock(self) -> Callable[[], float]:
        """Return the monotonic clock in seconds."""
        ...

    @property
    def sleep(self) -> Callable[[float], None]:
        """Return the sleep of the retry delay."""
        ...

    @property
    def stderr(self) -> Callable[[str], None]:
        """Return the writer of one standard-error line."""
        ...

    @property
    def runtime(self) -> Path:
        """Return the interpreter that runs the download worker."""
        ...

    @property
    def now(self) -> Callable[[], datetime]:
        """Return the local time with its offset, for the entry record."""
        ...


def _nothing() -> None:
    """Do nothing before publication: an admitted pin has no record of its own to write."""


@dataclass(frozen=True, kw_only=True)
class InstallTarget:
    """What one installation fetches, accepts and publishes: an admitted pin, or an evidence candidate.

    `accept` checks the staged archive and returns the SHA-256 the entry
    records; `before_publish` runs once the entry is complete in staging.
    `reuse` is None when any valid entry may be reused without comparing its
    archive digest (production). Otherwise it is called before each reuse
    check, the lock-free one and the one under the lock, and returns the
    archive digest a reused entry must record, or None when no entry may be
    reused at that moment (an evidence candidate without a trust record yet).
    """

    version: str
    triple: str
    asset: str
    size: int
    member: str
    url: str
    accept: Callable[[Path], str]
    before_publish: Callable[[], None] = _nothing
    reuse: Callable[[], str | None] | None = None


def _verified(pin: AdmittedPin, archive: Path) -> str:
    """Verify a staged archive against the manifest and return the manifest digest."""
    verify_archive(archive, pin)
    return pin.sha256


def manifest_target(pin: AdmittedPin) -> InstallTarget:
    """Install an admitted pin as production always did: the manifest's size and digest, nothing before publication."""
    return InstallTarget(version=pin.version, triple=pin.triple, asset=pin.asset, size=pin.size, member=pin.member,
                         url=download_url(pin), accept=functools.partial(_verified, pin))


def _write(path: Path, content: bytes) -> None:
    """Write complete bytes beside the file, then replace it, so a reader never finds half a record."""
    temporary = path.with_name(f"{path.name}.tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def _reported(outcome: ChildOutcome) -> tuple[str, str, str | None]:
    """Read the worker's outcome line: its outcome class, its error and any local path it could not write."""
    fields = outcome_fields(outcome.stdout)
    if fields.get("outcome") not in _OUTCOMES:
        return "fatal", f"the download worker reported no outcome, status {outcome.status}", None
    path = fields.get("path")
    return str(fields["outcome"]), str(fields.get("error", "")), None if path is None else str(path)


def _attempts(count: int) -> str:
    """Count attempts in words."""
    return f"{count} attempt" if count == 1 else f"{count} attempts"


class _Installation:
    """One installation attempt of a pin by the lock holder."""

    def __init__(self, layout: CacheLayout, target: InstallTarget, budget: BudgetPolicy, seams: InstallSeams, lock: CacheLock) -> None:
        """Name the staging directory of this attempt after this process."""
        self._layout = layout
        self._target = target
        self._budget = budget
        self._seams = seams
        self._lock = lock
        owner = seams.current_identity()
        self._attempt = Attempt("staging", owner, secrets.token_hex(4))
        self._staging = layout.attempt_dir(target, "staging", owner, self._attempt.token)
        self._owner_file = OwnerFile(owner)

    def _failure(self, stage: Stage, detail: str) -> ProvisioningError:
        """Describe a failed stage at the entry directory."""
        return ProvisioningError(stage, version=self._target.version, path=self._layout.entry_dir(self._target), detail=detail)

    def run(self) -> None:
        """Create staging, fill it, retire the old entry and publish; clean up only what this call created and every ended child left."""
        try:
            self._staging.mkdir()
        except OSError as error:
            # A directory this call did not create, a name collision included, is never removed.
            raise permission_failure(self._target.version, error, self._staging) from error
        try:
            _write(self._staging / OWNER_FILE, self._owner_file.encode())
        except OSError as error:
            shutil.rmtree(self._staging, ignore_errors=True)
            raise permission_failure(self._target.version, error, self._staging) from error
        try:
            self._fill()
            self._target.before_publish()
            retire_entry(self._layout, self._target, self._attempt)
            self._publish()
        except UnconfirmedEndError as error:
            self._lock.retain_record()
            detail = f"{error}; its lock record and staging directory stay until every recorded process is DEAD"
            raise self._failure(Stage.CONTAINMENT, detail) from error
        except OSError as error:
            shutil.rmtree(self._staging, ignore_errors=True)
            raise permission_failure(self._target.version, error, self._staging) from error
        except BaseException:
            shutil.rmtree(self._staging, ignore_errors=True)
            raise

    def _record(self, child: ProcessIdentity) -> None:
        """Record a suspended child in the lock record, then in the owner file, before it resumes."""
        self._lock.record_child(child)
        self._owner_file = self._owner_file.with_child(child)
        _write(self._staging / OWNER_FILE, self._owner_file.encode())

    def _launch(self, request: ChildRequest) -> ChildOutcome:
        """Start a recorded child; a refused creation or recording ends it unrun and fails the stage."""
        try:
            return self._seams.launch(request)
        except UnconfirmedEndError:
            raise
        except ContainmentError as error:
            cause = error.__cause__
            if error.call == "record" and isinstance(cause, PermissionError):
                raise permission_failure(self._target.version, cause, self._staging) from error
            raise self._failure(Stage.CONTAINMENT, str(error)) from error

    def _fill(self) -> None:
        """Download, accept, extract and probe in staging, then write the entry record and drop the owner file."""
        archive = self._staging / self._target.asset
        self._download(archive)
        try:
            asset_sha256 = self._target.accept(archive)
        except VerificationError as error:
            raise self._failure(Stage.VERIFICATION, str(error)) from error
        try:
            digest, size = extract_member(archive, self._target, self._staging)
        except ExtractionError as error:
            raise self._failure(Stage.EXTRACTION, str(error)) from error
        archive.unlink()
        self._probe()
        record = EntryRecord(
            version=self._target.version, triple=self._target.triple, asset=self._target.asset, asset_sha256=asset_sha256,
            executable_sha256=digest, executable_size=size, provisioned=self._seams.now().isoformat(timespec="seconds"),
        )
        _write(self._staging / ENTRY_RECORD, record.encode())
        (self._staging / OWNER_FILE).unlink()

    def _download(self, archive: Path) -> None:
        """Run at most two recorded worker attempts against one absolute deadline D; only a retryable outcome with time left is retried.

        Each worker request carries D's absolute expiry on the seams' monotonic clock (the launcher's clock), never a
        duration sampled earlier: the launcher counts creation and recording against it and never resumes a worker
        whose expiry passed while it was recorded. The worker itself receives what remains, for its socket timeout.
        """
        budget, seams = self._budget, self._seams
        deadline = seams.clock() + budget.download
        announce(seams.stderr, downloading_line(self._target), version=self._target.version, path=self._layout.entry_dir(self._target))
        failures: list[str] = []
        while True:
            remaining = deadline - seams.clock()
            if remaining <= 0:
                raise self._failure(Stage.DOWNLOAD, self._spent(failures))
            request = WorkerRequest(mode="archive", url=self._target.url, target=archive, expected_size=self._target.size,
                                    remaining=remaining)
            executable, arguments = worker_command(seams.runtime, self._layout.tooling_root, request)
            outcome = self._launch(ChildRequest(executable, tuple(arguments), cwd=self._staging, record=self._record, expires=deadline))
            if outcome.timed_out:
                raise self._failure(Stage.DOWNLOAD, f"the download did not finish within its budget of {budget.download} s")
            kind, error, refused = _reported(outcome)
            if kind == "ok":
                return
            if refused is not None:
                raise denied_write(self._target.version, refused, f"the download worker reported {error}", self._staging)
            failures.append(error)
            if kind == "fatal" or len(failures) == _ATTEMPTS:
                raise self._failure(Stage.DOWNLOAD, f"download failed after {_attempts(len(failures))} ({error})")
            if deadline - seams.clock() <= budget.retry_delay:
                raise self._failure(Stage.DOWNLOAD, self._spent(failures))
            seams.sleep(budget.retry_delay)

    def _spent(self, failures: list[str]) -> str:
        """Explain a download budget D spent before an attempt could start."""
        if not failures:
            return f"its budget of {self._budget.download} s was spent before the first attempt"
        return (f"download failed after {_attempts(len(failures))} ({failures[-1]}); no time remained for a retry"
                f" within its budget of {self._budget.download} s")

    def _probe(self) -> None:
        """Run the recorded staging probe within its budget; it must report the pin."""
        outcome = self._launch(probe_request(self._staging / EXECUTABLE, inherited=(), deadline=self._budget.probe, record=self._record))
        if outcome.timed_out:
            raise self._failure(Stage.PROBE, f"the version probe did not end within its budget of {self._budget.probe} s")
        problem = probe_problem(outcome, self._target)
        if problem is not None:
            raise self._failure(Stage.PROBE, problem)

    def _publish(self) -> None:
        """Publish staging by one directory rename; Windows never replaces an existing target."""
        self._staging.rename(self._layout.entry_dir(self._target))


def install(layout: CacheLayout, target: InstallTarget, budget: BudgetPolicy, seams: InstallSeams, lock: CacheLock) -> None:
    """Install a target while holding its lock, leaving a published entry or the state the failure contract names.

    Args:
        layout: The cache layout of the executing checkout, production or evidence.
        target: The admitted pin (`manifest_target`) or evidence candidate to install.
        budget: The caller's resolved stage budgets.
        seams: The launcher, identity, clock, sleep, standard-error writer, worker runtime and local time.
        lock: The held cache lock of this pin, where each child is recorded.

    Raises:
        ProvisioningError: Any stage failed; staging was removed unless a child's end is unconfirmed.
    """
    _Installation(layout, target, budget, seams, lock).run()


def retire_entry(layout: CacheLayout, pin: CachePin, attempt: Attempt) -> None:
    """Move an existing entry aside, under the lock, starting from the state it finds.

    Args:
        layout: The cache layout of the executing checkout.
        pin: The pin whose entry is retired.
        attempt: The attempt whose owner and token name the retired executable and directory.

    Raises:
        ProvisioningError: The in-use stage: a guard or another open handle refused a rename.
    """
    entry = layout.entry_dir(pin)
    if not entry.is_dir():
        return
    executable = entry / EXECUTABLE
    retired = layout.attempt_dir(pin, "retired", attempt.owner, attempt.token)
    for source, target, what in ((executable, entry / f"{retired.name}.exe", EXECUTABLE), (entry, retired, "the entry directory")):
        if source.exists():
            try:
                source.rename(target)
            except OSError as error:
                msg = f"{what} cannot be moved aside while it is in use: {error}"
                raise ProvisioningError(Stage.IN_USE, version=pin.version, path=entry, detail=msg) from error


# eof
