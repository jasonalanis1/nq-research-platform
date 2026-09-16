# S001a — Level Sweep Reversal on compressed prior days, PRIOR-DAY levels only (S001 salvage spawn)

**Frozen spec. Written 2026-09-15 (7:00 pm CT cycle, standing operating directive s.3 Step 4).
Stage at writing: SPECIFY -> FREEZE. Not edited after the FREEZE row in
research/ledger/strategies.jsonl (directive s.13). Disappointment produces a FIX ONCE or a
close to LEARN -- S001a has NO salvage of its own (s.7: one salvage per strategy; the Level
Sweep Reversal family's salvage was spent on S001). Module:
src/strategy_s001a_level_sweep_reversal_prior_day.py.**

## 1. Lineage (Salvage spawn, directive s.7)

S001 (research/infrastructure/strategy-specs/S001-level-sweep-reversal.md) was KILLED at its
SCREEN: 131 Discovery trades, net -$116.38 at 1 micro after assumed costs. Its Salvage check
(research/studies/S001-screen-and-salvage-2026-09-15.md, src/salvage_check.py) found ONE
condition that the Mechanism agent had named in advance (S001 spec s.4 item 5, "level
source"), that is known at signal time, and that is a single rule: sweeps of a PRIOR-DAY
level made money (n=40, +$353.70 net at 1 micro, 57.5% wins, +0.080R net) while sweeps of a
pre-market level lost (n=91, -$470.08). The Integrity reading took that one condition and
declined "long only" (overlapping, and taking both would be slice-hunting). S001a is that
filtered version, entering the loop at SPECIFY as s.7 requires.

**The ONLY change from S001 is the level set.** Nothing else is tuned: window, confirmation
margin, entry, stop, target, time exit, size and costs are S001's, restated below verbatim.

## 2. Mechanism (one paragraph, Mechanism agent)

Yesterday's high and low are the reference levels every participant on every timeframe
can see, so resting stops and breakout orders cluster there most densely; the pre-market
high/low is set on thin overnight volume and is a reference for far fewer participants.
A push through yesterday's extreme that cannot hold -- the bar closes back on the original
side by a margin -- means the liquidity beyond a level the whole market watched was taken
and the chasers are trapped; their exit is the reversal. After a compressed prior session
(bottom-tercile trailing range, the hyp-000048 fact: today is expected ~6% quieter) that
sweep is more likely a liquidity grab inside a range than the first leg of a trend day.
S001's Salvage measured exactly this split: prior-day-level sweeps +0.080R net, pre-market-
level sweeps -0.282R net, on the same compressed days with the same trade.

## 3. The whole trade (Monetization agent) -- S001's trade with one added rule

| rule | value |
|---|---|
| instrument | MNQ (micro Nasdaq-100), signals computed on the NQ 1-minute series (America/New_York timestamps) |
| condition (Salvage menu 2, unchanged from S001) | trade ONLY on sessions flagged `prior_day_narrow` = True by `volatility_conditioning.build_conditioning_frame` (frozen hyp-000048 definition: prior RTH day's range <= the 20th percentile of the trailing 20 RTH-day ranges, shifted). Known before the session opens. |
| levels (unchanged computation) | SUPPORT = min(prior calendar day's low, today's pre-market low before 08:30 ET); RESISTANCE = max(prior calendar day's high, today's pre-market high) -- `detect_level_sweep.compute_levels`, unchanged, each level tagged with its source (`prior_day_low` / `premarket_low`, `prior_day_high` / `premarket_high`). |
| **THE ADDED RULE (the salvage condition)** | **a signal is taken ONLY when the swept level's source is the PRIOR DAY (`prior_day_low` or `prior_day_high`). A session whose first confirmed sweep is of a pre-market level is NO TRADE for the session** -- the first confirmation of the session still "wins" exactly as in S001 (one trade a session, no second look later in the window), so the screen reproduces S001's 40-trade prior-day cell by construction rather than creating a new, differently-timed trade. Which level is the prior-day one is known before 08:30 ET. |
| watch window | 08:30 ET to 10:00 ET (family convention, WATCH_MINUTES=90; disclosed in S001 s.3: one hour before the cash open, kept unchanged) |
| sweep + confirmation | a bar's low < SUPPORT (or high > RESISTANCE), then a bar whose CLOSE is back beyond the level by >= 5.0 points (`close_min_distance`). First confirmation of the session wins; long or short. One trade per session. |
| entry | the OPEN of the bar AFTER the confirming bar (no lookahead; the paper loop's convention) |
| stop | the sweep extreme (lowest low of the sweep for a long, highest high for a short) |
| target | entry +/- 1.35 x risk (TARGET_R_MULTIPLE=1.35) |
| time exit | 15:55 ET: flat at the close of the 15:55 bar if neither stop nor target has been touched; no overnight |
| same-bar ambiguity | stop wins (bot_stack_paper_run._resolve_fill_outcome) |
| size | 1 micro contract, always (directive s.2 PAPER). Reported at 5 and 10 micros too (s.5). |
| sizing facts used | as S001: prior_day_narrow is the condition; the structural stop is left as is. VXN regime and scheduled-news flag are recorded per trade for information only (the menu no longer applies to S001a -- no second salvage). Wide-open -> wider-midday (hyp-000162 / S005) remains the named FIX ONCE input if the 15:55 time exit proves wasteful. |
| costs (ASSUMED) | commission $2.50/side + 1 tick (0.25 pt) slippage/side = $6.00 per micro round trip = 3.0 index points (src/paper_book.py ASSUMED_COST_USD_PER_MICRO_RT). Labelled ASSUMED until B4b measures it. **Cost-fragile flag (s.11) applies now: the historical cell's avg R is +0.080 < 0.10.** |
| paper-engine gates (not S001a rules) | the B7 loop's Risk/State Engine session gate (refuses expected-range multiplier <= 0.8944, scheduled-event days, stale data) applies in PAPER and not in the SCREEN -- the same disclosed screen/paper difference as S001. |

## 4. Where this should fail (Mechanism agent; recorded for LEARN -- S001a gets no salvage)

1. **High-VXN regime**: a sweep of yesterday's extreme in a high-vol regime is more often
   the first leg of a move (S001's menu 1 HIGH cell lost -0.275R).
2. **Trend day despite a quiet prior day**: when the day expands anyway, the reversal is
   the wrong bet by construction (ex-post label; diagnostic only).
3. **Short side**: S001's shorts lost (-0.321R); the prior-day-HIGH sweeps (23 of the 40
   cell trades) are the shorts. If S001a loses, expect it to be there.
4. **Scheduled-news days**: expansion days; the paper engine's gate already refuses them.
5. **Firing rate**: 40 trades over ~2,100 Discovery sessions is one trade per ~50
   sessions. The 6-week paper window (~30 sessions) is expected to produce ~0-1 trades,
   far under the s.6 15-trade floor. **Stated up front: unless the forward rate differs
   from history, S001a reaches its 6-week point unjudgeable and s.6 makes that a KILL.**
   The paper record, not this paragraph, decides.

## 5. Screen (directive s.2 SCREEN), pre-registered

One pass, Discovery slice only (data_split.get_discovery_data), src/screen_strategy.py,
the paper loop's bookkeeping, fill at the signal's entry price, ASSUMED costs above.
**One number: net $ at 1 micro after assumed costs.** Because S001a is S001's signal
filtered by a per-trade tag S001 already recorded, the screen is expected to reproduce the
salvage cell (40 trades, +$353.70) exactly; a different number means the module does not
implement the spec and is a defect, not a result. Net > 0 -> PAPER today; net <= 0 ->
KILLED, no salvage (s.7), LEARN.

## 6. Judgment (directive s.6)

40 trades or 6 weeks in paper, whichever first. KEEP: avg R > 0 after costs and the worst
streak inside a daily limit of three average winners. FIX ONCE (the named candidates: the
08:30 window start; the 15:55 time exit via the S005 input; long-only was NOT taken at
salvage and is a legitimate single FIX ONCE if the shorts are the losers). KILL: lost
money or < 15 trades in 6 weeks -- the honest expectation at the historical firing rate,
see s.4 item 5. Costs ASSUMED throughout; cost-fragile.
