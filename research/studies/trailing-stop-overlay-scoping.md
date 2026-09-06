# Trailing-Stop Variant of the Weekly Trend Overlay -- exp-049

## Status: v1 built and TESTED. Result: kill. exp-047 signal family now SHELVED per pre-commitment.

Directly follows exp-048's kill: the Advisor's own recommended next step was
a trailing exit that participates in the tail rather than capping it, as a
genuinely new, freshly pre-registered hypothesis -- not a retune of exp-048.
Jason authorized proceeding straight to building this, delegating the
specific design to the Advisor's review, per the same pattern used for
exp-048's final design decision.

## 1. Provenance

Directly from the Advisor's own suggested next step after exp-048's kill,
which Jason then authorized. Not a retune of exp-048 -- a materially
different exit mechanism (ratcheting trail vs. hard cap), pre-registered
fresh.

## 2. Reuse over invention

Reuses, unmodified: exp-047's weekly signal/positions (direction 100%
inherited, unchanged), the 20-day-ATR risk unit (1R) and -1R stop-loss
definition from exp-048, the same cost accounting and analyze_primary()/
robustness functions. What's new: once a position's favorable excursion
reaches +2R intraweek, the stop-loss level is replaced by a trailing stop
that ratchets in the favorable direction, using the SAME 1R distance
already defined (no new free parameter).

## 3. Every free parameter pinned down before any result exists

- Entry/direction/1R sizing/-1R initial stop: unchanged from exp-048.
- Trail distance: the same 1R already defined for the stop-loss -- not a
  new number.
- Trail activation: once running peak favorable excursion (long: highest
  bar High since entry; short: lowest bar Low since entry) reaches the
  same +2R level exp-048 used to define its hard cap.
- **Explicit per-bar algorithm (long position; short is the mirror image),
  walking the entry week's 1-minute bars in chronological order, causal
  with no same-bar lookahead:**
  1. At the start of each bar, the exit level in force is `current_stop`,
     whatever it was set to at the END of the previous bar (initially
     `entry_price - 1R`, matching exp-048's stop exactly).
  2. Check this bar's Low against `current_stop`. If touched, exit at
     `current_stop` (fill price = the touched level exactly, no slippage
     -- identical convention to exp-048). Done for this week.
  3. If not touched: update `peak = max(peak, this bar's High)`.
  4. If the trail has not yet activated and `peak >= entry_price + 2R`
     (the same activation level exp-048 used for its hard cap): activate
     the trail.
  5. If the trail is active: `current_stop = max(current_stop, peak - 1R)`
     (ratchets tighter only, never loosens) -- this becomes the level
     checked in step 2 of the NEXT bar.
  6. If the week ends with no exit triggered, exit at the normal weekly
     rebalance price -- identical to exp-047/048's "neither touched" case.
  This ordering (check exit using the PRIOR bar's level, then update
  peak/trail using the CURRENT bar) is what removes same-bar ambiguity:
  a bar cannot be stopped out by a trail level it itself just set.
- Peak/trough measurement basis: bar High/Low (matches exp-048's own
  touch-detection basis for the -1R stop and +2R target exactly -- not a
  more or less favorable basis).
- Fill-price convention: exit exactly at the touched level (stop, trail,
  or normal rebalance price) -- identical to exp-047/exp-048, no slippage
  modeled.
- Promotion bar: same adapted bar as exp-047/048, but read AT LEAST AS
  STRICTLY as exp-048's stricter follow-on reading -- this is now the
  THIRD test in a family built on one near-miss (exp-047), and the SECOND
  follow-on attempt specifically targeting the tail-capture mechanism.

## 4. Known risks and reasons for skepticism, disclosed up front

- This is a genuinely new, if parameter-free, exit RULE SHAPE
  ("activate at +2R, trail by 1R") that has never been tested, even
  though both numbers involved are inherited. A clean result either way
  should not be read as having been "obviously going to happen" -- it's
  a real test of a real, previously-untested combination.
- Still cannot manufacture directional edge that isn't there. Direction
  is 100% inherited from exp-047, itself a near-miss, not a confirmed
  edge.
- Per the Advisor's explicit framing: if this also comes back a kill or
  another near-miss, the exp-047 signal family (weekly trend-following on
  NQ) is SHELVED after this -- not followed by an exp-050 variant. Three
  attempts on one underlying near-miss without a clear, comfortable
  promotion is the pre-committed stopping point for this line of work,
  decided now, before this result exists, specifically so this doesn't
  become a search for the variant that happens to clear the bar.

## 5. Path from result to verdict

Same two checks as exp-047/048 (90% bootstrap CI entirely above zero, AND
economically meaningful vs. cost drag), read at least as strictly as
exp-048's follow-on reading -- a narrow/technical pass, or a mean
materially below exp-047's own raw-signal mean, is not treated as
clearing the bar.

## 6. Discovery/Validation/Holdout discipline

Discovery slice only, matching every other hypothesis.

## 7. Multiple-testing accounting

Gets its own exp-049 number and Research Ledger entry
(`strategy_origin: "derivative"`, linked to hyp-000017/exp-047 and
hyp-000018/exp-048). Explicitly the third test in this family --
counted as such, not as an independent trial.

## 8. What this is NOT

- Not a claim this will succeed -- exp-048 already showed this signal's
  edge depends on tail weeks a hard cap removes; whether a trail
  preserves enough of that tail to matter is an open, honestly-tested
  question, not assumed.
- Not license for an exp-050 if this also fails -- per Section 4, this
  family is shelved after this result either way (unless a comfortable,
  clear pass).
- Not authorized to be re-parametrized (different trail distance,
  different activation level) if this comes back null -- same
  pre-commitment discipline as exp-048.

## 9. ASCII-only

Confirmed.

## Advisor review (2026-09-06)

The Advisor confirmed this design resolves both objections raised against
a trailing exit at the exp-048 design stage (no cross-week position state;
no new, untested free parameter -- the trail reuses the same disclosed
1R). One precise addition was required before building: the explicit,
written per-bar algorithm in Section 3 above (same-bar ordering,
high/low measurement basis, fill-price convention, rebalance-bar
interaction), each pinned to match exp-048's existing convention exactly.
With that documented, the Advisor cleared this design to build as scoped,
and recommended reading the promotion bar at least as strictly as
exp-048's, with an explicit pre-commitment (Section 4) to shelve this
signal family after this result if it is not a clear, comfortable pass.


## Result (2026-09-06, exp-049)

Built and run exactly as scoped, per the Advisor-cleared per-bar algorithm
in Section 3.

**Exit-path breakdown:** stopped_or_trailed 148 weeks (49.5%), neither
(exits at normal weekly rebalance) 151 weeks (50.5%).

**Primary result: mean weekly net P&L +10.20 points, 90% bootstrap CI
[-6.88, +27.87]** -- spans zero, not statistically credible. Economically
meaningful on the mean alone, which per Section 4/5's stricter bar does
not clear this on its own.

**Direct comparison across the whole family:**
- exp-047 (raw signal, no overlay): mean +19.38, CI [-1.165, +40.414]
- exp-048 (hard +2R cap): mean +10.53, CI [-6.37, +28.38]
- exp-049 (this test, 1R trail activated at +2R): mean +10.20, CI [-6.88, +27.87]

exp-049's mean is nearly IDENTICAL to exp-048's -- despite giving the
position room to run past +2R rather than capping it there. This was NOT
the going-in expectation (a trail was expected to preserve more of the
raw signal's edge than a hard cap).

**Diagnostic run on already-generated data (not a new test, per the
Advisor's request before accepting this result as final):** of the 148
stopped_or_trailed weeks, the exit R-multiple distribution shows 136
weeks (91.9%) exited at almost exactly -1R -- i.e., the plain initial
stop-loss, with the trail never even activating. Only 12 weeks ever
reached the +2R trail-activation level at all, and of those, most
trailed out shortly after activation (rounded R-multiple histogram:
-1R x136, +1R x8, +2R x3, +3R x1). This confirms the mechanism is
implemented correctly (no bug) -- the trail simply almost never gets a
chance to do its job, because a 1-times-ATR retracement from an
intra-week peak is a fast, common event on NQ's weekly volatility, so
the trail behaves almost exactly like a hard cap in practice. The
honest reading, per the Advisor: this specific trail distance (1R) is
too tight relative to NQ's weekly ranges for a trailing exit to
meaningfully out-perform a hard cap here -- not evidence that trailing
exits can never work.

**Robustness:** dropping the single largest week (2021-W05) reduces the
mean to +7.96 (CI [-8.75, +24.83], still spans zero). Split-half: first
half mean +6.30 (CI [-6.56, +20.22]), second half mean +14.07 (CI
[-17.93, +45.91], much wider) -- both individually span zero.

**Verdict: kill.**

**Advisor's independent assessment, confirmed:** the near-identical means
of exp-048 and exp-049 is actually stronger evidence than either result
alone -- it shows the problem is not an artifact of one specific capping
mechanism, but that exp-047's already-marginal edge is concentrated in a
small number of large trending weeks, and any overlay tested so far that
limits how far a winning week can run (whether by hard level or by
trailing giveback) removes enough of that tail to break the confidence
interval.

**Per the pre-committed rule in Section 4 of this document: the exp-047
signal family (weekly trend-following on NQ, in all overlay variants
tested) is now SHELVED.** This is the second follow-on attempt on the
same underlying near-miss without a clear, comfortable pass -- the
pre-registered stopping point. The obvious next idea (try a wider trail
distance, since 1R turned out too tight) is explicitly NOT pursued here,
per the Advisor's direct warning that doing so would be a third
follow-on attempt and exactly the kind of post-hoc parameter search
(testing progressively looser parameters until one clears the bar) the
pre-commitment exists to prevent. A materially different trail distance
would need to be scoped as an entirely new, independently pre-registered
hypothesis in the future, not a continuation of this family. Logged to
the research ledger as hyp-000019 (REJECTED). See
`src/study_trailing_stop_overlay.py` for the full implementation.
