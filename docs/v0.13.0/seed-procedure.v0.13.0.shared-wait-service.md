# Repeatable Codex seed delivery

## Why the seed procedure needs tighter control

The initial series lets each fresh session choose how to read the same two
frozen drafts. Truncated tool output and repeated reads have produced materially
different retained context. Two A2 preparations failed the fixed 5% matching
gate. Full-file equality alone does not establish matched starting context.

On 2026-09-16 the operator requested automated fresh tabs and instruction-file
delivery for the next Codex series. The prepared launcher uses these controls;
live repeatability and the new measurements remain unproved. Its seed is under
`a.shared-wait-service/codex-controlled-proposal-20260916/`. All initial-series
results and rejected preparations remain unchanged.

## Controlled reads for the separate series

1. Freeze the same two complete drafts from one recorded commit. Preserve their
   original bytes and SHA-256 values.
2. Split each file into ordered UTF-8 chunks at whole-line boundaries, with at
   most 9,000 bytes per chunk. Reject a line exceeding that bound. Concatenating
   each file's chunks must reproduce its original bytes exactly. Record each
   chunk's order, byte count, path and SHA-256 before the first measured session.
3. Give every baseline, A and B session the same generated seed input and chunk
   order. Read each chunk once in a separate tool call, printing only its text.
   Do not perform broad tool discovery, repository inventories or additional
   reads of the full drafts as part of seeding.
4. If any chunk fails or is truncated, retain a failed preparation. Do not add
   recovery reads that would change its context, or publish a benchmark.
5. Verify the actual native outputs, exact UUID, normal `READY` completion,
   retained context and unchanged exposed configuration. Keep the 5% matching
   gate. Prompt instructions alone do not prove full reads or repeatability.

The prepared example has 17 chunks. Their byte-for-byte reconstruction was
verified in ordinary code. No measured session has used them, so consistent
live context remains unproven.

## Codex operator input template

The implementing session expands the ordered paths into a generated input file.
The human can invoke the [named-tab launcher](codex-tabs.v0.13.0.shared-wait-service.md)
to start the fresh TUIs, bind their UUIDs and queue the seed contents. Its small
identity setup turn is recorded outside measurements and repeated in every new
conversation. The canonical seed input is:

```text
Read both frozen drafts completely and keep their contents in context for the
next task. The ordered chunk files below concatenate to the exact full drafts.
Read each chunk once, in order, using a separate functions.exec call that invokes
tools.exec_command directly. Print only the returned output string with
text(result.output); use max_output_tokens: 10000 for the shell call.

Read rules/run_commands.md first, as required by this checkout. No tool discovery
or repository inventory is needed for this reading task. For each chunk, run:

Get-Content -LiteralPath '<chunk path>' -Raw -Encoding UTF8

Do not additionally read the original drafts. If a result fails or is truncated,
stop and report SEED_READ_FAILED. Do not analyze or summarize the drafts. After
all chunks have been read completely, reply exactly READY.

<Ordered absolute chunk paths for both complete frozen drafts>
```

## Evidence and operator cost of switching

Adoption requires a separate series with its own recorded seed-delivery method
and prompt/chunk hashes. Keep the same host/model/settings, seed revision and
declared timing bounds unless another explicitly recorded control changes.
Do not combine its trial pairs with the initial series's different preparation
method. It requires a new ten-minute baseline and three fresh trials per arm in
A/B, B/A, A/B order. Earlier failures and the unmatched B2 remain visible.

The bridge's later unmeasured automatic-wake check passed, as recorded in the
probe results. The reading procedure does not itself establish a complete
functional benchmark route or certify request-attempt coverage. Those evidence
gates remain separate.
