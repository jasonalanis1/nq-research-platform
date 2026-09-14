# Portfolio — hyp-000162 (M30: opening-range width → midday range, NQ)

September 14th, 5:00 pm CT scheduled cycle. `src/portfolio_hyp162.py`, numbers in
`research/studies/hyp162-portfolio-2026-09-14.json`. Validation slice only
(2021-10-04 → 2024-01-03); every model's coefficients are fit on **Discovery
only**, so Validation never informs them. Holdout untouched.

## The question

Not "is it real" — the one-shot Validation answered that this afternoon (PASS).
**Does it add to the conditioning stack the project already runs, or restate it?**
Precedent: hyp-000142 was flagged here for retaining only 53% against the coil
plus prior-day realized range *together*, and the rule that came out of it is the
one applied now — combine by residual, never by product.

The Director held each validated fact fixed **one at a time** (75–88% retained).
That answers "is it a restatement of any single fact". Portfolio asks the joint
version: a candidate can survive every fact individually and still be their
combination.

## Result: it does NOT add to the stack

**T1 — joint residual separability.** Fit the existing stack (VXN level, overnight
coil, prior-day range) on Discovery, score on Validation, take the residual, and
measure the candidate's HIGH−LOW spread of that residual:

| | spread | 90% CI |
|---|---:|---|
| raw | +0.289 | (+0.193, +0.384) |
| after the whole stack | **+0.059** | **(−0.029, +0.151)** — not credible |

**Retained share 17.7%, lower bound −14.3%, against a 50% bar. Fails.**

**T2 — does it improve the forecast?** The practical test, and the decisive one.
Both models fit on Discovery, scored on Validation:

| | MAE | correlation |
|---|---:|---:|
| existing stack | 0.3252 | 0.403 |
| stack + the 10:00 update | 0.3256 | 0.409 |

**The forecast gets very slightly worse** (−0.15%, 90% CI −0.69% to +0.56% — not
credible in either direction). Adding the candidate to the stack buys nothing
measurable.

**T3 — controls, because the method changed.** T1 uses regression where the
Director used stratification, and regression absorbs more. So the Director's own
method was re-run on the Validation slice:

| held fixed | retained (stratified) | lower 90% |
|---|---:|---:|
| VXN level | 68.7% | 47.6% |
| overnight coil | 74.8% | 54.4% |
| prior-day range | 94.4% | 78.0% |
| its own lagged self | 95.6% | 80.2% |
| **the three jointly** (terciles of the stack's forecast) | **52.0%** | **14.9%** |

**Single-fact separability replicates out of sample** — close to Discovery's
79.8 / 75.3 / 83.6 / 87.2. The collapse happens only when the stack is held fixed
*together*, and it happens under **both** methods: 17.7% linear, 52.0% stratified,
and neither interval clears the bar (lower bounds −14.3% and +14.9%).

Honest statement of the method sensitivity: the point estimate of joint retention
is method-dependent (18% vs 52%), so this write-up does not lean on either
number. What both methods agree on is what the verdict rests on — **the joint
retention interval does not clear the 50% bar**, and the forecast does not
improve.

## What this means, in plain terms

The candidate's whole appeal was timing: every input in the existing stack is
known before the open, and this one is a **10:00 ET update**. The test says that
update carries no measurable information about the midday range beyond what was
already knowable at the open. The first half-hour tells you the day is going to
be busy — but the VXN level, the overnight coil and yesterday's range had already
told you that.

That is a substantive negative result about intraday information flow in this
instrument, not a technicality: it says the market's opening half-hour is mostly
*confirming* an already-visible volatility state rather than revealing a new one.

## Disposition: **DO NOT PROMOTE — and do not spend a Holdout slot**

- **Not added to B2's conditioning stack.** It would be a fourth input that is
  substantially the first three restated, and the forecast test says it pays
  nothing.
- **No Holdout slot requested.** 3 of 5 Gen-2 slots remain and they are scarce;
  spending one to confirm a fact that does not improve the stack would be waste.
- **Not closed as null.** It is a Validation-passed standalone fact and stays in
  the registry as one — real, same-session-specific, and known at 10:00 ET.
  If a future use needs a midday range estimate *without* access to the pre-open
  stack, this is the fact that provides it.

"No credible portfolio path" is a valid successful outcome, the same way
Monetization's "no credible path" is. The pipeline did its job: four stages said
advance, and the stage whose specific question is *does this add to what we
already own* said no, with numbers, out of sample.

## What this changes beyond this candidate

**Single-fact separability is too weak a bar and should stop being decisive.**
The Director's 50%-against-each-fact test passed this candidate at 75–88% and the
joint test then found 18–52%. Every conditioning fact in the registry was cleared
against that same one-at-a-time test. The joint version built here should become
the standard Portfolio test, and the two existing multi-input facts
(hyp-000105, hyp-000142) are worth re-checking against it — hyp-000142 already
showed the warning sign (53% against two facts jointly) and was promoted anyway.

That re-check is queued, not done here, and it is a LEARN item rather than a
re-litigation: no promoted result is modified by this cycle.
