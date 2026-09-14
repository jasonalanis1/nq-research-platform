# Tony — Full Scope

**Version: September 14th, 2026 (v3).** Supersedes `FULL_SCOPE_2026-09-13.md`.

Audited against the complete change log since the prior version was committed
(commit `7614ad7`, September 13th 8:50 pm CT): 27 commits, 46 files added, 14
core files modified. Every rule, tool, form, registry, metric and parked decision
that changed is listed in Section 14, not only the headline ones.

---

# Why this document exists

So you can read the whole system in one sitting without asking anyone, and so
that anyone else — an advisor, a reviewer, a future version of me — can tell in
an hour what this project believes, what it has proven, what it has failed at,
and what it refuses to do.

It is also a control on me. A system that reports on itself will drift toward
flattering itself. Writing the state down in full, dated, superseding the last
version, with the failures listed beside the wins, makes drift visible.

---

# 1. The vision

A systematic trading bot for Nasdaq-100 futures (NQ) that trades on evidence,
not opinion — where every rule it follows survived a test designed to kill it,
and where the process of finding those rules is automated enough to run without
supervision.

The bot is the product. The research platform is how the product gets built. When
those two compete for a cycle's time, **the bot wins** — `docs/BOT_ROADMAP.md`
outranks the research queue.

---

# 2. The central belief — everything follows from this

**It is much easier to fool yourself than to find an edge.**

Nearly every rule here exists to make self-deception expensive: pre-registration,
frozen scopes, sealed data, blind review, multiplicity penalties, mandatory
baselines, one shot per candidate. The project treats a beautiful result as a
suspect until it has survived an attempt to kill it.

The clearest proof this belief is correct is H118 — described in Section 5 — a
signal that passed all three validation stages and turned out to be the stock
market going up.

---

# 3. The honest current state

**155 hypotheses tested. 141 rejected. 2 survivors. Zero directional edges.**

| | |
|---|---|
| Distinct hypotheses | 155 |
| Rejected | 141 |
| Survivors (Holdout passed) | 2 — both **magnitude**, not direction |
| Registered trials, project-wide | 468 |
| Trials since the last survivor | 159 |
| Trials per survivor | 234 |
| Test suite | 446 passing |
| Operational checks | 13, all green |

**The two survivors:**
1. High implied volatility (VXN) relative to its own trailing level → a wider
   next session.
2. A quiet midday → an expanded afternoon.

**A third is advancing:** a wide opening 30 minutes → a wider midday
(hyp-000162). It passed its statistical stage including the project-wide
multiplicity correction, then passed separability against every fact above. It
is a magnitude fact too.

**The bot:** milestones B0–B6 complete, B7 live in a thin first version. It has
**never filled a single order.** Not once. The entire execution half is built,
tested, and unexercised, blocked on price data that ends September 8th.

**The gap that defines the project right now:** the bot cannot go live without a
directional entry signal, and the idea queue contains **zero of nineteen**
candidate families that are about direction. Every one is about magnitude. This
is structural, not an oversight — the queue ranks by strength, volatility is
predictable and direction is not, so magnitude wins every ranking on merit. The
engine will keep producing better sizing inputs indefinitely while the entry slot
stays empty.

---

# 4. How it all fits together — one loop

This is the whole system as a single circuit. Every tool in Sections 6–10 sits at
one of these stations.

```
  ① LOOK ............ Idea Factory / Observatory / the shelf
       |
       v
  ② EXPLAIN ......... mechanism doc, written BEFORE the scan
       |
       v
  ③ TEST ............ scan > statistical > director >
       |              blind gate > validation > holdout
       |
       +----------------------------+
       |                            |
       v                            v
  ④a FAILURE                   ④b SURVIVOR
     -> NEGATIVE KNOWLEDGE         -> FACT REGISTRY
        (closure form,                  |
         failure-mode taxonomy)         v
       |                        ⑤ THE BOT
       |                           B0 contract > B1 signal >
       |                           B2 risk/state > B3 entry >
       |                           B4 order path > B5 measurement >
       |                           B6 kill switches > B7 paper run >
       |                           B8 live-limited > B9 scale
       |                            |
       |                            v
       |                        ⑥ EXECUTION DATA
       |                           fills, slippage, latency
       |                            |
       +<---------------------------+
         both feed back to ① — and NEITHER is ever
         allowed to touch the sealed Validation or
         Holdout slices
```

**① Look.** The Idea Factory crosses every market state on disk against every
session window and a five-outcome battery, on the Discovery slice only, and
ranks what it finds. It is **descriptive and never a result** — a queue entry is
a candidate for a mechanism document, nothing more. Every cell it looked at is
counted, because looking has a cost that must be paid later.

**② Explain.** Before any test runs, a mechanism document is written: what the
claim is, **who is on the other side of the trade and why they are there**, why
this is not curve-fitting, what would falsify it, and the frozen scope of the one
scan allowed. "It filters out losers" is rejected as fitting. No mechanism, no
test — enforced mechanically by `ops_checks`.

**③ Test.** One shot, frozen scope, hashed before data is touched. The candidate
then walks the stages: Discovery scan → Statistical (four questions, power,
multiplicity) → Director Re-Evaluation (*is it NEW*, not is it real) →
Monetization → blind Integrity Gate → one-shot Validation → Holdout (requires
Jason). A mechanical integrity suite runs before the Gate on every candidate.

**④ Both outcomes are kept.** A failure is written up in a closure form with a
classified failure mode and becomes **negative knowledge** — it is the reason the
next cycle doesn't retry it, and it feeds back to ① to shape what gets looked at.
A survivor enters the **fact registry** and becomes available to the bot. Roughly
9 out of 10 candidates die here, and that is the system working.

**⑤ The bot.** Validated facts become bot components. The Risk/State Engine (B2)
turns volatility facts into a daily decision — how big, how far, whether at all.
It never answers *which way*. The entry (B3) is currently an acknowledged
placeholder because no directional fact exists to put there.

**⑥ Execution data feeds back — and stops at a wall.** Fills, slippage, latency
and reconciliation flow back to improve execution, sizing and cost assumptions.
They **never** touch the sealed Validation or Holdout slices. The research data
and the execution data are separate circuits that meet only at the bot. This is
the "two clocks rule" (Section 8) made physical.

**What makes it a loop and not a pipeline:** negative knowledge steers the next
look, and execution reality steers the sizing layer, so the system's search gets
narrower and its execution gets more honest over time — without either being
allowed to contaminate the sealed evidence.

---

# 5. How the research is structured

## Data is split by time, and the split is sacred

| Slice | Period | Use |
|---|---|---|
| **Discovery** | 2015 → Oct 2021, 2,101 sessions | All searching. Everything exploratory happens here. |
| **Validation** | Oct 2021 → Jan 2024, 700 sessions | One-shot confirmation of a frozen spec. |
| **Holdout** | Sealed | Requires Jason's explicit sign-off. Opened 3 times, ever. |

A candidate that touches Validation gets **one** attempt. The spec is hashed
before the data is read. Re-running with a changed definition is a different
trial and is counted as one.

## The promotion bar — all four required

1. Statistically credible on its own terms (90% CI excluding the correct null).
2. Survives the **project-wide multiplicity correction** for how many things have
   been looked at.
3. Survives the **blind Integrity Gate**.
4. **Separable** — it is not a restatement of a fact the project already owns.

## The two nulls — the rule that killed H118

Every result must be measured against the **correct** null, not zero:

- A directional claim is measured against **the instrument's own drift over the
  same horizon**, with a block bootstrap because overlapping windows are not
  independent.
- A magnitude claim is measured against **the unconditional range**, not against
  no-change.

**H118** was the project's most important failure. Buy after price closes far
below its session VWAP, hold 10 days. It passed Discovery, Validation *and*
Holdout — the project's first apparent real edge. A late baseline diagnostic
asked whether it beat NQ's own 10-day drift. It does not: +0.12 with a CI of
(−0.26, +0.49) on Discovery, +0.05 with (−0.59, +0.66) on Validation. Neither
clears zero. **It made money in backtest because the index rose.** Rejected
September 12th, retained as failure mode #7, no promotion path, and its
forward log now runs for information only.

This is the single most valuable thing the project has produced: the proof that
three stages of validation can all pass and still be wrong if the baseline is
wrong.

## Scarce resources, enforced

Holdout slots (5 total, 3 spent), Validation attempts (one per candidate, two per
family), conditional-stack attempts (two powered nulls closes the format — one
spent), and the data budget (~$20/month, largely unspent).

---

# 6. How we research — the front half

## Where ideas come from — the Idea Factory

Two modes, both descriptive, both on Discovery only, both spending no hypothesis
ID and registering no scan:

- **Single-state mode.** Every market state × every session window × five
  outcomes (move, range, MFE, MAE, time-to-extreme). Ranked by |z|.
- **Interaction mode (`--interactions`, new September 14th).** Every *pair* of
  states, cross-tabbed. See Section 14 for what it found.

**The timing rule** is what makes this legitimate rather than fishing. Every
state carries the moment its value is actually known, and may only be crossed
with an outcome window starting at or after that moment. In interaction mode the
rule applies to **both** layers — a pairing is only as legitimate as its
worst-timed layer. The engine's first run produced a spectacular top result
(distance-from-VWAP → same-session move, z = −20.4) that was pure circularity;
the rule now drops that and hundreds like it before ranking.

**Every cell looked at is counted** and the count is carried into any spec
sourced from the table, so the multiplicity of the look is paid for rather than
forgotten.

## Two hypothesis formats

- **Flat** — one state, one window, one outcome.
- **Conditional stack** — context → location → trigger, adopted September 13th
  with ten binding rules. The first test is always **paired** (trigger alone vs
  trigger inside the context), because a stack passing on its own tells you
  nothing about whether the context did any work. A paired family is two trials,
  not one.

**Stack A**, the format's first and only result: the expected-range context known
at the prior close does **not** change what an opening-range break does next.
Difference +0.0247R, CI90 (−0.0496, +0.0976), n = 566/977 against a floor of
100 — a **powered null**, not a thin one. hyp-000161 rejected. One of the
format's two permitted nulls is spent.

Its consequence is doctrine: the Risk/State Engine is a **sizing and permission**
layer, not an entry filter.

## The shelf — why we don't draw thin

Ideas are sourced continuously from five channels (map, literature, practitioner,
observatory, gut — each recorded so hit rates accumulate). The shelf counts only
entries that are genuinely drawable: written up, mechanism doc done, resurrection
ruling signed, data on disk. Floor of 3. **Below the floor the owed action is
more sourcing, never a thin draw.** Draw order is information gain × edge
potential, not age.

## What we've concluded about where the edge isn't

87 of the 141 rejected hypotheses were directional, covering essentially the
entire classical intraday playbook: gap fades (9+ variants), opening-range and
initial-balance breakouts, level-sweep reversals, VWAP mean reversion, momentum
and continuation, trend following, multi-timeframe alignment, cross-asset
lead-lag (bonds, oil, currencies), event drift (FOMC, NFP, CPI), reference-level
fades, round numbers, and multi-day drift conditioned on a state.

**All null.** That is real negative knowledge, and it is the strongest thing the
project can hand an outside advisor.

---

# 7. The bot — the product roadmap

| # | Component | Status |
|---|---|---|
| B0 | Signal contract | **DONE** |
| B1 | Signal engine | **DONE** for B3 |
| B2 | Risk/State Engine | **BUILT** — sizing + permission only (Stack A proved it is not an entry filter) |
| B3 | Base entry, frozen | **DONE** — an acknowledged **placeholder**, never an edge, its P&L is never evidence |
| B4a | Order path (simulated) | **DONE** — contract, deliberately hostile broker, full state machine |
| B4b | Order path (real broker) | **BLOCKED ON JASON** — IBKR futures permission in a 30-day cooldown (~Oct 13th) |
| B5 | Execution measurement | **FIRST CUT DONE** — the 14 frozen checks, reports INSUFFICIENT SAMPLE honestly |
| B6 | Kill switches | **WIRED** — called before every order, fail-closed |
| B7 | Continuous paper run | **LIVE (thin)** — **blocked on data**, zero fills ever |
| B8 | Live-Limited | **MISSING** — Jason's authorization alone, non-delegable |
| B9 | Scale behind evidence | **MISSING** |

**B4a's design principle worth naming:** the simulated broker is *deliberately
hostile*. It rejects, partially fills, disconnects mid-order and returns late
acknowledgements, on command or at a seeded rate. An order path written only
against a broker that behaves is a path whose failure modes were never exercised.
Crash recovery is proven by a test that leaves an unresolved order on disk and
confirms a fresh process recovers it from the broker's own authoritative state.

**B6 is fail-closed and proven on real data.** On September 8th a real signal
fired, the Risk/State Engine permitted it, and capital protection **blocked** it
— the per-trade swing was $468 against a $50–150 band. That is the gate working
outside a test file for the first time.

---

# 8. How we prove we can execute it — the back half

Fourteen frozen execution checks, measured not assumed: signal timing,
exactly-once firing, order correctness, quantity, entry/exit instructions, orders
reaching the broker, fills recorded, expected-vs-actual price, **slippage
measured not assumed**, latency, rejects and duplicates, position reconciliation,
no orphan positions after a crash, and everything logged for reconstruction.

**The two clocks rule, binding.** A *statistical* forward test (does the signal
behave as expected on unseen days) and an *execution* qualification (does the
implementation capture it under real orders, fills, slippage and latency) are
different questions with different evidence. They are never conflated and never
compared against each other. The rule is made physical by two separate log files:
`bot_stack_forward_log.jsonl` (statistical) and `bot_stack_paper_log.jsonl`
(execution). The file split *is* the rule.

**Honest about what it cannot see:** every check reports its own sample size and
returns INSUFFICIENT SAMPLE rather than a false pass. At N=0 it says so. A green
from a check that never ran is worse than no check at all.

---

# 9. The agents — how the work is done and reviewed

Ten roles, each with a defined job and the standing obligation to report
RAN / NOT RUN with a reason every cycle: Operations, Director, Mechanism,
Discovery, Statistical, Integrity Gate, Validation, Monetization, Portfolio,
LEARN.

**The Director's question is "is it NEW", not "is it real."** Statistical answers
the latter. The Director residualizes a candidate against every fact the project
already owns and reports the share retained against a 50% bar. Precedents: H116
retained 98% and advanced; hyp-000140 retained 32% and the Director ruled *real
is not new*.

**The Integrity Gate runs blind.** It receives the frozen spec and the raw cell
outputs — not the narrative sections of the mechanism doc, not the expected
result, not the Director's recommendation. A test asserts the packet contains no
line from the narrative sections.

**The Gate now has a mechanical half** (new, Section 14): seven checks that run
on every candidate before the blind review, green/red, no judgment. A red is a
*blocking finding for the Gate*, never an automatic close.

---

# 10. How we learn — and how we guard against fake work

Every closed hypothesis gets a closure form with a classified failure mode.
Failure modes are named and reusable; #7 is the H118 mode — *beat the wrong
baseline*.

**Named shapes of manufactured work, each with a guard:**

- *Busy work* — cycles that produce artifacts but move no candidate. Guard: an
  operational check that fails when three consecutive cycles move no ledger row,
  scan, document or inventory entry. **It fired today** and is described in
  Section 14.
- *Reassuring reports* — a role that files a comforting summary instead of doing
  work. Guard: the checks are mechanical code, not an agent's judgment.
- *Retuning after a result* — guard: hashed frozen scopes, one shot.
- *Restatement as discovery* — guard: the Director's separability stage.
- *A queue that looks healthy but feeds nothing* — guard: new September 14th, the
  Idea Factory must report its split by job with the direction count stated even
  when it is zero.

---

# 11. Rules that never bend

- Never fabricate data. Ever.
- The Holdout is sealed. Only Jason opens it.
- A frozen strategy is never retuned. Disappointing behaviour permits retain,
  restrict, suspend or retire — never a live edit.
- The placeholder entry is never a strategy, never an edge, and its P&L is never
  evidence.
- The Idea Factory queue is descriptive and never a result.
- One stack = one trial; a paired family = two.
- Below the shelf floor, source more — never draw thin.
- **B8 live authorization is Jason's alone and is non-delegable.**
- No statistical result authorizes capital by itself.
- Nothing touches H118 or EXP047 without Jason.
- An automated cycle never edits a forward-validation evidence log on its own
  initiative — not even to correct a known error.

---

# 12. Autonomy — what runs without me and what doesn't

Cycles run every two hours on the odd Central hour, **pre-booked as independent
one-shots** (changed today — see Section 14). Each cycle:

1. **Preflight** — one command: lock, budget clock, pipeline sweep, both daily
   checkers, shelf/sourcing position. Writes a receipt.
2. **Ordering principle** — advance the lowest incomplete bot milestone that can
   actually move; if none can, say which is blocked and why, then fall through to
   research.
3. **The work item.**
4. **Close-out** — one command: tests, operational checks, commit *and push*
   verified, lock released, preflight receipt verified as this cycle's. Writes
   one compliance row.

**Runs unattended:** everything through Validation, including spending a
Validation attempt.

**Requires Jason:** opening the Holdout, authorizing live capital, buying data,
and any decision about frozen evidence.

---

# 13. What I want critiqued

1. Three of the project's four validated facts predict magnitude. Zero predict
   direction, after 87 directional attempts. Is "magnitude is predictable,
   direction is not" the correct conclusion — or the signature of looking only at
   OHLCV bars, which cannot see order flow?
2. Is the promotion bar so conservative it kills real but modest edges? Šidák at
   N=467 sets the Discovery bar near 3.7 standard errors; a true 0.05R edge would
   need ~5,400 trades to clear it and a once-a-session hypothesis gets ~2,100. How
   would we tell "no edge" from "filter too strict"?
3. 468 trials in roughly two weeks is a very high search rate, and the
   multiplicity penalty grows with it. Is the answer fewer and better-motivated
   hypotheses rather than a looser bar?
4. The bot has never filled an order. Is building the entire execution half before
   having anything to execute the right sequencing, or elaborate procrastination?
5. If direction is genuinely unavailable, what is the honest business built on
   magnitude prediction alone — and is a directional futures bot simply the wrong
   goal for this data?
6. What is the single biggest way this project could still be fooling itself?

---

# 14. Everything that changed since v2 (September 13th, 8:50 pm CT)

Audited against 27 commits, 46 files added, 14 core files modified.

## 14.1 New tools

| Tool | What it is |
|---|---|
| `stack_spec.py` | Conditional-stack schema, validator, hash-at-registration, attempt counter |
| `stack_scan_runner.py` | Paired stack runner — layers in time order, difference bootstrap |
| `validate_hyp156.py` | Written and hashed **before the data exists** |
| `broker_interface.py` | The broker contract — Order/Ack/Fill/Position, vendor-neutral |
| `simulated_broker.py` | Deliberately hostile broker: rejects, partial fills, mid-order disconnects, late acks |
| `order_path.py` | Signal → order → ack → fill → reconciliation → crash recovery |
| `bot_forward_log.py` | The free **statistical** forward test (two clocks rule) |
| `execution_measurement.py` | B5 — the 14 frozen execution checks |
| `bot_stack_paper_run.py` | B7 — the **execution** loop, one row per session |
| `integrity_checks.py` | U6 — the Gate's 7-check mechanical suite |
| `market_behavior_discovery_scan_036.py` | The M30 scan |
| `cycle_preflight.py` | The standing opening sequence, as one command |
| `cycle_close.py` | The standing closing sequence + the compliance record |
| `cycle_review.py` | The whole day's cycles side by side |
| `statistical_hyp162.py` | Statistical stage for hyp-000162 |
| `director_reeval_hyp162.py` | Director separability for hyp-000162 |

## 14.2 Modified tools

- `idea_factory.py` — **new `--interactions` mode** (U28); `build_frame()`
  extracted so both modes cannot drift apart.
- `ops_checks.py` — **two new checks: `preflight` and `git-sync`** (11 → 13);
  `awaiting-jason` fixed to actually read the "Blocked — needs Jason" section.
- `project_wide_multiplicity.py` — `STACK_REGISTRY`, `register_stack()`,
  `stacks_attempted()`; scan_035 and scan_036 registered.
- `research_ledger.py` — **U24 status-transition guard**: post-Validation
  statuses are refused without a validation-slice row.
- `integrity_blind_packet.py` — six stack checks added to the Gate brief.
- `mechanisms/TEMPLATE.md` — sections 4a / 4b / 9a.
- `git_unlock.sh` — now clears stale remote-tracking ref locks.

## 14.3 New rules, forms and registries

- **UNDERPOWERED** closure status — the format's own failure mode; consumes an
  attempt; the definition is never loosened to fix it.
- **STACK_REGISTRY** — every stack hashed at registration; a changed spec is a
  different trial.
- **`look_cells_k`** — the number of cells a look table examined, carried into
  any spec sourced from it.
- **B7 execution anchor** — separate from the statistical forward anchor, written
  to disk so a later cycle cannot silently move it.
- **Preflight receipt + compliance record** — the opening and closing sequences
  now leave evidence; a skipped step is visible, not silent.
- **Scheduling changed from a chain to pre-booked one-shots** — previously each
  cycle booked its successor, so one failure ended the day silently.
- **Standing change:** run the mechanical suite on a candidate *before* the Gate.
- **Standing change:** the Idea Factory must report its queue split by job, with
  the direction count stated even when zero.

## 14.4 Results produced

- **Stack A → hyp-000161: POWERED NULL.** First conditional-stack result. One of
  two permitted nulls spent. Consequence: B2 is sizing/permission, not an entry
  filter.
- **U28 interaction table: nothing.** K = 9,910 distinct cells examined; with that
  many looks a cell needs |z| ≈ 4.56 to stand out family-wise; the strongest is
  4.4. **Zero clear it.** At the project's current resolution the market states on
  disk do not visibly modify one another beyond their own separate effects — so
  the conditional-stack format has no sourced material better than the pair that
  already produced a null.
- **U6 first runs.** Stack A: 3 green, 2 red (era-dependent; top 5% of
  observations carry 188% of a small net effect). hyp-000142: 5 green, 0 red —
  the first independent structural audit of a promoted fact, and it holds.
- **Scan 036 → hyp-000162.** All three registered predictions passed. Then
  Statistical **PASS** (stable across halves and both volatility regimes,
  survives Šidák at N=467 with the whole adjusted interval above zero, Validation
  would be 82% powered at half the effect). Then Director **ADVANCE** (75–88%
  retained against every existing fact *and* against its own lagged self).
- **M32 / Entry 36 sourced** with the shifted-signal placebo **pre-registered as a
  gating control** — written in because hyp-000162 passed everything and then
  tripped one.

## 14.5 Errors found and corrected — the honest column

- **The staff meeting's central premise was false.** It claimed H118 was the
  project's one directional edge and recommended building the live bot around it.
  H118 had been rejected two days earlier. Cause: a query deduplicated the
  append-only ledger by name keeping the *first* row, so superseded statuses read
  as current; and `NEXT_UP.md`'s top section still said "Holdout passed."
  Both fixed; the ledger's latest row per ID is now stated as the status of
  record.
- **Scope overreach, corrected by Jason.** A line reading "hunt larger trades
  only" was written into the handoff file. **Intraday remains primary**, larger
  candidates are not disqualified, and no horizon boundary is imposed.
- **Three false verdicts inside U6, caught on its own first runs.** The roll-date
  check flagged ordinary calendar exposure (12.7% base rate against a 5%
  threshold); cost-sensitivity *passed* an effect that had inverted under 2×
  costs; the placebo failed a Holdout-passed fact because a volatility tercile
  persists day to day. All fixed with regression tests.
- **K inflated 33%** in the interaction table (14,740 → 9,910) — it counted label
  rows rather than distinct data cells, and that number feeds registered specs.
- **A false FAIL in the new git guardrail** — a stale remote-ref lock made pushed
  work look unpushed. It would have failed every unattended cycle.
- **The `awaiting-jason` check never read the section named "Blocked — needs
  Jason."** Everything parked there had been invisible.
- **The opening sequence was silently skipped in four consecutive cycles.** The
  daily checkers did not run at all; nothing detected it. This is why
  `cycle_preflight.py` exists.
- **The busy-work guardrail fired correctly** after three infrastructure cycles
  and cleared when the next cycle moved the pipeline. It should keep firing on
  schedule; a guardrail that only fires when you already agree with it is not a
  guardrail.

## 14.6 Methodological lessons added to KNOWLEDGE

1. **A structural check needs its own base rate before its threshold means
   anything** — and the base rate must be computed, not assumed. Three checks
   were wrong on first contact with real data, all in the same direction: firing
   on something normal.
2. **A high placebo score is a reason to run the residualised test, not a verdict
   on its own.** Yesterday's opening range does 74% of hyp-000162's work, yet
   87% survives holding yesterday fixed. Both are true: a lagged and a current
   predictor can share a persistent driver without being substitutes.
3. **Pre-registration protects against moving the goalposts; it does not protect
   against asking too few questions.** hyp-000162 passed every registered
   prediction including a prior-day-range control, while a variable never in the
   scope explained most of it.
4. **Infrastructure that pays off one cycle later is not busy work — but the
   alert should keep firing anyway.**

## 14.7 Parked on Jason

| Item | Status |
|---|---|
| **H118's open position predates the forward anchor** | Its one open paper position is dated Sept 8th; the anchor is Sept 9th. Written by a bug fixed five minutes before the log was committed. Three options: void it, keep it excluded from the 40-trade count, or keep it with reasoning recorded. **Not touched** — frozen evidence. |
| **Data currency** | Prices end Sept 8th. B7 cannot accumulate any execution sample. Seven years of 1-minute data cost $5–15 against an untouched $20/month cap. This is an *operating cost*, distinct from the NO PURCHASE decision about new instruments. |
| **6E validation pull** | hyp-000156 passed Statistical four ways and cleared its Gate conditions; Validation cannot run without it. A standing "no" is a fine answer — better decided than defaulted. |
| IBKR futures permission | 30-day cooldown to ~Oct 13th. Not to be re-raised before then. |
| Šidák method | Jason's call. |
| PAPER VERIFIED review threshold | Undefined governance gap, flagged by Jason himself. |
| D11 swing strategy | Awaits Jason — do not build. |
| B8 live authorization | Jason's alone, non-delegable. |

---

*End of Full Scope v3. Next version supersedes this one and must audit against
the change log since this commit.*
