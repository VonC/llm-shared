# Run the implement chain on one plan step

<img src="../assets/logo-llm-shared-review-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

You select the plan step and start `implement-step`. The AI owns the subsequent
Groundhog, implementation-check, missing-work, and grouped-commit handoffs.
Your role is to validate the evidence and approve the commit plan.

🔁 In this tutorial you execute one step of a settled implementation plan
and watch the automated chain carry it from code to a reviewed commit
plan, with a single "go ahead" at the very end. You need an effort whose
plan is settled: `docs\plan.vX.Y.Z.<topic>.md` and its validation
companion exist, and the plan's decision table is in place (see
[the requirement tutorial](02-from-draft-to-settled-requirement.md)).

## 1. Start the step

```txt
/implement-step 1
```

The skill reads the plan, the design and the requirement, writes a short
analysis, then writes the classes and their tests in full — no
placeholders, tests first for a new class, `__init__.py` files updated.

## 2. Watch the green gate

The step is not done until one `ghog day` walk is green. The model runs
it redirected to `a.ghog.log`, branches on the exit code, and fixes what
the report names. You can follow along from a second console.

## 3. The chain hands off by itself

Once the walk is green, the model runs `pw handoff check 1`, which writes
the next prompt to `a.prompt.txt` and copies it to the clipboard. From
here the chain runs with no menu and no "go ahead":

1. `/implementation-check 1` — reads the diff and the plan, writes its
   verdict into `docs\plan.vX.Y.Z.<topic>.validation.md`, first sentence
   exactly `Yes. Step 1 has been fully implemented.` or `No. ...`,
2. `pw handoff after-check 1` — neutral on purpose: `pw` reads the
   verdict line the check just wrote and routes the branch,
3. on `No` — `/implement-missing-step 1` fills the listed gaps, then the
   check runs again,
4. on `Yes` — `/group-commits-msg` stages everything (`git add -A`),
   groups the files from least dependent to most dependent, and writes
   one conventional commit message per group into `a.commit`.

## 4. Stop at the commit gate

The chain always stops at `a.commit`: writing the messages is automatic,
making the commits is not. The model shows the commit plan and a
multi-choice built by `pw skill --after-commit 1`:

```txt
1. Go ahead
2. Go ahead, and implement step 2
3. Type something else
```

Read `a.commit` (the staged diff snapshot in `a.diff` justifies the
grouping). Edit it if a group or a wording is off.

## 5. Replay the commits

Say `go ahead` (or run `gcba`). The tool validates `a.commit`, then
creates the commits in order, least dependent first. The step is done:
implemented, tested, checked, committed — and the validation document
keeps the trace of every check iteration.

## 👉 Next steps after the chain

- [Group a dirty tree into conventional commits](../how-to/group-commits-into-conventional-messages.md)
  to use the commit half on its own, outside a plan.
- [Prepare a release from any branch](../how-to/prepare-a-release.md) once
  the last step is committed.
- [One launcher, three modes](../explanation/one-launcher-three-modes.md)
  for what `pw handoff` builds and why.
