#!/bin/bash
#********************************************************************
# Script Name:  activity_report.sh
# Description:  Builds "a.md", an activity-report analysis document,
#               from the commit messages and the Markdown-file diffs
#               of one or more git working trees, between a start date
#               and an end date (default: today). It does not read the
#               full codebase: only git log and the diff of *.md files.
#
# Location:     llm-shared/scripts/ (mutualized across projects).
#
# Parameters:
#   -s | --start <YYYY-MM-DD>   start date, inclusive (required)
#   -e | --end   <YYYY-MM-DD>   end date, inclusive (default: today)
#   -o | --out   <file>         output file (default: <PWD>/a.md)
#   <worktree> ...              one or more git working trees. When
#                               none is given, the current directory.
#
# Usage:        bash <LLM_SHARED_DIR>/scripts/activity_report.sh \
#                 --start 2026-05-29 . ../my-project
#               (run from the calling project root so a.md lands there)
#
# Writes:       <out> (default <PWD>/a.md)
#
# Exit codes:
#   1 - bad arguments
#********************************************************************

info()  { echo "Info:  $1"; }
task()  { echo "Task:  $1"; }
ok()    { echo "Ok:    $1"; }
warn()  { echo "Warn:  $1" >&2; }
fatal() { echo "Error: $1" >&2; exit "${2:-1}"; }

#  ===============================================
#  PARSE ARGUMENTS
#  ===============================================
start=""
end=""
out=""
declare -a trees=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    -s|--start) start="$2"; shift 2 ;;
    -e|--end)   end="$2";   shift 2 ;;
    -o|--out)   out="$2";   shift 2 ;;
    -h|--help)
      echo "Usage: activity_report.sh --start YYYY-MM-DD [--end YYYY-MM-DD]"
      echo "                          [--out a.md] <worktree> [<worktree> ...]"
      exit 0 ;;
    -*) fatal "Unknown option '$1'" 1 ;;
    *)  trees+=("$1"); shift ;;
  esac
done

[[ -n "${start}" ]] || fatal "Missing required --start <YYYY-MM-DD>" 1
[[ "${start}" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] \
  || fatal "Bad --start '${start}', expected YYYY-MM-DD" 1

end="${end:-$(date +%F)}"
[[ "${end}" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] \
  || fatal "Bad --end '${end}', expected YYYY-MM-DD" 1

out="${out:-${PWD}/a.md}"
[[ ${#trees[@]} -gt 0 ]] || trees=(".")

from="${start} 00:00:00"
to="${end} 23:59:59"

info "Period from '${start}' to '${end}' (both inclusive)"
info "Working trees: ${trees[*]}"
info "Output '${out}'"

#  ===============================================
#  WRITE a.md
#  ===============================================
task "Collecting commit messages and Markdown diffs"
{
  echo "# Activity report to be analyzed"
  echo ""
  echo "Period: from ${start} to ${end} (both dates included)."
  echo ""

  for wt in "${trees[@]}"; do
    name="$(cd "${wt}" 2>/dev/null && basename "$(pwd)" || echo "${wt}")"
    echo "## ${name}"
    echo ""

    if ! git -C "${wt}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      echo "Path: ${wt}"
      echo ""
      echo "Not a git working tree; skipped."
      echo ""
      warn "'${wt}' is not a git working tree; skipped"
      continue
    fi

    abs="$(cd "${wt}" && pwd)"
    echo "Path: ${abs}"
    echo ""

    #  --- commit messages over the window (oldest first) ---
    echo "### Commit messages"
    echo ""
    log_out="$(git -C "${wt}" log --reverse \
      --since="${from}" --until="${to}" \
      --date=short --format='- %ad %h %s%n%w(0,2,2)%b')"
    if [[ -n "${log_out}" ]]; then
      echo "${log_out}"
    else
      echo "No commits in the period."
    fi
    echo ""

    #  --- diff of *.md over the window ---
    echo "### Md diff"
    echo ""
    start_rev="$(git -C "${wt}" rev-list -1 --before="${from}" HEAD 2>/dev/null)"
    end_rev="$(git -C "${wt}" rev-list -1 --before="${to}" HEAD 2>/dev/null)"
    if [[ -z "${end_rev}" ]]; then
      echo "No commit at or before the end date; no Markdown diff."
      echo ""
      continue
    fi
    # When there is no commit before the start day, diff from the empty
    # tree so the first in-window Markdown content shows as added.
    if [[ -z "${start_rev}" ]]; then
      start_rev="$(git -C "${wt}" hash-object -t tree /dev/null)"
    fi
    diff_out="$(git -C "${wt}" diff "${start_rev}" "${end_rev}" -- '*.md')"
    if [[ -n "${diff_out}" ]]; then
      echo '```diff'
      echo "${diff_out}"
      echo '```'
    else
      echo "No Markdown changes in the period."
    fi
    echo ""
  done
} > "${out}"

ok "Activity-report analysis written to '${out}'"
