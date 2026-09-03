# Historical Options/Implied-Volatility Data Feasibility

*2026-09-03. A factual feasibility check, not a decision. Prompted by
the Advisor's recommendation after
`docs/OPTIONS_VOLATILITY_EXECUTION_FEASIBILITY.md`: before writing any
backtest for a standalone volatility-capture options structure (e.g. a
straddle around known CPI/NFP/FOMC release times), check whether the
DATA to price such a backtest honestly even exists and what it costs
-- the same discipline already applied to the ES futures purchase and
the economic-calendar data. No code, no purchase, no experiment, no
ledger entry.*

## The short answer

**Real NQ futures options data exists and is reachable through
Databento (the vendor this project already has a relationship with),
but only as raw chain data, not pre-computed implied volatility --
meaning the project would need to build its own options-pricing
machinery (Black-Scholes or similar) from scratch, something it has
never done. The exact dollar cost is not yet known** -- Databento
prices usage-based ("from $0.50/GB" for CME data), and getting a real
number requires running their cost calculator against a specific date
range and data resolution, a small follow-up step, not a purchase.
Cheaper/free alternatives exist but are all for a *different* product
(NDX/SPX index options, not NQ futures options) -- a real
approximation, not the thing itself.

## Findings, source by source

**Databento (already-used vendor) -- confirmed real NQ futures options
data, cost not yet quoted.** Their `GLBX.MDP3` dataset ("CME Globex
MDP 3.0") explicitly covers options on CME/CBOT/NYMEX/COMEX futures,
including NQ, with history back to 2010. Pricing is pay-as-you-go from
$0.50/GB (uncompressed) for raw trade/quote data, or included in a
subscription -- no flat multi-year number is published; an exact
figure needs their cost calculator run against a chosen date range and
schema. **Important limitation: Databento does not compute Greeks or
implied volatility** -- "options greek data" sits as an unbuilt,
unstatused item on their own public feature roadmap. Using this route
means pulling raw options trade/quote data and deriving IV ourselves
via a standard pricing model -- new financial-engineering work this
project has never done, on top of the data cost itself.

**CME Group's own "Greeks and Implied Volatility Data" product --
exists, but priced by quote only.** CME sells pre-computed Delta,
Gamma, Theta, Vega, Rho, and IV across its "top 40 futures contracts"
(unclear from public pages whether NQ is included), 5 years of
history, via CME DataMine. This would skip the "build our own pricing
model" problem entirely if NQ is covered -- but actual self-service
pricing isn't published; it requires a DataMine account or emailing
CME's market-data sales team for a quote. CME's general enterprise
distribution-license fee schedule (~$34k/year) is visible but is
clearly not the relevant retail/self-service price, so it's not a
usable cost signal here.

**VXN (CBOE Nasdaq-100 Volatility Index) -- likely free, but not
directly confirmed.** VXN is the Nasdaq-100 analog to VIX. It is
notably **absent** from CBOE's own free historical-volatility-index
download page and from FRED (both list VIX-family series but not
VXN). Third-party aggregators (Yahoo Finance, Investing.com, Barchart)
each have a VXN historical-data page with coverage back to 2001, which
would comfortably cover this project's full Discovery/Validation
window -- but a working free CSV export wasn't directly verified in
this pass (one fetch attempt 404'd) and would need a direct spot-check
before being relied on.

**CBOE DataShop and `historicaloptiondata.com` -- real, priced, but
the wrong underlying product.** Both offer real historical options
chain/Greeks/IV data with concrete pricing (`historicaloptiondata.com`:
roughly $230-$1,150/year for quotes-only, $315-$1,495/year with
Greeks/IV, up to $2,035 for a full IV surface, history to 2002) -- but
both run on the OPRA feed, which covers **U.S. equity/ETF/index
options (NDX, SPX, QQQ), not CME futures options**. NDX options are
cash-settled and European-style; NQ futures options are American-style
options on a futures contract -- related but genuinely different
products with different settlement and volatility dynamics. This is a
real, usable, cheap approximation if an exact NQ-futures-options
backtest turns out to be too costly or slow to arrange -- but it is an
approximation, not the thing itself, and would need to be disclosed as
such in any resulting study, the same way this project has disclosed
every other proxy or adaptation.

**OptionMetrics IvyDB -- exists, not retail-accessible.** Covers
listed options including some futures-options products, but access is
via WRDS, an institutional/university subscription model -- not
something purchasable directly by this project.

## What this means for the project, without deciding anything

There is a real, non-approximated path (Databento, using data this
project already knows how to pull) to eventually backtest a
straddle-style structure honestly -- but it is not a simple "here's
the price, go" answer the way the ES purchase was. Two real open
questions before any purchase: (1) what the actual dollar cost is for
a useful date range and resolution (needs a specific Databento
cost-calculator run, not yet done), and (2) whether the project wants
to build its own options-pricing/IV-derivation code (a new category of
work) or pursue CME's pre-computed Greeks/IV product instead (cost
unknown, needs a sales quote). A cheaper, faster, but approximate path
exists via VXN or NDX-options data if either of those questions turns
out to be a real blocker -- flagged honestly as an approximation, not
a substitute.

No purchase made, no code written, no options account opened, no
experiment created, no ledger entry -- a factual finding only, same
spirit as every prior feasibility check in this project.

## Sources

- [Databento CME Globex MDP 3.0 dataset](https://databento.com/datasets/GLBX.MDP3)
- [Databento Options Market Data](https://databento.com/options)
- [Databento Pricing](https://databento.com/pricing)
- [Databento roadmap: get options greek data](https://roadmap.databento.com/b/n0o5prm6/feature-ideas/get-options-greek-data)
- [CBOE Historical Data for VIX and Other Volatility Indices](https://www.cboe.com/tradable-products/vix/vix-historical-data/)
- [FRED VIXCLS series](https://fred.stlouisfed.org/series/VIXCLS)
- [Yahoo Finance ^VXN history](https://finance.yahoo.com/quote/%5EVXN/history/)
- [Investing.com CBOE Nasdaq 100 Volatility Historical Data](https://www.investing.com/indices/cboe-nasdaq-100-voltility-historical-data)
- [Barchart $VXN Price History](https://www.barchart.com/stocks/quotes/$VXN/price-history/historical)
- [CME Group Greeks and Implied Volatility Data](https://www.cmegroup.com/market-data/greeks-and-implied-volatility-data.html)
- [CME Group January 2025 Market Data Fee List (PDF)](https://www.cmegroup.com/market-data/files/january-2025-market-data-fee-list.pdf)
- [CME DataMine Self-Service Platform (wiki)](https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457088998/CME+DataMine+Self-Service+Platform)
- [CBOE DataShop Data Products](https://datashop.cboe.com/data-products)
- [CBOE DataShop Option EOD Summary](https://datashop.cboe.com/option-eod-summary)
- [Historical Option Data (historicaloptiondata.com)](https://historicaloptiondata.com/)
- [OptionMetrics -- WRDS](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/optionmetrics/)
- [OptionMetrics: Premier Historical U.S. Futures Data announcement](https://www.businesswire.com/news/home/20210311005674/en/OptionMetrics-Announces-Premier-Historical-U.S.-Futures-Data-for-Research-on-Markets-Risk)
