# Idea Inventory — vetted, unscanned research directions

Per AMENDMENT v2.3 (research/infrastructure/agent-governance-structure.md).
Sessions TOP UP in slack, DRAW from the top under load. ENTRY BAR: all
FIVE (state variable, mechanism claim, horizon, Integrity Gate
resurrection ruling, and -- since September 11th 2026, UPGRADE 1 -- a
MAP ANCHOR naming the research/market_structure_map.md entry it probes)
or it is not an entry. Because Mechanism now writes BEFORE the scan
(UPGRADE 3), the one-line mechanism claim here is the seed of the
mechanism doc, not a separate later step. First created 2026-09-10 --
the project's own inventory was never actually seeded despite AMENDMENT
v2.3's own "Status" section describing it as starting empty on
2026-09-10; that session found it missing and created it with 1 entry.

STATUS (September 11th, 2026, adoption staff meeting for the Upgrade
Brief): live entries are Entry 8 (re-anchored to map M7, range use) and
Entry 12 (M5, added 9:37 pm CT). CLOSED this cycle: Entry 9 (M10, Scan 011,
null, 9:33 pm CT), Entry 10 (M11, Scan 012, near-miss not retuned, 9:36 pm CT),
Entry 11 (M1, Scan 013, null, 9:42 pm CT -- closing-move family closed for good).
below. Entry 6 and Entry 7 are SHELVED, not closed -- no attempt spent:
neither names a forced participant (both are volatility-clustering
claims), so neither can carry a map anchor. They may return if a map
entry is added that they genuinely probe. Entries 1-5 closed, see below.
---

## ENTRY 1 — overnight_range_vs_atr, first-RTH-hour reaction (NEW horizon, known descriptor) — CLOSED 2026-09-10 (Scan 006)

1. **STATE VARIABLE**: `overnight_range_vs_atr` (already implemented,
   market_state_primitives.py) — the overnight session's high-low range
   (prior RTH close to today's RTH open) divided by ATR14, bucketed into
   terciles on the frozen Discovery-sample edges used previously (H116's
   own frozen edges, research/studies/overnight-range-mid-10d-drift-h116-spec.md
   — reuse, do not refit). Implementable as written: no new data source,
   only a new forward-return window.
2. **MECHANISM CLAIM**: a wide overnight range means information arrived
   while RTH was closed (Asia/Europe session flow, futures-only price
   discovery, overnight news) that RTH participants have not yet had a
   chance to react to with full liquidity. The FIRST HOUR of RTH is where
   that information gets processed by the deepest pool of participants —
   predicting EITHER continuation (RTH confirms and extends the overnight
   move as more informed flow agrees) or reversion (RTH fades an
   overnight overreaction driven by thinner futures-only liquidity).
   Counterparty: overnight futures-only participants who moved price on
   thin liquidity, now trading against the deeper RTH pool that arrives
   at 09:30 ET.
3. **HORIZON**: intraday — RTH open (09:30 ET) to RTH open + 60 minutes.
   Genuinely untried: H116 (the only prior use of this descriptor) tested
   only 1/3/5/10-TRADING-DAY close-to-close forward windows, never the
   immediate RTH reaction the overnight range itself would most directly
   inform.
4. **INTEGRITY GATE RESURRECTION RULING**: SECOND ATTEMPT on
   overnight_range_vs_atr (H116 = attempt 1, MID tercile, 10d horizon,
   status: per docs/BACKLOG.md, closed after its own Validation-slice
   prospective test — see H116's ledger lineage, hyp-000117/118).
   DIFFERENTLY MOTIVATED, not cosmetic: H116 asked "does an elevated
   overnight range predict a multi-day drift"; this asks "does it predict
   the FIRST HOUR's own reaction," a mechanistically distinct, much
   shorter question using a genuinely different forward-return
   construction (intraday minute-level, not daily close-to-close).
   Engages the 2-attempt limit on overnight_range_vs_atr — this would be
   the LAST attempt on this state variable regardless of outcome.

DRAWN and run 2026-09-10 20:15 UTC session as Scan 006
(src/market_behavior_discovery_scan_006.py). RESULT: 0/3 cells ranked --
clean null, no monotonic gradient, all cells far below both cost floors
(atr_norm 0.011-0.017 vs 0.05 floor). Per this entry's own Integrity Gate
ruling, this was the LAST attempt on overnight_range_vs_atr (H116 =
attempt 1, closed at Validation; this = attempt 2, closed at Discovery).
2-attempt limit now EXHAUSTED -- no further attempts on this state
variable without a new staff-meeting-level justification. No hypothesis
ID spent. Mandatory zero-survivor staff meeting held, disposition PIVOT
(close this entry, continue drawing the remaining shelf). Full detail:
research/sessions/2026-09-10-2015.md, data/market_behavior_discovery_scan_006_results.json.

---

## ENTRY 2 — days_to_monthly_opex, pre/post-expiry volatility compression (G1: mechanism-first, structural) — CLOSED 2026-09-11 (Scan 007)

Generation-meeting positions (fixed order):

- **LEARN**: `days_to_monthly_opex` was scanned once before (Scan 004,
  2026-09-10) testing RETURN direction/magnitude across
  intraday/overnight/1d/2d horizons and terciles — 36 cells, 1 raw
  survivor (`low` tercile / intraday), which FAILED split-sample
  robustness (atr_norm 0.016 vs 0.068 across halves, 4.3x ratio) and was
  closed 0/36. LEARN also surfaces a live DATA INTEGRITY finding from
  this project's own history: the continuous NQ 1-min series has ZERO
  usable RTH bars on quarterly witching Fridays (3rd Friday of Mar/Jun/
  Sep/Dec — the continuous-contract roll appears to splice exactly on
  those dates). 4 of the 12 monthly opex dates/year ARE quarterly
  witching Fridays. Any cell touching the opex day itself, or the day
  immediately adjacent to it, in those 4 months is exposed to this gap.
  Flagged here so Discovery does not silently rediscover it.
- **DISCOVERY (scoping)**: the untested mechanism is not "does opex
  proximity predict tomorrow's return" (closed above) but "does dealer
  gamma-hedging flow around monthly options expiry COMPRESS realized
  volatility (range) into expiry and RELEASE it after" — a pinning /
  post-expiry-unwind claim, tested on RANGE as the outcome, not on
  signed return. State variable reused as-is (`days_to_monthly_opex`,
  already implemented, market_state_primitives_v4.py); new outcome
  variable needed: same-day RTH range on the day immediately before
  opex, and on the day immediately after, each vs. trailing-20d average
  RTH range (existing convention, reused from overnight-coil). No new
  data source. Scoping note for whoever draws this: the two safest first
  cells are the 8 NON-quarterly-witching months (Jan/Feb/Apr/May/Jul/
  Aug/Oct/Nov) run cleanly first; the 4 quarterly-witching months
  either excluded from the initial pass or flagged and reported
  separately, never silently pooled in given the known RTH gap.
- **INTEGRITY GATE (resurrection, per variable)**: SECOND ATTEMPT on
  `days_to_monthly_opex` (Scan 004 = attempt 1). Ruled NOT cosmetic: the
  mechanism claim differs in kind (gamma-hedging-driven volatility
  compression vs. a generic proximity-to-event return-direction scan),
  and the outcome statistic differs (range/realized-volatility vs.
  signed return) — same guard already accepted for the vwap_dist LOW
  1-day variant and the midday-lull persistence-vs-reversion split.
  This is the LAST attempt on `days_to_monthly_opex` regardless of
  outcome.
- **STATISTICAL (multiplicity cost)**: minimal footprint by design — 2
  cells pre-registered (day-before, day-after), each split further only
  by the witching/non-witching data-integrity cut (so effectively up to
  4 reported cells, not a free-ranging bucket sweep). Whoever runs this
  must add a `scan_00X_opex_volatility_compression` entry to
  SCAN_REGISTRY in src/project_wide_multiplicity.py before any CI is
  treated as final, per the module's own maintenance note.
- **MECHANISM (pre-registered predictions, written before any number is
  looked at)**: (1) day-before-opex RTH range < trailing-20d average
  range, more so than an ordinary day (pinning); (2) day-after-opex RTH
  range > trailing-20d average, more so than an ordinary day (unwind);
  (3) FALSIFIABLE: if gamma exposure is the true driver, the effect
  should be WEAKER or ABSENT on the 4 quarterly-witching months once
  their data-integrity risk is controlled for (a different flow regime
  — quarterly witching bundles futures + index options + single-stock
  options expiry together, and typically carries HIGHER, not lower,
  activity) — i.e. the compression story predicts monthly-only opex
  behaves differently from quarterly witching, which is itself a
  testable, falsifying-capable split, not just a data-quality caveat.
- **DIRECTOR DISPOSITION**: CONTINUE — add to inventory as Entry 2,
  frozen scope as above. Genuinely new mechanism claim, no resurrection
  problem, cheap in multiplicity, carries 3 predictions made before any
  number exists (this project's stated general shortage per the
  three-levers diagnosis).

1. **STATE VARIABLE**: `days_to_monthly_opex` (reused, implemented).
2. **MECHANISM CLAIM**: dealer gamma-hedging flow into monthly options
   expiry suppresses realized volatility as expiry approaches (pinning
   toward high-open-interest strikes) and releases it once expired
   positions roll off — counterparty is whoever is short the volatility
   compression without realizing dealer hedging flow is the cause (i.e.
   directional traders reading pre-expiry quiet as a regime signal
   rather than a mechanical, temporary effect).
3. **HORIZON**: intraday/same-day — RTH range on the day immediately
   before and the day immediately after monthly opex. Short per Standing
   Research Priority.
4. **INTEGRITY GATE RESURRECTION RULING**: second (and final) attempt on
   `days_to_monthly_opex`; ruled distinct in mechanism and outcome
   statistic from Scan 004's closed return-direction test. See full
   reasoning above.

DRAWN and run 2026-09-11 02:40 UTC session as Scan 007
(src/market_behavior_discovery_scan_007.py). RESULT: clean null on both
primary (non-witching) pre-registered predictions. before_opex_non_witching
n=54 mean_ratio=1.038 ci_90=[0.938,1.149] (P1 predicted <1, NOT confirmed).
after_opex_non_witching n=53 mean_ratio=0.922 ci_90=[0.789,1.070] (P2
predicted >1, NOT confirmed -- point estimate is even in the opposite
direction from the release prediction, though not credibly so). Witching-
month cells (n=27 each) also both null, no directional signal, reported
separately per this entry's own scoping note -- no evidence either way on
falsifiable prediction P3 since the primary cells never showed an effect
for the witching cells to be weaker or stronger THAN. No gamma-pinning or
post-expiry-unwind signature detectable in raw RTH range at this sample
size. Per this entry's own pre-registered terms, a null on P1/P2 CLOSES
it -- no resurrection terms to invoke, 2-attempt limit on
`days_to_monthly_opex` now EXHAUSTED regardless (Scan 004 = attempt 1,
closed 0/36 on return-direction; this = attempt 2, closed 0/4 on
range-compression). No further attempts on this state variable without a
new staff-meeting-level justification. Ledger: hyp-000138 (Discovery,
REJECTED). SCAN_REGISTRY updated (scan_007, 4 cells, 0 promoted). Full
detail: research/sessions/2026-09-11-0240.md,
data/market_behavior_discovery_scan_007_results.json.

---

## ENTRY 3 — overnight-vs-RTH return divergence persistence (G2: external knowledge input) — CLOSED 2026-09-11 (Statistical stage, REJECTED)

Generation-meeting positions (fixed order):

- **LEARN**: searched docs/BACKLOG.md and the ledger for "overnight
  premium", "overnight anomaly", "close-to-open", "open-to-close" —
  no prior test of this framing exists in this project. Distinct from
  overnight-coil (hyp-000056/057: overnight RANGE predicting RTH RANGE
  persistence — a volatility-magnitude claim) and from Entry 1 above
  (overnight RANGE predicting first-hour reaction). This entry is about
  the SIGN of return earned overnight vs. the sign/magnitude earned
  during RTH — a returns-decomposition claim, not a range/volatility
  claim. No resurrection.
- **DISCOVERY (scoping)**: sourced from published market-microstructure
  research (the well-documented "overnight/close-to-open return
  premium" literature in US equity index futures — e.g. Lou, Polk &
  Skouras-style overnight-return decomposition work cited in the
  project's own prior macro-announcement literature review pattern).
  Per G2's meeting brief: imported ideas take the SAME entry bar and
  resurrection ruling as anything originated in-house, distinguished in
  the ledger by `strategy_origin: external_literature` when drawn (new
  origin tag — `data_discovered` and `rd_generated` already exist in the
  ledger schema; this project has not yet logged an externally-sourced
  idea distinctly, worth adding for provenance). State variable:
  trailing 20-trading-day cumulative overnight return (close-to-open,
  signed) MINUS trailing 20-day cumulative RTH return (open-to-close,
  signed), both ATR-normalized. Buildable from data already on disk with
  one small new function (RTH open-to-close return by day does not yet
  exist as a named descriptor; overnight close-to-open return is already
  implicit in the unsigned `gap_vs_atr` construction and just needs the
  sign kept rather than only the magnitude/distance framing used today).
- **INTEGRITY GATE (resurrection, per variable)**: FIRST ATTEMPT on this
  state variable and this mechanism family. Clean.
- **STATISTICAL (multiplicity cost)**: single pre-registered cell to
  start (does an elevated trailing divergence predict continuation vs.
  reversion of tomorrow's own overnight/RTH split, terciles on the
  trailing-divergence measure, ONE horizon: next 1 trading day). Cheapest
  possible first cut — 3 buckets x 1 horizon = 3 cells, well below any
  prior scan's footprint. Add to SCAN_REGISTRY when run.
- **MECHANISM (pre-registered predictions)**: (1) overnight order flow in
  index futures is structurally dominated by price-insensitive,
  mandate-driven buying (retirement-account and index-fund contribution
  flow transacted via futures/ETF creation ahead of the cash open) while
  RTH flow is more often short-horizon and index-relative, absorbing or
  fading the overnight move — this predicts PERSISTENCE (continuation)
  of an elevated overnight-vs-RTH divergence, not reversion, because the
  structural buyer does not become a seller tomorrow just because they
  bought today; (2) FALSIFIABLE: if the effect is instead a pure
  mean-reverting statistical artifact (stretched z-score reverting to
  mean with no real flow story), the SIGN of predicted next-day
  divergence should be reversion, not persistence — the two mechanisms
  make opposite directional predictions, which is exactly what makes
  this worth a pre-registered single shot rather than a bucket sweep;
  (3) counterparty prediction: the effect, if real, should be WEAKER
  immediately after days classified `low` on `volume_vs_expected` (an
  existing descriptor) since the mechanical flow story predicts the
  effect scales with real participation, not just price action — a test
  NOT restating the effect itself.
- **DIRECTOR DISPOSITION**: CONTINUE — add to inventory as Entry 3.
  Satisfies G2's brief (external, mechanism-attached, cheap, genuinely
  novel to this project) and gives the generation meeting two
  opposite-direction, falsifiable predictions rather than one, which is
  the exact gap the three-levers diagnosis named (zero pre-registered
  mechanisms in this project's history until this session).

1. **STATE VARIABLE**: trailing 20-day cumulative overnight return minus
   trailing 20-day cumulative RTH return, ATR-normalized (new small
   function on existing OHLCV data, no new data source).
2. **MECHANISM CLAIM**: overnight index-futures flow is structurally
   price-insensitive (mandate-driven contribution/rebalancing flow) and
   should persist when elevated, rather than mean-revert, because the
   buyer/seller doing it is not making a tactical call that a stretched
   number would deter — counterparty is RTH participants whose flow
   tends to fade/absorb it without an informational edge of their own.
3. **HORIZON**: next 1 trading day's own overnight/RTH split — short,
   per Standing Research Priority.
4. **INTEGRITY GATE RESURRECTION RULING**: first attempt, clean, no
   resurrection risk found.

Not yet drawn or scanned. Requires: one new outcome/state function (RTH
open-to-close signed return by day, trivial extension of existing
daily-bar machinery) and the trailing-divergence rolling construction,
pre-registered (terciles, single 1-day horizon) before any result is
examined.

DRAWN and run 2026-09-11 03:2X UTC session as Scan 008
(src/market_behavior_discovery_scan_008.py), immediately after the same
session's TOP-UP generation meeting restored the 3-entry floor (added
Entry 5). RESULT: LOW tercile null (n=364, mean=0.0347, ci_90=[-0.0288,
0.1002]); MID tercile null (n=364, mean=-0.0046, ci_90=[-0.0635,0.0533]);
HIGH tercile CREDIBLE (n=364, mean=-0.0746, ci_90=[-0.1371,-0.0099]).
This confirms P2, the pre-registered FALSIFYING ALTERNATIVE
(mean-reverting statistical artifact), NOT P1 (the entry's primary
persistence/mandate-flow mechanism claim) -- the two were mutually
exclusive single-shot predictions on the same two cells, exactly as
designed, and it resolved in the direction that undercuts the original
mechanism story. This is a genuine single-cell Discovery-stage survivor
(credible CI, magnitude above the ~0.05 ATR-unit floor convention used
elsewhere in this project) -- per AGENT PROTOCOL Rule 1, routed to
CANDIDATE TRIAGE rather than closed as a null. Grade and next-step
recorded in research/sessions/2026-09-11-0329.md; per the MECHANISM
GATE, a mechanism doc for the REVERSION story (not the persistence
story this entry pre-registered) is required before this candidate can
advance past Triage to Statistical. Ledger: hyp-000139 (Discovery,
PROMISING). SCAN_REGISTRY updated (scan_008, 3 cells, 1 hypothesis ID
spent). This entry does not re-close under the 2-attempt limit language
used for null closures above -- it remains OPEN, parked at Candidate
Triage, pending the Mechanism-doc step. P3 (volume-conditioning
counterparty check) was run only for the credible HIGH tercile per its
own pre-registration; see data/market_behavior_discovery_scan_008_results.json
for that result. Full: research/sessions/2026-09-11-0329.md,
src/market_behavior_discovery_scan_008.py.

MECHANISM DOC WRITTEN 2026-09-11 (05:45 UTC automated session):
research/mechanisms/overnight-rth-divergence-reversion-high-tercile.md,
POST-HOC (results seen before writing). Explains the WINNING side (P2,
reversion/mechanical-mean-reversion-of-a-stretched-rolling-statistic),
not the entry's own primary P1 persistence claim. Names a genuinely
weak counterparty ("possibly no identifiable counterparty, mechanical
artifact" rather than a named economic actor) -- flagged as a reason
for skepticism regardless of how the 3 new predictions resolve. 3
untested predictions registered: (P1) reversion should be present in
BOTH overnight-driven and RTH-driven subgroups if mechanical, only in
overnight-driven if the entry's P1 story is instead correct with the
wrong sign; (P2) reversion should generalize to 10d/30d window variants
of the same divergence construction, not be a 20d-only knife-edge; (P3)
reversion should be volume-independent if mechanical, weaker under low
volume_vs_expected if flow-driven. Per the MECHANISM GATE, hyp-000139's
input condition for STATISTICAL is now met (not yet run). Ledger:
hyp-000139 updated (status unchanged, PROMISING; notes record the gate
being satisfied).

STATISTICAL STAGE run 2026-09-11 (research/studies/hyp139-statistical-stage-2026-09-11.md,
src/statistical_stage_hyp139.py): 4 questions + same-data selection disclosure +
this mechanism doc's own P1-P3, on the same Discovery sample Scan 008 used. Q3
(project-wide multiplicity correction, the binding constraint) FAILS -- Sidak-adjusted
90% CI [-0.2119, 0.0626] crosses zero at the live Discovery trial count (N=275), even
though the raw CI does not. Q1 (stability) also fails independently (only 1 of 2
chronological halves credible on its own). Mechanism predictions mixed: P2 (10d/30d
window generalization) CONFIRMED; P1 (overnight- vs RTH-driven split) same sign but
underpowered, neither subgroup independently credible; P3 (volume-conditioning) NOT
confirmed and ran opposite the doc's own volume-independence prediction (reversion
concentrated in HIGH-volume days, absent in low-volume days) -- also inconsistent with
this entry's own original P1/persistence story, which predicted the wrong sign
entirely. CLOSED, REJECTED per this project's established binding-constraint convention
(same Q3 multiplicity check closed range-contraction and overnight-coil 2026-09-10).
Ledger: hyp-000139 updated via update_status (PROMISING -> REJECTED). Entry 3 now
CLOSED alongside Entry 1 and Entry 2 -- live count drops to 2 (Entry 4, Entry 5),
TOP-UP owed again.

---

## ENTRY 4 — day_of_week (Friday), RTH range vs trailing-20d average (fresh generation meeting, TOP-UP owed 2026-09-10 20:53 UTC close) — CLOSED 2026-09-11 (Scan 009)

Generation-meeting positions (fixed order):

- **LEARN**: reconciling the record first, because this session's own
  opening state was wrong. The prior session's "Cadence note" (superseded
  below) claimed the 3-entry floor was already met and described Entry 1
  as available to draw; both were false — Entry 1 CLOSED at Scan 006
  (2026-09-10, 0/3, clean null, 2-attempt limit on
  `overnight_range_vs_atr` exhausted), and the live count at that
  session's own close was 2, under the floor. The TOP-UP obligation this
  meeting discharges is real, not manufactured by a stale note — the
  underlying STATUS line and NEXT_UP.md queue item 0 both independently
  confirmed it before this meeting opened. Separately, on the raw
  material: `day_of_week` has never been tested as a standalone,
  individually-scanned state variable in this project. It appears exactly
  twice in the ledger (hyp-000016, hyp-000042), both times as one of 8-16
  features fed into an L1-regularized logistic-regression ensemble
  predicting next-day return SIGN — both runs zeroed out every
  coefficient including day_of_week's, and both closed REJECTED on a
  joint statistical test that never isolated or reported a per-day effect
  at all. That is not a test of "does Friday behave differently," it is a
  test of "does an 8-16-feature linear combination predict tomorrow's
  return sign," which failed for unrelated reasons (all features flat,
  not specifically day_of_week). KNOWN UNEXPLORED, confirmed: day_of_week
  as a standalone variable, with its own directional mechanism claim, on
  its own native outcome (same-day RTH range, not next-day return sign).
- **DISCOVERY (scoping)**: proposes testing `day_of_week` (already
  implemented, market_state_primitives.py, categorical Mon=0..Fri=4) in
  isolation, on Friday specifically, against same-day RTH range vs. the
  trailing-20-day RTH range average (existing convention, reused from the
  overnight-coil and opex-compression framing) — a calendar-liquidity
  claim, not a directional-return claim, and not a re-expression of any
  closed candidate. This is the well-documented "weekend effect" family
  in equity-index literature (position-trimming and thinner
  participation ahead of non-trading-day gap risk) — imported the same
  way Entry 3 imported the overnight-premium literature, tagged
  `strategy_origin: external_literature` when drawn. No new data source;
  no new descriptor code required (day_of_week already exists in
  market_state_primitives.py, only unused as a primary scan variable).
- **INTEGRITY GATE (resurrection, per variable)**: FIRST ATTEMPT on
  `day_of_week` as a standalone hypothesis with its own mechanism and its
  own outcome variable. Ruled NOT a resurrection or cosmetic reframing of
  hyp-000016/hyp-000042: those tested a joint 8-16-feature model against
  NEXT-DAY RETURN SIGN and never reported or isolated a day_of_week
  coefficient or effect on its own; this tests day_of_week alone against
  SAME-DAY RTH RANGE, a different outcome statistic on a different
  variable role (single categorical splitter vs. one input among many in
  a regularized joint fit). Clean. Also checked and ruled distinct from
  Entry 2 (days_to_monthly_opex, a monthly-calendar / options-expiry
  mechanism) and from the validated range-contraction finding
  (range_vs_atr, a volatility-persistence mechanism with no calendar
  component) — day_of_week's mechanism here is liquidity/participation
  tied to the WEEKLY calendar specifically, not multi-day range momentum
  or the monthly options cycle.
- **STATISTICAL (multiplicity cost)**: single pre-registered cell —
  Friday's own RTH range vs. trailing-20d RTH range average, one
  bucket (day_of_week == Friday), one horizon (same day, no forward
  drift). As cheap as Entry 3's first cut (3 cells) and cheaper than
  Entry 2's (up to 4 reported cells) — this is 1 cell. Multiple-testing
  exposure from this entry, if drawn, is minimal; whoever draws it must
  still add a `scan_00X_day_of_week_friday_range` entry to SCAN_REGISTRY
  in src/project_wide_multiplicity.py before quoting any CI as final,
  per that module's standing maintenance note. No bucket sweep across
  all 5 weekdays planned for the first cut — Discovery's own note above
  scopes this narrowly to Friday, where the mechanism claim is sharpest;
  Monday (the natural counterpart, weekend-information-digestion) is
  flagged as a candidate SECOND cell only if Friday's result is credible
  and worth the added multiplicity, never pooled in blind.
- **MECHANISM (pre-registered predictions, written before any number is
  looked at)**: two mechanisms that make OPPOSITE predictions about the
  same cell, the same structure Entry 3 used. (1) RISK-TRIMMING /
  WEEKEND-GAP-AVOIDANCE: participants who do not want open exposure
  across a non-trading weekend (macro headline risk, no ability to react
  intraday) reduce position-taking activity into Friday's close —
  predicts Friday RTH range COMPRESSES relative to the trailing-20d
  average, a volatility-suppression effect from reduced order flow, the
  same directional shape as the opex-pinning claim in Entry 2 but from a
  different (weekly-calendar, not options-expiry) cause. (2) FALSIFYING
  ALTERNATIVE — THIN-LIQUIDITY AMPLIFICATION: if the dominant Friday
  effect is instead simply LOWER PARTICIPATION (fewer market makers and
  algos willing to warehouse risk into an illiquid session) rather than
  active risk-trimming, the same lower-volume condition should EXPAND
  same-size order flow's price impact, not compress it — predicting
  Friday RTH range is ELEVATED, not suppressed, relative to trailing
  average. These are opposite-signed predictions for the identical cell,
  so the single pre-registered test is informative regardless of which
  way it resolves — a clean null (range statistically indistinguishable
  from trailing average) would itself teach something: that neither
  weekly-calendar mechanism is strong enough to show up in raw range,
  distinct from the still-open opex/monthly-calendar question in Entry
  2. (3) A third, non-restating prediction for extra falsification
  power: if either mechanism is real and volume-driven (not purely
  psychological), the effect should be WEAKER on Fridays classified
  `high` on the existing `volume_vs_expected` descriptor (i.e., Fridays
  that actually saw normal-or-above participation should look more like
  an ordinary day) — the same style of non-restating counterparty check
  Entry 3 used with the same descriptor.
- **DIRECTOR DISPOSITION**: CONTINUE — add to inventory as Entry 4. Clears
  the NO MANUFACTURED WORK standing test on both prongs: this is a claim
  the project would have proposed before seeing any data (weekend-effect
  liquidity mechanisms are a standard, pre-existing market-microstructure
  hypothesis family, not fit to anything already observed in this
  project's own results), and a null teaches something concrete (that
  neither the risk-trimming nor the thin-liquidity story is strong enough
  to move raw same-day RTH range on this instrument, narrowing what the
  weekly calendar can plausibly explain going forward). Single cell, two
  opposite pre-registered predictions, first attempt on a variable that
  has sat unused as a standalone hypothesis for the whole project despite
  being implemented since v1 of market_state_primitives.py. Restores the
  3-entry floor.

1. **STATE VARIABLE**: `day_of_week` (already implemented,
   market_state_primitives.py), restricted to the Friday value for the
   first cut.
2. **MECHANISM CLAIM**: Friday RTH range differs from an ordinary day's
   because of weekly-calendar-driven participation changes — EITHER
   compressed (risk-trimming ahead of non-trading weekend gap exposure)
   OR elevated (thinner liquidity amplifying ordinary order flow's price
   impact) — counterparty on the compression story is whoever reads a
   quiet Friday as a directional signal rather than a mechanical
   participation effect; counterparty on the amplification story is
   whoever is short volatility into what looks like an ordinary Friday.
3. **HORIZON**: same day — Friday's own RTH range against its own
   trailing-20d RTH range average. No forward drift measured. Shortest
   possible horizon, per Standing Research Priority.
4. **INTEGRITY GATE RESURRECTION RULING**: first attempt on `day_of_week`
   as a standalone hypothesis with its own mechanism and outcome
   variable; the two prior ledger appearances (hyp-000016, hyp-000042)
   tested it only as one of many zeroed-out coefficients in a joint
   next-day-return-sign model and never isolated a day_of_week effect.
   Clean, not a resurrection.

Not yet drawn or scanned. Requires: no new descriptor code (day_of_week
already exists); one small outcome comparison (same-day RTH range vs.
trailing-20d average, an existing convention reused, not a new
construction) and the SCAN_REGISTRY entry noted above at draw time.

DRAWN and run 2026-09-11 14:2X UTC session (autonomous overnight cycle)
as Scan 009 (src/market_behavior_discovery_scan_009.py). RESULT: primary
pre-registered cell is a CLEAN NULL -- Friday RTH range vs trailing-20d
average, n=307, mean_ratio=1.0319, ci_90=[0.9736,1.0929], straddles 1.0.
Neither P1 (risk-trimming compression) nor P2 (thin-liquidity
amplification) confirmed. Per this entry's own pre-registered terms, a
null itself is informative: neither weekly-calendar mechanism moves raw
same-day RTH range on this instrument at this sample size. No
hypothesis ID spent (same convention as Entry 1's Scan 006 closure --
a clean null on the one pre-registered gating cell does not warrant a
ledger entry). Mandatory zero-survivor staff meeting held, disposition
PIVOT (close this entry; Monday, flagged only as a candidate SECOND
cell contingent on a credible Friday result, is now moot and not run).

P3 (non-restating, reported not gated, per the entry's own scoping):
Friday's own cell splits sharply by volume_vs_expected median --
LOW-volume Fridays: n=104, mean_ratio=0.8367, ci_90=[0.7434,0.9539],
credible, compressed (P1-shaped). HIGH-volume Fridays: n=105,
mean_ratio=1.2418, ci_90=[1.1446,1.3479], credible, elevated (P2-
shaped). Both subgroups are individually credible and point in
OPPOSITE directions -- exactly the kind of pattern that would cancel
out in the pooled primary cell above, which is consistent with what was
observed (pooled result null). This is flagged for awareness only: it
was explicitly pre-registered as non-gating and exploratory, was not
used to retune or re-cut the primary result, and is NOT promoted to a
new hypothesis or a new Idea Inventory entry on this run -- doing so
post-hoc from an already-exploratory split would itself be exactly the
kind of manufactured, results-informed hypothesis generation the
project's NO MANUFACTURED WORK standing test exists to prevent. If a
future generation meeting wants to pursue "does day_of_week's effect on
RTH range depend on volume regime" as its OWN pre-registered claim,
written before re-looking at this split, that is a legitimate fresh
entry -- not assumed here. Full: research/sessions/2026-09-11-1422.md,
src/market_behavior_discovery_scan_009.py,
data/market_behavior_discovery_scan_009_results.json.

---

## Cadence note for the next session

UPDATE September 11th, 3:02 pm CT (scheduled cycle): TOP-UP generation meeting run, added
Entry 8 (vxn_level_vs_trailing HIGH, next-day RTH range vs trailing-20d
average -- second and last attempt on this variable; separability from
the overnight coil pre-registered as a Triage gate). Floor RESTORED to 3
(Entry 6, Entry 7, Entry 8). Entries 1-5 CLOSED. No TOP-UP owed. Per the
DRAW rule, draw order is oldest-live-first: Entry 6, then Entry 7, then
Entry 8.

## ENTRY 5 — |gap_vs_atr| magnitude, same-day RTH range expansion (fresh generation meeting, TOP-UP owed 2026-09-11 session) — CLOSED 2026-09-11 (Director Re-Evaluation, REJECTED: redundant with validated overnight-coil range finding)

RESULT (September 11th, 1:03 pm CT, scheduled cycle): CLOSED at Director Re-Evaluation. Separability
check vs overnight_range_vs_atr (hyp-056/057, validated): corr 0.69; only 32% of
the Scan 010 effect survives controlling for overnight range; the compression leg
is entirely the overnight-coil finding, the elevation leg keeps a ~+10% residual
(credible, n=437). Staff meeting: real but not new -> ABANDON Monetization,
hyp-000140 REJECTED. LEARN: known-true, not-incremental. Full:
research/studies/hyp140-director-reeval-2026-09-11.md.

Generation-meeting positions (fixed order):

- **LEARN**: `gap_vs_atr` (signed opening gap vs prior RTH close, ATR-
  normalized) has been tested repeatedly in this project's history, but
  every prior test (`fade_the_gap`, `gap_down_fade_longonly_h89`,
  `gap_down_fade_multiday_h91`, `gap_fade_h87` and its H87-stability
  reshape) treats the gap as a DIRECTIONAL setup: does price fade back
  toward the gap-fill level, or continue, measured against a signed
  return or R-multiple target. None of them use the gap's MAGNITUDE
  (`abs(gap_vs_atr)`) to predict same-day REALIZED RANGE. Checked
  docs/BACKLOG.md and the ledger by both name and by outcome statistic
  ("gap" + "range" co-occurrence) — no match. KNOWN UNEXPLORED,
  confirmed: gap magnitude as a same-day volatility (not direction)
  predictor.
- **DISCOVERY (scoping)**: proposes `abs(gap_vs_atr)` (already
  implemented as `gap_vs_atr` in market_state_primitives.py, just take
  the magnitude), terciled, against same-day RTH range vs. trailing-20d
  RTH range average — same outcome convention reused from Entry 2 and
  Entry 4 (a range-vs-trailing-average ratio, not a return). A large
  overnight gap means new information arrived that RTH has not yet
  repriced; a small gap means overnight and RTH open agree, i.e. no
  fresh repricing pressure. No new data source, no new descriptor code
  — `gap_vs_atr` already exists, only its absolute value and a new
  outcome comparison are needed (the range-vs-trailing-average
  construction is already used twice in this project).
- **INTEGRITY GATE (resurrection, per variable)**: SECOND USE of the
  underlying `gap_vs_atr` descriptor, but ruled NOT cosmetic and not
  a resurrection: every prior test used the SIGNED value against a
  DIRECTIONAL/return outcome (does the gap fade or continue); this uses
  the ABSOLUTE VALUE against a RANGE/volatility outcome (does an
  uncertain open produce a busier session). Different variable role
  (magnitude vs. sign) and a different outcome statistic (range vs.
  signed return), the same distinction already accepted for Entry 2
  (days_to_monthly_opex: return-direction closed, range-compression
  new) and Entry 4 (day_of_week: joint-model coefficient closed,
  standalone range test new). Ruled: first attempt on gap MAGNITUDE as
  a volatility predictor; the existing signed-gap-fade family (4 closed
  hypotheses) is a separate 2-attempt lineage and is not touched or
  reopened by this entry.
- **STATISTICAL (multiplicity cost)**: single pre-registered cell
  structure — 3 terciles (low/mid/high `abs(gap_vs_atr)`) x 1 outcome
  (same-day RTH range vs trailing-20d average) = 3 cells, no forward
  horizon, no bucket sweep. Same footprint class as Entry 2/Entry 4.
  Whoever draws this must add a `scan_00X_gap_magnitude_range_expansion`
  entry to SCAN_REGISTRY in src/project_wide_multiplicity.py before
  quoting any CI as final.
- **MECHANISM (pre-registered predictions, written before any number is
  looked at)**: (1) HIGH `abs(gap_vs_atr)` tercile -> same-day RTH range
  is credibly ELEVATED vs. trailing-20d average (unresolved overnight
  information gets worked out intraday by the deeper RTH pool — the
  same "information arrived overnight, RTH hasn't reacted yet" logic
  Entry 1 used for the first-hour question, applied here to the whole
  session's range instead of direction); (2) LOW `abs(gap_vs_atr)`
  tercile -> same-day RTH range is credibly COMPRESSED vs. trailing-20d
  average (an open that agrees with the prior close signals no fresh
  repricing pressure, an orderly low-information session); (3)
  FALSIFIABLE, non-restating: if the effect is genuinely about
  UNCERTAINTY rather than mere gap size, it should be WEAKER on HIGH
  `abs(gap_vs_atr)` days that also show `high` `volume_vs_expected`
  (i.e., a big gap that is ALREADY being met with heavy participation
  has already started resolving the uncertainty by the open, leaving
  less incremental range to unfold during RTH) — the same
  non-restating counterparty-check structure Entry 3 and Entry 4 used.
- **DIRECTOR DISPOSITION**: CONTINUE — add to inventory as Entry 5.
  Passes the standing test (would have been proposed before seeing any
  data — gap-magnitude-predicts-realized-volatility is a standard
  market-microstructure intuition, not fit to any of this project's own
  prior gap-direction results) and a null teaches something concrete
  (that overnight repricing uncertainty, measured by gap size alone,
  does not detectably spill into same-day range beyond what ordinary
  days already show). Restores the 3-entry floor to 3 (Entry 3, Entry
  4, Entry 5).

1. **STATE VARIABLE**: `abs(gap_vs_atr)` (existing `gap_vs_atr`
   descriptor, market_state_primitives.py, magnitude only).
2. **MECHANISM CLAIM**: a large opening gap reflects overnight
   information the RTH session has not yet had a chance to fully
   reprice, producing an elevated same-day realized range as the
   deeper RTH liquidity pool works through it; a small gap reflects
   agreement between the overnight and RTH consensus, producing a
   quieter, compressed-range session — counterparty is whoever is
   short realized volatility into a large, unresolved overnight gap
   without accounting for the incremental intraday repricing still to
   come.
3. **HORIZON**: same day — the gap day's own RTH range against its own
   trailing-20d RTH range average. No forward drift measured. Shortest
   possible horizon, per Standing Research Priority.
4. **INTEGRITY GATE RESURRECTION RULING**: first attempt on gap
   MAGNITUDE as a volatility (range) predictor; distinct variable role
   and outcome statistic from the closed signed-gap-fade/continuation
   lineage (4 closed hypotheses, direction-only). Clean, not a
   resurrection.

Not yet drawn or scanned. Requires: no new descriptor code (`gap_vs_atr`
already exists, only `abs()` needed); the range-vs-trailing-average
outcome convention (already reused twice); the SCAN_REGISTRY entry
noted above at draw time.

DRAWN and run 2026-09-11 16:4X UTC session (interactive, Jason present)
as Scan 010 (src/market_behavior_discovery_scan_010.py). RESULT: BOTH
primary pre-registered predictions CONFIRMED, credibly, in the
predicted directions -- HIGH tercile n=556 ratio=1.1921
ci_90=[1.1484,1.2375] (elevation, P1 confirmed); LOW tercile n=556
ratio=0.9130 ci_90=[0.8813,0.9478] (compression, P2 confirmed); MID
tercile null as expected. A genuine two-sided Discovery-stage survivor.
P3 (non-restating, reported not gated) ran OPPOSITE its own prediction:
predicted WEAKER elevation on high-volume HIGH-gap days, found STRONGER
(mean=1.4005 vs 1.0195 low-vol, not even credible on its own) -- a real
flag against the specific uncertainty-resolution causal story, though
it does not undo the confirmed raw elevation/compression finding itself.
Routed to CANDIDATE TRIAGE (hyp-000140, PROMISING), not closed -- stays
OPEN in this inventory, does NOT count toward the 3-entry floor while in
Triage (same convention as Entry 3's Scan 008 handling). Per the
MECHANISM GATE, cannot advance past Triage without a mechanism doc that
also engages with why the P3 volume-conditioning check pointed the
wrong way. SCAN_REGISTRY: scan_010_2026-09-11 (3 cells). Full:
research/sessions/2026-09-11-1635.md,
src/market_behavior_discovery_scan_010.py,
data/market_behavior_discovery_scan_010_results.json.

MECHANISM DOC WRITTEN 2026-09-11 (same interactive session, immediately
following): research/mechanisms/abs-gap-vs-atr-same-day-range-magnitude.md.
NOT post-hoc for the primary claim (P1/P2 were pre-registered before
Scan 010 ran and both confirmed). Proposes a volatility-transmission
mechanism (gap magnitude proxies unresolved overnight repricing the RTH
session inherits) and a diffuse counterparty (whoever prices same-day
range off a trailing average rather than the gap itself) -- weaker than
H118, stronger than hyp-000139's "no identifiable counterparty". Also
engages the P3 anomaly head-on: proposes a reframe (heavy volume on a
large gap CONFIRMS the gap is real rather than resolving its
uncertainty) and writes 3 new, not-yet-tested predictions (gap
validated-vs-faded split; full volume x gap-magnitude grid; a
volume-tercile re-cut of the P3 median split) that must be run before
Director Re-Evaluation or Monetization. STAFF MEETING (interactive,
Jason present) reviewed and accepted the doc: Candidate Triage grade
B, disposition CONTINUE. hyp-000140 stays PROMISING, Entry 5 stays
OPEN -- next queue item is running the doc's own Section 3 predictions
as a pre-registered Statistical-stage pass. Full:
research/mechanisms/abs-gap-vs-atr-same-day-range-magnitude.md.

STATISTICAL STAGE run 2026-09-11 (same interactive session):
src/statistical_stage_hyp140.py,
research/studies/hyp140-statistical-stage-2026-09-11.md. All 4 standard
questions PASS on both LOW and HIGH cells: Q1 stability (both
chronological halves credible, same sign); Q2 regime dependence (not
concentrated in one volatility regime); Q3 magnitude/multiplicity (both
cells SURVIVE Sidak-adjusted correction -- the exact test that closed
hyp-000139 -- with room to spare, clearing the 0.05 floor); Q4 selection
sensitivity (consistent across quintile/tercile/quartile cuts). This is
now the strongest Discovery-stage candidate this project has produced.
The mechanism doc's own P1-P3 predictions, tested honestly: P1
(validated-vs-faded) ran OPPOSITE its prediction (elevation stronger in
the FADED subgroup) -- the doc's reframe for the P3 anomaly does not
hold; P2 (volume x gap grid) confirmed only on the HIGH-gap side, not
symmetric; P3 (volume-tercile re-cut) CONFIRMED the original
volume-conditioning effect is real and not a median-split artifact, but
still without a working causal story. The unresolved P3 mechanism
question is carried forward as an open research question, not a
blocker -- the primary elevation/compression finding does not depend on
it. PROMOTED to Director Re-Evaluation. Full:
research/studies/hyp140-statistical-stage-2026-09-11.md.

## ENTRY 7 — SHELVED September 11th 2026 (no map anchor, no attempt spent) — opening_range_vs_atr (HIGH), next-day RTH range vs trailing-20d average (fresh generation meeting, TOP-UP owed 2026-09-11 16:3X UTC close, Jason present interactively)

Generation-meeting positions (fixed order):

- **LEARN**: `opening_range_vs_atr` (first-30-minute RTH range vs
  ATR14, already implemented since v1) has been tested exactly once,
  as part of Scan 003 (2026-09-09): MID tercile against signed 1-day
  forward RETURN (close-to-close), alongside 3/5/10-day horizons on
  the same directional outcome. That cell cleared the initial gate
  (atr_norm 0.054) but FAILED split-sample robustness (first-half
  effect near zero, 22x magnitude ratio) -- closed, not promoted.
  Every other cell/horizon in that scan tested the same RETURN outcome,
  never RANGE. Checked docs/BACKLOG.md and the ledger for any
  opening_range_vs_atr + range/volatility co-occurrence -- none found.
  Also checked Scan 004 (options-expiration/session-transition/multi-
  day reference-level descriptors) and confirmed opening_range_vs_atr
  was not among that scan's three variables. KNOWN UNEXPLORED,
  confirmed: opening_range_vs_atr as a volatility-persistence (range)
  predictor, distinct from its one prior directional test.
- **DISCOVERY (scoping)**: proposes `opening_range_vs_atr` HIGH tercile
  (a wide first-30-minute range) against the FOLLOWING day's RTH range
  vs. its own trailing-20d RTH range average -- the same range-vs-
  trailing-average convention already reused across Entry 2/4/5/6, and
  the same next-day-forward framing Entry 6 used (today's descriptor,
  known well before the close, predicting tomorrow's own range --
  clean no-lookahead, and avoids the definitional overlap that would
  exist if today's own opening range were used to predict today's own
  full-session range, since the former is a strict subset of the
  latter). HIGH bucket chosen (not MID, which Scan 003 already tested
  and closed) both for freshness and because the mechanism claim below
  is sharpest at the wide-range extreme. No new data source, no new
  descriptor code.
- **INTEGRITY GATE (resurrection, per variable)**: SECOND ATTEMPT on
  `opening_range_vs_atr`, ruled NOT cosmetic: Scan 003 tested the MID
  tercile against a SIGNED RETURN outcome (does a mid-sized opening
  range predict which way price drifts over the next 1-10 days); this
  tests the HIGH tercile against a RANGE outcome (does a wide opening
  range predict tomorrow's own realized volatility). Different bucket,
  different outcome statistic (range vs. signed return), different
  mechanism family (volatility persistence vs. directional momentum/
  reversion) -- the same class of distinction already accepted for
  Entry 2 (days_to_monthly_opex), Entry 4 (day_of_week), Entry 5 (gap
  magnitude) and Entry 6 (volume_vs_expected), each a second use of an
  already-implemented descriptor under a genuinely different question.
  Ruled: clean, not a resurrection. LAST attempt on this state variable
  regardless of outcome (2-attempt limit: Scan 003/mid/return = attempt
  1, closed; this = attempt 2).
- **STATISTICAL (multiplicity cost)**: single pre-registered cell --
  HIGH tercile only, one outcome (next-day RTH range vs trailing-20d
  average), no bucket sweep, no horizon sweep. Same minimal footprint
  class as Entry 4/6. Whoever draws this must add a
  `scan_00X_opening_range_next_day_range` entry to SCAN_REGISTRY in
  src/project_wide_multiplicity.py before quoting any CI as final.
- **MECHANISM (pre-registered predictions, written before any number is
  looked at)**: (1) HIGH `opening_range_vs_atr` -> next-day RTH range
  is credibly ELEVATED vs. trailing-20d average (a wide first-30-
  minute range signals an active, high-conviction session -- fresh
  news, aggressive early positioning -- and that elevated-information
  regime persists at least one more session via ordinary volatility
  clustering, the same logic behind this project's own validated
  range-contraction finding, applied here to a new but structurally
  similar descriptor). (2) FALSIFYING ALTERNATIVE: if instead the wide
  opening range reflects a one-off event that gets fully absorbed
  intraday (news resolves, early positioning completes, no residual
  uncertainty carries forward), next-day range should be
  INDISTINGUISHABLE from trailing average or even COMPRESSED (today's
  session used up the available volatility budget) -- these are
  opposite-signed predictions for the identical cell, so the single
  test is informative regardless of which way it resolves, the same
  structure Entry 3 and Entry 4 used. (3) FALSIFIABLE, non-restating:
  if the effect is genuinely about persistent information flow rather
  than a one-day volatility spike, it should be WEAKER on HIGH-opening-
  range days that ALSO show `low` `volume_vs_expected` that same day
  (a wide range on thin volume looks more like a one-off gap/air-
  pocket than a sustained information-driven regime) -- the same
  non-restating counterparty-check structure Entry 3, 4, and 5 used.
- **DIRECTOR DISPOSITION**: CONTINUE -- add to inventory as Entry 7.
  Passes the standing test (would have been proposed before seeing any
  data -- volatility clustering/persistence is a standard, well-
  established market-microstructure intuition applied to an existing
  descriptor, not fit to this project's own already-observed results)
  and a null teaches something concrete (that a wide opening range,
  measured this way, does not detectably predict tomorrow's own range
  beyond ordinary variation). Restores the 3-entry floor to 3 (Entry 5,
  Entry 6, Entry 7).

1. **STATE VARIABLE**: `opening_range_vs_atr` (already implemented,
   market_state_primitives.py), HIGH tercile only for this first cut.
2. **MECHANISM CLAIM**: a wide first-30-minute RTH range reflects an
   active, high-conviction session (fresh news, aggressive early
   positioning) whose elevated volatility persists into at least the
   next session via ordinary volatility clustering, producing an
   elevated next-day RTH range -- counterparty is whoever is short
   realized volatility into tomorrow's session without accounting for
   today's already-elevated-information regime carrying forward.
3. **HORIZON**: next day -- today's own opening_range_vs_atr (known
   ~10:00 ET) against TOMORROW's own RTH range vs. its trailing-20d
   average. Shortest horizon that avoids the same-day definitional
   overlap (today's opening range is a strict subset of today's own
   full-session range), per Standing Research Priority.
4. **INTEGRITY GATE RESURRECTION RULING**: second and LAST attempt on
   `opening_range_vs_atr` (Scan 003/mid tercile/signed-return = attempt
   1, closed at split-sample); this attempt uses a different bucket,
   a different outcome statistic (range vs. signed return), and a
   different mechanism family (volatility persistence vs. directional
   momentum/reversion). Clean, not a resurrection.

Not yet drawn or scanned. Requires: no new descriptor code
(`opening_range_vs_atr` already exists); the range-vs-trailing-average
outcome convention (already reused four times); the SCAN_REGISTRY entry
noted above at draw time.


## ENTRY 6 — SHELVED September 11th 2026 (no map anchor, no attempt spent) — volume_vs_expected (LOW), next-day RTH range vs trailing-20d average (fresh generation meeting, TOP-UP owed 2026-09-11 12:1X UTC close)

Generation-meeting positions (fixed order):

- **LEARN**: `volume_vs_expected` (RTH volume vs its own trailing-20d
  average, already implemented, market_state_primitives_v2.py) was
  scanned once before (Scan 002, 2026-09-09): `volume_vs_expected/low`
  tercile against 10-day forward RETURN, and it failed the split-sample
  robustness screen outright -- "not credible in the first half at all"
  (docs/BACKLOG.md line ~1402). That closes the RETURN-DIRECTION, 10-DAY
  question for the LOW tercile. It has never been tested against RANGE
  as the outcome, and never at a short (1-day) horizon. It also appears
  as a CONDITIONING variable (not a primary state variable) in Entry
  3's P3 and Entry 5's P3 non-restating counterparty checks -- a
  supporting role only, never the primary hypothesis. KNOWN UNEXPLORED,
  confirmed: volume_vs_expected as a standalone next-day RANGE
  predictor.
- **DISCOVERY (scoping)**: proposes `volume_vs_expected` LOW tercile
  (day already implemented; edges to be cut fresh on the frozen
  Discovery-sample convention used throughout this project, not reused
  from Scan 002's return-oriented edges since the outcome differs) against
  the FOLLOWING day's RTH range vs. its own trailing-20d RTH range
  average -- same range-vs-trailing-average convention reused from
  Entry 2/4/5. Mechanism is about tomorrow, not today: a low-volume
  (disengaged) session leaves information under-processed, which the
  next session's deeper participation then works through. No new data
  source; no new descriptor code (volume_vs_expected and the
  range-vs-trailing-average outcome both already exist).
- **INTEGRITY GATE (resurrection, per variable)**: SECOND ATTEMPT on
  `volume_vs_expected`, ruled NOT cosmetic: Scan 002 tested the LOW
  tercile's OWN-day volume against a 10-DAY FORWARD RETURN; this tests
  it against the FOLLOWING day's RANGE (volatility, not direction) at a
  1-day horizon -- different variable role in the causal claim (today's
  volume predicting tomorrow's engagement/range, not today's volume
  predicting a multi-day drift), different outcome statistic, different
  horizon. Same distinction class already accepted for Entry 2
  (days_to_monthly_opex), Entry 4 (day_of_week) and Entry 5
  (gap_vs_atr magnitude). This is the LAST attempt on `volume_vs_expected`
  regardless of outcome (2-attempt limit: Scan 002/return-direction/10d =
  attempt 1; this = attempt 2).
- **STATISTICAL (multiplicity cost)**: single pre-registered cell --
  volume_vs_expected LOW tercile only (not a 3-tercile sweep; MID/HIGH
  not tested unless this cell is credible and a second cut is separately
  justified), one horizon (next 1 trading day), one outcome (range vs
  trailing-20d average). 1 cell -- the cheapest footprint class used so
  far in this shelf (matches Entry 4). Whoever draws this must add a
  `scan_00X_volume_low_nextday_range` entry to SCAN_REGISTRY in
  src/project_wide_multiplicity.py before quoting any CI as final.
- **MECHANISM (pre-registered predictions, written before any number is
  looked at)**: (1) PRIMARY -- a LOW volume_vs_expected day is followed
  by a next-day RTH range that is credibly ELEVATED vs. trailing-20d
  average: thin participation leaves genuine price discovery
  incomplete, and the deeper pool that returns the next session works
  through it, producing a busier follow-on day (the same "unresolved
  information gets processed later, by deeper liquidity" logic Entry 1
  and Entry 5 used, applied here to volume-driven disengagement rather
  than overnight-range or gap size); (2) FALSIFYING ALTERNATIVE, same
  cell -- if low volume instead reflects a genuinely quiet, low-news
  REGIME rather than one under-processed day, the low-volume state
  should be STICKY (today's low volume predicts tomorrow's range is
  ALSO compressed, volatility clustering with volume, not a release);
  the two mechanisms predict opposite signs for the identical cell, so
  the single pre-registered shot is informative either way, the same
  discipline Entry 3/4/5 used; (3) non-restating counterparty check: if
  the elevation mechanism (1) is real, it should be WEAKER when the
  low-volume day itself falls on a Friday (Entry 4's own mechanism, if
  real, already predicts thin Friday participation for calendar
  reasons unrelated to information content) -- controls for the two
  entries' mechanisms being confounded rather than independent.
- **DIRECTOR DISPOSITION**: CONTINUE -- add to inventory as Entry 6.
  Passes the standing test (volume-quiet-day-predicts-next-day-range-
  release is a standard market-microstructure intuition, proposable
  before any data was seen, not fit to this project's own Scan 002
  result which tested something outright different) and a credible
  null teaches something concrete (that today's volume shortfall alone
  does not forecast tomorrow's range once separated from the
  overnight-range and gap-magnitude channels Entry 1/5 already probe).
  Restores the 3-entry floor to 3 (Entry 4, Entry 5, Entry 6).

1. **STATE VARIABLE**: `volume_vs_expected` (already implemented,
   market_state_primitives_v2.py), LOW tercile only, fresh edges cut on
   the Discovery sample for this outcome (not reused from Scan 002).
2. **MECHANISM CLAIM**: a low-volume RTH session reflects incomplete
   price discovery that the next session's deeper participant pool
   works through, producing an elevated following-day RTH range --
   counterparty is whoever reads a quiet volume day as a stable, settled
   price rather than an unprocessed one and is short volatility into
   the next session as a result.
3. **HORIZON**: next 1 trading day's own RTH range. Short, per Standing
   Research Priority.
4. **INTEGRITY GATE RESURRECTION RULING**: second (and final) attempt on
   `volume_vs_expected`; ruled distinct in variable role, outcome
   statistic and horizon from Scan 002's closed 10-day return-direction
   test. See full reasoning above.

Not yet drawn or scanned. Requires: no new descriptor code: only a
lagged (t-1 volume_vs_expected -> t range) join and the SCAN_REGISTRY
entry noted above at draw time.

## ENTRY 8 — vxn_level_vs_trailing (HIGH), next-day RTH range vs trailing-20d average (map anchor M7, range footprint; map-ranked #4) — VALIDATION CANDIDATE, GATED at Holdout (hyp-000142/143/144; Scan 014 9:47 pm CT -> Statistical PASS -> Director CONTINUE -> blind Gate CONDITIONAL resolved -> one-shot Validation PASS 9:57 pm CT: HIGH 1.120 [1.066,1.177], Sidak [1.026,1.213]). Waiting on Jason for a Holdout slot. (fresh generation meeting, TOP-UP owed after Entry 5's Director Re-Evaluation closure, September 11th, 3:02 pm CT scheduled cycle)

Generation-meeting positions (fixed order):

- **LEARN**: `vxn_level_vs_trailing` (VXN daily close vs. its own
  trailing-20d average, market_state_primitives_v2.py, the project's
  only cross-market series on disk) has been used exactly once as a
  state variable: Scan 002 (2026-09-09) tested it against SIGNED
  forward RETURNS (1/2/5/10-day, all three terciles) -- nothing
  survived split-sample. Scan 005 used a different construction
  (nq_vxn_divergence, relative-value reversion) and closed 0/24. Two
  legacy directional hypotheses (vxn_level_standalone_signal,
  vxn_roc_standalone_signal) are closed. NEVER tested: VXN as a
  predictor of NEXT-DAY REALIZED RANGE. Standing LEARN constraint from
  today's hyp-000140 closure applies: any same/next-day-range entry
  must carry a mechanism distinct from the validated overnight-coil
  finding (overnight_range_vs_atr) AND a pre-registered separability
  check against it. This entry is built to satisfy both.
- **DISCOVERY (scoping)**: proposes `vxn_level_vs_trailing` HIGH
  tercile (VXN closing above its own recent norm) against the
  FOLLOWING day's RTH range vs. its trailing-20d RTH range average --
  the same outcome convention as Entry 2/4/5/6/7. VXN's daily close is
  fixed at ~16:15 ET on day t; the outcome is day t+1's RTH session.
  Clean, no lookahead, no definitional overlap. The outcome is already
  normalized by recent realized range, so the variable is effectively
  "implied vol elevated relative to its own norm" predicting "realized
  range elevated relative to its own norm" -- the implied-leads-
  realized question, not a vol-level question. No new data source, no
  new descriptor code.
- **INTEGRITY GATE (resurrection, per variable)**: SECOND ATTEMPT on
  `vxn_level_vs_trailing`, ruled NOT cosmetic: attempt 1 asked whether
  the VXN level predicts DIRECTION (signed return); this asks whether
  it predicts MAGNITUDE (next-day range). Different outcome statistic,
  different mechanism family (options-implied variance information vs.
  directional fear/greed), same class of distinction accepted for
  Entries 2/4/5/6/7. Distinct from overnight_range_vs_atr by
  construction: VXN is an OPTIONS-market price set during the RTH
  session, not a realized overnight price range. Ruled clean, not a
  resurrection. LAST attempt on this state variable regardless of
  outcome (2-attempt limit: Scan 002/return = attempt 1; this = 2).
- **STATISTICAL (multiplicity cost)**: single pre-registered gating
  cell -- HIGH tercile only, one outcome, no bucket or horizon sweep.
  LOW tercile is REPORTED (predicted compressed, <1.0) but is not a
  gating cell. Whoever draws this must add a
  `scan_0NN_vxn_next_day_range` entry to SCAN_REGISTRY before quoting
  any CI as final.
- **MECHANISM (pre-registered predictions, written before any number is
  looked at)**: (1) HIGH `vxn_level_vs_trailing` -> next-day RTH range
  credibly ELEVATED vs. trailing-20d average (options prices embed
  expected variance; when the market is paying up for NQ variance
  relative to its own recent norm, the following session's realized
  range should run above its recent norm -- implied information leads
  realized). (2) FALSIFYING ALTERNATIVE: if elevated VXN is mostly
  variance-risk-premium noise or lags realized vol rather than leads
  it, next-day range is INDISTINGUISHABLE from trailing average.
  Opposite-signed predictions on the identical cell. (3) SEPARABILITY
  (the coil test, pre-registered, gating for advancement not for the
  Discovery result itself): the HIGH-VXN effect, residualised on
  overnight_range_vs_atr tercile, must retain at least 50% of its raw
  magnitude AND stay credible; if it retains less than 50%, it is the
  overnight-coil finding restated through the options market and is
  CLOSED as redundant at Triage, without a Mechanism doc being written.
  (4) Non-restating counterparty check: the effect should be STRONGER
  when the prior-day realized range was NOT already elevated (VXN
  high but yesterday quiet = implied leading realized, the mechanism
  claim; VXN high and yesterday already wild = VXN merely reflecting
  realized). Reported, not gating.
- **DIRECTOR DISPOSITION**: CONTINUE -- add to inventory as Entry 8.
  Passes the standing test (implied-leads-realized is a textbook
  question that would have been asked before seeing any of this
  project's data) and a null teaches something concrete (that VXN,
  measured this way, carries no next-day range information beyond
  what realized range already gives). Restores the floor to 3 (Entry
  6, Entry 7, Entry 8). Built to today's LEARN lesson: separability
  from the coil is pre-registered as a gate, not discovered after.

1. **STATE VARIABLE**: `vxn_level_vs_trailing` (already implemented,
   market_state_primitives_v2.py), HIGH tercile only for the gating
   cell; LOW reported.
2. **MECHANISM CLAIM**: options-implied variance leads next-session
   realized range -- when VXN closes above its own recent norm, the
   market is pricing information about tomorrow's volatility that
   realized range has not yet shown; counterparty is whoever is short
   next-day realized volatility while the options market is paying
   up for it.
3. **HORIZON**: next day -- day t's VXN close (~16:15 ET) against day
   t+1's RTH range vs. its trailing-20d average.
4. **INTEGRITY GATE RESURRECTION RULING**: second and LAST attempt on
   `vxn_level_vs_trailing` (Scan 002/signed return = attempt 1, closed
   at split-sample); different outcome statistic and mechanism family;
   distinct from overnight_range_vs_atr by data source (options vs
   realized overnight range), with the separability check above
   pre-registered as a Triage gate. Ruled: clean, not a resurrection.


---

## ENTRY 9 — M10: midday directional retrace of the morning move (map-ranked #1, September 11th 2026) — CLOSED September 11th, 9:33 pm CT (Scan 011)

RESULT: clean null on all six pre-registered cells (3 |morning-move| terciles x lull 11:30->13:30 and 11:30->16:00; HIGH/lull n=558 mean -0.0006 ATR ci_90 [-0.026,+0.026]). P1 refuted, P2 not credible, P3 untestable (no effect to separate; narrow-midday sub-cell n=77 showed credible continuation, opposite sign -- exploratory, not promoted). Zero-survivor staff meeting held, disposition PIVOT (shelf cadence). Attempt 1 of 2 on M10 spent. No hypothesis ID. Full: research/mechanisms/midday-directional-retrace-m10.md Sections 5-6.

1. **STATE VARIABLE**: morning move = RTH 9:30-11:30 ET close-to-close
   return in ATR14 units (`morning_move_vs_atr`, new primitive, sign kept),
   terciles by |magnitude| cut on the Discovery sample.
2. **MECHANISM CLAIM**: a large morning move is partly carried by liquidity
   thinning into the European close (11:30 ET); when the deep pool returns
   at ~13:30 ET part of that move retraces. Counterparty: whoever chased the
   morning move into thinning liquidity. Falsifier: no retrace, or retrace
   independent of morning-move size.
3. **HORIZON**: intraday -- 11:30 -> 13:30 ET, and 11:30 -> 16:00 as a
   second horizon. Resolves daily.
4. **INTEGRITY GATE RESURRECTION RULING**: NEW. Not the IB-breakout family
   (no breakout), not a gap fade, not the midday-lull RANGE finding
   (hyp-000105/106/133) -- but must be shown SEPARABLE from it at the
   Statistical stage (Portfolio double-count risk). Predictions must be
   written before the scan (Mechanism doc first).
5. **MAP ANCHOR**: M10.

## ENTRY 10 — M11: NQ-ZN correlation breakdown -> 1-3 day (map-ranked #2) — CLOSED September 11th, 9:36 pm CT (Scan 012)

RESULT: P1 fails the pre-registered bar at all three horizons (HIGH corr-tercile fwd return null; HIGH-minus-LOW 3d -0.135 ATR ci_90 [-0.291,+0.019], a near-miss, not retuned). Sign and 1d->3d drift shape matched the claim (P2), recorded as consistent-with only. Zero-survivor staff meeting held, disposition PIVOT (shelf cadence). Attempt 1 of 2 on M11 spent. No hypothesis ID. Full: research/mechanisms/nq-zn-correlation-breakdown-m11.md Sections 5-6.

1. **STATE VARIABLE**: rolling 20-day correlation of NQ and ZN daily RTH
   returns (`nq_zn_corr_20d`), terciles cut on the Discovery sample; ZN
   1-minute data on disk (data/ZN_1min_databento_2026-09-07.csv).
2. **MECHANISM CLAIM**: balanced and risk-parity books size the equity leg
   against the bond hedge; when the hedge stops working (correlation
   flips toward positive) they must cut equity exposure over the next
   sessions. Counterparty: leveraged books de-risking on a schedule, not
   on price. Falsifier: NQ forward return unrelated to correlation state.
3. **HORIZON**: 1, 2, 3 trading days close-to-close.
4. **INTEGRITY GATE RESURRECTION RULING**: NEW. The closed family
   (hyp-000031/034/035) tested "ZN's own move predicts NQ" (lead-lag);
   this tests the CO-MOVEMENT state. Different measurement, different
   claim. LEARN flagged it untried on 2026-09-10.
5. **MAP ANCHOR**: M11.

## ENTRY 11 — M1: cash-close move conditioned on close-window volume (map-ranked #3) — CLOSED September 11th, 9:42 pm CT (Scan 013)

RESULT: clean null on all six pre-registered cells (HIGH close-volume / next-open n=537 mean +0.017 ATR ci_90 [-0.031,+0.065]; LOW null; 10:00 horizon null; no size dependence). Zero-survivor staff meeting held, disposition PIVOT. Attempt 2 of 2 on the closing-move family (with hyp-000110) -- family CLOSED FOR GOOD. No hypothesis ID. Full: research/mechanisms/cash-close-imbalance-volume-conditioned-m1.md Sections 5-6.

1. **STATE VARIABLE**: 15:50-16:00 ET return in ATR14 units, gated by
   15:50-16:00 volume vs. its trailing 20-day mean for that window
   (`close_move_vs_atr`, `close_volume_vs_norm`); HIGH-volume tercile only.
2. **MECHANISM CLAIM**: MOC rebalancing imbalances are executed at the
   cash close and absorbed by futures; an abnormally heavy close window
   marks a forced imbalance whose price impact partially reverts by the
   next open. Counterparty: MOC-constrained funds paying for immediacy.
   Falsifier: next-morning move unrelated to close-window move once
   conditioned on volume.
3. **HORIZON**: overnight -- 16:00 -> next 9:30 open and -> 10:00.
4. **INTEGRITY GATE RESURRECTION RULING**: SECOND AND LAST ATTEMPT on the
   closing-move family (hyp-000110 closing_pressure_reversal was
   unconditioned). Enters only on the volume-conditioned claim. Logged as
   attempt 2 of 2 at insertion.
5. **MAP ANCHOR**: M1.

## ENTRY 12 — M5: month-end NQ-vs-ZN relative performance -> last-2 / first-2 session return (map-ranked #4, September 11th, 9:37 pm CT) — CLOSED September 11th, 11:07 pm CT (Scan 015)

Generation meeting (extra cycle, Jason's direction to use the full budget; TOP-UP owed after Entries 9 and 10 closed this cycle):
- LEARN: turn-of-month (hyp-000108) tested the UNCONDITIONAL calendar claim and closed; M6 was ruled a resurrection. M5 is a different claim -- the conditioning variable is NQ month-to-date minus ZN month-to-date, i.e. how far the equity leg has outrun the bond leg, which 108 never measured. The ZN lead-lag family (031/034/035) used ZN's own move as a signal; here ZN is the benchmark the rebalancer is measured against. Not a resurrection.
- Discovery: both series on disk (NQ, ZN 1-min); ~45 month-ends in the Discovery slice (2015-01 to 2021-09). Novelty: no prior test on relative-performance state.
- Integrity Gate (per-variable): NEW claim, map-anchored. Thin sample flagged as the main risk; Statistical must state power before scope freezes, and the scope must pre-register which horizon is gating so the two horizons are not both mined.
- Statistical (cost): ~45 events x 2 horizons = 2 cells; with n~45 per cell the detectable effect at 90% CI is large (roughly >=0.35 ATR mean); anything smaller will read null even if real. State this in the mechanism doc; do not widen the window post hoc.
- Mechanism: written BEFORE the scan (research/mechanisms/ to follow at draw). Claim, counterparty, 2 predictions, falsifier below.
- Director: ranked #4 on the frozen map ranking; enters the shelf as the next draw after TOP-UP.

1. **STATE VARIABLE**: `nq_minus_zn_mtd` = NQ month-to-date RTH close-to-close return minus ZN month-to-date return, measured at the close of the 3rd-to-last session of the month; terciles cut on the Discovery sample (~45 month-ends).
2. **MECHANISM CLAIM**: pension and balanced mandates rebalance equity vs. bonds at month-end; when NQ has outrun ZN month-to-date they are forced sellers of equity in the last two sessions (and the flow reverses, or fades, in the first two of the next month). Counterparty: mandated rebalancers executing on the calendar regardless of price. Falsifier: last-2-session NQ return unrelated to the HIGH tercile of relative outperformance.
3. **HORIZON**: gating = last 2 sessions of the month (close of session T-3 -> close of last session); reported = first 2 sessions of the next month. Resolves monthly (slow -- thin-sample caveat above).
4. **INTEGRITY GATE RESURRECTION RULING**: NEW. Distinct from hyp-000108 (unconditional), from M6 (does not enter), and from the ZN lead-lag family. Attempt 1 of 2 at insertion.
5. **MAP ANCHOR**: M5.

**RESULT (September 11th, 11:07 pm CT, Scan 015)**: CLOSED, clean null.
n=79 usable month-ends (nearly double the ~45 estimated at scoping -- not
a thin-sample non-result). HIGH tercile gating return -0.0405 ATR ci_90
[-0.4063,+0.3185] (null); LOW +0.1960 ATR ci_90 [-0.1442,+0.5554] (null);
no monotonic gradient (only MID was credible, at -0.3988, which the
mechanism does not predict as the standalone effect). P1_FAIL. Reported
(reversal) window not mined per pre-registered scope. Mechanism doc
updated (research/mechanisms/nq-zn-month-end-relative-performance-m5.md).
No hypothesis id spent. Attempt 1 of 2 on nq_minus_zn_mtd closed; one
attempt remains if a genuinely different horizon/window is proposed later.

## ENTRY 13 — M3b: post-FOMC-statement continuation vs. reversal (14:00 -> 14:30 / 15:00 / close) (map-ranked #5, September 11th, 9:41 pm CT) — CLOSED September 11th, 11:13 pm CT (Scan 016)

Generation meeting (extra cycle; TOP-UP owed after Entry 11 closed):
- LEARN: the release-day reaction family is CLOSED for CPI/NFP (hyp-000115/116, 8:30 releases). FOMC 14:00 is a different event never tested post-release; pre-FOMC drift (hyp-000111) tested the 24h BEFORE the statement, not the reaction after. Not a resurrection. FOMC dates already on disk in src/study_fomc_volatility.py (FOMC_DATES).
- Discovery: the state is the first-30-minute post-statement move (14:00 -> 14:30) in ATR units, signed; outcomes are the subsequent 14:30 -> 15:00 and 14:30 -> 16:00 returns, sign-adjusted so continuation is positive.
- Integrity Gate (per-variable): NEW claim, map-anchored. THIN: ~8 events/yr, roughly 55 statements in the Discovery slice. Two horizons only; gating horizon pre-registered as 14:30 -> 16:00 (the presser at 14:30 is inside it; continuation through the presser is the claim).
- Statistical (cost): n~55 per cell x 1 tercile split is too thin for terciles -- scope as a SINGLE cell (all FOMC days, sign-adjusted continuation) plus a reported split by |initial move| median. Detectable effect at n~55 is large (roughly >=0.3 ATR); stated so a null is read as "underpowered or absent", never as "absent".
- Mechanism: written BEFORE the scan (research/mechanisms/ at draw). Claim: dealers re-hedge and systematic books re-position on the statement's surprise, and the presser at 14:30 usually confirms rather than reverses the statement, so the initial 30-minute move continues into the close. Counterparty: whoever fades the initial move expecting the presser to walk it back.
- Director: rank 5 on the frozen map ranking; enters the shelf after M5 (Entry 12).

1. **STATE VARIABLE**: `fomc_initial_move_vs_atr` = (14:30 close - 14:00 close) / ATR14 on FOMC statement days, signed (windows half-open).
2. **MECHANISM CLAIM**: statement surprise triggers dealer re-hedging and systematic re-positioning that takes more than 30 minutes to complete; the 14:30 presser confirms the statement more often than it reverses it, so the initial move continues. Counterparty: fade traders positioned for a presser walk-back. Falsifier: sign-adjusted 14:30 -> 16:00 return not credibly positive, or credibly negative (reversal).
3. **HORIZON**: intraday, gating 14:30 -> 16:00; reported 14:30 -> 15:00. Resolves per FOMC day (thin, ~8/yr).
4. **INTEGRITY GATE RESURRECTION RULING**: NEW (different event from CPI/NFP; different window from pre-FOMC drift). Attempt 1 of 2 at insertion.
5. **MAP ANCHOR**: M3b.

**RESULT (September 11th, 11:13 pm CT, Scan 016)**: CLOSED, clean null.
n=52 usable FOMC days (of 53 registered -- essentially the full sample,
not an underpowered subset). Sign-adjusted 14:30->16:00 continuation mean
-0.0126 ATR ci_90 [-0.1381,+0.1076], not credibly positive. P1_FAIL. P2
(initial-move-size split) not mined per pre-registered scope. Mechanism
doc updated (research/mechanisms/post-fomc-continuation-m3b.md). No
hypothesis id spent. Attempt 1 of 2 on the post-FOMC-continuation claim
closed; one attempt remains if a genuinely different window is proposed.

## ENTRY 14 — M4: pre-FOMC drift, exact Lucca-Moench window (map-ranked #6; SECOND AND LAST attempt on pre-FOMC drift; September 11th, 9:50 pm CT) — CLOSED FOR GOOD September 11th, 11:18 pm CT (Scan 017)

Generation meeting (extra cycle; TOP-UP owed after Entry 8 went to Validation Candidate):
- LEARN / Discovery verification (the map's own entry condition): hyp-000111 (study_pre_fomc_drift.py) measured (a) the PRIOR day's full RTH return and (b) the overnight return into the FOMC morning. The Lucca-Moench (2015) window is prior-day 14:00 ET -> FOMC-day 14:00 ET: it EXCLUDES the prior-day morning that 111 included and INCLUDES the FOMC-day 09:30-14:00 session that 111 omitted. The windows differ materially; the map's entry condition is met. This is attempt 2 of 2 on pre-FOMC drift and the LAST.
- Integrity Gate (per-variable): enters only on the exact L-M window; any other window is a resurrection of 111. THIN: 53 FOMC statements in Discovery (src/study_fomc_volatility.FOMC_DATES). Single gating cell.
- Statistical (cost): one cell, n=53; detectable effect at 90% is large (roughly >= 0.3 ATR mean); power must be stated before the scope freezes; a null is read as "underpowered or absent".
- Mechanism (to be written BEFORE the scan): dealers and systematic books reduce short-vol / hedging inventory into the statement and buy back the equity leg as the event risk resolves; the pre-announcement drift is the premium paid for bearing the event. Counterparty: whoever sells equity exposure into the meeting for insurance. Falsifier: L-M-window return not credibly positive vs. the matched non-FOMC baseline window.
- Director: rank 6 on the frozen ranking; last on the shelf after Entries 12 and 13.

1. **STATE VARIABLE**: FOMC-statement day (calendar), window prior-day 14:00 -> FOMC-day 14:00 ET (half-open), return in ATR14 units; baseline = the same 24h window on all non-FOMC days.
2. **MECHANISM CLAIM**: event-risk premium harvested into the announcement (Lucca-Moench). Counterparty: insurance buyers into the meeting. Falsifier: FOMC-window mean not credibly above the non-FOMC baseline.
3. **HORIZON**: 24h, resolves per FOMC (8/yr).
4. **INTEGRITY GATE RESURRECTION RULING**: SECOND AND LAST attempt on pre-FOMC drift (hyp-000111); enters only because the window is the exact published one and differs from 111's. Attempt 2 of 2 at insertion.
5. **MAP ANCHOR**: M4.

**RESULT (September 11th, 11:18 pm CT, Scan 017)**: CLOSED FOR GOOD, near-miss.
n=52 FOMC-day-ending 14:00->14:00 windows, mean +0.1329 ATR, ci_90
[-0.0052,+0.2632] -- right direction, CI lower bound just barely crosses
zero, not credible. P1_FAIL, not retuned. This was the second and last
attempt on pre-FOMC drift (hyp-000111 = attempt 1); 2-attempt limit now
exhausted -- the family is closed for good. Mechanism doc updated
(research/mechanisms/pre-fomc-drift-exact-lm-window-m4.md). No hypothesis
id spent.

## ENTRY 15 — M9: Nasdaq-100 quarterly rebalance close-window volume/move -> next-day reaction (map-ranked #7, September 11th, 11:37 pm CT) — INDETERMINATE, RE-PARKED September 12th, 12:20 am CT (Scan 018)

Generation meeting (interactive, Jason: "do what you gotta do, don't wait
for me" -- TOP-UP owed after Entries 12/13/14 all closed and the shelf
hit 0/3, genuine QUEUE EXHAUSTED):
- LEARN: M9 was PARKED (map row) pending a free, on-disk calendar of
  Nasdaq-100 index-effective dates -- no prior test exists on this
  variable at all, so no resurrection risk. Sourced and filed this
  session: src/nasdaq_rebalance_calendar.py, the quarterly quad-witching
  Fridays (3rd Friday of March/June/September/December), the dates index
  funds must trade into the close to match the new share counts (and, in
  December, the annual composition reconstitution). Verified against
  Nasdaq's own 2025 press release (2025-12-19 Friday -> 2025-12-22 Monday
  effective) -- the mechanical rule reproduces the one real anchor
  available.
- Discovery: NQ 1-min data on disk covers the full calendar; ~34 of the
  48 filed dates fall in the Discovery slice (2015-2021).
- Integrity Gate (per-variable): NEW, map-anchored, no resurrection risk
  (never tested before). Ad hoc SPECIAL rebalances (e.g. 2023-07-24) are
  explicitly excluded from this calendar -- only the mechanical quarterly
  dates are in scope, so no cherry-picking of "helpful" extra events.
- Statistical (cost): ~34 events, one gating cell (last-10-minute
  close-window move/volume, sign-adjusted); a second, reported-only cell
  compares next-morning reaction. At n~34 the minimum detectable effect
  at 90% CI is large (roughly >=0.35-0.4 ATR/volume-ratio) -- a null
  reads as "underpowered or absent."
- Mechanism (to be written BEFORE the scan): forced, price-insensitive
  index-fund trading concentrated in the last 10 minutes of quarterly
  rebalance Fridays should show up as elevated close-window volume and/or
  an abnormal close-window move vs. a normal day, with at least partial
  reversal the following session as the forced flow's price impact fades.
  Counterparty: liquidity providers and arbitrageurs who take the other
  side of the imbalance, expecting mean-reversion once the rebalance
  flow clears.
- Director: rank 7 on the frozen map ranking (was parked; now first
  available draw since M5/M3b/M4 all closed this cycle).

1. **STATE VARIABLE**: calendar day-of-quarterly-rebalance (Nasdaq
   quad-witching Friday, src/nasdaq_rebalance_calendar.QUARTERLY_REBALANCE_FRIDAYS),
   no bucketing needed (event either occurs or not).
2. **MECHANISM CLAIM**: index funds and other passive trackers must
   execute the new share weights (and, in December, composition changes)
   at the closing print, concentrating price-insensitive volume in the
   last 10 minutes of quarterly rebalance Fridays -- this should produce
   an elevated close-window move and/or volume vs. a normal day, with at
   least partial next-day reversal as the temporary price impact fades.
   Counterparty: liquidity providers/arbitrageurs positioned to absorb
   and unwind the imbalance.
3. **HORIZON**: intraday (last 10 min of the rebalance Friday, gating),
   next full session (reported). Resolves quarterly (~4/yr).
4. **INTEGRITY GATE RESURRECTION RULING**: NEW. Never tested in this
   project before. Attempt 1 of 2 at insertion.
5. **MAP ANCHOR**: M9.


RESULT (Scan 018, run September 12th, ~12:15 am CT): INDETERMINATE, not a
null. n_rebalance_days = 0 of 27 quarterly quad-witching Fridays that fall
in the Discovery slice -- the continuous-contract NQ data file has a
systematic gap on every single one of those dates (data stops ~09:29 ET
Friday morning, resumes the following session), because the Nasdaq-100
rebalance date and the CME NQ quarterly futures roll date are the same
day, and this project's continuous-contract file appears to gap exactly
on roll-day RTH sessions. Verified directly against the raw CSV (not a
scan-code bug). No analytical shot at the claim was actually possible, so
per the 2-attempt convention this does NOT count as a spent attempt. M9
re-PARKED on the map -- see research/mechanisms/nasdaq-rebalance-close-
window-m9.md Section 6 for full detail and the two options put to Jason
(source roll-day-covering NQ data, or retire M9 permanently). Calendar
module (src/nasdaq_rebalance_calendar.py) itself is correct and kept on
file for future use if better data is sourced.

## ENTRY 16 — M12: cross-asset correlation convergence (NQ/ZN/6E/CL) -> forced risk-parity delevering -> NQ 1-3 day return (map-ranked #1, September 12th, 1:40 am CT) — CLOSED September 12th, 1:52 am CT (Scan 019)

Generation meeting (interactive, Jason lifted the cross-asset hold: "Run
cross-asset first"):
- LEARN (resurrection check, run against the full ledger by name AND by
  what is measured): cross-asset has been touched three times before, all
  closed, none with this claim. exp-063/hyp-000032 (6E same-day direction
  -> next-day NQ direction) and exp-064/hyp-000033 (same for CL) were
  naive LEAD-LAG tests -- "does market X's own return predict NQ" -- both
  Step-1 REJECTED with near-zero differences. exp-051/hyp-000021 and
  exp-052/hyp-000022 combined all four markets into one trend/reversal
  PORTFOLIO -- a monetization framing, both REJECTED. M11/Scan 012 tested
  PAIRWISE NQ-ZN correlation BREAKDOWN (divergence), attempt 1 spent,
  near-miss. This entry is none of those: it conditions on BASKET-WIDE
  correlation CONVERGENCE and names a specific forced participant. Not a
  resurrection. CLEARED.
- Discovery: all four instruments on disk with near-identical Discovery
  coverage -- NQ 2101 days, ZN 2096, 6E 2089, CL 2099, all spanning
  2015-01-01 to 2021-10-01. This is a DAILY-resolution study, roughly 680
  observations per tercile, not a calendar-event study. That is the best-
  powered scope drawn since the Discovery Engine started; the last four
  entries were all calendar-bound at n=52-79.
- Statistical (power): at ~680 per tercile the minimum detectable effect
  at 90% CI is roughly 0.06-0.08 ATR -- comfortably below the sizes this
  project has treated as economically meaningful. A null here is a real
  null, NOT "underpowered or absent." This matters: it is the first
  cross-asset scope where a clean null actually closes the question.
- Statistical (confound, raised BEFORE the scope froze and binding on it):
  correlation spikes cluster inside selloffs. If the HIGH tercile is just
  "NQ already fell hard," a negative forward return is the closed
  momentum/continuation family restated, not new structure. Required, not
  optional: report mean trailing 5-day NQ return by tercile, AND split the
  gating cell by the sign of that trailing return. If the effect lives
  only in the already-falling subset, the entry closes as a confound, not
  a finding, regardless of how credible the headline number looks.
- Mechanism (written BEFORE the scan, research/mechanisms/cross-asset-
  correlation-convergence-m12.md): portfolio variance is a mechanical
  function of the correlation matrix, so when average pairwise correlation
  across a multi-asset book rises, measured portfolio volatility rises
  even with every position unchanged -- a vol-targeting or risk-parity
  mandate then FORCES a gross-exposure cut. Equities are the largest gross
  leg in these books, so NQ absorbs the largest share of the forced sale.
  Signed (not absolute) correlation is the right measure: a strongly
  NEGATIVE correlation also diversifies and lowers portfolio variance.
- Director: rank 1. It is the only remaining map entry reachable with data
  already on disk, and the only untried axis; every other entry is closed,
  closed for good, or parked on data. Also the last free shot before the
  data-ceiling conversation becomes the real decision.

1. **STATE VARIABLE**: five-day change in the 20-day rolling average of
   the six pairwise Pearson correlations among daily log returns of NQ,
   ZN, 6E and CL. Terciles frozen on the full Discovery slice, never
   refit per sub-slice.
2. **MECHANISM CLAIM**: a sharp basket-wide correlation RISE mechanically
   raises measured portfolio volatility for vol-targeting/risk-parity
   books, forcing a gross-exposure cut at an unchanged vol target
   regardless of view; equities are the largest gross leg, so NQ takes
   the largest share of the forced selling, producing negative forward
   drift over the 1-3 days the delevering takes to execute. Counterparty:
   discretionary and liquidity-providing capital willing to absorb
   mandate-driven supply that carries no information.
3. **HORIZON**: 1, 2 and 3 trading days (gating claim at 3 days).
   Resolves daily -- fast, in line with the standing speed preference.
4. **INTEGRITY GATE RESURRECTION RULING**: NEW. Attempt 1 of 2.
5. **MAP ANCHOR**: M12.


RESULT (Scan 019, September 12th, ~1:50 am CT): CLOSED, REFUTED, and the
cleanest null the Discovery Engine has produced. n=1659, 553 per tercile.
Gating claim was credibly NEGATIVE 3-day drift in the HIGH tercile; the
measured value was credibly POSITIVE (+0.1897 ATR, ci_90 [+0.0804,
+0.3020]) -- opposite sign, not just absent. The decisive number is the
lack of any gradient: LOW +0.1988 / MID +0.1815 / HIGH +0.1897 ATR at
h=3, a spread of 0.017 ATR across the whole range of the state variable
against a detectable effect size of 0.06-0.08. The conditioning variable
does nothing. Eight of nine cells read "credibly positive" purely because
NQ drifted up over 2015-2021 and that drift shows through every bucket
equally. Attempt 1 of 2 on M12.
Two things came out of it that outlast the entry: (1) a disclosed post-hoc
subset (HIGH tercile + trailing 5-day NQ return negative -> +0.5074 ATR)
which is NOT being pursued -- post-hoc subset of a failed gating cell, and
it is the closed short-term-reversal family wearing a correlation label;
if ever revisited it enters as a NEW map entry with its own ruling, never
as attempt 2 here. (2) A methodological finding: the unconditional 3-day
drift is +0.18-0.20 ATR (cross-checked as ~15-16% annualized against the
Nasdaq-100's actual ~20% over the period, so it is the real risk premium,
not a bug), which means "90% CI above ZERO" is the wrong bar for any
long-only directional claim -- the right null is the unconditional drift.
Full detail and the H118 implication: research/mechanisms/cross-asset-
correlation-convergence-m12.md Sections 8-10.


## ENTRY 17 — M13: leveraged-ETF close rebalance -> last-30-min continuation, instrument as a factor RTY/ES/NQ (sourcing 2a, September 12th, ~9:25 am CT) — PARKED: not testable at the current data ceiling (needs RTY/ES)

Generation (sourcing stage, first entry under the new template,
research/sourcing/TEMPLATE.md; from outside-AI response A via the synthesis
doc): full mechanism doc research/mechanisms/letf-close-rebalance-m13.md.
- LEARN/Integrity: NEW, not a resurrection of hyp-000110 or M1 (direction of
  inference reversed, different participant). Confound with intraday momentum
  (entry 2b) is pre-registered and separated by instrument/AUM ordering.
- Discovery: NQ on disk; RTY and ES NOT on disk (queue item 3). One scan,
  instrument as a factor, 15 cells. Do NOT run NQ alone first.
- Statistical: daily n (~1,600 per instrument), well powered. NULL 1 applies.
- Director: rank 1 of the new slate. Holding period: 30 minutes. Track:
  directional alpha. Realization path: time-based exit at the close.

1. **STATE VARIABLE**: |9:30-15:30 return| / ATR14, terciles frozen on
   Discovery, per instrument.
2. **MECHANISM CLAIM**: LETF sponsors must rebalance (L^2-L)*AUM*r into the
   close in the day's direction; concentrated, informationless, scheduled
   flow produces late-day continuation, largest where the LETF complex is big
   relative to the future's close liquidity (RTY).
3. **HORIZON**: 15:30 -> 16:00 (gating); next session (reported).
4. **INTEGRITY GATE RESURRECTION RULING**: NEW. Attempt 1 of 2.
5. **MAP ANCHOR**: M13. STATUS: FILED, WAITING ON DATA + JASON'S GO.


## ENTRY 18 — M14: option-dealer gamma regime -> late-day continuation DIFFERENCE, NQ and ES (sourcing 2b, September 12th, ~9:32 am CT) — PARKED: not testable at the current data ceiling (needs ES)

Generation (sourcing stage, TEST cycle with Jason watching): full mechanism
doc research/mechanisms/hedging-demand-gamma-regime-m14.md.
- LEARN/Integrity: NEW; not a resurrection of the closed VXN family; shares
  the late-day channel with M13 by design and tests only the regime
  DIFFERENCE. Decay recorded (base effect 1993-2013, published 2018/2021).
- Discovery: needs ES 1-minute bars (queue item 3). 8 cells.
- Statistical: daily n; the gating statistic is a between-regime difference
  with its own CI; NULL 1 per cell; volatility-tercile control pre-registered.
- Director: rank 2 by information gain -- decides the options-data purchase
  either way. Track: risk-execution first. Realization: time-based, close.
- Information gain / edge potential: both stated in doc Section 6.

1. **STATE VARIABLE**: trailing 20-day lag-1 autocorrelation of ES 30-min
   intraday returns, terciles frozen on Discovery, lagged one day.
2. **MECHANISM CLAIM**: short-gamma dealers must hedge WITH the day's move
   into the close, amplifying it; long-gamma dealers damp it.
3. **HORIZON**: 15:30 -> 16:00 (gating); next session (reported).
4. **INTEGRITY GATE RESURRECTION RULING**: NEW. Attempt 1 of 2.
5. **MAP ANCHOR**: M14. STATUS: FILED, WAITING ON ES DATA + JASON'S GO.
