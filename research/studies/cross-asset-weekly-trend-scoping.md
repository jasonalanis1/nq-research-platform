# Cross-Asset Diversified Test of the Weekly Trend Signal -- exp-051

## Status: v2 -- cleared by the Path-to-Profitability Advisor conditional on the v1->v2 changes below. NOT YET BUILT -- blocked on real Databento cost quotes for 3 new instruments (Section 4), not yet purchased.

## 1. Provenance

Directly from a 2026-09-07 strategy conversation: Jason asked whether
this project has been searching an unproductive sandbox (single-
instrument NQ price patterns), and both Claude and the Advisor
independently concluded yes -- 26 hypotheses, zero clearing the
promotion bar, on one of the most heavily-traded, most heavily-
researched instruments in the world, using only public price data. The
Advisor's recommendation: stop inventing new NQ-only patterns, and
instead test whether the ONE signal that ever came close (exp-047's
weekly trend momentum sign) holds up spread across a diversified
basket of instruments -- how real trend-following actually works in
practice. Jason authorized scoping this ("Yeah").

## 2. Why cross-ASSET-CLASS, not just more equity index futures

Adding ES or YM alongside NQ would NOT be genuine diversification --
all three are large-cap US equity index futures that move together
most of the time (this project's own exp-037 found ES's and NQ's
overnight gaps correlated). Real diversification comes from spreading
across asset classes with meaningfully different price drivers.

**Basket (4 instruments, one per asset class):**
- NQ (Nasdaq-100 e-mini) -- already have -- equity index
- ZN (10-Year Treasury Note futures) -- rates
- 6E (Euro FX futures) -- currency
- CL (WTI Crude Oil futures) -- commodity

Deliberately small and cheap -- a first, honest look at whether
diversification helps at all, not a production-scale system.

## 3. Signal-family lineage and selection-bias disclosure (v2 -- Advisor-required)

**This is NOT a fresh, independent first test.** It is the fourth test
touching the exp-047 signal family (047: raw signal, near-miss ->
048: hard-cap overlay, kill -> 049: trailing-stop overlay, kill ->
051: this test), and critically it reuses the SAME 2015-2021 Discovery
window that produced the original near-miss. exp-047 was chosen for
this treatment specifically because it was the closest-to-passing
signal of 26 tested -- that selection itself inflates the odds of an
apparent pass that isn't real. Diversification could "work" on
ZN/6E/CL in this specific historical window by chance, the same way
a single-instrument variant can brush the bar by chance.

**Because of this, a pass here is NOT treated as confirmed edge.**
Per the Advisor's explicit requirement: even if the combined portfolio
clears the two-part promotion bar on Discovery data, this only earns
the SAME status exp-047's raw signal would have earned had it passed
outright -- eligibility for out-of-sample corroboration (Validation
slice, or folded into exp-050's prospective-tracking approach), NOT
an immediate promotion to live-authorization discussion. This is
disclosed here, before any result exists, specifically so a Discovery-
slice pass isn't quietly treated as more decisive than it honestly is.

## 4. Data acquisition -- NOT decided here, real costs involved, NOT YET PURCHASED

- NQ: already have.
- ES: already have Discovery-period data (purchased 2026-09-02, $8.35)
  but NOT part of this basket (Section 2) -- not used here.
- ZN, 6E, CL: NOT yet purchased. Next step, same discipline as every
  prior data acquisition in this project: Jason runs
  `metadata.get_cost()` himself from his own machine for each of these
  three, scoped to the Discovery date range ONLY (2015-01-01 ->
  2021-10-03, matching NQ/ES) -- not the full 2015-2026 range. Based on
  ES's own $8.35 for the identical range, expected similarly cheap
  (order of $10-30 total) -- an expectation, not a quote. No purchase
  happens until Jason sees the real numbers and approves.

## 5. Portfolio construction -- fully pinned down (v2 -- Advisor-required, was "not yet pinned down" in v1)

**Return-space, not raw points (correctness fix):** exp-047's
single-instrument convention (position * raw point price change) only
makes sense for one instrument -- NQ points, ZN points, 6E points, and
CL points are not comparable units (different contract multipliers).
Every instrument's weekly P&L is instead computed as a WEEKLY LOG
RETURN (position * log(this_week_close / prev_week_close)), which is
unit-free and directly comparable/summable across instruments. This
replaces exp-047's point-based P&L for this multi-instrument context
only -- the single-instrument exp-047/048/049/050 scripts are
UNCHANGED and continue to use points, since NQ-only comparisons to
their own history need to stay apples-to-apples with those results.

**Volatility-sizing formula (concrete, frozen, not "TBD"):** each
instrument's weekly risk weight = target_vol / trailing_20-trading-day
realized volatility of that instrument's own daily log returns
(annualized), computed using ONLY days through the close of the Friday
BEFORE the week being sized (no lookahead -- see below), where
target_vol is a fixed constant shared across all 4 instruments and all
weeks (its absolute value cancels out of the CI/pass-fail test itself,
since it scales the whole portfolio uniformly -- it only matters for
absolute P&L reporting, not the statistical test). Weights are
renormalized each week so the 4 instruments' weights sum to a constant
total (equal risk budget, not equal dollar).

**No-lookahead rule (explicit, v2 -- Advisor-required):** the
volatility used to size the position held during week W is computed
from daily returns dated strictly before week W's first trading day
(i.e., through the prior week's last trading day) -- never using any
day inside week W itself. Identical causal discipline to every other
frozen spec in this project (exp-048/049's ATR calculation is the
direct precedent, reused conceptually here).

## 6. What's being tested, mechanically

The exact exp-047 signal (sign of trailing 52-week cumulative log
return, weekly rebalance) computed INDEPENDENTLY on each of the 4
instruments (reusing `compute_weekly_momentum_signal`,
`resample_to_weekly_closes`, `compute_weekly_log_returns`,
`compute_positions` unmodified, once per instrument -- no
per-instrument tuning). Each instrument's signed weekly log return is
risk-weighted per Section 5 and summed into one portfolio weekly
return series.

**Primary test:** does the COMBINED PORTFOLIO'S weekly return series
clear the same two-part promotion bar (90% CI entirely above zero AND
economically meaningful vs. realized cost drag) that no single-
instrument version has ever cleared?

**Secondary/disclosure:** report each instrument's own individual
result too, so a portfolio-level pass can't hide behind one instrument
doing all the work.

## 7. Cost modeling -- scaled to 4-instrument turnover (v2 -- Advisor-required)

exp-047's `FLIP_COST_POINTS` is an NQ-specific point cost and cannot be
reused directly in a return-space, multi-instrument portfolio. Cost is
instead modeled as a fixed BASIS-POINT drag per instrument per flip
(a conservative, disclosed estimate of round-trip futures transaction
cost as a fraction of notional -- exact bps value to be set from
publicly documented futures commission/slippage estimates, disclosed
in the implementation, not silently assumed equal to NQ's absolute
point cost). Each of the 4 instruments' flips are costed independently
and rolled into the combined portfolio return each week -- turnover
does not shrink just because the portfolio is diversified; each
instrument can still flip on its own schedule.

## 8. Promotion bar

Same two-part bar (90% CI entirely above zero AND economically
meaningful vs. realized cost drag), applied to the COMBINED portfolio's
weekly return series, per Section 3's lineage-aware evidentiary
standard (a pass here is an eligibility result, not a promotion).

## 9. What this is NOT

- Not a claim diversification will definitely work.
- Not a full CTA-scale build -- 4 instruments, a first look.
- Not spending money without a real quote first (Section 4).
- Not a re-test of the ES overnight-gap idea (exp-032/037) -- unrelated
  mechanism.
- Not a decision to stop exp-050's parallel prospective validation of
  exp-047 on NQ alone, which continues regardless of this result.
- Not, per Section 3, a route to an immediate live-authorization
  conversation even on a clean Discovery-slice pass.

## 10. ASCII-only

Confirmed.

## Advisor review (2026-09-07)

v1 returned "cleared with changes, not cleared as-is." Required
changes, all incorporated above: (1) explicit signal-family lineage
and selection-bias disclosure, with a pass here treated as an
eligibility result requiring further out-of-sample corroboration, not
an immediate promotion (Section 3); (2) the volatility-sizing formula
fully pinned down rather than left open (Section 5); (3) an explicit
no-lookahead rule for the volatility calculation (Section 5); (4)
transaction-cost assumptions scaled to actual 4-instrument turnover,
not reused from the single-NQ cost basis (Section 7). During v2
drafting, one additional correctness issue was caught and fixed:
combining raw point P&L across instruments with different contract
multipliers is meaningless, so the portfolio is built in return-space
(weekly log returns) instead, and the single-instrument exp-047/048/
049/050 scripts are left unchanged.
