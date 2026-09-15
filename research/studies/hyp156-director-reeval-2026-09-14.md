# Director Re-Evaluation — hyp-000156 (M23: the London-open volatility burst, 6E)

September 14th, 7:00 pm CT scheduled cycle. `src/director_reeval_hyp156.py`,
numbers in `research/studies/hyp156-director-reeval-2026-09-14.json`.
Discovery only (6E on disk covers 2015-01-01 → 2021-10-03; the Validation slice
has never been fetched).

## The question

Statistical passed this in September 13th's cycle: +0.0537 ATR, 90% CI (+0.0426,
+0.0670), stable across halves and regimes, surviving Šidák at N=451. The
Re-Evaluation question is **"is it NEW, and is it worth spending the rest of the
pipeline on?"** Precedent: H116 retained 98% and advanced; hyp-000140 retained
32% and the Director ruled *real is not new*.

The doubt this candidate arrives with is specific. The claim is that one named
hour — 03:00–04:00 ET, the London open — is more volatile than the day's average
hour. In FX that is close to the most textbook fact there is. It is only NEW if
the London hour is distinguishable from **the general shape of 6E's 24-hour
clock**. If the European and US morning hours all look like this, the finding is
"session boundaries are volatile", which the project can have for free and must
not spend a data purchase on.

## The test

The frozen statistic — |return over the hour| / ATR14, minus that day's mean
US-RTH hourly |return| / ATR14 — recomputed for **every hour of the ET clock**,
with the candidate's own ATR convention and its own block bootstrap (block 10,
3,000 draws, seed 20260913). 23 hours had enough coverage; 1,163 sessions.

## Result: the London hour ranks **4th of 23**

| hour (ET) | effect | 90% CI |
|---|---:|---|
| 10:00 | **+0.0835** | (+0.068, +0.100) |
| 08:00 | +0.0745 | (+0.056, +0.092) |
| 09:00 | +0.0700 | (+0.054, +0.086) |
| **03:00 — the frozen London window** | **+0.0502** | (+0.035, +0.068) |
| 11:00 | +0.0222 | (+0.011, +0.035) |
| 04:00 | +0.0134 | (+0.001, +0.023) |

**London minus the best other hour (10:00 ET): −0.0333, 90% CI (−0.057,
−0.008).** The interval is entirely **below** zero — the London hour is not
merely indistinguishable from the top of the clock, it is credibly *smaller*
than the 10:00 ET hour.

**Six of 23 hours clear the same bar individually.** The candidate is one member
of a family, and not its largest member.

## Reading

The frozen claim is **true and not new**. "This hour beats the day's average
hour" is cleared by any hour with above-average activity, and 6E has several:
the European morning and, larger still, the US data-and-equity-open window
(08:00–10:00 ET). The statistic's baseline is the mean RTH hour, which is
dragged down by the quiet afternoon, so the bar is low by construction.

**A prior cycle's claim is corrected here.** The September 13th session report
recorded, from Scan 034, that "the London burst is London-specific" because the
Tokyo hour was credibly *quieter* than baseline. That comparison was incomplete:
it tested one alternative hour, not the clock. Against the full profile, three
hours beat London and one of them beats it credibly. The Tokyo result stands on
its own terms; the inference drawn from it does not.

## Disposition: **CLOSE — real is not new**

Finding: 6E has a pronounced hour-of-day volatility profile peaking in the US
morning (08:00–10:00 ET), with the London open a secondary peak ranking 4th.
Confidence: high — the ranking and the negative separability interval are both
clear, and they come from the candidate's own frozen machinery.
Novelty: none. The honest product is the broader statement about the clock,
which is textbook and costs nothing.
Research value: the closure has real value; the candidate does not.
Recommendation: **ABANDON.**

## Consequence: the 6E data purchase is WITHDRAWN

The Validation slice for 6E was parked on Jason as an open decision. **That
request is withdrawn — he does not need to answer it.** Validation would have
tested a claim that cannot be new no matter how it lands, on an instrument the
project does not trade, with a strategy that does not exist. Spending money on
it would have been the expensive way to learn what this cycle learned for free.

`src/validate_hyp156.py` and its frozen spec stay on disk as a record of a
correctly pre-registered test that was never run, and as a template — it is the
best-documented Validation spec the project has.

## What this leaves

The family closes on attempt 1 of 2; the second attempt is not spent and is not
owed. The LEARN entry is the useful residue: **before promoting any "window X is
special" claim, compute the full profile of comparable windows first.** A
single-alternative comparison (the Tokyo check) is not that, and this project has
now made that mistake once.
