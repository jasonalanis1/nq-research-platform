# Statistical stage — hyp-000156 (M23 London-open volatility burst, 6E)

Run September 13th, 7:00 pm CT test cycle (U2). Construction reproduced from Scan 030 exactly; the per-day
series is London-hour |return|/ATR14 minus that day's mean unconditional hourly |return|/ATR14 — the null
is the instrument's own behaviour, not zero. Block bootstrap block=10, N=3000, seed 20260913, 90% CI.

**Full sample:** n=891, mean diff +0.0537 ATR, ci_90 (+0.0426, +0.0670).

| Question | Result | Pass |
|---|---|---|
| Q1 stability (chronological halves) | 1st +0.0551 [0.040772197762939, 0.07159096255978446] · 2nd +0.0522 [0.033292163880154414, 0.072048615875786] | PASS |
| Q2 regime (trailing-20d range median) | low-vol +0.0478 [0.030068631282368623, 0.06847937476756212] · high-vol +0.0612 [0.04642410832330826, 0.07597650815342157] | PASS |
| Q3 multiplicity (Šidák, N_discovery=451, BINDING) | raw [0.0426, 0.067] → adjusted [0.0264, 0.081] | PASS |
| Q4 selection sensitivity (reported) | frozen_0300_0400 +0.0537 cred; alt_0300_0330 +0.0050 n/c; alt_0300_0500 +0.1147 cred; alt_0230_0330 +0.0380 cred | reported |
| Power at one-shot Validation | n=0 days (count only), power nan at Discovery effect, nan at half | — |

**Verdict: PASS**
