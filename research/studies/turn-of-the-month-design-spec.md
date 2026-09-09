# Turn-of-the-Month Effect -- Observatory v8 Design Spec

Frozen 2026-09-09. Sourced from the market-microstructure research
subagent's candidate list (2026-09-09), ranked #1 by the staff meeting
for "free/cheap data + real, documented mechanism" -- chosen as the
first move under Jason's "get more data inexpensively and pursue it"
instruction, and as the fastest yes/no test of whether mechanism-first
selection keeps working beyond OBS-FINDING-011.

## Mechanism

Turn-of-the-month (TOM) effect: equity index returns are documented in
the academic literature (Ariel 1987; Lakonishok & Smidt 1988; McConnell
& Xu 2008 confirm persistence out-of-sample) to be disproportionately
positive in a short window straddling the calendar month boundary --
attributed to systematic month-end/month-start institutional cash
flows (pension contributions, 401(k) auto-invests, mutual fund
rebalancing, index fund flows) that cluster in this window regardless
of the asset's own price behavior. This is a flow-driven, not
information-driven, mechanism -- the kind our validated findings
(range persistence, overnight coil) are NOT (those are pure
volatility-clustering). This is the project's first attempt at a
flow/calendar mechanism rather than a volatility mechanism.

Data requirement: none beyond what we already have. TOM classification
is derived purely from the calendar (trading-day-of-month), computed
from our existing NQ 1-min bar timestamps. No new data source, no
cost.

## Definition (magnitude-neutral where possible, but this IS inherently
a directional-mechanism hypothesis per the literature -- flagging this
up front per the LEARN direction-ambiguity failure mode; the measure
below is designed to test the direction that IS pre-specified in prior
literature, not discovered post-hoc)

Event: TOM window = last trading day of month through the 3rd trading
day of the following month, inclusive (the standard Ariel/Lakonishok-
Smidt window). Classify every RTH session in Discovery as TOM or
non-TOM (complement).

Outcome: close-to-close RTH return (09:30 open to 16:00 close, signed,
in points and in R using the project's standard 0.75pt round-trip
cost convention) for TOM days vs. non-TOM days.

Pre-specified direction (from literature): TOM days have a higher mean
return than non-TOM days. This is a directional pre-commitment stated
BEFORE running Discovery, per protocol -- avoids the direction-
ambiguity failure mode that hit OBS-FINDING-010.

## Method

Bootstrap mean-difference CI (N_BOOTSTRAP=3000, seed=7, 90% CI) on
(TOM mean return - non-TOM mean return), same convention as
observatory_v5/v6/v7. ATR-normalized cost-aware screen applies (v4
convention, 0.05 floor) since this is a directional/return finding,
not a magnitude finding.

Given ~10 years of Discovery data (~2500 trading days), expect roughly
4 TOM days/month x ~120 months = ~480 TOM-day observations -- a much
larger sample than most of this project's occurrence-based findings,
which reduces (but does not eliminate) the thin-sample-overconfidence
failure mode.

## Per protocol

Exploratory only, Discovery data only, non-trading. A credible AND
cost-viable result gets its own Behavioral Finding, then a frozen
hypothesis spec through the standard Discovery -> Validation pipeline
(2-attempt limit) before any live consideration. A null result gets
logged to the ledger and closes this thread -- no retuning the window
boundaries after seeing the result (the Ariel/Lakonishok-Smidt window
definition is taken as given, not fit to our data).
