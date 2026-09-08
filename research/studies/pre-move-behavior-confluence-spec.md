# Pre-Move Behavior, Signal Confluence — Frozen Spec (exp-107)

## Why this, not more single-trigger variants

exp-106 established the 6 individually-tested fresh behaviors each have
GROSS (pre-cost) edge close to zero -- not negative, just genuinely
absent. Widening stops on a zero-edge signal only shrinks losses toward
breakeven, it can't create profit. The one structurally different thing
left to try before abandoning single-day reactive triggers altogether:
does AGREEMENT between two independently-built, mechanistically
different signals carry more information than either alone? This is a
new, distinct mechanism (confluence), not a retune of any single one.

## exp-107: Volume-Imbalance x Trend-Alignment Confluence

**Idea:** exp-104 (signed opening volume) and exp-101 (multi-timeframe
trend alignment) are built from different data (volume vs. price shape)
and different windows (09:30-10:00 vs. hourly checkpoints through the
day). If both independently point the same direction on the same day,
that agreement may carry more signal than either alone, even though
each is individually edge-less.

**Detection:** Reuses `detect_volume_imbalance_signal_for_day` (exp-104,
unmodified) and `detect_alignment_signal_for_day` (exp-101, unmodified)
exactly as built. A confluence signal fires only on days where BOTH
produce a signal AND their directions agree. Entry/stop/target: uses
the trend-alignment signal's own entry/stop/target unchanged (the later-
forming, more information-rich of the two) -- confluence with the
volume-imbalance direction is used purely as a same-day directional
FILTER, no new price logic invented.

## Method

Step 1+2 together, same bootstrap/credibility bar as every prior batch
today (N_BOOTSTRAP=3000, seed=7, 90% CI, credible = CI entirely above
zero AND mean R-multiple net of cost >= 0.05R).

## Multiple-testing disclosure

1 pre-registered confluence combination, `search_batch_id
batch-2026-09-08-pre-move-confluence`. This is the only confluence pair
tested -- not a search over all possible pairings of today's 4
mechanisms (that would reintroduce the multiple-testing problem this
project's diagnostics exist to catch). Chosen because volume and price-
shape are the two most mechanistically distinct data types among
today's 4 signals.

## Decision rule / pre-commitment

Credible + economically-meaningful + n >= 40 earns a Validation-slice
prospective test. A null result here closes the single-day reactive-
trigger direction for pre-move behaviors -- per the pattern established
today (8 tests, 0 edge found, gross edge near zero throughout), further
search in this specific vein (short-horizon intraday reactive entries)
would not be a good use of further runs without a genuinely new data
source (not available without a paid feed already ruled out) or a
longer holding-period structure (a different research direction, not a
variant of today's).
