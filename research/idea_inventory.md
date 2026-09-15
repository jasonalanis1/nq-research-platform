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

## ENTRY 8 — vxn_level_vs_trailing (HIGH), next-day RTH range vs trailing-20d average (map anchor M7, range footprint; map-ranked #4) — HOLDOUT PASSED, THIRD hypothesis in project history to clear all three stages (hyp-000142/143/144/151; Scan 014 -> Statistical PASS -> Director CONTINUE -> blind Gate CONDITIONAL resolved -> Validation PASS: HIGH 1.120 [1.066,1.177] -> Holdout PASS, September 12th ~9:45 pm CT, Jason's sign-off (slot 3 of 5): HIGH 1.239 [1.170,1.313], Sidak [1.154,1.324], effect strengthened Validation->Holdout, disclosed as unusual. Portfolio review (research/studies/portfolio-hyp142-separability-2026-09-13.md): SEPARABLE, 53-66% retained residualized on the existing conditioning facts -- higher overlap than the other three, must combine by RESIDUAL not product if integrated into volatility_conditioning.py, deferred to Sept 19th product-build decision. KNOWN TRUE, conditioning fact. (fresh generation meeting, TOP-UP owed after Entry 5's Director Re-Evaluation closure, September 11th, 3:02 pm CT scheduled cycle)

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


## ENTRY 17 — M13: leveraged-ETF close rebalance -> last-30-min continuation, instrument as a factor RTY/ES/NQ (sourcing 2a, September 12th, ~9:25 am CT) — CLOSED (2026-09-13, Scan 028, P1_FAIL, hyp-000154 REJECTED)

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
5. **MAP ANCHOR**: M13. STATUS: CLOSED (2026-09-13, Scan 028, hyp-000154). Data ceiling lifted 2026-09-13: RTY_1min_databento_2026-09-13.csv and ES_1min_databento_2026-09-13.csv purchased (Jason, interactive session) and on disk. Common window (RTY-constrained, disclosed) 2017-07-09 -> 2021-10-03 used across all three instruments for comparability. P1 gate (TOP-tercile |r_day| sign-adjusted 15:30-16:00 return / ATR14, credibly positive vs each instrument's own unconditional NULL1) FAILED for RTY, ES, and NQ (diffs: RTY -0.0050 ci_90=(-0.0304,+0.0201); ES +0.0082 ci_90=(-0.0267,+0.0407); NQ +0.0060 ci_90=(-0.0221,+0.0371)). Falsifier (a) applies. Cross-instrument P2 ordering not reached (no instrument cleared the gate). VERDICT P1_FAIL. Entry closes.


## ENTRY 18 — M14: option-dealer gamma regime -> late-day continuation DIFFERENCE, NQ and ES (sourcing 2b, September 12th, ~9:32 am CT) — CLOSED (2026-09-13, Scan 029, P1_FAIL, hyp-000155 REJECTED)

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
5. **MAP ANCHOR**: M14. STATUS: CLOSED (2026-09-13, Scan 029, hyp-000155). Data ceiling lifted 2026-09-13: ES_1min_databento_2026-09-13.csv purchased and on disk, full Discovery range. P1 gate (TOP-regime minus BOTTOM-regime sign-adjusted close-window return, credibly positive) FAILED for both NQ (diff=-0.0221 ci_90=(-0.0427,+0.0007)) and ES (diff=-0.0162 ci_90=(-0.0382,+0.0104)) -- both point estimates negative, opposite the predicted sign, neither credible. Falsifier (a) applies. Entry closes.

## ENTRY 19 — M15: overnight vs intraday return split, NQ -> night leg carries the drift (sourcing 2c, September 12th, 11:00 am CT cycle) — CLOSED September 12th, ~5:00 pm CT (Scan 020, hyp-000145): clean null, night 55% of drift not 'all', attempt 1 of 2

Generation (sourcing stage, unattended cycle): full mechanism doc
research/mechanisms/overnight-vs-intraday-return-split-m15.md, written
BEFORE any scan. Source CHANNEL: literature (Lou-Polk-Skouras 2019 JFE
"A tug of war"; Cooper-Cliff-Gulen 2008 "Like night and day").
- LEARN/Integrity: NEW, signed at sourcing. Not a resurrection of the
  gap-fade family (gap sign as predictor), hyp-000139 (conditional
  divergence, reverted), or the overnight RANGE family (056/057,
  117/118). Attempt 1 of 2.
- Discovery: NQ 1-minute file on disk; 27 roll-Friday sessions lack the
  RTH block and are dropped with the count disclosed. 7 cells, 1 gating.
- Statistical: daily n (~1,650 Discovery sessions); block bootstrap
  (block 10) is the CI of record; NULL 1 is built into the gating
  statistic (night minus day legs of the same drift).
- Director: rank 1 by information gain -- sets the baseline for every
  future intraday directional claim either way. Edge potential moderate.
  Track: directional alpha. Realization: time-based (16:00 in, 09:30 out).
- Decay: whole Discovery sample is post-publication; first/second-half
  split is the pre-registered decay check (P2).
- KILL RULE: >50% of the night premium in the 09:29->09:30 open print
  terminates the family (P3).
- Information gain / edge potential: stated in doc Section 8.

1. **STATE VARIABLE**: none. Unconditional decomposition of each session
   into R_night (16:00 -> 09:30) and R_day (09:30 -> 16:00), / ATR14.
2. **MECHANISM CLAIM**: intermediaries decline to carry index inventory
   overnight; the close-to-open leg pays the premium, the open-to-close
   leg earns ~zero.
3. **HORIZON**: ~17.5 hours (gating); no multi-day cell.
4. **INTEGRITY GATE RESURRECTION RULING**: NEW. Attempt 1 of 2.
5. **MAP ANCHOR**: M15. STATUS: CLOSED (Scan 020, P1 FAIL; see mechanism doc Section 9 incl. the run-1 sample bug and the weekday-only warning).

## ENTRY 20 — M16: market intraday momentum, prior close->10:00 predicts 15:30->16:00, NQ (sourcing 2e, September 12th, 11:00 am CT cycle) — CLOSED September 12th, ~5:20 pm CT (Scan 021, hyp-000146): clean null in every cell, attempt 1 of 2

Generation (sourcing stage, unattended cycle): full mechanism doc
research/mechanisms/market-intraday-momentum-m16.md, written BEFORE any
scan. Source CHANNEL: literature (Gao-Han-Li-Zhou 2018 JFE "Market
intraday momentum").
- LEARN/Integrity: NEW, signed at sourcing. Not a resurrection of the IB
  breakout family (011/028/065/135), hyp-000045, hyp-000076, or M1.
  M13 is the pre-registered confound (P2 separates). Attempt 1 of 2.
- Discovery: NQ file on disk; roll-Friday sessions dropped, disclosed.
  10 cells, 1 gating.
- Statistical: daily n; block bootstrap CI of record; NULL 1 = middle
  tercile + unconditional last-30 mean reported beside the gate.
- Director: rank 2 by information gain (maps where in the session the
  predictable return lives; P2 tells M13/M14 whether close flow is
  information- or momentum-driven). Edge potential moderate; decay is
  the base case (sample ends 2013). Track: directional. Realization:
  time-based 15:30 -> 16:00.
- KILL RULE: >50% of the response in the 15:59->16:00 bar terminates.

1. **STATE VARIABLE**: tercile of R_first30 (prior 16:00 close -> 10:00),
   / ATR14, frozen on Discovery.
2. **MECHANISM CLAIM**: close-scheduled flow (NAV rebalancers, vol
   targeters) trades in the direction of the morning's information.
3. **HORIZON**: 15:30 -> 16:00 same session (gating).
4. **INTEGRITY GATE RESURRECTION RULING**: NEW. Attempt 1 of 2.
5. **MAP ANCHOR**: M16. STATUS: CLOSED (Scan 021, P1 FAIL; see mechanism doc Section 9).

## ENTRY 21 — M17: intraday periodicity, same half-hour slot next day (open + close slots), NQ (literature, September 12th, ~4:40 pm CT test cycle) — CLOSED September 12th, ~5:35 pm CT (Scan 022, hyp-000147): clean null in all 3 slots, attempt 1 of 2

Generation (sourcing stage, TEST cycle under the budget-use rule): full
mechanism doc research/mechanisms/intraday-periodicity-same-slot-next-day-m17.md,
written BEFORE any scan. Source CHANNEL: literature (Heston-Korajczyk-Sadka
2010 JF).
- LEARN/Integrity: NEW, signed at sourcing. Not a resurrection of M16
  (same-day), M1/hyp-000110 (close -> next open), IB family, calendar
  family. Shares a participant class with M16 (close-scheduled flow),
  disclosed. Attempt 1 of 2.
- Discovery: NQ on disk; roll-Friday sessions dropped, counted. 17 cells,
  2 gating (open slot, close slot), Sidak at 2.
- Statistical: daily n; block bootstrap CI of record; NULL 1 = each slot's
  own unconditional mean, reported beside the gate; MIDDAY slot is the
  specificity control (P2).
- Director: rank 3 (behind Entries 19, 20). Information gain moderate
  (fourth angle on "is scheduled flow fully competed in NQ"); edge
  potential low-moderate, decay is the base case. Track: directional.
  Realization: time-based 30-min hold.
- KILL RULE: >50% of the next-day slot response in its first 1-min bar.

1. **STATE VARIABLE**: sign (and tercile of |size|/ATR14) of slot k return
   on day t, k in {OPEN 09:30-10:00, CLOSE 15:30-16:00}; MIDDAY control.
2. **MECHANISM CLAIM**: schedule-constrained institutional execution
   repeats direction in the same slot on consecutive days.
3. **HORIZON**: same slot, next session (30-minute hold).
4. **INTEGRITY GATE RESURRECTION RULING**: NEW. Attempt 1 of 2.
5. **MAP ANCHOR**: M17. STATUS: CLOSED (Scan 022, P1 FAIL; see mechanism doc Section 9).

## ENTRY 22 — M18: volume-conditioned daily reversal (Campbell-Grossman-Wang), NQ (literature, September 12th, ~5:10 pm CT test cycle) — CLOSED (Scan 026, 2026-09-13 ~1:20 am CT, hyp-000152 REJECTED): P1 gating passed (HIGH-volume cell credibly negative) but P2 failed (not credibly below LOW-volume cell); NQ's own daily reversal, volume adds no gradient; not killed

Generation (sourcing stage, TEST cycle): full mechanism doc
research/mechanisms/volume-conditioned-daily-reversal-m18.md, written
BEFORE any scan. Source CHANNEL: literature.
- LEARN/Integrity: NEW with two disclosed adjacencies (hyp-000043 volume
  level alone; M1/hyp-000110 close-window flow). Integrity re-checks
  separability from M1 at Statistical if P1 passes. Attempt 1 of 2.
- Discovery: NQ on disk (volume included). 10 cells, 1 gating.
- Statistical: daily n; block bootstrap; NULL 1 = unconditional lag-1
  daily autocorrelation; the gate is the HIGH-volume cell, P2 the
  gradient; P3 separates informed from liquidity volume.
- Director: rank 3. Information gain moderate (a null closes the volume
  channel as a state variable, with 043); edge low-moderate, decay base
  case. Track: directional. Realization: time-based next session.
- KILL RULE: >50% of the response in the next session's first 1-min bar.

1. **STATE VARIABLE**: tercile of RTH volume / trailing-20d mean (lagged
   edges), frozen on Discovery; sign of today's RTH return.
2. **MECHANISM CLAIM**: liquidity-provision concessions after large
   non-informational imbalances reverse next session.
3. **HORIZON**: next RTH session (gating).
4. **INTEGRITY GATE RESURRECTION RULING**: NEW, adjacencies disclosed.
   Attempt 1 of 2.
5. **MAP ANCHOR**: M18. STATUS: CLOSED. Drawn and scanned same cycle (2026-09-13 ~1:20 am CT) once the shelf reached 3/3. Scan 026: HIGH-volume sign-adjusted next-day mean n=555 mean=-0.0942 ci_90=(-0.1523,-0.0463) -- credibly negative (P1 PASS). HIGH-minus-LOW diff mean=-0.0590 ci_90=(-0.1253,+0.0054) -- not credibly negative (P2 FAIL). Kill check: first-min share=0.036, not killed -- a real session-long effect, just not volume-graded. VERDICT: P1_PASS_P2_FAIL, closed per falsifier (b). Logged hyp-000152 (REJECTED, data_slice=discovery). Closes the volume-gradient-on-reversal channel for good, alongside hyp-000043's closure of volume level alone.

## ENTRY 23 — M19: Treasury auction concession and rebound, ZN (open scope; map channel; September 12th, ~5:05 pm CT cycle) — CLOSED (Scan 024, ~7:10 pm CT, hyp-000149 REJECTED): neither gating leg credible vs ZN's unconditional 3-session drift; n=40 events; thin-sample rule applies, not enough power to rule out a small real effect but nothing to advance

Generation (sourcing stage, scheduled cycle): full mechanism doc
research/mechanisms/treasury-auction-concession-zn-m19.md, written BEFORE
any scan. Source CHANNEL: map (forced participant: primary dealers'
bidding obligation), literature support Lou-Yan-Zhang 2013 RFS.
- LEARN/Integrity: NEW, signed at sourcing. Not a resurrection of the ZN
  lead-lag family, the cross-asset state claims, or the calendar family
  (obligated participant + pre-registered no-auction placebo). Attempt 1
  of 2.
- Discovery: ZN 1-minute on disk. Auction dates NOT on disk -- the
  sandbox cannot fetch treasurydirect.gov (robots-blocked). Needs one
  CSV: Auction Query -> Notes -> 2015-01-01 to 2021-12-31, saved as
  data/treasury_auctions_notes_2015_2021.csv. 14 cells, 2 gating.
- Statistical: EVENT-level n (~80 auctions in Discovery) -- thin-sample
  rule (failure mode #2) applies; block bootstrap; NULL 1 = ZN's own
  3-session drift.
- Director: information gain HIGH (first open-scope test: is the 0-for-11
  map record about the map or about NQ?); edge moderate-high (tens of
  ZN ticks per leg, 12x/year). Track: directional in ZN. Realization:
  time-based, 3-session legs.
- KILL RULE: post-leg concentrated in the first 1-min bar after the
  1 pm result.

1. **STATE VARIABLE**: session distance to the next / from the last
   10-year auction (t-3..t, t..t+3); bid-to-cover tercile if available.
2. **MECHANISM CLAIM**: dealer underwriting concession into the auction,
   recovered after.
3. **HORIZON**: 3 sessions per leg.
4. **INTEGRITY GATE RESURRECTION RULING**: NEW. Attempt 1 of 2.
5. **MAP ANCHOR**: M19. STATUS: FILED, WAITING ON auction dates.

## ENTRY 24 — M20: EIA weekly petroleum report pre/post-release volatility, CL (open scope; map channel; September 12th, ~5:45 pm CT cycle) — DISCOVERY PASSED, CLOSED AT MONETIZATION (no CL strategy to attach to); September 12th ~6:20 pm CT, hyp-000148

Generation (sourcing stage, scheduled cycle): full mechanism doc
research/mechanisms/eia-inventory-report-drift-cl-m20.md, written BEFORE
any scan. Source CHANNEL: map (forced participant: scheduled repricing at
a fixed release time), literature support Linn-Zhu 2004, Gu-Kurov-Wolfe
2018.
- LEARN/Integrity: NEW, signed at sourcing. Not a resurrection of CPI/NFP
  (direction-ambiguity CLOSED family -- different instrument, and this
  entry gates on MAGNITUDE not direction, explicitly built against that
  failure mode). Not on the SKIP LIST (calendar effects with no named
  participant) -- participant named. First CL event-day entry ever.
  Attempt 1 of 2.
- Discovery: CL 1-minute on disk; release-day rule (Wed, or Thu after a
  Monday holiday) computed from the existing NYSE holiday calendar --
  no new data file needed. 6 cells (9 with the optional surprise-size
  split), 1 gating.
- Statistical: hourly n (~350+ release weeks in Discovery); block
  bootstrap; NULL 1 = unconditional hourly |return|/ATR14 distribution,
  built into the gating statistic by construction.
- Director: rank 1 (only drawable entry this cycle). Information gain
  moderate-high (tests whether CPI/NFP's failure was the statistic or
  the instrument/event class); edge potential moderate, volatility-track
  if it passes (same product class as the 3 validated facts). Track:
  risk-execution. Realization: event-anchored, 1-hour window.
- KILL RULE: post-release response concentrated in the release's own
  first minute (a print artifact, not an information-flow signature).

1. **STATE VARIABLE**: none (this is an unconditional event-window
   magnitude claim); EIA release Wednesday/Thursday-after-holiday.
2. **MECHANISM CLAIM**: scheduled repricing at the 10:30 ET release
   widens realized volatility in the hour after, more than an ordinary
   RTH hour.
3. **HORIZON**: 1 hour pre, 1 hour post (gating on post).
4. **INTEGRITY GATE RESURRECTION RULING**: NEW. Attempt 1 of 2.
5. **MAP ANCHOR**: M20. STATUS: CLOSED (Scan 023 Discovery PASS; Monetization: no credible path; KNOWN TRUE / characterization on file. See mechanism doc Section 9).

## ENTRY 25 — M21: ECB rate decision pre/post-release volatility, 6E (open scope; map channel; companion to M20; September 12th, ~5:55 pm CT cycle) — CLOSED (Scan 025, September 13th ~12:20 am UTC, hyp-000150): Discovery PASS (diff +0.534 ATR, largest effect in the M20/M21 family), Statistical PASS, Director CONTINUE, Monetization NO CREDIBLE PATH (no 6E strategy exists to size); filed KNOWN TRUE alongside M20

Generation (sourcing stage, scheduled cycle): full mechanism doc
research/mechanisms/ecb-decision-day-volatility-6e-m21.md, written BEFORE
any scan. Source CHANNEL: map (forced participant: fixed public
announcement schedule), literature support Andersen-Bollerslev-Diebold-
Vega 2003, Ehrmann-Fratzscher 2005.
- LEARN/Integrity: NEW, signed at sourcing. Not a resurrection of
  CPI/NFP (different instrument/event, magnitude not direction) or
  pre/post-FOMC (US Fed, not ECB). No prior 6E-plus-event entry in the
  ledger. Explicit companion to M20 (P3 cross-check), not a duplicate.
  Attempt 1 of 2.
- Discovery: 6E 1-minute on disk; ECB press-conference dates (~8/year
  since 2015, fixed schedule) assembled as a short list in-script -- no
  new external data file needed. 6 cells, 1 gating.
- Statistical: hourly n (~50 ECB dates in Discovery); block bootstrap;
  NULL 1 = unconditional hourly |return|/ATR14 distribution.
- Director: rank 2 (behind M20). Information gain moderate (tests
  whether the scheduled-macro-event volatility design generalizes past
  one instrument); edge moderate if it passes, volatility-track. Track:
  risk-execution. Realization: event-anchored, 1-hour window.
- KILL RULE: response concentrated in the statement's own first minute
  (07:45 print), before the press-conference window the mechanism
  actually targets.

1. **STATE VARIABLE**: none (unconditional event-window magnitude
   claim); ECB press-conference dates.
2. **MECHANISM CLAIM**: scheduled repricing through the press conference
   widens realized volatility beyond an ordinary hour.
3. **HORIZON**: 1 hour, event-anchored (gating).
4. **INTEGRITY GATE RESURRECTION RULING**: NEW. Attempt 1 of 2.
5. **MAP ANCHOR**: M21. STATUS: DRAWABLE, second on the shelf.

## ENTRY 26 — M22: month-end index duration-extension flow, ZN (map-ranked, open scope) — CLOSED (Scan 027, 2026-09-13 ~3:20 am CT, hyp-000153 REJECTED): last-2-session ZN return vs unconditional 2-session drift not credibly positive (n=82, thin-sample); not killed

- Source CHANNEL: map (forced participant), literature-supported: bond
  index providers (Bloomberg US Aggregate/Treasury indices) rebalance
  composition monthly as new issuance lands; index-tracking funds and
  benchmarked accounts must extend duration to match, transacting in
  Treasury futures (cheapest/fastest instrument) concentrated in the
  last sessions of the month.
- Claim entirely inside ZN -- not a resurrection of M19 (auction
  concession: different participant, calendar anchored to specific
  auction dates, not month-end), M5 (NQ-vs-ZN relative performance,
  CLOSED clean null: cross-asset comparison, not a ZN-only claim), or
  turn-of-month (hyp-000108, CLOSED: NQ equity flow, first sessions of
  the month, not the last 2 before month-end). Genuinely distinct
  participant, distinct calendar anchor, distinct instrument-internal
  mechanism.
- Discovery: ZN 1-minute on disk (already loaded for M19); NYSE holiday
  calendar already in use project-wide. No new data needed.
- Statistical: last-2-RTH-session close-to-close return/ATR14 vs.
  unconditional 2-session drift (NULL 1, block bootstrap, block=5 per
  M19 convention); descriptive issuance-direction split (non-gating,
  low power); final-minute concentration kill check.
- Director: information gain moderate (tests whether a genuinely
  different, non-scheduled-event ZN-internal flow is visible at this
  data ceiling, complementing rather than restating the M20/M21
  scheduled-event-magnitude family); edge potential real if it passes
  since the realization path is already flat/time-boxed (no separate
  base strategy needed to monetize, unlike M20/M21's volatility-only
  facts). Track: directional, single-instrument.
- KILL RULE: response concentrated in the month's single final RTH
  minute (settlement/marking artifact, not a multi-session flow).

1. **STATE VARIABLE**: none (unconditional last-2-session window,
   calendar-anchored on month-end); descriptive issuance-direction
   split as a secondary, non-gating cell.
2. **MECHANISM CLAIM**: index-tracking bond funds forced to extend
   duration at month-end transact in ZN futures, bidding the last-2-
   session return up relative to ZN's own unconditional drift.
3. **HORIZON**: 1-2 sessions, calendar-anchored (gating).
4. **INTEGRITY GATE RESURRECTION RULING**: NEW. Attempt 1 of 2.
5. **MAP ANCHOR**: M22. STATUS: CLOSED. Drawn and scanned same cycle (2026-09-13 ~3:20 am CT). Scan 027: GATING cell n=82 mean=+0.1022 ci_90=(-0.1210,+0.2630) -- does not credibly clear zero. Not killed (final-minute share 0.096). Issuance-direction split omitted (no issuance-size data on disk beyond 10Y auction dates). VERDICT: P1_FAIL, closed per the doc's own falsifier. Logged hyp-000153 (REJECTED, data_slice=discovery). THIN-SAMPLE caveat: n=82 is a small sample, comparable to M19's n=40 -- this null does not rule out a smaller real effect, only that it is not visible at this data ceiling. Mechanism doc: research/mechanisms/month-end-duration-extension-zn-m22.md.

## ENTRY 27 — M23: London FX session-open volatility burst, 6E (map-ranked, open scope) — DRAWN & CLOSED September 13th, 11am CT cycle (Scan 030, hyp-000156, P1_PASS, Monetization deferred to new entry)

- Source CHANNEL: map (forced participant), literature-supported:
  Andersen & Bollerslev (1998, JF) and later microstructure work (Ito &
  Hashimoto 2006; Breedon & Ranaldo 2013) document the London FX session
  open as the largest intraday volatility periodicity spike in EUR/USD --
  a backlog of overnight orders, corporate/custodial flow, and
  session-triggered algorithmic strategies clearing at once against
  London's opening liquidity. NO scheduled news event involved.
- Explicitly NOT a third instance of the declined "scheduled event ->
  volatility magnitude jump" clone pattern (M20/M21): those are forced by
  a public news release; this is forced by the STRUCTURE of the trading
  day itself, the same class as M1 (NQ cash close) and M2 (NQ RTH open),
  never before tested on 6E. Not a resurrection of M21 (different clock
  time, different mechanism, no overlap) or the overnight-coil family
  (that is an NQ-only next-session RANGE persistence claim; this is a
  same-session 6E-only MAGNITUDE claim, no forecasting element).
- Discovery: 6E 1-minute on disk, full 24-hour coverage confirmed
  (00:00-23:59 local span verified directly against the loaded frame).
  No new data needed.
- Statistical: London-open hour (03:00-04:00 ET) |return|/ATR14 vs.
  unconditional hourly baseline (block bootstrap, block=10, matching
  M21's convention); pre-London hour reported unpinned as a specificity
  check; first-minute concentration kill check.
- Director: information gain HIGH -- this fires every trading day
  (~1,650 Discovery-slice observations), the best-powered open-scope
  entry sourced so far, versus M20's 329 and M21's 35 event dates. Edge
  potential real and structurally different from M20/M21: a
  daily-recurring session-open window is closer to NQ's cash-close/RTH-
  open product shape (useful for a standalone opening-range strategy at
  the London open, not only a sizing overlay on a pre-existing strategy)
  than a rare-event characterization with nothing to attach to --
  flagged explicitly so Monetization evaluates a standalone base-strategy
  path here rather than defaulting to "no credible path" the way M20/M21
  did.
- KILL RULE: response concentrated in the single first minute of the
  London session (03:00-03:01 ET, thin-liquidity print artifact rather
  than a genuine hour-long effect).

1. **STATE VARIABLE**: none (unconditional London-open-hour magnitude
   claim, fires daily); pre-London hour as a secondary, non-gating
   specificity check.
2. **MECHANISM CLAIM**: London FX dealers clearing a backlog of orders
   and algorithmic strategies at the session open drives realized
   |return|/ATR14 credibly above the unconditional hourly baseline.
3. **HORIZON**: 1 hour, session-boundary anchored, daily (gating).
4. **INTEGRITY GATE RESURRECTION RULING**: NEW. Attempt 1 of 2.
5. **MAP ANCHOR**: M23. STATUS: CLOSED (Scan 030, 2026-09-13 11am CT
   cycle, hyp-000156). GATING PASSED: London-open hour |return|/ATR14
   credibly exceeds the unconditional hourly baseline (diff +0.0400,
   ci_90=[+0.0279,+0.0550], n=891); pre-London hour does NOT (specificity
   confirmed); not a first-minute print artifact (share 0.194). A real,
   well-powered structural finding -- but Monetization found no existing
   6E base strategy to size, and per this doc's own Section 9, the
   standalone-strategy path (opening-range breakout/fade at the London
   open) is credible but requires a fresh, separately frozen hypothesis
   spec, not invented mid-cycle. Filed KNOWN TRUE; standalone-strategy
   design queued as a new sourcing candidate. Mechanism doc:
   research/mechanisms/london-open-volatility-6e-m23.md.

## ENTRY 28 — M24: month-end payment-cycle reversal, NQ (literature channel, September 13th, ~3:10 am CT cycle) — CLOSED, P1_FAIL

Generation (sourcing stage, scheduled cycle): full mechanism doc
research/mechanisms/month-end-payment-cycle-reversal-m24.md, written
BEFORE any scan. Source: Graziani (2024 EFMA working paper), "Time
Series Reversal: A Payment Cycle Friction" -- pension/cash-management
accounts forced to liquidate equity exposure to fund month-end
obligations, depressing price temporarily; the pressure reverses over
the following month.
- LEARN/Integrity: NEW. Disclosed against M6/hyp-000108 (opposite flow
  direction, unconditioned, first-3-days only -- different claim), M22
  (different instrument/mechanism/window), M5 (cross-asset relative,
  closed), hyp-000022 (unconditioned weekly basket reversal), and M18
  (volume-conditioned daily reversal, different conditioning variable
  and horizon). Attempt 1 of 2.
- Discovery: NQ daily aggregation, already on disk, no new data. 10
  cells, 1 gating. THIN-SAMPLE flagged in advance: ~82 monthly
  observations, ~27 per tercile (same disclosure discipline as M19).
- Statistical: block bootstrap (block=3, adapted for monthly
  frequency); NULL 1 = NQ's own unconditional next-month drift; P2 =
  LOW-vs-HIGH asymmetry (mechanism predicts no comparable effect on the
  HIGH side, since it is a forced-SELLING story only).
- Director: most direct monetization path of any open shelf candidate
  -- NQ already has an existing base strategy, unlike CL/6E/ZN's open
  "no base strategy" gap that stalled M20/M21/M22 at Monetization.
- KILL/CONFOUND RULE: if the next-month reversal is concentrated in its
  first 3 sessions, it is the closed turn-of-month effect (hyp-000108)
  bleeding across the month boundary, not an independent month-long
  reversal -- confounded regardless of the gating cell's own CI.

1. **STATE VARIABLE**: tercile of NQ's last-5-RTH-session (last week of
   the calendar month) close-to-close return, frozen on Discovery.
2. **MECHANISM CLAIM**: forced month-end equity liquidation for
   payroll/dividend/pension cash needs depresses price without
   information; the depression reverses over the following month.
3. **HORIZON**: 1 calendar month, time-based (gating).
4. **INTEGRITY GATE RESURRECTION RULING**: NEW, five adjacencies
   disclosed and distinguished. Attempt 1 of 2.
5. **MAP ANCHOR**: M24. STATUS: CLOSED. Mechanism doc:
   research/mechanisms/month-end-payment-cycle-reversal-m24.md.
   Scan 031 (2026-09-13, hyp-000157): P1 gate (LOW-tercile next-month
   return net of NQ's own unconditional drift) mean=+0.0112
   ci_90=(-0.0005,+0.0224) -- lower bound just barely negative, NOT
   credible. Not confounded with M6/hyp-000108 (first-3-session share
   0.452, below the 0.5 kill threshold). LOW-minus-HIGH P2 also not
   credible (diff=+0.0112 ci_90=(-0.0109,+0.0328)). Director concurred
   with closure despite the near-miss CI -- no re-test authorized
   without new information. Thin-sample family (80 months, ~27/tercile)
   -- a null here is not strong evidence the effect does not exist,
   only that it is not visible at this data ceiling. Entry closes;
   drops the shelf to Entry 29/30 (2 of 3), sourcing owed next cycle
   per SHELF RULE v2.


## ENTRY 29 — M25: monthly options-expiration week delta-hedge unwind, NQ (sourcing, September 13th, ~9:26 am CT, literature channel) — CLOSED, P1_FAIL

Generation (sourcing stage, 9:00 am CT scheduled cycle, shelf below floor
after drawing both M13 and M14 this same cycle): full mechanism doc
research/mechanisms/monthly-opex-week-delta-hedge-m25.md. Literature:
Stivers and Sun, "Returns and Option Activity over the Option-Expiration
Week for S&P 100 Stocks" (SSRN) -- large-cap stocks with actively traded
options show substantially higher average returns during the calendar
week containing the monthly third-Friday options expiration, driven by
option-dealer delta-hedge unwind as open interest runs off into
expiration (indicative +9.3%/year effect summed across 12 expiration
weeks/year, S&P 100 names).
- LEARN/Integrity: NEW. NOT the quarterly witching-day candidate declined
  this same day (7:00 am CT cycle, killed on an NQ RTH data-integrity gap
  on witching Fridays specifically) -- M25 is a whole-WEEK claim using
  ordinary daily sessions, none of which individually depend on the
  witching Friday's own intact 1-minute bars, and covers 12 events/year
  (every month) vs. quarterly witching's 4. NOT M14 (option-dealer gamma
  regime, CLOSED this cycle, hyp-000155, P1_FAIL) -- M14 tests an
  intraday-autocorrelation-derived regime conditioning the last-30-minute
  response; M25 tests a calendar-scheduled weekly return level with no
  estimated proxy. Real thematic overlap (both cite dealer delta-hedge
  unwind) but structurally independent tests, same overlap discipline as
  M13/M14.
- Statistical: ~78 expiration weeks vs. ~260 non-expiration weeks across
  Discovery -- well powered relative to M19 (n=40) and M22 (n=82).
- Director: not yet reached -- entry sourced and filed DRAWABLE, not
  drawn this cycle. Restores the shelf to the 3-entry floor (Entry 27,
  28, 29) per SHELF RULE v2 after both DRAWABLE entries (17, 18) were
  drawn and closed earlier in this same cycle.
- Budget-use note: NOT drawn this cycle by deliberate choice, not a
  data/mechanism blocker -- this cycle already ran two full multi-
  instrument scans (Scan 028, 15 cells; Scan 029, 8 cells) plus the
  data-ceiling resolution and a cost-log bug fix; drawing a third family
  in the time remaining risked a rushed cell design. First in line next
  cycle.

1. **STATE VARIABLE**: calendar partition (expiration week vs.
   non-expiration week), not an estimated proxy -- no lookahead risk.
2. **MECHANISM CLAIM**: option-dealer delta-hedge unwind as open interest
   runs off into the monthly third-Friday expiration creates mechanical
   buy-pressure drift across the containing week.
3. **HORIZON**: 1 calendar week (gating).
4. **INTEGRITY GATE RESURRECTION RULING**: NEW. Attempt 1 of 2.
5. **MAP ANCHOR**: M25. STATUS: CLOSED. Mechanism doc:
   research/mechanisms/monthly-opex-week-delta-hedge-m25.md.
   Scan 032 (2026-09-13, hyp-000158): P1 gate (expiration-week return,
   ATR14-normalized, net of NQ's own unconditional weekly drift)
   mean=+0.1872 ci_90=(-0.0291,+0.3950), n=80 -- not credible (lower
   bound negative). P2 (expiration minus non-expiration) also not
   credible: diff=+0.2429 ci_90=(-0.1167,+0.5907). Individual day-of-week
   cumulative cells (Tue/Wed/Thu/Fri) were credibly positive but this is
   descriptive, non-gating, and does not override the failed gate.
   Director concurred with closure -- a clean non-credible result, not a
   near-miss. Dealer-hedge-unwind premium documented for S&P 100 stocks
   not visible in NQ futures at this data ceiling. Entry closes; drops
   the shelf to Entry 30/31 (2 of 3), sourcing owed next cycle per SHELF
   RULE v2.

## ENTRY 30 — M26: Level Sweep Reversal (close_min_distance), conditioned on prior-day range contraction (resurrection, practitioner/map channel) — SOURCED September 13th, ~11:15 am CT; CLOSED September 13th, ~5:00 pm CT (Scan 033, hyp-000159, P1_FAIL, clean powered null, first sanctioned conditional retest)

- Source CHANNEL: practitioner/map (resurrection of a previously-closed
  directional idea, now conditioned differently). Origin: today's
  interactive conversation with Jason, who asked directly whether a
  pattern that failed unconditionally could still be real under a
  specific market condition -- the first concrete test of that question.
- Explicitly NOT a re-run of the unconditional Level Sweep Reversal
  family (exp-003 through exp-024, all six variants closed, most
  recently exp-023 close_min_distance -0.038R CI spans zero on the
  proper Discovery slice) -- this tests ONE specific, pre-chosen
  conditional claim, not another slice of the same dead unconditional
  pattern. Not the FVG entry trigger (killed decisively, exp-025). Not
  the undefined trend-structure-liquidity-filter idea. Not the
  event-conditioned-reference-level-fade thread (different setup,
  conditions on scheduled-event proximity not volatility state).
- Discovery: NQ 1-minute on disk, full Discovery range, no new data.
  Conditioning variable (`prior_day_narrow`, bottom-tercile prior-day
  range) already exists and was validated (HOLDOUT PASSED, hyp-046/048)
  for an unrelated purpose BEFORE this hypothesis existed -- chosen once,
  not searched over.
- Statistical: block bootstrap CI on per-trade R, compressed-day vs.
  non-compressed-day cells plus their difference (the actual test), plus
  a thin-sample disclosure check (Level Sweep Reversal fires
  infrequently, 150-220 trades historically).
- Director: information gain HIGH if real (first directional, not
  merely conditioning, signal to survive Discovery in months; validates
  the state-conditioning-on-old-ideas methodology Jason asked to
  prioritize ahead of September 19th) and real if null (answers a
  specific untested question plainly, closes one more Level Sweep
  Reversal branch for good). Edge potential: directly tradeable if real
  -- the setup already has a full entry/exit spec, unlike M23 this same
  cycle which would need a new strategy design.
- KILL RULE: none (an expectancy claim, not a magnitude/print-artifact
  claim) -- thin-sample disclosure substitutes for a kill rule here (if
  the compressed-day cell has fewer than ~40 trades, disclose as
  underpowered rather than claim a null).

1. **STATE VARIABLE**: `prior_day_narrow` (bottom tercile of trailing
   prior-day range, existing frozen definition from
   `src/volatility_conditioning.py`).
2. **MECHANISM CLAIM**: a level sweep during an already-compressed
   volatility regime is more likely a genuine liquidity grab ahead of
   continued range-bound trading; the same sweep during an
   already-expansive regime is more likely the start of a breakout,
   where reversal is the wrong bet -- explaining why the unconditional
   average came back flat.
3. **HORIZON**: intraday (same-day entry/exit per the existing Level
   Sweep Reversal spec), state known before the trading day begins.
4. **INTEGRITY GATE RESURRECTION RULING**: NEW conditional claim on an
   old, closed unconditional pattern. Attempt 1 of 2 (tracked per-
   conditioning-variable).
5. **MAP ANCHOR**: M26. STATUS: CLOSED (Scan 033, P1_FAIL: compressed-day net R +0.030, ci_90 (-0.109,+0.186), n=131; P2 diff +0.095 not credible; see mechanism doc Section 11). Mechanism doc:
   research/mechanisms/level-sweep-reversal-range-contraction-m26.md.
   Restores the 3-entry shelf floor (Entry 28, 29, 30).

## ENTRY 31 — M27: Tokyo FX session open, 6E (map/practitioner channel, September 13th, ~2:00 pm CT cycle) — CLOSED September 13th, 7:15 pm CT (Scan 034, hyp-000160, P1_FAIL: Tokyo hour credibly QUIETER than baseline, the opposite of London)

Generation (sourcing stage, scheduled cycle): sourced to restore the
3-entry shelf floor after M24/Entry 28 closed this cycle (P1_FAIL,
hyp-000157). Full mechanism doc
research/mechanisms/tokyo-fx-open-6e-m27.md, written BEFORE any scan.
Companion entry to M23 (London-open volatility, 6E, P1_PASS this same
day, hyp-000156): same open-scope, structural-session-boundary
methodology family, applied to the Tokyo FX session open
(19:00-20:00 ET) instead -- a distinct, non-overlapping window with its
own participant story (Japanese exporter/importer hedging flow, Asian
real-money accounts, Tokyo-based bank desks, not European dealers).
- LEARN/Integrity: NEW. Disclosed against M23 (non-overlapping window,
  different participants -- not a re-run), M20/M21 (both scheduled news
  events; this entry has none, purely session-structure), and M15
  (unconditional session-split decomposition, different claim shape,
  already closed). Attempt 1 of 2.
- Discovery: 6E 1-minute OHLCV, already on disk (confirmed this same
  cycle via Scan 030/M23), no new data. 4 cells, 1 gating, mirroring
  M23's own Scan 030 exactly.
- Statistical: block bootstrap (block=10, matches the M20/M21/M23
  hourly-frequency convention); NULL 1 = 6E's own unconditional hourly
  |return|/ATR14 baseline.
- Director: same open question M23 left unresolved -- 6E has zero
  existing base strategies, so a pass here again defers Monetization to
  a fresh sourced entry rather than a same-cycle strategy design.

1. **STATE VARIABLE**: Tokyo-open hour (19:00-20:00 ET) vs. pre-Tokyo
   hour (18:00-19:00 ET), 6E.
2. **MECHANISM CLAIM**: Tokyo-session-open order-backlog clearing against
   thin US-afternoon/Asian-session-seam liquidity elevates |return| in
   the opening hour, with no scheduled news event involved.
3. **HORIZON**: 1 hour (session-boundary anchored, fires daily).
4. **INTEGRITY GATE RESURRECTION RULING**: NEW, three adjacencies
   disclosed and distinguished (M23, M20/M21, M15). Attempt 1 of 2.
5. **MAP ANCHOR**: M27. STATUS: CLOSED (Scan 034 P1_FAIL, diff -0.0968 ci_90 (-0.1056,-0.0861) n=644; see mechanism doc Section 11). Mechanism doc:
   research/mechanisms/tokyo-fx-open-6e-m27.md. Restores the 3-entry
   shelf floor (Entry 29, 30, 31).

## ENTRY 32 — M28: Pre-holiday effect, NQ (literature channel, September 13th, ~3:15 pm CT cycle) — CLOSED (Directional Lane trial 1, Scan 037, September 15th ~11:00 pm CT, hyp-000163): Discovery P1 FAIL, CLEAN NULL (diff -2.41 pts, block CI (-15.62,+4.42), n=60). Write-up: research/studies/hyp-000163-directional-lane-trial1-2026-09-15.md

Generation (sourcing stage, scheduled cycle): sourced to restore the
3-entry shelf floor after M25/Entry 29 closed this cycle (P1_FAIL,
hyp-000158). Full mechanism doc
research/mechanisms/pre-holiday-effect-nq-m28.md, written BEFORE any
scan. Literature: Lakonishok and Smidt (1988, Review of Financial
Studies), Ariel (1990, Journal of Financial Economics) -- the trading
session immediately before an exchange holiday has historically shown
average returns many times larger than an ordinary session's average,
across multiple decades and markets. Never tested against NQ
specifically in this project.
- LEARN/Integrity: NEW. Disclosed against M6/hyp-000108 (turn-of-month,
  different calendar anchor), M24 (month-end payment-cycle reversal,
  closed, different anchor and mechanism), M25 (options-expiration
  week, closed, different anchor), and M22 (ZN month-end duration
  extension, closed, different instrument/anchor). Attempt 1 of 2.
- Discovery: NQ daily RTH aggregation, already on disk, no new data.
  4 cells, 1 gating. Thin-annual-event-count family (roughly 9
  NYSE full-closure holidays/year, ~55-65 usable pre-holiday sessions
  expected across Discovery).
- Mechanism honesty flag: weaker named-participant story than this
  project's other open-scope entries (M19-M27 all name a specific
  forced participant) -- included anyway given the unusual replication
  strength of the underlying empirical regularity across markets and
  decades.
- Director: not yet reached -- entry sourced and filed DRAWABLE, not
  drawn this cycle.

1. **STATE VARIABLE**: session immediately before vs. after an NYSE
   exchange holiday, NQ.
2. **MECHANISM CLAIM**: reduced short-selling/hedging activity and
   thinner volume ahead of a closure produce a small positive drift in
   the pre-holiday session.
3. **HORIZON**: 1 session (calendar-anchored, exchange-holiday
   boundary).
4. **INTEGRITY GATE RESURRECTION RULING**: NEW, four adjacencies
   disclosed and distinguished. Attempt 1 of 2.
5. **MAP ANCHOR**: M28. STATUS: DRAWABLE. Mechanism doc:
   research/mechanisms/pre-holiday-effect-nq-m28.md. Restores the
   3-entry shelf floor (Entry 30, 31, 32).


## ENTRY 33 — M29: Implied-minus-realized volatility gap (VXN vs NQ realized range), NQ (observatory channel, September 13th, ~5:05 pm CT interactive test cycle) — SOURCED, DRAWABLE (Stage 0 free-look first) — PARKED September 15th (magnitude freeze, refocus-2026-09-15.md s.3; sourced and still valid, not drawable until the directional question is answered)

Generation (sourcing stage, UPGRADE QUEUE v3 item U4): sourced to restore the
3-entry shelf floor after M26/Entry 30 closed this cycle (P1_FAIL, hyp-000159),
and because outside review D named it as the one state variable on disk that has
never been used -- the closest available proxy for options-dealer hedging. Full
mechanism doc research/mechanisms/implied-realized-vol-gap-nq-m29.md, written
BEFORE any look at the data. Filed as a LAYER-0 STATE PRIMITIVE, not a directional
claim.
1. **CLAIM**: gap = VXN(t-1) minus trailing-20-session realized vol of NQ; HIGH-gap
   days (implied >> realized, dealers dampening) show credibly LOWER next-session
   RTH range ratio than LOW-gap days (P1); effect survives residualizing on the
   VXN-level tercile (P2, separability from hyp-000142/144/151).
2. **MECHANISM**: dealers net short options hedge against the move (dampening);
   net long, hedge with the move (amplifying). Named participant; observable only
   through this price proxy.
3. **FROZEN SCOPE**: Stage 0 = descriptive free-look table (U11, no ID, no scan);
   Stage 1 = ONE 4-cell scan only if the free-look shows a footprint (block=10).
4. **RESURRECTION RULING**: NEW. Not hyp-000142 (different denominator), not M12,
   not the tabled VIX-term-structure idea. Duplicate-closure rule: if the gap
   tercile overlaps the VXN-level tercile >80% of days, close as duplicate.
5. **MAP ANCHOR**: M29. STATUS: DRAWABLE for Stage 0 as soon as U11 (Observatory
   free-look mode) exists. Restores the shelf to 3/3 (Entry 31, 32, 33).

## ENTRY 34 — M30: Opening-range width → midday range and excursion, NQ (observatory channel / Idea Factory queue, September 13th, ~7:15 pm CT test cycle) — DRAWN 2026-09-14, Scan 036, hyp-000162: ALL THREE PREDICTIONS PASSED, one INTEGRITY RED owed to the Gate

Generation (SOURCING RULE v3): taken from the top of research/observatory/idea-factory-2026-09-13.md
(`opening_range_vs_atr → range/mfe/mae`, strongest family, z ≈ 11 HIGH/midday). LEARN consulted: the
state has never been a registered conditioning variable; the initial-balance breakout family tested
DIRECTION after the first 30 minutes and is closed -- this is a SIZE claim and does not reopen it.
Mechanism doc research/mechanisms/opening-range-width-midday-excursion-nq-m30.md written BEFORE any
registered test.
0. **STATE VARIABLE**: `opening_range_vs_atr` (frozen in market_state_primitives; known 10:00 ET).
1. **CLAIM**: HIGH-tercile 30-minute opening range (09:30-10:00 ET) → credibly larger midday range and
   midday MFE/MAE than LOW-tercile; known 10:00, outcome from 11:30 (timing rule satisfied).
2. **MECHANISM**: market-maker inventory imbalance from an unbalanced open keeps repricing through midday.
3. **FROZEN SCOPE**: ONE 6-cell scan, block=10 (Section 9).
4. **RESURRECTION RULING**: NEW. Not exp-028/031 (direction), not F-048 (prior-DAY range; P3 tests it).
5. **MAP ANCHOR**: M30. STATUS: **DRAWN 2026-09-14** (7:00 am CT catch-up cycle) over the older Entry 32
   under SHELF RULE v2's ranking rule (information gain x edge potential), because Stack A established
   B2 needs SIZING material and this is the only drawable entry that produces it.
   Scan 036 -> **hyp-000162, PROMISING**: P1 gating diff +0.5193 ci_90 (+0.4475,+0.5975) n=555/556 PASS;
   P2 MFE +0.0886 and MAE +0.1108 ATR, both credibly positive; P3 83.6% retained after residualizing on
   the prior-day range tercile (bar 50%) PASS. Statistical (+POWER) owed, then the BLIND Integrity Gate.
   **BLOCKING FINDING for that Gate:** U6's mechanical suite is RED on the PLACEBO check -- the shifted
   (t+1) signal reaches 74% of the real effect, so yesterday's opening range predicts today's midday
   range nearly as well as today's does. P3 does NOT cover this (it residualized on prior-day RANGE, a
   different variable from prior-day OPENING range). Overlap 48.56%, just under the 50% guard, so the
   verdict is near a boundary and is disclosed as such. Attempt 1 of 2 for the family.

## ENTRY 35 — M31: Prior-day volume vs expected → first-30-minute range, NQ (observatory channel / Idea Factory queue, September 13th, ~7:17 pm CT test cycle) — SOURCED, DRAWABLE — PARKED September 15th (magnitude freeze, refocus-2026-09-15.md s.3; sourced and still valid, not drawable until the directional question is answered)

Generation (SOURCING RULE v3): second family from the queue (`volume_vs_expected → range`, HIGH/first30
z ≈ 8.4, n=385). LEARN consulted: volume was tested for DIRECTION (hyp-000043 REJECTED; M18 CLOSED
P1_PASS_P2_FAIL; Scan 002 cells) -- never for next-morning RANGE. Mechanism doc
research/mechanisms/prior-day-volume-first30-range-nq-m31.md written BEFORE any registered test.
1. **CLAIM**: HIGH-tercile prior-day volume/expected → credibly larger first-30 range next session.
2. **MECHANISM**: institutional execution desks finishing worked orders at the open.
3. **FROZEN SCOPE**: ONE 6-cell scan, block=10; volume-coverage disclosure (falsifier c).
4. **RESURRECTION RULING**: NEW as a range claim. Attempt 1 of 2.
5. **MAP ANCHOR**: M31. STATUS: DRAWABLE. First non-volatility input candidate for the Risk/State Engine.

## ENTRY 36 — M32: Open's location in the prior day's range → later-session range, NQ (observatory channel / Idea Factory queue, September 14th, ~9:25 am CT cycle) — SOURCED, DRAWABLE — PARKED September 15th (magnitude freeze, refocus-2026-09-15.md s.3; sourced and still valid, not drawable until the directional question is answered)

Generation (SOURCING RULE v3, source channel: OBSERVATORY): taken from
research/observatory/idea-factory-2026-09-13.md (`location_in_range → range`, 9 cells,
strongest |z| 6.8 at LOW/last_hour). The footprint is MONOTONE -- LOW above all-days in
every window, HIGH below in every window -- which is why the direction is pre-registered
rather than fitted. LEARN consulted: `location_in_range` has never been the conditioning
variable of a registered scan. Restores the shelf to 4/3.
0. **STATE VARIABLE**: `location_in_range` (frozen in market_state_primitives; known 09:30 ET).
1. **CLAIM**: sessions opening in the LOW tercile of the prior day's range show a credibly
   LARGER last-hour (15:00-16:00 ET) range ratio than HIGH-tercile opens. Known 09:30,
   outcome from 15:00 (timing rule satisfied by 5.5 hours).
2. **MECHANISM**: volatility asymmetry / leverage effect -- dealers short downside convexity
   hedging more actively as spot falls, plus vol-control and risk-parity funds cutting
   mandated exposure as realized vol rises, both concentrating into the close. That is why
   the gating window is the LAST HOUR and not the morning.
3. **FROZEN SCOPE**: ONE scan, 5 cell-groups, block=10, SEED=20260914 (Section 9), then
   integrity_checks.py BEFORE the Gate.
4. **RESURRECTION RULING**: NEW. Not F-048 (prior-day range SIZE), not M30/hyp-000162
   (opening-range WIDTH, known at 10:00), not the closed initial-balance direction family.
5. **MAP ANCHOR**: M32. STATUS: DRAWABLE. Known at 09:30 -- half an hour EARLIER than M30's
   state, and the earliest intraday sizing input the Risk/State Engine could act on.
   TWO GATING CONTROLS, both pre-registered: P3 residualizes on the overnight gap (if the
   whole effect is the gap, this is a duplicate of a known effect), and **P4 requires the
   shifted-signal placebo to FAIL to reproduce it** -- added directly from what hyp-000162
   cost this project on 2026-09-14, where a candidate passed every registered prediction and
   then tripped exactly that check. Pre-registering it means the answer is known before the
   Gate, not after.

## ENTRY 37 — batch_screen.py cheap-gate survivor: `opening_range_vs_atr` HIGH / midday -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=558, mean=+0.4774 vs all-days +0.3738, z=+10.97. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect +0.1036, Sidak-adjusted 90%-family interval [+0.0787, +0.1349]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `opening_range_vs_atr` (already implemented in market_state_primitives*.py; known at 10:00 ET).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 11:30-13:30 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `opening_range_vs_atr`.
5. **MAP ANCHOR**: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.1036 | Sidak(K=25) [+0.0787, +0.1349] | 90% unadj. [+0.0892, +0.1203]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.103582; legs={'shifted_t+1': 0.073956, 'inverted': -0.051838}; shifted_t+1 reaches 0.0740 vs the real 0.1036 (red at 50%) |
| 4. joint separability (T1) | OK | +0.0517 | 90% [+0.0378, +0.0680] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 38 — batch_screen.py cheap-gate survivor: `opening_range_vs_atr` LOW / midday -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=557, mean=+0.2779 vs all-days +0.3738, z=-10.15. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect -0.0959, Sidak-adjusted 90%-family interval [-0.1176, -0.0741]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `opening_range_vs_atr` (already implemented in market_state_primitives*.py; known at 10:00 ET).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 11:30-13:30 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `opening_range_vs_atr`.
5. **MAP ANCHOR**: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.0959 | Sidak(K=25) [-0.1176, -0.0741] | 90% unadj. [-0.1089, -0.0826]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | GREEN | -- | -- | real=-0.095938; legs={'shifted_t+1': -0.053883, 'inverted': 0.047883}; no gating placebo comes close to the real effect [shifted_t+1 reported but NOT gating: it re-selects 51% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0472 | 90% [-0.0600, -0.0350] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 39 — batch_screen.py cheap-gate survivor: `opening_range_vs_atr` HIGH / next_rth -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=550, mean=+1.0277 vs all-days +0.8453, z=+8.79. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect +0.1823, Sidak-adjusted 90%-family interval [+0.1217, +0.2512]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `opening_range_vs_atr` (already implemented in market_state_primitives*.py; known at 10:00 ET).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 09:30-16:00 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `opening_range_vs_atr`.
5. **MAP ANCHOR**: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.1823 | Sidak(K=25) [+0.1217, +0.2512] | 90% unadj. [+0.1464, +0.2232]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.182319; legs={'shifted_t+1': 0.138933, 'inverted': -0.091743}; shifted_t+1 reaches 0.1389 vs the real 0.1823 (red at 50%) |
| 4. joint separability (T1) | OK | +0.0874 | 90% [+0.0538, +0.1218] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 40 — batch_screen.py cheap-gate survivor: `opening_range_vs_atr` HIGH / last_hour -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=554, mean=+0.3645 vs all-days +0.2986, z=+8.77. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect +0.0660, Sidak-adjusted 90%-family interval [+0.0449, +0.0907]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `opening_range_vs_atr` (already implemented in market_state_primitives*.py; known at 10:00 ET).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 15:00-16:00 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `opening_range_vs_atr`.
5. **MAP ANCHOR**: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0660 | Sidak(K=25) [+0.0449, +0.0907] | 90% unadj. [+0.0523, +0.0796]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.065953; legs={'shifted_t+1': 0.056571, 'inverted': -0.034308}; shifted_t+1 reaches 0.0566 vs the real 0.0660 (red at 50%) |
| 4. joint separability (T1) | OK | +0.0183 | 90% [+0.0089, +0.0275] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 41 — batch_screen.py cheap-gate survivor: `vxn_minus_realized` LOW / first30 -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=555, mean=+0.3046 vs all-days +0.3737, z=-8.71. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect -0.0694, Sidak-adjusted 90%-family interval [-0.0941, -0.0451]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `vxn_minus_realized` (already implemented in market_state_primitives*.py; known at the previous evening's close).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 09:30-10:00 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `vxn_minus_realized`.
5. **MAP ANCHOR**: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.0694 | Sidak(K=25) [-0.0941, -0.0451] | 90% unadj. [-0.0838, -0.0544]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | GREEN | -- | -- | real=-0.069372; legs={'shifted_t+1': -0.05995, 'inverted': 0.034655}; no gating placebo comes close to the real effect [shifted_t+1 reported but NOT gating: it re-selects 87% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0280 | 90% [-0.0415, -0.0161] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 42 — batch_screen.py cheap-gate survivor: `volume_vs_expected` HIGH / first30 -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=385, mean=+0.4537 vs all-days +0.3737, z=+8.41. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect +0.0762, Sidak-adjusted 90%-family interval [+0.0503, +0.1046]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `volume_vs_expected` (already implemented in market_state_primitives*.py; known at the previous evening's close).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 09:30-10:00 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `volume_vs_expected`.
5. **MAP ANCHOR**: M31 (prior-day volume vs expected -> first-30-minute range, NQ; market_structure_map.md row M31)

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0762 | Sidak(K=25) [+0.0503, +0.1046] | 90% unadj. [+0.0613, +0.0924]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.076191; legs={'shifted_t+1': 0.048384, 'inverted': -0.039374}; inverted reaches -0.0394 vs the real 0.0762 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 60% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0168 | 90% [+0.0030, +0.0316] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 43 — batch_screen.py cheap-gate survivor: `vxn_minus_realized` LOW / morning -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=555, mean=+0.3672 vs all-days +0.4512, z=-8.37. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect -0.0845, Sidak-adjusted 90%-family interval [-0.1158, -0.0570]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `vxn_minus_realized` (already implemented in market_state_primitives*.py; known at the previous evening's close).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 10:00-11:30 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `vxn_minus_realized`.
5. **MAP ANCHOR**: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.0845 | Sidak(K=25) [-0.1158, -0.0570] | 90% unadj. [-0.1015, -0.0685]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | GREEN | -- | -- | real=-0.0845; legs={'shifted_t+1': -0.075895, 'inverted': 0.042212}; no gating placebo comes close to the real effect [shifted_t+1 reported but NOT gating: it re-selects 87% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0396 | 90% [-0.0549, -0.0264] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 44 — batch_screen.py cheap-gate survivor: `opening_range_vs_atr` HIGH / afternoon -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=554, mean=+0.3981 vs all-days +0.3220, z=+8.20. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect +0.0761, Sidak-adjusted 90%-family interval [+0.0524, +0.1042]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `opening_range_vs_atr` (already implemented in market_state_primitives*.py; known at 10:00 ET).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 13:30-15:00 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `opening_range_vs_atr`.
5. **MAP ANCHOR**: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0761 | Sidak(K=25) [+0.0524, +0.1042] | 90% unadj. [+0.0622, +0.0912]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.076116; legs={'shifted_t+1': 0.048994, 'inverted': -0.039595}; shifted_t+1 reaches 0.0490 vs the real 0.0761 (red at 50%) |
| 4. joint separability (T1) | OK | +0.0320 | 90% [+0.0189, +0.0455] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 45 — batch_screen.py cheap-gate survivor: `volume_vs_expected` HIGH / morning -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=385, mean=+0.5487 vs all-days +0.4512, z=+8.10. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect +0.0916, Sidak-adjusted 90%-family interval [+0.0572, +0.1308]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `volume_vs_expected` (already implemented in market_state_primitives*.py; known at the previous evening's close).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 10:00-11:30 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `volume_vs_expected`.
5. **MAP ANCHOR**: M31 (prior-day volume vs expected -> first-30-minute range, NQ; market_structure_map.md row M31)

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0916 | Sidak(K=25) [+0.0572, +0.1308] | 90% unadj. [+0.0713, +0.1117]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.091569; legs={'shifted_t+1': 0.057326, 'inverted': -0.047321}; inverted reaches -0.0473 vs the real 0.0916 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 60% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0192 | 90% [+0.0017, +0.0388] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 46 — batch_screen.py cheap-gate survivor: `vxn_minus_realized` LOW / rth -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=555, mean=+0.6804 vs all-days +0.8382, z=-8.05. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect -0.1585, Sidak-adjusted 90%-family interval [-0.2242, -0.1030]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `vxn_minus_realized` (already implemented in market_state_primitives*.py; known at the previous evening's close).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 09:30-16:00 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `vxn_minus_realized`.
5. **MAP ANCHOR**: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.1585 | Sidak(K=25) [-0.2242, -0.1030] | 90% unadj. [-0.1930, -0.1221]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | GREEN | -- | -- | real=-0.158547; legs={'shifted_t+1': -0.137494, 'inverted': 0.079202}; no gating placebo comes close to the real effect [shifted_t+1 reported but NOT gating: it re-selects 87% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0626 | 90% [-0.0917, -0.0337] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 47 — batch_screen.py cheap-gate survivor: `opening_range_vs_atr` LOW / next_rth -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=547, mean=+0.6816 vs all-days +0.8453, z=-7.87. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect -0.1638, Sidak-adjusted 90%-family interval [-0.2096, -0.1134]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `opening_range_vs_atr` (already implemented in market_state_primitives*.py; known at 10:00 ET).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 09:30-16:00 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `opening_range_vs_atr`.
5. **MAP ANCHOR**: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.1638 | Sidak(K=25) [-0.2096, -0.1134] | 90% unadj. [-0.1908, -0.1328]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | GREEN | -- | -- | real=-0.163787; legs={'shifted_t+1': -0.140557, 'inverted': 0.081744}; no gating placebo comes close to the real effect [shifted_t+1 reported but NOT gating: it re-selects 51% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0887 | 90% [-0.1155, -0.0597] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 48 — batch_screen.py cheap-gate survivor: `volume_vs_expected` HIGH / midday -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=385, mean=+0.4626 vs all-days +0.3738, z=+7.81. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect +0.0859, Sidak-adjusted 90%-family interval [+0.0536, +0.1230]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `volume_vs_expected` (already implemented in market_state_primitives*.py; known at the previous evening's close).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 11:30-13:30 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `volume_vs_expected`.
5. **MAP ANCHOR**: M31 (prior-day volume vs expected -> first-30-minute range, NQ; market_structure_map.md row M31)

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0859 | Sidak(K=25) [+0.0536, +0.1230] | 90% unadj. [+0.0665, +0.1055]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.085902; legs={'shifted_t+1': 0.066789, 'inverted': -0.044392}; inverted reaches -0.0444 vs the real 0.0859 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 60% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0248 | 90% [+0.0065, +0.0443] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 49 — batch_screen.py cheap-gate survivor: `vxn_minus_realized` LOW / next_rth -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=552, mean=+0.6897 vs all-days +0.8453, z=-7.51. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect -0.1569, Sidak-adjusted 90%-family interval [-0.2198, -0.0918]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `vxn_minus_realized` (already implemented in market_state_primitives*.py; known at the previous evening's close).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 09:30-16:00 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `vxn_minus_realized`.
5. **MAP ANCHOR**: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.1569 | Sidak(K=25) [-0.2198, -0.0918] | 90% unadj. [-0.1930, -0.1176]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | GREEN | -- | -- | real=-0.156934; legs={'shifted_t+1': -0.140072, 'inverted': 0.077832}; no gating placebo comes close to the real effect [shifted_t+1 reported but NOT gating: it re-selects 87% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0906 | 90% [-0.1257, -0.0581] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 50 — batch_screen.py cheap-gate survivor: `vxn_minus_realized` HIGH / morning -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=559, mean=+0.5256 vs all-days +0.4512, z=+7.44. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect +0.0738, Sidak-adjusted 90%-family interval [+0.0422, +0.1138]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `vxn_minus_realized` (already implemented in market_state_primitives*.py; known at the previous evening's close).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 10:00-11:30 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `vxn_minus_realized`.
5. **MAP ANCHOR**: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0738 | Sidak(K=25) [+0.0422, +0.1138] | 90% unadj. [+0.0545, +0.0941]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.073807; legs={'shifted_t+1': 0.067916, 'inverted': -0.03727}; inverted reaches -0.0373 vs the real 0.0738 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 88% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0270 | 90% [+0.0111, +0.0442] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 51 — batch_screen.py cheap-gate survivor: `vxn_minus_realized` HIGH / rth -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=559, mean=+0.9831 vs all-days +0.8382, z=+7.42. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect +0.1441, Sidak-adjusted 90%-family interval [+0.0766, +0.2177]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `vxn_minus_realized` (already implemented in market_state_primitives*.py; known at the previous evening's close).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 09:30-16:00 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `vxn_minus_realized`.
5. **MAP ANCHOR**: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.1441 | Sidak(K=25) [+0.0766, +0.2177] | 90% unadj. [+0.1066, +0.1854]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.144124; legs={'shifted_t+1': 0.129742, 'inverted': -0.072778}; inverted reaches -0.0728 vs the real 0.1441 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 88% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0349 | 90% [+0.0060, +0.0661] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 52 — batch_screen.py cheap-gate survivor: `vxn_minus_realized` HIGH / first30 -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=559, mean=+0.4320 vs all-days +0.3737, z=+7.39. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect +0.0580, Sidak-adjusted 90%-family interval [+0.0318, +0.0879]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `vxn_minus_realized` (already implemented in market_state_primitives*.py; known at the previous evening's close).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 09:30-10:00 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `vxn_minus_realized`.
5. **MAP ANCHOR**: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0580 | Sidak(K=25) [+0.0318, +0.0879] | 90% unadj. [+0.0422, +0.0752]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.058049; legs={'shifted_t+1': 0.047176, 'inverted': -0.029313}; inverted reaches -0.0293 vs the real 0.0580 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 88% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0171 | 90% [+0.0048, +0.0301] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 53 — batch_screen.py cheap-gate survivor: `volume_vs_expected` HIGH / overnight -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=386, mean=+0.7224 vs all-days +0.5962, z=+7.37. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect +0.1289, Sidak-adjusted 90%-family interval [+0.0805, +0.1803]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `volume_vs_expected` (already implemented in market_state_primitives*.py; known at the previous evening's close).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: prior 18:00 -> 09:30 ET (overnight) (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `volume_vs_expected`.
5. **MAP ANCHOR**: M31 (prior-day volume vs expected -> first-30-minute range, NQ; market_structure_map.md row M31)

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.1289 | Sidak(K=25) [+0.0805, +0.1803] | 90% unadj. [+0.0999, +0.1552]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.128894; legs={'shifted_t+1': 0.085569, 'inverted': -0.06453}; inverted reaches -0.0645 vs the real 0.1289 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 60% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0002 | 90% [-0.0099, +0.0087] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=False |

---

## ENTRY 54 — batch_screen.py cheap-gate survivor: `vxn_minus_realized` HIGH / next_rth -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=558, mean=+0.9957 vs all-days +0.8453, z=+7.30. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect +0.1490, Sidak-adjusted 90%-family interval [+0.0824, +0.2252]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `vxn_minus_realized` (already implemented in market_state_primitives*.py; known at the previous evening's close).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 09:30-16:00 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `vxn_minus_realized`.
5. **MAP ANCHOR**: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.1490 | Sidak(K=25) [+0.0824, +0.2252] | 90% unadj. [+0.1084, +0.1918]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.148986; legs={'shifted_t+1': 0.132235, 'inverted': -0.075099}; inverted reaches -0.0751 vs the real 0.1490 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 88% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0752 | 90% [+0.0433, +0.1115] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 55 — batch_screen.py cheap-gate survivor: `opening_range_vs_atr` LOW / last_hour -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=510, mean=+0.2423 vs all-days +0.2986, z=-7.18. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect -0.0563, Sidak-adjusted 90%-family interval [-0.0773, -0.0377]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `opening_range_vs_atr` (already implemented in market_state_primitives*.py; known at 10:00 ET).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 15:00-16:00 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `opening_range_vs_atr`.
5. **MAP ANCHOR**: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.0563 | Sidak(K=25) [-0.0773, -0.0377] | 90% unadj. [-0.0673, -0.0444]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=-0.056277; legs={'shifted_t+1': -0.045103, 'inverted': 0.02588}; shifted_t+1 reaches -0.0451 vs the real -0.0563 (red at 50%) |
| 4. joint separability (T1) | OK | -0.0136 | 90% [-0.0230, -0.0036] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 56 — batch_screen.py cheap-gate survivor: `volume_vs_expected` HIGH / rth -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=385, mean=+1.0070 vs all-days +0.8382, z=+7.18. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect +0.1653, Sidak-adjusted 90%-family interval [+0.0943, +0.2354]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `volume_vs_expected` (already implemented in market_state_primitives*.py; known at the previous evening's close).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 09:30-16:00 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `volume_vs_expected`.
5. **MAP ANCHOR**: M31 (prior-day volume vs expected -> first-30-minute range, NQ; market_structure_map.md row M31)

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.1653 | Sidak(K=25) [+0.0943, +0.2354] | 90% unadj. [+0.1240, +0.2076]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.165343; legs={'shifted_t+1': 0.124882, 'inverted': -0.085446}; inverted reaches -0.0854 vs the real 0.1653 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 60% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0370 | 90% [+0.0056, +0.0703] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 57 — batch_screen.py cheap-gate survivor: `opening_range_vs_atr` LOW / afternoon -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=510, mean=+0.2530 vs all-days +0.3220, z=-7.13. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect -0.0690, Sidak-adjusted 90%-family interval [-0.0921, -0.0477]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `opening_range_vs_atr` (already implemented in market_state_primitives*.py; known at 10:00 ET).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 13:30-15:00 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `opening_range_vs_atr`.
5. **MAP ANCHOR**: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.0690 | Sidak(K=25) [-0.0921, -0.0477] | 90% unadj. [-0.0805, -0.0561]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=-0.06899; legs={'shifted_t+1': -0.046064, 'inverted': 0.031727}; shifted_t+1 reaches -0.0461 vs the real -0.0690 (red at 50%) |
| 4. joint separability (T1) | OK | -0.0302 | 90% [-0.0426, -0.0175] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 58 — batch_screen.py cheap-gate survivor: `vxn_minus_realized` HIGH / last_hour -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=545, mean=+0.3503 vs all-days +0.2986, z=+6.82. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect +0.0519, Sidak-adjusted 90%-family interval [+0.0269, +0.0895]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `vxn_minus_realized` (already implemented in market_state_primitives*.py; known at the previous evening's close).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 15:00-16:00 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `vxn_minus_realized`.
5. **MAP ANCHOR**: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0519 | Sidak(K=25) [+0.0269, +0.0895] | 90% unadj. [+0.0340, +0.0697]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.051898; legs={'shifted_t+1': 0.046808, 'inverted': -0.026484}; inverted reaches -0.0265 vs the real 0.0519 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 88% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0087 | 90% [-0.0024, +0.0187] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=False |

---

## ENTRY 59 — batch_screen.py cheap-gate survivor: `vxn_minus_realized` LOW / midday -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=555, mean=+0.3095 vs all-days +0.3738, z=-6.79. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect -0.0645, Sidak-adjusted 90%-family interval [-0.0924, -0.0375]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `vxn_minus_realized` (already implemented in market_state_primitives*.py; known at the previous evening's close).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 11:30-13:30 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `vxn_minus_realized`.
5. **MAP ANCHOR**: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.0645 | Sidak(K=25) [-0.0924, -0.0375] | 90% unadj. [-0.0806, -0.0482]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | GREEN | -- | -- | real=-0.06454; legs={'shifted_t+1': -0.052495, 'inverted': 0.032241}; no gating placebo comes close to the real effect [shifted_t+1 reported but NOT gating: it re-selects 87% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0281 | 90% [-0.0427, -0.0142] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 60 — batch_screen.py cheap-gate survivor: `location_in_range` LOW / last_hour -> range (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=540, mean=+0.3503 vs all-days +0.2986, z=+6.79. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect +0.0519, Sidak-adjusted 90%-family interval [+0.0246, +0.0832]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `location_in_range` (already implemented in market_state_primitives*.py; known at 09:30 ET (RTH open)).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 15:00-16:00 ET (range outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `location_in_range`.
5. **MAP ANCHOR**: M32 (open's location in the prior day's range -> later-session range, NQ; per idea_inventory.md ENTRY 36, which sourced and drew this anchor). NOTE: as of this script's writing, market_structure_map.md's own table has not yet been updated to add an M32 row -- a pre-existing maintenance gap this script did not create and is not the file to fix (out of scope: this script may only append to idea_inventory.md, never edit market_structure_map.md). Flagged for LEARN/Director.

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0519 | Sidak(K=25) [+0.0246, +0.0832] | 90% unadj. [+0.0344, +0.0690]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.051901; legs={'shifted_t+1': 0.031492, 'inverted': -0.02612}; inverted reaches -0.0261 vs the real 0.0519 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 84% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0108 | 90% [-0.0227, -0.0003] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---

## ENTRY 61 — batch_screen.py cheap-gate survivor: `opening_range_vs_atr` HIGH / midday -> mfe (batch_screen.py, 2026-09-15) — SURVIVOR, batch K=25, screened only, not scanned — PARKED September 15th (Jason's refocus, research/infrastructure/refocus-2026-09-15.md s.3: magnitude research FROZEN; batch screening frozen; NOT DRAWABLE until the 72% placebo-RED rate has a real explanation)

Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item 0-ACCEL): drawn from the Idea Factory candidate_queue (idea_factory_2026-09-14.json), descriptive n=558, mean=+0.2214 vs all-days +0.1757, z=+6.71. Re-tested here with a calendar-time block bootstrap (block=10) and a Sidak correction at this batch's own K=25 (NOT the 143-cell sweep total): raw effect +0.0457, Sidak-adjusted 90%-family interval [+0.0291, +0.0631]. Gates 3 (shifted-signal placebo) and 4 (joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail bars at this stage -- see the FULL SCREEN TABLE below.

1. **STATE VARIABLE**: `opening_range_vs_atr` (already implemented in market_state_primitives*.py; known at 10:00 ET).
2. **MECHANISM CLAIM**: PROVISIONAL, inherited from the map anchor's own forced-participant story cited below; Director/Mechanism stage owed the full written claim before any registered scan (per src/idea_factory.py's own discipline: a queue entry is a candidate for a mechanism document, not a finding).
3. **HORIZON**: 11:30-13:30 ET (mfe outcome).
4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, not a Director-triaged entry -- Director owes the full resurrection check (ledger by name and by what is measured) before any scan is registered against this cell. See MAP ANCHOR for any known adjacency/attempt-limit flags on `opening_range_vs_atr`.
5. **MAP ANCHOR**: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the multiplicity denominator is never lost -- batch K = 25):

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0457 | Sidak(K=25) [+0.0291, +0.0631] | 90% unadj. [+0.0356, +0.0558]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.045654; legs={'shifted_t+1': 0.031266, 'inverted': -0.022848}; shifted_t+1 reaches 0.0313 vs the real 0.0457 (red at 50%) |
| 4. joint separability (T1) | OK | +0.0205 | 90% [+0.0112, +0.0312] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

---
