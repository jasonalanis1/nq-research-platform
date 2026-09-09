# Overnight-Down Wide-Regime Open Fade — Frozen Spec (H92 / exp-120)

Parent finding: OBS-FINDING-009. Same ATR-scaled-stop convention as
H87/H89 (adopted after the cost-dominance diagnostic), applied to a
genuinely new candidate.

## Setup

**Signal:** at the 09:30 RTH open: if the overnight session (prior
16:00 close -> 09:30 open) moved DOWN, AND the prior day was
classified "wide" (top-20th-percentile trailing-20-day range,
volatility_conditioning.py, unmodified) -> LONG (fade the overnight
decline). One signal per qualifying day, at the open bar. No short
side -- OBS-FINDING-009 only measured the down/wide combination; an
overnight-up/wide short-side mirror was NOT found Promising+cost-viable
in the v5 scan (overnight_up/wide/open credible only at 5/10min,
Interesting not Promising, and cost-dominated at 1min) and is not
included here.

**Entry:** open bar's close (09:30 bar). **Stop:** entry - `1.0 *
daily ATR(14)` (unchanged definition from H87/H89).
**Target:** entry + `1.35 * risk` (TARGET_R_MULTIPLE, unmodified).
Exit via `backtest.simulate_trade` (unmodified, exits by end of day if
neither touched). Cost: `ROUND_TRIP_COST_POINTS` (unmodified, 0.75).

## Method

Step 1+2, costed. Bootstrap mean-R-multiple CI, N_BOOTSTRAP=3000,
seed=7, 90% CI. Credible = CI entirely above zero AND mean R-multiple
net of cost >= 0.05R (economically meaningful).

## Disclosed risk (from OBS-FINDING-009)

The underlying setup is infrequent (~1 in 15 Discovery days), so even
a credible per-trade edge implies a low trade count per year --
flagged in the finding, not being re-litigated here, just carried
forward honestly. The Observatory measurement's cost-viable window is
3-10min; this trade needs the move to develop and hold through a
same-day ATR-scaled exit, same structural risk as H87/H89.

## Pre-commitment

No retuning of any parameter (gap regime definition, stop/target
multiples, cost) after seeing this result. One monetization attempt
against this finding; per standing practice a single re-shaped attempt
(e.g. excursion-derived exits) remains available if this one narrowly
misses, same as H81->H82 and H87->H89 precedent -- not more than that.
