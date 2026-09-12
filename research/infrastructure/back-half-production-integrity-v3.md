# Back-Half Architecture + Production Integrity Layer (v3)

Frozen 2026-09-10, on Jason's direction after an independent review of the
methodology's back half. Extends agent-governance-structure.md (v2), which
governs everything up to promotion and is UNCHANGED by this document.

## Why this exists

v2 made the front half rigorous: find something real, prove it's real,
prove it's monetizable. It treated PROMOTION as the point a candidate
clears the research bar. But the project's actual objective is an
automated profitable system, and promotion is not the finish line.

The core risk this document exists to prevent: **the standard must not
weaken once we finally have something that works.** The front half spent
123 hypotheses learning not to retune after a null result. That principle
has to survive promotion, not stop at it.

## The two ladders

FRONT HALF (v2, unchanged):
  behavior discovered -> behavior qualified -> monetization hypothesis ->
  frozen strategy -> formal validation -> PROMOTION

BACK HALF (this document):
  1. Research-Validated
  2. Statistical Forward Test
  3. Execution-Qualified (real paper trading)
  4. Live-Authorized
  5. Live-Monitored
  6. Retained / Restricted / Suspended / Retired

CRITICAL DISTINCTION, easy to conflate and expensive to get wrong:
- A STATISTICAL FORWARD TEST asks: does the signal still produce the
  validated distribution on data that did not exist when we froze it?
- EXECUTION QUALIFICATION asks: does our IMPLEMENTATION actually capture
  what the research says, once it meets real orders, fills, spreads,
  latency and operational failure?
These are different questions requiring different evidence. Passing one
does not pass the other. H118 is currently in stage 2 ONLY -- it has never
touched an execution path, because no execution infrastructure exists.

---

## THE PRODUCTION INTEGRITY LAYER (cross-cutting, stages 2-6)

Answers one question: "Is the strategy behaving the way the validated
research says it should?" It DIAGNOSES and AUTHORIZES. **It never
optimizes.** Improvement is a new hypothesis and goes back to the front
half as a new candidate, at the back of the queue, under the 2-attempt
limit. Four monitors:

1. SIGNAL INTEGRITY -- are the exact signals being generated per the
   frozen rules? Missed signals, duplicate signals, wrong timing, wrong
   bar reference, look-ahead creeping in via a live data feed.
2. EXECUTION INTEGRITY -- are orders entered, filled, sized and exited as
   specified? Realized slippage vs. modeled. Partial fills. Rejects.
3. STATISTICAL INTEGRITY -- is observed performance still compatible with
   the validated distribution? Not "is it profitable" -- is it *consistent
   with what we claimed*, which a losing streak inside expected variance
   still is.
4. REGIME / DRIFT -- has the environment changed enough that the original
   evidence may no longer apply?

## THE ANTI-OPTIMIZATION RULE (the single most important rule here)

The paper-trading period must not become another optimization period.

Forbidden, always, by any agent or automated process:
- "It produces fewer trades than expected, loosen the filter."  -> NEW HYPOTHESIS.
- "It lost three in a row, adjust the stop."                    -> NEW HYPOTHESIS.
- "The regime changed, let's adapt the parameters."             -> NEW HYPOTHESIS.
A frozen strategy is frozen. The ONLY permitted responses to disappointing
behavior are the predefined ones in stage 6: retain, restrict, suspend, or
retire. Anything else is a new candidate entering the front half.

---

## STAGE SPECIFICATIONS

### Stage 1 — RESEARCH-VALIDATED
Purpose: historical evidence says the strategy deserves consideration.
Agent: front half (v2), Integrity Gate signs off.
Inputs: Discovery + Validation + Holdout results, frozen spec.
Frozen criteria: 90% CI above zero at each stage, >= 0.05R, one
  pre-registered prospective test, Integrity Gate PASS.
Pass/fail: PASS -> stage 2. FAIL -> REJECTED, LEARN.
Allowed: freeze the forward-test spec.
Prohibited: any change to the strategy definition.
Escalation: Integrity Gate veto is final.

### Stage 2 — STATISTICAL FORWARD TEST  (H118 is here)
Purpose: does the signal still produce the validated distribution on data
  that did not exist at freeze time?
Agent: Paper Trading Monitor (mechanical); Statistical Monitor at review.
Inputs: frozen spec, live-forward price data, forward log.
Frozen criteria: pre-registered review point, ONE look, no interim peeking.
  H118: 40 resolved trades AND 12 calendar months, whichever later, CI on
  block-bootstrapped 10-day blocks. Pre-registered and NEVER moved.
Pass/fail: at the review point only.
Allowed: exactly two writes -- append a new signal, fill exit fields when
  the horizon elapses.
Prohibited: editing entries, deleting rows, recomputing closed rows,
  changing the definition or the review point, promoting early on a good
  run, any automated-session re-analysis (see v2 scope boundary).
Escalation: integrity problems -> flag to Jason, stop.

### Stage 3 — EXECUTION-QUALIFIED  (nothing has ever reached this)
Purpose: prove the IMPLEMENTATION captures the researched edge under real
  market contact. NOT "does it make money" -- that was stage 1-2's job.
Agent: Execution/Operational Monitor.
Inputs: live signal generation, real order placement (simulated or broker
  paper account), fills, timestamps, spreads.
Frozen criteria (set BEFORE the stage starts, per strategy): signal-match
  rate vs. the frozen rules; zero missed/duplicate signals; realized
  slippage within the modeled assumption; entry/exit timing within
  tolerance; realized trade distribution consistent with research
  distribution; no unhandled operational failures.
Pass/fail: all criteria met over a pre-registered sample -> stage 4.
Allowed: fixing IMPLEMENTATION BUGS (code that fails to execute the frozen
  spec correctly) -- this is repair, not optimization, and must be logged
  with before/after evidence.
Prohibited: changing the SPEC to match what the implementation happens to
  do. If implementation cannot capture the researched edge, the finding is
  that the edge is not executable -- a valid, honest, successful outcome.
Escalation: any spec/implementation conflict -> Research Director +
  Integrity, never resolved silently in code.

### Stage 4 — LIVE-AUTHORIZED
Purpose: permit real capital.
Agent: JASON ONLY. Not the Research Director, not Integrity, not any
  automated process. Standing rule, unchanged and non-delegable.
Inputs: stage 2 verdict, stage 3 verdict, position-sizing decision,
  written STOP/SUSPEND conditions (below).
Frozen criteria: stages 2 and 3 both passed; kill criteria written and
  frozen BEFORE authorization; sizing explicitly decided (not inherited
  from the 1-MNQ reporting convention).
Pass/fail: Jason's explicit decision. No statistical result authorizes
  capital on its own, ever.
Prohibited: proceeding on a strong result alone; automated authorization.

### Stage 5 — LIVE-MONITORED
Purpose: continuously determine whether the evidence still supports
  believing the edge is real. Live is not "turned on and forgotten."
Agent: Production Integrity Layer (all four monitors), reporting to
  Research Director + Integrity.
Frozen criteria: the stop/suspend conditions frozen at stage 4.
Allowed: reporting, diagnosis, and triggering a stage-6 response.
Prohibited: optimizing, adjusting, or "adapting" anything live.

### Stage 6 — RETAINED / RESTRICTED / SUSPENDED / RETIRED
Purpose: a predetermined response to deviation, decided before it happens.
Agent: Research Director + Integrity propose; Jason decides anything that
  changes capital exposure.
Responses: RETAIN (behavior within expectation) / RESTRICT (reduce size or
  narrow conditions -- note: narrowing conditions is a capital decision,
  NOT a strategy edit) / SUSPEND (stop trading, keep monitoring, go
  research the cause as a NEW candidate) / RETIRE (close, move to LEARN).
Prohibited: fixing the strategy in place.

---

## STOP / SUSPEND CONDITIONS (categories — thresholds derived per strategy,
## frozen before live authorization, never invented after the fact)

- Execution behavior materially violates the frozen specification
- Realized slippage exceeds the modeled assumption
- Signal generation diverges from the frozen implementation
- Sufficient live sample accumulates that is statistically incompatible
  with the validated distribution
- Drawdown exceeds a predefined research-derived boundary
- Market structure changes in a way that invalidates the mechanism
- Data feed or infrastructure integrity failure

Principle: decide what would make us stop BEFORE we know whether we will
need to stop. Same frozen-rule philosophy as the front half.

## Post-promotion agent flow

  PROMOTION -> Paper Trading Monitor -> Execution/Operational Monitor ->
  Statistical Monitor -> RESEARCH DIRECTOR -> Live Authorization (Jason) /
  Hold / Suspend -> Live Monitor -> Research Director + Integrity

The Research Director stays involved after a strategy is born. The failure
mode this prevents: the research team being rigorous right up to promotion
and then handing the strategy to an execution script.

## Known gap on adopting this (2026-09-10)

No execution infrastructure exists (scoped, never built -- IBKR native API
or Tradovate webhook, ~$60-115/mo). Stage 3 therefore cannot run for any
strategy today. H118 can complete stage 2 and still not be live-ready.
Building it crosses the $5 threshold and requires Jason's sign-off.

---

# AMENDMENT v3.1 — 2026-09-10 (Jason's decision after second review)

Supersedes the noted parts of v3 above. v3's philosophy, ladder and
Production Integrity Layer are otherwise unchanged.

## 1. TERMINOLOGY — binding, stop conflating these three

- **Prospective Statistical Forward Test** — the frozen strategy evaluated
  on unseen data as it arrives. Purpose: statistical validation. This is
  what H118 is in now, computed from daily bars by a script. It is NOT
  paper trading and must never be called that again. Stage 2's real name.
- **Paper Trading** — the frozen strategy running in REAL TIME through an
  actual signal engine and order path against simulated execution.
  Purpose: execution and operational qualification. Stage 3's real name.
  Nothing has ever reached this.
- **Live Trading** — real capital, under capital-protection controls.

Rationale: without this separation the project can convince itself it has
tested something it has not.

## 2. TWO CLOCKS, RUN IN PARALLEL — start the execution clock NOW

RESEARCH CLOCK (unchanged, frozen, do not touch):
  H118 -> prospective statistical forward test -> 40 resolved trades AND
  12 calendar months -> one statistical evaluation -> promotion decision.

EXECUTION CLOCK (starts immediately, independent):
  H118 frozen spec -> signal engine -> paper broker/orders -> fills,
  slippage, latency -> operational testing -> execution qualification.

They meet at the Live Authorization gate. Do NOT wait for the research
clock to finish before building the machinery -- that is how a project
discovers it needs several more months right when it thought it was done.

CRITICAL: the execution build must never become part of H118's research
test. H118 stays frozen. If the implementation cannot execute the frozen
spec, that is a finding about executability, never a reason to change the
spec (which would be a new hypothesis, back of the front-half queue).

## 3. STAGE 3 IS EVIDENCE-BASED, NOT CALENDAR-BASED — MODIFIES v3

Rigorous does not mean slow. Stage 3 concludes when a pre-registered
MINIMUM EXECUTION-VALIDATION SAMPLE is collected and every check passes --
not when a calendar interval elapses. Set the minimum sample BEFORE
starting. A high-frequency strategy may qualify in days; a sparse one
takes longer. Collect the minimum evidence necessary, then decide.

Be aggressive about removing wasted calendar time. Never aggressive about
reducing required evidence. Those are different, and only the first is
allowed.

## 4. THE 14 EXECUTION CHECKS (stage 3 pass criteria)

1. Signal occurs when the spec says it should
2. Signal occurs exactly once when it should
3. Correct order is generated
4. Correct quantity is generated
5. Entry/exit instructions are correct
6. Orders reach the broker
7. Fills are recorded
8. Expected vs. actual fill is measured
9. Slippage is MEASURED, not assumed
10. Latency is measured
11. Rejected / missed / duplicate orders are detected
12. Position state is reconciled
13. A system failure cannot silently leave an unintended position open
14. Everything is logged for later reconstruction

## 5. BUILD SCOPE — deliberately minimal

Build the minimum execution-validation layer needed to answer whether H118
can be executed as specified. Explicitly NOT: architecture for ten
strategies, portfolio optimization, dashboards, or an institutional-grade
production environment. Approved on the basis that this is now RESEARCH
INFRASTRUCTURE (a prerequisite to answering "can this be executed
profitably"), not speculative trading expenditure.

## 6. KILL POLICY — the two kills are different things

STATISTICAL KILL ("did our research hypothesis stop looking good?"):
  NOT PERMITTED during a predetermined forward-validation period. H118 is
  not killed, shortened, or modified on interim statistical performance.

EXECUTION / CAPITAL-PROTECTION KILL ("is the machine doing something other
than what we authorized?"):
  PERMITTED and REQUIRED once an executable system exists and especially
  once live. Protecting the purity of the experiment at the expense of the
  trading account is the wrong trade.

## 7. REVISED BACK-HALF FLOW

  behavior discovered -> behavior qualified -> monetization hypothesis ->
  frozen strategy -> formal statistical validation -> PROSPECTIVE
  STATISTICAL FORWARD TEST -> promotion decision -> REAL-TIME PAPER
  TRADING / EXECUTION QUALIFICATION -> live authorization review -> live
  trading -> continuous production monitoring -> Research Director review

Execution qualification runs in PARALLEL with the statistical forward test.

## 8. Governing philosophy (unchanged, extended)

Does the behavior exist? -> Can we monetize it? -> Does it survive unseen
data? -> Can we execute it correctly? -> Does execution preserve the
economics? -> Can we safely authorize capital? -> Does it keep working once
capital is deployed?

---

# AMENDMENT v3.2 -- capital-protection rules, Live-Limited (stage 3.5), broker

Frozen September 11th, 2026, from the Upgrade Brief (docs/TONY_UPGRADE_BRIEF.md),
Jason's direction decisions binding. Nothing in v3 / v3.1 is repealed.

## Jason's direction (Section 1 of the brief)

Money goal $1,000/month, $12,000 in the first 12 months; start small and
scale. Scale = whatever size and trade count the edge supports. Early
live: YES, tiny size, once execution qualification passes and BEFORE the
statistical review point ends. Starting risk budget $300, reserved for a
short-horizon edge (per-trade swing $50-150 per micro); up to $500 only
after a fast, measured paper record (20+ trades, slippage measured,
positive net) -- never on a backtest. H118 is NOT funded for early live:
its risk unit (~$700 per MNQ, +/-$1,000-1,400 per 10-day trade) would
consume $300 as noise within two or three positions; any H118 live
decision needs its own budget (~$2,000-3,000) and is Jason's call then.
Trailing loss: once profitable, give back about one-third of peak
profit (provisional).

## Capital-protection rules -- in code, checked before every order

src/capital_protection.py (tests/test_capital_protection.py). Frozen
config: starting budget $300 -> $500 after the paper record; trailing
kill at max(-$300, peak - max($300, peak/3)); slippage kill when the mean
fill deviation over the last 20 fills exceeds 25% of the working edge;
signal-divergence halt, zero tolerance, flag Jason; per-trade catastrophe
stop 2R (2 x entry-day ATR14) plus a daily loss cap of half the remaining
budget; position / order caps; fail-closed on any missing input.

These are ACCOUNT controls. Every trigger is logged as an execution-spec
divergence from the research spec. More than two catastrophe triggers in
40 trades is a finding about the strategy's tail -- reported, never
tuned. Statistical kills remain PROHIBITED during any forward-validation
window; execution / capital kills are REQUIRED from the first live order.

Integrity Gate ruling (adoption meeting): the execution-side catastrophe
stop is ADMISSIBLE under the scope boundary because it lives in the
execution spec and is logged as divergence; it is never applied to the
research record and never changes a frozen strategy's exit rule.

## Stage 3.5 -- LIVE-LIMITED

Inserted between 3 Execution-Qualified and 4 Live-Authorized. Applies to
the first SHORT-HORIZON candidate to reach it; H118 is not eligible at
the current budget.

- ENTRY: all 14 execution checks pass on paper with a pre-registered
  minimum sample -- 20 paper trades, slippage measured. Size: minimum
  contract. Governed entirely by the capital-protection rules above.
- The research clock is untouched: no statistical read, no status change,
  no interim peek. Live-Limited P&L is an EXECUTION record, not evidence
  about the hypothesis.
- Authorization remains Jason's alone. The change is that it may come
  BEFORE the statistical review point closes -- not that it is delegated.
- ENDS only by: a capital-protection kill, the statistical review point
  (then the normal promotion decision), or Jason.

## Broker and execution stack (UPGRADE 8)

Start on Tradovate paper for stage 3 (free paper accounts, native
TradingView integration, low MNQ commissions, webhook/API path -- verify
the current API access fee before committing). Interactive Brokers is the
more serious long-term home; move there if Tradovate's API limits bite.
Jason opens the paper account. The $60-115/mo execution-stack line
approved 2026-09-10 is separate from the $20 data cap; Jason to confirm
that approval stands under the new budget framing (open item, parked on
him with a 48-hour clock per the reporting rule).

## Status

Frozen. Code and tests on disk. Nothing live exists; no strategy is at
stage 3. The first candidate to enter stage 3 will be a map-anchored
short-horizon candidate, not H118.
