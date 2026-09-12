# Mechanism — overnight-vs-RTH return divergence, HIGH tercile, mean-reversion (hyp-000139)

Written: 2026-09-11  ·  POST-HOC
Results seen before writing: YES — Scan 008 (src/market_behavior_discovery_scan_008.py)
already ran and produced the HIGH-tercile result this document explains. Entry 3 of
research/idea_inventory.md pre-registered TWO mutually exclusive, opposite-signed
predictions on this same cell before the scan ran: P1 (persistence, structural/mandate-
flow story) and P2 (reversion, statistical-artifact/mean-reversion story). The scan
resolved in favor of P2, not P1. This document is the mechanism writeup for the winning
side (P2/reversion) — it was NOT the entry's own primary, pre-registered mechanism
claim, so per the MECHANISM GATE it earns hypothesis weight only, not evidence weight,
until its own NEW predictions (Section 3 below) are tested on data not yet touched.

## 1. The claim

The state variable is trailing 20-day cumulative overnight (close-to-open) return minus
trailing 20-day cumulative RTH (open-to-close) return, ATR-normalized — a rolling
divergence z-score between where the "overnight book" and the "day book" have been
making their money. The HIGH tercile is where overnight returns have been running well
ABOVE RTH returns for the past 20 days (overnight strength, RTH relative weakness, or a
mix). The credible result: after 20 days sitting in that state, the NEXT day's own
overnight-minus-RTH divergence tends to be NEGATIVE (mean = -0.0746 ATR units, 90% CI
[-0.1371, -0.0099]) — i.e. the gap narrows or flips, rather than persisting.

The mechanism this document proposes: a 20-day-old divergence this large is not evidence
of a durable structural split between two investor bases (the entry's own P1 claim); it
is evidence that the rolling statistic itself is stretched relative to its own trailing
distribution, and stretched z-score-like constructions of THIS kind (a difference of two
noisy 20-day sums) mean-revert mechanically because the individual daily overnight and
RTH returns that make up the sum are not, on this instrument, persistently
autocorrelated at the daily level — a run of "overnight strong, RTH weak" days is more
likely followed by ordinary or offsetting days than by more of the same, simply because
the 20-day window is long enough to have already captured most of whatever short-lived
episode produced the divergence (a single news week, an earnings/macro cluster, a
temporary positioning imbalance). By the time the trailing sum is in its own HIGH
tercile, the episode that built it is statistically more likely to be ending than
continuing.

## 2. Who is on the other side

The honest answer here is closer to "no identifiable counterparty" than the entry's own
P1 story offered (which named mandate-driven overnight buyers as a structural,
price-insensitive flow). If this document's reversion story is right, there is no single
economic actor being exploited — the "trade" is closer to fading a stretched rolling
statistic than to taking the other side of a named, persistent flow. The closest thing
to a counterparty: traders or systems that read a persistent 20-day overnight-vs-RTH
split as a durable regime shift (the entry's own P1 reading) and position for its
continuation — e.g. increasing overnight exposure specifically because "overnight has
been where the money is" — would be the ones giving up the edge this cell captures, if
the divergence in fact reverts more often than not. This is a much weaker, less
mechanistically satisfying counterparty than H118's forced-seller story or the
overnight-coil liquidity story, and that weakness is itself informative: it is a mark
against this being a robust, monetizable effect rather than a mechanical artifact of the
Statistical construction (a difference-of-two-rolling-sums measure regressing toward its
own mean).

## 3. Testable predictions

P1. **The reversion should be a general property of the divergence measure, not specific
    to which side (overnight or RTH) drove it into the HIGH tercile.** If this is
    mechanical mean-reversion of a stretched rolling statistic rather than a real
    overnight-vs-RTH economic asymmetry, splitting the HIGH-tercile days into
    "overnight-driven" (overnight leg unusually strong, RTH leg near-normal) versus
    "RTH-driven" (RTH leg unusually weak, overnight leg near-normal) should show the SAME
    sign and roughly similar magnitude of next-day reversion in both subgroups. A real
    overnight-specific mechanism (the entry's P1 story) would instead predict the effect
    concentrates in the overnight-driven subgroup only.

P2. **The reversion should be present, with similar sign and magnitude, in a
    volatility-scaled 10-day or 30-day version of the same trailing-divergence
    construction, not only the 20-day window actually scanned.** A mechanical
    stretched-statistic reversion should not be a knife-edge property of exactly 20 days;
    a genuine structural overnight-flow story would have no particular reason to
    generalize across window lengths either, so this prediction is not free, but its
    ABSENCE (i.e., reversion only shows up at 20 days and not at neighboring windows)
    would specifically support a data-mined, non-mechanical reading over this document's
    own mechanical-reversion story.

P3. **The HIGH-tercile reversion should be WEAKER (not restated, tested independently)
    on days where the trailing divergence was built from LOW `volume_vs_expected` days**
    — i.e., if participation was already thin while the divergence was accumulating, the
    stretched-statistic story predicts the same mechanical reversion regardless of
    volume (a pure autocorrelation-of-noisy-sums effect does not require any particular
    volume regime), whereas a real flow-based story (of either sign) would predict the
    effect tracks how much real participation, not just price action, built the
    divergence. This mirrors the entry's own P3 counterparty check (already run for the
    HIGH cell as a whole per data/market_behavior_discovery_scan_008_results.json,
    `p3_volume_conditioned` field — currently empty/not yet populated for this split) but
    must be re-run specifically conditioned on the reversion reading, not the persistence
    reading the entry pre-registered it against.

## 4. What would falsify this

If P1 shows the reversion is concentrated specifically in the overnight-driven subgroup
(not the RTH-driven subgroup), that favors a real overnight-flow-specific mechanism (of
some kind, possibly still a version of the entry's own P1 story with the sign of the
follow-through wrong) over this document's mechanical-reversion story. If P2 shows the
effect does NOT generalize to neighboring window lengths (10d, 30d) at all — i.e. it is
a knife-edge property of exactly 20 trading days — that is evidence AGAINST both this
document's mechanical story and the entry's structural story, and points toward the
result being closer to a Discovery-stage artifact of the specific window length chosen
(a form of the SLICING/COSMETIC-NOVELTY concern the governance doc names) than a real
effect either way. If P3 shows the reversion is equally strong or stronger in low-volume
subperiods, that also weakens the mechanical-statistic reading (which predicts volume
independence) without strongly supporting either alternative.

## 5. Prediction status

UPDATED 2026-09-11 (Statistical stage, research/studies/hyp139-statistical-stage-2026-09-11.md):

P1 — TESTED, MIXED. Overnight-driven subgroup (n=147, mean=-0.0758,
ci_90=[-0.1793,0.0163], NOT credible) and RTH-driven subgroup (n=217, mean=-0.0738,
ci_90=[-0.1552,0.0125], NOT credible) show the same sign and similar magnitude --
consistent with this document's mechanical-reversion shape, not concentrated in the
overnight-driven subgroup as the entry's original P1/persistence story would require --
but NEITHER subgroup is independently credible once split. Directionally consistent,
statistically underpowered; not a clean confirmation.

P2 — CONFIRMED. 10-day window (n=451, mean=-0.0609, ci_90=[-0.1178,-0.0038], credible)
and 30-day window (n=279, mean=-0.0886, ci_90=[-0.1603,-0.0210], credible) both
reproduce the same-signed, credible reversion as the 20-day construction. Not a
knife-edge property of exactly 20 days.

P3 — TESTED, NOT CONFIRMED, and resolved the OPPOSITE way this document anticipated.
Low-volume subset: n=182, mean=0.0130, ci_90=[-0.0581,0.0867], NOT credible
(wrong-signed point estimate). High-volume subset: n=182, mean=-0.1622,
ci_90=[-0.2718,-0.0646], credible, over 2x the full-sample magnitude. The mechanical
story predicts volume-INDEPENDENCE; instead the reversion is concentrated almost
entirely in high-volume days and absent in low-volume days. This is this document's own
falsification condition (Section 4) firing, just via the opposite path than the text
anticipated (stronger, not weaker, in one volume regime) -- and it is also inconsistent
with the entry's ORIGINAL P1/persistence story, which predicted the opposite sign of
divergence than Scan 008 actually found. The result does not cleanly support either
this document's mechanical story or the entry's original structural story.

## 6. Verdict

UPDATED 2026-09-11: hyp-000139 was REJECTED at Statistical
(research/studies/hyp139-statistical-stage-2026-09-11.md). The binding reason is NOT
these predictions -- it is Q3 (project-wide multiplicity correction): the Sidak-adjusted
90% CI at the live Discovery-stage trial count (N=275) is [-0.2119, 0.0626], crossing
zero, even though the raw CI does not. That is this project's established binding
constraint (the same check closed range-contraction and overnight-coil 2026-09-10
despite each clearing its raw CI and the 0.05 economic-meaningfulness floor). Q1
(stability) also failed independently: only one of two chronological halves is
credible on its own. The P1-P3 predictions above resolve to a genuinely mixed picture
rather than a rescue -- P2 supports the mechanical-reversion reading, but P3 actively
undercuts the "no real counterparty, stretched z-score" position this document staked
out as its most-defensible reading, without handing the candidate a credible
alternative story either (the entry's own original persistence mechanism predicted the
wrong sign outright). The counterparty problem flagged in Section 2 -- closer to "no
identifiable counterparty" than a named economic actor -- stands, unresolved either way,
and remains the honest summary of why this candidate never had a strong mechanism case
to begin with, independent of the multiplicity failure that formally closed it.
