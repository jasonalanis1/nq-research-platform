# Mechanism — Pre-holiday effect, NQ (M28, literature channel, open scope)

Written: 2026-09-13, ~3:15 pm CT (scheduled cycle) · PRE-REGISTERED.
Results seen before writing: NO. No scan exists.
Origin: sourcing owed this cycle after M25 (Entry 29) closed and dropped
the shelf below the SHELF RULE v2 floor of 3.

## 1. The claim
NQ's RTH return on the trading session immediately preceding an exchange
holiday (the last session before a market closure -- e.g. the day before
Thanksgiving, the day before Christmas, the day before Independence Day)
is credibly POSITIVE relative to NQ's own unconditional daily RTH
return (NULL 1). This is a long-documented equity-market anomaly
(Lakonishok and Smidt 1988, Review of Financial Studies; Ariel 1990,
Journal of Financial Economics) -- pre-holiday sessions across multiple
decades and markets have shown average returns many times larger than
an ordinary session's average.

## 2. Who is on the other side
No single named counterparty forcing a trade the way a pension fund's
month-end liquidation or a dealer's delta-hedge unwind does. The
literature's proposed explanations are lighter-conviction than this
project's usual named-participant standard: reduced short-selling /
hedging activity ahead of a closure (fewer market participants willing
to carry short risk over a closed session), positive-sentiment bias
going into a break, and thinner volume amplifying a small structural buy
lean. Flagged explicitly as a WEAKER mechanism story than this project's
other open-scope entries (M19-M27 all name a specific forced
participant) -- this entry is included anyway because the empirical
regularity itself is unusually well-replicated across markets and
decades, and testing it against NQ specifically (index futures, not
the cash-equity samples the original papers used) is itself informative
regardless of mechanism precision.

## 3. Why this is not the overfitting trap
This is a single, pre-specified calendar-anchor test (day immediately
before each NYSE holiday in the Discovery slice) using an already-
available, external, non-price-derived calendar (the NYSE holiday
calendar already used for M20's release-day rule) -- not a slice chosen
after looking at NQ's own return data. It is not a variant of any
already-tested calendar entry: distinct from turn-of-month (M6,
first-days-of-month), month-end payment-cycle (M24, closed), and
options-expiration week (M25, closed) -- this is anchored to exchange
CLOSURE dates, a completely different calendar mechanism with no overlap
with any of those anchors.

## 4. Testable predictions
P1 (GATING). The RTH session immediately before an NYSE holiday shows a
   credibly POSITIVE return relative to NQ's own unconditional daily RTH
   return (90% block-bootstrap CI entirely positive).
P2 (reported). The session immediately AFTER a holiday (the first
   session back) does NOT show the same elevation -- specificity check,
   distinguishes a genuine pre-holiday effect from generic
   low-volume-session noise around any market closure.

## 5. What would falsify this
(a) P1 fails (CI does not clear zero, or clears negative) -- closes this
    entry; the historically documented equity pre-holiday effect does
    not transfer to NQ futures at this data ceiling.
(b) P1 passes but P2 also shows the same elevation post-holiday -- not
    specific to the PRE-holiday timing, more likely generic
    holiday-adjacent thin-volume noise, not the mechanism the literature
    describes.
(c) THIN-SAMPLE kill: NYSE observes roughly 9 full-closure holidays per
    year (New Year's, MLK, Presidents, Good Friday, Memorial, Juneteenth,
    Independence, Labor, Thanksgiving, Christmas -- some years fewer
    depending on weekday landing), so Discovery slice (~7 years) yields
    roughly 55-65 pre-holiday sessions. If the usable count comes in
    below ~40, disclose as thin-sample per the same convention as M19.

## 6. Information gain and edge potential
Information gain: moderate. A well-replicated multi-decade, multi-market
anomaly that has never been tested against NQ specifically in this
project. A pass would be a genuinely new directional characterization
fact; a null is also informative (the effect may have decayed since the
original 1980s-1990s literature, or may not transfer from cash equities
to index futures).
Edge potential if real: NQ already has an existing base strategy
(per M24's own framing of NQ's advantage over the open-scope CL/6E/ZN
family) -- IF this passes, a credible near-term path to sizing/timing
integration exists, unlike the 6E/CL structural-volatility family's
usual dead end.

## 7. Resurrection ruling (LEARN + Integrity)
- NOT M6/hyp-000108 (turn-of-month inflows, first sessions of the
  calendar month) -- different calendar anchor entirely (exchange
  closure dates, not month boundaries).
- NOT M24 (month-end payment-cycle reversal, CLOSED) -- different
  calendar anchor, different claimed mechanism (forced selling reversing
  over a month, not reduced short interest before a one-day closure).
- NOT M25 (options-expiration week, CLOSED) -- different calendar
  anchor (third-Friday-of-month, not exchange holidays).
- NOT M22 (ZN month-end duration extension, CLOSED) -- different
  instrument and different anchor.
RULING: NEW. Attempt 1 of 2.

## 8. Instrument-choice gate
1. NQ only -- consistent with this project's current instrument focus;
   NYSE holiday calendar already in use project-wide (M20's release-day
   rule), no new data needed.
2. Daily anchor (the session immediately before/after a holiday),
   same-day horizon -- no lookahead (the holiday calendar is known years
   in advance).
3. Directional (signed daily return), not magnitude. NULL 1 = NQ's own
   unconditional daily RTH return.

## 9. Frozen scope (for the scan)
ONE scan, full Discovery range, NQ daily RTH aggregation (already on
disk project-wide). Four cells:
  1. Pre-holiday session return net of NULL 1 (unconditional daily RTH
     return), block bootstrap CI                        <== GATING (P1)
  2. Post-holiday session return net of NULL 1, specificity check,
     reported (P2)
  3. Unconditional daily RTH return distribution mean (NULL 1 reference)
  4. Trade-count / thin-sample disclosure cell (falsifier c)
Statistical convention: block bootstrap, block=5 (thin annual event
count, consistent with the M19/M22/M25 convention for infrequent
calendar-anchored events), N_BOOT=3000, SEED=20260913, 90% CI,
"credible" = CI entirely on one side of zero.
One shot. No new cells, no retuning after seeing results.

## 10. Prediction status
P1 -- untested. P2 -- untested. NOT drawn this cycle: sourced to restore
the shelf floor per SHELF RULE v2 after M25/Entry 29 closed; drawing
deferred to preserve budget for a careful, unhurried close-out on top of
the M25 disposition already completed this cycle. DRAWABLE as of this
doc's completion; first in line next cycle.
