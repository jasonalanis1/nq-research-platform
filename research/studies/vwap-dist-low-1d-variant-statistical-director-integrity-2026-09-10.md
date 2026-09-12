# vwap_dist_vs_atr LOW, 1-day variant — Candidate Triage / Statistical / Director Re-Eval / Integrity Gate checkpoint

Written 2026-09-10, automated session. Covers the pipeline stages
between the Discovery-slice confirmation (hyp-000136, DISCOVERY_PASS)
and the single-shot Validation-slice test (slice 1d, not yet run at
the start of this document).

## Candidate Triage (Research Director function) — GRADE B+

n=558, CI_90 [0.0534, 0.1650] entirely above zero, mean R 0.1097 (>
0.05 economic floor by a wide margin), matches the pre-registered
positive direction. Clean pass on both volatility-regime and
trend-regime splits (4/4 sub-slices credible and positive). One
caution, not disqualifying: chronological split-sample first half is
directionally consistent but not independently credible on its own
(n=266, CI touches zero). Not an A (H118's own regime-split record was
cleaner on all cuts, including split-sample) but clears the C+ bar for
Mechanism with room to spare, and the vol/trend regime cleanliness is
itself informative given Portfolio's eventual double-counting question
(3 of 3 existing validated findings are volatility/range facts — this
candidate's regime-INDEPENDENCE argues against it being another
volatility-conditional restatement).

## Statistical Agent — the 4 questions + same-data selection disclosure

**1. Stability.** Mostly stable. Vol-regime: low-vol R=0.136 [0.025,
0.246], high-vol R=0.226 [0.110,0.364] — both credible, same sign, high
vol shows a LARGER point effect (expected under an overshoot/absorption
story — bigger moves need more absorption). Trend-regime: uptrend
R=0.128 [0.058,0.201], downtrend R=0.288 [0.131,0.466] — both credible.
Chronological split-sample: second half credible (R=0.138 [0.068,
0.208]), FIRST half not independently credible (R=0.079 [-0.012,
0.167]) though same sign and point estimate is 72% of the second
half's. Read: most likely a power issue (n=266 alone is a thinner
sample than the regime splits, which each retain ~50% of n=558 too —
comparable size — yet both regime splits stayed credible; the
chronological first half specifically is the one slice that doesn't),
not evidence the effect is chronologically decaying or was only
recently present, but disclosed as a real, unresolved caution rather
than explained away.

**2. Regime dependence.** Not regime-dependent by the two cuts run
(volatility, trend) — effect present and credible in all four
sub-slices, sign-consistent, and if anything STRONGER in high-vol and
downtrend regimes, both directions one would expect from an
overshoot-absorption mechanism reacting to more/faster dislocation.

**3. Magnitude.** Net mean R=0.1097 on realistic costs (round-trip
0.75pt against ~19.5pt gross average move — costs are a small fraction
of the edge at this horizon, contrary to the STANDING RESEARCH
PRIORITY's general caveat that short horizons should be more
cost-sensitive; disclosed as a candidate-specific exception to that
general caution, verified rather than assumed). Cost-stress test run
this session (not logged to ledger — diagnostic only):
    1x  (0.75pt)   mean_R=0.1097  credible=True
    2x  (1.50pt)   mean_R=0.1012  credible=True
    5x  (3.75pt)   mean_R=0.0757  credible=True, still clears 0.05 floor
   10x  (7.50pt)   mean_R=0.0331  credible=False
   15x  (11.25pt)  mean_R=-0.0094 credible=False
The edge survives roughly a 5x cost stress before failing the economic
floor and roughly 8-10x before losing statistical credibility — a wide
margin versus H118's own reported cost sensitivity, and the honest
opposite of "only survives on optimistic costs" (which would mean
dead). Not relaxed to produce this result — same ROUND_TRIP_COST_POINTS
constant as every other candidate, only multiplied upward for the
stress test itself.

**4. Selection sensitivity / same-data selection disclosure.** This
cell (vwap_dist_vs_atr/low/1d) was one of 44 cells Scan 002 screened,
all 44 already disclosed and counted in Discovery-stage multiplicity
exposure (src/project_wide_multiplicity.py SCAN_REGISTRY,
scan_002_2026-09-09 entry, unchanged by this candidate — see the
Integrity Gate pre-clearance doc's Q4). It was NOT selected because
this run looked favorable; it was queued by Jason on 2026-09-10 BEFORE
this session examined any 1d-specific result, motivated by the
horizon-shape pattern already visible in the disclosed Scan 002 table
and in H118's own mechanism doc. The Discovery-slice confirmation run
this session (hyp-000136) reproduces that pre-existing pattern using
the project's canonical per-trade-R convention (see spec addendum for
the metric-discrepancy finding) rather than introducing a new
selection event.

Finding / Confidence / Novelty / Research Value / Recommendation:
Finding: candidate clears Discovery with one disclosed split-sample
caution, is regime-independent, and is far more cost-robust than the
general short-horizon caveat would suggest. Confidence: MODERATE-HIGH
(strong on 3 of 4 questions, one real caution on stability). Novelty:
LOW by design — this is an intentional re-expression of vwap_dist_vs_
atr/LOW at a different horizon, not a new discovery, per its own spec.
Research Value: HIGH as a mechanism instrument regardless of outcome —
resolves ~10x faster than H118 and directly tests H118's own P2
front-loading question. Recommendation: CONTINUE to Director
Re-Evaluation.

## Director Re-Evaluation

Question: does this evidence justify spending the Validation-slice
attempt (the single shot this candidate gets, and the last attempt
available on vwap_dist_vs_atr/LOW under the 2-attempt limit)? YES.
Three reasons: (1) the Discovery-slice result is credible, economically
meaningful by a wide margin, and cost-robust — the statistical bar for
proceeding is clearly cleared; (2) the split-sample caution is a reason
for care in interpreting the Validation-slice result, not a reason to
withhold it — a genuinely pre-registered out-of-sample test is exactly
what resolves that kind of ambiguity, better than more Discovery-slice
diagnostics could; (3) this is explicitly Jason's queued, pre-approved
next step (NEXT_UP.md slice 1d), motivated by a real open mechanism
question (H118's own P2/P4 tension) rather than being generated under
this session's own discretion. Disposition: CONTINUE.

## Integrity Gate checkpoint (before Discovery -> Validation)

Standing brief applied: no data leakage (Validation data has not been
touched by this candidate or read by this session prior to this
checkpoint); no Discovery/Validation contamination (frozen bucket edges
computed on Discovery data only, unchanged); candidate was NOT selected
after seeing its own Validation result (it doesn't have one yet); the
2-attempt limit is tracked and will be exhausted, any outcome, once
this resolves; multiple-testing exposure accounted for (Discovery-stage
already counted, Validation-stage will add exactly one new trial when
logged, consistent with how every other candidate's first Validation
attempt is counted); direction was pre-registered before this session
examined any 1d-specific result; no parameter has been or will be
changed after seeing a result at any slice; mechanism doc exists
(research/mechanisms/vwap-dist-low-1d-variant.md) with a genuinely
pre-registered prediction (P2) specifically for the test about to run;
not a resurrection (per the pre-clearance doc). VERDICT: PASS. Cleared
to proceed to the single-shot Validation-slice test (slice 1d).

Binding reminder carried into that test: ONE shot. Whatever the result,
it is logged and the 2-attempt limit on vwap_dist_vs_atr/LOW is then
exhausted — no further horizon cuts, no retuning, no second Validation
attempt regardless of outcome.
