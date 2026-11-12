# Specification review transcript for v0.14.0

- Exchange: specification/design-specification/v0.14.0/shared_lifecycle_gate
- Reviewed document: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-11-05T20:10:02+01:00
- Exchange: specification/design-specification/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for design-specification shared_lifecycle_gate (round 1)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
Review round: 1

### Requestor assessment for design-specification shared_lifecycle_gate (round 1)

The design translates the consolidated requirement without reopening its sixteen decisions. Python 3.12 and later, real recurring 3.12 execution alongside 3.13, Windows validation, K1 exit code 4, independent plugins, unchanged timing/records and process-free llm-shared tests are preserved.

Seven questions cover import/loading, selection/root binding, inert fixture declarations, fixture ownership instrumentation, the xdist validation barrier, interpreter provisioning and direct-full compatibility evidence. Each includes two alternatives with pros/cons, a recommendation, a proposed answer and an explicit pending user decision. No recommendation is recorded as a user choice. The options are sufficient for writer review; independent review must assess feasibility and identify any missing design questions.

Source inspection confirmed the combined plugin, record dependency, existing coverage boundary, project environment and groundhog spawn seams. Direct full validation does not execute check.bat today; the design therefore identifies a separate own-project preflight proposal rather than claiming that existing path already supplies compatibility evidence.

The design stays at interface, ownership, state and validation architecture level. There are no file-by-file implementation steps or rollout checklist. Markdown validation passed with zero issues. This is the first design review, so no reviewer wording suggestions have yet been applied.

### Change summary for design-specification shared_lifecycle_gate (round 1)

Initial v0.14.0 shared lifecycle gate design, derived from the consolidated requirement. Added architecture, canonical standalone import identities, prepared activation, strict startup behavior, record continuity, permission declaration/ownership/reporting, compatibility validation and acceptance cases. Added seven pending design questions through oqm. Requirement and implementation source remain unchanged.

### Writer response for design-specification shared_lifecycle_gate (round 1)

Writer response:

Please assess the entire design against the consolidated requirement and current source, including questions that may be missing. In particular, examine early loader ordering and import-failure translation, duplicate registration, project-bound environment refresh, fixture-object declarations under strict pytest without audit, nested fixture/finalizer ownership, thread permission expiry, xdist's pre-execution validation barrier and exit code 4, standalone modules with no shared-helper runtime imports, record compatibility, and recurring Python 3.12 evidence for day and direct full validation without adding a consumer prerequisite. All seven answers are proposals awaiting explicit human decisions. Do not reopen confirmed requirement choices.

### Reviewer focus for design-specification shared_lifecycle_gate (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `claude`

Completed artifacts:

- `.reviews/a.review-active.specification.design-specification.v0.14.0.shared_lifecycle_gate.md`
- `.reviews/a.review-requested.design-specification.v0.14.0.shared_lifecycle_gate.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-11-05T20:23:06+01:00
- Exchange: specification/design-specification/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification shared_lifecycle_gate round 1

I read the complete design (SHA-256
`36c92b006f739b19ba27c055134067bc20937fd6abc208bcbb94eeb7518de3ba`), the
consolidated requirement and the round 1 request. I checked the design's
pytest, xdist, coverage and tooling assumptions against the installed
pytest 9.1.0, pytest-xdist 3.8.0, pytest-cov 7.1.0 and Ruff 0.15.13, and
against `check.bat`, `senv.bat`, `tests/simulation_policy.py` and
`tests/conftest.py`.

**The design follows the consolidated requirement.** It keeps the sixteen
decisions without reopening them: independent policies under unique
top-level names, prepared activation only, unchanged settings, records and
timing, the test and fixture permission boundaries, own-scope reporting,
the Python 3.12 minimum with a 3.10-readable entry path, and recurring 3.12
evidence limited to llm-shared's own validation. The seven questions are
real design choices with distinct options. The fixture dictionary works as
described: in pytest 9.1 a decorated fixture is a hashable
`FixtureFunctionDefinition`, usable as a dictionary key, including with
`@pytest.fixture(name=...)`. The wall measurement matches today's sum of
report durations.

**K1's exit code cannot hold when the loader itself is missing (new
question).** Every selected policy is imported through
`llm_shared_pytest_loader`, injected as `-p llm_shared_pytest_loader`. The
likeliest K1 cause, an llm-shared checkout that moved or broke, removes the
loader too. pytest 9.1's `import_plugin` then raises its own `ImportError`,
which `main()` does not catch: the run stops before tests, as K1 wants, but
with exit code 1, a traceback and no mention of the selection. Preparation
can check the directory when the shell is prepared and before each
groundhog stage spawns pytest. A plain `pytest` in a shell prepared before
the checkout moved still reaches pytest's own error. That narrows a
confirmed requirement decision, so it needs the user's explicit choice
(proposed Q08).

The design's claim that the loader is "the first injected `-p` option",
ahead of "later explicit `-p` options", is also inexact. pytest prepends
`PYTEST_ADDOPTS` to the command line and then prepends the tracked
`addopts` before both. A policy named with `-p` in tracked `addopts` is
therefore imported before the loader, and its import failure is pytest's
own. The how-to should say never to name the policies in tracked
`addopts`, which A2 already implies.

**Tracked lifecycle settings break runs without the gate (new
question).** G1 allows the four `test_lifecycle_*` keys in a project's
pytest configuration. When collection starts, pytest 9.1 reports every key
that no loaded plugin registered as `Unknown config option`. That happens
in every run outside the prepared environment and in audit-only
selections:

- a warning in each such run;
- an error under warnings-as-errors;
- a usage error under `--strict-config` or pytest's `strict` setting.

A2 promises those runs keep working, but the requirement states the
harmlessness rule only for fixture declarations. pytest's `addini`
overwrites a repeated registration without error, and unknown-key
validation runs after the root conftest's `pytest_addoption`. A project can
therefore register the keys itself in plain pytest, provided the gate
resolves its defaults so that such a registration cannot change them
(proposed Q09).

**llm-shared's 100% coverage needs its own activation path (requested
change).** `-p` modules are imported during argument preparsing, before
pytest-cov starts coverage in `pytest_load_initial_conftests`. If
llm-shared's own prepared shell or groundhog stages select the policies,
their module-level code runs before measurement and the plugin modules
cannot reach 100%. The design should state that llm-shared selects nothing
for itself and loads both policies only through `tests/conftest.py`, as gap
item 7 says. It should also say that llm-shared's tests import the modules
only by their canonical names.

Today's audit calls `sys.addaudithook` at import. A process-wide guard, not
a per-module flag, should keep a second import path or a module reload from
adding a second hook.

**Routine static fixes would undo the compatibility boundary (requested
change).** `check.bat` runs `ruff check --fix` over the whole project. Ruff
takes its target from `requires-python = ">=3.13,<3.14"`, with `ALL` rules
fixable, and Pyright checks `tools` at `pythonVersion = "3.13"`. The
routine fix pass can rewrite the standalone modules into syntax or APIs
newer than 3.10 or 3.12, and extra 3.12 checks run beside it would only
report the damage afterwards. The main configuration needs per-path
targets:

- Ruff's `per-file-target-version`, supported by the installed 0.15.13, at
  `py310` for `tools/pytest_plugins/**`;
- a Pyright execution environment for that directory at Python 3.12.

APIs reached before the version check also stay 3.10-available.

**Four precisions (wording or simplification).**

- Q04 binds fixture ownership to the executing thread. The design should
  state the consequence the requirement left open: a start on any other
  thread, even while the fixture's setup or teardown is still running, is
  not that fixture's own work and is judged under the active lifecycle.
  The how-to should say so, because helpers such as process pools start
  processes from their own threads.
- Q05: pytest-xdist already schedules only after every worker has reported
  its collection (`collection_is_completed`). E1's barrier is that point: a
  worker that fails validation fails its collection rather than reporting
  it, and the controller translates the outcome to exit code 4. In round 4
  I verified that a worker's own exit status does not become the
  controller's.
- Q07: with G1 running the executable harness for every day walk and every
  direct full run, `check.bat` needs only the static 3.12 checks and the
  3.10 parse check. Every `ghog check` then stays fast, and the rule for
  reusing a result inside one invocation is no longer needed.
- The question blocks write identifiers such as `tools/pytest_plugins`,
  `LLM_SHARED_PYTEST_PLUGINS`, `check.bat`, `ghog full` and `-p` without
  code spans, as one long line per paragraph; the rest of the document
  wraps and uses code spans.

**Disposition.** Two new user questions, the coverage activation path and
the static-tool targets go beyond wording. Another automated round should
check them once the writer has added them.

### Question verdicts for design-specification shared_lifecycle_gate round 1

Existing questions (formulation reviewed; all pending, no user decision):

- Q01 import route: agree with A1, my choice. Correct the option-ordering
  claim (tracked `addopts` come before `PYTEST_ADDOPTS`); the missing-loader
  case becomes Q08.
- Q02 selection and binding: agree with B1, my choice.
- Q03 fixture declaration: agree with C1, my choice; verified that pytest
  9.1 fixture objects are hashable dictionary keys.
- Q04 fixture ownership: agree with D1, my choice; state that starts on any
  other thread are not the fixture's own work, even during its setup.
- Q05 xdist barrier: agree with E1, my choice; build it on xdist's existing
  wait for every worker's collection.
- Q06 Python 3.12 environment: agree with F1, my choice.
- Q07 direct full validation: agree with G1, my choice; keep `check.bat` to
  the static checks once G1 runs the executable harness.

Proposed new questions:

- Q08 missing loader after preparation: my choice H1 (check at preparation
  and before each groundhog stage; accept pytest's own import error for a
  shell prepared before llm-shared moved, as an explicit K1 qualification).
- Q09 tracked lifecycle settings without the gate: my choice I1 (a
  plain-pytest root-conftest registration, with the gate resolving its own
  defaults).

Outstanding human decisions: Q01 to Q09.

### Requested changes for design-specification shared_lifecycle_gate round 1

Requested changes:

1. Add Q08 and Q09 after Q07, using the blocks below (or an equivalent
   formulation), each at `User decision: pending`. Q08 qualifies the
   confirmed K1 contract only if the user accepts it; do not record it as
   settled.
2. In "Early failure and duplicate loading", replace the claim that the
   loader precedes "later explicit `-p` options" with the actual order:
   tracked `addopts` options, then `PYTEST_ADDOPTS`, then the command line.
   State that a policy named in tracked `addopts` is imported before the
   loader and that the opt-in how-to never names the policies there.
3. In "Process-free regressions and executable compatibility", state
   llm-shared's own activation: its prepared shell and groundhog stages
   select nothing for llm-shared, both policies load only through
   `tests/conftest.py` after coverage has started, and its tests import the
   modules only by their canonical names. Add that the audit hook is
   installed once per process, guarded process-wide, so a second import
   path or a module reload cannot add a second hook.
4. In the compatibility section, require per-path targets in the main
   static configuration, not only extra checks: Ruff
   `per-file-target-version` at `py310` for `tools/pytest_plugins/**`
   (`check.bat` runs `ruff check --fix` with the 3.13 target inferred from
   `requires-python`), and a Pyright execution environment for that
   directory at Python 3.12, with APIs reached before the version check
   kept 3.10-available.
5. Under "Fixture ownership and finalization", state that a process start
   on any thread other than the one executing the fixture operation is not
   that fixture's own work, even while its setup or teardown is running,
   and is judged under the active lifecycle; add it to the how-to
   contents.
6. In Q05, name the existing xdist barrier: scheduling starts only after
   every worker reports its collection, so a worker that fails declaration
   validation fails its collection instead of reporting it, and the
   controller translates the outcome to exit code 4.
7. In Q07 and the compatibility section, once G1 runs the executable
   harness for day and direct full validation, keep `check.bat` to the
   static Python 3.12 checks and the Python 3.10 parse check, and drop the
   rule for reusing a harness result inside one invocation.
8. Wrap the question blocks like the rest of the document and put
   identifiers (`tools/pytest_plugins`, `LLM_SHARED_PYTEST_PLUGINS`,
   `LLM_SHARED_PYTEST_ROOT`, `LLM_SHARED_PROCESS_FIXTURES`, `check.bat`,
   `ghog full`, `-p`, `PYTHONPATH`) in code spans.

Proposed Q08 block:

```markdown
### Q08: Missing shared infrastructure after preparation

Question description: K1 requires a prepared run whose selected plugin
cannot be imported to stop before tests with exit code 4, naming the plugin
and the selection. The proposed route imports the policies through
`llm_shared_pytest_loader`, itself injected as `-p llm_shared_pytest_loader`
in `PYTEST_ADDOPTS`. The likeliest K1 cause, an llm-shared checkout that
moved or broke, also removes the loader. pytest 9.1 then raises its own
`ImportError` for that `-p` module: the run still stops before any test,
but with exit code 1 and a traceback naming only the loader module, not the
selection. Preparation can check the directory when the shell is prepared
and before each groundhog stage spawns pytest. A plain `pytest` in a shell
prepared before llm-shared moved still reaches pytest's own error.

#### BBQ for Q08

An attendant checks each cookout kit at the gate and names any missing
thermometer and who ordered it. If the attendant has gone home, an
unchecked grill still refuses to light, but nobody says what was missing or
who asked for it. The club can confirm an attendant is on duty when the
cookout is booked and again whenever a grill is wheeled out, and accept the
silent refusal for a grill lit later; or it can also hang a checklist on
the grill's own lighter. In this picture: the attendant is the early
loader, booking is shell preparation, wheeling out a grill is a groundhog
stage, a grill lit later is a plain `pytest` in a shell prepared before
llm-shared moved, and the lighter's checklist is a pytest shortcut in the
prepared shell that checks the loader first.

#### Options for Q08

- Option H1: shell preparation and every groundhog stage check that the
  loader and each selected policy are present before activating or
  spawning pytest, and fail with the K1 message and exit code 4 when they
  are not. A shell prepared before the infrastructure disappeared stops
  at pytest startup with pytest's own import error for the loader (exit
  code 1, selection not named), recorded as a K1 qualification.
  - pro: no new launcher; every newly prepared shell and every groundhog
    stage keeps K1's exit code and message, and no test ever runs without
    the selected enforcement.
  - con: narrows the confirmed K1 contract for one case, which needs the
    user's explicit acceptance.
- Option H2: H1, plus a `pytest` shortcut in the prepared shell that checks
  the loader first and exits with code 4 and the K1 message.
  - pro: a typed `pytest` in a stale prepared shell keeps K1's exit code
    and message.
  - con: covers typed commands only: `python -m pytest`, scripts and IDE
    runs launched from that shell keep H1's behavior; adds the alias the
    design otherwise avoids.

#### Recommended option for Q08 (with arguments for this choice)

Option H1: the residual case still stops before any test, so selected
enforcement never silently disappears, which is K1's purpose. It arises only
in a shell prepared before llm-shared moved, and preparing the shell again
restores the full diagnostic. H2 adds an alias for a partial gain.

#### Answer to Q08: option H1 (with reason why it must be accepted as the answer)

Option H1: preparation and every groundhog stage verify the loader and
selected policies before activation, with the K1 message and exit code 4.
The design and the opt-in how-to state the residual case: in a shell
prepared before the shared infrastructure became unavailable, pytest stops
at startup with its own import error for the loader, and preparing the
shell again restores the K1 diagnostic. This is a proposed K1 qualification
pending the user's explicit decision.

User decision: pending
```

Proposed Q09 block:

```markdown
### Q09: Lifecycle settings where the gate is not loaded

Question description: the requirement lets a project set the four
`test_lifecycle_*` keys in its tracked pytest configuration. When
collection starts, pytest 9.1 reports every key that no loaded plugin
registered as `Unknown config option`. That happens in every run outside
the prepared environment and in audit-only selections. It is a warning in
each such run, an error under warnings-as-errors, and a usage error under
`--strict-config` or pytest's `strict` setting. Q01 A2 of the requirement
promises those runs keep working; the requirement states that rule only
for fixture declarations. pytest's `addini` accepts a repeated
registration of the same key without error, and unknown keys are checked
after the root conftest's `pytest_addoption` has run.

#### BBQ for Q09

A club writes its preferred grill temperatures on a card kept in every
picnic basket. Guests who do not use the club's thermometer find a card
they cannot read; some ignore it, and the strictest refuse to cook. The
club can print a short legend on the card, ask strict families to keep the
temperatures in their heads, or accept the refusals. In this picture: the
card is the tracked pytest configuration, the thermometer is the gate
plugin, the guests are runs without it, the strictest guests are strict
configuration settings, and the legend is a project-side registration of
the four keys.

#### Options for Q09

- Option I1: the opt-in how-to gives a plain-pytest snippet for the
  project's root `conftest.py` that registers the four keys with
  `parser.addini` in `pytest_addoption`. The gate resolves its own
  defaults, so the project's registration cannot change them.
  - pro: tracked settings stay harmless everywhere, under every strict
    setting, with no llm-shared import; the gate still validates them
    wherever it is loaded.
  - con: a few lines per project that must keep the key names in step
    with the gate.
- Option I2: projects that need strict configuration keep the keys out of
  tracked configuration; the prepared selection supplies them as `-o`
  overrides in prepared runs only.
  - pro: nothing in tracked files; runs without the gate never see the
    keys.
  - con: settings move from reviewed project configuration to the shell;
    another preparation input to document and test.
- Option I3: document the limitation: tracked settings warn in every run
  without the gate and fail strict-config runs; such projects keep the
  defaults or pass `-o` on prepared command lines.
  - pro: no new mechanism.
  - con: breaks A2's promise for strict projects that need non-default
    limits, and adds a warning to every run outside the prepared
    environment.

#### Recommended option for Q09 (with arguments for this choice)

Option I1: it keeps G1's project-configuration level usable without any
new failure outside the prepared environment, in plain pytest, and needs
only that the gate not depend on registration defaults. I2 moves reviewed
settings into the shell, and I3 gives up A2's promise for strict projects.

#### Answer to Q09: option I1 (with reason why it must be accepted as the answer)

Option I1: the opt-in how-to provides the root-conftest registration of the
four keys, the gate applies its documented defaults when a key is absent
from configuration regardless of any registration default, and acceptance
adds a run without the gate, under strict configuration and
warnings-as-errors, with tracked settings present.

User decision: pending
```

### Writer instructions for design-specification shared_lifecycle_gate round 1

1. Apply the requested changes: add Q08 and Q09 at `User decision:
   pending`, correct the option-ordering claim, state llm-shared's own
   activation path and the once-per-process audit hook, require per-path
   static targets, state the thread rule for fixture ownership, name the
   existing xdist barrier in Q05, simplify `check.bat` under Q07, and wrap
   the question blocks with code spans.
2. Keep Q01 to Q07 at `User decision: pending`; record a decision only
   from the user's explicit choice. Do not reopen confirmed requirement
   decisions; Q08 presents a K1 qualification for the user to accept or
   reject.
3. Request another automated review round covering the new questions and
   the revised sections. Do not consolidate.

### Final reviewer decision for design-specification shared_lifecycle_gate round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-11-05T20:36:39+01:00
- Exchange: specification/design-specification/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for design-specification shared_lifecycle_gate (round 2)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
Review round: 2

### Requestor assessment for design-specification shared_lifecycle_gate (round 2)

The revised design retains every confirmed requirement, including Python 3.12
execution, selected-import exit code 4, independent policies and no process
permissions in llm-shared's own suite. Q01-Q07 retain all options and pending
human statuses. Nine questions now cover the unresolved design choices;
their recommendations are proposals, not user decisions.

Q08 asks where to materialize a self-contained bootstrap independently of the
shared checkout. Both options preserve K1. Q09 covers plain-pytest registration
of tracked settings when the gate is absent. These complete the design
questions identified in round 1; no further missing question is currently known.
The existing options and proposed answers remain sufficient after the edits.

Accepted reviewer wording and technical corrections are applied: real option
order, coverage-safe own-suite activation, process-wide audit singleton,
per-path Ruff and Pyright targets, cross-thread ownership, xdist collection
barrier, static-only check.bat, and wrapped question prose with code spans.

Independent review should assess whether the independent cached bootstrap closes
the stale-preparation failure without fallback policy imports or installation,
and whether all nine question formulations remain within design scope.

### Change summary for design-specification shared_lifecycle_gate (round 2)

- Added an independent, atomically refreshed bootstrap cache, preserving exit
  code 4 when the entire shared checkout disappears after shell preparation.
  Q08 compares a user-local cache default with explicitly configured external
  storage. Neither creates a review artifact home or changes consumer files.
- Corrected tracked addopts, PYTEST_ADDOPTS and command-line ordering; policy
  imports must stay out of tracked addopts.
- Added Q09 and the proposed plain-pytest key-registration interface, with
  gate-owned defaults and explicit configuration/override precedence.
- Specified conftest-only own-suite activation after coverage starts and
  canonical imports; the audit dispatcher is guarded once per process.
- Required main Ruff py310 per-file targets and a Python 3.12 Pyright
  environment, with pre-refusal APIs available on 3.10.
- Clarified other-thread process starts, the existing all-worker collection
  barrier and controller exit-4 translation.
- Kept check.bat static-only; day and direct full invoke fresh executable
  compatibility evidence through the own-project preflight.
- Added acceptance cases, updated adoption guidance and wrapped question prose.
  Every original question, option and pending user status is retained.

### Writer response for design-specification shared_lifecycle_gate (round 2)

Writer response:

Accepted every requested correction except the proposed weakening of K1.
There is an explicit disagreement on adding a design question that qualifies
the confirmed startup exit code: the user chose exit code 4, and design review
must not reopen that requirement. The missing-loader failure itself is valid.

The revised design addresses it by materializing the loader independently of
the shared checkout during preparation. Removing that checkout leaves the
bootstrap able to raise an identifying pytest.UsageError, with no cached
policy or installed-policy fallback. This covers plain pytest, python -m
pytest and script entry points, rather than a typed-command alias. Q08 now
asks about bootstrap storage; both alternatives retain the existing K1 contract.
Please examine this compliant alternative instead of treating pytest's exit
code 1 as an accepted qualification.

Accepted Q09 as proposed in substance. Root-conftest addini registration must
not alter gate defaults; tracked configuration and -o are resolved explicitly.
Coverage, singleton, static configuration, thread, xdist and compatibility
simplification corrections are present. The nine questions await explicit
human decisions. No consolidation or implementation has been performed.

### Reviewer focus for design-specification shared_lifecycle_gate (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-11-05T20:41:38+01:00
- Exchange: specification/design-specification/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification shared_lifecycle_gate round 2

I read the complete revised design (SHA-256
`22535fb49d898ea8b28c9ca01561ec4af344c1336487bdf1aa535d588a2700c2`) and the
round 2 request.

**Round 1's corrections are applied.** The design now reflects pytest's real
option order and keeps policy `-p` entries out of tracked `addopts`. It gives
llm-shared a coverage-safe own-suite path: no selection for itself,
conftest-only loading after coverage starts, and canonical imports only. It
installs one audit dispatcher per process behind a process-wide guard. It
sets Ruff `py310` and Pyright 3.12 targets for `tools/pytest_plugins/**` in
the main configuration. It adds the thread rule for fixture ownership,
builds on xdist's existing `collection_is_completed` barrier with
controller exit-4 translation, and keeps `check.bat` to static checks. Q09
and its interface match the proposal, including gate-owned defaults. The
question prose is wrapped and uses code spans.

**The writer's disagreement on Q08 is right, and I withdraw my proposed K1
qualification.** A bootstrap copy of the loader kept outside the shared
checkout survives the checkout's removal. It can still raise an identifying
`pytest.UsageError`, exit code 4, for plain `pytest`, `python -m pytest` and
script entry points alike, without caching or installing any policy. That
satisfies the confirmed K1 contract where my proposal narrowed it. The
source loader in the policy directory also remains a fallback if only the
cache is removed, so pytest's own import error remains only when both the
cache and the checkout are gone. The design should say that in one
sentence, rather than claim K1 holds unconditionally.

**The proposed cache index breaks with several llm-shared checkouts
(requested change).** H1 indexes the cached bootstrap by consumer project
root and bootstrap contract version, and the bootstrap "checks the bound
shared policy path". Two llm-shared checkouts preparing the same consumer at
the same contract version write the same cache entry, for example a feature
worktree and the main checkout during this effort's own consumer trial. The
second preparation replaces the file a live shell from the first is using.
That shell then preflights the other checkout's path, or runs another
checkout's loader. When that worktree is removed after merging, the first
shell reports a false K1 failure although its own checkout is intact.

A layout without shared mutable files avoids this:

- the cache entry is immutable and content-addressed (a directory named by
  a hash of the bootstrap source), written once atomically and never
  replaced in place;
- the binding (project root, policy directory, selection) travels in the
  prepared environment, as `LLM_SHARED_PYTEST_ROOT` already does, not in
  the cached file;
- each cache directory holds only the bootstrap module, because it sits on
  `PYTHONPATH` ahead of everything else in every Python process of the
  shell.

The H1 con about identifying which project's cached bootstrap is active then
disappears, and cleanup becomes removal of unreferenced old versions.

**A stale bootstrap needs a contract check against the policies (requested
change).** Consumers load policies from the live checkout (requirement
Q09). After the shared checkout is updated, a shell prepared earlier keeps
its older bootstrap while the policy directory holds newer policies. The
design should define the bootstrap-to-policy contract version and its
behavior on mismatch: stop before tests with exit code 4 and a message
asking to prepare the shell again, rather than registering policies through
an older interface.

**Smaller precisions (wording).**

- The 3.10 rule "APIs reached before refusal are available on 3.10" has no
  check behind it, since Pyright checks the directory at 3.12. Keeping the
  code before refusal to `sys` and `pytest` imports and the version
  comparison makes that rule checkable by inspection and by the parse
  check.
- Q08's question and options should describe the content-addressed layout
  and environment binding once adopted; the BBQ can stay.

**No other question is missing.** The nine questions are design-level and
within the requirement's scope; the K1, A2, G1, Q15 and Q16 boundaries are
respected. The two requested changes alter the proposed cache mechanism, so
another automated round should check them.

### Question verdicts for design-specification shared_lifecycle_gate round 2

All nine questions are pending; no user decision is recorded.

- Q01 A1, Q02 B1, Q03 C1, Q04 D1, Q05 E1, Q06 F1, Q07 G1, Q09 I1: agree;
  these are also my choices. The round 1 corrections are applied.
- Q08 bootstrap storage: agree with the question and with H1 (user-local
  cache) as my choice, provided the cache is content-addressed and
  immutable with the binding carried by the prepared environment, and the
  bootstrap checks its contract version against the policies. I withdraw
  my round 1 proposal to qualify K1; the writer's alternative keeps K1.

Outstanding human decisions: Q01 to Q09. No question is missing.

### Requested changes for design-specification shared_lifecycle_gate round 2

Requested changes:

1. In "Early failure and duplicate loading" and Q08, replace the cache
   indexed by project root and contract version with an immutable,
   content-addressed entry: a directory named by a hash of the bootstrap
   source, written once atomically and never replaced in place, holding
   only the bootstrap module. Carry the binding (project root, policy
   directory, selection) in the prepared environment rather than in the
   cached file, so several llm-shared checkouts can prepare the same
   consumer without changing a bootstrap a live shell uses. Cleanup removes
   old unreferenced entries.
2. Define a bootstrap-to-policy contract version. When a prepared shell's
   bootstrap does not match the policy directory's contract, stop before
   tests with exit code 4 and a message asking to prepare the shell again;
   never register policies through a mismatched interface. Add the case to
   the acceptance table.
3. Replace "This preserves K1 without qualifying the confirmed
   requirement" with the exact boundary: the bootstrap survives removal of
   the shared checkout, the policy directory's source loader still serves
   if only the cache is removed, and only the removal of both leaves
   pytest's own import error.
4. Keep the code reached before the version refusal to `sys` and `pytest`
   imports and the version comparison, so "APIs reached before refusal are
   available on 3.10" is checkable while Pyright checks the directory at
   Python 3.12.
5. Update Q08's description, H1 and H2 to the content-addressed layout and
   environment binding; drop H1's con about identifying which project's
   bootstrap is active.

### Writer instructions for design-specification shared_lifecycle_gate round 2

1. Apply the requested changes to the bootstrap cache layout, the
   contract-version check, the K1 boundary sentence, the pre-refusal
   imports and the Q08 formulation.
2. Keep Q01 to Q09 at `User decision: pending`; record a decision only from
   the user's explicit choice. Do not reopen confirmed requirement
   decisions.
3. Request another automated review round covering the revised bootstrap
   mechanism. Do not consolidate.

### Final reviewer decision for design-specification shared_lifecycle_gate round 2

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor

- Recorded: 2026-11-05T20:46:44+01:00
- Exchange: specification/design-specification/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for design-specification shared_lifecycle_gate (round 3)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
Review round: 3

### Requestor assessment for design-specification shared_lifecycle_gate (round 3)

All nine design questions remain pending with their original IDs and options.
No additional question is missing. The revised Q08 remains a cache-placement
choice, with both options using the same safe cache and binding contract.

Accepted round 2 corrections are applied: immutable SHA-256-addressed loader
entries containing only the bootstrap module; environment-carried project,
policy directory and selection; no replacement of live entries; explicit
cleanup rules; a bootstrap-to-policy contract version and exit-4 mismatch
refusal; precise cache/source-loader availability; and an inspectable minimal
pre-refusal path. Existing options and proposed answers remain sufficient.

The design retains Python 3.12 execution, independent policies, live-checkout
policy loading, unchanged timing and records, and the process-free own suite.
Please verify the revised cache and stale-contract behavior, the two new
acceptance cases and the full document's consistency. No consolidation occurred.

### Change summary for design-specification shared_lifecycle_gate (round 3)

- Replaced mutable project-indexed bootstrap entries with immutable directories
  named by a SHA-256 source hash; each contains only the bootstrap module.
- Moved project root, selection and policy-path binding entirely into the
  prepared environment, including LLM_SHARED_PYTEST_POLICY_DIR.
- Required atomic publication, verification of existing entries and cleanup
  only when prepared sessions no longer need an entry.
- Defined a bootstrap-to-policy contract version, checked before registration;
  mismatch exits 4 and asks to prepare the shell again.
- Stated which loader remains after either cache or shared-checkout loss, and
  the infrastructure-loss boundary when both executable copies disappear.
- Limited pre-refusal execution to sys and pytest imports, version comparison
  and identifying usage-error refusal.
- Updated Q08 and added multi-checkout and stale-contract acceptance cases.
  All nine human decision markers remain pending.

### Writer response for design-specification shared_lifecycle_gate (round 3)

Writer response:

Accepted all round 2 findings. Immutable source-addressed bootstrap entries
eliminate shared mutable files between prepared shells. Bindings live in the
environment rather than the cached code, and the cache contains only the
loader module. Existing entries are verified rather than overwritten; cleanup
must preserve entries still needed by prepared sessions.

The contract-version check refuses stale bootstrap/new-policy interfaces before
registration, with exit code 4 and a request to prepare the shell again.
The source loader is available when only the cache disappears; the cached
loader remains when the shared checkout disappears. The document explicitly
states that removal of both executable copies leaves pytest's own import
error, without introducing a policy fallback.

The Python 3.10 pre-refusal boundary and Q08 wording are updated as requested.
The reviewer withdrew the round 1 K1 qualification, so no disagreement remains
on the revised mechanism. All design choices remain human-undecided.

### Reviewer focus for design-specification shared_lifecycle_gate (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-11-05T20:51:00+01:00
- Exchange: specification/design-specification/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification shared_lifecycle_gate round 3

I read the complete revised design (SHA-256
`3802d96594c91979927faa5eafb086455bfdf81947a7ee69385f5f8639f00c32`) and the
round 3 request. The changes sit in the activation sections, the acceptance
table and Q08; the rest matches the version reviewed in round 2.

**Round 2's requested changes are applied correctly.**

- Cache layout: each bootstrap entry is an immutable directory named by the
  SHA-256 hash of the bootstrap source, holding only the bootstrap module,
  published once atomically and verified rather than replaced. Changed
  source gets a new directory.
- Binding: the project root, the selection and the new
  `LLM_SHARED_PYTEST_POLICY_DIR` travel in the prepared environment, and the
  cached code contains none of them. Two llm-shared checkouts preparing the
  same consumer can no longer disturb each other's live shell; the new
  acceptance case covers it.
- Contract version: every policy and the loader expose one contract
  version, checked before registration. A mismatch, including a missing
  declaration, stops before tests with exit code 4 and asks to prepare the
  shell again; the second new acceptance case covers it.
- K1 boundary: the design now states exactly which copy remains. The
  cached bootstrap survives the shared checkout's removal, the source
  loader serves if only the cache is removed, and only the removal of both
  leaves pytest's own import error. That is accurate and keeps K1 without a
  qualification for any realistic single loss.
- Pre-refusal path: only `sys` and `pytest` imports, the version comparison
  and the usage-error raise run before refusal, so the Python 3.10 rule is
  inspectable while Pyright targets 3.12.

**One wording precision remains.** Cleanup "removes only entries no longer
needed by prepared sessions", but nothing can tell which entries a prepared
shell still uses: shells are not registered anywhere. The design should say
cleanup is an explicit, documented operation that the user runs, not an
automatic step of preparation. Its guide should note that removing an entry
a shell still uses leaves that shell on the source-loader path described
above. This changes no mechanism.

**No question is missing.** I rechecked the nine questions against the
consolidated requirement: K1, A2, G1, Q12 to Q16 and the coverage, static
targets and xdist corrections stay consistent with the new cache design.
The remaining edit is wording, so the formulation can converge; Q01 to Q09
are the outstanding human decisions.

### Question verdicts for design-specification shared_lifecycle_gate round 3

All nine questions are pending; no user decision is recorded.

- Q01 A1, Q02 B1, Q03 C1, Q04 D1, Q05 E1, Q06 F1, Q07 G1, Q09 I1: agree;
  these are also my choices. Unchanged since round 2.
- Q08 H1 (user-local, content-addressed, environment-bound bootstrap with a
  contract check): agree; my choice. H2 is a valid alternative for
  machines whose policy forbids a default user cache.

Outstanding human decisions: Q01 to Q09. No question is missing.

### Convergence evidence for design-specification shared_lifecycle_gate round 3

Covered wording:

1. In "Early failure and duplicate loading", replace "Cleanup removes only
   entries no longer needed by prepared sessions, never an older entry
   merely because a newer one exists." with:

   > Cleanup is an explicit, documented operation, never an automatic step
   > of preparation, because no record shows which entries prepared shells
   > still use. Removing an entry a shell still uses leaves that shell on
   > the policy directory's source loader, as described below.

2. In Q08 option H1's con, replace "old entries must remain while prepared
   shells still need them" with "old entries stay until the user runs the
   documented cleanup".

Convergence rationale:

Every round 1 and round 2 correction is applied. The bootstrap mechanism
keeps the confirmed K1 contract without a qualification, separate llm-shared
checkouts no longer interfere, and stale bootstraps are refused with exit
code 4. The nine questions are complete design choices with distinct options
and recommendations only. The remaining edit is the covered cleanup wording,
which changes no mechanism. The next step belongs to the human: decide Q01
to Q09. Once those decisions are recorded, a follow-up review of them is
needed before consolidation. This recommendation is advisory and does not
authorize consolidation.

### Writer instructions for design-specification shared_lifecycle_gate round 3

1. Apply the covered cleanup wording in "Early failure and duplicate
   loading" and Q08 H1's con. It does not need another automated round.
2. Present Q01 to Q09 to the user with explanations, and record each
   decision only from the user's explicit choice.
3. Do not consolidate. After the user decides, request a follow-up review
   of those decisions before consolidation.

### Final reviewer decision for design-specification shared_lifecycle_gate round 3

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-3 -->

## Round 3 by human - human-confirmation

- Recorded: 2026-11-06T23:34:20+01:00
- Exchange: specification/design-specification/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round

<!-- review-entry-id: human-confirmation-round-3 -->

## Round 4 by requestor

- Recorded: 2026-11-06T23:34:51+01:00
- Exchange: specification/design-specification/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for design-specification shared_lifecycle_gate (round 4)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
Review round: 4

### Requestor assessment for design-specification shared_lifecycle_gate (round 4)

#### Assessment of the shared lifecycle gate human decisions for design-specification shared_lifecycle_gate (round 4)

All nine design questions have explicit human decisions, confirmed on
2026-11-06. The full decision scan exits 0, reports no diagnostics and zero
undecided questions, and identifies the current document SHA-256 as
`4df4130d7b0683b875627d40a64dc6ecd78a74dd60386a1097609026d35d18b1`.

The existing options and answers remain sufficient in the writer's assessment:
the user selected the proposed option for every question, and the discussion
identified no additional question. This assessment needs independent review of
the recorded decisions and their qualifications against the whole design, the
consolidated requirement and related effort documents. Do not limit the review
to a comparison of option labels.

Check whether questions are missing, whether any confirmed choices conflict,
and whether their concrete acceptance conditions leave gaps. In particular,
check all-worker validation evidence and controller exit 4, pytest adapter
ownership boundaries, own-project compatibility preflight applicability,
bootstrap survival and contract checks, and absent-gate configuration handling.

The covered round 3 cleanup wording is already applied: cleanup is an explicit
documented user operation; no registry identifies entries still used by live
shells; Q08's H1 drawback accurately describes retention until manual cleanup.
No remaining round 3 wording suggestion is intentionally deferred.

Human choices must remain authoritative. Report any conflict with them rather
than silently replacing them with a reviewer recommendation. No consolidation,
staging or commit is authorized by this request.

### Change summary for design-specification shared_lifecycle_gate (round 4)

#### Changes since shared lifecycle gate design round 3 for design-specification shared_lifecycle_gate (round 4)

Applied the covered round 3 cleanup wording in the activation section and Q08
H1 drawback before the human discussion. Then recorded the following explicit
choices in their corresponding answer sections, preserving question IDs,
descriptions, options, analogies and recommendations:

| Question | Confirmed choice and acceptance conditions |
| --- | --- |
| Q01 | A1: dedicated shared import directory and early loader; Python 3.12+, unique module names, canonical registration and selected-import exit 4 retained. |
| Q02 | B1: selection in `LLM_SHARED_PYTEST_PLUGINS` through `senv`, with preparation binding `LLM_SHARED_PYTEST_ROOT`. |
| Q03 | C1: `LLM_SHARED_PROCESS_FIXTURES` maps decorated fixture objects to non-empty reasons; resolve registered definitions unambiguously and reject conflicts; harmless without audit. |
| Q04 | D1: bounded pytest execution/finalization/registry adapter; startup capability checks, unconfigure restoration, failure-safe ownership unwinding, and permission bound to executing thread and live token. |
| Q05 | E1: worker validation before successful collection through the all-worker barrier; explicit evidence, cancellation and identifying controller exit 4 for invalid declarations; declaration errors, missing evidence or inconsistent collection prevent scheduling. |
| Q06 | F1: independent manifest and dedicated Python 3.12 compatibility environment with verified absolute-path override; explicit setup, dependency/version checks, no skips for missing prerequisites and no consumer installs. |
| Q07 | G1: explicitly declared own-project executable preflight on every day/direct-full invocation; fresh evidence outside audited tests, applicability independent of policy selection, missing-3.12 failure and no ordinary-consumer prerequisite. |
| Q08 | H1: immutable source-hash user-local bootstrap entries, atomically published and verified; environment bindings, loader-only cache, contract exit 4, no partial activation and explicit cleanup. |
| Q09 | I1: plain-pytest root-conftest registration of the four keys; gate-owned defaults, explicit settings and `-o` precedence, strict unprepared/audit-only runs without shared imports. |

All choices were confirmed on 2026-11-06. Q01-Q04 and Q07 were typed option-1
selections; Q05, Q06, Q08 and Q09 were explicit native-picker selections.
Active pending markers and proposed-acceptance prose in those answers were
replaced by dated human confirmation and rationale. No question was removed,
and no design consolidation or implementation was performed.

### Writer response for design-specification shared_lifecycle_gate (round 4)

Writer response:

#### Writer response to shared lifecycle gate round 3 for design-specification shared_lifecycle_gate (round 4)

Accepted the cleanup wording precision and applied it before discussing the
questions. Presented every question separately with concrete behavior,
tradeoffs, examples and an actionable choice. Recorded only explicit answers.
The completed discussion follows the user's retained authority to record
decisions and obtain an independent follow-up review before consolidation.

The user chose A1/B1/C1/D1/E1/F1/G1/H1/I1. All nine questions and their history
remain present. There is no disagreement with the round 3 recommendations.
The full scan after the final answer reports every question confirmed and no
diagnostic; the pre-decision convergence answer has not been treated as review
of these subsequent human decisions.

Please review the full specification, the recorded decision rationales and
qualifications, effects on earlier decisions, consistency with
`docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md` and other related
effort documents, and missing or newly necessary questions.
Identify conflicts with confirmed human decisions explicitly. A recommendation
cannot overwrite them. Preserve all question blocks; consolidation still
requires its own explicit human choice at the next convergence gate.

### Reviewer focus for design-specification shared_lifecycle_gate (round 4)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-4 -->

## Round 4 by reviewer

- Recorded: 2026-11-06T23:54:01+01:00
- Exchange: specification/design-specification/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification shared_lifecycle_gate round 4

I read the complete design (SHA-256
`4df4130d7b0683b875627d40a64dc6ecd78a74dd60386a1097609026d35d18b1`), the
round 4 request and the consolidated feature request. The round 3 cleanup
wording is applied as covered. All nine questions now carry explicit user
decisions dated 2026-11-06, and I agree with every chosen option.

I checked the confirmed qualifications against pytest 9.1.0 and
pytest-xdist 3.8.0, the versions in llm-shared's environment. Two of them
rely on a mechanism those versions do not provide, one needs a
process-wide guard, and three need a precision. I verified both main findings with short pytest runs in a
temporary directory, outside the repository and its suite.

**Q05 / E1: the xdist barrier waits for an announced collection, not a
successful one.** The body says scheduling "waits for every worker's
successful collection" and that "invalid declarations fail that
collection". In xdist 3.8, `collection_is_completed` only counts workers
that sent `collectionfinish`; a failed collect report does not hold
scheduling. Three probes with two workers:

| Worker-side failure | Observed result |
| --- | --- |
| Module import error during collection on both workers | Scheduling continued: `1 passed, 2 errors`. |
| `pytest.UsageError` from `pytest_collection_modifyitems` on gw1 only | pytest calls `pytest_collection_finish` in a `finally`, so gw1 still announced its full collection. gw0 ran two tests, then the controller stopped with an INTERNALERROR (`assert not crashitem`), exit 3. |
| `pytest.UsageError` from a `tryfirst` `pytest_collection_finish` on gw1 only | gw1 announced nothing and no test ran, but the controller waited until a 60 s timeout killed it. |

E1 stays implementable and the user's choice stands: its con already said
a worker's normal collection failure is not enough. The body must state
the mechanism instead of the inaccurate premise. The worker validates
before xdist's announcement and withholds it after any declaration error.
The controller treats a worker that finishes before announcing as a stop,
never a wait, and exits 4 when that worker's evidence names a declaration
error. Validation that fails after the announcement is excluded, because
the other workers have already started tests by then.

**Q09 / I1: gate-owned defaults need a mechanism pytest 9.1 does not
expose publicly.** The body says the gate resolves absent values from its
own defaults "rather than registration defaults" and validates
"configuration presence and `-o` precedence explicitly". `Parser.addini`
silently replaces an earlier registration's help, type and default, and a
root conftest's `pytest_addoption` runs after a `-p` plugin's. For an
absent key, `config.getini` therefore returns the snippet's default: with
the gate registering `"0.1"` and an unguarded snippet registering `"9"`,
the gate read `'9'`. Telling an absent key from an explicit one would need
`config.inicfg`, which pytest 9.1 deprecates with
`PytestRemovedIn10Warning` (an error under warnings-as-errors), or the
private `_inicfg` store.

A public route exists. `pytest_addoption(parser, pluginmanager)` receives
the plugin manager, so the snippet can skip registration when
`pluginmanager.has_plugin("llm_shared_lifecycle_gate")` is true. With that
guard the gate read its default `'0.1'` for an absent key, `'0.5'` for a
tracked value and `'0.3'` for `-o`. With the gate absent, a tracked key
passed under `strict_config = true` and `filterwarnings = error`. When the
gate loads after the snippet, its own later registration replaces the
snippet's, so the gate's registration applies in both orders. This changes
how the confirmed I1 qualification is met ("defaults owned by the gate",
"independently of registration defaults"), so it needs a user decision
(new Q10) rather than a silent rewrite. I1 itself, plain-pytest
root-conftest registration, is unaffected.

**Q04 / D1: the fixture adapter needs the dispatcher's process-wide
guard.** The adapter wraps pytest's fixture execution and finalization,
which are process-global, and D1 requires restoration on unconfigure. For
the audit dispatcher, the design already says module-local flags are not
enough: one dispatcher per process, with sessions attaching and detaching
their own state. The adapter has no matching rule. An embedded session
that loads the audit, such as a `pytester` inline run in llm-shared's own
in-process isolation tests, would restore pytest's originals on its own
unconfigure. The outer audited session would then lose fixture ownership,
and a start inside an unexempt broader-scoped fixture would be judged as
the carrying test's work. This refines D1 without changing it.

**Smaller precision gaps.**

- Q02 / B1: "rejected or refreshed before selected enforcement starts"
  does not say who refreshes or what counts as a different project. Only
  preparation can refresh. At pytest startup the bootstrap can only
  reject, and a containment test on pytest's `rootpath` keeps projects
  whose pytest rootdir is a subdirectory working.
- Q07 / G1: "explicit llm-shared project-local declaration" can read as an
  untracked machine-local file, which this repository names `*.local.*`.
  It must be tracked in llm-shared so every clone and linked worktree runs
  the preflight.
- Q08 / H1: "verify any existing entry against that hash" does not say what
  a mismatch does. Entries are never replaced, so preparation must stop
  and publish nothing.
- Context: "The interfaces below are proposed design choices for review;
  they are not additional user decisions" is stale now that Q01 to Q09 are
  decided. The other "Propose" verbs can wait for consolidation.

**Missing question.** Q10, how the gate keeps its defaults when the
documented snippet also registers the keys. The Q05 and Q04 corrections
stay within the confirmed E1 and D1 and need no new question.

### Question verdicts for design-specification shared_lifecycle_gate round 4

All nine questions carry explicit user decisions dated 2026-11-06. I agree
with every chosen option, and each is also my own choice. None of my
findings conflicts with a chosen option. Two findings change how a
confirmed qualification is met, and only the Q09 one needs a new
decision.

- Q01 A1, Q03 C1, Q06 F1: agree; no change.
- Q02 B1: agree; state that only preparation refreshes a binding and that
  the bootstrap rejects a pytest `rootpath` outside the bound root with
  exit 4.
- Q04 D1: agree; "restoration on unconfigure" needs the dispatcher's
  process-wide guard, so a nested session cannot remove the outer
  session's fixture instrumentation.
- Q05 E1: agree; the body's barrier premise does not hold in xdist 3.8,
  which waits for announced collections, not successful ones. E1's con
  already anticipated this; the correction names the mechanism without
  changing the choice.
- Q07 G1: agree; the applicability declaration must be tracked in
  llm-shared.
- Q08 H1: agree; an existing entry that fails verification stops
  preparation.
- Q09 I1: agree with root-conftest registration. Its qualification that
  the gate resolves defaults "independently of registration defaults" has
  no public pytest 9.1 mechanism. How the gate keeps its defaults is a new
  decision (Q10), not a rewrite of I1.
- Q10 (missing): add it. My choice is J1, the snippet guarded by
  `pluginmanager.has_plugin`.

Outstanding human decisions: Q10 once added. Q01 to Q09 stay confirmed.

### Requested changes for design-specification shared_lifecycle_gate round 4

Requested changes:

1. In "Independent audit state and declaration interfaces", replace the
   passage from "Use xdist's existing `collection_is_completed` barrier"
   through "does not set the controller's status." with:

   > Use xdist's existing `collection_is_completed` barrier, which counts
   > the workers that have announced their collection. Each worker
   > validates in a `pytest_collection_finish` implementation ordered
   > before xdist's announcement. After any declaration error, it
   > withholds the announcement, leaves identifying evidence for the
   > controller and ends with a usage error, so the barrier never
   > completes. Validation never fails after the announcement: pytest
   > still runs `pytest_collection_finish` when
   > `pytest_collection_modifyitems` raises, and xdist then schedules the
   > announced collection on the other workers. The controller treats a
   > worker that finishes before announcing its collection as a stop,
   > never as a wait. When that worker's evidence names a declaration
   > error, the controller stops the remaining workers and exits 4 with
   > the identifying usage error. An announced collection is the worker's
   > validation evidence. Serial runs validate at the same point.

2. In "Fixture ownership and finalization", after "All ownership stacks
   unwind on failure.", add:

   > Install the fixture adapter once per process under the same
   > process-wide guard as the audit dispatcher. Each session attaches and
   > detaches its own ownership state. Restore pytest's original fixture
   > callables only when the last attached session detaches, and only
   > while they still hold the adapter's wrappers.

3. In "Opt-in and prepared-environment contract", replace "The root binds
   selection to that project; inherited preparation for a different
   project must be rejected or refreshed before selected enforcement
   starts." with:

   > The root binds selection to that project. Only preparation, in
   > `senv` or in groundhog's child environment, refreshes a binding. At
   > pytest startup, before registration, the bootstrap rejects a run
   > whose pytest `rootpath` lies outside `LLM_SHARED_PYTEST_ROOT`, with
   > exit code 4 naming the bound root and the selection; a rootdir inside
   > the project stays accepted. A nested pytest process for another
   > directory, such as a generated temporary project, clears the
   > preparation variables first.

4. In "Process-free regressions and executable compatibility", replace
   "Its applicability comes from an explicit llm-shared project-local
   declaration, never a consumer name or plugin selection." with:

   > Its applicability comes from an explicit declaration tracked in
   > llm-shared and read from the project under test, so every clone and
   > linked worktree of llm-shared runs it. Never derive it from a
   > consumer name, an untracked machine-local file or plugin selection.

5. In "Early failure and duplicate loading", after "verify any existing
   entry against that hash, and never replace an entry used by a prepared
   shell.", add:

   > An existing entry that fails verification stops preparation with a
   > diagnostic naming the entry and the documented cleanup. Preparation
   > never rewrites it and publishes no environment.

6. In "Measurement, limits and proof states", replace "The gate resolves
   absent values from its own documented defaults rather than
   registration defaults, because root-conftest registration can
   overwrite them. Validate configuration presence and `-o` precedence
   explicitly. Q09 compares this interface with prepared-only overrides
   and documented strict-mode limits." with:

   > Q09 confirmed this interface. pytest keeps the last `addini`
   > registration of a key, and a root conftest registers after a `-p`
   > plugin, so an unguarded snippet replaces the gate's type and default.
   > Q10 decides how the gate keeps its own defaults and the
   > `-o`/project/default precedence without deprecated or private pytest
   > configuration access.

7. In "Context for v0.14.0 shared lifecycle enforcement", replace "The
   interfaces below are proposed design choices for review; they are not
   additional user decisions." with:

   > Q01 to Q09 record the user's decisions of 2026-11-06. The other
   > interfaces below are design choices within those decisions and the
   > requirement.

8. Add these rows to the acceptance table:

   | Scenario | Expected outcome | Requirement basis |
   | --- | --- | --- |
   | One xdist worker finds an invalid declaration, the others are valid | No test starts on any worker; the controller exits 4 naming the declaration, stops the remaining workers and does not wait indefinitely. | Q13. |
   | Embedded session loads and unconfigures the audit inside an audited run | The outer session keeps one dispatcher, its fixture ownership and its permissions. | Q12. |
   | Prepared shell runs pytest with a rootpath outside the bound root | Exit 4 naming the bound root and the selection, before registration. | Q01, Q11. |
   | Gate loaded with the documented key snippet, in either loading order | Gate defaults, tracked values and `-o` overrides keep their precedence. | Q07, Q10 pending. |

9. Add Q10 after Q09:

   ```md
   ### Q10: Gate defaults beside the key-registration snippet

   Question description: The confirmed I1 snippet and the gate both
   register the four `test_lifecycle_*` keys with `parser.addini`. pytest
   9.1 keeps the last registration's type and default, and a root conftest
   registers after a `-p` plugin, so an unguarded snippet replaces the
   gate's defaults. Telling an absent key from an explicit one would need
   `config.inicfg`, deprecated in pytest 9.1 and an error under
   warnings-as-errors, or pytest's private configuration store. How should
   the gate keep its own defaults and the `-o`/project/default precedence?

   #### BBQ for Q10

   Two people write a grill temperature card for the same grill. When the
   club's thermometer is there, the club's card must be the one in use. In
   this picture: the cards are the two `addini` registrations, the club's
   card is the gate's registration, and looking for the thermometer is the
   plugin-manager guard.

   #### Options for Q10

   - Option J1: The documented snippet takes
     `pytest_addoption(parser, pluginmanager)` and registers the keys only
     when `pluginmanager.has_plugin("llm_shared_lifecycle_gate")` is false.
     The gate's own registration then supplies the defaults, and
     `config.getini` keeps today's precedence.
     - pro: Uses only public pytest API, keeps the current settings reader
       and works in both loading orders, under strict configuration and
       warnings-as-errors.
     - con: An outdated snippet copy without the guard silently replaces
       the gate's defaults when the gate loads first; public API cannot
       detect it.
   - Option J2: The gate reads raw presence and `-o` origin from pytest's
     private configuration store behind a startup capability check, with
     exit code 4 when the store changes.
     - pro: Stays correct whatever defaults a snippet registers.
     - con: Adds a second private pytest surface beside the fixture
       adapter, in an area pytest 9.1 is already moving to `getini`.
   - Option J3: Prescribe a snippet registering string keys with
     `default=None`; the gate treats `None` as absent and applies its own
     defaults.
     - pro: Uses only public API, and the gate default applies in either
       loading order.
     - con: A snippet with any other default silently becomes project
       configuration, so consumers must copy exact defaults rather than one
       guard.

   #### Recommended option for Q10 (with arguments for this choice)

   Option J1: The guard keeps the gate's registration authoritative
   through a documented hook argument, adds no pytest internals and keeps
   the current settings reader. Document the guard as part of the snippet.
   Verify both loading orders, an absent key, a tracked value and an `-o`
   override with the gate loaded, and tracked keys with the gate absent
   under strict configuration and warnings-as-errors.

   #### Answer to Q10: option J1 (with reason why it must be accepted as the answer)

   Option J1: It meets Q09's gate-owned defaults with public pytest API in
   every loading order the design supports.

   User decision: pending.
   ```

### Writer instructions for design-specification shared_lifecycle_gate round 4

1. Apply the requested changes to the xdist validation mechanism, fixture
   adapter guard, binding check, preflight declaration, cache entry
   verification, settings paragraph, context sentence and acceptance table.
2. Add Q10 after Q09 in the existing question format, with
   `User decision: pending`. Record a Q10 decision only from the user's
   explicit choice.
3. Keep the Q01 to Q09 option, recommendation, answer and confirmation
   text unchanged. The Q04 and Q05 corrections belong in the design body.
   If Q10 is decided, note there how it meets Q09's "defaults owned by the
   gate" rather than editing Q09.
4. Request another automated review round covering the corrected
   mechanisms and Q10. Do not consolidate.

### Final reviewer decision for design-specification shared_lifecycle_gate round 4

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-4 -->

## Round 5 by requestor

- Recorded: 2026-11-06T23:58:21+01:00
- Exchange: specification/design-specification/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for design-specification shared_lifecycle_gate (round 5)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
Review round: 5

### Requestor assessment for design-specification shared_lifecycle_gate (round 5)

#### Assessment of corrected mechanisms and the new defaults question for design-specification shared_lifecycle_gate (round 5)

The round 4 findings are accepted without disagreement. Corrected the xdist
barrier description and termination path, added process-wide fixture-adapter
attachment/restoration, and clarified root binding, tracked preflight
applicability and immutable-cache verification failure. These refinements
implement the confirmed choices; Q01-Q09 question blocks remain unchanged.

Q10 is newly added and undecided. It asks how the I1 registration snippet and
the gate retain gate-owned defaults with pytest 9.1. The writer agrees with
the reviewer's proposed J1 public plugin-manager guard, but this is not a human
decision. The three options, tradeoffs, analogy and proposed acceptance are
present; no further question was identified while applying round 4.

The full decision scan exits 0 with no diagnostics: ten questions, Q01-Q09
confirmed, Q10 alone undecided. Current design SHA-256:
`4501c7a85601fc88c5878e23da2dedfffd2bc54d35f7b0fef2e0059eaf88d209`.
The original explanation batch remains Q01-Q09; Q10 is outside its fixed scope.

Please check the corrected mechanisms and all acceptance cases against the
confirmed decisions and requirement. Check whether Q10's options and proposed
answer are sufficient, whether any question is missing, and whether any wording
still assumes a pending choice. Preserve the human decisions and surface any
conflict explicitly. No consolidation is authorized.

### Change summary for design-specification shared_lifecycle_gate (round 5)

#### Changes since the human-decision follow-up in round 4 for design-specification shared_lifecycle_gate (round 5)

- Describe xdist's barrier as counting announced collections. Validate in
  `pytest_collection_finish` before xdist announces, withhold an invalid
  worker's announcement, retain identifying evidence, and stop rather than
  hang when a worker finishes before announcement. Declaration errors stop
  remaining workers and yield controller exit 4; serial runs validate at the
  same point.
- Install the fixture adapter once per process with session-local ownership
  attachments. Restore originals only after the last session detaches and
  only if the callables still carry this adapter's wrappers.
- Allow binding refresh only during preparation. At startup reject a pytest
  rootpath outside the bound project with exit 4 before registration, while
  accepting contained roots. Generated-project subprocesses clear preparation.
- Require the llm-shared preflight declaration to be tracked and read from the
  project under test, covering every clone and linked worktree.
- Stop preparation after cache-entry verification failure, naming the entry
  and cleanup instructions; never rewrite the entry or publish an environment.
- Replace the unsupported default-resolution premise with the addini loading
  order problem and a reference to the new Q10 decision.
- Update the context sentence to acknowledge the dated Q01-Q09 human decisions.
- Add acceptance cases for one invalid xdist worker, nested audited sessions,
  mismatched prepared roots and both settings-registration loading orders.
- Append Q10 with J1/J2/J3, recommended J1 and an explicit pending marker.
  Preserve Q01-Q09's options, recommendations, answers and confirmation text.

No human decision was inferred for Q10. No implementation, consolidation,
staging or commit was performed.

### Writer response for design-specification shared_lifecycle_gate (round 5)

Writer response:

#### Writer response to the round 4 mechanism findings for design-specification shared_lifecycle_gate (round 5)

Accepted every requested change. The earlier description incorrectly equated
xdist's collection announcement with successful declaration validation. The
revised body now states the withholding, evidence and controller-stop mechanism
explicitly, without changing confirmed E1. D1 now has the process-wide guard
needed to keep nested sessions from removing an outer session's adapter.

Accepted the public-API finding for I1. Kept the confirmed Q09 text unchanged
and added Q10 as a distinct undecided implementation choice. Its proposed J1
meets Q09's gate-owned-default qualification through a guarded snippet and the
gate's authoritative registration; it has not been selected by the user.

Applied the requested binding, preflight declaration, cache-failure and context
precisions, and all four acceptance rows. All Q01-Q09 human decisions remain
intact. There is no disagreement to signal. Please independently review the
complete revised design and Q10 against the consolidated requirement, looking
for inconsistencies and missing questions before a new human gate.

### Reviewer focus for design-specification shared_lifecycle_gate (round 5)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-5 -->

## Round 5 by reviewer

- Recorded: 2026-11-07T00:02:11+01:00
- Exchange: specification/design-specification/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification shared_lifecycle_gate round 5

I read the complete revised design (SHA-256
`4501c7a85601fc88c5878e23da2dedfffd2bc54d35f7b0fef2e0059eaf88d209`) and the
round 5 request, and rechecked it against the consolidated feature request.

**Every round 4 change is applied as requested.**

- xdist validation: the body now says the barrier counts announced
  collections. Workers validate in `pytest_collection_finish` before xdist
  announces, withhold the announcement after a declaration error, and the
  controller stops instead of waiting, with exit 4 for declaration errors.
  This matches what the round 4 probes showed for pytest 9.1 and xdist 3.8,
  and it meets every condition in the confirmed E1 qualification: explicit
  evidence, cancellation, exit 4, and no scheduling after an error.
- Fixture adapter: installed once per process under the dispatcher's
  guard, with per-session attachment, and pytest's callables restored only
  at the last detach. This refines D1's "restoration on unconfigure"
  without contradicting it.
- Binding, preflight declaration and cache verification: only preparation
  refreshes a binding. A `rootpath` outside the bound root exits 4
  before registration. The preflight declaration is tracked and read from
  the project under test. A cache entry that fails verification stops
  preparation without publishing anything. All three match B1, G1 and H1.
- Settings paragraph: the unsupported presence-reading premise is gone,
  and the paragraph points to Q10.
- Acceptance table: the four new rows cover the corrected mechanisms.

**Q10 is complete.** Its three options are materially distinct: a public
guard, a private-store reader and a prescribed `None` default. Each states
its consequence, and the recommendation follows from public-API use and
the unchanged settings reader. The answer is marked as a proposal pending
the user. One relation should be visible to the user before deciding.
Q09's confirmed recommendation says the gate "reads configuration presence
and `-o` overrides explicitly", which is J2's mechanism. Choosing J1 or J3
keeps I1 and replaces only that sentence at consolidation. A sentence in
Q10's description can state this; it is wording.

**No conflict with a confirmed decision.** The Q01 to Q09 blocks are
unchanged. The body's precise mechanisms for Q04 and Q05 are consistent
with the confirmed option and answer text.

**Wording that still assumes a pending choice.** The context sentence does
not mention that Q10 is pending. Several body sentences still "propose"
interfaces the user has since confirmed: the target flow, the
`LLM_SHARED_PYTEST_PLUGINS` selection, the cache placement, the key
snippet, the fixture dictionary, the Python 3.12 environment and the
preflight. The `process_allowed` marker is a design choice that no
question covers, so "use" fits it better than "propose". These edits
change no mechanism.

**No question is missing.** The corrected mechanisms raise no new choice,
and the remaining edits are wording only, so the formulation can converge.

### Question verdicts for design-specification shared_lifecycle_gate round 5

Q01 to Q09 carry explicit user decisions dated 2026-11-06. Q10 carries a
proposed answer only.

- Q01 A1, Q02 B1, Q03 C1, Q04 D1, Q05 E1, Q06 F1, Q07 G1, Q08 H1, Q09 I1:
  agree; each is also my choice. The corrected body mechanisms for Q02,
  Q04, Q05, Q07 and Q08 implement these choices without changing them.
- Q10: agree with the question, its three options and the recommended J1,
  which is also my choice. Add one sentence relating Q09's
  presence-reading recommendation to J2, so the user sees what J1 or J3
  replaces at consolidation.

Outstanding human decisions: Q10. Consolidation stays a separate human
choice after that decision.

### Convergence evidence for design-specification shared_lifecycle_gate round 5

Covered wording:

1. Context section: replace "Q01 to Q09 below record the user's design
   decisions of 2026-11-06." with "Q01 to Q09 below record the user's
   design decisions of 2026-11-06; Q10 awaits a user decision."
2. Replace wording that still proposes confirmed interfaces:
   - "The proposed target flow is:" becomes "The target flow is:".
   - "Propose `LLM_SHARED_PYTEST_PLUGINS`, containing" becomes "Q02
     confirmed `LLM_SHARED_PYTEST_PLUGINS`, containing".
   - "Cache placement is proposed in Q08." becomes "Q08 confirmed the
     user-local cache placement."
   - "For tracked lifecycle keys to remain usable without the gate,
     propose a plain-pytest `pytest_addoption` snippet in the project's
     root `conftest.py` registering the four keys with `parser.addini`.
     This imports no shared code. Q09 confirmed this interface." becomes
     "For tracked lifecycle keys to remain usable without the gate, the
     project's root `conftest.py` carries a plain-pytest `pytest_addoption`
     snippet registering the four keys with `parser.addini`, as Q09
     confirmed. This imports no shared code."
   - "Propose a `process_allowed(reason="...")` pytest marker" becomes
     "Use a `process_allowed(reason="...")` pytest marker".
   - "Propose a plain module dictionary named" becomes "Q03 confirmed a
     plain module dictionary named".
   - "Propose a dedicated Python 3.12 virtual environment" becomes "Q06
     confirmed a dedicated Python 3.12 virtual environment".
   - "Propose an own-project whole-suite preflight" becomes "Q07 confirmed
     an own-project whole-suite preflight".
3. Q10 description: after "How should the gate keep its own defaults and
   the `-o`/project/default precedence?", add "Q09's recommendation
   describes reading presence explicitly, which is J2's mechanism; J1 or
   J3 keeps I1 and replaces that sentence at consolidation."

Convergence rationale:

Every round 4 correction is applied. The xdist validation path, fixture
adapter guard, binding check, preflight declaration and cache verification
now describe mechanisms that pytest 9.1 and xdist 3.8 support. They also
stay within the confirmed B1, D1, E1, G1 and H1 qualifications. Q10 is a
complete question with distinct options and a reasoned proposed answer.
The remaining edits are the covered wording, which changes no mechanism.
The next step belongs to the human: decide Q10. A follow-up review of that
decision is needed before consolidation. This recommendation is advisory
and does not authorize consolidation.

### Writer instructions for design-specification shared_lifecycle_gate round 5

1. Apply the covered wording in the context section, the confirmed-interface
   sentences and Q10's description. It does not need another automated
   round.
2. Keep the Q01 to Q09 blocks unchanged. Present Q10 to the user and
   record its decision only from the user's explicit choice.
3. Do not consolidate. After the user decides Q10, request a follow-up
   review of that decision before consolidation, as for Q01 to Q09.

### Final reviewer decision for design-specification shared_lifecycle_gate round 5

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-5 -->

## Round 5 by human - human-confirmation

- Recorded: 2026-11-07T00:21:53+01:00
- Exchange: specification/design-specification/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round

<!-- review-entry-id: human-confirmation-round-5 -->

## Round 6 by requestor

- Recorded: 2026-11-07T00:22:25+01:00
- Exchange: specification/design-specification/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for design-specification shared_lifecycle_gate (round 6)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
Review round: 6

### Requestor assessment for design-specification shared_lifecycle_gate (round 6)

All ten design questions have explicit human decisions. Q01-Q09 remain
A1/B1/C1/D1/E1/F1/G1/H1/I1, confirmed on 2026-11-06 and independently reviewed
through round 5. Q10=J1 was confirmed by the user's explicit chat selection
"1" on 2026-11-07 after its explanation and three-option choice.

The decision requires the plain-pytest root-conftest snippet to use
`pytest_addoption(parser, pluginmanager)` and register the lifecycle keys only
when `pluginmanager.has_plugin("llm_shared_lifecycle_gate")` is false. Gate
registration owns defaults when present; `config.getini` retains explicit
project settings and `-o` precedence. An outdated unguarded snippet can silently
replace defaults; the guard must be documented as part of the required snippet.

The options and rationale are sufficient, and I identify no additional question.
J1 retains Q09's confirmed I1 interface and replaces only the historical
presence-reading mechanism sentence during separately authorized consolidation.
That historical recommendation and all other question blocks remain intact.
The body points to Q10 pending consolidation; this decision does not authorize
consolidation, staging, commits or implementation.

Please independently examine Q10 and its recorded comments, whole-design
consistency, effects on Q01-Q09, requirement/design alignment and related
documents. Identify missing or new questions and surface any conflict with a
human decision rather than overwriting it. Verify that both loading orders,
absent keys, tracked values, command-line overrides, strict configuration and
warnings-as-errors are covered. The full decision scanner exits 0 with ten
confirmed questions, zero undecided and no diagnostics.

### Change summary for design-specification shared_lifecycle_gate (round 6)

Since round 5 reviewed SHA-256
`4501c7a85601fc88c5878e23da2dedfffd2bc54d35f7b0fef2e0059eaf88d209`:

- Applied every covered wording correction from the retained round 5 answer:
  context acknowledges pending Q10; confirmed interfaces no longer say
  proposed; the marker says use; Q10 explains how J1/J3 relate to Q09's
  historical presence-reading recommendation.
- Recorded Q10=J1 and the explicit 2026-11-07 human decision, rationale,
  unguarded-snippet limitation, validation expectations and Q09 relationship.
  Removed only Q10's active pending prose and marker.
- Preserved Q01-Q09 blocks, all Q10 options and its historical recommendation.
  No consolidation, implementation, staging or commit occurred.

Current design SHA-256:
`e99282900ba373197a60126ecd1e10512b50187d891092cf3d4b159b81819465`.

### Writer response for design-specification shared_lifecycle_gate (round 6)

Writer response:

Accepted all round 5 covered wording and its convergence assessment. The
original Q01-Q09 explanation batch is reviewed; the human explicitly selected
Explain undecided questions and then selected J1 for Q10. The separate Q10
batch therefore requires this independent follow-up review under the recorded
discussion authority.

No disagreement with the reviewer and no human decision overridden. Preserve
Q09's historical recommendation until consolidation; the Q10 answer explicitly
records how the chosen public guard supersedes that mechanism without changing
I1's requirement for plain-pytest registration and gate-owned defaults.

Please review the complete specification and new decision rather than treating
pre-decision round 5 convergence as its approval. Consolidation remains a
separate human choice after this follow-up review. Do not consolidate.

### Reviewer focus for design-specification shared_lifecycle_gate (round 6)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-6 -->

## Round 6 by reviewer

- Recorded: 2026-11-07T00:25:37+01:00
- Exchange: specification/design-specification/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification shared_lifecycle_gate round 6

I read the complete design (SHA-256
`e99282900ba373197a60126ecd1e10512b50187d891092cf3d4b159b81819465`) and the
round 6 request, and rechecked Q10 against the consolidated feature request
and the Q01 to Q09 decisions.

**The round 5 covered wording is applied.** Confirmed interfaces no longer
say "propose", the marker says "use", and Q10's description relates J1 and
J3 to Q09's presence-reading recommendation.

**The Q10 decision is recorded faithfully.** The answer block records J1 as
the user's explicit selection of 2026-11-07, with its rationale and the
unguarded-copy limitation. It also lists the validation expectations and
the Q09 relationship. The options, analogy and recommendation are
unchanged. No other question block changed.

**Q10 fits the other decisions and the requirement.**

- Q09 I1 stays confirmed. J1 keeps the plain-pytest root-conftest
  registration and meets I1's "defaults owned by the gate" through the
  gate's own registration. Only the recommendation's presence-reading
  sentence is superseded, and the answer says so for consolidation.
- Requirement: `config.getini` keeps the `-o`/project/plugin-default
  precedence and the four defaults, as requirement decisions Q07 and Q10
  require. No
  shared import or unknown key appears when the gate is absent.
- Q01 and Q08: the guard depends on the canonical plugin name. The
  bootstrap registers modules by their canonical names, and explicit
  `-p llm_shared_lifecycle_gate` loading and llm-shared's own canonical
  imports register the same name. The guard therefore sees the gate in
  every supported loading path.

**Coverage of the requested checks.** The acceptance row for the documented
snippet "in either loading order" covers absent keys (gate defaults),
tracked values and `-o` overrides with the gate loaded. The row for tracked
keys with the gate absent covers strict settings. Q10's answer names strict
configuration and warnings-as-errors for that case explicitly. Nothing is
missing.

**Wording left behind by the decision.**

- The context section still says "Q10 awaits a user decision".
- The settings paragraph still says "Q10 decides how the gate keeps its
  own defaults", where it can now state the chosen guard.
- The last acceptance row's basis still reads "Q07, Q10 pending".
- The documentation paragraph lists "tracked-key registration" without
  the guard, although J1 makes the guard part of the required snippet.

These edits change no mechanism.

**No question is missing and no decision conflicts.** Q01 to Q10 all carry
explicit user decisions. The remaining edits are wording only, so the
formulation can converge.

### Question verdicts for design-specification shared_lifecycle_gate round 6

All ten questions carry explicit user decisions: Q01 to Q09 dated
2026-11-06 and Q10 dated 2026-11-07.

- Q01 A1, Q02 B1, Q03 C1, Q04 D1, Q05 E1, Q06 F1, Q07 G1, Q08 H1, Q09 I1:
  agree; each is also my choice. Unchanged since round 5.
- Q10 J1: agree; it was also my choice. It meets Q09's gate-owned defaults
  with public pytest API, keeps the requirement's precedence and defaults,
  and documents its one limitation, an outdated unguarded snippet copy.

Outstanding human decisions: none on the questions. Consolidation stays a
separate human choice.

### Convergence evidence for design-specification shared_lifecycle_gate round 6

Covered wording:

1. Context section: replace "Q01 to Q09 below record the user's design
   decisions of 2026-11-06; Q10 awaits a user decision." with "Q01 to Q09
   below record the user's design decisions of 2026-11-06, and Q10 the
   decision of 2026-11-07."
2. "Measurement, limits and proof states": replace "Q10 decides how the
   gate keeps its own defaults and the `-o`/project/default precedence
   without deprecated or private pytest configuration access." with "Q10
   confirmed the guard: the snippet takes
   `pytest_addoption(parser, pluginmanager)` and registers the keys only
   when `pluginmanager.has_plugin("llm_shared_lifecycle_gate")` is false.
   The gate's own registration then supplies the defaults, and
   `config.getini` keeps the `-o`/project/default precedence without
   deprecated or private pytest configuration access."
3. Acceptance table, last row: replace the basis "Q07, Q10 pending." with
   "Q07, Q10."
4. "Temporary consumer trial and documentation": replace "tracked-key
   registration," with "tracked-key registration with its plugin-manager
   guard,".

Convergence rationale:

The round 5 covered wording is applied, and the Q10 decision is recorded
as the user's explicit choice with its rationale, limitation and validation
expectations. J1 is consistent with the confirmed Q01, Q08 and Q09
decisions and with the requirement's settings precedence and defaults. All
ten questions are decided, no question is missing, and the remaining edits
are covered wording that changes no mechanism. The next step belongs to the
human: choose whether to consolidate. This recommendation is advisory and
does not authorize consolidation.

### Writer instructions for design-specification shared_lifecycle_gate round 6

1. Apply the covered wording in the context section, the settings
   paragraph, the last acceptance row and the documentation paragraph. It
   does not need another automated round.
2. Keep the Q01 to Q10 blocks unchanged.
3. Do not consolidate unless the user chooses Consolidate at the
   convergence gate.

### Final reviewer decision for design-specification shared_lifecycle_gate round 6

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-6 -->

## Round 6 by human - human-confirmation

- Recorded: 2026-11-07T00:51:13+01:00
- Exchange: specification/design-specification/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-6 -->
