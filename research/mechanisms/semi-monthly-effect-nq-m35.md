# Mechanism — Semi-monthly effect on NQ RTH return, NQ (M35, literature channel, open scope)

Written: 2026-09-16, ~3:00 pm CT (scheduled cycle) · PRE-REGISTERED.
Results seen before writing: NO. No scan exists.
Origin: sourcing owed this cycle (shelf at 0/3, directional lane trials
1-4 all closed same-cycle they were sourced) — directional lane trial 5
candidate, sourced per the memo's rule (mechanism/calendar/structure,
never the Idea Factory state library).

## 1. The claim
NQ's mean RTH return on sessions in the FIRST HALF of each calendar
month (the first 9 RTH trading sessions of the month, Ariel's own
window length) is credibly POSITIVE relative to NQ's own unconditional
daily RTH return (NULL 1), while the SECOND HALF of the month (the
remaining RTH sessions) is not credibly different from NULL 1. Source:
Ariel, Robert A. (1987), "A Monthly Effect in Stock Returns," *Journal
of Financial Economics* 18(1), 161-174 — using CRSP data 1963-1981,
Ariel found that essentially the entire cumulative positive return to
holding US equity indices was earned in the first half of the trading
month, with the second half indistinguishable from zero; the finding
has since been replicated out of sample (e.g. Ariel 1990; Lakonishok
and Smidt 1988, *Review of Financial Studies*, "Are Seasonal Anomalies
Real? A Ninety-Year Perspective," documenting a related within-month
pattern across the DJIA 1897-1986). Never tested against NQ, or any
instrument, in this project.

## 2. Who is on the other side
A named, recurring, price-insensitive flow, distinct from the
turn-of-month participant already tested at M6: US retirement and
payroll systems overwhelmingly disburse and invest on a SEMI-MONTHLY or
BIWEEKLY cycle anchored near the 1st and the 15th of the month —
biweekly/semi-monthly payroll runs, employer/employee 401(k) and
pension plan contributions swept into index and target-date funds on
the same schedule, and many corporate and government pay dates
clustering around the 1st and 15th (or the nearest prior business day).
Two contribution waves per month, not one, land new price-insensitive
buying demand into the market roughly every two weeks rather than only
at the month's start. Counterparty: whoever is selling into that
flow — a small, absorbable, mechanical, non-informational stream, the
same category of forced non-behavioral counterparty already accepted
for M1 (cash close), M22 (ZN duration extension) and M24 (payment-cycle
reversal).

## 3. Why this is not the overfitting trap
Single, pre-specified calendar-anchor test using ONLY the existing
trading-day-of-month count (computable from the RTH session index
already on disk project-wide, same aggregation used by M6, M24, M32-34)
— no new data or descriptor code required, no state library involved.
Checked in full against every existing calendar-anchor entry in
`research/idea_inventory.md` and `research/market_structure_map.md`:
- Not M6/hyp-000108 (turn-of-month inflows, spent) — M6 tests ONLY the
  first 3 RTH sessions of the month against the rest of the month, a
  narrow start-of-month window, and its own mechanism is a SINGLE
  monthly payroll/401(k) contribution wave. This entry tests a much
  wider 9-session first-half window against the remaining ~10-12
  sessions of the SAME month, and its mechanism is explicitly a
  TWICE-MONTHLY (semi-monthly/biweekly) flow, not a once-a-month one —
  a different claim, a different window length, and a different
  citation (Ariel 1987, not the turn-of-month literature M6 drew on).
  M6's own closure note ("conditioned on prior month is cosmetic")
  concerned a different, narrower resurrection attempt on the SAME
  3-session window; this entry does not touch that window's boundary
  at all past day 3.
- Not M24 (month-end payment-cycle reversal, CLOSED) — M24 conditions
  NEXT month's return on the LAST week of the CURRENT month's return
  tercile (a predictive, cross-month conditioning claim, forced-selling
  mechanism). This entry makes an UNCONDITIONAL, same-month, two-way
  split (first 9 sessions vs. the rest) with a buying-pressure
  mechanism — different horizon, different sign, different flow
  direction, no conditioning variable at all.
- Not M22 (ZN month-end duration extension, CLOSED) — different
  instrument (ZN), month-END anchored only (last 2 sessions), index-
  duration mechanism, not a within-month split.
- Not M25 (options-expiration week, CLOSED) — monthly opex anchor
  (3rd-Friday-of-month week), dealer delta-hedge mechanism, unrelated
  to trading-day-of-month count.
- Not M5 (month-end/quarter-end NQ-vs-ZN relative performance, spent)
  — cross-asset conditioning variable (NQ MTD minus ZN MTD), tests only
  the LAST 2 and FIRST 2 sessions of the month/quarter boundary, not a
  first-half/second-half split of the whole month.
- Not M28 (pre-holiday, CLOSED trial 1), M32 (DST, CLOSED trial 2), M33
  (weekend/Monday, CLOSED trial 3), or M34 (Santa Claus Rally, CLOSED
  trial 4) — unrelated calendar anchors and mechanisms (exchange-
  closure, circadian/DST, day-of-week, turn-of-year).
- Not the FOMC/CPI/NFP family (M3a CLOSED, M3b one attempt spent, M4
  CLOSED FOR GOOD) — scheduled-announcement mechanism, not a
  trading-day-of-month calendar split; unrelated.
- Not `days_to_monthly_opex` (Entries 1-2, 2-attempt limit EXHAUSTED)
  — that state variable measures PROXIMITY TO monthly options expiry
  specifically (a single date each month) and its own outcome variable
  was realized-volatility compression/release, never a first-half vs.
  second-half return-direction split of the whole month.

## 4. Testable predictions
P1 (GATING). The first-half-of-month window (first 9 RTH trading
   sessions of each calendar month, Ariel's own window length) mean RTH
   return is credibly POSITIVE relative to NQ's own unconditional daily
   RTH return (90% block-bootstrap CI entirely positive).
P2 (reported, specificity). The second-half-of-month window (all
   remaining RTH sessions of the month, after the first 9) reported
   against the same NULL 1 — Ariel's own finding predicts this cell is
   NOT credibly different from zero (the effect concentrates in the
   first half), so a P2 pass in the SAME direction as P1 would weaken
   the claim's specificity rather than support it.
P3 (reported, descriptive). First-half of the Discovery slice (years
   2015-2018) vs. second-half (years 2018-2021) of the first-half-of-
   month effect, both net of NULL 1 — decay check, same style used by
   M33/M34's P3.

## 5. What would falsify this
(a) P1 fails (CI does not clear zero, or clears negative) — closes this
    entry; the documented semi-monthly effect does not transfer to NQ
    futures RTH sessions at this data ceiling.
(b) P1 passes but P2 (second half) ALSO passes credibly positive with a
    similar magnitude — the pattern would not be a first-half-specific
    effect, just an unconditional upward daily drift over the period,
    already known and uninformative as a distinct calendar claim.
(c) Thin-sample check (not expected to bind): first-half sessions occur
    ~9x per month across ~81 months of the Discovery slice — expected
    n well above 500, the best-powered directional-lane candidate
    sourced so far if it clears the ordinary n=40 floor as expected.

## 6. Information gain and edge potential
Information gain: MODERATE — well-powered (expected n in the hundreds,
unlike M32's 13 or M34's 6), a single clean pre-specified split, and a
named non-behavioral counterparty distinct from every prior directional
entry's mechanism family (semi-monthly flow, not turn-of-month, month-
end, weekend, DST, or turn-of-year). If P1 passes and P2 stays null,
this is the first directional-lane candidate with both a credible
gating result AND clean specificity — worth a Statistical-stage look
before any Monetization question is asked (not decided here; the
directional lane's rule is one Discovery-stage shot per cycle
regardless of outcome). If it nulls, it joins M28/M32/M33 as a fourth
decades-old, heavily-replicated calendar anomaly that does not survive
in modern NQ futures — informative on its own terms either way.

## 7. Resurrection ruling (LEARN + Integrity)
NOT M6/hyp-000108 (turn-of-month, spent, 3-session window, once-a-month
mechanism — this entry's window is 9 sessions and its mechanism is
twice-a-month). NOT M24 (month-end payment-cycle reversal, CLOSED,
cross-month conditioning claim, forced-selling). NOT M22 (ZN duration,
CLOSED, different instrument). NOT M25 (opex week, CLOSED, unrelated
anchor/mechanism). NOT M5 (NQ-vs-ZN relative performance, spent,
cross-asset conditioning, boundary-only window). NOT M28/M32/M33/M34
(unrelated calendar anchors/mechanisms). NOT the FOMC/CPI/NFP family
(scheduled-announcement mechanism, unrelated to trading-day-of-month).
NOT `days_to_monthly_opex` (Entries 1-2, exhausted, different outcome
statistic and anchor). RULING: NEW. Attempt 1 of 2.

## 8. Instrument-choice gate
1. NQ only — consistent with this project's current instrument focus;
   uses the existing RTH session index already on disk project-wide
   (same daily aggregation as M6/M24/M32-34), no new data or descriptor
   code needed.
2. Trading-day-of-month count, no lookahead (known trivially at the
   open of each session from the calendar alone).
3. Directional (signed daily RTH return, aggregated to a window mean),
   not magnitude. NULL 1 = NQ's own unconditional daily RTH return over
   the same Discovery slice (same NULL 1 convention as M33).

## 9. Frozen scope (for the scan)
ONE scan, full Discovery range (2015-01-01 -> 2021-10-03,
`src/data_split.py`), NQ daily RTH aggregation (already on disk
project-wide, no new data needed). Within each calendar month, RTH
sessions are numbered by trading-day-of-month (1-indexed, in session
order). Four cells:
  1. First-half sessions (trading-day-of-month 1-9) mean RTH return net
     of NULL 1 (NQ's own unconditional daily RTH return), block-
     bootstrap CI                                          <== GATING (P1)
  2. Second-half sessions (trading-day-of-month 10+) mean RTH return
     net of NULL 1, reported (P2, specificity)
  3. First-half of Discovery years (2015-2018) vs. second-half
     (2018-2021) of the first-half-of-month effect, both net of NULL 1,
     reported descriptive (P3, decay check)
Plus reference/count cells (NULL 1 mean, session counts per group).
Statistical convention: block bootstrap, block=9 (window length, same
"block = overlap length" rule used project-wide — e.g. M32's transition
week block=5, M34's turn-of-year window block=7), N_BOOT=3000,
SEED=20260916, 90% CI, "credible" = CI entirely on one side of zero.
One shot. No new cells, no retuning after seeing results.

## 10. Prediction status
P1 -- untested. P2 -- untested. P3 -- untested. Sourced this cycle
(~3:00 pm, September 16th) to restore the shelf floor after M34 closed
last cycle as directional lane trial 4. Budget allows drawing the same
cycle (memo's own source-then-draw precedent, used for trials 1-4
already).
