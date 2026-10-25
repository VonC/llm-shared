# Explain and decide the remaining specification questions

Use this guide when a requirement, issue, design, or plan has reviewed questions
whose proposed answers still need your decision.

## Invocation model

At specification review convergence, choose `Explain undecided questions`, or
invoke the skill with the exact document:

```text
$llm-shared:explain-undecided-questions on docs/v1.4.0/feature-request.v1.4.0.route-warnings.md
```

Claude Code and Copilot use `/explain-undecided-questions`. Other hosts load
the corresponding workflow or canonical
[instruction](../../instructions/explain-undecided-questions.md).
If a review round is active, the requestor finishes that round first. Direct
invocation without an exchange is supported, but does not establish independent
convergence by itself.

For a newly added Codex skill, run `llmup` and start a new Codex thread to refresh
discovery. An existing thread can read the canonical instruction explicitly;
see [picking up skill edits](pick-up-skill-edits-without-restarting.md).

## Decide one question at a time

The agent scans explicit user records, identifies the next and last undecided
questions, and saves the starting position for this batch. A proposed answer,
even one accepted by the reviewer, remains undecided until you confirm it.

For a batch Q59–Q73, the first explanation displays `Q59/Q73 7%`, and the last
displays `Q73/Q73 100%`. This measures position in the explanation sequence;
the displayed question still needs your answer. Answering or pausing does not
reset the starting position. The [scanner reference](../reference/question-decisions.md)
defines navigation and the progress formula.

Each explanation covers the behavior, a realistic example, an analogy, the
options and tradeoffs, a recommendation, and effects on related questions.
Reply with your choice and qualifications, or ask for clarification. The agent
records your explicit decision and comments in that question's answer. It keeps
the question, options, and original recommendation. A deferred question remains
undecided; dependent questions still need explicit decisions.

## Review the consequences before consolidation

Choosing this skill authorizes recording your answers and the follow-up
independent review. You can place that review on hold. It does not authorize
consolidation, staging, or commits.

After the last decision, the agent announces that a fresh review must check
the decisions and comments for inconsistencies and additional questions. It
uses the existing requestor exchange and `Revise and review again` transition,
or enters the specification review gate when no exchange exists. The reviewer
session remains separately started by you.

At the next convergence, any new undecided questions form a new explanation
batch when you select it. Once decisions and their review are complete, you
choose consolidation or another review round.

## Pause during the discussion

Invoke `pause-session` normally. Its snapshot preserves the document, fixed
starting position, current question, delivered explanation, decision status,
and follow-up review state. `resume-session` rescans the document and continues
the question awaiting your decision. If you paused after recording the final
answer, it starts the required review; if that review was already published,
it resumes the existing round.

See [pause and resume](pause-and-resume-a-session.md) for the session commands.
