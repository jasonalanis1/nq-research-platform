# Asymmetric Stop-Loss/Take-Profit Overlay on the Weekly Trend Signal -- exp-048

## Status: v2 APPROVED by Jason (2026-09-06, via explicit delegation to the Advisor's recommendation on the final open design question) and TESTED. Result: kill.

Candidate ID (if approved): exp-048. Written per the Research Scoping Agent
process (`docs/RESEARCH_SCOPING_AGENT.md`), directly implementing Jason's own
risk-management idea (paraphrased: "if I put in $100, I'm willing to lose up
to $75 before I sell, but if it's going up, I hold until I've at least
doubled my winnings before selling") applied concretely to exp-047, the
weekly trend-following signal that is this project's closest near-miss to
date. v2 incorporates six changes required by the Path-to-Profitability
Advisor's independent review of v1 (see "Advisor review" section at the end)
before this is ready for Jason's line-by-line sign-off.

## 1. Provenance

Directly from Jason's own explicit idea, raised during a 2026-09-06
conversation about whether the project's whole approach needed to change.
Not sourced from an outside claim. Applied to exp-047's signal specifically
because it is the one signal in this project's 24-hypothesis history that
came close to clearing the promotion bar -- disclosed plainly in Section 4
below as a selection-risk choice, not a neutral one.

## 2. Reuse over invention

Reuses exp-047's weekly momentum-sign signal completely unmodified (52-week
trailing lookback, ISO-week resampling, same sign-based long/short
direction) as the ENTRY signal only -- direction is 100% inherited from
exp-047, unchanged. What's new: instead of exp-047's simple "hold the full
week, P&L = that week's price change," this test defines an explicit
stop-loss and take-profit level at entry, checked against real intraday
price data (1-minute bars, already available) during the holding week.

## 3. Every free parameter pinned down before any result exists

- **Entry**: same as exp-047 -- start of each classifiable week, direction
  = sign of the trailing 52-week log return.
- **Risk unit (1R)**: a trailing 20-day Average True Range (ATR) as of the
  first trading day of the entry week, computed from existing daily
  OHLC data (aggregated from the 1-minute series already on hand). Chosen
  over a fixed point value because NQ itself ranged roughly 4,000-16,000+
  across the Discovery window -- a fixed point stop would mean wildly
  different risk at different times. 20 days (not the more standard
  14-day textbook default) is used because it more closely matches this
  signal's own ~52-week (slow) rebalancing cadence; this is a real,
  disclosed free choice, not empirically tuned -- see Section 4 for the
  pre-commitment that this will not be revisited based on the result.
- **Stop-loss**: -1R from entry (mirrors "willing to lose up to 75% of
  stake," normalized to a risk-multiple rather than a dollar amount so it
  isn't tied to one specific account size).
- **Take-profit**: +2R from entry, as a HARD cap (mirrors "at least
  doubled winnings" as a fixed target rather than a trailing/ratcheting
  exit). Flagged explicitly in Section 4 as a real design tension, not an
  oversight.
- **Path check**: walk forward through the entry week's 1-minute bars in
  chronological order. Whichever level (stop or target) is touched first
  determines the exit. If a single bar's high/low range touches both
  levels at once, the stop is conservatively assumed to trigger first
  (standard industry convention for same-bar ambiguity, not something to
  resolve in the strategy's favor). If neither level is touched during
  the entry week, exit at the normal weekly rebalance point, identically
  to exp-047 (no stop/target realized that week).
- **Weekend/gap handling**: the intraday path check only runs during
  the week's actual trading-session bars already present in the data (no
  synthetic overnight/weekend path is invented). If the position gaps
  through both levels between one bar and the next (e.g., over a
  weekend), the FIRST level reached in price terms by the new bar's
  open is treated as the trigger -- pinned now, not decided after seeing
  results.
- **Multi-week holds**: a stop/target set at entry is evaluated ONLY
  within that single entry week. At the next weekly rebalance point, if
  neither level was touched, the position (and its stop/target) resets
  fresh for the new week using a newly-computed ATR and the new week's
  entry price -- it does not carry over unresolved across multiple weeks.
- **Cost accounting**: identical to exp-047 -- `FLIP_COST_POINTS` charged
  only on weeks where the direction itself flips from the prior
  classifiable week, reused unmodified.
- **Promotion bar**: the same adapted bar precedent (90% bootstrap CI on
  the resulting P&L series entirely above zero, AND economically
  meaningful vs. cost drag) -- but see Section 4 for why this needs to be
  read more strictly here than it was for exp-047 itself, given this is a
  follow-on test of a near-miss, not an independent first test.

## 4. Known risks and reasons for skepticism, disclosed up front

- **This is a form of selection risk / multiple-testing exposure that
  must be named plainly, not glossed over.** exp-047 was not chosen for
  this overlay because trend-following signals are theoretically the
  best candidate for a stop/target structure -- it was chosen because its
  confidence interval happened to come closest to clearing zero, out of
  24 prior tries. Building this overlay on exp-047 is, functionally, a
  second test on the same near-miss data, wearing a new hypothesis ID.
  Per the Advisor's explicit recommendation, this bar is read more
  strictly here than it would be for an independent first test: a
  narrow pass (CI barely above zero) is NOT being treated as sufficient
  to promote -- only a clear, comfortable pass, well clear of zero on
  both ends, would be treated as a real signal rather than noise from a
  second roll of the dice on the same near-miss.
- **A hard +2R take-profit may cap exactly the tail returns that make a
  trend-following signal work in the first place.** Trend followers
  typically make their money from a small number of large winning moves,
  not from a high win rate. A hard cap at +2R gives away that tail. The
  pilot tabulation below (Section 4a) shows this is not a theoretical
  concern -- it happens on a meaningful share of weeks. This is a known,
  named risk of the design, not a bug to fix quietly if the result comes
  back weak.
- **20-day ATR and the 2:1 reward:risk ratio are free parameters that
  must not be tuned after seeing a result.** Pre-commitment, stated
  plainly: if exp-048 comes back null (fails either the statistical or
  economic check) under these exact parameters, the conclusion is "a
  hard stop/target overlay does not turn this near-miss into a clear
  pass" -- full stop. It does NOT license trying a different ATR window,
  a different R:R ratio (e.g. 1.5:1 or 3:1), or a trailing exit instead
  of a hard cap, on this same Discovery data. Any of those would be
  exactly the kind of after-the-fact parameter search this project's
  rules exist to prevent. A different structure (e.g., a trailing stop
  instead of a hard target) is a genuinely different hypothesis and
  would need its own fresh scoping and its own honest accounting of how
  many things have now been tried on this same signal -- not an
  automatic next attempt.
- **This still cannot manufacture directional edge from nothing.** The
  underlying direction call is unchanged from exp-047, which itself was
  a near-miss, not a confirmed edge. The single most likely outcome,
  stated honestly before this is run, is that this also comes back null
  -- quite possibly with a wider, noisier confidence interval than
  exp-047's own, since path-dependent stops/targets add a real new
  source of variance on top of an already-thin signal.

### 4a. Pilot tabulation (descriptive only -- run 2026-09-06, NOT a promotion-relevant result)

Per the Advisor's explicit recommendation, before any parameter is locked
for Jason's sign-off, a purely descriptive pass was run showing how
exp-047's 299 classifiable weeks resolve under the exact rule above (1R
stop / 2R target / 20-day ATR). This reports counts only -- no P&L, no
verdict, not logged to the research ledger (same convention as other free,
descriptive Step-1 checks in this project, e.g. exp-043/044's Step 1):

- Stop hit first: 136 weeks (45.5%)
- Target hit first: 42 weeks (14.0%)
- Neither hit (exit at normal weekly rebalance, as in exp-047): 121 weeks
  (40.5%)
- Median 1R (20-day ATR) at entry: ~109 points; mean ~140 points (wide
  range, 37-545 points, reflecting NQ's own price-level and volatility
  changes across 2015-2021)

This confirms the tail-capping concern in Section 4 is real and material,
not hypothetical: fewer than 1 in 7 weeks ever reach the +2R target,
while nearly half stop out at -1R first. Whatever exp-048 concludes, this
distribution -- not just the final P&L number -- should be part of what
Jason sees before deciding whether a hard 2R cap is the structure he
actually wants tested, versus a trailing exit (a different, not-yet-scoped
hypothesis).

## 5. Path from result to verdict

Same two checks used throughout this project, applied more strictly per
Section 4:
1. Statistical check: 90% bootstrap CI on the resulting weekly net P&L
   series (now path-dependent: -1R, +2R, or the unresolved week's actual
   price change) -- must be comfortably above zero, not merely
   technically above zero, given this is a follow-on test of a
   near-miss.
2. Economic check: mean weekly net P&L against the same cost-drag-relative
   threshold precedent.
Both must clear, comfortably, for anything beyond "null." If either check
is a narrow/borderline pass, this will be reported to Jason and the
Advisor as an inconclusive near-miss requiring explicit discussion, not
promoted on a technicality.

## 6. Discovery/Validation/Holdout discipline

Discovery slice only, matching every other hypothesis. No Validation-slice
test unless this clears both checks above, comfortably.

## 7. Multiple-testing accounting

Gets its own exp-XXX number (exp-048, if approved) and Research Ledger
entry (`strategy_origin: "derivative"`, `parent_hypothesis_id` linked to
hyp-000017/exp-047). Explicitly logged and disclosed as a second test on
the same near-miss signal, per Section 4 -- counted as such in any future
accounting of how many things have been tried in this project, not as an
independent 25th trial.

## 8. What this is NOT

- Not a claim this will succeed -- if anything, the honest prior is
  slightly against it, for the reasons in Section 4.
- Not a new directional signal -- direction is 100% inherited from
  exp-047, unchanged.
- Not license to try a different ATR window or R:R ratio if this specific
  version fails -- see the pre-commitment in Section 4.
- Not a trailing-stop design (which would better match "at least doubled
  winnings" literally) -- that is a distinct, not-yet-scoped hypothesis,
  noted here as a possible future direction only if Jason specifically
  wants it scoped separately, not as a fallback if exp-048 fails.
- Not authorized to be built. Needs Jason's own explicit, line-by-line
  sign-off on the parameters above (especially the 20-day ATR window and
  the hard 2:1 R:R cap, both free choices not present in exp-047) before
  any model code is written, per this project's standing frozen-spec
  discipline.

## 9. ASCII-only

Confirmed.

## Advisor review (2026-09-06)

The Path-to-Profitability Advisor reviewed v1 of this draft independently
and identified six required changes before this would be ready for
Jason's sign-off, all incorporated into this v2:
1. Explicitly disclose the selection-risk/multiple-testing exposure of
   applying this overlay specifically to exp-047 (the closest near-miss)
   -- done, Section 4.
2. Justify or change the 20-day ATR window -- justified (tied to the
   signal's own weekly cadence) rather than left as an unexplained
   default, Section 3.
3. Flag the hard +2R take-profit's tail-capping risk explicitly rather
   than treating it as a detail -- done, Section 4, and quantified via
   the pilot tabulation, Section 4a.
4. Pin the weekend/gap-risk rule up front -- done, Section 3.
5. Add an explicit pre-commitment that a null result closes this line of
   inquiry rather than inviting parameter retuning -- done, Section 4.
6. Run and disclose a purely descriptive pilot tabulation of how the 299
   exp-047 weeks resolve under the proposed rule, so Jason approves
   parameters with the resulting sample-size tradeoff visible, not blind
   -- done, Section 4a.

The Advisor's full independent review is available on request; its core
judgment, in its own words: "worth building only with the [six] named
changes... with those... this is a reasonable, disciplined test of a
genuinely different question... and is worth building. As currently
scoped [v1], it has the right instincts... but under-discloses its own
selection bias and glosses over a real design flaw (tail-capping)."


## Result (2026-09-06, exp-048)

Built and run exactly as scoped in v2, hard-cap design per the Advisor's
explicit recommendation (Section "Advisor review" above). Reused exp-047's
signal/position machinery completely unmodified; new code limited to the
20-day ATR risk-unit calculation and the intraday path-dependent stop/target
exit resolution.

**Exit-path breakdown** (matches the pre-registered pilot tabulation in
Section 4a exactly, confirming the path logic was not altered between the
pilot and the full run): stop hit first 136 weeks (45.5%), target hit first
42 weeks (14.0%), neither touched 121 weeks (40.5%).

**Primary result: mean weekly net P&L +10.53 points, 90% bootstrap CI
[-6.37, +28.38]** -- spans zero, not statistically credible. Economically
meaningful on the mean alone (threshold was 0.22 pts), but per Section 4's
stricter follow-on-test bar, an economic pass alone does not clear this.

**Direct comparison to exp-047 (the same signal, no overlay):** exp-047's
mean was +19.38 pts/week with CI [-1.165, +40.414]. The overlay's mean is
roughly HALF of the raw signal's, and its CI is WIDER on both ends, not
narrower -- despite adding defined risk management.

**Robustness:** dropping the single largest week (2020-W16) reduces the
mean further to +8.60 (CI [-7.85, +25.09], still spans zero). A first-
half/second-half split shows both halves individually span zero, with the
second half's CI ([-16.63, +48.82]) much wider than the first's.

**Verdict: kill.** Per this document's pre-committed interpretation
caveat: this rejects the SPECIFIC 1R-stop/hard-2R-cap/20-day-ATR design --
not Jason's underlying risk-management intuition in general.

**Advisor's independent sanity check (2026-09-06), confirmed:** the
implementation is sound (no leakage, refit, or scope creep -- the exit-
path counts matching the pilot exactly is expected and confirms
consistency). The "kill" classification is not a close call -- both
robustness cuts still span zero, one very widely. The result is the
expected signature of a hard take-profit cap on a fat-tailed trend-
following return distribution, not a new or surprising finding: trend-
following P&L is driven by a small number of large winning weeks, and a
hard cap at +2R systematically amputates exactly those weeks -- which is
why the mean roughly halved AND the confidence interval widened rather
than tightened (removing the large wins removes the observations that
were both raising the mean and narrowing the bootstrap distribution
around it).

**Honest bottom line, stated plainly per the Advisor's own words:** "this
result undercuts the original idea... The data says the opposite [of
improving the signal]: the overlay did not improve the risk/reward
profile, it degraded it... Weekly trend-following on NQ appears to derive
its edge from a small number of outsized trending moves, and a hard
take-profit is structurally the wrong tool to apply to that kind of return
distribution." This is a structural mismatch between the overlay design
and the signal's own source of edge, not evidence that the ATR window or
the R:R ratio needs adjusting.

**Per the pre-committed rule in Section 4: this line of inquiry is now
closed.** The ATR window and R:R ratio will not be retuned on this same
Discovery data. If Jason wants defined-risk management tested on this
signal in the future, the Advisor's recommended path is a genuinely
different, freshly pre-registered design (e.g., a trailing exit that
participates in the tail rather than capping it) -- a new hypothesis, not
a retune of exp-048. Logged to the research ledger as hyp-000018
(REJECTED). See `src/study_asymmetric_stop_target_overlay.py` for the
full implementation.
