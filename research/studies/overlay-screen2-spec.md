# Overlay Screen 2: Overnight-Coil + Release-Day Magnitude — Frozen Spec (2026-09-08)

exp-086/087 — same quick, cheap, non-exhaustive screen as exp-077
(`vol-regime-overlay-screen-spec.md`), reused for the two conditioning
facts confirmed since: the overnight-coil finding (hyp-000056/057,
survived Validation last night) and the CPI/NFP/FOMC release-day
"moves more" magnitude finding (exp-039/exp-040, confirmed years ago,
never converted into a mechanical rule). Directly answers the two
queued items from the "what causes the market to move" conversation:
convert the coil finding into something tradeable, and use the
already-established scheduled-catalyst fact rather than building new
catalyst infrastructure from scratch.

**Disclosed expectation going in:** exp-077 ran this exact technique
with the range-contraction finding (closely related — both are
volatility-persistence facts) on these same 4 signals and found no
credible conditioning effect in any of them. This is a real repeat of
a technique that already came back empty once; run anyway because it's
cheap and the conditioning variable is genuinely different, but the
honest prior going in is "probably nothing," not "probably something."

## Scope

Same 4 Level Sweep Reversal variants as exp-077 (the only signals with
per-trade dated CSVs on disk): `close_min_distance` / `full_bar_range`
x `protected` / `not_protected`. All 4 already REJECTED standalone;
this cannot reopen them, only screen whether either conditioning
variable would have mattered.

**exp-086 (overnight coil):** classify each trade's entry date by
whether that day's overnight range was "coiled" (bottom 20th pctl of
its own trailing 20-day distribution, same definition as hyp-000056,
computed on Discovery data only since all 4 signals' trades are
Discovery-slice). Compare `r_multiple_net` mean, coiled days vs.
non-coiled days.

**exp-087 (release-day magnitude):** classify each trade's entry date
as a CPI/NFP/FOMC release day (free BLS/Fed calendar, same source as
exp-039/040) or normal day. Compare `r_multiple_net` mean, release
days vs. normal days.

## Method

Bootstrap difference-in-means CI, N_BOOTSTRAP=3000, seed=7, 90% CI,
this project's standard method. A bucket with too few trades (<10, per
exp-077's own precedent skipping a 9/16-trade bucket) is skipped and
disclosed, not forced.

## Decision rule

Exploratory/diagnostic only, same as exp-077 — no promotion possible
regardless of result (all 4 underlying signals are closed, no-retuning
rule applies to them). A credible difference here is evidence the
conditioning fact has some real value in general, informing whether
it's worth designing a purpose-built overlay on a live/future signal —
it does NOT reopen either the 4 closed Level Sweep lines or the
already-closed CPI/NFP directional-reversal lines (exp-042/045).

## Multiple-testing disclosure

2 pre-registered conditioning variables x 4 signals = 8 comparisons,
one shared `search_batch_id`, run together, no follow-up conditions
added after seeing results.
