# Backlog

A single place to capture every idea the moment it comes up, so nothing said in passing gets lost. Any new idea should get logged here immediately, even before it's decided on. Reviewed as part of the regular project check-ins.

## Active

- **Initial Balance breakout continuation** — proposed by Jason 2026-09-01, directly (not sourced from a video clip), after the trend-structure liquidity filter's inconsistent result closed out the reversal thesis. Explicit direction: pick the next research area based on established NQ/market-structure concepts rather than Jason choosing it himself, explain the reasoning, and proceed without waiting for further instruction. Selected because every idea tested to date (Level Sweep Reversal's three variants, the FVG entry trigger, the trend-structure liquidity filter) shares the same underlying bet -- a level sweeps, price reverses -- and all six have failed; testing more reversal variants would itself be the kind of search-until-something-looks-positive pattern this project's integrity rules exist to prevent. This pivots to a genuinely different, independently well-documented thesis (continuation, not reversal): the "Initial Balance" from Market Profile / Auction Market Theory (CBOT, 1980s) -- the range set in the first stretch of trading after the open, and whether price holds that range (a range day) or breaks and runs with it (a trend day). Tied directly to the project's stated objective (behavior around the NQ 8:30 AM NY open), needs no new data source. Note: this project already has an "ORB placeholder" (`research/setups/orb-placeholder.md`) from 2026-08-15 testing a superficially similar continuation idea (15-min range, 60-min breakout window, 1x-range-width target) that was killed on 2yr real data (exp-013, 493 trades, -0.062R) -- but under the OLD pre-Research-Integrity-Protocol methodology (full contaminated window, never Discovery-slice-specific), with arbitrary untuned parameters the placeholder's own doc disclaimed. This is a related but meaningfully distinct idea (Market-Profile-grounded 30-min Initial Balance, breakout window to noon, project-standard 1.35R target), tested fresh against the Discovery slice specifically -- see `research/setups/initial-balance-breakout.md` for the frozen definition and full comparison to the old placeholder.

**Status update 2026-09-03: tested.** This ran as exp-028 (`research/experiments/_index.md`) -- 1,654 trades, statistically decisive kill (90% CI entirely below zero). Kept here as a historical record of the reasoning for picking this direction, not as an open item.

*(move items here from Parked when they're picked up)*

## In Scoping

- **NEW RESEARCH PHASE (queued, not yet started): intraday market-behavior
  characterization, professional-systematic-trader framing** -- proposed by
  Jason 2026-09-08, as a mission refinement layered on top of the
  2026-09-08 "market behavior -> condition -> strategy -> trade -> outcome"
  redefinition (same underlying approach, sharper verbiage). Jason's framing,
  verbatim intent: stop asking "what strategy should I try next?" and instead
  ask, in sequence -- "What is the market doing when it gives us an
  opportunity?" -> "Can we recognize that behavior in real time?" -> "When we
  recognize it, is there a statistically meaningful advantage to taking a
  particular trade?" Pipeline: observe market behavior -> identify recurring
  condition -> measure what happens next -> determine whether the behavior is
  exploitable -> match/design a strategy -> validate.

  Context: after 43 hypotheses at daily-bar resolution with 0% Validation-stage
  survival (including both portfolio-bundling and two ensemble attempts also
  failing), Jason's explicit decision was: continue the cheap Discovery-vs-
  Validation effect-size/ledger diagnostic; abandon daily-bar hypothesis-
  hunting for now (not permanently); pivot toward intraday behavior
  characterization; keep the execution-infrastructure track running in
  parallel. Explicitly do NOT purchase any intraday/order-flow data yet --
  first define exactly what information/behaviors are being sought using the
  1-min OHLCV data already on hand (no order-book/tick data available).

  Path-to-Profitability Advisor's independent read on this pivot (obtained
  2026-09-08): directionally sound, but only if treated as a genuinely new
  mechanism class (intraday structure/liquidity rhythm), not "daily research
  run at finer resolution" -- otherwise the much larger candidate space (many
  more possible windows/anchors/lookbacks at 1-min resolution) just relocates
  the same replication-failure problem with worse multiple-testing risk.
  Candidate behaviors it suggested scoping from (all derivable from existing
  1-min OHLCV, no new data needed): opening-range structure (first 30/60-min
  range vs. ATR, close inside/outside), intraday VWAP reversion/trend
  persistence, volume-profile skew across the session (U-shape strength,
  midday lull depth), momentum-burst bars (range+volume spike vs. trailing
  norm, continuation vs. exhaustion), overnight-gap first-hour fill/no-fill
  dynamics. Process cautions: pre-register exact windows/anchors/thresholds
  before looking at results (finer resolution = more researcher-degrees-of-
  freedom than the daily-bar batches); watch for look-ahead bias specific to
  intraday features (e.g. VWAP not yet fully formed within the bar); keep the
  same Discovery/Validation split and frozen-spec discipline; given 0/43 so
  far, consider a stricter promotion bar for this batch rather than reusing
  the one that has passed 43 and validated none.

  STATUS UPDATE 2026-09-08 (overnight autonomous run): batch 1 completed --
  see "Intraday Behavior Batch 1" under Tested/Closed. One finding
  (range-contraction/volatility-persistence) became the first-ever
  Validation-slice survivor in the project's history, but is not yet a
  costed rule. Remaining candidate behaviors not yet tried at intraday
  resolution: none from the Advisor's original 5-item list (all were
  either tested in batch 1 or excluded as already-covered ground). Next
  step, awaiting Jason: (1) decide on a concrete costed overlay design for
  the range-contraction finding (Advisor recommends a sizing/stop-width
  overlay on an existing signal over a standalone rule), and (2) decide
  whether to generate a fresh round of intraday candidate behaviors or
  shift effort elsewhere.

- **REAL FORK, needs Jason's decision:** this project now has 3
  confirmed, Validation-survived volatility-conditioning facts
  (range-contraction, overnight-coil, release-day-magnitude) and 0
  surviving directional signals to attach any of them to. Overlay-
  screening them onto already-dead signals (exp-077, exp-086, exp-087)
  has been tried 3 times and found nothing, which is expected -- a
  conditioning variable can't resurrect a signal that has no edge to
  condition. Two real paths forward: (a) design a brand-new
  directional signal specifically meant to pair with one of these
  volatility facts (e.g. a breakout-style entry sized/timed around
  release-day or post-coil expansion, since those predict WIDER range
  -- opposite structure from a mean-reversion entry); or (b) accept
  these are non-directional characterizations, stop trying to overlay
  them onto dead signals, and look for the next new directional idea
  independently. Not decided -- surfaced for Jason, not resolved
  autonomously, since it's a real scoping/direction call, not a
  mechanical fix.
- **Next Market Behavior Advisor consultation.** All 5 of its first-
  round candidates are now tested (1 of 5 survived Validation). Next
  natural checkpoint: consult it again for a fresh round -- likely
  after the fork above is resolved, so new candidates are built with
  the "needs to pair with a real directional signal" lesson in mind
  rather than repeating another volatility-only characterization.

*(nothing else currently open)*

## Ongoing / Prospective Tracking

- **exp-050: Prospective validation of exp-047 (weekly trend-following
  signal)** -- built 2026-09-06, per the Path-to-Profitability Advisor's
  recommendation and Jason's authorization ("let's run it"), directly
  following the exp-047/048/049 family's shelving below. Tracks the raw
  exp-047 signal forward on data that did not exist yet at freeze time
  (2026-08-19 19:59:00 America/New_York, the exact last on-disk bar at
  sign-off) rather than re-mining anything already on disk. Pre-registered
  checkpoints at 104/156/208 weeks, hard 260-week maximum horizon, a
  one-sided early-kill rule (Monte-Carlo-justified ~5% false-kill rate),
  no early-pass rule. Zero prospective weeks logged yet -- waiting on new
  NQ data to be fetched forward (cadence/cost of that ongoing paid pull
  is Jason's call, not yet decided). See
  `research/studies/prospective-validation-exp047-scoping.md`,
  `src/study_prospective_exp047.py`, ledger hyp-000020.

## Parked

- **Individual stocks as an alternative to NQ futures** -- raised by Jason 2026-09-03 during the post-"step back" conversation, considered and set aside (not rejected outright, parked). Both Claude's own assessment and the Path-to-Profitability Advisor's independent take agreed: moving to individual stocks multiplies the number of things being searched from one instrument to thousands of tickers, which multiplies the risk of "finding" a fake edge purely by chance -- the exact failure mode this project's promotion bar and Discovery/Validation split exist to prevent. It would also mean new data cost and none of what's been learned about NQ (calendar effects, gap behavior, reversal patterns) carries over. Revisit only if the NQ-specific search genuinely runs dry across multiple future checkpoints, not as a first resort.



- **Fundamental/macro finance plugins** (equity research, earnings analysis, economic calendar data — e.g. LSEG, Daloopa, S&P Global-style tools) — considered 2026-08-18. They solve a different problem (company/macro fundamentals) than this project's current focus (technical price-pattern backtesting on NQ futures). Revisit only if a future strategy hypothesis becomes fundamentals- or macro-driven (e.g., trading around FOMC/CPI releases), which Level Sweep Reversal is not.

- **Fair Value Gap (FVG) lower-timeframe entry trigger** — considered 2026-08-18, from a YouTube Short (ICT/Smart Money Concepts style). Same core thesis as the existing Level Sweep Reversal setup (sweep a significant level, price fails to close beyond it, reversal expected), but with a mechanically different entry technique: instead of "close back beyond the level" (the three variants already tested), enter on a 3-candle price imbalance ("Fair Value Gap") on a lower timeframe once the higher-timeframe rejection is seen. Not just a parameter tweak — a genuinely different entry trigger, so not redundant with exp-013 through exp-020. Source claim ("catches 3.6R almost every day") is one cherry-picked anecdotal example with no sample size or losing trades shown — not evidence, don't weight it. If tested later, must go through the full research-only/holdout pipeline like everything else, and would need a precise, non-cherry-pickable definition of "Fair Value Gap" before backtesting.

- **Trend-structure-aware liquidity filter** — considered 2026-08-18, from a second YouTube Short (ICT/Smart Money Concepts style). Claims a meaningful difference between sweeping "interior" liquidity (swing highs/lows inside an established trend) versus sweeping the "protected high/low" (the structural point that, if broken, would flip the trend classification itself) — the former is framed as a normal stop-hunt-then-continuation, the latter as an actual reversal signal invalidating the setup. Points at a real gap in the current Level Sweep Reversal setup, which doesn't distinguish these two cases at all — it treats every prior-day/pre-market level sweep the same regardless of trend context. Genuinely specific and testable as a context filter (relates to the "volatility regime / trend-day vs range-day" filter idea already on the table), not just another generic pattern. Caveat: "swing high," "protected high," and "break of structure" have no single standard definition — programmatically defining them introduces new parameter choices that are themselves an overfitting risk (each definition choice is a knob that could get tuned until something looks good). Must go through the same research-only, holdout-respecting pipeline as everything else if tested — no fast-tracking because the theory sounds more rigorous.

- **research_ledger.py hypothesis ID gaps** — found 2026-08-24, while logging exp-023/024. **Closed 2026-09-07**: `_next_hypothesis_id()` now reads the highest numeric suffix among distinct hypothesis_id values already in the ledger (status updates reuse an id, never mint a fresh one) instead of counting total lines appended. Verified against a scratch ledger reproducing the exact gap scenario (a hypothesis with one status update followed by a fresh hypothesis correctly got hyp-000002, not hyp-000003). The real ledger file was not touched or rewritten -- this only changes how the NEXT id is computed going forward.

- **score_results.py's profit_factor unit mismatch** — found 2026-08-24, while reviewing exp-025. **Already closed 2026-09-01** (this backlog entry was stale): `score_results.py` now prints both the original raw-points profit factor and an R-multiple-normalized version side by side, with the R version called out as the one to prefer. Confirmed still present and correct on 2026-09-07.

- **research_ledger.py has no `search_batch_id` field** -- found 2026-09-03. **Closed 2026-09-07**: `HypothesisRecord` gained a `search_batch_id` field (optional, set by the calling script when multiple hypotheses come from one joint run); `larry_validate.py`'s `evaluate_candidate()` now tries an exact batch-based sibling count first and only falls back to lineage-walking when no batch id is set. `n_trials_override` still exists as a manual escape hatch. Verified with a scratch-ledger test: a 2-hypothesis batch with different immediate parents was correctly counted as 2, and a hypothesis with no batch id correctly fell through to the old lineage logic. Existing ledger rows (hyp-000007/hyp-000008 included) are untouched and keep using their documented `n_trials_override` -- this is additive, not a retroactive rewrite.

## Tested / Closed

- **2026-09-08: Volatility-conditioned position sizing added
  (position_size_multiplier() in src/volatility_conditioning.py) --
  not a hypothesis test, a usable tool.** Per the staff-meeting
  conclusion (Claude, Path-to-Profitability Advisor, and Market Behavior
  Advisor all converged): stop hunting new directional bar patterns for
  now (confirmed exhausted at both daily and 60-min resolution this
  session -- 65+ hypotheses, 0 directional survivors), and make the two
  confirmed volatility facts usable instead. Pure risk-management
  transform (inverse volatility sizing): bigger size on days expected
  quieter, smaller size on days expected wider, so expected dollar risk
  per trade stays roughly constant. Fed directly from the existing
  get_volatility_conditioning() output, clipped to [0.5x, 1.5x] so a
  stacked condition can't push size to an extreme. NOT a return claim,
  not subject to the 90%-CI promotion bar -- only answers "how many
  contracts," never "should I take this trade." Its real economic value
  is untested (no promoted directional signal exists yet to size).
  Wiring this into real order sizing needs the execution-infrastructure
  decision (Tradovate account/webhook, a $-spend track) -- parked,
  separate from this. Full detail:
  research/studies/volatility-position-sizing-spec.md.


- **2026-09-08: exp-094 through exp-099, bar-behavior batches 1+2 re-tested
  at 60-minute intraday resolution -- ALL 6 REJECTED.** Same 6 mechanisms
  (bearish/bullish rejection wick, failed breakout continuation, bullish/
  bearish engulfing, three-bar directional sequence) that failed at daily
  resolution in batches 1 and 2, re-run unmodified except for the bar unit
  (60-min RTH bars instead of daily), to isolate whether the DAILY
  timeframe itself -- not the pattern ideas -- was why nothing survived.
  All 6 came back null, well-powered (n=797 to 2802, all far above the
  40-trade prospective-test threshold, no thin-sample caveats):
  exp-094 n=1211 ci_90=(-0.00034,0.00011); exp-095 n=1217
  ci_90=(-0.00020,0.00022); exp-096 n=985 ci_90=(-0.00004,0.00046);
  exp-097 n=884 ci_90=(-0.00039,0.00024); exp-098 n=797
  ci_90=(-0.00015,0.00043); exp-099 n=2802 ci_90=(-0.00009,0.00022).
  Per the pre-committed interpretation in
  research/studies/bar-behavior-intraday-batch-spec.md: this is the
  daily-timeframe-efficiency checkpoint resolving in the "it's not just
  the daily timeframe" direction -- the same 6 candle/bar-pattern shapes
  fail identically at both daily and hourly resolution, on a 6.5x more
  granular dataset with no lookback-window handicap. Combined with the 8
  prior directional bar/candle hypotheses (batches 1+2, wicks, breakout,
  engulfing, sequences) and the COT-positioning line's Discovery-to-
  Validation reversal, the project now stands at roughly 65+ tested
  hypotheses with 0 directional signals surviving to Validation, and the
  bar-pattern search specifically (not just at daily granularity) appears
  exhausted. The 2 confirmed facts (range-contraction, overnight coil)
  remain volatility-conditioning facts, not directional edges. Ledger:
  hyp-000066 through hyp-000071, search_batch_id
  batch-2026-09-08-bar-behavior-intraday. Full detail:
  research/studies/bar-behavior-intraday-batch-spec.md.


- **2026-09-08: exp-093, IB Breakout conditioned on "wide prior day" (Market
  Behavior Advisor's purpose-built pairing) -- REJECTED.** Mechanistically
  motivated (unlike the 3 earlier mean-reversion overlay screens): IB
  Breakout is a continuation setup that needs room to run, paired with the
  volatility-conditioning module's confirmed "above-average range expected"
  flag. 1709 IB Breakout signals on Discovery (of 2101 days scanned).
  Wide-prior-day trades: n=386, mean r_multiple_net=-0.0543. Rest: n=1323,
  mean=-0.0724. Diff=+0.0181, ci_90=(-0.0883, 0.1281), NOT credible -- no
  effect. Closes this specific pairing for good; IB Breakout itself was
  already closed standalone (hyp-000011). Ledger: parent_hypothesis_id
  hyp-000011. Full detail:
  research/studies/ib-breakout-volatility-conditioned-spec.md.


- **2026-09-08: Volatility Conditioning Module built (src/volatility_conditioning.py)
  -- not a hypothesis test, a usable tool.** Per Jason's direction after
  the COT-positioning line closed: stop generating new directional
  hypotheses for now, turn what's already confirmed into something
  usable, and keep the Market Behavior Advisor integrated with current
  work (its charter was extended accordingly -- see
  docs/MARKET_BEHAVIOR_ADVISOR.md's "Extension" section). Combines the
  project's only two Validation-confirmed findings (range-contraction,
  hyp-000046/048; overnight coil, hyp-000056/057) into one reusable
  `get_volatility_conditioning(date, frame)` function that returns an
  expected-range multiplier for any given day, using the honest
  Validation-slice numbers (not the larger Discovery-slice ones). Not
  itself a strategy and not subject to the 90%-CI promotion bar --
  it makes no P&L claim. Explicitly disclosed in its own docstring:
  predicts range, never direction; its economic value as a real
  sizing/stop-width input hasn't been demonstrated (the earlier
  overlay screens found no effect on the specific dead signals they
  tested); any future strategy that wants to use this as a real input
  needs its own frozen spec and its own test. Full detail:
  research/studies/volatility-conditioning-module-spec.md.


- **2026-09-08: CFTC COT positioning, full Discovery + Validation
  prospective test -- strongest-ever Discovery result FAILED
  Validation (exp-091/092, hyp-000063). Closed.** Follow-up to exp-044
  (COT positioning, Step1 fail on a thin 2015-2018-only partial
  window). Jason manually downloaded the CFTC's own official 2019-2023
  TFF archive files (network-blocked from both sandbox and device) to
  extend the same frozen method to the full Discovery window.
  DISCOVERY RESULT (exp-091): n=350 weeks, both Step 1 and Step 2
  (costed) passed cleanly -- mean net pnl +20.10 pts/week, ci_90=(1.48,
  39.83), economically meaningful. The best Discovery-stage result in
  the project's history. VALIDATION PROSPECTIVE TEST (exp-092, single
  pre-registered test, unmodified method): n=118 weeks (2021-10-04 to
  2023-12-22), mean net pnl FLIPPED to -48.95 pts/week, ci_90=(-116.02,
  16.82) -- not credible, not economically meaningful. FAILED. Per the
  no-retuning rule, closes the COT/Leveraged-Money-positioning line for
  good. This is the clearest illustration yet of the project's
  effect-size-inflation pattern: even the strongest, most well-powered
  Discovery pass on record did not survive out-of-sample testing.
  Full detail: research/studies/cot-positioning-full-discovery-spec.md,
  research/studies/cot-positioning-prospective-spec.md.


- **2026-09-08: Bar behavior batch 2 -- engulfing + three-bar sequence,
  all REJECTED (exp-088/089/090). Candle-pattern family now closed.**
  Second and final batch of the daily-bar candle patterns Jason asked
  for. Bullish engulfing (n=69) and bearish engulfing (n=71) both
  spanned zero; three-bar directional sequence tested as momentum-
  continuation (n=428, well-powered, genuinely different mechanism
  from the reversal-style conditions) also spanned zero. Combined with
  batch 1 (rejection wick, failed breakout -- both REJECTED), this
  closes out 5 distinct daily/bar-level directional mechanisms with 0
  survivors. Per the pre-committed trigger (Path-to-Profitability
  Advisor, agreed before this batch ran): this is the signal for a
  real "is NQ too efficient at this timeframe" conversation with
  Jason, not another quiet pivot to a 6th candidate family. Full
  detail: research/studies/bar-behavior-batch2-spec.md.


- **2026-09-08: Overlay screen 2 -- overnight coil + release-day
  magnitude on the 4 Level Sweep variants (exp-086/087) -- no
  credible effect, confirms structural blocker.** Same quick-screen
  technique as exp-077 (range-contraction), applied to the two newer
  confirmed volatility-conditioning facts: the overnight-coil finding
  (hyp-000056/057) and the long-standing CPI/NFP/FOMC release-day
  "moves more" magnitude finding (exp-039/040, confirmed years ago,
  never converted into a rule). Neither conditions the 4 already-
  closed Level Sweep Reversal variants' economics (all CIs span
  zero; the 2 "protected" variants skipped, too few trades). This is
  the THIRD overlay-screen attempt (range-contraction, coil,
  release-day) to come back empty. Conclusion: the real limitation
  isn't the conditioning facts -- it's that this project currently
  has no live/future directional signal for any of them to attach
  to. Converting a confirmed volatility fact into money requires a
  directional signal to condition, which the project doesn't
  currently have. Flagged as a real scoping decision for Jason
  (see "In Scoping" below), not resolved here. Full detail:
  research/studies/overlay-screen2-spec.md.


- **2026-09-08 (overnight, unattended): Intraday Behavior Batch 3 +
  prospective test (exp-083/084, exp-085) -- SURVIVED VALIDATION.**
  Final 2 of the Market Behavior Advisor's 5 original candidates.
  exp-083 (midday lull character -> afternoon re-engagement) found no
  credible Step-1 effect (n=1630, ci spans zero, hyp-000055) -- closed.
  exp-084 (overnight/Globex range compression, "pre-open coiling" ->
  that same day's own RTH range) found a real, well-powered (n=332)
  Step-1 effect: coiled overnight sessions are followed by a credibly
  SMALLER RTH range (ratio 0.78, ci_90 entirely below 1.0) --
  volatility-persistence, not the "coil precedes breakout" folklore
  (hyp-000056). Its single pre-registered Validation-slice prospective
  test PASSED (exp-085, n=103, ratio 0.89, ci_90=(0.830, 0.960),
  hyp-000057) -- the second finding in the whole project (after batch
  1's range-contraction) to survive real out-of-sample confirmation,
  and the first Market-Behavior-Advisor-sourced one. CAVEAT: this is a
  volatility-conditioning characterization, not itself a directional
  return rule -- it does not by itself clear the promotion bar and
  needs translation into an actual tradeable use before further
  evaluation. Net across all 5 Market Behavior Advisor candidates
  (batches 2+3): 1 of 5 survived to Validation (overnight coil), 4 of 5
  closed (effort/absorption, base breakout too thin, trend-day shape,
  lull re-engagement). Full detail:
  research/studies/intraday-behavior-batch3-spec.md,
  research/studies/intraday-behavior-batch3-prospective-spec.md.

- **2026-09-08 (overnight, unattended): Intraday Behavior Batch 2 +
  prospective tests (exp-078/079/080, exp-081/082).** First batch
  sourced from the new Market Behavior Advisor role rather than Claude's
  own reasoning -- it proposed 5 trading-craft-reasoned candidates
  (effort-vs-result absorption, multi-day base-building, time-of-day
  lull/re-engagement, overnight-range coiling, trend-day first-hour
  shape), checked against the ledger for overlap; 3 were selected for
  this batch (the other 2 queued below, not dropped). RESULTS: exp-078
  (effort/absorption) found a real Step-1 differentiation -- absorbed
  ("stalled") effort bars showed a small credible reversal (hyp-000050),
  but FAILED its Validation-slice prospective test (n=15, too few
  instances in the smaller slice, hyp-000053) -- closed. exp-079
  (multi-day base breakout) technically cleared its CI but on n=9
  (hyp-000051) -- flagged as too thin to trust or even prospective-test,
  same caution as the project's exp-054 precedent; not tested further as
  designed. exp-080 (trend-day first-hour shape) found a real, well-
  powered (n=421) Step-1 effect in the "choppy" group -- opposite of
  what the trend-like group was expected to show (hyp-000052) -- but
  FAILED its Validation-slice prospective test with a sign flip
  (hyp-000054) -- closed. Net: 0 of 3 candidates survived out-of-sample
  confirmation, extending the project's pattern (now 2/2 intraday
  batches with a Discovery-PROMISING rate but 0% sustained Validation
  survival except the still-standing range-contraction finding from
  batch 1). Full detail: research/studies/intraday-behavior-batch2-spec.md,
  research/studies/intraday-behavior-batch2-prospective-spec.md.


- **2026-09-08 (overnight, unattended): Intraday Behavior Batch 2 +
  prospective tests (exp-078/079/080, exp-081/082).** First batch
  sourced from the new Market Behavior Advisor role rather than Claude's
  own reasoning -- it proposed 5 trading-craft-reasoned candidates
  (effort-vs-result absorption, multi-day base-building, time-of-day
  lull/re-engagement, overnight-range coiling, trend-day first-hour
  shape), checked against the ledger for overlap; 3 were selected for
  this batch (the other 2 queued below, not dropped). RESULTS: exp-078
  (effort/absorption) found a real Step-1 differentiation -- absorbed
  ("stalled") effort bars showed a small credible reversal (hyp-000050),
  but FAILED its Validation-slice prospective test (n=15, too few
  instances in the smaller slice, hyp-000053) -- closed. exp-079
  (multi-day base breakout) technically cleared its CI but on n=9
  (hyp-000051) -- flagged as too thin to trust or even prospective-test,
  same caution as the project's exp-054 precedent; not tested further as
  designed. exp-080 (trend-day first-hour shape) found a real, well-
  powered (n=421) Step-1 effect in the "choppy" group -- opposite of
  what the trend-like group was expected to show (hyp-000052) -- but
  FAILED its Validation-slice prospective test with a sign flip
  (hyp-000054) -- closed. Net: 0 of 3 candidates survived out-of-sample
  confirmation, extending the project's pattern (now 2/2 intraday
  batches with a Discovery-PROMISING rate but 0% sustained Validation
  survival except the still-standing range-contraction finding from
  batch 1). Full detail: research/studies/intraday-behavior-batch2-spec.md,
  research/studies/intraday-behavior-batch2-prospective-spec.md.


- **2026-09-08: Volatility-regime overlay quick screen (exp-077,
  hyp-000049).** Per Jason's direction ("try all the strategies, quick
  easy tests, don't over-exhaust it") -- reused the 4 Level Sweep
  Reversal variants' already-saved per-trade backtest files (only
  strategies with per-trade dated data on disk; others only have
  aggregate results and would need a real rerun, flagged not done) and
  joined trade dates to the range-contraction/volatility-persistence
  regime (hyp-000046/048). No credible conditioning effect in any of the
  3 testable variants (all CIs span zero). Does not reopen the 4 closed
  Level Sweep lines, and does not itself resolve whether the
  volatility-persistence finding has real economic value -- that still
  needs a proper costed overlay design on a live/future signal.


- **2026-09-08: Intraday Behavior Batch 1 (exp-072/073/074) + prospective
  tests (exp-075/076).** First genuinely intraday-resolution (1-min bar)
  characterization batch, per Jason's "professional systematic trader"
  framing. 3 pre-registered conditions (search_batch_id
  batch-2026-09-08-intraday-behavior-1), checked against the ledger first
  to avoid re-mining already-tested ground (opening-range/IB breakout,
  VWAP mean reversion, and gap-fill were all excluded as already tested).
  RESULTS: exp-072 (volume-profile skew, front/back-loaded volume days)
  Step 1 PASS on Discovery (hyp-000044) but FAILED its Validation-slice
  prospective test with both buckets flipping sign (hyp-000047) --
  closed, was noise. exp-073 (momentum-burst bars, 15-min continuation)
  Step 1 FAIL (hyp-000045) -- closed. exp-074 (range-contraction cycle --
  narrow/wide-range days vs. next-day range ratio) Step 1 PASS on
  Discovery in the PERSISTENCE direction, not the originally-predicted
  mean-reversion direction (hyp-000046), AND PASSED its Validation-slice
  prospective test, same direction both times though effect size shrank
  ~3-5x (hyp-000048). **This is the first hypothesis in the project's
  48-hypothesis history to survive a Validation-slice prospective test.**
  Advisor's independent read (obtained same day): almost certainly
  ordinary, well-documented volatility clustering/GARCH-type
  autocorrelation, not a proprietary NQ discovery -- real and replicated,
  but the shrinkage from Discovery to Validation should temper
  expectations heavily for whether it survives costs. This is a
  range/volatility-level characterization, NOT a costed P&L rule --
  economic-meaningfulness leg of the promotion bar has not been tested.
  Advisor's recommended next step: a position-sizing/stop-target-width
  overlay on an existing directional signal (lower complexity, doesn't
  require inventing a new directional edge) rather than a standalone
  breakout-width rule. STATUS: flagged to Jason as a real statistical
  milestone worth knowing about, explicitly NOT framed as a found edge --
  next step (designing the concrete costed overlay) is a scoping
  judgment call awaiting his sign-off before any implementation.
  Effect-size-inflation diagnostic (research/studies/effect-size-inflation-diagnostic-2026-09-08.md,
  process artifact, no ledger entry) also completed same day per Jason's
  decision to continue it -- found all 4 prior Discovery-PROMISING ->
  Validation-REJECTED pairs showed the same shape (narrow Discovery CI
  that didn't hold precision out of sample), supporting the Advisor's
  "methodology, not just data ceiling" read of the original 0/43 result.

- **exp-071 (2026-09-08): Daily volume level as a standalone next-day signal -- REJECTED.** First test of TOTAL daily volume (distinct from the earlier breakout-bar volume check, exp-030, already closed) against next-day return, testing both directions honestly with no predicted sign pinned in advance. No credible effect either way (hyp-000043). Consistent with the meta-review's pattern -- every standalone daily-resolution dimension tried so far (price, volatility, cross-market, options, bar-behavior, volume) has come back null or failed to replicate.
- **exp-070 (2026-09-08): Ensemble v2, real-move-magnitude feature -- REJECTED, closed.** Second attempt at combining features into one model (v1 = exp-046). Swapped the coarse CPI/NFP flag for an actual magnitude feature (built free, from existing price data), per the Advisor's fix to v1's sparse-dummy issue. Landed in an almost identical dead spot as v1: AUC 0.4936, everything zeroed by regularization, both halves exactly a coin flip (hyp-000042). Confirms exp-063's direct finding that this magnitude effect isn't real. Closes the ensemble idea for a second time -- no further variants without a genuinely new ingredient.
- **exp-069 (2026-09-08): Momentum-continuation prospective test -- FAIL, closed.** Since exp-066/068's opposite-direction finding was only visible after looking at Discovery results, re-testing it honestly required fresh (Validation-slice) data rather than re-signing the same Discovery numbers (which would have been a guaranteed, meaningless pass). Neither condition replicated out of sample (hyp-000040/041) -- both CIs span zero. Closes the entire bar-behavior batch 1 line for good, no retuning. Confirms the original Discovery-stage finding was very likely noise.
- **exp-066/067/068 (2026-09-08): First bar-behavior batch (wick rejections, failed breakout) -- 2 of 3 REJECTED-as-predicted but showing a real opposite-direction signal.** Under the new mission redirection (market behavior -> condition -> strategy), pre-registered 3 candle/bar patterns as one batch (per Advisor guardrail against pattern-shotgunning). All 3 REJECTED for their predicted (reversal) direction, no retuning -- but 2 of 3 (rejection wick at resistance, failed-breakout day) independently showed a statistically credible effect in the OPPOSITE direction: continuation/momentum, not reversal. Disclosed, not silently adopted as a pass (hyp-000037/038/039). Advisor reviewed for lookahead bugs (none found) and confirmed a fresh, separately pre-registered continuation hypothesis is the honest next step, not a re-sign of this result. Flagged to Jason since it clears the 90% bar, even though technically filed as REJECTED.
- **exp-063 (2026-09-08): Options-implied vs realized move on CPI/NFP days -- NO CREDIBLE EFFECT, closed.** Bought real NQ options trade data ($1.92) to test the variance-risk-premium idea properly (implied moves historically overstate what actually happens on event days, per outside research). Built the straddle-vs-realized comparison, caught and fixed two real construction bugs before looking at any result (contract rollover timing, and a mismatched time horizon), verified the strike-parsing with a put-call-parity check. Event days and ordinary days both show a wide, zero-spanning range -- no credible gap either way (hyp-000036). This closes out the options/vol angle entirely, on top of the earlier VXN-based checks. Alt-data avenues scoped so far (vol, cross-market, options) are all now closed or parked; next is a fresh gameplan review on what's left to try.
- **exp-062 (2026-09-07): ZN bond-lead signal, real prospective test -- FAIL, closed.** Extended the ZN bond data through the Validation period ($3.68, small paid fetch) to properly test the one promising candidate from earlier. Didn't hold up on fresh data -- wide range, spans zero. This closes the ZN/bonds line for good; no retuning (hyp-000035).
- **exp-063, 064, 065 (2026-09-07): Currency (6E), Oil (CL), and 3-day bond move -- all REJECTED.** Rounded out the cross-market search: same-day currency and oil moves don't predict NQ's next day (hyp-000032, hyp-000033); a slower 3-day bond-move version of the ZN idea also doesn't (hyp-000034). The free, already-owned data for this branch is now used up -- ZN same-day (exp-061) remains the one live candidate, still parked pending the small data purchase.
- **exp-061 (2026-09-07): ZN (10Y Treasury) same-day move as a next-day NQ signal -- PROMISING, Step 1 only, NOT yet trusted.** First cross-market candidate under the new alt-data gameplan. Simple, single-instrument test (not a repeat of the earlier 4-instrument portfolio tests, which were rejected): NQ returns more the day after ZN closes up than after ZN closes down. Statistically clears the bar on Discovery data (hyp-000031). Per standing rule: needs a real costed trading rule + one prospective test on fresh data + Advisor sign-off before this means anything. Paused here for review, not proceeding to Step 2 automatically.
- **exp-060 (2026-09-07): VXN 5-day rate of change as a signal -- REJECTED.** Tested whether fear building/draining fast (not just VXN's level) predicts next-day NQ direction. No credible effect (hyp-000030). Combined with exp-059's VXN-level failure, both VXN framings are now closed -- vol/options-based standalone signals via VXN are done as a line of inquiry.

- **exp-059: VXN level as a standalone predictive signal -- REJECTED**
  -- 2026-09-07, hyp-000029. First test of the strategic pivot agreed
  after the 2026-09-07 assessment (58 experiments in, mostly price/
  time patterns, both Claude and the Advisor recommended trying a
  genuinely different kind of data). VXN (the Nasdaq options market's
  own fear gauge) was already on hand for free but had only ever been
  used to check whether OTHER findings were priced in, never tested as
  its own signal. Step 1 (statistical only, no costs): does NQ's
  next-day return differ after an unusually calm vs unusually fearful
  prior VXN close? Result: n=301 calm days, n=629 fearful days, 90% CI
  on the difference (-0.002132, 0.000292) -- spans zero. VXN's raw
  level alone carries no next-day directional signal. Closed; no
  costed rule was built. See the ledger (hyp-000029) for full detail.

- **exp-058: Prospective validation of exp-057's high-volatility candidate --
  REJECTED** -- 2026-09-07, hyp-000028. Pre-registered single test of exp-057's
  one candidate (Initial Balance Breakout doing worse than its own average on
  high-volatility days), on the Validation slice only. Result: n=259 trades,
  mean R-multiple -0.0746 (still negative), 90% CI [-0.1910, 0.0433] spans zero
  -- fails both the statistical-credibility and economic-meaningfulness legs.
  exp-057's finding does not replicate out of sample; treated as noise from the
  pilot, not a real effect. Line closed per the pre-registered rule: no
  retuning of the volatility threshold. See the ledger (hyp-000027,
  hyp-000028) for full detail.

- **exp-057: Intraday collective-evidence pilot (Level Sweep x2, IB
  Breakout, Fade the Gap)** -- 2026-09-07, hyp-000027. Follow-on to
  exp-055/056 after Jason asked what's next and Claude/Advisor agreed
  to point the collective-evidence machinery at the deferred intraday
  condition variables instead of expanding to the full 49-strategy
  library. Ran on 4 intraday lenses -- 2 correlated Level Sweep exit
  variants plus 2 genuinely independent setups (Initial Balance
  Breakout, Fade the Gap), all reporting net R-multiples. 3 of 4
  conditions from the original brainstorm were testable (volatility
  regime, prior-day direction, opening-range width); time-of-day was
  dropped when the data couldn't honestly support it across all 4
  lenses (disclosed in the run notes, not silently dropped). All 8
  buckets cleared the pre-registered eligibility floor (>=30 distinct
  days, >=3 of 4 lenses with >=10 trades). One mechanically-selected
  candidate: high-volatility days show lenses collectively
  underperforming their own baseline (n=701 days, 90% CI [0.4372,
  0.4848], entirely below the 0.5 no-effect line). Exploratory only,
  same rule as exp-055 -- next step is a single pre-registered
  prospective test on the Validation slice before this is trusted.
  See `research/studies/intraday-collective-evidence-pilot-scoping.md`
  and the ledger (hyp-000027) for full detail.

- **exp-055/056: Collective-evidence pilot (trend family) + prospective
  validation** -- exp-055 (2026-09-07, hyp-000025) piloted the new
  cross-strategy, week-first aggregation machinery Jason proposed
  (strategies as lenses, conditions pre-registered, aggregate by week
  before by lens) on the trend family's 4 correlated variants
  (exp-047/048/049/051) -- explicitly a dry run of the machinery, not a
  test of independent corroboration, since all 4 lenses share one
  underlying signal. Of 11 pre-registered (condition, value) buckets,
  one stood out: `distance_from_52wk_ma = low` (near-MA / weak-trend
  weeks), n=42 distinct weeks, mean fraction of lenses beating their
  own baseline = 0.268, 90% CI [0.185, 0.357] -- entirely below 0.5.
  Logged as PROMISING (exploratory only, per the pilot's own frozen
  promotion rule) and immediately taken to a single pre-registered
  prospective test, exp-056 (2026-09-07, hyp-000026): does excluding
  weak-trend weeks improve exp-047's own raw signal, evaluated ONLY on
  the Validation slice (2021-10-04 -> 2024-01-03), signal computed
  continuously across Discovery+Validation for warm-up continuity.
  Result: FAIL. n=54 weeks, mean +76.21 pts/week, but 90% CI
  [-6.32, +156.20] still crosses zero -- does not clear the
  statistical-credibility bar. exp-055's finding does not replicate
  out of sample; treated as noise from the correlated-lens pilot, not
  a real effect. This filtered-signal line is closed per the
  pre-registered rule: no retuning of the distance threshold or
  lookback window. See
  `research/studies/collective-evidence-pilot-scoping.md` and the
  ledger (hyp-000025, hyp-000026) for full detail.

- **exp-051: Cross-asset diversified test of the weekly trend signal**
  -- tested 2026-09-07, once ZN/6E/CL data was purchased ($19.14
  total). Result: kill (hyp-000021). Mean weekly portfolio net return
  was positive (+0.0003/week, inverse-vol-weighted across NQ/ZN/6E/CL)
  but the 90% confidence interval crossed zero, so it doesn't clear
  the statistical-credibility gate. Per the pre-registered follow-up
  plan (frozen spec Section 11), this is a clean kill, not followed by
  parameter variants on this same construction. A real bug was found
  and fixed during this run: WTI crude legitimately traded negative on
  2020-04-20/21 (the well-known May-2020 contract expiry event), which
  broke the log-return math and silently produced a NaN "kill" on the
  first pass -- fixed as a general validity guard (non-positive
  reference close treated as no usable close), re-run once, real
  result recorded. See `research/studies/cross-asset-weekly-trend-scoping.md`
  and the ledger (hyp-000021) for full detail.

- **exp-052: Cross-asset short-term weekly reversal (Step 1, raw
  unfiltered)** -- tested 2026-09-07, first genuinely new signal
  family in this project (distinct from exp-047/051's 52-week trend
  family and from exp-034's intraday VWAP-reversion family). Signal:
  bet against last week's own return, same NQ/ZN/6E/CL basket and
  portfolio construction as exp-051. Result: kill (hyp-000022). Mean
  weekly portfolio net return was essentially flat (+0.0000356/week),
  90% CI [-0.000612, +0.000652] spans zero and also fails the
  economic-meaningfulness gate outright -- not a near-miss like
  exp-047, no signal at all. First/second-half split flips sign
  (+0.000457 vs -0.000383), confirming genuine instability rather than
  a borderline case. Step 2 (calm-week volatility-percentile filter)
  was pre-specified but gated behind a Step 1 pass, per the frozen
  spec -- since Step 1 did not clear the bar, Step 2 was not run. Part
  of the 2026-09-07 multi-signal-family round Jason asked for (test
  several different signal types across the same basket); this is the
  first installment. See
  `research/studies/cross-asset-short-term-reversal-scoping.md` and
  the ledger (hyp-000022) for full detail.

## Shelved

- **Weekly trend-following signal family on NQ (exp-047, exp-048, exp-049)** -- shelved
  2026-09-06 per a pre-committed rule. exp-047 (raw weekly momentum sign) was this
  project's closest-ever near-miss (mean +19.38 pts/week, 90% CI [-1.165, +40.414]).
  Two follow-on risk-management overlays were tested at Jason's request: exp-048 (a
  hard +2R take-profit cap) and exp-049 (a 1R trailing stop activated at +2R) --
  both came back kills with nearly identical means (~+10.2-10.5 pts/week, both CIs
  spanning zero), roughly half the raw signal's mean, because both overlay designs
  remove the small number of large trending weeks that drive this signal's edge.
  Per the frozen spec's pre-commitment (named before either follow-on result
  existed), two follow-on attempts on the same near-miss without a clear,
  comfortable pass is the stopping point -- not followed by further parameter
  variants (e.g. a wider trail distance), which would be a post-hoc search for the
  variant that clears the bar. Revisit only via an entirely new, independently
  pre-registered hypothesis (a materially different design, or a prospective test
  on new future data) -- not a continuation of this family.

## Rejected

- **Order-flow / buying-vs-selling-pressure signals** -- closed out 2026-09-07
  at Jason's explicit request (drop it entirely, don't keep bringing it up).
  Previously parked 2026-09-03 after being priced out at ~$54,000/year for the
  historical depth this project's methodology needs (see git history / prior
  versions of this file for the full pricing detail). Moved from Parked to
  here, not just left sitting -- Jason wants this off the list of things that
  keep resurfacing as an option, not merely deprioritized.
