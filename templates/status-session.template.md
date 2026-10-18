# Session status response

Choose one opening below, fill its placeholders, then use the three-point body.
This is a response template, not a file to create in the artifact home.

## Opening when an unprocessed prompt exists

status-session: unprocessed resume prompt found at `{relative-prompt-path}`
({unused or new since previous use}), paused by `{agent id or unknown}`.
Summary of the saved prompt; no work resumed.

## Opening when no unprocessed prompt exists

status-session: no unprocessed resume prompt at `{relative-prompt-path}`
({no saved prompt found or latest prompt already used}). Summary of the latest
notes, handoffs and journals in `{relative-artifact-home}`.

## Opening when the state cannot be determined

status-session: cannot determine whether an unprocessed resume prompt exists
at `{relative-prompt-path, or .review-artifacts.ini if home resolution failed}`:
{diagnostic}. {Summary based only on readable notes, or no usable evidence available.}

## Three-point body for every state

1. **Objective:** {Saved or last recorded task, topic and scope; source path and
   date. If unavailable, say the objective is unknown.}
2. **Progress:** {Completed work, current action and verification limits; source
   path and date. State missing, stale or conflicting evidence when applicable.}
3. **Next actions or blockers:** {Recorded next action, pending decision or
   blocker; source path. Say none recorded or unknown when appropriate.}
