# Observatory — fixed state classifier, v1 (NQ + ZN, Discovery)

Written: September 12th, ~4:30 pm CT (TEST cycle, queue v2 item 4, last
listed sub-step). Characterize, do not claim. No ML; every state is a fixed
rule from prior information only. Script:
`src/observatory_state_classifier_v1.py`; full output in
`data/observatory_state_classifier_v1_results.json`. n = 1,330 Discovery
sessions with NQ, ZN and overnight data all present.

## States computable at the ceiling
- RATE: prior RTH session NQ and ZN returns opposite sign (rate_confirmed,
  the normal risk-on/off configuration) vs same sign (rate_conflicted).
- OVERNIGHT VARIANCE: tercile of overnight range / ATR14 (edges frozen on
  Discovery).
- PRIOR CASH-SESSION VARIANCE: tercile of prior RTH range / ATR14.
PARKED (needs ES): broad-equity agreement vs NQ-only residual.

## Result (RTH session described by the state; all vs ATR14, lagged)

| State | n | range ratio [90% CI] | abs ret/ATR | signed ret/ATR [90% CI] |
|---|---|---|---|---|
| UNCONDITIONAL | 1330 | 1.038 | 0.524 | +0.036 [+0.007, +0.063] |
| rate_confirmed | 791 | 1.044 [0.99, 1.09] | 0.515 | +0.065 [+0.029, +0.100] |
| rate_conflicted | 539 | 1.028 [0.99, 1.08] | 0.537 | -0.007 [-0.057, +0.033] |
| ovn_high | 444 | **1.290** [1.22, 1.37] | 0.659 | +0.073 [+0.010, +0.133] |
| ovn_mid | 444 | 0.983 [0.94, 1.02] | 0.497 | +0.002 |
| ovn_low | 442 | **0.840** [0.80, 0.88] | 0.416 | +0.032 |
| cash_high | 445 | **1.223** [1.15, 1.30] | 0.622 | +0.026 |
| cash_mid | 445 | 1.003 | 0.515 | +0.064 |
| cash_low | 440 | **0.886** [0.85, 0.93] | 0.435 | +0.016 |

Joint rate x overnight: the range effect is entirely the overnight state
(1.29 / 0.98 / 0.84 in both rate states); the rate state adds nothing to
range.

## Reading
1. **Range is conditioned by variance state, monotonically and strongly,
   in both directions.** The low side is the validated overnight-coil
   fact (hyp-056/057) and the validated range-contraction fact
   (hyp-046/048). The HIGH side (wide overnight -> +29% RTH range; wide
   prior day -> +22%) is the same persistence read from the other tail.
   It was never separately validated because the existing facts were
   framed one-sided; it is the same latent state, not new information --
   record it as characterization of KNOWN TRUE, not as a candidate.
2. **The rate state does nothing for range** (1.04 vs 1.03) and its
   directional reading is not distinguishable from NQ's own drift:
   rate_confirmed +0.065 vs unconditional +0.036, CIs overlapping almost
   entirely; rate_conflicted -0.007. The confirmed-minus-conflicted gap
   (0.07 ATR) is exactly the size and shape of thing the two-nulls rule
   exists to stop us from chasing, and it sits next to a CLOSED family
   (daily ZN lead-lag, hyp-031/034/035). NOT drawable. Not an entry.
3. Nothing here is a new hypothesis. The classifier's value is as the
   context layer the three validated volatility facts already provide,
   now expressed as one table with both tails, and as a documented
   negative on "rate configuration" as a state -- so the literature and
   practitioner channels do not re-propose it.

## What this closes for item 4
All four listed sub-steps of the Observatory program at the current data
ceiling are now done: separability of the three volatility facts (all
pairwise separable), lead-lag v1 and v2 (none at >=5 min, both sessions,
unconditional and shock-conditioned), and the fixed state classifier
(variance states condition range; rate state conditions nothing). What
remains of the original spec (ES/RTY/YM instruments; broad-equity vs
NQ-residual states) is parked on the data ceiling with everything else
that needs ES. Item 4 is CLOSED at the ceiling.

## Map-ready output
- Map note under LEARN / KNOWN TRUE: variance persistence is two-sided
  (high begets high as strongly as low begets low); still range-only,
  still a sizing input, not a signal.
- Map note under KNOWN FAILED / characterized: NQ-ZN rate-configuration
  as a state -> no range effect, directional effect not separable from
  drift; cross-asset lead-lag at the ceiling -> none at any resolution
  or session, unconditional or shock-conditioned.
