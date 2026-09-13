# Outside-review master synthesis — all six reviews, consolidated (v2)

**Written:** September 13th, ~5:30 pm CT. Supersedes v1 (which covered three reviews).
**Purpose:** Jason pulled the September 19th checkpoint forward and gathered six outside
reviews of Tony over the afternoon. This is the single record of all of them — every
recommendation, list, formula, form, and observation preserved — plus where they agree,
where they conflict, what needs verifying against Tony's actual state, and the decisions
only Jason can make. Sits alongside `sept19-checkpoint-deliberation-2026-09-13.md`,
`perspective-scoping-2026-09-13.md`, and the weekly-review draft as checkpoint scope.

**Labels:**
- **A — Growth & Scalability Review** (the file `tony-growth-review-2026-09-13.md`; Jason's
  earlier forwarded "short version" is the same review, so they're merged here).
- **B — "CONTINUE with a major architectural upgrade"** (18 sections).
- **C — "Research operating system"** (registries, Q-score, 30/60/90 roadmap, ten metrics).
- **D — "The generation process is designed like a review process"** (short; Observatory
  free-look + VXN-vs-realized gap).
- **E — "Scalable Research & Trading-System Development Framework"** (19 sections; idea
  generation engine, taxonomy, question families, idea genome, behavior library).
- **F — "Idea Factory"** (engines table, question matrix, intake/test-design/strategy/closure
  forms, capacity lanes, weekly scorecard).

---

## 1. Headline

Six reviews, zero pivots. Every one says **CONTINUE**, and every one lands on the same
diagnosis in different words:

> Tony's validation machinery is the asset. Tony's idea-generation front end is the
> bottleneck. The validated volatility facts are the raw material for the first thing
> Tony can actually run, not consolation prizes. Fix generation by making it structured
> and observation-first — not by generating a thousand more one-off hypotheses.

A and D go one step further than the others: they say the *reason* generation is weak
is that Tony's current sourcing bar (citation + published effect + named forced
participant + mechanism doc **before** any look at the data) selects for ideas that are
already in print and already competed away. Literature going 0-for-4 this week is the
filter working as designed, not bad luck.

---

## 2. Consensus matrix

| # | Point | A | B | C | D | E | F |
|---|---|---|---|---|---|---|---|
| C1 | CONTINUE; no pivot; keep validation discipline intact | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| C2 | Two (or three) parallel tracks: research AND build/paper-trade | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| C3 | Idea generation is the bottleneck; better stats can't compensate | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| C4 | Validated volatility facts are **state variables** → build a risk/state layer from them | ✓ | ✓ | ✓ | ✓ (as conditioning) | ✓ | ✓ |
| C5 | Paper-trade / execution qualification starts now, as infrastructure, not as proof of alpha | ✓ (now) | ✓ | ✓ | — | ✓ | ✓ |
| C6 | Conditional retest of dead ideas only via ONE pre-registered condition from an established mechanism or validated state | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| C7 | Swing exit must be frozen as a rule before results; exit research is its own family | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| C8 | Don't buy data yet; write a trigger for when it would earn its purchase | ✓ | ✓ | ✓ | — | ✓ | — |
| C9 | Shift sourcing weight from literature/calendar toward map/mechanism/structure; keep literature alive at low priority with a higher bar | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| C10 | Integrity Gate isn't truly independent (one model = one blind-spot set); fix structurally | ✓ (code) | ✓ (blindness) | ✓ (skeptic role) | — | — | — |
| C11 | Ask many pre-registered questions of the same data via families/batteries, with family-level multiplicity accounting | ✓ (outcome battery) | ✓ (question matrix) | ✓ (families) | ✓ (time × state cuts) | ✓ (question families) | ✓ (question matrix) |
| C12 | Observation comes before story: look at the data first, then ask who's forcing it | ✓ | ✓ (Observatory as state-discovery engine) | — | ✓ (bluntest) | ✓ (core philosophy) | ✓ |
| C13 | Failures must produce reusable information (negative constraints, residual state info), not just "FAILED" | — | — | ✓ | — | ✓ | ✓ |
| C14 | Every fact / hypothesis / strategy needs a durable registry or library with lineage | — | — | ✓ (3 registries) | — | ✓ (behavior library + idea genome) | ✓ (feature library + forms) |
| C15 | Replace "hypotheses closed" with yield metrics (actionable-pass rate, strategy-conversion, fidelity, family yield) | — | — | ✓ | — | ✓ | ✓ |
| C16 | M23 Statistical stage: finish it, but don't let a 6E result pull the project off the NQ mission | — | ✓ | ✓ | — | ✓ | — |
| C17 | Tokyo companion is worth running because it's mechanically related, not because London makes it likelier | — | ✓ | — | — | — | ✓ |

---

## 3. Each review preserved in full

### A — Growth & Scalability Review (six findings, ranked next steps, Q&A)

**Findings**
- **A. The machine works; it's pointed at the hardest target in finance.** 137 hypotheses,
  zero directional survivors, on 1-minute bars of the most liquid index future in the
  world — the expected result, not a defect. Directional edges in NQ from price alone are
  the single most competed thing in markets. Rigor was never the problem.
- **B. The pipeline already found where the edge is and keeps filing it as "not a
  strategy."** Everything that survived is about *how much* and *when*, not *which way*:
  range persistence, overnight coil → quiet day, midday lull → quiet afternoon, VXN →
  next-day range, London open / ECB / EIA bursts. Volatility persistence is the most
  robust fact in finance and what every desk builds sizing, targets, stops on. Six
  confirmations, three out-of-sample, none built into anything. Largest untapped asset.
- **C. The statistical bar is too tight in one specific place.** Project-wide Šidák at
  ~275 trials means a Discovery cell needs a p-value ~250× smaller than a normal 90%
  test — *on top of* two out-of-sample confirmations that already control false
  discoveries. Stacking both is why nothing clears. Professional practice: control
  multiplicity *within a scan* (false discovery rate), let Validation/Holdout be the
  project-wide control. Not a loosening — a removal of double-counting.
- **D. The Integrity Gate isn't independent; H118 proved it.** One model in every role
  shares one blind-spot set; baseline confusion passed three stages because every
  reviewer had the same gap. Blind packaging doesn't fix that. **Code does:** drift null,
  overnight/intraday split, cost sensitivity, roll-date contamination, subperiod
  stability — run mechanically on every candidate, like `ops_checks.py`, so a green
  result can't depend on someone remembering to ask.
- **E. The money goal and the risk budget don't fit each other or the instrument.** One
  MNQ moves ~$600–900 on a normal day; a 0.05R edge is worth ~$30–45/trade. $1,000/month
  on a $300 loss budget requires trading daily while carrying daily noise 2–3× the entire
  budget — the kill switch fires before the edge shows up. Keep $300 as the hard loss
  limit. Replace "$1,000/month" with "positive measured expectancy after costs over N
  trades," let size follow the record.
- **F. "Nowhere to put it" is self-imposed.** M20 (crude) and M21 (euro) are the same
  class of finding as M23, and the Sept 12th rule says NQ is the default vehicle, not
  the search space. Micro contracts exist for both. All three are one family: does a
  scheduled volatility burst convert to a tradeable structure?

**Why it matters:** Tony has quietly proven that in this data **direction is noise and
volatility is signal.** The 19th plan treats that as a consolation prize; it's the actual
finding. It changes what "hypothesis generation" means: stop asking "does X predict up or
down?" and ask "what does the market do inside a known volatility state?" — that's where
conditional directional edges (Topic 2), exit rules (Topic 6), and the first
paper-tradeable candidate live.

**What to do next (ranked)**
1. **Un-park the execution clock — now.** Execution qualification doesn't need a
   promoted strategy. Fills, slippage, latency, reconciliation, kill switch can all be
   measured on paper with a dummy signal. The thresholds still flagged "unset"
   (slippage, drawdown, divergence) can't be set without measuring, and can't be
   measured without an order path. Build phases 6–8 on the free paper endpoint already
   identified. Every future candidate inherits it. Spend already approved 9/10.
2. **Build the Risk Engine — the volatility product.** Input: validated range forecasts.
   Output for any trade: that day's expected range, target distance, stop distance,
   size. Turns "three facts" into something every candidate uses; the sizing overlay
   professionals run first. Most concrete answer to "paper trade what's validated."
3. **Multi-question scans, done honestly (Topic 1 upgrade).** For each state variable,
   pre-register a fixed **outcome battery** instead of one outcome: mean vs. drift-null,
   range ratio, max favorable / max adverse excursion (how far a trade went for you vs.
   against you before exit — this is how exits get designed), time-to-resolution.
   Register every cell up front, FDR within the battery.
4. **First conditional candidates through the normal pipeline:**
   - *Inside forecast-compressed days:* fade moves beyond X% of forecast range back
     toward VWAP. Mechanism: liquidity providers win quiet days; breakouts fail.
   - *Overnight vs. intraday return split on NQ.* Nearly all equity-index drift accrues
     overnight; intraday is flat-to-negative. Highly replicated, testable on disk,
     measured against the drift null by construction.
   - *Scheduled-event volatility structure* (M20/M21/M23 as one family; add NFP/CPI/FOMC
     on NQ). Bracket entry before or fade after — pre-register which.
5. **Swing exit — scope after item 3, not before.** An exit rule only makes sense
   attached to a behavior with multi-day drift that a stop doesn't race. Once item 3
   produces excursion data, the standard candidate is a volatility-scaled trailing stop
   fed by the Risk Engine.
6. **Integrity test suite in code (finding D).** 19th agenda, under the freeze.
7. **Statistical-bar review (finding C).** Same.
Items 1, 2, 4 are build/queue work that don't touch the freeze. Items 3, 6, 7 are rule
changes for the scheduled review.

**Section-11 Q&A (short answers):** Continue? Yes — pivot the *target* from direction to
structure; more aggregate directional scans have near-zero expected value. Bar too tight?
In the Šidák stacking, yes; otherwise right. Ranking by info gain × edge potential?
Right, with a guard: cap the share of long-shots per cycle. Declining data? Right for
now; Risk Engine + first paper record earns the purchase. Shelf rule? Real; it relocated
the problem to sourcing, where it belongs. Blind Gate independent? No (see D). Back half
matches professional practice? Yes, but run in the wrong order — execution parked behind
research. Highest-value next move? Build the sizing product, then hunt for direction
inside it. Biggest way still fooling yourself: believing a directional edge must exist
because the machine to find one is this good.

### B — "CONTINUE with a major architectural upgrade" (18 sections)

- **H118 as a category error:** measured against zero, not the asset's own unconditional
  drift. Existing controls (leakage, frozen specs, multiplicity, resurrection, family
  limits, costs, Integrity review, OOS) are strong but don't cover "are we measuring the
  economic question correctly?" A perfectly adjusted p-value on the wrong null is still
  wrong.
- **Benchmark & Economic Validity Gate before Statistical** — seven questions: (1)
  correct null; (2) unconditional behavior; (3) naive long/short benchmark; (4)
  time-of-day benchmark; (5) vol-normalized performance; (6) directional / relative /
  conditional / risk-state?; (7) survives simplest competing explanation. Full audit
  (§13): **Benchmark** (unconditional return, drift, matched time-of-day, matched vol
  state, long/short) · **Direction** (long, short, symmetric, relative) · **Measurement**
  (raw points, ATR-normalized, R-multiple, vol-adjusted, benchmark-relative) ·
  **Concentration** (year, regime, time of day, event, few observations) · **Placebo**
  (randomized entry, shifted signal, inverted signal) · **Alternative explanation**
  (trend, volatility, seasonality, drift, liquidity, market beta).
- **Execution infra has value at $0 P&L** — signal timing, sizing, realized slippage,
  routing, latency, frequency, operational failures, signal correlation, capital
  requirements; reusable for every future strategy.
- **Level-sweep question matrix** (12 questions): unconditional; conditional on prior
  volatility; overnight range; prior-session direction; distance from VWAP; time of day;
  market volatility; NQ vs ES vs RTY; same vs opposite direction; immediate vs delayed;
  after compression vs expansion; after failed vs successful breakouts. **Register the
  whole family before looking; carry the family's multiplicity burden.**
- **Observatory → market-state discovery engine.** State → Transition → Outcome. Look
  for persistence, reversal, continuation, vol expansion/contraction, asymmetry, timing,
  cross-market relationships, conditional interactions. Monetization asks afterward.
- **Seven uses for a state variable:** entry filter, position sizing, stop distance,
  profit target, trade permission, holding period, execution rules.
- **Four-layer org chart:** Market Intelligence (Discovery, Mechanism, Observatory) ·
  Alpha Research (Statistical, Director) · Strategy Engineering (Monetization,
  Portfolio, Execution) · Research Integrity (cross-cutting).
- **Portfolio's future role:** "what independent sources of return or risk information
  do we possess?" — Market State → Alpha Forecast → Expected Opportunity → Position Size
  → Execution Model → Risk Controls.
- **Data Acquisition Trigger** (six conditions): credible mechanism exists; missing
  variable specifically required; high expected information gain; can't be falsified
  with current data; likely edge justifies cost; purchase resolves a defined decision.
- **Priority formula:** Expected Information Gain × Edge Potential × Testability ×
  Strategic Reusability ÷ Research Cost.
- **Conditional retest hard rule:** reopen only via a pre-specified conditioning family;
  the variable must come from an established mechanism or validated state.
- **Swing:** separate research horizon, must fit hours-to-days; "entry + fixed exit
  architecture," never "entry → optimize 15 exits"; decompose entry/exit/sizing/regime.
- **Integrity Gate structural blindness:** receives frozen candidate, raw outputs, audit
  rules, ledger, benchmark results — NOT the Discovery narrative, Mechanism persuasion,
  expected result, or Director recommendation. "Don't ask the skeptic to review the
  sales pitch."
- **Target architecture:** Observatory → Direction/Volatility/Structure states →
  Conditional Research → Alpha Discovery → Economic Validity Gate → Statistical →
  Director → Monetization → Integrity Gate → Validation/Holdout → Strategy Engineering
  (Entry/Sizing/Exit) → Paper Trading → Execution Data → Live Qualification → Capital.
  Execution data feeds back without contaminating confirmation data.
- **30–60 days, four workstreams:** Discovery Engine v2 (highest) · State Engine ·
  Execution Qualification · New Alpha Research (mechanism → state → conditional →
  monetization).
- **Queue priority:** 1 Discovery Engine v2 · 2 state engine → paper · 3
  mechanism/participant research · 4 conditional re-testing · 5 finish M23 (don't let 6E
  distort NQ mission) · 6 Tokyo companion · 7 swing (bounded) · 8 data: still no.
- **Philosophy:** build a machine that discovers, validates, monetizes, executes, and
  retires alpha; the next evolution is a closed-loop research OS, not another agent.

### C — "Research operating system" (registries, Q-score, roadmap, metrics)

- Bot is optimized to test ideas, not produce/rank/combine/operationalize them. 11
  closures → 1 useful, 2 real-but-unusable, 8 null.
- **Linear pipeline → evidence graph:** mechanism → state feature → entry context →
  risk/exit rule → portfolio behavior. A failed idea becomes a negative constraint, a
  conditional-retest candidate, or channel-yield evidence.
- **Three registries:** *evidence/fact* (ID, definition, market, horizon, mechanism,
  status, stability, expiry/review date, related facts) · *hypothesis* (ID, channel,
  claim, mechanism, test count, status, failure mode) · *strategy* (ID, linked fact/signal
  IDs, entry/exit, costs, exposure limits, paper status, promotion history). Bidirectional
  links.
- **Seven bounded research families:** session-transition · compression/expansion ·
  event-mechanics (only where tradeable) · cross-market confirmation ·
  regime-conditioned retests · exit research · execution-quality. Rule: one mechanism,
  one predeclared condition, one primary outcome, one frozen validation plan. Correct M26
  statement: "does the rejected level-sweep reversal have positive conditional expectancy
  specifically after prior-day range contraction, because compression plausibly
  concentrates the liquidity-release move."
- **Q-score:** Q = 0.30·Mechanism + 0.25·Actionability + 0.20·Testability +
  0.15·Distinctiveness + 0.10·Reuse; Q ≥ 0.65 for full pipeline entry.
- **Safeguards:** immutable holdout; full ledger; family-level attempt accounting;
  walk-forward for strategy prototypes; embargo/purging on overlapping labels; cost
  realism as baseline; robustness tests; DSR + PBO at family level.
- **Promotion = seven-way agreement:** mechanism coherence; sample/regime coverage; OOS
  stability; cost-adjusted expectancy; parameter robustness; low single-date/trade
  dependence; real execution-spec compatibility. Automate as a release gate.
- **MVP paper strategy — state-conditioned breakout:** state layer (prior-day
  contraction, overnight coil, VXN, session eligibility) · trigger layer independent of
  state (range break, ORB, failed-breakout reversal) · risk layer (fixed R, no averaging,
  daily loss limit, max exposure, event avoidance) · exit research layer (1R/2R, time,
  vol-trailing, session close) · no-trade layer. Warning: "predicts wider range" ≠
  "predicts direction."
- **Six promotion stages:** candidate → validated component → prototype → shadow/paper →
  limited live → scaled live. "Scale behind evidence."
- **Research-control plane — persist per run:** hypothesis+mechanism; channel+family;
  instrument/interval/dates; data hash+timestamp; commit; params+seed; feature defs +
  signal timestamps; cost model; results/diagnostics/plots/trade list/decision; reviewer
  decision; links.
- **Seven roles with "must not do alone":** source scout; hypothesis designer; test
  engineer; skeptic; strategy assembler; paper-trade operator; research director.
- **Allocation:** 40% mechanism-first · 25% assembly+exit · 20% conditional retests ·
  10% observatory/execution · 5% literature/practitioner.
- **30/60/90:** *1–30* registries, Q-score, family taxonomy retro-tag, M23 Statistical,
  M26/M27 as frozen, automated pre-release suite (calendar, day-of-week, symbol, cost,
  lookahead, one-print), weekly dashboard, one full paper spec · *31–60* shadow engine
  logging every signal/fill/block/exception, exit research formal, walk-forward reports,
  attempt-count + selection-bias flag, negative-knowledge library, bounded combos (2–3
  filters × 1 trigger × 3 exits) · *61–90* paper vs expected distribution, signal
  quality / fill realism / missed-trade rate / latency / slippage variance / override
  frequency, retire unstable prototypes, promote few to limited-live-eligible with
  pre-set ceiling, reallocate by yield, day-90 data-cap checkpoint.
- **Ten metrics:** actionable-pass rate · strategy-conversion rate · paper-trade fidelity
  · family yield · reuse rate · time-to-decision · reproducibility rate · defect escape
  rate · concentration risk · experiment debt.
- **Seven decisions for the 19th:** two-track mandate; fact→signal→strategy;
  family quotas; conditional-retest protocol; first paper prototype; swing-exit scope as a
  rule; minimum ledger + automated release checks.

### D — "The generation process is designed like a review process"

- **The critique:** an idea can't become an entry until it has a citation, published
  effect size, decay evidence, named forced participant, confounds, kill rule, and
  multiplicity cost. Great bar for *testing*; terrible bar for *finding*, because the only
  ideas that clear it on paper already exist in print — exactly the ones the market has
  already traded away. **Literature 0-for-4 isn't bad luck; the filter selects for
  competed-away ideas.**
- **Where real edges come from:** someone looks at the data first, notices the market
  behaves differently at a specific time under a specific condition, *then* asks who's
  forcing it. The looking comes before the story. Tony has the slice for that —
  Discovery is explicitly "the only place anyone may search" — but treats it like
  Validation, refusing to look without a pre-written mechanism. The rule is doing the
  wrong job.
- **Change 1 — let the Observatory look freely on Discovery data, cheaply.** Descriptive
  only; no hypothesis ID spent; no scan registered. Cut NQ by **when** (overnight, first
  30 min, midday, last hour, around events) × **state** (the validated volatility facts).
  Nearly every real index-futures edge is a time-of-day × state interaction; scans have
  run at daily buckets and 10-day drift — far too coarse to see one. The template then
  applies to what shows a footprint, before Validation. **The confirmation slices are
  what protect you, not the template.**
- **Change 2 — add one unused state variable: the gap between VXN and realized range.**
  When implied volatility sits well above what's actually being realized, options dealers
  are positioned in a way that dampens moves (mean reversion); when below, the reverse.
  The closest proxy in Tony's data to the dealer hedging Jason said he can't see.
- **Bluntest version:** right now Tony generates ideas by writing essays. It should
  generate them by looking.

### E — "Scalable Research & Trading-System Development Framework" (19 sections)

- **Executive direction:** CONTINUE; evolve from strategy-testing system to scalable
  research-to-execution system. Objective: a machine that repeatedly discovers,
  validates, monetizes, executes, monitors, replaces edges. Five connected
  capabilities: market observation · structured idea generation · rigorous validation ·
  strategy construction + execution qualification · continuous learning.
- **§1 Core philosophy:** Market → Observe → Measure → Characterize → Baseline → Generate
  → Test → Monetize → Freeze → Validate → Execute; not "find strategy online → backtest →
  modify until profitable." Observatory stays exploratory, never a confirmation engine.
- **§2 Idea-Generation Engine, five sources:** (A) market-structure observations —
  compressed range → expansion; failed breakout → continuation/reversal; overnight
  positioning → RTH; opening → later session; vol state → direction; prior-day → next
  day; repeated level interaction → response — *observation first, trade later*. (B)
  participant/mechanism hypotheses — forced rebalancing, hedging, index/ETF flows,
  options positioning, liquidity provision, institutional execution, MM inventory,
  benchmark execution, session transitions, cross-market arb, risk constraints,
  scheduled institutional activity — must produce a measurable prediction with specific
  time/instrument/differential. (C) conditional hypotheses on independently established
  state variables; never search hundreds of conditions after the result. (D)
  cross-market — ES/RTY/VIX-VXN/bonds/USD/vol → NQ; lead/lag + mechanism, not
  correlation mining. (E) time/state transitions — overnight, premarket, opening,
  morning, midday, afternoon, close, post-close as distinct states; "what changes from
  State A to B?"
- **§3 Research taxonomy per hypothesis:** family (trend, reversal, breakout, failed
  breakout, volatility, range, liquidity, session transition, cross-market,
  participant-driven, calendar/event, state-conditional, relative-value) · mechanism ·
  observable variable · prediction · falsifier · monetization path · required data ·
  research cost · strategic reusability.
- **§4 Generate questions before strategies.** Weak: "buy NQ after overnight low sweep."
  Better: "conditional distribution of subsequent returns after an overnight low
  sweep." Best: "...conditional on overnight compression, vol state, distance from
  prior close."
- **§5 Question families** per event: Direction (continue? reverse? asymmetric?) ·
  Magnitude (larger/smaller than normal?) · Timing (immediate / later / next session /
  several) · Conditionality (vol, trend, overnight range, time of day) · Cross-market
  (leads? confirmation matters?) · Persistence (stable over years? regime-robust?) ·
  Monetization (direction / sizing / filtering / stop-target / holding period). Entire
  family defined before results.
- **§6 Two environments, absolute separation:** Discovery (broad, thousands of
  relationships, exploratory stats, fast rejection, nothing confirmed) vs. Confirmation
  (one candidate, one predefined test, frozen rules, known search history, known
  costs/benchmark, OOS, then holdout).
- **§7 Research capital allocation:** Priority = Information Gain × Edge Potential ×
  Testability × Strategic Reusability ÷ Research Cost.
- **§8 Vol findings as first state layer:** sizing, stop, target, eligibility, expected
  opportunity, holding period, execution aggressiveness, strategy selection. "Alpha
  predicts opportunity. State predicts environment. Risk converts opportunity into
  exposure. Execution converts exposure into fills."
- **§9 Conditional retesting as formal channel:** allowed only via predefined
  conditioning family justified by independent state info or materially different
  mechanism; each retest needs new mechanism, new prediction, predefined condition,
  documented reason the original test couldn't answer it.
- **§10 Market-Behavior Library:** store "NQ exhibits X under Y" not "Exp 118 failed";
  fields: behavior, confidence, instrument, timeframe, condition, mechanism, status
  (observed/promising/validated/rejected/disproven), monetization attempts.
- **§11 Idea Genome:** every hypothesis inherits parent metadata (parent behavior →
  derived question → derived hypothesis → monetization → validation); lets the system
  ask which families repeatedly fail, which mechanisms repeatedly help, which variables
  recur in survivors, where capital is repeatedly spent.
- **§12 Director as research portfolio manager:** 30% mechanism/participant · 25%
  Observatory/state · 20% conditional · 15% cross-market · 10% exploratory — adjustable
  by evidence.
- **§13 Failure produces information:** what failed, why, which assumption, which
  mechanism falsified, what remains true — "opening fade failed after costs" ≠ "opening
  structure has no information"; preserve residual state info explicitly.
- **§14 Execution track now:** prove the machine converts a frozen signal into an order
  lifecycle; measure signal/order timestamps, type, intended vs actual price, spread,
  slippage, latency, rejections, partials, position state, realized P&L, expected vs
  actual.
- **§15 Don't optimize strategy around execution yet:** measure, don't rescue; execution
  improvements become their own family later.
- **§16 Architecture:** Observatory → Idea Generation (Mechanisms / State Changes /
  Cross-Market) → Question Families → Discovery → Economic Validity Gate → Statistics →
  Director → Monetization → Integrity Gate → Validation/Holdout → Strategy Engine (Alpha
  / State / Risk) → Execution → Paper/Live → Execution Data → Research Feedback (must not
  contaminate confirmation).
- **§17 Roadmap:** P1 Discovery Engine v2 (taxonomy, families, question matrices,
  mechanism templates, conditional rules, genealogy, capital scoring, duplicate
  detection, family exposure tracking) · P2 State Engine · P3 mechanism-first research
  (identifiable participant, measurable, time-constrained, falsifiable, cross-market
  implications) · P4 conditional research · P5 execution qualification · P6 finish
  M23/current candidates without NQ-mission drift · P7 swing as separate family · P8 data
  only via a Data Acquisition Trigger.
- **§18 Success:** Tony autonomously identifies a behavior, explains it, generates a
  controlled family, benchmarks correctly, tests, constructs a frozen monetization
  hypothesis, validates OOS, sends to execution qualification without improvisation.
- **§19 Principle:** preserve the architecture; improve the component evidence says is
  weak. Observe → Explain → Predict → Test → Monetize → Validate → Execute → Learn. **Don't
  solve the 137-hypothesis problem with 1,000 more hypotheses; make the generation space
  structured, mechanism-driven, auditable, reusable.**

### F — "Idea Factory" (engines, forms, scoring, lanes, weekly scorecard)

- **Core upgrade:** make idea generation a formal product of the bot — a dedicated layer
  before testing — with structured outputs that can be ranked, audited, reused,
  automated. Operating loop: observation → mechanism → family → precise candidate →
  pre-test score → frozen test → evidence outcome → strategy component or reusable
  learning. Every result is a reusable object: pass → fact/filter/exit/sizing/strategy;
  failure → negative constraint; near-miss → one governed conditional retest; true-but-
  not-actionable → tagged and deprioritized (EIA/ECB).
- **Nine generation engines** (with priority): market-structure map (H) · regime/state
  (H) · event-mechanics (M-H) · cross-market (M-H) · path-shape — does the route into a
  level matter more than the level? speed, volume, touches, failed breaks, dwell time
  (M) · exit/trade-management — MAE/MFE, holding time, session (H) · execution-quality —
  when to decline or resize (H) · literature/practitioner (exploratory, only after
  mechanism + actionability screening) · failure-reuse (required). Favor the first six.
- **Start from behavior, not indicators** — when does liquidity enter/leave; when are
  participants repositioning; when does compression become expansion; balance /
  imbalance / persistence / exhaustion / failed discovery; which conditions change an
  existing setup's value; which facts decide *whether not to trade*; what affects
  reaching target before stop/time. Example upgrade from "does a 9:30 breakout work?" to
  "after prior-day contraction and overnight coil, does the first confirmed opening-range
  break in the highest-liquidity window have greater expansion and lower reversal
  frequency than unconstrained conditions?" (state, event, comparison, outcome,
  mechanism, use all specified).
- **Question matrix** (eight dimensions): market state · time structure · location · path
  · cross-market context · participant pressure · outcome type (direction, magnitude,
  volatility, reversal risk, holding time, slippage, target completion) · action (entry,
  block, size, exit, execution). Worked London-open family: range expansion vs
  directional? stronger after Asian coil? stronger near overnight H/L? trigger,
  no-trade warning, or exit/sizing? same at Tokyo and U.S. open? — Tokyo companion is the
  right next move.
- **Idea families, not isolated ideas** — family record: mechanism, markets, states,
  outcomes, permitted variants (one state + one location + one session def), prohibited
  (threshold tuning after results). No child test without: parent family, sibling count,
  why it differs, primary outcome chosen beforehand, protected slices untouched.
- **Candidate intake form** (19 fields): ID · title · parent family · source channel
  (map, observatory, literature, practitioner, failure reuse, cross-market,
  user-directed) · market (tradeable or research-only) · timeframe/horizon · observation ·
  mechanism · one-sentence claim · at most one new condition · comparator · primary
  outcome · secondary (diagnostic only, can't rescue) · tradeability · dependencies ·
  risks · pre-test score · decision (queue/park/reject/design) · reviewer ≠ originator.
- **One-sentence hypothesis rule:** *If [condition], then [outcome] should differ from
  [comparison] over [horizon], because [mechanism].*
- **Pre-test score:** 0.30 Mechanism + 0.25 Actionability + 0.20 Testability + 0.15
  Distinctiveness + 0.10 Reuse, each 0–5. Thresholds: 4.0–5.0 priority; 3.2–3.9 queue if
  capacity, tighten design; 2.5–3.1 park; <2.5 reject with reason code into
  negative-knowledge library. Auto-reject/park: no mechanism; no tradeable path;
  ambiguous calendar/session; too few observations; same question already failed without
  material new condition; too many tunables; no primary outcome; condition chosen because
  it looked good in past output.
- **Test-design form** (~30 fields): hypothesis ID, family, version, preparer,
  independent reviewer, frozen claim, mechanism, instrument/contract handling, data
  source+version, sample dates, partitions, timezone/session defs, calendar source,
  feature defs, entry/trigger, condition, comparator, primary metric, secondary
  diagnostics, min sample, expected direction, cost model, allowed params, disallowed
  post-hoc mods, leakage checks, concentration checks, stability checks, promotion
  criteria, failure criteria, required artifacts. Incomplete = "design debt," not queue.
- **Conditional-retest protocol** (eight conditions): documented null/near-miss;
  condition chosen before rerun; independent mechanism or validated fact; one new
  variable; both versions reported; new ID linked to original; fresh Validation +
  Holdout; family attempt count incremented. Weak vs strong retest examples (level
  sweep; stop 6→18; every weekday).
- **Feature/fact library** (eight categories with definition cards: ID, plain-English
  def, exact calc, inputs, timezone, start date, caveats, version, users): vol/range
  state · session state · location · path/auction · cross-market · event · execution ·
  outcome labels.
- **Strategy-assembly form** (14 components): ID/version · objective · universe · state
  filters · entry trigger (separate from filters) · invalidation · sizing · exit logic ·
  no-trade rules · cost model · risk controls · backtest evidence links · paper protocol ·
  promotion/kill criteria. Explicitly what the swing-exit item needs before it's
  researchable.
- **Exit research pipeline:** MFE, MAE, time-to-target, time-to-stop, P(target before
  stop), exit by vol state, by session, fast vs slow return, time-stop value,
  trailing-exit value, state-based exit. **Predeclared exit comparison (five only):**
  fixed stop+target · fixed stop+time exit · fixed stop+vol-trailing · fixed
  stop+session-end · one conditional exit tied to a validated fact.
- **Closure form:** ID · family · closure status (clean null / near miss / data
  limitation / execution limitation / valid-but-non-actionable / invalid premise /
  duplicate) · primary outcome · sample adequacy · mechanism verdict · robustness · cost
  sensitivity · concentration · data-quality · what was learned · what not to retest ·
  permitted future condition · related facts/strategies · capacity action. Failure
  conversion examples (opex week; Treasury auction; RTY/ES/NQ momentum; EIA/ECB).
- **Capacity lanes** (max active): immediate strategy assembly 1–2 · high-priority
  discovery 3–5 · conditional retests 1–2 · exit research 1–2 · observatory/data quality
  1–2 · exploratory sourcing backlog only · parked/debt no coding. Allocation: 40%
  structural/mechanism · 25% assembly/paper prep · 15% exit research incl. swing · 10%
  conditional retests from M26 · 5% observatory/data/execution · 5% literature.
- **Quality-control release gates** (ten): symbol/instrument · session/timezone ·
  calendar · missing data · lookahead · cost · concentration · parameter · partition ·
  reproducibility.
- **Weekly report:** executive layer (advanced / rejected / paper-trading / decision
  needed / risks-debt / sustainable actionable rate) + research-factory scorecard
  (ideas sourced, passing gate, tests completed, clean nulls, statistical passes,
  actionable passes, facts → feature library, strategies assembled, paper days/signals,
  QA pass rate, open debt — this week / rolling 30 / implication) + required weekly
  decisions (family capacity up/down; promote/park/kill; fact earned assembly?; prototype
  in range?; blocker before scale; the ONE question to answer next).
- **Ten decisions for the 19th:** approve Idea Factory layer; adopt question matrix +
  family taxonomy; require intake form + score; feature/fact library from existing
  findings; strict conditional-retest protocol; separate exit pipeline then define the
  swing exit; strategy-assembly form before any paper launch; negative-knowledge library;
  automated release checks; replace volume metrics with yield metrics.

---

## 4. Where the reviews differ

| Topic | Positions | Note |
|---|---|---|
| **What to paper-trade first** | A, B, E: risk/state engine alone (sizing, stop, target, permission; no directional trigger). C, F: state-conditioned breakout with a separate simple trigger from day one. | The one real fork. Recommendation in §6, D3. |
| **Execution clock timing** | A: un-park *now*, with a dummy signal. B/E: parallel workstream. C: days 31–60. | Tony's own records list clock items 1a/1c as "Jason's call." |
| **Šidák / multiplicity** | A: current stacking is wrong, use FDR within scan, let OOS be the project-wide control. B/C: keep multiplicity, add Economic Validity Gate / DSR-PBO reporting. | Not contradictory; A's claim needs code verification before any bar change. |
| **Integrity Gate fix** | A: code (mechanical test suite), blind packaging doesn't fix shared blind spots. B: structural blindness of the packet. C: separated skeptic role. | Compatible — do both. |
| **Mechanism doc before looking** | D: drop it at the Observatory stage; look first, story second. B/E/F: observation-first *and* mechanism required before a *test*. Tony today: mechanism doc before any scan. | The reconciliation: free descriptive looking at Discovery (no ID, no registration) → mechanism → registered family → test. D and E actually agree; the conflict is with Tony's current rule. |
| **Swing exit — when** | A: after excursion data exists. B: freeze before any result. C/F: define the rule now. | Freeze the *rule* now; calibrate *parameters* from paper-trading excursion data. |
| **Capacity percentages** | C: 40/25/20/10/5. E: 30/25/20/15/10. F: 40/25/15/10/5/5. | Three different splits — evidence that the exact numbers are guesses; the *direction* is unanimous. |
| **Goal/capital fit** | Only A raises it ($1,000/mo vs $300 vs $600–900/day per micro). | Possibly the most important practical point across all six. |
| **M20/M21 "no path"** | Only A challenges it (micro contracts exist for crude and euro). | Contradicts Tony's Monetization rulings; decision item. |
| **Agent structure** | B: four layers. C/F: seven roles with prohibitions. E: Director as portfolio manager. | Compatible: org chart + job descriptions + allocation authority. |

---

## 5. My own observations (candid)

1. **D is the sharpest single point in the set, and it's aimed squarely at a rule Tony
   adopted on purpose.** SHELF RULE v2 + "mechanism doc BEFORE scan" were built to stop
   fishing. D says they also stop *finding*. Both are true. The reconciliation is in
   Tony's own design already — Discovery is "the only place anyone may search" — but
   cycles haven't been allowed to use it that way. The fix (free descriptive time-of-day ×
   state cuts, no ID spent, no scan registered, template applied only to what shows a
   footprint) is a **rule change under the freeze** and the most consequential one on the
   list.
2. **A's Šidák number matches the code.** N_discovery=275 is exactly what closed hyp-139
   at Statistical, and the VXN log shows "Šidák cumulative" applied again at the blind Gate
   on Validation. Whether that's double-counting depends on whether the Validation-stage
   correction re-counts Discovery trials against an already-independent sample. Diagnose
   read-only first; it's a bar change and stays frozen until Jason rules.
3. **A's "nowhere to put it is self-imposed" is a real catch.** MCL (micro crude) and M6E
   (micro euro) exist. Tony's Monetization stage ruled "no credible path" for M20/M21
   because no base strategy exists on those instruments — but A's point is that
   scheduled-event volatility *is* the strategy family, and it's the same family as M23.
   That's a reclassification, not a new test.
4. **D's VXN-minus-realized-range variable is cheap and untried.** VXN daily and NQ
   realized range are both on disk. It's a new state primitive (Layer 0), not a rule
   change — it can be sourced through the normal shelf without touching the freeze.
5. **B still treats H118 as a completed failure.** It's in frozen forward validation
   (EXP047: 40 trades AND 12 months). The baseline lesson is already built into every
   scan since (M22, M24, M25 all compared against the instrument's own drift). The
   Economic Validity Gate still adds value — placebo, concentration, and
   alternative-explanation checks are NOT systematic today — but the null part is done.
6. **C's and F's Q-score weights and thresholds are invented** (0.30/0.25/0.20/0.15/0.10;
   Q≥0.65; 4.0/3.2/2.5). The five dimensions are sound — Actionability alone would have
   deprioritized EIA/ECB. Adopt the dimensions; calibrate weights against the 137 closed
   hypotheses before trusting a cutoff. Same for all three capacity splits.
7. **C's and F's citation lists are partly noise** (a student-aid site and a bank
   regulator appear). The underlying ideas — Deflated Sharpe Ratio, Probability of
   Backtest Overfitting, walk-forward, purged CV — are standard (Bailey / López de
   Prado). F's "send status" paragraph is an artifact of the tool that wrote it; ignore.
8. **"Six confirmed volatility facts" depends on the stage you count at.** Holdout:
   midday-lull/afternoon, VXN-level/next-day range. Validation or Discovery-pass-no-path:
   range-contraction, overnight-coil, M20, M21, M23 (Statistical still owed). Four to
   seven depending on the bar. The argument doesn't change; the checkpoint doc should
   state the exact count.
9. **A's outcome battery + D's time × state cuts = the concrete Discovery Engine v2
   spec.** B/E/F describe the same thing at larger scale (question matrices, families,
   engines). The minimal version — for each validated state variable, pre-register mean
   vs drift-null, range ratio, MFE/MAE, time-to-resolution, cut by session window, FDR
   within the battery — can be built as one script in the existing repo pattern.
10. **Most of this is structural and therefore frozen.** Pulling the 19th forward means
    Jason can lift or scope the freeze now. Nothing structural below gets built until he
    does.
11. **Cost/usage reality.** F's full apparatus (four forms, nine engines, feature library,
    capacity lanes, scorecard) is weeks of build. A's list plus D's two changes fit
    inside the existing 2-hour cadence this week. Sequence matters more than
    completeness.

---

## 6. Decisions only Jason can make

| # | Decision | Reviews | Recommendation |
|---|---|---|---|
| D1 | **Lift, extend, or scope the freeze** | All assume changes happen | Lift for the named list D2–D16; keep everything else frozen. |
| D2 | **Two-track mandate, formally** | Unanimous | Yes; it's already the Sept 13th deliberation outcome. |
| D3 | **What to paper-trade first** | A/B/E: risk engine alone; C/F: breakout + trigger | Risk/State Engine alone. It's the only thing validated. A directional trigger enters only as its own pre-registered candidate. |
| D4 | **Un-park the execution clock** | A: now; others: parallel/later | Now, for measurement only (fills, slippage, latency, reconciliation on a dummy signal via the free paper endpoint). Spend already approved 9/10. |
| D5 | **Šidák stacking** | A: fix; B/C: add gate | Diagnose read-only now; rule after seeing whether it double-counts. |
| D6 | **Integrity Gate** | A: code; B: blindness | Both: tighten `integrity_blind_packet.py` (evidence in, narrative out) AND write the mechanical suite (drift null, overnight/intraday split, cost sensitivity, roll-date contamination, subperiod stability) into `ops_checks`-style code. |
| D7 | **Economic Validity Gate** | B; C/F overlap | Adopt the parts not already done: placebo, concentration, alternative-explanation checklist. |
| D8 | **Observatory free-look rule** (D) | D; E agrees in principle | Adopt: descriptive time-of-day × state cuts on Discovery only, no ID spent, no scan registered, nothing promoted without a mechanism doc + registered family. This is the single highest-leverage rule change. |
| D9 | **Sourcing emphasis / channel quotas** | B, C, E, F | Adopt the direction (map/structure up, literature down with a higher bar); no hard percentages yet. |
| D10 | **Conditional-retest protocol as written rule** | Unanimous | Adopt F's eight conditions (they subsume B's hard rule and E's four requirements). M26 already complies. |
| D11 | **Swing exit** | Unanimous: must be a rule | Jason names the architecture (fixed / time / trailing / vol-trailing / state-conditioned); it's registered as F's five-exit predeclared family; parameters calibrated from paper excursion data (A). |
| D12 | **Goal/capital fit** (A) | Only A | Replace "$1,000/month" with "positive measured expectancy after costs over N trades"; $300 stays the hard loss limit; size follows the record. |
| D13 | **Reclassify M20/M21** (A) | Only A | Move from "no path" to the scheduled-event volatility family alongside M23 (micro contracts exist); the family becomes one Monetization question. |
| D14 | **VXN-minus-realized-range state variable** (D) | Only D | Source through the normal shelf now — it's a data primitive, not a rule change. |
| D15 | **Registries / libraries / forms** (C, E, F) | C, E, F | Adopt in order of cheapness: closure form (F) → fact registry (C) / behavior library (E) → feature library (F) → intake + test-design forms (F) → idea genome (E). Hypothesis ledger already exists. |
| D16 | **Metrics + weekly format** (C, F) | C, F | Replace "hypotheses closed" with actionable-pass rate, strategy-conversion rate, paper fidelity, family yield; adopt F's weekly scorecard shape. |
| D17 | **Data purchase** | Unanimous no | Write B's six-condition trigger down so the answer becomes "not until X." |

---

## 7. Unified build sequence (if D1 approves the named list)

Every artifact below is tagged with who proposed it so nothing is orphaned.

**This week — inside the existing 2-hour cycles, no new infrastructure**
1. Šidák stacking diagnosis, read-only (A).
2. M23 Statistical stage (B, C, E).
3. M26 and M27 exactly as frozen (C, F) — M26 is the first sanctioned conditional retest.
4. Source the VXN-minus-realized-range state variable to the shelf (D).
5. Register A's three conditional candidates as one-condition families: fade-to-VWAP ×
   compressed prior day; overnight-vs-intraday split; scheduled-event volatility as one
   family (M20 + M21 + M23 + NFP/CPI/FOMC on NQ) (A; F's London family questions fold in).
6. Write the Integrity Gate blindness spec (B) and mechanical test suite spec (A) as
   pre-registrations — build later.
7. Write the Economic Validity Gate additions as a checklist (B).
8. Write the closure form (F) and apply it retroactively to this week's eleven closures.
9. The moment Jason names the exit architecture: register the five-exit family (F) with
   A's "parameters from excursion data" rule.

**Weeks 2–3 — structural, needs the freeze lifted**
10. Observatory free-look mode (D): time-of-day windows × validated states, descriptive
    output only, spends nothing.
11. Discovery Engine v2 minimal: the outcome battery (mean vs drift-null, range ratio,
    MFE/MAE, time-to-resolution) per state variable, FDR within battery (A), extended
    by B/E/F question dimensions as families get registered.
12. Risk/State Engine spec (A, B, E): inputs = validated range facts; outputs = expected
    range, target distance, stop distance, size multiplier, trade-permission flag.
    Frozen, versioned, no P&L claim.
13. Execution-clock measurement on the H118 order path with a dummy signal (A).
14. Fact registry / behavior library (C, E) + feature library definition cards (F).
15. Family-level attempt accounting in `project_wide_multiplicity.py` (C, F).
16. Reclassify M20/M21 into the event-volatility family (A).

**Weeks 4–8**
17. Shadow/paper engine running the Risk/State Engine on live sessions, logging every
    signal, blocked trade, exception, expected vs assumed fill (C, E, F).
18. Exit research pipeline live on the first prototype: MFE/MAE, time-to-target,
    P(target before stop), by vol state and session (F, A).
19. Intake + test-design forms enforced as queue gates; idea genome lineage (E, F).
20. Metrics dashboard on C's ten metrics / F's scorecard; weekly report in F's shape.
21. Day-60 review: does anything trip B's Data Acquisition Trigger?

---

## 8. Plain-language glossary (terms used above)

- **Expectancy** — average profit per trade after costs, across wins and losses. "Positive
  expectancy" = the strategy makes money on average per trade.
- **R / R-multiple** — profit measured in units of the risk taken. A 2R win made twice
  what you'd have lost if the stop was hit.
- **Drift null** — the comparison baseline: NQ goes up on average anyway (~15–16%/yr in
  Discovery), so a "long" idea has to beat that, not beat zero.
- **Šidák / FDR / multiplicity** — corrections for the fact that testing many things makes
  something look significant by luck. Šidák is a strict version (every test must clear a
  much higher bar); FDR (false discovery rate) is a looser version that controls the
  *share* of false positives inside a batch. A's point: Tony applies the strict one across
  the whole project *and* re-confirms out of sample — belt plus suspenders plus a second
  belt.
- **MFE / MAE** — maximum favorable / adverse excursion: the furthest a trade went in your
  favor / against you before it closed. This is the data exits are designed from.
- **Implied vs realized volatility** — implied = what options prices *expect* movement to
  be (VXN); realized = what actually happened. When implied ≫ realized, option dealers
  are positioned to dampen moves; when implied ≪ realized, to amplify them (D's variable).
- **Dealer hedging** — market makers who sold options buy/sell the underlying to stay
  neutral; their forced flow is a mechanical source of pressure.
- **Micro contracts (MNQ, MCL, M6E)** — 1/10-size futures; MNQ moves ~$600–900 on a
  normal day (A's number).
- **Trailing stop / volatility-scaled trailing stop** — a stop that follows price as it
  moves in your favor; "volatility-scaled" means the distance is set from expected range,
  not fixed points.
- **Sizing overlay** — a layer that decides *how much* to trade based on expected
  volatility, separate from the signal that decides *whether* to trade.
- **Placebo test** — run the same test with a randomized, shifted, or inverted signal; if
  the "edge" survives, it was never the signal.
- **Walk-forward** — repeatedly validate on the next unseen slice rather than one
  train/test split.

---

## 9. One-paragraph version for the record

Six independent outside reviews reached the same verdict: continue, don't pivot, and
stop treating Tony's validated volatility facts as consolation prizes. The validation
discipline is the asset; the idea-generation front end is the bottleneck, and two of the
six say *why* — the sourcing bar requires a citation and a mechanism before anyone is
allowed to look, which selects for ideas that are already in print and already traded
away. The fix is to look first (free descriptive time-of-day × state cuts on Discovery
data, spending nothing), register pre-declared families and outcome batteries, then test
only what shows a footprint; and in parallel turn the proven volatility facts into a
frozen risk/sizing engine and start measuring real execution. Everything material is a
structural change under the freeze until Jason lifts it. Three things the reviews left
for Jason alone: which exit architecture he means by "swing trading with a particular
exit," whether a $1,000/month goal is compatible with a $300 budget on an instrument that
moves $600–900 a day per micro, and whether to reclassify the crude and euro volatility
passes from "nowhere to put it" into the same event-volatility family as the London-open
pass.
