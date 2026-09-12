# Mechanism — Nasdaq-100 quarterly rebalance close-window volume/move (M9)

Written: September 11th, 11:38 pm CT (2026-09-12 04:38 UTC)  ·  Pre-registered
Results seen before writing: no — this doc precedes Scan 018 (not yet written or run).

## 1. The claim
Nasdaq-100 index funds and other passive trackers are contractually
obligated to hold the new index share weights (and, on the December quad-
witching Friday, the new index composition) starting the following
trading session. Because the effective date is fixed and announced in
advance, these funds trade to match it precisely at the closing print of
the quarterly quad-witching Friday (3rd Friday of March/June/September/
December) — this concentrates price-insensitive, forced volume in the
last 10 minutes of that session. This should show up as (a) elevated
close-window trading volume vs. a normal day, and/or (b) an abnormal
close-window price move, with at least partial reversal in the following
session as the temporary price impact of the forced flow fades.

## 2. Who is on the other side
Counterparty: liquidity providers, market makers, and arbitrageurs who
recognize the rebalance-day imbalance and take the other side of it,
expecting the price impact to be temporary and to mean-revert once the
forced flow clears — they are compensated for absorbing the imbalance by
the reversal itself.

## 3. Testable predictions
P1. The close-window (last 10 minutes of RTH) sign-adjusted move on
quarterly rebalance Fridays is credibly larger in magnitude than on
matched normal (non-rebalance) days — the single pre-registered gating
cell.
P2 (reported, not gating). The following session's sign-adjusted open-to-
close return shows at least partial reversal of the rebalance-day
close-window move (a temporary-impact signature, not a permanent level
shift).

## 4. What would falsify this
Close-window move/volume on rebalance Fridays not credibly different from
normal days (no detectable forced-flow signature at all), OR a credible
close-window effect that shows NO reversal tendency the next session (a
permanent level shift would argue the mechanism isn't temporary
price-impact from forced flow, though it would not by itself disprove
that flow occurred).

## 5. Prediction status
P1 — INDETERMINATE — Scan 018 ran but could not test the claim: n_rebalance_days = 0
(see Section 6). Not a null result.
P2 — not reached (P1 did not produce a usable sample).

## 6. Verdict
INDETERMINATE — data cannot support this test, not a refutation. Scan 018
(run 2026-09-12, ~12:15 am CT) found ZERO usable rebalance Fridays in the
1612-day Discovery-slice sample, out of 27 quarterly quad-witching Fridays
that fall within the Discovery date range (2015-02 to 2021-10). Root
cause, verified directly against the raw source CSV
(data/NQ_1min_databento_2026-09-09.csv): the continuous-contract data file
has a genuine, systematic gap on every single one of these 27 dates —
trading data simply stops between roughly 09:29 and 09:30 ET on the
rebalance Friday itself and does not resume until the following session
(confirmed for 2018-03-16, where the file jumps directly from a
2018-03-16 09:29 ET row to a 2018-03-19 09:20 ET row, skipping the entire
Friday RTH session, the weekend, and Monday premarket — the same pattern
holds for all 27 candidate dates checked). This is NOT a scan bug (no
units error, no off-by-one, no timezone issue — verified by direct
inspection of both the built feature frame and the raw CSV) and NOT a
thin-sample null — it is a complete absence of the needed observations,
caused by the fact that the Nasdaq-100 quarterly rebalance date is also
the CME quarterly NQ futures expiration/roll date, and the continuous-
contract series this project's data pipeline is built on appears to have
been assembled with a gap exactly at each quarterly roll's RTH session.
This is a data-construction issue affecting M9 specifically (its event
dates are, by definition, futures-roll dates) and does not affect any
other closed map entry.

Because zero rebalance-day observations were produced, no analytical shot
was actually taken at the claim -- P1's stated falsifier was never given
a chance to fire. Per the standing 2-attempt convention, this does NOT
count as a spent attempt: an indeterminate result from a data-availability
failure is not the same as a null or near-miss from a real test. M9 is
returned to the map as PARKED, now for a corrected, more specific reason:
not "no calendar" (the calendar is built, verified, and correct — see
src/nasdaq_rebalance_calendar.py) but "no roll-day RTH data in the current
continuous-contract file." This is an IMMEDIATE item for Jason: M9 cannot
be tested further without either (a) a different/supplementary NQ data
source with roll-day coverage (e.g. a raw front-month series that does not
gap on expiration, or an explicit back-adjusted continuous series built to
preserve roll-day RTH bars), or (b) a decision to retire M9 permanently as
untestable with available data. Calendar provenance unchanged: 3rd Friday
of Mar/Jun/Sep/Dec, mechanically computed, verified against Nasdaq's own
2025 reconstitution press release; ad hoc special rebalances excluded from
scope entirely.
