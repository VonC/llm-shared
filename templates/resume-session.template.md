# Session resume usage receipt

- Schema: {2 for a manual resume; 3 for a marked resume}
- Prompt: a.session-resume.local.md
- SHA-256: {64 lowercase hexadecimal characters for the exact prompt bytes}
- Project root: {absolute resolved primary checkout path}
- Used at: {YYYY-MM-DDTHH:MM:SS+HH:MM}
- Forced: {true or false}
- Paused by: {agent id from the prompt's first line, or unknown}
- Resumed by: {agent id of the resuming session}
- Agent override: {not needed, or consented by the user at YYYY-MM-DDTHH:MM:SS+HH:MM}
- Launch id: {marked resume only, omit this line on a manual resume: the marker's launch id, 32 lowercase hexadecimal characters}
- Receiving pane: {marked resume only, omit this line on a manual resume: the full 36-character UUID of the pane that received the marked command}
- Assignment binding: {marked resume only, omit this line on a manual resume: the marker's assignment digest, 64 lowercase hexadecimal characters}

## Reconciliation recorded at resume

{Observed branch and HEAD, relevant changes since pause, required references
read, and the next authorized action. No credentials or review capabilities.}

## Meaning of this usage flag

This receipt records successful context recovery, not task completion.
Schema 3 keeps every schema 2 line and only adds marked-resume bindings, which
hold no token or capability.
