# S001 — SCREEN result and SALVAGE check (2026-09-15, Day One)

Strategy: S001 Level Sweep Reversal on compressed prior days (M26 via Salvage).
Frozen spec: research/infrastructure/strategy-specs/S001-level-sweep-reversal.md (sha256
dfd4bee4..., module 664d9a30..., registry FREEZE row research/ledger/strategies.jsonl).
Screen: `python3 src/screen_strategy.py strategy_s001_level_sweep_reversal` -> data/screen_S001_2026-09-15.json (git-tracked copy: research/studies/S001-screen-2026-09-15.json).
Salvage: `python3 src/salvage_check.py data/screen_S001_2026-09-15.json --extra level_source,direction` -> data/salvage_S001_2026-09-15.json (git-tracked copy: research/studies/S001-salvage-2026-09-15.json).

## SCREEN (directive s.2): one number

Discovery slice only (2,101 sessions, 2015-01-01 .. 2021-10-03). Paper-loop bookkeeping
(src/bot_stack_paper_run.py `_resolve_fill_outcome`, fill at the signal's entry). Costs
ASSUMED: $6.00 per micro round trip ($2.50/side commission + 1 tick/side slippage).

| | |
|---|---|
| trades | **131** (one per compressed-prior-day session with a confirmed sweep -- the same 131 Scan 033 found) |
| **net after assumed costs, 1 micro** | **-$116.38** (5 micros -$581.90; 10 micros -$1,163.80) |
| gross | +$669.62 (+334.7 index points over 131 trades = +2.6 pts a trade) |
| assumed costs | $786.00 (131 x $6.00 = 3.0 pts a trade) |
| win rate | 46.6% |
| average R, net | **-0.172R** (gross +0.099R; median risk 11.25 pts, so the 3.0-pt cost is ~0.21R a trade) |
| exits | 69 stop, 60 target, 2 time exit |
| verdict | **LOST MONEY after assumed costs -> SALVAGE** (s.2) |

Why it differs from Scan 033's "+0.030R net": Scan 033 charged the full-size NQ cost
basis (0.75 pts a trade, src/backtest.py ROUND_TRIP_COST_POINTS at $20/pt) and entered
at the confirming bar's close. S001 is the MICRO the paper book trades, where the same
$2.50/side commission is 2.5 pts, plus next-bar-open entry. The gross edge (+2.6 pts a
trade) is real in this sample and smaller than a micro's assumed round trip. That is
failure mode 1 (cost dominance) stated in dollars, and it is exactly what s.11's
cost-fragile flag exists for.

## SALVAGE CHECK (directive s.7): when did it work?

Menu, computed by src/salvage_check.py (definitions in its header). PROFITABLE = net > 0
at 1 micro with >= 15 trades (the s.6 floor a paper run needs to be judged); avg R is
shown because KEEP is an avg-R rule.

| condition | side | n | net $ (1 micro) | win | avg R net | reading |
|---|---|---:|---:|---:|---:|---|
| 1. VXN vs trailing | HIGH | 21 | -277.27 | 43% | -0.275 | loses, as the spec predicted |
| | LOW | 110 | +160.89 | 47% | -0.152 | dollars positive, **avg R negative** -- a few large-risk winners; fails KEEP by construction, not a salvage |
| 2. day's own range vs trailing | TREND | 36 | +62.90 | 53% | +0.004 | ex-post label (the day's range is not known at entry): diagnostic only, cannot be a filter |
| | RANGE | 95 | -179.28 | 44% | -0.238 | |
| 3. time of day | pre-09:30 trigger | 33 | +24.06 | 42% | -0.300 | dollars barely positive, avg R the worst cell: not a salvage |
| | 09:30-10:00 trigger | 98 | -140.44 | 48% | -0.128 | |
| 4. scheduled-news day | NEWS | 10 | -71.54 | 40% | -0.327 | loses, as predicted (thin) |
| | QUIET | 121 | -44.84 | 47% | -0.159 | |
| spec-named 5: level source | **prior-day level (high or low)** | **40** | **+353.70** | **57.5%** | **+0.080** | **the mechanism's own prediction: pre-market levels are thin, prior-day levels are the real reference** |
| | pre-market level | 91 | -470.08 | 42% | -0.282 | |
| spec-named 1: direction | long | 51 | +204.55 | 57% | +0.064 | the spec predicted shorts lose; they do (-$320.93, -0.321R). But 34 of the 51 longs (pre-market-low sweeps) lost -$222; the long edge IS the prior-day-low cell (17 trades, +$426.74) |
| | short | 80 | -320.93 | 40% | -0.321 | |

Integrity reading (menu-only rule): two sides qualify on dollars AND average R with
>= 15 trades -- "prior-day level" (n=40, +$353.70, +0.080R) and "long" (n=51, +$204.55,
+0.064R). They overlap (the prior-day-low longs are in both). One salvage per strategy:
the Director takes the ONE condition that (a) the Mechanism named in advance, (b) is
known at signal time, (c) is a single rule, and (d) has the better average R:
**prior-day levels only**. "Long only" is not taken as well -- taking both would be
"find the slice that looks good", which s.7 forbids.

## Verdict and what happens next

- **S001: KILLED at SCREEN** (lost money after assumed costs). Its Salvage check is done;
  it is closed. One salvage per strategy: the Level Sweep Reversal family has now had
  its salvage.
- **S001a spawned at SPECIFY** (directive s.7): S001's whole trade, restricted to sweeps
  of a PRIOR-DAY level (support = yesterday's low when it is the lower level;
  resistance = yesterday's high when it is the higher). Historical cell: 40 trades over
  the Discovery slice (~one per 50 sessions), +$353.70 net at 1 micro, 57.5% wins,
  +0.080R -- **cost-fragile** (< 0.10R) and, at that firing rate, certain to hit the 6-week
  point with fewer than 15 trades (s.6 KILL floor) unless the forward rate differs.
  Both facts go in its spec so nobody is surprised. It gets its own spec file, module,
  FREEZE and SCREEN next cycle; its screen must be run on the same Discovery data and
  will, by construction, reproduce the +$353.70 -- the SCREEN is a formality here and
  the PAPER record is the test.
- **LEARN:** (1) the Level Sweep Reversal edge, where it exists, is at PRIOR-DAY levels
  on compressed days; pre-market levels are noise (91 trades, -$470). (2) A micro
  contract's assumed commission ($2.50/side = 2.5 pts on MNQ) is 3x the full-size NQ
  cost basis every earlier study used; any intraday strategy with median risk ~11 pts
  needs > 0.2R gross a trade just to pay it. Cost-fragile is the default state of
  short-horizon NQ trades at this cost assumption, and B4b's measured number is the
  most valuable missing input in the project.
