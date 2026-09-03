# Research Integrity Protocol

*2026-08-20. Governs how the future Strategy R&D Agent is allowed to search for
edges without manufacturing false positives through repeated testing. Detail inside
the already-approved Phase 1-11 framework from docs/AUTOMATION_ARCHITECTURE.md — no
new numbering system.*

## Decisions locked — 2026-08-20

1. No autonomous Strategy R&D or formal Larry candidate validation begins until the
   expanded historical dataset has been acquired, quality-checked, and formally
   split into Discovery/Validation/Holdout. No interim split of the current ~2
   years. Until then, this period is for infrastructure, documentation, and
   analysis of already-completed experiments only.
2. The six-state Larry classification is now the single official Strategy Status
   field, replacing the earlier 10-state list. The old states move to a separate
   Strategy Origin field (see below), not discarded.
3. A failed formal holdout evaluation permanently consumes one holdout slot. A
   candidate cannot reclaim that slot through modification or retesting.
4. The current 112-day holdout (2026-04-07 -> 2026-08-14) remains protected as
   "Holdout Generation 1" until the expanded dataset and new three-way split are
   established.

## Three-field model

**Strategy Origin** (metadata): External claim / Jason hypothesis / R&D-generated /
data-discovered / derivative.

**Strategy Status** (the six-state classification): REJECTED -> PROMISING ->
VALIDATION CANDIDATE -> HOLDOUT PASSED -> FORWARD VALIDATION -> PAPER VERIFIED.

**Live Authorization**: Not authorized / human-approved / automated-approved. This
field records earned eligibility only — it is never a substitute for the per-trade
approval CLAUDE.md already requires for Phase 9. A strategy marked "human-approved"
has met Phase 9's requirements; that does not mean any individual future trade
executes without Jason's real-time approval unless/until it separately clears
Phase 10's requirements in docs/AUTOMATION_ARCHITECTURE.md.

## Data acquisition (future work, not today)

Target 5 years minimum of NQ history, 7-10 years if cost and data quality both hold
up. Check cost via Databento's free `metadata.get_cost()` call, and quality via a
spot check of older sample dates. Watch specifically for whether a candidate's edge
is stable within the most recent 2-3 years alone, not only averaged across a full
decade that includes very different market regimes.

## The split — chronological, not random (future work, not today)

```
Oldest data -> DISCOVERY (~60%) -> VALIDATION (~20%) -> FINAL HOLDOUT (~20%) -> Present
```

Chronological, not randomized, to avoid leaking information across nearby,
serially-correlated dates. The R&D agent only ever sees Discovery. Once a candidate
is formally promoted, its parameters are frozen and it's re-tested on Validation
data it never touched during discovery.

The current legacy holdout (2026-04-07 -> 2026-08-14) is preserved, not replaced,
and treated as "Holdout Generation 1" while new history is acquired.

## Holdout Generation 1 — finite budget

5 formal candidate evaluations total for this holdout generation, ever. A candidate
must first pass, on Discovery + Validation data: minimum trade count, positive
research expectancy after realistic costs, predefined robustness tests, parameter
stability, out-of-sample validation, Deflated Sharpe Ratio / multiple-testing
adjustment, Probability of Backtest Overfitting (PBO) analysis where applicable, no
unresolved look-ahead or data-quality issues. Each individual holdout use still
requires Jason's explicit, in-the-moment sign-off. A failed evaluation still
consumes a slot.

## Renewable holdout generations

```
Holdout Generation 1: 5 candidate slots -> retired (uses current legacy holdout)
Holdout Generation 2: new unseen historical period -> 5 slots
Forward Generation:   live future data -> ongoing, never exhausted
```

Forward paper trading (Phase 7) becomes the long-run sustainable confirmation
mechanism once historical holdout budgets are spent.

## What Larry implements

**Status update, 2026-09-03: no longer future work for the DSR/PBO piece.**
`src/larry_validate.py` wires the real `purgedcv` library
(https://github.com/eslazarev/purged-cross-validation, MIT licensed,
Bailey & Lopez de Prado 2014) to `research_ledger.py`. Verified against a
synthetic scenario (planted-edge config correctly deflated from DSR 0.988
naive to 0.548 honest at n_trials=50; PBO 0.42-0.61 across runs, correctly
flagging a data-mined pick as overfit) and then applied for real to the
Level Sweep Reversal liquidity-filter family (hyp-000007, hyp-000008 --
both REJECTED: DSR 0.366 and 0.068 respectively, both below the 0.90
threshold; PBO 0.278 for both, above the 0.25 threshold too). The other
items below it (parameter sensitivity, out-of-sample performance as a
Larry-issued classification rather than this project's existing
Discovery/Validation/Holdout split, and the full REJECTED/PROMISING/
VALIDATION CANDIDATE/HOLDOUT PASSED/FORWARD VALIDATION/PAPER VERIFIED
classification ladder) remain future work, not today.

Full statistical bundle per candidate: observed Sharpe, number of trials, effective
number of trials, correlation between trials, expected maximum Sharpe under
multiple testing, Deflated Sharpe Ratio, Probability of Backtest Overfitting,
bootstrap confidence interval, expectancy, drawdown, profit factor, trade count,
parameter sensitivity, out-of-sample performance. DSR/PBO require real engineering
(CSCV) — check for an existing, tested open-source implementation before writing
from scratch.

Larry issues a research classification, never a binary "significant = profitable":
REJECTED, PROMISING, VALIDATION CANDIDATE, HOLDOUT PASSED, FORWARD VALIDATION,
PAPER VERIFIED.

## Team structure

No new agent for the validator role. Larry already fills it structurally. The
change is scope: Larry's mandate becomes confirmation-only (freeze parameters, test
on data the R&D agent never touched, apply DSR/PBO, issue a classification) and is
explicitly barred from proposing what to test next.

## Full pipeline, mapped onto the existing Phase 1-11 framework

| Pipeline stage | Existing Phase |
|---|---|
| Strategy R&D Agent (generate/mutate/combine) | Phase 2 |
| Research Ledger (experiment IDs, search-tree logging, running global count) | Cross-cutting |
| Larry — independent validation | Phase 3-4 |
| Limited Holdout (5 slots, Generation 1) | Phase 5 |
| TradingView / Paper Trading | Phase 6-7 |
| Paper Performance Database | Phase 7-8 infrastructure |
| Risk Engine | Phase 8+ |
| Execution Engine | Phase 8-10 |
| Automated Trader | Phase 10-11 |

## Prominent counter (future work, not today)

The dashboard/roadmap should eventually show something like: "1,847 hypotheses
tested. 37 candidates reached validation. 4 received holdout access. 1 survived."

## Build order

1. Decisions above are locked (done, this session).
2. Acquire additional historical data (cost + quality check first) — not today.
3. Build the Research Ledger, chronological split logic, and Larry's DSR/PBO
   implementation — pure infrastructure, once (2) is settled — not today.
4. Only then build the Strategy R&D Agent itself, scoped to Discovery data only.

## Search stopping point -- checkpoint policy (added 2026-09-03)

Raised by Jason after exp-041's null result: at what point does this
project stop hunting for new hypotheses? No answer to this existed
anywhere in the project's docs before this entry -- `AUTOMATION_ARCHITECTURE.md`'s
"kill switch" only covers live-trading safety controls, a different
question entirely.

Decided (per the Path-to-Profitability Advisor's recommendation, adopted
as-is): review every 5 newly-tested hypotheses whether genuinely distinct
*mechanism families* are still being found, versus thin variants of
families already tested and rejected. This is a deliberate, logged
checkpoint, not a felt sense of "we've tried a lot of things" -- log the
review explicitly in `docs/ROADMAP.md` each time it happens: which
mechanism families have been tried, whether the newest 5 opened a new one
or just varied an old one, and an explicit go/no-go call on continuing
the search versus shifting effort elsewhere (e.g. building out execution
infrastructure for a setup that does eventually clear the promotion bar,
or re-examining whether the promotion bar itself is calibrated correctly
given how many honest nulls it has now produced). This is a checkpoint to
force an explicit decision, not a hard cap -- the search does not
automatically stop at any fixed hypothesis count.

As of 2026-09-03: seventeen hypotheses tested across five mechanism
families (level-sweep liquidity reversal, opening-range/volatility
regime, calendar/seasonal, scheduled-macro-release magnitude, and now
scheduled-macro-release direction), zero cleared the promotion bar. This
checkpoint is retroactively due (17 > 15) -- next hypothesis work should
open with this review rather than jumping straight to a new candidate.
