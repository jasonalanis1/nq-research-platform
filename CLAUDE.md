# Project instructions for Claude

This file is automatically read by Claude Code (and this project's Claude
sessions generally) at the start of work in this repo. It's where
standing rules for how to work on this project live, so they don't need
to be repeated every conversation.

## Who Jason is

A futures trader (NQ, focused on the 8:30 AM NY open) with minimal Python
experience. Explain steps clearly, don't assume programming background,
give exact install/click instructions when relevant. See `README.md` and
`docs/ROADMAP.md` for full project context and current status.

## The research/ knowledge layer — rules to follow automatically

This project keeps a `research/` folder (see `research/README.md` for the
full explanation) that separates the *thinking* from the *code*. Follow
these rules without being asked each time:

1. **When Jason pastes an idea or observation** (a market note, an
   article, "I noticed X happen at the open"), file it in
   `research/raw/` as a new dated file. Don't ask permission first — just
   file it, then mention where it went.
2. **If that idea is testable as a hypothesis**, create a stub file in
   `research/experiments/` (follow the naming pattern
   `exp-NNN-short-description.md`, see existing files for the template)
   and add a row to `research/experiments/_index.md`.
3. **Every time a backtest variant is run** (different setup, different
   parameters, different data), log it as a NEW file in
   `research/experiments/` and a NEW row in `_index.md`. Never overwrite
   or edit a previous experiment's results, even if a later run
   supersedes it — the old one stays as history. It's fine and expected
   for `_index.md` to grow over time.
4. **`research/experiments/_index.md` is the source of truth** for
   everything that's been tried. Keep it current whenever an experiment
   is added.
5. **Never edit, "clean up," or hand-correct backtest results, equity
   curves, or any other code-generated output** (files in `data/`,
   `charts/`, or an experiment's recorded results). These are ground
   truth from the pipeline. If a result looks wrong, the fix is to find
   and fix the bug in the code, then re-run — never to hand-edit the
   output to what it "should" say.
6. **Setup definitions** (`research/setups/*.md`) are the exception to
   rule 5 — those describe intent and are expected to evolve as Jason
   refines what he actually trades. Keep them in sync with whatever
   `src/detect_setups.py` (or its successors) actually implements.

## Safety boundary (do not relax without Jason explicitly asking, live)

Do not autonomously write code that touches live/real-money execution.
Stages 1-4 (data, detection, backtesting, scoring) are safe to build and
iterate on. Stage 5 (live automation) requires Jason's direct,
in-the-moment approval each time — not a standing green light from an
earlier conversation.
