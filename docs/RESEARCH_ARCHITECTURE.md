NQ Research Platform — Strategic Direction & Next-Phase Instructions

Purpose of this instruction

The ultimate objective of this project is not simply to build a TradingView alert for the current Level Sweep Reversal setup.
The ultimate objective is to build a research-driven NQ futures trading system that can:

1. Discover and evaluate potentially profitable trading setups.
2. Test those setups against high-quality historical market data.
3. Determine whether an observed edge is statistically credible and robust.
4. Test strategies on unseen/out-of-sample data.
5. Account realistically for commissions, slippage, spread, missed fills, and other trading costs.
6. Identify the exact market conditions in which a strategy works or fails.
7. Produce a clear, actionable trade signal when a sufficiently validated setup occurs.
8. Eventually support human-approved trade execution.
9. Never represent an unproven strategy as a profitable strategy.

The current Level Sweep Reversal is one candidate strategy, not the assumed final strategy.

Critical strategic correction

Do not optimize the entire project around the current Level Sweep Reversal simply because it is currently the best-performing setup tested.

The current results are:
- ORB: approximately -0.062R expectancy.
- Level Sweep Reversal / close_any: approximately -0.063R.
- Level Sweep Reversal / close_min_distance: approximately +0.043R.
- Level Sweep Reversal / full_bar_range: approximately +0.042R.

The two positive variants have not yet demonstrated statistical significance.
Therefore: +0.043R does not mean we found a profitable strategy.
Treat these variants as research candidates.
The system must remain capable of testing completely different strategies and combinations of market conditions without requiring the project architecture to be rebuilt.

The desired end state

The eventual user experience should be something approximately like:

"NQ is currently meeting the conditions for Strategy X.
Direction: Short
Entry: 23,XXX
Stop: 23,XXX
Target: 23,XXX
Expected risk/reward: X.XR
Historical expectancy for this setup under these conditions: X.XXR
Sample size: XXXX trades
Out-of-sample expectancy: X.XXR
Statistical confidence: [appropriate metric]
Current market conditions: [description]
Signal quality: [validated / experimental]
No trade should be taken unless the strategy passes the project's validation requirements."

That is the direction we are building toward.

Architecture the project should move toward

Think of the system as six layers.

Layer 1 — Market Data
Greg should maintain reliable historical and current NQ data.
The data layer should eventually support:
- 1-minute bars
- Higher timeframe bars derived from raw data
- Session information
- New York time
- 8:30 AM market-open context
- Previous day high/low
- Overnight high/low
- Previous session close
- Opening range
- Volatility measures
- Volume where available
- VWAP where appropriate
- ATR
- Trend information
- Market structure information
- Economic/news-event timestamps if reliable data is available

Do not add indicators simply because they are popular.
Every feature should have a research reason for existing.

Layer 2 — Feature / Market Context Engine
Build a reusable feature engine that can describe what the market looks like at the moment a potential trade occurs.
Examples:
- Distance from previous day high/low
- Distance from overnight high/low
- Opening range size
- ATR
- Relative volatility
- Trend direction
- Recent momentum
- Volume conditions
- VWAP relationship
- Time since market open
- Day of week
- Major economic event proximity
- Whether price is inside/outside a predefined range
- Whether a level has been tested previously
- Number of consecutive directional candles
- Recent swing highs/lows

The important principle is: Features should be stored independently from strategies.
That allows future strategies to reuse the same market information.

Layer 3 — Strategy Research Engine
This is the most important next phase.
Larry should be capable of testing multiple strategy families rather than only the current Level Sweep Reversal.
Candidate categories should include, at minimum:
- Opening Range Breakout
- Opening Range Reversal
- Liquidity/level sweep reversal
- Previous-day high/low reactions
- Overnight high/low reactions
- VWAP reversion
- Momentum/breakout continuation
- Mean reversion
- Trend continuation
- Failed breakout setups
- Market structure breaks
- Volatility expansion/contraction setups

Do NOT assume any of these are profitable. They are candidate hypotheses to investigate.

For every candidate strategy, define:
- Exact entry conditions
- Exact entry price methodology
- Exact stop methodology
- Exact target methodology
- Position sizing assumptions
- Maximum holding time
- Session/time restrictions
- Conditions that invalidate the setup
- Cost assumptions
- Slippage assumptions
- Trade management rules

No vague rules such as: "Price looks strong." "Market is trending." "Level looks important."
Every rule must eventually be convertible into an objective, testable condition.

Strategy discovery

The system should eventually allow us to ask: "What recurring NQ market conditions appear to produce positive expectancy?"
This does NOT mean blindly running thousands of indicators and selecting whatever produces the highest backtest. That would create a serious overfitting/data-mining problem.
Instead, research should proceed through hypothesis-driven testing.

For example:
Hypothesis: "When NQ sweeps a significant overnight high during the first 30 minutes after the 8:30 AM New York open and then closes back below that level, price has a tendency to reverse."
Then define the hypothesis mathematically, test it, and record the result.

The system should maintain a research registry containing:
- Hypothesis
- Strategy version
- Exact rules
- Data period
- Number of trades
- Expectancy
- Profit factor
- Win rate
- Average winner
- Average loser
- Maximum drawdown
- Sharpe/Sortino where appropriate
- Distribution of returns
- Costs
- Slippage
- Statistical tests
- Out-of-sample results
- Stress-test results
- Final status

Validation requirements

A strategy should not be considered "proven" simply because it produces positive backtest results.
Before a strategy can be classified as production-ready, it should pass progressively stronger validation.
At minimum investigate:
1. In-sample testing
2. Out-of-sample testing
3. Walk-forward testing
4. Bootstrap/resampling analysis
5. Parameter sensitivity
6. Cost/slippage stress testing
7. Different market regimes
8. Different days of week
9. Different times of day
10. Drawdown analysis
11. Trade distribution analysis
12. Comparison against a reasonable null/random baseline

The system should specifically detect whether a strategy's profitability depends on one narrow parameter choice.
For example, if a strategy works only with a 7-minute opening range but fails at 6 or 8 minutes, that should be flagged as potential overfitting.
Likewise, if a strategy only works during one tiny historical period, it should be flagged.

Avoiding overfitting

This is a core project requirement.
Do not repeatedly modify a strategy until the historical data looks good.
Every experiment must be versioned and logged. Do not overwrite failed experiments.
The system should make it difficult to accidentally "research the answer" by repeatedly tuning parameters against the same dataset.
Whenever practical, maintain a portion of data that is not touched during strategy development and reserve it for final validation.

Strategy scoring

Do not rank strategies based solely on win rate.
The primary objective is risk-adjusted expectancy and robustness.
Create a standardized strategy scorecard that considers factors such as:
- Expectancy per trade
- Profit factor
- Maximum drawdown
- Sample size
- Statistical confidence
- Out-of-sample performance
- Walk-forward stability
- Parameter robustness
- Cost sensitivity
- Regime stability

Do not create an arbitrary composite score without documenting exactly how it is calculated.
If a strategy has insufficient evidence, label it: INSUFFICIENT EVIDENCE, rather than forcing it into a winner/loser classification.

Tony — live signal layer

Tony should continue being developed, but he must remain explicitly experimental.
Tony's job is: Detect conditions.
Tony is NOT currently responsible for proving profitability.
Tony should never imply: "This is a profitable trade."
Instead, the alert should communicate something like: "Experimental Strategy Signal Detected" and include:
- Strategy name/version
- Timestamp
- Direction
- Entry
- Stop
- Target
- Risk/reward
- Relevant market context
- Validation status
- Historical sample size
- Historical expectancy
- Whether the signal is inside or outside the strategy's validated conditions

This creates a clean separation between research and live signaling.

Future execution layer

Eventually the project may support: Signal → Jason reviews → Jason approves → trade executes.
Do NOT build autonomous execution yet.
Any future execution layer must have explicit safeguards including:
- Human approval
- Maximum daily loss
- Maximum position size
- Maximum number of trades
- Kill switch
- Duplicate-order prevention
- Connection failure handling
- Data-quality checks
- Order confirmation
- Position reconciliation
- Emergency shutdown

The project should never silently transition from alerts into autonomous real-money trading.

Trading strategy research

Jason does not have enough trading experience to independently generate a large library of high-quality strategy hypotheses.
Therefore, the project should support importing strategy ideas from:
- Trading education
- Research papers
- Documented trading methodologies
- Trading videos
- Books
- Market microstructure research
- Other credible sources

However: A strategy source is a hypothesis, not evidence of profitability.
If Jason provides a trading video, extract the strategy into objective rules first. Then test the rules.
Do not assume the creator's claimed win rate or profitability is accurate.

Immediate next steps

Before continuing to expand Tony, perform an architecture/research review.
Answer these questions:
1. Does the current codebase support adding multiple independent strategies without major restructuring?
2. Is there a reusable market-feature engine?
3. Is there a formal experiment registry?
4. Are all strategy versions being preserved?
5. Is there a clean separation between training/in-sample and out-of-sample data?
6. Can Larry perform walk-forward testing?
7. Can Larry perform parameter sensitivity testing?
8. Can Larry perform realistic transaction-cost and slippage testing?
9. Can we compare strategies using the same standardized metrics?
10. Can Tony consume signals from any validated strategy rather than being hard-coded to Level Sweep Reversal?
11. Can new strategy hypotheses be added without rewriting the entire system?
12. Can we eventually run paper trading using the exact same signal logic that would be used for live trading?

If any answer is "no," prioritize fixing the architecture before adding more strategy-specific features.

Research roadmap

Proceed in this general order:

Phase 1 — Foundation
Complete and verify: Reliable NQ data, Feature engine, Experiment registry, Versioned strategy definitions, Standardized backtesting, Cost/slippage model

Phase 2 — Research
Build a small library of objectively defined candidate strategies. Test them using the same methodology. Do not optimize them aggressively. The goal is to discover whether meaningful edges exist.

Phase 3 — Validation
For candidates showing promise: Out-of-sample testing, Walk-forward testing, Stress testing, Parameter robustness, Regime analysis, Statistical analysis

Phase 4 — Paper trading
Only strategies that survive validation should move into paper trading.
Compare: Backtest results, Real-time signals, Actual theoretical fills, Slippage, Missed signals, Execution timing

Phase 5 — Human-approved live trading
Only after sufficient paper-trading evidence should the system be considered for real-money use. Jason must explicitly approve each trade.

Phase 6 — Potential automation
Only after the system has demonstrated robust performance should autonomous execution even be considered. That is a future phase, not a current requirement.

Current Level Sweep Reversal

Continue collecting data on: close_min_distance, full_bar_range
Do not declare either one the winner yet.
Tony may support both if technically useful, but label both as experimental.
The purpose of Tony at this stage is to validate the live signal workflow, not to generate trading profits.

Communication requirement

Jason is a beginner in both programming and systematic trading.
Whenever you make a significant architectural or research decision:
1. Explain what the decision means in plain English.
2. Explain why it matters.
3. Explain what could go wrong.
4. State what you recommend doing next.
5. Clearly distinguish facts from assumptions and hypotheses.

Do not ask Jason to make a technical decision unless his decision is actually necessary.
When a decision can be determined objectively through research or code inspection, determine it and explain the result instead.

Most important principle

The project is not trying to find a strategy that looks good on historical data.
It is trying to determine whether an actual, repeatable trading edge exists.
If the evidence says there is no edge, the correct outcome is: No trade.
If the evidence says there is an edge, the system must be able to demonstrate why we believe that edge is real, how robust it is, and under what conditions it works.
The system should optimize for truth and robustness, not for producing trades.

---

## Implementation status (maintained by Claude, most recent first)

**2026-08-16 — Recommendation #1 implemented: a real holdout slice now exists.**

Architecture review findings (from inspecting the actual codebase, not
assumptions) are recorded in this session's conversation log; the
headline finding was: every experiment run in this project so far has
tested against 100% of whatever real data existed at the time, and as
more data got pulled, the SAME variants were re-tested on a bigger
window each time. There was never a genuine out-of-sample check, and no
untouched data existed to eventually run one against.

Fixed by adding `src/data_holdout.py`, a shared module that draws a
fixed line in the current ~2-year Databento dataset
(`data/NQ_1min_databento_2026-08-16.csv`, 2024-08-15 through 2026-08-14,
625 trading days total):

- **Research data (usable for normal testing):** 2024-08-15 through
  2026-04-06 — 513 trading days (~82%).
- **Holdout data (untouched):** 2026-04-07 through 2026-08-14 — 112
  trading days (~18%), sitting inside the target 15-20% range.

Every script that loads real price data (`detect_setups.py`,
`detect_level_sweep.py`, `backtest.py`, `plot_open.py`,
`plot_setup_example.py`) now calls `apply_holdout_boundary()` right
after loading. By default this silently (well — loudly, via a printed
console message) drops any bars on/after 2026-04-07, so Larry's normal
detect → backtest → score → confidence_analysis pipeline only ever sees
research data. Touching the holdout requires deliberately setting the
`ALLOW_HOLDOUT_DATA=1` environment variable, which prints an
impossible-to-miss warning every time it's used. `dashboard.html` shows
the research/holdout day split on its data-coverage card as a status
inventory (this does not touch or "use" the holdout data, just reports
its date range).

**The holdout has NOT been used yet.** No strategy has been tested
against it. It stays untouched until a candidate strategy is judged
ready for the one-time final validation check described in this
document's Phase 3 — using it earlier than that, even "just to check,"
would burn the only genuinely unseen data this project has.

**2026-08-16 — Recommendations #2-4 implemented.**

- **#2, consolidated data loading:** `src/data_loader.py` is now the one
  place that finds/loads the active real data file (DST-safe timestamp
  parsing + holdout boundary included). `detect_setups.py`,
  `detect_level_sweep.py`, `backtest.py`, `plot_open.py`,
  `plot_setup_example.py`, and `generate_dashboard.py` all call it
  instead of each carrying its own copy. Verified by re-running every
  rewired script.
- **#3, structured experiment registry:** `research/experiments/_index.md`
  now has real columns — Setup, Variant, Sample Size, Win Rate,
  Expectancy, Profit Factor, Max Drawdown, Statistically Significant,
  Verdict — instead of prose that needed regex-scraping. All 18 existing
  rows were backfilled from each experiment's own write-up file (no
  values changed, no conclusions altered — this was a format upgrade,
  not a re-analysis); a couple of early cells are `-` where the original
  write-up didn't record profit factor/drawdown, rather than guessed.
  `generate_dashboard.py` was updated to read the new columns directly.
- **#4, formal significance check:** `confidence_analysis.py` now prints
  a direct `Statistically distinguishable from zero (90% bootstrap CI):
  YES/NO` line, computed from the same bootstrap interval it already
  built. Verified against exp-017's already-known-by-hand result
  (`close_min_distance`, 221 trades) — the script now independently
  reproduces "NO, CI -18.89R to +37.08R" without anyone reading
  percentiles by hand.

**2026-08-16 — the holdout mechanism already caught something real.**
Greg checked for new data since the last Databento pull (none was
available yet). Larry then re-tested `close_min_distance` and
`full_bar_range` — the first time either ran through the
holdout-respecting pipeline (all prior tests of these variants predate
`data_holdout.py` and unknowingly included the 112 days now set aside).
Result: `close_min_distance` flipped from +0.043R to **-0.014R**, and
`full_bar_range` shrank from +0.042R to **+0.008R** (roughly breakeven).
Logged as exp-019/020. This is exactly the kind of overfitting/regime-
dependency signal the holdout boundary exists to catch — a large chunk
of both variants' apparent "stabilizing" edge was concentrated in the
most recent ~4 months. Neither variant currently shows a research-only
edge worth acting on. See `research/setups/level-sweep-reversal.md` for
full detail.

**Still open from the architecture review** (not yet fixed, in rough
priority order): no feature engine (Layer 2 of the architecture — reusable
market-context columns like distance-from-PDH/PDL, ATR, VWAP, day-of-week,
independent of any one strategy); no walk-forward testing or automated
parameter-sensitivity sweep capability; no Sharpe/Sortino or regime/
day-of-week breakdowns in the standard metrics set; Tony does not exist
as code yet.
