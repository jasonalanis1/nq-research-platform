# S005 — opening-range width as a stop-sizing overlay on S008: the null

7:00 pm scheduled cycle, September 17th 2026. Spec
`research/infrastructure/strategy-specs/S005-or-width-stop-overlay-on-S008.md`
(frozen before any data was touched), module
`src/strategy_s005_or_width_stop_overlay.py`, numbers
`data/screen_S005.json` against the host baseline
`data/screen_S008_host_alone.json`. Discovery slice only, 2101 sessions.
Validation and Holdout untouched.

## The question, and why it was worth one screen

hyp-000162 (opening-range width → midday range) is **VALIDATED_NOT_PROMOTED**:
`research/studies/hyp162-portfolio-2026-09-14.md` found joint residual retention
~17.7% against a 50% bar, and adding the 10:00 update to the existing forecast
stack made that forecast very slightly **worse** (MAE 0.3252 → 0.3256).

So it is never a standalone strategy. The one narrow question left over was
whether it could still earn its place as a **sizing** input — because sizing is
a non-linear transform of a forecast, and stop placement decides which trades
survive noise. A fact can be redundant for forecasting and still be useful for
sizing. That, and only that, was pre-specified and screened.

**Host: S008.** The best-performing frozen strategy, the only one in PAPER that
is **not SLOW** (0.3351 trades/session → 42.2 projected in six months, against
40), so a real improvement would reach a 40-trade judgment on a working clock.
Mechanically it is also the right host: S008 already sizes its stop off an
intraday **range** (`0.50 × the 09:30–15:00 range`), the exact quantity the fact
would inform. S002 is higher-frequency but is SLOW and is an overnight carry
with no intraday-range risk for the fact to touch. **S008's frozen spec and
module were not edited** (s.13); the overlay is its own frozen spec and module
and imports the host read-only.

The overlay changes exactly one thing:
`risk' = clip(ORW / trailing-20 median ORW, 0.75, 1.35) × 0.50 × RNG`, with the
1.5R target riding the rescaled risk. ORW is known at 10:00 ET, five hours
before the host's 15:00 decision.

## Result: it changes nothing

All four cost combinations, same slice, same bookkeeping, net $ at one contract:

| combination | host alone | with overlay | delta | net R host → overlay |
|---|---:|---:|---:|---:|
| **MNQ market (decision basis)** | **1,950.18** | **1,901.21** | **−48.97** | −8.2 → −7.9 |
| MNQ limit *(OPTIMISTIC)* | 2,302.18 | 2,253.21 | −48.97 | −3.6 → −3.5 |
| NQ market | 27,316.22 | 26,826.48 | −489.74 | +1.9 → +2.0 |
| NQ limit *(OPTIMISTIC)* | 30,836.22 | 30,346.48 | −489.74 | +6.4 → +6.5 |

Gross 2.6503 vs 2.6851 pt/trade, against the 1.300 pt MNQ market cost. Both
**limit** rows are an **OPTIMISTIC UPPER BOUND**: a resting limit order is
assumed always to fill at its price, and real ones miss fills and are adversely
selected.

A hair *better* in R, a hair *worse* in dollars and points. Neither is material.

**704 trades in both. All 704 entries identical. Win rate 0.4688 in both. Only
16 of 704 trades (2.3%) changed exit reason at all.** The scaler was live and
not degenerate — k mean 1.1099, median 1.1657, full range 0.750–1.350, 362 of
704 (51.4%) at a clip bound, zero fallbacks to k = 1. The input did move the
stops; the stops moving did not move the result.

## Why — both mechanisms were named in the spec before the screen

**Failure mode 2.** Scaling the stop and the 1.5R target *together* by the same
k is a **no-op in R by construction**. It can only change an outcome through
which level is touched **first**. It changed first-touch ordering on 2.3% of
trades, and those changes were a wash.

**Failure mode 1, the deeper one.** ORW and the host's RNG are both range
measures of the **same session**, so the scaler largely re-states a quantity the
host's stop already used. This is the Portfolio finding again — the opening
half-hour *confirms* an already-visible volatility state rather than revealing a
new one — now observed on a **traded result** instead of a forecast.

## Disposition: LEARN

Per the decision rule fixed in the spec before the screen. Not salvaged (the
strategy did not lose money, so no salvage is owed) and **not varied**: hunting
a k-band or a tercile split that looks better is exactly the ex-post slicing the
salvage rule forbids.

**This null is a good result.** hyp-000162 has now failed to add value as a
forecast input (Portfolio, September 14th) and as a sizing input (here,
September 17th), by two different methods on two different slices. Absent a
genuinely different use, it is a **closed question** and should not be
re-sourced. Queue advances to S006 (Stack A).
