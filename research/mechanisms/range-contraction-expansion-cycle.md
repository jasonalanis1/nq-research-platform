# Mechanism — Range Contraction/Expansion Cycle (hyp-000046 Discovery / hyp-000048 Validation)

Written: 2026-09-10  ·  **POST-HOC**
Results seen before writing: YES — Discovery (exp-074) and the single
pre-registered Validation-slice prospective test (exp-076) were both
complete before this document existed. **This is a hypothesis, not
evidence.** It carries no weight toward promotion on its own.

## 1. The claim

Days classified `narrow` (own trailing-20-day range below the 20th
percentile) tend to be followed by a wider-than-average next day; days
classified `wide` (above the 80th percentile) tend to be followed by a
narrower-than-average next day. The candidate explanation: realized range
is not a static property of the instrument but a regime that compresses
ahead of resolution (participants sit on hands into an unresolved question
-- an upcoming data print, an options-expiration pin, a lack of fresh
information -- narrowing the trading range) and then releases once the
question resolves; symmetrically, an unusually wide day is often the
release itself -- a one-off information or flow shock -- after which
activity normalizes back toward the ordinary range because the shock does
not repeat night after night.

A second, competing, and equally plausible explanation must be stated
alongside it: this descriptor is a ratio against ITS OWN trailing average
(today's range / trailing-20-day average range). Any ratio built this way
carries a mechanical tendency to look mean-reverting even with zero market
information content, because an unusually low realized value of a
moderately-autocorrelated series is, by construction, likely to be followed
by a value closer to the series' own recent average -- this is regression
to the mean of the descriptor's arithmetic, not necessarily a market
phenomenon. Distinguishing (a) a real behavioral/informational coiling-and-
release cycle from (b) an artifact of normalizing against a trailing
average is the central open question this document exists to sharpen, not
resolve.

## 2. Who is on the other side

Genuinely unclear, and this is stated plainly rather than glossed over, per
the README's instruction that "unknown" is a red flag, not a footnote. This
is a volatility/range CHARACTERIZATION, not a directional return rule --
nobody is required to be long or short to be "on the other side" of a
range forecast the way they are for H118's directional drift. If claim (a)
is right, the closest thing to a counterparty is short-dated options
sellers/dealers whose gamma-hedging flow mechanically dampens realized
range into a pin (narrow) and unwinds once the pin breaks (wide) -- but
this project has no options-flow or dealer-positioning data to confirm
that. If claim (b) is right, there is no counterparty at all: it is a
property of the measurement, not of trading behavior, and "who profits"
does not apply.

## 3. Testable predictions

P1. **Lag decay, not a flat or growing effect.** If this is a coiled-spring
    release (claim a) or ordinary mean-reversion-in-range (also broadly
    consistent with a), the next-day effect should be the strongest and
    should decay by day two and largely vanish by day three -- a temporary
    state normalizing, not a persistent regime shift. A flat or growing
    effect out to 2-3 days would be inconsistent with a one-shot release
    and would need a different story.

P2. **Calendar/event clustering.** If narrow days are genuinely
    "coiling ahead of a catalyst" (claim a, the more specific and more
    interesting version), they should occur disproportionately in the 1-2
    trading days before scheduled information events already tracked
    elsewhere in this project (FOMC, CPI, NFP, monthly options expiration --
    `days_to_monthly_opex` already exists as a computed descriptor from
    Scan 004). If narrow-day frequency is statistically indistinguishable
    from its base rate near these events, that undercuts the informational-
    coiling story specifically (though not claim (a) in its weaker,
    purely-mechanical-exhaustion form).

P3. **Cross-instrument coherence with VXN.** If range compression/expansion
    reflects a real volatility regime rather than NQ-specific microstructure
    noise, a narrow-range NQ day should coincide with a below-trailing-
    average VXN level (options-implied vol tracking realized-range
    compression), and a wide-range day should coincide with an elevated
    VXN level. `vxn_level_vs_trailing` already exists as a computed
    descriptor (Scan 002). No coherence with VXN would point toward an
    NQ-specific or purely mechanical effect rather than a market-wide
    volatility-regime phenomenon.

## 4. What would falsify this

A flat or growing (not decaying) multi-day effect (falsifies claim (a) in
both forms, leaves only the mechanical-artifact explanation as credible).
Absence of BOTH calendar clustering and VXN coherence (does not falsify
the effect's existence, but leaves only the mechanical-artifact
explanation standing, and downgrades this from "real market behavior" to
"be careful trading a normalization artifact").

## 5. Prediction status

**P1 -- TESTED 2026-09-10** (Statistical-stage pass, Discovery+Validation
combined sample, n=557 narrow / n=522 wide -- see
research/studies/statistical-stage-pass-2026-09-10.md for full numbers).
**PARTIAL CONFIRM.** Magnitude decays monotonically TOWARD the null with
each additional day (narrow: t+1 mean=0.862, t+2=0.882, t+3=0.895; wide:
t+1=1.306, t+2=1.269, t+3=1.249 -- both legs moving toward 1.0 every day,
as predicted) but does NOT "largely vanish" by day 3 -- both legs remain
statistically credible away from 1.0 even at t+3 (narrow ci_90
[0.862,0.928], wide ci_90 [1.202,1.298]). The weaker reading of the
prediction holds (decay, not full vanish) -- a "coiled-spring, one-shot
release" story is too strong; a "gradually normalizing regime" story
fits the data better.

**P2 -- TESTED 2026-09-10. NOT CONFIRMED.** Narrow days: 12.0% fall
within +/-2 trading days of monthly OPEX vs an unconditional base rate of
12.9% (n=557). Wide days: 13.2% vs the same 12.9% base rate (n=523).
Both indistinguishable from base rate. Per this document's own
falsification criterion, this undercuts the specific "informational
coiling ahead of a scheduled catalyst" reading of claim (a) without
touching the broader mechanical-exhaustion / ordinary volatility-
clustering reading.

**P3 -- TESTED 2026-09-10. CONFIRMED, cleanly, in both buckets and in
the predicted direction.** Narrow days: mean vxn_level_vs_trailing =
-0.061 vs an overall mean of +0.003 (n=557); 76.8% of narrow days sit
BELOW their own trailing VXN average vs a 57.2% unconditional base
rate. Wide days: mean vxn_level_vs_trailing = +0.081 (opposite sign, as
predicted); only 35.8% sit below trailing VXN vs the same 57.2% base
rate. This is a real, falsifiable, non-restated prediction that came
true -- the strongest mechanism-level evidence this candidate has: range
compression/expansion is coherent with a market-wide volatility regime
(VXN), not an NQ-specific microstructure artifact.

## 6. Verdict

Two of three predictions bear directly on the claim-(a) vs claim-(b)
question this document exists to sharpen. P3 (VXN coherence) is a clean,
confirmed, falsifiable result and is real evidence FOR a market-wide
volatility-regime mechanism over a pure normalization artifact -- an
artifact of ratio-against-own-trailing-average would have no reason to
coincide with an independently-measured, differently-constructed series
(VXN) in the predicted direction. P1 (lag decay) partially supports a
regime/persistence reading over a one-shot-release reading. P2 (opex
clustering) found nothing, narrowing the story to non-calendar-driven
persistence. Read together, the mechanism-level evidence net INCREASES
confidence this is a real, structural, market-wide phenomenon rather
than a mechanical trailing-average artifact -- more than this document
had when it was written.

That said, mechanism support is not the promotion bar. The
Statistical-stage pass (research/studies/statistical-stage-pass-2026-09-10.md)
also re-confirmed this session's earlier finding that BOTH Validation
legs fail the project's own multiplicity-corrected 90% bound (narrow:
adjusted 0.852-1.036, crosses 1.0; wide: adjusted 0.978-1.184, crosses
1.0), and found split-sample stability, volatility-regime independence,
and threshold-selection robustness all clean (no red flags there). Per
NEXT_UP.md queue item 0's explicit standard -- "only candidates that
survive both the corrected numbers AND the mechanism checks should go
to Director Re-Evaluation" -- this candidate does NOT advance: the
corrected-CI failure is the binding constraint, not the mechanism
question. Disposition: **ABANDON at Statistical stage** (hyp-000048
updated REJECTED in the ledger, in place, no new hypothesis_id spent).
Recorded honestly as a real, well-evidenced, well-replicated market
phenomenon (LEARN: KNOWN TRUE, ordinary volatility clustering, now with
cross-instrument coherence evidence) that nonetheless does not clear
THIS project's strict multiple-testing standard for promotion -- "real"
and "clears our bar" are different questions, and this document should
not blur them.
