# Session list response

Choose one opening below, fill its placeholders, then give both lists.
This is a response template, not a file to create.

## Opening when the session journal exists

list-session: {count} session(s) waiting to be resumed and {count} in progress,
from `{session journal path}`.

## Opening when no session journal exists

list-session: no session journal at `{session journal path}`; no paused or
resumed session is recorded yet.

## Sessions waiting to be resumed

1. `{absolute checkout path}`: resume with `{agent id}` ({host product}),
   paused at {timestamp} on `{branch}` at `{short SHA}`; {disk check result}.
   {Journal summary.}

{Newest pause first. Write `None.` when no session is waiting.}

## Sessions in progress or interrupted

1. `{absolute checkout path}`: in progress with `{agent id}` ({host product}),
   resumed at {timestamp} from {prompt or notes}; {disk check result}.
   {Next action recorded in the journal.}

{Newest resume first. Write `None.` when every resumed checkout has been
paused since. Add once: if one of these chats was interrupted, invoke
`resume-session` in its folder, in the named agent, to resume from its
latest notes.}
