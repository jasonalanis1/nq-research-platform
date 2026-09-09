# Closing-Pressure Reversal -- Observatory v10 Design Spec

Frozen 2026-09-09. Sourced from the market-microstructure research
agent (dispatched this session on "auction mechanics / closing price
formation"), ranked #1 of that batch for citation strength, zero data
cost, and no overlap with tested candidates.

## Mechanism

Bogousslavsky & Muravyev (2023, "Who Trades at the Close?", Journal of
Financial Economics) document systematic late-day price pressure
around the closing auction, followed by next-day reversal -- large
directional order flow concentrated in the final minutes of trading
pushes price away from fair value, which partially corrects the
following session. This is distinct from every prior candidate tested
here: not overnight gap magnitude (hyp-000056/057/092/093, which
measures the close-to-open move), not intraday range persistence
(the 3 validated findings), and not MOC imbalance itself (which needs
a paid real-time imbalance feed we don't have) -- this uses the LAST
15 MINUTES OF RTH RETURN as a free, OHLCV-derivable proxy for closing
imbalance direction/magnitude, then looks at the NEXT session's
return, not the overnight gap.

Data requirement: none beyond what we already have -- last-15-min RTH
return (15:45-16:00 ET) is derivable from existing NQ 1-min bars.

## Definition (directional, pre-specified from literature -- avoids
direction-ambiguity failure mode)

Event: classify each Discovery day by its last-15-min RTH return
(15:45 close to 16:00 close), signed. Split into "late_up" (top
tercile of trailing-20-day distribution of this measure, by magnitude,
positive sign) and "late_down" (bottom tercile, negative sign) --
complement is all other days ("moderate").

Outcome: NEXT session's full RTH return (09:30 open to 16:00 close,
signed, in points).

Pre-specified direction (from literature): reversal, not continuation.
late_up days -> next-day return should skew NEGATIVE relative to
moderate days. late_down days -> next-day return should skew POSITIVE
relative to moderate days. Stated before running Discovery.

## Method

Bootstrap mean-difference CI (N_BOOTSTRAP=3000, seed=7, 90% CI) on
(late_up next-day mean - moderate next-day mean) and separately
(late_down next-day mean - moderate next-day mean), same convention as
observatory_v5. ATR-normalized cost-aware screen applies (v4
convention, 0.05 floor) since this is a directional/return finding.
Credible = CI excludes zero AND direction matches the pre-specified
reversal sign for that leg.

## Per protocol

Exploratory only, Discovery data only, non-trading. A credible AND
cost-viable result on either leg gets its own Behavioral Finding, then
a frozen hypothesis spec through the standard Discovery -> Validation
pipeline (2-attempt limit) before any live consideration. A null
result on both legs is logged and closes this thread -- no retuning
the tercile definition or the 15-minute window after seeing the
result.
