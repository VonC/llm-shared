# vX.Y.Z {topic} implementation tracking and validation

{Yes/No this step was implemented}. (no detail, the first sentence MUST be "Yes, it is implemented" or "No, it is not implemented", as based on the current diff and repository state, and followed by an empty line).
(empty line)
{One-line theme sentence that explains what this implementation review is tracking. And, if it is not yet implemented, what is missing as a short summary (a more complete section will follow in the detailed analysis).}

> Initial-skeleton note: the first version of this document (written by the
> `write-plans` skill, before any implementation check) does not use the `{...}`
> guidance below for the per-step check sections. It fills `Goal for Step N` and
> `Step N improvement expectations`, opens every `Analysis of Step N
> implementation state` with "Not started. Step N is not implemented because ...",
> and fills every other section (`What was implemented`, `New types or classes
> introduced`, `Architecture check`, `Performance check`, `Security check`,
> `Unit test coverage check`, `Feature integrity`) with the literal placeholder
> `_(empty — no check has taken place yet.)_.`. The `{...}` guidance below applies
> only once an implementation check replaces those placeholders.
>
> Markdown lint note: never leave a space immediately inside an inline code span
> (MD038) -- write a needed space as the token `[space]`, as in `` `[space]${x}` ``.
> The empty placeholder ends in `)_.` so the line is not pure italic text (MD036).

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

{Start with a direct status statement: `Yes. Step N has been fully implemented.` or `No. Step N has NOT been fully implemented.` Base the conclusion on the current diff, repository state, and focused validation results. On the first write, the sentence must be: "Not started. Step N is not implemented because ...". On subsequent writes, the sentence must be updated to reflect the current state.}
(empty line)
{short summary of why the step is considered implemented or not, and what is missing if it is not yet implemented, knowing that a detailed list of what is missing is provided in the `Missing work for Step N` section.}

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

### Security check for Step N

- **Input validation & sanitization**: {State whether all step inputs/parameters are strictly validated and sanitized}.
- **Safe execution & resource access**: {State whether system calls, filesystem paths, and resources are accessed safely without injection or traversal risks}.
- **Data protection & logging**: {State whether sensitive information, secrets, or internal stack traces are prevented from leaking in logs, errors, or commits}.

{Close the section with a short conclusion that states whether any security vulnerability or smell is visible in the current step.}

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

{Repeat the Step N block for every planned implementation step, followed by the mandatory Step Final security review block below.}

---

## Step {Final}. Final Security & OWASP Top 10 Review

### Analysis of Step {Final} implementation state

{Start with: `Yes. Step Final has been fully implemented.` or `No. Step Final has NOT been fully implemented.`}

(empty line)
{Short summary of the security audit results.}

### Goal for Step {Final}

Audit the cumulative changes against the OWASP Top 10 vulnerability matrix and verify that no side effects or regressions are introduced.

### What was implemented for Step {Final}

- **Audit execution**: {Summary of static checks, dependency scan, secret scan, and code inspection}.
- **Validation evidence**: {Audit output, security test suite pass, zero High/Critical findings}.

### OWASP Top 10 Audit Findings Matrix

| OWASP Category | Applicable? | Findings / Evidence | Status (Pass/Fail) |
| --- | --- | --- | --- |
| A01 Broken Access Control | {Yes/No} | {Checked path traversal, permissions, access checks} | {PASS/FAIL} |
| A02 Cryptographic Failures | {Yes/No} | {No hardcoded secrets, verified sensitive-hooks} | {PASS/FAIL} |
| A03 Injection Flaws | {Yes/No} | {No raw shell execution, parameter injection, or SQLi} | {PASS/FAIL} |
| A04 Insecure Design | {Yes/No} | {Trust boundaries and fail-safe defaults respected} | {PASS/FAIL} |
| A05 Security Misconfiguration | {Yes/No} | {No debug/verbose error leaks in production paths} | {PASS/FAIL} |
| A06 Vulnerable Dependencies | {Yes/No} | {Dependency audit check confirmed no known CVEs} | {PASS/FAIL} |
| A07 Auth & Identification | {Yes/No} | {Authentication and session controls intact} | {PASS/FAIL} |
| A08 Software/Data Integrity | {Yes/No} | {Safe serialization/deserialization confirmed} | {PASS/FAIL} |
| A09 Logging & Monitoring | {Yes/No} | {Sanitized logs, no credentials/PII logged} | {PASS/FAIL} |
| A10 SSRF / Remote Fetch | {Yes/No} | {Network endpoints and fetch targets strictly bounded} | {PASS/FAIL} |

### Security Review Conclusion

{State clearly if the effort is certified free of major OWASP Top 10 vulnerabilities or if remediation is required.}
