# Legacy routing to JSON: study for resume-paused

This study answers the request recorded with design Q01=B on 2026-11-09: can
an older pause whose routing exists only as a readable table become a pause
that bulk launch can route, and at what risk? It extends the
[design's migration study](design.v0.14.0.resume-paused.md#legacy-routing-migration-study)
with what Step 2 of [the implementation plan](plan.v0.14.0.resume-paused.md)
now parses. It is a study, not an approved converter: no conversion runs in
bulk discovery, preview or delivery, and none is implemented.

## What the Step 2 reader accepts as routing

Bulk launch reads routing only from one fenced block opened by the line
`` ```json resume-paused-routing ``, holding schema `resume-paused-routing`
version 1 (`tools/resume_paused_routing.py`). A readable table rendered from
that object, headed `| Routing item | Value |`, may follow it and must then
equal the rendering line for line.

| Prompt content | Reader outcome | Bulk launch |
| --- | --- | --- |
| No routing block and no routing table | Routing absent | Skipped; manual `resume-session` unchanged |
| A routing table only, of either form | Routing table-only | Skipped; manual `resume-session` unchanged |
| One valid block, all targets known | Routing resolved | Eligible for the later planner checks |
| One valid block with an explicit `{"unknown": reason}` part | Routing unresolved | That target skipped; the rest of the pause kept |
| Two blocks, the legacy table beside a block, or a differing rendered table | Routing error | Checkout fails without input |
| Malformed JSON, a repeated key, an unknown key or version | Routing error | Checkout fails without input |
| Block identity differing from the prompt header | Routing error | Checkout fails without input |

The prompt header keeps the grammar the installed `tuitp` reads: the first
line `# <agent-id>: Resume session: <title>` and the `- Session role:` line.
A routing block adds lines after them and changes neither.

## The legacy table and why it cannot be read as routing

The pause template on this branch documents a table with the header
`| Target | Agent host and intended role | TUIOS session identity | ...`,
plus bullet lines such as `- Pausing pane:` and `- Review pairing:`. Its cells
are free prose filled by an agent: a host and a role in one cell, a pane id
next to its label, evidence sentences, and placeholders such as "not
applicable" or "unknown" with or without a reason. The canonical main
template has no routing section at all.

| Routing part | Where the legacy table holds it | Gap for a strict reader |
| --- | --- | --- |
| Pause checkout and snapshot | `- Routing checkout:` and the prompt header | Recoverable from the header |
| Pausing pane | `- Pausing pane:` prose | Host, session, UUID and label share one sentence |
| Target role and host | One cell, such as "Claude, requestor" | No fixed order or vocabulary |
| TUIOS session and pane UUID | Two cells, the UUID often shortened | A short id cannot identify a live pane |
| Exchange identity | `- Review pairing:` prose | Family, document, step and occurrence in one sentence |
| Unknown or not applicable | Free wording, reason optional | Not distinguishable from a value |

A parser for this prose would have to guess where one value ends, and the
design forbids guessing a pane, a role or an exchange. The Step 2 reader
therefore classifies a table-only prompt as table-only and never reads its
cells.

## Hazards of rewriting an existing pause

Adding a JSON block changes the prompt's bytes, so its SHA-256 changes. That
single fact drives every hazard below.

1. **A consumed pause can look unused.** A usage receipt matches the old
   digest. After a rewrite it names different bytes, and the state table
   reads that as "new prompt since previous use": a pause that was already
   resumed would be offered again, by bulk launch and by manual
   `resume-session`.
2. **The installed launcher would resume it again.** `tuitp` compares the
   receipt's `- SHA-256:` line with the prompt's bytes; a rewritten prompt
   no longer matches, so a created or restored session would receive the
   resume command at startup.
3. **A concurrent resume can race the rewrite.** A receiving agent may be
   reading the prompt or writing its receipt while a converter replaces the
   file; the receipt could then bind bytes that no longer exist.
4. **Missing intent cannot be recovered.** A legacy table records what the
   pausing agent observed then. Shortened ids, prose roles and absent
   reasons cannot be completed later without inventing assignments, and a
   valid block that records them as unknown stays ineligible anyway.
5. **Rewriting receipts would hide the problem.** Deleting or editing a
   receipt to keep the digest consistent would manufacture eligibility,
   which the design forbids.

## Proposed path for older pauses

Use the path that already exists: resume the old pause with ordinary
`resume-session` in its own pane, then pause again with the updated
`pause-session`. The new pause records currently verified routing in the JSON
block, with fresh pane identities and its own digest and receipt history, and
the old receipt keeps protecting the old bytes.

A separate explicit converter for unused legacy pauses remains possible, but
only after its own review settles:

- the documented table forms it accepts and the explicit values it reads,
  with every contradiction rejected and every missing value left unknown;
- independent live validation of checkout, host, TUIOS session, full pane
  UUID, intended roles and exact exchange or explicit not-applicable;
- a check, immediately before any write, of receipt validity, exact source
  bytes and concurrent resume activity, refusing consumed prompts and
  uncertain reuse evidence;
- atomic replacement after an explicit reviewed conversion action that keeps
  the first-line heading, `- Session role:`, the historical author and the
  snapshot, records conversion time and source separately, and leaves a
  prompt that already holds valid JSON unchanged;
- recovery when a conversion fails, and tests for each of these rules.

These points are study findings, not decided design questions, and they add
nothing to the current delivery.

## Limits of this study

The study reads the branch template, the design and the Step 2 reader. It
does not sample real legacy prompts for their table variants, and it does not
validate any conversion against the installed `tuitp` or a live pane. The
deferred senv integration keeps its own obligations, unchanged by this study.
