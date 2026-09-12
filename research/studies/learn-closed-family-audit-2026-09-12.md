# LEARN closed-family audit (item 0b) -- September 11th, 9:32 pm CT (2026-09-12 02:32 UTC)

Jason's instruction (September 11th, 7:50 pm CT): for every closed idea family, record attempts spent, how it closed, and -- for families with one attempt left -- whether any research/market_structure_map.md entry supplies a genuinely DIFFERENT mechanism claim (a new reason the market would do it), not a new filter, horizon, or bucket boundary. Integrity Gate ruling per family: NEW CLAIM (eligible for a shelf entry, attempt 2 of 2, map anchor required) or CLOSED FOR GOOD. Expected outcome stated up front: most families are CLOSED FOR GOOD. Ledger read only; no scans, no data.

Mechanical part: `src/learn_closed_family_audit.py` (groups the 107 closed name-level families into 37 claim clusters -- the 2-attempt limit is per CLAIM, not per variant name; output data/learn_closed_family_audit.json). Attempt counts come from Discovery-slice ledger rows; where the ledger under-counts (backfilled or hygiene rows), the map's own LEARN pre-check of September 11th is authoritative and is cited.

## Result in one line
**Zero new shelf entries.** Every one-attempt-left cluster is either CLOSED FOR GOOD, already re-entered on the map (M1 <- hyp-000110, M4 <- hyp-000111 -- not duplicated here), or PARKED on data the $20/mo budget does not yet cover (options). The expected outcome held.

## Rulings on the one-attempt-left clusters (Integrity Gate)

| cluster | ids | how it closed | map entry with a genuinely different claim? | ruling |
|---|---|---|---|---|
| \|gap\| magnitude -> same-day range | 140 | redundant with overnight-coil (32% retained) | none; M2 is closed and is a breakout/fade claim, not a range claim | CLOSED FOR GOOD |
| closing-pressure reversal (unconditioned) | 110 | null | M1 (close-window volume as the imbalance proxy) IS the second attempt -- already Entry 11 | already re-entered, do not duplicate |
| COT positioning | 063, 064, 093 | closed on Validation | none -- no map entry names a forced participant acting on COT; weekly data | CLOSED FOR GOOD |
| release-day reaction CPI/NFP | 115, 116 | cost-dominated / null | map pre-check: at limit (two tests). M3b (post-FOMC) is a different EVENT, already on the map as NEW, not a resurrection | CLOSED FOR GOOD |
| cross-asset short-term reversal | 022 | null | M11 is co-movement breakdown, not reversal -- different claim, already Entry 10; nothing supplies a reversal claim | CLOSED FOR GOOD |
| days_to_monthly_opex | 138 (+ Entry 2) | wrong direction / null | map pre-check: CLOSED (Scan 004 direction + Scan 007 range = 2). Expiry dealer hedging has no footprint without options data | CLOSED FOR GOOD (revisit only with options data) |
| intraday collective-evidence pilot | 027, 099 | closed on Validation | methodology pilot, not a market claim -- nothing to anchor | CLOSED FOR GOOD |
| effort vs result absorption | 050, 053, 095 | closed on Validation | none -- an absorption claim needs order-flow data (deferred by data policy) | CLOSED FOR GOOD until data budget grows |
| intraday lull re-engagement | 055 | null | M10 is a different claim (morning-move retrace during the lull, liquidity mechanism, conditioned on move size) -- already Entry 9 | 055 CLOSED FOR GOOD; M10 proceeds as Entry 9 |
| intraday momentum continuation | 040, 041, 045 | closed on Validation | none -- no forced participant for intraday bursts; M8 (CTA) is multi-day and closed | CLOSED FOR GOOD |
| multi-day base breakout | 051, 125 | regime artifact / closed on Validation | M8 closed; breakout family at limit | CLOSED FOR GOOD |
| overnight coil -> RTH range | 056, 057 | multiplicity-corrected Validation fail | not a candidate: KNOWN TRUE conditioning fact, integrated in volatility_conditioning.py | CLOSED as strategy, RETAINED as conditioning |
| range-contraction / expansion cycle | 046, 048 | multiplicity-corrected Validation fail | same as above | CLOSED as strategy, RETAINED as conditioning |
| trend-day shape | 052, 054, 096 | closed on Validation | none | CLOSED FOR GOOD |
| volume profile skew | 044, 047, 094 | closed on Validation | none | CLOSED FOR GOOD |
| H117 location_in_range low + uptrend -> 10d | 119, 120, 128 | closed on Validation (sign flipped) | none -- "buy the dip in an uptrend" has no forced-participant entry; M8 closed | CLOSED FOR GOOD unless a map entry is added |
| multi-day pullback continuation | 079, 080, 091 | not robust (n=15) / null | v1 + v2 are effectively two attempts; M8 closed | CLOSED FOR GOOD |
| options VRP | 036 | inconclusive on $1.92 sample | needs paid options data; not closed on evidence | PARKED on data (data policy: after profitability) |
| H116 overnight_range_vs_atr mid -> 10d | 117, 118, 127 | closed on Validation | map pre-check: CLOSED (Entry 1 / Scan 006 spent the second attempt on the variable) | CLOSED FOR GOOD |
| overnight-vs-RTH return divergence | 139 | multiplicity-corrected fail | none | CLOSED FOR GOOD |
| pre-FOMC drift | 111 | thin-sample / null | M4 IS the second attempt (rank 6, enters only if 111's window differs from Lucca-Moench) | already re-entered, do not duplicate |
| turn-of-month (unconditional) | 108 | null | M6 ruled resurrection (does not enter); M5 (NQ-vs-ZN month-to-date relative performance) is a different claim, already on the map at rank 4 | CLOSED FOR GOOD for the unconditional claim |
| vwap_dist LOW -> 1d (H118 sibling) | 136, 137 | closed on Validation | vwap_dist LOW 2-attempt limit exhausted (session log 2026-09-10 16:54) | CLOSED FOR GOOD |
| intraday VWAP fade | 013, 084 | decisively negative / null | none | CLOSED FOR GOOD |
| witching volatility | 109 | null | expiry dealer hedging: no footprint without options data | PARKED on data |

## Clusters already at the 2-attempt limit (no ruling needed; recorded so it is never asked again)
weekly / multi-day trend following (6 attempts, EXP-047 tracks it forward) · candlestick / bar patterns (12) · cross-asset lead-lag ZN/currency/oil (3) · volume level / imbalance / vacuum (5) · gap / overnight-extreme open fade (10) · IB / opening-range breakout (3) · level-sweep reversal (8) · reference-level fades (6) · multi-factor combination (2) · pre-NFP drift (3) · VXN level / ROC as direction (2; RANGE use open as Entry 8).

## What this changes
Nothing enters the shelf from this audit. The map's LEARN pre-check of September 11th was already correct on every family it named; this audit extends the same rulings to the 14 clusters it did not name and writes them down. Two families the audit would otherwise have flagged (110, 111) are already the map's second attempts (M1, M4) -- confirmed not duplicated. Three items are parked on data, not evidence (options VRP, witching, expiry dealer hedging) and re-open only when the data budget grows per the data policy.

## Full machine table
See data/learn_closed_family_audit.json (clusters + name-level families) and the script's printed table.
