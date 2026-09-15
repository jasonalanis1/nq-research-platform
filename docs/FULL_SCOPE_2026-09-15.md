# Tony — Full Scope

**Version: September 15th, 2026 (v4).** Supersedes `FULL_SCOPE_2026-09-14.md`.

Audited against the complete change log since the prior version was committed
(commit `fc7c0fd`, September 14th ~8:50 pm CT): 19 commits, 59 files changed,
9,198 insertions, 496 deletions. Every rule, tool, form, registry, metric and
parked decision that changed is listed in Section 14, not only the headline
ones.

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
market going up. The second-clearest proof landed in the last 24 hours: hyp-000162
passed every registered prediction at Discovery, Statistical, the blind Gate
(6 of 7 conditions), and a pre-registered one-shot Validation — and still failed
when tested jointly against the facts the project already owns (Section 14.4).
Passing every stage individually is not the same as surviving the whole stack at
once.

---

# 3. The honest current state

**155 hypotheses tested. 142 rejected. 2 survivors, both magnitude. A third
result — real, validated, but not promoted.**

| | |
|---|---|
| Distinct hypotheses | 155 |
| Rejected | 142 |
| Survivors (Holdout passed) | 2 — both **magnitude**, not direction |
| Validated, not promoted | 1 — hyp-000162 (Section 14.4: PASS at Validation, DO NOT PROMOTE at Portfolio) |
| Registered trials, project-wide | 467 |
| Trials since the project's own last "alive" result | 6 |
| Trials per "alive" result (467 / 3) | 155.7 |
| Test suite | 491 passing |
| Operational checks | 13 — 12 green, 1 WARN (`awaiting-jason`: real parked items in Section 14.7, not a defect) |

**The two survivors, unchanged since v3:**
1. High implied volatility (VXN) relative to its own trailing level → a wider
   next session.
2. A quiet midday → an expanded afternoon.

**The third result closed out this window, and it is not a clean win.**
hyp-000162 (a wide opening 30 minutes → a wider midday) passed its Statistical
stage, its blind Gate (conditionally, 6 of 7 discharged), and its pre-registered
one-shot Validation at +0.32 — 66% of the Discovery effect. Then Portfolio tested
it **jointly** against the three facts the project already owns (VXN level, coil,
prior-day range) instead of one at a time: joint retention fell to 17.7% against
a 50% bar, and the decisive forecast test made out-of-sample MAE slightly worse,
not better. Verdict **VALIDATED_NOT_PROMOTED** — a new disposition, distinct from
REJECTED (it is not null) and distinct from HOLDOUT PASSED (it does not attach to
the bot). No Holdout slot was spent. The project's own progress metric
(`src/progress_metric.py`) still counts it as the most recent "alive" result
because it cleared a real out-of-sample bar and was not later rejected — that is
why the table above separates "survivors (Holdout passed)" from the metric's
broader "alive" count of 3; conflating the two would overstate what actually
reached the bot.

A separability blind spot came out of this: single-fact separability at a 50%
bar (the Director's existing test) had passed hyp-000162 at 75-88% against each
existing fact individually. It is the **joint** test that killed it. This is now a
project-wide method finding (Section 14.4), queued to re-check the two Holdout
survivors against the same joint bar.

**hyp-000156** (London-open 6E volatility burst) also closed this window, as a
rejection: recomputing the frozen statistic across all 23 ET hours instead of
just the one Tokyo comparison originally run showed London ranks 4th of 23 and
is credibly **smaller** than the best other hour, not special. This also
corrected a claim carried in the record since before v3 ("the London burst is
London-specific") and took a pending 6E data purchase off Jason's desk entirely.

**Lever C landed:** `src/batch_screen.py`, a cheap 4-gate Discovery-only screen,
ran for the first time and screened 25 of 143 ranked candidate cells. All 25
survived Gate 1 and were written to the shelf as Entries 37-61 — the shelf is now
**29/3 drawable**, up from 4/3 in v3. None of this spends a hypothesis ID; every
one of the 25 still owes Director, Mechanism, Statistical, Gate and Validation in
full. 18 of the 25 (72%) flagged RED on the shifted-signal placebo — logged, not
auto-rejected, and read honestly below (Section 14.4) as evidence the
highest-ranked cells cluster on slow-moving persistent states rather than fresh
information.

**The bot:** milestones B0-B6 complete, B7 now producing real fills for the
first time. **The bot has filled orders — 16 of a pre-registered 20-fill
minimum**, per `src/execution_block.py`'s own cumulative count, all through
frozen placeholders (B3's real entry rule and, since this window, a
high-frequency placeholder built to reach the sample faster), none of them a
claimed edge. One capital-protection kill fired on the placeholder as expected.
Real slippage still needs real micro orders — no demo or paper account anywhere
simulates that (Section 14.4/14.5) — so B8 remains the gate on the actual cost
number.

**The gap that defines the project right now, unchanged:** the bot cannot go
live without a directional entry signal, and every candidate on the shelf —
including all 25 new batch-screen survivors — is about magnitude. Zero are about
direction. This is structural, not an oversight: the engine ranks by strength,
volatility is predictable and direction is not, so magnitude wins every ranking
on merit. The entry slot stays empty no matter how fast the sizing engine gets
better sizing inputs.

---

# 4. How it all fits together — one loop

This is the whole system as a single circuit. Every tool in Sections 6-10 sits at
one of these stations. Two things changed position this window: the LOOK station
now screens in batches instead of one candidate at a time, and the loop grew its
own status readout.

```
  ⓪ SCHEDULE ........ send_later chain, self-booking every 11pm
       |               (cycle_preflight opens every cycle, cycle_close
       |                and session_report close every cycle)
       v
  ① LOOK ............ Idea Factory / Observatory / the shelf
       |               batch_screen.py -- cheap 4-gate pre-filter,
       |               20-30 candidate cells at once, spends no ID
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

  session_report.py reads every one of the stations above at the close of
  every cycle and prints the owner's briefing -- it is the loop's own
  status readout, not a separate process.
```

**⓪ Schedule.** New this window (Section 14.3). The day's cycles are
`send_later` one-shots aimed at this persistent session; the 11pm cycle books
the entire next day, including the next 11pm carrying the same booking
instruction — a self-perpetuating chain that requires no manual booking ever
again. `cycle_preflight.py` opens every cycle (lock, budget, sweep, daily
checkers, shelf position) and `cycle_close.py` plus `session_report.py` close
it. This station did not exist as a described part of the loop in v3; it is the
reason every other station below runs unattended at all.

**① Look.** The Idea Factory crosses every market state on disk against every
session window and a five-outcome battery, on the Discovery slice only, and
ranks what it finds. It is **descriptive and never a result** — a queue entry is
a candidate for a mechanism document, nothing more. Every cell it looked at is
counted, because looking has a cost that must be paid later. New this window:
`batch_screen.py` sits between the Idea Factory's ranked table and the full
per-candidate pipeline, cheaply re-testing 20-30 cells at once (block-CI effect,
Sidak at the batch's own K, a shifted-signal placebo, joint separability against
the existing stack) so the front of the loop can move in batches instead of one
candidate at a time. It still spends no hypothesis ID and still owes the full
Director/Mechanism/Statistical/Gate/Validation stack for anything it flags —
it narrows what gets a full look, it does not replace one.

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
This window added a joint-separability form at the Director/Portfolio boundary
(`portfolio_hyp162.py`'s T1 test) after single-fact separability let a candidate
through that a joint test then killed (Section 14.4) — the single-fact form is
now understood project-wide to be too weak on its own.

**④ Both outcomes are kept.** A failure is written up in a closure form with a
classified failure mode and becomes **negative knowledge** — it is the reason the
next cycle doesn't retry it, and it feeds back to ① to shape what gets looked at.
A survivor enters the **fact registry** and becomes available to the bot. Roughly
9 out of 10 candidates die here, and that is the system working. hyp-000162
demonstrates a third path this window: a candidate can clear every stage and
still be judged VALIDATED_NOT_PROMOTED at the exit — real, but not fact-registry
material because it restates what the registry already knows.

**⑤ The bot.** Validated facts become bot components. The Risk/State Engine (B2)
turns volatility facts into a daily decision — how big, how far, whether at all.
It never answers *which way*. The entry (B3) is currently an acknowledged
placeholder because no directional fact exists to put there. New this window: a
second, frozen, high-frequency placeholder (`execution_dummy.py`) runs alongside
B3 for the sole purpose of producing enough order-path plumbing events to reach
the pre-registered 20-fill sample fast — it is not a second strategy and carries
no more claim to an edge than B3 does.

**⑥ Execution data feeds back — and stops at a wall.** Fills, slippage, latency
and reconciliation flow back to improve execution, sizing and cost assumptions.
They **never** touch the sealed Validation or Holdout slices. The research data
and the execution data are separate circuits that meet only at the bot. This is
the "two clocks rule" (Section 8) made physical. This window's execution data
also fed back into the capital model itself (Section 14.3): the paper loop now
denominates its budget in R (the trade's own stop) instead of Jason's live
dollar band, a change made at the account-control layer, never at a frozen
strategy's definition — the live dollar rules stayed untouched and moved to B8.

**What makes it a loop and not a pipeline:** negative knowledge steers the next
look, execution reality steers the sizing layer, and the schedule itself now
regenerates without anyone booking it — so the system's search gets narrower,
its execution gets more honest, and its own uptime gets more reliable over time,
without any of that being allowed to contaminate the sealed evidence.

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
trial and is counted as one. hyp-000162's Validation spec (`validate_hyp162.py`)
was committed and sha256-hashed **before it ran**, as its own separate earlier
commit (`ee53308`) — the first time this project pre-registered a Validation
spec as a distinct commit rather than a section inside the mechanism doc,
specifically so the pre-registration is independently verifiable in the git
history rather than taken on the project's own word.

## The promotion bar — all four required

1. Statistically credible on its own terms (90% CI excluding the correct null).
2. Survives the **project-wide multiplicity correction** for how many things have
   been looked at.
3. Survives the **blind Integrity Gate**.
4. **Separable** — it is not a restatement of a fact the project already owns.

Bar 4 got sharper this window. hyp-000162 cleared single-fact separability
against every existing fact individually (75-88% retained) and still failed a
**joint** separability test held against all of them together (17.7% retained).
Single-fact separability at a 50% bar is now flagged project-wide as too weak a
test on its own (Section 14.4) — a candidate can restate a *combination* of
existing facts without restating any one of them.

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

Holdout slots (5 total, 3 spent — unchanged this window; hyp-000162 explicitly
did not request one), Validation attempts (one per candidate, two per family —
hyp-000162 spent its one attempt this window and PASSED it; the 6E Validation
attempt hyp-000156 would have needed was withdrawn before it was ever spent),
conditional-stack attempts (two powered nulls closes the format — one spent, no
new stack ran this window), and the data budget (~$20/month cap, $0.0185 spent
on the September 14th top-up, effectively unspent).

---

# 6. How we research — the front half

## Where ideas come from — the Idea Factory

Two modes, both descriptive, both on Discovery only, both spending no hypothesis
ID and registering no scan:

- **Single-state mode.** Every market state × every session window × five
  outcomes (move, range, MFE, MAE, time-to-extreme). Ranked by |z|.
- **Interaction mode (`--interactions`).** Every *pair* of states, cross-tabbed.

**The timing rule** is what makes this legitimate rather than fishing. Every
state carries the moment its value is actually known, and may only be crossed
with an outcome window starting at or after that moment. In interaction mode the
rule applies to **both** layers — a pairing is only as legitimate as its
worst-timed layer.

**Every cell looked at is counted** and the count is carried into any spec
sourced from the table, so the multiplicity of the look is paid for rather than
forgotten. This window's new front-end, `batch_screen.py`, inherits the same
discipline at batch scale: its own Sidak correction is computed at the batch's
own K (25 for the first run), stated explicitly as *not* the full 143-cell sweep
total, and carried forward into `idea_inventory.md` on every survivor entry so
the multiplicity denominator is never lost between the screen and whatever full
scan eventually draws that entry.

## Two hypothesis formats

- **Flat** — one state, one window, one outcome.
- **Conditional stack** — context → location → trigger, ten binding rules. The
  first test is always **paired** (trigger alone vs trigger inside the context),
  because a stack passing on its own tells you nothing about whether the context
  did any work. A paired family is two trials, not one.

**Stack A**, the format's only result to date: the expected-range context known
at the prior close does **not** change what an opening-range break does next.
Difference +0.0247R, CI90 (−0.0496, +0.0976), n = 566/977 against a floor of
100 — a **powered null**, not a thin one. hyp-000161 rejected. One of the
format's two permitted nulls is spent. No new conditional-stack trial ran this
window.

Its consequence remains doctrine: the Risk/State Engine is a **sizing and
permission** layer, not an entry filter.

## The shelf — why we don't draw thin

Ideas are sourced continuously from five channels (map, literature, practitioner,
observatory, gut — each recorded so hit rates accumulate), plus, new this
window, the cheap batch screen as a sixth: `batch_screen.py` reads directly from
the Idea Factory's own ranked candidate table and writes survivors straight to
the shelf. The shelf counts only entries that are genuinely drawable: written
up, mechanism doc done, resurrection ruling signed, data on disk. Floor of 3.
**Below the floor the owed action is more sourcing, never a thin draw.** Draw
order is information gain × edge potential, not age.

**Shelf position: 29/3 drawable**, up from 4/3 in v3 — the jump is entirely
`batch_screen.py`'s first run (25 survivors, Entries 37-61). Every one of those
25 is flagged DRAWABLE but explicitly "screened only, not scanned" — the cheap
screen substitutes for nothing downstream.

## What we've concluded about where the edge isn't

87 of the 142 rejected hypotheses are directional, covering essentially the
entire classical intraday playbook: gap fades (9+ variants), opening-range and
initial-balance breakouts, level-sweep reversals, VWAP mean reversion, momentum
and continuation, trend following, multi-timeframe alignment, cross-asset
lead-lag (bonds, oil, currencies), event drift (FOMC, NFP, CPI), reference-level
fades, round numbers, and multi-day drift conditioned on a state. This count did
not move this window — the one new closure (hyp-000156, London-open 6E
volatility burst) is a magnitude claim on a different instrument, not part of
this directional family.

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
| B4b | Order path (real broker) | **BLOCKED ON JASON** — IBKR futures permission in a 30-day cooldown (~Oct 13th); **recommended this window: build the IBKR adapter now against paper so it is proven before the cooldown lifts** |
| B5 | Execution measurement | **FIRST CUT DONE** — the 14 frozen checks; now scoring a real, growing sample (16/20 fills) instead of reporting INSUFFICIENT SAMPLE at N=0 |
| B6 | Kill switches | **WIRED** — called before every order, fail-closed; fired again this window on the placeholder's expected trailing kill, exactly as designed |
| B7 | Continuous paper run | **LIVE, accelerating** — a second frozen placeholder now runs alongside B3 to reach the execution sample faster; capital model now R-denominated |
| B8 | Live-Limited | **MISSING** — Jason's authorization alone, non-delegable |
| B9 | Scale behind evidence | **MISSING** |

**What changed under B7 this window, in order:**

1. **The paper capital model is now denominated in R**, per the September 14th
   staff-meeting disposition (Section 14.3): `capital_protection.PAPER_CONFIG`
   and `effective_config()` express Jason's $300/$500 budget and $50-150 swing
   band as multiples of R (1R = the trade's own stop in dollars: 4R start, 6R
   after a 20-trade record, 4R trailing floor) instead of fixed dollars. The
   **live** dollar rules are untouched and now belong entirely to B8 — this was
   an account-control change, never a strategy edit. Replayed under the new
   model, the order path saw its first real orders ever: 4 orders, 4 fills, all
   at the intended price, 8/8 mechanical and 14/14 measurement checks PASS.
2. **A frozen high-frequency placeholder, `execution_dummy.py`, was added**
   (Jason: "I need answers sooner... push this as fast as possible") to reach
   the pre-registered 20-fill minimum in days instead of the ~27 trading days
   B3's once-a-session rate would take. It fires four times a session at fixed
   clock times, claims no edge, and every signal it emits is labelled
   `placeholder`. Two real defects were caught and fixed by Step A before any
   live order under this new strategy: a test had been writing synthetic fills
   into the **live** execution journal (purged, `tests/conftest.py` now
   redirects every test away from the live record unconditionally, no test can
   reach it again regardless of whether its author remembered to isolate it);
   and the daily order cap was counting by wall-clock day instead of session
   date, so catching up several sessions in one run tripped the cap after 4
   orders total instead of per session.
3. **16 of 20 fills reached.** One capital-protection kill fired on the
   placeholder's expected 4R trailing stop, exactly as designed — a
   `paper_account_reset` mechanism (proven in rehearsal before any live result,
   never after one, per the anti-optimization rule) lets the sample continue
   past a kill instead of stopping collection.
4. **Broker research corrected an earlier wrong suggestion.** No demo or paper
   account anywhere — Tradovate, IBKR, TradeStation, all checked — produces real
   slippage data; every one of them simulates fills. The real cost number
   requires genuine live orders, which is B8. Recommendation: build the B4b
   IBKR adapter now, proven against paper, so it is ready the moment the
   futures-permission cooldown lifts (~Oct 13th).
5. **24-hour cadence** (12 cycles/day, up from a daytime-only 2-hour cadence)
   was booked to reach the sample faster; batch screening (Lever C) is the
   overnight cycles' work while the bot loop only scores complete sessions.

**B4a's design principle, unchanged:** the simulated broker is *deliberately
hostile*. It rejects, partially fills, disconnects mid-order and returns late
acknowledgements, on command or at a seeded rate. An order path written only
against a broker that behaves is a path whose failure modes were never
exercised. Crash recovery is proven by a test that leaves an unresolved order on
disk and confirms a fresh process recovers it from the broker's own
authoritative state.

**B6 is fail-closed and proven on real data twice now.** On September 8th a real
B3 signal fired, the Risk/State Engine permitted it, and capital protection
**blocked** it — the per-trade swing was $468 against the (then-applicable) live
$50-150 band. On September 14th, under the R-denominated paper model, the
placeholder's 4R trailing kill fired on a running P&L for the first time outside
a test file, exactly as specified.

---

# 8. How we prove we can execute it — the back half

Fourteen frozen execution checks, measured not assumed: signal timing,
exactly-once firing, order correctness, quantity, entry/exit instructions, orders
reaching the broker, fills recorded, expected-vs-actual price, **slippage
measured not assumed**, latency, rejects and duplicates, position reconciliation,
no orphan positions after a crash, and everything logged for reconstruction.

**The two clocks rule, binding, and now visibly load-bearing.** A *statistical*
forward test (does the signal behave as expected on unseen days) and an
*execution* qualification (does the implementation capture it under real orders,
fills, slippage and latency) are different questions with different evidence.
They are never conflated and never compared against each other. The rule is made
physical by two separate log files: `bot_stack_forward_log.jsonl` (statistical)
and `bot_stack_paper_log.jsonl` (execution). This window's live-journal
contamination incident (Section 14.5) was a test accidentally violating exactly
this separation at the file-isolation level, not the two-clocks logic itself —
`tests/conftest.py` now makes that violation structurally impossible rather than
relying on each test author to remember it.

**Honest about what it cannot see:** every check reports its own sample size and
returns INSUFFICIENT SAMPLE rather than a false pass. At N=0 it says so. A green
from a check that never ran is worse than no check at all. At 16/20 fills, checks
1-8 (mechanical) are running for real; slippage (check 9) is not yet measurable
until 20, and the number that comes back at 20 will still not be a **real** cost
figure — every fill behind it is simulated by a demo broker, and only B8's live
micro orders can produce a genuine slippage number (Section 7).

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
is not new*; hyp-000162 retained 75-88% against every fact **individually** and
advanced — then Portfolio's **joint** version of the same idea retained only
17.7% and killed it (Section 3, Section 14.4). The single-fact form is not being
retired, but it is no longer treated as sufficient on its own.

**The Integrity Gate runs blind.** It receives the frozen spec and the raw cell
outputs — not the narrative sections of the mechanism doc, not the expected
result, not the Director's recommendation. A test asserts the packet contains no
line from the narrative sections. hyp-000162's Gate run this window found two
real defects no earlier stage had raised (within-arm bootstrap blocks needed
correcting; a full-sample tercile edge needed recomputing) and ruled CONDITIONAL
— 6 of 7 conditions were discharged with numbers before Validation ran; the 7th
(the cost clause) stays open because it needs the execution record, not more
research.

**The Gate's mechanical half**, seven checks that run on every candidate before
the blind review, green/red, no judgment. A red is a *blocking finding for the
Gate*, never an automatic close. Extended this window with the shifted-signal
placebo as the equivalent mechanical check inside `batch_screen.py`'s own
4-gate screen — 18 of 25 first-run survivors flagged RED there and were carried
forward, logged, not auto-rejected, per the same standard the Gate itself uses.

---

# 10. How we learn — and how we guard against fake work

Every closed hypothesis gets a closure form with a classified failure mode.
Failure modes are named and reusable; #7 is the H118 mode — *beat the wrong
baseline*.

**Named shapes of manufactured work, each with a guard:**

- *Busy work* — cycles that produce artifacts but move no candidate. Guard: an
  operational check that fails when three consecutive cycles move no ledger row,
  scan, document or inventory entry.
- *Reassuring reports* — a role that files a comforting summary instead of doing
  work. Guard: the checks are mechanical code, not an agent's judgment. This
  window's owner's briefing (`session_report.py`, Section 14.3) was built to the
  same standard: every figure is read live from the project's own files at
  print time, not hand-typed, so the scoreboard cannot drift from what the files
  actually say. Three reporting bugs were found and fixed building it — see
  Section 14.5.
- *Retuning after a result* — guard: hashed frozen scopes, one shot. Explicitly
  reaffirmed this window: Jason's standing direction that paper trading is "for
  experimenting" does **not** loosen this — experimenting means candidates
  frozen before they run, never tuning one in flight.
- *Restatement as discovery* — guard: the Director's separability stage,
  strengthened this window by the addition of a joint form (Section 5) after
  the single-fact form let a restatement through.
- *A queue that looks healthy but feeds nothing* — guard: the Idea Factory must
  report its split by job with the direction count stated even when it is zero.
  Still zero this window (Section 3).
- *A schedule that quietly stops* — new this window's own honest finding, not a
  guard yet formalized as a check: two duplicate 11pm triggers for the same
  instant were found and removed during the 9pm close-out (Section 14.5), which
  would have silently double-booked the next day had they gone unnoticed.

---

# 11. Rules that never bend

- Never fabricate data. Ever.
- The Holdout is sealed. Only Jason opens it.
- A frozen strategy is never retuned. Disappointing behaviour permits retain,
  restrict, suspend or retire — never a live edit.
- The placeholder entry is never a strategy, never an edge, and its P&L is never
  evidence. This now applies to **two** placeholders (B3 and the execution
  dummy), on identical terms.
- The Idea Factory queue is descriptive and never a result. `batch_screen.py`'s
  cheap screen inherits this exactly — a screen survivor is a candidate for the
  shelf, not a finding.
- One stack = one trial; a paired family = two.
- Below the shelf floor, source more — never draw thin.
- **B8 live authorization is Jason's alone and is non-delegable.**
- No statistical result authorizes capital by itself.
- Nothing touches H118 or EXP047 without Jason.
- An automated cycle never edits a forward-validation evidence log on its own
  initiative — not even to correct a known error.

**Verified against this window's actual work, not assumed:** nothing above was
touched. The two changes that came closest to a rule boundary were both checked
explicitly and both landed outside it — the R-denominated paper capital model is
an account-control change, not a strategy edit, and the live dollar rules it
replaces in paper were moved intact to B8, never altered; and Jason's "shorter
holding period is now a ranking criterion" is a Discovery-stage preference among
**candidates not yet run**, not a retune of anything frozen.

---

# 12. Autonomy — what runs without me and what doesn't

Cycles run every two hours, 24 hours a day (accelerated from a daytime-only
cadence this window, Jason: "push this as fast as possible"), **pre-booked as
independent one-shots, chained through a single self-booking step**: the 11pm
cycle books the entire next day's cycles, including the next 11pm carrying the
same booking instruction, so the schedule regenerates itself and never again
depends on anyone remembering to book it (Section 14.3). Each cycle:

1. **Preflight** — one command: lock, budget clock, pipeline sweep, both daily
   checkers, shelf/sourcing position. Writes a receipt.
2. **Ordering principle** — advance the lowest incomplete bot milestone that can
   actually move; if none can, say which is blocked and why, then fall through to
   research.
3. **The work item.**
4. **Close-out** — one command: tests, operational checks, commit *and push*
   verified, lock released, preflight receipt verified as this cycle's. Writes
   one compliance row, then prints the owner's briefing (`session_report.py`).

**Runs unattended:** everything through Validation, including spending a
Validation attempt — hyp-000162's Validation ran unattended this window and
passed; the subsequent Portfolio DO NOT PROMOTE call also ran unattended, because
it is a research judgment, not a capital or Holdout decision.

**Requires Jason:** opening the Holdout, authorizing live capital, buying data,
and any decision about frozen evidence. The September 14th data top-up
(Section 14.4) still had to run from Jason's own terminal — the sandboxed
session's egress to Databento is still blocked.

---

# 13. What I want critiqued

1. Three of the project's four validated-or-better facts predict magnitude
   (two Holdout-passed, one Validated-not-promoted). Zero predict direction,
   after 87 directional attempts and 25 new batch-screen survivors, all of them
   also magnitude. Is "magnitude is predictable, direction is not" the correct
   conclusion — or the signature of looking only at OHLCV bars, which cannot see
   order flow?
2. Is the promotion bar so conservative it kills real but modest edges? Šidák at
   N=467 sets the Discovery bar near 3.7 standard errors; a true 0.05R edge would
   need ~5,400 trades to clear it and a once-a-session hypothesis gets ~2,100. How
   would we tell "no edge" from "filter too strict"? hyp-000162 is a live version
   of this question now: it cleared every single-fact bar and still lost to a
   joint test. Was the joint test right, or is joint separability itself now the
   filter that is too strict?
3. 18 of 25 batch-screen survivors (72%) flagged RED on the shifted-signal
   placebo — logged, not rejected, on the theory that a persistent slow-moving
   state can legitimately fail a same-direction-shifted placebo without being
   fake. Is that theory correct, or is it a convenient reason to keep 18
   candidates that a stricter reading would drop before they ever reach the
   shelf?
4. The bot has filled orders for the first time, but every one of them is
   through a placeholder built explicitly to reach a sample size fast, not
   through anything with a claimed edge. Is 20 plumbing fills from two
   placeholders actually informative about execution quality once a real
   directional strategy exists, or are we measuring the pipes with water that
   tells us nothing about what will eventually flow through them?
5. 467 trials in about three weeks is a very high search rate, and the
   multiplicity penalty grows with it. Is the answer fewer and better-motivated
   hypotheses rather than a looser bar — and does `batch_screen.py`, which adds
   25 more candidates to the queue in one run, make that problem worse even
   though each one is individually cheap?
6. If direction is genuinely unavailable, what is the honest business built on
   magnitude prediction alone — and is a directional futures bot simply the wrong
   goal for this data?
7. What is the single biggest way this project could still be fooling itself?

---

# 14. Everything that changed since v3 (September 14th, 8:50 pm CT)

Audited against 19 commits, 59 files changed, 9,198 insertions, 496 deletions.

## 14.1 New tools

| Tool | What it is |
|---|---|
| `data_topup_databento.py` | Quotes the exact refresh cost, refuses above a cap, writes a new data file (old bars stay authoritative), logs real cost, runs the continuity check |
| `data_continuity_check.py` | 7 checks on freshly-pulled data before it is trusted |
| `b7_replay.py` | B7 Step A — replays every session since the execution anchor through the real B7 loop into its own log/journal, 8 mechanical checks |
| `execution_block.py` | The standing "Execution" block every execution-touching cycle report ends with (fills, cumulative toward 20, measured cost, defects) |
| `monetization_hyp162.py` | Monetization stage for hyp-000162 (sizing input, cost share, regime-stability caveat) |
| `gate_conditions_hyp162.py` | The blind Gate's 6-of-7-discharged CONDITIONAL ruling for hyp-000162, with numbers |
| `validate_hyp162.py` | The frozen, sha256-hashed, pre-registered one-shot Validation spec for hyp-000162, committed before it ran |
| `director_reeval_hyp156.py` | Recomputes the frozen hyp-000156 statistic across all 23 ET hours, not just the original Tokyo comparison |
| `portfolio_hyp162.py` | Portfolio's joint-separability form (T1) — the test that produced DO NOT PROMOTE |
| `execution_dummy.py` | Frozen high-frequency placeholder, 4 orders/session, no claimed edge, built to reach the 20-fill sample fast |
| `batch_screen.py` | The cheap 4-gate Discovery-only screen (Lever C): block-CI effect with a calendar-time bootstrap, batch-own-K Sidak, shifted-signal placebo, joint separability |
| `session_report.py` | The owner's briefing printed at the close of every cycle — MONEY / THE BOT / PIPELINE / OPERATIONS / YOUR DESK, every figure read live from the project's own files |

## 14.2 Modified tools

- `capital_protection.py` — added `PAPER_CONFIG` and `effective_config()`: the
  paper loop's budget, raised budget and trailing floor are now expressed in R
  (the trade's own stop) instead of fixed dollars; live `CONFIG` and its
  $50-150/$300 rules are byte-for-byte unchanged.
- `order_path.py` — now takes a `cfg` parameter so callers can pass the paper or
  live capital config explicitly instead of a module-level constant.
- `bot_stack_paper_run.py` — wired to `effective_config()`; gained
  `--strategy {b3,dummy}` so the same loop can run either the real placeholder
  or the acceleration dummy, with per-strategy coverage in its own tests; gained
  the `paper_account_reset` mechanism so a capital-protection kill does not stop
  fill collection.
- `tests/conftest.py` — new autouse fixture that redirects every test's
  `bot_stack_paper_run` paths (log, journal, anchor) to a temp directory
  unconditionally, closing the live-journal-contamination incident (Section
  14.5) at the root rather than relying on each test to isolate itself.

## 14.3 New rules, forms and registries

- **VALIDATED_NOT_PROMOTED** — a new ledger disposition, distinct from REJECTED
  (not a null result) and HOLDOUT PASSED (does not attach to the bot); no
  Holdout slot is spent reaching it.
- **Joint separability (T1)**, `portfolio_hyp162.py`'s form — tests a candidate
  against every existing fact held together, not one at a time; project-wide
  method item queued to re-run the two Holdout survivors against it.
- **`STACK_REGISTRY`/batch-K bookkeeping extended to batch_screen.py** — every
  screen survivor carries its own screen's K (25 for the first run) into
  `idea_inventory.md` so the multiplicity denominator travels with the entry.
- **PAPER_CONFIG / R-denominated paper capital** — 1R = the trade's own stop;
  4R start, 6R after a 20-trade record, 4R trailing floor; live dollar rules
  untouched and reassigned to B8 scope.
- **Execution block standard** — every cycle report touching execution ends
  with `execution_block.py`'s printed block; the rule states explicitly when to
  interrupt Jason (a capital-protection trip, an integrity problem on promoted
  work, or a defect changing a frozen spec's meaning) and when not to (a
  rejection, a defect found and fixed, a candidate advancing a stage).
- **Self-booking schedule** — the 11pm cycle books the whole next day, ending
  the need for anyone to book cycles manually; if an 11pm cycle ever fails to
  book, the next cycle to notice books the remainder of the day and reports
  the gap.
- **Owner's briefing standard** — `session_report.py`'s five fixed sections,
  read live from the project's own files at print time, so the report cannot
  drift from what actually happened; SPEND demoted from a standing section to
  an on-demand item on YOUR DESK.
- **Corrected sample-size standard** — the pre-registered execution-validation
  minimum is stated everywhere as 20 paper trades with slippage measured, not
  40 (Section 14.5).

## 14.4 Results produced

- **hyp-000162 → PASS at Validation, DO NOT PROMOTE at Portfolio.** One-shot
  Validation: +0.32, 66% of the Discovery effect, both pre-registered gating
  predictions cleared. Portfolio's joint residual against VXN + coil +
  prior-day range held together: +0.059 (−0.029, +0.151), retained 17.7%
  (lower bound −14.3%) against a 50% bar; the decisive forecast test moved MAE
  from 0.3252 to 0.3256 — slightly worse, not credible. Single-fact
  separability against each existing fact individually still replicates
  out-of-sample at 69-96%, so the collapse is specifically joint-vs-single, not
  a method failure elsewhere. Status VALIDATED_NOT_PROMOTED, no Holdout slot
  spent. Project-wide method item queued: re-check hyp-000105 and hyp-000142
  (the two Holdout survivors) against the same joint test.
- **hyp-000156 → CLOSED, real is not new.** Recomputing the frozen statistic
  across all 23 ET hours (not just the single Tokyo comparison originally run)
  puts London 4th of 23; London minus the best other hour (10:00 ET) is
  −0.0333 (−0.057, −0.008) — credibly **smaller**, not merely
  indistinguishable. Six of 23 hours clear the same bar; London is one member
  of a family, not a special window. Corrects a claim in the record since
  before v3 that the burst was "London-specific." The pending 6E Validation
  data purchase is withdrawn from Jason's desk entirely.
- **Batch screen (Lever C), first real run.** 25 of 143 ranked candidate cells
  screened, 25/25 survived Gate 1 (block-CI effect with a calendar-time
  bootstrap, credible at the batch's own Sidak K=25), written to
  `idea_inventory.md` as shelf Entries 37-61 (shelf 29/3 drawable, up from
  4/3). 18 of 25 (72%) flagged RED on the shifted-signal placebo — logged as a
  finding, not auto-rejected, and read as the top-ranked cells clustering on
  slow-moving persistent states rather than fresh information; flagged to
  Director/LEARN as an open question, not resolved here.
- **Data refresh landed, $0.0185.** Step A replay found and fixed two real
  defects before any live order under the refreshed data: a Sunday-evening
  fragment with no RTH was scoring as a session, and the in-progress current
  day would have booked a fabricated exit from `session_end_fallback` had it
  filled; `session_is_complete()` now refuses both and is shared by the live
  loop and the replay so they cannot drift apart. Step B logged 3 new live
  sessions (Sept 9-11): record before the capital-model change was 4 sessions,
  0 orders, 0 fills, all blocked by B6 for swing width — a structural finding
  (the $50-150 band fits only ~2.4% of 2026 signals, median swing $376,
  against ~77% in 2018, because NQ moved from ~4,500 to ~29,500 while the band
  stayed fixed in dollars), not a bug, and nothing was changed to fix it —
  parked on Jason, resolved by the staff meeting below.
- **Staff meeting on the swing band** corrected the premise: capital protection
  was blocking correctly; the $50-150 band is Jason's own current live
  appetite from September 11th, not a stale rule; the real collision is that
  appetite against a much-wider-stopped placeholder strategy. Disposition
  MODIFY: R-denominate the **paper** capital model, leave the **live** dollar
  rules untouched and move them to B8. Jason: "I am available to add more
  money if the ROI on the trade is there" — recorded as conditional, not an
  authorization.
- **Replay under the new model:** first real orders ever through the order
  path — 4 orders, 4 fills, every fill at the intended price, no hanging
  positions, 8/8 mechanical and 14/14 measurement checks PASS.
- **Acceleration:** `execution_dummy.py` reached 16 of the pre-registered
  20-fill minimum, with one capital-protection kill recorded as evidence the
  trailing stop fires on a running P&L outside a test file. Broker research
  corrected an earlier wrong suggestion: no demo or paper account anywhere
  produces real slippage data (every one simulates fills); the real cost
  number needs B8. Recommendation: build the B4b IBKR adapter now against
  paper so it is proven before the ~Oct 13th futures-permission cooldown
  lifts.

## 14.5 Errors found and corrected — the honest column

- **A live journal contamination.** A test had been writing four synthetic
  fills (price 135.05, date 2026-01-06) into the **live** execution journal —
  the permanent record the entire back half of the roadmap measures against.
  Purged, the incident documented in
  `research/incidents/live-journal-contamination-2026-09-14.md`, and
  `tests/conftest.py` now redirects every test away from the live record
  unconditionally, so no future test can reach it whether or not its author
  remembered to isolate it.
- **A daily order-cap bug.** `capital_protection.py`'s cap was counting orders
  by wall-clock day instead of session date, so catching up several sessions
  in one replay run tripped the 4-orders-per-day cap after 4 orders **total**
  instead of resetting per session — found and fixed by Step A before any
  live order under the new dummy strategy.
- **The paper-trading sample size was reported wrong.** The pre-registered
  execution-validation minimum is 20 paper trades with slippage measured (the
  back-half spec, Stage 3.5 ENTRY); 40 is `capital_protection`'s unrelated
  catastrophe-tail window, and the data-refresh queue item had conflated the
  two. Both reports now cite 20.
- **A 422 error on the first real data pull.** GLBX.MDP3's historical end lags
  real time by ~20 minutes; asking for "now" as the top-up window's end failed
  outright with `422 data_end_after_available_end` rather than returning what
  exists. Nothing was purchased on the failed attempt. Fixed by reading the
  dataset's real available end from `metadata.get_dataset_range` and clamping
  the window to it, with a now-minus-30-minutes fallback if that read itself
  fails (errs toward asking for less, never more).
- **Three reporting bugs found building `session_report.py`.** "Moved this
  session" was a guessed 3-hour window, now bound to the actual cycle
  checkpoint; "in flight" listed candidates that had already closed, now
  checked against the latest ledger status rather than a stale snapshot; two
  different "this week" counts both read audit backfills as real work — the
  odds line is now date-independent on purpose so a backfill cannot inflate
  it.
- **A scope-overreach line, corrected by Jason.** A line reading "hunt larger
  trades only" had been written into a handoff file. Intraday remains primary;
  larger candidates are not disqualified; no horizon boundary is imposed.
- **A duplicate scheduling bug, found closing out the day.** Two separate
  11:00 pm CT triggers had been booked for the exact same instant — a
  duplicate left over from an earlier session or compaction — which would have
  double-run the close-out and double-booked the next day. The stale duplicate
  was deleted; a full trigger listing confirmed exactly one trigger per
  remaining slot through tomorrow 11pm. For completeness: two duplicate 9:00
  pm triggers also fired for a slot this cycle's manual work already covered —
  redundant but harmless, since the work they would have repeated was
  idempotent-checked rather than literally re-run twice; both were one-shots
  and are already gone from the active list on their own.

## 14.6 Methodological lessons added to KNOWLEDGE

1. **Single-fact separability at a 50% bar is too weak a test project-wide.** A
   candidate can retain 75-88% against every existing fact taken one at a time
   and still retain only 17.7% against all of them held together. The joint
   form is now the standard the project trusts; the two Holdout survivors are
   queued to be re-checked against it.
2. **A high placebo-red rate is a finding, not an automatic rejection —** but it
   needs a real explanation, not a shrug. 72% of the batch screen's first-run
   survivors flagged RED on the shifted-signal placebo, consistent with the
   top-ranked cells clustering on slow-moving persistent states that a
   same-direction shift cannot distinguish from the real effect; this is
   recorded as an open Director/LEARN question, not a closed one.
3. **Recompute the full profile before calling anything "special."** hyp-000156
   was carried on a claim ("London is London-specific") built from a single
   comparison hour. Computing the statistic across all 23 hours showed London
   is not even the best of its family. The lesson generalizes: any "window X is
   special" claim needs the full comparison set before it is trusted, not the
   one comparison that happened to be run first.
4. **An account-control change is not a strategy change, but it still needs its
   own paper trail.** Denominating the paper budget in R moved fast (same-day,
   with Jason's go-ahead) precisely because it was written up as distinct from
   the frozen strategy it sizes — the anti-optimization rule was never at risk
   because the object being changed was never the strategy's definition.
5. **A report that reads its numbers live cannot silently drift — but it can
   still be wrong on its first try.** All three `session_report.py` bugs were
   logic errors in what counted as "this session" or "in flight," not stale
   data; live-reading eliminates one failure mode, not all of them.

## 14.7 Parked on Jason

| Item | Status |
|---|---|
| **B4b / IBKR futures permission** | 30-day cooldown to ~Oct 13th. Recommendation this window: build the adapter now against paper regardless, so it is proven before the cooldown lifts. Not to be re-raised before then. |
| **B8 live authorization** | Jason's alone, non-delegable. The real slippage/cost number cannot exist without it — no demo or paper account anywhere simulates real fills (Section 14.4). |
| **hyp-000162's cost clause** | The Gate's 7th condition stays open; it needs the execution record (currently 16/20 fills), not more research. |
| **hyp-000162 joint-separability re-check** | Project-wide item: re-run the two Holdout survivors (hyp-000105, hyp-000142) against the new joint separability test before treating the single-fact result as sufficient anywhere else. |
| **H118's open position predates the forward anchor** | Unresolved since before v3 — its one open paper position is dated Sept 8th; the anchor is Sept 9th. Not touched — frozen evidence. |
| Šidák method | Jason's call. |
| PAPER VERIFIED review threshold | Undefined governance gap, flagged by Jason himself. |
| D11 swing strategy | Awaits Jason — do not build. |
| 18/25 batch-screen placebo-RED cells | Not a decision item yet — flagged to Director/LEARN first; may surface to Jason if the joint-separability re-check treats it as a project-wide pattern. |

---

*End of Full Scope v4. Next version supersedes this one and must audit against
the change log since this commit.*
