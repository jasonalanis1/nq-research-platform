# OBS-FINDING-011: Midday-to-Afternoon Range Persistence

Written per the protocol addendum, before any further use.

## Definition

Midday session (12:00-14:00 ET) range in the bottom 20th percentile of
its own trailing 20-day distribution ("narrow midday") vs. afternoon
session (14:00-16:00 ET) range relative to its own trailing 20-day
average ("afternoon range ratio"). Source: study_midday_lull_afternoon_
expansion.py (exp-125), Discovery data.

## Measurement

n=411 narrow-midday days, n=1201 not-narrow days (1612 total usable).
Narrow-midday afternoons: mean ratio 0.713, ci_90=(0.686, 0.743) --
credibly BELOW 1.0 (quieter than average). Not-narrow-midday
afternoons: mean ratio 1.160, ci_90=(1.126, 1.194) -- credibly ABOVE
1.0 (busier than average). Both extremely tight CIs given the large
sample sizes. This is the strongest range-type effect measured in this
project's history (wider spread than hyp-000046/048's 0.94 vs.
baseline or hyp-000056/057's 0.89 vs. baseline).

## Judgment: my own hypothesis was wrong about direction, the finding is real

The frozen spec (research/studies/observatory-v7-design-spec.md) went
in expecting the OPPOSITE result: that a quiet midday represented
pent-up energy that would resolve into an ACTIVE afternoon once
participation resumed. The data says the reverse: activity PERSISTS
within a session, the same direction as every other range-persistence
finding in this project (a narrow day begets a narrow next day; a
coiled overnight begets a tighter RTH day). Recorded honestly per the
LEARN principle -- my mechanism story was wrong, but the underlying
family of measurements (activity/range persistence over adjacent
windows) is now confirmed a THIRD time, at a different time scale
(within-day session-to-session, vs. day-to-day and overnight-to-day),
and with the strongest effect size yet. The real mechanism is more
likely simple volatility clustering/regime persistence operating at
finer granularity than previously measured, not a liquidity-vacuum/
release story.

## Status

Real, very strong, high-confidence measurement. Same category as
hyp-000046/048 and hyp-000056/057 -- a volatility-conditioning fact,
not a directional signal. Given its strength (this is the tightest,
largest-sample range-persistence result the project has produced),
recommend folding it into volatility_conditioning.py as a same-day
intraday multiplier (usable from 14:00 onward once the midday session
is known), same treatment as the other two validated findings. Not yet
prospectively validated on the Validation slice -- required before
being trusted for that use, per standing protocol (pre-registered
single test, same as hyp-000048/057's own validation).

## Prospective validation (exp-126) -- PASSED

n=142 narrow-midday Validation days: mean ratio 0.816, ci_90=(0.762,
0.878) -- credibly below 1.0, same direction as Discovery, clear
margin (not marginal). n=404 not-narrow: mean ratio 1.091, ci_90=
(1.037, 1.147) -- credibly above 1.0. This is the project's THIRD
finding ever to survive a Validation-slice prospective test, and the
cleanest/most confident of the three (tightest CIs relative to effect
size, largest combined sample). Integrated into
src/volatility_conditioning.py as get_afternoon_conditioning() --
kept separate from the existing get_volatility_conditioning() function
because this signal is only known intraday (14:00 ET onward), not at
the open, so it cannot be conflated with a pre-open sizing decision.
