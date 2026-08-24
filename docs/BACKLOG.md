# Backlog

A single place to capture every idea the moment it comes up, so nothing said in passing gets lost. Any new idea should get logged here immediately, even before it's decided on. Reviewed as part of the regular project check-ins.

## Active

*(things currently being worked on — move items here from Parked when they're picked up)*

## Parked

- **Fundamental/macro finance plugins** (equity research, earnings analysis, economic calendar data — e.g. LSEG, Daloopa, S&P Global-style tools) — considered 2026-08-18. They solve a different problem (company/macro fundamentals) than this project's current focus (technical price-pattern backtesting on NQ futures). Revisit only if a future strategy hypothesis becomes fundamentals- or macro-driven (e.g., trading around FOMC/CPI releases), which Level Sweep Reversal is not.

- **Fair Value Gap (FVG) lower-timeframe entry trigger** — considered 2026-08-18, from a YouTube Short (ICT/Smart Money Concepts style). Same core thesis as the existing Level Sweep Reversal setup (sweep a significant level, price fails to close beyond it, reversal expected), but with a mechanically different entry technique: instead of "close back beyond the level" (the three variants already tested), enter on a 3-candle price imbalance ("Fair Value Gap") on a lower timeframe once the higher-timeframe rejection is seen. Not just a parameter tweak — a genuinely different entry trigger, so not redundant with exp-013 through exp-020. Source claim ("catches 3.6R almost every day") is one cherry-picked anecdotal example with no sample size or losing trades shown — not evidence, don't weight it. If tested later, must go through the full research-only/holdout pipeline like everything else, and would need a precise, non-cherry-pickable definition of "Fair Value Gap" before backtesting.

- **Trend-structure-aware liquidity filter** — considered 2026-08-18, from a second YouTube Short (ICT/Smart Money Concepts style). Claims a meaningful difference between sweeping "interior" liquidity (swing highs/lows inside an established trend) versus sweeping the "protected high/low" (the structural point that, if broken, would flip the trend classification itself) — the former is framed as a normal stop-hunt-then-continuation, the latter as an actual reversal signal invalidating the setup. Points at a real gap in the current Level Sweep Reversal setup, which doesn't distinguish these two cases at all — it treats every prior-day/pre-market level sweep the same regardless of trend context. Genuinely specific and testable as a context filter (relates to the "volatility regime / trend-day vs range-day" filter idea already on the table), not just another generic pattern. Caveat: "swing high," "protected high," and "break of structure" have no single standard definition — programmatically defining them introduces new parameter choices that are themselves an overfitting risk (each definition choice is a knob that could get tuned until something looks good). Must go through the same research-only, holdout-respecting pipeline as everything else if tested — no fast-tracking because the theory sounds more rigorous.

- **research_ledger.py hypothesis ID gaps** — found 2026-08-24, while logging exp-023/024. Hypothesis IDs are assigned by total-lines-appended, not total-distinct-hypotheses -- so ID numbers have gaps whenever a hypothesis has multiple lines (e.g. hyp-000001 spans lines 1-2, so the next fresh hypothesis is hyp-000003, not hyp-000002). Not a data-integrity bug -- lineage and uniqueness are correct -- but worth fixing eventually so ID gaps don't get mistaken for deleted records in what's meant to be a tamper-evident ledger.

## Rejected

*(considered and ruled out, with why — nothing here yet)*
