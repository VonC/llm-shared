# Session journal

Private index of the sessions paused and resumed with llm-shared, across every
checkout of this user. pause-session and resume-session maintain it, following
the "Session journal across checkouts" section of the llm-shared
`instructions/pause-session.md`; list-session reads it. Per checkout, it keeps
only the latest pause entry and the latest resume entry. Never copy it into a
repository, and never write credentials or review capabilities in it.

## Pause by {agent id} at {YYYY-MM-DDTHH:MM:SS+HH:MM} in `{absolute checkout path}`

- Host: {host product and model, as the prompt's Paused by line records them}
- Branch and HEAD: `{branch}` at `{short SHA}`
- Prompt: `{prompt path relative to the checkout}`, SHA-256 `{64 lowercase hexadecimal characters}`
- Summary: {two or three sentences: the task, where it stopped, and the next action or blocker}

## Resume by {agent id} at {YYYY-MM-DDTHH:MM:SS+HH:MM} in `{absolute checkout path}`

- Host: {host product and model}
- Source: {prompt `{relative path}`, SHA-256 `{digest}`, with its state: unused, new prompt since previous use or forced reread; or the relative note paths, with no saved prompt found or latest prompt already used}
- Agent override: {not needed, or consented by the user at YYYY-MM-DDTHH:MM:SS+HH:MM over `{previous agent id or unknown}`}
- Next action: {the action this resume continues with}
