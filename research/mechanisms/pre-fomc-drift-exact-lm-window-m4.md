# Mechanism — pre-FOMC drift, exact Lucca-Moench window (M4, attempt 2 of 2, LAST)

Written: September 11th, 11:14 pm CT (2026-09-12 04:14 UTC)  ·  Pre-registered
Results seen before writing: no — this doc precedes Scan 017 (not yet written or run).

## 1. The claim
Following Lucca-Moench (2015), NQ drifts upward over the exact 24 hours
before an FOMC statement — prior-day 14:00 ET to FOMC-day 14:00 ET — because
option sellers, dealers, and systematic vol-targeting books reduce
short-volatility/hedging inventory ahead of the event and buy back equity
exposure as the event risk resolves and is priced out. This is distinct
from hyp-000111 (attempt 1), which measured the prior day's full RTH return
plus the overnight return into the FOMC morning — a different, non-exact
window that both excludes part of the prior afternoon (14:00->16:00) that
the true L-M window includes... no, precisely: 111's construction EXCLUDES
the prior-day morning (09:30-14:00) that the L-M window does NOT include
either, but 111 INCLUDES it by using the full prior RTH day, and 111
EXCLUDES the FOMC-day 09:30-14:00 session that the true L-M window DOES
include. The two windows overlap substantially but are not identical — this
is the map's own entry condition, verified in the generation meeting.

## 2. Who is on the other side
Counterparty: insurance buyers who purchase downside protection (puts,
short-equity hedges) into the meeting and pay away the drift as the premium
for that protection — a price-insensitive, calendar-driven buyer of
protection rather than a view-driven trader.

## 3. Testable predictions
P1. The L-M window (prior-day 14:00 -> FOMC-day 14:00) mean return, in ATR14
units, is credibly positive across FOMC days in the Discovery slice — the
single pre-registered gating cell.
P2 (reported, not gating). The FOMC-window mean is compared against a
matched baseline: the same 24-hour window (previous-day 14:00 -> next-day
14:00) on all non-FOMC trading days in Discovery — the effect should be
larger than the unconditional baseline drift, not just positive in
isolation.

## 4. What would falsify this
L-M-window mean return not credibly positive, OR not credibly larger than
the matched non-FOMC baseline (i.e., indistinguishable from ordinary
day-to-day drift).

## 5. Prediction status
P1 — NOT CONFIRMED (near-miss, not credible) — Scan 017: n=52 FOMC-day-
ending 14:00->14:00 windows, mean +0.1329 ATR, ci_90 [-0.0052, +0.2632].
Direction matches the prediction (positive) and the lower CI bound sits
just barely below zero — a genuine near-miss, same shape as Scan 012's
NQ-ZN correlation-breakdown near-miss — but it does not clear the credible
bar (CI must exclude zero). P1_FAIL, not retuned.
P2 — not tested — pre-registered scope: read only if P1 passes; it did not.

## 6. Verdict
NOT CONFIRMED at Discovery — a near-miss, not a clean null, but the
pre-registered bar (credibly positive) was not cleared. This was the
SECOND AND LAST attempt on pre-FOMC drift (hyp-000111 = attempt 1); the
2-attempt limit is now exhausted. Pre-FOMC drift CLOSED FOR GOOD as a
family. No hypothesis id spent (did not clear the credible+cost-floor
screen). LEARN entry filed: near-miss, not a named failure mode — worth
remembering if a materially different, non-resurrective window is ever
proposed for a THIRD family member, though the 2-attempt convention means
that would need Director sign-off as a genuinely new claim, not a
retry.
