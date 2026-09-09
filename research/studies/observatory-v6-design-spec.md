# Observatory v6 Design Spec

Frozen 2026-09-09. New event family: first RTH touch of the prior
session's Value Area High (VAH), Value Area Low (VAL), or Point of
Control (POC) -- from the new volume_profile.py infrastructure
(research/studies/volume-profile-infra-spec.md). Structurally
different from v1 (fixed reference-level touches: prior-day H/L,
overnight H/L, VWAP) even though the mechanic (first-touch) is the
same -- these 3 levels are volume-derived, not price-derived, and
represent where the prior session's activity actually concentrated
rather than its extremes or a simple time-weighted average.

## Event definitions

- `prior_poc`, `prior_vah`, `prior_val`: first RTH touch of the prior
  day's Point of Control / Value Area High / Value Area Low
  (volume_profile.build_daily_volume_profile, unmodified).

Same 4 time buckets, 6 horizons, volatility-regime conditioning, and
ATR-normalized cost-aware screen (floor 0.05) as v4/v5. Baseline/
ranking machinery otherwise unchanged from v1.

## Per protocol

Any Promising/Interesting AND cost-viable candidate gets its own
Behavioral Finding before any hypothesis spec is written.
