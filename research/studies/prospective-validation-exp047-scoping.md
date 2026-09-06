# Prospective Validation of the Weekly Trend-Following Signal -- exp-050

## Status: v2 APPROVED by Jason (2026-09-06, "let's run it") and cleared by the Path-to-Profitability Advisor conditional on the v1->v2 changes below. Ready to build.

## 1. Provenance

Directly from the Path-to-Profitability Advisor's own recommendation
during the 2026-09-06 "what's next for the whole project" consultation,
which Jason then authorized. Not a new hypothesis -- the signal itself
(exp-047: sign of trailing 52-week cumulative log return, weekly
rebalance) is completely frozen and unchanged. What's new is HOW it is
being evaluated: on data that did not exist at freeze time, tracked
forward in real time, rather than re-tested against any data already
on disk.

## 2. Why this is not just "Holdout Gen 2 access"

This project already has two reserved, budgeted, not-yet-spent
out-of-sample slices (Validation: 2021-10-04 -> 2024-01-03; Holdout
Gen 2: 2024-01-04 -> 2026-04-06) plus a legacy Holdout Gen 1 slice
(2026-04-07 onward, partially already on disk). exp-047 never cleared
the Discovery-slice promotion bar -- it was a near-miss, logged
REJECTED. Only a promoted candidate earns access to a finite holdout
slice; spending Validation or Holdout Gen 2 on a rejected hypothesis
would waste a scarce resource on something that didn't earn it, and
using the already-on-disk portion of Holdout Gen 1 would not even be a
genuine out-of-sample test any more.

So: this test uses NONE of those reserves.

## 3. FREEZE ANCHOR (v2 change -- Advisor-required)

v1 used a calendar date (2026-09-06) as the freeze point. The Advisor
correctly flagged that this is not the same claim as "no data existed
yet": routine re-runs of `data_fetch_databento.py` for other purposes
could in principle have already pulled bars between the last on-disk
date and the calendar freeze date, which would make the "impossible to
have been influenced, even unconsciously" claim in v1 too strong.

**Fixed anchor: the exact timestamp of the LAST bar present in any data
file on disk at the moment this v2 document is signed off:**

    2026-08-19 19:59:00 America/New_York

(confirmed 2026-09-06 by reading the last row of
`data/NQ_1min_databento_2026-08-20.csv`, the active data file).

This exact timestamp is recorded here AND in the ledger entry below.
`src/study_prospective_exp047.py` (Section 5) hard-asserts (raises, does
not silently skip) if it is ever asked to log a week containing any bar
at or before this timestamp. Only bars strictly after it count as
"prospective." This also means the ~4.5 months of Holdout Gen 1 data
already on disk (2026-04-07 -> 2026-08-19) is explicitly NOT used here
and remains fully reserved for its original purpose.

## 4. Reuse over invention

100% reused, unmodified: `compute_weekly_momentum_signal`,
`resample_to_weekly_closes`, `compute_weekly_log_returns` (from
`study_nq_weekly_trend_following.py`), and `compute_positions`,
`FLIP_COST_POINTS`, `analyze_primary` (including its `bootstrap_mean_ci`
helper -- same n_bootstrap, same seed, same nonparametric resample
convention), `robustness_drop_largest_pnl_day`, `robustness_split_half`
(from `study_nq_trend_following.py`). This is the RAW exp-047 signal
exactly as originally tested -- no ATR overlay, no stop-loss, no
take-profit, no trailing exit (both overlay variants already failed
independently and are shelved; carrying either forward would be
re-testing a killed variant under a new label).

## 5. What "running" this actually means, mechanically

1. New 1-minute NQ bars are pulled forward via the existing
   `data_fetch_databento.py` (no new fetch logic needed). This has a
   small, real, recurring dollar cost (Databento is paid). **Cadence
   and cost authorization is explicitly NOT decided in this document --
   that is Jason's call to make separately, each time or as a standing
   authorization, outside this design's scope.**
2. `src/study_prospective_exp047.py` (new script): for each ISO week
   whose data is fully available and entirely after the freeze anchor
   (Section 3), computes the exact same weekly momentum signal using
   only data through the end of the most recently CLOSED week (causal,
   no lookahead -- identical convention to exp-047), and appends one row
   to `research/ledger/prospective_exp047_log.jsonl`: iso week, position
   (+1/-1), realized weekly price change, net P&L, whether a flip cost
   was incurred. Raises (does not silently skip) if asked to process a
   week touching the freeze-anchor timestamp or earlier.
3. Idempotent and safe to re-run any time -- only appends rows for
   newly-closed, not-yet-logged weeks.
4. **Tamper evidence (v2 addition):** every append to
   `prospective_exp047_log.jsonl` is committed to git in its own commit
   (never squashed/amended), same convention already used for
   `research/ledger/hypotheses.jsonl` -- git history is the tamper-
   evidence mechanism; a later edit to a historical row is visible as a
   diff against a dated commit.
5. **Governance note (v2 addition):** no other study or script in this
   project computes or publishes exp-047's performance over the
   prospective window independently of this mechanism. A second,
   informal "how's exp-047 doing" calculation run elsewhere would be a
   backdoor look that could bias checkpoint discretion even if this
   script's own interim-look discipline is followed perfectly.

## 6. Pre-committed interim-look discipline (v2 -- fully specified)

- **Statistic:** the CUMULATIVE (from the freeze anchor, not a trailing
  window) 90% bootstrap CI of net weekly P&L, using the exact same
  `bootstrap_mean_ci()` function exp-047 used (same seed, same
  n_bootstrap). Recomputed each time the script runs.
- **Early-kill rule (the only permitted interim action other than
  infrastructure health checks):** if the cumulative 90% CI is entirely
  below zero (BOTH bounds negative, not just the lower bound) for 26
  consecutive logged weeks, that is an early, honest kill. One-sided --
  there is no equivalent early-PASS rule, since no real capital is at
  risk during tracking (paper/log only) and continuing to track a
  signal already showing a sustained, decisively negative real-time
  result has no research value.
  - **Justification for "26 consecutive weeks" (v2 addition, per the
    Advisor's request for a stated rationale rather than an arbitrary
    number):** simulated under a null (mean-zero, iid weekly returns,
    SD ~218.5 pts -- the value implied by exp-047's own realized CI and
    n), checking the cumulative-CI-entirely-below-zero condition every
    week from week 2 through week 104, requiring a run of 26
    consecutive weeks before triggering gives a false-kill rate of
    ~5.0% over the full 104-week window (20,000-path Monte Carlo,
    normal approximation to the bootstrap for tractability) -- in the
    same ballpark as a single clean hypothesis test at the 5% level,
    despite continuous weekly monitoring. (For reference: 13 weeks
    would give ~9.5%, 52 weeks ~1.7% -- 26 was chosen as the point
    where continuous monitoring's false-kill inflation is brought back
    down to roughly a single-look rate, without waiting so long that a
    genuinely dead signal keeps getting tracked for another year.)
- **No other interim decision of any kind.** Looking at the log to
  confirm it's running correctly (no missed weeks, no data-quality
  breaks) is always fine; using an interim look to informally judge
  progress, or adjusting anything based on what interim rows show, is
  not.

## 7. Pre-registered checkpoint schedule (v2 -- full schedule, not just the first checkpoint)

Checkpoints at **104 / 156 / 208 weeks** from the freeze anchor. At each:
re-run the exact same two-part exp-047 promotion bar (90% CI entirely
above zero AND net P&L >= 2x the currently realized average cost drag,
recomputed prospectively each time -- same formula as exp-047, not a
fixed carried-over number).
- Clears both at any checkpoint -> becomes `VALIDATION CANDIDATE`
  (Research Ledger status scale) -- live authorization, position
  sizing, real capital all become a SEPARATE decision with Jason at
  that time, not implied by this document.
- Does not clear, or inconclusive, at 104 or 156 weeks -> continue to
  the next pre-registered checkpoint automatically -- no new decision
  needed, no re-litigating the plan.
- **Hard maximum horizon: 260 weeks (~5 years) from the freeze anchor.**
  If the 208-week checkpoint doesn't clear, tracking continues to 260
  weeks as the final look; at 260 weeks, regardless of how promising or
  inconclusive the result looks, this mechanism formally closes -- pass,
  fail, or "still ambiguous" all get logged as the final, terminal
  verdict at that point. No open-ended "keep going a bit longer"
  extension. This removes the exact decide-after-seeing-the-result gap
  the Advisor flagged in v1.

## 8. Multiple-testing / ledger accounting

Own hypothesis ID: **exp-050 / hyp-000020**, status `FORWARD VALIDATION`.
`data_slice_used`: **`"prospective"`** -- a new fifth value being added to
`research_ledger.py`'s `VALID_DATA_SLICES` (previously `discovery` /
`validation` / `holdout_gen1` / `holdout_gen2`), with an explicit,
code-level guard (not just documentation) that a `"prospective"` record
can never be treated as satisfying a Validation or Holdout requirement
for any other hypothesis.

## 9. What this is NOT

- Not a new hypothesis search -- the signal is 100% frozen, identical
  to exp-047.
- Not spending any of this project's budgeted Validation, Holdout
  Gen 2, or already-existing Holdout Gen 1 allocations.
- Not a promise of a fast answer -- explicitly a multi-year mechanism.
- Not authorization for live trading or real capital -- paper/tracking
  only. A future pass at any checkpoint is the START of a separate
  live-authorization conversation, not the end of one.
- Not a decision about the Databento re-fetch cadence/cost -- left
  explicitly to Jason, outside this document's scope.
- Not open to a "let's just see how it's going" informal read that
  changes the checkpoint schedule, the early-kill rule, or the 260-week
  maximum horizon after the fact.

## 10. ASCII-only

Confirmed.

## Advisor review (2026-09-06)

v1 was reviewed and returned "cleared with changes, not cleared as-is."
Required changes, all incorporated above: (1) replace the calendar
freeze date with the exact last-on-disk-bar timestamp, with a hard
assertion guard in the script; (2) fully specify the interim-look
statistic (cumulative CI, same bootstrap function) and give a
simulation-based rationale for the 26-consecutive-week early-kill
threshold rather than an arbitrary number; (3) pre-register the FULL
checkpoint schedule (104/156/208 weeks) plus a hard 260-week maximum
horizon, closing the "decide after seeing the 104-week result" gap.
Recommended additions also incorporated: a code-level guard preventing
`"prospective"` records from substituting for Validation/Holdout
requirements; tamper-evidence via git-commit-per-append (matching this
project's existing ledger convention); an explicit statement that the
economic-meaningfulness threshold is the same formula (2x realized cost
drag) recomputed prospectively, not a fixed carried-over number; and a
governance note against any other concurrent, independent computation
of exp-047's prospective-window performance. With all of the above, the
Advisor's verdict was: cleared to build.
