# NQ Research Platform — Roadmap

This is the plain-English map of what we're building, in order. We will NOT
build all of this at once — each stage is its own mini-project that has to
work before we move to the next one. Skipping ahead is how most home-built
trading systems end up broken and untrustworthy.

## Stage 0 — Environment (today)
Get a working, repeatable way to pull NQ price data and look at it. No
strategy logic yet. Just "can we reliably get clean data for the 8:30 AM NY
open window."

## Stage 1 — Data Layer
A script/module whose only job is: given a date range, return clean OHLCV
(Open/High/Low/Close/Volume) bars for NQ, in New York time, with no gaps or
duplicate rows, saved to disk so we don't re-download every time. Everything
downstream depends on this being trustworthy. Garbage data in = garbage
backtest out, no matter how good the strategy logic is.

## Stage 2 — Setup Detection
Code that scans historical bars and flags "this looks like [pattern X]" —
e.g. a range breakout at the open, a failed auction, an opening drive, a
gap-and-go. This is where your trading knowledge gets turned into rules a
computer can check mechanically. We'll start with ONE setup, get it fully
working end-to-end through every later stage, then add more.

## Stage 3 — Backtesting Engine
Given: historical data + a setup-detection rule + entry/exit/stop rules.
Output: a list of every simulated trade it would have taken, with entry
price, exit price, P&L, and timestamps. This is the part that tells you
honestly whether an idea has an edge, not just whether it "looks good" on a
chart.

## Stage 4 — Scoring / Statistics
Turn the raw trade list from Stage 3 into numbers that matter: win rate,
average win vs average loss, expectancy, max drawdown, Sharpe-like ratio,
performance by day of week / by session / by market regime. This is what
lets you compare Setup A vs Setup B objectively instead of by gut feel.

## Stage 5 — Automation (future, only after 1-4 are proven)
Only once a setup has survived rigorous backtesting and (ideally) a period
of paper trading do we talk about connecting this to a broker for live or
semi-live execution. This is the highest-risk stage (real money, real bugs
cost real dollars) so it comes last on purpose.

---

## Where we are right now

**Stage 0 is done:** we can generate/pull NQ minute data, and we produced
a first chart of the 8:30 AM NY open window (currently using synthetic
placeholder data, since the cloud sandbox used to build this can't reach
real market data sites — `src/data_fetch.py` is ready to pull the real
thing once run on a machine with normal internet access). The project is
also now under git version control, with setup instructions in
`README.md` for backing it up to GitHub and for continuing development
locally using Claude Code on a Mac.

**Stage 2 has a first working example:** Jason hadn't picked a specific
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

**Stages 3 and 4 also now have working first passes**, built the same
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

Stage 5 (live automation) remains explicitly gated on Jason's direct,
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
API) — but that's a Stage 1 upgrade, not a blocker for building the system
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
