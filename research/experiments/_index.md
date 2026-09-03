# Experiments Index

The running scoreboard of everything tested. This file is the source of
truth for what's been tried — update it every time a backtest variant
runs, and never overwrite a previous row's results (add a new row/file
instead, even if it's a re-run of a similar idea).

**Structured format (upgraded 2026-08-16, per docs/RESEARCH_ARCHITECTURE.md's
architecture review, recommendation #3):** each metric now has its own
column instead of being buried in free-text prose. `-` means the value
wasn't recorded for that run (mainly the two earliest experiments,
before this file settled into a consistent write-up format) — never
guessed or backfilled from memory. **Statistically Significant** is
`Not tested` unless a run specifically went through
`confidence_analysis.py`'s bootstrap significance check (see that
script's `Significant (95% two-sided)` line) — a positive expectancy
alone does NOT mean `Yes`.

| ID | Setup | Variant | Date | Sample Size | Win Rate | Expectancy | Profit Factor | Max Drawdown | Statistically Significant | Verdict |
|----|-------|---------|------|--------------|----------|-------------|----------------|----------------|------------------------------|---------|
| exp-001 | ORB | placeholder | 2026-08-15 | 46 | 37.0% | -0.287R (gross, no costs) | 0.51 | -15.10R | Not tested | retest — pipeline validation only, see notes |
| exp-002 | ORB | placeholder | 2026-08-16 | 46 | 37.0% (23.0%-50.9%) | -0.307R (net of costs) | - | - | Not tested | retest — pipeline validation only, see notes |
| exp-003 | Level Sweep Reversal | baseline (pre-variant-split) | 2026-08-16 | 38 | 2.6% (0.0%-7.7%) | -0.684R (net of costs) | 0.36 | -32.02R | Not tested | retest — pipeline validation only, see notes |
| exp-004 | ORB | placeholder | 2026-08-16 | 19 | 63.2% (41.5%-84.8%) | +0.206R (net of costs) | 1.38 | -3.58R | Not tested | retest — tiny sample, see notes |
| exp-005 | Level Sweep Reversal | baseline (pre-variant-split) | 2026-08-16 | 13 | 7.7% (0.0%-22.2%) | -0.822R (net of costs) | 0.54 | -9.52R | Not tested | retest — tiny sample, see notes |
| exp-006 | Level Sweep Reversal | close_any | 2026-08-16 | 16 | 50.0% (25.5%-74.5%) | +0.132R (net of costs) | 2.51 | -4.17R | Not tested | retest — 1 of 3 variants compared, no winner picked, see notes |
| exp-007 | Level Sweep Reversal | close_min_distance | 2026-08-16 | 15 | 66.7% (42.8%-90.5%) | +0.545R (net of costs) | 4.33 | -2.04R | Not tested | retest — 1 of 3 variants compared, no winner picked, see notes |
| exp-008 | Level Sweep Reversal | full_bar_range | 2026-08-16 | 15 | 53.3% (28.1%-78.6%) | +0.238R (net of costs) | 1.94 | -3.02R | Not tested | retest — 1 of 3 variants compared, no winner picked, see notes |
| exp-009 | ORB | placeholder | 2026-08-16 | 125 | 52.0% (43.2%-60.8%) | -0.028R (net of costs) | 0.80 | -18.50R | Not tested | retest — exp-004's positive result did NOT hold up, see notes |
| exp-010 | Level Sweep Reversal | close_any | 2026-08-16 | 68 | 42.6% (30.9%-54.4%) | -0.052R (net of costs) | 1.41 | -9.23R | Not tested | retest — exp-006's positive result did NOT hold up, see notes |
| exp-011 | Level Sweep Reversal | close_min_distance | 2026-08-16 | 63 | 46.0% (33.7%-58.3%) | +0.054R (net of costs) | 1.45 | -10.11R | Not tested | retest — edge compressed hard from exp-007, stayed positive, see notes |
| exp-012 | Level Sweep Reversal | full_bar_range | 2026-08-16 | 60 | 45.0% (32.4%-57.6%) | +0.033R (net of costs) | 1.11 | -6.01R | Not tested | retest — edge compressed hard from exp-008, stayed positive, see notes |
| exp-013 | ORB | placeholder | 2026-08-16 | 493 | 50.5% (46.1%-54.9%) | -0.062R (net of costs) | 0.82 | -55.39R | Not tested | kill — clearly negative at 493 trades, treating as settled, see notes |
| exp-014 | Level Sweep Reversal | close_any | 2026-08-16 | 237 | 42.6% (36.3%-48.9%) | -0.063R (net of costs) | 1.36 | -24.21R | Not tested | retest — confirms exp-010's negative read, weakest of 3 variants, see notes |
| exp-015 | Level Sweep Reversal | close_min_distance | 2026-08-16 | 221 | 45.7% (39.1%-52.3%) | +0.043R (net of costs) | 1.33 | -14.85R | Not tested | retest — held stable vs exp-011, strongest of 3 variants, no winner picked yet, see notes |
| exp-016 | Level Sweep Reversal | full_bar_range | 2026-08-16 | 197 | 45.7% (38.7%-52.6%) | +0.042R (net of costs) | 1.19 | -13.77R | Not tested | retest — held stable vs exp-012, near-tied with close_min_distance, no winner picked yet, see notes |
| exp-017 | Level Sweep Reversal | close_min_distance | 2026-08-16 | 221 | 45.7% (unchanged by cost) | +0.011R (2x-cost stress; was +0.043R normal) | 1.29 (2x-cost stress) | -16.25R (2x-cost stress) | **No** (90% bootstrap CI on total R: -18.89R to +37.08R, spans zero) | retest — thin edge, survives cost stress barely, not yet statistically significant, see notes |
| exp-018 | Level Sweep Reversal | full_bar_range | 2026-08-16 | 197 | 45.7% (unchanged by cost) | +0.010R (2x-cost stress; was +0.042R normal) | 1.16 (2x-cost stress) | -15.04R (2x-cost stress) | **No** (90% bootstrap CI on total R: -17.98R to +34.56R, spans zero) | retest — thin edge, survives cost stress barely, not yet statistically significant, see notes |
| exp-019 | Level Sweep Reversal | close_min_distance | 2026-08-16 | 173 | 43.4% (36.0%-50.7%) | -0.014R (net of costs) | 1.18 | -14.85R | **No** (90% bootstrap CI on total R: -26.38R to +21.45R, spans zero) | retest — FIRST holdout-respecting test of this variant; flipped negative once the 112-day holdout was excluded (was +0.043R when it was included), see notes |
| exp-020 | Level Sweep Reversal | full_bar_range | 2026-08-16 | 151 | 44.4% (36.4%-52.3%) | +0.008R (net of costs) | 1.10 | -13.77R | **No** (90% bootstrap CI on total R: -21.83R to +24.90R, spans zero) | retest — FIRST holdout-respecting test of this variant; shrank to roughly breakeven once the 112-day holdout was excluded (was +0.042R when it was included), see notes |
| exp-021 | Level Sweep Reversal | close_min_distance | 2026-08-20 | 172 | 43.0% (35.6%-50.4%) | -0.021R (net of costs) | 1.15 | -13.80R | **No** (90% bootstrap CI on total R: -29.57R to +20.56R, spans zero) | retest — re-run after the 2026-08-20 rolling-window fix added one research day (513->514); prior comparable result exp-019 (173 trades, -0.014R), essentially unchanged, see notes |
| exp-022 | Level Sweep Reversal | full_bar_range | 2026-08-20 | 150 | 44.0% (36.1%-51.9%) | -0.001R (net of costs) | 1.07 | -12.71R | **No** (90% bootstrap CI on total R: -23.49R to +23.44R, spans zero) | retest — re-run after the 2026-08-20 rolling-window fix added one research day (513->514); prior comparable result exp-020 (151 trades, +0.008R), essentially unchanged, now dead flat, see notes |
| exp-023 | Level Sweep Reversal | close_min_distance | 2026-08-23 | 461 | 43.6% (39.1%-48.1%) | -0.038R (net of costs) | 1.10 | -31.55R | **No** (90% bootstrap CI on total R: -58.67R to +22.21R, spans zero) | retest — FIRST test on the Discovery slice (2015-01-01 to 2021-10-03, non-overlapping with exp-019/021); largest sample yet, negative, see notes |
| exp-024 | Level Sweep Reversal | full_bar_range | 2026-08-23 | 558 | 44.8% (40.7%-48.9%) | -0.083R (net of costs) | 1.30 | -79.21R | **No** (90% bootstrap CI on total R: -93.64R to +1.47R, spans zero but barely) | retest — FIRST test on the Discovery slice (2015-01-01 to 2021-10-03, non-overlapping with exp-020/022); weakest result yet for this variant, see notes |
| exp-025 | Level Sweep Reversal (FVG Entry Trigger) | fvg_entry_close_any | 2026-08-24 | 500 | 41.0% (36.7%-45.3%) | -0.208R (net of costs) | 1.13 | -111.31R | **Yes** (90% bootstrap CI on total R: -149.41R to -59.02R, entirely below zero) | kill — FIRST test of the FVG entry trigger, Discovery slice; first statistically decisive result in the project, see notes |
| exp-026 | Level Sweep Reversal (Trend-Structure Liquidity Filter) | close_min_distance, protected-level sweeps only | 2026-09-01 | 44 | 50.0% (35.2%-64.8%) | +0.118R (net of costs) | 1.22 | -5.41R | **No** (90% bootstrap CI on total R: -6.78R to +17.16R, spans zero) | kill — FIRST test of the liquidity filter; positive but far below the 150-trade promotion bar, not significant; Jason directed this line closed 2026-09-01, see notes |
| exp-027 | Level Sweep Reversal (Trend-Structure Liquidity Filter) | full_bar_range, protected-level sweeps only | 2026-09-01 | 59 | 44.1% (31.4%-56.7%) | -0.076R (net of costs) | 0.88 | -12.15R | **No** (90% bootstrap CI on total R: -19.33R to +11.41R, spans zero) | kill — negative point estimate, no separation from the interior-sweep comparison bucket; Jason directed this line closed 2026-09-01, see notes |
| exp-028 | Initial Balance Breakout (Continuation) | ib_minutes=30, breakout window 9:00am-noon ET | 2026-09-01 | 1654 | 42.6% (40.2%-44.9%) | -0.077R (net of costs) | 0.80 | -130.53R | **Yes** (90% bootstrap CI on total R: -202.05R to -48.21R, entirely below zero) | kill — first continuation-thesis test, largest sample of any setup tested so far, statistically decisive; reinforces exp-013's earlier ORB placeholder finding, see notes |
| exp-033 | Fade the Gap | target=prior_close, 1:1 R:R, noon ET exit window | 2026-09-02 | 1061 | 52.1% (49.1%-55.1%) | -0.079R (net of costs) | 0.86 | -102.84R | **Yes** (90% bootstrap CI on total R: -138.82R to -28.75R, entirely below zero) | kill — direct mechanical test of exp-032's gap-fill/correlation finding; win rate above 50% but not enough to overcome costs under this setup's forced 1:1 R:R, statistically decisive rejection, see notes |
| exp-034 | VWAP Mean Reversion | 2σ entry band, stop=entry±1σ, target=VWAP, open-ended resolution | 2026-09-02 | 2066 | 28.7% (26.7%-30.6%) | -0.628R (net of costs) | 0.47 | -1297.78R | **Yes** (90% bootstrap CI on total R: -1450.38R to -1134.35R, entirely below zero) | kill — first setup sourced from external day-trading-technique research rather than this project's own findings; largest sample and most decisive rejection of any setup tested here, see notes |

**Verdict key:** `keep` (worth pursuing further) · `kill` (edge not
supported, drop it) · `retest` (inconclusive as tested — data, sample
size, or setup definition needs to change before this row means
anything)

**Note on exp-001:** this was run on SYNTHETIC (fake, random-walk) data
as a way to prove the backtest pipeline itself works correctly, not as a
real test of the ORB pattern. A random dataset showing no edge is the
*correct* result. This row should not be read as "ORB doesn't work" —
it means "the code correctly found no edge in data that has none." Real
verdict pending: real data + (likely) Jason's actual setup definition
rather than this placeholder.

**Note on exp-019/exp-020:** these were the fifth round of testing on
this close_min_distance / full_bar_range comparison, following four
earlier rounds (exp-006-008, exp-010-012, exp-014-016, exp-017-018) on
substantially overlapping data, during which a third variant (close_any)
was dropped as weakest. The "not statistically significant" bootstrap
CI reported for both treats each as an isolated test and does not
account for this prior selection history. The practical verdict is
unchanged either way (both were already not significant) — this note
exists for the record's honesty, not because it changes the conclusion.

**Note on exp-029:** not a row in the table above — it's a
characterization study (`research/studies/open-return-persistence.md`),
not a strategy backtest with trades/entry/stop/target, so it doesn't fit
this table's columns. Result: a clean null across five time horizons on
whether the Initial Balance's own direction predicts anything about what
follows (see the study doc and exp-029's write-up for full numbers) —
relevant context for reading exp-028's rejection, not a strategy verdict
of its own.

**Note on exp-030:** also not a row in the table above, same reasoning
as exp-029 — Step 1 (the raw correlation check,
`research/setups/volume-confirmed-ib-breakout.md`) came back null, so
Step 2 (the actual bucket-split backtest that would have produced
trades) was correctly never run. No strategy variant exists to log a
row or a ledger entry for. See the write-up for the honest limitation
found in the baseline used (doesn't control for intraday volume
seasonality) before concluding volume adds nothing here.

**Note on exp-031:** also not rows in the table above, same reasoning as
exp-029/030 — this breaks down the SAME already-logged Initial Balance
Breakout trades from exp-028 by day-of-week rather than testing a new
mechanical variant, so it produces no new strategy to log a row or
ledger entry for. Result: a clean, notably uniform null across all five
weekdays (expectancy -0.056R to -0.092R on every single day) — see the
write-up.

**Note on exp-032:** not a row in the table above (characterization
study, no trades — same reasoning as exp-029/030/031), but flagged
specially: this is the first study in the project to find something
other than a clean null. Gap-fill rate significantly above 50% in both
directions (~58%), and a significant negative correlation between gap
size and the +90-minute forward return. Triggered this study's own
Step 3 rule — see exp-033 for the resulting mechanical-rule test, and
read exp-032's own write-up for why this is being treated cautiously
(multiple-testing exposure, and same-slice circularity) rather than as
a confirmed edge.

**exp-033** (a full table row above) is that mechanical-rule test:
"fade the gap" at 1:1 R:R with a noon exit, entry=today's 8:30 open,
target=prior_close literally. REJECTED, statistically decisively (90%
CI -138.82R to -28.75R, entirely below zero) despite a win rate above
50% — the forced 1:1 structure needed comfortably more than a bare
majority to clear realistic costs. Does not contradict exp-032's
underlying characterization finding, which remains a real, statistically
supported result on its own terms; it shows this specific honest
translation of that finding into a costed trade doesn't survive intact.
See exp-033's write-up for the full interpretation, including a real
data edge case (Sunday's continuous-trading bars) found and fixed during
this test, and confirmation that exp-032's own results are unaffected by
it.

**exp-034** (a full table row above) is the first setup this project has
tested that came from outside its own findings: per Jason's explicit
request for research into widely-used day-trading techniques, VWAP Mean
Reversion (fading a close beyond the session VWAP's 2σ band back toward
VWAP) was chosen as the one genuinely new, institutionally-grounded idea
surfaced by that research (see `research/setups/vwap-mean-reversion.md`'s
"Where this came from" for the full filtering pass against everything
already tested). Result: REJECTED, decisively — the largest sample
(2066 resolved trades) and most statistically decisive rejection in the
project's history (90% CI -1450.38R to -1134.35R, entirely below zero,
0% of bootstrap sims profitable). An important honest finding surfaced
along the way: the setup's open-ended intraday watch window means a
2σ excursion off session VWAP happens on nearly every trading day
(2081 of 2101), not the rare, selective event the source material's
framing implied. Two real implementation bugs were found and fixed
during testing (a stop that could land on the wrong side of entry, and
a small number of zero-risk signals after rounding); both are covered
by new regression tests and documented in the write-up.

**exp-035** is a characterization study, not a strategy row: does
proximity to NQ's public quarterly futures expiration date (3rd Friday
of Mar/Jun/Sep/Dec) explain anything about Initial Balance Breakout's
trades, or about the overnight gap's size -- a direct test of
`docs/ROADMAP.md`'s longstanding, previously untested claim that a
continuous futures contract series shows "small price jumps at
rollover dates." Result: clean null on both checks. IB Breakout's
Expiration Week (n=131, -0.086R) and Normal Week (n=1578, -0.067R)
trades are statistically indistinguishable; the overnight gap runs
somewhat larger near expiration (37.03 vs 32.84 points) but the 90%
bootstrap CI on that difference ([-4.12, +13.70] pts) spans zero. No
mechanical rule triggered, no ledger entry (same characterization-study
convention as exp-029/030/031). Honestly flagged limitation: the public
expiration date is a proxy for this data's actual, unknown roll
date(s), so this null cannot rule out a splice effect on a different
date -- only around this specific proxy. See
`research/studies/futures-expiration-effects.md` and
`research/experiments/exp-035-futures-expiration-effects.md` for the
full reasoning and results.
**exp-036** is a characterization study, not a strategy row: does
realized-volatility regime itself (high vs. low tercile, 20-trading-day
causal trailing lookback, expanding percentile-rank classification)
carry information about the post-8:30 directional return, independent
of any specific price level -- the first hypothesis this project has
tested whose mechanism isn't level-interaction. Went through the most
deliberate freeze process in the project's history: a formal Phase 2
Research Direction Report, then a Frozen Study Specification reviewed
line-by-line by Jason before any code was written, with one approved
change (an originally-proposed minimum prior-history floor was removed
as an unjustified free parameter). Result: clean null on the primary,
pre-committed test. Mean 30-minute return difference between high- and
low-vol days was +1.241 points, 90% bootstrap CI [-0.252, +2.862] --
spans zero -- and below the pre-committed 1.5-point economic threshold
even before considering the sign. Both robustness checks were reported
as-is per the frozen spec: dropping the single largest-magnitude day
barely moved the estimate; a first-half/second-half split showed the
point estimate was unstable across the sample (further reinforcing the
null rather than suggesting a sub-period worth chasing). One secondary
horizon (120 minutes, reported descriptively only per the frozen
no-fishing rule) happened to show a CI excluding zero -- explicitly not
treated as a finding, exactly as the spec pre-committed to avoid. No
mechanical rule proposed, no ledger entry. See
`research/studies/volatility-regime-post-open-behavior.md` and
`research/experiments/exp-036-volatility-regime-post-open-behavior.md`
for the full specification, reasoning, and results.
**exp-037** is a characterization study, not a strategy row -- the
project's first two-instrument analysis: does ES's overnight gap (its
own 8:30 AM ET open minus its own prior-day 4:00 PM ET reference
close, computed identically to NQ's) carry information about NQ's
90-minute post-8:30 forward return, beyond what NQ's own
already-characterized overnight gap (exp-032) already captures? Came
out of a strict, Jason-instructed data-feasibility-only study
(`research/studies/es-cross-market-feasibility.md`) that confirmed a
live Databento cost quote ($8.351282700896) before any hypothesis was
chosen, followed by a Frozen Study Specification reviewed before any
code was written (`research/studies/es-overnight-gap-incremental-information.md`).
Primary test: a joint OLS regression of NQ's forward return on both
NQ's and ES's overnight gaps, with the 90% bootstrap CI on ES's
coefficient (b2) as the pre-committed statistic. Result: clean null --
b2 = -0.0816, 90% CI [-0.432, +0.262] -- spans zero, and the translated
economic effect (1.081 points) fell short of the 1.5-point threshold.
The inner join with NQ's data dropped zero days on either side. Both
robustness checks were reported as-is per the frozen spec: dropping
the single largest-|ES_gap| day barely moved the estimate, and a
first-half/second-half split showed the point estimate was unstable
across the sample. No mechanical rule proposed, no ledger entry. See
`research/studies/es-overnight-gap-incremental-information.md` and
`research/experiments/exp-037-es-gap-incremental-information.md` for
the full specification, reasoning, and results.
**exp-038** is a characterization-and-promotion study, the first at
daily resolution in this project's history: after exp-037's null, the
Path-to-Profitability Advisor recommended testing whether the entire
project's premise held at a different timeframe before spending on new
data, using a classic 252-trading-day time-series-momentum signal
(Moskowitz/Ooi/Pedersen convention) -- long/short NQ based on the sign
of the trailing ~12-month log return, daily rebalanced, fully causal.
Required a disclosed, one-time adaptation of the standing 150-trades
promotion bar (a daily-P&L bootstrap CI and a cost-drag-relative
economic threshold, since this signal flips only a handful of times by
construction) -- approved by Jason and logged in
`docs/ROADMAP.md`'s "Promotion bar" section. Result: clean null -- mean
daily net P&L +0.772 points across 1,463 days, 90% CI [-4.075, +5.501]
-- spans zero. 44 flips across the sample (~6.5/year), so not a thin
1-2-trend bet. Both robustness checks reported as-is: dropping the
largest-magnitude day barely moved the estimate, and a
first-half/second-half split showed the sign itself was unstable. A
real implementation bug (a day-pairing error that dropped two days of
P&L per single missing reference-close day instead of skipping over
it) was caught via a sanity check on the usable-sample size and fixed
before the result was trusted. No mechanical rule proposed, no ledger
entry. See `research/studies/nq-daily-trend-following.md` and
`research/experiments/exp-038-nq-daily-trend-following.md` for the
full specification, reasoning, and results.

## exp-039: Scheduled Macro-Release Volatility (CPI/NFP)

Fourteenth hypothesis, fifth mechanism family (scheduled information),
following the economic-calendar feasibility check and a Jason decision
(against the Advisor's specific recommendation) to scope this to
CPI/NFP only, deferring FOMC. Tests whether NQ's 30-minute post-8:30
**absolute** (magnitude, not signed) return is larger on CPI/NFP
release days than on normal days -- the announcement-volatility-
clustering effect, not a directional-edge claim.

**Result: POSITIVE -- the first non-null result in this project's
history.** Mean |return| difference +11.333 pts, 90% bootstrap CI
[+8.103, +14.939] -- entirely above zero and well past the 1.5-point
economic threshold. Survives dropping the single largest-|return| day
and a first-half/second-half split (both halves independently
significant, though the effect roughly doubles in size in the second
half). Both CPI-only and NFP-only sub-groups independently clear the
same bars. All four secondary horizons (60/90/120/180 min) also agree
in direction, reported descriptively only. Gate conditions 1-4
(statistical credibility, economic meaningfulness, plausible
mechanism, not an artifact) are all satisfied for the first time in
this project; condition 5 (a simple mechanical rule specifiable
without fitting to the result) was flagged in the frozen spec as
unlikely to resolve the usual way, since this is a magnitude finding,
not a directional one -- a volatility-capture structure, not a
long/short signal, would be the natural next design question. No
ledger entry yet. See `research/studies/economic-release-volatility.md`
and `research/experiments/exp-039-scheduled-macro-release-volatility.md`
for the full specification and results.

## exp-040: Scheduled Macro-Release Volatility (FOMC)

Sixteenth hypothesis, second test within the scheduled-information
family (after exp-039's Validation-confirmed CPI/NFP result). Tests
whether NQ's 30-minute post-2:00-PM-ET **absolute** return is larger
on FOMC policy decision days than on normal days. Required one new
piece of machinery (`compute_forward_return_at()`, a parameterized
generalization of the existing 8:30-AM-anchored forward-return
function, since FOMC releases at 2:00 PM ET) and a calendar-overlap
check the Advisor caught was missing from the first spec draft before
sign-off: 6 FOMC/CPI same-day overlaps found and excluded from the
primary classification (47 dates remain), 0 FOMC/NFP overlaps, and 14
of the 47 primary dates found to also fall in an expiration week
(disclosed, not excluded, since exp-035 found that variable null on
its own).

**Result: POSITIVE -- the second non-null result in this project's
history.** Mean |return| difference +13.759 pts, 90% bootstrap CI
[+8.263, +19.831] -- entirely above zero, well past the 1.5-point
economic threshold. Survives dropping the single largest-|return| day
and a first-half/second-half split (both halves independently
significant, effect roughly triples in the second half, same pattern
already seen in exp-039). All four secondary horizons agree in
direction. Release/normal ratio 2.22x, closely matching exp-039's
2.44x Discovery ratio -- strengthening the case that the
announcement-volatility-clustering mechanism is real and general
across release types, not specific to how CPI/NFP was tested. Gate
conditions 1-4 satisfied; condition 5 (a directional mechanical rule)
remains the disclosed limitation. Scoped to Discovery only, matching
how exp-039 was first tested -- Validation replication is a separate
future decision, not automatic. No ledger entry. See
`research/studies/fomc-release-volatility.md` and
`research/experiments/exp-040-fomc-release-volatility.md` for the full
specification and results.

## exp-041: Post-Release Directional Continuation

Seventeenth hypothesis, third test within the scheduled-information
family, first to test DIRECTION rather than magnitude: does NQ's
initial 30-minute post-release move (CPI/NFP/FOMC, pooled) tend to
continue over the following 150 minutes? Unlike exp-039/040, a
positive result here would have been directly a specifiable mechanical
rule, not a disclosed limitation.

**Result: NULL.** Mean directional continuation -2.947 pts, 90% CI
[-11.328, +4.361] -- spans zero. Both robustness checks (drop-largest,
split-half) stay null; the effect's sign is not even stable across the
chronological split. Fourteenth null hypothesis (of seventeen tested,
counting distinct hypotheses). One disclosed, unplanned
side-observation: the cpi-only descriptive breakdown shows a
statistically credible (CI entirely below zero) REVERSAL tendency, not
pre-registered and not promoted -- recorded as a lead requiring its
own fresh frozen spec, not treated as a finding. Does not undermine
exp-039/040's own magnitude findings (a different question about the
same event days). No ledger entry. See
`research/studies/post-release-directional-continuation.md` and
`research/experiments/exp-041-post-release-directional-continuation.md`
for the full specification and results.
