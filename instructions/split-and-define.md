# Split and define feature-requests and issues

Check the prompt for a `draft.vX.Y.Z.<topic>.md` document. Review it and
regroup its several topics into feature-requests and issues. This skill defines
the collection and its delivery order; it does not create any requirement
document.

The input draft must already be classified as:

```md
- Type: collection (feature-requests and issues)
```

If that line is absent or the draft contains only one topic, stop and return to
`process-draft` for correction.

## Mark the draft as an umbrella

Add this metadata line immediately after the collection type:

```md
- Draft role: umbrella
```

Keep the versioned draft under its umbrella slug for the lifetime of the
collection. Child requirements and branches use their own item slugs; they do
not rename or replace the umbrella.

## Define the ordered requirement index

Add or replace the exact
`## List of feature-requests and issues to create` section. Start it with this
compact table, using one row per requirement:

```md
## List of feature-requests and issues to create

| Order | Type | Key title | Slug | Status | Requirement | Validation plan |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Issue | Fix the bug in Z when doing W | `z-w-bug` | pending | - | - |
| 2 | Feature-request | Add support for X in Y | `x-y-support` | pending | - | - |
```

The table is the machine-readable, authoritative delivery index:

- `Order` starts at 1 and is consecutive.
- `Type` is exactly `Feature-request` or `Issue`.
- `Key title` is concise and does not repeat the slug in brackets.
- `Slug` contains two or three short topic words separated by `-`, using only
  lowercase letters, digits, `_`, or `-`, and starting with a letter or digit.
- `Status` is exactly `pending` for every newly split item.
- `Requirement` and `Validation plan` are exactly `-` while the item is
  pending.

After the table, add `### Requirement details for the umbrella`. For every row,
add one numbered H4 section in the same order. State its type, key title, slug,
what content was regrouped into it, why that boundary and title were chosen,
and which earlier items it depends on. Preserve concrete rules, examples, and
constraints from the source draft.

Review the final order so the most independent requirement is first and each
dependent requirement follows everything it needs. The order is an execution
contract: `pw skill --after-merge` and `process-draft` always select the first
pending row.

Do not mark an item complete here. `implementation-check` owns that transition:
when its final plan step makes the validation plan fully implemented, it changes
the matching row to `completed` and records the requirement and validation-plan
paths. A pending row with complete validation evidence, or a completed row with
missing evidence, is an error rather than an invitation to guess.

## Handoff after defining the umbrella

Before using or showing a host-prefixed workflow command, read
[`../rules/command_prefix_char.md`](../rules/command_prefix_char.md) and use its
prefix rule.

Once the index is settled, run `pw skill --after-merge <umbrella-draft>` through
its launcher (see [`run-pw.md`](run-pw.md)), passing the umbrella's exact
repository-relative path in its selected docs layout. This read-only lookup
validates the table and prints the first ordered action:

```text
<command-prefix>process-draft on <umbrella-draft> based on <first-slug>
```

Read [`../rules/interactive_menu.md`](../rules/interactive_menu.md), present
that printed command as the contextual next-step choice, and run it when
selected, with no additional go-ahead at this umbrella-level hand-off.
`process-draft` creates the focused child draft, stops for the child's human
review, and hands it to `write-requirement` only after that separate approval.
Include
`Type something else` as the correction choice when the host provides a native
menu. If the lookup fails or prints nothing, stop and report the malformed or
ambiguous umbrella instead of composing a requirement command by hand.
