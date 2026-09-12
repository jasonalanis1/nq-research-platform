# Observatory — information-transmission map, v2 (both sessions, 4 resolutions, shock-conditioned)

Written: September 12th, ~4:25 pm CT (TEST cycle under the new budget-use
rule, continuing queue v2 item 4 past v1's stopping point). Characterization
only -- no hypothesis, no ledger row, no promotion bar.

## Scope
Same NQ/ZN/6E/CL basket, Discovery slice, extended in the three directions
v1 listed as "next": RTH AND overnight (18:00 -> 09:30 ET) sessions; 5, 15,
30 and 60-minute bars; and a SHOCK-CONDITIONED view -- bars where the other
instrument's |return| is in its top 5%, then NQ's sign-adjusted response
1-4 bars later in units of NQ's own bar std, block-bootstrap 90% CI. Both
directions (shock in other -> NQ; shock in NQ -> other). Script:
`src/observatory_information_transmission_v2.py`; full grid on disk in
`data/observatory_info_transmission_v2_results.json` (24 session x
resolution x pair cells, each with the lag table and both shock tables).

## Result, in one table

Unconditional: contemporaneous |corr| vs the largest |corr| at any nonzero lag.

| Cell | NQ-ZN lag0 / max lag≠0 | NQ-6E lag0 / max | NQ-CL lag0 / max |
|---|---|---|---|
| RTH 5m  | -0.30 / 0.02 | -0.04 / 0.01 | +0.10 / 0.01 |
| RTH 15m | -0.32 / 0.03 | -0.01 / 0.02 | +0.14 / 0.01 |
| RTH 30m | -0.33 / 0.04 | -0.01 / 0.02 | +0.13 / 0.03 |
| RTH 60m | -0.32 / 0.06 | -0.02 / 0.01 | +0.10 / 0.04 |
| OVN 5m  | -0.28 / 0.01 | -0.00 / 0.01 | +0.04 / 0.01 |
| OVN 15m | -0.29 / 0.02 | +0.01 / 0.01 | +0.03 / 0.00 |
| OVN 30m | -0.30 / 0.01 | +0.02 / 0.01 | +0.05 / 0.01 |
| OVN 60m | -0.32 / 0.04 | +0.03 / 0.01 | +0.09 / 0.01 |

Shock-conditioned (shock in the other instrument -> NQ one bar later, sd
units): every one of the 24 cells has a lag-1 mean between -0.04 and +0.09
sd, against a same-bar response of 0.7-1.0 sd for ZN and CL. Of the 24
lag-1 CIs, one excludes zero (overnight 5-min, CL -> NQ, +0.036 sd,
CI +0.010 to +0.065); two more sit with a lower bound a hair below zero
(RTH 30/60-min ZN -> NQ, +0.07 / +0.09). Reverse direction (shock in NQ ->
other) is the same picture. With 192 shock-lag cells at 90% CIs, roughly
19 would clear zero by chance; one did. This is a null consistent with
its own multiplicity, and the one clearance is 0.036 sd -- not a size that
survives a spread.

## Reading
1. The NQ-ZN (negative, ~-0.3) and NQ-CL (positive, ~+0.1 in RTH, weaker
   overnight) contemporaneous relationships are stable across every
   session and resolution. NQ-6E is ~0 everywhere. Nothing new -- this is
   the known cross-asset structure and it is confirmed at the ceiling.
2. **Transmission between these four instruments is complete within one
   bar at every resolution tested, in both sessions, unconditionally and
   after shocks.** Whatever lead-lag exists is inside 5 minutes. That is
   the same conclusion as the unconditional 15-min v1 read, now with the
   two obvious escape hatches (other resolutions; conditional on a shock)
   closed. Combined with M11 and M12, four lenses now agree: at 1-minute
   OHLCV on this basket, cross-asset information flow is not a place NQ
   money is left on the table.
3. The overnight session does not behave differently from RTH here. The
   overnight CL relationship is weaker (thinner CL overnight), not
   structurally different.

## What this settles / does not
- Settles, for the map: the NQ/ZN/6E/CL lead-lag question at >=5-minute
  resolution. LEARN should record "cross-asset lead-lag at the current
  ceiling: characterized, nothing to draw from" so it is not re-proposed
  by the literature or practitioner channels under another name.
- Does not settle: sub-5-minute (tick) lead-lag -- already on the SKIP
  LIST as a trade; and lead-lag with ES/RTY/YM, which are parked at the
  data ceiling.

## Next under item 4
The fixed, interpretable state classifier (broad-equity agreement /
NQ-only residual / rate-confirmed / rate-conflicted / overnight vs cash
variance) reporting forecast range and MAE per state. That is a different
question (does the STATE of the basket condition NQ's own behavior) from
this one (does the basket LEAD NQ), and it is what the three validated
volatility facts would plug into.
