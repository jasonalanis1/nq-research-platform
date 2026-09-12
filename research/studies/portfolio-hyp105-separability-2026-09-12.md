# Portfolio review — hyp-000105/106/141 (midday-lull → afternoon range persistence)

Hypothesis IDs covered (full family): hyp-000105, hyp-000106, hyp-000133, hyp-000141.

Written: September 11th, 9:xx pm CT (2026-09-12, scheduled cycle). Closes the FROZEN-tier item the pipeline sweep has carried since Holdout passed (September 11th, 7:29 pm CT).

## Question
Per AMENDMENT v2 (Portfolio Agent's first job): does this finding add incremental information, or is it the same latent volatility-persistence state already captured by the validated overnight-coil finding (`overnight_range_vs_atr`, hyp-056/057), restated at a finer intraday grain? The mechanism doc for this family names this exact risk directly.

## Method
Same separability discipline as H116 (2026-09-09) and H140's Director Re-Evaluation (2026-09-11): correlation, within-tercile spread, and residualized (partial) spread, controlling for `overnight_range_vs_atr` tercile. Script: `src/portfolio_hyp105_separability.py`. Discovery-slice data only, frozen exp-125 construction, nothing retuned.

## Result (n=1,285 days)
- Correlation of the narrow-midday signal with `overnight_range_vs_atr`: **-0.19** (mild — nowhere near H140's 0.69 that flagged it as redundant).
- Overlap: narrow-midday days that are also low-overnight-range tercile: 47.9% (vs. 33% expected under independence — some real relationship, but far short of identity).
- Raw narrow-vs-not spread in afternoon-range ratio: 0.44.
- Spread survives, and stays credible, within **every** overnight-range tercile individually (low 0.29, mid 0.31, high 0.64 — if anything stronger in the high-overnight-range bucket, the opposite of what redundancy would predict).
- Residualized (overnight-range-tercile mean removed): spread 0.36, **82.5% of the raw spread retained**.

## Verdict
**SEPARABLE.** This sits with H116 (98% retained) rather than H140 (32% retained, ABANDON). The midday-lull → afternoon persistence effect is not the overnight-coil fact showing up again at a different time window — it carries genuinely incremental information about same-day volatility state. Disposition: **KNOWN TRUE, incremental** — both facts stay in `src/volatility_conditioning.py` as independent conditioning/sizing inputs (`get_volatility_conditioning` for the overnight-coil family, `get_afternoon_conditioning` for this one), used together rather than one subsuming the other. Neither is a directional/tradeable edge (conditioning facts only, per the project's standing convention for all 3 volatility-persistence survivors) — no forward-test spec is owed, no Jason input needed. Closes the FROZEN-tier queue item.

Not addressed here (out of scope for Portfolio's incremental-information question, deliberately): sizing/combination rules for using both conditioning facts together — that is a "how do we combine" question, explicitly not this check's job.
