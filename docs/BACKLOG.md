# Backlog

A single place to capture every idea the moment it comes up, so nothing said in passing gets lost. Any new idea should get logged here immediately, even before it's decided on. Reviewed as part of the regular project check-ins.

## Active

- **Initial Balance breakout continuation** — proposed by Jason 2026-09-01, directly (not sourced from a video clip), after the trend-structure liquidity filter's inconsistent result closed out the reversal thesis. Explicit direction: pick the next research area based on established NQ/market-structure concepts rather than Jason choosing it himself, explain the reasoning, and proceed without waiting for further instruction. Selected because every idea tested to date (Level Sweep Reversal's three variants, the FVG entry trigger, the trend-structure liquidity filter) shares the same underlying bet -- a level sweeps, price reverses -- and all six have failed; testing more reversal variants would itself be the kind of search-until-something-looks-positive pattern this project's integrity rules exist to prevent. This pivots to a genuinely different, independently well-documented thesis (continuation, not reversal): the "Initial Balance" from Market Profile / Auction Market Theory (CBOT, 1980s) -- the range set in the first stretch of trading after the open, and whether price holds that range (a range day) or breaks and runs with it (a trend day). Tied directly to the project's stated objective (behavior around the NQ 8:30 AM NY open), needs no new data source. Note: this project already has an "ORB placeholder" (`research/setups/orb-placeholder.md`) from 2026-08-15 testing a superficially similar continuation idea (15-min range, 60-min breakout window, 1x-range-width target) that was killed on 2yr real data (exp-013, 493 trades, -0.062R) -- but under the OLD pre-Research-Integrity-Protocol methodology (full contaminated window, never Discovery-slice-specific), with arbitrary untuned parameters the placeholder's own doc disclaimed. This is a related but meaningfully distinct idea (Market-Profile-grounded 30-min Initial Balance, breakout window to noon, project-standard 1.35R target), tested fresh against the Discovery slice specifically -- see `research/setups/initial-balance-breakout.md` for the frozen definition and full comparison to the old placeholder.

**Status update 2026-09-03: tested.** This ran as exp-028 (`research/experiments/_index.md`) -- 1,654 trades, statistically decisive kill (90% CI entirely below zero). Kept here as a historical record of the reasoning for picking this direction, not as an open item.

*(move items here from Parked when they're picked up)*

## In Scoping

*(nothing currently open)*

## Ongoing / Prospective Tracking

- **exp-050: Prospective validation of exp-047 (weekly trend-following
  signal)** -- built 2026-09-06, per the Path-to-Profitability Advisor's
  recommendation and Jason's authorization ("let's run it"), directly
  following the exp-047/048/049 family's shelving below. Tracks the raw
  exp-047 signal forward on data that did not exist yet at freeze time
  (2026-08-19 19:59:00 America/New_York, the exact last on-disk bar at
  sign-off) rather than re-mining anything already on disk. Pre-registered
  checkpoints at 104/156/208 weeks, hard 260-week maximum horizon, a
  one-sided early-kill rule (Monte-Carlo-justified ~5% false-kill rate),
  no early-pass rule. Zero prospective weeks logged yet -- waiting on new
  NQ data to be fetched forward (cadence/cost of that ongoing paid pull
  is Jason's call, not yet decided). See
  `research/studies/prospective-validation-exp047-scoping.md`,
  `src/study_prospective_exp047.py`, ledger hyp-000020.

## Parked

- **Individual stocks as an alternative to NQ futures** -- raised by Jason 2026-09-03 during the post-"step back" conversation, considered and set aside (not rejected outright, parked). Both Claude's own assessment and the Path-to-Profitability Advisor's independent take agreed: moving to individual stocks multiplies the number of things being searched from one instrument to thousands of tickers, which multiplies the risk of "finding" a fake edge purely by chance -- the exact failure mode this project's promotion bar and Discovery/Validation split exist to prevent. It would also mean new data cost and none of what's been learned about NQ (calendar effects, gap behavior, reversal patterns) carries over. Revisit only if the NQ-specific search genuinely runs dry across multiple future checkpoints, not as a first resort.



- **Fundamental/macro finance plugins** (equity research, earnings analysis, economic calendar data — e.g. LSEG, Daloopa, S&P Global-style tools) — considered 2026-08-18. They solve a different problem (company/macro fundamentals) than this project's current focus (technical price-pattern backtesting on NQ futures). Revisit only if a future strategy hypothesis becomes fundamentals- or macro-driven (e.g., trading around FOMC/CPI releases), which Level Sweep Reversal is not.

- **Fair Value Gap (FVG) lower-timeframe entry trigger** — considered 2026-08-18, from a YouTube Short (ICT/Smart Money Concepts style). Same core thesis as the existing Level Sweep Reversal setup (sweep a significant level, price fails to close beyond it, reversal expected), but with a mechanically different entry technique: instead of "close back beyond the level" (the three variants already tested), enter on a 3-candle price imbalance ("Fair Value Gap") on a lower timeframe once the higher-timeframe rejection is seen. Not just a parameter tweak — a genuinely different entry trigger, so not redundant with exp-013 through exp-020. Source claim ("catches 3.6R almost every day") is one cherry-picked anecdotal example with no sample size or losing trades shown — not evidence, don't weight it. If tested later, must go through the full research-only/holdout pipeline like everything else, and would need a precise, non-cherry-pickable definition of "Fair Value Gap" before backtesting.

- **Trend-structure-aware liquidity filter** — considered 2026-08-18, from a second YouTube Short (ICT/Smart Money Concepts style). Claims a meaningful difference between sweeping "interior" liquidity (swing highs/lows inside an established trend) versus sweeping the "protected high/low" (the structural point that, if broken, would flip the trend classification itself) — the former is framed as a normal stop-hunt-then-continuation, the latter as an actual reversal signal invalidating the setup. Points at a real gap in the current Level Sweep Reversal setup, which doesn't distinguish these two cases at all — it treats every prior-day/pre-market level sweep the same regardless of trend context. Genuinely specific and testable as a context filter (relates to the "volatility regime / trend-day vs range-day" filter idea already on the table), not just another generic pattern. Caveat: "swing high," "protected high," and "break of structure" have no single standard definition — programmatically defining them introduces new parameter choices that are themselves an overfitting risk (each definition choice is a knob that could get tuned until something looks good). Must go through the same research-only, holdout-respecting pipeline as everything else if tested — no fast-tracking because the theory sounds more rigorous.

- **research_ledger.py hypothesis ID gaps** — found 2026-08-24, while logging exp-023/024. **Closed 2026-09-07**: `_next_hypothesis_id()` now reads the highest numeric suffix among distinct hypothesis_id values already in the ledger (status updates reuse an id, never mint a fresh one) instead of counting total lines appended. Verified against a scratch ledger reproducing the exact gap scenario (a hypothesis with one status update followed by a fresh hypothesis correctly got hyp-000002, not hyp-000003). The real ledger file was not touched or rewritten -- this only changes how the NEXT id is computed going forward.

- **score_results.py's profit_factor unit mismatch** — found 2026-08-24, while reviewing exp-025. **Already closed 2026-09-01** (this backlog entry was stale): `score_results.py` now prints both the original raw-points profit factor and an R-multiple-normalized version side by side, with the R version called out as the one to prefer. Confirmed still present and correct on 2026-09-07.

- **research_ledger.py has no `search_batch_id` field** -- found 2026-09-03. **Closed 2026-09-07**: `HypothesisRecord` gained a `search_batch_id` field (optional, set by the calling script when multiple hypotheses come from one joint run); `larry_validate.py`'s `evaluate_candidate()` now tries an exact batch-based sibling count first and only falls back to lineage-walking when no batch id is set. `n_trials_override` still exists as a manual escape hatch. Verified with a scratch-ledger test: a 2-hypothesis batch with different immediate parents was correctly counted as 2, and a hypothesis with no batch id correctly fell through to the old lineage logic. Existing ledger rows (hyp-000007/hyp-000008 included) are untouched and keep using their documented `n_trials_override` -- this is additive, not a retroactive rewrite.

## Tested / Closed

- **exp-051: Cross-asset diversified test of the weekly trend signal**
  -- tested 2026-09-07, once ZN/6E/CL data was purchased ($19.14
  total). Result: kill (hyp-000021). Mean weekly portfolio net return
  was positive (+0.0003/week, inverse-vol-weighted across NQ/ZN/6E/CL)
  but the 90% confidence interval crossed zero, so it doesn't clear
  the statistical-credibility gate. Per the pre-registered follow-up
  plan (frozen spec Section 11), this is a clean kill, not followed by
  parameter variants on this same construction. A real bug was found
  and fixed during this run: WTI crude legitimately traded negative on
  2020-04-20/21 (the well-known May-2020 contract expiry event), which
  broke the log-return math and silently produced a NaN "kill" on the
  first pass -- fixed as a general validity guard (non-positive
  reference close treated as no usable close), re-run once, real
  result recorded. See `research/studies/cross-asset-weekly-trend-scoping.md`
  and the ledger (hyp-000021) for full detail.

## Shelved

- **Weekly trend-following signal family on NQ (exp-047, exp-048, exp-049)** -- shelved
  2026-09-06 per a pre-committed rule. exp-047 (raw weekly momentum sign) was this
  project's closest-ever near-miss (mean +19.38 pts/week, 90% CI [-1.165, +40.414]).
  Two follow-on risk-management overlays were tested at Jason's request: exp-048 (a
  hard +2R take-profit cap) and exp-049 (a 1R trailing stop activated at +2R) --
  both came back kills with nearly identical means (~+10.2-10.5 pts/week, both CIs
  spanning zero), roughly half the raw signal's mean, because both overlay designs
  remove the small number of large trending weeks that drive this signal's edge.
  Per the frozen spec's pre-commitment (named before either follow-on result
  existed), two follow-on attempts on the same near-miss without a clear,
  comfortable pass is the stopping point -- not followed by further parameter
  variants (e.g. a wider trail distance), which would be a post-hoc search for the
  variant that clears the bar. Revisit only via an entirely new, independently
  pre-registered hypothesis (a materially different design, or a prospective test
  on new future data) -- not a continuation of this family.

## Rejected

- **Order-flow / buying-vs-selling-pressure signals** -- closed out 2026-09-07
  at Jason's explicit request (drop it entirely, don't keep bringing it up).
  Previously parked 2026-09-03 after being priced out at ~$54,000/year for the
  historical depth this project's methodology needs (see git history / prior
  versions of this file for the full pricing detail). Moved from Parked to
  here, not just left sitting -- Jason wants this off the list of things that
  keep resurfacing as an option, not merely deprioritized.
