# hyp-000156 (M23) — frozen one-shot Validation spec

Frozen: September 13th, ~7:10 pm CT, before any Validation data exists on disk.
Status: **BLOCKED ON DATA** — 6E on disk covers 2015-01-01 → 2021-10-03 (the Discovery
slice only). The Validation slice, 2021-10-04 → 2024-01-03, has never been fetched.

## The one test
Exactly Scan 030's construction on the Validation slice, nothing changed:
per day, |return 03:00–04:00 ET| / ATR14 (ATR14 = trailing-14-session mean of the
09:30–16:00 range, shifted one day) minus that day's mean unconditional hourly
|return| / ATR14 over 09:30–16:00. Block bootstrap block=10, N_BOOT=3000,
SEED=20260913, 90% CI. **PASS = CI on the mean diff entirely above zero AND the
Šidák-adjusted CI at the then-current N_validation (20 today) also above zero.**
Pre-London specificity cell (02:00–03:00) reported, not gated. First-minute share
kill check as in Scan 030. One shot; no retuning; no alternate windows examined.

## Power (from the Statistical stage)
Discovery sd of the per-day diff = 0.2066; Discovery effect +0.0537. Validation
n will be ~570 trading days if the slice is fetched in full; at that n, power at
the Discovery effect ≈ 1.0, at half the effect ≈ 0.97 — the test is decisive
either way. No outcome on Validation has been examined (none exists on disk).

## What this needs from Jason
One data pull: 6E 1-minute OHLCV, 2021-10-04 → 2024-01-03, from Databento via
`src/quote_data_pulls.py` on his Terminal (neither the device shell nor the cloud
can reach Databento). Expected cost is in the same band as the September 12th
quotes (ES $14.69 for a longer span) — under the $5+ rule it is his call. This is
NOT a Data Acquisition Trigger question (it is the same data type, for the slice
the protocol already requires), but the dollar rule still applies.

## After the pull
Run the script (to be written from Scan 030, Validation loader swapped, nothing
else) → Monetization (v2.5 order) → blind Gate → Holdout request. Monetization note
in advance: 6E has no base strategy in this project; M6E micro contracts exist;
this is the scheduled-event / session-transition volatility family (M20+M21+M23),
so the monetization question is the family's, not this entry's alone.
