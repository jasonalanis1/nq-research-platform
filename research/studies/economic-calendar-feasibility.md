# Economic-Release Calendar Feasibility Report

**Status: feasibility CONFIRMED via free, authoritative sources. No
experiment created, no ledger entry, no calendar data purchased or
downloaded, no hypothesis frozen, Validation/Holdout untouched.**
Produced per Jason's explicit instruction, following the pivot after
exp-038 (daily time-series momentum, null) and the Advisor's
recommendation to test this family next -- see `docs/ROADMAP.md`'s
2026-09-02 entries.

## 1. Data cost

Researched via live web search (2026-09-02), not assumed from memory,
same discipline as the ES feasibility check. Three commercial calendar
aggregators were evaluated (Trading Economics, Financial Modeling Prep,
Investing.com/ForexFactory) alongside official government sources.

**Finding: this hypothesis does not need a paid commercial calendar at
all.** The three most commonly cited market-moving US scheduled
releases -- FOMC rate decisions, CPI, and the monthly Employment
Situation (NFP) -- are each available, free, with exact release dates
and times, directly from the issuing government agency:

- **FOMC decisions**: federalreserve.gov publishes each meeting's press
  release with an explicit release-time header (e.g. "For release at
  2:00 p.m. EDT," confirmed on the 2016-06-28 release). Historical
  materials pages cover 2015-2020 year-by-year, plus the standard
  press-release archive covers 2021.
- **CPI and NFP**: bls.gov maintains year-by-year "Schedule of
  Releases" archive pages (e.g. bls.gov/schedule/2016/home.htm)
  confirming exact release dates; both are released at a fixed,
  well-documented 8:30 AM ET (BLS's own published convention, rarely
  deviated from).

Total cost: **$0.** No API key, no subscription, no purchase.

## 2. Data availability

Confirmed historical coverage for all three release types across the
full Discovery period (2015-01-01 through 2021-10-03) via the archive
pages above. Approximate counts over that span: ~54 FOMC decisions
(8/year), ~81 CPI releases (12/year), ~81 NFP releases (12/year) --
comparable in order of magnitude to the day-classification sample
sizes already used in exp-035's expiration-week check.

Two commercial paid alternatives were also researched in case broader
multi-indicator "surprise" (actual-vs-expected) data is wanted later:
Trading Economics (~$149-299/month, third-party-sourced pricing, not
required for this hypothesis) and Financial Modeling Prep (Premium
tier ~$59/month, needed for 2015-era historical depth). Neither is
needed for the frozen hypothesis below, which only requires release
*dates and times*, not surprise magnitudes.

Two free-to-browse sites (Investing.com, ForexFactory) were explicitly
**ruled out**: both have Terms of Service that expressly prohibit
automated scraping and redistribution, with no official API offered as
an alternative. Not used, regardless of convenience.

## 3. Technical integration

Simpler than the ES cross-market work: this needs no second instrument,
no cross-instrument join, no new data-loader changes. It's a **day
classification** problem, structurally identical to exp-035's
"is_exp_week" pattern already built and tested for the futures-
expiration study -- a small, manually-assembled CSV of ~216 dates (54
FOMC + 81 CPI + 81 NFP) with release date and time, loaded once and
joined to the existing per-day return/forward-return dataframes already
used throughout this project. No changes needed to `data_loader.py`,
`data_split.py`, or any instrument-loading path.

## 4. Timestamp/session compatibility -- the one real design fork

CPI and NFP both release at 8:30 AM ET -- the exact reference point
this project's entire intraday framework is already built around
(`detect_ib_breakout.OPEN_HOUR`/`OPEN_MINUTE`, reused everywhere).
Conditioning "was today a CPI/NFP day" onto the existing 8:30-anchored
forward-return machinery is a clean, direct fit, no new time convention
needed.

**FOMC decisions release at 2:00 PM ET, a different time of day than
every other study in this project has used.** Testing FOMC's own
market reaction honestly would need a *new* reference point (a 2:00 PM
forward-return window), not a reuse of the existing 8:30-anchored one.
Two options: (a) restrict the primary hypothesis to CPI/NFP only, which
fits the existing framework with zero new conventions, deferring FOMC
to a clearly-scoped secondary/future extension; or (b) include FOMC
with its own separate 2:00 PM reference point, a small but real new
piece of machinery. This is a genuine, disclosed design choice for
whichever frozen spec follows this report -- not resolved here.

## 5. Look-ahead considerations

Low risk, structurally: release dates are public knowledge well in
advance (FOMC meeting dates are published up to a year ahead; BLS's
release schedule is published annually in advance), so classifying a
day as "CPI day" or "FOMC day" using only the calendar (not price
data) introduces no look-ahead by construction -- unlike exp-035's
expiration-proximity check, which had to flag that the public
expiration date is a proxy for an unknown actual roll date. There is no
equivalent proxy problem here: the calendar dates are exact and public.

## 6. Research-design feasibility

The natural framing, mirroring exp-035's own structure most directly:
does the post-release forward return (or its variance/magnitude)
differ between release days and non-release days, at the project's
existing horizon menu? This is a clean two-group comparison, reusing
`bootstrap_mean_diff_ci()` unmodified -- no new statistical machinery
needed, unlike the ES and trend-following studies. The main design
discipline required: pre-commit to exactly these three release types
(FOMC, CPI, NFP) for the reason stated in Section 1 (the most commonly
cited, not selected by trying several and picking the interesting
one), and pre-commit to the 8:30-vs-2:00-PM framing decision (Section
4) before looking at any results.

## 7. Risks

(1) Multiple-testing: three release types is three sub-comparisons on
overlapping day-count logic; needs the same "one pre-committed primary
test, others descriptive" discipline as every prior study, not three
separate primary tests. (2) Calendar overlap: FOMC/CPI/NFP dates could
occasionally coincide with each other or with expiration weeks already
tested in exp-035 -- needs a real overlap check before finalizing the
day-classification logic, not assumed away. (3) Manually assembling
~216 dates from year-by-year government archive pages is a real,
non-trivial one-time task (not scraping in the ToS sense -- these are
official public government publication pages, not a commercial site
whose terms prohibit automated access -- but still real effort to do
carefully and verify). (4) Sample size per release type (~54-81 days
each) is smaller than this project's typical characterization-study
samples (~1,100-1,700 days) -- worth sizing the resulting confidence
intervals honestly before over-interpreting a null or a hit.

## 8. Recommendation for the next step

Answering the same four framing questions used for the ES feasibility
report:

**A. Economically feasible** -- yes, confirmed at $0 for the core
hypothesis (FOMC/CPI/NFP dates and times, from free government
sources). Paid commercial calendars exist but are not required.

**B. Technically feasible** -- yes, and simpler than the ES work: no
new instrument, no join, reuses exp-035's existing day-classification
pattern directly.

**C. Scientifically defensible** -- yes, if pre-committed to exactly
FOMC/CPI/NFP (structurally justified as the most commonly cited
releases, not results-chosen) and if the 8:30-vs-2:00-PM framing choice
(Section 4) is resolved before any data is examined, not after.

**D. Sufficiently different from what's already been tested** -- yes.
Conditions on scheduled information timing, not on price/volume
patterns, level touches, volatility regime, or cross-market
comovement -- the one candidate mechanism genuinely distinct from all
four families tested so far (per the Advisor's own framing after
exp-038).

STATUS: **FEASIBLE at zero cost**, pending one disclosed design
decision (Section 4: CPI/NFP-only vs. including FOMC with its own
reference point) to be resolved in the frozen specification.

NEXT ACTION: This report's job is done -- it does not choose or freeze
a hypothesis on its own. Per the newly-mandatory Advisor consultation
rule, both Claude's and the Advisor's independent takes on whether and
how to proceed will be presented to Jason next, before any hypothesis
is frozen. No code has been written beyond this feasibility check.
