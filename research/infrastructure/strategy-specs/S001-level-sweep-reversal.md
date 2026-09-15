# S001 — Level Sweep Reversal on compressed prior days (M26, via Salvage)

**Frozen spec. Written 2026-09-15 (Day One of the standing operating directive, s.14.4).
Stage at writing: SPECIFY -> FREEZE. Not edited after the FREEZE row in
research/ledger/strategies.jsonl (directive s.13). Disappointment produces S001a or a FIX
ONCE, never an edit here. Module: src/strategy_s001_level_sweep_reversal.py.**

## 1. Lineage (Salvage, directive s.7)

The unconditional Level Sweep Reversal (research/setups/level-sweep-reversal.md,
src/detect_level_sweep.py, exp-003..024, hyp-000001/003/007/008) was closed six times as a
raw effect. Scan 033 (hyp-000159, M26, research/mechanisms/level-sweep-reversal-range-
contraction-m26.md s.11) then split its 474 Discovery trades by the validated
`prior_day_narrow` state (hyp-000046/048, HOLDOUT PASSED): compressed prior day
**+0.030R net, n=131**; non-compressed **-0.065R net, n=343**. Under the CI bar that was a
P1 FAIL. Under the directive it is the Salvage menu's condition 2 (range-bound prior day)
on a fully specified trade that made money after costs. S001 is that filtered version.
One salvage per strategy: this IS the Level Sweep Reversal family's salvage; if S001
fails its own paper run it gets its own menu check (s.7) and then closes for good.

## 2. Mechanism (one paragraph, Mechanism agent)

Yesterday's high/low and the pre-market high/low are reference levels that resting
stops and breakout orders cluster around. A push through one of them that cannot hold
-- the bar closes back on the original side by a margin -- means the liquidity beyond the
level was taken and the breakout buyers/sellers who chased it are trapped; their exit is
the reversal. That story only dominates when the market is NOT in an expansion regime:
after a compressed prior session (bottom-tercile trailing range, the hyp-000048 fact
says today is expected to be ~6% quieter than usual) a sweep is more likely a liquidity
grab inside a range than the first leg of a trend day, which is exactly what the
Scan 033 split showed (compressed +0.030R vs non-compressed -0.065R).

## 3. The whole trade (Monetization agent)

| rule | value |
|---|---|
| instrument | MNQ (micro Nasdaq-100), signals computed on the NQ 1-minute series (America/New_York timestamps) |
| condition (Salvage menu 2) | trade ONLY on sessions flagged `prior_day_narrow` = True by `volatility_conditioning.build_conditioning_frame` (frozen: prior RTH day's range <= the 20th percentile of the trailing 20 RTH-day ranges, shifted; src/study_intraday_behavior_batch1.py LOOKBACK_DAYS=20, RANGE_NARROW_PCTL=20). Known before the session opens. |
| levels | SUPPORT = min(prior calendar day's low, today's pre-market low before 08:30 ET); RESISTANCE = max(prior calendar day's high, today's pre-market high) -- `detect_level_sweep.compute_levels`, unchanged |
| watch window | 08:30 ET to 10:00 ET (90 minutes from the family's 8:30 "NY open" convention -- research/setups/level-sweep-reversal.md:27, WATCH_MINUTES=90). Disclosed: 08:30 ET is one hour BEFORE the cash open; this is the family's convention as tested and is kept unchanged so the screen is the same trade Scan 033 measured. Changing it is a FIX ONCE candidate, not a quiet edit. |
| sweep + confirmation | a bar's low < SUPPORT (or high > RESISTANCE), then a bar whose CLOSE is back beyond the level by >= 5.0 points (`close_min_distance`, MIN_CONFIRM_DISTANCE_POINTS=5.0). First confirmation of the session wins; long or short. One trade per session. |
| entry | the OPEN of the bar AFTER the confirming bar (no-lookahead convention of the paper loop, as B3 and the execution dummy). Disclosed: the family's tests entered at the confirming bar's close; the paper loop cannot fill at a price that has already printed, so the screen and the paper run both use next-bar open. |
| stop | the sweep extreme (lowest low of the sweep for a long, highest high for a short) -- structural, the family's stop |
| target | entry +/- 1.35 x risk (TARGET_R_MULTIPLE=1.35, risk = entry - stop) |
| time exit | 15:55 ET: flat at the close of the 15:55 bar if neither stop nor target has been touched (the paper loop's bookkeeping exit; no overnight) |
| same-bar ambiguity | stop wins (bot_stack_paper_run._resolve_fill_outcome) |
| size | 1 micro contract, always (directive s.2 PAPER). Results are also reported at 5 and 10 micros (s.5). |
| sizing facts used | (a) prior_day_narrow (hyp-000048, next-day range x0.9438) is the CONDITION itself -- the structural stop is left as is because the expected range is only ~6% smaller and the stop is set by the sweep, not by a multiple. (b) VXN -> next-session range (hyp-000142) and quiet-midday -> afternoon (hyp-000105) are NOT part of S001's rules; VXN regime is recorded per trade for the Salvage menu (condition 1). Wide-open -> wider-midday (hyp-000162 / S005) is the named FIX ONCE input if the 15:55 time exit proves wasteful. |
| costs (ASSUMED) | commission $2.50/side + 1 tick (0.25 pt) slippage/side = $6.00 per micro round trip = 3.0 index points (src/integrity_checks.py COMMISSION_PER_SIDE_USD, SLIPPAGE_TICKS_PER_SIDE, TICK_SIZE; src/paper_book.py ASSUMED_COST_USD_PER_MICRO_RT). Labelled ASSUMED until B4b measures it. Cost-fragile flag at avg R < 0.10. |
| paper-engine gates (not S001 rules) | the B7 loop's Risk/State Engine (src/risk_state_engine.py decision_for) refuses a session when expected-range multiplier <= 0.8944 (bottom decile: prior_day_narrow alone is 0.9438 and passes; narrow AND coiled overnight is 0.844 and is refused), on a scheduled-event day, or on stale data. The SCREEN does not apply these gates; the paper record does. Disclosed as the one known screen/paper difference. |

## 4. Where this should fail (Mechanism agent's Salvage menu for S001)

1. **High-VXN regime** (menu 1): a sweep in a high-vol regime is more often the start of
   a move; expect the short side and high-VXN days to be the losers.
2. **Trend day despite a quiet prior day** (menu 2, the day's OWN range vs trailing):
   when the day expands anyway the reversal is the wrong bet by construction.
3. **Confirmation after 09:30** (menu 3, time of day): a sweep confirmed inside RTH
   proper has the cash-open flow behind it; the 08:30-09:30 pre-market confirmations
   and the 09:30-10:00 ones may behave differently.
4. **Scheduled-news days** (menu 4): FOMC/CPI/NFP sessions are expansion days.
5. **Level source**: pre-market levels are thinner than prior-day levels; sweeps of a
   pre-market level may be noise (recorded per trade as `level_source`).

## 5. Screen (directive s.2 SCREEN), pre-registered

One pass, Discovery slice only (data_split.get_discovery_data, 2015-01-01 .. 2021-10-03),
src/screen_strategy.py, same fill/exit bookkeeping as the paper loop, fill at the
signal's entry price (no broker simulation), ASSUMED costs above. **One number: net $ at
1 micro after assumed costs.** Also reported: trades, win rate, average R, gross. No CI
gate, no multiplicity correction, no holdout. Net > 0 -> PAPER today; net <= 0 ->
SALVAGE by the menu in s.4.

## 6. Judgment (directive s.6)

40 trades or 6 weeks in paper, whichever first. KEEP: avg R > 0 after costs and the
worst streak inside a daily limit of three average winners. FIX ONCE: near break-even
or a wasteful exit (the named candidates: the 08:30 window start; the 15:55 time exit
via the S005 input). KILL: lost money or < 15 trades in 6 weeks. **Stated up front:** Scan 033 found
131 compressed-day trades over the ~1,700-session Discovery slice, i.e. one trade per
~13 sessions; 6 weeks (~30 sessions) is therefore ~2-3 trades, far below the 15-trade
floor, before the paper-engine gates remove any. Unless the forward record fires far
more often than history, S001 will reach its 6-week point with too few trades and s.6
makes that a KILL ("a strategy that barely trades cannot be judged and is not worth the
paper slot"), followed by its Salvage check. That is the honest expectation; the
directive names S001 first through Salvage regardless, and the paper record -- not this
paragraph -- decides.
