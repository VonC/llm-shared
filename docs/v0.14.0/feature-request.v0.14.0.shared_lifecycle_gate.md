# Every Suite Gets a Stopwatch

- Type: feature-request
- Test group: whole suite
- Target version: v0.14.0
- Slug: shared_lifecycle_gate

## Draft basis and user need for the shared lifecycle gate

As the maintainer of a project that uses llm-shared, I want to turn on the
per-test lifecycle budget that llm-shared enforces on its own suite, so that the
budget the shared test-writing instruction asks for is checked by every test
run instead of being left to each agent's care.

The [draft](draft.v0.14.0.shared_lifecycle_gate.md) records the need and the
import check of 2026-11-03. This requirement states the requested behavior; how
the plugins are packaged and made importable remains design work.

## Current behavior in v0.13.0 for the lifecycle gate

- llm-shared's own suite runs under a lifecycle gate. Each test lifecycle,
  setup through teardown, stays at or under a CPU ceiling
  (`test_lifecycle_limit`, default 0.1 s) and a wall limit
  (`test_lifecycle_wall_limit`, default 1 s). A test proven under its ceiling on
  this checkout passes up to its band top (`test_lifecycle_cpu_band_factor`,
  default 2.5), until `test_lifecycle_cpu_drift_runs` (default 3) consecutive
  measured runs above the ceiling cost its proof. Proofs and accepted
  exceptions live in the untracked per-checkout record
  `a.test-lifecycle-cpu.local.json` in the review artifact home, written once
  per run by the xdist controller, and every run ends with a
  `lifecycle CPU band` summary.
- A value that would switch the gate off (a limit not above 0 or not finite, a
  factor under 1, a drift count that is not a whole number of at least 1) stops
  pytest with a usage error naming the key, exit code 4.
- The same module also rejects process creation: at import it installs a Python
  audit hook that fails any test, fixture included, that starts a process.
  The hook stays installed for the rest of the process.
- Both live in llm-shared's `tests/` (`tests/simulation_policy.py` and
  `tests/lifecycle_cpu_record.py`), loaded through `pytest_plugins` in
  `tests/conftest.py`. The gate and the process audit cannot be loaded apart.
- The record code imports `tools.review_artifact_configuration` and
  `tools.review_exchange_models` to find the review artifact home: the home
  `.review-artifacts.ini` names, else `.reviews`, used only when it exists and
  its `.gitignore` is exactly `*`.
- The coverage source is `tools` only, so the gate's own code sits outside
  llm-shared's 100% coverage gate.
- A consuming project gets neither the gate nor the audit. llm-shared is never
  installed (`package = false`); groundhog runs from llm-shared's environment
  but spawns the project's own `pytest`, found on the `PATH` the project's
  `senv.bat` prepares, so tests run in the project's interpreter and import
  path. None of the seven consuming projects checked on 2026-11-03 has
  llm-shared on that path, and six have a top-level `tools` package of their
  own, one a `tests` package, so llm-shared's root on the path would not help.
- Those projects run pytest 9.1, one on Python 3.12 and six on 3.13; one has
  pytest-xdist and six have Hypothesis.
- `instructions/write-fast-python-tests.md` tells every project's agent to keep
  each lifecycle under the two limit keys, but in a consuming project no
  over-budget test fails. Its only time check is the groundhog `speed` verdict,
  which judges call time only and flags a call only when it is both a
  statistical outlier and above the project's duration floor.

## Gap to close in the implementation for the shared lifecycle gate

1. Two shared pytest plugins, each enabled only by naming it with `-p`, in a
   project's `addopts` or on one command line:
   - the lifecycle gate: both limits, the CPU band and drift guard, the
     per-checkout record and the end-of-run summary;
   - the process audit.

   Neither loads unless named: a project that does nothing sees no change in
   any test outcome or summary.
2. Each plugin works alone, and both together behave as the current gate does.
   The audit tracks the running test by itself, so a project whose tests still
   start processes can take the gate now and add the audit once its tests are
   converted.
3. Each plugin has an import name of its own, never `tools` or `tests`, and
   loads in a project that has top-level packages with those names, without
   hiding them or being hidden by them. The plugin files live under llm-shared's
   `tools/`.
4. At test time the plugins import only the standard library and pytest. The
   artifact home lookup comes with the gate plugin and keeps today's rule:
   the home `.review-artifacts.ini` names, else `.reviews`, recorded only when
   that home exists and its `.gitignore` is exactly `*`; otherwise every test
   stays strict and the summary says nothing was recorded.
5. Both plugins run in the consuming project's interpreter on Python 3.12 and
   later with pytest 9.1 and later, with or without pytest-xdist, and without
   needing Hypothesis.
6. The gate keeps today's contract unchanged: the four `test_lifecycle_*` ini
   keys, their defaults and their precedence (`-o` for one run, then the
   project's pytest configuration, then the plugin default); the usage error
   with exit code 4; how one test's CPU limit is chosen; the record name,
   schema, `nodes` and `exceptions` objects; one record write per run on the
   controller; the failure message and the summary lines of
   `wiki/reference/test-lifecycle-limits.md`.
7. llm-shared becomes the first user. `tests/conftest.py` loads both shared
   plugins instead of its own modules, and no second copy of the gate or the
   audit remains under `tests/`. Every assertion of the current gate tests is
   kept, and the plugin code now counts toward the 100% coverage gate.
8. One documented, supported import route makes the plugins importable from a
   consuming project, for a plain `pytest` run in the project's shell and for
   every groundhog stage. The design selects that route so that it satisfies
   the activation scope this requirement settles and the package-name rule of
   item 3.
9. The documentation describes the plugins for any project: the test lifecycle
   reference and how-to pages, a how-to for a consuming project opting in to
   each plugin, and `instructions/write-fast-python-tests.md`, which says where
   the budget is enforced and how a project turns it on.
10. llm-shared is public: no consuming project is named in the plugins, their
    tests or their documentation.

## Acceptance criteria for the shared lifecycle gate

- A project that names neither plugin gets the same outcomes and summary as
  before.
- With the gate plugin only, a test whose lifecycle uses more CPU than its
  limit fails with today's message, giving both clocks and the basis of the
  limit; a proven test inside its band top passes and is listed as a band pass;
  a test that starts a process is not failed for it.
- With the audit plugin only, a test or fixture that starts a process fails,
  naming the test and the process event; no lifecycle limit is applied, no
  `lifecycle CPU band` summary appears and no lifecycle record is written.
- With the gate plugin and no existing ignored artifact home, every test is
  held to its ceiling, nothing is recorded, and the summary says so.
- With both plugins, every current gate and audit test of llm-shared passes
  unchanged in what it asserts.
- In a project with its own top-level `tools` and `tests` packages, both
  plugins load through the documented way, and the project's own packages still
  import.
- Loading either plugin imports no llm-shared module other than the plugin
  itself.
- An invalid value of any `test_lifecycle_*` key stops pytest with exit code 4
  and a message naming the key.
- Under pytest-xdist the record is written once per run, by the controller;
  without xdist the single process writes it.
- llm-shared's whole-suite `ghog day --full=speed` passes with the shared
  plugins, at 100% coverage that includes the plugin modules.

## Out of scope for the shared lifecycle gate

- Turning either plugin on in any consuming project, or converting a consuming
  project's tests to meet the budget.
- Changing the groundhog `speed` verdict or its duration floor.
- llm-shared's other suite plugins (`tests.memory_filesystem`,
  `tests.scenario_cli`, `tests.scenario_generation`,
  `tests.testmon_monitoring`) and the rest of `tests/conftest.py`, which stay
  llm-shared's own.

## Code references for the shared lifecycle gate

- `tests/simulation_policy.py`: process audit hook, lifecycle CPU and wall
  measurement, ini key declarations, failure message.
- `tests/lifecycle_cpu_record.py`: band policy, record parsing and writing,
  artifact home lookup, `LifecycleGate`, controller-side `BandCollector` and
  the end-of-run summary.
- `tests/conftest.py`: loads both modules through `pytest_plugins` with the
  other suite plugins.
- `tests/unit/tools/test_lifecycle_policy.py` and
  `tests/unit/tools/test_lifecycle_cpu_band.py`: the gate's current tests.
- `pyproject.toml`: the project's `test_lifecycle_*` values, `addopts`, and the
  coverage source `tools`.
- `tools/review_artifact_configuration.py` and `tools/review_exchange_models.py`:
  the artifact home lookup the record uses today.
- `tools/groundhog/commands.py` and `tools/groundhog/runner.py`: find the
  project's `pytest` on `PATH` and spawn it with spawn-only environment
  overrides.
- `senv.bat`: puts llm-shared's `bin` on `PYTHONPATH`, not its root.
- `wiki/reference/test-lifecycle-limits.md`,
  `wiki/how-to/set-test-lifecycle-limits.md`,
  `wiki/explanation/why-fast-tests-keep-the-work-they-assert.md` and
  `instructions/write-fast-python-tests.md`: the gate's documentation.

## Open questions for the v0.14.0 shared lifecycle gate feature request

### Q01: Where an opted-in project's gate applies

Question description: the requirement enables each plugin by naming it with
`-p` in the project's `addopts` or on one command line. A name in `addopts`
travels with the project's tracked configuration, so every pytest run of that
project loads it: in an llm-shared shell, but also in an IDE test runner, on a
continuous-integration machine, or on another clone where llm-shared is absent.
There, pytest stops at startup because the plugin cannot be imported. The
requirement does not say whether the gate must apply to every run of an
opted-in project, or only to the runs llm-shared prepares (the project's
`senv.bat` shell and every groundhog stage), nor what happens elsewhere.

#### BBQ for Q01

A club decides its barbecue grills must carry a thermometer. If the rule is
written into the grill itself, every grill, even one lent to a neighbour who
owns no thermometer, refuses to light. If the rule belongs to the club's own
cookouts, the club's grills always carry one there, and a lent grill still
lights. The question is whether the thermometer rule belongs to the grill or
to the club's cookouts. In this picture: the grill is the consuming project's
pytest configuration, the thermometer is the shared plugin, the club's
cookouts are the shells and groundhog stages llm-shared prepares, and the
neighbour's garden is an IDE runner, a CI machine or a clone without
llm-shared.

#### Options for Q01

- Option A1: every run of an opted-in project applies the gate; a run where the
  plugin cannot be imported stops at startup, naming the missing plugin.
  - pro: the budget can never be skipped by accident; one rule everywhere.
  - pro: matches the requirement's current `addopts` wording.
  - con: every place the project's tests run (CI, IDE, other clones) must
    provide llm-shared, or the project cannot run its tests at all there.
- Option A2: when a project has opted in, a plain `pytest` run from the
  project's prepared shell and every groundhog test stage load the selected
  plugins; runs outside that prepared environment get no automatic
  activation, and may still name a plugin explicitly where it is importable.
  - pro: the agent workflows llm-shared documents run tests through groundhog
    or the project's prepared shell, so those runs are gated.
  - pro: no new failure mode for CI, IDE runners or clones without llm-shared.
  - con: a plain `pytest` outside an llm-shared shell is not gated.
  - con: the opt-in cannot be a bare `-p` in tracked `addopts`; the
    requirement wording changes.
- Option A3: every run tries to apply the gate; a run where the plugin cannot
  be imported continues without it and prints a visible notice.
  - pro: gated wherever llm-shared is present, and never blocking elsewhere.
  - con: needs something in the project that can run and print without the
    plugin, beyond a plain `-p`.
  - con: a notice in a long log is easy to miss, so the budget can silently
    lapse on a machine where llm-shared moved.

#### Recommended option for Q01 (with arguments for this choice)

Option A2: the budget exists for the work agents do, and the agent workflows
llm-shared documents run tests through groundhog or the project's prepared
shell. A2 gates every one of those runs and adds no failure mode to places
that never had llm-shared, which matters for a consuming project that runs its
tests elsewhere. It does not promise that every agent uses that environment.
A1 makes llm-shared a hard dependency of every test run of the project; A3
trades that for a budget that can lapse without anyone noticing.

#### Answer to Q01: option A2 (with reason why it must be accepted as the answer)

Option A2: it gates the runs of the documented agent workflows, which is the
need stated in the user story, while a project's other environments keep
working unchanged. The current requirement still names the plugins with `-p`
in `addopts`; only if the user selects A2 does consolidation change gap items
1 and 8 and the first acceptance criteria, so that the project declares the
opt-in and llm-shared's prepared shell and groundhog apply it. Q11 settles what
a prepared run does when a selected plugin cannot be imported.

User decision: confirmed — option A2.

Decision date: 2026-11-04.

The project declares the opt-in. A plain `pytest` run in the project's
prepared `senv.bat` shell and every groundhog test stage load the selected
plugins. Runs outside that prepared environment receive no automatic
activation, but may name a plugin explicitly where it is importable.
This applies the policies to the documented agent workflows while leaving
other environments working without requiring llm-shared there. A bare
`pytest` outside the prepared environment receives no automatic gate.

User comment: explain the remaining questions in greater detail, including
concrete examples, option tradeoffs, the recommendation and effects on other
questions. Q11's missing-plugin behavior remains undecided.

Review clarification dated 2026-11-05: the preceding user comment records the
state at the time. Q11 was subsequently decided as K1 on 2026-11-04.

Review consequences pending consolidation (round 3, 2026-11-05): selecting a
plugin through both prepared activation and explicit loading must load it
once, without duplicate registration or doubled summaries. Repeatable
in-process evidence must cover prepared-shell and groundhog activation and
K1's startup failure, within the coverage gate on `tools`. H3 adds the
temporary real-environment trial. These are review consequences, not new
recorded user decisions.

### Q02: What proves the Python 3.12 support

Question description: the requirement promises both plugins on Python 3.12
and later, because one consuming project still runs 3.12. llm-shared itself
runs on 3.13 only, and its test infrastructure requires 3.13. The acceptance
criteria do not say what evidence shows the plugins work on 3.12.

#### BBQ for Q02

A sauce is promised to suit a guest who cannot eat garlic, but the kitchen
only ever tastes it with garlic bread. The cook can either serve it once on
plain bread to that guest, or check the recipe card for every ingredient. In
this picture: the guest is the consuming project on Python 3.12, the garlic
bread is llm-shared's 3.13 environment, serving it on plain bread is a real
run under Python 3.12, and checking the recipe card is a static check of the
plugin files against Python 3.12.

#### Options for Q02

- Option B1: acceptance includes a run of the plugins' own tests under a Python
  3.12 interpreter.
  - pro: direct evidence; catches runtime differences, not only syntax.
  - con: those tests must run without llm-shared's 3.13-only test helpers, and
    a second interpreter enters the validation.
- Option B2: acceptance relies on static checks of the plugin files targeting
  Python 3.12 (linter and type checker set to 3.12), with the full behaviour
  proven on 3.13.
  - pro: cheap, runs in every check, and catches syntax and standard-library
    features newer than 3.12 in small stdlib-plus-pytest modules.
  - con: indirect: it cannot show import-time behaviour, pytest hook
    compatibility or runtime library behaviour on 3.12, so it does not
    demonstrate the runtime support the requirement promises.
- Option B3: drop the 3.12 promise; the plugins require 3.13, like llm-shared.
  - pro: one interpreter, nothing extra to prove.
  - con: the consuming project on 3.12 cannot opt in until it upgrades.

#### Recommended option for Q02 (with arguments for this choice)

Option B1: the requirement promises runtime support on Python 3.12, and only
a run under 3.12 shows that the plugins load, hook into pytest and behave
there. Static checks set to 3.12 (B2) stay useful as a cheap supplement on
every change, but they cannot demonstrate import-time or hook behaviour. B1
costs a second interpreter and tests that do not depend on llm-shared's
3.13-only helpers; B3 excludes a project the requirement wants to serve.
Revised after the round 1 review, which showed that B2 alone does not
establish the runtime promise.

#### Answer to Q02: option B1 (with reason why it must be accepted as the answer)

Option B1: acceptance includes executable evidence under Python 3.12 for
plugin loading, independent and combined operation, settings rejection,
lifecycle enforcement and audit attribution. That evidence uses tests
independent of llm-shared's 3.13-only helpers, and static checks set to 3.12
supplement it. The exact harness and test location belong to the design. If
the user prefers B2, the requirement must say that 3.12 support is checked
statically only, not demonstrated at runtime.

Historical decision, superseded by the user's compatibility requirement on
2026-11-05:

> On 2026-11-04 the user selected B3: require Python 3.13, promise no Python
> 3.12 support and require no Python 3.12 validation. Supporting 3.12 was
> not then a priority. That decision superseded the proposed B1 answer and
> would have removed the 3.12 promise at consolidation. Its statement that
> Q08 remained open was historical; Q08 was subsequently confirmed as H3.

User decision: confirmed: Python 3.12 compatibility is required when a
consuming project needs it; this supersedes B3.

Decision dated 2026-11-05: the user explicitly requires compatibility with
Python 3.12 if a consuming project needs that interpreter. A current
consumer's declared interpreter constraint requires 3.12, so both plugins
must support Python 3.12 and later. Acceptance requires executable Python
3.12 evidence of plugin loading and behavior, alongside Python 3.13
validation; static checks or a simulated version alone cannot demonstrate
runtime compatibility. The Python 3.12 evidence must not depend on
llm-shared's Python 3.13-only test helpers; its harness remains design work.
This does not require changing llm-shared's own interpreter or upgrading
any consuming project. Q08 H3 remains confirmed and can share suitable
3.12 evidence. Q15's load-time check must use the revised 3.12 minimum.

Review consequence pending consolidation (round 5, 2026-11-05): gap item
8's import route must work in a consuming interpreter outside llm-shared's
own declared Python range, currently `>=3.13,<3.14`, without installing
llm-shared or anything bound by that declaration into the consumer.
This includes Python 3.12 and the later versions promised by gap item 5.
Plugin documentation names Python 3.12 and 3.13 as the interpreters
validated for this release. Any earlier consolidation step derived from B3
or the old O2 threshold that would raise gap item 5 to 3.13 is superseded;
the 3.12 evidence schedule is settled by Q16 P3.

### Q03: Which platforms the plugins promise

Question description: today the gate is only exercised on Windows, where the
process CPU clock advances in ticks of about 15.6 ms. Its audit events already
name POSIX calls (`os.fork`, `os.posix_spawn`, `os.exec`), and the plugins will
be shared tooling. The requirement does not say whether Linux and macOS are
supported, merely tolerated, or out of scope.

#### BBQ for Q03

A grill timer is sold as working on gas, and it has only ever been tested on
gas. It has no part that needs gas, but nobody has tried it on charcoal. The
label can say "gas only", "gas and charcoal", or "tested on gas". In this
picture: the timer is the shared plugin pair, gas is Windows, charcoal is
Linux and macOS, and the label is what the documentation and acceptance
criteria promise.

#### Options for Q03

- Option C1: Windows only, as proven today.
  - pro: the promise matches the evidence exactly.
  - con: a project tested on Linux CI is told it is unsupported, though
    nothing in the plugins is Windows-specific.
- Option C2: Windows, Linux and macOS, each proven.
  - pro: a full promise for shared tooling.
  - con: needs runs on platforms llm-shared does not use today.
- Option C3: validated on Windows; documented as intended to use portable
  APIs, with Linux and macOS unvalidated in this release and no other
  platform in acceptance.
  - pro: honest about the evidence without excluding other platforms.
  - con: a platform-specific defect elsewhere would surface at a user, not in
    acceptance.

#### Recommended option for Q03 (with arguments for this choice)

Option C3: the plugins rely on `time.process_time`, the audit-hook API and
pytest, all portable APIs, so excluding other platforms would be arbitrary,
while proving them needs machines llm-shared does not use. A portable API does
not prove the same audit events and timing on every system, so C3 claims only
what is validated and states the rest as intent.

#### Answer to Q03: option C3 (with reason why it must be accepted as the answer)

Option C3: it keeps the acceptance evidence on the platform every consuming
project uses today and does not overstate the rest. The documentation then
says: validated on Windows; intended to use portable APIs; Linux and macOS
unvalidated in this release.

User decision: confirmed — option C3.

Decision date: 2026-11-04.

Validate the plugins on Windows. Document their intent to use portable APIs,
with Linux and macOS explicitly unvalidated in this release and no other
platform required for acceptance. This keeps the support statement aligned
with the evidence without excluding use on other platforms.

### Q04: Which phases the shared process audit covers

Question description: today the audit rejects a process started while a test
runs, its setup and teardown included, shared fixtures included, and leaves
pytest's own startup (worker start, collection, `conftest.py` import) alone. A
consuming project may start processes at import or collection time. The
requirement does not say whether the shared audit keeps today's window or also
covers collection.

#### BBQ for Q04

A smoke detector watches the patio while food is on the grill, from lighting
to cleaning, but not while the chairs are being carried out. Someone could
light a fire while carrying chairs. In this picture: the smoke detector is
the process audit, food on the grill is a test's setup, call and teardown,
carrying chairs is collection and `conftest.py` import, and lighting a fire is
starting a process.

#### Options for Q04

- Option D1: keep today's window: each test's setup, call and teardown, shared
  fixtures included; collection and worker startup are not watched.
  - pro: same behaviour as llm-shared's audit, so its proof carries over.
  - con: a process started at module import or collection goes unseen.
- Option D2: also watch collection and `conftest.py` import.
  - pro: no process creation anywhere in the test run escapes.
  - con: tooling a project runs at collection (plugins, version probes) may
    start processes legitimately and would fail every run.
- Option D3: today's window by default, with an ini switch to watch collection
  too.
  - pro: stricter projects can opt in further.
  - con: one more setting to document and test, for a case not seen so far.

#### Recommended option for Q04 (with arguments for this choice)

Option D1: the audit exists to keep test work in process and cheap, and the
lifecycle CPU gate measures the same window, so the two stay aligned.
Collection-time processes are not a reported problem, and D2 could break
projects through third-party plugins they do not control.

#### Answer to Q04: option D1 (with reason why it must be accepted as the answer)

Option D1: it preserves the proven behaviour, matches the CPU gate's window
and adds no failure outside the tests. The requirement then states that the
hook may stay installed for the whole process, while enforcement is active
only during a test's setup, call and teardown, shared-fixture work attributed
to the active lifecycle included; collection and worker startup stay outside
that window.

User decision: confirmed — option D1.

Decision date: 2026-11-04.

Preserve the current enforcement window: each test's setup, call and teardown,
including shared-fixture work attributed to the active lifecycle. The hook
may remain installed throughout the process, but collection, `conftest.py`
imports during collection and pytest worker startup stay outside enforcement.
This preserves the existing policy and its alignment with lifecycle timing.

### Q05: Exemptions from the process audit

Question description: in llm-shared no test may start a process, with no
exemption. A consuming project may have a few tests that must start one, for
example an end-to-end test of its own command line. The requirement lets such a
project take the gate without the audit, but does not say whether the audit
may exempt single tests.

#### BBQ for Q05

The patio rule says no open flame. A family with one old fire pit can either
skip the rule entirely until the pit is replaced, or keep the rule and post a
signed note naming the one fire pit and why it stays. In this picture: the
patio rule is the process audit, the old fire pit is a test that must start a
process, skipping the rule is taking the gate without the audit, and the
signed note is a per-test exemption with a recorded reason.

#### Options for Q05

- Option E1: no exemption: a project takes the audit for its whole suite or
  not at all.
  - pro: same rule as llm-shared; no exemption list that only grows.
  - pro: the gate-only opt-in already offers the gradual path.
  - con: one unconvertible test keeps a whole project off the audit.
- Option E2: a per-test marker exempts a test, with a required reason, listed
  at the end of every run.
  - pro: a project can audit everything else now.
  - con: a visible but easy escape that weakens the guarantee over time.
- Option E3: exemption by path pattern in the project's configuration.
  - pro: groups end-to-end tests in one place.
  - con: coarse; new tests under the pattern are exempt without review.

#### Recommended option for Q05 (with arguments for this choice)

Option E1: llm-shared's rule is that tests simulate at the nearest function
instead of starting processes, and slow or process-starting tests are
converted rather than excluded. The gate-only opt-in already lets a project
adopt the budget before its audit conversion is done, so an exemption
mechanism is not needed for adoption.

#### Answer to Q05: option E1 (with reason why it must be accepted as the answer)

Option E1: it keeps the audit's guarantee whole and consistent with
llm-shared's own suite, while the separate gate opt-in covers gradual
adoption. The requirement then states that there are no per-test or path
exemptions from the audit, and that a project may enable the lifecycle plugin
without enabling the audit.

User decision: confirmed — option E2.

Decision date: 2026-11-04.

Allow a per-test marker to exempt a test from the process audit, with a
required reason. List the exemptions at the end of every run. This permits
auditing the remaining tests while selected tests retain process creation.
The exemption does not grant a CPU or wall-time exception. This choice
supersedes the proposed E1 answer above; consolidation must replace its
no-exemption rule and add the marker, required reason and reporting behavior.
The follow-up review must examine how exemptions interact with shared-fixture
setup and teardown under Q04's lifecycle enforcement window.

Review consequences pending consolidation (round 3, 2026-11-05): E2 needs
the contracts proposed in Q12 to Q14. A marker registered only by the audit
plugin would break strict-marker runs outside A2's prepared environment;
Q13 therefore includes registration independent of loading that plugin.
The audit-only acceptance criterion must allow its exemption list while
still excluding a lifecycle CPU band summary. The no-opt-in criterion must
also exclude an exemption list. llm-shared's own whole-suite run must list
no exemption; E2 does not authorize process-starting tests in this suite.

Measurement clarification from review: the CPU clock measures only the
test process. A child's CPU is outside that budget, including in gate-only
runs. The wall limit still measures elapsed setup-through-teardown time,
including waits for a child during that lifecycle; it does not bound the
lifetime of a child left running afterwards. This changes neither E2's
timing qualification nor F1's accepted CPU exceptions.

Review clarification dated 2026-11-05 (round 5): the round 3 consequence
that llm-shared's own whole-suite run lists no exemption includes L3
fixture exemptions. That suite declares neither test nor fixture
exemptions; E2 and L3 do not authorize process-starting work in it.

### Q06: Where a consuming project's accepted CPU exceptions live

Question description: today an accepted slow test is an `exceptions` entry
(measured `cpu`, `attempted`, `reason`) in the untracked per-checkout record.
In a consuming project with several clones or contributors, an exception
accepted in one clone does not exist in the others. groundhog's call-duration
exclusions, by contrast, live in tracked project configuration. The
requirement keeps today's record unchanged, without saying whether that suits
consuming projects.

#### BBQ for Q06

A cook writes "this brisket may take longer" on a sticky note on their own
oven. A second cook in another kitchen never sees it. The note could move to
the shared recipe book, but the time written on it was measured on the first
oven. In this picture: the sticky note is an `exceptions` entry in the
untracked per-checkout record, the other kitchen is another clone of the
project, the recipe book is tracked project configuration, and the measured
time is the entry's machine-specific `cpu` value.

#### Options for Q06

- Option F1: keep today's place: exceptions live in the untracked per-checkout
  record.
  - pro: the `cpu` value is measured on that machine, where it is true.
  - pro: no change to the record contract llm-shared already uses.
  - con: each clone must accept the same slow test again.
- Option F2: exceptions move to a tracked project file; proofs stay per
  checkout.
  - pro: an accepted slow test is a reviewed project decision, shared by all
    clones.
  - con: a measured CPU value from one machine becomes everyone's ceiling.
  - con: changes the contract for llm-shared's own suite too.
- Option F3: both: tracked exceptions, overridden by per-checkout ones.
  - pro: shared decisions with local tuning.
  - con: two sources and a precedence rule to explain.

#### Recommended option for Q06 (with arguments for this choice)

Option F1: the exception's ceiling is a measured CPU value, which only holds on
the machine that measured it, and exceptions are meant to stay rare. Keeping
them per checkout matches the record's purpose and the requirement's promise
of an unchanged contract.

#### Answer to Q06: option F1 (with reason why it must be accepted as the answer)

Option F1: it keeps exceptions true to the machine they were measured on and
avoids a second source of ceilings. Accepted CPU exceptions remain in the
ignored per-checkout record and are not copied into tracked configuration;
their fields and the wall limit are unchanged. The requirement already states
the record is unchanged; the answer confirms that for consuming projects.

User decision: confirmed — option F1.

Decision date: 2026-11-04.

Keep accepted CPU exceptions in the ignored per-checkout record, with their
existing measured `cpu`, `attempted` and `reason` fields. Do not distribute
them through tracked configuration or add a second source of exceptions.
Each checkout establishes its own accepted CPU exceptions; the wall limit
and the separate process-audit exemption choice remain unchanged.

### Q07: A report-only mode for adoption

Question description: a consuming project opting in with an existing suite may
see many lifecycles over 0.1 s at once. The gate deliberately refuses any
setting that would switch it off. The requirement does not say whether
opting in may start in a mode that measures and lists offenders without
failing them.

#### BBQ for Q07

A new food inspector arrives at a restaurant. They can close the kitchen on
the first visit for every violation, or spend a first visit writing a list
only. The restaurant can also ask for the old, looser rules for a while. In
this picture: the inspector is the lifecycle gate, closing the kitchen is
failing over-budget tests, the list-only visit is a report-only mode, and the
looser rules are a higher `test_lifecycle_limit` and
`test_lifecycle_wall_limit` the project sets for a while.

#### Options for Q07

- Option G1: no report-only mode: opting in enforces; a project that needs
  time sets a higher `test_lifecycle_limit`, and a higher
  `test_lifecycle_wall_limit` where wall time overruns, in its configuration
  and lowers them later.
  - pro: keeps the decision that no setting switches the gate off.
  - pro: proofs earned under a looser ceiling already stop holding when the
    ceiling is lowered.
  - con: the first runs after opting in can fail many tests at once.
- Option G2: an ini switch for report-only: measure, record and list
  offenders, fail nothing.
  - pro: gentle adoption with a full list of offenders.
  - con: a setting that switches the enforcement off, against the earlier
    decision; it can stay on forever.
- Option G3: an automatic grace period: the first runs after opting in only
  report.
  - pro: no setting to forget.
  - con: hidden state; the same suite passes or fails depending on history.

#### Recommended option for Q07 (with arguments for this choice)

Option G1: it keeps the gate's rule that no value turns it off, and the
existing CPU and wall settings already give a project a temporary, visible,
tracked loosening. A run reports a violation for every lifecycle it executes;
selection or early-stop options can keep it from a complete inventory, which a
full run without them gives, so a report-only mode would add little.

#### Answer to Q07: option G1 (with reason why it must be accepted as the answer)

Option G1: it reuses a mechanism that already exists and keeps the gate
honest. The how-to for consuming projects then shows how to adopt with
temporarily higher CPU and wall limits and lower them step by step, and notes
that only a full run without selection or early-stop options lists every
offender.

User decision: confirmed — option G1, with all four settings configurable.

Decision date: 2026-11-04.

Opting in enforces the gate immediately, with no report-only mode or automatic
grace period. A project may adopt with higher CPU and wall limits and lower
them later. The CPU limit, wall limit, CPU band factor and consecutive
drift-run count all remain configurable:

| Setting | Valid values |
| --- | --- |
| `test_lifecycle_limit` | Finite seconds, greater than zero |
| `test_lifecycle_wall_limit` | Finite seconds, greater than zero |
| `test_lifecycle_cpu_band_factor` | Finite factor, at least 1 |
| `test_lifecycle_cpu_drift_runs` | Finite whole number, at least 1 |

For each setting, a pytest command-line `-o` override takes precedence over
project pytest configuration, which takes precedence over the plugin default.
No value disables enforcement. This confirms configurability and validation,
not the defaults, which remain the subject of Q10.

Review consequence pending consolidation (round 3, 2026-11-05): the baseline
description of invalid settings must explicitly include a non-finite band
factor and a drift count that is not a finite whole number. This matches
the existing `setting()` validation and the confirmed G1 table.

### Q08: Evidence for the consuming-project criteria

Question description: two acceptance criteria describe a consuming project:
the plugins load beside the project's own top-level `tools` and `tests`
packages, and they import no other llm-shared module. llm-shared's suite
forbids starting a process and holds every test to 0.1 s of CPU, so it cannot
spawn a pytest run in a sample project. The requirement does not say what
evidence accepts these criteria.

#### BBQ for Q08

A camping stove is promised to work at any campsite. The maker can test it on
a mock campsite built inside the factory, or take it once to a real campsite
and light it there without changing anything at the site. In this picture:
the stove is the plugin pair, the mock campsite is an in-process sample
project inside llm-shared's suite, the real campsite is one consuming
project, and lighting it without changes is a temporary trial in that
project's environment that leaves nothing enabled behind.

#### Options for Q08

- Option H1: in-process tests in llm-shared's suite only, with a sample project
  holding its own `tools` and `tests` packages.
  - pro: repeatable on every run, inside the existing gates.
  - con: a sample project may miss what a real one does (its own conftest, its
    own plugins, its environment).
- Option H2: a temporary trial in one consuming project's environment,
  covering both activation contexts (a plain `pytest` run from its prepared
  shell and a groundhog stage), changing none of its files, enabling the
  plugins nowhere persistently, and recorded without naming the project.
  - pro: real-world evidence of the documented route.
  - con: one-off; not repeated when the plugins change.
  - con: a command-line trial in one context alone would not show both
    activation contexts.
- Option H3: both.
  - pro: repeatable coverage plus one real-world confirmation.
  - con: two kinds of evidence to keep in the validation plan.

#### Recommended option for Q08 (with arguments for this choice)

Option H3: the in-process tests keep the import-name and dependency rules
checked on every change, and one real trial shows the documented route works
in a project llm-shared does not control. The trial is temporary validation,
not adoption: it changes no file there, enables nothing persistently and names
no project, so it fits the public-repository rule and the out-of-scope line on
persistent adoption. Where it fits, the Python 3.12 evidence of Q02 and this
evidence can share a run.

#### Answer to Q08: option H3 (with reason why it must be accepted as the answer)

Option H3: neither kind of evidence is enough alone, and together they cost
little. Acceptance then combines repeatable isolated-project evidence with a
temporary trial in a consuming environment that covers both activation
contexts, changes none of that project's files and enables the plugins
nowhere persistently; the validation plan records the trial without naming
the project.

User decision: confirmed — option H3.

Decision date: 2026-11-04.

Require both repeatable in-process isolation tests in llm-shared's suite and
a temporary trial in one real consuming environment. The trial covers a
plain pytest run in the prepared shell and a groundhog test stage, changes
none of the consuming project's files, enables nothing persistently and is
recorded without naming the project.

Historical qualification, superseded on 2026-11-05:

> Acceptance evidence targeted Python 3.13 on Windows under Q02 B3 and
> Q03 C3; the recommendation's Python 3.12 evidence reference did not apply.

Compatibility amendment dated 2026-11-05: Q02 now requires Python 3.12
runtime compatibility as well as Python 3.13 validation. The Windows-only
validation scope from C3 remains. Suitable Python 3.12 evidence and the
temporary consuming-environment trial may share a run; the trial still
covers both prepared-shell pytest and groundhog, without changing consumer
files, persistent enablement or public naming.

### Q09: The stability promise to opted-in projects

Question description: a consuming project loads the plugins from a live
llm-shared checkout, so an llm-shared update changes the gate in every
opted-in project at once: a new default, a renamed key or a new record schema
would reach them all. The requirement fixes today's contract for this
version, but not what later changes may do, nor whether a record written
before the move (llm-shared's own included) keeps its proofs.

#### BBQ for Q09

A spice blend is supplied to many restaurants from one shared jar that the
supplier refills. If the supplier changes the recipe, every restaurant's dish
changes the next day. The supplier can promise to announce changes and keep
old labels readable, promise nothing, or let each restaurant keep its own
jar. In this picture: the shared jar is the live llm-shared checkout, the
recipe is the ini keys, defaults and record schema, the old labels are
records written by earlier versions, and a restaurant's own jar is a pinned
plugin version per project.

#### Options for Q09

- Option I1: bounded compatibility: for this extraction, existing valid
  records stay readable, exceptions keep their meaning, and proofs stay
  eligible under the unchanged current-ceiling rules; a later change of the
  ini keys, defaults or record schema is documented with its compatibility or
  migration behaviour.
  - pro: no proof is lost by the move, and later changes come with their
    migration path.
  - con: every later contract change carries a documentation and migration
    cost.
- Option I2: no promise: like other llm-shared tools, the live checkout is the
  contract.
  - pro: no extra work.
  - con: an update can fail or reset every opted-in project at once.
- Option I3: each project pins a plugin version.
  - pro: projects upgrade when they choose.
  - con: version management that llm-shared does not have for any other tool;
    it is a design and upgrade-policy alternative, not the current packaging
    model.

#### Recommended option for Q09 (with arguments for this choice)

Option I1: the gate fails tests, so an undocumented change of its contract
breaks other projects' work. Bounded to this extraction, readable records and
documented later changes are the smallest promise that protects them, without
promising every future schema forever or that a proof survives a changed
ceiling (the current-ceiling rule already withdraws such proofs). The record
already reads entries without `proven_cpu` from before that field existed, so
this is the existing practice written down. A changelog line alone could not
prevent surprises; a documented compatibility or migration behaviour can.

#### Answer to Q09: option I1 (with reason why it must be accepted as the answer)

Option I1: for this extraction, existing valid records remain readable,
exceptions keep their meaning, and proofs remain eligible under the unchanged
current-ceiling rules; later contract changes are documented with their
compatibility or migration behaviour. It adds a criterion that llm-shared's
existing record keeps its proofs across the move.

User decision: confirmed — option I1.

Decision date: 2026-11-04.

For this extraction, existing valid records remain readable, accepted CPU
exceptions retain their meaning and proofs remain eligible under the
unchanged current-ceiling rules. Validate that llm-shared's existing record
retains eligible proofs across the move. Later changes to configuration
keys, defaults or the record schema must document their compatibility or
migration behavior. This does not promise indefinite support for every
schema or preserve a proof earned above a newly lowered ceiling.

### Q10: The defaults a consuming project gets

Question description: the plugin defaults are llm-shared's own strict values:
0.1 s CPU, 1 s wall, a 2.5x band and 3 drift runs. llm-shared also sets three
of them explicitly in its `pyproject.toml`. The requirement keeps the defaults
unchanged, without saying whether a consuming project should get the same
strict values by default or must choose its own.

#### BBQ for Q10

A new grill ships with a preset cooking time. The maker can preset its own
chef's tight timing, preset a relaxed one, or ship without a preset so each
cook must set one before the first use. In this picture: the preset is the
plugin default of each `test_lifecycle_*` key, the chef's tight timing is
llm-shared's 0.1 s and 1 s, and each cook is a consuming project.

#### Options for Q10

- Option J1: the same defaults as today; a project overrides them in its
  configuration.
  - pro: matches `write-fast-python-tests.md`, which already says 0.1 and one
    second by default.
  - pro: one set of numbers across llm-shared and every project.
  - con: strict from the first run for a project that sets nothing.
- Option J2: looser plugin defaults; llm-shared keeps 0.1 s by setting it
  explicitly.
  - pro: gentler first runs.
  - con: the shared instruction and the plugin would disagree by default.
- Option J3: no defaults: each project must set every key, or the run stops
  with a usage error.
  - pro: every project's numbers are deliberate and visible.
  - con: more ceremony to opt in; four lines before anything works.

#### Recommended option for Q10 (with arguments for this choice)

Option J1: the shared instruction already states those numbers as the default
budget, and Q07's recommended answer gives a project a visible way to loosen
the ceiling while it converts. One set of defaults keeps the instruction, the
plugin and the documentation consistent.

#### Answer to Q10: option J1 (with reason why it must be accepted as the answer)

Option J1: it keeps the defaults consistent with the instruction every
project's agent already follows, and per-project overrides remain available
with the existing precedence. The requirement already states unchanged
defaults; the answer confirms them for consuming projects. If the user selects
J2 or J3 instead, its conflict with the unchanged-contract baseline of gap
item 6 is reported before consolidation.

User decision: confirmed — option J1.

Decision date: 2026-11-04.

Keep the existing plugin defaults for consuming projects: 0.1 seconds CPU,
1 second wall time, a CPU band factor of 2.5 and 3 consecutive measured
over-ceiling runs before withdrawing proof. All four settings remain
configurable under Q07 G1: command-line `-o` overrides project pytest
configuration, which overrides plugin defaults. Opting in with no overrides
enforces these defaults immediately.

### Q11: A prepared run that cannot import a selected plugin

Question description: added after the round 1 review. When a project has
opted in to one or both plugins, a run that is meant to load them (under Q01's
recommended answer, a run from the project's prepared shell or a groundhog
stage) may find a selected plugin missing: llm-shared moved, its environment is
broken, or the import route is misconfigured. The requirement does not say what
that run does. Under proposed option A2 of Q01, runs outside the prepared
environment are not concerned: they get no automatic activation. This is an
observable product behaviour; the
injection and packaging mechanisms stay design work.

#### BBQ for Q11

The club's cookout rule says every grill carries a thermometer, and on cookout
day one thermometer is missing from the kit. The cook can refuse to light that
grill until a thermometer is found, light it anyway and mention the missing
thermometer, or use the smoke alarm that did arrive and say only half the kit
came. In this picture: the cookout is a run llm-shared prepares for an
opted-in project, the missing thermometer is a selected plugin that cannot be
imported, refusing to light is failing at startup, lighting anyway is a
warning and a run without the plugin, and using only the smoke alarm is
running with the remaining plugin and reporting partial enforcement.

#### Options for Q11

- Option K1: the run fails at startup, naming the plugin that cannot be
  imported and the opt-in that selected it.
  - pro: the enforcement an opted-in project asked for never silently
    disappears.
  - pro: the failure names what to repair.
  - con: testing in that environment is blocked until the setup is repaired.
- Option K2: the run warns and continues with neither selected policy
  enforced.
  - pro: testing stays available.
  - con: the budget disappears, and a warning in a long log is easy to miss.
- Option K3: when both plugins were selected, the run continues with the
  available one and reports partial enforcement; when only one plugin was
  selected, this outcome coincides with K2.
  - pro: keeps whatever checks can still run.
  - con: the same opt-in means different checks from one run to the next.

#### Recommended option for Q11 (with arguments for this choice)

Option K1: a project opts in to have its budget enforced, and the prepared
environment is exactly where that enforcement was promised; dropping it
silently (K2) or partly (K3) would make a green run mean less than the project
believes. The cost is bounded: only prepared runs of opted-in projects can
fail this way, and, under proposed option A2, environments outside the
prepared scope stay unaffected.

#### Answer to Q11: option K1 (with reason why it must be accepted as the answer)

Option K1: it keeps an opt-in meaning the same thing in every prepared run and
turns a broken setup into a named, repairable failure instead of a quietly
weaker run. The requirement then adds this failure rule for prepared runs of
opted-in projects, and an acceptance criterion for it.

User decision: confirmed — option K1.

Decision date: 2026-11-04.

An opted-in project's prepared-shell pytest run or groundhog test stage must
fail at startup if a selected plugin cannot be imported. The diagnostic names
the unavailable plugin and the opt-in that selected it. Do not continue with
missing or partial selected enforcement. Under Q01 A2, runs outside the
prepared environment receive no automatic activation; explicit plugin loading
there remains possible.

Review clarification dated 2026-11-05: Q11's references above to Q01's
recommended or proposed A2 describe the earlier review text. A2 was
confirmed on 2026-11-04 and governs the prepared-environment boundary.

Review consequence pending consolidation (round 3, 2026-11-05): K1's
acceptance criterion must make startup failure observable: before any test
runs, with a non-zero exit and the plugin and selecting opt-in named.
Historical reviewer proposal: use usage-error exit code 4, consistent with
invalid lifecycle settings. The user explicitly confirmed this K1
qualification on 2026-11-05.

User-confirmed qualification dated 2026-11-05: in K1's prepared opted-in
scope, failure to import a selected plugin must stop the run before tests
execute, with usage-error exit code 4 and a message naming the plugin and
selecting opt-in. Repeatable in-process tests must exercise this path as
well as successful activation, alongside H3's real-environment evidence.

Exit code 4 therefore applies to invalid settings, a selected plugin that
cannot import within K1's scope, invalid exemption declarations under M1
and interpreters below Q15's amended Python 3.12 minimum. K1's code was
confirmed separately, not inferred from Q13 or Q15.

### Q12: What an exemption covers when shared fixtures start processes

Question description: added after the round 3 review of the recorded
decisions. Q04's D1 charges shared-fixture work to the test whose lifecycle
is running. pytest sets up a module- or session-scoped fixture inside the
setup of the first test that requests it, and tears it down inside the
teardown of the last test before its scope ends (for a session fixture, the
last test of the process). Q05's E2 exempts single tests. If an exemption
follows D1's attribution, a shared fixture that starts a process passes when
an exempt test reaches it first, and errors when a test without exemption
does; pytest then reports that cached setup error for every test using the
fixture, the exempt one included. Under pytest-xdist each worker sets the
fixture up separately, so the result also changes with the distribution.
Shared teardown work is order dependent in the same way: it runs in
whichever test ends the fixture's scope, and a failure there is reported
on that test's teardown only. The requirement does not say which process
starts an exemption covers. Whatever the answer, the CPU clock
(`time.process_time`) counts only the test process: a child process's CPU is
outside every test's CPU budget. The wall limit bounds the elapsed time
spent waiting within the test lifecycle, not a detached child's lifetime.

#### BBQ for Q12

The patio's no-flame rule has one signed note for the family's old fire pit.
Lighting the pit also lights the shared patio heater. If the note covers
anything that happens while the pit is in use, the heater passes on the days
the pit is lit first, and breaks the rule on the days a guest switches the
heater on earlier. The family can tie the note strictly to the pit, accept
that the heater's verdict depends on who arrives first, or sign a second
note for the heater itself. In this picture: the patio rule is the process
audit, the signed note is a test's exemption marker, the fire pit is the
exempt test's own work, the patio heater is a module- or session-scoped
fixture that starts a process, who arrives first is the test order or the
xdist distribution, and the second note is a fixture-level exemption.

#### Options for Q12

- Option L1: an exemption covers only the exempt test's own work: its call
  and the setup and teardown of the function-scoped fixtures it requests.
  Work of a broader-scoped fixture is never exempt, whichever test triggers
  it.
  - pro: deterministic: the same suite gives the same audit result in every
    order and distribution.
  - pro: keeps E2 a strictly per-test exemption.
  - con: a project that starts a process in a shared fixture (for example a
    server started once per session) must move that start into the exempt
    test or a function-scoped fixture, paying it per test, or take the gate
    without the audit.
- Option L2: an exemption covers everything D1 charges to the exempt test's
  lifecycle, shared-fixture setup and teardown included.
  - pro: the simplest rule; it follows D1's attribution exactly.
  - con: the same commit can pass or fail the audit depending on test order
    and xdist distribution.
  - con: shared work a test without exemption depends on can pass only
    because an exempt test happened to trigger it.
- Option L3: L1, plus a fixture-level exemption marker with its own required
  reason, also listed at the end of every run; an exempt shared fixture may
  start processes whichever test triggers it.
  - pro: deterministic, and supports process-starting shared fixtures.
  - con: a second exemption form beyond E2's per-test marker, with its own
    contract and tests.
  - con: one fixture exemption covers every test using that fixture.

#### Recommended option for Q12 (with arguments for this choice)

Option L1: an audit whose result changes with test order cannot be trusted
when it fails, which rules out L2. L1 is the reading of E2 that keeps the
exemption per test, and its cost falls only on projects that start processes
in shared fixtures, which can still take the gate alone. L3 extends E2 to a
second exemption form; it can be decided later if a real project needs it.

#### Answer to Q12: option L1 (with reason why it must be accepted as the answer)

Option L1: the requirement then states that an exemption covers the exempt
test's call and its function-scoped fixtures, that a process started by a
module-, class-, package- or session-scoped fixture stays audited, and
fails the lifecycle carrying it even if that test is exempt. A child
process's CPU is not measured, while the lifecycle wall limit still
applies. How the plugin tells shared-fixture work apart stays design work.

User decision: confirmed: option L3.

Decision date: 2026-11-05.

The user selected L3 after the Q12 explanation. Preserve the historical L1
recommendation above. A test exemption covers its call and function-scoped
fixture work. Add a separate fixture-level process-audit exemption with its
own required reason and end-of-run reporting. An exempt shared fixture may
start processes whichever test triggers it; that permission covers the
fixture's own work and does not exempt its consuming tests' own work.
CPU and wall enforcement remain unchanged. The declaration mechanism stays
design work; Q13 and Q14 must account for this additional exemption form.

Review clarification dated 2026-11-05 (round 5): L3's historical con,
"one fixture exemption covers every test using that fixture", refers to
the fixture's own work whenever it is exercised, not to consuming tests'
own work. The confirmed L3 boundary is unchanged.

Review consequences pending consolidation (round 5, 2026-11-05), proposed
by the reviewer and accepted by the writer for consistency review:

- A fixture permission covers its own setup and teardown, including its
  finalizers. It does not cover fixtures it requests, consuming test work
  or a process started later by a thread or pool it left running; a later
  start belongs to the lifecycle running then under D1.
- If an exempt function-scoped fixture belongs to an exempt test, credit
  process creation within the fixture to the fixture permission only.
  Q14 N2 may therefore report the test's permission as unused.
- No timing exception is granted. Process-start and wait wall time counts
  toward the lifecycle carrying the fixture's setup or teardown. A slow
  shared start can therefore affect a different test's wall verdict when
  order or worker distribution changes, as with any shared fixture.
  Document this in the opt-in how-to; G1's configurable wall limit remains
  available.

### Q13: What makes an exemption marker valid

Question description: added after the round 3 review. E2 asks for a per-test
marker with a required reason. pytest marks also apply to a whole class or
module (`pytestmark`) and to one parametrized case
(`pytest.param(..., marks=...)`), and a class or module mark reaches every
test inside it, including tests added later. That is the coarseness for
which E3 (path patterns) was not chosen. The requirement does not say where
the marker may be placed, or what a missing or empty reason does.
Separately, a marker known only to the audit plugin is unknown wherever that
plugin is not loaded: in a run that takes the gate alone, and, under Q01's
A2, in every run outside the prepared environment. With `--strict-markers`
such a run fails collection; without it, pytest warns about an unknown mark,
which a warnings-as-errors setting turns into a failure. A2 promises that
those environments keep working, so in every option below the documented
opt-in has the project register the marker in its tracked pytest `markers`
setting, and the marker has no effect where the audit plugin is not loaded.

Decision dependency dated 2026-11-05: confirmed Q12 L3 adds a separate
fixture-level exemption with its own required reason. In all options below,
this explicit fixture permission remains available; class- or module-level
placement refers to blanket test exemptions, not to permission attached to a
particular fixture. Fixture permission covers that fixture's work only.
If M1 is chosen, invalid fixture declarations or missing reasons also stop
the run before tests with an identifying usage error. If M3 is chosen, they
warn and grant no fixture exemption. The supported fixture declaration
mechanism remains design work; ordinary pytest marks on fixtures must not
be assumed to provide this behavior. The validation choices below require
a separate Q13 decision; L3 alone does not select one.

#### BBQ for Q13

The signed fire-pit note can be pinned to the pit itself, to the backyard, or
to the whole house. A note on the house also covers every pit built later,
without anyone signing again. A note whose reason is left blank can be
refused, or the pit can be lit anyway with a grumble. Guests who do not
follow the patio rule must still be able to read the note without being
confused by it. In this picture: the pit is one test function or
parametrized case, the backyard is a test class, the house is a test module,
a later pit is a test added to that class or module, the blank reason is a
marker without a non-empty reason, the grumble is a warning, and the guests
are runs where the audit plugin is not loaded.

#### Options for Q13

- Option M1: the marker counts only on a test function or one parametrized
  case; a class- or module-level exemption mark, or a marker without a
  non-empty reason, stops the run at collection with a usage error naming
  the test (exit code 4, with or without pytest-xdist).
  - pro: every exemption names one test and its reason; no test becomes
    exempt by being added to a file.
  - pro: a misplaced or unexplained exemption is caught before any test runs,
    pointing at the line to fix.
  - con: a module with several process-starting tests repeats the marker on
    each.
- Option M2: the marker counts wherever pytest marks apply, class and module
  included; a missing or empty reason stops the run at collection.
  - pro: familiar pytest behaviour; one line exempts a whole end-to-end
    module.
  - con: brings back E3's coarseness: a new test in an exempted module is
    exempt without review.
- Option M3: placement as in M1, but a class- or module-level mark or a
  missing reason only warns, and the test stays audited.
  - pro: does not deliberately reject the marker at collection; normal
    warning filters still apply.
  - con: the mistake shows up later as an audit failure, after a warning that
    is easy to miss.

#### Recommended option for Q13 (with arguments for this choice)

Option M1: E2 was chosen over E3 as a reviewed escape for a named test. M1
keeps that property, and a collection-time usage error, like the existing
one for invalid `test_lifecycle_*` values, names the line to fix. The
repetition it costs is the visible review the exemption is meant to carry.

#### Answer to Q13: option M1 (with reason why it must be accepted as the answer)

Option M1: the requirement then states that the exemption marker counts only
on a test function or a parametrized case, that a class- or module-level
exemption mark or a missing or empty reason stops the run at collection with
a usage error naming the test (exit code 4, with or without pytest-xdist),
that the opt-in how-to has the project
register the marker in its tracked pytest `markers` setting, and that the
marker has no effect in runs without the audit plugin.

User decision: confirmed: option M1, including the L3 fixture exemptions.

Decision date: 2026-11-05.

The user selected M1 after the explanation adapted to confirmed Q12 L3.
Allow a process exemption on a named test function or parametrized case,
and a separate explicitly identified fixture exemption. Reject blanket
class- or module-level test exemptions, invalid fixture declarations and
missing or empty reasons before tests run, with a usage error identifying
the offending declaration and exit code 4, with or without pytest-xdist.
Document project registration of the test marker for strict-marker runs
without the audit plugin. A fixture exemption covers its own work only;
the supported declaration mechanism remains design work. This decision
did not itself confirm K1's startup-import-failure exit code; the user
separately confirmed exit code 4 in Q11 on 2026-11-05.

Review consequence pending consolidation (round 5, 2026-11-05): under A2,
L3 and M1, the fixture declaration must preserve collection and execution
when audit is absent, including gate-only runs and environments where
llm-shared is not importable. It requires no llm-shared import from consumer
test or conftest files and introduces no pytest configuration key reported
as unknown without the plugin. This applies under strict markers, strict
configuration, pytest's strict setting and warnings-as-errors. pytest 9.1
rejects marks applied to fixtures, so the test marker cannot simply be
reused. The supported declaration mechanism remains design work.

### Q14: What the end-of-run exemption list reports

Question description: added after the round 3 review. E2 lists exemptions at
the end of every run. The requirement does not say which tests appear (every
collected exempt test, or only those that ran), what each line shows,
whether a run without the audit plugin shows a list, or what happens to an
exemption whose test no longer starts a process. That last case is how E2's
own con, an escape that weakens over time, would show: a test is converted,
its exemption stays, and nothing says so. Under pytest-xdist, as for the
lifecycle record, only the controller sees the whole run.

Decision dependency dated 2026-11-05: confirmed Q12 L3 also requires
fixture exemptions to appear with their own reasons. All options below
therefore apply to both exempt tests that ran and exempt fixtures whose
work ran, identifying the two kinds separately. A shared fixture's process
creation belongs to its own exemption, not to each consuming test's
permission. Under N2, use or non-use is evaluated within each exempt
scope's own work; under N3, an unused fixture exemption would also make
the run fail. A fixture not exercised by the selected tests is not an
unused executed exemption. These reporting choices were not inferred from
L3 or M1; the explicit Q14 decision is recorded below. Worker aggregation and fixture
identity mechanics remain design work.

#### BBQ for Q14

At the end of each cookout, the host reads out the signed fire-pit notes.
The host can read every note on file or only the notes for pits used that
day, can also say which of those pits stayed cold, or can tear up the note
of a pit that stayed cold. In this picture: the cookout is one pytest run
with the audit plugin loaded, the notes on file are exemption markers, the
pits used that day are exempt tests that ran, a pit that stayed cold is an
exempt test that started no process in this run, and tearing up the note is
failing that test.

#### Options for Q14

- Option N1: one end-of-run list, written once by the controller under
  xdist, of the exempt tests that ran, each with its reason; shown only when
  the audit plugin is loaded.
  - pro: short and stable; the minimum E2 asks for.
  - con: an exemption that is no longer needed goes unnoticed.
- Option N2: N1, and each line says whether that test started a process in
  this run; an unused exemption is flagged, never failed.
  - pro: makes the weakening visible and points at exemptions to remove.
  - con: a test that starts a process only on some platforms or inputs is
    flagged on the runs where it did not; worker reports carry one more fact.
- Option N3: N1, and an exempt test that starts no process fails, like a
  strict expected failure.
  - pro: no stale exemption survives.
  - con: a test that starts a process only sometimes fails on the other runs.

#### Recommended option for Q14 (with arguments for this choice)

Option N2: it answers E2's main risk without adding a failure mode. N1
leaves stale exemptions invisible, and N3 turns a conditional process start
into a failing test. Listing only tests that ran keeps the list true for
selected runs, and the controller-only write matches the record rule.

#### Answer to Q14: option N2 (with reason why it must be accepted as the answer)

Option N2: the requirement then states that a run with the audit plugin
ends with one list of the exempt tests that ran, each with its reason and
whether it started a process in that run, written once by the controller
under pytest-xdist; that an unused exemption is flagged and never fails; and
that a run without the audit plugin shows no exemption list.

User decision: confirmed: option N2, including L3 fixture exemptions.

Decision dated 2026-11-05: the user explicitly clarified N2. With the audit
plugin loaded, report exercised exempt tests and fixtures separately, each
with its own identity, reason and whether its permission was used to start
a process in its own scope. Attribute fixture process starts to the fixture's
permission, not to consuming tests. Flag unused exercised permissions without
failing the run; exclude fixtures whose work did not run. Under pytest-xdist,
the controller writes one combined summary. Runs without the audit plugin
show no exemption summary. CPU and wall-time enforcement remain unchanged.

Review consequence pending consolidation (round 5, 2026-11-05): report
each exercised fixture permission once per run, even if its fixture runs
several times across modules, classes or xdist workers. Report it as used
if any exercised instance on any worker started a process in that
fixture's own work. Credit such starts to the exempt fixture rather than a
consuming test permission, including when that fixture is function-scoped.
A start in a function-scoped fixture without its own exemption stays covered
by, and credited to, the exempt test's permission, as L3 states. This
is a proposed reporting precision for independent review, not a new
user decision.

### Q15: What the minimum Python requirement does on an older interpreter

Question description: added after the round 3 review. Q02's B3 says the
plugins require Python 3.13 and removes the 3.12 promise and its
validation. It does not say whether "require" is a documented support floor
or a check at load time. The difference is observable: one consuming project
runs Python 3.12. If it declared the opt-in, its prepared runs would, without
a check, load plugins whose behaviour on 3.12 is unvalidated, or fail at
import with an unrelated error that Q11's K1 diagnostic would report; with a
check, they would stop at startup with a message naming the required
version. A check tested on 3.13 by simulating an older version is not 3.12
validation, so both readings fit B3.

Compatibility amendment dated 2026-11-05: the description and options
below preserve the earlier Python 3.13 floor for review history. The user
has now required Python 3.12 compatibility under Q02. Apply the selected
O2 load-time check to interpreters below 3.12, never to supported 3.12
runs. Simulating an unsupported version tests the refusal path; it does
not replace executable compatibility evidence on Python 3.12.

#### BBQ for Q15

A new grill says "for gas bottles made from 2024 on". The label can be
advice only, so an older bottle may fit and may leak, or the valve can
refuse older bottles with a tag saying why. In this picture: the grill is
the plugin pair, a 2024 bottle is Python 3.13, an older bottle is Python
3.12, advice only is a documented support floor without a check, and the
refusing valve is a load-time version check that stops the run with a
message.

#### Options for Q15

- Option O1: a documented floor only: the plugins support Python 3.13 and
  later; on an older interpreter their behaviour is unspecified and nothing
  checks the version.
  - pro: no code and no test; the lightest reading of B3.
  - con: an opted-in project on 3.12 may get unvalidated enforcement that
    looks valid, or an import error that does not name the cause.
- Option O2: a load-time check: on Python older than 3.13, loading either
  plugin stops pytest at startup with a usage error naming the plugin and
  the required version.
  - pro: the same principle as K1: no quiet, unvalidated enforcement, and
    the message says what to change.
  - pro: tested in llm-shared's own suite on 3.13 by simulating the version,
    with no second interpreter.
  - con: a little code and one test for a version the user does not
    prioritize; a 3.12 project that would have worked is stopped.

#### Recommended option for Q15 (with arguments for this choice)

Option O2: the user chose K1 so that a prepared run never carries less
enforcement than the opt-in promises without saying so; O2 applies the same
rule to an unsupported interpreter for the cost of one check and one test.
O1 is acceptable if the user prefers no code at all for Python 3.12.

#### Answer to Q15: option O2 (with reason why it must be accepted as the answer)

Option O2: the requirement then states that loading either plugin on Python
older than 3.13 stops pytest at startup with a usage error naming the plugin
and the required version, and gap item 5 says Python 3.13 and later.

The preceding proposed answer uses the historical 3.13 floor; the following
explicit decision and compatibility amendment supersede that threshold.

User decision: confirmed: option O2, amended to the Python 3.12 minimum.

Decision dated 2026-11-05: the user selected O2, then explicitly required
Python 3.12 compatibility if a consuming project needs it. That condition
currently applies under Q02. Loading either plugin below Python 3.12 must
stop pytest before tests run, with a usage error naming the plugin and
required version. Python 3.12 must be accepted and validated at runtime;
Python 3.13 remains supported and validated. The check also applies to
explicit plugin loading outside the prepared-shell automatic activation
scope; runs loading neither plugin are unaffected. Test the refusal path
by simulating an interpreter below the supported minimum. This decision
did not itself confirm K1's import-failure exit code; the user separately
confirmed exit code 4 in Q11 on 2026-11-05.

Review consequence pending consolidation (round 5, 2026-11-05): O2's
refusal must run before any code an older interpreter cannot parse or
import. pytest 9.1 also runs on Python 3.10 and 3.11. Simulating a version
on 3.13 tests the refusal logic but cannot detect syntax or imports that
would fail first on a real older interpreter. Require a repeatable check
that code reached before the version check is valid for Python 3.10,
without adding a Python 3.10 runtime-support promise. The check mechanism
is design work. This is a review consequence, not an additional user
choice.

### Q16: When the Python 3.12 evidence runs

Question description: added after the round 5 review of the recorded
decisions. Q02 now requires executable Python 3.12 evidence for
acceptance, alongside Python 3.13 validation. It does not say whether that
evidence runs once, for this release's acceptance, or again whenever the
plugins change. The difference shows after acceptance. A consuming project
loads the plugins from the live llm-shared checkout (Q09), so a later
plugin change reaches its next prepared run at once. llm-shared's own
static checks treat everything under `tools/` as Python 3.13 code: Ruff
takes its target from `requires-python = ">=3.13, <3.14"`, and Pyright sets
`pythonVersion = "3.13"`. Neither would flag Python 3.13-only syntax or APIs
added to a plugin later. On a consuming project's Python 3.12, that plugin
could fail to import or fail while running; an import failure stops every
prepared run under K1 until llm-shared is fixed. llm-shared's tests may
not start processes, so a repeated 3.12 run is a separate validation step.

#### BBQ for Q16

The sauce from Q02 must suit the guest who cannot eat garlic. The cook
tasted it on plain bread once, when the recipe was written. Later cooks
adjust the recipe and taste it only with garlic bread. The kitchen can rely
on that first tasting, check each new recipe card for garlic, or taste it
on plain bread again after every change. In this picture: the first
tasting is the one-off Python 3.12 acceptance evidence, a later adjustment
is a later plugin change, the garlic bread is llm-shared's Python 3.13
validation, checking the card is a static check set to Python 3.12, and
tasting again is a repeated Python 3.12 run of the plugins' own tests.

#### Options for Q16

- Option P1: once: the executable Python 3.12 evidence belongs to this
  release's acceptance only, and may share H3's temporary trial; later
  changes are validated on Python 3.13 only.
  - pro: no second interpreter in routine validation.
  - con: a later change can break Python 3.12 without any check noticing;
    the first sign may be a consuming project's prepared runs stopping
    under K1.
- Option P2: executable evidence once at acceptance, plus static checks of
  the plugin modules set to Python 3.12 in every llm-shared check.
  - pro: cheap, runs on every change, and catches syntax or standard-library
    APIs newer than Python 3.12.
  - con: cannot demonstrate import-time, pytest-hook or runtime behavior on
    3.12, which Q02 says static checks alone cannot demonstrate.
- Option P3: P2's static checks, and the plugins' own Python 3.12 tests run
  again in llm-shared's regular whole-suite validation.
  - pro: keeps demonstrating the Python 3.12 promise, reusing the harness
    acceptance already requires.
  - con: a second interpreter and test environment in routine validation,
    run as a separate step outside the process-free suite; every machine
    that runs the whole-suite validation must be able to provide Python
    3.12.

#### Recommended option for Q16 (with arguments for this choice)

Option P3: Python 3.12 support is required because a current consuming
project needs it, and Q02 already rejects static evidence alone. Once
acceptance has built a Python 3.12 harness independent of llm-shared's
3.13-only helpers, running it again costs one separate step. P1 and P2 can
let the promise lapse unnoticed until a consuming project's runs stop.
P2 is the fallback if a second interpreter in routine validation is not
acceptable.

#### Answer to Q16: option P3 (with reason why it must be accepted as the answer)

Option P3: Q02's executable Python 3.12 evidence becomes a repeated part
of llm-shared's whole-suite validation rather than a one-off acceptance
run, and the plugin modules are also checked statically against Python
3.12. How the step is launched and what provides the Python 3.12
interpreter remain design work.
A whole-suite validation that cannot provide Python 3.12 fails rather
than skipping that step.

User decision: confirmed: option P3.

Decision dated 2026-11-05: the user selected P3. Regular whole-suite
validation includes both static checks targeting Python 3.12 for the plugin
modules and executable plugin tests under Python 3.12, alongside Python
3.13 validation. The Python 3.12 run is a separate step outside llm-shared's
process-free suite and uses a harness independent of its Python 3.13-only
helpers. Every machine running whole-suite validation must provide Python
3.12; otherwise validation fails rather than skipping the step. This keeps
the required compatibility checked after later plugin changes. The launch
mechanism and interpreter provision remain design work. This decision does
not authorize consolidation.

Review clarification dated 2026-11-05 (round 7): the Python 3.12 step
belongs to llm-shared's own whole-suite validation, as option P3
states. It adds no Python 3.12 requirement to a consuming project's
validation, including a groundhog run of that project's own suite.
