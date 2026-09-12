# Data pricing quotes — requested by Jason September 12th, ~1:35 am CT

"Quote me two one-off pulls: NQ trades/aggressor data, and NDX or QQQ
options open interest. Don't buy, just price. I'll set the ceiling from
that."

Nothing was purchased. No account was created. Everything below is from
Databento's public pricing pages and public API documentation.

## Headline: the "one-off pull" framing does not survive contact with how
## Databento actually prices deep history

The assumption behind the request was a one-time historical purchase,
maybe $30, maybe $300. That is not the shape of the offer for the data
that would match this project's Discovery slice (2015-01 to 2021-10).
Databento moved CME to plan tiers, and history DEPTH is the thing the
tiers gate:

| Plan | Price | History it actually includes |
|---|---|---|
| Standard | $199/month, no annual contract stated | L0 (OHLCV, definitions, STATISTICS, status) 16+ years. L1 (trades, TBBO, BBO, MBP-1) **12 months only**. L2/L3 1 month. Pay-as-you-go for more history. |
| Plus | $1,750/month, **annual contract required** | L1 (incl. trades) extended to **16+ years**. |
| Unlimited | $4,500/month, annual contract required | All schemas L0-L3, 16+ years. |

New accounts get **$125 in free credits** (6-month expiry, one per team).

## Pull 1 — NQ trades with aggressor side

Aggressor side lives in the `trades` schema, which is L1.

- To cover 2015-2021 (matching the existing Discovery slice): that is
  16-year L1 history = the **Plus** tier, $1,750/month on an annual
  contract = **~$21,000/year**. This is not a ceiling adjustment, it is a
  different category of expense, and it is emphatically out of range.
- Pay-as-you-go for deep history on top of Standard is offered but the
  $/GB rate for GLBX.MDP3 is NOT published publicly (see "what I could
  not get" below). Rough sizing for scale only: NQ trades at roughly
  700k trades/day average over the period, ~48 bytes/record uncompressed
  in DBN, ~1,700 trading days = order of **50-60 GB**. Whatever the CME
  rate turns out to be, multiply it by ~55. This is my own estimate, not
  a quote, and the trade-count assumption is the soft part.
- The genuinely bounded option: **$199 for a single month of Standard**,
  which includes 12 months of trades history, then cancel. That is a
  real, known, small number.

### The catch on the $199 option, and it is a serious one
Those 12 months are the most RECENT 12 months. This project's Discovery
slice ends 2021-10-03; everything after 2024-01-04 is Holdout, and the
last stretch is the forward-validation window that H118 and EXP047 are
currently accumulating evidence in. Searching for hypotheses in recent
data would burn the cleanest out-of-sample data the project has, which is
the one asset the whole Discovery/Validation/Holdout structure exists to
protect.
It is not unworkable — it would mean deliberately carving a new, declared
Discovery window out of recent data and accepting that the corresponding
period is spent for search — but that is a methodology decision for
Jason, not a purchasing decision, and it should be made explicitly rather
than discovered afterwards.

## Pull 2 — NDX / QQQ options open interest (dealer positioning)

- Open interest is carried in the **`statistics`** schema, which is an
  **L0** schema. On the CME table above, L0 comes with 16+ years of
  history even on the $199 Standard tier. If OPRA is tiered the same way,
  options open interest is far cheaper to reach than options trades.
  I could not confirm OPRA's tier table — the pricing page did not break
  out OPRA separately.
- What IS documented, from Databento's own API reference example for
  OPRA.PILLAR: `trades` = **$280.00/GB** historical ($336/GB live), while
  `cbbo-1s` = **$2.00/GB**. A 140x spread between schemas inside one
  dataset. This is the single most useful pricing fact found: the schema
  chosen matters far more than the date range.
- Sizing for open interest is small — one record per contract per day.
  QQQ carries on the order of 5-10k listed contracts; at ~50 bytes that
  is well under 1 GB per year. If the statistics rate is near the low end
  of that spread, this pull is plausibly tens of dollars, not thousands.
  If it is priced like trades, it is a few hundred.

## What I could not get, and the exact way to get it for free
Databento does not publish per-GB rates by dataset on any public page;
they are behind the data catalog and the API. Two free endpoints return
authoritative figures with no purchase and no commitment:
- `metadata.list_unit_prices(dataset=...)` — the full $/GB table per
  schema for that dataset.
- `metadata.get_cost(...)` — an **exact dollar quote for one precisely
  specified request** (dataset, symbols, schema, date range) before
  ordering anything.
Both need only a free API key. If Jason creates the free account and
hands over a key, the exact number for both pulls can be on the table in
minutes; alternatively he can run the catalog calculator himself. Either
way the $125 signup credit covers the exploration.

## Recommendation (Claude's, one line)
Do not set a ceiling from the estimates above — get the two free
`get_cost` quotes first, because the honest spread between "options open
interest via a cheap schema" and "NQ trades deep history" spans roughly
two orders of magnitude, and a ceiling set in the middle of that would be
arbitrary in both directions.
