# Resume interrupted reviews

Use this instruction when a user asks to resume an interrupted specification or
code review. This is the only public resume entry point: do not create or call
a shell `rvw_resume` command.

The bare user request `resume` authorizes automatic ownership pickup after the
role and identity gates pass. Do not ask for a token, generation, new-session
declaration, pickup directive, or reclaim choice. Preserve role-session
isolation from `instructions/review-requestor.md` throughout this workflow.

## Inspect the interrupted review

Read [`../rules/run_commands.md`](../rules/run_commands.md), then run the
shared launcher from the caller repository:

```powershell
& "<LLM_SHARED_DIR>\bin\review_exchange.bat" migration-check
```

When migration check reports `migration-required`, run
`migrate-artifacts`, repeat `migration-check`, and stop on `blocked` or any
non-ready recheck. Read the final inspection result as typed JSON: do not infer
an exchange, role, or next action from filenames or prose.

Only after a ready recheck, run `resume-inspect`. Supply the invoked adapter's
schema-validated `llm_nature` as `--trusted-host-hint` when it names a known
host; omit the hint for `unknown` and use host detection. Do not infer a model
from its protocol role. Supply `--role requestor` or `--role reviewer` only
when the user selected that role.

## Continue the selected review role

`role-selection-required`, `confirmation-required`, and
`exchange-selection-required` require the stated human choice. Once inspection
returns `ready`, continue without another confirmation:

For multiple exchanges, show the returned candidates and use the human's
selection as `--document <returned-document>` on inspection and claim. Carry
the returned `--implementation-step` for code exchanges sharing a plan. For a
role conflict show both natures and all returned evidence and ask `Override`
or `Stop`; only an explicit `Override` permits `--override` for this attempt.
Stop on blocked, inconsistent, interrupted, or escalated evidence.

For every selected concrete live exchange, run automatic `claim` before
dispatching the role. Copy the document, round and occurrence from inspection:

```powershell
& "<LLM_SHARED_DIR>\bin\review_exchange.bat" claim --document <document> --role <role> --round <round> --occurrence <occurrence>
```

Carry the same known host hint and approved override into this call. If the
session already holds a capability, pass its paired `--ownership-generation`
and `--ownership-token`; repeating the claim with that valid pair is
idempotent. If that pair is stale, or absent, claim performs lease-independent pickup even with a fresh
lease. Keep the returned pair only in the session and pass it to every later
fenced command. Never save it to files, environment variables, or transcripts.
If the selection changed, inspect again; do not guess a new identity. A claim
does not authorize the human convergence choice or a commit.

Intact expired leases do not stop global waiting or selected resume. The
support operations accept lease-only abandonment while retaining migration,
damaged-artifact, identity, and locked selection gates. A global reviewer leaves
expired answers and requestor-owned work untouched and keeps waiting; only a
pending or abandoned request is eligible for its atomic claim.

Dispatch the action from the successful claim (or idle inspection):

- `review-request` routes to the matching specification or code reviewer.
- `wait-exact-answer` routes to the matching requestor's exact answer wait.
- `continue-requestor` routes to the requestor's owned action.
- `follow-workflow` runs and follows `pw skill`.
- `wait-any-request` runs the quiet foreground command below.

For a global reviewer wait, run one foreground process and await its final JSON
result without an LLM polling loop:

```powershell
& "<LLM_SHARED_DIR>\bin\review_exchange.bat" wait-any-request
```

The command emits no idle output. `found` exits 0 and includes the session-only
ownership capability; `ambiguous` and `cancelled` exit 3; invalid input and an
operational failure exit 2. A graceful host or console interruption is
`cancelled`; a hard process kill may produce no result. Do not persist a waiter,
start writer work from a reviewer route, or use a requestor route to consume an
arbitrary future request.

On `found`, retain the returned capability. Run `resume-inspect` for the
selected document and step with `--role reviewer` and the same host hint.
Apply the selected-role identity gate, including Override or Stop when needed,
then run `claim` with the returned capability pair for idempotent identity
completion. Never issue an unqualified pickup for a request already claimed
by this wait. Use the selected candidate's
family, document, umbrella, step, round, and occurrence to enter its existing
reviewer instruction, and run exact `status` to obtain `paths.request`. The
reviewer reads only that current request. After every answer, including an
intermediate answer or convergence, enter `wait-any-request` again. Never
start a requestor or run `pw skill` from a reviewer route.

A requestor enters its specification or code requestor instruction with the
selected exact context and capability. It consumes an available answer,
waits for that exchange's exact answer, presents an existing convergence gate,
or resumes an already authorized owning action according to durable status.
After exchange release, run and follow `pw skill` immediately. Never consume
an arbitrary request or start a reviewer from a requestor route.
