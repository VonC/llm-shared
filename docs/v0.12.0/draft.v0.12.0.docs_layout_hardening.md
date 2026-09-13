# Not Every Folder Is an Effort

- Type: issue

## Why this effort exists

v0.11.0 shipped a fifth documentation layout, `docs/vX.Y.Z/<slug>/`. Widening
`_is_supported_docs_dir` to accept it closed a real defect that predated the
layout: a draft nested one directory deeper was already resolved by
`relevant_drafts`, while `docs_dirs` refused its parent, so the topic resolved
and every sibling document went invisible.

That widening left three rough edges. None of them breaks the repository today,
and each is a decision about the contract the layout establishes rather than a
repair of it, which is why they were deliberately kept out of the commits that
added the layout.

## 1. Effort-directory recognition accepts any lowercase name

`_is_supported_docs_dir` accepts a depth-two path when its first part is a full
version and its second part matches a slug shape. Nothing requires the
directory to hold an effort. A probe against the current implementation:

```text
docs/v1.2.3/topic    -> accepted
docs/v1.2.3/images   -> accepted
docs/v1.2.3/sub      -> accepted
docs/v1.2.3/My_Slug  -> rejected (uppercase)
docs/v1.2.3/a.scratch -> rejected (dot)
```

An assets or images directory beside the documents is indistinguishable from an
effort directory, and every consumer of `docs_dirs` would then scan it. No such
directory exists under any version directory today, so this is latent rather
than live.

Candidate answers, to settle in the design:

- require the directory to contain at least one `<type>.v<version>.<slug>.md`;
- require the directory name to match the slug of a draft it contains;
- keep the shape test and document the constraint instead.

## 2. The two document front doors disagree on the same tree

With the same document present at `docs/v1.2.3/` and at `docs/v1.2.3/my_slug/`:

```text
resolve_document(...)  -> raises Ambiguous feature-request document for ...
select_document(...)   -> returns docs/v1.2.3/feature-request... quietly
```

Before the layout widened, both ignored the nested copy. The divergence may be
correct: `resolve_document` fails closed by design, and `select_document`
preferring the canonical draft's own parent through `_topic_docs_dirs` is
deliberate existing behaviour. What is missing is a decision and a test. No
test pins either behaviour today, so whichever is intended can drift.

## 3. The directory pattern is borrowed from umbrella rows

`COLLECTION_SLUG_RE` exists to validate slugs in an umbrella collection table.
The layout change reuses it as a directory-name pattern. The two rules are
unrelated, so a future change to collection-row slugs would silently move
effort-directory recognition with it. A dedicated pattern for the directory
test would decouple them, and point 1 would define it anyway.

## Considered and declined

`docs_relative_dir` gained `slug: str | None = None` and raises
`NewDraftError` when the `version-slug` layout arrives without a slug. Making
the parameter required would delete the test that proves that raise, and both
in-tree callers already pass a slug. The default stays.

## Out of scope for this effort

The intermittent failure of `migration_journey[former-default]` in
`tests/acceptance/review_resume/` is a review-acceptance stability problem, not
a documentation-layout one. It has failed across three rounds with three
symptoms: a `FileNotFoundError` masking a migration refusal, a `WinError 5`
rollback at journal publication, and a thirty-second `migrate-artifacts`
subprocess timeout under parallel workers. The journal retry shipped in
v0.11.0 addressed only the second. It deserves its own draft.

## Suggested validation

- A probe covering each accepted and rejected directory shape, including the
  ones listed above.
- A test pinning whichever front-door behaviour the design settles on.
- The existing end-to-end layout test extended to whatever the new predicate
  requires of an effort directory.
