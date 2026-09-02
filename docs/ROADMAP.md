# NQ Research Platform — Roadmap

This is the plain-English map of what we're building, in order. We will NOT
build all of this at once — each stage is its own mini-project that has to
work before we move to the next one. Skipping ahead is how most home-built
trading systems end up broken and untrustworthy.

## Phase 1 — Environment (today)
Get a working, repeatable way to pull NQ price data and look at it. No
strategy logic yet. Just "can we reliably get clean data for the 8:30 AM NY
open window."

## Phase 2 — Data Layer
A script/module whose only job is: given a date range, return clean OHLCV
(Open/High/Low/Close/Volume) bars for NQ, in New York time, with no gaps or
duplicate rows, saved to disk so we don't re-download every time. Everything
downstream depends on this being trustworthy. Garbage data in = garbage
backtest out, no matter how good the strategy logic is.

## Phase 3 — Setup Detection
Code that scans historical bars and flags "this looks like [pattern X]" —
e.g. a range breakout at the open, a failed auction, an opening drive, a
gap-and-go. This is where your trading knowledge gets turned into rules a
computer can check mechanically. We'll start with ONE setup, get it fully
working end-to-end through every later stage, then add more.

## Phase 4 — Backtesting Engine
Given: historical data + a setup-detection rule + entry/exit/stop rules.
Output: a list of every simulated trade it would have taken, with entry
price, exit price, P&L, and timestamps. This is the part that tells you
honestly whether an idea has an edge, not just whether it "looks good" on a
chart.

## Phase 5 — Scoring / Statistics
Turn the raw trade list from Phase 4 into numbers that matter: win rate,
average win vs average loss, expectancy, max drawdown, Sharpe-like ratio,
performance by day of week / by session / by market regime. This is what
lets you compare Setup A vs Setup B objectively instead of by gut feel.

## Phase 6 — Automation (future, only after Phases 1-5 are proven; expands into Phases 6-11 — see docs/AUTOMATION_ARCHITECTURE.md)
Only once a setup has survived rigorous backtesting and (ideally) a period
of paper trading do we talk about connecting this to a broker for live or
semi-live execution. This is the highest-risk stage (real money, real bugs
cost real dollars) so it comes last on purpose.

---

## Where we are right now

**Phase 1 is done:** we can generate/pull NQ minute data, and we produced
a first chart of the 8:30 AM NY open window (currently using synthetic
placeholder data, since the cloud sandbox used to build this can't reach
real market data sites — `src/data_fetch.py` is ready to pull the real
thing once run on a machine with normal internet access). The project is
also now under git version control, with setup instructions in
`README.md` for backing it up to GitHub and for continuing development
locally using Claude Code on a Mac.

**Phase 3 has a first working example:** Jason hadn't picked a specific
setup yet, so as a starting point (built the evening of 2026-08-15 with
Jason's go-ahead to make progress without him needing to be hands-on),
`src/detect_setups.py` implements a standard "Opening Range Breakout"
(ORB): the high/low of the first 15 minutes after 8:30 defines a range,
and a break above/below it within the next 60 minutes is the signal,
with a stop at the opposite side of the range and a 1x-range target.
`src/plot_setup_example.py` draws real example days showing the range,
entry, stop, and target on a chart. Both run against the synthetic data
for now.

**THIS IS A PLACEHOLDER, NOT NECESSARILY JASON'S ACTUAL SETUP.** The
parameters (15-min range, 60-min watch window, 1x-range target) were
picked as reasonable, well-documented defaults, not tuned or validated
in any way.

**Phases 4 and 5 also now have working first passes**, built the same
evening with Jason's explicit go-ahead to keep moving without him
needing to be hands-on:

- `src/backtest.py` — walks forward through the minute bars after each
  signal to see whether the stop or the target got hit first, and saves
  a trade-by-trade result log to `data/backtest_results.csv`. Caveat:
  the synthetic data only covers 6:00-11:00 AM each day, so a lot of
  trades (31 of 77 in the latest run) ran out of data before resolving
  either way — marked "unresolved" and excluded from scoring rather than
  guessed at. This should mostly resolve itself once real (full-session)
  data is used.
- `src/score_results.py` — turns the resolved trades into a scorecard
  (win rate, average win/loss in R-multiples, expectancy, profit factor,
  max drawdown) plus an equity curve chart.

**What the first synthetic-data run actually showed, and why that's a
GOOD sign, not a bad one:** the placeholder ORB setup came out
unprofitable on the synthetic data (37% win rate, expectancy -0.29R).
That's expected and correct — the synthetic data is just random noise
with no real intraday structure, so a real trading pattern SHOULD NOT
show an edge on it. Seeing a clean negative result here is actually a
sanity check that the backtest math itself isn't broken or secretly
biased toward showing fake wins. The real test only means something once
this same pipeline runs on real market data with Jason's actual setup.

**What's genuinely still needed from Jason before this can go further:**
1. His actual setup definition, to replace the ORB placeholder (or tune
   its parameters) with what he really watches for.
2. Real data — requires running on his own Mac (or connecting the
   desktop app) since this cloud sandbox can't reach market data sites.
3. A decision on position sizing / contract count once we're ready to
   turn R-multiples into real dollar figures — not needed yet.

Phases 6-11 (live automation) remain explicitly gated on Jason's direct,
in-the-moment approval each time — that boundary hasn't changed.

**Also added:** an automated test suite (`tests/`, run with `pytest`) that
checks the detection and backtest logic against small hand-built examples
with known-correct answers — 8 tests, all passing as of the last update.
This is pure engineering hygiene (doesn't need Jason's input) done while
waiting on the two items above.

**2026-08-16 additions — cost modeling + confidence ranges:**
`backtest.py` now subtracts an estimated commission + slippage cost from
every resolved trade (previously results were unrealistically frictionless
"gross" numbers) — see the cost assumptions documented at the top of that
file, which are generic placeholders, not Jason's real broker costs.
`score_results.py` now reports a rough 95% confidence interval on the win
rate instead of a bare number, so it's visible when a result is based on
too small a sample to trust. A new script, `confidence_analysis.py`,
bootstrap-resamples the trade results to show a realistic spread of
plausible outcomes (both "what if these same trades had landed in a
different order" and "what might the next 100 trades look like") instead
of presenting one backtest run as if it were the only possible outcome.
Logged as `research/experiments/exp-002-orb-synthetic-with-costs.md`,
without touching or overwriting exp-001, per the project's experiment
rules.

**2026-08-16 — first real setup defined: Level Sweep Reversal.** Built
from Jason describing what he wanted pulled from a video he shared (see
`research/raw/2026-08-16-video-reference-chart.md`) and making the
concrete calls on level selection and confirmation logic. Full definition
in `research/setups/level-sweep-reversal.md`. Detection code in
`src/detect_level_sweep.py`; `backtest.py`, `score_results.py`, and
`confidence_analysis.py` were generalized to accept a setup name so
multiple setups' results never overwrite each other. First test logged
as `exp-003` — unprofitable on synthetic data (expected/correct), with a
result shape (2.6% win rate, huge average winner) meaningfully different
from ORB's, a good sign the pipeline isn't just producing generic output.
The ORB placeholder is left in place, untouched, for comparison — not
retired.

**Where things stand now:** two setups (ORB placeholder, Level Sweep
Reversal real candidate), both fully wired through detect → backtest
(with costs) → score (with confidence range) → bootstrap analysis. Both
blocked on the same two things: real data (Jason's Mac) and, ideally,
more real-world refinement of Level Sweep Reversal's specifics once
Jason can watch it against real price action.

**2026-08-16 — first REAL data pulled, both setups re-tested.** Working
directly on Jason's own Mac (not the cloud sandbox), `src/data_fetch.py`
successfully pulled real NQ 1-minute bars from Yahoo Finance for the
first time. Along the way it fixed a bug: the script assumed Yahoo allows
59 days of 1-minute history in one request; Yahoo's real limit is 30 days
total, fetched in chunks of ~8 days per request. The script now loops
over 7-day windows and stitches them together — this got caught by
Yahoo's API returning a clear error, not by silently-wrong data, so
nothing bad slipped through. Also fixed: `score_results.py` and
`confidence_analysis.py` had a hardcoded "SYNTHETIC DATA" label in their
output regardless of what data was actually used; `backtest.py` now
records whether the data was real or synthetic in its results file, and
both scripts read that instead of assuming.

With ~24 trading days of real data (2026-07-19 through 2026-08-14), both
setups were re-run: ORB placeholder came out positive (63.2% win rate,
+0.206R expectancy, logged as `exp-004`) and Level Sweep Reversal came
out negative (7.7% win rate, -0.822R expectancy, logged as `exp-005`).
**Neither result should be treated as a real verdict yet** — both are
built on very small samples (19 and 13 resolved trades), and Level Sweep
Reversal in particular is still Claude's first-pass translation of
Jason's video reference into rules, not something Jason has validated
against real charts himself. The genuinely useful outcome today is that
the full pipeline (fetch → detect → backtest → score → confidence) now
runs cleanly end-to-end on real market data, with correct labeling.

**What's still needed from Jason:** review
`research/setups/level-sweep-reversal.md` against his own read of real
price action and flag anything the coded rules got wrong before that
setup's results mean anything. Real data will also keep accumulating
over time as `data_fetch.py` is re-run periodically (Yahoo only exposes a
rolling 30-day window per pull).

**2026-08-16 — Level Sweep Reversal reviewed against the video, target
rule fixed.** Walked through `research/setups/level-sweep-reversal.md`
piece by piece with Jason. He didn't have a strong enough feel to judge
most of it from experience, so left levels/watch-window/sweep-definition
unchanged. Two changes he did have evidence for or a clear preference on:

- **Target rule fixed.** Comparing the setup against
  `research/raw/2026-08-16-video-reference-chart.md` showed the original
  "target the opposite level" rule didn't match the video — that trade's
  real target was a modest ~1.35x-risk distance, not the far opposite
  level. Target rule changed to `entry ± 1.35 × risk` accordingly.
- **Reversal confirmation split into three variants** (`close_any`,
  `close_min_distance`, `full_bar_range`) instead of picking one, since
  Jason wanted to compare rather than guess from a single small backtest.

All three variants, re-run with the corrected target rule on the same
real ~24-day data, turned profitable (exp-006/007/008: +0.132R, +0.545R,
+0.238R expectancy respectively) — a sharp turnaround from exp-005's
-0.822R. This is encouraging but **not a verdict**: 15-16 trades per
variant is far too small a sample, and no variant has been chosen as "the"
setup — that comparison stays open until more real data accumulates.

**2026-08-16 — Databento added as a second, better real-data source; all
setups re-tested on 6 months instead of ~24 days.** Jason signed up for
Databento (a paid market data vendor) to get past Yahoo's ~30-day 1-minute
history limit. `src/data_fetch_databento.py` now pulls ~6 months of real
1-minute NQ futures bars from CME Globex's own feed (`GLBX.MDP3`,
continuous front-month `NQ.c.0`) — the API key is kept out of chat
entirely, read from an environment variable or a gitignored local file.
Every other script automatically prefers this data over the Yahoo file.

Loading this larger dataset surfaced a real bug: `pd.read_csv(...,
parse_dates=True)`, duplicated across 5 scripts, silently fails to parse
timestamps correctly when a file's date range crosses a Daylight Saving
Time change (mixed UTC offsets) — Yahoo's short pulls never crossed DST,
so this never showed up before. Fixed in all 5 places.

**The headline result: none of the small-sample findings from earlier
today held up well.** Re-run on ~6 months of Databento data (exp-009
through exp-012): ORB placeholder went from +0.206R (19 trades) to
-0.028R (125 trades) — essentially flat. All three Level Sweep Reversal
confirmation variants compressed sharply too — `close_any` flipped
negative (-0.052R), while `close_min_distance` and `full_bar_range`
stayed positive but barely (+0.054R and +0.033R, down from +0.545R and
+0.238R respectively). This is exactly the kind of thing the project's
confidence-interval/sample-size warnings exist to catch — the earlier
~15-20 trade results were, in hindsight, optimistic. Nothing here is
being treated as a final verdict, but it's an honest signal that Level
Sweep Reversal, as currently defined, may need more than confirmation-rule
tuning to find a real edge — worth a direct conversation with Jason about
next direction (rethink levels/watch window/entry timing, or move on to
a different setup idea).

**2026-08-16 — extended to 2 years of Databento data, after checking the
cost first.** Jason asked for a cost quote before pulling more data.
Databento's `metadata.get_cost()` endpoint (a free check, no data pulled)
priced 2 years of 1-minute NQ bars at ~$2.55 — trivial against his
reported ~$124 remaining balance. `data_fetch_databento.py`'s
`LOOKBACK_DAYS` was bumped from 182 to 730 and re-run: 698,873 rows,
August 2024 through August 2026.

Re-tested everything again (exp-013 through exp-016). ORB's negative
signal sharpened further (-0.062R at 493 trades, only 6.6% of simulations
profitable — now treated as settled, not worth further re-testing).
Level Sweep Reversal's `close_any` variant confirmed negative
(-0.063R at 237 trades). The notable result: `close_min_distance`
(+0.043R at 221 trades, was +0.054R at 63) and `full_bar_range` (+0.042R
at 197 trades, was +0.033R at 60) both **stabilized** instead of
continuing to shrink toward zero the way the earlier 24-day→6-month jump
did — the first sign either might reflect something real rather than
small-sample noise. Still not proof of a tradeable edge (a few
hundredths of an R per trade is thin, and this backtest doesn't model
real fills or discretionary judgment), but a more encouraging checkpoint
than 6 months alone gave.

**2026-08-16 — robustness-checked the two surviving Level Sweep variants
(exp-017/018).** Two follow-up questions on close_min_distance and
full_bar_range's 2-year results, before trusting the "stabilized" finding
above: are they statistically distinguishable from zero expectancy, and
do they survive higher trading costs? Answers: **not statistically
significant yet** (a 90% bootstrap confidence interval on total R spans
solidly negative to strongly positive for both — using
`confidence_analysis.py`'s existing bootstrap, no new code needed for
this part), and **survive a 2x cost stress test only barely** (both stay
positive but drop to roughly a quarter of their normal-cost expectancy).
`backtest.py` gained a `COST_STRESS_MULTIPLIER` environment variable for
this (defaults to 1.0/no change; a non-default value writes to a
separate `_stress<N>x` output file so it can never overwrite a normal
logged result). Honest read: neither variant has a confirmed edge yet —
promising enough to keep watching, not solid enough to act on.

**2026-08-16 — a real out-of-sample holdout was carved out, and it
changed the verdict on every tested variant.** Following strategic
guidance Jason adopted (`docs/RESEARCH_ARCHITECTURE.md`), an
architecture review found this project had never actually done
out-of-sample testing — every re-test (24 days → 6 months → 2 years)
re-ran the same variants on a strictly larger but still fully-visible
window. Fixed via `src/data_holdout.py`: a fixed line at 2026-04-07
splits the ~2-year Databento dataset into 513 research days (usable for
normal testing) and 112 holdout days (untouched, reserved for one future
final validation check). Every script that loads real price data now
excludes the holdout portion by default.

Re-testing `close_min_distance` and `full_bar_range` against the
research-only portion for the first time (exp-019/020) — the first time
either had ever run through a genuinely holdout-respecting pipeline —
made the picture materially worse: `close_min_distance` flipped negative
(+0.043R → **-0.014R**, 173 trades) and `full_bar_range` dropped to
essentially breakeven (+0.042R → **+0.008R**, 151 trades). Neither is
statistically distinguishable from zero (90% bootstrap CI spans zero for
both).

**Bottom line: all four tested variants — ORB, close_any,
close_min_distance, and full_bar_range — now show no statistically real
edge once tested with a proper holdout.** ORB and close_any were already
clearly negative before the holdout even mattered; close_min_distance
and full_bar_range looked encouraging on the full (holdout-contaminated)
2-year window but did not hold up once genuinely unseen-at-test-time
data was used. None of this rules out a real edge existing — the holdout
sample (112 days) is itself still fairly small, and this doesn't test
whether the underlying pattern needs a different definition entirely —
but nothing tested so far has cleared even the first real bar of
evidence.

**Also this session:** Tony's first Pine Script deliverables were built
(`pine/level_sweep_close_min_distance.pine`,
`pine/level_sweep_full_bar_range.pine`) — TradingView alert scripts that
detect the same conditions as the two Level Sweep variants, each firing
an alert explicitly labeled "Experimental Signal Detected — not a proven
edge" per the strategic doc's requirement that Tony detect conditions
without ever implying a signal is a proven profitable trade. These are
first-draft, hand-translated Pine Script that has not been run/compiled
in an actual TradingView environment yet (no Pine execution environment
is available to Claude) — verify in TradingView's Pine Editor and
sanity-check fired signals against the Python backtest results before
trusting any alert.

**2026-08-20 -- Research Integrity Protocol locked in, and a proper Discovery/Validation/Holdout split built.** Following an architecture review, `docs/RESEARCH_INTEGRITY_PROTOCOL.md` was written and its core decisions locked: the six-state Larry classification (REJECTED -> PROMISING -> VALIDATION CANDIDATE -> HOLDOUT PASSED -> FORWARD VALIDATION -> PAPER VERIFIED) became the official way to track how far a candidate has gotten, and the original 112-day holdout (2026-04-07 onward) was preserved as "Holdout Generation 1" rather than being touched or replaced.

The historical dataset was then extended back to 2015-01-01 (up from the ~2 years pulled in mid-August) and, once quality-checked, split by fixed calendar dates -- chronologically, not randomly, so nearby days can't leak information across the split -- into three pieces (`src/data_split.py`, wired in as of 2026-08-23): **Discovery** (2015-01-01 to 2021-10-03, ~60%, the only data any future idea-searching is allowed to see), **Validation** (2021-10-04 to 2024-01-03, ~20%, reserved for a one-time confirming re-test of a promoted candidate with its parameters frozen), and **Holdout Generation 2** (2024-01-04 to 2026-04-06, ~20%, a second sealed reserve, separate from and in addition to Generation 1). Every one of these pieces stays untouched until a candidate has actually earned the right to see it -- nothing has advanced past Discovery yet.

**2026-08-23 -- the promotion bar (defined below) now explicitly gates Discovery data from the sealed holdout.** A setup has to clear, on Discovery data only: positive expectancy after realistic costs, at least 150 trades, and a 90% bootstrap confidence interval on expectancy that sits entirely above zero -- before it's even eligible to be checked against Generation 1 or Generation 2's sealed holdout data. Nothing has cleared this bar yet.

**2026-08-23 -- a tamper-evident hypothesis ledger now exists** (`research/ledger/hypotheses.jsonl`, written by `research_ledger.py`): every hypothesis tested gets an append-only entry recording its strategy name, where the idea came from, its exact parameters, which data slice it ran on, trade count, expectancy, profit factor, max drawdown, its current six-state status, whether it's authorized for live use (always "not authorized" so far -- separate from, and in addition to, the per-trade approval CLAUDE.md already requires), and free-text notes. Nothing is ever edited or deleted -- a status change (e.g. an early "PROMISING" read becoming "REJECTED" once the full write-up was done) is logged as a new line, not an overwrite, so the full history of how a verdict was reached stays visible. (One known cosmetic quirk, logged in `docs/BACKLOG.md`: hypothesis ID numbers count total lines written, not distinct hypotheses, so IDs have gaps -- not a data problem, just something to not mistake for a deleted record.) `src/larry_validate.py` was also sketched out this session, showing how Larry's formal Deflated Sharpe Ratio / Probability of Backtest Overfitting checks (via the third-party `purgedcv` library, verified against a synthetic test case before being trusted) will turn a hypothesis's results into a status update -- not wired in yet, but its thresholds were decided (DSR >= 0.90 AND PBO <= 0.25, both required, not either/or).

**2026-08-23/24 -- two more Level Sweep Reversal variants re-tested on the new Discovery slice, both still REJECTED.** `close_min_distance` and `full_bar_range` (the two variants that had looked "stabilized" back on 2026-08-16's 2-year window) were re-tested for the first time against the Discovery slice specifically -- the largest, cleanest sample either has ever seen. Both came back negative: `close_min_distance` at -0.038R over 461 trades (exp-023), `full_bar_range` at -0.083R over 558 trades (exp-024). (The third original variant, `close_any`, was not re-tested here -- it was already settled negative back on 2026-08-16, at -0.063R over 237 trades, before the Discovery split existed, and nothing since has given a reason to revisit it.)

**2026-08-24 -- a new idea, the Fair Value Gap (FVG) entry trigger, tested for the first time and REJECTED -- the project's first statistically decisive result.** Pulled from `docs/BACKLOG.md`, given a precise frozen definition (`research/setups/fvg-entry-trigger.md`) that swaps Level Sweep Reversal's "close back beyond the level" entry for a 3-candle Fair Value Gap pattern, then tested on 500 Discovery-slice trades (exp-025, `fvg_entry_close_any`). Result: -0.208R expectancy, and a 90% bootstrap confidence interval (-149.41R to -59.02R) that sits entirely below zero -- meaning "no real edge" isn't a plausible read of this result the way it still is for close_min_distance/full_bar_range. (A real zero-risk-signal bug was found and fixed in `src/detect_fvg_entry.py` before this result could be trusted -- see exp-025's write-up for detail.) Only one FVG variant (`close_any` confirmation) has been tested so far -- no second FVG experiment exists yet.

**2026-09-01 -- trend-structure liquidity filter built, unit-tested, and now tested against real Discovery-slice data -- REJECTED (does not clear the promotion bar).** During an unattended overnight session (Jason's explicit go-ahead to push forward without him present), the last untested `docs/BACKLOG.md` idea was given a frozen, precise definition (`research/setups/trend-structure-liquidity-filter.md`) and implemented (`src/trend_structure.py`, 11 new tests, full suite 34/34 passing) as a post-hoc filter that classifies each existing Level Sweep Reversal signal as sweeping a "protected" trend-structure point vs. an "interior" level -- built with an explicit no-lookahead confirmation lag so a swing point can never leak future price information into an earlier signal's classification. The real data file was found later that night on Jason's Mac (`/Users/jasona/Downloads/nq_research_platform`, the canonical copy with the actual Databento CSV) and the real Discovery-slice backtest ran against it. Because the naive day-by-day scan was too slow to fit this session's time limits over ~2.2M Discovery rows, a performance-only reimplementation of the outer loop (`fast_scan_all_days()`) was written and verified byte-identical to the original, unmodified `detect_level_sweep.py` functions on a 200-day check slice before being trusted for the full run.

**Results (exp-026, exp-027): inconsistent, not promotable.** Both Level Sweep Reversal variants were classified into protected/not_protected buckets and backtested separately. `close_min_distance`'s protected bucket came back weakly positive but tiny (44 trades, +0.118R expectancy, 90% bootstrap CI -6.78R to +17.16R -- spans zero). `full_bar_range`'s protected bucket came back negative (59 trades, -0.076R expectancy, CI -19.33R to +11.41R -- also spans zero), showing no separation from its own not_protected comparison bucket. Neither clears the promotion bar (both fail the >=150-trade and CI-above-zero requirements), and the two variants don't even agree with each other on direction -- the kind of inconsistency that argues against a real trend-structure effect rather than for one, on top of the multiple-testing caveat already flagged in the setup doc (this is the fifth hypothesis tested against the Level Sweep Reversal base thesis, and `purgedcv`-based DSR/PBO correction still isn't available to check for accumulating false-positive risk). Both results were logged properly: `hyp-000007` and `hyp-000008` in the hypothesis ledger, full write-ups in `research/experiments/exp-026-*.md` and `exp-027-*.md`, and rows added to `research/experiments/_index.md`. `docs/BACKLOG.md`'s trend-structure liquidity filter idea can now be considered tested.

**2026-09-01 -- pivot to a continuation thesis: Initial Balance Breakout, tested and REJECTED on the largest sample in the project.** After the trend-structure liquidity filter closed out the sixth straight test of the reversal thesis (a level sweeps, price reverses), Jason directed a change in approach: rather than choosing the next idea himself, he asked Claude to act as research lead, pick the next area based on established NQ/market-structure concepts, explain the reasoning, and proceed without waiting for further instruction. The reasoning: continuing to test reversal variants would itself be the kind of search-until-something-looks-positive pattern the project's integrity rules exist to prevent, so the pivot went to a genuinely different, independently well-documented thesis -- continuation, not reversal. The "Initial Balance" (Market Profile / Auction Market Theory, CBOT, early 1980s): the range set in the first 30 minutes after the 8:30 AM open, and whether price holds it (a range day) or breaks and runs with it (a trend day). Frozen definition: `research/setups/initial-balance-breakout.md`, explicitly compared there against this project's existing "ORB placeholder" (a superficially similar idea already killed on 2yr real data back on 2026-08-16, exp-013) so the new test wasn't mistaken for a clean slate.

**Result: REJECTED, on the largest and most decisive sample any setup in this project has produced.** `src/detect_ib_breakout.py` (30-min Initial Balance, breakout window 9:00 AM-noon, first close beyond either side, opposite-side stop, the project's standard 1.35R target) ran against the full Discovery slice: 1654 resolved trades, expectancy -0.077R, 90% bootstrap CI -202.05R to -48.21R -- entirely below zero, only 0.2% of bootstrap sims profitable (exp-028, `hyp-000011`). This reinforces rather than merely repeats the existing ORB placeholder finding: two meaningfully different definitions of "trade the breakout of an early-session range" have now both failed decisively.

**A correction made along the way:** while reviewing that Discovery-slice run, Claude found the trend-structure liquidity filter's two ledger entries (`hyp-000007`/`hyp-000008`, logged the prior session) had been mistakenly marked `PROMISING` instead of `REJECTED`, inconsistent with this project's own convention for a null/negative Discovery-slice result. Corrected via `research_ledger.py`'s append-only `update_status()` (new lines referencing the originals, not edits) and `_index.md`'s verdicts updated from `retest` to `kill`, per Jason's explicit direction in this session to close that line of investigation rather than revisit it.

**2026-09-01 -- a step back from chart patterns: does the open predict anything at all?** With both major thesis families now rejected (reversal and continuation), Jason asked Claude to keep going with the same mandate -- act as research lead, don't wait for instruction. Rather than inventing an eighth named pattern, Claude ran a characterization study, not a strategy test: does the Initial Balance's own directional return (the same 8:30-9:00 window already frozen for Initial Balance Breakout) predict anything about forward returns at five fixed horizons (30/60/90/120/180 minutes), with no chart pattern imposed at all? See `research/studies/open-return-persistence.md` and `research/experiments/exp-029-open-return-persistence-study.md`.

**Result: a clean null across all five horizons, on ~1,700 days.** Every correlation sat within about +/-0.07 of zero, every 90% bootstrap CI (on both the correlation and the up-day/down-day mean difference) spanned zero, with no consistent sign across horizons. This is a second, more fundamental line of evidence pointing the same direction as the seven rejected strategy hypotheses: it isn't only that seven specific chart-pattern implementations found no edge, the raw unconditional relationship between the open's early direction and what follows doesn't show one either, at least not in this simple linear form.

**2026-09-01 -- first test of a new data dimension: volume.** Jason reaffirmed the standing mandate ("get us to the goal") after the Open Return Persistence study's null. Verified the data's `Volume` column is genuine, varying, real Databento volume (not a placeholder) and tested the oldest independent technical-analysis heuristic not yet tried in this project: does a breakout accompanied by unusually high relative volume behave differently than one that isn't? `research/setups/volume-confirmed-ib-breakout.md` defines a same-day self-normalizing relative-volume measure (`rel_volume`) added directly to `src/detect_ib_breakout.py`'s signal dict (additive, non-breaking), with a disciplined two-step plan: characterize the raw correlation first, only build a bucket-split filter if that correlation actually warrants one.

**Result: another clean null, Step 2 correctly never triggered.** Correlation(`rel_volume`, trade outcome) across all 1654 resolved Discovery-slice IB Breakout signals: -0.0229, 90% CI [-0.0645, +0.0190] -- spans zero (exp-030). Per the doc's own rule, no bucket-split backtest was built since the correlation gave no basis for one -- avoiding constructing a filter just to go looking for a result that wasn't there. One real limitation surfaced honestly in the write-up: the same-day baseline used doesn't control for ordinary intraday volume seasonality (volume naturally rises toward the 9:30 AM cash-equity open regardless of any real breakout conviction), so this specific test is weaker evidence against a volume effect than a time-of-day-controlled baseline would be -- flagged as the natural next refinement if volume is revisited.

**2026-09-01 -- third conditioning check: day-of-week, also null.** Continuing per Jason's standing direction ("get us to the goal"), broke down the same 1654 already-collected Initial Balance Breakout trades (exp-028) by NY calendar day-of-week -- a real, long-documented (if debated) phenomenon in academic finance, needing no new data. `research/setups/day-of-week-ib-breakout.md` / exp-031.

**Result: clean, notably uniform null.** Every one of the five weekdays showed negative expectancy in a tight band (-0.056R to -0.092R), win rates clustered at 42-44%, none statistically significant, none within reach of the promotion bar. The uniformity itself is informative -- if a real day-of-week effect were hiding inside this setup's aggregate failure, it would most plausibly surface as one or two days behaving differently; instead the failure looks essentially identical no matter which day it is, arguing against a day-of-week explanation rather than for one.

**Current status: zero setups have cleared the promotion bar (seven strategy hypotheses tested -- six reversal-thesis, one continuation-thesis, all REJECTED -- plus three conditioning/characterization checks on Initial Balance Breakout's trades finding no explanatory relationship in price persistence, breakout volume, or day-of-week). Genuinely new ground from here likely means either a different setup family entirely, or a calendar cut fine enough to need data this project doesn't have yet (an economic-release calendar, futures expiration dates) -- both real options, neither free. Deciding between them, or accepting the current evidence as this data's honest answer for pure intraday price/volume/calendar patterns, is the next call.**

**2026-09-01 -- fourth check, and the first genuinely new data dimension: does the overnight gap mean anything?** Per Jason's standing mandate, and with three straight conditioning checks on Initial Balance Breakout's own trades all coming back null, Claude stepped away from IB Breakout entirely rather than keep slicing the same rejected setup's data a fourth way. `research/studies/overnight-gap-behavior.md` defines the first fresh, non-IB-derived question of the project: using the standard 4:00 PM ET cash-equity close as the reference point (honesty-flagged as a real convention choice for a near-24-hour-traded instrument), does the gap between that prior close and today's 8:30 AM open fill by noon more often than chance, and does the gap's size predict the forward return at the same five fixed horizons used in the Open Return Persistence study?

**Result: the first non-null finding in this project's history (exp-032).** Gaps filled by noon 58.4% of the time after a gap up (n=784, 90% CI [55.5%, 61.4%]) and 58.1% of the time after a gap down (n=556, 90% CI [54.7%, 61.5%]) -- both intervals sit entirely above the 50% coin-flip baseline. Separately, gap size correlated negatively with the +90-minute forward return (-0.1408, 90% CI [-0.2142, -0.0595], n=1318) -- significant, and directionally consistent with the fill-rate result (both point toward mean reversion of the gap). The other four horizons (+30, +60, +120, +180 minutes) stayed null. Two honest cautions accompany this: seven total comparisons were run (two fill-rate groups, five horizons), so multiple-testing exposure is real; and any mechanical rule built from this finding and tested on the same Discovery slice that produced it is not independent confirmation -- only a check that the finding survives becoming an actual costed trade. Per the study's own frozen Step 3 rule, a real relationship found in Steps 1-2 requires defining and testing a concrete mechanical rule next, so a "fade the gap" setup is the immediate next piece of work (`research/experiments/exp-033-fade-the-gap.md`, not yet started).

**Current status: zero setups have cleared the promotion bar, but for the first time this project has a non-null finding to build on.** Seven strategy hypotheses (six reversal-thesis, one continuation-thesis) remain REJECTED, and three conditioning checks on Initial Balance Breakout's trades (price persistence, breakout volume, day-of-week) all found nothing. Separately, the Overnight Gap Behavior study found a statistically significant above-chance gap-fill rate and a significant negative correlation at the +90-minute horizon -- real enough to test as an actual trading rule, but not yet confirmed independently of the Discovery slice it was found on. The next step is to define and test that mechanical rule (fade-the-gap) on the same Discovery slice as a first, necessarily circular check; genuine confirmation would require the project's own Validation slice, which no setup has ever reached.

**2026-09-02 -- the mechanical rule tested, and it doesn't survive contact with real costs.** Per exp-032's own Step 3 rule, `research/setups/fade-the-gap.md` defined the most direct possible trading translation of the gap-fill finding: fade the gap at today's 8:30 open, target = the prior close literally (not this project's usual 1.35R multiple, since the entire premise is a specific price level), a symmetric 1:1 stop forced by that target shape, exit bounded at noon ET to match the underlying study's own watch window. A real data edge case surfaced and was fixed along the way: NQ's near-continuous data means a Sunday "calendar day" only has bars from its evening reopen onward, which was briefly getting matched as a bogus 8:30 AM entry before a guard was added (and `overnight-gap-behavior.md`'s own results were separately checked and confirmed unaffected by the same issue).

**Result: REJECTED, decisively (exp-033).** 1061 resolved trades, win rate 52.1% (CI 49.1%-55.1%) -- genuinely above the 50% coin-flip line, consistent with the underlying finding -- but not enough to overcome costs under a forced 1:1 R:R, which needs comfortably more than a bare majority rather than every other setup's ~43% breakeven-ish threshold. Expectancy -0.079R, 90% bootstrap CI -138.82R to -28.75R, entirely below zero. This doesn't undo exp-032's characterization finding, which remains real on its own terms -- it shows this particular honest translation of it into a costed trade doesn't work. Logged as `hyp-000012`.

**Current status: zero setups have cleared the promotion bar, across eight strategy hypotheses now tested (six reversal-thesis, one continuation-thesis, and one gap-fill-thesis, all REJECTED) plus four conditioning/characterization checks (three on Initial Balance Breakout's trades finding nothing; one on the overnight gap finding something real that still didn't survive being turned into a trade).** Every genuinely different thesis tried against this data and this cost model -- reversal off a swept level, continuation off a breakout, and now mean-reversion off an overnight gap -- has failed to produce a setup that clears the promotion bar. Two narrower, specifically-justified variants of the gap idea remain on the table if picked back up (a partial-fill target, a magnitude-based filter on which gaps to trade), but neither is being pursued automatically. Genuinely new ground from here most plausibly means either a different setup family entirely, or a calendar cut fine enough to need data this project doesn't have yet (an economic-release calendar, futures expiration dates). Deciding between them, or accepting the current evidence as this data's honest answer for pure intraday price/volume/calendar/gap patterns, is the next call.**

**2026-09-02 -- stepping outside the project's own findings for the first time: what do real day traders actually use?** Per Jason's explicit request ("keep pushing... deep research on how normal day traders hit their marks and techniques that have been widely used"), Claude ran a genuine research pass across futures-specific trading education sources, prop-firm content, and academic/SSRN literature on VWAP execution, rather than continuing to generate or condition on this project's own already-tested ideas. Several widely-used techniques were surfaced and explicitly set aside as not genuinely new: ICT-style liquidity-sweep concepts (the same thesis as the six-times-rejected reversal family, under different vocabulary), Volume Profile/Value Area and floor-trader pivot reversion (the same "static precomputed level" shape as Fade the Gap), and further Opening Range Breakout variants (already tested twice). VWAP mean reversion was chosen as the one mechanically distinct idea: a DYNAMIC level recomputed continuously through the session, grounded in VWAP's role as a real institutional execution benchmark rather than a technical-analysis "the market remembers this price" claim -- see `research/setups/vwap-mean-reversion.md` for the full reasoning, including an explicit flag that the retail sources' claimed 65-85% win rates are unverified marketing and are not relied on anywhere in the definition.

**Result: REJECTED, and the most decisive rejection in this project's history (exp-034).** Fading a close beyond the session VWAP's 2σ band, stop at entry±1σ, target at VWAP itself -- a natural 2:1-or-better structure by construction. 2066 resolved trades (largest sample of any setup tested here), win rate 28.7% (CI 26.7%-30.6%), expectancy -0.628R, 90% bootstrap CI -1450.38R to -1134.35R, entirely below zero, 0% of bootstrap sims profitable. An honest interpretive finding came out of the result itself: because the watch window is open-ended (no time cutoff, unlike Fade the Gap), a 2σ excursion off session VWAP turned out to happen on nearly every single trading day (2081 of 2101) rather than the rare, selective event the source material's framing implied -- the setup's real behavior didn't match the story told about it, independent of whether it was profitable. Two real implementation bugs were caught via anomalous statistics and fixed during testing (a stop that could land on the wrong side of entry for fast moves; a handful of zero-risk signals after rounding), both now covered by regression tests. Logged as `hyp-000013`.

**Current status: zero setups have cleared the promotion bar, across nine strategy hypotheses now tested (six reversal-thesis, one continuation-thesis, one gap-fill-thesis, and one VWAP-reversion-thesis, all REJECTED) plus four conditioning/characterization checks (three on Initial Balance Breakout's trades finding nothing; one on the overnight gap finding something real that still didn't survive being turned into a trade).** Every genuinely different thesis tried against this data and this cost model -- reversal off a swept level, continuation off a breakout, mean-reversion off an overnight gap, and now mean-reversion off session VWAP -- has failed to produce a setup that clears the promotion bar, and the VWAP result is the largest and most statistically decisive rejection yet. Narrower, specifically-justified follow-ups remain on the table for both the gap idea (a partial-fill target, a magnitude-based filter) and the VWAP idea (a bounded intraday watch window, a higher sigma multiple), but none is being pursued automatically -- per this project's standing discipline, each would need its own justification rather than being tried just because the first version didn't work. Genuinely new ground from here most plausibly means either a different setup family entirely, or a calendar cut fine enough to need data this project doesn't have yet (an economic-release calendar, futures expiration dates). Deciding between them, or accepting the current evidence as this data's honest answer for pure intraday price/volume/calendar/gap/VWAP patterns, is the next call.**

**2026-09-02 -- closing the loop on one of the two named "genuinely new ground" candidates: futures expiration.** Rather than generate another strategy variant on the gap or VWAP theses, Claude tested the other named candidate from the line above -- futures expiration/rollover proximity -- since it needed no new data acquisition, only a public, well-documented CME quarterly expiration calendar (3rd Friday of Mar/Jun/Sep/Dec) applied to data already collected. Two checks: whether Initial Balance Breakout's existing trades behave differently in the calendar week of an expiration, and whether the overnight gap itself runs larger near expiration (a direct test of this doc's own longstanding, never-investigated claim that a continuous futures series shows "small price jumps at rollover dates").

**Result: clean null on both checks (exp-035).** IB Breakout's Expiration Week (n=131, -0.086R) and Normal Week (n=1578, -0.067R) trades are statistically indistinguishable -- expiration proximity explains nothing about that setup's rejection. The overnight gap runs somewhat larger near expiration (37.03 vs 32.84 points) but the 90% bootstrap CI on that difference ([-4.12, +13.70] pts) spans zero. No mechanical rule triggered, no ledger entry -- a characterization study, not a strategy. Honestly flagged: the public expiration date is a proxy for this data's actual, unknown roll date(s), so this specifically doesn't rule out a splice effect on a different date, only around this proxy. This closes out one of the two candidates named above as "genuinely new ground" with an honest answer, leaving the other (an economic-release calendar) as the remaining candidate that would require a genuinely new data source this project doesn't currently have.

**Current status: zero setups have cleared the promotion bar, across nine strategy hypotheses tested (all REJECTED) plus five conditioning/characterization checks -- four came back clean null (three on Initial Balance Breakout's own trades, one on futures-expiration proximity), and one (the overnight gap) found something real that still didn't survive being turned into a trade.** Every genuinely different thesis and every genuinely different conditioning variable tried against this data and this cost model has now been looked at honestly: reversal off a swept level, continuation off a breakout, mean-reversion off an overnight gap, mean-reversion off session VWAP, day-of-week, breakout volume, price persistence, and futures-expiration proximity. None has produced a setup that clears the promotion bar, and none of the conditioning checks found a hidden subgroup worth pursuing. The remaining, not-yet-exhausted options are: a genuinely new data source (an economic-release calendar, which this project doesn't have), one of the several narrower, specifically-justified follow-ups already named for the gap and VWAP setups (none pursued automatically, per standing discipline), or accepting the current body of evidence as this data's honest answer for intraday price/volume/calendar/gap/VWAP patterns at this cost model. This is a genuine decision point worth surfacing rather than defaulting past.

**2026-09-02 -- a formal research-direction review, then the first test of a genuinely different mechanism: volatility regime.** Rather than generate a tenth level-interaction variant, Jason asked for a structured Phase 2 Research Direction Review before any further code: what has this project actually tested, what mechanisms does it cover, and what's left. That review found all nine strategy hypotheses tested to date -- six reversal-off-a-swept-level variants, IB Breakout, Fade the Gap, and VWAP Mean Reversion -- share the same underlying bet: something happens when price touches, breaks, or reverts to a specific reference price. Volatility regime (grounded in volatility clustering and regime-dependent institutional flow, independent of any price level) was identified as the highest-value untested mechanism. Jason approved that direction, then required the hypothesis tightened to one primary question and one primary outcome, and reviewed a full Frozen Study Specification line-by-line before authorizing any implementation -- the most deliberately gated study this project has produced. One change was made during that review: an originally-proposed minimum prior-history floor was removed as an unjustified free parameter rather than kept.

**Result: clean null on the primary, pre-committed test (exp-036).** Does the mean 30-minute post-8:30 return differ between high- and low-realized-volatility tercile days (20-trading-day causal trailing lookback, expanding percentile-rank classification)? Mean difference +1.241 points, 90% bootstrap CI [-0.252, +2.862] -- spans zero, and below the pre-committed 1.5-point economic threshold regardless. Both pre-specified robustness checks were reported as-is, neither rescuing the result: dropping the single largest-magnitude day barely moved the estimate, and a first-half/second-half split showed the point estimate itself was unstable across the sample. One secondary horizon (120 minutes, reported descriptively only, exactly per the frozen no-fishing rule) happened to show a CI excluding zero -- explicitly not treated as a finding, which is precisely what that rule exists to prevent. No mechanical rule proposed, no ledger entry -- a characterization study, and a genuine null on a mechanism this project hadn't tried before.

**Current status: zero setups have cleared the promotion bar, across nine strategy hypotheses tested (all REJECTED) plus six conditioning/characterization checks -- five came back clean null (three on Initial Balance Breakout's own trades, one on futures-expiration proximity, and now one on volatility regime), and one (the overnight gap) found something real that still didn't survive being turned into a trade).** This is the first time the project has tested a mechanism genuinely outside level-interaction, and it also came back null. The remaining, not-yet-exhausted options per the Phase 2 review: a genuinely new data source (an economic-release calendar, or cross-market/relative-value data, neither of which this project currently has), one of the several narrower, specifically-justified follow-ups already named for the gap and VWAP setups (none pursued automatically, per standing discipline), or accepting the current body of evidence as this data's honest answer for intraday price/volume/calendar/gap/VWAP/volatility-regime patterns at this cost model. This is a genuine decision point worth surfacing to Jason rather than defaulting past.

**2026-09-02 -- before choosing a cross-market hypothesis, a strict data-feasibility-only check.** Per Jason's explicit instruction, before any cross-market hypothesis was chosen or frozen, a feasibility-only study evaluated data cost, data access, technical integration, and research design for adding ES (E-mini S&P 500 futures) as a second instrument -- no experiment, no ES-vs-NQ test, no parameter search. Databento's live cost quote for ES's Discovery-period 1-minute data, obtained by Jason directly (this environment's network egress cannot reach Databento's API), came back at $8.351282700896 -- confirmed feasible. Three candidate mechanisms were assessed; Mechanism 3 (does ES's overnight gap add information about NQ's forward return beyond NQ's own already-characterized overnight gap) was recommended as the best-specified and lowest-multiple-testing-risk of the three. See `research/studies/es-cross-market-feasibility.md`.

**2026-09-02 (same day) -- Mechanism 3 frozen and tested.** Jason approved the ES data purchase, and a Frozen Study Specification for Mechanism 3 was drafted and presented for sign-off before any code was written -- the same gate used for exp-036. Primary test, pre-committed: in a joint OLS regression of NQ's 90-minute forward return on both NQ's own overnight gap and ES's overnight gap, does ES's gap coefficient (b2) carry incremental information after NQ's own gap (already found real in exp-032) is already in the model? See `research/studies/es-overnight-gap-incremental-information.md`.

**Result: clean null on the primary, pre-committed test (exp-037) -- the project's first two-instrument analysis.** b2 = -0.0816, 90% bootstrap CI [-0.432, +0.262] -- spans zero. Translated economic effect (1.081 points) fell short of the 1.5-point threshold. The inner join between NQ's and ES's valid days dropped zero days on either side. Both pre-specified robustness checks were reported as-is, neither rescuing the result: dropping the single largest-|ES_gap| day barely moved the estimate, and a first-half/second-half split showed the point estimate itself was unstable across the sample (as with exp-036's own split-half check). No mechanical rule proposed, no ledger entry -- a characterization study, and a genuine null on this project's first cross-market mechanism.

**Current status: zero setups have cleared the promotion bar, across nine strategy hypotheses tested (all REJECTED) plus seven conditioning/characterization checks -- six came back clean null (three on Initial Balance Breakout's own trades, one on futures-expiration proximity, one on volatility regime, and now one on ES's overnight gap as incremental information), and one (the overnight gap) found something real that still didn't survive being turned into a trade.** Both mechanisms tested outside level-interaction -- volatility regime and now cross-market -- have come back null. The remaining, not-yet-exhausted options per the Phase 2 review and the feasibility report: the two other candidate cross-market mechanisms named in `research/studies/es-cross-market-feasibility.md` (lead-lag correlation, NQ/ES relative-strength spread), a genuinely new data source (an economic-release calendar, which this project doesn't have), one of the several narrower, specifically-justified follow-ups already named for the gap and VWAP setups (none pursued automatically, per standing discipline), or accepting the current body of evidence as this data's honest answer for intraday price/volume/calendar/gap/VWAP/volatility-regime/cross-market patterns at this cost model. This is a genuine decision point worth surfacing to Jason rather than defaulting past.

**2026-09-02 (same day) -- PIVOT: paused mechanism-by-mechanism hunting.** After exp-037, the Path-to-Profitability Advisor was run on the explicit choice in front of Jason (test lead-lag/relative-strength next, pursue the economic-calendar data source, or pause and address the approach itself). Claude's own initial lean was toward the cheapest next test (lead-lag, since ES data is already purchased). The Advisor recommended pausing instead: twelve hypotheses across three structurally distinct mechanism families have now all gone null, Mechanisms 1/2 are the leftover candidates from the same feasibility report whose flagship candidate already failed, lead-lag specifically has a bad economic prior (a textbook effect institutional stat-arb has likely already competed away), and the execution path is not the bottleneck (Phase 8/9 broker plan is already decided) -- what's being tested is. Jason reviewed both takes and chose the Advisor's recommendation. Per the Advisor's own final point, the next step is a short, explicit conversation with Jason about whether the promotion bar or the data granularity/type used so far (NQ 1-minute OHLCV bars only) is calibrated to what's actually findable in this market, rather than another characterization study.

**2026-09-02 (same day) -- daily/swing timeframe tested, second-opinion consensus.** Following the pivot above, Claude asked Jason where to focus: the data itself, the promotion bar, or the whole approach. Jason asked for the tradeoffs, then for the Advisor's independent take. Both agreed on one concrete test rather than more discussion: classic time-series momentum (Moskowitz/Ooi/Pedersen, 252-trading-day lookback) at daily resolution, using data already on hand, at zero incremental cost -- a mechanism with real academic/CTA support, structurally different from every sub-hour, level-touch mechanism tested so far. Because this signal flips only a handful of times across the Discovery window by construction, Jason approved a disclosed, one-time adaptation of the standing 150-trades promotion bar (a daily-P&L bootstrap CI and a cost-drag-relative economic threshold) for this test only, after the tradeoffs against simply shortening the lookback were presented explicitly -- logged in the Promotion bar section above. See `research/studies/nq-daily-trend-following.md`.

**Result: clean null (exp-038) -- the first daily-resolution test in this project's history.** Mean daily net P&L +0.772 points across 1,463 usable days, 90% bootstrap CI [-4.075, +5.501] -- spans zero. 44 position flips over 6.75 years (~6.5/year), so not a thin bet on one or two historical trends. Both robustness checks reported as-is, neither rescuing the result: dropping the single largest-magnitude day barely moved the estimate, and a first-half/second-half split showed the sign itself was unstable (positive vs. negative), the same instability pattern seen in exp-036's and exp-037's own split-half checks. A real implementation bug -- a day-pairing error that dropped two days of P&L for every single missing reference-close day instead of skipping over it -- was caught via a sanity check on the usable-sample size and fixed before the result was trusted; the fix changed the point estimate and flip count materially but not the null conclusion. No mechanical rule proposed, no ledger entry.

**Current status: zero setups have cleared the promotion bar, across thirteen hypotheses tested (all REJECTED or NULL) spanning four structurally distinct mechanism families -- level-interaction, volatility-regime, cross-market, and now daily trend-following -- and two timeframes (intraday and, for the first time, daily).** The daily-timeframe test was designed to answer two questions at once: was the twelve-null streak a timeframe artifact, and does the deeper "find a technical pattern in liquid futures with cheap data" premise still hold. Both came back null under a real, academically-grounded, disclosed-adaptation test -- not evidence the premise is definitely wrong, but no longer evidence it's simply a matter of trying a different lookback window. This is the point the Advisor's own framing anticipated: a genuine decision on whether to continue searching (a new data type, e.g. order flow or options positioning; the two remaining cross-market candidates; an economic-release calendar) or to treat the accumulated evidence as this data's honest answer and reconsider the project's core approach. Surfaced to Jason as a live decision, not defaulted past.

**2026-09-02 (same day) -- economic-calendar feasibility confirmed, CPI/NFP-only scope chosen.** Per the pivot above, the Advisor's recommendation to test the scheduled-information family was checked for feasibility first, same discipline as the ES purchase. Confirmed FEASIBLE at zero cost: FOMC/CPI/NFP dates and times are all available free from federalreserve.gov and bls.gov's own official archive pages (Investing.com/ForexFactory ruled out -- ToS-prohibited scraping, no API). The one real design fork: CPI/NFP release at 8:30 AM ET, fitting the project's existing intraday framework directly, while FOMC releases at 2:00 PM ET and would need its own new reference point. Per the mandatory Advisor-consultation rule, both Claude's lean (CPI/NFP only, defer FOMC, avoid adding new machinery before the simpler test is even run) and the Advisor's independent recommendation (include FOMC now, as the single most information-dense scheduled event, rather than risk it becoming a 15th-variant follow-up later) were shown to Jason side by side. Jason chose CPI/NFP only, against the Advisor's specific recommendation. See `research/studies/economic-calendar-feasibility.md` and `research/studies/economic-release-volatility.md`.

**Result: POSITIVE (exp-039) -- the first non-null result across fourteen hypotheses and five mechanism families.** Mean 30-minute post-8:30 |return| is +11.333 points larger on CPI/NFP release days than on normal days, 90% bootstrap CI [+8.103, +14.939] -- entirely above zero, well past the 1.5-point economic threshold. Both robustness checks and both CPI-only/NFP-only sub-group splits independently confirm the effect; all four secondary horizons agree in direction. This is a magnitude finding (announcement-volatility clustering), not a directional one, by design -- the study's own frozen spec disclosed in advance that gate condition 5 (a simple mechanical rule specifiable without fitting to the result) would not resolve the usual way: a positive result here points toward a volatility-capture structure (wider stops, a straddle-like setup), not a long/short signal. No ledger entry yet. See `research/experiments/exp-039-scheduled-macro-release-volatility.md`.

**Current status: zero setups have cleared the promotion bar, across fourteen hypotheses tested spanning five structurally distinct mechanism families -- level-interaction, volatility-regime, cross-market, daily trend-following, and now scheduled information -- but for the first time, one of them (exp-039) is not a null.** Thirteen straight nulls across four families and two timeframes were followed by a genuine positive finding on the one mechanism the Advisor identified as structurally distinct from everything tried before. It is a magnitude finding, not a directional one, so it does not slot into this project's existing mechanical-rule pipeline the way a positive result on any prior study would have -- the natural next step is a volatility-capture design question (position sizing, wider stops, a straddle-like structure around known release days), which is a different and heavier design lift than every prior conversion attempt. Per the mandatory Advisor-consultation rule, both Claude's own read and the Advisor's independent read on what this changes and what to do next are being presented to Jason before any direction is proposed -- this is the first time that conversation is about a real result rather than another null.

## A note on how tonight's autonomous work was scoped (2026-08-15)

Jason asked me to keep building without him present, including
overnight/multi-day, until I hit something needing his decision. Two
honest limits on that, recorded here so future-Claude (and Jason) don't
lose the thread: (1) there is no standing background process — work only
happens in a live conversation or when the scheduled daily check-in task
fires; nothing runs continuously between those. (2) I hit the real
stopping point the same night: further progress on the trading logic
itself requires Jason's actual setup description and real (non-synthetic)
data, neither of which I can generate myself. What I built after
reaching that point (the test suite) was deliberately scoped to be useful
regardless of what setup Jason eventually picks, rather than continuing
to guess at trading-logic decisions that are his to make.

## A note on data quality

We're starting with free Yahoo Finance data (ticker `NQ=F`) via the
`yfinance` Python library. This is good enough to build and debug the whole
system. Its real limitation: Yahoo only gives ~60 days of 1-minute history,
and futures data quality (especially around session rollovers/contract
switches) is not institutional-grade. Before trusting any backtest result
with real money, we should upgrade the data layer to a real futures data
vendor (e.g. Databento, Norgate, IQFeed, or your broker's historical data
API) — but that's a Phase 2 upgrade, not a blocker for building the system
itself.

## A note on "NQ=F"

`NQ=F` is Yahoo Finance's symbol for the continuous front-month E-mini
Nasdaq-100 futures contract. "Continuous" means Yahoo automatically splices
together whichever contract month is currently most active, so you get one
unbroken price series instead of having to track contract expirations
yourself. This is convenient but introduces small price jumps at contract
rollover dates — something to be aware of later when we look closely at
edge cases.

## Promotion bar (added 2026-08-18)

A setup only becomes eligible for the sealed holdout check once it has, on
research-only data: (1) expectancy > 0 after realistic cost assumptions,
(2) at least 150 trades, and (3) a 90% bootstrap confidence interval on
expectancy that stays entirely above zero. This is the formal bar going
forward — no setup gets promoted to a holdout check without clearing it.

**One-time, explicitly scoped exception (2026-09-02):** this bar
assumes a discrete, frequently-repeating trade shape. For the NQ Daily
Time-Series Momentum study, whose signal flips only a handful of times
across the whole Discovery window by construction, Jason approved
adapting the mechanics (a bootstrap CI on the daily P&L series, and an
economic threshold measured against this strategy's own realized cost
drag, in place of trade-counting) while keeping every underlying
principle intact. See "Why the promotion bar is adapted for this
study" in `research/studies/nq-daily-trend-following.md` for the full
reasoning. This does not change the 150-trades bar above for any
other setup, past or future.

## Tony's Pine Script verified working (2026-08-18/19)

Both pine/level_sweep_close_min_distance.pine and pine/level_sweep_full_bar_range.pine
were manually reviewed against src/detect_level_sweep.py, two behavioral bugs were
found and fixed (day-skipping on no-premarket-data, same-bar long/short mutual
exclusivity), and both were tested live in TradingView: compiled with no errors,
plotted support/resistance step-lines correctly, and one real signal fired
(close_min_distance, SHORT, 2026-08-04, Entry 29233.25 / Stop 29282.25 / Target
29167.1) with target math independently verified against the 1.35x-risk formula
in the Python source. That date falls inside the sealed holdout window, so it
couldn't be cross-checked against a logged backtest row -- but the math
verification alone confirms the script's core calculation logic is correct.
Alert creation was set up in TradingView but push notification delivery is
unconfirmed (didn't fire in first test) -- flagged to revisit later, not blocking.
