# Intraday Behavior Batch 3 — Frozen Spec (2026-09-08)

Search batch ID: `batch-2026-09-08-intraday-behavior-3`. Step 1 only.
Discovery slice only. The remaining 2 of the Market Behavior Advisor's 5
original candidates from the batch-2 sourcing round, queued in the
backlog and picked up the same session per Jason's "run them all now"
instruction.

## The 2 conditions

**exp-083 — Midday lull character / afternoon re-engagement.** Define
the "lull" as 12:00-13:00 ET. Compute the lull's own net directional
return. Outcome: return from 13:00 ET to session close, signed WITH the
lull's own direction (continuation test), no sign pinned in advance.
Genuinely different from exp-080 (which used the FIRST hour's shape, not
midday) and from exp-072 (which used volume concentration/skew across
the whole session, not the lull window's own directional character).

**exp-084 — Overnight (Globex) range compression ("pre-open coiling").**
Overnight range = High-Low across all 1-min bars from the prior day's
16:00 ET reference close to the current day's 09:30 ET open. Classify a
day's overnight range as "coiled" if it's in the bottom
`COIL_PCTL=20` of its own trailing 20-day overnight-range distribution.
Outcome: that day's own full RTH-session range (09:30-16:00 ET),
relative to its trailing 20-day average RTH range (a ratio, same
convention as exp-074/hyp-000046). Checked for overlap with hyp-000046/048
(range-contraction): that finding used the PRIOR DAY's full RTH range to
predict the NEXT day's range; this uses the SAME day's OVERNIGHT
(Globex, thin-liquidity) range to predict that SAME day's own upcoming
RTH range -- a different anchor (overnight vs. prior full session) and a
same-day (not next-day) relationship, so it is not a restatement, though
related in spirit (both are volatility-persistence-flavored). Disclosed
explicitly per the Market Behavior Advisor's own flagged risk on this
candidate.

## Method

Same as batch 1/2: nonparametric bootstrap, N_BOOTSTRAP=3000, seed=7,
90% CI, Step 1 only. Any pass logged PROMISING and provisional pending a
single Validation-slice prospective test, per the effect-size-inflation
diagnostic's finding.

## Multiple-testing disclosure

2 pre-registered conditions, one shared `search_batch_id`, run together,
no follow-up conditions added after seeing results.
