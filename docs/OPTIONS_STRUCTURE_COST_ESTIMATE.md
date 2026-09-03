# Options/Volatility-Structure Cost Estimate

*2026-09-03. Jason asked to actually price out the options/volatility-
structure idea (rather than leave it shelved on a guess). This
document is that pricing pass -- still no purchase, no code, no
broker account, no experiment, no ledger entry. It builds directly on
`docs/OPTIONS_DATA_FEASIBILITY.md` and
`docs/OPTIONS_VOLATILITY_EXECUTION_FEASIBILITY.md`.*

## The short answer

**Both the data cost and the engineering cost turned out cheaper than
the earlier feasibility checks feared -- but a bigger, more important
question got surfaced in the process, and it needs answering FIRST,
for free, before either dollar is spent or any code is written.**

## Data cost: likely low, not yet confirmed exactly

Databento prices historical options data by data volume (GB), not by
number of strikes/expiries -- "from $0.50/GB" for CME Globex
(GLBX.MDP3), which covers NQ options back to 2010. New accounts get
**$125 in free credit** (expires 6 months after signup). The actual
backtest need is narrow: short windows around 8:30am ET and 2pm ET on
roughly 200 specific historical days (the same CPI/NFP/FOMC dates
already used in exp-039/040/041) -- not continuous multi-year tick
data. No exact figure is published for this specific slice; getting
one requires running Databento's own cost calculator, which needs a
signup but no payment. **Real risk, not yet ruled out**: an options
chain has many strikes, each generating its own quote/trade stream, so
"a few hours on 200 days" could still add up to more data than the
same window of plain futures data this project is used to pricing --
the calculator, not this estimate, has the real number.

## Engineering cost: lower than previously feared

The earlier feasibility check flagged needing to "build our own
options-pricing/IV-derivation machinery from scratch" as a real,
never-done-before risk for this project. That's no longer accurate:
**QuantLib** (pip-installable, actively maintained, latest release
mid-2026) implements Black-76 (the standard model for options on
futures, not equity Black-Scholes), American-style exercise (Barone-
Adesi-Whaley or binomial-tree engines), and Greeks, all out of the
box. This converts "invent options pricing theory" into "learn and
wire up an existing, real, tested library" -- the same shape as this
project's recent `purgedcv` (DSR/PBO) precedent, not a fundamentally
new kind of risk. Rough estimate, by comparison to this project's own
past study builds (each has taken roughly one focused session: spec,
Advisor review, implementation, tests, real-data run): **3-5 focused
sessions**, not 1, since this is genuinely new subject matter for the
project and a real bug has surfaced in nearly every new domain tackled
so far.

## Execution cost: unchanged, and not the current blocker

Confirmed in the earlier doc, unchanged here: Interactive Brokers
supports NQ futures options programmatically, $0 account minimum, but
requires a margin account and a discretionary "futures options"
trading permission with unpublished approval criteria. This only
matters for eventually placing a LIVE trade, not for backtesting the
idea -- a real future gate, not a dollar cost, and not relevant to the
next decision.

## The more important thing this pass surfaced

Per the Path-to-Profitability Advisor's review of this estimate:
exp-039/040 show that realized price moves are bigger on CPI/NFP/FOMC
days. **That is not the same thing as options being mispriced around
those days.** Implied volatility is typically bid up ahead of known
scheduled events precisely because the market expects a bigger move --
this is the well-documented volatility risk premium. A structure that
buys options ahead of a known release needs realized volatility to
exceed what was already implied beforehand, not just be large in
absolute terms. This project's two confirmed findings have never been
compared against what the options market was already charging for
that risk on the same days -- an honest gap, not previously
disclosed as one.

**This check is free and needs no new engineering**: compare implied
volatility (via VXN, already identified in
`OPTIONS_DATA_FEASIBILITY.md` as a likely-free, if not yet fully
verified, data source) against the realized moves already measured in
exp-039/040/041, on the same event days. If implied vol already ran
higher than what subsequently realized, a simple "buy volatility ahead
of the release" structure most likely has no edge -- the historically
documented edge in options markets more often runs the other way
(selling volatility), which carries materially different and larger
tail risk, a much bigger consideration for a first options venture
than anything this project has automated so far.

## What this means for the project, without deciding anything

The dollar and engineering costs are not the blocker they looked like
-- both are real but modest next steps, not a multi-thousand-dollar or
multi-week commitment. The actual next step that matters is cheaper
than either: check whether this project's own confirmed magnitude
findings would have been tradeable through options at all, using free
VXN data and no new code, before spending anything on Databento or
QuantLib. No purchase made, no code written, no broker account opened,
no experiment created, no ledger entry -- a factual finding only.

## Sources

- [Databento Pricing](https://databento.com/pricing)
- [Databento Options Market Data](https://databento.com/options)
- [Databento: End of Early Access -- $125 in free credits](https://roadmap.databento.com/announcements/end-of-early-access-125-in-free-credits-for-all-users)
- [QuantLib on PyPI](https://pypi.org/project/QuantLib/)
- [QuantLib release history](https://libraries.io/pypi/QuantLib)
- `docs/OPTIONS_DATA_FEASIBILITY.md` (2026-09-03, this project)
- `docs/OPTIONS_VOLATILITY_EXECUTION_FEASIBILITY.md` (2026-09-02, this project)
