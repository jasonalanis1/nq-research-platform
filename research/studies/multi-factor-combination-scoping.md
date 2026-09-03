# Multi-Factor Combination Model -- Scoping Proposal (DRAFT, not yet approved)

## Status: draft scoping proposal only. No code written. Not authorized.

This document exists to be reviewed and revised -- by the
Path-to-Profitability Advisor and by Jason, line-by-line, the same
gate exp-036 (volatility regime) went through before any
implementation began. Nothing in this document is frozen yet. It is
the proposal for what WOULD get frozen, if approved.

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
   21 hypotheses, most came back flat, dead-center nulls -- combining
   zeros with zeros produces zero, it doesn't rescue them. Only a
   couple of findings show any real, non-zero signal at all (the
   CPI/NFP/FOMC magnitude effect, primarily). This model is being
   scoped as an honest experiment, not sold as a likely breakthrough --
   expectations should stay calibrated to that.
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
(day-of-week, turn-of-month, expiration-week). The premise being
tested is whether some COMBINATION of them carries joint information
that no single one showed by itself -- a fundamentally different
question than any single-factor test already run.

- Event-day type (cpi / nfp / fomc / normal) -- `study_economic_calendar.classify_day()`, `study_futures_expiration`'s FOMC classifier
- Volatility regime -- `study_volatility_regime.compute_trailing_volatility()`
- Overnight gap size and direction -- `study_overnight_gap`'s reference-close/gap machinery
- Day-of-week -- calendar, no new code
- Turn-of-month flag -- `study_turn_of_month.classify_turn_of_month()`
- Trailing 252-day momentum sign -- `study_nq_trend_following.compute_momentum_signal()`
- Futures-expiration-week flag -- `study_futures_expiration`'s calendar
- CFTC Leveraged Money weekly positioning change sign -- `study_cot_positioning.py` (2015-2018 only -- this feature would only be non-missing for that sub-window, disclosed as a real limitation, not silently imputed)

**Deliberately excluded from this list**: anything requiring new,
uncosted data (order-flow, options/IV) -- consistent with everything
already parked in `docs/BACKLOG.md`.

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
4. If the Discovery-slice fit shows real joint predictive power, the
   frozen model (coefficients fixed, no more tuning) is tested once on
   Validation data -- the first time this project would use
   `data_split.get_validation_data()` for a genuinely new model rather
   than as a one-time exception, per its intended purpose.
5. "Winner" still means what it has always meant: if this is ever
   translated into an actual trading rule (a costed backtest of "go
   long/short when the model says X"), it is held to the SAME
   promotion bar as every other hypothesis (expectancy > 0 after
   costs, >= 150 trades, 90% CI entirely above zero) -- no new,
   looser bar for this just because it's a model instead of a single
   rule.

## What this is NOT

- Not an open-ended search engine. One frozen specification, tested
  once on Discovery, at most once on Validation if it clears step 4.
- Not a guarantee of finding anything. Given how few non-zero
  ingredients this project has found in 21 tries, a null result here
  is a real, honest, and likely possible outcome -- disclosed up front,
  not added after the fact if it happens.
- Not authorized to be built yet. This draft needs the Advisor's
  review and Jason's explicit line-by-line sign-off on the target
  variable choice, the feature list, and the model type before any
  code is written.
