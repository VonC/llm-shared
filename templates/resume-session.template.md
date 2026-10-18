# Session resume usage receipt

- Schema: 2
- Prompt: a.session-resume.local.md
- SHA-256: {64 lowercase hexadecimal characters for the exact prompt bytes}
- Project root: {absolute resolved primary checkout path}
- Used at: {YYYY-MM-DDTHH:MM:SS+HH:MM}
- Forced: {true or false}
- Paused by: {agent id from the prompt's first line, or unknown}
- Resumed by: {agent id of the resuming session}
- Agent override: {not needed, or consented by the user at YYYY-MM-DDTHH:MM:SS+HH:MM}

## Reconciliation recorded at resume

{Observed branch and HEAD, relevant changes since pause, required references
read, and the next authorized action. No credentials or review capabilities.}

## Meaning of this usage flag

This receipt records successful context recovery, not task completion.
