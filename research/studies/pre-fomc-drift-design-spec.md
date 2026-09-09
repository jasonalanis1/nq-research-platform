# Pre-FOMC Announcement Drift -- Observatory v11 Design Spec

Frozen 2026-09-09. Direct outcome of the "identify direction" staff
meeting: strongest-documented mechanism this project has not yet
tested, free calendar data, genuinely new (not adjacent to anything
tested or excluded).

## Mechanism

Lucca & Moench (2015, NY Fed Staff Report 512, "The Pre-FOMC
Announcement Drift") document large, systematic positive equity
returns in the 24 hours before scheduled FOMC statement releases
(2pm ET on the second day of each meeting) -- average ~49bps over that
window in their sample, "too large to be explained by standard
asset pricing models," present across major equity indices, absent in
Treasuries/money markets. Later work (e.g. "The disappearing pre-FOMC
announcement drift," Cocoma, Czasonis, Kritzman 2020-21) argues the
effect weakened or vanished post-financial-crisis in SOME samples --
so this is NOT settled science, and we test it fresh on our own data
rather than assume either paper's conclusion holds for NQ specifically.

Data requirement: FOMC scheduled-meeting decision dates (the day the
2pm ET statement is released), 2015 through the Discovery cutoff
(2021-10-03). Free, public record (federalreserve.gov). CAVEAT: the
date list used here (research/studies/fomc_dates_2015_2021.py or
inline in the study script) was compiled from public historical
records and spot-checked, not independently re-verified against the
Fed's site line-by-line for this session -- if a small number of
dates are off by a day, it costs a few observations, not a systemic
bias, since dates are used as fixed labels only, no data-derived
positioning. Flagging this honestly per the frozen-spec discipline.

## Definition (directional, pre-specified from literature)

Event: FOMC day = a scheduled FOMC statement-release date. Window:
the FULL RTH SESSION IMMEDIATELY BEFORE the FOMC day (i.e., the prior
trading day's 09:30-16:00 RTH return) plus the overnight session into
FOMC morning (16:00 prior day to 09:30 FOMC day) -- combined, this
approximates the ~24-hour pre-announcement window used in the
literature, adapted to session boundaries we can measure cleanly.
Two sub-measurements, reported separately (not blended), to keep the
result interpretable: (a) prior-day RTH return, (b) overnight return
into FOMC morning. Outcome in both cases: the return itself (signed,
points), compared against the same measure on all non-pre-FOMC days
(complement).

Pre-specified direction (from literature): pre-FOMC returns skew
POSITIVE relative to the complement, on average, regardless of the
eventual hike/cut/hold outcome (the literature's finding is about
anticipation, not the decision itself). Stated before running
Discovery.

## Method

Bootstrap mean-difference CI (N_BOOTSTRAP=3000, seed=7, 90% CI) on
(pre-FOMC mean - non-pre-FOMC mean), separately for each sub-window.
Same convention as observatory_v5. ATR-normalized cost-aware screen
applies (v4 convention, 0.05 floor) -- this is a directional/return
finding. Credible = CI excludes zero AND direction matches the
pre-specified positive sign.

Sample size: ~31 scheduled FOMC meetings expected in Discovery
(2015-2021-10-03, roughly 8/year including 2020's emergency meetings)
-- thin, similar to Turn-of-the-Month's ~40 events but smaller. Flag
per LEARN thin-sample-overconfidence failure mode: treat "Promising"
here with real skepticism; this is exploratory scoping, not a signal
we'd act on without a larger-sample robustness check.

## Per protocol

Exploratory only, Discovery data only, non-trading. A credible AND
cost-viable result on either sub-window gets its own Behavioral
Finding (thin-sample caveat stated explicitly), not immediate
promotion. A null result on both sub-windows is logged and closes
this thread -- no retuning the window definition or date list after
seeing the result.
