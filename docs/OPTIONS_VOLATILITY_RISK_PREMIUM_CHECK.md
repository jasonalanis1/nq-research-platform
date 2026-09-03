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

**Update, 2026-09-03 (later the same day, device reconnected):** this
project's own real data check has now been run (see "The project's own
real data" section below). It did NOT confirm or contradict the
literature finding above -- it came back honestly inconclusive, because
VXN (a smoothed 30-day volatility average) turns out to be the wrong
instrument to see a single day's event pricing. The literature finding
above remains the best evidence this project has on this question.

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

## The project's own real data (2026-09-03, device reconnected)

Jason downloaded the real VXN (CBOE Nasdaq-100 Volatility Index) daily
history directly from FRED (`data/VXNCLS_MAX.csv`, 2001-02-02 through
2026-09-02) and this project ran its own version of the question above
against its own exact Discovery-period CPI/NFP/FOMC event days -- the
same 160 CPI+NFP days and 47 FOMC days already frozen and used by
exp-039 and exp-040. Script: `src/study_vxn_pricing_check.py`.

**Test 1 (primary, no modeling assumptions): is VXN higher the day
before an event than the day before a normal day?** No. For every
event type -- CPI, NFP, CPI+NFP pooled, FOMC -- the mean VXN level on
the trading day before the event was statistically indistinguishable
from normal days (90% bootstrap CI on the difference straddled zero in
every case; point estimates were tiny, roughly -0.3 to +0.1 points on
a base of about 21). The market's own headline volatility gauge simply
does not visibly move ahead of these specific known dates.

**This is a real, honestly-run result, but it does not mean the
market ignores these events.** VXN is a smoothed, 30-day, blended
measure (same construction as VIX) -- one specific day's known event
is a small fraction of what feeds into a 30-day average, so VXN is
structurally too blunt an instrument to detect single-day event
pricing even if it is genuinely happening (which the literature
finding above says it is, for FOMC and NFP specifically, using actual
short-dated event options rather than a 30-day blended index). Test 1
answering "no measurable difference" is best read as "VXN can't see
this," not "there's nothing there."

**Test 2 (secondary, approximate): does a VXN-derived implied 30-minute
move over- or under-predict the actual realized 30-minute move on
event days?** Initially looked informative -- implied over-predicted
realized by about +9.8 points on CPI+NFP days (90% CI entirely above
zero) -- but a baseline control (running the identical comparison on
ordinary days with no known catalyst) showed the SAME over-prediction,
and larger: about +21.3 points on ordinary days versus +9.8 on
CPI+NFP days, and +18.0 on ordinary days versus +4.6 on FOMC days (not
even significant for FOMC). In other words, the model built to convert
VXN into a 30-minute expected move over-predicts real 30-minute moves
on EVERY kind of day, event or not, and does so MORE on ordinary days
than on event days. That is a property of the modeling assumption
disclosed in the script's docstring (spreading a 30-day figure evenly
across a 390-minute trading day understates how concentrated real
intraday volatility actually is), not evidence about event-day
pricing specifically. Test 2, as built, is not informative on this
question -- disclosed honestly rather than reported as if it were.

**Bottom line:** this project's own real-data check neither confirms
nor overturns the literature-based finding above. It ran a legitimate
test with real data and got an honest "this instrument can't answer
that" result on the sharp version of the question. The academic
finding (real event-day options, not a blended index) remains the
best available evidence. A genuinely decisive project-native version
of this question would need real day-specific options pricing data
(e.g. the Databento CME options pull priced in
`docs/OPTIONS_STRUCTURE_COST_ESTIMATE.md`), not VXN.

## Limitations of this pass, disclosed plainly

This was a literature check, not this project's own data-driven test --
that data-driven version has SINCE been run (see "The project's own
real data" section above) and came back honestly inconclusive on the
sharp version of the question, because VXN (a smoothed 30-day average)
isn't a sharp enough instrument to see single-day event pricing. A
genuinely decisive project-native answer would still need real
day-specific options pricing data, not VXN.

## Sources
- `src/study_vxn_pricing_check.py` -- this project's own real-data check against `data/VXNCLS_MAX.csv` and the exact Discovery event-day universes from `study_economic_calendar.py` / `study_fomc_volatility.py`


- [NBER Working Paper 28306: Event-Day Options](https://www.nber.org/system/files/working_papers/w28306/w28306.pdf)
- [CBOE: S&P Index Volatility Surface Embeds 1/2 Point FOMC Intraday Volatility Premium](https://ww2.cboe.com/insights/posts/s-p-index-volatility-surface-embeds-point-fomc-intraday-volatility-premium)
- [FRED: CBOE NASDAQ 100 Volatility Index (VXNCLS)](https://fred.stlouisfed.org/series/VXNCLS) -- confirms data back to 2001-02-02, correcting the earlier "absent from FRED" finding
- [ALFRED: VXNCLS series page](https://alfred.stlouisfed.org/series?seid=VXNCLS)
