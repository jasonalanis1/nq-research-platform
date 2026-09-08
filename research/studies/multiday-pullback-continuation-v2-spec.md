# Multi-Day Pullback Continuation, Frequency-Increased Follow-Up — Frozen Spec (exp-109)

## Why this is a legitimate follow-up, not a retune-after-result

exp-108 (hyp-000079) was NOT rejected -- it was CREDIBLE and
economically meaningful, just too thin (n=15) to trust or test further.
This is the same category of legitimate extension this project has used
before (e.g. extending the COT-positioning Discovery window to its
intended full range before its own separate prospective test): widening
the net for a structural, disclosed reason to get a trustworthy sample
of the SAME underlying idea, not retuning thresholds after seeing a bad
result to manufacture a good one. Per the 2026-09-08 staff meeting, two
structural changes, made together and disclosed:

1. **Allow repeat signals per trend segment** (exp-108 capped at the
   FIRST pullback re-cross only, to avoid double-counting a choppy
   MA-straddling stretch as many signals). This version allows every
   valid re-cross, with a `MIN_BARS_BETWEEN_SIGNALS = 5` cooldown so two
   signals can't fire on adjacent days.
2. **Shorter trend/pullback windows**: `TREND_MA = 30` (was 50),
   `PULLBACK_MA = 10` (was 20) -- a faster cadence that both defines
   "established trend" more often and pulls back to it more often,
   appropriate given the amount of Discovery history available (an MBA
   observation: 50/20 was slow relative to how much data we have).

Stop (`1.5 * ATR14`), target (`1.35R`), and 20-day max-hold timeout are
UNCHANGED from exp-108.

## New risk this raises, and how it's handled

The Path-to-Profitability Advisor flagged that repeat signals within
the same trend segment are not independent draws (they share the same
underlying trend condition) -- the standard bootstrap CI assumes
i.i.d. resampling. This run reports BOTH the standard bootstrap AND a
block-bootstrap-by-trend-segment check (resampling whole trend segments
with all their signals together, not individual trades) as a robustness
check on the same result. If the two disagree materially, the
non-independence concern is treated as disqualifying regardless of what
the standard bootstrap alone shows.

## Method

Otherwise identical to exp-108: Step 1+2 together, N_BOOTSTRAP=3000,
seed=7, 90% CI, credible = CI entirely above zero AND mean R-multiple
net of cost >= 0.05R.

## Multiple-testing disclosure

One frequency-increased follow-up to hyp-000079, `search_batch_id
batch-2026-09-08-multiday-pullback-v2`. This is the ONE follow-up this
too-thin result earns -- a null or still-too-thin result here closes
the multi-day pullback-continuation idea for good, no further window
tuning.

## Decision rule / pre-commitment

Credible (on BOTH the standard and block-bootstrap check) +
economically meaningful + n >= 40 earns a single Validation-slice
prospective test. Anything else (null, still too thin, or the two
bootstrap methods disagreeing) closes this specific idea.
