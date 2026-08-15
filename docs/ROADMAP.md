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
