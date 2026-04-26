#!/bin/bash

# Default to HEAD if $1 is empty
TARGET_MERGE=${1:-HEAD}
MESSAGE_FILE="a.commit"

# --- Validation: Project Directory ---
if [[ -z "$project_dir" || ! -d "$project_dir" ]]; then
    echo "Error: project_dir is undefined or not a valid directory." >&2
    exit 1
fi

# --- Validation: a.commit (Existence and Content) ---
if [[ ! -f "$MESSAGE_FILE" ]]; then
    echo "Error: '$MESSAGE_FILE' does not exist." >&2
    exit 1
fi

if [[ ! -s "$MESSAGE_FILE" ]]; then
    echo "Error: '$MESSAGE_FILE' is empty. Please add your multi-line message before running." >&2
    exit 1
fi

# --- Validation: Merge Commit ---
if ! git rev-parse --verify "$TARGET_MERGE^2" >/dev/null 2>&1; then
    echo "Error: Commit $TARGET_MERGE is not a merge commit." >&2
    exit 1
fi

# --- Reword Logic ---
TREE=$(git show -s --format=%T "$TARGET_MERGE")
P1=$(git rev-parse "$TARGET_MERGE^1")
P2=$(git rev-parse "$TARGET_MERGE^2")
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Create the new merge commit object with original parents
NEW_MERGE_SHA=$(git commit-tree "$TREE" -p "$P1" -p "$P2" -F "$MESSAGE_FILE")

if [[ -z "$NEW_MERGE_SHA" ]]; then
    echo "Error: Plumbing failed to create new commit object." >&2
    exit 1
fi

# Update the branch tip
git update-ref refs/heads/"$CURRENT_BRANCH" "$NEW_MERGE_SHA"

echo "Success: Merge reworded. HEAD is now $NEW_MERGE_SHA."
exit 0
