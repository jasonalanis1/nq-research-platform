# Options/Volatility-Structure Execution Feasibility

*2026-09-02. A factual feasibility check, not a decision. Prompted by
the Path-to-Profitability Advisor's review after exp-040 (FOMC): with
the scheduled-macro-release-volatility family now 2-for-2 (exp-039
CPI/NFP, exp-040 FOMC), both magnitude-not-direction findings, the
Advisor's recommendation was to check whether a volatility-capture
structure is even executable BEFORE any design work -- the same
discipline already applied to the ES data purchase and to Robinhood's
futures-API gap (`docs/EXECUTION_BROKER_FEASIBILITY.md`). This
document answers that question and nothing else: no code, no broker
account, no purchase, no experiment, no ledger entry.*

## The short answer

**A real options structure on NQ is programmatically reachable, but
only through a broker this project's existing automation plan doesn't
currently use (Interactive Brokers), and only past a discretionary
approval gate.** A cheaper, simpler fallback -- widening stop-loss
distance on a plain directional NQ futures position around known
release times, no options involved -- is already executable on the
exact same Tradovate/NinjaTrader + bridge stack
`docs/EXECUTION_BROKER_FEASIBILITY.md` already confirmed works for
this project's futures automation.

## What was checked

Whether NQ futures options (CME options on the E-mini Nasdaq-100
futures contract) -- or any comparable programmatic volatility-capture
product -- can be placed via a real, documented API (not just clicked
by a human), through a broker realistically accessible to an
individual retail trader.

## Findings, broker by broker

**Tradovate -- partial / unconfirmed at the API level.** The platform
now markets "Options on Futures" and shows an options-chain view in
the app. No Tradovate API documentation was found confirming
programmatic options-order placement specifically -- every documented
order-endpoint example found (`/order/placeoco`, bracket orders, etc.)
is a futures-contract order flow. Community forum threads about the
options chain (Greeks, mobile visibility) read as an early/thin
feature, not a mature one. **Not confirmed usable for this purpose.**

**NinjaTrader -- no, for the automation stack already in use.**
NinjaTrader's own support forum states plainly: options on futures
"cannot be traded through NinjaTrader Continuum" -- Continuum/Rithmic
being the exact connection type CrossTrade/PickMyTrade use for this
project's already-confirmed automated NQ/MNQ futures path. Options are
reachable inside NinjaTrader 8 only via a separate Interactive Brokers
connection, and no evidence was found that automated (API/NinjaScript)
order placement works through that bolted-on path. **Not usable
through the automation stack this project has already validated for
directional futures.**

**Interactive Brokers -- yes, confirmed.** The TWS API documentation
explicitly supports a `FuturesOnOptions` (FOP) contract type --
options on futures, including NQ, placeable programmatically via the
TWS/IBKR API (Python, Java, C++, and others). Access notes: the
account minimum is $0, but futures trading requires a margin account
(not a cash account), and trading futures options specifically
requires requesting a separate "futures options" permission through
IBKR's Client Portal. IBKR does not publish exact approval criteria --
it states eligibility depends on "financial profile (age, liquid net
worth, investment objectives, product knowledge, and prior trading
experience)," a discretionary suitability gate, not a fixed dollar
threshold. **Confirmed usable, but on a broker/platform this project's
existing automation plan (Tradovate/NinjaTrader via CrossTrade/
PickMyTrade) does not currently include, and subject to an approval
process whose outcome isn't knowable in advance.**

**Other brokers.** No other broker with genuine, documented API
support for NQ futures options specifically was found in this pass.
Tastytrade/tastyworks has a documented API and strong options
reputation but NQ-futures-options API support was not verified here --
flagged as a possible follow-up only if IBKR's approval gate proves a
real blocker, not pursued further now.

## The simpler fallback: a stop-width overlay, no options needed

Both findings this family has produced are magnitude findings -- NQ
moves more around known release times, not in a predictable direction.
The cheapest way to act on that without touching options at all is a
risk-management overlay on an ordinary directional futures position:
wider stop-loss distance (or smaller size) specifically around known
CPI/NFP/FOMC times. This is **already executable today** on the exact
stack this project's own broker feasibility check already confirmed:
CrossTrade's documented bracket-order feature supports stop-loss
distances set as an absolute price or as a relative offset (ticks,
points, dollars, or percent) per webhook signal, on both Tradovate and
NinjaTrader. One platform nuance worth knowing: NinjaTrader
recalculates the bracket distance from the actual fill price
(wait-for-fill), while Tradovate fixes bracket prices at submission
time. No new broker, no new approval process, no new infrastructure --
this path only needs a directional setup to attach it to, which is
this project's actual, unrelated bottleneck (no setup has ever cleared
the promotion bar).

## What this means for the project, without deciding anything

This doesn't change any phase, threshold, or plan in
`docs/AUTOMATION_ARCHITECTURE.md` or
`docs/EXECUTION_BROKER_FEASIBILITY.md` -- that's Jason's call. What it
adds: a real options-based volatility-capture structure is possible in
principle (via IBKR) but would mean adding a broker this project
hasn't used or tested anywhere else, past an approval gate with
unknown odds -- a genuinely bigger lift than anything built so far.
The cheaper, simpler version of the same idea (a stop-width overlay,
not real options) needs no new infrastructure at all -- it is blocked
only by the same thing every other finding in this project is blocked
by: no directional setup has ever cleared the promotion bar to attach
it to.

No code, no broker account, no options approval requested, no
experiment, no ledger entry -- a factual finding only, same spirit as
every prior feasibility check in this project.

## Sources

- [TWS API v9.72+: Options](https://interactivebrokers.github.io/tws-api/options.html) -- FuturesOnOptions (FOP) contract sample, confirms programmatic NQ-futures-options support.
- [Interactive Brokers Required Minimums](https://www.interactivebrokers.com/en/accounts/required-minimums.php) -- $0 account minimum for individual accounts.
- [Adding Trading Permissions & Subscribing to Market Data -- IBKR Campus](https://ibkrcampus.com/campus/trading-lessons/trade-permissions-mkt/) -- futures-options permission request process, no disclosed eligibility criteria.
- [Minimum to Trade Futures on Interactive Brokers -- Benzinga](https://www.benzinga.com/money/minimum-to-trade-futures-on-interactive-brokers) -- margin-account requirement for futures.
- [Tradovate -- Why Tradovate](https://www.tradovate.com/why-tradovate/) -- "Options on Futures" marketing claim.
- [Options and the Tradovate Options Chain -- Tradovate Community (2018)](https://tradovate.zendesk.com/hc/en-us/community/posts/360000845427-Options-and-the-Tradovate-Options-Chain)
- [Add Greeks to Options Chain -- Tradovate Feature Requests](https://community.tradovate.com/t/add-greeks-to-options-chain/1219)
- [Options on futures -- NinjaTrader Support Forum](https://forum.ninjatrader.com/forum/ninjatrader-8/platform-technical-support-aa/1274973-options-on-futures)
- [Trying to trade options through NinjaTrader Continuum -- NinjaTrader Support Forum](https://forum.ninjatrader.com/forum/ninjatrader-8/platform-technical-support-aa/1286742-trying-to-trade-options-through-ninjatrader-continuum) -- "options on futures cannot be traded through NinjaTrader Continuum."
- [CrossTrade -- Bracket Orders documentation](https://crosstrade.io/docs/webhooks/advanced-options/bracket-orders) -- dynamic/relative stop-loss support on Tradovate and NinjaTrader.
