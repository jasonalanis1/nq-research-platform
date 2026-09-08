# Daily Volume Level as a Next-Day NQ Signal -- Frozen Spec (exp-071)

## Status: FROZEN 2026-09-08, before any Discovery-slice number is looked at.

## Why this is genuinely new, not a re-test

Every hypothesis in this project so far has used price alone, except
one: exp-030 (volume-confirmed IB breakout), which tested whether
BREAKOUT-BAR volume (relative to that morning's own IB-window average)
improved an already-rejected INTRADAY strategy -- correlation ~0, no
effect, closed. This is a different question at a different resolution:
does the TOTAL DAY's traded volume, relative to its own recent history,
say anything about the NEXT day's return -- the same "single condition,
whole trading day, Step 1 only" shape already used for VXN/ZN/6E/CL,
just with volume instead of price as the condition. Not previously
tested in this project at daily resolution or as a standalone
(non-breakout-conditional) signal.

## Motivation

"Unusually high volume" is a widely-cited technical-analysis concept
distinct from "volume confirms a breakout" (already tested and closed)
-- the idea that an outsized participation day (regardless of that
day's own direction) often marks either capitulation/exhaustion
(predicting reversal) or informed accumulation (predicting
continuation). Genuinely ambiguous in the literature which way it
should point -- this spec tests BOTH directions honestly by measuring
the actual difference, not assuming a predicted sign the way the
bar-behavior batch did (a lesson taken directly from that batch's
result: predicting a specific direction and then discarding the
opposite-direction finding as noise wasted the batch's most informative
result).

## Frozen hypothesis

Day T's volume = sum of 1-minute Volume across the full calendar day
(reused unmodified daily-bar grouping from
`study_bar_behavior_batch1.build_daily_bars`, extended here to also sum
Volume). Day T's volume ratio = Day T's volume / trailing 20-day
average daily volume (the 20 days strictly BEFORE day T, matching this
project's standard vol-lookback convention).

Split Discovery-slice days into terciles by volume ratio (low / mid /
high, matching the tercile convention already used in
study_volatility_regime.py's own precedent). Test: does NEXT day's
close-to-close log return differ between the HIGH-volume tercile and
the LOW-volume tercile? (Mid tercile reported descriptively only, not
part of the primary test -- matches the existing volatility-regime
precedent of a high-vs-low comparison.)

Statistically credible = 90% bootstrap CI on (mean next-day return
after HIGH volume) - (mean next-day return after LOW volume) entirely
on one side of zero -- NO predicted sign pinned in advance (per the
Motivation section above); either a credible positive or a credible
negative difference counts as Step 1 PASS, reported honestly in
whichever direction it comes out.

## Statistical gate

Step 1 only (no costs), same gate as exp-059 through exp-065. If it
passes: PROMISING, requires the standard costed-rule design + one
prospective Validation-slice test before anything is trusted, same as
every other line. If it fails: REJECTED, closed, no retuning (no
alternate lookback window, no alternate tercile cutoffs tried after
seeing this result).
