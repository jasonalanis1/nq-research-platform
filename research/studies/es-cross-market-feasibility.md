# ES Cross-Market Feasibility Report

**Status: feasibility study only. No experiment created, no ledger
entry, no ES data purchased or downloaded, no ES-vs-NQ test run,
Validation/Holdout untouched.** Produced per Jason's explicit
instruction following the Phase 2 review's acceptance and the closure
of Family C (volatility regime, exp-036, null).

## 1. Data cost

**I could not obtain a live, authoritative cost quote.** Databento's
API host (`hist.databento.com`) is blocked by network egress policy in
both of my execution environments this session -- the sandboxed shell
bridged to your machine and the cloud container both returned a 403
from the proxy on `metadata.get_cost()` and `metadata.get_billable_size()`.
This is an infrastructure limitation of my own access, not a finding
about Databento or your account. The `databento` Python package
installs and imports fine; the API key file (`.databento_key`) is
present and readable; only the outbound network call itself is blocked.

**What I can give you instead: a grounded estimate from your own
prior, already-paid quote**, not a guess. `src/data_fetch_databento.py`'s
own history records that on 2026-08-20 you were quoted and paid $14.42
for the full NQ history pull, 2015-01-01 through that day (~11.64
years), at `ohlcv-1m` / `GLBX.MDP3` / `NQ.c.0`. That's ~$1.24/year.
Scaled to exactly the Discovery-period date range (2015-01-01 ->
2021-10-03, ~6.76 years), the NQ-equivalent cost over that window would
have been roughly **$8.40**. ES is a comparably liquid CME product at
the same `ohlcv-1m` schema (one row per traded minute, not per tick, so
bar count -- and therefore likely cost, since Databento's historical
pricing scales with data volume -- should be the same order of
magnitude as NQ's, not tick-volume-driven). My estimate for ES over the
same Discovery-period range: **roughly $7-12**, not a quote.

**The authoritative number is one command away, but has to be run from
somewhere that can reach Databento.** This exact call, run from your
own Mac Terminal (where the original NQ pulls succeeded) or anywhere
with working egress to `hist.databento.com`, returns the real number in
under a second and purchases nothing:

```python
import sys; sys.path.insert(0, "src")
from data_fetch_databento import get_api_key, DATASET, SCHEMA
import databento as db

client = db.Historical(key=get_api_key())
cost = client.metadata.get_cost(
    dataset=DATASET, symbols=["ES.c.0"], schema=SCHEMA,
    stype_in="continuous", start="2015-01-01", end="2021-10-04",
)
print("ES Discovery-period cost estimate (USD):", cost)
```

**Current account balance: unknown, not stale-assumed.** The only
balance figure in this project's history is "~$124" from 2026-08-16 --
before the $14.42 history-extension purchase and anything since, and
now over two weeks old. I'm not treating that as current. Databento's
Python client doesn't appear to expose a balance/account endpoint (the
prior cost checks were always compared against a balance you read off
the web portal yourself, not fetched programmatically) -- so "current
account/balance information... if the existing tooling exposes it" is
answered honestly as: it doesn't, as far as I can find. You'd need to
check the portal directly.

## 2. Data availability

`GLBX.MDP3` is CME Globex's exchange-wide feed, not a per-symbol
subscription -- ES trades on the same Globex platform as NQ, so the
existing account almost certainly already has entitlement to it with no
subscription upgrade needed. I can't verify this with full certainty
without network access (an entitlement gap would show up as the
`get_cost()` call above failing with a permissions error rather than
returning a number, so that same command doubles as the access check).
Symbol construction: `ES.c.0` follows Databento's standard
`{root}.{roll_rule}.{rank}` continuous-contract convention, the same
`.c.0` (calendar-roll, front month) rule already frozen for `NQ.c.0` --
this should be a direct, like-for-like analog, but I have not been able
to run `symbology.resolve()` to confirm it resolves cleanly across the
full 2015-2021 Discovery window (same network block). Worth confirming
alongside the cost call.

## 3. Technical integration

Retrieving ES through the existing infrastructure is a small,
well-contained change, not a new pipeline. `fetch_databento_minute_data()`
in `src/data_fetch_databento.py` already parameterizes `DATASET`,
`SYMBOL`, and `SCHEMA` as module constants and produces output in the
exact `Open/High/Low/Close/Volume`, NY-time-indexed shape every
downstream script expects (`data_loader.py`, `backtest.py`, etc.).
Pulling ES needs only a second symbol constant (or a small refactor to
accept a symbol argument) and a second output filename convention (e.g.
`ES_1min_databento_<date>.csv`, mirroring the existing `NQ_1min_*.csv`
convention so `data_loader.py`'s file-discovery logic isn't confused).
No change to `backtest.py`, `data_split.py`, or `data_holdout.py` is
needed for the pull itself.

**Expected data volume**, computed directly from the real NQ Discovery
slice rather than guessed: NQ's Discovery slice is 2,236,964 one-minute
bars over 2,101 trading days (2015-01-01 through 2021-10-01, the last
bar before the 2021-10-03 boundary). The full NQ history CSV (2015-01-01
through 2026-04-06) is 3,810,547 rows / 250.9 MB; the Discovery portion
is ~58.7% of that file by row count. Extrapolating the same proportion
to a same-schema, same-date-range ES pull: **roughly 2.0-2.3M rows,
~130-150 MB**, the same order of magnitude as NQ's Discovery file, not
a new category of size.

## 4. Timestamp/session compatibility

Both instruments would come from the identical pipeline path: Databento
returns UTC timestamps, `fetch_databento_minute_data()` localizes to
UTC then converts to `America/New_York` -- so an ES pull would produce
an index directly comparable to NQ's without a separate conversion
step. Both are CME Group products trading on the same Globex platform
under materially the same near-24-hour schedule and daily maintenance
break, so gross session boundaries should align well; I have not
verified minute-level alignment of the maintenance-break window for ES
specifically against NQ's, and wouldn't assume it without checking once
real data is in hand.

**A real, non-trivial risk**: NQ and ES won't necessarily print a
traded bar in exactly the same set of minutes. Databento's `ohlcv-1m`
schema emits a bar only for minutes with at least one trade -- a thin
minute for one instrument and not the other (more likely in the
lower-volume 2015-2016 era, per the same 2011-vs-2015 quality
consideration already documented for NQ) would leave gaps that need an
explicit, pre-decided join strategy (inner join drops the minute
entirely for both; a left join anchored on NQ's bars needs an explicit
forward-fill-or-exclude rule for ES). This is exactly the kind of
"missing bars" question you asked about, and it doesn't have a
default-safe answer -- it has to be a frozen decision at hypothesis
time, not discovered ad hoc.

**Weekends, holidays, and contract rolls**: there is currently no
explicit calendar logic anywhere in this pipeline for any of these --
weekends/holidays are implicitly absent because the raw feed simply has
no trades to report, and the continuous-contract splice at rollover is
handled entirely inside Databento's own `stype_in="continuous"`
symbology, not by any code in this repo. That's already true for NQ
today and would be equally true, unverified beyond a manual spot-check,
for ES -- the same caveat this project already carries and documents
for NQ ("small price jumps at rollover dates") would apply to ES too,
and a joint NQ+ES analysis adds the possibility that the two
instruments' contracts don't roll on the same calendar day, which
hasn't been checked.

## 5. Look-ahead considerations

Structurally, nothing about adding a second instrument breaks the
causal-computation discipline already used throughout this project
(e.g. `get_reference_close()`'s "last bar at or before 4pm ET" pattern)
-- an ES-derived feature computed only from ES bars timestamped at or
before the NQ decision point is point-in-time-safe the same way
existing single-instrument features are, as long as the same discipline
is actually applied to the ES side and not assumed.

The specific new risk this project hasn't had to think about before:
**bar-labeling and publish-latency mismatches between two feeds.**
Both come from the same vendor and schema, so bar-timestamp semantics
should be identical, but this hasn't been directly verified and
shouldn't be assumed. A subtler version: if a "1-minute bar" for one
instrument is finalized/published to the historical record with
different latency than the other's (unlikely but not verified), a naive
timestamp join could implicitly use information that wouldn't actually
have been available "as of" that minute in real time -- the same kind
of honesty check this project already applies to its own reference-close
conventions, just extended to a cross-feed join.

## 6. Research-design feasibility

Agreed with the framing in your message, and worth restating plainly:
**a raw ES-NQ correlation would be close to a foregone conclusion and
would prove nothing useful.** Both are broad equity-index futures
riding largely the same macro factor; a high unconditional correlation
between their returns is the expected, uninteresting null, not evidence
of anything tradable. The only version of this worth testing is
explicitly incremental: does an ES-derived feature predict NQ's forward
return **after** conditioning on NQ's own relevant information (its own
lagged/contemporaneous return, and where relevant its own already-built
features like the overnight gap or the volatility regime), not in
isolation. That's a materially harder research-design problem than a
correlation coefficient, and it needs its own frozen specification
(what NQ-only baseline model the ES feature has to beat, not just
"does adding ES help by eye") before any test is run -- not resolved by
this feasibility check, flagged as the real work still ahead if this
proceeds.

## 7. Candidate mechanisms (up to three, not tested)

**Mechanism 1 -- minute-level lead-lag from differential liquidity/update
speed.** Mechanism: broad market-moving information may get impounded
into the more liquid of two closely related instruments fractionally
faster, creating a brief lead-lag relationship. Info flow: ES's return
over the most recent minute(s) predicts NQ's forward return over a
matched horizon, controlling for NQ's own recent return. Genuinely
different from the level-interaction family: yes -- this is a
cross-instrument timing effect, not a price-level bet. Expressible
without parameter optimization: the general question is well-posed, but
the specific lag length is itself a parameter that needs a structural
(not results-based) justification the way the 20-day vol lookback was
frozen, rather than searched. Expected sample size: very large (every
minute across ~2,100 Discovery trading days, matching NQ's ~2.24M-bar
count) -- good for power, but minute-bar returns are heavily
autocorrelated, so this needs robust/block-bootstrap inference, not a
naive per-minute t-test, or the significance will be badly overstated.
Primary research question: does ES's lagged 1-minute return carry
information about NQ's forward 1-minute return beyond NQ's own
autocorrelation? Look-ahead risk: the bar-labeling/publish-latency
concern in Section 5 applies most acutely here, at the finest
granularity. Multiple-testing risk: high if multiple lags get tried;
low if exactly one lag is frozen in advance.

**Mechanism 2 -- NQ/ES relative strength (spread) as a risk-appetite
signal.** Mechanism: NQ (Nasdaq-100, growth/tech-heavy) is structurally
higher-beta and more discount-rate-sensitive than ES (broad market);
periods where NQ's return diverges from ES's beyond what's typical may
reflect a genuine risk-appetite or sector-rotation shift, not noise.
Info flow: the NQ-minus-ES return spread over a lookback window predicts
NQ's own subsequent path (continuation in trending regimes, or reversion
toward ES). Genuinely different from level-interaction: yes -- it's
about relative performance against a related market, not a price level.
Expressible without optimization: the concept is well-defined, but
needs one upfront, non-results-based choice of lookback window and
normalization (raw point spread vs. beta-adjusted) -- more design
surface than Mechanism 3, below. Expected sample size: daily or
coarser-intraday framing would put this in the same range as the
volatility-regime study (~2,000 Discovery days). Look-ahead risk:
moderate -- any beta/normalization constant must itself be computed
causally (expanding-window, not whole-sample) the same way volatility
regime's terciles were. Multiple-testing risk: moderate, concentrated
in the normalization choice rather than a results-chosen lookback, if
that choice is pinned down structurally in advance.

**Mechanism 3 -- ES overnight gap as incremental information beyond NQ's
own overnight gap (recommended, see Section 9).** Mechanism: this
project's own framework already centers on the 8:30 ET event and
already found real (if untradeable) signal in NQ's own overnight gap
(exp-032). ES's overnight move (its own prior-close-to-open gap,
computed with the identical `get_reference_close()`-style causal
convention already frozen for NQ) is an independent read on "what the
broader market did overnight" that doesn't require re-deriving anything
from NQ's own path. Info flow: does ES's overnight gap predict NQ's
post-8:30 return **after** NQ's own already-characterized overnight gap
is already in the model -- an explicitly nested, incremental-information
test by construction, directly answering Section 6's concern rather than
sidestepping it. Genuinely different from level-interaction: yes.
Expressible without optimization: yes, cleanly -- reuses
`get_reference_close()` and the existing five-horizon menu unmodified,
no new lookback or threshold to invent. Expected sample size: similar
to exp-032's (n in the 500-1,300 range depending on gap-direction
grouping). Look-ahead risk: low, if ES's reference close is computed
with the exact same causal 4pm-ET convention already frozen for NQ.
Multiple-testing risk: lowest of the three -- one clean nested
comparison, not a lag or normalization search.

## 8. Risks

Beyond what's covered per-mechanism above: (1) this would be the
project's first two-instrument analysis, so any code shared between the
NQ and ES loading paths needs its own tests before being trusted, the
same discipline every single-instrument study here has already gone
through; (2) two additional named candidates (D: scheduled economic
info, E: cross-market, now partially explored here) sitting alongside
each other means the project's overall multiple-testing exposure keeps
growing regardless of which one is chosen -- freezing exactly one
mechanism, not more, matters more here than usual; (3) the data-quality
caveat already on record for NQ's pre-2016 era (thin coverage) may or
may not apply identically to ES and hasn't been checked.

## 9. Recommendation for the next step

Answering your four framing questions directly:

**A. Economically feasible** -- very likely yes, based on the grounded
NQ-cost-precedent extrapolation (~$7-12), but not confirmed with a live
quote due to the network block described in Section 1. Not yet a firm
yes.

**B. Technically feasible** -- yes. The pipeline change needed is small
and well-understood; the real technical work is in the join/gap-handling
design (Section 4), not in data acquisition.

**C. Scientifically defensible** -- yes, but only if the eventual test
is framed as incremental information over NQ's own baseline (Section 6),
not a bare correlation. Mechanism 3 is designed around this constraint
from the start; Mechanisms 1 and 2 would need more upfront design work
to meet it honestly.

**D. Sufficiently different from what's already been tested** -- yes,
for all three candidate mechanisms. None is a level-interaction bet;
all condition on or compare against an external instrument rather than
NQ's own price levels.

Given A is not yet confirmed (only estimated), I'm not calling this
fully cleared yet -- one real number is still missing.

STATUS: **FEASIBLE, PENDING ONE CONFIRMATION** (the live cost/access
check in Section 1 -- everything else checked out or is a known,
name-able design decision, not an open unknown).

NEXT ACTION: Run the `metadata.get_cost()` call in Section 1 from
somewhere with working network access to `hist.databento.com` (your own
Mac Terminal is the known-working path, per the original NQ pulls) and
report back the real number and whether it returned successfully
(confirming entitlement) or errored (revealing a gap). No data should
be purchased or downloaded yet -- that call only prices it. Once that
number is in hand, the next decision after this report is choosing and
freezing Mechanism 3 (or overriding that choice) as the one hypothesis
to specify in full, the same way volatility regime was frozen before
any code was written.
