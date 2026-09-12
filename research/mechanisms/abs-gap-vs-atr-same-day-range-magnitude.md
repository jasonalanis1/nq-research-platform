# Mechanism — |gap_vs_atr| magnitude, same-day RTH range (hyp-000140)

Written: 2026-09-11 (interactive session, Jason present)
Results seen before writing: YES for P1/P2 (the entry's own two-sided prediction, already
confirmed) — NO in the sense that this document's own NEW predictions (Section 3) are
written before looking at any data beyond what Scan 010 already produced. Idea Inventory
Entry 5 pre-registered both P1 (elevation on HIGH gap magnitude) and P2 (compression on
LOW gap magnitude) at the generation meeting, before Scan 010 ran; both were then
confirmed. The entry ALSO pre-registered a third, non-gating check (P3: weaker elevation
on high-volume HIGH-gap days), which ran the opposite way. This document is not a
post-hoc mechanism invented to explain a surprise result on the primary cells — the
primary mechanism was written first and vindicated — but it does have to account for the
P3 surprise honestly, and per the MECHANISM GATE the P3 explanation earns hypothesis
weight only until its own new predictions (Section 3) are tested on data not yet used.

## 1. The claim

The state variable is `abs(gap_vs_atr)` — the magnitude (not sign) of the overnight gap
between prior RTH close and today's open, ATR-normalized, terciled fresh on the Discovery
sample. The outcome is same-day RTH range vs. its own trailing-20d average, the same
range-vs-trailing-average construction already used for Entry 2 (days_to_monthly_opex)
and Entry 4 (day_of_week).

Result: a genuine two-sided, monotonic-shaped effect. LOW-magnitude-gap days show
compressed same-day range (n=556, mean_ratio=0.9130, 90% CI [0.8813, 0.9478] — about 9%
below the trailing average, credibly). MID-magnitude days are null (CI spans 1.0, as a
non-gating middle cell should be). HIGH-magnitude-gap days show elevated same-day range
(n=556, mean_ratio=1.1921, 90% CI [1.1484, 1.2375] — about 19% above the trailing
average, credibly).

The mechanism this document proposes: the size of the overnight gap is a direct proxy
for how much unresolved repricing the RTH session inherits at the open. A small gap means
the overnight session and yesterday's RTH close already agree — there is no backlog of
fresh information the day session needs to work through, so RTH trades in a narrower,
more orderly range than usual. A large gap means new information (news, macro data,
overnight positioning) arrived that the RTH session has not yet had a chance to reprice
through its own deeper liquidity pool; that backlog gets worked out during the day,
producing a busier, wider-than-usual session. This is a volatility-transmission story,
not a directional one — it says nothing about which way price moves, only how much
ground it covers, which is exactly why measuring `abs()` rather than the signed value is
the right construction and why it is a distinct variable role from the closed
signed-gap-fade lineage (fade_the_gap, gap_down_fade_longonly_h89,
gap_down_fade_multiday_h91, gap_fade_h87), which all asked whether price reverts toward
the gap-fill level.

## 2. Who is on the other side

Whoever is short realized volatility into a large, unresolved overnight gap without
adjusting their sizing or hedges for it — for example, an options seller or a
volatility-targeting strategy that prices a session's expected range primarily off recent
realized range (the trailing-20d average this entry benchmarks against) rather than
off that morning's own gap size. A large gap is public, cheaply observable information
the moment the session opens; a participant who has priced their exposure the night
before, or who re-prices only on a lag, is systematically under-hedged on exactly the
days this cell says will run wider than usual. Symmetrically, on small-gap days, anyone
holding volatility exposure sized for an "average" session is paying for more
volatility-transmission risk than the day is likely to deliver — the counterparty there
is closer to a structural volatility seller collecting a premium that a same-day realized
measure would say is mispriced. Neither side is a single, clean, named institutional flow
(unlike H118's forced-seller story); it is closer to "whoever prices same-day range off a
trailing average instead of off the morning's own gap," which is a real but softer
counterparty than this project's strongest candidates. That the effect is CONFIRMED on
both pre-registered legs (not just one gate clearing by chance) is what makes it a
genuine Triage-worthy candidate despite the counterparty being diffuse rather than named.

## 3. Testable predictions

The entry's own P3 (reported, not gated) predicted that HIGH-gap days ALSO showing high
`volume_vs_expected` would show a WEAKER elevation than HIGH-gap days with low volume —
reasoning that heavy same-day participation would mean the uncertainty is already being
resolved by the time it's measured, leaving less incremental range still to unfold. The
data ran the opposite way: low-volume HIGH-gap days were NOT credible on their own
(n=197, mean=1.0195, null), while high-volume HIGH-gap days were MORE elevated than the
full HIGH cell itself (n=197, mean=1.4005, credible). That result needs an honest
account, not a rewrite of the primary story to fit it after the fact.

P1. **Reframe: volume is not resolving the gap's uncertainty, it is confirming it is
    real.** A large gap accompanied by heavy volume is more likely a large gap that the
    market actually believes and is actively repricing around (fresh information,
    validated by participation), versus a large gap on ordinary or light volume, which is
    more likely a mechanical or liquidity-driven gap (a stale quote, thin overnight book,
    an isolated large order) that the RTH session may partly ignore or fade rather than
    extend. If this reframe is right, splitting the HIGH-gap cell a second way — by
    whether the gap itself is later "validated" (RTH continues in the gap's direction on
    above-median volume in the first RTH hour) versus "faded" (RTH partially reverses the
    gap on above-median volume) — should show the elevation effect concentrated in the
    validated subgroup, with the faded subgroup closer to the MID-tercile null. This is a
    new split, not yet computed on the Discovery sample for this construction.

P2. **The volume-elevation relationship should be monotonic, not a two-point artifact.**
    If real, splitting the full sample (all terciles, not just HIGH) by `volume_vs_expected`
    tercile and checking the same-day-range ratio at each gap-magnitude x volume cell
    should show volume amplifying the effect in BOTH directions — high volume making
    LOW-gap days even MORE compressed (participants confirming there is genuinely nothing
    to reprice) as well as HIGH-gap days more elevated — rather than volume only mattering
    on the HIGH-gap side. A one-sided relationship (volume matters for elevation but not
    for compression) would weaken this reframe and point back toward something specific to
    large gaps rather than a general volume-amplifies-repricing story.

P3. **The volume-conditioning result should NOT be an artifact of the median-split
    construction itself.** Re-running the HIGH-gap x volume split with volume terciled
    (not median-split) should preserve the same ordering (elevation increasing with
    volume), not just reproduce a two-bucket coincidence. A result that only holds at the
    median cut and flattens or reverses with a finer volume cut would be a caution flag
    against over-reading the entry's own already-exploratory P3 check.

## 4. What would falsify this

If P1's validated/faded split shows elevation equally present in BOTH subgroups (or
concentrated in the FADED subgroup instead), the "volume confirms the gap is real"
reframe fails, and the P3 anomaly would remain genuinely unexplained rather than resolved
— a mark against advancing this candidate past Triage without a better account. If P2
shows volume amplifies elevation on HIGH-gap days but has no comparable effect on
LOW-gap compression, that is a one-sided pattern this document's symmetric
volume-amplification story does not predict, and would call for a narrower,
HIGH-gap-specific explanation instead (closer to the entry's original uncertainty-
resolution logic being backwards rather than simply refined). If P3 shows the volume
relationship dissolves under a finer cut, the P3 finding itself should be treated as
likely noise from a single, already-exploratory median split (n=197 per subgroup) rather
than a real, monotonic volume-conditioning effect worth building further predictions on.

## 5. Prediction status

NOT YET TESTED. P1-P3 above require new splits (validated-vs-faded gap subclassification,
a full volume-tercile x gap-tercile grid, and a volume-tercile re-cut of the existing
HIGH-gap cell) not yet computed on the Discovery sample. This is the next Statistical-
stage step for hyp-000140, to be run as its own pre-registered pass before any Director
Re-Evaluation or Monetization discussion.

## 6. Verdict

Candidate Triage grade: **B**. The primary two-sided result (P1/P2 elevation and
compression, both pre-registered, both credible, both with economically meaningful
magnitude — 19%/9% relative to the ~0.05 floor convention used elsewhere in this project)
is a genuine Discovery-stage survivor and the strongest reason to keep going. The grade is
B and not A because of two honest drags: (1) the counterparty is diffuse rather than
named (Section 2) — weaker than this project's strongest candidates (H118) but not as
weak as hyp-000139's "no identifiable counterparty" case; (2) the P3 volume-conditioning
result ran opposite the entry's own pre-registered prediction, and while this document's
reframe (Section 3) offers a coherent alternative story, that story is itself untested —
it is not yet evidence, only a hypothesis competing with "the entry's original P3 logic
was simply wrong and there is no clean explanation yet." hyp-000140 stays in Candidate
Triage, ledger status PROMISING, unchanged; this document does not itself move it forward
— per the MECHANISM GATE, Section 3's predictions must be tested first. Idea Inventory
Entry 5 stays OPEN pending that Statistical-stage pass, consistent with the project's
existing hyp-000139/Entry 3 precedent for OPEN-not-closed handling of Triage candidates.
