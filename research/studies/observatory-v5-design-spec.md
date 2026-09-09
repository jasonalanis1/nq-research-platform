# Observatory v5 Design Spec

Frozen 2026-09-09. Staff-meeting consensus for the next default
Observatory scan after v4 closed with no open lead (Path-to-
Profitability Advisor and Market Behavior Advisor takes folded in
below, per standing practice).

## Candidates considered

- Day-of-week effects -- Path-to-Profitability Advisor: low prior, this
  is a well-known, heavily-arbitraged effect class in equity index
  futures; unlikely to survive cost even if found. Deprioritized.
- Value-area / failed-auction concepts (market profile) -- Market
  Behavior Advisor: mechanistically plausible but requires volume-
  profile machinery this project doesn't have yet; bigger build for an
  unproven family. Deprioritized for now, not ruled out permanently.
- **Overnight-session-return persistence/reversion** -- both advisors:
  genuinely untested (checked: no prior study covers this), cheap
  (reuses daily_bars + existing overnight-window logic from
  study_overlay_screen2.py's coil lookup pattern, no new data), and a
  real occurrence-based (not touch-based) event type, distinct from
  v1/v2's level-touches and v3's gap/volume-spike occurrences. Selected.

## Definition

Event: the overnight session's own directional move (16:00 prior RTH
close -> 09:30 current-day RTH open), signed. Two event types:
`overnight_up` (close-to-open return > 0) and `overnight_down` (< 0),
magnitude-bucketed is NOT used (kept as a simple binary direction, per
v1's own-baseline-vs-conditional convention) -- outcome measured is RTH
forward return from the open, same horizons/buckets/regime
conditioning as v1/v3.

Question: does the overnight move's direction predict continuation
(trend) or reversion (fade) during RTH, relative to the unconditional
RTH baseline? This is the natural pairing with H87/H89 (which tested
gap MAGNITUDE vs baseline, not overnight DIRECTION vs baseline) --
distinct question, not a retest.

Same 4 time buckets, 6 horizons, volatility-regime conditioning, and
the v4 ATR-normalized cost-aware screening (floor 0.05) as v4.

## Per protocol

Any Promising/Interesting AND cost-viable candidate gets its own
Behavioral Finding before any hypothesis spec is written.
