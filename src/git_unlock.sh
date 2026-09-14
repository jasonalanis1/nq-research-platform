#!/usr/bin/env bash
# Move stale git lock files aside. The device shell cannot delete files, so git's
# own cleanup of .git/index.lock / HEAD.lock can fail and block the next commit.
# Run before every git command in a cycle:  bash src/git_unlock.sh
cd "$(dirname "$0")/.." || exit 1
mkdir -p _to_delete
# refs/remotes/*/*.lock added 2026-09-14: a stale one does NOT block a commit or a
# push -- the push succeeds -- but it blocks the REMOTE-TRACKING REF from updating,
# so `git status -sb` then reports "ahead N" forever against a remote that already
# has the work. That false reading reached ops_checks' git-sync check and would have
# failed every cycle tonight while nobody was watching.
for f in .git/index.lock .git/HEAD.lock .git/refs/heads/main.lock \
         .git/refs/remotes/origin/main.lock .git/refs/remotes/origin/HEAD.lock; do
  if [ -e "$f" ]; then mv "$f" "_to_delete/$(basename "$f").stale-$(date +%s%N)" && echo "moved stale $f"; fi
done
exit 0
