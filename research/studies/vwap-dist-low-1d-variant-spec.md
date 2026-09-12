# VWAP-Distance-Low, 1-Day Variant -- Frozen Spec

Frozen 2026-09-10. Integrity Gate pre-clearance: PASS, unconditional
(research/studies/vwap-dist-low-1d-variant-integrity-preclearance-2026-09-10.md).
Written before any result at this horizon is examined -- the Scan 002
Discovery numbers quoted in research/NEXT_UP.md and the H118 mechanism
doc are the ONLY numbers seen prior to freezing this spec; they are
what motivated the question, not a peek at this spec's own result.

## Relationship to H118 -- read before anything else

This is a VARIANT OF A KNOWN FINDING (H118, hyp-000121), never a new
discovery. It is attempt 2 of 2 under the 2-attempt limit on
vwap_dist_vs_atr/LOW (H118 = attempt 1). It does NOT touch H118: no
H118 ledger row is edited, no H118 spec/status file is modified, and
neither candidate's forward results inform the other (STRICT
SEPARATION, both directions, per Jason's 2026-09-10 framing).

## Mechanism question being tested

H118's mechanism doc (research/mechanisms/h118-vwap-dist-low.md), P2:
two-thirds of the 10-day effect lands in day 1, flat through day 5,
then jumps 5->10 with no mechanism story behind the jump. This variant
asks: does the 1-day slice, evaluated as its OWN pre-registered
candidate on its own out-of-sample data, hold up on Validation the way
H118's 10-day slice did? A pass would be the strongest evidence yet
that the FIRST DAY of H118's edge is where the real, mechanism-
consistent effect lives. A Validation-slice failure at 1d, if H118's
10d Validation passed, would be informative in the other direction
(the 1-day effect from Discovery doesn't replicate even though the
10-day figure that contains it does) and does not retroactively change
H118's own accepted status.

## Definition (identical to H118 except horizon)

Event: a trading day whose vwap_dist_vs_atr falls in the LOW tercile
of the FROZEN Discovery-sample bucket edges from H118's own spec:
[-inf, -0.0460, 0.1471, inf]. Not refit here, not refit for this
horizon -- same edges, same variable, same Discovery sample used to
compute them.
Position: enter LONG at that day's RTH reference close.
Exit: at the RTH reference close 1 trading day later (skip if the exit
day falls outside available data).
Pre-specified direction: POSITIVE net return (matches the sign observed
in every horizon of Scan 002's exploratory pass, including 1d: +13.38
pts gross-of-cost in the original scan).
Cost: ROUND_TRIP_COST_POINTS (src/backtest.py), one round-trip per
trade, same realistic cost model as H118 -- NOT relaxed. Per the
STANDING RESEARCH PRIORITY's caveat #1: costs bite harder on a smaller
gross edge (~13pt gross vs H118's ~20pt), and if this only survives on
optimistic costs it is dead.
Risk unit for R-multiple: entry-day ATR(14), same convention as H118/
H116/H117 (units only, not a stop distance).

## Method, in slices (per NEXT_UP.md)

1c. Discovery-slice CONFIRMATION run (this is confirmation of an
    already-scanned cell, not a new search -- the 1d number is already
    in the Scan 002 record). Bootstrap 90% CI, N_BOOTSTRAP=3000, seed=7,
    same as H118. Expect to reproduce ~13.4 pts / ~0.105R gross-
    consistent shape; logged regardless of outcome.
1d. ONE pre-registered Validation-slice test (src/data_split.py
    get_validation_data), single shot, run only after Mechanism +
    Statistical + Director Re-Evaluation + Integrity Gate checkpoint
    clear the Discovery-slice result. Logged whatever it shows.
1e. Portfolio incremental-information check, required regardless of
    outcome: same latent effect as H118 restated in a shorter window,
    or independent information? (Governs whether promoting both this
    and H118 would double-count one effect.)

## Per protocol

Hypothesis attempt 2 of 2 on vwap_dist_vs_atr/LOW (2-attempt limit now
exhausted after this resolves, any outcome). Ledger: strategy_name
`vwap_dist_low_1d_variant`, strategy_origin `derivative`,
parent_hypothesis_id = hyp-000121 (H118's own Discovery row). Never
logged as an H118 row, never as `..._h118...`. No retuning of the
bucket edges, the 1-day horizon, or the entry/exit convention after
seeing any result at any slice.

## ADDENDUM 2026-09-10 -- metric clarification found during slice 1c

The Discovery-slice confirmation run (frozen script:
src/study_vwap_dist_low_1d_variant.py, per-trade entry-day-ATR14
R-multiple, no baseline subtraction -- the SAME convention H118's own
canonical ledger row hyp-000121 uses) returned n=558 (matches exactly),
mean net points +18.78, mean R 0.1097, CI_90 [0.0534, 0.1650] -- NOT the
"~13.4 pts / 0.105R" figure this spec's own Method section said to
expect, quoted from research/NEXT_UP.md's "Scan 002 Discovery numbers"
table.

Investigated rather than silently accepted (the whole point of a
confirmation run against a frozen script is to catch exactly this kind
of thing). Root cause, traced to src/market_behavior_discovery_scan_002.py:
that screening script's "edge" figure is `mean_fwd_return - baseline_mean`
(bucket mean MINUS the unconditional mean across ALL days, i.e. it nets
out the sample's average drift), and its "R" is that baseline-adjusted
points figure divided by a single dataset-wide AVERAGE ATR14 -- not
each trade's own entry-day ATR14. That is a fast, cheap, exploratory
screening metric, appropriate for ranking 172 cells against each other,
and it is NOT the same statistic as this project's official R-multiple
convention (per-trade entry-day-ATR normalization, no baseline
subtraction) that every frozen candidate script -- H116, H117, H118,
and now this one -- actually uses and logs to the ledger. The two
happen to sit close for the R figure at this horizon (0.110 vs 0.105)
but diverge materially in points (18.78 vs 13.38) because of the
baseline-drift subtraction.

This is a genuine, disclosed finding, not a retune: the candidate's
DEFINITION (state variable, frozen bucket edges, 1-day horizon,
entry/exit convention, cost model, direction) is completely unchanged.
Only the pre-registration TEXT's expected-number annotation was wrong,
because it quoted a screening-stage approximation as if it were the
frozen-script figure. Flagging for NEXT_UP.md and future sessions: the
"Scan 002 Discovery numbers" table's pts/R figures for vwap_dist_vs_atr
(and, by the same code path, every other Scan 002/003/004 cell) are
SCREENING APPROXIMATIONS, not directly comparable to a promoted
candidate's own canonical ledger R. Anyone using that table to predict
or sanity-check a frozen-script result should expect this gap.

Corrected expectation for 1c, logged: n=558, mean R = 0.1097 (net,
credible, 90% CI entirely above zero), mean net points +18.78.
Verdict: DISCOVERY_PASS. Ledger: hyp-000136.
