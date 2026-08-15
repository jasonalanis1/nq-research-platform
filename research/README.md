# Research Knowledge Layer

This folder is where the *thinking* behind the project lives, separate
from the code in `src/`. The code answers "does this setup work"; this
folder answers "what have we tried, what did we learn, and why."

- **`raw/`** — the dump zone. Half-formed ideas, articles, "I noticed X
  happen at the open today" observations. Nothing here needs to be
  polished or even correct — it's a scratch pad, not a conclusion.
- **`journal/`** — one dated entry per work session, in plain language.
  A running diary of what we did and decided, so picking the project back
  up after a break doesn't mean re-deriving where things left off.
- **`experiments/`** — one file per hypothesis tested, plus `_index.md`,
  a scoreboard table of every experiment run. This is the project's
  memory of what's been tried, so we never accidentally re-test the same
  idea thinking it's new, and never lose track of what got ruled out
  (and why).
- **`setups/`** — the real setup definitions, as they get refined over
  time. Distinct from `experiments/`: this is "what the setup IS,"
  experiments are "what happened when we tested it."

## The rules (also encoded in `CLAUDE.md` at the project root so any
Claude session, in this environment or on your Mac, follows them
automatically):

1. When you paste an idea or observation, it gets filed in `raw/`. If
   it's testable, an experiment stub gets created in `experiments/` and a
   row gets added to `experiments/_index.md`.
2. Every backtest variant run gets logged as a NEW experiment entry —
   never overwrites an old one. Old results stay around even after being
   superseded, so the history of what was tried is never lost.
3. `experiments/_index.md` is kept up to date as the single source of
   truth for everything that's been tried.
4. Backtest results, equity curves, and code output never get edited or
   "cleaned up" after the fact. Those are ground truth from the pipeline
   — if a result looks wrong, the fix is to fix the code and re-run, not
   to hand-edit the output.
