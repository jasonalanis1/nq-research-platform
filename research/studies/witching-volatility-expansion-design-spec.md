# Quarterly Witching Volatility Expansion -- Observatory v9 Design Spec

Frozen 2026-09-09. Sourced from the market-microstructure research
agent (dispatched this session on "options/gamma expiration mechanics"
and "futures roll/calendar mechanics" -- both independently surfaced
this as the strongest free, no-new-data candidate).

## Mechanism

Quarterly ("quadruple") witching -- the simultaneous expiration of
stock index futures, stock index options, stock options, and
single-stock futures on the third Friday of March/June/September/
December -- is documented to produce abnormally elevated volume and
realized volatility (Stoll & Whaley 1987, 1991, "Program Trading and
Expiration-Day Effects"). This is a magnitude/volatility-clustering
mechanism, the same family as this project's 3 validated findings
(range-contraction, overnight coil, midday-afternoon persistence) --
NOT a directional mechanism, which is why it's framed as a magnitude
comparison here, avoiding the direction-ambiguity failure mode
entirely (per LEARN taxonomy).

Data requirement: none beyond what we already have. Witching dates are
calendar-derived (3rd Friday of Mar/Jun/Sep/Dec) from existing bar
timestamps -- zero incremental cost, same as Turn-of-the-Month.

Distinct from the excluded candidates: NOT options-expiration gamma
pinning (needs OI-by-strike data we don't have), NOT 0DTE gamma flow
(needs paid intraday options data and overlaps H87/H89 gap-fade,
already exhausted), NOT calendar-spread/roll basis effects (cost/
liquidity story, not price -- both research agents independently
concluded this has no directional plausibility).

## Definition (magnitude-based, directional pre-commitment: elevated)

Event: witching day = 3rd Friday of March, June, September, or
December. Outcome: RTH range (High-Low, 09:30-16:00) on the witching
day relative to its own trailing 20-day average RTH range (a ratio --
same convention as hyp-000046/048's range-contraction measurement and
observatory-v7's midday/afternoon measurement). Compared against the
complement (non-witching days).

Pre-specified direction (from literature): witching-day ratio > 1.0
(elevated realized range vs. trailing average), and greater than the
non-witching complement's ratio. Stated before running Discovery.

## Method

Bootstrap mean-ratio CI (N_BOOTSTRAP=3000, seed=7, 90% CI), same
convention as observatory_v7/study_range_contraction. Credible =
witching-day ratio's CI entirely above 1.0 AND above the non-witching
complement's CI. ATR-normalized cost-aware screen does not directly
apply (magnitude finding, like the 3 validated findings) -- a credible
result's economic use would be as a volatility-conditioning input
(added to volatility_conditioning.py), not a standalone directional
trade, per the same protocol as the other 3 range findings.

Sample size caveat (flagged up front, per LEARN thin-sample-
overconfidence failure mode): ~4 witching days/year x ~10 years of
Discovery = ~40 witching-day observations. This is the thinnest sample
of any Observatory scan run this project to date (well under
MIN_N_FOR_PROMISING=40 used elsewhere) -- treat any "Promising" label
here with extra skepticism; a "Interesting" or weaker label is the
realistic ceiling for a sample this size, and a positive result here
would need unusually strong effect size/consistency to be taken
seriously, not just a CI that clears zero on a small n.

## Per protocol

Exploratory only, Discovery data only, non-trading. A credible result
gets its own Behavioral Finding (with the sample-size caveat stated
explicitly), not immediate promotion, given the small-n concern above.
A null result is logged and closes this thread -- no retuning the
witching-date definition after seeing the result.
