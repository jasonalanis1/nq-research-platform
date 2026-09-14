# Portfolio pass over the fact registry — September 13th, 7:00 pm CT test cycle

Portfolio's one question: for each standing fact, is it incremental information or the same latent state restated? Residual convention as in the hyp-142 review (share of a fact's effect retained after residualizing on the others).

| Fact | Verdict | Evidence | Consequence for the Risk/State Engine (B2) |
|---|---|---|---|
| F-048 prior-day range → next range | INCREMENTAL, anchor | 82.8% retained vs coil (Sept 12th) | Base multiplier (product convention with F-057, validated jointly) |
| F-057 overnight coil → RTH range | INCREMENTAL | 82.8% retained vs prior-day range | Base multiplier |
| F-105 midday-lull → afternoon range | INCREMENTAL, intraday-only | 82.5% retained vs coil; 66.1% vs prior-day range | Separate afternoon update (usable from 14:00 ET), never in the pre-open number — already enforced |
| F-142 VXN level → next range | INCREMENTAL but MOST OVERLAPPING | 53–66% retained vs F-048 + F-057 | Enters by residual only: 1 + 0.239 × 0.53 — implemented in B2 today |
| M20 / M21 / M23 event bursts | ONE FAMILY, not three facts | same construction, same null, three instruments | Not in B2 (NQ engine); the family's monetization question is the family's, not any one entry's |
| M29 implied-minus-realized gap | UNDECIDED — Stage 0 only | 47% tercile overlap with F-142, corr +0.33; sign opposite to pre-registered P1 | Not in B2 until Stage 1 resolves the residual on F-142 |

Portfolio's standing warning restated: three of four validated facts are volatility-persistence in different clothes. Adding a fifth "quiet begets quiet" fact to B2 must be justified by its residual, not its raw ratio. Nothing here activates Portfolio's combination role (0 validated directional strategies), so this pass is information-only.
