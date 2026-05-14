# vX.Y.Z {topic} implementation plan -- {short subtitle}

{One-line theme sentence that explains the implementation shape for this version.}

- **{Theme line 1}**: {Short summary of one major implementation thread}.
- **{Theme line 2}**: {Short summary of one major implementation thread}.
- **{Theme line 3}**: {Short summary of one major implementation thread}.

## Plan goal for vX.Y.Z {topic}

Implement the full vX.Y.Z {topic} feature set as described in `docs/design.vX.Y.Z.{topic}.md` and any linked requirement document, targeting the confirmed outcomes in ordered implementation steps.

- **Step 0 goal**: {Perf-gate baseline, test-first guard, or first setup step if relevant}.
- **Step 1 goal**: {First implementation slice}.
- **Step 2 goal**: {Second implementation slice}.
- **Step N goal**: {Final integration, acceptance, tooling, or rollout slice}.

{Add Step N.1 follow-up goals when the repo needs an inserted cleanup, split, or alignment slice between two main steps.}

---

## Scope anchors for vX.Y.Z {topic} plan

This plan implements the design from `docs/design.vX.Y.Z.{topic}.md` and any linked requirement document, targeting the following outcomes:

1. {Outcome 1}.
2. {Outcome 2}.
3. {Outcome 3}.

The following are explicitly **in scope** for this plan:

- {Delivered capability, interface, or flow}.
- {Delivered capability, interface, or flow}.
- {Delivered capability, interface, or flow}.

The following are explicitly **deferred** to {next version} and beyond:

- {Deferred item}.
- {Deferred item}.

---

## Complexity Bound Clarification for vX.Y.Z

The scaling target for all vX.Y.Z code paths is:

- **O(1) amortized per hot-loop event**: {Per request, per message, per line, or per lookup bound}.
- **O(n) total per phase**: {Startup, pruning, bounded iteration, or loading bound}.

No vX.Y.Z code path should introduce `O(n^2)` or `O(n log n)` cost on the response path. Any new path that breaks this bound must be called out as a defect before merge.

---

## File-based IO cost clarification for vX.Y.Z {topic}

{Keep this section aligned with the design document. Use a bullet list for a short rule set, or replace it with a four-column IO classification table when several read and write paths need explicit classification.}

- No directory scan on the response path.
- All blocking CPU or filesystem work moved off the event loop when the feature is async.
- All persisted state writes use the required atomic-write pattern for this repo.
- In-memory caches or stores remain the first read path when the design requires bounded response-path IO.

---

## Confirmed technical facts for vX.Y.Z plan viability

These facts should be drawn from direct code inspection of the current repository tree.

**Files at or approaching the 550-line risk threshold** (must not grow in place):

- `{path/to/file.py}`: **{line_count} lines** -- {Line-budget rule or split guidance}.
- `{path/to/file.py}`: **{line_count} lines** -- {Line-budget rule or split guidance}.

**Files safe to extend** (current lines, expected additions):

- `{path/to/file.py}`: {current lines} -- {Expected additions and why this file is still safe}.
- `{path/to/file.py}`: {current lines} -- {Expected additions and why this file is still safe}.

**What does not exist yet (all new for vX.Y.Z)**:

- `{new/module/or/package/path}`.
- `{new/module/or/package/path}`.

**Other confirmed technical facts that affect plan shape**:

- **{Dependency or packaging fact}**: {Why it matters for implementation}.
- **{Runtime or browser fact}**: {Why it matters for implementation}.

---

## Current test-tree validation snapshot for vX.Y.Z {topic}

Existing test packages that vX.Y.Z must not break:

- `{existing test package}` -- {Current size, limits, or note about where new tests should go}.
- `{existing test package}` -- {Current size, limits, or note about where new tests should go}.

New test leaf directories to create for vX.Y.Z:

- `{new test package path}`.
- `{new test package path}`.

---

## Runtime file note for vX.Y.Z {topic} plan

{Use this section only when the plan adds generated or runtime-only files under ignored paths. If it is not relevant, remove the section.}

- `{runtime/generated/file}` -- {Why it appears and whether `.gitignore` already covers it}.
- `{runtime/generated/file}` -- {Why it appears and whether `.gitignore` already covers it}.

---

## Shared execution command checklist for all vX.Y.Z {topic} steps

Apply this checklist for every numbered step, filling in the step-specific paths.

1. Count lines before edits on all step files: `{line-count command}`.
2. Apply tests-first changes as described under the step implementation section.
3. Run the step-targeted test command.
4. Run the step grep checks.
5. Run the shared gate loop until both the focused tests and the repo gate pass in the same cycle.
6. Count lines after edits and compare them with the step line-budget checkpoint.
7. If any Python file exceeds the repo line-limit rule after edits, stop and apply the split guidance before committing.

---

## Ready-to-run command templates for all vX.Y.Z {topic} steps

Use these template forms in each step, substituting actual paths.

- Line count before: `{line-count command}`
- Targeted tests: `{pytest command}`
- Grep checks: `{rg command}`
- Shared gate loop: `{focused tests}; {repo gate command}`
- Line count after: `{line-count command}`

---

## Shared timeout target policy for vX.Y.Z {topic} perf-complexity gates

{Use this section only when the plan has step-owned perf gates or time-bound responsiveness checks. If it is not relevant, remove the section.}

- Add focused event-loop responsiveness gates with the agreed timeout and synthetic fixtures only.
- Mark each Step 0 gate with explicit owning-step text when the work is still pending.
- Remove the `xfail` or placeholder status in the owning step when the implementation lands.

Gate-to-step ownership for vX.Y.Z:

- `{perf gate name}` -> remove placeholder status in Step {N}.
- `{perf gate name}` -> remove placeholder status in Step {N}.

---

## Numbered steps for vX.Y.Z {topic}

### Step N. {step title}

#### Step N -- analysis and intent for {topic or area}

Issues to address:

- {Issue 1}.
- {Issue 2}.

Fix intent:

- {Implementation intent 1}.
- {Implementation intent 2}.

Expected outcome:

- {Expected result 1}.
- {Expected result 2}.

Step framing:

- Design link: {Design section, decision, or requirement anchor}.
- Execution checklist reference: {Name of the shared execution checklist section in this document}.

#### Step N -- implementation for {topic or area}

**Files involved**:

- `{path/to/file}` ({new|update|delete}).
- `{path/to/test_file}` ({new|update|delete}).

**Tests first**:

- {Test additions or updates}.
- {Property test, perf gate, or regression guard when relevant}.

**Classes and behavior**:

- `{Type, function, route, or script}`: {What it must do}.
- `{Type, function, route, or script}`: {What it must do}.

**Completion criteria**:

- `{pytest command}`.
- `{rg command}`.
- {Observable outcome that proves the step is done}.

#### Step N -- addendums for {topic or area}

Line-budget checkpoint:

- `{path/to/file}`: before {x} -> target <= {y}.
- `{path/to/test_file}`: before {x} -> target <= {y}.

Split guidance:

- {What to extract if a main file grows too far}.

Full workflow timing run readiness:

- `{focused tests}; {repo gate command}`

Time-gated status for Step N:

- {Perf gate to remove, timeout target to keep, or say that no perf gates are affected}.

---

{Repeat the Step N block for each implementation slice. Use Step N.1 when the plan inserts a follow-up slice between two main steps. Keep the document at implementation level only: files, tests, commands, budgets, rollout order, and completion checks.}
