# Review requestor coordination instruction

Use this instruction when a specialized writer workflow delegates a review
exchange to the shared requestor role. The specialized workflow still owns its
analysis, edits, response text, convergence assessment, and any action approved
by a human. This instruction owns only the common coordination sequence.

## Command boundary for review requestors

Resolve `<LLM_SHARED_DIR>` as the absolute parent of the `instructions` folder
that contains this canonical file. Do not resolve a launcher against the
consuming repository, guess a sibling `llm-shared` folder, or rely on an
`LLM_SHARED_DIR` environment variable. Every shared review launcher self-locates
its llm-shared Python, so call it directly by the resolved full path from
PowerShell; do not run either repository's `senv.bat` first.

Run every protocol operation through
`& "<LLM_SHARED_DIR>\bin\review_exchange.bat"`. That launcher is the
non-interactive adapter over `ReviewExchangeCore`; do not reproduce its state
transitions in an LLM instruction and do not mutate review artifacts by hand.

Every command takes an operation followed by the exact context arguments:

```powershell
& "<LLM_SHARED_DIR>\bin\review_exchange.bat" <operation> --family <specification-or-code> --document <exact-path> --umbrella <exact-path-when-present> --implementation-step <code-step-when-applicable> --convergence-signal <registered-token> --another-round-label <registered-label> --continue-owning-workflow-label <registered-label>
```

Omit `--umbrella` when there is no umbrella. Omit `--implementation-step` for
specification review. Do not search for a nearby document when the supplied
exact path is missing or invalid.

Both roles must pass the *same* context, because every operation compares the
context built from these arguments against the one stored in the request
artifact and the coordination record. A role that omits an umbrella the other
supplied gets `state: inconsistent` and the diagnostic `artifact context
differs from core context; coordination context differs from core context`,
which names two differences but neither the field nor the flag. That is a
mismatched invocation, not a damaged exchange: `reclaim`, `resolve` and
`archive` are all wrong answers to it. Re-run `status` with the umbrella
included before concluding anything about the exchange. `pw` names it on the
routed command as `with umbrella <umbrella-draft>`, and it is also readable
from `umbrella_path` in the published request envelope and from
`context.umbrella_path` in the coordination record.

## Caller-owned Markdown inputs for review requestors

Create substantive input as UTF-8 files inside the configured artifact home,
`.reviews` by default. Each name must follow the effectively ignored `a.*`
convention. The launcher checks the location, name, Git ignore result,
existence, and UTF-8 encoding before it reads a file once. It never deletes a
caller-owned input.

### One artifact home holds every runtime review file

Every review artifact is home-local: the request, answer, coordination record,
tombstone, transition lock, archives, retained code-review evidence, the
`a.review-mode` marker, guidance, question state, the migration journal, and
every caller-owned input and renderer output either role writes. Do not create
a review scratch file at the project root, and do not read one from there.

The home is repository-local and declared once in `.review-artifacts.ini`:

```ini
[review-artifacts]
home = .reviews
```

Without that file the home is `.reviews`. It is created with a home-local
`.gitignore` holding exactly `*`, so everything inside it is effectively
ignored, and it may never be the repository root or an existing tracked
directory. Read the effective home from `ReviewArtifactConfiguration`, or
derive it from any path a launcher returns in `paths`, rather than assuming the
default.

The reviewed document and its versioned transcript are the deliberate
exceptions. They are tracked project documentation: the transcript stays beside
the document it records, never under the home.

### Caller-owned paths are never protocol artifact paths

An `a.*` name is necessary and not sufficient, and neither is living in the
artifact home: protocol artifacts and caller scratch files now share that
directory, so placement no longer separates them. Every path in the `paths`
object a launcher returns — `request`, `answer`, `tombstone`, `coordination`,
`transition_lock` — carries an ignored home-local `a.*` name, and each one is
owned by the shared core alone. A caller-owned input or renderer output must
never be one of them. Choose a name that cannot collide, such as
`.reviews/a.spec-review.answer-content.<slug>.md`, and pass it to
`--answer-content-output` or `--request-content-output`; publication then
copies that content into the protocol path itself.

Writing a rendered artifact straight to `paths.request` or `paths.answer` does
not publish it, and it is not a shortcut for publication. It creates a live
artifact the exchange never recorded: the transcript gains no entry, the
coordination record is not advanced, and the counterpart artifact is not
consumed. The next `status` then observes a request and an answer at once,
which `_classify_invalid_live_shape` treats as mutually exclusive, and every
later operation reports `state: inconsistent` before any status or lease logic
runs. The round cannot proceed and cannot be reclaimed, because the fault is a
shape the protocol forbids rather than a lease that lapsed. Render to a
scratch output, then publish; never render onto the artifact.

Use the shared `templates/review-request.template.md` shape for complete
request or answer content. Start the Markdown with one `#` title, make
`## JSON` its first section, put the fenced JSON envelope inside that section,
and start every later top-level authored section at `##`. Pass that complete
Markdown through `--content-file`. Pass only the complete substantive content
to append to the transcript through `--summary-file`. Optional human guidance
enters through `--guidance-file`.

Before publishing a request, its human-readable authored content must include
each applicable identity field exactly once:

- `Umbrella draft: <exact-path>` or `Umbrella draft: none`
- `Reviewed specification: <exact-path>` for specification review
- `Implementation plan: <exact-path>` for code review
- `Implementation step: <identifier>` for code review
- `Review round: <positive-number>`

The envelope and these fields must agree with the command context and current
coordination round. Leave specialized findings, repair reports, assessments,
and recommendations to the calling workflow.

### Heading rules for authored review content

Every round is appended to a transcript that already holds the earlier rounds,
so a heading is written once but read inside a growing document. Two rules
follow, and they bind requestor and reviewer content alike:

- **Exactly one top-level heading per transcript, which is its title.** Author a
  round's own title at `##` or deeper, never at `#`. A `#` inside appended
  content gives the transcript a second top-level heading and breaks its
  outline.
- **Every heading text must be unique within the transcript.** A bare
  `## Evidence` or `### Findings` is unique in the round that writes it and
  duplicated the moment the next round appends the same word.

Qualify each authored heading with what actually makes it unique, choosing the
discriminator that explains the repetition rather than a counter. Any heading
that belongs to a review round ends with `(round N)`:

- the step and round, for content inside one exchange, as in
  `#### Evidence for step 5 topic (round 2)`;
- the exchange, where a transcript accumulates several exchanges over one
  document and each restarts at round 1, as in
  `### Evidence for topic (exchange 2) (round 1)`.

The paired specification- and code-review renderers apply this rule at the input
boundary. Their generated request sections are level 2 and their generated
transcript sections are level 3, so headings inside caller-authored assessment,
implementation, change-summary, guidance, response, and reviewer prose are
shifted to level 3 or level 4 respectively while their relative depth is
retained. Human guidance is rendered as its own Markdown block below the
`Human guidance:` label. Each embedded heading is then qualified with the step
or specification identity, slug, exchange when applicable, and final
`(round N)` suffix. Fenced code examples remain literal.

Titles must also be well formed: no doubled word from interpolation, so
`step 5` and never `step step 5`, and no trailing punctuation.

A transcript a Markdown linter reports `MD024` or `MD025` on is a defect in the
round that appended to it, not in the linter configuration. Neither rule may be
disabled to make a transcript pass.

## Role-session isolation

Role assignment is an external orchestration boundary, not an exchange
operation. A requestor must never spawn, start, delegate, invoke, or message a
reviewer agent or reviewer session. This prohibition includes subagents, child
agents, agent-assignment tools, direct model calls, reviewer skills or prompts,
and `pw skill code-reviewer` or `pw skill spec-reviewer`. A `request-pending`
route makes work available to an independently running reviewer; it does not
authorize the requestor to create that reviewer.

Immediately after publishing a request, the requestor's only automated next
action is the same session's bounded `wait-answer`. Run it even when no reviewer
appears to be active. If the wait stops, report its durable outcome; never fill
the missing counterpart role. The reviewer must already be waiting or must be
started independently by the human or an external reviewer service that the
requestor does not control.

A reviewer must reject an invocation initiated by an automated requestor or by
a parent agent acting as requestor, even when `pw` can resolve a valid pending
review route. Only a reviewer already waiting independently, or one started by
the human or an external reviewer service, may enter `wait-request` and assess
the request. This provenance check happens before any review command, file read,
assessment, repair, or answer publication.

The boundary is reciprocal. A reviewer must never spawn, start, delegate,
invoke, or message a requestor agent or requestor session. This includes
subagents, child agents, agent-assignment tools, direct model calls, requestor
skills or prompts, and `pw skill code-review-requestor` or
`pw skill spec-review-requestor`. Publishing an answer is the whole handoff to
the existing requestor role. After `changes-requested`, the reviewer waits for
the next round with `wait-request`; after convergence or a terminal handoff, it
waits for any specification or code request through the configured artifact
home and its global monitoring mechanism.

If the global monitoring mechanism has not shipped, its absence never
authorizes the reviewer to create a requestor. The reviewer remains available
under the specialized reviewer's documented interim wait instead. A requestor
must reject an invocation initiated by an automated reviewer or by a parent
agent acting as reviewer before any requestor command, file read, workflow
mutation, or response processing.

## Automated requestor sequence

Intermediate rounds use reciprocal active waits across the two agent sessions.
After the requestor publishes a request, it waits for the answer. After the
reviewer publishes a `changes-requested` answer, that same reviewer invocation
waits for the replacement request. The requestor consumes the answer, updates
the reviewed work, continues the round, and publishes that replacement while
the reviewer is already waiting. No human prompt or new reviewer invocation
belongs between those actions. Each role runs one bounded protocol wait for its
counterpart rather than an external polling loop. A convergence answer ends this
automatic exchange at the durable human gate, which ends the reviewer's rounds
but not its session: the reviewer moves to its artifact-home wait and stays
available for the next request, so a requestor may publish a fresh exchange
without arranging a new reviewer invocation.

1. Call `status` with the exact context. Exit `3` with outcome `disabled` means
   the calling workflow follows its existing non-review path and creates no
   exchange artifacts.
2. Call `activate` before the first mutation. It validates the marker, Git
   repository, and effective ignore coverage. Call `start` only for an idle
   exchange.
3. Finish the request content and transcript summary files, then call
   `publish-request --content-file <path> --summary-file <path>`.
4. Without invoking or contacting a reviewer, call `wait-answer` once. This is
   one bounded in-process wait, not repeated
   short slices. Progress JSON is written only to standard error. Read the
   single final standard-output object after the command returns.
5. Read only the exact answer path returned in `paths.answer`. Let the
   specialized workflow assess or apply that feedback outside the protocol
   command.
6. For an intermediate answer, call `consume-answer` with
   `--reviewed-work-changed true` or `false` and add `--disagreement` only for
   an explicit disagreement. If automation remains active, call `continue`,
   author the replacement request, publish it, and wait again. The reviewer is
   already in its post-answer `wait-request`; successful replacement
   publication releases that wait into the next reviewer assessment.
7. At convergence, retain the answer and present the specialized assessment,
   reviewer recommendation, identity summary, and registered labels to the
   human. The reviewer cannot call `confirm`.
8. Pass the selected display label to `confirm --choice-label <label>`. Add
   `--guidance-file <path>` only when the human supplied guidance. Another
   round returns active authority for a replacement request. A continuing
   outcome returns `owning_action_authorized: true`.
9. Perform the specialized owning action only after that durable authorization.
   Call `complete` only after the action succeeds. If a later session reports
   the pending authorization again, do not ask the human twice; finish the
   authorized action and call `complete`.

## Escalation and recovery commands

Use `reclaim` when `status` reports a round abandoned only because its lease
expired while the expected actor was still working. It renews the durable
lease in place and restores the pending round without touching any request,
answer, or transcript content; it is idempotent while the round stays live.
Reclaim never applies once an escalation is recorded, and it never repairs an
interrupted or inconsistent exchange.

Use `reclaim --force --summary-file <path>` only when a human decides that a
recorded escalation was a stopped handoff rather than a failure, typically when
the exchange continues as a manual back-and-forth after an automated wait timed
out. The forced resume requires an escalated exchange whose request, answer, and
transcript are intact; it restores the same round number and hands it back to
the actor its artifact shape names, and it appends the authored summary to the
transcript as durable evidence. It never repairs an interrupted or inconsistent
exchange, and no automated role may substitute it for `resolve` or `archive`.

Use `complete --force --summary-file <path>` only when a human explicitly
decides to close an `abandoned-mid-round` exchange instead of resuming it. The
forced completion requires the intact artifact-free abandoned shape, appends
the authored decision to the transcript idempotently, and then removes only
the coordination record. It does not manufacture convergence, authorize an
owning action, or replace normal `complete`; an automated role may not choose
it without the human's explicit close decision.

Use `repair-request-transcript --summary-file <path>` only when a pending
request is the final transcript entry and a restarted exchange exposed a
legacy round-one identity collision. The requestor supplies the same
substantive summary with headings qualified by `(exchange N)`; the core keeps
the durable request artifact, replaces only that final legacy entry through
the existing crash-repair marker, and assigns the request a unique
`request-round-N-exchange-M` footer. It rejects non-final, first-exchange, and
non-request-pending shapes.

Use `escalate --summary-file <path>` when the specialized workflow must stop
automation with an authored reason. Use `cancel --summary-file <path>` for a
human cancellation at convergence.

An escalated exchange stays stopped until a human identifies authoritative
evidence. Record that decision in an ignored home-local summary file, then call
`resolve --summary-file <path>` to clear stopped evidence or
`archive --summary-file <path>` to preserve it under derived archive names.
Both operations start a fresh round. Do not resume the interrupted transition.

## Result and exit contract for review requestors

Every invocation writes exactly one final JSON object to standard output with
the applicable `operation`, `identity`, `state`, `outcome`, `round`, `paths`,
and `diagnostic` fields. A wait may write periodic JSON diagnostics to standard
error and nothing else to standard output before that final object.

- Exit `0`: the operation completed and the returned state grants its reported
  next action.
- Exit `3`: an expected protocol stop such as disabled mode, timeout,
  abandonment, inconsistency, pending repair, escalation, human confirmation,
  or a pending human-authorized owning action.
- Exit `2`: invalid input or an unexpected fatal error. Stop and report the
  diagnostic without editing protocol artifacts manually.

Use `wait-request` and `publish-answer` only when a specialized reviewer adapter
delegates those counterpart operations to this same command surface.
