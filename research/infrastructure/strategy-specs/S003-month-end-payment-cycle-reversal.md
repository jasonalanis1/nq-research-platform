# S003 — Month-end payment-cycle reversal, NQ (M24) as a FULL strategy

FROZEN 2026-09-16 (11:00 pm CT cycle). Module:
`src/strategy_s003_month_end_payment_cycle_reversal.py`.
Standing directive s.13: neither this file nor the module is edited after the
FREEZE row lands in `research/ledger/strategies.jsonl`. A change is a FIX ONCE
(directive s.6), never an edit.

---

## 1. Lineage — why a CLOSED effect is back (directive s.9)

M24 (`research/mechanisms/month-end-payment-cycle-reversal-m24.md`) was closed
2026-09-13 as hyp-000157, **P1_FAIL**, on Scan 031: the LOW-tercile next-month
return net of NQ's own unconditional next-month drift came back
**mean +0.0112, block CI (-0.0005, +0.0224), n=27** — the lower bound sits a
hundredth of a percent on the wrong side of zero. The closure form records it as
a *near miss* with an *adequate* sample and a *weakened* mechanism.

It was never a strategy. Nothing was ever built around it: no entry price, no
stop, no cost accounting, no exit other than "the next month's close." The
directive's revamp premise (s.9) is exactly this case — it was killed for failing
an academic test (*is this effect statistically real?*) that the directive has
retired as a gate, and it has never been asked the business question
(*does this trade make money after costs?*). The directive names it by name as
top of the revamp list. **This spec is the first time M24 is a trade.**

Two facts from Scan 031 that this spec relies on and does NOT re-derive:
- The confound check cleared: the first-3-RTH-session share of the LOW-tercile
  next-month return is **0.452**, below the 0.5 kill threshold, so this is not
  the closed M6/hyp-000108 turn-of-month inflow effect wearing a different hat.
- The HIGH tercile is flat (mean +0.0000), as a forced-*selling*-only story
  predicts. The effect, such as it is, lives on the down side only.

Nothing in this spec re-uses Scan 031's *tercile boundaries* — see s.3.

## 2. Mechanism (one paragraph, Mechanism agent)

Pension funds, corporate treasuries and payroll/dividend-funding accounts owe
cash on a fixed calendar schedule: payroll, pension disbursements, dividend
funding, all clustered at month-end. To raise that cash they sell broad equity
exposure, and they sell it because the calendar says so, not because they have
a view. A forced, non-discretionary seller with a deadline pushes price below
where information alone would put it, and because no new information was
transmitted, the push is transient: it decays as ordinary two-sided buying
resumes over the following weeks. So a calendar month whose final week was weak
*relative to how weak NQ's final weeks usually are* is a month in which that
liquidation pressure was unusually heavy, and the price it left behind should
recover over the month that follows. The trade is: buy the last print of a
month that was sold into, hold through the decay, sell the last print of the
next month. The participant is identified, the deadline is real, the impact is
mechanical, and the horizon is set by how long it takes normal flow to absorb
an inventory shock — not by a curve fit.

## 3. The whole trade (Monetization agent)

| | |
|---|---|
| **instrument** | MNQ (micro NQ), 1 contract, always |
| **universe** | the final RTH session of each calendar month |
| **condition** | that session's *last-week return* is at or below the **33.3rd percentile of the previous 24 month-end observations** of the same quantity (minimum 12 observations, else no trade) |
| **last-week return** | `entry price / Close of the 5th-prior RTH session − 1`. Every input is printed before the entry bar opens. |
| **entry** | long at the **OPEN of the 15:59 ET bar** of month *t*'s final RTH session |
| **exit** | flat at the **OPEN of the 15:59 ET bar** of month *t+1*'s final RTH session, declared to the paper loop as an absolute `market_context["exit_ts"]` (the cross-session walk, choice 7 in `src/bot_stack_paper_run.py`) |
| **stop** | `entry − 4.0 × ATR20` (daily RTH true range, 20-session mean, lagged one session so it is known at the entry bar). **A disaster cap, not a management stop.** R = 4.0 × ATR20. |
| **target** | **none.** A decay trade has no target; the module passes an unreachable sentinel so the shared bookkeeping can only ever exit on the stop or the clock. `risk_multiple` is meaningless for this strategy and is recorded as such. |
| **size** | 1 micro, always. No scaling, no conditional sizing. |
| **costs** | **ASSUMED**: $2.50/side commission + 1 tick/side slippage = **$6.00 per micro round trip** (3.0 MNQ points). Labelled ASSUMED everywhere until B4b measures real fills (directive s.11). |

**Why a trailing percentile and not Scan 031's frozen tercile.** Scan 031 froze
its tercile boundaries on the whole Discovery slice, which is fine for a
statistical cell and inadmissible in a strategy: a trader standing at the end of
January 2016 cannot know the 33rd percentile of 2015–2021. The trailing-24-month
percentile is the same idea made knowable at decision time. It is not a tuned
parameter: 24 months is two years of the monthly cycle, the shortest window that
sees each calendar month twice, and 33.3% is Scan 031's own tercile split
carried over unchanged.

**Stop distance and the validated magnitude facts.** The three validated facts
(VXN → next-session range; quiet midday → expanded afternoon; wide open → wider
midday) were each considered and **none of them is used, because none of them
applies here**: all three are intraday or next-session magnitude statements, and
this trade holds ~21 sessions. Using an intraday range fact to size a monthly
stop would be borrowing authority a fact does not have. The stop is instead
scaled to the trade's own horizon: one month is ~21 RTH sessions, and a
random-walk scaling of a daily range to 21 sessions is √21 ≈ 4.6 daily ATRs.
The cap is set at **4.0 × ATR20**, just inside that, so it sits at the edge of
an ordinary month's excursion rather than inside it — it exists to bound a
crash, and it should almost never be the exit. If it fires often, that is
itself a finding and is reported.

**Known frequency limit, stated before the screen.** This strategy fires at most
once a calendar month and, on the condition, roughly one month in three. Over
the Discovery slice that is ~25–30 trades; in forward paper it is ~0–1 trades in
six weeks. **It will therefore almost certainly reach its 6-week judgment point
under the directive's 15-trade floor and be KILLed as unjudgeable (s.6),** the
same structural fate S001a faces. That is a property of the mechanism's
frequency, not a defect in the spec, and it is written here in advance so no
later cycle can present it as a surprise. The screen is the number that carries
information about this strategy; the paper slot is cheap and runs anyway.

**Session exclusions.** A month whose final RTH session is a fragment or a
holiday half-day (last bar before 15:55 ET, or no 15:59 bar) is no trade. If the
exit month's final session is not on disk yet, the signal still fires with a
placeholder exit timestamp that the loop's cross-session guard refuses: the
entry session is DEFERRED whole, nothing is logged, nothing is force-closed, and
it is re-scored once the exit session's bars exist. The placeholder can never
book a trade — only defer one. Identifying the final session of a month is a
*calendar* fact, not a price fact; where the data cannot yet confirm it (the
last session on disk, with a holiday-shortened tail), the module declines rather
than guesses, and that month is simply not traded.

## 4. Where this should fail (Mechanism agent) — this becomes S003's Salvage menu

1. **Information-driven month-ends.** When the last week was weak because
   something actually broke, not because someone had payroll to fund, there is
   no transient to reverse. Proxy: the next month opens with a further leg down.
   (Scan 031's non-gating cell 10 is the same idea.)
2. **High-VXN regimes.** When the market is repricing risk, month-end selling is
   a small part of a large flow and the cash-management footprint is drowned.
   (Salvage menu condition 1.)
3. **Sustained downtrends.** A month-long long in a downtrend fights the tape
   for 21 sessions; the decay is real but smaller than the trend it sits inside.
   (Salvage menu condition 2.)
4. **Turn-of-month bleed.** If essentially all of the gain lands in the first 3
   sessions of the new month, this is M6's inflow effect and not M24's
   liquidation reversal, whatever the P&L says. (Scan 031 measured 0.452 on
   Discovery; it is re-checkable per trade.)
5. **The stop itself.** A fixed cap on a 21-session hold rarely helps and can
   convert a recoverable drawdown into a locked loss at exactly the wrong time.
6. **Costs are irrelevant here and that cuts both ways.** $6.00 against a
   month-long swing is noise, so unlike S001a/S002 this strategy is *not*
   cost-fragile — but that also means the screen number is almost entirely the
   raw effect, which Scan 031 already showed is small and not statistically
   credible. A positive screen here is a thin, honest edge, not a discovery.

Salvage, if it is owed, runs the fixed s.7 menu (VXN high/low; trending vs
range-bound; time of day — degenerate here, every entry is at 15:59, and it will
be reported as degenerate rather than quietly dropped; scheduled-news day or
not) plus conditions 1, 3 and 4 above. One salvage, menu only.

## 5. Screen (directive s.2), pre-registered at FREEZE

`python3 src/screen_strategy.py strategy_s003_month_end_payment_cycle_reversal`,
Discovery slice only (2015-01-01 → 2021-10-03), the paper loop's own
bookkeeping, ASSUMED costs. **One number: net USD at 1 micro after assumed
costs.** Net > 0 → PAPER this cycle. Net ≤ 0 → Salvage by the s.7 menu.
No CI gate, no multiplicity gate, no holdout. Trades whose exit falls past the
end of the Discovery slice are excluded as OPEN, never force-closed.

## 6. Judgment (directive s.6)

40 trades or 6 weeks, whichever first. Given s.3's frequency limit the 6-week
clock will arrive first with far fewer than 15 trades, which is a KILL as
unjudgeable. S003 gets one salvage, ever.
