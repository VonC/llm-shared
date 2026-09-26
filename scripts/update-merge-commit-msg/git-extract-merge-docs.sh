#!/bin/bash

# Dump the documents a merge brought in, for the merge-message reword.
# a.commit stays at the project root (the human reviews it there); the
# a.docs dump goes to the review artifact home (.reviews unless
# .review-artifacts.ini declares another home), never the project root
# (see rules/artifact_files.md), through the shared tools/artifact_home.py.

LLM_SHARED="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

#  Print the artifact-home path of one file of the calling project, through
#  the shared tools/artifact_home.py helper (llm-shared venv when present).
artifact_file() {
    local root="$1" name="$2" py="" cand
    for cand in "${LLM_SHARED}"/venvs/python_3*llm-shared*/Scripts/python.exe \
                "${LLM_SHARED}"/venvs/python_3*llm-shared*/bin/python; do
        if [[ -x "${cand}" ]]; then py="${cand}"; break; fi
    done
    [[ -n "${py}" ]] || py="$(command -v python3 || command -v python)"
    [[ -n "${py}" ]] || return 1
    PYTHONPATH="${LLM_SHARED}" "${py}" -m tools.artifact_home "${root}" "${name}" \
        | tr -d '\r'
    return "${PIPESTATUS[0]}"
}

# Default to HEAD if $1 is empty
TARGET_MERGE=${1:-HEAD}

# --- Validation: Project Directory ---
if [[ -z "$PRJ_DIR" || ! -d "$PRJ_DIR" ]]; then
    echo "Error: PRJ_DIR is undefined or not a valid directory." >&2
    exit 1
fi

if ! cd "$PRJ_DIR"; then
    echo "Error: Failed to enter project directory $PRJ_DIR." >&2
    exit 1
fi

MESSAGE_FILE="$PRJ_DIR/a.commit"

# --- Validation: Merge Commit ---
if ! git rev-parse --verify "$TARGET_MERGE^2" >/dev/null 2>&1; then
    echo "Error: Commit $TARGET_MERGE is not a merge commit (no second parent)." >&2
    exit 1
fi

P1=$(git rev-parse "$TARGET_MERGE^1")
P2=$(git rev-parse "$TARGET_MERGE^2")

# --- Lineage Exploration ---
# Use the merge parents directly so the script does not depend on branch names
# still existing locally after the merge.
mapfile -t COMMITS < <(git rev-list "$P2" "^$P1")

if [[ ${#COMMITS[@]} -eq 0 ]]; then
    echo "Error: No unique commits found in the second parent lineage." >&2
    exit 1
fi

# Find all .md files changed in docs/ between the merge parents
MD_FILES=()
while IFS= read -r FILE; do
    if git cat-file -e "$P2:$FILE" 2>/dev/null; then
        MD_FILES+=("$FILE")
    fi
done < <(
    git diff --name-only "$P1" "$P2" -- docs |
        grep '^docs/.*\.md$' |
        sort -u
)

if [[ ${#MD_FILES[@]} -eq 0 ]]; then
    echo "Error: No .md files found in the docs/ directory of the unique lineage." >&2
    exit 1
fi

# --- File Operations ---
# 1. Empty a.commit (ensuring it exists but is size 0)
: > "$MESSAGE_FILE"

# 2. Dump .md contents to a.docs in the artifact home
if ! OUTPUT_FILE="$(artifact_file "$PRJ_DIR" a.docs)"; then
    echo "Error: Cannot resolve the artifact home of $PRJ_DIR." >&2
    exit 1
fi
: > "$OUTPUT_FILE"

for FILE in "${MD_FILES[@]}"; do
    {
        echo "--- File: $FILE ---"
        git show "$P2:$FILE"
        echo
    } >> "$OUTPUT_FILE"
done

echo "Success: Docs dumped to $OUTPUT_FILE. '$MESSAGE_FILE' has been emptied."
exit 0
