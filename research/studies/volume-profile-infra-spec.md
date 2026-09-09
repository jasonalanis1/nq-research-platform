# Volume Profile Infrastructure Spec

Frozen 2026-09-09. New infrastructure module to support value-area/
market-profile-style Observatory candidates (v6+), as previewed in the
2026-09-09 staff meeting.

## Method (disclosed approximation -- no tick/order-book data available)

This project only has 1-minute OHLCV bars, not tick or order-book data,
so a true Time-Price-Opportunity profile is not buildable. Standard,
disclosed approximation: each 1-minute bar's full volume is assigned to
that bar's typical price ((High+Low+Close)/3), binned into 1-point
price buckets (4 ticks per bucket -- coarse enough to keep buckets
populated given 1-minute granularity, fine enough to resolve NQ's
intraday range). This is the same class of approximation commonly used
when only bar data is available; it will understate profile precision
within a single wide-range bar but is unbiased in aggregate across a
session.

**Point of Control (POC):** the 1-point bucket with the highest total
RTH volume for the session.

**Value Area (VAH/VAL):** starting from the POC bucket, expand outward
(adding whichever adjacent bucket, above or below, has more volume)
until >=70% of the session's total RTH volume is captured (standard
70% convention). VAH = top of the captured range, VAL = bottom.

Computed per RTH session (09:30-16:00) only -- overnight volume
excluded, consistent with how "the day's value area" is conventionally
defined.

## Reuse

`build_daily_volume_profile(day_df) -> {"poc": float, "vah": float,
"val": float, "total_volume": float}`. Used the same way
`build_daily_bars` is reused across the project -- computed once,
unmodified thereafter.
