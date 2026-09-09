# Pre-NFP (Jobs Report) Announcement Drift -- Observatory v12 Design Spec

Frozen 2026-09-09. Continuation of the pre-FOMC drift thread (same
"macroeconomic announcement premium" family, Savor & Wilson 2013;
window/magnitude sourced from a related NBER working paper on
pre-announcement returns). CPI was considered and explicitly NOT
selected -- the same literature source reports CPI's pre-announcement
drift as small and NOT statistically significant (-2.14bps, t=-0.69),
so it isn't a strong enough mechanism to spend a hypothesis slot on.
NFP (Non-Farm Payrolls / jobs report) is: positive drift, economically
meaningful, statistically significant in the source literature
(~10bps, t=3.63) -- a real candidate, unlike CPI.

## Mechanism

NFP is released at 8:30am ET on (almost always) the first Friday of
each month. The literature attributes a positive pre-release drift to
a risk premium for scheduled uncertainty resolution -- investors
demand compensation for holding into a known high-impact information
event, not because they know the outcome direction. Same family as
pre-FOMC drift (tested this session, thin/non-credible but right-
direction and above cost floor) -- this is a second, independent shot
at the same "scheduled-macro-announcement premium" mechanism, with a
different (non-overlapping) calendar, roughly doubling the combined
evidence available on this mechanism family without touching the
FOMC result itself.

Data requirement: NFP release dates -- free, public (BLS calendar).
Approximated here as the first Friday of each month (the standard
rule; occasional shifts due to holidays/government shutdowns are a
known, rare exception -- flagged as a caveat, same as the FOMC date
list, costs a few observations at most if a date is off, not a
systemic bias).

## Definition (directional, pre-specified from literature)

Event: NFP day = first Friday of each month (Discovery-period
exceptions not individually re-verified this session). Window: prior
trading day's close (16:00 ET) through 5 minutes before the 8:30am ET
release -- approximated here as the overnight return (prior RTH close
-> NFP-day open, since our bars don't extend to 8:25am specifically
but overnight covers the full pre-release window). Outcome: overnight
return (signed, points) on NFP days vs. all other days (complement).

Pre-specified direction (from literature): NFP-day overnight return
skews POSITIVE relative to the complement. Stated before running
Discovery.

## Method

Bootstrap mean-difference CI (N_BOOTSTRAP=3000, seed=7, 90% CI), same
convention as pre-FOMC drift and observatory_v5. ATR-normalized
cost-aware screen applies (0.05 floor). Credible = CI excludes zero
AND direction matches the pre-specified positive sign.

Sample size: ~78 NFP dates expected in Discovery (2015-2021-10-03,
~12/year) -- meaningfully LARGER than the FOMC sample (~53), some
protection against the thin-sample issue that limited the FOMC result,
though still modest by the project's own MIN_N_FOR_PROMISING=40
threshold once split any further.

## Per protocol

Exploratory only, Discovery data only, non-trading. A credible AND
cost-viable result gets its own Behavioral Finding, then a frozen
hypothesis spec through Discovery -> Validation (2-attempt limit)
before any live consideration. A null result is logged and closes
this thread -- no retuning the date rule or window after seeing the
result. This closes out the macro-announcement-premium family for
this research cycle regardless of outcome -- CPI is deliberately not
tested (weak literature support), and no third macro-release
candidate will be added without a new mechanism-first reason.
