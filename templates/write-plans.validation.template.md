# vX.Y.Z {topic} implementation tracking and validation

{Yes/No this step was implemented}. (no detail, the first sentence MUST be "Yes, it is implemented" or "No, it is not implemented", as based on the current diff and repository state, and followed by an empty line).
(empty line)
{One-line theme sentence that explains what this implementation review is tracking. And, if it is not yet implemented, what is missing as a short summary (a more complete section will follow in the detailed analysis).}

---

## File-based IO cost clarification for vX.Y.Z {topic} (implementation)

All implementation work must respect the IO classification established in `docs/plan.vX.Y.Z.{topic}.md`. The key constraints carried forward from the plan are:

- {Constraint 1}.
- {Constraint 2}.
- {Constraint 3}.
- {Constraint 4}.

---

## Complexity Bound Clarification for vX.Y.Z (implementation)

The scaling target for all vX.Y.Z code paths is:

- **O(1) amortized per hot-loop event**: {Per request, per message, per line, or per lookup bound}.
- **O(n) total per phase**: {Startup, pruning, bounded iteration, or loading bound}.

Every implemented step should be reviewed against this bound in its Performance check section.

---

## Step N. {step title}

### Analysis of Step N implementation state

{Start with a direct status statement such as `Yes. Step N has been fully implemented.` or `No. Step N is still incomplete because ...`. Base the conclusion on the current diff, repository state, and focused validation results.}
{On the first write, the sentence must be: "Not started. Step N is not implemented because ...". On subsequent writes, the sentence must be updated to reflect the current state.}

### Goal for Step N

{Restate the planned goal from `docs/plan.vX.Y.Z.{topic}.md` in one short paragraph.}

### Step N improvement expectations

- {Expected behavior 1}.
- {Expected behavior 2}.
- {Expected behavior 3}.

### What was implemented for Step N

{Explain what the current diff and repository state actually delivered. Use concrete bullets and include focused validation evidence when available.}

- **{Area 1}**: {What changed and why it matters}.
- **{Area 2}**: {What changed and why it matters}.
- **Validation evidence**: {Focused tests, grep checks, or repo gate results that support the conclusion}.

### Missing work for Step N

{This section is mandatory whenever the `Analysis of Step N implementation state` status above is anything other than a full "Yes, it is implemented": "No, it is not fully implemented", "partially implemented", "mostly implemented" all require it, even when the section was absent from the document before this check. Gather here every gap, even those already described in the Architecture, Performance, Unit test coverage, or Feature integrity sections: this is the single work list read by `implement-missing-step.md`. Omit this whole section only when writing the initial empty skeleton of this document (no check has taken place yet, since no step is implemented), and remove it when a later check finds the step implemented, since its work list is then done.}

- {Missing element 1: code, test, wiring, or a file over the line budget — concrete enough to implement without re-deriving the analysis}.
- {Missing element 2}.

### New types or classes introduced for Step N

- `{Type, class, helper, or test suite}`: {Role}.
- `{Type, class, helper, or test suite}`: {Role}.

{If the step introduced no new production type, say so directly and explain whether the step was completed with functions, wiring, or test-only support code instead.}

### Architecture check for Step N

- **{Layer or package area}**: {Why the placement is correct, or what smell still needs watching}.
- **{Boundary direction}**: {Why imports and responsibilities still follow the repo's architecture}.
- **{Split or maintainability note}**: {Optional note about file size, helper extraction, or package surface}.

{Close the section with a short conclusion that states whether a DDD-Hexagonal violation or adapter smell is visible in the current step.}

### Performance check for Step N

- **No new `O(n^2)` or `O(n log n)` path**: {State the conclusion and why}.
- **Hot-path bound**: {Explain the request-path or loop-path cost}.
- **Startup or background path**: {Explain the startup, cleanup, or background-task cost when relevant}.
- **Plan-bound alignment**: {Explain whether the step stays inside the bound promised by the plan}.

{Close the section with a short conclusion that states whether the step stays inside the plan's complexity target.}

### Unit test coverage check for Step N

{This is only for unit test, not for integration, smoke, regression or acceptance tests.}

- **{Class or function}**: {State whether it is covered at 100% or not, and if not, what is missing}.
- **{Class or function}**: {State whether it is covered at 100% or not, and if not, what is missing}.
- ...

No, there is no unit-tested class below 100% that needs completing for Step N.

Or

Yes, there is a unit-tested class below 100% that needs completing for Step N: {Class or function} is covered at {coverage percentage}%, missing tests for {missing cases or lines}.

### Feature integrity for Step N

- **Existing feature behavior**: {State whether any existing route, service, or workflow was impaired}.
- **Reporting or diagnostics**: {State whether logs, warnings, status payloads, or reporting signals were preserved or extended}.
- **Compatibility or rollout note**: {State any intentional behavior change, preserved alias, or follow-up watch point}.

{Close the section with a short conclusion that states whether any existing feature or reporting capability appears impaired.}

---

{Repeat the Step N block for every planned implementation step. Keep this document review-only: compare the current state to the plan, record evidence, call out incomplete work, and avoid new design-choice questions.}
