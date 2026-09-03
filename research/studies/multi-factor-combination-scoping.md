# Multi-Factor Combination Model -- Scoping Proposal (DRAFT v2, not yet approved)

## Status: draft scoping proposal only. No code written. Not authorized.

This document exists to be reviewed and revised -- by the
Path-to-Profitability Advisor and by Jason, line-by-line, the same
gate exp-036 (volatility regime) went through before any
implementation began. Nothing in this document is frozen yet. It is
the proposal for what WOULD get frozen, if approved.

**v2 changelog**: revised after the Advisor's review of v1 flagged six
real gaps. See the six numbered items below, each addressed inline
where it applies, plus a new "Stability check" step and a new
"Accounting" section.

## Where this came from

After twenty-one hypotheses (single-factor, single-mechanism tests,
one idea at a time), Jason asked whether the project should stop
hunting for one dominant edge and instead build something out of
several smaller real things combined -- the same idea real
quantitative trading firms use (Grinold's "Fundamental Law of Active
Management": combined signal quality scales with both how strong each
signal is AND how many roughly-independent signals go into it).

This project's own `docs/RESEARCH_INTEGRITY_PROTOCOL.md`, written
2026-08-20, already planned for a version of this: a future "Strategy
R&D Agent" (Phase 2: "generate/mutate/combine") gated behind two
prerequisites -- the chronological Discovery/Validation/Holdout split,
and Larry's DSR/PBO multiple-testing correction tooling. Both are now
built and have been applied for real (`src/larry_validate.py`). This
proposal is the disciplined, narrowly-scoped version of that idea: ONE
frozen multi-factor model, not an open-ended search engine.

## Two honest constraints this proposal is built around

1. **This project has very few genuinely non-zero ingredients.** Of
   22 hypotheses now (exp-045, run the same day this draft was first
   written, closed out the CPI/NFP reversal near-miss for good), most
   came back flat, dead-center nulls -- combining zeros with zeros
   produces zero, it doesn't rescue them. Only one finding shows any
   real, non-zero signal at all going into this model (the
   CPI/NFP/FOMC magnitude effect). This model is being scoped as an
   honest experiment, not sold as a likely breakthrough -- expectations
   should stay calibrated to that.
2. **Informally re-reading old write-ups for "hints" is data-dredging.**
   The safe version of "use what we've learned" is: reuse the actual
   NUMBERS already computed in past studies as candidate inputs to
   ONE model, specified in full before any fitting happens -- not
   picking and choosing after the fact which old finding "feels"
   relevant.

## Proposed candidate features (all already computed, nothing new)

Every candidate below reuses an existing column or an existing,
unmodified function from a past study. Inclusion here is not a claim
that each one works alone -- several tested null in isolation
(day-of-week, turn-of-month, expiration-week, and now the direct
CPI/NFP/FOMC reversal bet itself via exp-045). The premise being tested
is whether some COMBINATION of them carries joint information that no
single one showed by itself -- a fundamentally different question than
any single-factor test already run.

- Event-day type (cpi / nfp / fomc / normal) -- `study_economic_calendar.classify_day()`, `study_futures_expiration`'s FOMC classifier
- Volatility regime -- `study_volatility_regime.compute_trailing_volatility()`
- Overnight gap size and direction -- `study_overnight_gap`'s reference-close/gap machinery
- Day-of-week -- calendar, no new code
- Turn-of-month flag -- `study_turn_of_month.classify_turn_of_month()`
- Trailing 252-day momentum sign -- `study_nq_trend_following.compute_momentum_signal()`
- Futures-expiration-week flag -- `study_futures_expiration`'s calendar
- CFTC Leveraged Money weekly positioning change sign -- `study_cot_positioning.py` (2015-2018 only, see gap 2 below)

**Deliberately excluded from this list**: anything requiring new,
uncosted data (order-flow, options/IV) -- consistent with everything
already parked in `docs/BACKLOG.md`.

**Gap 1 (Advisor, addressed): why re-include event-day type after
exp-045 killed it directly.** exp-041/042/045 already answered "does
event-day type BY ITSELF predict a directional reversal" -- no. That is
a different, narrower question than what this model asks: whether
event-day type carries information JOINTLY with other conditions (say,
volatility regime or momentum direction) that neither shows alone.
That is a legitimate, different statistical question, not a relabeled
resurrection of exp-045 -- but it is being flagged explicitly, with a
pre-registered interpretation rule attached: **if the frozen model's L1
regularization zeros out this feature's coefficient entirely, that
result is treated as RECONFIRMING exp-039/040/041/042/045's own
findings, not as a surprise requiring further investigation.** No
follow-up test of this specific feature is planned regardless of which
way it comes out.

## Target variable (needs Jason/Advisor sign-off on which one)

Two candidates, not both -- pick one before freezing:

(a) Sign of the next N-hour (proposed: 90-minute, matching this
    project's existing standard forward-return horizon) forward
    return from each classifiable point.
(b) Sign of the next full trading day's close-to-close return
    (matching the daily resolution `study_nq_trend_following.py`
    already uses).

Recommendation for discussion, not a decision: (b), since roughly half
the candidate features above (COT, turn-of-month, momentum) are
themselves daily/weekly-resolution by nature -- mixing daily-resolution
features with an intraday target would need an extra, disclosed
assumption about how a daily signal applies to an intraday bet.

**Gap 3 (Advisor, addressed): daily resolution needs its own cost
model and trade definition, spelled out now, not decided while
coding.** If (b) is chosen: one "trade" = one full trading day held,
position entered at the prior day's reference close and exited at the
current day's reference close (the exact convention
`study_nq_trend_following.py` already uses for exp-038), with
`FLIP_COST_POINTS` (`2 * ROUND_TRIP_COST_POINTS`, that file's existing
constant, reused unmodified) charged only on days the model's position
differs from the immediately prior day's position. No new cost
convention is being invented.

## Proposed model type: regularized logistic regression, not a black box

A single logistic regression predicting the sign of the target
variable from the features above, with L1 (Lasso-style) regularization
-- chosen deliberately over a more complex model (random forest,
gradient boosting, neural network) for three reasons: (1) it stays
interpretable -- every feature gets one coefficient, explainable in
plain language, matching how every other finding in this project has
been explained; (2) L1 regularization can zero out a feature entirely,
which functions as an honest, principled "this didn't help" the same
way a null hypothesis test does, rather than papering over weak
features with a complex model that always looks like it fits; (3)
fewer free parameters means less overfitting risk with a Discovery
sample of only a few thousand daily rows and a handful of features.

**Gap 2 (Advisor, addressed): the CFTC feature's missing years need an
explicit, pre-registered rule, not an ad hoc coding decision.**
Primary approach: keep the full Discovery sample size for every OTHER
feature by adding a second, paired input alongside the CFTC signal --
a binary "CFTC data available for this date" flag -- and setting the
CFTC signal itself to a neutral value (0, "no signed change") on any
date it's missing. The availability flag lets the model separate "no
COT signal on this date" from "a genuine zero-change reading," rather
than the model wrongly treating a missing year as agreeing with a
flat/no-signal week. Disclosed robustness check, to be reported
alongside the primary result either way: refit the identical model on
the 2015-2018 sub-window only (where CFTC data has no gaps) and check
whether the CFTC coefficient's sign and rough size hold up on that
smaller, fully-populated slice.

**Gap 4 (Advisor, addressed): how a predicted probability becomes an
actual bet, decided now.** Two-stage gate, matching the Step 1/Step 2
structure already used in exp-043/exp-044:

- **Step 1 (statistical, no cost)**: fit the frozen model on Discovery
  via purged/embargoed cross-validation (below), and check whether its
  out-of-fold classification accuracy (or AUC, whichever this
  document's revision settles on before freezing) is credibly above
  50/50 -- no coin-flip model is worth costing out.
- **Step 2 (costed rule, gated on Step 1)**: only if Step 1 clears, the
  simplest possible, deliberately un-tuned translation rule: go long
  if the model's predicted probability of a positive next-day return
  is > 0.5, short if < 0.5. No threshold search, no "optimize the cutoff
  for the best backtest" -- 0.5 is the one and only threshold that will
  ever be tried, chosen for being parameter-free, not because it was
  checked and found to work best.

## Proposed validation discipline

1. Feature list, target variable, and model type are frozen in a
   revised version of this document BEFORE any code is written --
   this draft is not that frozen version.
2. Regularization strength (the one true hyperparameter) is chosen via
   purged/embargoed cross-validation WITHIN Discovery only (reusing
   `src/larry_validate.py`'s existing `purgedcv` integration), never
   tuned against Validation or Holdout. This is disclosed here in
   advance specifically so it cannot later be quietly re-run with a
   different setting if the first one disappoints.
3. This whole model -- one feature list, one target, one model type,
   one regularization procedure -- counts as ONE experiment (its own
   exp-XXX number and research-ledger entry), not a menu of variants.
   No "try a few model types and report the best one."
4. **Gap 5 (Advisor, added as new step): a stability check, run BEFORE
   any move to Validation, the same diagnostic that is what actually
   caught exp-045's problem today.** Split Discovery chronologically in
   half; refit the identical frozen model on each half independently;
   compare coefficient signs and cross-validated accuracy between the
   two halves. Meaningful disagreement (a feature flipping sign, or
   accuracy collapsing to coin-flip in either half) is disclosed as an
   instability flag and is grounds to NOT proceed to Validation, even
   if the full-Discovery fit alone looked clean.
5. If the Discovery-slice fit clears Step 1, the stability check, AND
   shows real joint predictive power, the frozen model (coefficients
   fixed, no more tuning) is tested once on Validation data -- the
   first time this project would use `data_split.get_validation_data()`
   for a genuinely new model rather than as a one-time exception, per
   its intended purpose.
6. "Winner" still means what it has always meant: if this is ever
   translated into an actual trading rule (Step 2 above, tested for
   real), it is held to the SAME promotion bar as every other
   hypothesis (expectancy > 0 after costs, >= 150 trades, 90% CI
   entirely above zero) -- no new, looser bar for this just because
   it's a model instead of a single rule.

## Gap 6 (Advisor, addressed): accounting

This experiment gets its own `exp-XXX` number and Research Ledger
entry like every other hypothesis, and counts toward this project's
cumulative trial count the same way. If it ever produces a candidate
that reaches formal promotion, it goes through Larry's DSR/PBO check
before "promote" is used for real -- no exemption for being a combined
model rather than a single rule. Being "one experiment" internally
(one feature list, one target, one model type -- see validation-
discipline item 3) does not mean it is free of the project's broader
multiple-testing accounting; it is simply one well-defined draw from
that pool, same as everything else.

## What this is NOT

- Not an open-ended search engine. One frozen specification, tested
  once on Discovery, at most once on Validation if it clears the gates
  above.
- Not a guarantee of finding anything. Given how few non-zero
  ingredients this project has found in 22 tries, a null result here
  is a real, honest, and likely possible outcome -- disclosed up front,
  not added after the fact if it happens.
- Not authorized to be built yet. This draft needs the Advisor's
  review and Jason's explicit line-by-line sign-off on the target
  variable choice, the feature list, the model type, and the six items
  addressed above before any code is written.
