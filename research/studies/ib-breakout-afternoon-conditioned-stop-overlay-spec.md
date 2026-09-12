# IB Breakout, Afternoon-Conditioned Stop-Width Overlay -- Frozen Spec (exp-127)

Queue item 0 (NEXT_UP.md, queued 2026-09-10, 08:15 session): a COSTED
CONDITIONING-OVERLAY STUDY using the midday-lull narrow-midday
characterization (hyp-000106 / OBS-FINDING-011), pairing it with an
EXISTING detected setup and conditioning its stop/target sizing, per the
Monetization position on hyp-000106 (research/sessions/2026-09-10-0815.md):
hyp-000106 is a volatility/range characterization, not a directional
signal, so it cannot be scored against the returns-based promotion bar
on its own -- it needs a costed overlay on a real setup to mean anything
economically.

Written 2026-09-10, automated session (4th automated run today). Every
section below is committed BEFORE any result is looked at.

## 1. LEARN consultation (Rule 5), by name

Checked research/infrastructure/agent-governance-structure.md and
docs/BACKLOG.md (the LEARN buckets' actual content lives in BACKLOG
prose, not a separate file -- confirmed no dedicated LEARN.md exists).

KNOWN FAILED / KNOWN FAILURE MODE directly relevant: "a conditioning
variable can't resurrect a signal that has no edge to condition"
(docs/BACKLOG.md "REAL FORK" entry). Four prior overlay screens exist:

  - exp-077/086/087 (hyp-000049 et al.): the 4 Level Sweep Reversal
    variants (already-REJECTED mean-reversion setups) split into
    groups by prior_day_narrow/wide/coiled_overnight flags. All CIs
    span zero. "Does not itself resolve whether the volatility-
    persistence finding has real economic value -- that still needs a
    proper costed overlay design on a live/future signal."
  - exp-093 (hyp-000065, parent hyp-000011): IB Breakout (already-
    REJECTED standalone, hyp-000011) split into wide-prior-day vs.
    rest. n=386 wide (mean -0.0543) vs n=1323 rest (mean -0.0724),
    diff +0.0181, ci_90 (-0.0883, 0.1281) -- not credible. "Closes this
    specific pairing for good."

KNOWN UNEXPLORED, still open as of this write: position_size_
multiplier() (src/volatility_conditioning.py, built 2026-09-08) --
"NOT a return claim... its real economic value is untested (no
promoted directional signal exists yet to size)." The Market Behavior
Advisor's own recorded recommendation (2026-09-08, docs/BACKLOG.md
"Intraday Behavior Batch 1" entry): "a position-sizing/stop-target-
width overlay on an existing directional signal (lower complexity,
doesn't require inventing a new directional edge) rather than a
standalone breakout-width rule." That specific design has never been
built. This study is the first attempt at it.

Resurrection ruling: NOT a resurrection of exp-077/086/087/093.
Those four are binary GROUP-SPLIT screens (partition existing trades
into two populations by a static day-level flag, compare mean
r_multiple_net between populations, same fixed stop/target
throughout). This study is a MID-TRADE, TIME-GATED STOP-WIDTH
ADJUSTMENT applied to the SAME trades under two policies (paired
design, not a two-sample split) -- mechanistically and statistically
distinct, and it is the specific design the Advisor recommended and
that has sat open in KNOWN UNEXPLORED for two days. It also uses a
volatility fact (hyp-000106, midday->afternoon persistence) that has
never been overlaid onto any directional setup before -- only
prior_day_narrow/wide and coiled_overnight have been tried.

## 2. Integrity Gate pre-clearance (Rule 5)

VERDICT: PASS, CONDITIONAL on tempered interpretation.

Conditions attached, binding regardless of outcome:
  - This is the 5th overlay-screen-family diagnostic on this project's
    2 confirmed volatility-conditioning facts against dead/marginal
    directional setups. 4 of 4 priors found nothing. Multiplicity
    awareness: a positive result here should be read with elevated
    skepticism, not celebrated as the first hit after 4 misses.
  - IB Breakout's own baseline economics are close to breakeven but
    net negative (~-0.065R blended, hyp-000011/exp-093 numbers) -- a
    stop-width overlay is a genuine, different mechanism from directly
    resurrecting directional edge, but it still cannot be expected to
    flip a net-negative setup solidly positive; a marginal, CI-crossing
    result should not be stretched into a promotion case.
  - Any credible positive finding here is NOT itself a promotion
    event. Per the exact precedent set in exp-093's own spec: it
    becomes its OWN new, separately pre-registered hypothesis (a
    "wide/narrow-afternoon-conditioned IB breakout stop overlay"),
    subject to its own Validation-slice prospective test before any
    further consideration. This diagnostic run alone can only ABANDON
    the pairing (null) or OPEN a new candidate line (credible) -- never
    promote anything by itself.
  - No spend, no Holdout slot, does not touch H118/EXP047, does not
    retune IB Breakout's closed standalone verdict (hyp-000011 stays
    REJECTED as-is).
  - SCAN_REGISTRY (src/project_wide_multiplicity.py) is unaffected --
    that registry tracks multi-cell Discovery Engine scans; confirmed
    neither exp-077/hyp-000049 nor exp-093/hyp-000065 (the direct
    precedents for this kind of single-pairing overlay diagnostic) are
    entries in it, so this diagnostic follows the same convention and
    is not itself a new scan requiring a registry row.

## 3. Base setup (reused, unmodified)

Initial Balance Breakout (src/detect_ib_breakout.py, hyp-000011,
REJECTED standalone). Reused unmodified: detect_ib_breakout_for_day(),
backtest.ROUND_TRIP_COST_POINTS. Entries 9:00-12:00 ET. Fixed stop =
opposite side of the 30-min Initial Balance range. Fixed target =
entry +/- 1.35R (TARGET_R_MULTIPLE). Discovery slice only
(data_split.get_discovery_data), matching every other hypothesis and
matching exp-093's own precedent exactly.

## 4. Conditioning fact (reused, unmodified)

get_afternoon_conditioning() / build_midday_afternoon_frame()
(src/volatility_conditioning.py), built from hyp-000106 / OBS-FINDING-011
(Validation-confirmed 2026-09-09, exp-126): narrow_midday (12:00-14:00 ET
range in the bottom 20th percentile of its own trailing 20-day window)
predicts a NARROWER afternoon range (multiplier 0.8161, Validation n=142,
ci_90 0.7615-0.8784); not-narrow predicts a slightly WIDER afternoon
range (multiplier 1.0910, Validation n=404, ci_90 1.0372-1.1473).
Explicitly documented in the module as "only meaningful from 14:00 ET
onward" -- this governs the causality rule below.

## 5. Causality constraint (why this can only be a MID-TRADE adjustment)

IB Breakout entries occur 9:00-12:00 ET, before the 12:00-14:00 ET
midday window the conditioning fact is computed from. Using the
afternoon-conditioning multiplier to set the INITIAL stop at entry
would be look-ahead (the midday session has not happened yet for any
IB Breakout entry). The only causally valid use is: for a trade STILL
OPEN when the first bar at/after 14:00:00 ET arrives (midday session
complete, conditioning now known), adjust the stop FROM THAT POINT
FORWARD only. Trades already exited (stop or target hit) before 14:00
are mechanically identical under both arms -- logged and reported
separately, excluded from the paired-difference test as uninformative
by construction (a difference of exactly zero for both, not evidence of
"no effect").

## 6. The exact overlay rule, pinned before any result exists

Two arms run over the IDENTICAL signal set (same entries, same original
stop, same target):

  UNCONDITIONED (baseline): backtest.simulate_trade() unmodified,
  exact reproduction of hyp-000011/exp-093's own method.

  CONDITIONED: walk forward bar-by-bar exactly as simulate_trade()
  does, EXCEPT: at the first bar with timestamp >= 14:00:00 ET (if the
  trade has not already exited), compute:
    - original_risk = abs(entry - original_stop) (frozen at signal
      time, from the IB range width -- never recomputed).
    - mult = get_afternoon_conditioning(day, midday_afternoon_frame)
      ["expected_afternoon_range_multiplier"].
    - adjusted_risk = original_risk * mult.
    - new_stop = entry - adjusted_risk (long) or entry + adjusted_risk
      (short) -- re-anchored from ENTRY, not from whatever price is at
      14:00, so this is a pure risk-WIDTH rescale, not a
      trailing-toward-current-price mechanism (kept simple, no new
      free parameter beyond the already-confirmed multiplier).
    - Target is NEVER modified -- isolates this as a stop/risk-sizing
      test only, not a joint stop+target redesign.
    - From that bar onward, current_stop = new_stop for the rest of
      the walk. If the 14:00 bar's own High/Low already breaches
      new_stop, exit that bar at new_stop (same "stop assumed hit
      first on an ambiguous bar" convention simulate_trade() already
      uses for stop/target overlap).
    - If a trade never reaches a 14:00 bar because the day's data ends
      first, or narrow_midday is unclassifiable (insufficient
      lookback -- get_afternoon_conditioning()'s own documented
      default, mult=1.0910, "not narrow"), the function's own existing
      default behavior is used as-is, no special-cased exception.

  R-multiple denominator for BOTH arms stays original_risk (the
  as-entered IB range width) -- the adjusted stop changes WHICH exit
  price is realized, never what "1R" means, so conditioned/unconditioned
  r_multiple_net values stay in the same units and are directly,
  fairly comparable.

## 7. Statistical test

Paired bootstrap: for each trade, diff = r_multiple_net_conditioned -
r_multiple_net_unconditioned. Bootstrap the MEAN of diff directly
(paired, not the two-sample group-difference method exp-077/093 used --
appropriate here since it is the same trade under two policies, not two
populations). N_BOOTSTRAP=3000, seed=7 (project standard,
bootstrap_diff_ci's convention), 90% CI on the percentile bootstrap.

Reported, pre-registered, in this order:
  1. All trades (paired diff, most trades will show diff=0 by
     construction -- pre-14:00 exits -- this is the intent-to-treat
     view).
  2. AFFECTED-ONLY subset (trades still open at the 14:00 bar -- the
     only ones where the two arms can differ at all) -- the real test
     of the overlay's mechanism.
  3. Within the affected subset, split by narrow vs. not-narrow
     afternoon (diagnostic only, explains direction/magnitude, not a
     second promotion test).
  4. Cost-stress check: same comparison with COST_STRESS_MULTIPLIER=2
     applied to both arms identically, per this project's standard
     stress-testing practice -- a result that only survives at 1x costs
     is flagged, not treated as robust.

## 8. Decision rule

Diagnostic tier, same as exp-077/093 -- not a promotion event either
way.
  - NULL (CI spans zero on the affected-only subset, #2 above): closes
    this specific pairing (IB Breakout continuation x afternoon-range
    persistence, stop-width mechanism) for good. No retuning (no
    different re-anchor rule, no different multiplier clipping) without
    an independently new motivating reason.
  - CREDIBLE (CI entirely on one side of zero on #2, economically
    non-trivial, survives the 2x cost stress in the same direction):
    logged as a fresh, separately pre-registered hypothesis candidate
    (its own hyp id, strategy_origin: "derivative", parent hyp-000011)
    -- flagged for a Validation-slice prospective test before any
    further consideration, exactly the exp-093 precedent. Never
    treated as validated by this single Discovery-slice diagnostic
    alone.

## 9. Multiple-testing accounting

Logged to the ledger with its own hypothesis id, parent_hypothesis_id:
hyp-000011, strategy_origin: "derivative", search_batch_id: null
(single-pairing diagnostic, not a registered multi-cell scan -- same
convention as hyp-000049/hyp-000065, confirmed neither is in
SCAN_REGISTRY). Counted as the 5th diagnostic overlay-screen attempt in
its family for anyone reading LEARN afterward.

## 10. What this is NOT

  - Not a retest or retuning of IB Breakout's own closed standalone
    verdict (hyp-000011 stays REJECTED, untouched).
  - Not a resurrection of exp-077/086/087/093 (see Section 1/2).
  - Not itself a promotion event, win or lose (Section 8).
  - Not a position-size (contract-count) test -- position_size_
    multiplier() rescales contract count, which does not change
    r_multiple_net at all under this project's R-normalized convention
    (R-multiple is per-unit-risk, invariant to contract count); a stop-
    width rescale is the version of "sizing" that can actually show up
    in the metric this project trusts, so that is what is tested here.
  - Does not touch H118, EXP047, or the Execution Clock.

## 11. ASCII-only

Confirmed.

## Result (2026-09-10, exp-127)

Built and run exactly as scoped in Section 6, no changes after seeing
any number.

1709 IB Breakout Discovery signals (of 2101 days scanned) -- same
population as hyp-000011/exp-093. Of these, only 82 (4.8%) were still
open (neither stop nor target hit) at the first bar >= 14:00 ET -- IB
Breakout's modest 1.35R target and tight IB-range stop mean most trades
resolve within the same morning. The other 1627 are mechanically
identical under both arms (diff=0 confirmed by direct check, as
pre-registered).

**All trades (intent-to-treat, n=1709): mean paired diff +/-0.0000,
90% CI [-0.0026, 0.0022]. Not credible** -- expected, since 95% of the
sample cannot differ by construction.

**Affected-only (n=82, the real test): mean paired diff -0.0004, 90%
CI [-0.0571, 0.0456]. Not credible.** Mean baseline 0.0736R vs. mean
conditioned 0.0732R -- essentially unchanged.

**Diagnostic split:** narrow_midday=True (n=30, tighter stop applied):
diff -0.0215, CI [-0.1660, 0.0753]. narrow_midday=False (n=52, wider
stop applied): diff +0.0118, CI [-0.0207, 0.0520]. Both span zero,
both thin. Directionally the sign each subset moved is what the
mechanism would predict (tightening costs a little when it clips a
trade that would have worked out, loosening helps a little when it
gives a trade room) but neither clears any bar, and 30/52-trade
subsets are exactly the kind of thin sample this project does not
trust on their own.

**Cost-stress (COST_STRESS_MULTIPLIER=2x): affected-only diff +0.0003,
CI [-0.0566, 0.0465].** Materially unchanged from 1x -- expected, since
the SAME round-trip cost is subtracted from both arms of a paired diff,
so cost level barely moves the difference (it moves the absolute
r_multiple_net levels, which it does: baseline mean 0.0736 -> 0.0568
at 2x stress). The diff being cost-insensitive is a property of the
paired design itself, not evidence of the overlay's robustness -- noted
so this isn't over-read.

**Verdict: NULL. Per Section 8's pre-registered decision rule, this
closes the pairing (IB Breakout continuation x afternoon-range
persistence, stop-width mechanism) for good.** No retuning (a
different re-anchor rule, a different multiplier clipping, a lower
14:00 threshold to capture more affected trades) without an
independently new motivating reason -- doing so now would be exactly
the post-hoc parameter search this project's integrity rules exist to
prevent.

**Honest read, for LEARN:** the mechanism itself was never seriously
tested here -- only 82 of 1709 trades (4.8%) ever reached the point
where it could act, far short of a well-powered test even before
looking at the CI width (+/-0.05R on n=82 is a wide band). This is a
STRUCTURAL mismatch, not a weak effect: IB Breakout's own 1.35R target
and tight stop mean the overwhelming majority of trades resolve before
early afternoon, so a 14:00-gated overlay has almost nothing to act on
for THIS specific setup. The 4-overlay-screen LEARN lesson ("a
conditioning variable can't resurrect a signal that has no edge to
condition") is confirmed again, but this run adds a sharper, separate
lesson worth carrying forward: get_afternoon_conditioning() specifically
needs a setup whose trades are typically STILL OPEN in the 14:00-16:00
window to ever get a fair test -- IB Breakout structurally is not that
setup. A future attempt at this specific KNOWN UNEXPLORED item (a real
position-sizing/stop-width overlay using this conditioning fact) should
pick a setup with materially longer average time-in-trade (e.g. VWAP
Mean Reversion's open-ended hold, or a setup that holds overnight),
not another morning-resolving continuation/breakout setup, or it will
run into the same structural-mismatch ceiling regardless of whether
the underlying volatility fact has real value.

**Ledger:** hyp-000135, parent_hypothesis_id hyp-000011,
strategy_origin "derivative", data_slice_used "discovery",
strategy_status REJECTED (diagnostic, no promotion event). Not in
SCAN_REGISTRY (single-pairing diagnostic, per Section 9). Full
implementation: `src/study_ib_breakout_afternoon_conditioned_stop.py`.
Raw output: `data/exp127_ib_breakout_afternoon_conditioned_results.json`,
`data/exp127_ib_breakout_afternoon_conditioned_trades.csv` (+
`_stress2x` variants).
