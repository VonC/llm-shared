## Review identity for $identity_label (round $round_number)

$identity_fields

## Code review evidence for $identity_label (round $round_number)

```json
$code_review_evidence
```

## Review scope for $identity_label (round $round_number)

Apply `implementation-check` to the exact implementation plan step and inspect
the staged changes as the review subject. Make every safe, unambiguous repair
that remains inside that step. Work that exceeds the step or needs a product
decision must be returned as feedback rather than edited.

Leave each repair staged and name every repaired path in the answer. Inspect
and amend `a.commit` only when file membership, grouping, order, scope, or the
conventional subject no longer matches the staged work. Do not commit.

## Requestor assessment for $identity_label (round $round_number)

$assessment

## Implementation report for $identity_label (round $round_number)

$implementation_report

## Change summary for $identity_label (round $round_number)

$change_summary

$response_section

## Required reviewer conclusion for $identity_label (round $round_number)

Publish either a changes-requested answer or an advisory commit-ready
recommendation through the shared review exchange. Identify the evidence you
checked, list every repaired path, classify each repair as substantive or
polishing-only, and state whether `a.commit` remains accurate. A substantive
repair changes code, tests, acceptance behavior, or commit grouping and cannot
validly finish the workflow in the same round. A commit-ready recommendation
never authorizes a commit.
