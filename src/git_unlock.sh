#!/usr/bin/env bash
# Move stale git lock files aside. The device shell cannot delete files, so git's
# own cleanup of .git/index.lock / HEAD.lock can fail and block the next commit.
# Run before every git command in a cycle:  bash src/git_unlock.sh
cd "$(dirname "$0")/.." || exit 1
mkdir -p _to_delete
for f in .git/index.lock .git/HEAD.lock .git/refs/heads/main.lock; do
  if [ -e "$f" ]; then mv "$f" "_to_delete/$(basename "$f").stale-$(date +%s%N)" && echo "moved stale $f"; fi
done
exit 0
