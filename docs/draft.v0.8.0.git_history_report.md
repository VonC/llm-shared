# Commit and Tell

- Type: feature-request

## Context

`llm-shared\tools\git_history_dashboard\build.py` currently target pdfsplitter. I need you to include that as part of a skill able to generate a git history report for any project, as well as update its associated comment.

## Existing content

- the shared ghd tool, `llm-shared\tools\git_history_dashboard\build.py`, targeting pdfsplitter.
- the template `llm-shared\tools\git_history_dashboard\template.html`, targeting pdfsplitter, with a LLM-written comment/observations block.

Outputs:

- `pdfsplitter\docs\git_history_dashboard\dashboard.html` and `pdfsplitter\docs\git_history_dashboard\data.json` — now 3,416 commits (was 3,152), range 26 Jun 2024 → 22 Jun 2026, over 24 months. Active days 302/727 (42%), peak week 161 (week of 9 Mar 2026), peak day 43 (12 Mar 2026). Metrics/lead auto-filled from placeholders.
- scratch git_history.csv (git-ignored, not committed)

Comments/text updated (the hand-written observations block, which build.py does not auto-generate — it lives in `llm-shared\tools\git_history_dashboard\template.html`)

## skill

I need the skill to create or update the git history report for any project, by running the build.py script with the appropriate parameters (e.g., project path, output path). The skill should also be able to update the associated comment with the latest observations based on the new data.

The template should no longer include the generated analysis but include a file able to include the latest analysis, which the skill will update after running the build.py script. The skill should also ensure that the generated dashboard.html and data.json are saved in the specified output path, and that the dashboard.html is opened in the default browser after creation or update.

Update would include:

- Extended the time narrative through the day it is called.
- Corrected the type story: feat leads all-time (764); tests↔refactors track (584 vs 472); docs (625) swells through the v9.5.0–v9.8.0 polluted-PDF / resources-isolation planning work. (number given for illustration)
- Verified the hour peak (21:00 = 327) and weekday (Thursday 545 edges Tuesday 537). (number given for illustration)
- Refreshed top scopes to the current leaders: domain, web, plan, workflow, release (from the repo analysis, may differ on other projects).

I need a white/dark mode toggle for the dashboard.html, and a way to filter the data.json by date range and commit type (feat, fix, docs, test, refactor, chore). The skill should also generate a summary of the top contributors and their commit counts.

The skill must open in the default browser the generated dashboard.html after the report is created or updated. It should also log any errors encountered during the process and provide a summary of the actions taken.
