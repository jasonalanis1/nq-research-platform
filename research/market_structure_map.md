# Market Structure Map — LEARN bucket 5: KNOWN STRUCTURE

Created September 11th, 2026 (UPGRADE 1, Jason's direction from the outside
review of the Full Scope doc). Owned by LEARN; Discovery drafts, the
Director ranks. **Every scan scope must name the map entry it probes. An
Idea Inventory entry with no map anchor is not an entry.**

Why this exists: 132 hypotheses, one survivor, and the shelf had become
three variants of "descriptor -> next-day range." Cutting generic
variables into terciles is search, not discovery. Each entry below names
WHO is forced to trade, WHEN, and what footprint that must leave in
1-minute NQ data. If nobody is forced, it is not structure and it does
not go on this map.

Data ceiling (UPGRADE 2): $20/month, 1-minute bars only. No order flow.
So the map is built from what 1-minute bars CAN see: session boundaries,
public calendars, cross-asset state. Sub-15-minute microstructure is out
of reach until profits fund data.

## LEARN pre-check (run September 11th, 2026, against the full ledger)

Families at the 2-attempt limit or otherwise closed -- a map entry that
touches one must carry a genuinely different mechanism claim or it does
not enter:

- IB / opening-range breakout: hyp-000011, 028 (Validation), 065, 135 -- CLOSED.
- Gap fade / overnight-extreme open fade: hyp-000012, 087, 089, 092, 101,
  102, 103/104 (Validation), 085, 090 -- CLOSED.
- Release-day reaction (CPI / NFP pooled): hyp-000115, 116 -- CLOSED.
- Pre-NFP drift: hyp-000112, 113, 114 -- CLOSED. Pre-FOMC drift: hyp-000111 -- one attempt spent.
- Turn-of-month (unconditional calendar): hyp-000108 -- one attempt spent, same claim as M6.
- Closing-pressure reversal: hyp-000110 -- one attempt spent.
- Weekly / multi-day trend following (CTA proxy): hyp-000017, 018, 019, 023, 024, 025, 026 -- CLOSED, EXP-047 tracks it forward.
- VXN level / ROC as a directional signal: hyp-000029, 030 -- CLOSED (range, not direction, still open: Entry 8).
- ZN leads NQ (lead-lag): hyp-000031, 034, 035 (Validation) -- CLOSED. Correlation-breakdown is a different claim.
- days_to_monthly_opex: hyp-000138 + Entry 2 -- CLOSED.
- overnight_range_vs_atr: H116 + Entry 1 -- CLOSED.
- Midday lull -> afternoon RANGE expansion: hyp-000105/106/133 -- VALIDATED (range), GATED at Holdout. Any midday DIRECTIONAL claim must be separable from it.

KNOWN FAILURE MODE added September 11th, 7:08 pm CT (from the first blind
Gate run): pandas `between_time` is inclusive at both ends, so adjacent
windows share their boundary bar. Every intraday-window spec states
half-open boundaries explicitly.

## The map

| # | Situation (ET) | Who is forced, and why | Footprint to measure | Horizon | LEARN / Integrity ruling | Director rank |
|---|---|---|---|---|---|---|
| M1 | Cash close 15:50-16:00 | Index funds, ETFs, rebalancers must execute MOC; futures absorb the imbalance | Last-10-min move, conditioned on close-window volume vs. its 20-day norm -> next-morning open and first 30 min RTH | Overnight | CLOSED FOR GOOD (Scan 013, September 11th 9:42 pm CT): second and last attempt on the closing-move family, clean null, 6/6 cells, no size dependence. Was: SECOND ATTEMPT (hyp-000110 unconditioned). | -- |
| M2 | RTH open 9:30-10:00 | Overnight inventory resolves; opening auction imbalance | Opening-range break conditioned on overnight range and gap | Intraday | CLOSED. IB-breakout and gap-fade families both at the 2-attempt limit; "conditioned on overnight range and gap" is cosmetic novelty over hyp-000065/101. Does not enter without a claim that is not a breakout and not a fade. | -- |
| M3a | Scheduled releases: CPI/PPI 8:30, NFP | Everyone reprices at once; dealers re-hedge | Post-release continuation vs. reversal 30/60/120 min | Intraday | CLOSED for CPI/NFP (hyp-000115, 116 at limit). | -- |
| M3b | FOMC statement 14:00 (+ presser 14:30) | Same, but a different event never tested post-release | 14:00 -> 14:30 / 15:00 / close continuation vs. reversal | Intraday | ATTEMPT 1 SPENT (Scan 016, September 11th 11:13 pm CT): clean null, n=52 of 53 FOMC days. A second attempt needs a genuinely different window (e.g. a reversal claim instead of continuation). | 1 |
| M4 | Pre-FOMC drift | Lucca-Moench: equities drift up the 24h before statements | Prior-day 14:00 -> FOMC-day 14:00 return vs. baseline | 1 day | CLOSED FOR GOOD (Scan 017, September 11th 11:18 pm CT): second and last attempt, near-miss (+0.1329 ATR, ci_90 [-0.0052,+0.2632]), not credible. 2-attempt limit exhausted. Was: SECOND ATTEMPT (hyp-000111). | -- |
| M5 | Month-end / quarter-end, last 2 sessions | Pension and balanced funds rebalance equity vs. bonds; when NQ has outrun ZN month-to-date they are forced sellers | NQ MTD minus ZN MTD (relative performance) -> last-2-day and first-2-day return | 1-3 days | ATTEMPT 1 SPENT (Scan 015, September 11th 11:07 pm CT): clean null, n=79 (nearly double the ~45 estimated), no credible gradient across terciles. A second attempt needs a genuinely different horizon/window. | 1 |
| M6 | Turn-of-month inflows | Payroll / 401k contributions land in the first sessions | First 3 sessions vs. baseline | 1-3 days | RESURRECTION of hyp-000108 (same claim, same window). "Conditioned on prior month" is cosmetic. Does not enter. | -- |
| M7 | Vol-control / risk-parity deleveraging | Vol-targeting funds must sell as VXN spikes and re-buy as it falls, over 1-3 days | VXN change (1d, 3d) -> NQ forward 1-3 day return | 1-3 days | DIRECTIONAL use is CLOSED (hyp-000029 level, 030 ROC). RANGE use: hyp-000142 -> Statistical PASS -> Validation PASS (hyp-000144, September 11th 9:57 pm CT: HIGH 1.120 [1.066,1.177], Sidak-adjusted clears). VALIDATION CANDIDATE, GATED at Holdout (Jason). LAST attempt on the variable either way. A directional re-entry needs a claim that is not "VXN ROC predicts direction". | (Entry 8) |
| M8 | CTA trend flows | Trend followers add after multi-day breakouts, cut after breakdowns | 20/50-day breakout state -> 1-3 day continuation | 1-3 days | CLOSED. Seven trend-following attempts; EXP-047 tracks the family forward. Does not enter. | -- |
| M9 | Nasdaq-100 rebalance / reconstitution days | Index funds must trade the change at the close; dates public | Close-window volume and move vs. normal days; next-day reaction | Overnight | RE-PARKED (September 12th, 12:20 am CT): calendar (src/nasdaq_rebalance_calendar.py) is correct and on file, but Scan 018 found the continuous-contract NQ data file has a systematic gap on every one of the 27 in-range rebalance Fridays (data stops ~09:29 ET, resumes next session) -- the rebalance date and the NQ futures quarterly roll date are the same day, and the roll-day RTH session appears to be missing project-wide from this data file. n_rebalance_days=0, INDETERMINATE not null, not a spent attempt. Needs Jason: source roll-day-covering NQ data, or retire M9 permanently. See research/mechanisms/nasdaq-rebalance-close-window-m9.md. | -- |
| M10 | European close 11:30 / midday lull | Liquidity providers step back; hyp-000106 characterized the RANGE lull | Lunch-hour (11:30-13:30) reversal of the morning (9:30-11:30) move, conditioned on morning-move size vs. ATR | Intraday | ATTEMPT 1 SPENT (Scan 011, September 11th 9:55 pm CT): clean null, all 6 cells. A second attempt needs a claim that is not "morning move retraces in the lull". Was: NEW as a DIRECTIONAL claim. Must be separable from the validated midday-lull RANGE finding (Portfolio double-count risk); the mechanism claim is "morning move driven by thinning liquidity partially retraces when the deep pool returns at 13:30", not "range compresses". Daily n. | 1 |
| M11 | Cross-asset divergence NQ-ZN | Systematic and risk-parity books rebalance when the equity-bond hedge breaks | Rolling 20-day NQ-ZN return correlation breakdown (state) -> NQ 1-3 day | 1-3 days | ATTEMPT 1 SPENT (Scan 012, September 11th 9:36 pm CT): P1 not confirmed, HIGH-minus-LOW 3d -0.135 ATR ci_90 [-0.291,+0.019] near-miss, sign and drift shape right, magnitude not credible. A second attempt needs a forced-flow proxy, not a window/bucket change. Was: NEW. Distinct from the closed ZN lead-lag family (031/034/035). | 2 |
| M12 | Cross-asset correlation regime across the NQ/ZN/6E/CL basket | Risk-parity and vol-targeting funds must cut GROSS exposure when average pairwise correlation across their book rises -- measured portfolio volatility is a mechanical function of the correlation matrix, so a correlation spike forces delevering at an unchanged vol target regardless of view. Equities are the largest gross leg, so NQ absorbs the largest share of that forced selling. | 20-day rolling average pairwise correlation across the 4-instrument basket; sharp RISES (top tercile of 5-day change) -> NQ forward 1-3 day return | 1-3 days | NEW (September 12th, 1:40 am CT, Jason lifted the cross-asset hold: "Run cross-asset first"). LEARN: distinct from M11 (pairwise NQ-ZN correlation BREAKDOWN, attempt 1 spent) -- this is basket-wide correlation CONVERGENCE forcing a gross-exposure cut, the opposite state and a different forced participant. Distinct from exp-063/064 (naive 6E/CL lead-lag, both closed) and exp-051/052 (4-instrument trend/reversal PORTFOLIO, both closed) -- neither conditioned on a correlation state nor named a forced participant. Not a resurrection. KNOWN CONFOUND, pre-registered: correlation spikes cluster in selloffs, so the gating cell MUST disclose trailing NQ return by tercile or the result is indistinguishable from the closed momentum/continuation family. ATTEMPT 1 SPENT (Scan 019, September 12th, 1:52 am CT): REFUTED with no gradient -- LOW +0.1988 / MID +0.1815 / HIGH +0.1897 ATR at h=3, spread 0.017 ATR against a 0.06-0.08 detectable effect, n=553 per tercile. The state variable carries no information; the gating claim was negative drift and the measured value was credibly POSITIVE. Best-powered scope the engine has run, so this is a real null, not an underpowered one. A second attempt needs a genuinely different forced-flow proxy, not a window or bucket change -- and at the current data ceiling there isn't one. | -- |
| M13 | Leveraged-ETF close rebalance | Leveraged and inverse ETF sponsors must trade (L^2-L)*AUM*r into every close, in the day's direction, by prospectus | Sign-adjusted 15:30-16:00 return conditioned on |day-so-far return|, instrument as a factor (RTY, ES, NQ); ordering RTY > ES >= NQ and growth with AUM are the fingerprint vs generic intraday momentum | Intraday (last 30 min), next-session reversal reported | NEW (September 12th, ~9:25 am CT, sourcing entry 2a from the outside-AI synthesis). Not a resurrection of hyp-000110 / M1 (those used the close move as predictor; this predicts the close move from the day). Confound = intraday momentum (2b), separated by the instrument/AUM ordering. Mechanism doc research/mechanisms/letf-close-rebalance-m13.md. WAITING on RTY + ES data (queue item 3) -- do not scan NQ alone. | 1 |

Expiry-day dealer hedging is real structure but has no visible footprint
in 1-minute NQ without options data -- deferred until the data budget grows.

## Director ranking, first three scopes (frozen at the adoption staff meeting, September 11th, 2026)

Ranked on: resolves in weeks (daily sample), data already on disk, NEW ruling,
and a mechanism claim that can carry a PRE-registered prediction (Mechanism
now writes BEFORE the scan, UPGRADE 3).

1. **M10** midday directional retrace, conditioned on morning-move size. Intraday; daily n; Mechanism doc owed first.
2. **M11** NQ-ZN correlation breakdown -> 1-3 day. Daily n; ZN on disk; Mechanism doc owed first.
3. **M1** cash-close move conditioned on close-window volume -> next morning. Overnight; daily n; last attempt on the family.

M5, M3b, M4 all drawn and closed 2026-09-11/12. M9 drawn as Entry 15,
found INDETERMINATE on a data gap (not a null) 2026-09-12 12:20 am CT and
RE-PARKED pending better NQ data -- Jason is sourcing that himself. M12
ADDED and drawn as Entry 16 September 12th, 1:40 am CT on Jason's explicit
go-ahead; it is the last untried axis reachable with data already on disk.
M2, M6, M8 do not enter.

STANDING NOTE (Jason + an outside read, September 12th, ~1:35 am CT): the
"widen the forced-participant definition" and "lift the $20/month data
ceiling" options are NOT separate -- the definition can only widen as far
as the data lets us SEE the participant. Everything closed so far
(rebalances, FOMC, month-end, opex, the close) is scheduled, public, and
the most heavily competed flow in NQ; nine clean nulls there is the
expected result, not bad luck. The participants who plausibly leave money
on the table -- dealers hedging options gamma, basis arbs, intraday
liquidity takers -- are not visible in 1-minute OHLCV at all. So widening
the definition without new data produces lottery tickets with a nicer
story attached. M12 is the last free shot; after it, the honest next move
is priced data, not more map entries. Ceiling policy (Jason): price the
pulls first, set the ceiling from the quotes, and expect the change to buy
ONE new search axis -- one or two entries, most closing null -- not a
restocked shelf.

## Maintenance

- Discovery maintains this file. LEARN vets every edit against the ledger
  by name AND by what is measured. Integrity issues the per-entry ruling.
  Statistical attaches the thin-sample cost where events are calendar-bound.
- A map entry is never "closed" -- structure persists. Its ATTEMPTS close.
  Record each attempt's hypothesis IDs in the ruling column.
- Weekly report to Jason (UPGRADE 9) states map coverage: which entries
  scanned, which open.
