# Mechanism — Overnight Coil -> Same-Day RTH Range (hyp-000056 Discovery / hyp-000057 Validation)

Written: 2026-09-10  ·  **POST-HOC**
Results seen before writing: YES — Discovery (exp-084) and the single
pre-registered Validation-slice prospective test (exp-085) were both
complete before this document existed. **This is a hypothesis, not
evidence.**

## 1. The claim

When the overnight (Globex, prior-day 16:00 ET to today's 09:30 ET, thin-
liquidity) session's range sits in the bottom 20th percentile of its own
trailing 20-day distribution, that SAME day's regular-hours (09:30-16:00
ET) range also tends to be narrower than its own trailing average
(mean_ratio 0.89, credibly below 1.0 on both Discovery and Validation).

Candidate mechanism: this is a SAME-DAY persistence of a latent "is there
anything to trade today" state, not day-over-day mean reversion in
volatility. The overnight session is a low-participation window that
mostly reflects whatever information has accumulated since the prior
close. A quiet overnight session is evidence that little or no material
information arrived; absent a fresh catalyst, the RTH session that follows
has nothing new to react to either, so it also stays quiet. This is
structurally DIFFERENT from the range-contraction/expansion mechanism
document (research/mechanisms/range-contraction-expansion-cycle.md), which
predicts the OPPOSITE pattern one day later (narrow prior RTH day -> WIDER
next RTH day, a reversion/release story). Both being true is not a
contradiction -- they describe different clocks (overnight->same-day vs.
day->next-day) -- but it is worth stating plainly that "quiet predicts
quiet" and "quiet predicts a release" are different claims, and this
document should not borrow the other's story without checking it applies
here.

## 2. Who is on the other side

As with the range-contraction candidate, this is a range CHARACTERIZATION,
not a directional rule, so "who profits" does not have a clean answer.
Speculatively, if this were operationalized (e.g., selling RTH intraday
straddle-equivalent risk specifically on pre-identified coiled-overnight
days), the counterparty would be intraday breakout/momentum traders who
pay for optionality or take directional risk anticipating an RTH move that
these specific days statistically don't deliver. This is NOT confirmed --
this project has no options-flow or intraday-trader-positioning data, and
this counterparty is inferred, not observed. Stated honestly as a gap.

## 3. Testable predictions

P1. **Same-day volume co-movement.** If the mechanism is a shared "no news
    today" latent state rather than a range-specific artifact, RTH volume
    on coiled-overnight days should ALSO run below its own trailing
    average (using `volume_vs_expected`, already computed in Scan 002) --
    not just range. A quiet-range day with NORMAL or above-average volume
    would argue against the shared-latent-state story.

P2. **Calendar DE-clustering (opposite direction from the range-
    contraction candidate's P2).** If coiled-overnight days reflect the
    absence of an anticipated catalyst, they should be UNDER-represented,
    not over-represented, in the 1-2 sessions immediately around scheduled
    macro events (FOMC, CPI, NFP, monthly OPEX -- `days_to_monthly_opex`
    already computed) relative to their unconditional base rate, since
    anticipation of a scheduled event tends to keep even overnight activity
    elevated. Finding elevated (not reduced) event-proximity would
    contradict the "no catalyst" story specifically.

P3. **Regime robustness, not regime concentration.** If this is a genuine
    same-day informational-state effect rather than an artifact of one
    ambient volatility regime, it should hold with the same sign in both a
    low-VXN and a high-VXN subsample (using `vxn_level_vs_trailing`,
    already computed). Concentration in one VXN regime only would match
    the exact KNOWN FAILURE MODE that killed Scan 003's last surviving
    candidate (effect entirely in one volatility regime) and should be
    treated with the same suspicion here.

## 4. What would falsify this

Normal-or-above RTH volume on coiled-overnight days (breaks the shared-
latent-state story). Coiled-overnight days clustering disproportionately
NEAR scheduled macro events rather than away from them (contradicts the
"no catalyst" reading). Effect concentrated in a single VXN regime subset
(matches a known contamination pattern rather than a distinct mechanism).

## 5. Prediction status

**P1 -- TESTED 2026-09-10** (Statistical-stage pass, n=444 coiled days --
see research/studies/statistical-stage-pass-2026-09-10.md).
**CONFIRMED.** Coiled-overnight days: same-day RTH volume ratio (own
total RTH volume / trailing-20-day average) mean=0.903, ci_90
[0.876,0.930], credibly below 1.0. This is below the all-days baseline
of 1.056 (ci_90 [1.039,1.073], credibly ABOVE 1.0 -- volume has trended
up over the sample). Coiled-overnight days run quiet on volume too, not
just range -- consistent with the shared "no news today" latent-state
story, not just a range-specific artifact.

**P2 -- TESTED 2026-09-10. NOT CONFIRMED (no effect found, either
direction).** Coiled-overnight days: 15.8% fall within +/-2 trading days
of monthly OPEX vs an unconditional base rate of 15.9% (n=444) --
indistinguishable. No de-clustering (predicted) and no clustering
either. Undercuts the specific "anticipation of a scheduled event keeps
overnight activity elevated" story without touching the general
no-catalyst reading elsewhere in this document.

**P3 -- TESTED 2026-09-10. NOT ROBUST -- a real caution, not a clean
pass.** Split by the sample's own VXN-regime median: low-VXN subsample
(n=356) mean RTH-range-ratio=0.766, ci_90 [0.737,0.796], credible. High-
VXN subsample (n=88) mean=0.963, ci_90 [0.882,1.044] -- CROSSES 1.0, not
credible. Same sign in both (below 1.0) but the effect is materially
weaker and statistically non-credible in the high-VXN slice. This
partially matches the project's own KNOWN FAILURE MODE (effect
concentrated in one volatility regime) that killed Scan 003's last
survivor -- flagged with the same suspicion here, though n=88 is thin
enough that this reads as underpowered-in-that-slice rather than a
clean refutation. Note this is a DIFFERENT regime cut than the ATR14
split used for the "regime dependence" Statistical-stage question,
which found no concentration (0.797 low-ATR-vol vs 0.813 high-ATR-vol,
both credible) -- the VXN-based split and the realized-ATR-based split
disagree, which is itself worth remembering (KNOWN FAILURE MODE
addendum): a "no regime concentration" verdict can depend on which
regime variable is used to test it.

## 6. Verdict

P1 is a clean, confirmed, falsifiable result for the shared same-day
"nothing to trade today" latent-state story over a range-specific
artifact. P2 found nothing (narrows the story, doesn't break it). P3 is
a genuine caution -- not a refutation, but the exact shape of failure
(regime-subset concentration) that this project has learned to treat
with suspicion, and it appears specifically on the VXN cut, not the ATR
cut, which is itself informative rather than a wash.

The Statistical-stage pass (research/studies/statistical-stage-pass-2026-09-10.md)
found split-sample stability clean (both chronological halves credible,
similar magnitude) and threshold-selection robustness clean (pctl 15
and 25 both close to the frozen pctl-20 result), but re-confirmed this
session's earlier finding that the single Validation leg fails the
project's own multiplicity-corrected 90% bound (adjusted 0.786-1.003,
barely crosses 1.0). Per NEXT_UP.md queue item 0's standard, this
candidate does NOT advance to Director Re-Evaluation -- the
corrected-CI failure is already binding, and P3's regime-concentration
caution is a second, independent reason not to treat this as a clean
pass even setting the correction aside. Disposition: **ABANDON at
Statistical stage** (hyp-000057 updated REJECTED in the ledger, in
place, no new hypothesis_id spent).
