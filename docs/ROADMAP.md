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

**Next up — Stage 2:** pick ONE specific trading setup Jason watches for
around the 8:30 open (e.g. range breakout, failed break/reversal, gap
fill, opening drive) and turn it into a rule the computer can detect
automatically in the data. Not yet decided as of the last update.

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
