# NQ Market Behavior Observatory — v1 Frozen Design Spec

Status: FROZEN before implementation, per this project's standing
protocol. Approved 2026-09-08 (Jason), following external professional
review of the project's overall direction.

## Objective (verbatim, as approved)

> Build a non-trading exploratory Observatory that measures conditional
> intraday NQ behavior following predefined market events. The
> Observatory may identify candidate behaviors for further research but
> may not declare, promote, optimize, or validate a trading strategy.
> All candidates selected for formal research must subsequently enter
> the existing frozen-specification Discovery/Validation pipeline.

## The core principle: the Observatory discovers, it does not confirm

Everything below exists in service of one rule: nothing the Observatory
outputs is a finding. It is a ranked list of candidates. A candidate
becomes a finding only after it is converted into its own frozen
hypothesis spec and passes the SAME Discovery-then-single-Validation-
prospective-test pipeline every hypothesis in this project has always
used (see `docs/RESEARCH_INTEGRITY_PROTOCOL.md`, unchanged). The
Observatory adds a layer BEFORE hypothesis #81, not a bypass around it:

```
Market data -> Observatory (measurement only, Discovery slice only)
            -> ranked candidate list (exploratory, disclosed exposure)
            -> [human/AI selects a candidate]
            -> frozen hypothesis spec written (entry/stop/target FIRST
               designed here, not inside the Observatory)
            -> existing Discovery Step 1(+2) test of that specific,
               now-strategy-shaped hypothesis
            -> single pre-registered Validation-slice prospective test
            -> promotion decision (90% bar, unchanged)
```

## v1 scope (deliberately small -- this is itself an experiment)

**Question v1 exists to answer:** does systematically measuring
conditional market behavior produce materially better research
candidates than the strategy-first process used for hypotheses #1-80?
Not "does the Observatory find an edge" -- if v1 produces several
robust, economically coherent behaviors that later survive the existing
validation process, the approach is proven and the Observatory expands.
If it produces many interesting-looking relationships that collapse
under validation, that is an equally real answer: the Observatory is
just another multiple-testing engine, and the project returns to
whatever comes after that (a new data source, most likely).

**Events (reference levels), 5 total:**
- Prior RTH day's high
- Prior RTH day's low
- Overnight (Globex) session high
- Overnight (Globex) session low
- Session VWAP (RTH-cumulative, resets each day)

**States (conditioning variables at the moment of the event), 2
dimensions:**
- Volatility regime: reuses this project's existing
  `RANGE_NARROW_PCTL`/`RANGE_WIDE_PCTL` classification (prior day's
  range vs. its trailing 20-day distribution, unmodified from
  `study_intraday_behavior_batch1.py`) -- 3 buckets: narrow / normal /
  wide.
- Time of day: 4 coarse RTH buckets -- open (09:30-10:30), mid-morning
  (10:30-12:00), midday (12:00-14:00), afternoon (14:00-16:00).

**Outcome horizons:** 1, 3, 5, 10, 15, 30 minutes forward from the
event.

**Measurements per (event type x state bucket x horizon):**
- forward return (points and as a fraction of the day's typical range,
  for comparability across volatility regimes)
- frequency of positive return
- maximum favorable excursion (MFE) and maximum adverse excursion (MAE)
  within the horizon
- the full distribution (mean, median, std, 10th/25th/75th/90th
  percentiles) -- not just the mean, per the explicit instruction that
  the shape of the conditional distribution matters, not only its
  average

## Event definition (formal, to remove the ambiguity in "interacts")

An event fires the FIRST time, per reference level per session, that
price reaches that level: `High >= level >= Low` on some 1-minute bar,
where the level was NOT already touched earlier that same session (for
prior-day-high/low and overnight-high/low, "session" = that RTH day;
for VWAP, first touch after 09:35 to allow the VWAP calculation a few
bars to stabilize). Only the FIRST touch counts -- no re-triggering on
repeated touches of the same level in the same session. This is a
location/state description, not a directional read: it does not matter
whether price is approaching from above or below, or whether it
breaks through, holds, or reverses -- that is exactly the kind of
question the outcome measurement answers, not the event definition.

Non-overlapping handling: if two different reference levels are touched
by the same 1-minute bar (e.g., prior-day high and overnight high sit
at nearly the same price), both events fire independently and are
measured independently -- they are different location facts about the
same moment, not a conflict to resolve.

## Baseline (control) construction

Every conditional measurement is compared against an unconditional
baseline measured the same way, over the same Discovery period: forward
returns and MFE/MAE from EVERY RTH 1-minute bar (not just event
moments), at the same horizons, EXCLUDING bars that fall within any
event's own forward-measurement window (to avoid the baseline being
contaminated by the events themselves). This directly answers the
"12-point move sounds interesting, but NQ moves 11.5 points over
arbitrary 10-minute windows anyway" concern -- every candidate's
reported effect is `conditional - baseline`, never the conditional
figure alone.

## Candidate ranking (NOT p-value gated)

For each (event type x state bucket x horizon) combination, computed
in Discovery data only:
- effect size: conditional mean minus baseline mean, in the same units
- sample size (n events in this bucket)
- 90% bootstrap CI on the conditional-minus-baseline difference
  (same N_BOOTSTRAP=3000/seed=7 convention as every other study, used
  here for effect-size estimation, NOT as a promotion gate)
- consistency across years: Discovery data split into
  early/middle/late thirds; effect sign and rough magnitude checked for
  agreement across all three (a candidate whose sign flips across
  thirds is flagged, not discarded outright, but ranked down)
- concentration check: what fraction of the total effect comes from
  the single largest-magnitude event (a candidate dominated by one or
  two outlier days is flagged, not discarded outright, but ranked down)
- economic plausibility: a short, human/AI-written one-line note per
  candidate (not a computed score) -- does this event x state
  combination have a story, or is it an arbitrary corner of the search
  space that happened to look good

**Labels (not "significant"/"not significant"):** Promising (n
comfortably above this project's usual 40-trade prospective-test floor,
CI clearly away from zero, consistent sign across all three sub-
periods, effect not concentrated in outliers, a plausible mechanism) /
Interesting (meets some but not all of the above -- worth a human/AI
look, not yet worth freezing a hypothesis) / Weak (small, thin, or
inconsistent) / No meaningful difference (conditional ~= baseline).

## Multiple-testing disclosure (built into the output, not an afterthought)

5 events x 3 volatility states x 4 time buckets x 6 horizons x
(4+ measurements each) is a large combination space by construction.
The Observatory's own output file states the total combinations scanned
front and center, and every candidate list is labeled EXPLORATORY. This
is the explicit acknowledgment that "20 extraordinary-looking
combinations out of 500 scanned" are 20 candidates from a search, not
20 discoveries -- exactly Jason's stated design principle.

## Handoff to hypothesis #81 onward

A "Promising" candidate does not get promoted, sized, or traded from
inside the Observatory. It gets written up as its own frozen hypothesis
spec (this project's normal `research/studies/<name>-spec.md` format),
at which point -- and only at which point -- entry/stop/target logic is
designed around the behavior. That spec then runs through Discovery
Step 1(+2) and a single Validation-slice prospective test exactly like
every prior hypothesis in this project. The Observatory's own
exploratory-search exposure does not get inherited as statistical
credibility by the resulting hypothesis -- the hypothesis earns its own
credibility the normal way, from its own frozen, independently-run
test.

## What v1 explicitly does NOT do

No entry/stop/target logic anywhere in this codebase. No P&L, no
R-multiples, no cost model. No declaration that any behavior is an
"edge." No use of Validation or Holdout data (Discovery only, same as
every hypothesis-search phase in this project). No more than the 5
events / 2 state dimensions / 6 horizons listed above -- expansion is a
deliberate v2 decision after v1's own results are reviewed, not
something to add opportunistically while building.
