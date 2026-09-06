# Multi-Factor Combination Model -- Scoping Proposal (v3, APPROVED and TESTED -- exp-046)

## Status: APPROVED by Jason 2026-09-06, line-by-line, as-is. Built and tested the same day as exp-046. Result: REJECTED (clean kill). See "Result (2026-09-06, exp-046)" section below for the full outcome; the rest of this document is kept as the frozen record of what was authorized and why.

This document exists to be reviewed and revised -- by the
Path-to-Profitability Advisor and by Jason, line-by-line, the same
gate exp-036 (volatility regime) went through before any
implementation began. Nothing in this document is frozen yet. It is
the proposal for what WOULD get frozen, if approved.

**v2 changelog**: revised after the Advisor's review of v1 flagged six
real gaps. See the six numbered items below, each addressed inline
where it applies, plus a new "Stability check" step and a new
"Accounting" section.

**v3 changelog**: revised after a second Advisor review of v2 (and
Jason's instruction to close out routine fixes like this one without a
separate follow-up round, per his 2026-09-06 note, to keep this
project's day-to-day usage efficient). Four changes: (1) fixed a real
bug the Advisor caught in `src/build_multi_factor_features.py` -- the
momentum column was silently populated with a continuous magnitude
instead of the +1/-1 sign it claimed to be; fixed and the CSV
regenerated (see updated "Data assembled" section below); (2) pinned
the Step 1 evaluation metric, previously left as an open blank; (3)
quantified the stability-check's disqualifying threshold, previously a
subjective judgment call; (4) formally locked the target variable to
(b), previously phrased as "for discussion."

## Data assembled (2026-09-04, pure prep -- not a test)

Per Jason's go-ahead to start pulling the ingredients together while
this draft is still under review: `src/build_multi_factor_features.py`
now exists and has been run. It joins every candidate feature listed
below into one table, one row per Discovery-slice trading day
(1,717 rows, 2015-01-02 to 2021-10-01), saved to
`data/multi_factor_features_discovery.csv` (gitignored, like every
other data file in this project). It also includes both candidate
target-variable columns (next-day return in points, and its sign) as
descriptive data only -- building this table did not decide between
them.

This is pure data assembly: no model was fit, no statistic was tested,
and nothing here is a result. One real bug was caught and fixed while
building it: NQ's Sunday-evening reopen bars get grouped under
Sunday's own calendar date, which has no valid session close -- left
unhandled, this silently broke the Monday/Friday day-pairing for the
overnight-gap and target columns (a very similar edge case to one
already fixed once before in this project's fade-the-gap study). Fixed
by filtering to only valid trading days before pairing consecutive
days, the same convention already used elsewhere in this codebase.

**Update (2026-09-06, v3): a second real bug was caught, this time by
the Advisor's review, and fixed the same day.** The `momentum_sign`
column was populated by calling
`study_nq_trend_following.compute_momentum_signal()`, which returns a
continuous trailing return (a magnitude), not the +1/-1 sign the
column name and this document both promised -- `compute_positions()`
is the function in that file that actually produces the sign, and it
had not been called. Fixed by calling `compute_positions()` on the
magnitude output, and the CSV has been regenerated; spot-checked
afterward (values are now exactly +1.0/-1.0/missing, 1,337 / 127 / 253
respectively). Also, per this document's v3 changelog above, the
target variable is no longer an open, undecided column pair --
`target_next_day_return_sign` (daily close-to-close) is now the
locked target; `target_next_day_return_pts` remains in the table only
as supporting/descriptive data, not a second candidate.

## Result (2026-09-06, exp-046)

Built and run the same day Jason approved this draft as-is. Implementation:
`src/study_multi_factor_combination.py`. Full results:
`data/study_multi_factor_combination_results.json`. Logged to the research
ledger as hyp-000016 (REJECTED). Path-to-Profitability Advisor independently
reviewed the implementation against this frozen spec and the saved result
before this was reported -- confirmed no spec deviation and no methodological
red flag.

**Modeling population**: 1,457 of 1,717 Discovery rows (260 excluded: 254 for
a missing feature during a warmup window, 6 for an exact-zero target with no
sign), 2016-02-02 to 2021-09-30. Class balance 58.3% up / 41.7% down.

**Step 1 (statistical, no cost): FAILED.** Best out-of-fold AUC (purged
5-fold CV, regularization strength C=0.01, the strongest tried) was 0.4936,
90% bootstrap CI [0.4750, 0.5110] -- squarely straddling 0.5, not
distinguishable from a coin flip. Weaker regularization (larger C) performed
worse, not better (AUC fell to 0.4580 at C=10) -- the textbook signature of
noise, not signal, being fit. Step 2 (costed translation rule) was never
run, correctly gated on Step 1 failing.

**Stability check**: also flagged instability, though for a mechanical
reason consistent with the above rather than a separate concern -- at
C=0.01, every one of the 15 design-matrix columns was zeroed by L1
regularization, both on the full-Discovery fit and independently within
each chronological half. A model with every coefficient at zero predicts a
constant probability, which produces an AUC of exactly 0.5 by convention --
both halves showed exactly 0.5, at the 0.53 instability floor.

**Bottom line**: none of the 8 candidate features -- individually already
null or near-null across exp-020 through exp-045 -- carry joint predictive
information when combined, at least not of the specific kind this model
(linear combination via logistic regression) could find. This closes out
the multi-factor combination idea as scoped; no Validation-slice test was
authorized or warranted, since the frozen gate for reaching Validation was
never cleared.

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

**Decided (v3): (b), daily close-to-close sign.** Roughly half the
candidate features above (COT, turn-of-month, momentum) are themselves
daily/weekly-resolution by nature, and -- confirmed when
`build_multi_factor_features.py` was actually written -- only the
daily target was ever built; no 90-minute intraday target exists
anywhere in this project's code or data. Choosing (a) now would mean
writing new, untested intraday-alignment code from scratch, on top of
mixing daily-resolution features with an intraday target (an extra,
disclosed assumption this project has never needed to make elsewhere).
(b) is not just preferred, it is the only candidate with real
supporting code and data already in hand. Locked; not open for further
discussion absent a new, disclosed reason to revisit it.

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
  out-of-fold **ROC-AUC (decided in v3; not accuracy)** is credibly
  above 0.5 -- no coin-flip model is worth costing out. AUC over raw
  accuracy specifically because it evaluates the model's predicted
  probabilities directly, without needing to first pick a
  classification threshold -- keeping Step 1 a pure statistical check,
  fully separate from Step 2's threshold decision below.
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
   compare coefficient signs and cross-validated AUC between the two
   halves. **Quantified threshold (decided in v3, not a judgment call
   made after the fact):** disclosed as an instability flag, and
   grounds to NOT proceed to Validation even if the full-Discovery fit
   looked clean, if EITHER of the following holds: (i) any feature
   that is non-zero (not L1-zeroed) in BOTH halves has opposite-sign
   coefficients between the two halves; or (ii) either half's
   out-of-fold AUC falls to <= 0.53 (a fixed, pre-registered near-
   coin-flip band, not tuned after seeing the result).
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
