# Step {x} journal for {slug}

Private, git-ignored writer journal. Read it in full before acting on any
restart. Never rebuild the step state from memory.

## Step {x} objectives

- {objective taken from the plan step, one per line}

## Step {x} main goal

{one or two sentences: what is true once this step is committed}

## Step {x} context in the plan and umbrella

- Plan: `{effort-dir}/plan.vX.Y.Z.{slug}.md`, step {x} ({position}/{total}): {step title}
- Validation plan: `{effort-dir}/plan.vX.Y.Z.{slug}.validation.md`
- Design: `{effort-dir}/design.vX.Y.Z.{slug}.md`
- Requirement: `{effort-dir}/{feature-request or issue}.vX.Y.Z.{slug}.md`
- Umbrella: `{umbrella draft path}`, topic {n}/{total}: {umbrella row title} (or: none, standalone topic)
- Previous steps relied on: {step ids and what this step builds on, or: none}
- Next step after this one: {step id and title, or: last step}
- Handoff: `{artifact-home}/a.{slug}.step{x}.handoff.md`

## Step {x} milestone log

- {YYYY-MM-DDTHH:MM:SS+HH:MM} | start | journal and handoff created from the plan
