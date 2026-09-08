# Meta-Review: Discovery-to-Validation Replication Rate (2026-09-08)

## Why this exists

After ~70 experiments across price/time patterns, volatility, cross-
market single-instrument leads, a real-options-data variance-risk-
premium check, a batch of bar-level behaviors (plus a prospective
follow-up), and two ensemble/multi-factor-combination attempts, every
currently-scoped research line is now closed (REJECTED). Rather than
reflexively picking a new, unscoped data category to search next (the
Advisor's explicit caution), this is a step back: what does the
project's own 42-hypothesis ledger say about whether MORE category-
hunting is actually a good use of time right now?

## The finding

**Every single hypothesis that ever reached a real Validation-slice
(prospective) test has failed to replicate. 6 for 6, 0%.**

| Discovery-stage "PROMISING" candidate | Validation-slice test | Result |
|---|---|---|
| hyp-000023 (weekly trend, low-vol-regime split) | hyp-000024 | REJECTED |
| hyp-000025 (collective-evidence pilot, trend family) | hyp-000026 | REJECTED |
| hyp-000027 (intraday collective-evidence pilot) | hyp-000028 | REJECTED |
| hyp-000031 (ZN bond-lead standalone) | hyp-000035 | REJECTED |
| hyp-000037 (bar-behavior rejection wick) | hyp-000040 | REJECTED |
| hyp-000039 (bar-behavior failed breakout) | hyp-000041 | REJECTED |

This is not "we haven't found the right category yet" -- it's a
consistent, structural pattern: Discovery-stage evidence in this
project has NEVER once held up out of sample, across very different
mechanism types (trend-following variants, cross-market lead/lag,
candle-level behavior). That is the signature of a systematic issue
with how Discovery-stage "promising" gets decided, not bad luck on
which market/mechanism to search next.

## Candidate explanations (not mutually exclusive)

1. **The Discovery window (2015-2021) may not represent the Validation
   window's (2021-2024) actual regime.** 2021-2024 includes the fastest
   Fed hiking cycle in decades and very different realized-vol dynamics
   than most of 2015-2021. A real relationship in one regime plausibly
   just isn't present in the other -- this would show up exactly as "6
   for 6 fails," independent of any methodology flaw.
2. **Genuine multiple-testing/degrees-of-freedom inflation at the
   Discovery stage.** Even with the no-shotgun discipline, choices made
   along the way (which confirmation-rule variant, which lookback,
   which threshold) add up across dozens of experiments to real
   flexibility that a single 90%-CI-on-Discovery-alone check doesn't
   fully account for.
3. **NQ intraday/daily returns in this window may simply be close to
   informationally efficient at the timeframes tested (daily-resolution
   single-condition signals).** Not provable from this ledger alone,
   but consistent with the data.

## A separate, smaller finding: ledger status hygiene

4 hypotheses (hyp-000023, hyp-000025, hyp-000027, hyp-000031) are still
recorded with `strategy_status: PROMISING` as their most recent (only)
ledger row, even though each was later closed by a Validation-slice
test under a DIFFERENT hypothesis_id (hyp-000024/026/028/035
respectively). The ledger's append-only design means a reader has to
manually trace `parent_hypothesis_id` chains to see this -- scanning
`strategy_status` alone currently overstates how many candidates are
still actually live (shows 8 PROMISING; only ZN's status is arguably
still "open" in spirit, and even that was superseded). Flagging this as
a real, fixable reporting gap, not proposing to edit history -- the
ledger's own "append, never edit" rule is a deliberate integrity
feature, not a bug, so the fix belongs in tooling (e.g. a small script
that resolves parent chains for reporting) rather than the ledger
itself.

## Recommendation

Per the Advisor's review: this doesn't mean stop testing new ideas
forever, but it does mean the RIGHT next use of time is not "search
category #12" on the same Discovery-stage methodology that has never
once produced a durable result. Two honest options going forward,
neither requiring Jason's involvement to start per his standing
autonomy rule (this is process work, not a promotion/kill decision or
a purchase):

1. Before any new hypothesis, check whether Discovery-stage effect
   sizes across all 42 logged experiments are systematically larger
   than what later held up -- a simple, cheap analysis of the ledger's
   own numbers (no new data, no new code beyond a summary script).
2. If a new mechanism is tested going forward, treat Discovery-stage
   "PROMISING" with more skepticism than before -- this ledger itself
   is now the strongest evidence available that a Discovery pass is
   necessary but nowhere near sufficient.

This is a process finding, not a hypothesis test -- no ledger entry
logged for it (nothing was tested against price data). Filed here as a
research-integrity artifact for the next actual hypothesis this project
runs.
