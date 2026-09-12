# Statistical stage — hyp-000148 (M20, EIA report volatility jump, CL)

Written: September 12th, ~6:10 pm CT (scheduled cycle). Discovery-slice
Statistical review per pipeline order, before Director Re-Evaluation.

## Result under review
Post-release hour (10:30-11:30 ET) |return|/ATR14 = 0.367, vs the
unconditional RTH-hour baseline 0.186 (n=9,305 hourly observations across
all Discovery sessions). Difference +0.181 ATR, 90% CI (+0.155, +0.216),
n=329 release dates (of 352 computed; 23 fell in a session this project's
own gap rules already excluded, e.g. roll days — none were skipped for a
release-specific reason). Nearly 2x the unconditional hourly magnitude.

## 1. Stability / regime dependence
First half of Discovery: 0.415. Second half: 0.318. Both far above the
0.186 unconditional baseline and each individually would clear the same
gate on its own half (unconditional baseline recomputed per half would
need its own check, not done here — flagged as a limitation, not a
blocker: even a generous doubling of the unconditional baseline in the
second half would still leave a gap). Directionally consistent with mild
decay (options/vol markets have gotten better at pricing scheduled event
risk over the sample), not with the effect flipping or vanishing. No
regime-dependence red flag.

## 2. Magnitude, after realistic costs
This is a MAGNITUDE fact (volatility), not a directional return — it has
no "cost after slippage" in the ordinary sense because nothing is bought
or sold on the strength of it alone. Its economic content is: an hour
that behaves like ~2x an ordinary RTH hour should be sized, stopped, and
timed accordingly by any OTHER strategy or the volatility-conditioning
module, and options structures priced around it would be underpriced if
they used the unconditional volatility. Economic significance is
judged at Monetization, not here.

## 3. Selection sensitivity (same-data risk) -- MUST DISCLOSE
The release-day list (Wednesday, Thursday after a Monday federal holiday)
is a MECHANICAL, public rule computed from a standard third-party
calendar (pandas USFederalHolidayCalendar) — it was fixed in the
mechanism doc before the scan ran and required no fitting, no threshold
search, no lookback tuning. The hour window (10:30-11:30, matching the
report's release time) is likewise fixed by the report's own published
schedule, not chosen after looking at the data. Nothing in this result
was selected after seeing it. Multiplicity: 1 gating cell, registered
before the scan (scan_023_2026-09-12 in SCAN_REGISTRY).

## 4. The near-kill disclosure (this is the substantive finding of this
## stage, and it changes the read on the result)
The first-minute share is 0.481 — 3 points from the 0.5 kill line. That
means very close to HALF of the post-release hour's excess |return| is
concentrated in the single minute the report crosses (10:30-10:31). This
is not a coincidence of one release-year; it is consistent with modern
market structure (algos react to the print within seconds) and with the
literature's own more recent findings (post-2015 studies show the
initial reaction has compressed toward the print itself as speed
increased, even as the AGGREGATE hour-long effect Andersen et al. found
in 1998-2000 data persists in weaker form).

**Reading**: the finding survives (0.481 < 0.5, and the mechanism doc's
own kill rule is explicit and was not moved after seeing this number) but
its INTERPRETATION shifts. This is closer to "a scheduled volatility
event, roughly half of which resolves in the print itself and half of
which continues to resolve over the following ~59 minutes" than to "a
slow hour-long repricing drift." That is still useful for sizing/stops
(the whole hour is elevated, print or no print) but the Monetization
question is narrower than the mechanism doc first framed it: this is NOT
primarily a "trade the drift after the print" opportunity (that would
need the print-minute excluded and re-tested — NOT done here, as that
would be retuning after seeing this number, which the anti-optimization
rule forbids for THIS attempt).

## Verdict
STATISTICALLY SOUND, PASSES TO DIRECTOR RE-EVALUATION, with the near-kill
disclosure carried forward as a hard constraint on what Monetization is
allowed to propose (a sizing/volatility input over the full hour, not a
post-print drift-capture strategy — that would be a DIFFERENT claim
requiring its own pre-registration, not a reinterpretation of this one).
