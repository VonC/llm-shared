#!/bin/bash

# Default to HEAD if $1 is empty
TARGET_MERGE=${1:-HEAD}
MESSAGE_FILE="a.commit"

# --- Validation: Project Directory ---
if [[ -z "$PRJ_DIR" || ! -d "$PRJ_DIR" ]]; then
    echo "Error: PRJ_DIR is undefined or not a valid directory." >&2
    exit 1
fi

# --- Validation: Merge Commit ---
if ! git rev-parse --verify "$TARGET_MERGE^2" >/dev/null 2>&1; then
    echo "Error: Commit $TARGET_MERGE is not a merge commit (no second parent)." >&2
    exit 1
fi

P1=$(git rev-parse "$TARGET_MERGE^1")
P2=$(git rev-parse "$TARGET_MERGE^2")
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# --- Lineage Exploration ---
# Exclude commits that exist on branches other than main or the current feature branch
OTHER_BRANCHES=$(git for-each-ref --format='%(refname:short)' refs/heads | grep -vE "^(main|$CURRENT_BRANCH)$")
COMMITS=$(git rev-list "$P2" "^$P1" --not "${OTHER_BRANCHES}")

if [[ -z "$COMMITS" ]]; then
    echo "Error: No unique commits found in the second parent lineage." >&2
    exit 1
fi

# Find all .md files in the docs/ folder
MD_FILES=$(git ls-tree -r --name-only "$P2" | grep '^docs/.*\.md$' | sort -u)

if [[ -z "$MD_FILES" ]]; then
    echo "Error: No .md files found in the docs/ directory of the unique lineage." >&2
    exit 1
fi

# --- File Operations ---
# 1. Empty a.commit (ensuring it exists but is size 0)
: > "$MESSAGE_FILE"

# 2. Dump .md contents to a.docs
OUTPUT_FILE="$PRJ_DIR/a.docs"
: > "$OUTPUT_FILE"

for FILE in $MD_FILES; do
    {
        echo "--- File: $FILE ---"
        git show "$TARGET_MERGE:$FILE"
        echo
    } >> "$OUTPUT_FILE"
done

echo "Success: Docs dumped to $OUTPUT_FILE. '$MESSAGE_FILE' has been emptied."
exit 0
