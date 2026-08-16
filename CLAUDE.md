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

## Strategic direction — read `docs/RESEARCH_ARCHITECTURE.md`

That file (added 2026-08-16, from strategic guidance Jason got and
adopted as the project's north star) is the long-term plan and should
shape decisions automatically, without Jason having to re-explain it
each session. Read it at the start of substantial work on this project.
The short version of what it means day to day:

- The goal is a general research platform that can test MANY candidate
  strategies through the same standardized pipeline — not a platform
  built around Level Sweep Reversal specifically. Don't special-case
  code around today's best-performing setup.
- No backtest result — however positive — gets called "proven" or
  "profitable" until it's cleared out-of-sample testing, walk-forward
  testing, and the other validation steps that document lists. Default
  language for an unvalidated positive result is "candidate" or
  "promising," never "a strategy that works."
- Before building more strategy-specific features (including expanding
  Tony), prioritize fixing architecture gaps the plan depends on —
  see that doc's "Immediate next steps" questions and the standing
  architecture-review findings from 2026-08-16 (ask Jason for the
  current status if picking this up in a new session, or re-run the
  same review).
- Tony (the future live-alert layer) stays explicitly experimental —
  never implies a signal is a proven profitable trade, and does not get
  built out further without Jason's explicit go-ahead (this is separate
  from, and in addition to, the Stage 5 safety boundary below).

## Holdout data — do not touch without a very deliberate reason

As of 2026-08-16, `data/NQ_1min_databento_2026-08-16.csv` has a real
holdout slice carved out: **2026-04-07 onward is untouched holdout
data**, set aside for a future one-time out-of-sample validation check
(see `docs/RESEARCH_ARCHITECTURE.md`'s implementation status for the
full reasoning). Every script that loads real price data
(`detect_setups.py`, `detect_level_sweep.py`, `backtest.py`,
`plot_open.py`, `plot_setup_example.py`) calls
`apply_holdout_boundary()` from `src/data_holdout.py`, which excludes
holdout data by default and requires the environment variable
`ALLOW_HOLDOUT_DATA=1` to include it. **Never set that variable, and
never suggest Jason set it, "just to check something" or as part of
routine testing** — that would burn the only genuinely unseen data this
project has. It's for one deliberate, final validation check on a
candidate strategy that has already cleared everything else in
`docs/RESEARCH_ARCHITECTURE.md`'s validation checklist, and that
decision should be made explicitly with Jason, not made quietly by
running a script with a flag on.

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
