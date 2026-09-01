# exp-031 — Day-of-Week Conditioning of Initial Balance Breakout, Discovery slice (real data)

**Date:** 2026-09-01
**Status:** kill (no weekday shows a meaningfully different result; none clears the promotion bar)

## Hypothesis

Day-of-week / calendar-position effects (the "Monday effect" and
related weekend/turn-of-week anomalies) are a long-documented, if
debated, empirical phenomenon in academic finance. Does which NY
business day it is change anything about Initial Balance Breakout's
already-collected trade outcomes? Full definition:
`research/setups/day-of-week-ib-breakout.md`.

## Data used

The SAME 1654 already-resolved Discovery-slice Initial Balance Breakout
trades from exp-028 (detection/entry logic completely unchanged) — no
re-detection, no parameter change, just grouped by each trade's NY
calendar day-of-week.

## Method

`pd.Timestamp.day_name()` on each trade's date, grouped into
Monday-Friday. Per weekday: trade count, win rate, expectancy (mean
`r_multiple_net`), total R, and a 90% bootstrap confidence interval on
total R (2,000 resamples, same convention as every other setup in this
project). All five weekdays reported regardless of outcome, per the
frozen doc's anti-cherry-picking rule.

Reused the exact same verified fast-scan approach as exp-028/030 (byte-
identical to `detect_ib_breakout.scan_all_days()` on a 200-day check
slice) via a temporary driver, deleted after use.

## Results

| Weekday | n | Win rate | Expectancy | Total R | 90% CI | Significant? | Clears promotion bar? |
|---|---|---|---|---|---|---|---|
| Monday | 346 | 42.5% | -0.092R | -31.88 | [-68.90, +4.94] | No | No |
| Tuesday | 335 | 43.6% | -0.056R | -18.64 | [-52.98, +17.46] | No | No |
| Wednesday | 334 | 42.2% | -0.091R | -30.31 | [-66.08, +4.51] | No | No |
| Thursday | 339 | 42.2% | -0.074R | -25.19 | [-59.70, +10.28] | No | No |
| Friday | 300 | 42.3% | -0.069R | -20.85 | [-53.30, +12.15] | No | No |

## Interpretation

**Clean null, and a notably uniform one.** Every single weekday is
negative, every weekday's expectancy sits in a tight band (-0.056R to
-0.092R, a much narrower spread than sampling noise alone would need to
produce something that looks this consistent), every weekday's win rate
clusters around 42-44%, and no weekday comes remotely close to the
150-trade / positive-expectancy / CI-above-zero promotion bar. If a real
day-of-week effect existed in this setup's results, it would most
plausibly show up as one or two days behaving meaningfully differently
from the rest — instead, the failure Initial Balance Breakout already
showed in aggregate (exp-028) shows up almost identically no matter
which day of the week it is. This is evidence AGAINST a day-of-week
explanation for the setup's overall negative result, not evidence for
one hiding in a specific day.

This is now the third characterization/conditioning check in a row
(after open-return-persistence and volume-confirmation) to come back
null on Initial Balance Breakout's trades. Taken together, none of
price direction, breakout volume, or calendar day-of-week meaningfully
explains or rescues the setup's rejection.

## Next step

Kill — no weekday is worth carrying forward as its own candidate, and
this doesn't point toward a promising subgroup to dig into further. Of
the three conditioning angles tried since exp-028 (price persistence,
volume, day-of-week), all three are now closed. Genuinely new ground
from here would mean either a different setup family entirely, a finer
calendar cut (e.g. week of monthly/quarterly index futures expiration,
economic-release days) that would need new data (an economic calendar)
this project doesn't have yet, or accepting that pure intraday
price/volume/calendar patterns around the 8:30 open, tested the several
ways established market theory suggests, have not turned up a real edge
in this dataset so far.
