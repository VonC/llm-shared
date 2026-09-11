# Enable independent review mode

<img src="../assets/logo-llm-shared-transparent.png" alt="llm-shared logo" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Use this guide to opt a repository into future two-agent exchanges or return it
to its ordinary single-agent stops. Change only the project-root marker; do not
create, rename, or edit exchange artifacts.

Do not reconstruct protocol filenames or edit protocol artifacts. Read the one
final JSON result and follow its returned `paths` whenever an operation names an
artifact.

## Enable review mode

1. Prepare the configured artifact home (`.reviews` by default) with a local
   `.gitignore` containing `*`. Create an empty `a.review-mode` inside that home
   to use the bounded-wait default, three hours unless a settings file says otherwise.
2. To version another default for every review in this repository, add
   `.review-exchange.ini` at the Git root:

   ```ini
   [review-exchange]
   wait_timeout_seconds = 7200
   ```

   An invalid repository value is ignored, and the three-hour setting shipped
   by llm-shared applies instead.
3. To select another positive limit for this exchange alone, put exactly one
   line in the marker:

   ```text
   wait_timeout_seconds=1200
   ```

4. Start the normal specification or implementation skill. Its `pw` handoff
   samples the marker at the documented boundary and routes to the matching
   requestor.
5. Read the final JSON. Exit `0` reports the next active action; its `paths`
   member is authoritative for any request, answer, or coordination artifact.

An empty marker and a marker with one positive override are valid. A directory,
extra setting, non-integer, zero, or negative value returns exit `2`; correct
the marker rather than editing exchange state.

## Disable review mode

1. Check that no exchange is active. If one is active, finish or recover it
   through its requestor before changing the opt-in marker.
2. Remove the artifact-home `a.review-mode` file and any legacy project-root
   marker that would otherwise remain as a fallback.
3. Run the next ordinary workflow. With no marker, it keeps its existing human
   stop and creates no exchange artifacts.
4. A direct status call returns final JSON with disabled state and a null round.
   Its `paths` member is still populated, so read the state rather than the
   presence of a path: the coordination artifact it names does not exist while
   the marker is absent.

Removing the marker is an opt-out for later workflow entry, not a recovery
operation for an exchange already in progress.

This page states user-visible behavior. The canonical
[shared requestor instruction](../../instructions/review-requestor.md) remains
authoritative for agent policy.

Next: [run a specification review](run-specification-review.md) or
[run an implementation code review](run-implementation-code-review.md).
