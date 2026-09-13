# Outside-review synthesis — three reviews, consolidated (September 13th, ~4:30 pm CT)

Purpose: Jason pulled the September 19th checkpoint conversation forward to today
and gathered three outside reviews of Tony. This file consolidates all three so
nothing is lost, marks where they agree and disagree, flags what needs verifying
against Tony's actual state before acting, and lists the decisions only Jason can
make. Sits alongside `sept19-checkpoint-deliberation-2026-09-13.md`,
`perspective-scoping-2026-09-13.md`, and the weekly-review draft as checkpoint scope.

Labels used below:
- **R1** — Jason's forwarded summary ("direction is noise, volatility is signal").
- **R2** — the long 18-section review ("CONTINUE with a major architectural upgrade").
- **R3** — the "research operating system" review (tables, Q-score, 30/60/90 roadmap).

---

## 1. The headline: all three say the same thing

None of the three recommends a pivot. All three say **CONTINUE**, and all three
independently land on the same diagnosis:

> Tony is very good at rejecting bad ideas and not yet good at producing good ones.
> The validation architecture is the asset. The discovery front-end is the bottleneck.
> The validated volatility facts are not consolation prizes — they are the raw
> material for the first thing Tony can actually run.

That convergence, from three separate sources looking at the same files, is the
strongest single signal in this whole exercise.

---

## 2. Where all three agree (the consensus — safest to act on)

| # | Consensus point | R1 | R2 | R3 |
|---|---|---|---|---|
| C1 | CONTINUE; do not pivot; keep the validation discipline intact | ✓ | ✓ | ✓ |
| C2 | Two concurrent tracks — keep researching AND start building/paper-trading — exactly the blended posture from the Sept 13th deliberation | ✓ | ✓ | ✓ (three tracks: research / strategy assembly / platform-governance) |
| C3 | Hypothesis generation is the real bottleneck, not statistical testing; "better stats don't compensate for weak discovery" | ✓ | ✓ | ✓ |
| C4 | The validated volatility/range facts are **state variables**, not finished work — build a risk/state layer from them | ✓ ("Risk Engine from range forecasts") | ✓ ("State Engine") | ✓ ("fact → signal → strategy") |
| C5 | Paper-trade the validated facts now, but as **infrastructure/execution qualification**, not as proof of alpha | ✓ (un-park execution clock) | ✓ (Workstream 3) | ✓ (shadow deployment) |
| C6 | Conditional re-testing of dead ideas is legitimate ONLY with one pre-registered condition drawn from an already-established mechanism or validated state — never "try 47 conditions until one works" | ✓ | ✓ (hard rule, §11) | ✓ (one mechanism / one condition / one outcome / one frozen plan) |
| C7 | Swing trading: fine, but the exit must be frozen as a rule before any result is seen, and exit research must be its own controlled family — not an exit-optimization loophole | ✓ (scope exit after excursion data) | ✓ (§12) | ✓ (exit research family; decision #6) |
| C8 | Do not buy better data yet | (implied) | ✓ ("data must earn its purchase") | ✓ (checkpoint at day 90) |
| C9 | Map/mechanism channel outperformed literature channel this week; shift sourcing emphasis toward structural participants, keep literature alive at lower priority with a higher bar | — | ✓ | ✓ (5% allocation, higher gate) |
| C10 | The Integrity Gate is procedurally but not epistemically independent — fix it with **structural blindness** (give it the evidence, not the pitch) | ✓ | ✓ (§14) | ✓ (skeptic role) |
| C11 | Ask multiple distinct questions of the same data via **pre-registered families**, with family-level multiplicity accounting | ✓ | ✓ (Hypothesis Family → Question Matrix) | ✓ (bounded research families) |

---

## 3. What each review says that the others don't (preserved in full)

### R1 — Jason's forwarded summary (shortest, but raises three things nobody else does)

1. **The finding, restated:** in this data, direction is noise and volatility is
   signal. Six confirmed volatility facts (three out-of-sample), zero directional
   survivors in 137 tries. "That's the finding, not a shortfall."
2. **Three structural issues underneath it** — the first and third appear in no
   other review:
   - (a) **Šidák stacking.** The project-wide Šidák correction, applied on top of
     two out-of-sample confirmations, **double-counts** and is why nothing clears.
     *(Needs verification — see §5.)*
   - (b) **Integrity Gate not independent** — one model, one set of blind spots;
     "H118 proved it."
   - (c) **Goal/capital mismatch.** A $1,000/month goal doesn't fit a $300 budget
     on an instrument that swings $600–900 a day per micro contract. *(No other
     review touches this. It is a real decision item — see §6.)*
3. **Reframes the hypothesis-generation upgrade:** not "more angles on which way,"
   but "what does the market do inside a known volatility state" — that's where
   conditional edges (Topic 2), exit rules (Topic 6), and the first
   paper-tradeable candidate all live.
4. **Specific next steps:**
   - Un-park the execution clock **now** — it never needed a promoted strategy,
     and the slippage/drawdown thresholds still marked "unset" can't be set
     without an order path to measure them.
   - Build the **Risk Engine** from the validated range forecasts — that IS
     "paper-trade what's validated."
   - Run three named conditional candidates through the normal pipeline:
     **fade-to-VWAP on compressed days**, **overnight-vs-intraday split**, and
     **scheduled-event volatility as one family including crude and euro**.
   - Scope the swing exit **after** excursion data exists, not before.
   - Bar (threshold) and Gate fixes go on the 19th agenda **under the freeze**.

### R2 — the 18-section review (deepest on research design)

- **The H118 lesson as a category error:** the strategy was measured against
  zero rather than the asset's own unconditional drift. Existing controls
  (leakage, frozen specs, multiplicity, resurrection, family limits, costs,
  Integrity review, OOS confirmation) are strong but don't cover "are we
  measuring the economic question correctly in the first place?" A perfectly
  adjusted p-value on the wrong null is still the wrong answer.
- **New formal layer before Statistical: the Benchmark & Economic Validity
  Gate.** Every candidate must answer seven questions: (1) correct null; (2)
  unconditional behavior of the instrument; (3) what a naive long/short benchmark
  does; (4) what a time-of-day benchmark does; (5) volatility-normalized
  performance; (6) is the effect directional, relative, conditional, or merely a
  risk-state effect; (7) does it survive the simplest competing explanation.
  Full audit spec (§13): **Benchmark** (unconditional return, drift, matched
  time-of-day, matched volatility state, long/short) · **Direction** (long,
  short, symmetric, relative) · **Measurement** (raw points, ATR-normalized,
  R-multiple, vol-adjusted, benchmark-relative) · **Concentration** (year,
  regime, time of day, event, few observations) · **Placebo** (randomized entry,
  shifted signal, inverted signal) · **Alternative explanation** (trend,
  volatility, seasonality, drift, liquidity, market beta). "This would have
  killed H118 immediately."
- **Execution infrastructure has value even at $0 P&L** — it produces
  information on signal timing, sizing, realized slippage, routing, latency,
  trade frequency, operational failures, signal correlation, and actual capital
  requirements, and it becomes reusable for every future strategy.
- **The level-sweep question matrix** (the concrete example of "many distinct
  questions"): unconditional response; conditional on prior volatility;
  overnight range; prior-session direction; distance from VWAP; time of day;
  market volatility; NQ vs ES vs RTY; same vs opposite direction; immediate vs
  delayed; after compression vs expansion; after failed vs successful
  breakouts. Critical: **register the whole family before looking, then carry
  the multiplicity burden for the family.**
- **Observatory → market-state discovery engine.** Fundamental object is
  "map conditional relationships," not "find a strategy." State → Transition →
  Outcome. Look for persistence, reversal, continuation, vol expansion,
  vol contraction, asymmetry, timing, cross-market relationships, conditional
  interactions. Monetization asks "can this be a trade?" only afterward.
- **Seven uses for a state variable** (why the vol facts are undervalued):
  entry filter, position sizing, stop distance, profit target, trade permission
  (don't trade when opportunity is compressed), holding period, execution rules.
- **Four-layer reframe of the seven agents:** Layer 1 Market Intelligence
  (Discovery, Mechanism, Observatory — "what does the market do?"); Layer 2
  Alpha Research (Statistical, Director — "what's unusual, persistent,
  economically meaningful?"); Layer 3 Strategy Engineering (Monetization,
  Portfolio, Execution — "can it be traded?"); Layer 4 Research Integrity
  (cross-cutting — "are we fooling ourselves?").
- **Portfolio's future role:** "what independent sources of return or risk
  information do we possess?" — Market State → Alpha Forecast → Expected
  Opportunity → Position Size → Execution Model → Risk Controls.
- **Data Acquisition Trigger** (replace "we aren't buying" with "data must earn
  its purchase"): buy only if (1) an existing discovery establishes a credible
  mechanism; (2) the missing variable is specifically required to test it; (3)
  expected information gain is high; (4) it can't be falsified with current
  data; (5) the likely edge justifies the cost; (6) the purchase resolves a
  defined decision.
- **Priority formula upgrade:** Research Priority = Expected Information Gain ×
  Edge Potential × **Testability** × **Strategic Reusability** ÷ **Research
  Cost**. A result that changes many future decisions outranks one that settles
  an obscure calendar effect.
- **Swing trading** is a separate research horizon, not a new philosophy — must
  fit the hours-to-days window; test "entry hypothesis + fixed exit
  architecture," never "entry → optimize 15 exits"; decompose entry / exit /
  sizing / regime so you can see which component carries the apparent alpha.
- **Integrity Gate structural blindness spec:** the Gate receives the frozen
  candidate, raw data outputs, predefined audit rules, research ledger, and
  benchmark results — and does NOT receive the Discovery narrative, the
  Mechanism agent's persuasion, the expected result, or the Director's
  recommendation. "Don't ask the skeptic to review the sales pitch."
- **Target architecture:** Market Observatory (state discovery) → Direction /
  Volatility / Structure states → Conditional Research → Alpha Discovery →
  Economic Validity Gate → Statistical → Director → Monetization → Integrity
  Gate → Validation/Holdout → Strategy Engineering (Entry / Sizing / Exit) →
  Paper Trading → Execution Data → Live Qualification → Capital. Execution data
  feeds back into research **without contaminating confirmation data.**
- **30–60 day plan, four workstreams:** (1) Discovery Engine v2 — highest
  priority; (2) State Engine — frozen market-state framework, measure signal
  availability / expected range / sizing implications / filtering /
  interaction with future candidates; (3) Execution Qualification — real-time
  paper trading of the frozen state/risk framework; (4) New Alpha Research —
  shift to mechanism → state → conditional behavior → monetization.
- **Priority order for the queue:** 1 Discovery Engine v2 · 2 state engine into
  paper trading · 3 mechanism/participant research · 4 conditional re-testing ·
  5 finish M23's Statistical stage (but don't let a 6E result distort the NQ
  mission) · 6 Tokyo companion (worth running because mechanically related, not
  because London makes it likelier) · 7 swing (bounded) · 8 data purchase: still no.
- **Philosophical reframe:** the goal is not "find an alpha signal" but "build a
  machine that can discover, validate, monetize, execute, and retire alpha." The
  next evolution is not another agent; it's turning the pieces into a
  closed-loop research operating system.

### R3 — the "research operating system" review (deepest on operations/governance)

- **Diagnosis in one line:** the bot is optimized to test individual ideas, not
  to produce, rank, combine, and operationalize candidates. Throughput is up;
  usable yield is not (11 closures → 1 useful, 2 real-but-unusable, 8 null).
- **Linear pipeline → evidence graph:** idea → test → pass/fail should become
  mechanism → state feature → entry context → risk/exit rule → portfolio
  behavior. A failed directional idea should not just disappear — it becomes a
  reusable negative constraint, a conditional-retest candidate, or evidence
  that a source channel is low-yield.
- **Separate facts, signals, and strategies** as three distinct object types,
  each with its own registry:
  - *Evidence/fact registry:* fact ID, definition, market, horizon, mechanism,
    statistical status, stability, expiry/review date, related facts.
  - *Hypothesis registry:* hypothesis ID, source channel, pre-registered claim,
    mechanism, test count, decision status, failure mode.
  - *Strategy registry:* strategy ID, linked fact/signal IDs, entry/exit rules,
    costs, exposure limits, paper-trading status, promotion history.
  Every strategy links backward to its facts/experiments; every conclusion links
  forward to the strategy tests it enables.
- **Seven bounded research families** (the multi-lens engine): session-transition
  structure · compression/expansion · event-mechanics (only where the instrument
  is tradeable) · cross-market confirmation (ES/NQ/RTY/VIX/VXN/rates/FX) ·
  regime-conditioned retests · exit research · execution-quality research.
  Rule: **one mechanism, one predeclared conditioning variable, one primary
  outcome, one frozen validation plan.** The correct M26 statement: "test whether
  the rejected level-sweep reversal has positive conditional expectancy
  specifically following prior-day range contraction, because compression
  plausibly concentrates the liquidity-release move."
- **Pre-test candidate quality score:** Q = 0.30·Mechanism + 0.25·Actionability +
  0.20·Testability + 0.15·Distinctiveness + 0.10·Reuse value; threshold Q ≥ 0.65
  for full pipeline entry; below that sits in a backlog. Would have flagged
  EIA/ECB as low-actionability before they consumed test slots.
- **Non-negotiable safeguards:** immutable holdout; full research ledger;
  family-level attempt accounting (a pass after 80 variants carries a much
  higher burden than after one); walk-forward validation for strategy
  prototypes; embargo/purging where labels overlap; cost realism as baseline;
  robustness/sensitivity tests; Deflated Sharpe Ratio + Probability of Backtest
  Overfitting reported at the family level.
- **Promotion requires agreement on seven things, not a p-value:** mechanism
  coherence; sample size and regime coverage; OOS stability; cost-adjusted
  expectancy; parameter robustness; low dependence on one date/print/trade;
  compatibility with a real execution spec. Automate as a release gate (cites
  the kill-check denominator and Monday-drop bugs as the reason).
- **Minimum viable paper strategy — state-conditioned breakout framework:**
  *State layer* (prior-day range contraction, overnight coil, VXN context,
  session eligibility) · *Trigger layer* — a simple pre-defined directional
  trigger (range break, opening-range break, failed-breakout reversal) that is
  **independent of the state facts** · *Risk layer* (fixed R ceiling, no
  averaging down, daily loss limit, max concurrent exposure, event avoidance) ·
  *Exit research layer* (fixed 1R/2R, time exit, vol-adjusted trailing stop,
  session-close exit) · *No-trade layer* (poor liquidity, high expected
  slippage, scheduled news, regime conflict). Explicit warning: **"predicts
  wider range" ≠ "predicts direction"** — some facts are worth more for sizing,
  tactic selection, exit timing, or declining trades than for long/short.
- **Six promotion stages:** research candidate → validated component → strategy
  prototype → shadow/paper → limited live → scaled live. "Scale behind evidence."
- **Research-control plane — persist per run:** hypothesis + mechanism; source
  channel + family; instrument, bar interval, exact dates; dataset version/hash
  + ingestion timestamp; code commit; parameters + seed; feature definitions +
  signal timestamps; cost model + execution assumptions; results, diagnostics,
  plots, raw trade list, decision; reviewer decision + reason; links to parent
  facts, related hypotheses, downstream strategies.
- **Seven separated roles** (even if one bot performs them serially with locked
  handoffs): source scout (must not promote its own idea); hypothesis designer
  (must not browse results for a favorable formulation); test engineer (must not
  alter the hypothesis after seeing output); skeptic/reviewer (must not change
  data/code without a recorded issue); strategy assembler (must not treat facts
  as automatic directional signals); paper-trade operator (must not override
  rules without a recorded reason); research director (must not rewrite
  evidence).
- **Weekly capacity allocation:** 40% mechanism-first structural research · 25%
  strategy assembly + exit research · 20% controlled conditional retests · 10%
  observatory/execution research · 5% literature/practitioner sourcing (kept
  alive, higher bar).
- **30/60/90 roadmap.** *Days 1–30:* build the three registries; add the Q-score
  and actionability check; freeze a family taxonomy and retro-tag every result;
  finish M23's Statistical stage; run M26 and M27 strictly as specified; build
  an automated pre-release test suite (calendar integrity, day-of-week coverage,
  symbol correctness, cost model, lookahead, concentration/one-print kill);
  weekly dashboard (sourced / tested / passed / actionable passes / strategies
  created / family yield / cost / open debt); write one full paper-trading spec.
  *Days 31–60:* launch the shadow engine (timestamp every signal, expected vs
  assumed fill, rule state, blocked trade, exception); formalize exit research;
  rolling walk-forward reports; family attempt-count + selection-bias flag;
  negative-knowledge library; test a bounded set of combinations (2–3 state
  filters × 1 trigger × 3 exits). *Days 61–90:* compare paper vs expected
  historical distribution; measure signal quality, fill realism, missed-trade
  rate, latency, slippage variance, override frequency; retire what can't run
  stably in real time; promote a small number to limited-live-eligible with a
  hard ceiling set beforehand; reallocate capacity by yield; formal checkpoint
  on whether the $20/month data cap is still the binding constraint.
- **Ten metrics that matter** (replace "hypotheses closed"): actionable-pass
  rate · strategy-conversion rate · paper-trade fidelity · research-family yield
  · reuse rate · time-to-decision · reproducibility rate · defect escape rate ·
  concentration risk · experiment debt.
- **Seven decisions for the 19th:** (1) approve the two-track mandate; (2) adopt
  fact → signal → strategy; (3) approve research-family quotas; (4) adopt the
  conditional-retest protocol; (5) choose the first paper prototype (likely the
  state-conditioned breakout); (6) define the swing-exit scope as a rule; (7)
  approve a minimum experiment ledger + automated release checks.

---

## 4. Where the reviews differ (real disagreements or different emphasis)

| Topic | R1 | R2 | R3 | Note |
|---|---|---|---|---|
| **What to paper-trade first** | A Risk Engine built from range forecasts (sizing/risk, no directional trigger) | A frozen State Engine (measure, don't assume profit) | A state-conditioned **breakout** with a separate directional trigger | R1/R2 say start with the risk/state layer alone; R3 wants a directional trigger attached from day one. This is a real fork — see §6, decision D3. |
| **Execution clock timing** | Un-park **now** | Workstream 3, parallel | Days 31–60 | R1 is the most aggressive. Tony's own records list execution-clock items 1a/1c as "Jason's call," so this is his decision either way. |
| **Šidák / multiplicity** | Says the current stacking is **wrong** (double-counts) and must be fixed | Says multiplicity is necessary but can't fix a wrong null — add the Economic Validity Gate | Says report DSR/PBO at the family level | R1 wants the bar changed; R2/R3 want a different gate added. Not contradictory, but R1's claim needs checking against the code before anyone acts on it. |
| **Swing exit — when to scope it** | After excursion data exists | Freeze the exit before any result is interpreted | Define it as a rule at the checkpoint | Not actually in conflict: freeze the *rule* now, calibrate its *parameters* only from excursion data once paper trading produces it. |
| **Goal/capital fit** | Flags $1,000/mo vs $300 budget vs $600–900/day swings | silent | silent | Only R1 raises it. It may be the most important practical point of the three. |
| **Agent structure** | silent | Four layers over the existing seven agents | Seven roles with "must not do alone" prohibitions | Compatible — R2 is the org chart, R3 is the job descriptions. |
| **Numbers** | "six confirmed vol facts, 137 tries" | "137 hypotheses" | "eleven closures" | Different counting windows, not a conflict. |

---

## 5. My own observations — what needs verifying or adjusting before acting

Candid, per your standing preference:

1. **R1's Šidák double-counting claim is plausible and must be checked, not
   assumed.** Tony's own log for the VXN family shows the blind Gate applying
   "Šidák cumulative" on Validation *after* a project-wide N_discovery
   correction at Statistical. If the Validation-stage correction is re-counting
   Discovery-stage trials against an already-independent out-of-sample sample,
   R1 is right and the bar is harder than it should be. But that's a
   **gating-rule change**, which is exactly what the September 19th freeze
   covers — so it should be diagnosed now (read-only, no rule change) and
   decided by you, not quietly fixed.
2. **R2 treats H118 as a completed failure. It isn't, yet.** H118 is in frozen
   forward validation (EXP047, 40 trades AND 12 months). The baseline-confusion
   lesson R2 draws from it is already recognized in the full scope and already
   changed how nulls are constructed (every scan since compares against the
   instrument's own unconditional drift — M22, M24, M25 all did). The Economic
   Validity Gate would still add real value (placebo, concentration, and
   alternative-explanation checks are NOT currently systematic), but it's less
   of a gap than R2 implies.
3. **R3's Q-score weights are made up.** The five dimensions are sound —
   especially Actionability, which would have correctly de-prioritized EIA/ECB —
   but 0.30/0.25/0.20/0.15/0.10 and the 0.65 threshold have no basis in Tony's
   data. Adopt the dimensions, calibrate the weights against the 137 closed
   hypotheses before trusting a cutoff.
4. **R3's citation list is partly noise** (a student-aid site and a bank
   regulator appear as "sources"). The underlying ideas — Deflated Sharpe Ratio,
   Probability of Backtest Overfitting, walk-forward — are standard and real
   (Bailey / López de Prado). Use the ideas; don't cite that list as authority.
5. **"Six confirmed volatility facts" depends on what you count.** At Holdout:
   midday-lull/afternoon-range and VXN-level/next-day-range (both KNOWN TRUE,
   separable). At Validation or Discovery-pass-but-no-path: range-contraction,
   overnight-coil, M20 (EIA/crude), M21 (ECB/euro), M23 (London-open/6E,
   Statistical stage still owed). The count is somewhere between four and seven
   depending on which stage you require. The argument doesn't change; the
   number in the checkpoint document should be precise.
6. **Most of what all three recommend is structural change — and therefore
   under the freeze.** Pulling the 19th forward means you can lift or scope the
   freeze now. Nothing below should be built until you do.
7. **Cost/usage reality.** R3's full roadmap (three registries, control plane,
   dashboard, shadow engine) is a multi-week build. R1's list (un-park the
   clock, Risk Engine from what's validated, three named conditional candidates)
   is achievable inside the existing 2-hour cadence. Sequencing matters more
   than completeness.

---

## 6. Decisions only you can make (the checkpoint, pulled forward)

| # | Decision | Options | What the reviews say | My recommendation |
|---|---|---|---|---|
| D1 | **Lift, extend, or scope the structural-change freeze** | Lift fully / lift for a named list / keep until the 19th | All three assume changes happen | Lift for a named list only — the items in D2–D6 — keep the rest frozen. |
| D2 | **Adopt the two-track mandate formally** | Yes / No | Unanimous | Yes — it's already the Sept 13th deliberation outcome; make it explicit in KNOWLEDGE.md. |
| D3 | **What to paper-trade first** | (a) Risk/State Engine alone — sizing, stop distance, trade permission, no directional trigger (R1, R2) · (b) State-conditioned breakout with a separate simple trigger (R3) | Split 2–1 | (a) first. It is the only thing Tony has actually validated. Adding an untested directional trigger reintroduces exactly the problem (direction = noise) the data keeps showing. Add a trigger only as its own pre-registered candidate. |
| D4 | **Un-park the execution clock** | Now (R1) / after the state engine exists (R2, R3) | R1 says now | Now, for the *measurement* part only (fill vs. reference, slippage, latency on the H118 path already frozen). Items 1a/1c were parked as your call; this is you making it. |
| D5 | **Šidák stacking** | Diagnose only / diagnose + fix | R1 says fix | Diagnose now under the freeze (read-only report); decide the fix after seeing whether it actually double-counts. |
| D6 | **Integrity Gate blindness** | Adopt the R2 spec (evidence in, narrative out) | Unanimous | Adopt. It's a packet-construction change, not a bar change; `integrity_blind_packet.py` already exists and can be tightened. |
| D7 | **Economic Validity Gate before Statistical** | Adopt R2's seven-question spec / adopt partially / defer | R2 strongly; R3 overlaps (placebo, concentration) | Adopt the parts Tony doesn't already do: placebo (shifted/inverted/random entry), concentration by year/regime/event, and the alternative-explanation checklist. The correct-null and vol-normalization parts are already in place since the baseline fix. |
| D8 | **Sourcing emphasis and channel quotas** | Adopt R3's 40/25/20/10/5 / adopt the direction without the numbers | R2, R3 | Adopt the direction (map/mechanism up, literature down with a higher bar); don't hard-code percentages yet — one week of evidence is too thin for quotas. |
| D9 | **Conditional-retest protocol as a written rule** | Adopt | Unanimous | Adopt R2's hard rule verbatim: reopen only via one pre-specified conditioning family whose variable comes from an established mechanism or validated state. M26 is the first instance and already complies. |
| D10 | **Swing trading exit** | Freeze the exit rule now as a family (fixed R / time / vol-trailing / session-close / state-conditioned) | Unanimous that it must be a rule before results | You still need to say which exit architecture you have in mind. Once you do, it's registered as its own family, and its parameters get calibrated from paper-trading excursion data — not from backtests. |
| D11 | **The goal/capital question** ($1,000/mo vs $300 budget vs $600–900/day per micro) | Restate the goal / raise the budget / accept a longer horizon | Only R1 raises it | Needs an honest answer before any "limited live" stage is even discussed. This is the one item none of the outside reviews resolved and Tony can't resolve for you. |
| D12 | **Data purchase** | Still no, with R2's six-condition trigger written down | Unanimous no | Adopt the trigger as the written rule so the answer stops being "no" and becomes "not until X." |

---

## 7. Proposed sequence (if you approve D1 with the named list)

Ordered by "achievable inside the existing cadence" first, big builds last.

**This week (inside 2-hour cycles, no new infrastructure):**
1. Diagnose the Šidák stacking (D5) — read-only report, no rule change.
2. Finish M23's Statistical stage (already owed; both R2 and R3 list it).
3. Run M26 and M27 exactly as frozen (M26 is the first sanctioned conditional
   retest; it's already scheduled for the 5:00 pm cycle).
4. Write the Integrity Gate blindness spec (D6) and the Economic Validity Gate
   additions (D7) as mechanism-doc-style pre-registrations — build later.
5. Register R1's three conditional candidates as pre-registered families with
   one condition each: fade-to-VWAP × compressed prior day; overnight-vs-intraday
   split; scheduled-event volatility as one family (EIA + ECB + any NQ-relevant
   release) — the last one finally gives M20/M21 somewhere to live.
6. Write the swing-exit family the moment you specify the rule (D10).

**Next 2–3 weeks (structural, needs the freeze lifted):**
7. Risk/State Engine spec (D3a): inputs = the validated range facts; outputs =
   expected range, sizing multiplier, stop distance, trade-permission flag.
   Frozen, versioned, no P&L claim.
8. Un-park execution-clock measurement (D4) on the existing H118 order path.
9. Fact / hypothesis / strategy registries (R3) — the hypothesis ledger already
   exists; the fact and strategy registries are the new pieces.
10. Family-level attempt accounting in `project_wide_multiplicity.py`.

**Weeks 4–8:**
11. Shadow/paper engine running the Risk/State Engine on live sessions, logging
    every signal, blocked trade, and exception.
12. First metrics dashboard using R3's ten metrics (actionable-pass rate,
    strategy-conversion rate, fidelity, family yield, etc.) — replaces
    "hypotheses closed" as the progress number.
13. Day-60 review: does anything justify revisiting the $20/month data cap
    under the R2 trigger?

---

## 8. One-paragraph version for the record

Three independent outside reviews reached the same verdict: continue, don't
pivot, and stop treating Tony's validated volatility facts as consolation
prizes. Tony's validation discipline is the asset; its discovery front-end is the
bottleneck. The fix is not more tests but better questions — pre-registered
families of conditional questions built on the market states Tony has already
proven — plus a parallel track that turns those proven states into a frozen
risk/sizing engine and starts measuring real execution. Everything material is a
structural change and sits under the freeze until Jason lifts it. Two things the
outside reviews left for Jason alone: which exit architecture he means by
"swing trading with a particular exit," and whether a $1,000/month goal is
compatible with a $300 budget on an instrument that moves $600–900 a day per
micro contract.
