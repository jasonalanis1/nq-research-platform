# Volatility Risk Premium Check: Is the CPI/NFP/FOMC Magnitude Finding Actually Tradeable?

*2026-09-03. Follow-up to `docs/OPTIONS_STRUCTURE_COST_ESTIMATE.md`, which
flagged an unanswered question: exp-039/040 show NQ moves more on
CPI/NFP/FOMC days, but that alone doesn't mean a "buy volatility ahead
of the release" options structure would be profitable, since options
markets typically price in known scheduled events in advance. This
document is a first-pass answer, done without this project's own
day-by-day options data (not yet accessible this session -- see
Limitations). No purchase, no code, no broker account, no experiment,
no ledger entry.*

## The short answer

**Real published research on this exact question, for the closest
available proxy (S&P 500 futures options), found that implied
volatility has historically OVER-predicted what actually happened on
FOMC and jobs-report days -- consistent with the concern raised in the
cost estimate.** This does not by itself kill the idea, but it is real
evidence against a simple "buy volatility ahead of the known event"
structure for two of this project's three event types. CPI specifically
was not found directly studied in this pass.

## What was found

**NBER Working Paper 28306, "Event-Day Options" (Beckmeyer, Glabadanidis, Wright/NBER, 2011-2020 sample):**
studies Treasury futures and S&P 500 E-mini futures options around FOMC
meetings and employment reports specifically. Finding: implied
volatility on these event days runs consistently ABOVE what
subsequently realized -- a positive variance risk premium -- for every
asset studied, S&P 500 included. Reported premium for S&P 500: **0.248
percentage points on FOMC days, 0.204 percentage points on employment-
report days** (variance terms; for 5- and 10-year Treasury futures the
paper states plainly that "about half of the typical increase in
options-implied variance is a variance risk premium" on FOMC days --
i.e. roughly half of what the options market charges extra for these
days does not show up as real movement).

**CBOE's own research desk** (a live commentary post, not an academic
study) independently confirms the mechanism qualitatively for FOMC
specifically: it describes measuring "an intraday volatility premium"
of about half a VIX point specifically attributable to a coming FOMC
decision, embedded in the broader index options market ahead of the
meeting -- corroborating, informally, that the market does price in
FOMC-day risk in advance, consistent with the NBER paper's harder
numbers.

**CPI specifically: not directly confirmed in this pass.** No study
with CPI-specific implied-vs-realized numbers was found in this
search. CPI is the same general category of event (scheduled,
widely-known, uncertainty-resolving) as FOMC and NFP, and the variance
risk premium is a broadly documented phenomenon across most option
markets generally -- so the same pattern is plausible for CPI too, but
this is an inference from the general pattern, not a confirmed,
sourced finding the way FOMC and NFP now are. Flagged honestly as a
gap, not glossed over.

## What this means for the project, without deciding anything

This is real evidence, not a guess -- but it is a proxy (S&P 500
options, not NQ/Nasdaq-100 options specifically) and it is historical
average behavior, not a guarantee about any specific future day. It
meaningfully raises the bar for a simple "buy volatility ahead of a
known release" structure: the closest available real research says
this exact kind of bet has, on average, been a bad trade for the
option buyer on two of this project's three event types. It does not
rule out every possible options-based structure (e.g., a structure
that specifically bets WITH the volatility risk premium -- selling
rather than buying -- would need a different, much larger tail-risk
conversation before it belongs in this project at all) -- but it
substantially weakens the specific idea this thread started from.

## Limitations of this pass, disclosed plainly

This is a literature check, not this project's own data-driven test.
No day-by-day comparison was run between actual VXN levels (or NQ
options pricing) and this project's own 209 specific CPI/NFP/FOMC
event days -- that would be the rigorous, project-standard version of
this question, and it still requires real structured data access
(VXNCLS is confirmed freely available on FRED itself, back to 2001 --
correcting `docs/OPTIONS_DATA_FEASIBILITY.md`'s earlier finding that it
was absent from FRED; that search only checked FRED and missed that it
is, in fact, there) that wasn't reachable with the tools available this
session (page-reading web tools, not a structured CSV/API pull). That
real version of the check remains the next step, not replaced by this
one.

## Sources

- [NBER Working Paper 28306: Event-Day Options](https://www.nber.org/system/files/working_papers/w28306/w28306.pdf)
- [CBOE: S&P Index Volatility Surface Embeds 1/2 Point FOMC Intraday Volatility Premium](https://ww2.cboe.com/insights/posts/s-p-index-volatility-surface-embeds-point-fomc-intraday-volatility-premium)
- [FRED: CBOE NASDAQ 100 Volatility Index (VXNCLS)](https://fred.stlouisfed.org/series/VXNCLS) -- confirms data back to 2001-02-02, correcting the earlier "absent from FRED" finding
- [ALFRED: VXNCLS series page](https://alfred.stlouisfed.org/series?seid=VXNCLS)
