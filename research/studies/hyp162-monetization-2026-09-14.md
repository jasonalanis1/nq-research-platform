# Monetization — hyp-000162 (M30: opening-range width → midday range, NQ)

September 14th, 1:00 pm CT scheduled cycle. `src/monetization_hyp162.py`,
numbers in `research/studies/hyp162-monetization-2026-09-14.json`.
Discovery only (1,666 sessions), Scan 036's frozen construction reused exactly
— this stage re-expresses the effect in decision units, it does not re-test it.

Owed after the Director Re-Evaluation's ADVANCE
(`hyp162-director-reeval-2026-09-14.md`). The question here is not "is it real"
and not "is it new" — both answered — but **is there a credible path from this
fact to money, and what does it cost?** "No credible path" would have been a
valid success.

## 1. There is no standalone trading path, and there was never going to be

This is a RANGE fact. A range forecast has no sign: it says how far price will
travel between 11:30 and 13:30, not which way. It cannot be a strategy by
itself. Same structural position as hyp-000142 (VXN → next-session range) and
the two prior-day-range facts.

The credible path is the one the project already owns: a **sizing and
permission input** to B2 (`volatility_conditioning.py` →
`risk_state_engine.py`), in the same form the existing multipliers take.

## 2. What it is worth as a sizing input

Expected-midday-range multiplier by opening-range tercile, against the
all-session mean (x1.00 = "no information"):

| opening range (10:00 ET) | n | mean midday range | multiplier |
|---|---:|---:|---:|
| LOW | 556 | 40.1 pts | **x0.76** |
| MID | 555 | 44.0 pts | x0.97 |
| HIGH | 555 | 54.4 pts | **x1.26** |

A 50-point spread of information between the outer terciles, available at
10:00 ET — half an hour after the open and four hours before the existing
afternoon update. In B2's own terms (stop = 0.5 x expected range) that is a
**14.3-point difference in expected range, so ~7.2 points of stop distance.**

## 3. The magnitude is conditional, as the Director flagged

Multiplier spread (HIGH − LOW) computed inside each prior-day-range tercile,
rather than assumed constant:

| prior-day range | HIGH−LOW multiplier | HIGH−LOW points |
|---|---:|---:|
| LOW | +0.49 | +6.7 |
| MID | +0.29 | **−3.5** |
| HIGH | +0.46 | +23.3 |

**The ratio effect holds in all three strata; the POINTS effect does not, and
the MID stratum flips sign.** That is not a contradiction and not a defect:
the multiplier is applied to each session's own trailing-20 average, so the
ratio is the decision-relevant unit and the points column depends on where
that baseline happens to sit. It is stated here because anyone reading "the
effect scales with volatility" as "more points in every regime" would be
wrong. What scales cleanly is the *relative* effect in the high-volatility
stratum (+23 points there, the only stratum where both agree strongly).

## 4. Cost check (monetization-screening-rule.md)

| tercile | implied stop | 0.75pt cost as share | clears 5% bar |
|---|---:|---:|---|
| LOW | 20.0 pts | 3.7% | yes |
| HIGH | 27.2 pts | 2.8% | yes |

Both clear. But the honest number is the **increment**: the 0.75pt fixed cost
is **10.5% of the 7.2-point stop-distance change this fact produces**. The
fact clears the screening rule; the *change it makes* is roughly ten times the
cost of a trade, not a hundred.

## 5. Double-counting (the residual Portfolio will ask for)

Within each level of the existing pre-open multiplier, the HIGH−LOW midday
ratio spread:

| pre-open multiplier level | n | HIGH−LOW ratio |
|---|---:|---:|
| 0.9438 | 283 | +0.376 |
| 1.0000 | 691 | +0.362 |
| 1.0809 | 360 | +0.603 |

Raw spread is +0.52. So 70–115% survives holding the existing pre-open
multiplier fixed — consistent with the Director's 75–88% retention against the
individual facts, measured a different way. **Combine by residual, never by
product**, same rule as hyp-000142.

## 6. Measured costs

Zero direct cost. No data purchase (the state variable is already on disk from
the NQ series), no execution, no new instrument. Indirect cost: a wrong midday
range forecast mis-sizes stops, bounded by the multiplier range 0.76–1.26.

## 7. What this does NOT do

It does not unblock the bot. B7's one real session (Sept 8th) was blocked
because the per-trade swing was $468 against a $50–150 band — a 26% sizing
change does not close a 3x gap. This fact improves how B2 sizes a live
directional strategy; the project does not currently have one (B3 is an
explicit placeholder, and every directional family tried has been rejected).
It is worth exactly what a sizing input is worth, which is real but second-order
to the direction problem still parked on Jason.

## Verdict: CREDIBLE PATH EXISTS — conditioning input, zero cost

Finding: as a third conditioning window (pre-open → **10:00 midday** → 14:00
afternoon), worth x0.76 / x1.26 on expected midday range, surviving the
existing pre-open multiplier at 70–115%.
Confidence: moderate — Discovery point estimates, no CI on the multipliers
themselves; the exact numbers would be set from Validation/Holdout, never from
Discovery.
Novelty: the earliest intraday sizing input the project has.
Research value: high for B2, nil for the direction problem.
Recommendation: **CONTINUE** — to the blind Integrity Gate, handed the narrowed
question from the Director plus this stage's own caveat (§3: the ratio effect
is regime-stable, the points effect is not).
