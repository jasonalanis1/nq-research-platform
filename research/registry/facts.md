# Fact registry (seeded September 13th, ~5:55 pm CT; U16)

One row per validated market fact. A fact is not a strategy. Every strategy must
link back to the fact IDs it uses; every fact lists the strategies using it.

| Fact ID | Definition (plain) | Instrument | Horizon | Mechanism (short) | Stage reached | Stability | Related facts | Used by |
|---|---|---|---|---|---|---|---|---|
| F-048 (hyp-046/048) | Compressed prior-day range → smaller next-session range (ratio 0.94) | NQ | next session | volatility persistence | Validation PASS | 2 slices, consistent | F-057, F-142 | volatility_conditioning.py; Risk/State Engine (U13) |
| F-057 (hyp-056/057) | Overnight coil → smaller RTH range (ratio 0.89) | NQ | same session | volatility persistence | Validation PASS | 2 slices, consistent | F-048 | volatility_conditioning.py; U13 |
| F-105 (hyp-105/106/133/141) | Quiet midday → quiet afternoon (ratio 0.74) | NQ | same session | intraday persistence | Holdout PASS | 3 slices; 82.5% retained vs coil | F-057 | U13 |
| F-142 (hyp-142/144/151) | Elevated VXN vs trailing → larger next-session range (ratio 1.24 holdout) | NQ | next session | implied vol leads realized | Holdout PASS | strengthened Val→Holdout; 53–66% retained vs F-048/F-057 (combine by residual) | F-048, F-057, M29 | U13 |
| M20 (hyp-148) | EIA petroleum report → post-release volatility burst | CL | 1 hour | scheduled information release | Discovery PASS; reclassified into event-volatility family (D13) | 1 slice | M21, M23 | family U5c |
| M21 (hyp-150) | ECB decision → post-release volatility burst (+0.53 ATR) | 6E | 1 hour | scheduled information release | Discovery PASS, Statistical PASS; reclassified (D13) | 1 slice | M20, M23 | family U5c |
| M23 (hyp-156) | London FX open → volatility burst (+0.04 ATR, n=891) | 6E | 1 hour | session-transition liquidity | Discovery PASS; Statistical OWED (U2) | 1 slice | M27 (Tokyo, queued) | family U5c |
| M29 (Entry 33) | Implied-minus-realized vol gap: HIGH gap → larger range (descriptive; sign opposite to pre-registered P1) | NQ | next session | dealer positioning proxy (contested by Stage 0) | Stage 0 free-look only | — | F-142 (47% overlap, distinct) | none yet |

Negative facts worth keeping (from this week's closures; closure forms owed, U8):
direction is noise at daily, 10-day, and now time-of-day × state resolution
(free-look 2026-09-13: 72 direction cells, max |z| 2.2); monthly/weekly
calendar-anchored directional claims (M22, M24, M25) do not survive on NQ/ZN at this
data ceiling; Level Sweep Reversal has no conditional edge on compressed days (M26).
