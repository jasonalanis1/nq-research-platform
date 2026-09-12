# Monetization — hyp-000142/144 (vxn_level_vs_trailing HIGH -> next-session RTH range)

September 11th, 9:45 pm CT (2026-09-12 02:45 UTC), extra cycle. Stage: post-Validation Monetization (AMENDMENT v2.5 order), before the frozen Holdout spec.

## Realization path
This is a next-session RANGE fact, not a directional signal. There is no credible STANDALONE trading path: a range forecast has no sign, so it cannot be a strategy on its own, and building an options/straddle expression is outside the data budget and outside scope (never write broker/order code; options data deferred by the data policy). The credible path is the same one the three existing conditioning facts use: an input to `src/volatility_conditioning.py` -- expected-range multiplier for the NEXT session, known before the open (VXN close of day t-1 is public by ~16:15 ET), used to size stops/targets and position size for whatever directional strategy is live (today: none; H118 is in its statistical forward test and is frozen -- this fact does not touch it).

## Execution spec (for the conditioning use)
Signal time: after the VXN close on day t-1 (FRED VXNCLS, daily). Applied to: day t's RTH session sizing. Inputs: vxn_level_vs_trailing at the frozen edges (LOW <= -0.0608, HIGH > +0.0258). Output: expected-range multiplier -- Validation-slice point estimates would be HIGH x1.12, LOW x0.86, MID x1.00 (Discovery: 1.31 / 0.80 / 1.01); the exact multipliers are set only AFTER Holdout, from the Holdout estimate, never from Discovery. No orders, no fills, no slippage -- nothing is executed on this fact alone.

## Measured costs
Zero direct cost: no data purchase (VXN already on disk from FRED, free), no execution. Indirect cost: none until a directional strategy is live; then the cost of a WRONG range forecast is mis-sized stops, bounded by the multiplier range (0.86-1.12 on Validation numbers).

## Portfolio note (owed formally after Holdout, flagged now)
Separability vs the overnight-coil fact was 66% (coil alone) and 53% (coil + prior-day realized range) -- it clears the >= 50% bar but roughly half of this fact is an echo of realized range the conditioning module already sees. Portfolio's incremental-information question must be answered before the multiplier is combined with the existing ones (no double-counting: combine by residual, not by product).

## Verdict
Credible path EXISTS (conditioning input, zero cost). Proceed to the frozen Holdout spec and the blind Integrity Gate; then Waiting on Jason for a Holdout Gen 2 slot (3 of 5 remain).
