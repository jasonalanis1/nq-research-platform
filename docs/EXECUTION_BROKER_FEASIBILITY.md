# Execution Broker Feasibility: Robinhood + TradingView

*2026-09-02. A factual feasibility check, not a decision. Prompted by the
Path-to-Profitability Advisor's first live review (see
docs/PATH_TO_PROFITABILITY_ADVISOR.md's History), which found that
"Robinhood" appeared nowhere in this project's actual architecture
documents despite being the broker Jason has discussed using -- and that
docs/AUTOMATION_ARCHITECTURE.md's Phase 8 ("a broker's paper API") never
named or verified a specific broker at all. This document checks the
actual current facts, via web research, before any of Phases 6-11 are
built around an assumption that turns out to be wrong.*

## The short answer

**Robinhood supports real NQ futures trading for a human, but not for
software, as of today.** There is a real, confirmed gap between what a
person can click and what a program can call. The good news: the
project's own Phase 6 design (TradingView Pine Script signal generation)
is already broker-agnostic, and there's a mature, standard path to real
automated futures execution -- it just doesn't go through Robinhood.

## What Robinhood actually offers today

**Manual futures trading (humans only):** CME Group and Robinhood
announced CME futures "rolling out on the Robinhood mobile app" starting
January 29, 2025 -- specifically naming the Nasdaq-100 among four equity
index benchmarks (alongside S&P 500, Russell 2000, Dow), plus crypto,
FX, metals, and energy contracts. This is real and current. The press
release is explicit that access is through "the Robinhood mobile app"
and makes no mention of programmatic access, an API, or automated order
placement anywhere -- this is a human-clicks-the-app feature.

**Programmatic/API trading ("Agentic Trading"):** Separately, Robinhood
has a genuinely real, current API for AI agents to place real orders --
built on the Model Context Protocol (MCP), the same open standard Claude
itself uses for tool connections. This launched in beta on 2026-05-27
for equities and options, and expanded on 2026-07-20 to crypto (spot and
"Lighter perpetuals," a crypto-derivative product, not the same thing as
a traditional CME futures contract). As of the most recent information
found (2026-07-21), **futures trading is not mentioned as a supported
asset class, and no roadmap for adding it was found.**

**The gap, stated plainly:** a person can open the Robinhood app and buy
or sell an NQ futures contract by hand today. Nothing in this project's
Signal -> Risk Engine -> Execution Engine -> Broker pipeline (per
AUTOMATION_ARCHITECTURE.md) can currently place that same order through
Robinhood programmatically. Phase 8 ("Automated paper execution... via a
broker's paper API") and Phase 10 (automated live execution) cannot be
built against Robinhood for NQ futures specifically, as things stand
today. This could change -- Agentic Trading is expanding by asset class
roughly every couple of months (equities/options -> crypto), so futures
support is plausible later, but isn't something to build a plan around
happening on any particular timeline.

## What does exist for automated futures execution

This is not a dead end -- automated TradingView-to-futures-broker
execution is a mature, well-established pattern in the retail futures
trading world, just built around different brokers than Robinhood.
**Tradovate** and **NinjaTrader** are the two most common futures
brokers/platforms with real, documented APIs, both supporting NQ and
MNQ contracts, and both have multiple existing third-party bridge
services (CrossTrade, PickMyTrade, and others) specifically built to
take a TradingView webhook alert and place a real order on one of them
automatically. This is exactly the shape Phase 6 (TradingView signal
generation) through Phase 8 (automated execution) already describe --
the missing piece was never the TradingView side, only which broker
Phase 8's "broker's paper API" actually points at.

## What this means for the project, without deciding anything

This document doesn't change AUTOMATION_ARCHITECTURE.md's phases,
thresholds, or promotion criteria -- that's Jason's call, and Phases
6-11 are explicitly deferred, not being built right now regardless.
What it does is remove a silent assumption before it could cause wasted
work later: if "Robinhood" was the implicit plan for Phase 8+
automation, that plan needs a different broker for the automated stages
specifically. A few real options, not a recommendation among them:

1. **Robinhood for Phase 9 (human-approved live execution), a
   futures-API broker (Tradovate/NinjaTrader) for Phase 8 and Phase 10+
   automation.** Since Phase 9 already requires a human to approve every
   trade in real time, a human placing that approved trade by hand in
   the Robinhood app Jason may already be using isn't blocked by any of
   the above -- only the *automated* phases are.
2. **Standardize on Tradovate/NinjaTrader (or similar) for all of Phases
   8-11**, so paper execution (Phase 8) and eventual live automation
   (Phase 10) are tested against the exact same broker/API from the
   start, rather than switching brokers mid-pipeline.
3. **Wait and re-check Agentic Trading's asset coverage periodically** --
   cheap to do, and if Robinhood adds futures to it later, this whole
   question resolves itself. Not a plan to build around now, but worth a
   note to revisit rather than forgetting the question was ever open.

No code, no broker integration, no experiment, no ledger entry -- this
is a factual finding only, same spirit as the ES cost-feasibility check.

## Sources

- [CME Group: CME Futures to Launch on Robinhood](https://www.cmegroup.com/media-room/press-releases/2025/1/29/cme_group_futurestolaunchonrobinhoodbringingnewtradingopportunit.html) -- 2025-01-29, confirms Nasdaq-100 futures on the Robinhood mobile app, no API/programmatic mention.
- [Robinhood: Agentic Trading overview](https://robinhood.com/us/en/support/articles/agentic-trading-overview/) -- official support article on the MCP-based agent trading feature and its approval modes.
- [Robinhood is Now Open to Agents](https://robinhood.com/us/en/newsroom/robinhood-is-now-open-to-agents/) -- Robinhood's own newsroom post on the Agentic Trading launch.
- [TechCrunch: Robinhood now lets your AI agents trade stocks](https://techcrunch.com/2026/05/27/robinhood-now-lets-your-ai-agents-trade-stocks/) -- 2026-05-27 beta launch coverage, equities and options.
- [Genfinity: Robinhood Agentic Trading Opens to Crypto](https://genfinity.io/2026/07/21/robinhood-agentic-trading-crypto-ai-agents/) -- 2026-07-21, most recent asset-class expansion found (crypto spot + perpetuals), no futures mention or roadmap.
- [CrossTrade: Complete Automation Suite for NinjaTrader 8 & Tradovate](https://crosstrade.io/) -- example of an established TradingView-to-futures-broker bridge product.
- [PickMyTrade: TradingView Webhook Alerts Documentation](https://blog.pickmytrade.io/tradingview-webhook-automation-trading-alerts/) -- example documentation of the standard TradingView-webhook-to-futures-broker automation pattern.

## Addendum, 2026-09-03: minimum-useful confirmation, not a new lead

The Path-to-Profitability Advisor's 2026-09-03 consultation was explicit
that broker research is not a new hypothesis or trading "lead" -- it is
infrastructure work that only matters once a candidate has actually been
promoted, and doing it now is premature relative to where this project's
hypothesis search stands. Its recommendation was a cheap, one-time
confirmation only, done in parallel with hypothesis work rather than in
place of it. This addendum is that confirmation, nothing more.

**Confirmed**: both Tradovate and NinjaTrader support NQ and MNQ
(E-mini and Micro E-mini NASDAQ-100) directly, and both have a mature,
multi-vendor ecosystem of TradingView-webhook-to-broker automation
products beyond the two already cited above -- QuantOTC and ClearEdge
were also found offering the same TradingView-alert-to-Tradovate/
NinjaTrader bridge pattern, and flowbots.ninja documents the same
approach. This is consistent with, not a change to, the three options
already laid out above: it confirms the *mechanism* (webhook-driven
automation into either broker) is real and commercially mature, not
a one-off or unmaintained tool. It does not rank Tradovate against
NinjaTrader, does not estimate cost, and does not decide anything --
that decision was already, correctly, left open above, and stays open
here.

No code, no account created, no integration attempted. This remains a
factual finding only.

### Additional sources (2026-09-03)

- [QuantOTC: TradingView to Tradovate & NinjaTrader Bridge](https://www.quantotc.com/works/tv-tradovate-ninja) -- another TradingView-webhook-to-futures-broker bridge product, same automation pattern as CrossTrade/PickMyTrade.
- [ClearEdge: TradingView Automation -- Webhooks to Futures Broker Setup](https://clearedge.trading/post/tradingview-automation-futures) -- same pattern, third independent vendor found.
- [flowbots.ninja support: differences between TradingView (Tradovate accounts) and NinjaTrader OCO exit orders](https://support.flowbots.ninja/hc/en-us/articles/35329571844244-Differences-between-TradingView-Tradovate-accounts-and-NinjaTrader-OCO-exit-orders) -- vendor documentation confirming both brokers are live, supported automation targets, not just marketing claims.
