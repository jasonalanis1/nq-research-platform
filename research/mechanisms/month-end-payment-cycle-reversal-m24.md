# Mechanism — Month-end payment-cycle reversal, NQ (M24, literature, open scope)

Written: 2026-09-13, ~3:10 am CT (scheduled cycle) · PRE-REGISTERED.
Results seen before writing: NO.
Source CHANNEL: literature. Graziani (2024), "Time Series Reversal: A
Payment Cycle Friction" (EFMA Annual Meeting working paper): the S&P 500
shows a MONTHLY reversal -- a negative return in the final week of a
calendar month credibly predicts a positive return over the FOLLOWING
month. The author attributes this to institutional investors (pension
funds, payroll/dividend-funding accounts) who must liquidate equity
positions to fund cash obligations that cluster at month-end, regardless
of market conditions -- a forced, non-discretionary seller whose price
impact is transient and reverses as the liquidity pressure passes.

## 1. Who is forced, and why
Pension funds, corporate treasuries, and payroll/dividend-funding
accounts must generate cash for month-end disbursements (payroll,
dividends, pension contributions) on a fixed calendar schedule; the sale
is a cash-management necessity, not a view on the market, so it depresses
price without new information, and the depression unwinds over the
following weeks as normal buying resumes. This is a genuinely different
participant and claim shape from every other calendar entry on this map:
- M6 / hyp-000108 (turn-of-month inflows, CLOSED): a different, opposite
  flow (payroll/401k INFLOWS landing as purchases) predicting a POSITIVE
  drift in the FIRST 3 sessions of the month, unconditioned on anything
  that happened the prior month. This entry is the OUTFLOW side, is
  conditioned on the SIGN of the last week's return, and predicts a
  full MONTH of drift, not 3 days -- disclosed explicitly, and Cell 6-7
  below are a direct confound check against this closed family.
- M22 (month-end ZN duration-extension flow, DRAWABLE, not yet scanned):
  a different instrument (bonds, not equities), a different forced
  participant (index-tracking duration mandates, not cash-obligation
  liquidation), a different window (last 2 sessions, not the whole
  following month), and a different direction logic (unconditional
  buying pressure, not a sign-conditioned reversal).
- M5 (month-end NQ-vs-ZN relative performance, CLOSED, clean null):
  a cross-asset RELATIVE claim (NQ vs ZN), entirely different from this
  entry's single-instrument, calendar-conditioned reversal.
- hyp-000022 cross_asset_short_term_reversal (REJECTED): unconditioned
  WEEKLY reversal on a cross-asset basket -- different horizon (weekly,
  not monthly), different instrument set (basket, not NQ alone), and
  unconditioned (no calendar-position trigger).
- M18 (volume-conditioned daily reversal, CLOSED this cycle): daily
  horizon, conditioned on VOLUME, not calendar position. Unrelated
  conditioning variable and unrelated horizon.

## 2. The claim
Following a calendar month in which NQ's LAST-WEEK-OF-MONTH return
(defined below) is in its BOTTOM tercile (a proxy for "meaningful
forced-selling pressure into month-end"), the NEXT calendar month's
cumulative RTH close-to-close return is credibly POSITIVE relative to
NQ's own unconditional next-month drift (NULL 1) -- i.e., the
month-end price depression from forced liquidation reverses over the
following month. Falsifiable in one sentence: if the LOW-tercile cell's
next-month return, net of NQ's own unconditional monthly drift, does not
clear a 90% block-bootstrap CI excluding zero, the payment-cycle
friction is not visible in NQ index futures at this data ceiling and the
entry closes.

## 3. Instrument-choice gate
NQ is not a substitute vehicle here -- it is a direct expression of the
claim: pension and cash-management flows that must liquidate broad
equity exposure to fund month-end obligations transact in, or directly
move, the index itself (cash and futures arbitraged tightly together).
No cross-index comparison is needed; this is a standalone directional
claim in NQ against NQ's own baseline (NULL 1), per the project's
two-nulls convention for a single-instrument directional claim.

## 4. Footprint to measure
LAST-WEEK-OF-MONTH return = NQ's close-to-close return over the final 5
RTH sessions of each calendar month (a fixed, non-discretionary window;
short months use however many trading sessions remain, never fewer than
4). NEXT-MONTH return = close-to-close return from the last session of
month t to the last session of month t+1. Terciles of the last-week
return frozen on Discovery. Block-bootstrap 90% CI (block=3, chosen for
monthly-frequency data with far fewer natural observations than the
project's daily-bar entries -- flagged as a THIN-SAMPLE family from the
outset, same disclosure convention as M19's n=40 events) is the CI of
record.

## 5. Kill rule / confound check
If the "next month" reversal is really just concentrated in the first
1-3 sessions of that month, it is not a month-long reversal at all --
it is the closed turn-of-month inflow effect (hyp-000108/M6) bleeding
across the calendar boundary, and this family is CONFOUNDED, not
independently confirmed, regardless of its own CI. Measured as the
share of the next-month cumulative return attributable to its first 3
RTH sessions (cells 6-7 below); if that share exceeds 50%, the family is
recorded confounded and closes on that basis even if Cell 1 (P1) passes.

## 6. Resurrection check
See Section 1 above for the full disclosure against M6/hyp-000108, M22,
M5, hyp-000022, and M18. Genuinely distinct: single-instrument (NQ),
calendar-position-conditioned (last week of month, sign of return),
month-long horizon, forced-SELLING (not inflow) mechanism. No prior
project entry has tested a sign-conditioned, month-length reversal
anchored on the calendar month boundary.

## 7. Data needed
None beyond what is already on disk: NQ 1-minute OHLCV, already
aggregated to daily bars for every other calendar entry on this map,
and a standard calendar-month boundary (no external calendar needed --
month-end is a property of the trading-day index already in use
project-wide). No new purchase, no new source.

## 8. Realization path
Time-based: if the last week of month t lands in the bottom tercile,
enter long at month t's close, exit at month t+1's close. No stop/target
ambiguity (matches the exit-design requirement before freezing any
monetization spec).

## 9. Product track
Directional, single-instrument (NQ). NQ already has an existing base
strategy path unlike CL/6E/ZN's open monetization gap (this is the same
instrument as the validated volatility facts' underlying), so a
Discovery pass here, if it survives Statistical/Director/Monetization,
would not face the "no base strategy" dead end that stalled M20/M21/M22 at
Monetization -- this is the most direct monetization path of any open
candidate on the shelf.

## 10. Frozen scope (for the scan)
ONE scan, Discovery only (82 calendar months, 2015-01 through
2021-10-01). Terciles of last-week-of-month return frozen on Discovery.
Cells to register:
  1. LOW-tercile (bottom, most negative last week) next-month mean,
     block CI, vs NULL 1                              <- GATING (P1)
  2. HIGH-tercile (positive last week) next-month mean, same statistic
     (P2 asymmetry check -- the mechanism predicts no comparable effect
     here, since it is specifically a forced-SELLING story)
  3. MID-tercile (reported)
  4. LOW minus HIGH, bootstrap on the difference (P2, reported)
  5. unconditional next-month mean (NULL 1)
  6-7. share of the LOW-tercile next-month return in its first 3 RTH
       sessions vs the remaining sessions of that month (confound/kill
       check against hyp-000108/M6)
  8-9. LOW-tercile cell on Discovery first-half vs second-half (P4,
       explicitly flagged LOW-POWER given ~41 months per half against
       an already-thin ~27-month tercile -- descriptive only, not a
       second gate)
  10. same statistic restricted to LOW-tercile months where the next
      month itself does NOT start with a further leg down (a raw
      stability check, reported not gating)
10 cells, 1 gating. THIN-SAMPLE family (flagged in advance, same
disclosure discipline as M19): ~82 monthly observations, ~27 per
tercile. A null here is not strong evidence the effect does not exist
at all -- only that it is not visible at this data ceiling, exactly the
thin-sample framing already applied to M19's n=40 events.

## Status
CLOSED, P1_FAIL (2026-09-13, Scan 031, hyp-000157).

## 11. Disposition (2026-09-13, Scan 031, hyp-000157)
GATING (P1): LOW-tercile next-month return, net of NQ's own
unconditional next-month drift -- mean=+0.0112, ci_90=(-0.0005,+0.0224),
n=27. Lower bound sits just barely on the negative side of zero: NOT
credible. Directionally consistent with the predicted mechanism but not
statistically confirmed at this data ceiling.
SECONDARY (P2 asymmetry): HIGH-tercile net of NULL1 mean=+0.0000
ci_90=(-0.0141,+0.0229), null, as the mechanism itself predicted (a
forced-selling-only story should show nothing on the HIGH side). MID
was credibly negative (ci_90=(-0.0231,-0.0005)), not predicted either
way, reported only. LOW-minus-HIGH difference (the real P2 test):
diff=+0.0112 ci_90=(-0.0109,+0.0328), not credible.
CONFOUND/KILL check: first-3-RTH-session share of the LOW-tercile
next-month return = 0.452, below the 0.5 kill threshold -- NOT
confounded with the closed M6/hyp-000108 turn-of-month inflow effect.
Descriptive-only split (P4, explicitly low-power): first-half
mean=+0.0173 ci_90=(+0.0072,+0.0313) positive; second-half
mean=+0.0055 ci_90=(-0.0175,+0.0204) null. Not treated as a second
gate, consistent with the doc's own framing.
Stability check (cell 10, LOW excluding months with a further leg
down): mean=+0.0210 ci_90=(+0.0010,+0.0433), positive -- but this is a
reported, non-gating cell and does not override the P1 gating failure.
VERDICT: P1_FAIL. Falsifier (a) applies (Section 5). The payment-cycle
friction is not visible in NQ futures at this data ceiling -- thin-
sample family as flagged in advance (80 usable months, ~27 per
tercile). A null here is not strong evidence the effect does not exist,
only that it is not visible at this sample size. Entry closes.
DIRECTOR RE-EVALUATION: CONCUR with closure -- the gating cell's CI
sits close enough to zero (lower bound -0.0005) that a materially
larger sample could plausibly flip it, but per this project's own
discipline a near-miss CI is not treated differently from a clean
miss. No re-test authorized under the family's 2-attempt budget without
new information (e.g., a longer data history or a materially different
instrument).
MONETIZATION: NOT RUN -- gating failed, no path to a strategy design
step.
